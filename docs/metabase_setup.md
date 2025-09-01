# Secure Metabase Static Embedding (Single Dashboard)

## Prereqs

- Metabase at http://localhost:3000 (persists to Postgres).

- Backend (FastAPI) at http://localhost:8000; Frontend (Vite/React).

- Cards NDJSON: metabase/seed/cards.ndjson.

## Metabase env

- Generate a 32-byte hex for app encryption (PowerShell):

```
$b = New-Object byte[] 32; (New-Object System.Security.Cryptography.RNGCryptoServiceProvider).GetBytes($b)
($b | ForEach-Object ToString X2) -join '' | ForEach-Object ToLower
```

- Set:

MB_SITE_URL=http://localhost:3000
MB_ENCRYPTION_SECRET_KEY=<64-hex>


- Restart Metabase: docker compose up -d --build

## Import cards (Windows)

- Run scripts/metabase_import_cards.ps1 to create the “Summary Dashboards” collection and add the 5 cards:

```
powershell -ExecutionPolicy Bypass -File .\scripts\metabase_import_cards.ps1
```

- Create & publish dashboard

1. In Metabase → + New → Dashboard, add the 5 cards → Save.

2. Share → Embed → Static embedding:

- Set org_id = Locked (required in JWT).

- (Optional) Lock or make editable project_id.

- Publish. Copy the Embedding Secret Key (64-hex).

## Backend env

MB_SITE_URL=http://localhost:3000
MB_EMBED_SECRET_KEY=<64-hex from Static embedding screen>
MB_DASHBOARD_DEFAULT_DASHBOARD_ID=<numeric id of your dashboard>


## Backend code

- backend/app/metabase/jwt.py provides create_signed_url(...).

- backend/app/routes/metabase.py exposes:

   - GET /api/dashboards → [ { id, name } ] (now one default).

   - POST /api/metabase/signed → { url } (server injects locked org_id from user token).

## Frontend

- Page frontend/src/pages/Dashboard.tsx calls:

   - listDashboards() → select dashboard.

   - getSignedDashboard(id) → renders returned url in <iframe>.

## Troubleshooting

- Blank iframe → dashboard not Published for Static embedding OR a Locked param (e.g., org_id) missing from JWT.

- “Invalid signature” → the secret must be decoded from hex to raw bytes before signing (binascii.unhexlify).

- Wrong scope → check your SQL template tags ({{org_id}}, {{project_id}}) and Embed dialog locks.

## Licensing

- Free/OSS embeds show “Powered by Metabase”; do not remove branding without a paid plan.