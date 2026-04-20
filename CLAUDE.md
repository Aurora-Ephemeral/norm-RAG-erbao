# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Qwen-RAG is a full-stack intelligent document Q&A system using Retrieval-Augmented Generation. Users upload documents to knowledge bases and ask questions; the backend uses the Qwen LLM (via Alibaba DashScope) with LangChain for RAG pipelines.

## Development Commands

### Backend (FastAPI)

```bash
cd service
# Run development server (port 3000, auto-reload)
python main.py

# Run tests
pytest test/

# Run a single test
pytest test/service/test_intent_router.py
```

The backend reads environment config based on `APP_ENV` env var (defaults to `development`), loading the corresponding `.env.<APP_ENV>` file.

### Frontend (React/Vite)

```bash
cd web
npm install
npm run dev      # dev server
npm run build    # production build
npm run lint     # ESLint
```

## Architecture

**Stack:** FastAPI + SQLAlchemy + PostgreSQL (backend) / React 19 + Redux Toolkit + TDesign UI + Vite (frontend)

### Backend Layers (`service/app/`)

```
API Routes (app/api/routes/)
    ↓
Service Layer (app/service/)
    ↓
CRUD Layer (app/crud/)
    ↓
SQLAlchemy ORM Models (app/domain/)
    ↓
PostgreSQL
```

- **`app/api/routes/`** — FastAPI routers: `chat.py` (SSE streaming Q&A), `knowledgebase.py` (KB CRUD), `document.py` (stub/TODO)
- **`app/service/`** — Business logic; validates, maps schemas, raises HTTP exceptions
- **`app/crud/`** — `BaseCrud[ModelType, CreateSchema, UpdateSchema]` is a generic CRUD base; domain-specific cruds inherit from it
- **`app/domain/`** — SQLAlchemy ORM models and Pydantic schemas, organized by domain (e.g., `knowledge_base/model.py`, `knowledge_base/schemas.py`)
- **`app/rag/`** — LangChain pipeline (`chain.py`) + prompt templates (`prompt.py`). Uses `ChatTongyi` (Qwen). **Note:** retriever is not yet wired up — context is currently a placeholder.
- **`app/util/query.py`** — `IntentRouter`: classifies user queries into categories (板材/螺栓/表面防护/涂装) using keyword rules + DashScope embedding similarity
- **`app/util/https.py`** — SSE streaming helpers
- **`app/core/config.py`** — Pydantic Settings; key env vars: `LLM_MODEL`, `TEMPERATURE`, `DATABASE_URL`
- **`app/db/Postgresql.py`** — SQLAlchemy engine + `get_db()` dependency for session injection

### Standard API Response Shape

All endpoints return:
```json
{ "code": 200, "message": "success", "data": null, "success": true }
```
Defined in `app/domain/http/schemas.py` as `HTTPResponse`.

### Frontend Structure (`web/src/`)

- `router.tsx` — React Router v7 with a shared `Layout` (header + sidebar)
- `store/` — Redux Toolkit slices
- `utils/request.ts` — Axios instance with auth token injection and error handling
- `locales/` — i18next translations (en/zh)
- Path alias `@/` maps to `web/src/`

## Current Implementation Status

- Knowledge Base CRUD: fully implemented end-to-end
- Chat/RAG: intent routing works; RAG chain built but retriever is TODO (dummy context)
- Document API: all endpoints return 501 Not Implemented
- Frontend: layout scaffold in place; page content is mostly placeholder
