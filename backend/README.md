# ImpactView – Backend (FastAPI + Postgres)

**Dev API:** `http://localhost:8000/api/v1`  
**Docs:** `http://localhost:8000/docs`  
**Health:** `http://localhost:8000/health`

This backend serves the ImpactView app. It ships with a Docker Compose dev stack (Postgres + FastAPI) and a few hard-won tips to avoid the usual “why is this 500/404/422?” spiral.

---

## ⚡ TL;DR (Run it now)

```bash
# Start Docker services (from the repo root):

## Without MinIO:

docker compose up -d --build

## With MinIO (if you want uploads/storage):

docker compose -f docker-compose.yml -f minio.yaml up -d --build

## Check they’re up:

docker compose ps

## You want db, redis, backend, worker, metabase (and minio if included) all Up.
# Health pings:

curl -sS http://localhost:8000/health
curl -sS http://localhost:3000/api/health

# To debug:
docker compose logs --tail=100 backend

# Frontend (in VS Code Terminal 2):

cd frontend
npm install        # first time only
npm run dev
```

- Open http://localhost:5173
. Your vite.config.ts proxy lets the UI call /api/... without extra env.

- Metabase first-run (only the first time):

. Go to http://localhost:3000, create admin.

. Add the Postgres DB: Host db, Port 5432, User postgres, Password password, DB metabase.

. (Optional) Import your NDJSON files from the metabase/ folder.

- MinIO (only if you included it):

. Console: http://localhost:9001

. Login with MINIO_ROOT_USER / MINIO_ROOT_PASSWORD

. Create bucket impactview (matches S3_BUCKET=impactview in backend/.env).


---

## 📁 Structure (backend)

```
backend/
  app/
    main.py                 # FastAPI app (prefix /api/v1)
    api/                    # Routers: auth, users, data, reports, investors...
    core/security.py        # JWT helpers (access & refresh)
    database.py             # SQLAlchemy engine/session
    models/                 # SQLAlchemy models
    schemas/                # Pydantic schemas
  migrations/               # DB migrations
  Dockerfile
  docker-compose.yml        # Dev stack (db + backend)
  .env                      # ← you create this file
```

---

## 🔐 Create `.env`

Create `backend/.env`:

```dotenv
# --- Database (Docker dev) ---
DATABASE_URL=postgresql://postgres:password@db:5432/mega_x
DATABASE_SSL_MODE=prefer

# --- JWT/Auth (provide both naming styles to satisfy helpers) ---
JWT_SECRET=replace-with-long-random-hex
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

SECRET_KEY=replace-with-another-long-random-string
ALGORITHM=HS256
# optional: minutes for refresh if your code uses it
# REFRESH_TOKEN_EXPIRE_MINUTES=10080  # 7 days

# --- CORS (add your dev frontend origins) ---
ALLOWED_ORIGINS=http://localhost:8080,http://127.0.0.1:8080

# --- Optional integrations (placeholders ok) ---
OPENAI_API_KEY=sk-xxx
XERO_CLIENT_ID=...
XERO_CLIENT_SECRET=...
XERO_REDIRECT_URI=http://localhost:8000/api/v1/integrations/xero/callback
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/integrations/google/callback
```

> **Tip:** Use long random values for `JWT_SECRET` and `SECRET_KEY`.

---

## 🐳 Docker Compose (dev)

`backend/docker-compose.yml` (already set up for you):

- Loads **all** vars from `.env`
- Waits for Postgres to be **healthy**
- Mounts your code (`--reload` auto-restarts Uvicorn on file changes)

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: mega_x
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d mega_x || exit 1"]
      interval: 5s
      timeout: 5s
      retries: 15
    restart: unless-stopped

  backend:
    build:
      context: .
      dockerfile: Dockerfile
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    env_file:
      - .env
    environment:
      # Compat aliases some code expects (in addition to .env)
      ALGORITHM: ${JWT_ALGORITHM:-HS256}
      ACCESS_TOKEN_EXPIRE_MINUTES: ${JWT_ACCESS_TOKEN_EXPIRE_MINUTES:-60}
      REFRESH_TOKEN_EXPIRE_MINUTES: ${REFRESH_TOKEN_EXPIRE_MINUTES:-10080}
      PYTHONUNBUFFERED: "1"
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped

volumes:
  postgres_data:
```

> **Do I need to rebuild every time?**  
> No. Code changes hot-reload. Rebuild only if you change Python deps/Dockerfile:
> ```bash
> docker compose build backend --no-cache && docker compose up -d
> ```

---

## 🗄️ Migrations

```bash
# make sure the stack is up
docker compose up -d

# apply migrations
docker compose exec backend alembic upgrade head

