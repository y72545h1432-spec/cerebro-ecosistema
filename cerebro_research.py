"""cerebro_research.py — Motor de Investigación Infinita: saturación semántica + rotación de enfoques.

GLOBALIZADO (2026-06-22, F6): esta lógica vivía DUPLICADA e idéntica en dos proyectos
(`tu-tienda/DOCUMENTACION/II_DAEMON/investigacion_infinita.py` y
`tu-proyecto-agente/research/INVESTIGACION_INFINITA/investigacion_infinita.py`). Es una utilidad del ECOSISTEMA
(la usa la skill `investigacion-infinita`), no de un proyecto -> vive aquí, fuente única. Cada proyecto
conserva un `investigacion_infinita.py` que es un SHIM fino reexportando de este módulo.

Máquina de estado pura y reanudable. Toda dependencia de embeddings entra por `sim_fn` inyectada
(default = `sim_semantica`, que usa `cerebro_semantica.py` del ecosistema), de modo que la lógica se
testea sin GPU.
"""
from __future__ import annotations

import json
import pathlib
import sys

ENFOQUES_DEFAULT = [
    "neurociencia",
    "SOTA-computer-use",
    "training/LoRA",
    "tokens/eficiencia",
    "infra-opensource",
    "datos/datasets",
    "seguridad/robustez",
    "percepcion/UX",
]


def sim_semantica(a, b):
    """sim_fn por defecto: similitud semántica vía `cerebro_semantica` del ecosistema.

    Contrato: float en [0,1]. Import perezoso para no cargar embeddings salvo en corridas
    reales. `cerebro_semantica.scores(query, docs)` devuelve una lista de similitudes en
    [0,1] con degradación elegante (densos -> TF-IDF sklearn -> coseno TF-IDF stdlib), así
    que esta capa SIEMPRE funciona aunque no haya GPU ni sklearn.
    """
    ruta_cerebro = str(pathlib.Path(__file__).resolve().parent)
    if ruta_cerebro not in sys.path:
        sys.path.insert(0, ruta_cerebro)
    import cerebro_semantica  # noqa: E402  (import perezoso intencional)
    res = cerebro_semantica.scores(a, [b])
    if not res:
        return 0.0
    # clamp: el coseno puede desbordar [0,1] por error de float; el contrato es estricto.
    return max(0.0, min(1.0, float(res[0])))


class Investigacion:
    def __init__(self, tema, umbral=0.78, k=3, m=2, enfoques=None, sim_fn=None):
        self.tema = tema
        self.umbral = umbral
        self.k = k                 # sub-ramas repetidas consecutivas -> rama saturada
        self.m = m                 # ramas repetidas consecutivas -> tema saturado
        self.enfoques = list(enfoques) if enfoques else list(ENFOQUES_DEFAULT)
        self.idx_enfoque = 0
        self.nodos = []            # list[dict]
        self.rep_L1 = 0            # ramas repetidas consecutivas
        self.rep_L2 = 0            # sub-ramas repetidas consecutivas (rama actual)
        self.ola = 0               # nº de ola completada
        self.sim_fn = sim_fn       # (texto_a, texto_b) -> float en [0,1]

    # --- enfoques (motor C: diversidad) -------------------------------------
    def enfoque_actual(self):
        return self.enfoques[self.idx_enfoque]

    def rotar_enfoque(self):
        self.idx_enfoque = (self.idx_enfoque + 1) % len(self.enfoques)
        return self.enfoque_actual()

    def agregar_enfoque(self, nombre):
        if nombre not in self.enfoques:
            self.enfoques.append(nombre)

    # --- dedup semántico (motor A: parada) ----------------------------------
    def _texto_nodo(self, nodo):
        return f"{nodo.get('titulo', '')} {nodo.get('resumen', '')}".strip()

    def es_repetido(self, texto):
        if self.sim_fn is None or not self.nodos:
            return False
        mejor = max(self.sim_fn(texto, self._texto_nodo(n)) for n in self.nodos)
        return mejor >= self.umbral

    # --- registro de nodos + saturación -------------------------------------
    def nueva_rama(self):
        self.rep_L2 = 0

    def agregar_nodo(self, nivel, padre, titulo, resumen, fuentes=None, recomendacion=None):
        texto = f"{titulo} {resumen}".strip()
        if self.es_repetido(texto):
            if nivel == 1:
                self.rep_L1 += 1
            elif nivel == 2:
                self.rep_L2 += 1
            return None
        if nivel == 1:
            self.rep_L1 = 0
        elif nivel == 2:
            self.rep_L2 = 0
        nodo = {
            "id": f"N{len(self.nodos) + 1}",
            "nivel": nivel,
            "padre": padre,
            "enfoque": self.enfoque_actual(),
            "titulo": titulo,
            "resumen": resumen,
            "fuentes": fuentes or [],
            "recomendacion": recomendacion or "",
            "estado": "nuevo",
        }
        self.nodos.append(nodo)
        return nodo

    def rama_saturada(self):
        return self.rep_L2 >= self.k

    def tema_saturado(self):
        return self.rep_L1 >= self.m

    # --- persistencia / reanudación -----------------------------------------
    def guardar(self, ruta):
        datos = {
            "tema": self.tema,
            "umbral": self.umbral,
            "k": self.k,
            "m": self.m,
            "enfoques": self.enfoques,
            "idx_enfoque": self.idx_enfoque,
            "nodos": self.nodos,
            "rep_L1": self.rep_L1,
            "rep_L2": self.rep_L2,
            "ola": self.ola,
        }
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)

    @classmethod
    def cargar(cls, ruta, sim_fn=None):
        with open(ruta, encoding="utf-8") as f:
            d = json.load(f)
        inv = cls(d["tema"], umbral=d["umbral"], k=d["k"], m=d["m"],
                  enfoques=d["enfoques"], sim_fn=sim_fn)
        inv.idx_enfoque = d["idx_enfoque"]
        inv.nodos = d["nodos"]
        inv.rep_L1 = d["rep_L1"]
        inv.rep_L2 = d["rep_L2"]
        inv.ola = d.get("ola", 0)
        return inv

    # --- render del mapa ----------------------------------------------------
    def render_grafo(self):
        estado = "SATURADO" if self.tema_saturado() else "abierto"
        lineas = [
            f"# Investigación Infinita — {self.tema}",
            "",
            f"> Ola: {self.ola} · Estado del tema: **{estado}** · Nodos: {len(self.nodos)}",
            "",
        ]
        ramas = [n for n in self.nodos if n["nivel"] == 1]
        for rama in ramas:
            lineas.append(f"## {rama['id']} · {rama['titulo']}  _(enfoque: {rama['enfoque']})_")
            lineas.append("")
            lineas.append(f"{rama['resumen']}")
            if rama["fuentes"]:
                lineas.append(f"- Fuentes: {', '.join(rama['fuentes'])}")
            if rama["recomendacion"]:
                lineas.append(f"- **Recomendación #1:** {rama['recomendacion']}")
            lineas.append("")
            hijos = [n for n in self.nodos if n["nivel"] == 2 and n["padre"] == rama["id"]]
            for h in hijos:
                lineas.append(f"- **{h['id']} · {h['titulo']}** _(enfoque: {h['enfoque']})_ — {h['resumen']}")
                if h["fuentes"]:
                    lineas.append(f"  - Fuentes: {', '.join(h['fuentes'])}")
                if h["recomendacion"]:
                    lineas.append(f"  - Recomendación #1: {h['recomendacion']}")
            lineas.append("")
        return "\n".join(lineas)
