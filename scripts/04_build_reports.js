const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell,
  WidthType, ShadingType, BorderStyle, AlignmentType, LevelFormat, convertInchesToTwip
} = require("docx");

const PAGE = { size: { width: 12240, height: 15840 } }; // US Letter

function h1(text) { return new Paragraph({ text, heading: HeadingLevel.HEADING_1, spacing: { before: 300, after: 150 } }); }
function h2(text) { return new Paragraph({ text, heading: HeadingLevel.HEADING_2, spacing: { before: 240, after: 120 } }); }
function p(text, opts = {}) {
  return new Paragraph({ children: [new TextRun({ text, ...opts })], spacing: { after: 160 } });
}
function bullet(text) {
  return new Paragraph({ text, bullet: { level: 0 }, spacing: { after: 80 } });
}
function cell(text, opts = {}) {
  return new TableCell({
    width: { size: opts.width || 25, type: WidthType.PERCENTAGE },
    shading: opts.header ? { type: ShadingType.CLEAR, fill: "1F2937" } : undefined,
    children: [new Paragraph({ children: [new TextRun({ text, bold: !!opts.header, color: opts.header ? "FFFFFF" : "000000", size: 20 })] })],
  });
}
function table(headers, rows, widths) {
  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    columnWidths: widths.map(w => Math.round(w * 90)),
    rows: [
      new TableRow({ children: headers.map((hh, i) => cell(hh, { header: true, width: widths[i] })) }),
      ...rows.map(r => new TableRow({ children: r.map((c, i) => cell(String(c), { width: widths[i] })) })),
    ],
  });
}

/* ============================================================
   BUSINESS REPORT
   ============================================================ */

