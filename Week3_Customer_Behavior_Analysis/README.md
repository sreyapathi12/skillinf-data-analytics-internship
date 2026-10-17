# Week 3 – Customer Behavior Analysis

## Objective
Analyse customer purchase records to discover popular products, buying patterns and customer segments. Clean and transform the data with Python (Pandas), visualise the results, and provide a concise report of actionable insights.

## Files
- `customer_behavior_analysis.ipynb` – the full analysis (executed, with outputs and charts)
- `REPORT.md` – concise report of findings and recommended actions
- `charts/` – the six charts used in the report
- `data/raw_transactions.csv` – messy input data
- `data/clean_transactions.csv` – cleaned data
- `data/customer_segments.csv` – recency, frequency, spend and segment per customer
- `data/insights.json` – the key numbers quoted in the report
- `src/generate_data.py` – creates the synthetic dataset (sample data, not a real retailer)

## What was done
1. **Clean and transform (Pandas):** removed duplicates, recovered blanks from the same order, converted mixed date formats and text prices, standardised text, fixed quantities. 1,762 raw rows became 1,720 (log in the notebook).
2. **Popular products:** units, revenue and category share per product.
3. **Buying patterns:** monthly seasonality, weekday pattern, payment mix, basket size, products bought together (support and lift).
4. **Customer segments:** RFM (recency, frequency, monetary) with five rule-based segments.
5. **Report:** five findings, each with a recommended action.

## Headline results
- Revenue ₹29.99 lakh from 1,388 orders and 300 customers.
- Electronics is 43% of revenue; Oct–Dec is 42%.
- Champions are 20% of customers and 45% of revenue.

## Run it yourself
```
pip install -r requirements.txt
python src/generate_data.py
jupyter notebook customer_behavior_analysis.ipynb
```

## Tools
Python, Pandas, NumPy, Matplotlib, Seaborn, Jupyter
