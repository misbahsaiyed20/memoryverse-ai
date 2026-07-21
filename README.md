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

## Known items / notes

- `npm audit` reports one moderate advisory nested inside Next.js's own
  `postcss` dependency. It only resolves by force-downgrading Next to v9, so
  it's left as-is for now — track for a future Next.js patch release.
- `DATABASE_URL` in `.env.example` uses local defaults
  (`postgres:postgres@localhost:5432/memoryverse`). The backend boots fine
  without a live Postgres connection since Sprint 1 has no models or queries
  that touch the DB yet — you'll only need Postgres running once Sprint 2
  adds models + Alembic migrations.
