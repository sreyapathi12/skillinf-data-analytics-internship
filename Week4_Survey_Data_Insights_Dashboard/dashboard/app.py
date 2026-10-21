"""Survey Data Insights Dashboard (Streamlit).

Run from this folder:   streamlit run app.py
Reads ../data/cleaned_survey_data.csv (personal details already removed).
"""
import os

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from scipy import stats

from survey_calcs import (BLUE, GRID, INK, INK2, LOW_N, MUTED, ORDINAL5, SERIES, SEQ, SURFACE, GROUPS, RATING_QUESTIONS,
                          STAY_ORDER, WORKLOAD_ORDER, group_means, kpis, load_clean, multi_choice, nps, rating_distribution,
                          rating_summary, single_choice, trend)

st.set_page_config(page_title="Survey Data Insights Dashboard", layout="wide")
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "cleaned_survey_data.csv")
QLABELS = list(RATING_QUESTIONS.values())


@st.cache_data
def load():
    return load_clean(DATA)


def show(chart):
    chart = (chart.configure(background=SURFACE).configure_view(stroke=None)
             .configure_axis(labelColor=MUTED, titleColor=INK2, gridColor=GRID, domainColor="#c3c2b7", tickColor="#c3c2b7", labelFontSize=12, titleFontSize=12)
             .configure_legend(labelColor=INK2, titleColor=INK2, labelFontSize=12, titleFontSize=12, orient="bottom")
             .configure_title(color=INK, fontSize=15, anchor="start"))
    st.altair_chart(chart, theme=None, width="stretch")


df_all = load()

# ---------------- sidebar filters (query-string values pre-select a view, e.g. ?dept=Support) ----------------
qp = st.query_params
def preset(key, options):
    wanted = [v for v in qp.get_all(key) if v in options]
    return wanted or options

st.sidebar.header("Filters")
opts = {k: sorted(df_all[c].unique()) for k, c in [("round", "survey_round"), ("dept", "department"), ("loc", "location"), ("age", "age_group"), ("tenure", "tenure")]}
f_round = st.sidebar.multiselect("Survey round", opts["round"], default=preset("round", opts["round"]), key="f_round")
f_dept = st.sidebar.multiselect("Department", opts["dept"], default=preset("dept", opts["dept"]), key="f_dept")
f_loc = st.sidebar.multiselect("Location", opts["loc"], default=preset("loc", opts["loc"]), key="f_loc")
f_age = st.sidebar.multiselect("Age group", opts["age"], default=preset("age", opts["age"]), key="f_age")
f_tenure = st.sidebar.multiselect("Tenure", opts["tenure"], default=preset("tenure", opts["tenure"]), key="f_tenure")
df = df_all[df_all.survey_round.isin(f_round) & df_all.department.isin(f_dept) & df_all.location.isin(f_loc)
            & df_all.age_group.isin(f_age) & df_all.tenure.isin(f_tenure)]

st.title("Survey Data Insights Dashboard")
st.caption(f"Employee engagement survey (sample data, 3 rounds). Showing **{len(df)}** of {len(df_all)} valid responses. "
           f"Every result shows its number of responses (n); groups under {LOW_N} responses are less reliable.")
if df.empty:
    st.warning("No responses match these filters. Select more options in the sidebar.")
    st.stop()

# ---------------- KPI cards ----------------
k = kpis(df)
c = st.columns(5)
c[0].metric("Responses", f"{k['responses']:,}", border=True)
c[1].metric("Avg satisfaction (1-5)", f"{k['avg_satisfaction']:.2f}", help=f"Average overall satisfaction rating; n = {k['n_q1']}", border=True)
c[2].metric("Satisfied (rated 4-5)", f"{k['pct_satisfied']:.1f}%", help=f"n = {k['n_q1']}", border=True)
c[3].metric("Net Promoter Score", f"{k['nps']:+.0f}", help=f"Promoters (9-10) minus detractors (0-6); n = {k['n_nps']}", border=True)
c[4].metric("Plan to stay (Yes)", f"{k['pct_staying']:.1f}%", help=f"Plan to stay for the next 12 months; n = {k['n_stay']}", border=True)

