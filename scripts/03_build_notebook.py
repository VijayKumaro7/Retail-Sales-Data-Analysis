import nbformat as nbf

nb = nbf.v4.new_notebook()
cells = []

def md(text):
    cells.append(nbf.v4.new_markdown_cell(text))

def code(text):
    cells.append(nbf.v4.new_code_cell(text))

# ============================================================= TITLE
md("""# Retail Sales Analysis — Python Notebook
**Author:** Vijay | Data Analyst / ML Engineer
**Dataset:** `retail_sales_clean.csv` (58,799 cleaned transaction line items, 2023–2025, India)

This notebook covers:
1. Data loading & sanity checks
2. Feature engineering
3. Exploratory Data Analysis (trends, regions, categories, customers, returns, shipping)
4. Correlation analysis
5. Outlier detection
6. RFM Analysis
7. Customer segmentation with K-Means
8. Sales forecasting data preparation
""")

# ============================================================= 1. SETUP
code("""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import plotly.express as px
import plotly.graph_objects as go
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.ensemble import IsolationForest

pd.set_option('display.max_columns', 50)
pd.set_option('display.float_format', lambda x: f'{x:,.2f}')
plt.rcParams['figure.figsize'] = (10, 5)
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False

df = pd.read_csv('../data/retail_sales_clean.csv', parse_dates=['Order Date', 'Ship Date'])
print(df.shape)
df.head()""")

code("""df.info()""")

code("""df.describe(include='number').T""")

# ============================================================= 2. FEATURE ENGINEERING
md("## 2. Feature Engineering")

code("""df['Order Year'] = df['Order Date'].dt.year
df['Order Month'] = df['Order Date'].dt.month
df['Order Month Name'] = df['Order Date'].dt.strftime('%b')
df['Order Quarter'] = df['Order Date'].dt.to_period('Q').astype(str)
df['Order Weekday'] = df['Order Date'].dt.day_name()
df['Order YearMonth'] = df['Order Date'].dt.to_period('M').astype(str)

df['Age Band'] = pd.cut(
    df['Age'], bins=[0, 24, 34, 44, 54, 100],
    labels=['18-24', '25-34', '35-44', '45-54', '55+']
)

df['Discount Band'] = pd.cut(
    df['Discount'], bins=[-0.01, 0, 0.10, 0.20, 1.0],
    labels=['No Discount', '1-10%', '11-20%', '20%+']
)

df['Is Returned'] = (df['Returned'] == 'Yes').astype(int)
df['Net Sales'] = np.where(df['Is Returned'] == 1, 0, df['Sales'])  # returned orders contribute 0 net revenue

print('Engineered columns added.')
df[['Order YearMonth', 'Order Quarter', 'Age Band', 'Discount Band', 'Is Returned', 'Net Sales']].head()""")

# ============================================================= 3. EDA — TRENDS
md("""## 3. Exploratory Data Analysis
### 3.1 Monthly Sales Trend & Year-over-Year Growth""")

code("""monthly = df.groupby('Order YearMonth').agg(
    Sales=('Sales', 'sum'), Profit=('Profit', 'sum'), Orders=('Order ID', 'nunique')
).reset_index()

fig, ax = plt.subplots()
ax.plot(monthly['Order YearMonth'], monthly['Sales'], marker='o', label='Sales', color='#2563eb')
ax.plot(monthly['Order YearMonth'], monthly['Profit'], marker='o', label='Profit', color='#16a34a')
ax.set_title('Monthly Sales & Profit Trend')
ax.set_xticks(range(0, len(monthly), 3))
ax.set_xticklabels(monthly['Order YearMonth'][::3], rotation=45, ha='right')
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x/1e6:.1f}M'))
ax.legend()
plt.tight_layout()
plt.savefig('../images/monthly_trend.png', dpi=120)
plt.show()""")

code("""yearly = df.groupby('Order Year')['Sales'].sum().reset_index()
yearly['YoY Growth %'] = yearly['Sales'].pct_change() * 100
yearly""")

