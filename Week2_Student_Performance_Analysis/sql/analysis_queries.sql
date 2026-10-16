-- Week 2: Student Performance Analysis - analysis queries
-- Run schema.sql first. Every query reports GROUPS only; no individual student is ranked or labelled.
-- Pass mark = 40; grade bands: A>=80, B>=65, C>=50, D>=40, F<40.

-- Q1. Overall summary
SELECT COUNT(DISTINCT student_id) AS students,
       COUNT(*)                   AS result_rows,
       ROUND(AVG(marks), 2)       AS avg_marks,
       ROUND(100.0 * SUM(CASE WHEN marks >= 40 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pass_rate_pct,
       ROUND(100.0 * SUM(classes_attended) / SUM(classes_held), 1)               AS attendance_pct
FROM results;

-- Q2. Subject-wise results (JOIN + GROUP BY + ORDER BY)
SELECT su.subject_name,
       ROUND(AVG(r.marks), 2) AS avg_marks,
       MIN(r.marks) AS min_marks,
       MAX(r.marks) AS max_marks,
       ROUND(100.0 * SUM(CASE WHEN r.marks >= 40 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pass_rate_pct,
       ROUND(100.0 * SUM(r.classes_attended) / SUM(r.classes_held), 1)             AS attendance_pct
FROM results r
JOIN subjects su ON su.subject_id = r.subject_id
GROUP BY su.subject_name
ORDER BY avg_marks DESC;

-- Q3. Section-wise results
SELECT st.section,
       COUNT(DISTINCT st.student_id) AS students,
       ROUND(AVG(r.marks), 2)        AS avg_marks,
       ROUND(100.0 * SUM(CASE WHEN r.marks >= 40 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pass_rate_pct
FROM results r
JOIN students st ON st.student_id = r.student_id
GROUP BY st.section
ORDER BY st.section;

-- Q4. Average marks by subject and section (conditional aggregation)
SELECT su.subject_name,
       ROUND(AVG(CASE WHEN st.section = 'A' THEN r.marks END), 1) AS sec_A,
       ROUND(AVG(CASE WHEN st.section = 'B' THEN r.marks END), 1) AS sec_B,
       ROUND(AVG(CASE WHEN st.section = 'C' THEN r.marks END), 1) AS sec_C,
       ROUND(AVG(CASE WHEN st.section = 'D' THEN r.marks END), 1) AS sec_D
FROM results r
JOIN students st ON st.student_id = r.student_id
JOIN subjects su ON su.subject_id = r.subject_id
GROUP BY su.subject_name
ORDER BY su.subject_name;

-- Q5. Attendance band vs marks (CTE + CASE)
WITH banded AS (
    SELECT marks,
           100.0 * classes_attended / classes_held AS att_pct,
           CASE
             WHEN 100.0 * classes_attended / classes_held < 75 THEN 'Below 75%'
             WHEN 100.0 * classes_attended / classes_held < 85 THEN '75-84%'
             WHEN 100.0 * classes_attended / classes_held < 95 THEN '85-94%'
             ELSE '95%+'
           END AS attendance_band
    FROM results
)
SELECT attendance_band,
       COUNT(*)               AS result_rows,
       ROUND(AVG(marks), 2)   AS avg_marks,
       ROUND(100.0 * SUM(CASE WHEN marks >= 40 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pass_rate_pct
FROM banded
GROUP BY attendance_band
ORDER BY MIN(att_pct);

-- Q6. Grade distribution
WITH graded AS (
    SELECT CASE WHEN marks >= 80 THEN 'A'
                WHEN marks >= 65 THEN 'B'
                WHEN marks >= 50 THEN 'C'
                WHEN marks >= 40 THEN 'D'
                ELSE 'F' END AS grade
    FROM results
)
SELECT grade,
       COUNT(*) AS result_rows,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM results), 1) AS share_pct
FROM graded
GROUP BY grade
ORDER BY grade;

-- Q7. Subjects with average marks below the overall average (subquery in HAVING)
SELECT su.subject_name,
       ROUND(AVG(r.marks), 2) AS avg_marks,
       (SELECT ROUND(AVG(marks), 2) FROM results) AS overall_avg
FROM results r
JOIN subjects su ON su.subject_id = r.subject_id
GROUP BY su.subject_name
HAVING AVG(r.marks) < (SELECT AVG(marks) FROM results)
ORDER BY avg_marks;

-- Q8. Rank subjects within each section (window function RANK)
WITH sec_subject AS (
    SELECT st.section, su.subject_name, AVG(r.marks) AS avg_marks
    FROM results r
    JOIN students st ON st.student_id = r.student_id
    JOIN subjects su ON su.subject_id = r.subject_id
    GROUP BY st.section, su.subject_name
)
SELECT section,
       subject_name,
       ROUND(avg_marks, 2) AS avg_marks,
       RANK() OVER (PARTITION BY section ORDER BY avg_marks DESC) AS rank_in_section
FROM sec_subject
ORDER BY section, rank_in_section;

-- Q9. Each subject's average vs the mean of all subject averages (window AVG OVER)
WITH subj AS (
    SELECT su.subject_name, AVG(r.marks) AS avg_marks
    FROM results r
    JOIN subjects su ON su.subject_id = r.subject_id
    GROUP BY su.subject_name
)
SELECT subject_name,
       ROUND(avg_marks, 2) AS avg_marks,
       ROUND(avg_marks - AVG(avg_marks) OVER (), 2) AS diff_from_subject_mean
FROM subj
ORDER BY diff_from_subject_mean DESC;

-- Q10. How student-level average marks are distributed (counts only, no individual IDs shown)
WITH student_avg AS (
    SELECT student_id, AVG(marks) AS avg_marks
    FROM results
    GROUP BY student_id
)
SELECT CASE WHEN avg_marks >= 80 THEN '80 and above'
            WHEN avg_marks >= 65 THEN '65 to 79'
            WHEN avg_marks >= 50 THEN '50 to 64'
            ELSE 'Below 50' END AS average_marks_band,
       COUNT(*) AS students
FROM student_avg
GROUP BY average_marks_band
ORDER BY MIN(avg_marks) DESC;

