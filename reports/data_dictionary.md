# Data Dictionary — `retail_sales_clean.csv`

| Column | Type | Description | Example |
|---|---|---|---|
| Order ID | string | Unique identifier for an order (one order can have multiple line items) | ORD-100234 |
| Order Date | date | Date the order was placed | 2024-03-14 |
| Ship Date | date | Date the order shipped (always >= Order Date after cleaning) | 2024-03-17 |
| Customer ID | string | Unique customer identifier | CUST-04213 |
| Customer Name | string | Customer full name (title-cased; "Unknown Customer" where unrecoverable) | Rohan Sharma |
| Customer Segment | string | Consumer / Corporate / Small Business / Home Office | Consumer |
| Gender | string | Male / Female / Other | Female |
| Age | integer | Customer age in years | 34 |
| City | string | Customer's city | Bengaluru |
| State | string | Customer's state | Karnataka |
| Region | string | North / South / East / West | South |
| Product ID | string | Unique product identifier | PRD-00231 |
| Product Name | string | Product display name (brand + sub-category + variant) | Samsung Smartphone Pro |
| Category | string | Top-level product category | Electronics |
| Sub Category | string | Product sub-category | Smartphones |
| Brand | string | Product brand | Samsung |
| Quantity | integer | Units purchased in this line item (always > 0 after cleaning) | 2 |
| Unit Price | float | List price per unit (₹), winsorized at the IQR upper bound | 24999.00 |
| Discount | float | Discount applied, as a fraction (0–0.9) | 0.10 |
| Cost Price | float | Cost per unit (₹) used to compute profit | 17999.00 |
| Sales | float | `Quantity × Unit Price × (1 − Discount)`, rounded to 2 decimals | 44998.20 |
| Profit | float | `Sales − (Quantity × Cost Price)` | 8998.20 |
| Profit Margin | float | `Profit / Sales` (0 where Sales is 0) | 0.20 |
| Payment Method | string | Credit Card / Debit Card / UPI / Net Banking / Cash on Delivery / Wallet | UPI |
| Shipping Mode | string | Same Day / Express / Standard / Economy | Standard |
| Delivery Days | integer | `Ship Date − Order Date` in days | 3 |
| Returned | string | Yes / No — whether the line item was returned | No |

## Derived / Supplementary Files

| File | Description |
|---|---|
| `data/customer_rfm.csv` | One row per customer: Recency, Frequency, Monetary, R/F/M scores, RFM segment label, K-Means cluster |
| `data/daily_sales_timeseries.csv` | Daily aggregated sales with calendar features and rolling averages, prepared for forecasting |
| `reports/kpi_summary.json` | Headline KPI snapshot used to drive the executive dashboard |
| `reports/data_cleaning_log.md` | Row-by-row account of every cleaning transformation applied to the raw extract |

## Known Data Characteristics (by design, documented for transparency)

- **Grain:** one row = one product line item within an order (not one row per order).
- **Currency:** Indian Rupees (₹); dataset simulates a pan-India retail chain.
- **Time range:** January 2023 – December 2025 (3 full calendar years) with a
  built-in festive-season (Oct–Nov) and New Year (Jan) demand seasonality.
- **Return rate:** modeled higher for Electronics/Fashion and for heavily
  discounted line items, mirroring common e-commerce return patterns.
