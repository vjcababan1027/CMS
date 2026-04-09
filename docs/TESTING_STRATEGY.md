# Testing Strategy and Validation Report (Phase 14)

## 1) Scope

This document captures:
- testing depth options (critical-path vs thorough)
- backend/API validation approach with curl
- frontend validation approach
- current findings and known issues
- retest checklist for closure

---

## 2) Testing Levels

## Critical-Path Testing
Focus only on core operational flow:
1. backend starts
2. login works
3. authenticated endpoint works (`/users/me`)
4. key list endpoint works (`/users/`)
5. frontend can load and call backend

## Thorough Testing
Full coverage of API + frontend:
- exercise all major endpoints with happy path, error path, and edge cases
- verify role boundary behavior (admin vs teacher)
- verify validation semantics and status codes
- verify each frontend page/section interaction and route guard behavior

---

## 3) Backend/API Test Method (Curl-first)

Base:
- `http://127.0.0.1:8001/api/v1`

Auth token bootstrap pattern:
```bash
curl -X POST "http://127.0.0.1:8001/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@cms.com&password=admin1234!"
```

Use returned bearer token for protected requests:
```bash
-H "Authorization: Bearer <jwt-access>"
```

Minimum endpoint families for thorough coverage:
- `/auth/*`
- `/users/*`
- `/students/*`
- `/classes/*`
- `/attendance/*`
- `/grades/*`
- `/grade-weights/*`
- `/grade-transmutations/*`
- `/risk-predictions/*`
- `/interventions/*`
- `/parent-reporting/*`
- `/reports/*`

For each family, verify:
- create/list/get/update/delete (where applicable)
- invalid payload handling
- missing auth / wrong role access behavior
- non-existent resource handling (`404`)

---

## 4) Frontend Test Method

Pages/components to cover:
- Login
- Dashboard
- Students
- Classes
- Attendance
- Grades
- Early Warning
- Parent Reporting
- Reports
- Users
- Protected route + layout navigation

Checklist per page:
- load succeeds
- links/buttons/inputs function
- API errors display gracefully
- role-gated actions hidden/blocked appropriately

---

## 5) Current Validation Findings

Completed checks:
- Backend starts on `127.0.0.1:8001`
- `POST /auth/login` returns `200`
- `POST /auth/refresh-token` with refresh token returns `200`
- `GET /users/me` returns `200`
- `GET /users/` now returns `200` after email data cleanup

Resolved issue:
- `/users/` response `500` caused by reserved-domain (`*.local`) values against strict `EmailStr` serialization.
- Data cleanup to valid domains resolved this endpoint response failure.

Known open issue:
- `POST /auth/refresh-token` still accepted an access token in runtime verification checks (returned `200` during observed tests), though hardening logic was introduced.

---

## 6) Retest Checklist (Open)

- [ ] Reproduce and fix refresh endpoint token-type rejection behavior (`access` token should fail refresh).
- [ ] Re-run auth matrix:
  - [ ] login success/failure
  - [ ] refresh with refresh token success
  - [ ] refresh with access token failure
- [ ] Run users CRUD + role checks for admin/teacher paths.
- [ ] Run full endpoint family matrix listed above (happy/error/edge).
- [ ] Execute frontend page-by-page interaction smoke and role-gate validation.
- [ ] Record final pass/fail status and attach command snippets in closure notes.

---

## 7) Exit Criteria

Testing is considered complete when:
1. no known P0/P1 auth or serialization defects remain,
2. all major endpoint families pass critical behavior checks,
3. frontend primary flows are operational for intended roles,
4. documented known issues are either fixed or explicitly accepted.
