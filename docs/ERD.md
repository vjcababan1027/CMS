# ERD — Intelligent Decision Support System

## Core Entities

- **users**
  - `id` (PK)
  - `email` (unique)
  - `hashed_password`
  - `full_name`
  - `role` (`admin` / `teacher`)
  - `is_active`
  - timestamps

- **classes**
  - `id` (PK)
  - `class_code` (unique)
  - `name`
  - `teacher_id` (FK → users.id)
  - timestamps

- **students**
  - `id` (PK)
  - `student_code` (unique)
  - identity/profile fields
  - `is_active`
  - timestamps

- **enrollments**
  - `id` (PK)
  - `student_id` (FK → students.id)
  - `class_id` (FK → classes.id)
  - unique (`student_id`, `class_id`)
  - timestamps

- **attendance**
  - `id` (PK)
  - `student_id` (FK → students.id)
  - `class_id` (FK → classes.id)
  - `date`
  - `status`
  - `recorded_by` (FK → users.id)
  - timestamps
  - indexes:
    - (`class_id`, `date`)
    - (`student_id`, `class_id`, `date`)

- **grades**
  - `id` (PK)
  - `student_id` (FK → students.id)
  - `class_id` (FK → classes.id)
  - `period`
  - grade component fields + computed/transmuted values
  - timestamps
  - indexes:
    - (`class_id`, `period`)
    - (`student_id`, `class_id`, `period`)

- **grade_weights**
  - `id` (PK)
  - `class_id` (FK → classes.id)
  - `period`
  - component weight fields
  - unique (`class_id`, `period`)
  - timestamps

- **grade_transmutations**
  - mapping table for raw → transmuted conversion rules

- **risk_predictions**
  - `id` (PK)
  - `student_id` (FK → students.id)
  - `class_id` (FK → classes.id)
  - `risk_level`
  - `risk_score`
  - `prediction_date`
  - `is_active`
  - timestamps
  - indexes:
    - (`class_id`, `is_active`, `prediction_date`)
    - (`student_id`, `class_id`, `prediction_date`)

- **parents**
  - `id` (PK)
  - `user_id` (FK → users.id)
  - contact fields
  - timestamps

- **student_parents** (bridge table)
  - `id` (PK)
  - `student_id` (FK → students.id)
  - `parent_id` (FK → parents.id)
  - `is_primary_contact`
  - timestamps

- **parent_email_logs** (service-level log table)
  - email dispatch status/history for parent reporting notifications

---

## Relationship Summary (Cardinality)

- **users (teacher)** 1 ── * **classes**
- **classes** 1 ── * **enrollments**
- **students** 1 ── * **enrollments**
- **classes** 1 ── * **attendance**
- **students** 1 ── * **attendance**
- **users** 1 ── * **attendance** (as recorder)
- **classes** 1 ── * **grades**
- **students** 1 ── * **grades**
- **classes** 1 ── * **grade_weights**
- **classes** 1 ── * **risk_predictions**
- **students** 1 ── * **risk_predictions**
- **users** 1 ── * **parents**
- **students** * ── * **parents** (via **student_parents**)

---

## Integrity / Cascade Notes

Recent model integrity hardening enabled ORM relationships and cascades for dependent collections, including:
- Class-owned collections (enrollments, grades, attendance, risk predictions, grade weights)
- Student-owned collections (enrollments, grades, attendance, risk predictions, student-parent links)
- Parent-owned student links

This supports cleaner referential behavior at the ORM layer and aligns with centralized record integrity objectives.
