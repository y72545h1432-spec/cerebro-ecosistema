"""cerebro_llm.py — cliente LLM OpenAI-compatible MULTI-PROVEEDOR con FALLBACK. Stdlib pura (urllib).

POR QUE EXISTE (2026-06-21): el ecosistema puede correr workers/llamadas LLM a COSTO $0 usando los tiers GRATUITOS
de proveedores que hablan el protocolo OpenAI (`POST /chat/completions`): Groq, Google Gemini y
OpenRouter. Un solo cliente sirve para los tres porque el protocolo es el mismo; si uno falla o agota
su cuota del dia, se cae al siguiente automaticamente. Sin dependencias (urllib) -> fiel al ecosistema.

APTO PARA REPO PUBLICO: NINGUNA clave vive en el codigo. Todo se configura por variables de entorno
o por un archivo .env (auto-cargado, ver _cargar_dotenv): clona el repo, pega tu(s) clave(s) gratis
(sin tarjeta) en `.cerebro/.env` (o en ./.env, o exporta CEREBRO_ENV_FILE) y funciona.

CONFIG (variables de entorno):
  GROQ_API_KEY            clave gratis de https://console.groq.com   (sin tarjeta)
  CEREBRAS_API_KEY        clave gratis de https://cloud.cerebras.ai  (sin tarjeta, ~1M tok/dia)
  OPENROUTER_API_KEY      clave gratis de https://openrouter.ai/keys (modelos :free)
  GEMINI_API_KEY          clave gratis de https://aistudio.google.com (o GOOGLE_API_KEY)
  CEREBRO_LLM_PROVIDERS   orden de respaldo, ej "groq,cerebras,openrouter,gemini" (default ese)
  CEREBRO_LLM_MODEL       fuerza un modelo concreto (ignora el mapeo por tier)
  CEREBRO_LLM_BASE_URL    + CEREBRO_LLM_API_KEY (+ CEREBRO_LLM_MODEL) -> proveedor CUSTOM (cualquiera
                          OpenAI-compatible: otro servicio, un gateway propio, etc.)

USO:
  import cerebro_llm
  r = cerebro_llm.chat([{"role": "user", "content": "hola"}], tier="haiku")
  print(r["text"], "via", r["provider"])      # r: {ok, text, tool_calls, provider, model, cost, ...}

TESTEABLE SIN RED NI TOKENS: monkeypatch `cerebro_llm._post` con un fake -> la cadena, el mapeo de
modelos y el parseo de tool_calls se prueban sin tocar internet (ver test_cerebro_llm.py).
"""
from __future__ import annotations
import os
import time
import json
import urllib.request
import urllib.error

# --------------------------------------------------------------------------- presets de proveedores
# Cada proveedor: base_url OpenAI-compatible, las env vars donde buscar su clave, y el modelo GRATIS
# por defecto para cada tier. Los slugs de modelo cambian con el tiempo: se pueden sobreescribir por
# entorno (CEREBRO_LLM_MODEL) o por el toml ([api.models]). Aqui van defaults razonables (jun-2026).
PROVIDERS = {
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "env_keys": ["GROQ_API_KEY"],
        "consigue": "https://console.groq.com  (gratis, sin tarjeta)",
        "models": {"haiku": "llama-3.1-8b-instant",
                   "sonnet": "llama-3.3-70b-versatile",
                   "opus": "llama-3.3-70b-versatile"},
    },
    "cerebras": {
        "base_url": "https://api.cerebras.ai/v1",
        "env_keys": ["CEREBRAS_API_KEY"],
        "consigue": "https://cloud.cerebras.ai  (gratis, sin tarjeta, ~1M tok/dia)",
        # Cerebras free expone pocos modelos (verificado 2026-06-23: gpt-oss-120b, zai-glm-4.7). gpt-oss-120b
        # es fuerte para codigo/tool-use. Verifica los vigentes con GET /v1/models si cambian.
        "models": {"haiku": "gpt-oss-120b",
                   "sonnet": "gpt-oss-120b",
                   "opus": "zai-glm-4.7"},
    },
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
        "env_keys": ["GEMINI_API_KEY", "GOOGLE_API_KEY"],
        "consigue": "https://aistudio.google.com/apikey  (gratis, sin tarjeta)",
        "models": {"haiku": "gemini-2.5-flash-lite",
                   "sonnet": "gemini-2.5-flash",
                   "opus": "gemini-2.5-flash"},
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "env_keys": ["OPENROUTER_API_KEY"],
        "consigue": "https://openrouter.ai/keys  (gratis; modelos :free)",
        "models": {"haiku": "meta-llama/llama-3.3-70b-instruct:free",
                   "sonnet": "deepseek/deepseek-r1:free",
                   "opus": "deepseek/deepseek-r1:free"},
    },
}
# Orden de respaldo (jun-2026): primero los gratis SIN tarjeta y fiables (groq, cerebras), luego
# openrouter (:free), y gemini AL FINAL porque su free-tier sufre un bug de billing ("prepayment
# credits depleted" -> 429 espurio) que lo hace poco fiable. Ver _es_espurio() y II_AGENT_TEAM/BACKLOG.md.
DEFAULT_ORDER = ["groq", "cerebras", "openrouter", "gemini"]

