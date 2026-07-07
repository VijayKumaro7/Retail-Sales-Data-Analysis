# Power BI Executive Dashboard — Build Guide

> **Why a guide instead of a `.pbix` file:** Power BI Desktop is a licensed Windows
> application that can't run in this environment, so a binary `.pbix` can't be
> generated here. This guide plus the companion `retail_executive_dashboard.html`
> (open directly in any browser) together deliver the same dashboard: the HTML
> version is the live, explorable artifact for your portfolio/demo; this guide lets
> you rebuild the identical model natively in Power BI Desktop in ~20 minutes if a
> recruiter or interviewer specifically wants to see a `.pbix`.

## 1. Data Model

**Source:** `data/retail_sales_clean.csv` (single fact table — one row per order line item).

Recommended star-schema split for a "proper" Power BI model (Get Data → Power Query):

| Table | Derived from | Key columns |
|---|---|---|
| `Fact_Sales` | retail_sales_clean.csv (drop descriptive columns, keep IDs + measures) | Order ID, Order Date, Ship Date, Customer ID, Product ID, Quantity, Unit Price, Discount, Cost Price, Sales, Profit, Payment Method, Shipping Mode, Delivery Days, Returned |
| `Dim_Customer` | distinct Customer ID, Customer Name, Customer Segment, Gender, Age, City, State, Region | Customer ID (PK) |
| `Dim_Product` | distinct Product ID, Product Name, Category, Sub Category, Brand, Unit Price, Cost Price | Product ID (PK) |
| `Dim_Date` | auto date table or `CALENDAR(MIN(Fact_Sales[Order Date]), MAX(Fact_Sales[Order Date]))` | Date (PK) |

Relationships (all 1-to-many, single direction, from dimension to fact):
`Dim_Customer[Customer ID] → Fact_Sales[Customer ID]`
`Dim_Product[Product ID] → Fact_Sales[Product ID]`
`Dim_Date[Date] → Fact_Sales[Order Date]`

Use Power Query to split the flat CSV into these four tables (Remove Duplicates on
the key column after selecting the dimension columns) — this is the same
normalization logic already applied in `scripts/02_clean_dataset.py`.

## 2. Core DAX Measures

```dax
Total Sales = SUM(Fact_Sales[Sales])

Total Profit = SUM(Fact_Sales[Profit])

Profit Margin % = DIVIDE([Total Profit], [Total Sales], 0)

Total Orders = DISTINCTCOUNT(Fact_Sales[Order ID])

Total Customers = DISTINCTCOUNT(Fact_Sales[Customer ID])

Avg Order Value = DIVIDE([Total Sales], [Total Orders], 0)

Returned Orders = CALCULATE([Total Orders], Fact_Sales[Returned] = "Yes")

Return Rate % = DIVIDE([Returned Orders], [Total Orders], 0)

Repeat Customers =
VAR OrdersByCustomer =
    SUMMARIZE(Fact_Sales, Fact_Sales[Customer ID], "Orders", DISTINCTCOUNT(Fact_Sales[Order ID]))
RETURN
    COUNTROWS(FILTER(OrdersByCustomer, [Orders] > 1))

Repeat Customer % = DIVIDE([Repeat Customers], [Total Customers], 0)

Sales YoY % =
VAR CurrentYearSales = [Total Sales]
VAR PriorYearSales = CALCULATE([Total Sales], SAMEPERIODLASTYEAR(Dim_Date[Date]))
RETURN DIVIDE(CurrentYearSales - PriorYearSales, PriorYearSales, 0)

Sales MTD = TOTALMTD([Total Sales], Dim_Date[Date])

Sales Rolling 3M =
CALCULATE([Total Sales], DATESINPERIOD(Dim_Date[Date], MAX(Dim_Date[Date]), -3, MONTH))

Rank Product by Sales =
RANKX(ALL(Dim_Product[Product Name]), [Total Sales], , DESC)
```

## 3. Page Layout (matches the HTML dashboard 1:1)

**Page 1 — Executive Overview**
- Card visuals: Total Sales, Total Profit, Profit Margin %, Total Orders, Total
  Customers, Avg Order Value, Return Rate % (7 KPI cards across the top)
- Line chart: Total Sales & Total Profit by month (`Dim_Date[YearMonth]` on axis)
- Filled map / shape map: Total Sales by `Dim_Customer[State]`
- Clustered bar: Total Sales & Profit by Region
- Slicers: Year, Region, Category (synced across pages)

**Page 2 — Category & Product Deep-Dive**
- Bar chart: Sales & Profit by Category / Sub-Category (drill-down enabled)
- Table: Top 10 products by `[Total Sales]` with `[Rank Product by Sales]`
- Table: Bottom 10 products (filter `[Total Orders] >= 5`)
- Donut: Sales by Brand

**Page 3 — Customer Analysis**
- Donut: Sales by Customer Segment
- Bar: Customers & Sales by Age Band
- KPI: `[Repeat Customer %]`
- Scatter: Recency vs Monetary (import `data/customer_rfm.csv` as a supplementary table)

**Page 4 — Operations (Payment / Shipping / Returns)**
- Donut: Payment Method distribution
- Bar: Avg Delivery Days by Shipping Mode
- Bar: Return Rate % by Category
- KPI: `[Return Rate %]`, Sales Lost to Returns (`CALCULATE([Total Sales], Fact_Sales[Returned]="Yes")`)

## 4. Dynamic Filters

Add a slicer panel (Region, Category, Customer Segment, Payment Method, Year/Quarter)
on every page, set to **Sync Slicers** across all four pages so the executive view
stays consistent while drilling into detail pages.

## 5. Publishing

`File → Publish → Publish to Power BI` (workspace of your choice), then share the
report link or export a PDF snapshot for the portfolio README.
