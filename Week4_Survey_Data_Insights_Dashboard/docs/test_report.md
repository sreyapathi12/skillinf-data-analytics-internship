# Test report

Run on 2026-10-21 with `python tests/run_checks.py`. **29 of 29 checks passed.**

Method: each figure on the dashboard is re-calculated with plain Python (csv module), independent of pandas and the dashboard code, and compared. The dashboard itself is opened and driven with Streamlit's AppTest.

| # | Check | Result | Detail |
|---|---|---|---|
| 1 | Raw file is the untouched export (456 rows, still holds personal-detail columns) | PASS | sha256 5bd30cfd6a09265a... |
| 2 | Cleaned file has no personal details (name, e-mail, phone) | PASS |  |
| 3 | Response IDs are unique | PASS |  |
| 4 | Cleaned row count matches the cleaning log | PASS | 420 valid responses |
| 5 | All ratings Q1-Q5 are between 1 and 5 | PASS |  |
| 6 | All recommend scores (Q6) are between 0 and 10 | PASS |  |
| 7 | Standardised text has only expected values | PASS |  |
| 8 | KPIs match an independent calculation (all responses) | PASS | n=420, avg 3.82, NPS +25.8 |
| 9 | KPIs match an independent calculation (Support department) | PASS | n=92, avg 3.31, NPS -4.3 |
| 10 | KPIs match an independent calculation (Round 3 only) | PASS | n=145, avg 3.91, NPS +32.1 |
| 11 | Response % for q7_workload: counts match and total 100% | PASS | n=409 |
| 12 | Response % for q8_stay_next_12_months: counts match and total 100% | PASS | n=420 |
| 13 | Rating distributions sum to 100% for every question | PASS |  |
| 14 | Benefit counts match an independent count | PASS | top: Health insurance 192 |
| 15 | NPS formula on small examples | PASS | [10,9,8,7,6,0] -> 0; [9,9,9,3] -> +50 |
| 16 | Group average and n match (work-life balance, Support) | PASS | n=90 |
| 17 | Small groups are flagged (n < 30) | PASS |  |
| 18 | Dashboard opens with no errors | PASS | 5 tabs, 5 filters |
| 19 | KPI cards show the independent numbers (no filter) | PASS | {'Responses': '420', 'Avg satisfaction (1-5)': '3.82', 'Satisfied (rated 4-5)': '66.3%', 'Net Promoter Score': '+26', 'Plan to stay (Yes)': '64.8%'} |
| 20 | Filters work: Support + Round 3 cards match the independent numbers | PASS | n=28, avg 3.39, NPS +0 |
| 21 | Filters that match nobody show a warning instead of crashing | PASS |  |
| 22 | Group comparison tab changes without errors | PASS |  |
| 23 | Browser: 'Ratings' tab draws its charts | PASS | 1 charts, screenshot screenshots/01_ratings.png |
| 24 | Browser: 'Group comparison' tab draws its charts | PASS | 2 charts, screenshot screenshots/02_group_comparison.png |
| 25 | Browser: 'Trends' tab draws its charts | PASS | 2 charts, screenshot screenshots/03_trends.png |
| 26 | Browser: 'Choices & NPS' tab draws its charts | PASS | 4 charts, screenshot screenshots/04_choices_and_nps.png |
| 27 | Browser: 'Comments' tab draws its charts | PASS | 1 charts, screenshot screenshots/05_comments.png |
| 28 | Browser: opening ?dept=Support shows the Support-only numbers | PASS | KPI cards: 92, 3.31, 44.0%, -4, 45.7% |
| 29 | Browser: no JavaScript or console errors | PASS |  |

## Not covered
- How the charts look is judged by eye in `screenshots/`; the checks only confirm they draw.
- Browsers other than Chromium.