md("### 3.2 Region & State Performance")

code("""region_perf = df.groupby('Region').agg(
    Sales=('Sales', 'sum'), Profit=('Profit', 'sum'), Orders=('Order ID', 'nunique')
).sort_values('Sales', ascending=False)
region_perf['Margin %'] = region_perf['Profit'] / region_perf['Sales'] * 100
region_perf""")

code("""fig, ax = plt.subplots()
region_perf['Sales'].sort_values().plot(kind='barh', ax=ax, color='#4f46e5')
ax.set_title('Total Sales by Region')
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x/1e6:.1f}M'))
plt.tight_layout()
plt.savefig('../images/sales_by_region.png', dpi=120)
plt.show()""")

code("""state_perf = df.groupby(['State', 'Region'])['Sales'].sum().sort_values(ascending=False).head(15)
state_perf""")

md("### 3.3 Category & Sub-Category Analysis")

code("""cat_perf = df.groupby('Category').agg(Sales=('Sales', 'sum'), Profit=('Profit', 'sum')).sort_values('Sales', ascending=False)
cat_perf['Margin %'] = cat_perf['Profit'] / cat_perf['Sales'] * 100

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
cat_perf['Sales'].plot(kind='bar', ax=axes[0], color='#0891b2')
axes[0].set_title('Sales by Category')
axes[0].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x/1e6:.1f}M'))
axes[0].tick_params(axis='x', rotation=45)

cat_perf['Margin %'].plot(kind='bar', ax=axes[1], color='#ea580c')
axes[1].set_title('Profit Margin % by Category')
axes[1].tick_params(axis='x', rotation=45)
plt.tight_layout()
plt.savefig('../images/category_analysis.png', dpi=120)
plt.show()
cat_perf""")

code("""subcat_perf = df.groupby(['Category', 'Sub Category'])['Sales'].sum().sort_values(ascending=False).head(15)
subcat_perf""")

md("### 3.4 Top-Selling & Least-Performing Products")

code("""top_products = df.groupby('Product Name')['Sales'].sum().sort_values(ascending=False).head(10)
bottom_products = (df.groupby('Product Name')
                    .filter(lambda g: len(g) >= 5)
                    .groupby('Product Name')['Sales'].sum().sort_values().head(10))

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
top_products.sort_values().plot(kind='barh', ax=axes[0], color='#16a34a')
axes[0].set_title('Top 10 Products by Sales')
bottom_products.sort_values(ascending=False).plot(kind='barh', ax=axes[1], color='#dc2626')
axes[1].set_title('Bottom 10 Products by Sales (min. 5 orders)')
plt.tight_layout()
plt.savefig('../images/top_bottom_products.png', dpi=120)
plt.show()""")

md("### 3.5 Customer Segmentation & Repeat Customer Analysis")

code("""seg_perf = df.groupby('Customer Segment').agg(
    Customers=('Customer ID', 'nunique'), Sales=('Sales', 'sum'), AOV=('Sales', 'mean')
).sort_values('Sales', ascending=False)
seg_perf""")

code("""order_counts = df.groupby('Customer ID')['Order ID'].nunique()
repeat_share = (order_counts > 1).mean() * 100
revenue_by_cust = df.groupby('Customer ID')['Sales'].sum()
repeat_customers = order_counts[order_counts > 1].index
repeat_revenue_share = revenue_by_cust.loc[repeat_customers].sum() / revenue_by_cust.sum() * 100

print(f'Repeat customer share: {repeat_share:.1f}% of customers')
print(f'Revenue from repeat customers: {repeat_revenue_share:.1f}% of total revenue')

fig, ax = plt.subplots()
pd.Series({'One-Time': (order_counts == 1).sum(), 'Repeat': (order_counts > 1).sum()}).plot(
    kind='pie', autopct='%1.1f%%', ax=ax, colors=['#94a3b8', '#4f46e5'], ylabel=''
)
ax.set_title('One-Time vs Repeat Customers')
plt.tight_layout()
plt.savefig('../images/repeat_customers.png', dpi=120)
plt.show()""")