const businessReport = new Document({
  sections: [{
    properties: { page: { size: PAGE.size, margin: { top: 1080, bottom: 1080, left: 1080, right: 1080 } } },
    children: [
      new Paragraph({ text: "Retail Sales Analysis", heading: HeadingLevel.TITLE, spacing: { after: 100 } }),
      new Paragraph({ children: [new TextRun({ text: "Business Report — FY2023–FY2025", size: 26, color: "6B7280" })], spacing: { after: 60 } }),
      new Paragraph({ children: [new TextRun({ text: "Prepared by Vijay · Data Analyst / ML Engineer", size: 20, color: "6B7280" })], spacing: { after: 400 } }),

      h1("1. Objective & Scope"),
      p("This report analyzes three years (2023–2025) of retail transaction data for a simulated pan-India retail chain, covering 58,799 cleaned order line items across 8,767 customers and six product categories. The goal is to surface actionable insights on sales performance, profitability, customer behavior, and operational efficiency to support business decision-making."),

      h1("2. Data & Methodology"),
      p("Data was sourced as a raw transactional export (60,320 rows) and put through a documented cleaning pipeline: duplicate removal, missing-value imputation using context-appropriate strategies (e.g. segment-median age, modal payment method by region), correction of invalid records (non-positive quantity/price, ship-before-order dates), and IQR-based outlier winsorization on unit price. The full transformation log is in data_cleaning_log.md. 2.52% of raw rows were removed or corrected."),
      p("Analysis was performed in three layers: SQL (36 validated queries covering aggregates, window functions, CTEs, ranking, and CLV), Python (Pandas/NumPy/Scikit-learn for EDA, RFM analysis, and K-Means customer segmentation), and an executive dashboard (interactive HTML + a Power BI build guide)."),

      h1("3. Key Performance Indicators"),
      table(
        ["Metric", "Value"],
        [
          ["Total Sales", "₹208.4 Cr"],
          ["Total Profit", "₹55.9 Cr"],
          ["Overall Profit Margin", "26.8%"],
          ["Total Orders", "57,718"],
          ["Total Customers", "8,767"],
          ["Average Order Value", "₹36,106"],
          ["Return Rate", "7.43%"],
          ["Repeat Customer Share", "92.2% of customers"],
        ],
        [50, 50]
      ),

      h1("4. Sales & Profit Trends"),
      p("Monthly sales ranged from a summer trough (~₹4.3–4.8 Cr in February each year) to a festive-season peak (~₹7.1–7.6 Cr in October–November), a recurring and highly predictable seasonal pattern across all three years. January also shows a smaller secondary peak tied to New Year sales."),
      p("Year-over-year, overall sales growth was roughly flat to slightly declining after 2023, indicating the business is currently in a mature, seasonally-stable phase rather than a high-growth phase — the opportunity is more about margin and retention than raw volume expansion."),

      h1("5. Regional & State Performance"),
      table(
        ["Region", "Total Sales", "Total Profit", "Margin %"],
        [
          ["West", "₹54.8 Cr", "₹14.7 Cr", "26.9%"],
          ["South", "₹52.2 Cr", "₹14.1 Cr", "27.0%"],
          ["North", "₹50.8 Cr", "₹13.5 Cr", "26.6%"],
          ["East", "₹50.6 Cr", "₹13.6 Cr", "26.8%"],
        ],
        [25, 25, 25, 25]
      ),
      p("Regional performance is remarkably even — West leads by revenue but all four regions convert sales to profit at a near-identical ~27% rate. This means regional growth initiatives should focus on volume/demand generation rather than margin optimization, since there's no region meaningfully under- or over-performing on efficiency."),

      h1("6. Category & Product Analysis"),
      p("Electronics is the dominant category: ~59% of total sales and ~58% of total profit, but it also carries a 9.0% return rate, second only to Fashion (9.4%). Home & Furniture is the second-largest category by sales (~₹45.3 Cr) with a comparable ~27% margin. Grocery and Books & Stationery are small, low-margin-dollar categories that may be better positioned as basket-builders / footfall drivers than standalone profit centers."),
      p("The top 10 products by revenue are concentrated in laptops, headphones, and camera accessories from Dell, HP, boAt, Sony, and Apple — high-ticket electronics anchor overall revenue. Least-performing products (with at least 5 orders each) are long-tail SKUs across Fashion and Books & Stationery with low unit economics."),

      h1("7. Customer Behavior & Segmentation"),
      p("92.2% of customers have placed more than one order, and the large majority of total revenue comes from this repeat-buyer base — this is a retention-driven business, not a one-time-acquisition business. Consumer is the largest segment by both customer count and revenue, followed by Corporate."),
      p("RFM (Recency, Frequency, Monetary) analysis segmented customers into five behavioral groups — Champions, Loyal Customers, Potential Loyalists, At Risk, and Lost/Hibernating — enabling targeted retention or win-back campaigns. A complementary K-Means clustering on log-transformed RFM features (selected via silhouette score) produced a small number of natural customer clusters with distinct recency/frequency/monetary profiles, exported to customer_rfm.csv for CRM activation."),

      h1("8. Returns & Operational Performance"),
      p("Fashion (9.4%) and Electronics (9.0%) have materially higher return rates than Grocery, Home & Furniture, and Books & Stationery (~6.2–6.7%). Return rate also increases with discount depth — orders discounted 20% or more return notably more often than full-price or lightly-discounted orders, suggesting a link between promotional intensity and post-purchase dissatisfaction or impulse-buy reversal."),
      p("Shipping mode shows only a modest relationship with returns (7.4%–7.7% across Same Day, Express, Standard, and Economy) — delivery speed alone does not appear to be a major lever for reducing returns in this dataset."),
      p("Payment method is dominated by UPI (~31% of transactions) and Credit Card (~28%), reflecting a digitally-native, India-first payment mix; Cash on Delivery and Wallet are minority channels."),

      h1("9. Recommendations"),
      bullet("Prioritize retention programs (loyalty tiers, win-back campaigns for the 'At Risk' RFM segment) over acquisition spend, given how much of revenue already comes from repeat buyers."),
      bullet("Investigate Fashion and Electronics return drivers specifically at high discount tiers (20%+) — consider tightening return windows or improving product-page sizing/spec accuracy for these categories rather than discounting further."),
      bullet("Treat Grocery and Books & Stationery as basket-building categories rather than standalone growth targets; reallocate marketing spend toward Electronics and Home & Furniture where absolute profit dollars are largest."),
      bullet("Since regional margins are nearly identical, prioritize demand-generation (marketing, assortment, store/warehouse footprint) in East and North to close the sales gap with West and South, rather than searching for regional cost-efficiency wins."),
      bullet("Use the RFM/K-Means segments to drive CRM campaigns: Champions get early access/loyalty perks, At Risk gets win-back offers, Lost/Hibernating gets a reactivation discount test (measuring return-rate impact carefully, given the discount-return correlation found above)."),

      h1("10. Limitations & Next Steps"),
      p("This dataset is synthetically generated with realistic structure and seasonality but is not sourced from a live business system — absolute figures should be read as illustrative of method, not as real financial results. Suggested next steps: (1) fit and back-test an actual forecasting model (Prophet/SARIMA/XGBoost) on the prepared daily time series, (2) extend RFM/K-Means into a live CRM segment sync, (3) add a basket-affinity (market basket) analysis if order-level (not just line-item-level) transaction keys become available."),
    ],
  }],
});

