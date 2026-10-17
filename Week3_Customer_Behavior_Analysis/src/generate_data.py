"""Generate the SYNTHETIC customer purchase dataset used in Week 3.

Creates data/raw_transactions.csv with realistic buying patterns (festive-season
peak, weekend lift, product pairs, loyal vs one-time customers) and deliberately
messy values (duplicates, mixed date formats, text prices, inconsistent text,
blanks, negative quantities) so the cleaning step in the notebook has real work to do.
Run:  python src/generate_data.py
"""
import csv, os, random, datetime as dt

random.seed(11)
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "data", "raw_transactions.csv")

PRODUCTS = [  # name, category, unit price (INR), popularity weight
    ("Wireless Earbuds", "Electronics", 1999, 10), ("Smartwatch", "Electronics", 4999, 3),
    ("Power Bank", "Electronics", 1299, 8), ("Bluetooth Speaker", "Electronics", 2499, 4),
    ("Water Bottle", "Home & Kitchen", 499, 7), ("Desk Lamp", "Home & Kitchen", 899, 4),
    ("Cushion Set", "Home & Kitchen", 799, 3), ("Cotton T-Shirt", "Fashion", 599, 9),
    ("Running Shoes", "Fashion", 2999, 4), ("Backpack", "Fashion", 1499, 5),
    ("Protein Powder", "Health & Wellness", 1799, 4), ("Green Tea Pack", "Health & Wellness", 349, 8),
]
PAIRS = {"Wireless Earbuds": "Power Bank", "Running Shoes": "Cotton T-Shirt",
         "Protein Powder": "Water Bottle", "Desk Lamp": "Cushion Set", "Smartwatch": "Wireless Earbuds"}
CATS = sorted({p[1] for p in PRODUCTS})
CITIES = ["Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Chennai", "Pune", "Kolkata", "Jaipur"]
CITY_W = [18, 18, 18, 12, 10, 9, 8, 7]
MONTH_W = {(2025,10):1.3,(2025,11):1.5,(2025,12):1.2,(2026,1):.9,(2026,2):.8,(2026,3):.9,
           (2026,4):.9,(2026,5):1.0,(2026,6):.9,(2026,7):.9,(2026,8):1.0,(2026,9):1.0}
START = dt.date(2025, 10, 1)
DAYS = [START + dt.timedelta(i) for i in range(365)]
DAY_W = [MONTH_W[(d.year, d.month)] * (1.35 if d.weekday() >= 5 else 1.0) for d in DAYS]
by_name = {p[0]: p for p in PRODUCTS}

def pick_product(fav):
    pool = [p for p in PRODUCTS if p[1] == fav] if random.random() < 0.6 else PRODUCTS
    return random.choices(pool, weights=[p[3] for p in pool])[0][0]

orders = []
for i in range(1, 301):
    r = random.random()
    if r < 0.20: kind, n = "loyal", max(7, round(random.gauss(12, 3)))
    elif r < 0.60: kind, n = "regular", max(2, round(random.gauss(4.5, 1.3)))
    elif r < 0.90: kind, n = "occasional", random.randint(1, 2)
    else: kind, n = "lapsed", random.randint(1, 2)
    end = None
    if kind in ("loyal", "regular") and random.random() < 0.28: end = START + dt.timedelta(random.randint(120, 260))
    if kind == "lapsed": end = START + dt.timedelta(random.randint(60, 150))
    allowed = [(d, w) for d, w in zip(DAYS, DAY_W) if end is None or d <= end]
    cid, city, fav = f"C{i:04d}", random.choices(CITIES, CITY_W)[0], random.choice(CATS)
    for d in random.choices([a[0] for a in allowed], weights=[a[1] for a in allowed], k=n):
        items = [pick_product(fav)]
        if items[0] in PAIRS and random.random() < 0.28: items.append(PAIRS[items[0]])
        elif random.random() < 0.10: items.append(pick_product(fav))
        if random.random() < 0.08: items.append(pick_product(fav))
        items = list(dict.fromkeys(items))  # distinct products per order
        pay = random.choices(["UPI", "Card", "COD", "Wallet"], [.5, .3, .15, .05])[0]
        orders.append((d, cid, city, pay, items))
orders.sort(key=lambda o: o[0])

rows = []
for k, (d, cid, city, pay, items) in enumerate(orders, 1):
    for name in items:
        _, cat, price, _ = by_name[name]
        qty = random.choice([1, 1, 2, 3]) if price < 1000 else random.choice([1, 1, 1, 2])
        rows.append(dict(order_id=f"ORD-{10000+k}", customer_id=cid, order_date=d, product=name,
                         category=cat, unit_price=price, quantity=qty, payment_method=pay, city=city))

# ---- make it messy ----
fmts = ["%Y-%m-%d", "%d/%m/%Y", "%d-%b-%Y"]
for r in rows:
    r["order_date"] = r["order_date"].strftime(random.choices(fmts, [.5, .3, .2])[0])
    if r["city"] == "Bengaluru" and random.random() < 0.4: r["city"] = "Bangalore"
    elif random.random() < 0.04: r["city"] = random.choice([r["city"].lower(), r["city"] + " "])
idx = list(range(len(rows))); random.shuffle(idx)
take = lambda k: [idx.pop() for _ in range(k)]
for i in take(15): rows[i]["quantity"] = ""
for i in take(5): rows[i]["quantity"] = -abs(rows[i]["quantity"])
for i in take(20): rows[i]["customer_id"] = ""
for i in take(25): rows[i]["payment_method"] = ""
for i in take(60): rows[i]["unit_price"] = f"Rs. {rows[i]['unit_price']:,}"
for i in take(55):
    c = rows[i]["category"]; rows[i]["category"] = random.choice([c.lower(), c.upper(), c + " "])
for i in random.sample(range(len(rows)), 30):          # exact duplicate rows
    rows.insert(random.randint(0, len(rows)), dict(rows[i]))

cols = ["order_id","customer_id","order_date","product","category","unit_price","quantity","payment_method","city"]
with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
print(f"wrote {len(rows)} rows, {len(orders)} orders to {os.path.normpath(OUT)}")
