# Architecture Overview

```
┌─────────────┐      presigned PUT       ┌──────────────┐
│   Frontend  │ ───────────────────────▶ │    MinIO     │
│ (React/Vite)│                          │  (S3 API)    │
└─────┬───────┘                          └─────┬────────┘
      │ 1. POST /uploads/presign                │
      │ 2. POST /uploads/:id/complete           │
      │ 3. Poll /uploads/:id/workflow <─────────┘
      │            │
      │            ▼
      │      ┌──────────┐    enqueue jobs     ┌──────────┐
      │      │ FastAPI  │ ───────────────────▶│  Redis   │
      │      │  (API)   │                     │   RQ     │
      │      └────┬─────┘                     └────┬─────┘
      │           │  validate/ingest jobs           │
      │           ▼                                 │
      │      ┌──────────┐         read/write        │
      │      │ RQ Worker│ ─────────────────────────┘
      │      │ (Python) │
      │      └────┬─────┘
      │           │
      │        pandas → schema + preview
      │           │              ▲
      │           ▼              │ SQL
      │      ┌──────────┐        │
      │      │ Postgres │ ◀──────┘
      │      └──────────┘
      │           │
      │           ▼
      │   Plotly specs / AI prompts / WeasyPrint PDFs
      │           │
      ▼           ▼
  Dashboards   AI Q&A + PDF reports (via Ollama + MinIO)
```

## Data flow

1. **Upload** – Frontend requests a presigned PUT URL from FastAPI, uploads the Excel file directly to MinIO, and confirms completion. FastAPI persists an `uploads` record and a `workflow` step.
2. **Validation** – An RQ worker downloads the workbook from MinIO, infers schema/preview with pandas, creates a `datasets` row, and marks the validation workflow step succeeded (or failed with structured errors).
3. **Ingestion** – When triggered, the worker normalises the workbook into a canonical Postgres table and updates workflow state + dataset metadata.
4. **Dashboards** – FastAPI derives Plotly JSON specs from dataset metadata and/or table data. React consumes these specs via `react-plotly.js`.
5. **AI Copilot** – FastAPI summarises schema + aggregates and calls the Ollama `llama3.1:8b-instruct` model (local HTTP API). Responses are stored as `ai_events` for auditing.
6. **Reporting** – A WeasyPrint HTML template renders KPI tables, Plotly charts (converted to PNG via Kaleido), AI narratives, and schema appendix. The PDF is stored in MinIO and a presigned GET URL is returned.
7. **Edge** – Nginx proxies `localhost:8081` → FastAPI (`8080`), bumping `client_max_body_size` to 30 MB for uploads.

## Key modules

- `backend/app/routes/mvp/` – REST endpoints for uploads, workflows, datasets, dashboards, AI, reports, and health.
- `backend/app/jobs.py` – RQ job definitions (`validate_upload`, `ingest_dataset`).
- `backend/app/services/` – Validation heuristics, ingestion helpers, dashboard generation, AI integration, and report rendering.
- `backend/app/storage/presign.py` – MinIO client helpers for presigned PUT/GET URLs and bucket CORS management.
- `frontend/src/api/mvp.ts` – Typed API client for MVP endpoints (presign, workflows, dashboards, AI, reports).
- `frontend/src/pages/Upload.tsx` – Upload flow with workflow polling + ingest trigger.
- `frontend/src/pages/Dashboard.tsx` – Plotly chart rendering, AI Q&A, and PDF generation controls.

## Environments & services

| Service   | Port | Purpose                                   |
|-----------|------|-------------------------------------------|
| FastAPI   | 8080 | Core API (`/uploads`, `/dashboards`, etc.) |
| Nginx     | 8081 | User-facing gateway → FastAPI             |
| MinIO     | 9000 | S3-compatible object store                |
| MinIO UI  | 9001 | Optional console                          |
| Postgres  | 5432 | Application database                      |
| Redis     | 6379 | RQ job queue                              |
| Ollama    | 11434| Local LLM inference                       |

All services are defined in `docker-compose.yml` and run with zero external cost.
