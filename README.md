# Qwen-RAG — Intelligent Technical Standards Q&A System

An enterprise-grade RAG (Retrieval-Augmented Generation) system built on Qwen LLM + LangChain + pgvector, designed for intelligent retrieval and Q&A over automotive industry technical standard documents.

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | Qwen3-Max (Alibaba Cloud DashScope) |
| RAG Framework | LangChain + LangChain Community |
| Vector Database | PostgreSQL + pgvector |
| Backend Framework | FastAPI + SQLAlchemy |
| Async Tasks | Celery + Redis |
| Object Storage | MinIO (S3-compatible) |
| Frontend Framework | React 19 + Redux Toolkit + TDesign UI + Vite |

---

## Backend Four-Layer Architecture

```
┌─────────────────────────────────────┐
│         API Routes Layer            │  FastAPI routers — receive requests, return responses
│   app/api/routes/                   │  chat / knowledgebase / document / file
├─────────────────────────────────────┤
│         Service Layer               │  Business logic, parameter validation, exception handling
│   app/service/                      │  ChatService / FileService / KnowledgeBaseService
├─────────────────────────────────────┤
│         CRUD Layer                  │  Database operations, generic BaseCrud base class
│   app/crud/                         │  ChunkCrud / DocumentCrud / FileCrud
├─────────────────────────────────────┤
│         Domain Layer                │  ORM models + Pydantic schemas
│   app/domain/                       │  knowledge_base / document / file / chunk / chat
└─────────────────────────────────────┘
```

All dependencies are injected via FastAPI `Depends`. The `db Session` lifecycle is managed by the framework and released automatically at the end of each request.

---

## Knowledge Base Design

The system is organized around four core concepts:

```
KnowledgeBase
    └── Document              ← Links a KB to a file; carries business-level attributes
            └── RagChunk      ← The smallest unit for vector retrieval

RawFile                       ← Deduplicated file storage; one file can be linked to
                                documents across multiple knowledge bases
```

**Key design decisions:**

- **File and Document decoupling**: `RawFile` is deduplicated by MD5 — uploading the same file multiple times stores only one copy. `Document` records the business semantics of a file within a specific knowledge base (standard number, part type, version, etc.)
- **Status belongs to Document**: Processing status (PROCESSING / ACTIVE / FAILED) lives on `Document`, not `RawFile`, because chunking and embedding are document-level concerns, not file-level concerns
- **Per-KB configuration**: Each knowledge base stores its own `retrieval_strategy` (VECTOR / HYBRID / KEYWORD), `embedding_model`, `top_k`, and `chunk_size`
- **Chunks carry structural metadata**: `section_title`, `section_path`, `page_no`, and `metadata_json` preserve the original document hierarchy and enable source citation

---

## Document Processing Pipeline

After a file is uploaded, it is processed through a two-stage Celery async pipeline:

```
Upload PDF
    │
    ▼
[MinIO storage] → RawFile persisted to DB
    │
    ▼
processing_document_task (Celery)
    ├── Parse PDF (structured extraction: paragraphs / tables / heading hierarchy)
    ├── Smart chunking (section-boundary splits, preserving section_path / rows / footnotes)
    └── Bulk-insert chunks to DB → triggers ↓

embed_document_task (Celery)
    ├── Query unembedded chunks (idempotent: WHERE embedding IS NULL)
    ├── Batch-call DashScope text-embedding-v3 (batch size 10, 5 parallel threads)
    └── Write vectors to pgvector Vector(1024) column
```

---

## RAG Q&A Pipeline

```
User question (Chinese / English / German)
    │
    ▼
① History Loading
    └── HistoryProvider.get_messages(conversation_id) → last N turns (sliding window)
    │
    ▼
② Query Preprocessing (single LLM call, history injected)
    ├── Coreference resolution (resolve pronouns / references using history)
    ├── Translate resolved query to English
    ├── Extract standard numbers (TL 240 / DIN EN ISO 9227 / etc.)
    └── Identify part types (sheet_metal / bolt / surface_protection / coating)
    │
    ▼
③ Hybrid Retrieval (parallel)
    ├── Vector search:     pgvector cosine similarity  → top hybrid_candidate_k
    └── Full-text search:  PostgreSQL tsvector / BM25  → top hybrid_candidate_k
    │
    ▼
④ RRF Fusion (Reciprocal Rank Fusion)
    └── Merge and deduplicate both result lists by rank position (k=60)
    │
    ▼
⑤ Rerank
    └── DashScope gte-rerank cross-encoder → top rerank_top_k
    │
    ▼
⑥ Prompt Assembly (history injected)
    ├── System prompt (role definition + citation rules)
    ├── Conversation history (last N turns for follow-up context)
    ├── Retrieved chunks (with section / page / type annotations)
    └── User question
    │
    ▼
⑦ LLM Streaming Generation (Qwen3-Max)
    │
    ▼
SSE pushed to frontend → messages persisted to DB (user + assistant)
```

### Retrieval Layer Architecture

