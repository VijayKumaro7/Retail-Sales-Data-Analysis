/* =====================================================================
   RETAIL SALES ANALYSIS — SQL QUERY LIBRARY
   Table: sales  (one row = one order line item)
   Dialect: ANSI SQL / SQLite-compatible (portable to Postgres, Snowflake,
   BigQuery with minor date-function substitutions noted inline).
   ===================================================================== */


/* ---------------------------------------------------------------------
   SECTION A — CORE AGGREGATE ANALYSIS
   --------------------------------------------------------------------- */

-- A1. Overall business KPIs
SELECT
    COUNT(DISTINCT "Order ID")                    AS total_orders,
    COUNT(DISTINCT "Customer ID")                 AS total_customers,
    ROUND(SUM("Sales"), 2)                         AS total_sales,
    ROUND(SUM("Profit"), 2)                        AS total_profit,
    ROUND(SUM("Profit") * 100.0 / SUM("Sales"), 2) AS overall_profit_margin_pct,
    ROUND(SUM("Sales") * 1.0 / COUNT(DISTINCT "Order ID"), 2) AS avg_order_value,
    ROUND(SUM(CASE WHEN "Returned" = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS return_rate_pct
FROM sales;

-- A2. Monthly sales trend
SELECT
    strftime('%Y-%m', "Order Date")   AS order_month,
    ROUND(SUM("Sales"), 2)            AS monthly_sales,
    ROUND(SUM("Profit"), 2)           AS monthly_profit,
    COUNT(DISTINCT "Order ID")        AS orders
FROM sales
GROUP BY order_month
ORDER BY order_month;

-- A3. Year-over-year growth (aggregate by year, then compare with LAG)
WITH yearly AS (
    SELECT strftime('%Y', "Order Date") AS yr, SUM("Sales") AS yearly_sales
    FROM sales
    GROUP BY yr
)
SELECT
    yr,
    yearly_sales,
    LAG(yearly_sales) OVER (ORDER BY yr)                                  AS prior_year_sales,
    ROUND((yearly_sales - LAG(yearly_sales) OVER (ORDER BY yr)) * 100.0
          / LAG(yearly_sales) OVER (ORDER BY yr), 2)                      AS yoy_growth_pct
FROM yearly
ORDER BY yr;

-- A4. Region-wise performance
SELECT
    "Region",
    COUNT(DISTINCT "Order ID")   AS orders,
    ROUND(SUM("Sales"), 2)       AS total_sales,
    ROUND(SUM("Profit"), 2)      AS total_profit,
    ROUND(AVG("Profit Margin") * 100, 2) AS avg_margin_pct
FROM sales
GROUP BY "Region"
ORDER BY total_sales DESC;

-- A5. State-wise sales (top 15)
SELECT "State", "Region",
       ROUND(SUM("Sales"), 2)  AS total_sales,
       ROUND(SUM("Profit"), 2) AS total_profit
FROM sales
GROUP BY "State", "Region"
ORDER BY total_sales DESC
LIMIT 15;

-- A6. Category & sub-category performance
SELECT "Category", "Sub Category",
       ROUND(SUM("Sales"), 2)   AS total_sales,
       ROUND(SUM("Profit"), 2)  AS total_profit,
       ROUND(SUM("Profit") * 100.0 / SUM("Sales"), 2) AS margin_pct,
       COUNT(*)                 AS line_items
FROM sales
GROUP BY "Category", "Sub Category"
ORDER BY total_sales DESC;

-- A7. Payment method distribution
SELECT "Payment Method",
       COUNT(*)                                  AS transactions,
       ROUND(SUM("Sales"), 2)                    AS total_sales,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM sales), 2) AS pct_of_transactions
FROM sales
GROUP BY "Payment Method"
ORDER BY transactions DESC;

