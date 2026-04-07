-- ============================================================
-- 05_validation_queries.sql
-- AP Saigon Petro — Validation Queries
-- Run after populating data to verify integrity & anomalies
-- ============================================================

USE lubricants_demo;

-- ============================================================
-- SECTION 1: TECHNICAL VALIDATION
-- ============================================================

-- 1.1 Record counts
SELECT '=== RECORD COUNTS ===' AS section;
SELECT 'regions' AS table_name, COUNT(*) AS row_count FROM regions
UNION ALL SELECT 'channels', COUNT(*) FROM channels
UNION ALL SELECT 'distributors', COUNT(*) FROM distributors
UNION ALL SELECT 'products', COUNT(*) FROM products
UNION ALL SELECT 'suppliers', COUNT(*) FROM suppliers
UNION ALL SELECT 'production_lines', COUNT(*) FROM production_lines
UNION ALL SELECT 'sales_orders', COUNT(*) FROM sales_orders
UNION ALL SELECT 'payments', COUNT(*) FROM payments
UNION ALL SELECT 'production_batches', COUNT(*) FROM production_batches
UNION ALL SELECT 'raw_material_costs', COUNT(*) FROM raw_material_costs;

-- 1.2 Referential integrity
SELECT '=== REFERENTIAL INTEGRITY ===' AS section;

SELECT 'orphan_sales_distributor' AS check_name, COUNT(*) AS issues
FROM sales_orders s LEFT JOIN distributors d ON s.distributor_id = d.distributor_id
WHERE d.distributor_id IS NULL;

SELECT 'orphan_sales_product' AS check_name, COUNT(*) AS issues
FROM sales_orders s LEFT JOIN products p ON s.product_id = p.product_id
WHERE p.product_id IS NULL;

SELECT 'orphan_payments_order' AS check_name, COUNT(*) AS issues
FROM payments p LEFT JOIN sales_orders s ON p.order_id = s.order_id
WHERE s.order_id IS NULL;

SELECT 'orphan_batch_line' AS check_name, COUNT(*) AS issues
FROM production_batches pb LEFT JOIN production_lines pl ON pb.line_id = pl.line_id
WHERE pl.line_id IS NULL;

SELECT 'orphan_batch_product' AS check_name, COUNT(*) AS issues
FROM production_batches pb LEFT JOIN products p ON pb.product_id = p.product_id
WHERE p.product_id IS NULL;

SELECT 'orphan_rmc_supplier' AS check_name, COUNT(*) AS issues
FROM raw_material_costs r LEFT JOIN suppliers s ON r.supplier_id = s.supplier_id
WHERE s.supplier_id IS NULL;

-- 1.3 Business logic checks
SELECT '=== BUSINESS LOGIC ===' AS section;

SELECT 'profit_calc_mismatch' AS check_name, COUNT(*) AS issues
FROM sales_orders
WHERE ABS(gross_profit_vnd - (total_revenue_vnd - total_cogs_vnd)) > 1;

SELECT 'cogs_sum_mismatch' AS check_name, COUNT(*) AS issues
FROM sales_orders
WHERE ABS(total_cogs_vnd - (cogs_material_vnd + cogs_production_vnd + cogs_transport_vnd)) > 1;

SELECT 'negative_revenue' AS check_name, COUNT(*) AS issues
FROM sales_orders WHERE total_revenue_vnd <= 0;

SELECT 'negative_cogs' AS check_name, COUNT(*) AS issues
FROM sales_orders WHERE total_cogs_vnd <= 0;

SELECT 'margin_out_of_range' AS check_name, COUNT(*) AS issues
FROM sales_orders WHERE gross_margin_pct < 0 OR gross_margin_pct > 60;

SELECT 'yield_out_of_range' AS check_name, COUNT(*) AS issues
FROM production_batches WHERE yield_rate < 0.90 OR yield_rate > 1.00;

SELECT 'negative_quantity' AS check_name, COUNT(*) AS issues
FROM sales_orders WHERE quantity_liters <= 0;

-- ============================================================
-- SECTION 2: STATISTICAL VALIDATION
-- ============================================================

-- 2.1 Monthly revenue trend (verify seasonality)
SELECT '=== MONTHLY REVENUE TREND ===' AS section;
SELECT DATE_FORMAT(order_date, '%Y-%m') AS month,
       COUNT(*) AS num_orders,
       ROUND(SUM(total_revenue_vnd)/1e9, 1) AS revenue_billion,
       ROUND(AVG(gross_margin_pct), 1) AS avg_margin_pct
FROM sales_orders
GROUP BY month ORDER BY month;

-- 2.2 Annual revenue magnitude check
SELECT '=== ANNUAL REVENUE (last 12 months) ===' AS section;
SELECT ROUND(SUM(total_revenue_vnd)/1e9, 1) AS annual_revenue_billion
FROM sales_orders
WHERE order_date >= DATE_SUB('2026-03-31', INTERVAL 12 MONTH);
-- Expect: 700-900 ty VND

