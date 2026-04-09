# Intelligent Decision Support System — Execution TODO

## Phase 0 — Alignment and Baseline
- [x] Fix backend startup blocker in `backend/app/models/risk_prediction.py` (missing SQLAlchemy imports)
- [x] Add `GET /api/v1/users/me` and route-order fix in `backend/app/api/v1/endpoints/users.py`
- [x] Align frontend API base URL via `frontend/.env` to backend running on `http://127.0.0.1:8001/api/v1`
- [x] Restart/confirm frontend dev server with updated env
- [ ] Re-validate post-login flow for admin/teacher end-to-end

## Phase 1 — User Management Module (Req #1, #16)
- [ ] Verify JWT login/logout flow and token refresh behavior
- [ ] Ensure password hashing algorithm/security config is production-safe
- [ ] Complete user CRUD behavior (add/edit/deactivate/reactivate)
- [ ] Enforce role-based authorization across all protected endpoints
- [ ] Confirm role-based frontend routing and protected views

## Phase 2 — Student Profile Management (Req #2, #15)
- [x] Validate/create student CRUD with duplicate prevention
- [x] Ensure parent/guardian details persist correctly
- [x] Implement/verify class assignment via class code
- [ ] Implement endpoint/view for individual academic records
- [ ] Add/verify required-field and duplicate validation errors

## Phase 3 — Class Management (Req #3)
- [x] Validate unique class code generation/enforcement
- [x] Verify teacher assignment to classes
- [x] Verify add/remove students by class code flow
- [x] Ensure records are correctly isolated per class

## Phase 4 — Attendance Management (Req #4)
- [x] Confirm attendance mark/create/update endpoints and UI integration
- [x] Store attendance per date/session with constraints
- [x] Implement/generate attendance summaries
- [ ] Ensure attendance is included in performance evaluation paths

## Phase 5 — Grading Management (Req #5, #15)
- [x] Ensure grading components exist: Quizzes/Oral/Activity/Attendance/Major Exam
- [ ] Enforce weight distribution total = 100%
- [x] Support grading periods: Prelim/Midterm/Semi-Finals/Finals
- [x] Validate grade encoding per student/class/period/component
- [ ] Implement spreadsheet-style grade entry UX (or practical equivalent)
- [x] Verify automatic per-period and overall grade computations

## Phase 6 — Grade Transmutation (Req #6)
- [x] Confirm transmutation mapping table storage and retrieval
- [x] Implement/verify raw->transmuted conversion API behavior
- [x] Ensure responses include both raw and transmuted grade

## Phase 7 — Grade Summary & Reports (Req #7, #12)
- [x] Show grade summaries per grading period and overall final grade
- [x] Include per-component breakdown in reports
- [x] Add optional export support (CSV/PDF if feasible)
- [x] Add charts/summary cards for dashboard/reporting

## Phase 8 — Early Warning System + AI/ML (Req #8, #9)
- [x] Confirm risk classification logic (Low/Moderate/High)
- [x] Ensure factors include grades/attendance/missing requirements
- [x] Verify trend tracking across grading periods
- [ ] Validate ML training/inference pipeline (Scikit-learn/XGBoost)
- [x] Expose prediction API endpoint and integrate in UI

## Phase 9 — Intervention Recommendation (Req #10)
- [x] Implement recommendation generation by risk level
- [x] Include actions: remedial, extra assignments, counseling, parent notification
- [ ] Show recommendations per student in relevant UI views

## Phase 10 — Notification Systems (Req #13, #14)
- [ ] Verify realtime app notifications/toasts for risk/deadlines/missing grades
- [x] Validate parent reporting API output (grades, attendance, risk, remarks)
- [x] Ensure immediate email behavior for high-risk students
- [ ] Confirm scheduler operation (APScheduler/Celery/cron path in project)
- [x] Verify email logs persistence (date/status/error details)

## Phase 11 — Centralized Record Integrity (Req #11, #15)
- [x] Audit DB normalization and relationships (users/students/classes/grades/attendance/parents)
- [x] Verify referential integrity and cascade behavior
- [x] Add missing DB constraints/indexes for consistency/performance

## Phase 12 — Security Hardening (Req #16)
- [x] Confirm JWT settings/lifetimes/refresh security posture
- [x] Audit sensitive data exposure in API responses/logs
- [x] Confirm endpoint permission boundaries (admin vs teacher)

## Phase 13 — System Design Deliverables (Req #17)
- [x] Produce ERD documentation
- [x] Produce REST API structure documentation
- [x] Produce architecture diagram + clean-architecture mapping notes
- [x] Add deployment/runbook + environment variable guide
- [x] Add testing strategy/report documentation

## Phase 14 — Final Integration and Validation
- [ ] Critical-path test pass (backend + frontend + auth + core modules)
- [ ] Thorough API checks for major endpoints and key error paths
- [ ] Frontend route/page behavior smoke check
- [ ] Final documentation/readme runbook alignment
