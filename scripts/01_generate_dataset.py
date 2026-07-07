"""
01_generate_dataset.py
Generates a realistic, intentionally messy retail sales dataset (60,000+ rows)
for the Retail Sales Analysis portfolio project.

Messiness injected on purpose (to be fixed in the cleaning stage):
- Duplicate rows
- Missing values in several columns
- Inconsistent text casing / whitespace
- Invalid dates (ship date before order date)
- Negative / zero quantities and prices
- Outlier unit prices
- Mixed date formats
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

RNG_SEED = 42
np.random.seed(RNG_SEED)
random.seed(RNG_SEED)

N_BASE_RECORDS = 58000  # will grow past 60k after duplicates are appended

# ---------------------------------------------------------------------------
# Reference dimensions (India-focused retail chain, 3 calendar years)
# ---------------------------------------------------------------------------

REGIONS_STATES_CITIES = {
    "North": {
        "Delhi": ["New Delhi", "Dwarka", "Rohini"],
        "Punjab": ["Ludhiana", "Amritsar", "Chandigarh"],
        "Haryana": ["Gurugram", "Faridabad", "Panipat"],
        "Uttar Pradesh": ["Lucknow", "Noida", "Kanpur"],
    },
    "South": {
        "Karnataka": ["Bengaluru", "Mysuru", "Hubballi"],
        "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai"],
        "Telangana": ["Hyderabad", "Warangal"],
        "Kerala": ["Kochi", "Thiruvananthapuram"],
    },
    "West": {
        "Maharashtra": ["Mumbai", "Pune", "Nagpur"],
        "Gujarat": ["Ahmedabad", "Surat", "Vadodara"],
        "Rajasthan": ["Jaipur", "Udaipur"],
        "Goa": ["Panaji"],
    },
    "East": {
        "West Bengal": ["Kolkata", "Howrah"],
        "Odisha": ["Bhubaneswar", "Cuttack"],
        "Bihar": ["Patna"],
        "Jharkhand": ["Ranchi"],
    },
}

CATEGORY_TREE = {
    "Electronics": {
        "sub": ["Smartphones", "Laptops", "Headphones", "Cameras", "Accessories"],
        "brands": ["Samsung", "Apple", "OnePlus", "Sony", "boAt", "Dell", "HP"],
        "price_range": (999, 120000),
    },
    "Fashion": {
        "sub": ["Men's Apparel", "Women's Apparel", "Footwear", "Watches", "Bags"],
        "brands": ["Levi's", "Zara", "H&M", "Puma", "Nike", "Titan", "Fossil"],
        "price_range": (299, 8999),
    },
    "Home & Furniture": {
        "sub": ["Furniture", "Kitchenware", "Home Decor", "Bedding", "Lighting"],
        "brands": ["IKEA", "Godrej Interio", "Urban Ladder", "Prestige", "Philips"],
        "price_range": (399, 45000),
    },
    "Grocery": {
        "sub": ["Staples", "Beverages", "Snacks", "Dairy", "Personal Care"],
        "brands": ["Tata", "ITC", "Nestle", "Amul", "HUL", "Patanjali"],
        "price_range": (29, 1999),
    },
    "Sports & Fitness": {
        "sub": ["Fitness Equipment", "Sportswear", "Outdoor Gear", "Cycles"],
        "brands": ["Decathlon", "Nike", "Adidas", "Yonex", "Cosco"],
        "price_range": (199, 32000),
    },
    "Books & Stationery": {
        "sub": ["Fiction", "Non-Fiction", "Academic", "Office Supplies"],
        "brands": ["Penguin", "HarperCollins", "Classmate", "Camlin", "Parker"],
        "price_range": (49, 2499),
    },
}

CUSTOMER_SEGMENTS = ["Consumer", "Corporate", "Small Business", "Home Office"]
GENDERS = ["Male", "Female", "Other"]
PAYMENT_METHODS = ["Credit Card", "Debit Card", "UPI", "Net Banking", "Cash on Delivery", "Wallet"]
SHIPPING_MODES = ["Standard", "Express", "Same Day", "Economy"]

FIRST_NAMES = ["Aarav","Vivaan","Aditya","Vihaan","Arjun","Sai","Reyansh","Krishna","Ishaan","Rohan",
               "Ananya","Diya","Isha","Aadhya","Myra","Saanvi","Kavya","Riya","Priya","Neha",
               "Rahul","Karthik","Suresh","Vijay","Anil","Deepak","Manish","Rakesh","Sanjay","Amit",
               "Pooja","Sneha","Divya","Meera","Shreya","Kiran","Nisha","Swati","Anjali","Ritu"]
LAST_NAMES = ["Sharma","Verma","Iyer","Nair","Reddy","Gupta","Mehta","Singh","Rao","Kulkarni",
              "Patel","Das","Bose","Chatterjee","Menon","Pillai","Joshi","Desai","Khan","Kapoor"]

# ---------------------------------------------------------------------------
# Build customer master (drives repeat-purchase behavior)
# ---------------------------------------------------------------------------
N_CUSTOMERS = 9000
customers = []
for i in range(1, N_CUSTOMERS + 1):
    region = random.choice(list(REGIONS_STATES_CITIES.keys()))
    state = random.choice(list(REGIONS_STATES_CITIES[region].keys()))
    city = random.choice(REGIONS_STATES_CITIES[region][state])
    customers.append({
        "Customer ID": f"CUST-{i:05d}",
        "Customer Name": f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
        "Customer Segment": random.choices(CUSTOMER_SEGMENTS, weights=[0.55, 0.2, 0.15, 0.10])[0],
        "Gender": random.choices(GENDERS, weights=[0.48, 0.48, 0.04])[0],
        "Age": int(np.clip(np.random.normal(35, 11), 18, 75)),
        "City": city,
        "State": state,
        "Region": region,
        # skew: a small % of customers order much more often (loyal repeat buyers)
        "order_weight": np.random.choice([1, 2, 3, 8], p=[0.55, 0.25, 0.12, 0.08]),
    })
customers_df = pd.DataFrame(customers)

# ---------------------------------------------------------------------------
# Build product master
# ---------------------------------------------------------------------------
products = []
pid = 1
for category, meta in CATEGORY_TREE.items():
    for sub in meta["sub"]:
        for brand in meta["brands"]:
            n_variants = random.randint(2, 4)
            for v in range(n_variants):
                low, high = meta["price_range"]
                unit_price = round(np.random.uniform(low, high), 2)
                cost_ratio = np.random.uniform(0.55, 0.8)  # cost as % of price
                products.append({
                    "Product ID": f"PRD-{pid:05d}",
                    "Product Name": f"{brand} {sub[:-1] if sub.endswith('s') else sub} {['Pro','Plus','Lite','Max','Classic','Essential'][v % 6]}",
                    "Category": category,
                    "Sub Category": sub,
                    "Brand": brand,
                    "Unit Price": unit_price,
                    "Cost Price": round(unit_price * cost_ratio, 2),
                })
                pid += 1
products_df = pd.DataFrame(products)
# a handful of products are chronic under-performers / discontinued-ish (used for "least performing")
products_df["popularity_weight"] = np.random.choice(
    [0.2, 1, 1, 2, 5], size=len(products_df), p=[0.15, 0.35, 0.25, 0.15, 0.10]
)

print(f"Customers: {len(customers_df)}  Products: {len(products_df)}")

# ---------------------------------------------------------------------------
# Generate order-level transactions
# ---------------------------------------------------------------------------
START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2025, 12, 31)
DATE_RANGE_DAYS = (END_DATE - START_DATE).days

# seasonality: festive months (Oct-Nov) and Jan sales get a boost
MONTH_BOOST = {1: 1.15, 2: 0.9, 3: 0.95, 4: 0.9, 5: 0.95, 6: 0.9,
               7: 0.9, 8: 0.95, 9: 1.05, 10: 1.35, 11: 1.4, 12: 1.15}

customer_weights = customers_df["order_weight"].values / customers_df["order_weight"].sum()
product_weights = products_df["popularity_weight"].values / products_df["popularity_weight"].sum()

rows = []
order_id_counter = 100000

# Weighted day sampling to create the seasonal pattern
day_offsets = np.arange(DATE_RANGE_DAYS + 1)
day_dates = [START_DATE + timedelta(days=int(d)) for d in day_offsets]
day_probs = np.array([MONTH_BOOST[d.month] for d in day_dates], dtype=float)
day_probs = day_probs / day_probs.sum()

for _ in range(N_BASE_RECORDS):
    order_id_counter += 1
    order_id = f"ORD-{order_id_counter}"

    order_date = np.random.choice(day_dates, p=day_probs)
    order_date = pd.Timestamp(order_date) + timedelta(hours=random.randint(8, 21), minutes=random.randint(0, 59))

    cust_idx = np.random.choice(len(customers_df), p=customer_weights)
    cust = customers_df.iloc[cust_idx]

    prod_idx = np.random.choice(len(products_df), p=product_weights)
    prod = products_df.iloc[prod_idx]

    quantity = np.random.choice([1, 2, 3, 4, 5], p=[0.45, 0.28, 0.15, 0.08, 0.04])
    unit_price = prod["Unit Price"]
    discount_pct = np.random.choice([0, 0.05, 0.10, 0.15, 0.20, 0.30], p=[0.35, 0.2, 0.2, 0.13, 0.08, 0.04])

    shipping_mode = random.choices(SHIPPING_MODES, weights=[0.5, 0.3, 0.1, 0.1])[0]
    delivery_days_map = {"Same Day": (0, 1), "Express": (1, 3), "Standard": (3, 7), "Economy": (5, 12)}
    lo, hi = delivery_days_map[shipping_mode]
    delivery_days = random.randint(lo, hi)
    ship_date = order_date + timedelta(days=delivery_days)

    payment_method = random.choices(PAYMENT_METHODS, weights=[0.28, 0.18, 0.30, 0.10, 0.09, 0.05])[0]

    # returns are more likely for Fashion & Electronics, and for heavily discounted items
    base_return_prob = 0.06
    if prod["Category"] in ("Fashion", "Electronics"):
        base_return_prob += 0.03
    if discount_pct >= 0.2:
        base_return_prob += 0.02
    returned = np.random.rand() < base_return_prob

    rows.append({
        "Order ID": order_id,
        "Order Date": order_date,
        "Ship Date": ship_date,
        "Customer ID": cust["Customer ID"],
        "Customer Name": cust["Customer Name"],
        "Customer Segment": cust["Customer Segment"],
        "Gender": cust["Gender"],
        "Age": cust["Age"],
        "City": cust["City"],
        "State": cust["State"],
        "Region": cust["Region"],
        "Product ID": prod["Product ID"],
        "Product Name": prod["Product Name"],
        "Category": prod["Category"],
        "Sub Category": prod["Sub Category"],
        "Brand": prod["Brand"],
        "Quantity": quantity,
        "Unit Price": unit_price,
        "Discount": discount_pct,
        "Cost Price": prod["Cost Price"],
        "Payment Method": payment_method,
        "Shipping Mode": shipping_mode,
        "Delivery Days": delivery_days,
        "Returned": "Yes" if returned else "No",
    })

df = pd.DataFrame(rows)

# ---------------------------------------------------------------------------
# Derived financial fields
# ---------------------------------------------------------------------------
df["Sales"] = (df["Quantity"] * df["Unit Price"] * (1 - df["Discount"])).round(2)
df["Profit"] = (df["Sales"] - (df["Quantity"] * df["Cost Price"])).round(2)
df["Profit Margin"] = (df["Profit"] / df["Sales"]).round(4)

print(f"Clean base rows generated: {len(df)}")

# ---------------------------------------------------------------------------
# Inject realistic messiness (this is the RAW file — cleaning happens later)
# ---------------------------------------------------------------------------
raw = df.copy()

# 1. Duplicate ~4% of rows verbatim
dupe_sample = raw.sample(frac=0.04, random_state=1)
raw = pd.concat([raw, dupe_sample], ignore_index=True)

# 2. Missing values scattered across several columns
for col, frac in [("Customer Name", 0.015), ("Age", 0.02), ("City", 0.01),
                   ("Discount", 0.01), ("Payment Method", 0.015), ("Ship Date", 0.008),
                   ("Delivery Days", 0.01), ("Returned", 0.005)]:
    idx = raw.sample(frac=frac, random_state=hash(col) % 1000).index
    raw.loc[idx, col] = np.nan

# 3. Inconsistent text casing / stray whitespace
def messy_case(x):
    if pd.isna(x):
        return x
    choice = random.random()
    if choice < 0.3:
        return f"  {x.upper()}  "
    elif choice < 0.6:
        return x.lower()
    return x

case_idx = raw.sample(frac=0.12, random_state=7).index
raw.loc[case_idx, "City"] = raw.loc[case_idx, "City"].apply(messy_case)
case_idx2 = raw.sample(frac=0.12, random_state=8).index
raw.loc[case_idx2, "Customer Segment"] = raw.loc[case_idx2, "Customer Segment"].apply(messy_case)

# 4. Some ship dates before order dates (data entry errors)
bad_ship_idx = raw.sample(frac=0.006, random_state=3).index
raw.loc[bad_ship_idx, "Ship Date"] = raw.loc[bad_ship_idx, "Order Date"] - timedelta(days=2)

# 5. A few negative / zero quantities and prices (entry errors)
bad_qty_idx = raw.sample(frac=0.003, random_state=4).index
raw.loc[bad_qty_idx, "Quantity"] = -1
bad_price_idx = raw.sample(frac=0.002, random_state=5).index
raw.loc[bad_price_idx, "Unit Price"] = 0

# 6. Outlier unit prices (fat-finger data entry, e.g. extra zero)
outlier_idx = raw.sample(frac=0.0015, random_state=6).index
raw.loc[outlier_idx, "Unit Price"] = raw.loc[outlier_idx, "Unit Price"] * 50

# 7. Recompute Sales/Profit/Margin so raw file is internally consistent with its own (messy) inputs,
#    but leave some as NaN reflecting missing Discount, etc. This mimics a real "as-exported" extract.
mask_valid = raw["Unit Price"].notna() & raw["Quantity"].notna() & raw["Discount"].notna()
raw.loc[mask_valid, "Sales"] = (raw.loc[mask_valid, "Quantity"] * raw.loc[mask_valid, "Unit Price"] *
                                 (1 - raw.loc[mask_valid, "Discount"])).round(2)
raw.loc[mask_valid, "Profit"] = (raw.loc[mask_valid, "Sales"] - (raw.loc[mask_valid, "Quantity"] * raw.loc[mask_valid, "Cost Price"])).round(2)
raw.loc[mask_valid, "Profit Margin"] = (raw.loc[mask_valid, "Profit"] / raw.loc[mask_valid, "Sales"]).round(4)

# 8. Mixed date string formats to mimic multi-source export inconsistency
def format_date_mixed(d, row_idx):
    if pd.isna(d):
        return d
    fmt_choice = row_idx % 4
    if fmt_choice == 0:
        return d.strftime("%Y-%m-%d")
    elif fmt_choice == 1:
        return d.strftime("%d/%m/%Y")
    elif fmt_choice == 2:
        return d.strftime("%d-%b-%Y")
    else:
        return d.strftime("%Y-%m-%d %H:%M:%S")

raw = raw.reset_index(drop=True)
raw["Order Date"] = [format_date_mixed(d, i) for i, d in enumerate(raw["Order Date"])]
raw["Ship Date"] = [format_date_mixed(d, i) for i, d in enumerate(raw["Ship Date"])]

# Shuffle rows so duplicates aren't all at the tail
raw = raw.sample(frac=1, random_state=99).reset_index(drop=True)

print(f"Raw (messy) rows: {len(raw)}")
raw.to_csv("/home/claude/retail_project/data/retail_sales_raw.csv", index=False)
print("Saved raw dataset -> data/retail_sales_raw.csv")
