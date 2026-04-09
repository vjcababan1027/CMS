# Architecture — Intelligent Decision Support System

## 1) High-Level Architecture

- **Frontend**: React (Vite), page-driven UI, authenticated API consumption.
- **Backend API**: FastAPI (`/api/v1`), modular endpoint routers.
- **Data Layer**: SQLAlchemy ORM models + relational PostgreSQL.
- **Security Layer**: OAuth2 password flow + JWT access/refresh tokens.
- **Domain Services**:
  - parent notification/email service
  - risk/intervention orchestration
- **Background/Scheduler**:
  - notification scheduling hooks (biweekly + high-risk dispatch)
- **ML Layer**:
  - risk prediction model interfaces and periodic retraining placeholders.

---

## 2) Backend Layer Mapping (Clean-ish Layering)

### API Layer
- `backend/app/api/v1/endpoints/*`
- Responsibility:
  - HTTP contract
  - request validation
  - auth dependency enforcement
  - response shaping

### Core / Security / Config
- `backend/app/core/config.py`
- `backend/app/core/security.py`
- Responsibility:
  - env/settings
  - JWT issue/verify
  - role guards

### Data Access Layer
- `backend/app/models/*`
- `backend/app/schemas/*`
- `backend/app/db/*`
- Responsibility:
  - persistence model
  - schema serialization/deserialization
  - session management

### Services / Tasks
- `backend/app/services/*`
- `backend/app/tasks/*`
- Responsibility:
  - side effects (email/logging/dispatch)
  - scheduled workflows

### ML
- `backend/app/ml/*`
- Responsibility:
  - prediction/training artifacts and interfaces

---

## 3) Frontend Layer Mapping

- `frontend/src/pages/*`:
  - route-level feature pages (students/classes/attendance/grades/reports/early warning)
- `frontend/src/components/*`:
  - layout/protected-route/shared UI
- `frontend/src/contexts/AuthContext.jsx`:
  - auth state and token-aware flow
- `frontend/src/services/*`:
  - API client wrappers / CRUD helpers

---

## 4) Request / Data Flow

1. User authenticates via `/api/v1/auth/login`.
2. Frontend stores token context and calls protected endpoints.
3. Backend validates bearer token + role dependency.
4. Endpoint performs ORM operations and returns schemas.
5. For risk/parent-reporting flows, backend may trigger service-level dispatch/logging.
6. Scheduler can invoke periodic reporting/high-risk scans.

---

## 5) Security Boundaries

- Role gates:
  - `admin` for high-privilege management/dispatch operations.
  - `teacher|admin` for instructional/class-scoped operations.
- Token hardening:
  - token type claim enforcement (`access` vs `refresh`)
  - refresh endpoint strict type check
- Config hardening:
  - shorter default access token TTL
  - production guard for `SECRET_KEY` strength

---

## 6) Centralized Record Integrity (Recent)

Recent updates strengthened model-level integrity by enabling:
- explicit bidirectional relationships
- cascade behavior for dependent records
- targeted indexes for attendance/grades/risk queries

This improves consistency, query performance, and maintainability across modules.

---

## 7) Runtime / Deployment Notes

Development run pattern:
- Backend: Uvicorn serving FastAPI app
- Frontend: Vite dev server

Operational expectations:
- `.env` values should override defaults for DB/security/email.
- Production must provide strong `SECRET_KEY`.
- Background scheduler and SMTP paths should be explicitly configured per environment.

---

## 8) Deployment Runbook (Dev/Stage/Prod)

### Backend (FastAPI)
```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

### Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev
```

### Health/Access
- Backend docs: `http://127.0.0.1:8001/docs`
- API prefix: `http://127.0.0.1:8001/api/v1`
- Frontend dev: `http://127.0.0.1:5173` (default Vite)

### CORS and API Base URL
- Frontend API base should target backend v1 prefix.
- If CORS issues appear, ensure backend allowlist includes the active frontend origin.

---

## 9) Environment Variable Reference (from `app/core/config.py`)

| Variable | Purpose | Typical Dev Value |
|---|---|---|
| `PROJECT_NAME` | API/service display name | `Intelligent Decision Support System` |
| `API_V1_STR` | API route prefix | `/api/v1` |
| `SECRET_KEY` | JWT/signing key | long random string |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | access token TTL | `60` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | refresh token TTL | `7` |
| `POSTGRES_SERVER` | DB host | `localhost` |
| `POSTGRES_USER` | DB user | `postgres` |
| `POSTGRES_PASSWORD` | DB password | `<secret>` |
| `POSTGRES_DB` | DB name | `cms_db` |
| `SQLALCHEMY_DATABASE_URI` | full DB URI (computed/override) | `postgresql://...` |
| `SMTP_HOST` | SMTP server | `smtp.gmail.com` (example) |
| `SMTP_PORT` | SMTP port | `587` |
| `SMTP_USER` | SMTP username | `<email>` |
| `SMTP_PASSWORD` | SMTP password/app password | `<secret>` |
| `EMAILS_FROM_EMAIL` | from email address | `noreply@cms.com` |
| `EMAILS_FROM_NAME` | sender display name | `CMS Notifications` |
| `SMTP_MOCK_MODE` | bypass real sends in dev | `true`/`false` |
| `ENV` | runtime environment | `development` / `production` |

### Production Security Notes
- Use a strong `SECRET_KEY` and never commit it to source control.
- Keep token TTLs short and rotate keys per policy.
- Enforce HTTPS and secure secret injection through deployment platform.
