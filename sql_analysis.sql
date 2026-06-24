/* ============================================================
   Retail Sales Performance Analysis
   Author: Bharadwaja S.
   Tech: ANSI SQL (tested on Snowflake / PostgreSQL syntax)
   Purpose: Revenue trend, regional performance, and discount
            impact analysis on transactional retail sales data.
   ============================================================ */

-- 1. Monthly net revenue trend with month-over-month growth %
WITH monthly_rev AS (
    SELECT
        DATE_TRUNC('month', order_date)        AS sales_month,
        SUM(net_revenue)                        AS net_revenue,
        COUNT(DISTINCT order_id)                AS order_count
    FROM sales_transactions
    GROUP BY 1
)
SELECT
    sales_month,
    net_revenue,
    order_count,
    ROUND(
        100.0 * (net_revenue - LAG(net_revenue) OVER (ORDER BY sales_month))
        / NULLIF(LAG(net_revenue) OVER (ORDER BY sales_month), 0), 2
    ) AS mom_growth_pct
FROM monthly_rev
ORDER BY sales_month;


-- 2. Regional performance ranked by net revenue, with revenue share
SELECT
    region,
    SUM(net_revenue)                                            AS net_revenue,
    COUNT(DISTINCT order_id)                                    AS orders,
    ROUND(SUM(net_revenue) / SUM(units_sold), 2)                AS revenue_per_unit,
    ROUND(100.0 * SUM(net_revenue) / SUM(SUM(net_revenue)) OVER (), 2) AS pct_of_total_revenue,
    RANK() OVER (ORDER BY SUM(net_revenue) DESC)                AS region_rank
FROM sales_transactions
GROUP BY region
ORDER BY net_revenue DESC;


-- 3. Discount impact: does heavier discounting actually drive more volume?
SELECT
    discount_pct,
    COUNT(DISTINCT order_id)                AS orders,
    SUM(units_sold)                          AS total_units,
    ROUND(AVG(units_sold), 2)                AS avg_units_per_order,
    ROUND(SUM(gross_revenue) - SUM(net_revenue), 2) AS total_discount_value,
    ROUND(SUM(net_revenue), 2)               AS net_revenue
FROM sales_transactions
GROUP BY discount_pct
ORDER BY discount_pct;


-- 4. Top 10% of customers by net revenue (Pareto / "whale" check)
WITH customer_rev AS (
    SELECT
        customer_id,
        SUM(net_revenue) AS customer_net_revenue
    FROM sales_transactions
    GROUP BY customer_id
),
ranked AS (
    SELECT
        customer_id,
        customer_net_revenue,
        PERCENT_RANK() OVER (ORDER BY customer_net_revenue DESC) AS pct_rank
    FROM customer_rev
)
SELECT
    COUNT(*)                                   AS top_decile_customers,
    SUM(customer_net_revenue)                  AS revenue_from_top_decile,
    (SELECT SUM(customer_net_revenue) FROM customer_rev) AS total_revenue,
    ROUND(100.0 * SUM(customer_net_revenue) /
        (SELECT SUM(customer_net_revenue) FROM customer_rev), 2) AS pct_of_total_revenue
FROM ranked
WHERE pct_rank <= 0.10;


-- 5. Category performance by channel (Online vs In-Store), pivoted
SELECT
    category,
    SUM(CASE WHEN channel = 'Online'   THEN net_revenue ELSE 0 END) AS online_revenue,
    SUM(CASE WHEN channel = 'In-Store' THEN net_revenue ELSE 0 END) AS instore_revenue,
    SUM(net_revenue)                                                AS total_revenue
FROM sales_transactions
GROUP BY category
ORDER BY total_revenue DESC;
