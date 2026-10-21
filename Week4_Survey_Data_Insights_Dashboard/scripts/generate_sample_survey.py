"""Create the SAMPLE (synthetic) employee survey used in Week 4.

Writes data/raw_survey_responses.csv - an export that looks like a real form tool's
output: personal details (name, email, phone), mixed date formats, ratings stored as
text, inconsistent spellings, duplicates, repeat submissions, test entries and
incomplete responses. The cleaning notebook fixes all of that.
Run:  python scripts/generate_sample_survey.py
"""
import csv, os, random, datetime as dt

random.seed(2026)
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "data", "raw_survey_responses.csv")

DEPTS = ["Engineering", "Sales", "Support", "HR & Admin", "Finance"]
DEPT_W = [32, 20, 22, 12, 14]
DEPT_FX = {  # offsets on q1..q5 means
    "Engineering": [0.10, -0.05, 0.00, 0.25, -0.30], "Sales": [0.00, -0.20, 0.10, 0.00, 0.35],
    "Support": [-0.35, -0.45, -0.15, -0.10, -0.10], "HR & Admin": [0.15, 0.20, 0.20, 0.05, 0.00],
    "Finance": [0.05, 0.10, 0.00, -0.10, 0.10]}
LOCS = ["Bengaluru", "Pune", "Hyderabad", "Remote"]; LOC_W = [35, 20, 20, 25]
LOC_FX = {"Remote": [0, 0.30, -0.10, 0, 0]}
TENURE = ["Less than 1 year", "1-3 years", "3+ years"]; TEN_W = [30, 40, 30]
TEN_FX = {"Less than 1 year": [0.15, 0, 0, 0, 0], "3+ years": [-0.10, 0, 0, 0, 0]}
BASE = [3.7, 3.5, 3.9, 3.4, 3.2]
ROUND_FX = {1: [0, 0, 0, 0, 0], 2: [0.10, 0.10, 0.10, 0.05, 0], 3: [0.20, 0.20, 0.15, 0.10, 0]}
ROUNDS = {1: (dt.date(2026, 1, 5), 26), 2: (dt.date(2026, 4, 6), 24), 3: (dt.date(2026, 7, 6), 25)}
BENEFITS = ["Health insurance", "Flexible hours", "Learning budget", "Remote work", "Paid leave", "Performance bonus", "Wellness programs"]
BEN_BASE = [10, 8, 6, 7, 9, 6, 4]
BEN_DEPT = {"Engineering": {"Learning budget": 5, "Remote work": 4}, "Sales": {"Performance bonus": 6},
            "Support": {"Flexible hours": 5, "Wellness programs": 4}, "HR & Admin": {"Paid leave": 3}, "Finance": {"Performance bonus": 3}}
COMMENTS = {
 "workload": ["Workload gets too heavy at month end, we need more people on the team.", "Too many urgent tasks at once, please plan the work better.",
              "Deadlines are tight and overtime is becoming normal.", "Please balance the workload across team members."],
 "growth": ["I would like clearer promotion paths and more training.", "There are few chances to learn new skills in my current role.",
            "Please fund certifications and courses.", "A mentoring programme would help my career growth."],
 "pay": ["Salary reviews should happen more often and be more transparent.", "Pay is below market for my role.", "Please explain how bonuses are decided."],
 "communication": ["Leadership should share company plans more openly.", "Updates from management are often late or unclear.", "More regular team meetings would help us stay aligned."],
 "flexibility": ["Allow more flexible working hours.", "A hybrid option for all teams would help a lot.", "Let us choose our working hours around personal needs."],
 "tools": ["Our internal tools are slow and outdated.", "Better software and equipment would save a lot of time."],
 "positive": ["Happy with the team, nothing major to change.", "Great colleagues and a supportive manager.", "Keep up the good work, the culture is good."],
}
FIRST = ["Aarav", "Priya", "Rohan", "Sneha", "Vikram", "Ananya", "Karthik", "Meera", "Arjun", "Divya", "Imran", "Neha", "Rahul", "Pooja", "Suresh", "Kavya", "Nikhil", "Isha", "Manoj", "Tara"]
LAST = ["Sharma", "Reddy", "Mehta", "Iyer", "Singh", "Das", "Nair", "Joshi", "Rao", "Menon", "Khan", "Gupta", "Patel", "Verma", "Kulkarni"]
clip = lambda x, lo, hi: max(lo, min(hi, x))
wchoice = lambda items, w: random.choices(items, w)[0]

