# Plugins oficiales de Claude Code — catálogo para reactivar cuando se necesiten

> **Marketplace:** `claude-plugins-official` (oficial de Anthropic, Apache-2.0, riesgo bajo).
> **191 plugins disponibles** para esta máquina. Funcionalidad detallada de cada uno en
> [`catalogo-completo.md`](catalogo-completo.md) (descripción real extraída del manifiesto).
> Investigado/generado 2026-06-18. Relacionado: [[reference_plugins_trimmed]], [[reference-codegraph-evaluado]].

## ⚠️ Antes de activar (RAM)
Tienes solo **~1 GB de RAM libre** y el cliente recorta a **~21 plugins activos** a propósito
([[reference_plugins_trimmed]]). **NO actives en bloque.** Cada plugin con MCP/LSP arranca un
proceso `node` que come RAM. Regla: activa **uno por proyecto y por necesidad puntual**, mira el
**Context cost** que muestra `/plugin` antes de confirmar, y desactívalo al terminar.

## Cómo activar / desactivar
```
/plugin install <nombre>@claude-plugins-official     # activar
/plugin uninstall <nombre>@claude-plugins-official   # desactivar
/reload-plugins                                       # aplicar cambios
```
Si el marketplace no aparece: `/plugin marketplace add anthropics/claude-plugins-official`.
Los `*-lsp` requieren además el language-server en el PATH (p.ej. `npm i -g pyright` para pyright-lsp).

---

## Índice por categoría
> ✅ = ya activo en tus 21 · 🐏 = arranca proceso pesado (LSP/MCP), cuidado con la RAM.

### 🧰 Claude Code — desarrollo y workflow
`claude-code-setup` · `claude-md-management`✅ · `plugin-dev` · `skill-creator`✅ · `superpowers`✅ ·
`hookify`✅ · `feature-dev`✅ · `code-review`✅ · `code-simplifier`✅ · `commit-commands`✅ ·
`pr-review-toolkit` · `session-report`✅ · `frontend-design`✅ · `code-modernization` ·
`agent-sdk-dev` · `mcp-server-dev` · `mcp-apps` · `mcp-tunnels`🐏 · `ralph-loop` · `playground` ·
`math-olympiad` · `remember`✅ · `explanatory-output-style`✅ · `learning-output-style`✅

### 🔎 Inteligencia/búsqueda de código y revisión IA
`serena`🐏 · `lumen`🐏 · `sourcegraph`🐏 · `greptile` · `coderabbit` · `codspeed`

### 🔤 Language Servers (LSP) 🐏 — activar SOLO por proyecto que use ese lenguaje
`typescript-lsp` (TS/JS, tu-tienda/tu-proyecto-web) · `pyright-lsp` (Python, tu-proyecto-aprendizaje/tu-proyecto-agente/.cerebro) ·
`liquid-lsp` (Shopify Liquid) · `rust-analyzer-lsp` · `gopls-lsp` (Go) · `clangd-lsp` (C/C++) ·
`csharp-lsp` · `jdtls-lsp` (Java) · `kotlin-lsp` · `php-lsp` · `ruby-lsp` · `lua-lsp` · `swift-lsp`

### 🛡️ Seguridad y supply-chain
`security-guidance`✅ · `semgrep` · `sonarqube` · `aikido` · `42crunch-api-security-testing` ·
`nightvision` · `crowdstrike-falcon-foundry` · `sonatype-guide` · `ai-plugins` (Endor Labs) ·
`vanta` · `zscaler`

### 🌐 Navegador / testing E2E
`playwright`🐏 · `chrome-devtools-mcp`🐏

### ⚙️ Web frameworks / deploy
`vercel` · `netlify-skills` · `cloudflare` · `railway` · `expo` · `supabase` · `neon` · `convex` ·
`appwrite` · `valtown` · `laravel-boost` · `quarkus-agent` · `wordpress-com` · `sanity`

### ☁️ AWS
`aws-core` · `aws-agents` · `aws-amplify` · `aws-data-analytics` · `aws-dev-toolkit` ·
`aws-serverless` · `aws-startup-advisor` · `databases-on-aws` · `deploy-on-aws` ·
`migration-to-aws` · `sagemaker-ai` · `amazon-location-service`

