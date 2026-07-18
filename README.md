<div align="center">

<img src="images/logo.svg" alt="Retail Sales Data Analysis logo" width="120">

# Retail Sales Data Analysis

**End-to-End Analytics of a Pan-India Retail Chain (FY2023–FY2025)**

*Data engineering · SQL analysis · Python EDA · Machine learning segmentation · Executive reporting*

![Python](https://img.shields.io/badge/Python-Pandas%20%7C%20NumPy%20%7C%20scikit--learn-3776AB?logo=python&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-SQLite%20validated-003B57?logo=sqlite&logoColor=white)
![Power BI](https://img.shields.io/badge/Power%20BI-Build%20Guide%20%2B%20DAX-F2C811)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-F37626?logo=jupyter&logoColor=white)

</div>

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Business Objectives](#business-objectives)
3. [Key Performance Indicators](#key-performance-indicators)
4. [Methodology](#methodology)
5. [Analysis and Findings](#analysis-and-findings)
6. [Customer Segmentation](#customer-segmentation)
7. [Repository Structure](#repository-structure)
8. [Getting Started](#getting-started)
9. [Technology Stack](#technology-stack)
10. [Deliverables](#deliverables)
11. [Data Disclaimer](#data-disclaimer)

---

## Project Overview

This project demonstrates the complete analytics lifecycle for a simulated pan-India
retail chain operating across four regions between January 2023 and December 2025.
Starting from an intentionally messy 60,320-row transactional extract, the work
progresses through systematic data cleaning, a 36-query SQL analysis layer, full
exploratory data analysis in Python, RFM-based customer segmentation with K-Means
clustering, and culminates in an interactive executive dashboard supported by formal
business reports.

The objective is to replicate the standards of a production analytics engagement:
every transformation is logged, every metric is reproducible, and every finding is
traceable from raw data to boardroom recommendation.

---

## Business Objectives

The analysis was designed to answer the following questions:

- Where are revenue and profit growing or contracting, and what seasonal patterns drive demand?
- Which regions, states, categories, and products generate profit rather than volume alone?
- Who are the highest-value customers, and to what extent does revenue depend on repeat purchasing?
- Which categories and discount levels drive product returns, and what is the associated profit leakage?
- Does shipping mode or delivery speed influence return behavior?
- Can the customer base be segmented into actionable groups for targeted marketing?

---

## Key Performance Indicators

| Metric | Value |
|---|---|
| Total Sales | ₹208.40 Cr |
| Total Profit | ₹55.90 Cr |
| Overall Profit Margin | 26.8% |
| Total Orders | 57,718 |
| Total Customers | 8,767 |
| Average Order Value | ₹36,106 |
| Return Rate | 7.43% |

Source: `reports/kpi_summary.json`, computed from the cleaned dataset.

---

## Methodology

The project is organized as a five-stage pipeline. Each stage produces auditable
artifacts consumed by the next.

| Stage | Description | Key Artifacts |
|---|---|---|
| 1. Data Generation | Produce a realistic transactional dataset with deliberate quality defects: duplicates, missing values, invalid and mixed-format dates, and outliers | `scripts/01_generate_dataset.py`, `data/retail_sales_raw.csv` (60,320 rows) |
| 2. Data Cleaning | Resolve every defect with documented, row-counted transformations | `scripts/02_clean_dataset.py`, `data/retail_sales_clean.csv` (58,799 rows), `reports/data_cleaning_log.md` |
| 3. SQL Analysis | 36 validated queries covering aggregations, window functions, CTEs, ranking, and customer lifetime value | `sql/retail_sales_analysis.sql`, `data/retail_sales.db` |
| 4. Python EDA and Machine Learning | Exploratory analysis, feature engineering, RFM scoring, K-Means clustering, and forecasting preparation | `notebooks/Retail_Sales_Analysis.ipynb`, `data/customer_rfm.csv`, `data/daily_sales_timeseries.csv` |
| 5. Reporting | Interactive executive dashboard, Power BI build guide, and written business reports | `retail_executive_dashboard.html`, `dashboard/PowerBI_Build_Guide.md`, `reports/` |

---

## Analysis and Findings

### 1. Revenue Trend and Seasonality

Sales and profit track each other closely across all three fiscal years. A pronounced
demand spike recurs every October–November, coinciding with the Indian festive season,
at approximately 35–40% above trough months.

![Monthly Sales and Profit Trend](images/monthly_trend.png)

Aggregating all years by calendar month isolates the seasonal signal:

![Seasonal Sales Pattern](images/seasonal_trend.png)

**Implication:** inventory, staffing, and marketing investment should be weighted
toward the fourth-quarter festive window.

### 2. Regional Performance

The West and South regions lead on total sales, but the spread across all four regions
is narrow and profit margins are effectively uniform (approximately 26–27%). Regional
growth is therefore a volume opportunity rather than a margin-repair exercise.

![Total Sales by Region](images/sales_by_region.png)

### 3. Category Economics

Electronics generates approximately 59% of total sales and 58% of total profit,
making it the revenue engine of the business. Margin percentage, however, favors the
smaller categories: Grocery (~35%) and Books & Stationery (~32%) earn the most profit
per rupee of sales.

![Sales and Profit Margin by Category](images/category_analysis.png)

### 4. Product Concentration

The top-selling products are concentrated almost entirely in Electronics — laptops,
headphones, and accessories — while the slowest movers are predominantly Grocery and
Books items.

![Top and Bottom Products by Sales](images/top_bottom_products.png)

### 5. Customer Retention

92.2% of customers have purchased more than once, and repeat customers account for
the substantial majority of revenue. Retention economics dominate acquisition
economics in this business.

![One-Time vs Repeat Customers](images/repeat_customers.png)

### 6. Returns and Discounting

Fashion (9.4%) and Electronics (9.0%) carry the highest return rates, well above
Grocery and Home & Furniture (~6.2%). Return rate also rises materially with discount
depth: orders discounted 20% or more are returned at nearly 9.5%, versus under 7% for
full-price orders. Aggressive discounting therefore erodes profitability twice — once
through margin compression and again through elevated returns.

![Return Rate by Category and Discount Band](images/return_analysis.png)

### 7. Payments and Fulfillment

UPI (~31%) and credit cards (~28%) dominate the payment mix. Average delivery time
ranges from under 2 days (Same Day) to approximately 21 days (Economy), yet return
rates remain within a narrow 7.4–7.7% band across all shipping modes — delivery speed
is not a material lever on return behavior.

![Payment Methods and Shipping Modes](images/payment_shipping.png)

---

## Customer Segmentation

Customers were scored on Recency, Frequency, and Monetary value (RFM) and grouped
into five marketing-ready segments. Segment assignments per customer are available in
`data/customer_rfm.csv`.

![Customer Count by RFM Segment](images/rfm_segments.png)

| Segment | Profile | Recommended Action |
|---|---|---|
| Champions | Recent, frequent, high-spend buyers | Reward, retain, and solicit advocacy |
| Loyal Customers | Consistent repeat purchasers | Upsell and cross-sell |
| Potential Loyalists | Recent buyers with growing engagement | Nurture toward loyalty programs |
| At Risk | Previously active, now lapsing | Targeted win-back campaigns |
| Lost / Hibernating | Long-inactive customers | Low-cost reactivation only |

Cluster count for the complementary K-Means model was selected using the elbow method
and silhouette analysis. An interactive three-dimensional cluster visualization is
provided in `images/kmeans_3d_clusters.html`.

![Elbow Method and Silhouette Score](images/kmeans_selection.png)

---

## Repository Structure

```
Retail-Sales-Data-Analysis/
├── data/
│   ├── retail_sales_raw.csv             # 60,320 rows — source extract with quality defects
│   ├── retail_sales_clean.csv           # 58,799 rows — analysis-ready dataset
│   ├── retail_sales.db                  # SQLite build of the clean data
│   ├── customer_rfm.csv                 # RFM scores and K-Means cluster per customer
│   └── daily_sales_timeseries.csv       # Daily series with calendar features
├── sql/
│   └── retail_sales_analysis.sql        # 36 queries — aggregates, window functions, CTEs, CLV
├── notebooks/
│   └── Retail_Sales_Analysis.ipynb      # Full EDA, feature engineering, RFM, K-Means
├── scripts/
│   ├── 01_generate_dataset.py           # Stage 1 — dataset generation
│   ├── 02_clean_dataset.py              # Stage 2 — cleaning and logging
│   ├── 03_build_notebook.py             # Stage 3 — notebook construction
│   └── 04_build_reports.js              # Stage 4 — report generation
├── dashboard/
│   └── PowerBI_Build_Guide.md           # Data model and DAX measures for Power BI Desktop
├── reports/
│   ├── data_cleaning_log.md             # Transformation log with row counts
│   ├── data_dictionary.md               # Column-level reference
│   ├── kpi_summary.json                 # Headline KPIs
│   ├── Business_Report.docx             # Full findings and recommendations
│   └── Executive_Summary.docx           # One-page stakeholder summary
├── images/                              # Chart exports, project logo, 3D cluster visualization
├── retail_executive_dashboard.html      # Interactive executive dashboard (browser-based)
└── netlify.toml                         # Deployment configuration
```

---

## Getting Started

### Prerequisites

- Python 3.9 or later
- pip

### Installation

```bash
pip install pandas numpy scikit-learn matplotlib plotly nbformat jupyter
```

### Reproducing the Pipeline

```bash
# Stage 1 — generate the raw dataset
python scripts/01_generate_dataset.py

# Stage 2 — clean the data and write the cleaning log
python scripts/02_clean_dataset.py

# Stages 3–4 — execute the full analysis notebook
jupyter nbconvert --to notebook --execute --inplace notebooks/Retail_Sales_Analysis.ipynb
```

### Running the SQL Layer

Load `data/retail_sales_clean.csv` into any relational database, or use the prebuilt
SQLite database at `data/retail_sales.db`, and execute
`sql/retail_sales_analysis.sql`. The queries are written in portable ANSI SQL with
SQLite date functions; PostgreSQL, BigQuery, and Snowflake equivalents are documented
at the end of the file.

### Viewing the Dashboard

Open `retail_executive_dashboard.html` in any modern browser — no server or
installation is required. To rebuild the same data model natively in Power BI
Desktop, follow `dashboard/PowerBI_Build_Guide.md`.

---

## Technology Stack

| Layer | Technologies |
|---|---|
| Data Processing | Python, Pandas, NumPy |
| Machine Learning | scikit-learn (K-Means clustering, feature scaling), RFM methodology |
| Visualization | Matplotlib, Plotly, Chart.js (dashboard) |
| Database | SQL — validated on SQLite; portable to PostgreSQL, BigQuery, Snowflake |
| Business Intelligence | Power BI (data model and DAX measure guide) |
| Environment | Jupyter Notebook |

---

## Deliverables

| Deliverable | Audience | Location |
|---|---|---|
| Interactive Executive Dashboard | Leadership | `retail_executive_dashboard.html` |
| Business Report | Management and analysts | `reports/Business_Report.docx` |
| Executive Summary | Stakeholders | `reports/Executive_Summary.docx` |
| Power BI Build Guide | BI developers | `dashboard/PowerBI_Build_Guide.md` |
| Data Dictionary and Cleaning Log | Data teams | `reports/data_dictionary.md`, `reports/data_cleaning_log.md` |

---

## Data Disclaimer

The dataset is synthetically generated and does not represent any real company or
individuals. It is deliberately structured with realistic data-quality defects —
duplicates, missing values, invalid and mixed-format dates, and outliers — so that
the cleaning stage demonstrates production-grade data engineering judgment. The
complete transformation trail is documented in `reports/data_cleaning_log.md`.
