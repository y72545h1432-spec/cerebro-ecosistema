"""Similitud semantica NEUTRAL y PLUGGABLE para el ecosistema (la usa la memoria durable compartida).

Da un ranking de relevancia query->docs en capas, SIN dependencias pesadas (nada de torch):

  1. EMBEDDER DENSO (lo mas fuerte): endpoint OpenAI-compatible /v1/embeddings (tu servidor LLM local/llama.cpp
     con nomic-embed, que ya corre aqui). Semantica REAL: 'fatiga' encuentra 'coste de control'.
     Se auto-registra perezosamente desde LOCAL_ENDPOINT (env CEREBRO_EMBED_ENDPOINT o :<PUERTO_LLM>).
  2. TF-IDF + coseno (sklearn si esta) -> n-gramas, terminos raros. Offline.
  3. Token-coseno TF-IDF sin dependencias -> SIEMPRE disponible (orden lexico, mejor que subcadena).

POR QUE EXISTE (2026-06-17): `cerebro_memoria.buscar` recordaba por SUBCADENA -> un agente que busca
'fatiga' no hallaba el hecho que dice 'cansancio/coste de control'. Esto le da recall por SIGNIFICADO
a TODOS los agentes (claude, codex, opencode) -> menos misses, menos re-lectura de docs = menos tokens.

Gemelo: `tu-proyecto-agente/embed.py` hace lo mismo para la cache de decisiones de tu-proyecto-agente. Es DUPLICACION
CONSCIENTE y temporal: el camino de unificacion (que tu-proyecto-agente/embed.py reexporte de aqui, ya que tu-proyecto-agente
pone .cerebro en sys.path) queda anotado en memoria [[mejora-recall-semantico-memoria]]. No re-implementar
una tercera vez: importar de aqui.
"""
from __future__ import annotations

import json
import math
import os
import re
import time
from collections import Counter
from pathlib import Path
from typing import Callable, List, Optional, Tuple

_DENSE: Optional[Callable[[List[str]], List[List[float]]]] = None
_DENSE_TRIED = False
_WORD = re.compile(r"\w+", re.UNICODE)

# Veredicto del probe persistido: que un agente NO pague el timeout del endpoint muerto en CADA
# llamada por CLI (cada llamada = proceso nuevo). Se recuerda ok/fallo con TTL; al cargar un modelo
# de embeddings en tu servidor LLM local basta esperar el TTL (o borrar el archivo) para que se reactive.
_PROBE_CACHE = Path(__file__).resolve().parent / ".embed_probe.json"
_PROBE_TTL_S = 3600.0

# Endpoint OpenAI-compatible local (tu servidor LLM local por defecto). Override por entorno sin tocar codigo.
ENDPOINT = os.environ.get("CEREBRO_EMBED_ENDPOINT", "http://localhost:<PUERTO_LLM>/v1")
EMBED_MODEL = os.environ.get("CEREBRO_EMBED_MODEL", "text-embedding-nomic-embed-text-v1.5")

# Señal de degradacion (causa raiz #2 de la investigacion infinita: el fallo silencioso). Cuando el
# embedder denso no esta y caemos a TF-IDF, el recall pierde "significado" SIN avisar. Escribimos UN
# evento al log compartido (eventos.jsonl, lo ve cerebro_watch/cerebro_salud). Best-effort: si falla,
# NO rompe la busqueda (el camino caliente nunca se cae por la telemetria).
_EVENT_LOG = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "cerebro" / "eventos.jsonl"


def _senal_degradacion(detalle: str) -> None:
    try:
        rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "project": "ecosistema",
               "agent": "-", "runtime": "-", "sesion": "-", "type": "degradacion",
               "summary": detalle}
        _EVENT_LOG.parent.mkdir(parents=True, exist_ok=True)
        with _EVENT_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception:
        pass


def register_dense_embedder(fn: Callable[[List[str]], List[List[float]]] | None) -> None:
    """Registra (o quita con None) un embedder denso: textos -> un vector por texto."""
    global _DENSE, _DENSE_TRIED
    _DENSE = fn
    _DENSE_TRIED = True       # registro explicito: no auto-probar despues


def local_embedder(model: str | None = None, endpoint: str | None = None, timeout: float = 8.0):
    """Embedder denso contra /v1/embeddings local (sin torch). Si el server no responde, lanza ->
    `scores` cae a TF-IDF automaticamente."""
    import json
    import urllib.request
    mdl = model or EMBED_MODEL
    url = (endpoint or ENDPOINT).rstrip("/") + "/embeddings"

    def _embed(texts: List[str]) -> List[List[float]]:
        body = json.dumps({"model": mdl, "input": list(texts)}).encode("utf-8")
        req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read())
        return [d["embedding"] for d in data["data"]]

    return _embed