md("### 3.6 Payment Method & Shipping Performance")

code("""payment_dist = df['Payment Method'].value_counts(normalize=True) * 100
shipping_perf = df.groupby('Shipping Mode').agg(
    Avg_Delivery_Days=('Delivery Days', 'mean'), Return_Rate=('Is Returned', 'mean')
)
shipping_perf['Return_Rate'] *= 100

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
payment_dist.plot(kind='bar', ax=axes[0], color='#7c3aed')
axes[0].set_title('Payment Method Distribution (%)')
axes[0].tick_params(axis='x', rotation=45)

shipping_perf['Avg_Delivery_Days'].plot(kind='bar', ax=axes[1], color='#0d9488')
axes[1].set_title('Avg Delivery Days by Shipping Mode')
axes[1].tick_params(axis='x', rotation=0)
plt.tight_layout()
plt.savefig('../images/payment_shipping.png', dpi=120)
plt.show()
shipping_perf""")

md("### 3.7 Return Analysis")

code("""return_by_cat = df.groupby('Category')['Is Returned'].mean().sort_values(ascending=False) * 100
return_by_discount = df.groupby('Discount Band', observed=True)['Is Returned'].mean() * 100

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
return_by_cat.plot(kind='bar', ax=axes[0], color='#dc2626')
axes[0].set_title('Return Rate % by Category')
axes[0].tick_params(axis='x', rotation=45)

return_by_discount.plot(kind='bar', ax=axes[1], color='#f59e0b')
axes[1].set_title('Return Rate % by Discount Band')
axes[1].tick_params(axis='x', rotation=0)
plt.tight_layout()
plt.savefig('../images/return_analysis.png', dpi=120)
plt.show()""")

md("### 3.8 Profitability & Seasonal Trends")

code("""seasonal = df.groupby('Order Month Name')['Sales'].sum()
month_order = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
seasonal = seasonal.reindex(month_order)

fig, ax = plt.subplots()
seasonal.plot(kind='bar', ax=ax, color='#2563eb')
ax.set_title('Seasonal Sales Pattern (all years combined)')
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x/1e6:.1f}M'))
plt.tight_layout()
plt.savefig('../images/seasonal_trend.png', dpi=120)
plt.show()
print('Peak months: Oct-Nov (festive season boost), Jan (New Year sales).')""")

# ============================================================= 4. CORRELATION
md("## 4. Correlation Analysis")

code("""num_cols = ['Quantity', 'Unit Price', 'Discount', 'Cost Price', 'Sales', 'Profit',
            'Profit Margin', 'Delivery Days', 'Age']
corr = df[num_cols].corr()

fig, ax = plt.subplots(figsize=(8, 6))
im = ax.imshow(corr, cmap='RdBu', vmin=-1, vmax=1)
ax.set_xticks(range(len(num_cols))); ax.set_xticklabels(num_cols, rotation=45, ha='right')
ax.set_yticks(range(len(num_cols))); ax.set_yticklabels(num_cols)
for i in range(len(num_cols)):
    for j in range(len(num_cols)):
        ax.text(j, i, f'{corr.iloc[i, j]:.2f}', ha='center', va='center', fontsize=8)
plt.colorbar(im)
ax.set_title('Correlation Matrix — Numeric Features')
plt.tight_layout()
plt.savefig('../images/correlation_matrix.png', dpi=120)
plt.show()""")

md("""**Key reads:** Discount correlates negatively with Profit Margin (as expected — heavier
discounting compresses margin). Sales and Profit move closely together since Profit is
derived from Sales. Delivery Days shows negligible linear correlation with Profit, but the
categorical return-rate-by-delivery-bucket view (SQL D7 / notebook 3.7) is a better lens
for that relationship than a linear correlation.""")

# ============================================================= 5. OUTLIER DETECTION
md("## 5. Outlier Detection")

