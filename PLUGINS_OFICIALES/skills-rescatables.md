# Skills rescatables de los plugins oficiales — verdict + lista bajo demanda

> Revisión 2026-06-19 de las **2,563 skills** dentro de los 191 plugins oficiales.
> **Veredicto: NADA que rescatar/copiar en bloque ni ahora.** Razones abajo. Esto es un
> índice para cosechar **bajo demanda** el día que un proyecto lo necesite. Relacionado:
> [[reference-enametoolong-causa-ram]], catálogo en [`catalogo-completo.md`](catalogo-completo.md).

## Por qué no se rescata nada ahora
- **98 de 142 plugins con skills dependen de su MCP** → la skill sin el MCP es documentación, no capacidad (posthog 434, azure 202, stripe, mongodb, slack…). Copiar el texto no da función.
- **~80% son de productos que no usas** (AWS, SAP, Oracle, Azure, Zscaler, Snowflake…).
- **Lo provider-agnostic ya lo tienes** en tus skills propias (espejo `~/.claude/skills` + `~/.agents/skills`): `accessibility`, `performance`, `core-web-vitals`, `seo` (ya cubre GEO/AEO), `best-practices`, `web-quality-audit`, `ecommerce`, `marketing-digital`, `diseno`, `video-editing`, `hyperframes`, `superpowers`, `ia-aplicada`…
- **Lo Shopify** (`liquid-theme-a11y`, `liquid-theme-standards`, `shopify-liquid-themes`) ya está **activo** vía el plugin `liquid-skills`.
- Copiar = duplicar + inflar contexto/selección + romper el espejo Claude↔Codex + superficie de ataque (tu investigación en `REGISTRO_SKILLS_EXTERNAS.md`: *Under the Hood of SKILL.md*).

## Cosechar BAJO DEMANDA (solo si aparece la necesidad)
| Necesidad futura | Qué activar/cosechar | Dónde |
|---|---|---|
| Trabajo profundo de a11y/estándares en temas Shopify (tu-tienda) | `liquid-theme-a11y`, `liquid-theme-standards`, `shopify-liquid-themes` | **ya activas** (plugin `liquid-skills`) |
| Empaquetar tus skills `.cerebro` como plugin instalable | `plugin-dev` (comandos, no SKILL.md) | `/plugin install plugin-dev@claude-plugins-official` |
| Exponer `.cerebro` (memoria/tareas) como servidor MCP | `mcp-server-dev` | idem |
| Auditar un repo y sugerir hooks/skills/MCP al arrancar proyecto (regla #6) | `claude-code-setup` | idem |
| Escalar `cerebro_semantica` a un vector DB real | `qdrant-skills` (27) o `zilliz` (41) — conocimiento sin MCP | cache `claude-plugins-official\{qdrant-skills,zilliz}` |
| Adoptar Redis/ClickHouse/Cosmos | `redis-development`, `clickhouse-best-practices`, `azure-cosmos-db-assistant` (73 reglas) | idem (best-practices puras, sí distilables) |
| Verificación de frontend con navegador | `playwright` (ya tienes flujo propio de screenshots) | on-demand |

## Regla
Cuando una de esas necesidades sea real: activar el plugin un rato **o** cosechar **esa** skill concreta, verificarla (regla #7: SKILL.md + scripts + permisos), unificar sin duplicar, y registrar. Nunca en bloque.
