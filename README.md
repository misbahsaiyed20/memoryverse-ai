# MemoryVerse AI

**Your Personal Career Intelligence Engine.**

This is Sprint 1 — Module 1: project foundation only. No auth, uploads, database
tables, AI, or business logic yet. Just a working frontend, a working backend
with a `/health` route, and DB connection config wired up (no models).

---

## Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- PostgreSQL 14+ (only needed once you actually connect — Sprint 1's backend
  will boot without it since no models/queries exist yet)

---

## Frontend setup

```bash
cd frontend
cp .env.example .env.local   # already done, but re-run if you delete it
npm install
npm run dev
```

Runs at **http://localhost:3000**.

Stack: Next.js 15 (App Router) · TypeScript · Tailwind CSS · shadcn/ui
(CLI configured via `components.json`, no components added yet).

---

## Backend setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env           # edit DATABASE_URL to match your local Postgres
uvicorn app.main:app --reload --port 8000
```

Runs at **http://localhost:8000**.
Interactive API docs: **http://localhost:8000/docs**
Health check: **http://localhost:8000/api/v1/health**

Stack: FastAPI · SQLAlchemy (engine/session only, no models yet) ·
Pydantic Settings for env config.

---

## Project structure

```
memoryverse-ai/
├── frontend/            # Next.js 15 app
│   ├── app/              # App Router pages, layout, global styles
│   ├── components/       # shadcn/ui components go here (empty for now)
│   ├── lib/utils.ts      # cn() helper for shadcn
│   └── components.json   # shadcn/ui config
└── backend/              # FastAPI app
    ├── app/
    │   ├── main.py             # FastAPI app instance, CORS, router registration
    │   ├── core/config.py      # Pydantic Settings — all env vars load here
    │   ├── db/session.py       # SQLAlchemy engine/session (no models yet)
    │   ├── api/v1/health.py    # /api/v1/health router
    │   ├── models/             # empty — DB models land here (Sprint 2+)
    │   ├── schemas/            # empty — Pydantic request/response schemas
    │   ├── services/
    │   │   └── storage/base.py # StorageService interface (abstract, no impl yet)
    │   └── utils/               # empty — shared helpers
    └── requirements.txt
```

---

## Verifying the setup

- Frontend: visit `http://localhost:3000` — should show the MemoryVerse AI
  landing text.
- Backend: `curl http://localhost:8000/api/v1/health` — should return
  `{"status":"healthy"}`. (Note: the unversioned `/health` path from Sprint 1
  no longer exists — it moved to `/api/v1/health` as part of introducing API
  versioning.)

---

## Sprint 2 — Auth setup

Before `npm run dev` / `uvicorn` will actually let you sign in, you need a
Firebase project:

1. Create a project at [console.firebase.google.com](https://console.firebase.google.com)
2. **Authentication → Sign-in method → Google** → enable it
3. **Project Settings → General → Your apps → Web app** → copy the config
   values into `frontend/.env.local` (`NEXT_PUBLIC_FIREBASE_*`)
4. **Project Settings → Service Accounts → Generate new private key** →
   save the downloaded JSON as `backend/firebase-service-account.json`
   (already gitignored)

Without step 4, the backend still boots and `/health` still works — auth
routes return a clear `503` instead of crashing, so you can develop other
things without Firebase configured.

**New backend route:** `POST /api/v1/auth/login` — verifies the Firebase
ID token sent in `Authorization: Bearer <token>` and creates the user row
in Postgres on first login.

**New protected route:** `GET /api/v1/dashboard/stats` — requires the same
Bearer token on every call (not just at login), returns hardcoded
`{documents: 0, skills: 0, projects: 0, certificates: 0}` for now.

**New pages:** `/` (landing), `/login` (custom Google sign-in), `/dashboard`
(protected — redirects to `/login` if not signed in).

## Sprint 3 — Document uploads

**New backend routes** (all require `Authorization: Bearer <token>`, all
scoped to the authenticated user — accessing someone else's document
returns `404`, never `403`):
- `POST /api/v1/documents/upload` — multipart file upload
- `GET /api/v1/documents` — list your documents
- `GET /api/v1/documents/{id}` — get one
- `PATCH /api/v1/documents/{id}` — rename (`{"title": "..."}`)
- `DELETE /api/v1/documents/{id}` — delete (removes both the DB row and the file)
- `GET /api/v1/documents/{id}/download` — stream the original file back

Allowed types: `pdf, doc, docx, txt, png, jpg, jpeg`, max 25 MB. Files are
stored under `backend/uploads/` (configurable via `UPLOAD_DIR` in `.env`),
named by a generated UUID — never the original filename, never exposed
to the client.

**New frontend:** the dashboard's Documents section now has a real
drag-and-drop upload area (with per-file progress), a document list with
file-type icons, status badges, rename/delete/download actions, and the
same empty-state message from Sprint 2 (now shown only when you actually
have zero documents).

## Sprint 4 — Document processing

**⚠️ Manual step required before running:** run
`backend/sql/sprint4_manual_migration.sql` once against your existing
Postgres database (adds `extracted_text`, `processed_at`,
`processing_error` to `documents`). We're keeping `create_all()` instead
of Alembic for now, and `create_all()` never alters existing tables —
only creates missing ones.

```powershell
psql -U postgres -d memoryverse -f backend/sql/sprint4_manual_migration.sql
```

**New backend route:** `POST /api/v1/documents/{id}/process` — starts
text extraction as a FastAPI BackgroundTask. Returns immediately with
`{"data": {"status": "PROCESSING"}}`; the actual extraction happens
after the response is sent.

**Status lifecycle:** `UPLOADED → PROCESSING → PROCESSED` or `FAILED`.
`FAILED` documents can be retried (POST `/process` again); `PROCESSING`
or `PROCESSED` documents reject a second trigger with `409`.

**Supported types:** PDF (PyMuPDF), DOCX (python-docx), TXT (stdlib).
Legacy `.doc` uploads are accepted by Sprint 3 but have no processor
registered — triggering `/process` on one fails gracefully to `FAILED`
with a clear `processing_error`, not a crash.

**Document detail/list responses** now include `processed_at`,
`has_extracted_text` (boolean), and `processing_error` — the raw
extracted text itself is never returned by any Sprint 4 endpoint.

**Frontend:** each `UPLOADED`/`FAILED` document gets a "Process" action
(sparkle icon); `PROCESSING` shows a spinner; the dashboard polls every
3s while anything is processing so status updates show up without a
manual refresh; `FAILED` documents show their error message inline.

## Known items / notes

- `npm audit` reports one moderate advisory nested inside Next.js's own
  `postcss` dependency. It only resolves by force-downgrading Next to v9, so
  it's left as-is for now — track for a future Next.js patch release.
- `DATABASE_URL` in `.env.example` uses local defaults
  (`postgres:postgres@localhost:5432/memoryverse`). The backend boots fine
  without a live Postgres connection since Sprint 1 has no models or queries
  that touch the DB yet — you'll only need Postgres running once Sprint 2
  adds models + Alembic migrations.
