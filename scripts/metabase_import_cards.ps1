$ErrorActionPreference = "Stop"

# ===== CONFIG =====
$MetabaseUrl = "http://localhost:3000"
$MbUser = "admin@example.com"        # CHANGE
$MbPass = "your_admin_password"      # CHANGE
$CollectionName = "Summary Dashboards"
$CardsPath = ".\metabase\seed\cards.ndjson"   # adjust if needed

# ===== 1) Login =====
$session = Invoke-RestMethod -Method Post -Uri "$MetabaseUrl/api/session" -ContentType "application/json" -Body (@{username=$MbUser; password=$MbPass} | ConvertTo-Json)
$token = $session.id; if (-not $token) { throw "Login failed." }
$headers = @{ "X-Metabase-Session" = $token }

# ===== 2) Find or create collection =====
$all = Invoke-RestMethod -Method Get -Uri "$MetabaseUrl/api/collection" -Headers $headers
$cid = ($all.data | Where-Object { $_.name -eq $CollectionName } | Select-Object -First 1).id
if (-not $cid) {
  $new = Invoke-RestMethod -Method Post -Uri "$MetabaseUrl/api/collection" -Headers $headers -ContentType "application/json" -Body (@{name=$CollectionName; description="Dashboards based on summary tables."; color="#509EE3"} | ConvertTo-Json)
  $cid = $new.id
}

# ===== 3) Determine Database ID =====
$databases = Invoke-RestMethod -Method Get -Uri "$MetabaseUrl/api/database" -Headers $headers
$db = $databases.data | Select-Object -First 1
if (-not $db) { throw "No databases found in Metabase. Add Postgres in Admin → Databases." }
$dbId = $db.id

# ===== 4) Create cards from NDJSON =====
if (-not (Test-Path $CardsPath)) { throw "Cannot find $CardsPath" }

Get-Content $CardsPath | ForEach-Object {
  if (-not $_.Trim()) { return }
  $obj = $_ | ConvertFrom-Json
  if ($obj.model -ne "card") { return }

  if ($obj.dataset_query -and $obj.dataset_query.database -and $obj.dataset_query.database -ne $dbId) {
    $obj.dataset_query.database = $dbId
  }

  $payload = @{
    name = $obj.name
    description = $obj.description
    display = $obj.display
    dataset_query = $obj.dataset_query
    collection_id = $cid
    visualization_settings = @{}   # REQUIRED by /api/card
    result_metadata = @()
    cache_ttl = $null
    archived = $false
  } | ConvertTo-Json -Depth 50

  Invoke-RestMethod -Method Post -Uri "$MetabaseUrl/api/card" -Headers $headers -ContentType "application/json" -Body $payload | Out-Null
}
"Cards created."
