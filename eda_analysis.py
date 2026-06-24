"""
Retail Sales Performance Analysis
Author: Bharadwaja S.
Stack: Python (Pandas, NumPy, Matplotlib, Scikit-learn)

This script loads transactional retail data and performs:
  1. Data cleaning / feature engineering
  2. Exploratory analysis (revenue trends, regional mix, discount impact)
  3. A simple customer segmentation (RFM-style) using KMeans
  4. Export of summary tables for BI consumption (Power BI / Tableau)

Run: python eda_analysis.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

DATA_PATH = "data/sales_transactions.csv"


def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["order_date"])
    df["order_month"] = df["order_date"].values.astype("datetime64[M]")
    return df


def monthly_revenue_trend(df: pd.DataFrame) -> pd.DataFrame:
    trend = (
        df.groupby("order_month")["net_revenue"]
        .sum()
        .reset_index()
        .sort_values("order_month")
    )
    trend["mom_growth_pct"] = trend["net_revenue"].pct_change().round(4) * 100
    return trend


def regional_summary(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby("region")
        .agg(
            net_revenue=("net_revenue", "sum"),
            orders=("order_id", "nunique"),
            avg_order_value=("net_revenue", "mean"),
        )
        .reset_index()
        .sort_values("net_revenue", ascending=False)
    )
    summary["pct_of_total_revenue"] = (
        100 * summary["net_revenue"] / summary["net_revenue"].sum()
    ).round(2)
    return summary


def discount_impact(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("discount_pct")
        .agg(
            orders=("order_id", "nunique"),
            avg_units=("units_sold", "mean"),
            net_revenue=("net_revenue", "sum"),
        )
        .reset_index()
        .sort_values("discount_pct")
    )


def customer_segmentation(df: pd.DataFrame, n_clusters: int = 4) -> pd.DataFrame:
    """Simple RFM-style segmentation using KMeans clustering."""
    snapshot_date = df["order_date"].max() + pd.Timedelta(days=1)

    rfm = (
        df.groupby("customer_id")
        .agg(
            recency=("order_date", lambda x: (snapshot_date - x.max()).days),
            frequency=("order_id", "nunique"),
            monetary=("net_revenue", "sum"),
        )
        .reset_index()
    )

    features = rfm[["recency", "frequency", "monetary"]]
    scaled = StandardScaler().fit_transform(features)

    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    rfm["segment"] = km.fit_predict(scaled)

    segment_profile = (
        rfm.groupby("segment")[["recency", "frequency", "monetary"]]
        .mean()
        .round(2)
        .reset_index()
    )
    return rfm, segment_profile


def plot_revenue_trend(trend: pd.DataFrame, out_path: str = "monthly_revenue_trend.png"):
    plt.figure(figsize=(10, 5))
    plt.plot(trend["order_month"], trend["net_revenue"], marker="o")
    plt.title("Monthly Net Revenue Trend")
    plt.xlabel("Month")
    plt.ylabel("Net Revenue ($)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def main():
    df = load_data(DATA_PATH)

    trend = monthly_revenue_trend(df)
    regions = regional_summary(df)
    discounts = discount_impact(df)
    rfm, segments = customer_segmentation(df)

    trend.to_csv("output_monthly_trend.csv", index=False)
    regions.to_csv("output_regional_summary.csv", index=False)
    discounts.to_csv("output_discount_impact.csv", index=False)
    segments.to_csv("output_customer_segments.csv", index=False)

    plot_revenue_trend(trend)

    print("=== Monthly Revenue Trend (last 5 rows) ===")
    print(trend.tail())
    print("\n=== Regional Summary ===")
    print(regions)
    print("\n=== Discount Impact ===")
    print(discounts)
    print("\n=== Customer Segment Profiles ===")
    print(segments)


if __name__ == "__main__":
    main()
