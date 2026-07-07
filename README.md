# Portfolio Diligence Copilot 🧭

> An AI-native diligence & portfolio-monitoring workbench for private-equity-backed businesses.
> Upload a company's data room, run a durable multi-agent diligence pass, and get risk-flagged, source-cited findings — with portfolio-level KPIs on top.

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-async-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-App_Router-000000?logo=nextdotjs&logoColor=white)](https://nextjs.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector-4169E1?logo=postgresql&logoColor=white)](https://postgresql.org)
[![Temporal](https://img.shields.io/badge/Temporal-Durable_Workflows-000000?logo=temporal&logoColor=white)](https://temporal.io)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-4B0082)](https://langchain-ai.github.io/langgraph/)
[![MCP](https://img.shields.io/badge/MCP-Server-6E56CF)](https://modelcontextprotocol.io)
[![dbt](https://img.shields.io/badge/dbt-Analytics-FF694B?logo=dbt&logoColor=white)](https://getdbt.com)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docker.com)
[![CI](https://img.shields.io/badge/CI-GitHub_Actions-2088FF?logo=githubactions&logoColor=white)](https://github.com/features/actions)

---

## The Problem This Solves

Diligence on a target company is a slog. An analyst is handed a data room — financials, contracts, board decks, customer lists — and expected to surface the risks *fast*: revenue concentration, covenant exposure, churn signals, auto-renewing liabilities buried on page 40 of an MSA. Today that means someone reads for days, and the findings live in a one-off deck that's stale the moment it's delivered.

**Portfolio Diligence Copilot turns a data room into a queryable, monitored asset.** A user uploads a company's documents, hits **Run Diligence**, and watches a durable multi-agent workflow ingest, retrieve, analyze, and flag — producing source-cited findings graded by severity. Those findings roll up into a portfolio-level view so a fund can monitor every company it owns from one place, not one deck at a time.

Standard RAG answers a question. This system **runs a process** — a long, resumable, multi-step diligence pass — and treats its output as durable, structured data.

---

## What It Does

- **Data-room ingestion** — upload financials, contracts, board decks; the system chunks, embeds, and stores them with Postgres as the system of record and `pgvector` for retrieval.
- **Durable diligence runs** — a multi-step diligence pass orchestrated by **Temporal**, so a run survives failures, retries individual steps, and reports live progress instead of dying halfway through a 40-document batch.
- **Multi-agent analysis** — a **LangGraph** graph coordinates specialist agents (retrieval, financial, risk, synthesis, eval) rather than one monolithic prompt.
- **Source-cited findings** — every finding is graded (`low` / `medium` / `high`), categorized (`financial` / `legal` / `operational` / `market`), and linked back to the document it came from.
- **Portfolio analytics** — a **dbt** layer over the operational Postgres builds KPI marts so findings and companies roll up into fund-level views.
- **Composable via MCP** — the agent graph is exposed as an **MCP server**, so external tools (a Slack bot, another internal app) can query the portfolio without touching the internals.
- **Full frontend** — a **Next.js** app with a portfolio dashboard, document upload, streaming chat over the data room, and a live run-progress view.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                         FRONTEND  (Next.js)                            │
│   Portfolio dashboard · Upload · Streaming chat · Live run progress    │
└───────────────────────────────┬──────────────────────────────────────┘
                                 │  REST / SSE
┌───────────────────────────────▼──────────────────────────────────────┐
│                          API  (FastAPI, async)                         │
│   /companies · /documents · /runs · /query · /findings · MCP endpoint  │
└───────┬───────────────────────────┬───────────────────────────┬───────┘
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────┐        ┌──────────────────────┐      ┌────────────────┐
│  PostgreSQL   │        │   Temporal Workflow   │      │   MCP Server   │
│  system of    │◄──────►│   (durable diligence  │      │  wraps agent   │
│  record +     │        │        run)           │      │  graph as an   │
│  pgvector     │        │                       │      │  external tool │
└───────┬───────┘        │  ┌─────────────────┐  │      └────────────────┘
        │                │  │  LangGraph agents │  │
        │                │  │  Router →         │  │
        │                │  │  Retrieval →      │  │
        │                │  │  Financial →      │  │
        │                │  │  Risk →           │  │
        │                │  │  Synthesis →      │  │
        │                │  │  Eval             │  │
        │                │  └─────────────────┘  │
        │                └──────────────────────┘
        ▼
┌───────────────┐
│      dbt      │   staging → marts:  portfolio KPIs, findings rollups,
│  analytics    │                     severity distribution, coverage
└───────────────┘
```

---

## Tech Stack

| Layer | Technology | Role |
|---|---|---|
| Frontend | Next.js (App Router), TypeScript | Dashboard, upload, streaming chat, live workflow progress |
| API | FastAPI (async), Pydantic | REST + SSE endpoints, dependency injection |
| Primary store | PostgreSQL 16 | System of record — companies, documents, runs, findings |
| Vector search | pgvector | Chunk embeddings + similarity retrieval |
| Orchestration | Temporal | Durable, resumable multi-step diligence runs |
| Agents | LangGraph | Multi-agent coordination, tool use, state, eval |
| Interop | MCP server | Exposes the agent graph as an enterprise tool |
| Analytics | dbt | Portfolio KPI marts over operational Postgres |
| Infra | Docker Compose | Local Postgres + Temporal + Temporal UI |
| CI/CD | GitHub Actions | Lint, test, build; Azure Container Apps deploy path |

---

## The Diligence Workflow

A diligence run is a **Temporal workflow** — durable and resumable — that drives a **LangGraph** agent graph. Each agent is a discrete step so failures retry in isolation and progress is observable end-to-end:

1. **Router** — classifies the run's scope and routes documents by type.
2. **Retrieval Agent** — hybrid retrieval over the company's chunks (vector + metadata filters).
3. **Financial Agent** — surfaces revenue concentration, margin trends, covenant/liquidity signals.
4. **Risk Agent** — flags legal/operational exposure (auto-renewals, change-of-control clauses, key-person risk).
5. **Synthesis Agent** — writes graded, source-cited findings into Postgres.
6. **Eval Agent** — scores findings for groundedness and drops unsupported claims.

Because it's Temporal, the run's state lives in the workflow — so a crash mid-analysis resumes from the last completed activity rather than restarting from zero.

---

## Project Structure

```
portfolio-diligence-copilot/
├── docker-compose.yml          # Postgres (pgvector) + Temporal + Temporal UI
├── .env.example
├── requirements.txt
├── db/
│   └── init.sql                # core schema (system of record)
├── app/
│   ├── config.py               # typed settings
│   ├── db.py                   # async SQLAlchemy engine + session
│   ├── main.py                 # FastAPI entrypoint
│   ├── models/                 # SQLAlchemy models
│   ├── api/                    # routers: companies, documents, runs, query
│   ├── ingestion/              # chunking + embedding
│   ├── retrieval/              # pgvector retrieval
│   ├── agents/                 # LangGraph graph + agent nodes
│   ├── workflows/              # Temporal workflows + activities + worker
│   └── mcp/                    # MCP server exposing the agent graph
├── analytics/                  # dbt project (staging + marts)
├── frontend/                   # Next.js app
├── tests/
└── .github/workflows/          # CI + Azure deploy path
```

---

## Getting Started

**Prerequisites:** Docker, Python 3.11+, Node 18+ (for the frontend).

```bash
# 1. Start infrastructure (Postgres + Temporal + Temporal UI)
docker compose up -d

# 2. Python environment
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env

# 3. Run the API
uvicorn app.main:app --reload
```

**Verify:**

| URL | Expect |
|---|---|
| http://localhost:8000/health | `{"status":"ok","db":true}` |
| http://localhost:8000/docs | FastAPI Swagger UI |
| http://localhost:8080 | Temporal Web UI |

Frontend (once you reach that phase):

```bash
cd frontend
npm install
npm run dev        # http://localhost:3000
```

---

## Roadmap

- [x] **Phase 1 — Foundation:** repo, Docker infra, FastAPI skeleton, schema
- [ ] **Phase 2 — Data layer:** SQLAlchemy models, company/document CRUD, file upload
- [ ] **Phase 3 — Ingestion + RAG:** chunking, embeddings, pgvector retrieval, `/query`
- [ ] **Phase 4 — Agents:** LangGraph graph (Router → Retrieval → Financial → Risk → Synthesis → Eval)
- [ ] **Phase 5 — Temporal:** wrap the diligence run as a durable workflow
- [ ] **Phase 6 — MCP server:** expose the agent graph as an enterprise tool
- [ ] **Phase 7 — dbt:** portfolio KPI marts over Postgres
- [ ] **Phase 8 — Next.js:** dashboard, upload, streaming chat, live run progress
- [ ] **Phase 9 — CI/CD + Azure:** GitHub Actions, Dockerfiles, Azure Container Apps path

---

## Design Notes

- **Postgres as the system of record, not just a vector sidecar.** Companies, documents, runs, and findings are relational data; retrieval embeddings live alongside them via `pgvector`. One store, one source of truth.
- **Temporal over a plain task queue.** A diligence run is long, multi-step, and failure-prone — the honest case for durable execution and per-activity retries rather than fire-and-forget jobs.
- **Agents as discrete graph nodes.** Splitting analysis into specialist LangGraph nodes makes each step observable, testable, and independently retryable — and keeps an eval step in the loop to gate unsupported findings.
- **MCP for composability.** Wrapping the graph as an MCP server means the same capability powers the UI *and* any external tool, without duplicating logic.

---

## Status

Portfolio / reference implementation, built end-to-end to demonstrate a full-stack AI + data system: durable multi-agent workflows, a real frontend, Postgres-backed application state, and an analytics engineering layer. Structured for an Azure Container Apps deploy; runs locally via Docker Compose.

## License

MIT