def _maybe_autoregister() -> None:
    """Primer uso: VALIDA el embedder local con un probe corto y solo lo registra si responde de
    verdad (tu servidor LLM local sirviendo un modelo de embeddings). Si no hay (timeout/sin modelo), NO registra
    -> scores usa TF-IDF y NO se vuelve a intentar (evita colgar el segundos en cada busqueda)."""
    global _DENSE, _DENSE_TRIED
    if _DENSE is not None or _DENSE_TRIED:
        return
    _DENSE_TRIED = True
    verdict = _probe_cached()
    if verdict is False:
        return                          # veredicto reciente: no hay embeddings -> ni intentarlo
    try:
        probe = local_embedder(timeout=2.0)
        v = probe(["probe"])
        ok = bool(v and v[0])
        _probe_store(ok)
        if ok:
            _DENSE = local_embedder()   # validado -> registra el real (timeout normal para lotes)
    except Exception:
        _probe_store(False)             # sin modelo de embeddings -> queda TF-IDF (cache el fallo)


def _probe_cached() -> Optional[bool]:
    """Veredicto persistido del probe si sigue fresco (< TTL); None si caduco/no hay."""
    try:
        d = json.loads(_PROBE_CACHE.read_text(encoding="utf-8"))
        if time.time() - float(d.get("ts", 0)) < _PROBE_TTL_S:
            return bool(d.get("ok"))
    except Exception:
        pass
    return None


def _probe_store(ok: bool) -> None:
    prev = _probe_cached()   # antes de sobrescribir: para señalar SOLO en la transicion a degradado
    try:
        _PROBE_CACHE.write_text(json.dumps({"ok": bool(ok), "ts": time.time()}), encoding="utf-8")
    except Exception:
        pass
    if not ok and prev is not False:   # paso de denso/desconocido -> TF-IDF: avisar una vez por TTL
        _senal_degradacion("cerebro_semantica: embedder denso no disponible -> recall por TF-IDF "
                           "(sin significado). Cargar nomic-embed en tu servidor LLM local reactiva (TTL 1h).")


def has_dense() -> bool:
    """True si hay (o se pudo registrar) un embedder denso = semantica real por sinonimos."""
    _maybe_autoregister()
    return _DENSE is not None


def _cosine_matrix(qv, dvs):
    q = [float(x) for x in qv]
    qn = (sum(x * x for x in q) ** 0.5) + 1e-9
    out = []
    for d in dvs:
        dv = [float(x) for x in d]
        dn = (sum(x * x for x in dv) ** 0.5) + 1e-9
        out.append(sum(a * b for a, b in zip(q, dv)) / (qn * dn))
    return out


def _dense_rank(query: str, docs: List[str]):
    vecs = _DENSE([query] + list(docs))
    if not vecs or len(vecs) != len(docs) + 1:
        return None
    return _cosine_matrix(vecs[0], vecs[1:])


def _tfidf_rank(query: str, docs: List[str]):
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    vec = TfidfVectorizer(lowercase=True, ngram_range=(1, 2))
    m = vec.fit_transform(docs + [query])
    sims = cosine_similarity(m[-1], m[:-1])[0]
    return [float(s) for s in sims]


def _tokens(text: str) -> list[str]:
    return [w.lower() for w in _WORD.findall(text or "") if len(w) > 1]


def _token_rank(query: str, docs: List[str]) -> list[float]:
    """Fallback sin dependencias: coseno TF-IDF sobre tokens locales (siempre funciona)."""
    q = Counter(_tokens(query))
    doc_counts = [Counter(_tokens(doc)) for doc in docs]
    if not q:
        return [0.0 for _ in docs]
    n_docs = len(docs) + 1
    df = Counter()
    for counts in doc_counts + [q]:
        for tok in counts:
            df[tok] += 1

    def _vec(counts: Counter) -> dict:
        return {tok: cnt * (math.log((n_docs + 1) / (df[tok] + 1)) + 1.0) for tok, cnt in counts.items()}

    qv = _vec(q)
    qn = (sum(v * v for v in qv.values()) ** 0.5) + 1e-9
    out = []
    for counts in doc_counts:
        dv = _vec(counts)
        dn = (sum(v * v for v in dv.values()) ** 0.5) + 1e-9
        out.append(sum(qv.get(tok, 0.0) * dv.get(tok, 0.0) for tok in qv) / (qn * dn))
    return out


def scores(query: str, docs: List[str]) -> List[float]:
    """Similitud de `query` contra cada doc en [0,1]. SIEMPRE devuelve una lista (capa que aplique)."""
    if not docs:
        return []
    # No auto-registramos aqui a proposito: scores() usa el embedder solo si YA esta registrado
    # (asi tu-proyecto-agente/embed, que registra manual, no cambia de comportamiento). El auto-probe vive en
    # has_dense(), que es lo que llama la memoria antes de rankear.
    if _DENSE is not None:
        try:
            r = _dense_rank(query, docs)
            if r is not None:
                return r
        except Exception:
            pass            # server caido / sin modelo de embeddings -> baja a TF-IDF
    try:
        return _tfidf_rank(query, docs)
    except Exception:
        return _token_rank(query, docs)


def best(query: str, docs: List[str]) -> Optional[Tuple[int, float]]:
    sc = scores(query, docs)
    if not sc:
        return None
    i = max(range(len(sc)), key=lambda k: sc[k])
    return i, sc[i]
