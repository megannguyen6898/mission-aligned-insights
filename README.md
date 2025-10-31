# Mission Aligned Insights

End-to-end MVP that ingests `.xlsx` data, validates and ingests it into Postgres, generates Plotly dashboards, and produces AI-narrated PDF reports using an entirely local stack (FastAPI · Postgres · Redis/RQ · MinIO · Ollama · WeasyPrint · Nginx).

## Quick start

```sh
# 1. Copy environment template and customise if needed
cp .env.example .env

# 2. Build and launch the full stack
docker compose up -d --build

# 3. Pull the local model once (runs inside the Ollama container)
docker compose exec ollama ollama pull llama3.1:8b-instruct

# 4. Open the experience
# - API docs:       http://localhost:8080/docs
# - Frontend dev:   http://localhost:3000
# - Nginx gateway:  http://localhost:8081
```

To stop everything:

```sh
docker compose down
```

## Stack overview

- **FastAPI** backend (`backend/`) with SQLAlchemy + Alembic migrations.
- **Postgres**, **Redis**, **MinIO**, **Ollama**, **Nginx** orchestrated via Docker Compose.
- **RQ** workers (Redis queue) for validation and ingestion jobs.
- **Plotly** dashboards (server-side specs) rendered in React via `react-plotly.js`.
- **WeasyPrint** HTML → PDF pipeline storing artefacts in MinIO with presigned URLs.
- **Ollama** serving `llama3.1:8b-instruct` for on-device analytics copilot.

## Running backend & worker outside Compose (optional)

```sh
# prerequisites: Postgres, Redis, MinIO, Ollama already running
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080

# start RQ worker in another shell
python -m app.worker
```

## Frontend development

```sh
cd frontend
npm install        # run once (updates package-lock.json)
npm run dev        # Vite dev server on http://localhost:3000
```

## Manual acceptance checklist

1. Upload an `.xlsx` (≤10 MB) → Upload step shows **Complete**.
2. Validation auto-runs → schema + preview appear in Upload sidebar.
3. Click **Start ingest** → ingest step transitions to **Complete**.
4. On Dashboard, click **Generate dashboards** → KPI, category, and time-trend Plotly charts render.
5. Ask AI “Which regions are most efficient?” → response arrives as bullets in ≤12 s.
6. Click **Generate report** → download the narrated PDF (≥10 KB) with charts + appendix.
7. Hit `GET /healthz` → `database`, `redis`, `storage`, `ai` all return `true`.

## Testing

```sh
cd backend
pytest
```

The MVP test suite exercises presign + validation + ingestion flow (with mocked MinIO/Ollama), dashboard generation, AI responses, PDF report creation, and `/healthz` readiness.

## Notes

- All third-party services run locally; no paid APIs are required.
- MinIO buckets and objects are private—public access is granted only via presigned URLs.
- Nginx is configured with `client_max_body_size 30m` to support multi-megabyte uploads.
- To reset the workspace, remove the Postgres/MinIO Docker volumes: `docker compose down -v` (destructive).

See [SECURITY.md](SECURITY.md) for details on encryption, authentication, audit logging, and data retention.
