# Data cleaning log

Raw file: `data/raw_survey_responses.csv` (456 rows, left unchanged). Cleaned file: `data/cleaned_survey_data.csv` (420 valid responses).

| # | Step | Rows / values affected |
|---|---|---|
| 1 | Remove exact duplicate responses | 12 |
| 2 | Remove test submissions (name 'test' / test e-mail) | 3 |
| 3 | Convert timestamps in mixed formats to dates | 294 |
| 4 | Standardise department spelling/case | 25 |
| 5 | Standardise location spelling/case (Bangalore -> Bengaluru) | 60 |
| 6 | Standardise Q8 answers (yes / YES / Yes -> Yes) | 62 |
| 7 | Standardise benefit choices (spacing/case) | 56 |
| 8 | Convert ratings typed as text ('4 - Agree', 'Four', '4.0') to numbers | 30 |
| 9 | Impossible rating values (0, 6, 55, -1, 11) set to 'no response' | 7 |
| 10 | Remove repeat submissions (same e-mail in the same round, keep first) | 6 |
| 11 | Remove incomplete responses (fewer than 5 of 9 questions answered) | 15 |
| 12 | Impossible ages (5, 0, 150) and blank ages -> 'Not specified' | 13 |
| 13 | Blank department labelled 'Not specified' | 8 |
| 14 | Tag open-text comments by theme | 265 |
| 15 | Remove personal details (name, e-mail, phone) from the cleaned file | 3 |

## Decisions and assumptions
- Blank answers are kept as blank and excluded from that question's percentages; nothing is guessed.
- A repeat submission is the same e-mail address in the same survey round; the first one is kept. E-mail is used only for this check and then removed.
- A response is incomplete if fewer than 5 of the 9 closed questions (Q1-Q9) were answered.
- Ratings outside the allowed range (Q1-Q5: 1-5, Q6: 0-10) are treated as typing errors and set to no response.
- Ages outside 18-70 are treated as errors; the response stays in the data with age group 'Not specified'.
- Comments are tagged by simple keyword rules, so themes are approximate; one theme per comment.
- Personal details (name, e-mail, phone) are dropped from the cleaned file; the dashboard never uses them.
