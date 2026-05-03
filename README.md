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
① Query Preprocessing (single LLM call)
    ├── Translate to English (all documents are in English)
    ├── Extract standard numbers (PV1209 / DIN EN ISO 9227 / etc.)
    └── Identify part types (sheet_metal / bolt / surface_protection / coating)
    │
    ▼
② Hybrid Retrieval  ⚠️ In progress
    ├── Vector search: pgvector cosine similarity (semantic matching)
    ├── Full-text search: PostgreSQL tsvector (exact standard number matching)
    └── RRF merge (Reciprocal Rank Fusion)
    │
    ▼
③ Rerank  ⚠️ In progress
    └── Re-rank top-20 → top-5 (DashScope Rerank model)
    │
    ▼
④ Prompt Assembly  ⚠️ In progress
    ├── System prompt (role definition + numeric citation rules)
    ├── Retrieved chunks (with source annotations)
    └── User question (English)
    │
    ▼
⑤ LLM Streaming Generation (Qwen3-Max)
    │
    ▼
SSE pushed to frontend
```

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
│   │   │   │   ├── llm.py          # ChatTongyi factory, reads settings
│   │   │   │   ├── prompt.py       # Prompt templates
│   │   │   │   ├── chain.py        # LangChain LCEL chain builders
│   │   │   │   └── schemas.py      # QueryProcessing Pydantic model
│   │   │   ├── chunk/
│   │   │   │   └── model.py        # RagChunk, Vector(1024) field
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
│   └── .env.development            # Local env vars (not committed)
│
└── web/                            # Frontend (React + Vite)  ⚠️ In progress
    └── src/
        ├── pages/                  # Pages (placeholders)
        ├── store/                  # Redux Toolkit
        ├── components/Layout/      # Top bar + sidebar
        └── utils/request.ts        # Axios instance with token injection
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

### In Progress

- [ ] **Hybrid retrieval**: pgvector vector search + PostgreSQL full-text search (tsvector) + RRF fusion
- [ ] **Cross-document references**: secondary retrieval for standards referenced within retrieved chunks
- [ ] **Rerank**: re-ranking model to compress retrieval results
- [ ] **RAG Chain**: full Q&A chain with context (`build_rag_chain`)
- [ ] **Conversation history**: `conversation` / `message` tables, sliding-window history injection

### Planned

- [ ] **User and permission management**: registration/login, KB visibility (PRIVATE / TEAM / PUBLIC), RBAC
- [ ] **Frontend pages**: knowledge base management, document list, Q&A interface, history view
- [ ] **Document versioning**: `is_latest` field already reserved; supports multiple versions of the same standard
- [ ] **Evaluation framework**: RAG quality metrics (recall rate, answer relevance)

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
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+psycopg://...` |
| `REDIS_URL` | Redis connection string | `redis://:password@host:6379/0` |
| `MINIO_ENDPOINT` | MinIO address | `localhost:9000` |
| `DASHSCOPE_API_KEY` | Alibaba Cloud DashScope API key | — |