st.sidebar.divider()
st.sidebar.download_button("Download filtered data (CSV)", df.to_csv(index=False), file_name="filtered_survey_data.csv", mime="text/csv")
rs = rating_summary(df)
summary_md = "\n".join([
    "# Survey summary (current filters)", "",
    f"- Responses: {k['responses']}", f"- Average overall satisfaction: {k['avg_satisfaction']:.2f} (n={k['n_q1']})",
    f"- Satisfied (4-5): {k['pct_satisfied']:.1f}%", f"- NPS: {k['nps']:+.0f} (n={k['n_nps']})", f"- Plan to stay: {k['pct_staying']:.1f}% (n={k['n_stay']})", "",
    "| Question | n | Average | Most common | % favourable (4-5) |", "|---|---|---|---|---|"] +
    [f"| {r.question} | {r.n} | {r.mean:.2f} | {r.most_common} | {r.pct_favourable:.1f}% |" for r in rs.itertuples()])
st.sidebar.download_button("Download summary (Markdown)", summary_md, file_name="survey_summary.md", mime="text/markdown")

tab_r, tab_g, tab_t, tab_c, tab_m = st.tabs(["Ratings", "Group comparison", "Trends", "Choices & NPS", "Comments"])

# ---------------- Ratings ----------------
with tab_r:
    dist = rating_distribution(df)
    dist["label"] = dist["question"] + " (n=" + dist["n_total"].astype(str) + ")"
    order = [f"{q} (n={int(rs.loc[rs.question == q, 'n'].iloc[0])})" for q in QLABELS]
    show(alt.Chart(dist, title="How employees rated each statement").mark_bar(stroke=SURFACE, strokeWidth=1.5, size=26).encode(
        y=alt.Y("label:N", sort=order, title=None, axis=alt.Axis(labelLimit=260)),
        x=alt.X("pct:Q", title="% of valid responses", scale=alt.Scale(domain=[0, 100]), axis=alt.Axis(values=[0, 20, 40, 60, 80, 100])),
        color=alt.Color("rating:O", scale=alt.Scale(domain=[1, 2, 3, 4, 5], range=ORDINAL5), legend=alt.Legend(title="Rating (1 = lowest, 5 = highest)", orient="bottom")),
        order=alt.Order("rating:O"),
        tooltip=[alt.Tooltip("question:N", title="Question"), alt.Tooltip("rating:O", title="Rating"), alt.Tooltip("n:Q", title="Responses"),
                 alt.Tooltip("pct:Q", title="% of valid", format=".1f"), alt.Tooltip("n_total:Q", title="n (question)")]).properties(height=300))
    st.subheader("Rating summary")
    st.dataframe(rs.drop(columns="column").rename(columns={"question": "Question", "n": "n", "mean": "Average", "median": "Median", "most_common": "Most common answer",
                                                         "pct_favourable": "% favourable (4-5)"}).round(2), hide_index=True, width="stretch")

