# Retail Sales Analysis — End-to-End Data Analytics Portfolio Project

A production-style analysis of a simulated pan-India retail chain (2023–2025):
data generation & cleaning, SQL analysis, Python EDA/ML, and an executive
dashboard — built to demonstrate the full analyst workflow from messy raw
export to decision-ready insight.

## Business Questions Answered

- Where is revenue and profit growing or shrinking, and when (seasonality, YoY)?
- Which regions, states, categories, and products drive profit vs. just volume?
- Who are the highest-value customers, and how much of revenue depends on repeat buyers?
- Which categories/discount bands drive the most returns, and what's the profit leakage?
- Does shipping mode or delivery speed relate to returns?
- Can customers be segmented into actionable marketing groups (RFM + K-Means)?

## Project Structure

```
retail_project/
├── data/
│   ├── retail_sales_raw.csv            # 60,320 rows — intentionally messy source extract
│   ├── retail_sales_clean.csv          # 58,799 rows — analysis-ready dataset
│   ├── retail_sales.db                 # SQLite build of the clean data (for the SQL scripts)
│   ├── customer_rfm.csv                # RFM scores + K-Means cluster per customer
│   └── daily_sales_timeseries.csv      # Daily series with calendar features, forecasting-ready
├── sql/
│   └── retail_sales_analysis.sql       # 36 queries — aggregates, window functions, CTEs, CLV, ranking
├── notebooks/
│   └── Retail_Sales_Analysis.ipynb     # Full Python EDA, feature engineering, RFM, K-Means, forecasting prep
├── dashboard/
│   ├── retail_executive_dashboard.html # Self-contained, interactive executive dashboard (open in any browser)
│   └── PowerBI_Build_Guide.md          # Data model + DAX measures to rebuild natively in Power BI Desktop
├── reports/
│   ├── data_cleaning_log.md            # What was fixed and why, with row counts
│   ├── data_dictionary.md              # Column-by-column reference
│   ├── kpi_summary.json                # Headline KPIs
│   ├── Business_Report.docx            # Full findings report
│   └── Executive_Summary.docx          # One-page summary for stakeholders
├── images/                              # Exported chart PNGs + interactive K-Means 3D HTML
└── scripts/                             # Source scripts (01 generate → 02 clean → 03 build notebook)
```

## How to Reproduce

```bash
pip install pandas numpy scikit-learn matplotlib plotly nbformat jupyter
python scripts/01_generate_dataset.py     # -> data/retail_sales_raw.csv
python scripts/02_clean_dataset.py        # -> data/retail_sales_clean.csv + cleaning log
jupyter nbconvert --to notebook --execute --inplace notebooks/Retail_Sales_Analysis.ipynb
```

For the SQL layer, load the clean CSV into any database and run
`sql/retail_sales_analysis.sql` (written in portable ANSI SQL with SQLite date
functions; Postgres/BigQuery/Snowflake equivalents are noted at the bottom of
the file). All 36 queries were validated against a SQLite build as part of
this project.

For the dashboard, just open `dashboard/retail_executive_dashboard.html` in a
browser — no server or install required. See `dashboard/PowerBI_Build_Guide.md`
to rebuild the same model natively in Power BI Desktop.

## Headline Findings (FY2023–FY2025)

- **₹208.4 Cr total sales**, **₹55.9 Cr total profit** (26.8% overall margin) across 57,718 orders and 8,767 customers.
- **Electronics is the profit engine** — ~59% of total sales and ~58% of total profit, but also has an above-average 9.0% return rate.
- **October–November festive season** is the clearest recurring demand spike every year, ~35–40% above the summer trough months.
- **West and South regions lead** on total sales, but margin % is fairly even across all four regions (~26–27%) — growth headroom looks more like a volume story than a margin story.
- **92% of customers are repeat buyers**, and repeat customers account for the large majority of revenue — retention economics matter more here than one-time acquisition.
- **Fashion (9.4%) and Electronics (9.0%) have the highest return rates**, well above Grocery and Home & Furniture (~6.2%) — and return rate climbs noticeably for orders with 20%+ discounts, suggesting aggressive discounting doesn't just compress margin, it also drives more returns.
- **Shipping mode has only a modest effect on returns** (7.4%–7.7% across all four modes) — Economy runs slightly higher than the rest, but delivery speed alone isn't a major return-rate lever here.

Full methodology, caveats, and recommendations are in
`reports/Business_Report.docx`; a one-page version is in
`reports/Executive_Summary.docx`.

## Tech Stack

Python (Pandas, NumPy, scikit-learn, Matplotlib, Plotly) · SQL (SQLite-validated,
portable to Postgres/BigQuery/Snowflake) · Power BI (DAX + data model guide) ·
Jupyter.

## Notes on Data

This is a **synthetically generated but realistically-structured** dataset (not
scraped or sourced from a real company), built with intentional data-quality
issues — duplicates, missing values, invalid dates, mixed date formats, and
outliers — so the cleaning stage demonstrates real-world data engineering
judgment rather than working with an already-pristine CSV. See
`reports/data_cleaning_log.md` for the full transformation trail.
