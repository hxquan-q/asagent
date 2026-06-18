# asagent

A general-purpose **agent platform** over PostgreSQL, built on Python (FastAPI + LangChain/LangGraph) + Vue 3. Point it at a business database (e.g. a WMS), configure an agent, and ask questions in natural language — it queries the data and answers in rich, multi-format output (tables, charts, architecture/flow diagrams, SVG, HTML, images, files). Supports the **Anthropic Agent Skills** standard (upload `.zip` skills, hot-loaded, sandboxed), multi-vendor LLMs (OpenAI / DeepSeek / Tongyi / Ollama / any OpenAI-compatible), and an external API for direct programmatic Q&A.

## Architecture

```
frontend (Vue3 + Element Plus) ──HTTP/SSE──▶ backend (FastAPI + LangGraph)
                                              ├─ LLM factory (multi-vendor)
                                              ├─ ReAct agent runtime (streaming)
                                              ├─ tools: NL2SQL(read-only) / visualize / render / skills
                                              ├─ skills subsystem (Agent Skills) + sandbox (subprocess/docker)
                                              └─ metadata DB (SQLModel)  ◀──▶ business DB (Postgres, read-only)
```

- **Two databases**: a platform metadata DB (default SQLite for easy self-host; Postgres supported) and one-or-more read-only business datasources configured at runtime.
- **Output = typed content blocks** (`text`/`table`/`chart`/`diagram`/`svg`/`html`/`image`/`file`/`data`). Skills can dictate the output form.

## Quick start (dev)

Backend (conda env `as`):
```bash
cd backend
cp .env.example .env          # then edit SECRET_KEY / JWT_SECRET / ADMIN_PASSWORD
python -m uvicorn app.main:app --reload --port 8000
```
Frontend:
```bash
cd frontend
npm install && npm run dev    # http://localhost:5173 (proxies /api -> :8000)
```
Login at the console (default `admin` / the `ADMIN_PASSWORD` you set), add an LLM config, add a datasource, create an agent, and chat.

## Deploy (Docker, port 8899)

```bash
cd deploy
SECRET_KEY=$(python -c "import secrets;print(secrets.token_urlsafe(48))") \
JWT_SECRET=$(python -c "import secrets;print(secrets.token_urlsafe(48))") \
ADMIN_PASSWORD=change-me \
docker compose up -d --build
# -> http://<host>:8899  (nginx serves UI, proxies /api to backend, postgres for metadata)
```

## External API

Create an API key in the console (`API Keys` → the full key is shown once), then:
```bash
curl -N -X POST http://<host>:8899/api/v1/chat/sync \
  -H "X-API-Key: ask_xxx" -H "Content-Type: application/json" \
  -d '{"agent_id":1,"message":"库存最高的10个SKU"}'
# streaming (SSE): use POST /api/v1/chat with the same header
```

## Skills (Agent Skills standard)

A skill is a directory (upload as `.zip`) with `SKILL.md` (YAML frontmatter `name` + `description`) plus optional `scripts/` / `references/` / `assets/`. The agent loads them via progressive disclosure and runs scripts in a sandbox.

```
my-skill.zip
└── my-skill/
    ├── SKILL.md
    └── scripts/do_thing.py
```

## Security

- SQL is read-only (sqlglot whitelist + dangerous-function denylist; no multi-statement).
- Skill scripts run sandboxed (subprocess with rlimits/timeout, or a `--network=none --read-only` Docker container).
- HTML/SVG blocks are sanitised server-side (nh3) in addition to client-side DOMPurify.
- Secrets (LLM keys, datasource passwords) encrypted at rest; API keys hashed; bootstrap admin explicit.
- Outbound HTTP tool is SSRF-guarded (private/loopback hosts blocked) and off by default.
- The app refuses to boot with default/weak secrets in production.

## Project layout

```
backend/   FastAPI + LangGraph app (app/{core,llm,agent,tools,skills,sandbox,datasources,content,api,models})
frontend/  Vue3 + Element Plus console
deploy/    docker-compose, Dockerfiles, nginx.conf
data/      runtime: skills/, files/, asagent.db (gitignored)
```

## Status (v1)

Done: multi-vendor LLM factory, LangGraph ReAct runtime with SSE streaming, NL2SQL query tool, multi-format block output, Agent Skills (upload/hot-load/sandbox), JWT+API-key auth, Vue console, Docker deploy.

Later: multi-agent graph orchestration, RBAC/multi-tenant, chart SSR export, conversation vector memory (pgvector).
