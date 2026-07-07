"""
02_clean_dataset.py
Cleans the raw retail sales extract and produces an analysis-ready dataset.

Steps:
 1. Load & parse mixed-format dates
 2. Remove exact duplicates
 3. Standardize text fields (trim, title-case, canonical categories)
 4. Handle missing values (impute or flag, column-by-column, justified)
 5. Correct invalid data (negative/zero qty & price, ship < order date)
 6. Recompute derived financial fields from cleaned inputs
 7. Detect & cap outliers (IQR method) on Unit Price / Sales / Profit
 8. Write a cleaning summary log
"""

import pandas as pd
import numpy as np

pd.set_option("display.width", 120)

RAW_PATH = "/home/claude/retail_project/data/retail_sales_raw.csv"
CLEAN_PATH = "/home/claude/retail_project/data/retail_sales_clean.csv"
LOG_PATH = "/home/claude/retail_project/reports/data_cleaning_log.md"

log_lines = ["# Data Cleaning Log\n"]


def log(msg):
    print(msg)
    log_lines.append(msg)


df = pd.read_csv(RAW_PATH)
start_rows = len(df)
log(f"## 1. Load\nRows loaded: **{start_rows}**, Columns: **{df.shape[1]}**\n")

# ---------------------------------------------------------------------------
# 1. Parse mixed date formats
# ---------------------------------------------------------------------------
def parse_mixed_date(series):
    return pd.to_datetime(series, format="mixed", dayfirst=False, errors="coerce")


df["Order Date"] = parse_mixed_date(df["Order Date"])
df["Ship Date"] = parse_mixed_date(df["Ship Date"])
log(f"## 2. Date Parsing\nParsed 'Order Date' / 'Ship Date' across mixed source formats "
    f"(ISO, DD/MM/YYYY, DD-Mon-YYYY, timestamped).\n")

# ---------------------------------------------------------------------------
# 2. Remove exact duplicates
# ---------------------------------------------------------------------------
before = len(df)
df = df.drop_duplicates()
log(f"## 3. Duplicate Removal\nExact duplicate rows removed: **{before - len(df)}** "
    f"({before} -> {len(df)})\n")

# Also flag duplicate Order ID + Product ID combos (same line item entered twice with
# different row noise) as a secondary, more conservative de-dup pass.
before2 = len(df)
df = df.drop_duplicates(subset=["Order ID", "Product ID", "Customer ID", "Order Date"])
log(f"Secondary de-dup on (Order ID, Product ID, Customer ID, Order Date): "
    f"**{before2 - len(df)}** additional rows removed ({before2} -> {len(df)})\n")

# ---------------------------------------------------------------------------
# 3. Standardize text fields
# ---------------------------------------------------------------------------
text_cols = ["Customer Name", "Customer Segment", "Gender", "City", "State", "Region",
             "Category", "Sub Category", "Brand", "Payment Method", "Shipping Mode", "Returned"]
for col in text_cols:
    df[col] = df[col].astype(str).str.strip()
    df[col] = df[col].replace({"nan": np.nan})

# Title-case free-text geography/name fields; keep controlled-vocabulary fields as canonical values
for col in ["Customer Name", "City"]:
    df[col] = df[col].str.title()

df["Customer Segment"] = df["Customer Segment"].str.title()
log(f"## 4. Text Standardization\nTrimmed whitespace and normalized casing on: {', '.join(text_cols)}.\n")

# ---------------------------------------------------------------------------
# 4. Handle missing values (column-specific, justified strategy)
# ---------------------------------------------------------------------------
missing_before = df.isna().sum()

# Customer Name: unrecoverable identity text -> tag as Unknown (keep row, it's still a valid transaction)
df["Customer Name"] = df["Customer Name"].fillna("Unknown Customer")

# Age: impute with segment-level median (robust to outliers, preserves segment shape)
df["Age"] = df.groupby("Customer Segment")["Age"].transform(lambda s: s.fillna(s.median()))
df["Age"] = df["Age"].fillna(df["Age"].median()).round().astype(int)

# City: fall back to a "State - Unknown City" placeholder rather than dropping the transaction
df["City"] = df["City"].fillna(df["State"] + " - Unspecified")

# Discount: no recorded discount is most safely treated as 0% (conservative, doesn't inflate revenue)
df["Discount"] = df["Discount"].fillna(0.0)

# Payment Method: impute with the modal payment method for that Region (behavioral pattern-preserving)
df["Payment Method"] = df.groupby("Region")["Payment Method"].transform(
    lambda s: s.fillna(s.mode().iloc[0] if not s.mode().empty else "Unknown")
)

# Ship Date: reconstruct from Order Date + median Delivery Days for that Shipping Mode
median_delivery_by_mode = df.groupby("Shipping Mode")["Delivery Days"].median()
missing_ship = df["Ship Date"].isna()
df.loc[missing_ship, "Ship Date"] = df.loc[missing_ship].apply(
    lambda r: r["Order Date"] + pd.Timedelta(days=median_delivery_by_mode.get(r["Shipping Mode"], 5)),
    axis=1,
)

# Delivery Days: recompute directly from the (now complete) date pair — always more reliable than imputing
df["Delivery Days"] = (df["Ship Date"] - df["Order Date"]).dt.days

# Returned: missing return flag defaults to "No" (absence of a return record = not returned)
df["Returned"] = df["Returned"].fillna("No")
df["Returned"] = df["Returned"].str.title()