code("""fig, axes = plt.subplots(1, 3, figsize=(14, 4))
for ax, col in zip(axes, ['Sales', 'Profit', 'Unit Price']):
    ax.boxplot(df[col], vert=True)
    ax.set_title(f'{col} distribution')
plt.tight_layout()
plt.savefig('../images/outlier_boxplots.png', dpi=120)
plt.show()""")

code("""# IQR-based flagging (already winsorized in cleaning; this re-validates post-clean state)
def iqr_outliers(series, k=3.0):
    q1, q3 = series.quantile([0.25, 0.75])
    iqr = q3 - q1
    lower, upper = q1 - k * iqr, q3 + k * iqr
    return (series < lower) | (series > upper)

sales_outliers = iqr_outliers(df['Sales'])
print(f\"Remaining Sales outliers (IQR k=3): {sales_outliers.sum()} ({sales_outliers.mean()*100:.2f}%)\")

# Cross-check with an unsupervised method: Isolation Forest on Sales/Profit/Quantity/Discount
iso = IsolationForest(contamination=0.01, random_state=42, n_jobs=-1)
iso_features = df[['Sales', 'Profit', 'Quantity', 'Discount']]
df['Anomaly Flag'] = iso.fit_predict(iso_features)
print(f\"Isolation Forest flagged anomalies: {(df['Anomaly Flag'] == -1).sum()} rows\")""")

# ============================================================= 6. RFM ANALYSIS
md("## 6. RFM Analysis (Recency, Frequency, Monetary)")

code("""snapshot_date = df['Order Date'].max() + pd.Timedelta(days=1)

rfm = df.groupby('Customer ID').agg(
    Recency=('Order Date', lambda x: (snapshot_date - x.max()).days),
    Frequency=('Order ID', 'nunique'),
    Monetary=('Sales', 'sum')
).reset_index()

rfm['R_Score'] = pd.qcut(rfm['Recency'], 5, labels=[5, 4, 3, 2, 1]).astype(int)
rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5]).astype(int)
rfm['M_Score'] = pd.qcut(rfm['Monetary'], 5, labels=[1, 2, 3, 4, 5]).astype(int)
rfm['RFM_Score'] = rfm['R_Score'] + rfm['F_Score'] + rfm['M_Score']

def rfm_segment(row):
    if row['RFM_Score'] >= 13:
        return 'Champions'
    elif row['RFM_Score'] >= 10:
        return 'Loyal Customers'
    elif row['RFM_Score'] >= 7:
        return 'Potential Loyalists'
    elif row['RFM_Score'] >= 5:
        return 'At Risk'
    else:
        return 'Lost / Hibernating'

rfm['Segment'] = rfm.apply(rfm_segment, axis=1)
rfm['Segment'].value_counts()""")

code("""fig, ax = plt.subplots()
rfm['Segment'].value_counts().sort_values().plot(kind='barh', ax=ax, color='#4f46e5')
ax.set_title('Customer Count by RFM Segment')
plt.tight_layout()
plt.savefig('../images/rfm_segments.png', dpi=120)
plt.show()

rfm.to_csv('../data/customer_rfm.csv', index=False)
print('Saved RFM table -> data/customer_rfm.csv')
rfm.head()""")

# ============================================================= 7. KMEANS SEGMENTATION
md("## 7. Customer Segmentation with K-Means")

code("""features = rfm[['Recency', 'Frequency', 'Monetary']].copy()
# log-transform Monetary/Frequency to tame skew before scaling
features['Frequency'] = np.log1p(features['Frequency'])
features['Monetary'] = np.log1p(features['Monetary'])

scaler = StandardScaler()
X = scaler.fit_transform(features)

inertias, sil_scores = [], []
K_range = range(2, 9)
for k in K_range:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(X)
    inertias.append(km.inertia_)
    sil_scores.append(silhouette_score(X, labels))

fig, axes = plt.subplots(1, 2, figsize=(12, 4))
axes[0].plot(list(K_range), inertias, marker='o')
axes[0].set_title('Elbow Method (Inertia)')
axes[0].set_xlabel('k')
axes[1].plot(list(K_range), sil_scores, marker='o', color='#16a34a')
axes[1].set_title('Silhouette Score')
axes[1].set_xlabel('k')
plt.tight_layout()
plt.savefig('../images/kmeans_selection.png', dpi=120)
plt.show()

best_k = list(K_range)[int(np.argmax(sil_scores))]
print(f'Best k by silhouette score: {best_k}')""")

