# 20 · Red de roles IA (buscador, investigador y router por capacidad)

> Fecha de corte: 2026-06-18. Este mapa es una capa de decision encima de
> `17_ROUTER_POR_MODELO.md`: primero decide el **rol/capacidad** que hace falta; despues
> usa el router local por tier (`haiku`/`sonnet`/`opus`) o una IA externa si el rol exige
> investigacion web profunda, citas o contexto privado.

## Decision principal

La mejor IA para investigacion profunda hoy no debe integrarse como "un modelo unico para todo",
sino como **rol de buscador-investigador**:

- **Primario para investigacion profunda:** `Gemini Deep Research`.
- **Secundario/contraste para investigacion profunda con control de fuentes:** `OpenAI Deep Research`.
- **Buscador rapido con citas:** `Perplexity`.
- **Razonamiento, arquitectura y sintesis dentro del ecosistema local:** `Claude/Codex` segun disponibilidad.

Motivo: un benchmark reciente de agentes de deep research para trabajo tipo consultoria comparo
Claude Opus 4.6 con web search, OpenAI o3-deep-research y Gemini 3.1 Pro deep-research; Gemini tuvo
la mayor tasa de aceptacion conjunta (21.4%) frente a 9.5% de OpenAI y 9.5% de Claude, aunque todos
siguen fallando mucho y requieren verificacion humana. Otro benchmark academico, ResearcherBench,
concluyo que OpenAI Deep Research y Gemini Deep Research superaban claramente a otros sistemas en
preguntas cientificas abiertas. Por eso el ecosistema usa Gemini como primera pasada de investigacion,
OpenAI como segunda opinion controlada y Perplexity para localizar fuentes rapido.

Fuentes revisadas:
- OpenAI, "Introducing deep research" (2025-02-02, actualizado 2026-02-10): `https://openai.com/index/introducing-deep-research/`
- Google, "Try Deep Research..." (2024-12-11): `https://blog.google/products-and-platforms/products/gemini/google-gemini-deep-research/`
- Asthana et al., "Evaluating Deep Research Agents..." (arXiv, 2026-05-17): `https://arxiv.org/abs/2605.17554`
- Xu et al., "ResearcherBench..." (arXiv, 2025-07-22): `https://arxiv.org/abs/2507.16280`

Fuentes API revisadas:
- OpenAI API, Deep research: `https://developers.openai.com/api/docs/guides/deep-research/`
- OpenAI API, Web search: `https://developers.openai.com/api/docs/guides/tools-web-search/`
- Gemini API, Grounding with Google Search: `https://ai.google.dev/gemini-api/docs/google-search`
- Perplexity docs, APIs overview: `https://docs.perplexity.ai/docs/getting-started/overview`
- Perplexity docs, Sonar Deep Research: `https://docs.perplexity.ai/docs/sonar/models/sonar-deep-research`

## API aprovechable

La red distingue entre **mejor producto humano** y **mejor pieza automatizable por API**.
Si el ecosistema necesita ejecutar busquedas/informes desde scripts, hooks o futuros agentes, priorizar
las opciones con API aunque el producto web de otra IA sea mas comodo.

| Rol API | Opcion | Estado util | Uso recomendado |
|---|---|---|---|
| `buscador-api-profundo` | OpenAI `o3-deep-research` / `o4-mini-deep-research` via Responses API | API directa de deep research; requiere al menos una fuente (`web_search_preview`, file search/vector stores o MCP remoto) y puede usar code interpreter. | Informes largos, analisis con datos, investigacion con archivos internos o MCP compatible `search`/`fetch`. |
| `buscador-api-rapido` | OpenAI Responses API + `web_search` | API directa de busqueda web con filtros de dominios, fuentes y resultados de imagen. | Busqueda controlada por dominios permitidos/bloqueados, verificacion puntual y workflows internos. |
| `buscador-api-google` | Gemini API + Grounding with Google Search | No equivale necesariamente al producto Gemini Deep Research, pero devuelve `groundingMetadata` con queries, fuentes y soportes de cita. | Respuestas actuales con Google Search, citacion estructurada y comparacion contra OpenAI/Perplexity. |
| `buscador-api-perplexity` | Perplexity Sonar / Search API / `sonar-deep-research` | API orientada a busqueda y research; Sonar Deep Research hace busquedas exhaustivas, reportes y devuelve citas/coste/queries. | Busqueda web amplia, research rapido de mercado, due diligence y corpus de enlaces. |

