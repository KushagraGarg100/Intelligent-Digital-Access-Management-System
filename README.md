# Intelligent Digital Asset Management System

Production-ready, modular **Digital Asset Management (DAM)** system with:

- React + Tailwind dashboard UI
- Flask REST API with JWT auth + RBAC (Admin/User)
- PostgreSQL for metadata (users, assets, tags, versions)
- Google Cloud Storage (GCS) for file storage (with local fallback for dev)
- AI pipeline using **PyTorch + Hugging Face Transformers** for embeddings and auto-tagging
- **FAISS** for vector similarity search (semantic search + duplicate detection)
- Local development setup

## Folder structure

```
intelligent-dam/
  frontend/   # React + Tailwind UI
  backend/    # Flask REST API
  ai_service/ # AI pipeline + FAISS vector store
  database/   # SQL schema + sample seed data
```

## Quick start (local)

### Prerequisites

- **Python** 3.11+
- **Node.js** 20+ (includes npm)
- **PostgreSQL** 16+

### 1) Database (PostgreSQL)

Create a database and user (example):

```sql
CREATE USER dam_user WITH PASSWORD 'dam_pass';
CREATE DATABASE dam OWNER dam_user;
GRANT ALL PRIVILEGES ON DATABASE dam TO dam_user;
```

Apply schema:

- Run `database/schemas/schema.sql` against the `dam` database.

### 2) Backend (Flask API)

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

Set environment variables (PowerShell example):

```powershell
$env:DATABASE_URL="postgresql+psycopg2://dam_user:dam_pass@localhost:5432/dam"
$env:CORS_ORIGINS="http://localhost:5173"
$env:LOCAL_STORAGE_DIR="..\data\storage"
$env:FAISS_INDEX_PATH="..\data\vector\faiss.index"
$env:FAISS_META_PATH="..\data\vector\faiss_meta.jsonl"
$env:GCS_BUCKET=""  # keep empty to use local filesystem storage
```

Run:

```bash
flask --app app.main run --port 8080 --debug
```

Optional demo users:

```bash
python scripts/seed_demo_data.py
```

### 3) Frontend (React)

Create `frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:8080/api
```

Run:

```bash
cd frontend
npm install
npm run dev
```

Open:

- Frontend: `http://localhost:5173`
- Backend health: `http://localhost:8080/api/health`

### Minimal ~50% (no React — API + AI + Postgres only)

For a **working half** without installing Node: use **`README-50-PERCENT.md`** and run from `backend/` (includes `run_backend.ps1`). `app/main.py` ensures `ai_service` is importable.

## Using Google Cloud Storage (production)

- **Set** `GCS_BUCKET` to your bucket name.
- **Set** `GOOGLE_APPLICATION_CREDENTIALS` to your service-account JSON path.

If `GCS_BUCKET` is empty, the backend uses **local storage** at `LOCAL_STORAGE_DIR`.

## Core flows

### Upload flow

1. User uploads file
2. Backend stores it in GCS (or local dev store)
3. Backend sends it to AI module
4. AI module:
   - extracts embedding (CLIP)
   - generates tags (image CLIP similarity; text zero-shot)
   - checks near-duplicate via FAISS
5. Store:
   - metadata + tags + versions in PostgreSQL
   - embedding in FAISS (persisted on disk)
6. Return asset details to frontend

### Search flow

1. User enters query
2. AI module embeds query (CLIP text)
3. Search FAISS index
4. Return matching assets ordered by similarity

## Sample data

See `database/sample_seed.sql` and `backend/scripts/seed_demo_data.py`.

## Notes

- All secrets/config are read from environment variables.
- GCS is used in production; local filesystem fallback is enabled for development.