-- 2.3 Pareto check: top 20% SKU revenue share
SELECT '=== PARETO CHECK ===' AS section;
SELECT
  ROUND(SUM(CASE WHEN rn <= total_products * 0.2 THEN revenue ELSE 0 END) / SUM(revenue) * 100, 1) AS top_20_pct_share
FROM (
  SELECT product_id, SUM(total_revenue_vnd) AS revenue,
         ROW_NUMBER() OVER (ORDER BY SUM(total_revenue_vnd) DESC) AS rn,
         COUNT(*) OVER () AS total_products
  FROM sales_orders GROUP BY product_id
) t;
-- Expect: 75-85%

-- 2.4 YoY growth rate
SELECT '=== YoY GROWTH ===' AS section;
SELECT
  ROUND((SUM(CASE WHEN order_date >= DATE_SUB('2026-03-31', INTERVAL 12 MONTH) THEN total_revenue_vnd ELSE 0 END) /
  NULLIF(SUM(CASE WHEN order_date >= DATE_SUB('2026-03-31', INTERVAL 24 MONTH)
    AND order_date < DATE_SUB('2026-03-31', INTERVAL 12 MONTH) THEN total_revenue_vnd ELSE 0 END), 0) - 1) * 100, 1) AS yoy_growth_pct;
-- Expect: 6-10%

-- ============================================================
-- SECTION 3: DEMO SCENARIO DRY-RUNS
-- ============================================================

-- Scenario 1: Revenue & margin 6 months vs same period last year
SELECT '=== SCENARIO 1: REVENUE & MARGIN ===' AS section;
SELECT
  'current_6m' AS period,
  ROUND(SUM(total_revenue_vnd)/1e9, 1) AS revenue_bn,
  ROUND(SUM(gross_profit_vnd)/1e9, 1) AS profit_bn,
  ROUND(SUM(gross_profit_vnd)/SUM(total_revenue_vnd)*100, 1) AS margin_pct
FROM sales_orders
WHERE order_date >= '2025-10-01' AND order_date <= '2026-03-31'
UNION ALL
SELECT
  'same_period_ly',
  ROUND(SUM(total_revenue_vnd)/1e9, 1),
  ROUND(SUM(gross_profit_vnd)/1e9, 1),
  ROUND(SUM(gross_profit_vnd)/SUM(total_revenue_vnd)*100, 1)
FROM sales_orders
WHERE order_date >= '2024-10-01' AND order_date <= '2025-03-31';
-- Expect: current margin ~24-26%, last year ~27-29%

-- Scenario 2: Margin by region
SELECT '=== SCENARIO 2: MARGIN BY REGION ===' AS section;
SELECT r.region_name, r.macro_region,
  ROUND(SUM(s.total_revenue_vnd)/1e9, 1) AS revenue_bn,
  ROUND(SUM(s.gross_profit_vnd)/SUM(s.total_revenue_vnd)*100, 1) AS margin_pct
FROM sales_orders s
JOIN distributors d ON s.distributor_id = d.distributor_id
JOIN regions r ON d.region_id = r.region_id
WHERE s.order_date >= '2025-10-01'
GROUP BY r.region_name, r.macro_region
ORDER BY margin_pct ASC;
-- Expect: DBSCL ~19%, others ~24-31%

-- Scenario 2b: Margin by product type
SELECT '=== SCENARIO 2b: MARGIN BY PRODUCT TYPE ===' AS section;
SELECT p.product_type,
  ROUND(SUM(s.total_revenue_vnd)/1e9, 1) AS revenue_bn,
  ROUND(SUM(s.gross_profit_vnd)/SUM(s.total_revenue_vnd)*100, 1) AS margin_pct
FROM sales_orders s
JOIN products p ON s.product_id = p.product_id
WHERE s.order_date >= '2025-10-01'
GROUP BY p.product_type
ORDER BY margin_pct ASC;

-- Scenario 3: Top/Bottom NPP
SELECT '=== SCENARIO 3: TOP 10 NPP BY REVENUE ===' AS section;
SELECT d.distributor_id, d.distributor_name, d.tier,
  ROUND(SUM(s.total_revenue_vnd)/1e9, 1) AS revenue_bn,
  ROUND(SUM(s.quantity_liters)/1000, 0) AS volume_k_liters
FROM sales_orders s
JOIN distributors d ON s.distributor_id = d.distributor_id
WHERE s.order_date >= '2025-10-01'
GROUP BY d.distributor_id, d.distributor_name, d.tier
ORDER BY revenue_bn DESC
LIMIT 10;