### ☁️ Google Cloud / Azure / Microsoft
`azure` · `azure-cosmos-db-assistant` · `microsoft-docs` · `dataverse` · `bigquery-data-analytics` ·
`dataproc` · `looker` · `alloydb` · `alloydb-omni` · `cloud-sql-mysql` · `cloud-sql-postgresql` ·
`cloud-sql-sqlserver` · `spanner` · `firebase` · `firestore-native` · `data-agent-kit-starter-pack`

### 🗄️ Bases de datos y vectoriales
`mongodb` · `redis-development` · `clickhouse` · `clickhouse-best-practices` · `duckdb-skills` ·
`oracledb` · `snowflake-cortex-code` · `pinecone` · `qdrant-skills` · `zilliz` · `postman`

### 📊 Datos / ML / IA
`data-engineering` · `astronomer-data-agents` · `datahub-skills` · `knowledge-catalog` ·
`datarobot-agent-skills` · `dominodatalab` · `fiftyone` · `huggingface-skills` · `nvidia-skills` ·
`pydantic-ai` · `atomic-agents` · `togetherai-skills` · `pigment` · `oracle-ai-data-platform-workbench-spark-connectors`

### 📈 Observabilidad / analítica / incidentes
`sentry` · `sentry-cli` · `logfire` · `dash0` · `posthog` · `amplitude` · `pagerduty` · `rootly`

### 🔧 CI/CD / DevOps / repos
`github` · `gitlab` · `buildkite` · `teamcity-cli` · `terraform`

### 💬 CRM · productividad · comunicación
`notion` · `asana` · `linear` · `atlassian` · `airtable` · `slack` · `discord` · `telegram` ·
`imessage` · `apollo` · `apollo-skills` · `hunter` · `lusha` · `exa` · `firecrawl` ·
`youdotcom-agent-skills` · `circleback` · `forge-skills`

### 💳 Pagos / fintech / auth
`stripe` · `mercadopago` · `airwallex` · `sumup` · `revenuecat` · `rc` · `circle-skills` ·
`workos` · `auth0` · `duende-skills`

### 🎨 Marketing · media · generación IA
`runway-api` · `spotify-ads-api` · `save-to-spotify` · `windsor-ai` · `outputai` · `mapbox` ·
`figma` · `adobe-for-creativity` · `hyperframes`✅ · `mintlify` · `resend`

### 🛒 E-commerce / Shopify
`shopify`✅ · `shopify-ai-toolkit`✅ · `liquid-skills`✅ · `liquid-lsp`🐏

### 🏢 SAP / enterprise / Qt
`cds-mcp` · `sap-cds-mcp` · `sap-fiori-mcp-server` · `sap-mdk-server` · `ui5` ·
`ui5-typescript-conversion` · `qt-development-skills`

### 📚 Docs / utilidades
`context7`✅ · `microsoft-docs` · `legalzoom` · `fakechat`

---

## Más relevantes para TU ecosistema (cuando los necesites)
| Plugin | Por qué a ti |
|---|---|
| `security-guidance` ✅ | Ya activo — auditoría de seguridad en cada edit (refuerza regla #7). |
| `pyright-lsp` 🐏 | Tipos Python en vivo para `.cerebro`/tu-proyecto-agente/tu-proyecto-aprendizaje (activar por proyecto; `npm i -g pyright`). |
| `typescript-lsp` 🐏 | Para tu-tienda / tu-proyecto-web cuando toques TS/JS. |
| `plugin-dev` | Empaquetar tus skills cross-proyecto como plugin instalable. |
| `mcp-server-dev` | Exponer `.cerebro` (memoria/tareas) como servidor MCP. |
| `serena` / `lumen` 🐏 | Alternativas locales a CodeGraph (búsqueda semántica de código por LSP/AST+embeddings). |
| `playwright` 🐏 | Verificación visual de tu-tienda (ya usas screenshots Playwright propios). |

> Funcionalidad exacta de los 191: ver [`catalogo-completo.md`](catalogo-completo.md).