# ---------------- Group comparison ----------------
with tab_g:
    a, b = st.columns(2)
    gcol = a.selectbox("Compare by", list(GROUPS), format_func=GROUPS.get, key="g_dim")
    qcol = b.selectbox("Question", list(RATING_QUESTIONS), format_func=RATING_QUESTIONS.get, key="g_q")
    g = group_means(df[df[gcol] != "Not specified"], gcol, qcol).dropna(subset=["mean"]).sort_values("mean")
    g["label"] = g[gcol] + " (n=" + g["n"].astype(str) + np.where(g["low_n"], ", low n", "") + ")"
    g["lo"], g["hi"] = g["mean"] - g["ci"].fillna(0), g["mean"] + g["ci"].fillna(0)
    base = alt.Chart(g, title=f"{RATING_QUESTIONS[qcol]} by {GROUPS[gcol].lower()}").encode(
        y=alt.Y("label:N", sort=list(g["label"]), title=None, axis=alt.Axis(labelLimit=240)))
    rule = base.mark_rule(color=BLUE, strokeWidth=2).encode(x=alt.X("lo:Q", title="Average rating (dot) with 95% confidence range", scale=alt.Scale(zero=False), axis=alt.Axis(tickCount=6)), x2="hi:Q")
    dots = base.mark_point(size=130, color=BLUE, filled=True, opacity=1, stroke=SURFACE, strokeWidth=2).encode(
        x="mean:Q", fill=alt.condition("datum.low_n", alt.value(SURFACE), alt.value(BLUE)), stroke=alt.condition("datum.low_n", alt.value(BLUE), alt.value(SURFACE)),
        tooltip=[alt.Tooltip(f"{gcol}:N", title=GROUPS[gcol]), alt.Tooltip("n:Q", title="Responses (n)"), alt.Tooltip("mean:Q", title="Average", format=".2f"),
                 alt.Tooltip("lo:Q", title="95% range from", format=".2f"), alt.Tooltip("hi:Q", title="to", format=".2f")])
    show((rule + dots).properties(height=max(160, 52 * len(g))))
    pfmt = lambda v: "p < 0.001" if v < 0.001 else f"p = {v:.3f}"
    ok = g[g["n"] >= LOW_N]
    if len(ok) >= 2:
        p = stats.kruskal(*[df.loc[df[gcol] == x, qcol].dropna() for x in ok[gcol]]).pvalue
        hi_, lo_ = ok.iloc[-1], ok.iloc[0]
        gap = hi_["mean"] - lo_["mean"]
        if gap >= 0.30 and p < 0.05:
            st.success(f"Clear difference: {hi_[gcol]} averages {hi_['mean']:.2f} vs {lo_[gcol]} {lo_['mean']:.2f} (gap {gap:.2f}, {pfmt(p)}; groups with n >= {LOW_N}).")
        else:
            st.info(f"No clear difference: highest vs lowest group gap is {gap:.2f} ({pfmt(p)}). A clear difference needs a gap of at least 0.30 and p < 0.05.")
    else:
        st.info(f"Fewer than two groups have {LOW_N}+ responses under the current filters, so no comparison is made.")
    st.caption(f"Hollow dots = fewer than {LOW_N} responses (less reliable). Excludes 'Not specified'.")

    rows = []
    sizes = df[df[gcol] != "Not specified"].groupby(gcol).size()
    for col_, lab in RATING_QUESTIONS.items():
        gm = group_means(df[df[gcol] != "Not specified"], gcol, col_)
        rows += [dict(group=f"{r[gcol]} (n={sizes[r[gcol]]})", question=lab, mean=r["mean"], valid_n=int(r["n"])) for _, r in gm.iterrows()]
    heat = pd.DataFrame(rows).dropna()
    ch = alt.Chart(heat, title=f"Average rating by {GROUPS[gcol].lower()} and question")
    h = ch.mark_rect(stroke=SURFACE, strokeWidth=2).encode(
        x=alt.X("question:N", sort=QLABELS, title=None, axis=alt.Axis(labelAngle=0, labelLimit=140)), y=alt.Y("group:N", title=None, axis=alt.Axis(labelLimit=240)),
        color=alt.Color("mean:Q", scale=alt.Scale(range=SEQ), legend=alt.Legend(title="Average rating")),
        tooltip=[alt.Tooltip("group:N", title="Group"), alt.Tooltip("question:N", title="Question"), alt.Tooltip("mean:Q", title="Average", format=".2f"), alt.Tooltip("valid_n:Q", title="Valid answers (n)")])
    t = ch.mark_text(fontSize=13).encode(x=alt.X("question:N", sort=QLABELS), y="group:N", text=alt.Text("mean:Q", format=".2f"),
                                         color=alt.condition(alt.datum.mean > heat["mean"].mean(), alt.value("white"), alt.value(INK)))
    show((h + t).properties(height=max(140, 48 * heat["group"].nunique())))
    with st.expander("Table view"):
        st.dataframe(heat.pivot(index="group", columns="question", values="mean")[QLABELS].round(2), width="stretch")

