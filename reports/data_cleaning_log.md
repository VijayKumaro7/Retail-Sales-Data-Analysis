# Data Cleaning Log

## 1. Load
Rows loaded: **60320**, Columns: **27**

## 2. Date Parsing
Parsed 'Order Date' / 'Ship Date' across mixed source formats (ISO, DD/MM/YYYY, DD-Mon-YYYY, timestamped).

## 3. Duplicate Removal
Exact duplicate rows removed: **725** (60320 -> 59595)

Secondary de-dup on (Order ID, Product ID, Customer ID, Order Date): **500** additional rows removed (59595 -> 59095)

## 4. Text Standardization
Trimmed whitespace and normalized casing on: Customer Name, Customer Segment, Gender, City, State, Region, Category, Sub Category, Brand, Payment Method, Shipping Mode, Returned.

## 5. Missing Value Handling

| Column | Missing Before | Strategy | Missing After |
|---|---|---|---|
| Customer Name | 891 | Fill with 'Unknown Customer' (retain transaction) | 0 |
| Age | 1186 | Impute with median age per Customer Segment | 0 |
| City | 590 | Fallback to '<State> - Unspecified' | 0 |
| Discount | 594 | Fill with 0% (no discount recorded) | 0 |
| Payment Method | 885 | Impute with modal payment method per Region | 0 |
| Ship Date | 470 | Reconstruct from Order Date + median Delivery Days for that Shipping Mode | 0 |
| Delivery Days | 589 | Recompute from cleaned (Ship Date - Order Date) | 0 |
| Returned | 297 | Fill with 'No' (absence of return record) | 0 |

## 6. Invalid Data Correction

| Issue | Rows Affected |
|---|---|
| Quantity <= 0 (dropped) | 176 |
| Unit Price <= 0 (dropped) | 120 |
| Ship Date < Order Date (corrected) | 2996 |
| Discount out of range (clipped to [0, 0.9]) | 0 |

## 7. Outlier Handling
Unit Price IQR bounds (k=3): [-79,172.12, 109,181.43]. **1287** extreme values capped (winsorized) at the upper bound rather than dropped, to preserve transaction volume for legitimate high-end products.

## 8. Final Output
Rows: **60320** (raw) -> **58799** (clean). Removed/corrected 1521 problematic rows overall (2.52%).

Final null count check: 0 nulls remaining across all columns.