# status (optional)
docker compose exec backend alembic current
docker compose exec backend alembic history | tail -n 20
```

---

## 🧪 Quick API tests

> Windows PowerShell users: use the **object → ConvertTo-Json** pattern (avoids quote/422 issues). Replace emails/passwords as needed.

**Register**
```powershell
$Email = "user$([int](Get-Random -Minimum 100000 -Maximum 999999))@example.com"
$Body  = @{ email=$Email; name="Test User"; password="Secret123!" } | ConvertTo-Json -Compress
curl.exe -i "http://localhost:8000/api/v1/auth/register" -H "content-type: application/json" --data $Body
```

**Login**
```powershell
$Body = @{ email=$Email; password="Secret123!" } | ConvertTo-Json -Compress
curl.exe -i "http://localhost:8000/api/v1/auth/login" -H "content-type: application/json" --data $Body
# expect 200 + { access_token, refresh_token }
```

**Me (authorized)**
```powershell
$Tokens = (curl.exe "http://localhost:8000/api/v1/auth/login" -H "content-type: application/json" --data $Body | Select-String -Pattern "^{.*}$").Line | ConvertFrom-Json
$Access = $Tokens.access_token
curl.exe -i "http://localhost:8000/api/v1/users/me" -H "authorization: Bearer $Access"
```

**Docs**
```
http://localhost:8000/docs
```

---

## 🎛️ Dev frontend tip (Vite)

If the React dev server runs at `http://localhost:8080`, add this proxy so the frontend can call `/api/...` and have Vite rewrite to `/api/v1/...`:

```ts
// frontend/vite.config.ts
proxy: {
  "/api": {
    target: process.env.VITE_PROXY_TARGET || "http://localhost:8000",
    changeOrigin: true,
    secure: false,
    rewrite: (p) => p.replace(/^\/api/, "/api/v1"),
  },
}
```

Then your axios client can be:
```ts
// src/lib/api.ts
import axios from "axios";
export const api = axios.create({ baseURL: "/api" });
```

---

## 🔎 Logs & handy commands

```bash
# tail backend logs
docker compose logs backend --tail 100 --follow

# shell into backend container
docker compose exec backend bash

# quick JWT self-test inside container (catches missing envs)
docker compose exec backend python - <<'PY'
from app.core.security import create_access_token, create_refresh_token
print("access OK:", bool(create_access_token({"sub":"1"})))
print("refresh OK:", bool(create_refresh_token({"sub":"1"})))
PY

# list db tables
docker compose exec db psql -U postgres -d mega_x -c "\dt"
```

---

## 🧯 Troubleshooting

**500 on `/auth/login`**
- **JWT envs not loaded:** ensure `.env` exists and is referenced by `env_file`. Verify inside the container:
  ```bash
  docker compose exec backend python - <<'PY'
  import os
  print("JWT_SECRET set:", bool(os.getenv("JWT_SECRET")))
  print("SECRET_KEY set:", bool(os.getenv("SECRET_KEY")))
  print("ALGORITHM:", os.getenv("ALGORITHM"))
  print("ACCESS_TOKEN_EXPIRE_MINUTES:", os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
  PY
  ```
- **Audit log insert fails (table/enum/NOT NULL):** run migrations; if it still errors, temporarily wrap the audit insert in `try/except` so login succeeds, then fix the schema via migration.

**404s during dev**
- Backend routes live under `/api/v1/...`.
- Frontend should call `/api/...` (Vite will rewrite to `/api/v1/...`).  
  If backend logs show `/api/v1/api/...`, your proxy `target` incorrectly includes `/api/v1`.

**422 “JSON decode error” on curl (Windows)**
- Use the PowerShell examples above (avoid manual quoting).

**CORS**
- Ensure `ALLOWED_ORIGINS` includes your dev frontend (`http://localhost:8080`).

---

## ♻️ Reset (optional)

```bash
# stop services
docker compose down

# nuke db volume (destroys all data)
docker volume rm backend_postgres_data

# fresh start
docker compose up -d
docker compose exec backend alembic upgrade head
```

---

## 📚 Key endpoints

- `POST /api/v1/auth/register` → `{ email, name, password, organization_name? }`
- `POST /api/v1/auth/login` → `{ email, password }` → `{ access_token, refresh_token, token_type }`
- `POST /api/v1/auth/refresh` (Bearer refresh token)
- `GET  /api/v1/users/me` (Bearer access token)
- Data/Reports/Investors → see `/docs`

---

Happy shipping! If anything misbehaves, run:

```bash
docker compose logs backend --tail 200
```

and read the last traceback—it’ll tell you exactly which knob to turn.