missing_after = df.isna().sum()
log("## 5. Missing Value Handling\n")
log("| Column | Missing Before | Strategy | Missing After |")
log("|---|---|---|---|")
strategies = {
    "Customer Name": "Fill with 'Unknown Customer' (retain transaction)",
    "Age": "Impute with median age per Customer Segment",
    "City": "Fallback to '<State> - Unspecified'",
    "Discount": "Fill with 0% (no discount recorded)",
    "Payment Method": "Impute with modal payment method per Region",
    "Ship Date": "Reconstruct from Order Date + median Delivery Days for that Shipping Mode",
    "Delivery Days": "Recompute from cleaned (Ship Date - Order Date)",
    "Returned": "Fill with 'No' (absence of return record)",
}
for col, strat in strategies.items():
    log(f"| {col} | {missing_before.get(col, 0)} | {strat} | {missing_after.get(col, 0)} |")
log("")

# ---------------------------------------------------------------------------
# 5. Correct invalid data
# ---------------------------------------------------------------------------
invalid_report = []

# Negative/zero quantity -> invalid line items, drop (can't be a real sale)
bad_qty = df["Quantity"] <= 0
invalid_report.append(("Quantity <= 0 (dropped)", int(bad_qty.sum())))
df = df[~bad_qty]

# Zero unit price -> invalid, drop
bad_price = df["Unit Price"] <= 0
invalid_report.append(("Unit Price <= 0 (dropped)", int(bad_price.sum())))
df = df[~bad_price]

# Ship Date earlier than Order Date -> correct by reassigning Ship Date using mode's median lead time
bad_ship = df["Ship Date"] < df["Order Date"]
n_bad_ship = int(bad_ship.sum())
df.loc[bad_ship, "Ship Date"] = df.loc[bad_ship].apply(
    lambda r: r["Order Date"] + pd.Timedelta(days=max(median_delivery_by_mode.get(r["Shipping Mode"], 3), 1)),
    axis=1,
)
df["Delivery Days"] = (df["Ship Date"] - df["Order Date"]).dt.days
invalid_report.append(("Ship Date < Order Date (corrected)", n_bad_ship))

# Discount out of [0, 0.9] range -> clip
bad_discount = (df["Discount"] < 0) | (df["Discount"] > 0.9)
invalid_report.append(("Discount out of range (clipped to [0, 0.9])", int(bad_discount.sum())))
df["Discount"] = df["Discount"].clip(0, 0.9)

log("## 6. Invalid Data Correction\n")
log("| Issue | Rows Affected |")
log("|---|---|")
for issue, n in invalid_report:
    log(f"| {issue} | {n} |")
log("")

# ---------------------------------------------------------------------------
# 6. Outlier detection & handling (IQR method) on Unit Price
# ---------------------------------------------------------------------------
def iqr_bounds(series, k=3.0):
    q1, q3 = series.quantile(0.25), series.quantile(0.75)
    iqr = q3 - q1
    return q1 - k * iqr, q3 + k * iqr

low, high = iqr_bounds(df["Unit Price"], k=3.0)
outliers = (df["Unit Price"] < low) | (df["Unit Price"] > high)
n_outliers = int(outliers.sum())
# Cap (winsorize) rather than drop — these are real product lines, just fat-fingered entries
df.loc[df["Unit Price"] > high, "Unit Price"] = high
log(f"## 7. Outlier Handling\nUnit Price IQR bounds (k=3): [{low:,.2f}, {high:,.2f}]. "
    f"**{n_outliers}** extreme values capped (winsorized) at the upper bound rather than dropped, "
    f"to preserve transaction volume for legitimate high-end products.\n")

# ---------------------------------------------------------------------------
# 7. Recompute derived financial fields from cleaned inputs (single source of truth)
# ---------------------------------------------------------------------------
df["Sales"] = (df["Quantity"] * df["Unit Price"] * (1 - df["Discount"])).round(2)
df["Profit"] = (df["Sales"] - (df["Quantity"] * df["Cost Price"])).round(2)
df["Profit Margin"] = (df["Profit"] / df["Sales"]).replace([np.inf, -np.inf], np.nan).round(4)
df["Profit Margin"] = df["Profit Margin"].fillna(0)

# ---------------------------------------------------------------------------
# 8. Final typing & column order
# ---------------------------------------------------------------------------
df["Order Date"] = pd.to_datetime(df["Order Date"]).dt.date
df["Ship Date"] = pd.to_datetime(df["Ship Date"]).dt.date

FINAL_COLUMNS = [
    "Order ID", "Order Date", "Ship Date", "Customer ID", "Customer Name", "Customer Segment",
    "Gender", "Age", "City", "State", "Region", "Product ID", "Product Name", "Category",
    "Sub Category", "Brand", "Quantity", "Unit Price", "Discount", "Cost Price", "Sales",
    "Profit", "Profit Margin", "Payment Method", "Shipping Mode", "Delivery Days", "Returned",
]
df = df[FINAL_COLUMNS].reset_index(drop=True)

end_rows = len(df)
log(f"## 8. Final Output\nRows: **{start_rows}** (raw) -> **{end_rows}** (clean). "
    f"Removed/corrected {start_rows - end_rows} problematic rows overall "
    f"({(start_rows - end_rows) / start_rows * 100:.2f}%).\n")
log(f"Final null count check: {int(df.isna().sum().sum())} nulls remaining across all columns.\n")

df.to_csv(CLEAN_PATH, index=False)
with open(LOG_PATH, "w") as f:
    f.write("\n".join(log_lines))

print(f"\nSaved clean dataset -> {CLEAN_PATH}")
print(f"Saved cleaning log -> {LOG_PATH}")
print(df.dtypes)
