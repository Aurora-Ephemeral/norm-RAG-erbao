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
- **`app/crud/`** — `BaseCrud[ModelType, CreateSchema, UpdateSchema]` is a generic CRUD base; `ChunkCrud` adds `vector_search()` and `fulltext_search()` with metadata pre-filtering and configurable `limit`
- **`app/domain/chat/`** — LangChain chain (`chain.py`), prompt templates (`prompt.py`), LLM factory (`llm.py`), query schemas (`schemas.py`)
- **`app/domain/retrieval/`** — Pluggable retrieval pipeline layer:
  - `pipeline.py` — `RetrievalPipeline` ABC: defines `search(query) → List[RagChunk]`
  - `vector.py` — `VectorPipeline`: embedding + pgvector cosine search
  - `fulltext.py` — `FulltextPipeline`: PostgreSQL tsvector + ts_rank (BM25-style)
  - `hybrid.py` — `HybridPipeline`: runs both in parallel, applies RRF, then reranks
  - `fusion.py` — `reciprocal_rank_fusion()`: pure algorithm, no framework dependency
  - `rerank.py` — `rerank()`: converts RagChunk↔Document, calls DashScope gte-rerank, falls back to RRF order on failure
  - `retriever.py` — `RAGRetriever(BaseRetriever)`: thin LangChain adapter, pipeline → `List[Document]`
- **`app/domain/history/`** — Pluggable conversation history layer:
  - `provider.py` — `HistoryProvider` ABC: defines `get_messages(conversation_id) → List[BaseMessage]`
  - `slidingwindow.py` — `SlidingWindowProvider`: fetches last `window_size` turns, reverses to chronological order, converts to LangChain messages
  - `factory.py` — `create_history_provider(db, strategy)`: reads `settings.history_strategy`, instantiates the correct provider; extend here for user-level config
- **`app/domain/conversation/`** — Conversation entity (ORM + Pydantic schemas); `RagConversation` has `messageList` relationship with `selectinload` for detail queries
- **`app/domain/message/`** — Message entity; `MessageRoleEnum` (user/assistant); `MessageCrud.get_last_n_messages()` for history window queries
- **`app/domain/common/`** — Shared utilities: `utils.py` (`count_tokens()` — Chinese/English character-based token estimation); `schemas.py` (`FormattedDatetime` — Annotated type for uniform datetime serialization)
- **`app/core/config.py`** — Pydantic Settings; key env vars: `LLM_MODEL`, `TEMPERATURE`, `DATABASE_URL`, `VECTOR_SEARCH_TOP_K`, `FULLTEXT_SEARCH_TOP_K`, `HYBRID_CANDIDATE_K`, `RERANK_TOP_K`, `RERANKER_MODEL`, `HISTORY_STRATEGY`, `LAST_N_MESSAGES`
- **`app/core/model.py`** — DashScope model factories: `return_rerank_model()`. Intended to consolidate LLM / embedding / reranker factories here over time.
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
- Document processing pipeline: PDF parsing → chunking → embedding → pgvector storage, fully working
- Query preprocessing: translation + standard number + part type extraction + coreference resolution via single LLM call
- Hybrid retrieval: `HybridPipeline` wired into `ChatService` — vector + fulltext + RRF + DashScope reranker, all complete
- `fts_vector` generated column and GIN index added to `rag_chunk` table (migration applied manually)
- Conversation history: `rag_conversation` / `rag_message` tables, CRUD, `SlidingWindowProvider`, factory, injected into both preprocessing and RAG chains
- Document API: all endpoints return 501 Not Implemented
- Frontend: layout scaffold in place; page content is mostly placeholder

## Retrieval Design Notes

The retrieval layer uses a two-layer pattern to separate pipeline logic from LangChain:
- All pipelines implement `RetrievalPipeline.search(query) → List[RagChunk]` — pure Python, no LangChain
- `RAGRetriever(BaseRetriever)` is a thin adapter: calls `pipeline.search()`, converts `RagChunk → Document`
- `ChatService` selects the pipeline and passes it to `RAGRetriever`; `chain.py` is never touched when switching strategies

Candidate funnel: `hybrid_candidate_k` (default 30) candidates per path → RRF fusion → reranker → `rerank_top_k` (default 8) to LLM.

## History Layer Design Notes

The history layer mirrors the retrieval layer's two-layer pattern:
- `HistoryProvider` ABC defines `get_messages(conversation_id) → List[BaseMessage]` — pure Python, returns LangChain-ready messages
- `create_history_provider(db, strategy)` factory in `factory.py` reads `settings.history_strategy` and instantiates the correct provider; adding a new strategy only requires a new class + one `elif` in the factory
- `ChatService.__init__` calls the factory once; `ask_stream` only calls `get_messages()` — service layer is unaware of which strategy is active
- History is injected into **both** chains via `MessagesPlaceholder(optional=True)`: preprocessing chain uses it for coreference resolution; RAG chain uses it for contextual follow-up answers
- Messages are persisted after each turn: user message saved before streaming, assistant message saved after streaming completes (empty response on error is never written)