def make_person(i, rnd):
    dept, loc, ten = wchoice(DEPTS, DEPT_W), wchoice(LOCS, LOC_W), wchoice(TENURE, TEN_W)
    age = int(clip(random.gauss(32, 8), 21, 58))
    lat = []
    for q in range(5):
        m = BASE[q] + DEPT_FX[dept][q] + LOC_FX.get(loc, [0] * 5)[q] + TEN_FX.get(ten, [0] * 5)[q] + ROUND_FX[rnd][q]
        lat.append(random.gauss(m, 0.85))
    q = [int(clip(round(x), 1, 5)) for x in lat]
    rec = int(clip(round(2.0 * lat[0] + 0.8 + random.gauss(0, 1.3)), 0, 10))
    ov = lat[1] + random.gauss(0, 0.5) - (0.4 if dept == "Support" else 0)
    workload = ("Very manageable" if ov > 4.0 else "Manageable" if ov > 3.2 else "Sometimes overwhelming" if ov > 2.5 else "Often overwhelming")
    s = lat[0] + random.gauss(0, 0.6)
    stay = "Yes" if s > 3.5 else "Not sure" if s > 2.7 else "No"
    w = [b + BEN_DEPT.get(dept, {}).get(n, 0) for n, b in zip(BENEFITS, BEN_BASE)]
    ben = []
    while len(ben) < random.choice([2, 3, 3]):
        c = wchoice(BENEFITS, w)
        if c not in ben: ben.append(c)
    weakest = min(range(1, 5), key=lambda k: lat[k])  # q2..q5
    if random.random() < 0.62:
        theme = ["workload", "growth", "pay", "flexibility"][weakest - 1] if random.random() < 0.7 else random.choice(list(COMMENTS))
        if lat[0] > 4.3 and random.random() < 0.6: theme = "positive"
        comment = random.choice(COMMENTS[theme])
    else:
        comment = ""
    d0, span = ROUNDS[rnd]
    ts = dt.datetime.combine(d0 + dt.timedelta(random.randint(0, span)), dt.time(random.randint(8, 19), random.randint(0, 59)))
    first, last = random.choice(FIRST), random.choice(LAST)
    return dict(response_id=f"RSP-{i:04d}", timestamp=ts, respondent_name=f"{first} {last}", email=f"{first}.{last}{i}@example.com".lower(),
                phone=f"+91 9{random.randint(0,9)}{random.randint(1000,9999)} {random.randint(10000,99999)}", department=dept, location=loc,
                age=age, tenure=ten, q1_overall_satisfaction=q[0], q2_work_life_balance=q[1], q3_manager_support=q[2], q4_career_growth=q[3],
                q5_compensation_fairness=q[4], q6_recommend=rec, q7_workload=workload, q8_stay_next_12_months=stay,
                q9_valued_benefits="; ".join(ben), q10_comment=comment)

rows, i = [], 1
for rnd, n in [(1, 135), (2, 140), (3, 145)]:
    for _ in range(n): rows.append(make_person(i, rnd)); i += 1

RATING = ["q1_overall_satisfaction", "q2_work_life_balance", "q3_manager_support", "q4_career_growth", "q5_compensation_fairness"]
ALLQ = RATING + ["q6_recommend", "q7_workload", "q8_stay_next_12_months", "q9_valued_benefits", "q10_comment"]
words = {1: "one", 2: "Two", 3: "three", 4: "Four", 5: "five"}
idx = list(range(len(rows))); random.shuffle(idx)
take = lambda k: [idx.pop() for _ in range(k)]

for r in rows:                                   # skipped optional questions
    for c in RATING + ["q6_recommend"]:
        if random.random() < 0.015: r[c] = ""
    if random.random() < 0.02: r["q7_workload"] = ""
    if random.random() < 0.02: r["q9_valued_benefits"] = ""
for k in take(30):                               # ratings typed as text
    c = random.choice(RATING); v = rows[k][c]
    if v != "": rows[k][c] = random.choice([f"{v} - Agree", words[v], f"{v}.0", f" {v}"])
for k in take(6):                                # impossible values
    rows[k][random.choice(RATING)] = random.choice([0, 6, 55, -1])
rows[take(1)[0]]["q6_recommend"] = 11
for r in rows:                                   # inconsistent spellings
    if random.random() < 0.08: r["department"] = random.choice([r["department"].lower(), r["department"].upper(), r["department"] + " "])
    if r["location"] == "Bengaluru" and random.random() < 0.3: r["location"] = random.choice(["Bangalore", "bangalore", "BENGALURU"])
    elif random.random() < 0.05: r["location"] = random.choice([r["location"].lower(), r["location"] + " "])
    if random.random() < 0.15: r["q8_stay_next_12_months"] = random.choice([r["q8_stay_next_12_months"].lower(), r["q8_stay_next_12_months"].upper(), r["q8_stay_next_12_months"] + " "])
    if random.random() < 0.12: r["q9_valued_benefits"] = random.choice([r["q9_valued_benefits"].lower(), r["q9_valued_benefits"].replace("; ", ";"), r["q9_valued_benefits"].replace("; ", " ;  ")])
for k in take(8): rows[k]["department"] = ""
for k in take(3): rows[k]["age"] = random.choice([5, 150, 0])
for k in take(10): rows[k]["age"] = ""

dup_src = random.sample(range(len(rows)), 12)                    # exact duplicate rows
resub = []
for k in random.sample(range(len(rows)), 6):                     # same person submits twice in a round
    r = dict(rows[k]); r["response_id"] = f"RSP-{9000 + k}"
    r["timestamp"] = r["timestamp"] + dt.timedelta(hours=random.randint(1, 30))
    r["q1_overall_satisfaction"] = clip(int(r["q1_overall_satisfaction"] or 3) + random.choice([-1, 1]), 1, 5)
    resub.append(r)
incomplete = []
for _ in range(15):                                              # mostly-empty submissions
    p = make_person(9500 + _, random.choice([1, 2, 3]))
    for c in ALLQ[2:]: p[c] = ""
    p["q1_overall_satisfaction"] = random.choice([p["q1_overall_satisfaction"], ""])
    incomplete.append(p)
tests = []
for t in range(3):
    p = make_person(9800 + t, random.choice([1, 2, 3])); p["respondent_name"] = "test"; p["email"] = "test@test.com"; tests.append(p)

fmts = ["%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M", "%b %d, %Y %I:%M %p"]
allrows = rows + [dict(rows[k]) for k in dup_src] + resub + incomplete + tests
for r in allrows:
    if isinstance(r["timestamp"], dt.datetime): r["timestamp"] = r["timestamp"].strftime(fmts[int(r["response_id"][4:]) % 3])
random.shuffle(allrows)
cols = ["response_id", "timestamp", "respondent_name", "email", "phone", "department", "location", "age", "tenure"] + ALLQ
with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(allrows)
print(f"wrote {len(allrows)} rows ({len(rows)} genuine base responses) to {os.path.normpath(OUT)}")
