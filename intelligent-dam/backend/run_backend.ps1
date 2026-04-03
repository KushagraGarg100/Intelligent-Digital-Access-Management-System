# Minimal run: Flask API only. Requires PostgreSQL and venv with requirements installed.
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$root = Split-Path -Parent $PSScriptRoot
if (-not $env:DATABASE_URL) {
    $env:DATABASE_URL = "postgresql+psycopg2://dam_user:dam_pass@localhost:5432/dam"
}
if (-not $env:LOCAL_STORAGE_DIR) { $env:LOCAL_STORAGE_DIR = Join-Path $root "data\storage" }
if (-not $env:FAISS_INDEX_PATH) { $env:FAISS_INDEX_PATH = Join-Path $root "data\vector\faiss.index" }
if (-not $env:FAISS_META_PATH) { $env:FAISS_META_PATH = Join-Path $root "data\vector\faiss_meta.jsonl" }
if (-not $env:CORS_ORIGINS) { $env:CORS_ORIGINS = "http://localhost:8080" }
if ($null -eq $env:GCS_BUCKET) { $env:GCS_BUCKET = "" }

Write-Host "Backend: http://localhost:8080/api/health"
Write-Host "DATABASE_URL: $($env:DATABASE_URL)"
flask --app app.main run --port 8080 --debug
