"""Accuracy and dashboard checks. Writes docs/test_report.md.

Every number the dashboard shows is re-calculated here with plain Python (csv module),
without pandas or the dashboard code, and compared.   Run:  python tests/run_checks.py
"""
import csv, datetime, hashlib, json, math, os, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(ROOT, "dashboard"))
import pandas as pd
from streamlit.testing.v1 import AppTest
import survey_calcs as sc

RAW, CLEAN = os.path.join(ROOT, "data", "raw_survey_responses.csv"), os.path.join(ROOT, "data", "cleaned_survey_data.csv")
rows = list(csv.DictReader(open(CLEAN, encoding="utf-8")))
results = []
def check(name, ok, detail=""): results.append((name, bool(ok), detail))
num = lambda v: float(v) if v not in ("", None) else None

def independent(subset):
    q1 = [num(r["q1_overall_satisfaction"]) for r in subset if r["q1_overall_satisfaction"]]
    q6 = [num(r["q6_recommend"]) for r in subset if r["q6_recommend"]]
    q8 = [r["q8_stay_next_12_months"] for r in subset if r["q8_stay_next_12_months"]]
    prom, det = sum(x >= 9 for x in q6), sum(x <= 6 for x in q6)
    return dict(n=len(subset), avg=sum(q1) / len(q1), sat=100 * sum(x >= 4 for x in q1) / len(q1), nps=100 * (prom - det) / len(q6), stay=100 * sum(a == "Yes" for a in q8) / len(q8))

# 1. data integrity
raw_rows = list(csv.DictReader(open(RAW, encoding="utf-8")))
ins = json.load(open(os.path.join(ROOT, "data", "insights.json")))
check("Raw file is the untouched export (456 rows, still holds personal-detail columns)", len(raw_rows) == ins["rows_raw"] == 456 and {"respondent_name", "email", "phone"} <= set(raw_rows[0]),
      f"sha256 {hashlib.sha256(open(RAW, 'rb').read()).hexdigest()[:16]}...")
check("Cleaned file has no personal details (name, e-mail, phone)", not ({"respondent_name", "email", "phone"} & set(rows[0])))
check("Response IDs are unique", len({r["response_id"] for r in rows}) == len(rows))
check("Cleaned row count matches the cleaning log", len(rows) == ins["rows_clean"], f"{len(rows)} valid responses")
bad = [r for r in rows for c in sc.RATING_QUESTIONS if r[c] and not 1 <= float(r[c]) <= 5]
check("All ratings Q1-Q5 are between 1 and 5", not bad)
check("All recommend scores (Q6) are between 0 and 10", all(0 <= float(r["q6_recommend"]) <= 10 for r in rows if r["q6_recommend"]))
check("Standardised text has only expected values", {r["q8_stay_next_12_months"] for r in rows if r["q8_stay_next_12_months"]} <= set(sc.STAY_ORDER)
      and {r["department"] for r in rows} <= {"Engineering", "Sales", "Support", "HR & Admin", "Finance", "Not specified"})

# 2. calculations vs independent re-calculation
for label, subset in [("all responses", rows), ("Support department", [r for r in rows if r["department"] == "Support"]),
                      ("Round 3 only", [r for r in rows if r["round_no"] == "3"])]:
    exp, got = independent(subset), sc.kpis(pd.DataFrame(subset).replace("", float("nan")).astype({c: float for c in list(sc.RATING_QUESTIONS) + ["q6_recommend"]}))
    ok = (exp["n"] == got["responses"] and math.isclose(exp["avg"], got["avg_satisfaction"], abs_tol=1e-9) and math.isclose(exp["sat"], got["pct_satisfied"], abs_tol=1e-9)
          and math.isclose(exp["nps"], got["nps"], abs_tol=1e-9) and math.isclose(exp["stay"], got["pct_staying"], abs_tol=1e-9))
    check(f"KPIs match an independent calculation ({label})", ok, f"n={exp['n']}, avg {exp['avg']:.2f}, NPS {exp['nps']:+.1f}")

df = sc.load_clean(CLEAN)
for col, order in [("q7_workload", sc.WORKLOAD_ORDER), ("q8_stay_next_12_months", sc.STAY_ORDER)]:
    d = sc.single_choice(df, col, order); cnt = Counter(r[col] for r in rows if r[col])
    check(f"Response % for {col}: counts match and total 100%", math.isclose(d["pct"].sum(), 100) and all(cnt[a] == n for a, n in zip(d.answer, d.n)), f"n={d.total.iloc[0]}")
