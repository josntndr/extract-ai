<div align="center">

# 📄 Extract AI

### AI-Powered Document Intelligence & OCR Platform

Upload invoices, resumes, contracts and scanned documents — Extract AI detects the
document type, pulls the text (native PDF parsing **or** OCR), and uses an LLM with
**structured outputs** to turn it into clean, validated JSON you can query and export.

[![CI](https://img.shields.io/badge/CI-GitHub_Actions-2088FF?logo=githubactions&logoColor=white)](.github/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)
![License](https://img.shields.io/badge/License-MIT-green)

</div>

---

## ✨ Overview

Extract AI is a full-stack document-intelligence platform built to enterprise
engineering standards. It demonstrates a complete, production-shaped pipeline:

```
Upload → Classify (native PDF / scanned / image) → Extract text (PyMuPDF · EasyOCR · Tesseract)
       → LLM structured extraction (GPT-4o) → Validate → Persist (PostgreSQL) → View / Export
```

The backend is fully implemented and **tested end-to-end**; the codebase is laid out
so the remaining feature areas (RAG chat, analytics, additional document types) plug
into the same architecture without rework.

## 🚀 Features

| Area | Status | Notes |
|------|--------|-------|
| JWT auth + refresh-token **rotation** | ✅ | Single-use refresh tokens, revocation, RBAC (user/admin) |
| Secure uploads | ✅ | Extension + MIME + **magic-byte** validation, 50MB cap |
| Document classification | ✅ | Native PDF vs scanned PDF vs image |
| Text extraction | ✅ | PyMuPDF text layer with **layout-aware reading order**; OCR fallback for scans/images |
| Table extraction | ✅ | **pdfplumber** structured tables → JSON + GitHub-flavoured Markdown |
| OCR engine | ✅ | EasyOCR primary, **Tesseract fallback** on low confidence |
| LLM providers | ✅ | **OpenAI (GPT-4o) _and_ Anthropic (Claude)** behind one provider-agnostic interface, with retries |
| Structured-output forcing | ✅ | Constrained to a Pydantic schema on both providers (`messages.parse` / Structured Outputs) |
| Prompt engineering | ✅ | **zero-shot / few-shot / chain-of-thought** strategies, swappable per request |
| Prompt-strategy evaluation | ✅ | **Benchmark harness** scoring field-accuracy across strategies on labelled data |
| Resume extraction | ✅ | Name, contact, skills, education, experience + missing-field detection |
| Background + **batch** processing | ✅ | Single upload returns immediately; `POST /documents/batch` (async) handles many files with **partial-failure** reporting |
| React dashboard | ✅ | Upload, live status polling, structured result viewer |
| Security middleware | ✅ | Hardened headers, in-memory rate limiting, CORS allowlist |
| Test suite + CI | ✅ | 24 Pytest cases (auth, pipeline, providers, tables, batch, eval), Ruff, Docker build, Trivy scan |
| Invoice / contract / medical / report types | 🛣️ | Schema registry ready — add a Pydantic model to enable |
| Vision-language extraction (GPT-4V / Claude vision) | 🛣️ | Planned for image-heavy documents |
| RAG document chat (FAISS + LangChain) | 🛣️ | Planned (architecture documented below) |
| Cloud OCR / storage (Textract · S3 / GCS) | 🛣️ | Local storage with S3-ready interface today |

> ✅ = implemented & tested · 🛣️ = on the roadmap, architecture in place

## 🏗️ Architecture

```
┌──────────────┐     HTTPS/JSON      ┌─────────────────────────────────────────┐
│   Frontend   │ ──────────────────▶ │                Backend (FastAPI)         │
│ React + Vite │ ◀────────────────── │                                          │
│  React Query │                     │  ┌────────┐  ┌──────────────┐  ┌──────┐  │
└──────────────┘                     │  │  Auth  │  │  Documents   │  │ ...  │  │
                                     │  └────────┘  └──────┬───────┘  └──────┘  │
                                     │                     │ background task    │
                                     │            ┌────────▼─────────┐          │
                                     │            │ Document Pipeline│          │
                                     │            └────────┬─────────┘          │
                                     │      ┌──────────────┼───────────────┐    │
                                     │      ▼              ▼               ▼    │
                                     │  TextExtractor   OCR Service   Extraction│
                                     │  (PyMuPDF)    (EasyOCR/Tess.)  (GPT-4o)   │
                                     └─────────────────────┬────────────────────┘
                                                           ▼
                                                  ┌─────────────────┐
                                                  │   PostgreSQL    │
                                                  └─────────────────┘
```

## 📁 Folder Structure

```
extract-ai/
├── backend/
│   ├── app/
│   │   ├── api/v1/        # auth, documents routers
│   │   ├── core/          # config, security (bcrypt/JWT), logging
│   │   ├── database/      # SQLAlchemy models, session
│   │   ├── middleware/    # security headers, rate limiting
│   │   ├── schemas/       # Pydantic request/response + extraction schemas
│   │   ├── services/      # storage, text_extractor, ocr, extraction, pipeline
│   │   └── utils/         # upload validation
│   ├── alembic/           # migrations
│   ├── tests/             # pytest suite
│   └── Dockerfile
├── frontend/              # React + TS + Vite + Tailwind
├── storage/               # uploads / processed / exports (runtime)
├── .github/workflows/     # CI
├── docker-compose.yml
└── .env.example
```

## ⚙️ Installation

### Option A — Docker (recommended)

```bash
cp .env.example .env          # then set OPENAI_API_KEY (or leave OPENAI_MOCK=true)
docker compose up --build
```

- Backend API → http://localhost:8000  (Swagger UI at `/docs`)
- Frontend    → http://localhost:5173
- Migrations run automatically on backend start.

### Option B — Local backend

```bash
cd backend
python3.12 -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export DATABASE_URL="postgresql+psycopg://extract:extract@localhost:5432/extract_ai"
alembic upgrade head
uvicorn app.main:app --reload
```

> **No LLM key?** Set `LLM_MOCK=true` (or `OPENAI_MOCK=true`) to run the whole
> pipeline with a deterministic stub extractor — ideal for local dev and CI.
> Choose the provider with `LLM_PROVIDER=openai|anthropic`.

### Prompt engineering & evaluation

Extraction prompts ship as swappable **strategies** — zero-shot, few-shot, and
chain-of-thought (`LLM_PROMPT_STRATEGY`, or per request). A benchmark harness
scores field-level accuracy of each strategy against labelled fixtures so prompt
changes are measured, not guessed:

```bash
cd backend
python -m scripts.eval_prompts                      # configured provider (or mock)
LLM_PROVIDER=anthropic python -m scripts.eval_prompts
```

Output is a ranked table (`strategy · provider · accuracy · correct/total`).

### Frontend (local)

```bash
cd frontend && npm install && npm run dev
```

## 🔌 API Documentation

Interactive OpenAPI docs are served at **`/docs`** (Swagger) and **`/redoc`**.

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Create account |
| POST | `/api/v1/auth/login` | Get access + refresh tokens |
| POST | `/api/v1/auth/refresh` | Rotate refresh token, issue new pair |
| POST | `/api/v1/auth/logout` | Revoke a refresh token |
| GET  | `/api/v1/auth/me` | Current user |
| POST | `/api/v1/documents` | Upload + (async) process a document |
| POST | `/api/v1/documents/batch` | Upload many documents (async, **207 partial-failure** report) |
| GET  | `/api/v1/documents` | List your documents (paginated) |
| GET  | `/api/v1/documents/{id}` | Document detail + structured extraction |
| POST | `/api/v1/documents/{id}/reprocess` | Re-run the pipeline |
| DELETE | `/api/v1/documents/{id}` | Delete document + file |

## 🔐 Security Features

- **Password hashing** with bcrypt (72-byte safe).
- **JWT** access tokens + **rotating, single-use refresh tokens** with DB-backed revocation (replay detection).
- **RBAC** (`user` / `admin`) via FastAPI dependencies.
- **Upload hardening**: extension + declared-MIME + **magic-byte** sniffing, size cap, per-owner storage isolation.
- **Ownership checks** on every document access (no IDOR).
- **Hardened response headers** (CSP, HSTS, X-Frame-Options, nosniff, …).
- **Rate limiting** middleware (Redis-ready interface).
- **CORS allowlist** from env.
- **Secrets via environment** only — nothing committed; `.env.example` documents every var.

## 🤖 RAG Pipeline (roadmap)

```
Document text → chunk → embed → FAISS index → retriever → GPT-4o → cited answer
```
The `Document.extracted_text` column already persists the corpus needed to build
this; the chat module will index per-document and stream answers with source
citations and conversation history.

## 🧪 Testing & CI/CD

```bash
cd backend && pytest            # 13 tests: auth flow, refresh rotation, upload
                                #           validation, pipeline, ownership isolation
```

GitHub Actions ([ci.yml](.github/workflows/ci.yml)) runs on every push/PR:
**Ruff lint → Pytest + coverage → Docker image builds → Trivy security scan.**

## 🗺️ Future Improvements

- RAG document chat with streaming + citations (LangChain + FAISS)
- Invoice / contract / medical / business-report extraction schemas
- Admin analytics dashboard (OCR success rate, volume, AI usage)
- Rich exports (CSV / Excel / Markdown)
- S3 storage backend + Celery/RQ worker queue for processing at scale

## 📜 License

MIT — see [LICENSE](LICENSE).
