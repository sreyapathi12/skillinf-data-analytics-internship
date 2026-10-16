# Week 2 – Student Performance Analysis

## Objective
Analyse student marks, attendance and subject-wise results from a sample dataset, identify performance patterns, visualise the key statistics in a dashboard, and summarise the findings without drawing unsupported conclusions about individual students.

## Dataset
Synthetic sample data (not real students): 120 students in 4 sections (30 each), 5 subjects, 600 result rows. Student IDs are anonymous.

Three related tables (see `sql/schema.sql`):

| Table | Key columns |
|---|---|
| `students` | `student_id` (PK), `section` |
| `subjects` | `subject_id` (PK), `subject_name` |
| `results` | (`student_id`, `subject_id`) PK and FKs, `marks`, `classes_held`, `classes_attended` |

## What is in this folder
- `Week2_Student_Performance_Dashboard.xlsx` – interactive dashboard (Section and Subject filters, KPIs, 4 charts, findings), plus the Data and Notes sheets
- `sql/schema.sql` – table design, constraints and sample data
- `sql/analysis_queries.sql` – 10 analysis queries: JOINs, GROUP BY/HAVING, CASE, CTEs, subqueries, window functions (RANK, AVG OVER)
- `data/` – the three tables as CSV files

## Key findings (whole sample)
- Average marks 67.8; pass rate 99.3% at a pass mark of 40; average attendance 87.1%.
- Computer Science (72.9) and English (71.1) have the highest subject averages; Mathematics is lowest (61.3).
- Marks rise with attendance: 56.3 average for records below 75% attendance, 64.9 for 75-84%, 69.3 for 85-94% and 73.0 for 95%+. The correlation between attendance % and marks is 0.38.
- Section averages range from 65.3 to 70.4, a modest gap with about 30 students per section.

## Limits of these findings
- The data is synthetic, so the numbers illustrate the method rather than describe a real school.
- Attendance and marks are associated, which does not show that attendance causes higher marks.
- All results are for groups; no individual student is ranked or labelled.
- Small groups (such as the Below 75% band) give less reliable averages, so record counts are shown beside them.

## Tools
SQL (SQLite) and Microsoft Excel (formulas, data validation, charts)