dist = sc.rating_distribution(df)
check("Rating distributions sum to 100% for every question", all(math.isclose(g["pct"].sum(), 100) for _, g in dist.groupby("question")))
ben = sc.multi_choice(df); cnt = Counter(b.strip() for r in rows if r["benefits"] for b in r["benefits"].split(";"))
check("Benefit counts match an independent count", all(cnt[a] == n for a, n in zip(ben.answer, ben.n)), f"top: {ben.answer.iloc[0]} {ben.n.iloc[0]}")
check("NPS formula on small examples", math.isclose(sc.nps(pd.Series([10, 9, 8, 7, 6, 0]))["score"], 0) and math.isclose(sc.nps(pd.Series([9, 9, 9, 3]))["score"], 50),
      "[10,9,8,7,6,0] -> 0; [9,9,9,3] -> +50")
g = sc.group_means(df, "department", "q2_work_life_balance"); s = [num(r["q2_work_life_balance"]) for r in rows if r["department"] == "Support" and r["q2_work_life_balance"]]
check("Group average and n match (work-life balance, Support)", math.isclose(g.loc[g.department == "Support", "mean"].iloc[0], sum(s) / len(s)) and g.loc[g.department == "Support", "n"].iloc[0] == len(s), f"n={len(s)}")
check("Small groups are flagged (n < 30)", all(g["low_n"] == (g["n"] < sc.LOW_N)))

# 3. the Streamlit app itself
APP = os.path.join(ROOT, "dashboard", "app.py")
at = AppTest.from_file(APP, default_timeout=120).run()
check("Dashboard opens with no errors", not at.exception, f"{len(at.tabs)} tabs, {len(at.sidebar.multiselect)} filters")
exp = independent(rows)
shown = {m.label: m.value for m in at.metric}
check("KPI cards show the independent numbers (no filter)", shown["Responses"] == str(exp["n"]) and shown["Avg satisfaction (1-5)"] == f"{exp['avg']:.2f}"
      and shown["Satisfied (rated 4-5)"] == f"{exp['sat']:.1f}%" and shown["Net Promoter Score"] == f"{exp['nps']:+.0f}" and shown["Plan to stay (Yes)"] == f"{exp['stay']:.1f}%", str(shown))
at.multiselect(key="f_dept").set_value(["Support"]).run(); at.multiselect(key="f_round").set_value(["Round 3 (Jul 2026)"]).run()
exp = independent([r for r in rows if r["department"] == "Support" and r["round_no"] == "3"]); shown = {m.label: m.value for m in at.metric}
check("Filters work: Support + Round 3 cards match the independent numbers", not at.exception and shown["Responses"] == str(exp["n"]) and shown["Avg satisfaction (1-5)"] == f"{exp['avg']:.2f}"
      and shown["Net Promoter Score"] == f"{exp['nps']:+.0f}", f"n={exp['n']}, avg {exp['avg']:.2f}, NPS {exp['nps']:+.0f}")
at.multiselect(key="f_dept").set_value([]).run()
check("Filters that match nobody show a warning instead of crashing", not at.exception and len(at.warning) == 1)
at = AppTest.from_file(APP, default_timeout=120).run(); at.selectbox(key="g_dim").set_value("location").run(); at.selectbox(key="g_q").set_value("q3_manager_support").run()
check("Group comparison tab changes without errors", not at.exception)

bc = os.path.join(HERE, "browser_check.json")
if os.path.exists(bc):
    b = json.load(open(bc))
    for tab in ("Ratings", "Group comparison", "Trends", "Choices & NPS", "Comments"):
        check(f"Browser: '{tab}' tab draws its charts", b[tab]["charts_drawn"] >= b[tab]["expected_at_least"], f"{b[tab]['charts_drawn']} charts, screenshot {b[tab]['screenshot']}")
    check("Browser: opening ?dept=Support shows the Support-only numbers", b["Filtered view (?dept=Support)"]["kpi_values"][0] == str(independent([r for r in rows if r["department"] == "Support"])["n"]),
          "KPI cards: " + ", ".join(b["Filtered view (?dept=Support)"]["kpi_values"]))
    check("Browser: no JavaScript or console errors", not b["browser_errors"])

passed = sum(ok for _, ok, _ in results)
lines = ["# Test report", "", f"Run on {datetime.date.today().isoformat()} with `python tests/run_checks.py`. **{passed} of {len(results)} checks passed.**", "",
         "Method: each figure on the dashboard is re-calculated with plain Python (csv module), independent of pandas and the dashboard code, and compared. The dashboard itself is opened and driven with Streamlit's AppTest.", "",
         "| # | Check | Result | Detail |", "|---|---|---|---|"] + [f"| {i} | {n} | {'PASS' if ok else 'FAIL'} | {d} |" for i, (n, ok, d) in enumerate(results, 1)] + [
         "", "## Not covered", "- How the charts look is judged by eye in `screenshots/`; the checks only confirm they draw.", "- Browsers other than Chromium."]
open(os.path.join(ROOT, "docs", "test_report.md"), "w").write("\n".join(lines) + "\n")
print("\n".join(f"{'PASS' if ok else 'FAIL'}  {n}  {d}" for n, ok, d in results)); print(f"{passed}/{len(results)} passed")
sys.exit(0 if passed == len(results) else 1)
