"""Calculation helpers shared by the analysis notebook and the Streamlit dashboard.

Rules used everywhere:
  * Response % = answers of one kind / valid responses to THAT question x 100
    (blank answers are excluded from the denominator, and n is always reported).
  * Favourable = rating of 4 or 5. NPS = % promoters (9-10) minus % detractors (0-6).
  * A group with fewer than LOW_N responses is flagged as less reliable.
"""
import numpy as np
import pandas as pd

RATING_QUESTIONS = {
    "q1_overall_satisfaction": "Overall satisfaction",
    "q2_work_life_balance": "Work-life balance",
    "q3_manager_support": "Manager support",
    "q4_career_growth": "Career growth",
    "q5_compensation_fairness": "Compensation fairness",
}
GROUPS = {"department": "Department", "location": "Location", "age_group": "Age group", "tenure": "Tenure"}
WORKLOAD_ORDER = ["Very manageable", "Manageable", "Sometimes overwhelming", "Often overwhelming"]
STAY_ORDER = ["Yes", "Not sure", "No"]
LOW_N = 30

# Chart colours (validated palette: categorical slots 1-5, ordinal blue ramp, ink tokens)
BLUE, ORANGE = "#2a78d6", "#eb6834"
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]
ORDINAL5 = ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#104281"]
SEQ = ["#cde2fb", "#0d366b"]
INK, INK2, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#fcfcfb"


def load_clean(path):
    return pd.read_csv(path, parse_dates=["date"])


def rating_summary(df):
    rows = []
    for col, label in RATING_QUESTIONS.items():
        s = df[col].dropna()
        n = len(s)
        rows.append(dict(question=label, column=col, n=n,
                         mean=s.mean() if n else np.nan, median=s.median() if n else np.nan,
                         most_common=int(s.mode().min()) if n else np.nan,
                         pct_favourable=100 * (s >= 4).mean() if n else np.nan))
    return pd.DataFrame(rows)


def rating_distribution(df):
    rows = []
    for col, label in RATING_QUESTIONS.items():
        s = df[col].dropna()
        counts = s.value_counts().reindex([1, 2, 3, 4, 5], fill_value=0)
        for rating, c in counts.items():
            rows.append(dict(question=label, rating=int(rating), n=int(c), n_total=len(s),
                             pct=100 * c / len(s) if len(s) else np.nan))
    return pd.DataFrame(rows)


def single_choice(df, col, order):
    s = df[col].dropna()
    counts = s.value_counts().reindex(order, fill_value=0)
    total = int(counts.sum())
    return pd.DataFrame({"answer": counts.index, "n": counts.values.astype(int), "total": total,
                         "pct": 100 * counts.values / total if total else np.nan})


def multi_choice(df, col="benefits"):
    s = df[col].dropna()
    total = len(s)
    counts = s.str.split("; ").explode().value_counts()
    return pd.DataFrame({"answer": counts.index, "n": counts.values.astype(int), "total": total,
                         "pct": 100 * counts.values / total if total else np.nan})


def nps(series):
    s = series.dropna()
    n = len(s)
    if n == 0:
        return dict(score=np.nan, promoters=np.nan, passives=np.nan, detractors=np.nan, n=0)
    prom, det = int((s >= 9).sum()), int((s <= 6).sum())
    return dict(score=100 * (prom - det) / n, promoters=prom, passives=n - prom - det, detractors=det, n=n)


def group_means(df, group_col, q_col):
    g = df.groupby(group_col)[q_col].agg(["count", "mean", "std"]).reset_index()
    g.columns = [group_col, "n", "mean", "sd"]
    g["ci"] = 1.96 * g["sd"] / np.sqrt(g["n"].where(g["n"] > 1))
    g["low_n"] = g["n"] < LOW_N
    return g


def trend(df):
    rows = []
    for col, label in RATING_QUESTIONS.items():
        g = df.groupby(["round_no", "survey_round"])[col].agg(["count", "mean"]).reset_index()
        for _, r in g.iterrows():
            rows.append(dict(round_no=int(r["round_no"]), survey_round=r["survey_round"], question=label, n=int(r["count"]), mean=r["mean"]))
    return pd.DataFrame(rows)


def kpis(df):
    q1 = df["q1_overall_satisfaction"].dropna()
    stay = df["q8_stay_next_12_months"].dropna()
    return dict(responses=len(df),
                avg_satisfaction=q1.mean() if len(q1) else np.nan,
                pct_satisfied=100 * (q1 >= 4).mean() if len(q1) else np.nan,
                nps=nps(df["q6_recommend"])["score"],
                pct_staying=100 * (stay == "Yes").mean() if len(stay) else np.nan,
                n_q1=len(q1), n_nps=int(df["q6_recommend"].notna().sum()), n_stay=len(stay))
