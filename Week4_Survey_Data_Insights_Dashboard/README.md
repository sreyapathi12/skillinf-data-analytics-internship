# Week 4: Survey Data Insights Dashboard

An employee engagement survey (sample data, 3 rounds): cleaned, analysed, and shown in an interactive Streamlit dashboard with a findings report.

## Headline results
- 420 valid responses (456 raw). Average satisfaction **3.82/5**, NPS **+26**, **64.8%** plan to stay.
- Pay fairness is lowest (3.08). Support has the lowest satisfaction (3.31) vs HR & Admin (4.07).
- Manager support improved clearly across rounds; NPS rose +19.5 to +32.1.

## Folder structure
```
data/        raw_survey_responses.csv, cleaned_survey_data.csv, response_summary.csv, insights.json
notebooks/   analysis.ipynb  (cleaning + analysis + charts)
dashboard/   app.py (Streamlit), survey_calcs.py
charts/      8 PNG charts
report/      survey_findings_report.md
docs/        survey_questions.md, data_cleaning_log.md, test_report.md
scripts/     generate_sample_survey.py
tests/       run_checks.py (29 checks), take_screenshots.py
screenshots/ dashboard views
```

## Run the dashboard
```
pip install -r requirements.txt
cd dashboard
streamlit run app.py
```
Use the sidebar filters (round, department, location, age, tenure). Download buttons give the filtered data and a summary.

## Steps followed
1. Collected sample data. 2. Cleaned it (log in `docs/data_cleaning_log.md`). 3. Response % per question. 4. Ratings, NPS, group comparisons, trends. 5. Charts. 6. Dashboard. 7. Report. 8. Tested (`docs/test_report.md`).

## Tools
Python (pandas, scipy, matplotlib, seaborn), Altair, Streamlit.
