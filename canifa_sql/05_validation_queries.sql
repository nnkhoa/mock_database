-- ============================================================
-- 05_validation_queries.sql
-- CANIFA Retail Fashion — Validation Queries
-- ============================================================

USE canifa_retail_demo;


-- 1. Referential integrity
SELECT 'orphan_sales_store' AS check_name, COUNT(*) AS issues
FROM sales_transactions s LEFT JOIN stores st ON s.store_id = st.store_id
WHERE s.store_id IS NOT NULL AND st.store_id IS NULL
UNION ALL
SELECT 'orphan_sales_product', COUNT(*)
FROM sales_transactions s LEFT JOIN products p ON s.product_id = p.product_id
WHERE p.product_id IS NULL
UNION ALL
SELECT 'orphan_sales_channel', COUNT(*)
FROM sales_transactions s LEFT JOIN channels c ON s.channel_id = c.channel_id
WHERE c.channel_id IS NULL
UNION ALL
SELECT 'orphan_sales_promo', COUNT(*)
FROM sales_transactions s LEFT JOIN promotions pr ON s.promo_id = pr.promo_id
WHERE s.promo_id IS NOT NULL AND pr.promo_id IS NULL;

-- 2. Revenue = quantity × unit_price
SELECT 'revenue_mismatch' AS check_name, COUNT(*) AS issues
FROM sales_transactions
WHERE ABS(revenue - quantity * unit_price) > 1;

-- 3. Gross profit check
SELECT 'profit_mismatch' AS check_name, COUNT(*) AS issues
FROM sales_transactions
WHERE ABS(gross_profit - (revenue - quantity * cost_price)) > 1;

-- 4. No negative values
SELECT 'negative_revenue' AS check_name, COUNT(*) AS issues
FROM sales_transactions WHERE revenue < 0
UNION ALL
SELECT 'negative_quantity', COUNT(*)
FROM sales_transactions WHERE quantity <= 0
UNION ALL
SELECT 'negative_inventory', COUNT(*)
FROM inventory_snapshots WHERE quantity_on_hand < 0;

-- 5. Monthly revenue trend (seasonality check)
SELECT DATE_FORMAT(transaction_date, '%Y-%m') AS month,
       ROUND(SUM(revenue) / 1e9, 2) AS revenue_billion_vnd,
       COUNT(DISTINCT order_id) AS num_orders,
       COUNT(*) AS num_records
FROM sales_transactions
GROUP BY 1
ORDER BY 1;

-- 6. Pareto check: top 20% SKU revenue share
SELECT
  CASE WHEN rn <= total * 0.2 THEN 'Top 20%' ELSE 'Bottom 80%' END AS segment,
  ROUND(SUM(sku_revenue) / 1e9, 2) AS revenue_bn,
  ROUND(SUM(sku_revenue) / (SELECT SUM(revenue) FROM sales_transactions) * 100, 1) AS pct
FROM (
    SELECT product_id, SUM(revenue) AS sku_revenue,
           ROW_NUMBER() OVER (ORDER BY SUM(revenue) DESC) AS rn,
           (SELECT COUNT(DISTINCT product_id) FROM sales_transactions) AS total
    FROM sales_transactions GROUP BY product_id
) t
GROUP BY 1;

-- 7. Scenario 1: Top 10 best sellers (3 months)
SELECT p.product_id, p.product_name, p.category_id,
       SUM(s.quantity) AS total_qty, ROUND(SUM(s.revenue)/1e6, 1) AS revenue_m
FROM sales_transactions s
JOIN products p ON s.product_id = p.product_id
WHERE s.transaction_date >= DATE_SUB((SELECT MAX(transaction_date) FROM sales_transactions), INTERVAL 3 MONTH)
GROUP BY 1,2,3
ORDER BY total_qty DESC
LIMIT 10;

-- 8. Scenario 2: Promotion ROI
SELECT pr.promo_id, pr.promo_name, pr.promo_type,
       ROUND(SUM(s.revenue)/1e6, 1) AS promo_revenue_m,
       ROUND(SUM(s.discount_amount)/1e6, 1) AS discount_cost_m,
       pr.marketing_spend / 1e6 AS mktg_m,
       pr.platform_fee / 1e6 AS platform_m
FROM sales_transactions s
JOIN promotions pr ON s.promo_id = pr.promo_id
GROUP BY pr.promo_id, pr.promo_name, pr.promo_type, pr.marketing_spend, pr.platform_fee
ORDER BY promo_revenue_m DESC;

-- 9. Scenario 5: Gross margin Q1/2025 vs Q1/2024
SELECT
  CASE
    WHEN transaction_date BETWEEN '2024-01-01' AND '2024-03-31' THEN 'Q1/2024'
    WHEN transaction_date BETWEEN '2025-01-01' AND '2025-03-31' THEN 'Q1/2025'
  END AS quarter,
  ROUND(SUM(revenue) / 1e9, 2) AS revenue_bn,
  ROUND(SUM(gross_profit) / 1e9, 2) AS gross_profit_bn,
  ROUND(SUM(gross_profit) / SUM(revenue) * 100, 2) AS gross_margin_pct
FROM sales_transactions
WHERE transaction_date BETWEEN '2024-01-01' AND '2024-03-31'
   OR transaction_date BETWEEN '2025-01-01' AND '2025-03-31'
GROUP BY 1
ORDER BY 1;

-- 10. Scenario 6: Store performance — DT/m²
SELECT st.store_id, st.store_name, st.province, st.area_sqm, st.store_type,
       ROUND(SUM(s.revenue) / st.area_sqm / 1e6, 1) AS rev_per_sqm_m,
       ROUND(SUM(s.revenue) / 1e9, 2) AS total_rev_bn
FROM sales_transactions s
JOIN stores st ON s.store_id = st.store_id
WHERE s.transaction_date >= '2024-10-01'
GROUP BY st.store_id, st.store_name, st.province, st.area_sqm, st.store_type
ORDER BY rev_per_sqm_m DESC
LIMIT 15;
