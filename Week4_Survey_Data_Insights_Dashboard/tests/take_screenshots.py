"""Open the dashboard in a real browser, check every tab draws its charts, and save screenshots.

Needs:  pip install playwright   and a Chromium browser (playwright install chromium).
Run:    python tests/take_screenshots.py
Writes: screenshots/*.png and tests/browser_check.json
"""
import glob, json, os, subprocess, sys, time, urllib.request
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
PORT = 8599; URL = f"http://localhost:{PORT}"
server = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "app.py", "--server.headless", "true", "--server.port", str(PORT),
                           "--browser.gatherUsageStats", "false"], cwd=os.path.join(ROOT, "dashboard"), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    for _ in range(60):
        try:
            if urllib.request.urlopen(f"{URL}/_stcore/health", timeout=2).read() == b"ok": break
        except Exception: time.sleep(1)
    chrome = (glob.glob("/opt/pw-browsers/chromium-*/chrome-linux*/chrome") or [None])[0]
    report = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=chrome) if chrome else p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1900}, device_scale_factor=1)
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        def ready(expect_charts=1):
            page.wait_for_selector("text=Survey Data Insights Dashboard"); page.wait_for_timeout(2500)
            for _ in range(20):
                if page.locator('[data-testid="stVegaLiteChart"]:visible').count() >= expect_charts: break
                page.wait_for_timeout(500)
            page.wait_for_timeout(800)
        page.goto(URL); ready()
        tabs = [("Ratings", "01_ratings", 1), ("Group comparison", "02_group_comparison", 2), ("Trends", "03_trends", 2), ("Choices & NPS", "04_choices_and_nps", 4), ("Comments", "05_comments", 1)]
        for name, shot, expect in tabs:
            if name != "Ratings": page.get_by_role("tab", name=name).click(); page.wait_for_timeout(1500)
            ready(expect)
            n = page.locator('[data-testid="stVegaLiteChart"]:visible').count()
            page.screenshot(path=os.path.join(ROOT, "screenshots", f"{shot}.png")); report[name] = {"charts_drawn": n, "expected_at_least": expect, "screenshot": f"screenshots/{shot}.png"}
        page.goto(f"{URL}/?dept=Support"); ready()
        kpi = page.locator('[data-testid="stMetricValue"]').all_inner_texts()
        page.screenshot(path=os.path.join(ROOT, "screenshots", "06_filtered_support_department.png"))
        report["Filtered view (?dept=Support)"] = {"kpi_values": kpi, "screenshot": "screenshots/06_filtered_support_department.png"}
        report["browser_errors"] = [e for e in errors if "favicon" not in e][:5]
        browser.close()
    json.dump(report, open(os.path.join(HERE, "browser_check.json"), "w"), indent=2)
    print(json.dumps(report, indent=1))
finally:
    server.terminate()
