# REST API Structure — Intelligent Decision Support System

Base prefix: `/api/v1`

## Authentication
- `POST /auth/register`
  - Create user account (role-based user provisioning).
- `POST /auth/login`
  - OAuth2 password login, returns access + refresh token.
- `POST /auth/refresh-token`
  - Exchange valid refresh token for new token pair.

## Users
- `GET /users/me`
  - Current authenticated profile.
- User CRUD endpoints under `/users/*`
  - Admin-governed user lifecycle (create/update/activate/deactivate).

## Students
- Student CRUD under `/students/*`
- Class assignment and profile-linked operations for student records.

## Classes
- Class CRUD under `/classes/*`
- Teacher ownership and class roster management flows.

## Attendance
- Attendance CRUD/listing under `/attendance/*`
- Supports teacher/admin class-scoped operations and summaries.

## Grades
- Grade CRUD/listing under `/grades/*`
- Grading by period/components, with computed outputs.

## Grade Weights
- `/grade-weights/*`
- Per-class/per-period grade weight configuration.

## Grade Transmutations
- `/grade-transmutations/*`
- Raw-to-transmuted mapping and conversion support.

## Risk Predictions
- `/risk-predictions/*`
- Early warning outputs (risk level/score/trend windows).

## Interventions
- `/interventions/*`
- Recommendation retrieval by:
  - risk prediction id
  - student + class latest prediction
- Structured intervention response schema with category/priority/rationale.

## Parent Reporting
- `/parent-reporting/*`
- Parent report generation/logging/dispatch hooks.
- Role boundaries:
  - list logs: teacher/admin
  - create/update/dispatch: admin

## Reports
- `/reports/*`
- Aggregated reporting endpoints (grade/attendance/risk summaries).

---

## Authorization Model

Security dependencies in `app/core/security.py`:
- `get_current_active_user`
- `get_current_admin`
- `get_current_teacher_or_admin`

Typical boundary:
- Admin-only for platform management/sensitive dispatch actions.
- Teacher-or-admin for class-scoped instructional operations.
- Endpoint-level ownership checks used where teacher must own the class.

---

## Token Model

- Access token: short-lived, includes claim `type=access`
- Refresh token: longer-lived, includes claim `type=refresh`
- Refresh endpoint now enforces refresh token type validation.

---

## Error Semantics (Common)

- `401` invalid/expired token, malformed auth payload
- `403` role/permission denied
- `404` resource not found
- `409` duplicate/conflict scenarios
- `400` validation/business-rule failures

---

## Request/Response Examples + Curl

> Base URL used in examples: `http://127.0.0.1:8001/api/v1`

### 1) Login

**Endpoint**
- `POST /auth/login`
- Content-Type: `application/x-www-form-urlencoded`

**Curl**
```bash
curl -X POST "http://127.0.0.1:8001/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@cms.com&password=admin1234!"
```

**Sample Response (200)**
```json
{
  "access_token": "<jwt-access>",
  "refresh_token": "<jwt-refresh>",
  "token_type": "bearer"
}
```

### 2) Refresh Token

**Endpoint**
- `POST /auth/refresh-token?refresh_token=<jwt-refresh>`

**Curl**
```bash
curl -X POST "http://127.0.0.1:8001/api/v1/auth/refresh-token?refresh_token=<jwt-refresh>"
```

**Sample Response (200)**
```json
{
  "access_token": "<new-jwt-access>",
  "refresh_token": "<new-jwt-refresh>",
  "token_type": "bearer"
}
```

### 3) Current User Profile

**Endpoint**
- `GET /users/me`
- Authorization: `Bearer <access_token>`

**Curl**
```bash
curl "http://127.0.0.1:8001/api/v1/users/me" \
  -H "Authorization: Bearer <jwt-access>"
```

**Sample Response (200)**
```json
{
  "id": 1,
  "email": "admin@cms.com",
  "full_name": "Admin User",
  "role": "admin",
  "is_active": true,
  "created_at": "2026-04-01T10:00:00",
  "updated_at": null
}
```

### 4) List Users

**Endpoint**
- `GET /users/`
- Authorization: `Bearer <access_token>`

**Curl**
```bash
curl "http://127.0.0.1:8001/api/v1/users/" \
  -H "Authorization: Bearer <jwt-access>"
```

**Sample Response (200)**
```json
[
  {
    "id": 1,
    "email": "admin@cms.com",
    "full_name": "Admin User",
    "role": "admin",
    "is_active": true,
    "created_at": "2026-04-01T10:00:00",
    "updated_at": null
  }
]
```

### 5) Representative CRUD Pattern (Students)

**Create**
```bash
curl -X POST "http://127.0.0.1:8001/api/v1/students/" \
  -H "Authorization: Bearer <jwt-access>" \
  -H "Content-Type: application/json" \
  -d "{\"student_number\":\"2026-0001\",\"first_name\":\"Juan\",\"last_name\":\"Dela Cruz\"}"
```

**List**
```bash
curl "http://127.0.0.1:8001/api/v1/students/" \
  -H "Authorization: Bearer <jwt-access>"
```

**Update**
```bash
curl -X PUT "http://127.0.0.1:8001/api/v1/students/1" \
  -H "Authorization: Bearer <jwt-access>" \
  -H "Content-Type: application/json" \
  -d "{\"first_name\":\"Juan Carlo\"}"
```

**Delete**
```bash
curl -X DELETE "http://127.0.0.1:8001/api/v1/students/1" \
  -H "Authorization: Bearer <jwt-access>"
```

---

## Notes from Current Validation

- `/users/` previously returned `500` when seeded accounts used reserved-domain emails (`*.local`) with strict `EmailStr` response validation.
- After data cleanup to valid domains, `/users/` returned `200`.
- A known edge-case remains under investigation: refresh endpoint accepted access token in runtime checks.