-- A8. Shipping mode performance (avg delivery days & cost efficiency proxy)
SELECT "Shipping Mode",
       COUNT(*)                     AS shipments,
       ROUND(AVG("Delivery Days"), 2) AS avg_delivery_days,
       ROUND(SUM(CASE WHEN "Returned" = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS return_rate_pct
FROM sales
GROUP BY "Shipping Mode"
ORDER BY avg_delivery_days;

-- A9. Return analysis by category
SELECT "Category",
       COUNT(*)                                                        AS total_orders,
       SUM(CASE WHEN "Returned" = 'Yes' THEN 1 ELSE 0 END)              AS returned_orders,
       ROUND(SUM(CASE WHEN "Returned" = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS return_rate_pct,
       ROUND(SUM(CASE WHEN "Returned" = 'Yes' THEN "Sales" ELSE 0 END), 2) AS sales_lost_to_returns
FROM sales
GROUP BY "Category"
ORDER BY return_rate_pct DESC;

-- A10. Seasonal trend (sales by calendar month, all years combined)
SELECT strftime('%m', "Order Date") AS month_num,
       CASE strftime('%m', "Order Date")
           WHEN '01' THEN 'Jan' WHEN '02' THEN 'Feb' WHEN '03' THEN 'Mar' WHEN '04' THEN 'Apr'
           WHEN '05' THEN 'May' WHEN '06' THEN 'Jun' WHEN '07' THEN 'Jul' WHEN '08' THEN 'Aug'
           WHEN '09' THEN 'Sep' WHEN '10' THEN 'Oct' WHEN '11' THEN 'Nov' WHEN '12' THEN 'Dec'
       END AS month_name,
       ROUND(SUM("Sales"), 2) AS total_sales
FROM sales
GROUP BY month_num
ORDER BY month_num;

-- A11. Customer segment performance
SELECT "Customer Segment",
       COUNT(DISTINCT "Customer ID") AS customers,
       ROUND(SUM("Sales"), 2)        AS total_sales,
       ROUND(AVG("Sales"), 2)        AS avg_order_value
FROM sales
GROUP BY "Customer Segment"
ORDER BY total_sales DESC;

-- A12. Gender-based purchasing pattern
SELECT "Gender",
       COUNT(*) AS transactions,
       ROUND(SUM("Sales"), 2) AS total_sales,
       ROUND(AVG("Sales"), 2) AS avg_basket_value
FROM sales
GROUP BY "Gender";

-- A13. Age-band segmentation
SELECT
    CASE
        WHEN "Age" < 25 THEN '18-24'
        WHEN "Age" BETWEEN 25 AND 34 THEN '25-34'
        WHEN "Age" BETWEEN 35 AND 44 THEN '35-44'
        WHEN "Age" BETWEEN 45 AND 54 THEN '45-54'
        ELSE '55+'
    END AS age_band,
    COUNT(DISTINCT "Customer ID") AS customers,
    ROUND(SUM("Sales"), 2)        AS total_sales
FROM sales
GROUP BY age_band
ORDER BY age_band;


/* ---------------------------------------------------------------------
   SECTION B — RANKING & WINDOW FUNCTIONS
   --------------------------------------------------------------------- */

-- B1. Top 10 best-selling products by revenue
SELECT "Product Name", "Category",
       ROUND(SUM("Sales"), 2) AS total_sales,
       RANK() OVER (ORDER BY SUM("Sales") DESC) AS sales_rank
FROM sales
GROUP BY "Product Name", "Category"
ORDER BY total_sales DESC
LIMIT 10;

-- B2. Bottom 10 least-performing products (min 5 orders, to exclude noise)
SELECT "Product Name", "Category",
       COUNT(*) AS orders,
       ROUND(SUM("Sales"), 2) AS total_sales
FROM sales
GROUP BY "Product Name", "Category"
HAVING COUNT(*) >= 5
ORDER BY total_sales ASC
LIMIT 10;

-- B3. Top 3 products per category (window function partitioned ranking)
WITH ranked AS (
    SELECT "Category", "Product Name",
           SUM("Sales") AS total_sales,
           DENSE_RANK() OVER (PARTITION BY "Category" ORDER BY SUM("Sales") DESC) AS rnk
    FROM sales
    GROUP BY "Category", "Product Name"
)
SELECT * FROM ranked WHERE rnk <= 3 ORDER BY "Category", rnk;

-- B4. Top 20 customers by lifetime revenue
SELECT "Customer ID", "Customer Name",
       COUNT(DISTINCT "Order ID") AS orders,
       ROUND(SUM("Sales"), 2)     AS lifetime_revenue,
       ROUND(SUM("Profit"), 2)    AS lifetime_profit
FROM sales
GROUP BY "Customer ID", "Customer Name"
ORDER BY lifetime_revenue DESC
LIMIT 20;

-- B5. Running total of monthly sales (cumulative revenue, window function)
WITH monthly AS (
    SELECT strftime('%Y-%m', "Order Date") AS order_month, SUM("Sales") AS monthly_sales
    FROM sales GROUP BY order_month
)
SELECT order_month, monthly_sales,
       ROUND(SUM(monthly_sales) OVER (ORDER BY order_month), 2) AS cumulative_sales,
       ROUND(AVG(monthly_sales) OVER (ORDER BY order_month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2) AS rolling_3mo_avg
FROM monthly
ORDER BY order_month;

-- B6. Percent-of-total contribution by category (window function, no self-join)
SELECT "Category",
       ROUND(SUM("Sales"), 2) AS category_sales,
       ROUND(SUM("Sales") * 100.0 / SUM(SUM("Sales")) OVER (), 2) AS pct_of_total_sales
FROM sales
GROUP BY "Category"
ORDER BY category_sales DESC;

-- B7. Rank regions by profit margin within each year
WITH yearly_region AS (
    SELECT strftime('%Y', "Order Date") AS yr, "Region",
           SUM("Profit") * 1.0 / SUM("Sales") AS margin
    FROM sales
    GROUP BY yr, "Region"
)
SELECT yr, "Region", ROUND(margin * 100, 2) AS margin_pct,
       RANK() OVER (PARTITION BY yr ORDER BY margin DESC) AS margin_rank
FROM yearly_region
ORDER BY yr, margin_rank;

-- B8. First and most recent purchase date per customer (window functions)
SELECT DISTINCT "Customer ID",
       MIN("Order Date") OVER (PARTITION BY "Customer ID") AS first_purchase,
       MAX("Order Date") OVER (PARTITION BY "Customer ID") AS last_purchase
FROM sales
ORDER BY "Customer ID"
LIMIT 20;

-- B9. Month-over-month change in sales per region (LAG)
WITH region_month AS (
    SELECT "Region", strftime('%Y-%m', "Order Date") AS order_month, SUM("Sales") AS sales
    FROM sales GROUP BY "Region", order_month
)
SELECT "Region", order_month, sales,
       ROUND(sales - LAG(sales) OVER (PARTITION BY "Region" ORDER BY order_month), 2) AS mom_change
FROM region_month
ORDER BY "Region", order_month;

-- B10. NTILE — split customers into 4 revenue quartiles
WITH cust_rev AS (
    SELECT "Customer ID", SUM("Sales") AS revenue
    FROM sales GROUP BY "Customer ID"
)
SELECT "Customer ID", revenue,
       NTILE(4) OVER (ORDER BY revenue DESC) AS revenue_quartile
FROM cust_rev
ORDER BY revenue DESC;


/* ---------------------------------------------------------------------
   SECTION C — CTEs, CUSTOMER LIFETIME VALUE & COHORTS
   --------------------------------------------------------------------- */

-- C1. Customer Lifetime Value (CLV) proxy: total profit generated per customer
WITH clv AS (
    SELECT "Customer ID", "Customer Name",
           COUNT(DISTINCT "Order ID") AS total_orders,
           SUM("Sales")   AS total_revenue,
           SUM("Profit")  AS total_profit,
           MIN("Order Date") AS first_order,
           MAX("Order Date") AS last_order
    FROM sales
    GROUP BY "Customer ID", "Customer Name"
)
SELECT *,
       ROUND(total_profit * 1.0 / total_orders, 2) AS avg_profit_per_order,
       julianday(last_order) - julianday(first_order) AS customer_tenure_days
FROM clv
ORDER BY total_profit DESC
LIMIT 20;

-- C2. Repeat vs one-time customers
WITH order_counts AS (
    SELECT "Customer ID", COUNT(DISTINCT "Order ID") AS orders
    FROM sales GROUP BY "Customer ID"
)
SELECT
    CASE WHEN orders = 1 THEN 'One-Time' ELSE 'Repeat' END AS customer_type,
    COUNT(*) AS customers,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM order_counts), 2) AS pct_of_customers
FROM order_counts
GROUP BY customer_type;

-- C3. Repeat purchase rate & revenue contribution
WITH order_counts AS (
    SELECT "Customer ID", COUNT(DISTINCT "Order ID") AS orders, SUM("Sales") AS revenue
    FROM sales GROUP BY "Customer ID"
)
SELECT
    CASE WHEN orders = 1 THEN 'One-Time' ELSE 'Repeat' END AS customer_type,
    ROUND(SUM(revenue), 2) AS total_revenue,
    ROUND(SUM(revenue) * 100.0 / (SELECT SUM(revenue) FROM order_counts), 2) AS pct_of_revenue
FROM order_counts
GROUP BY customer_type;

-- C4. Monthly cohort retention (first purchase month -> subsequent activity)
WITH first_purchase AS (
    SELECT "Customer ID", MIN(strftime('%Y-%m', "Order Date")) AS cohort_month
    FROM sales GROUP BY "Customer ID"
),
activity AS (
    SELECT s."Customer ID", f.cohort_month,
           strftime('%Y-%m', s."Order Date") AS activity_month
    FROM sales s JOIN first_purchase f ON s."Customer ID" = f."Customer ID"
)
SELECT cohort_month,
       COUNT(DISTINCT "Customer ID") AS cohort_size,
       COUNT(DISTINCT CASE WHEN activity_month > cohort_month THEN "Customer ID" END) AS retained_customers,
       ROUND(COUNT(DISTINCT CASE WHEN activity_month > cohort_month THEN "Customer ID" END) * 100.0
             / COUNT(DISTINCT "Customer ID"), 2) AS retention_pct
FROM activity
GROUP BY cohort_month
ORDER BY cohort_month;

-- C5. RFM base metrics (Recency, Frequency, Monetary) as of dataset's max date
WITH ref_date AS (SELECT MAX("Order Date") AS max_date FROM sales)
SELECT s."Customer ID",
       julianday((SELECT max_date FROM ref_date)) - julianday(MAX(s."Order Date")) AS recency_days,
       COUNT(DISTINCT s."Order ID") AS frequency,
       ROUND(SUM(s."Sales"), 2) AS monetary
FROM sales s
GROUP BY s."Customer ID"
ORDER BY monetary DESC
LIMIT 20;

-- C6. High-value "champion" customers (top monetary quartile AND recent activity)
WITH ref_date AS (SELECT MAX("Order Date") AS max_date FROM sales),
rfm AS (
    SELECT "Customer ID",
           julianday((SELECT max_date FROM ref_date)) - julianday(MAX("Order Date")) AS recency_days,
           COUNT(DISTINCT "Order ID") AS frequency,
           SUM("Sales") AS monetary
    FROM sales GROUP BY "Customer ID"
)
SELECT * FROM rfm
WHERE monetary >= (SELECT monetary FROM (
        SELECT monetary, NTILE(4) OVER (ORDER BY monetary DESC) AS q FROM rfm
    ) WHERE q = 1 ORDER BY monetary ASC LIMIT 1)
  AND recency_days <= 60
ORDER BY monetary DESC;

-- C7. Products frequently bought together is out of scope for a single-line-item
--     fact table without a basket key; instead: category affinity by customer segment
SELECT "Customer Segment", "Category",
       ROUND(SUM("Sales"), 2) AS total_sales,
       RANK() OVER (PARTITION BY "Customer Segment" ORDER BY SUM("Sales") DESC) AS rnk
FROM sales
GROUP BY "Customer Segment", "Category";


/* ---------------------------------------------------------------------
   SECTION D — PROFITABILITY & REGIONAL COMPARISON
   --------------------------------------------------------------------- */

-- D1. Profit margin by category, ranked
SELECT "Category",
       ROUND(SUM("Sales"), 2)  AS total_sales,
       ROUND(SUM("Profit"), 2) AS total_profit,
       ROUND(SUM("Profit") * 100.0 / SUM("Sales"), 2) AS margin_pct,
       RANK() OVER (ORDER BY SUM("Profit") * 1.0 / SUM("Sales") DESC) AS margin_rank
FROM sales
GROUP BY "Category";

-- D2. Loss-making product lines (negative total profit)
SELECT "Product Name", "Category",
       ROUND(SUM("Sales"), 2) AS total_sales,
       ROUND(SUM("Profit"), 2) AS total_profit
FROM sales
GROUP BY "Product Name", "Category"
HAVING SUM("Profit") < 0
ORDER BY total_profit ASC;

-- D3. Discount impact on margin (bucketed)
SELECT
    CASE
        WHEN "Discount" = 0 THEN 'No Discount'
        WHEN "Discount" <= 0.10 THEN '1-10%'
        WHEN "Discount" <= 0.20 THEN '11-20%'
        ELSE '20%+'
    END AS discount_band,
    COUNT(*) AS orders,
    ROUND(AVG("Profit Margin") * 100, 2) AS avg_margin_pct,
    ROUND(SUM("Sales"), 2) AS total_sales
FROM sales
GROUP BY discount_band
ORDER BY MIN("Discount");

-- D4. Region vs Category cross-tab of profit
SELECT "Region", "Category", ROUND(SUM("Profit"), 2) AS total_profit
FROM sales
GROUP BY "Region", "Category"
ORDER BY "Region", total_profit DESC;

-- D5. Regional comparison: sales, profit, AOV, return rate in one view
SELECT "Region",
       COUNT(DISTINCT "Order ID") AS orders,
       ROUND(SUM("Sales"), 2) AS total_sales,
       ROUND(SUM("Profit"), 2) AS total_profit,
       ROUND(SUM("Sales") * 1.0 / COUNT(DISTINCT "Order ID"), 2) AS avg_order_value,
       ROUND(SUM(CASE WHEN "Returned" = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS return_rate_pct
FROM sales
GROUP BY "Region"
ORDER BY total_sales DESC;

-- D6. Brand profitability leaderboard
SELECT "Brand",
       ROUND(SUM("Sales"), 2) AS total_sales,
       ROUND(SUM("Profit"), 2) AS total_profit,
       ROUND(SUM("Profit") * 100.0 / SUM("Sales"), 2) AS margin_pct
FROM sales
GROUP BY "Brand"
HAVING SUM("Sales") > 0
ORDER BY total_profit DESC
LIMIT 15;

-- D7. Delivery delay vs return-rate correlation (bucketed)
SELECT
    CASE
        WHEN "Delivery Days" <= 2 THEN '0-2 days'
        WHEN "Delivery Days" <= 5 THEN '3-5 days'
        WHEN "Delivery Days" <= 8 THEN '6-8 days'
        ELSE '9+ days'
    END AS delivery_bucket,
    COUNT(*) AS orders,
    ROUND(SUM(CASE WHEN "Returned" = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS return_rate_pct
FROM sales
GROUP BY delivery_bucket
ORDER BY MIN("Delivery Days");

-- D8. Quarter-wise sales and profit trend
SELECT strftime('%Y', "Order Date") || '-Q' ||
       ((CAST(strftime('%m', "Order Date") AS INTEGER) - 1) / 3 + 1) AS quarter,
       ROUND(SUM("Sales"), 2) AS total_sales,
       ROUND(SUM("Profit"), 2) AS total_profit
FROM sales
GROUP BY quarter
ORDER BY quarter;

-- D9. Weekday vs weekend sales pattern
SELECT
    CASE CAST(strftime('%w', "Order Date") AS INTEGER)
        WHEN 0 THEN 'Sunday' WHEN 1 THEN 'Monday' WHEN 2 THEN 'Tuesday'
        WHEN 3 THEN 'Wednesday' WHEN 4 THEN 'Thursday' WHEN 5 THEN 'Friday'
        ELSE 'Saturday'
    END AS day_of_week,
    COUNT(*) AS orders,
    ROUND(SUM("Sales"), 2) AS total_sales
FROM sales
GROUP BY day_of_week
ORDER BY total_sales DESC;

-- D10. New vs returning customer sales split per month
WITH first_purchase AS (
    SELECT "Customer ID", MIN(strftime('%Y-%m', "Order Date")) AS cohort_month
    FROM sales GROUP BY "Customer ID"
)
SELECT strftime('%Y-%m', s."Order Date") AS order_month,
       SUM(CASE WHEN strftime('%Y-%m', s."Order Date") = f.cohort_month THEN s."Sales" ELSE 0 END) AS new_customer_sales,
       SUM(CASE WHEN strftime('%Y-%m', s."Order Date") > f.cohort_month THEN s."Sales" ELSE 0 END) AS returning_customer_sales
FROM sales s
JOIN first_purchase f ON s."Customer ID" = f."Customer ID"
GROUP BY order_month
ORDER BY order_month;

/* =====================================================================
   NOTE ON PORTABILITY
   - strftime()/julianday() are SQLite date functions.
     Postgres:  TO_CHAR(order_date,'YYYY-MM'), (date_a - date_b)
     BigQuery:  FORMAT_DATE('%Y-%m', order_date), DATE_DIFF(date_a, date_b, DAY)
     Snowflake: TO_CHAR(order_date,'YYYY-MM'), DATEDIFF(day, date_b, date_a)
   - All queries were executed and validated against a SQLite build of the
     cleaned dataset (58,799 rows) as part of this project.
   ===================================================================== */