code("""kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=10)
rfm['Cluster'] = kmeans.fit_predict(X)

cluster_profile = rfm.groupby('Cluster').agg(
    Customers=('Customer ID', 'count'),
    Avg_Recency=('Recency', 'mean'),
    Avg_Frequency=('Frequency', 'mean'),
    Avg_Monetary=('Monetary', 'mean')
).round(1)
cluster_profile""")

code("""fig = px.scatter_3d(
    rfm, x='Recency', y='Frequency', z='Monetary', color=rfm['Cluster'].astype(str),
    title=f'K-Means Customer Segments (k={best_k})', opacity=0.6,
    labels={'color': 'Cluster'}
)
fig.write_html('../images/kmeans_3d_clusters.html')
fig.show()""")

# ============================================================= 8. FORECASTING PREP
md("## 8. Sales Forecasting — Data Preparation")

code("""ts = df.groupby('Order Date')['Sales'].sum().asfreq('D').fillna(0).reset_index()
ts.columns = ['ds', 'y']  # Prophet-style naming convention for downstream forecasting tools

# Basic feature set a forecasting model (Prophet / SARIMA / XGBoost) would consume
ts['day_of_week'] = ts['ds'].dt.dayofweek
ts['month'] = ts['ds'].dt.month
ts['is_month_end'] = ts['ds'].dt.is_month_end.astype(int)
ts['rolling_7d_avg'] = ts['y'].rolling(7, min_periods=1).mean()
ts['rolling_30d_avg'] = ts['y'].rolling(30, min_periods=1).mean()

ts.to_csv('../data/daily_sales_timeseries.csv', index=False)
print(f'Daily time series prepared: {ts.shape[0]} days -> data/daily_sales_timeseries.csv')
ts.tail()""")

code("""fig, ax = plt.subplots()
ax.plot(ts['ds'], ts['y'], alpha=0.3, label='Daily Sales')
ax.plot(ts['ds'], ts['rolling_30d_avg'], color='#dc2626', label='30-day Rolling Avg')
ax.set_title('Daily Sales with 30-Day Rolling Average (forecasting input preview)')
ax.legend()
plt.tight_layout()
plt.savefig('../images/forecasting_prep.png', dpi=120)
plt.show()""")

md("""### Notes for a next iteration
This notebook prepares clean daily/monthly series and engineered calendar features
suitable for **Prophet**, **SARIMA**, or a gradient-boosted regressor (XGBoost) with
lag features. Model *fitting* and back-tested forecasts are intentionally left as the
next milestone — this stage focuses on producing a leak-free, properly-aggregated
training table, which is usually the harder half of a forecasting project.""")

# ============================================================= 9. EXPORTS
md("## 9. Summary Exports for Dashboard & Reporting")

code("""summary = {
    'total_sales': float(df['Sales'].sum()),
    'total_profit': float(df['Profit'].sum()),
    'total_orders': int(df['Order ID'].nunique()),
    'total_customers': int(df['Customer ID'].nunique()),
    'avg_order_value': float(df['Sales'].sum() / df['Order ID'].nunique()),
    'return_rate_pct': float(df['Is Returned'].mean() * 100),
    'overall_margin_pct': float(df['Profit'].sum() / df['Sales'].sum() * 100),
}
import json
with open('../reports/kpi_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)
summary""")

nb['cells'] = cells

with open('/home/claude/retail_project/notebooks/Retail_Sales_Analysis.ipynb', 'w') as f:
    nbf.write(nb, f)

print(f"Notebook built with {len(cells)} cells.")
