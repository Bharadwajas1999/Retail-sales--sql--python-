# Retail Sales Performance Analysis

A SQL + Python analysis of retail transaction data, covering revenue trends, regional performance, discount effectiveness, and customer segmentation.

## Business Problem

A multi-region retailer wants to understand:
- How net revenue is trending month over month
- Which regions and channels drive the most revenue
- Whether discounting actually increases order volume, or just erodes margin
- How to segment customers for targeted marketing (RFM-style)

## Dataset

`data/sales_transactions.csv` — 2,000 synthetic but realistic transaction records (2024–2025) with:
`order_id, order_date, region, category, channel, units_sold, unit_price, discount_pct, customer_id, gross_revenue, net_revenue`

## Tech Stack

- **SQL** (Snowflake / PostgreSQL syntax): window functions, CTEs, Pareto analysis
- **Python**: Pandas, NumPy for data wrangling; Scikit-learn (KMeans) for customer segmentation; Matplotlib for visualization

## Files

| File | Description |
|---|---|
| `sql_analysis.sql` | 5 analytical queries: monthly trend w/ MoM growth, regional ranking, discount impact, top-decile customer (Pareto) check, category x channel pivot |
| `eda_analysis.py` | End-to-end Python pipeline: cleaning, trend/regional/discount summaries, RFM customer segmentation via KMeans, exports CSVs + revenue trend chart |
| `data/sales_transactions.csv` | Source transaction data |

## Key Findings

- **Discounting beyond 5% does not meaningfully increase average units per order** — average units/order stays flat (~4.9–5.1) across all discount tiers, suggesting heavier discounts mainly erode margin rather than drive incremental volume.
- **Revenue is fairly evenly distributed across regions** (19–30% share each), with the West leading at ~30% of net revenue.
- Customer segmentation surfaces a clear high-value cluster (high frequency, high monetary, low recency) worth prioritizing for retention campaigns.

## How to Run

```bash
pip install pandas numpy matplotlib scikit-learn
python eda_analysis.py
```

Outputs: `output_monthly_trend.csv`, `output_regional_summary.csv`, `output_discount_impact.csv`, `output_customer_segments.csv`, `monthly_revenue_trend.png`

## Next Steps

- Connect `sales_transactions.csv` to Power BI / Tableau for an interactive dashboard (see companion project: `supply-chain-bi-dashboard` for DAX measure patterns)
- Extend segmentation with a time-series forecast of monthly revenue (e.g., Prophet or ARIMA)