Packer.toBuffer(businessReport).then(buf => {
  fs.writeFileSync("/home/claude/retail_project/reports/Business_Report.docx", buf);
  console.log("Business_Report.docx written");
});

/* ============================================================
   EXECUTIVE SUMMARY (one page)
   ============================================================ */

const execSummary = new Document({
  sections: [{
    properties: { page: { size: PAGE.size, margin: { top: 1080, bottom: 1080, left: 1080, right: 1080 } } },
    children: [
      new Paragraph({ text: "Retail Sales Analysis — Executive Summary", heading: HeadingLevel.TITLE, spacing: { after: 100 } }),
      new Paragraph({ children: [new TextRun({ text: "FY2023–FY2025 · Prepared by Vijay", size: 22, color: "6B7280" })], spacing: { after: 300 } }),

      h2("Headline Numbers"),
      table(
        ["Metric", "Value"],
        [
          ["Total Sales", "₹208.4 Cr"],
          ["Total Profit", "₹55.9 Cr (26.8% margin)"],
          ["Orders / Customers", "57,718 / 8,767"],
          ["Avg Order Value", "₹36,106"],
          ["Return Rate", "7.4%"],
          ["Repeat Customer Share", "92.2%"],
        ],
        [50, 50]
      ),

      h2("What's Working"),
      bullet("Electronics drives ~59% of sales and ~58% of profit — the single biggest lever in the business."),
      bullet("A strongly retention-driven customer base: 92% of customers are repeat buyers."),
      bullet("Consistent, predictable festive-season (Oct–Nov) demand spike every year — plannable for inventory and staffing."),
      bullet("Profit margin is nearly identical (~27%) across all four regions — operational efficiency is not the bottleneck."),

      h2("What Needs Attention"),
      bullet("Fashion (9.4%) and Electronics (9.0%) return rates are meaningfully above other categories (~6.2–6.7%)."),
      bullet("Return rate rises with discount depth — 20%+ discounted orders return more often, eroding the intended margin benefit further."),
      bullet("East and North regions lag West/South on total sales despite equal margins — a demand-generation gap, not a cost problem."),

      h2("Top 3 Recommendations"),
      bullet("Shift marketing/retention budget toward loyalty and win-back programs, not just acquisition — the revenue base is already retention-driven."),
      bullet("Audit high-discount (20%+) Fashion/Electronics promotions for return drivers before running further discount campaigns."),
      bullet("Use RFM + K-Means customer segments (see notebook / customer_rfm.csv) to target Champions and At-Risk customers differently in CRM outreach."),

      new Paragraph({ children: [new TextRun({ text: "Full analysis, methodology, and caveats: Business_Report.docx", italics: true, size: 20, color: "6B7280" })], spacing: { before: 300 } }),
    ],
  }],
});

Packer.toBuffer(execSummary).then(buf => {
  fs.writeFileSync("/home/claude/retail_project/reports/Executive_Summary.docx", buf);
  console.log("Executive_Summary.docx written");
});
