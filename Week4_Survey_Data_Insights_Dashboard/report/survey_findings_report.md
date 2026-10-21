# Survey Findings Report: Employee Engagement Survey

**Data:** sample survey, 3 rounds (Jan, Apr, Jul 2026). 456 raw rows, **420 valid responses** after cleaning (135 / 140 / 145 per round).
Percentages use the people who answered that question; `n` is shown each time. Groups under 30 responses are less reliable.

## Headline numbers
| Measure | Result |
|---|---|
| Average overall satisfaction | **3.82 / 5** (n=415); 66.3% rated 4-5 |
| Net Promoter Score | **+26** (n=411): 47.0% promoters, 21.2% detractors |
| Plan to stay 12 months | **64.8% Yes**, 22.1% Not sure, 13.1% No (n=420) |

## Key findings
1. **Pay is the weakest area.** Compensation fairness averages 3.08; only 32.9% are favourable (n=413). Engineering rates it lowest (2.76, n=131) and Sales highest (3.50, n=72).
2. **Support is the department that needs attention.** It has the lowest satisfaction (3.31, n=91, vs HR & Admin 4.07, n=54; gap 0.77, p<0.001) and the lowest work-life balance and career growth. 58.7% of Support say workload is often/sometimes overwhelming vs 35.3% elsewhere.
3. **Manager support is the strongest area** (3.87; 68.0% favourable) and is the one rating that clearly improved: 3.77 in Round 1 to 4.02 in Round 3.
4. **NPS rose each round:** +19.5, +25.4, +32.1.
5. **Newer staff are happier.** Under 1 year: 4.01 (n=133) vs 3+ years: 3.61 (n=128).
6. **Location and age show no clear difference** in ratings.
7. **Valued benefits:** health insurance (47.2%), flexible hours (42.3%), paid leave (39.8%). Wellness programs are lowest (26.0%). n=407.
8. **Comments** (265 people, 63.1%): top themes are Positive (23.8%), Flexibility (23.0%), Pay (18.9%), Workload (17.7%).

## Suggested actions
- Review pay fairness, starting with Engineering.
- Look at workload and growth options for the Support team.
- Share what is working in managers' support across teams.

## Limits
- Sample (synthetic) data, so results illustrate the method, not a real company.
- Comment themes come from keyword matching, so they are approximate.
- A "clear difference" needs a gap of 0.30+ and p<0.05 in groups of 30+ people; with 20 comparisons, a few could appear by chance.
- Survey answers show opinions, not causes.

## Charts
`charts/01` ratings, `02` department heatmap, `03` trend by round, `04` NPS, `05` workload and stay intent, `06` benefits, `07` comment themes, `08` work-life balance by department. Interactive version: `dashboard/app.py`. Screenshots: `screenshots/`.