**Decision API:** si la tarea debe correr sola desde el ecosistema, usar primero OpenAI Deep Research API
para investigacion profunda con herramientas, Perplexity Sonar Deep Research para web-wide research rapido,
y Gemini API con Google Search grounding como tercer punto de contraste. Gemini Deep Research queda como
opcion humana/manual excelente cuando se usa desde la app, no como adaptador automatico hasta confirmar una API equivalente.

**Restricciones importantes:**
- OpenAI Deep Research API no soporta function calling generico; soporta web search, file search/vector stores,
  MCP remoto compatible `search`/`fetch` y code interpreter.
- Gemini API cobra/contabiliza por busquedas que el modelo decide ejecutar con Grounding; guardar `groundingMetadata`.
- Perplexity Sonar Deep Research puede gastar por tokens, citas, reasoning y numero de busquedas; poner presupuesto y maximos.
- Cualquier conector con archivos internos o MCP debe pasar por revision de seguridad, sin credenciales en `.cerebro`.

## Rol: Buscador

**Nombre en el ecosistema:** `buscador`.

**Mision:** encontrar fuentes actuales, comparar informacion cambiante y devolver evidencia verificable
antes de que el agente local decida o escriba.

**IA asignada por defecto:**

| Caso | IA/modelo | Por que |
|---|---|---|
| Investigacion profunda, comparativa, multi-documento | Gemini Deep Research | Mejor resultado observado en benchmark reciente de deep research; plan previo y reporte con fuentes. |
| Segunda opinion, fuentes restringidas, MCP/apps o trazabilidad fuerte | OpenAI Deep Research | Permite restringir busqueda a sitios confiables y conectar fuentes por MCP/apps; bueno para contraste. |
| Busqueda rapida, noticias, enlaces y citas directas | Perplexity | Velocidad y formato de respuesta con fuentes; util antes de abrir una investigacion larga. |
| Web puntual dentro de Codex | `web.run` / `apify/rag-web-browser` | Para una pregunta concreta durante una tarea local. |

**Salida esperada del buscador:**

1. Respuesta breve.
2. Fuentes con URL.
3. Fecha de consulta o fecha de publicacion cuando importe.
4. Nivel de confianza: `alta`, `media`, `baja`.
5. Riesgos: contradicciones, fuentes no primarias, informacion vieja, posible marketing.
6. Recomendacion operativa para el ecosistema.

**Regla anti-alucinacion:** ningun informe de buscador se copia como verdad final. La sesion local debe
verificar fuentes criticas, especialmente si hay dinero, salud, legal, seguridad, dependencias, precios,
modelos, benchmarks o decisiones estructurales.

## Red de roles

| Rol | Responsable preferido | Uso principal | No usar para |
|---|---|---|---|
| `orquestador` | Claude/Codex tope disponible | Entender objetivo, dividir trabajo, decidir roles, integrar resultados. | Busquedas largas sin fuentes. |
| `buscador` | Gemini Deep Research -> OpenAI Deep Research -> Perplexity | Investigacion actual, comparativas, fuentes, evidencias. | Editar archivos locales directamente. |
| `arquitecto` | Opus / GPT frontier / Claude tope | Disenar sistemas, trade-offs, reglas del ecosistema, planes multi-paso. | Tareas mecanicas repetitivas. |
| `implementador` | Sonnet / GPT fuerte de codigo / Codex | Cambios de codigo y docs con verificacion. | Decisiones estrategicas sin contexto. |
| `mecanico` | Haiku / mini / modelo barato | Listar, formatear, buscar texto, mover piezas simples, pruebas repetibles. | Arquitectura, investigacion, refactors complejos. |
| `verificador` | Modelo distinto al implementador + herramientas reales | Revisar fuentes, correr tests, detectar contradicciones. | Afirmar sin evidencia. |
| `memoria` | `.cerebro\memoria` + `cerebro_memoria.py` | Guardar hechos durables, recuperar contexto por significado. | Duplicar memoria privada o historiales. |
| `gui` | `gui-control-seguro` + computer-use | Pantalla, OCR, clics, apps Windows. | Acciones sin foco confirmado o sin usuario mirando. |
| `local-ia` | tu servidor LLM local/Qwen/recursos locales | Batch barato, privacidad, tareas largas no urgentes. | Trabajo que requiera web actual o mucha VRAM sin lock. |