# --------------------------------------------------------------------------- circuit-breaker (D2)
# Un proveedor que devuelve 401/403/429 (clave/permiso/cuota) se "abre" por un cooldown: la cadena lo
# SALTA en vez de re-intentarlo en CADA llamada (lo que pasaba con Gemini "credits depleted"). Tras el
# cooldown se vuelve a intentar. Estado de proceso (se comparte entre threads del drenado; basta con dict).
_BREAKER: dict = {}            # {provider_name: epoch_hasta_el_que_esta_abierto}
BREAKER_COOLDOWN_S = 300       # 5 min: tiempo que un proveedor queda fuera tras un 401/403/429
BREAKER_COOLDOWN_ESPURIO_S = 45  # P0: cooldown CORTO para 429 espurios (bug billing free-tier Gemini)


def _breaker_activo(name: str) -> bool:
    hasta = _BREAKER.get(name, 0)
    if hasta and hasta > time.time():
        return True
    if hasta:
        _BREAKER.pop(name, None)   # expiró el cooldown -> reactiva
    return False


def _marcar_roto(name: str, cooldown_s: float | None = None) -> None:
    _BREAKER[name] = time.time() + (BREAKER_COOLDOWN_S if cooldown_s is None else cooldown_s)


def _es_espurio(code: int, body: str) -> bool:
    """P0: un 429 'espurio' = bug conocido del free-tier de Gemini ('prepayment credits depleted'),
    NO una cuota real agotada. Merece cooldown CORTO (reintentar pronto), no parar 5 min al proveedor.
    Ref: discuss.ai.google.dev .../prepayment-credits-depleted-error-on-free-tier."""
    return code == 429 and "prepayment" in (body or "").lower()


def _causa(code: int, body: str) -> str:
    """D4: traduce un error crudo de proveedor a una causa legible (no volcar HTML/JSON crudo)."""
    b = (body or "").lower()
    if code == 401:
        return "clave invalida o no autorizada"
    if code == 403:
        return "Cloudflare bloqueo el User-Agent" if ("cloudflare" in b or "1010" in b) else "prohibido (403)"
    if code == 429:
        if "prepayment" in b:
            return "bug billing free-tier (429 espurio): reintento corto / usar otro proveedor"
        if any(s in b for s in ("credit", "depleted", "billing", "balance")):
            return "creditos/saldo agotados (recargar o usar otra clave)"
        if "quota" in b:
            return "cuota diaria agotada"
        return "rate limit (429): demasiadas peticiones"
    return f"HTTP {code}"


class LLMSinClave(Exception):
    """Ningun proveedor tiene clave configurada en el entorno -> no se puede llamar a nadie."""


class LLMError(Exception):
    """Todos los proveedores de la cadena fallaron (red, cuota, error del modelo)."""


# --------------------------------------------------------------------------- resolucion de la cadena
_DOTENV_CARGADO = False