The retrieval layer is decoupled from the LangChain chain via a two-layer design:

```
RetrievalPipeline (ABC)          Pure Python — no LangChain dependency
    ├── VectorPipeline           embed_query → ChunkCrud.vector_search
    ├── FulltextPipeline         ChunkCrud.fulltext_search (tsvector + ts_rank)
    └── HybridPipeline           VectorPipeline + FulltextPipeline → RRF → Reranker

RAGRetriever (BaseRetriever)     Thin LangChain adapter — pipeline → List[Document]
```

This separation means pipeline logic is independently testable and new retrieval strategies can be added without touching the chain or service layer.

### History Layer Architecture

The history layer uses the same two-layer + factory pattern as the retrieval layer:

```
HistoryProvider (ABC)            Pure Python — returns List[BaseMessage] (LangChain-ready)
    └── SlidingWindowProvider    last N turns from DB, reversed to chronological order

create_history_provider(db, strategy)   Factory — reads settings.history_strategy
```

History is injected at two points via `MessagesPlaceholder(optional=True)`:
- **Preprocessing chain**: enables coreference resolution ("it" / "该标准" → concrete entity)
- **RAG chain**: enables contextual follow-up answers

Switching strategies (e.g. future `TokenBudgetProvider`) requires only a config change — `ChatService` is unaware of which provider is active.

---

## Project Structure

```
project/
├── service/                        # Backend (FastAPI)
│   ├── main.py
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── chat.py         # POST /chat/ask (SSE streaming Q&A)
│   │   │   │   ├── knowledgebase.py
│   │   │   │   ├── document.py
│   │   │   │   └── file.py
│   │   │   └── dependencies.py     # FastAPI dependency injection factories
│   │   ├── service/
│   │   │   ├── ChatService.py
│   │   │   ├── FileService.py
│   │   │   └── KnowledgeBaseService.py
│   │   ├── crud/
│   │   │   ├── BaseCrud.py         # Generic CRUD base class
│   │   │   ├── ChunkCrud.py        # bulk_update_embeddings / get_unembedded
│   │   │   ├── DocumentCrud.py
│   │   │   └── FileCrud.py
│   │   ├── domain/
│   │   │   ├── chat/
│   │   │   │   ├── llm.py          # ChatTongyi factory
│   │   │   │   ├── prompt.py       # Prompt templates
│   │   │   │   ├── chain.py        # LangChain LCEL chain builders
│   │   │   │   ├── retriever.py    # VectorRetriever (legacy, kept for reference)
│   │   │   │   └── schemas.py      # QueryProcessing Pydantic model
│   │   │   ├── retrieval/          # Retrieval pipeline layer
│   │   │   │   ├── pipeline.py     # RetrievalPipeline ABC
│   │   │   │   ├── vector.py       # VectorPipeline (embedding + cosine search)
│   │   │   │   ├── fulltext.py     # FulltextPipeline (tsvector + BM25)
│   │   │   │   ├── hybrid.py       # HybridPipeline (vector + fulltext + RRF + rerank)
│   │   │   │   ├── fusion.py       # reciprocal_rank_fusion()
│   │   │   │   ├── rerank.py       # rerank() — calls DashScope, maps back to RagChunk
│   │   │   │   └── retriever.py    # RAGRetriever — thin LangChain BaseRetriever adapter
│   │   │   ├── chunk/
│   │   │   │   └── model.py        # RagChunk, Vector(1024), fts_vector (generated)
│   │   │   ├── document/
│   │   │   │   └── model.py        # Document, DocStatusEnum
│   │   │   ├── file/
│   │   │   │   ├── parse.py        # Structured PDF parsing
│   │   │   │   ├── split_chunks.py # Smart chunking
│   │   │   │   ├── embedding.py    # Batch vectorization
│   │   │   │   └── tasks.py        # Celery tasks
│   │   │   └── knowledge_base/
│   │   │       └── model.py        # KnowledgeBase, RetrievalStrategyEnum
│   │   └── core/
│   │       ├── config.py           # Pydantic Settings, reads .env
│   │       ├── celery.py           # Celery config, autodiscover_tasks
│   │       └── minIO.py
│   │   └── core/
│   │       ├── config.py           # Pydantic Settings, reads .env
│   │       ├── model.py            # DashScope model factories (LLM / Embedding / Reranker)
│   │       ├── embedding.py        # embed_query / embed_batch
│   │       ├── celery.py           # Celery config, autodiscover_tasks
│   │       └── minIO.py
│   └── .env.development            # Local env vars (not committed)
│
└── web/                            # Frontend (React 19 + Vite)
    └── src/
        ├── pages/
        │   └── chat/               # Chat main page + sub-components
        │       ├── index.tsx        # Layout: sidebar (history) + main panel
        │       ├── type.ts
        │       └── components/
        │           ├── WelcomePage.tsx  # Typewriter intro + mode selector
        │           └── MessageList.tsx  # SSE streaming message list (Markdown)
        ├── api/                    # Axios-based API functions (conversation)
        ├── store/                  # Redux Toolkit (chatSlice)
        ├── components/Layout/      # Global header + sidebar
        ├── locales/                # i18n language packs (zh / en), split by feature module
        │   ├── zh/  (system.tsx, chat.tsx)
        │   └── en/  (system.tsx, chat.tsx)
        ├── router.tsx              # React Router v7: / → /chat, /chat/:id?
        ├── utils/request.ts        # Axios instance with unified error handling
        └── style/                  # Global CSS + TDesign overrides
```