## Politica de eleccion rapida

1. Si la pregunta depende de informacion actual o fuentes externas -> `buscador`.
2. Si requiere un informe profundo manual -> `buscador:Gemini Deep Research`; contrastar con OpenAI si la decision es importante.
3. Si requiere un informe profundo automatizable -> `buscador-api-profundo` (OpenAI Deep Research API) o `buscador-api-perplexity`.
4. Si solo hacen falta enlaces/citas rapidas -> `buscador:Perplexity`, `buscador-api-rapido` o web local.
5. Si es arquitectura del ecosistema -> `arquitecto`.
6. Si es edicion local verificable -> `implementador`.
7. Si es mecanico y reversible -> `mecanico`.
8. Antes de cerrar -> `verificador`.

## Integracion con el router por modelo

`17_ROUTER_POR_MODELO.md` sigue siendo el router operativo local. Esta red anade una capa semantica:

| Senal de tarea | Rol | Tier local sugerido | IA externa sugerida |
|---|---|---|---|
| "investiga", "mejor actual", "comparativa", "fuentes", "benchmark" | `buscador` / `buscador-api-*` | `opus` si no hay herramienta externa | Gemini Deep Research manual / OpenAI Deep Research API / Perplexity Sonar Deep Research / Gemini API grounding |
| "disena", "arquitectura", "protocolo", "trade-off" | `arquitecto` | `opus` | Ninguna salvo que falten fuentes. |
| "implementa", "integra", "corrige codigo" | `implementador` | `sonnet` u `opus` segun riesgo | Ninguna. |
| "lista", "formatea", "busca en archivos", "corre tests" | `mecanico` | `haiku` | Ninguna. |
| "verifica", "audita", "review", "contrasta" | `verificador` | `opus`/`sonnet` distinto al autor | OpenAI/Gemini si hay fuentes externas. |

## Prompts operativos

### Para `buscador:Gemini Deep Research`

```text
Actua como investigador del ecosistema. Investiga el estado actual de: <tema>.
Prioriza fuentes primarias, benchmarks recientes y documentacion oficial.
Devuelve: conclusion ejecutiva, tabla comparativa, fuentes con URL y fechas,
riesgos/limitaciones, y recomendacion concreta para integrarlo en ~\.cerebro.
No vendas una unica respuesta si hay incertidumbre; separa evidencia fuerte de inferencia.
```

### Para `buscador:OpenAI Deep Research`

```text
Haz una segunda opinion sobre este informe: <resumen o enlaces>.
Busca contradicciones, fuentes primarias omitidas, sesgos de benchmark y cambios recientes.
Devuelve solo diferencias relevantes, fuentes verificables y una recomendacion final.
```

### Para `buscador:Perplexity`

```text
Encuentra fuentes actuales y primarias sobre <tema>. Prioriza documentacion oficial,
papers, benchmarks y comunicados. Devuelve 5-10 enlaces con una frase de por que importan.
```

## Mantenimiento

- Revisar este mapa cuando cambien modelos principales, cuotas, benchmarks o herramientas de deep research.
- Si una IA externa se vuelve integrable por API/MCP local, crear adaptador especifico; hasta entonces,
  el rol `buscador` es una decision operativa, no un daemon autonomo.
- No guardar credenciales ni historiales privados de Gemini/OpenAI/Perplexity en `.cerebro`.