def _cargar_dotenv(path: str | None = None, forzar: bool = False) -> list:
    """P0: carga pares KEY=VALUE de un archivo .env a os.environ SIN pisar variables ya definidas
    (el entorno real SIEMPRE manda). Stdlib pura, sin dependencias. Esto es lo que hace cierta la
    promesa del docstring ('pega tu clave en .env y funciona'): antes nada leia el .env.
    Busca, en orden: CEREBRO_ENV_FILE > <dir de cerebro_llm>/.env > ./.env. Idempotente (solo la
    1a vez, salvo forzar=True o path explicito). Devuelve la lista de claves que cargo."""
    global _DOTENV_CARGADO
    if _DOTENV_CARGADO and not forzar and path is None:
        return []
    candidatos = [path] if path else [
        os.environ.get("CEREBRO_ENV_FILE"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"),
        os.path.join(os.getcwd(), ".env"),
    ]
    cargadas = []
    for c in candidatos:
        if not c or not os.path.isfile(c):
            continue
        try:
            with open(c, encoding="utf-8", errors="ignore") as fh:
                for linea in fh:
                    linea = linea.strip()
                    if linea.startswith("export "):
                        linea = linea[7:].strip()
                    if not linea or linea.startswith("#") or "=" not in linea:
                        continue
                    k, _, v = linea.partition("=")
                    k, v = k.strip(), v.strip().strip('"').strip("'")
                    if k and k not in os.environ:      # no pisar el entorno real
                        os.environ[k] = v
                        cargadas.append(k)
        except OSError:
            continue
    if path is None:
        _DOTENV_CARGADO = True
    return cargadas


def _env(*names: str) -> str | None:
    _cargar_dotenv()       # P0: asegura que un .env (si existe) ya este en os.environ
    for n in names:
        v = os.environ.get(n)
        if v:
            return v.strip()
    return None


def _orden(cfg: dict | None) -> list:
    """Orden de proveedores a intentar: CEREBRO_LLM_PROVIDERS > toml [api].providers > DEFAULT_ORDER."""
    env = _env("CEREBRO_LLM_PROVIDERS")
    if env:
        return [p.strip() for p in env.split(",") if p.strip()]
    api = (cfg or {}).get("api", {}) if isinstance(cfg, dict) else {}
    if isinstance(api.get("providers"), list) and api["providers"]:
        return list(api["providers"])
    return list(DEFAULT_ORDER)


def cadena(cfg: dict | None = None) -> list:
    """Proveedores DISPONIBLES (con clave) en orden de respaldo. Cada item:
    {name, base_url, api_key, models}. Incluye un proveedor 'custom' si CEREBRO_LLM_BASE_URL esta puesto."""
    out = []
    # 1) proveedor CUSTOM por entorno (cualquier endpoint OpenAI-compatible) -> primero si existe.
    cbase = _env("CEREBRO_LLM_BASE_URL")
    if cbase:
        out.append({"name": "custom", "base_url": cbase.rstrip("/"),
                    "api_key": _env("CEREBRO_LLM_API_KEY") or "x", "models": {}})
    # 2) presets, en orden, solo los que tengan clave.
    overrides = (cfg or {}).get("api", {}).get("models", {}) if isinstance(cfg, dict) else {}
    for name in _orden(cfg):
        prov = PROVIDERS.get(name)
        if not prov:
            continue
        key = _env(*prov["env_keys"])
        if not key:
            continue
        if _breaker_activo(name):   # D2: en cooldown tras 401/403/429 -> saltarlo
            continue
        models = dict(prov["models"])
        if isinstance(overrides.get(name), dict):
            models.update(overrides[name])
        out.append({"name": name, "base_url": prov["base_url"], "api_key": key, "models": models})
    return out


def _con_clave(cfg: dict | None = None) -> list:
    """Nombres de proveedores con clave configurada, IGNORANDO el circuit-breaker (para diagnostico:
    distinguir 'sin clave' de 'con clave pero en cooldown')."""
    nombres = []
    if _env("CEREBRO_LLM_BASE_URL"):
        nombres.append("custom")
    for name in _orden(cfg):
        prov = PROVIDERS.get(name)
        if prov and _env(*prov["env_keys"]):
            nombres.append(name)
    return nombres


def modelo_para(prov: dict, tier: str) -> str:
    """Modelo a usar: CEREBRO_LLM_MODEL (global) > mapeo por tier del proveedor > su 'sonnet' > '?'."""
    forced = _env("CEREBRO_LLM_MODEL")
    if forced:
        return forced
    m = prov.get("models") or {}
    return m.get((tier or "").lower()) or m.get("sonnet") or next(iter(m.values()), "gpt-3.5-turbo")


def proveedores_listos(cfg: dict | None = None) -> list:
    """Nombres de proveedores con clave (para diagnostico / dry-run)."""
    return [p["name"] for p in cadena(cfg)]


# --------------------------------------------------------------------------- HTTP (urllib)
def _post(base_url: str, api_key: str, payload: dict, timeout: int = 60) -> dict:
    """POST {base_url}/chat/completions con Bearer. Devuelve el JSON. Aislable en tests."""
    url = base_url.rstrip("/") + "/chat/completions"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("User-Agent", "Mozilla/5.0 (cerebro-agent-team)")  # Cloudflare (Groq) bloquea el UA de urllib -> 403 1010
    req.add_header("HTTP-Referer", "https://github.com")        # OpenRouter pide referer/title
    req.add_header("X-Title", "cerebro-agent-team")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _extraer(obj: dict) -> dict:
    """De la respuesta OpenAI saca {text, tool_calls, finish_reason}."""
    try:
        msg = obj["choices"][0]["message"]
    except (KeyError, IndexError, TypeError):
        return {"text": "", "tool_calls": [], "finish_reason": "error"}
    tcs = []
    for tc in (msg.get("tool_calls") or []):
        fn = tc.get("function", {}) or {}
        args = fn.get("arguments")
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except Exception:
                args = {"_raw": args}
        tcs.append({"id": tc.get("id", ""), "name": fn.get("name", ""), "args": args or {}})
    fr = (obj["choices"][0].get("finish_reason") if obj.get("choices") else None) or "stop"
    return {"text": msg.get("content") or "", "tool_calls": tcs, "finish_reason": fr}


# --------------------------------------------------------------------------- API publica
def chat(messages: list, tier: str = "sonnet", cfg: dict | None = None, tools: list | None = None,
         max_tokens: int = 1024, temperature: float = 0.3, timeout: int = 60) -> dict:
    """Llama al primer proveedor disponible; si falla, cae al siguiente de la cadena. COSTO = $0 en
    tiers gratuitos. Devuelve {ok, text, tool_calls, finish_reason, provider, model, cost, intentos}.
    Lanza LLMSinClave si no hay ninguna clave configurada; LLMError si TODOS fallan."""
    chain = cadena(cfg)
    if not chain:
        # D2/D4: distinguir 'sin clave' de 'con clave pero TODOS en cooldown' (mensaje accionable).
        if _con_clave(cfg):
            raise LLMError("todos los proveedores con clave estan en cooldown (circuit-breaker tras "
                           "401/403/429). Revisa cuota/credito/clave o espera el cooldown.")
        nombres = ", ".join(p["env_keys"][0] for p in PROVIDERS.values())
        raise LLMSinClave(
            "No hay clave de ningun proveedor gratis. Define al menos una variable de entorno: "
            f"{nombres}. Consigue una gratis (sin tarjeta) en console.groq.com / aistudio.google.com / openrouter.ai/keys.")
    intentos = []
    for prov in chain:
        model = modelo_para(prov, tier)
        payload = {"model": model, "messages": messages,
                   "max_tokens": max_tokens, "temperature": temperature}
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        try:
            obj = _post(prov["base_url"], prov["api_key"], payload, timeout)
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read().decode("utf-8")[:200]
            except Exception:
                pass
            if e.code in (401, 403, 429):       # D2: abre el breaker; D4: causa legible
                # P0: 429 espurio (bug billing free-tier) -> cooldown corto; resto -> 5 min.
                _marcar_roto(prov["name"], BREAKER_COOLDOWN_ESPURIO_S if _es_espurio(e.code, body) else None)
            intentos.append({"provider": prov["name"], "model": model,
                             "error": f"HTTP {e.code}: {_causa(e.code, body)}", "raw": body[:120]})
            continue
        except Exception as e:
            intentos.append({"provider": prov["name"], "model": model, "error": str(e)[:200]})
            continue
        out = _extraer(obj)
        return {"ok": True, "provider": prov["name"], "model": model, "cost": 0.0,
                "intentos": intentos, **out}
    raise LLMError(f"todos los proveedores fallaron: {intentos}")