---

## Development Status

### Completed

- [x] Knowledge base CRUD (create / read / update / delete)
- [x] File upload (MinIO storage + MD5 deduplication)
- [x] Structured PDF parsing (paragraphs / tables / heading hierarchy)
- [x] Smart chunking (section-boundary splits, structural metadata preserved)
- [x] Vectorization pipeline (two-stage Celery tasks + pgvector storage)
- [x] Query preprocessing (translation + standard number extraction + part type identification, single LLM call)
- [x] SSE streaming response framework
- [x] Hybrid retrieval: vector search + full-text search (tsvector/BM25) + RRF fusion
- [x] Reranker: DashScope gte-rerank cross-encoder, with RRF-order fallback
- [x] Retrieval pipeline layer: pluggable strategy design (VectorPipeline / FulltextPipeline / HybridPipeline)
- [x] Conversation history: `rag_conversation` / `rag_message` tables, `SlidingWindowProvider`, factory pattern, injected into preprocessing + RAG chains; coreference resolution in preprocessing prompt
- [x] **Frontend — Chat page**: conversation list sidebar, conversation create / switch / history load, SSE streaming message rendering (Markdown), AbortController mid-stream stop
- [x] **Frontend — Welcome page**: typewriter animation intro, simple / complex mode selector
- [x] **Frontend — i18n**: zh / en language packs split by feature module (`system`, `chat`), all UI text externalised via `react-i18next`
- [x] **Frontend — Global layout**: header with language switcher, shared sidebar shell

### In Progress / Next Up

- [ ] **Cross-document references**: secondary retrieval for standards referenced within retrieved chunks
- [ ] **Token budget history strategy**: `TokenBudgetProvider` — prune history by token count (Chinese/English estimation in `common/utils.py` already in place)

### Planned

- [ ] **User and permission management**: registration/login, KB visibility (PRIVATE / TEAM / PUBLIC), RBAC
- [ ] **Frontend — Knowledge base management**: list, create, delete, per-KB config UI
- [ ] **Frontend — Document management**: file upload, processing status polling, chunk preview
- [ ] **Frontend — Conversation delete**: delete button in sidebar is rendered but not yet wired to API
- [ ] **Document versioning**: `is_latest` field already reserved; supports multiple versions of the same standard
- [ ] **Evaluation framework**: RAG quality metrics (recall rate, answer relevance)
- [ ] **Observability**: full-chain tracing (LangSmith or custom), structured logging with request_id, Prometheus + Grafana metrics (QPS / P99 latency / error rate)
- [ ] **Token usage tracking**: record input/output token counts per request for cost monitoring and quota control

---

## Local Setup

### Required Services

```bash
# PostgreSQL (with pgvector extension), Redis, MinIO
# Recommended: start all via Docker Compose
```

### Backend

```bash
cd service
pip install -r requirements.txt

# Configure environment variables
cp .env.development.example .env.development
# Fill in DATABASE_URL / DASHSCOPE_API_KEY / MINIO_* / REDIS_URL

# Start FastAPI
python main.py

# Start Celery Worker
celery -A app.core.celery.celery_app worker --loglevel=info
```

### Frontend

```bash
cd web
npm install
npm run dev
```

---

## Environment Variables

| Variable | Description | Example |
|---|---|---|
| `LLM_MODEL` | Qwen model name | `qwen3-max` |
| `TEMPERATURE` | Generation temperature | `0` |
| `LLM_MAX_TOKENS` | Maximum output tokens | `2048` |
| `LLM_ENABLE_THINKING` | Enable Qwen3 thinking chain | `false` |
| `EMBEDDING_MODEL` | Embedding model | `text-embedding-v3` |
| `RERANKER_MODEL` | Reranker model | `gte-rerank` |
| `VECTOR_SEARCH_TOP_K` | Candidates per vector search | `10` |
| `FULLTEXT_SEARCH_TOP_K` | Candidates per full-text search | `10` |
| `HYBRID_CANDIDATE_K` | Candidates per path in hybrid mode | `30` |
| `RERANK_TOP_K` | Final results returned after reranking | `8` |
| `HISTORY_STRATEGY` | History provider strategy | `sliding_window` |
| `LAST_N_MESSAGES` | Number of turns kept in sliding window | `10` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+psycopg://...` |
| `REDIS_URL` | Redis connection string | `redis://:password@host:6379/0` |
| `MINIO_ENDPOINT` | MinIO address | `localhost:9000` |
| `DASHSCOPE_API_KEY` | Alibaba Cloud DashScope API key | — |