# ---------------- Trends ----------------
with tab_t:
    picked = st.multiselect("Questions", QLABELS, default=QLABELS, key="t_q")
    tr = trend(df)
    tr = tr[tr.question.isin(picked)]
    if tr.empty:
        st.info("Select at least one question.")
    else:
        rounds_n = df.groupby("survey_round").size()
        tr["round_label"] = tr["survey_round"] + " (n=" + tr["survey_round"].map(rounds_n).astype(str) + ")"
        order_r = list(tr.sort_values("round_no")["round_label"].unique())
        line = alt.Chart(tr, title="Average rating by survey round").mark_line(strokeWidth=2.5, point=alt.OverlayMarkDef(size=90, filled=True, stroke=SURFACE, strokeWidth=2)).encode(
            x=alt.X("round_label:N", sort=order_r, title=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y("mean:Q", title="Average rating (1-5)", scale=alt.Scale(zero=False)),
            color=alt.Color("question:N", scale=alt.Scale(domain=QLABELS, range=SERIES), legend=alt.Legend(title=None, orient="bottom", columns=5)),
            tooltip=[alt.Tooltip("question:N", title="Question"), alt.Tooltip("survey_round:N", title="Round"), alt.Tooltip("mean:Q", title="Average", format=".2f"), alt.Tooltip("n:Q", title="Responses (n)")])
        show(line.properties(height=360))
        with st.expander("Table view"):
            st.dataframe(tr.pivot(index="question", columns="round_label", values="mean").round(2), width="stretch")
    nr = pd.DataFrame([dict(round=r, score=nps(g["q6_recommend"])["score"], n=nps(g["q6_recommend"])["n"]) for r, g in df.groupby("survey_round")])
    nr["label"] = nr["round"] + " (n=" + nr["n"].astype(str) + ")"
    bars = alt.Chart(nr, title="Net Promoter Score by round").encode(x=alt.X("label:N", sort=list(nr["label"]), title=None, axis=alt.Axis(labelAngle=0)),
                                                                     y=alt.Y("score:Q", title="NPS"), tooltip=[alt.Tooltip("round:N", title="Round"), alt.Tooltip("score:Q", title="NPS", format="+.1f"), alt.Tooltip("n:Q", title="Responses (n)")])
    show((bars.mark_bar(color=BLUE, size=60) + bars.mark_text(dy=-8, color=INK2, fontSize=13).encode(text=alt.Text("score:Q", format="+.0f"))).properties(height=260))
    st.caption("Each round surveyed different (anonymous) employees, so this compares group averages, not the same people. Look for clear changes, not tiny ones.")

# ---------------- Choices & NPS ----------------
with tab_c:
    left, right = st.columns(2)
    nn = nps(df["q6_recommend"])
    cats = ["Detractor (0-6)", "Passive (7-8)", "Promoter (9-10)"]
    nd = pd.DataFrame({"category": cats, "n": [nn["detractors"], nn["passives"], nn["promoters"]], "order": [1, 2, 3]})
    nd["pct"] = 100 * nd["n"] / max(nn["n"], 1)
    arc = alt.Chart(nd, title=f"Likelihood to recommend (n={nn['n']})").mark_arc(innerRadius=62, outerRadius=105, stroke=SURFACE, strokeWidth=3).encode(
        theta=alt.Theta("n:Q", stack=True), order=alt.Order("order:Q"),
        color=alt.Color("category:N", scale=alt.Scale(domain=cats, range=[ORDINAL5[0], ORDINAL5[2], ORDINAL5[4]]), legend=alt.Legend(title=None, orient="bottom")),
        tooltip=[alt.Tooltip("category:N", title="Group"), alt.Tooltip("n:Q", title="Responses"), alt.Tooltip("pct:Q", title="%", format=".1f")])
    centre = alt.Chart(pd.DataFrame({"t": [f"NPS {nn['score']:+.0f}"]})).mark_text(size=26, fontWeight="bold", color=INK).encode(text="t:N")
    with left: show((arc + centre).properties(height=330))

    def choice_bar(d, title, color=BLUE):
        d = d.assign(label=d["answer"], txt=d["pct"].map(lambda v: f"{v:.0f}%"))
        base = alt.Chart(d, title=f"{title} (n={int(d['total'].iloc[0]) if len(d) else 0})").encode(
            x=alt.X("label:N", sort=list(d["label"]), title=None, axis=alt.Axis(labelAngle=0, labelLimit=240)), y=alt.Y("pct:Q", title="% of responses", scale=alt.Scale(domain=[0, max(float(d["pct"].max()), 1) * 1.2])),
            tooltip=[alt.Tooltip("answer:N", title="Answer"), alt.Tooltip("n:Q", title="Responses"), alt.Tooltip("pct:Q", title="%", format=".1f")])
        return (base.mark_bar(color=color, size=44) + base.mark_text(dy=-8, color=INK2, fontSize=12).encode(text="txt:N")).properties(height=290)
    with right: show(choice_bar(single_choice(df, "q8_stay_next_12_months", STAY_ORDER), "Plan to stay for the next 12 months?"))
    show(choice_bar(single_choice(df, "q7_workload", WORKLOAD_ORDER), "How manageable is your workload?"))
    ben = multi_choice(df); ben["txt"] = ben["pct"].map(lambda v: f"{v:.0f}%")
    bb = alt.Chart(ben, title=f"Benefits employees value most (n={int(ben['total'].iloc[0]) if len(ben) else 0}, up to 3 choices each)").encode(
        y=alt.Y("answer:N", sort="-x", title=None), x=alt.X("pct:Q", title="% of respondents", axis=alt.Axis(tickCount=5)),
        tooltip=[alt.Tooltip("answer:N", title="Benefit"), alt.Tooltip("n:Q", title="Respondents"), alt.Tooltip("pct:Q", title="%", format=".1f")])
    show((bb.mark_bar(color=BLUE, size=22) + bb.mark_text(align="left", dx=5, color=INK2, fontSize=12).encode(text="txt:N")).properties(height=300))
    with st.expander("Table view"):
        st.dataframe(ben.rename(columns={"answer": "Benefit", "n": "Respondents", "total": "Valid n", "pct": "% of respondents"}).round(1), hide_index=True, width="stretch")

# ---------------- Comments ----------------
with tab_m:
    cm = df.dropna(subset=["comment"])
    st.write(f"**{len(cm)}** of {len(df)} respondents ({100 * len(cm) / len(df):.0f}%) left a comment. Themes are tagged with simple keyword rules, so they are approximate.")
    th = cm["comment_theme"].value_counts().rename_axis("theme").reset_index(name="n")
    th["pct"] = 100 * th["n"] / max(len(cm), 1); th["txt"] = th["pct"].map(lambda v: f"{v:.0f}%")
    if len(th):
        tb = alt.Chart(th, title=f"What employees wrote about (n={len(cm)} comments)").encode(
            y=alt.Y("theme:N", sort="-x", title=None), x=alt.X("pct:Q", title="% of comments"),
            tooltip=[alt.Tooltip("theme:N", title="Theme"), alt.Tooltip("n:Q", title="Comments"), alt.Tooltip("pct:Q", title="%", format=".1f")])
        show((tb.mark_bar(color=BLUE, size=22) + tb.mark_text(align="left", dx=5, color=INK2, fontSize=12).encode(text="txt:N")).properties(height=300))
        pick = st.selectbox("Show comments about", ["All"] + list(th["theme"]), key="c_theme")
        shown = cm if pick == "All" else cm[cm.comment_theme == pick]
        st.dataframe(shown[["date", "survey_round", "department", "comment_theme", "comment"]].rename(columns={"survey_round": "round", "comment_theme": "theme"}).head(300),
                     hide_index=True, width="stretch")
    st.caption("Comments are anonymous and contain no names, e-mails or phone numbers.")