-- Scenario 3b: DSO trend for anomaly NPPs
SELECT '=== SCENARIO 3b: DSO TREND (ANOMALY NPPs) ===' AS section;
SELECT d.distributor_name,
  DATE_FORMAT(s.order_date, '%Y-%m') AS order_month,
  ROUND(AVG(p.days_from_invoice), 0) AS avg_dso,
  COUNT(*) AS num_payments
FROM payments p
JOIN sales_orders s ON p.order_id = s.order_id
JOIN distributors d ON p.distributor_id = d.distributor_id
WHERE p.distributor_id IN ('NPP-008', 'NPP-015', 'NPP-022')
AND s.order_date >= '2025-10-01'
GROUP BY d.distributor_name, order_month
ORDER BY d.distributor_name, order_month;

-- Scenario 3c: NPP Bach Khoa growth
SELECT '=== SCENARIO 3c: NPP BACH KHOA GROWTH ===' AS section;
SELECT
  'current_year' AS period,
  ROUND(SUM(total_revenue_vnd)/1e9, 2) AS revenue_bn,
  ROUND(SUM(quantity_liters)/1000, 0) AS volume_k
FROM sales_orders
WHERE distributor_id = 'NPP-003' AND order_date >= '2025-04-01'
UNION ALL
SELECT
  'previous_year',
  ROUND(SUM(total_revenue_vnd)/1e9, 2),
  ROUND(SUM(quantity_liters)/1000, 0)
FROM sales_orders
WHERE distributor_id = 'NPP-003' AND order_date >= '2024-10-01' AND order_date < '2025-04-01';

-- Scenario 4: Production yield by line
SELECT '=== SCENARIO 4: YIELD BY LINE (last 4 months) ===' AS section;
SELECT pl.line_name,
  DATE_FORMAT(pb.batch_date, '%Y-%m') AS month,
  ROUND(AVG(pb.yield_rate), 3) AS avg_yield,
  ROUND(AVG(pb.cost_per_liter_vnd), 0) AS avg_cost_per_liter
FROM production_batches pb
JOIN production_lines pl ON pb.line_id = pl.line_id
WHERE pb.batch_date >= '2025-12-01'
GROUP BY pl.line_name, month
ORDER BY pl.line_name, month;

-- Scenario 4b: Overall capacity utilization
SELECT '=== SCENARIO 4b: CAPACITY UTILIZATION ===' AS section;
SELECT DATE_FORMAT(pb.batch_date, '%Y-%m') AS month,
  ROUND(SUM(pb.output_quantity_liters) / 2850000 * 100, 1) AS utilization_pct
FROM production_batches pb
WHERE pb.batch_date >= '2025-06-01'
GROUP BY month ORDER BY month;

-- Scenario 5: Raw material price trend
SELECT '=== SCENARIO 5: RAW MATERIAL PRICE TREND ===' AS section;
SELECT DATE_FORMAT(month_date, '%Y-%m') AS month,
  material_type,
  ROUND(AVG(price_per_liter_vnd), 0) AS avg_price
FROM raw_material_costs
WHERE material_type IN ('base_oil_group_I', 'base_oil_group_II', 'base_oil_group_III')
GROUP BY month, material_type
ORDER BY material_type, month;

-- ============================================================
-- SECTION 4: FALLBACK QUERIES
-- ============================================================

-- Fallback 1: Industrial oil revenue in North
SELECT '=== FALLBACK 1: INDUSTRIAL OIL - NORTH ===' AS section;
SELECT DATE_FORMAT(s.order_date, '%Y-%m') AS month,
  ROUND(SUM(s.total_revenue_vnd)/1e9, 2) AS revenue_bn
FROM sales_orders s
JOIN distributors d ON s.distributor_id = d.distributor_id
JOIN regions r ON d.region_id = r.region_id
JOIN products p ON s.product_id = p.product_id
WHERE r.macro_region = 'Miền Bắc' AND p.product_group = 'Dầu công nghiệp'
AND s.order_date >= DATE_SUB('2026-03-31', INTERVAL 12 MONTH)
GROUP BY month ORDER BY month;

-- Fallback 2: Top 5 best-selling products
SELECT '=== FALLBACK 2: TOP 5 PRODUCTS ===' AS section;
SELECT p.product_name,
  ROUND(SUM(s.quantity_liters)/1000, 0) AS total_volume_k,
  ROUND(SUM(s.total_revenue_vnd)/1e9, 2) AS revenue_bn
FROM sales_orders s JOIN products p ON s.product_id = p.product_id
WHERE s.order_date >= '2025-10-01'
GROUP BY p.product_name ORDER BY total_volume_k DESC LIMIT 5;

-- Fallback 3: Payment status overview
SELECT '=== FALLBACK 3: PAYMENT STATUS ===' AS section;
SELECT payment_status,
  COUNT(*) AS num_orders,
  ROUND(SUM(total_revenue_vnd)/1e9, 1) AS amount_bn
FROM sales_orders
WHERE order_date >= '2025-10-01'
GROUP BY payment_status;
