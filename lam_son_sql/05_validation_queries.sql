-- =============================================================================
-- Lam Sơn Invest — Validation Queries
-- Database: construction_re_demo
-- =============================================================================

USE construction_re_demo;

-- =============================================================================
-- 1. TECHNICAL VALIDATION
-- =============================================================================

SELECT '=== 1. TECHNICAL VALIDATION ===' AS section;

-- Referential integrity
SELECT 'orphan_cost_items' AS check_name, COUNT(*) AS issues
FROM cost_items ci LEFT JOIN projects p ON ci.project_id = p.project_id WHERE p.project_id IS NULL
UNION ALL
SELECT 'orphan_receivables', COUNT(*)
FROM receivables r LEFT JOIN projects p ON r.project_id = p.project_id WHERE p.project_id IS NULL
UNION ALL
SELECT 'orphan_payables', COUNT(*)
FROM payables py LEFT JOIN projects p ON py.project_id = p.project_id WHERE p.project_id IS NULL
UNION ALL
SELECT 'orphan_material_purchases', COUNT(*)
FROM material_purchases mp LEFT JOIN projects p ON mp.project_id = p.project_id WHERE p.project_id IS NULL
UNION ALL
SELECT 'orphan_re_units', COUNT(*)
FROM real_estate_units reu LEFT JOIN projects p ON reu.project_id = p.project_id WHERE p.project_id IS NULL
UNION ALL
SELECT 'negative_cost_amounts', COUNT(*)
FROM cost_items WHERE actual_amount < 0
UNION ALL
SELECT 'negative_prices', COUNT(*)
FROM material_purchases WHERE unit_price < 0;

-- Cost consistency: actual_cost_to_date vs SUM(cost_items)
SELECT '=== Cost Consistency (TC projects) ===' AS section;
SELECT p.project_id, p.actual_cost_to_date AS project_level,
       SUM(ci.actual_amount) AS sum_cost_items,
       ABS(p.actual_cost_to_date - SUM(ci.actual_amount)) AS diff
FROM projects p
JOIN cost_items ci ON p.project_id = ci.project_id
WHERE p.project_type = 'thi_cong'
GROUP BY p.project_id;

-- Row counts
SELECT '=== Row Counts ===' AS section;
SELECT 'projects' AS tbl, COUNT(*) AS cnt FROM projects
UNION ALL SELECT 'project_milestones', COUNT(*) FROM project_milestones
UNION ALL SELECT 'cost_items', COUNT(*) FROM cost_items
UNION ALL SELECT 'material_purchases', COUNT(*) FROM material_purchases
UNION ALL SELECT 'material_price_index', COUNT(*) FROM material_price_index
UNION ALL SELECT 'project_financials', COUNT(*) FROM project_financials
UNION ALL SELECT 'bid_history', COUNT(*) FROM bid_history
UNION ALL SELECT 'receivables', COUNT(*) FROM receivables
UNION ALL SELECT 'payables', COUNT(*) FROM payables
UNION ALL SELECT 'cash_flow_actual', COUNT(*) FROM cash_flow_actual
UNION ALL SELECT 'real_estate_units', COUNT(*) FROM real_estate_units
UNION ALL SELECT 're_sales_monthly', COUNT(*) FROM re_sales_monthly
UNION ALL SELECT 'project_financing', COUNT(*) FROM project_financing;

-- =============================================================================
-- 2. STATISTICAL VALIDATION
-- =============================================================================

SELECT '=== 2. STATISTICAL VALIDATION ===' AS section;

-- Monthly revenue trend
SELECT '=== Monthly Revenue Trend ===' AS section;
SELECT DATE_FORMAT(fin_month, '%Y-%m') AS month,
       SUM(revenue_recognized) AS total_revenue
FROM project_financials GROUP BY month ORDER BY month;

-- Total revenue magnitude (~300-500 tỷ / 18 months)
SELECT '=== Total Revenue (tỷ VND) ===' AS section;
SELECT p.project_type, ROUND(SUM(pf.revenue_recognized)/1000, 0) AS revenue_ty
FROM project_financials pf JOIN projects p ON pf.project_id = p.project_id
GROUP BY p.project_type;

-- =============================================================================
-- 3. SCENARIO DRY-RUNS
-- =============================================================================

-- SCENARIO 1: Tổng quan dự án + Flag bất thường
SELECT '=== SCENARIO 1: RAG Status ===' AS section;
SELECT project_id, project_name, project_type, project_subtype,
       actual_progress_pct, planned_progress_pct,
       ROUND(actual_progress_pct - planned_progress_pct, 1) AS progress_gap,
       actual_cost_to_date, planned_budget,
       ROUND((actual_cost_to_date - planned_budget) / planned_budget * 100, 1) AS cost_variance_pct,
       CASE
         WHEN (actual_progress_pct - planned_progress_pct) < -15 OR
              (actual_cost_to_date - planned_budget) / planned_budget > 0.10 THEN 'RED'
         WHEN (actual_progress_pct - planned_progress_pct) < -5 OR
              (actual_cost_to_date - planned_budget) / planned_budget > 0.05 THEN 'YELLOW'
         ELSE 'GREEN'
       END AS rag_status,
       sold_units, total_units,
       CASE WHEN total_units > 0 THEN ROUND(sold_units/total_units*100,1) END AS absorption_pct
FROM projects
ORDER BY rag_status DESC, project_type;
-- Expected: TC-003 = RED (progress -23, cost +17%), BDS-001 absorption = 35%

-- SCENARIO 2: Cost overrun root cause TC-003
SELECT '=== SCENARIO 2: Cost Breakdown TC-003 ===' AS section;
SELECT cc.category_name_vi,
       SUM(ci.planned_amount) AS total_planned,
       SUM(ci.actual_amount) AS total_actual,
       ROUND((SUM(ci.actual_amount) - SUM(ci.planned_amount)) / SUM(ci.planned_amount) * 100, 1) AS variance_pct
FROM cost_items ci
JOIN cost_categories cc ON ci.category_id = cc.category_id
WHERE ci.project_id = 'TC-003'
GROUP BY cc.category_name_vi
ORDER BY variance_pct DESC;
-- Expected: NVL ~+28%, Thầu phụ ~+15%

SELECT '=== SCENARIO 2: Peak Steel Purchases ===' AS section;
SELECT mp.purchase_date, m.material_name, mp.unit_price AS buy_price,
       mpi.market_avg_price AS mkt_avg,
       ROUND((mp.unit_price - mpi.market_avg_price) / mpi.market_avg_price * 100, 1) AS premium_pct
FROM material_purchases mp
JOIN materials m ON mp.material_id = m.material_id
JOIN material_price_index mpi ON mp.material_id = mpi.material_id
  AND mpi.price_month = DATE(DATE_FORMAT(mp.purchase_date, '%Y-%m-01'))
WHERE mp.project_id = 'TC-003' AND mp.material_id IN (1,2)
ORDER BY premium_pct DESC LIMIT 5;
-- Expected: 2 purchases with premium > 8%

-- SCENARIO 3: Margin erosion
SELECT '=== SCENARIO 3: Margin by Subtype ===' AS section;
SELECT p.project_subtype,
       DATE_FORMAT(pf.fin_month, '%Y-%m') AS month,
       ROUND(AVG(pf.gross_margin_pct), 1) AS avg_margin
FROM project_financials pf
JOIN projects p ON pf.project_id = p.project_id
WHERE p.project_type = 'thi_cong'
GROUP BY p.project_subtype, month
ORDER BY p.project_subtype, month;
-- Expected: giao_thong 12.3% → 7.4% downtrend

SELECT '=== SCENARIO 3: Low Bid Ratios ===' AS section;
SELECT tender_name, project_subtype, bid_ratio, competitors_count, bid_date
FROM bid_history
WHERE project_subtype = 'giao_thong'
ORDER BY bid_date DESC LIMIT 5;
-- Expected: 3 recent bids with ratio < 0.88

-- SCENARIO 4: Cash flow risk
SELECT '=== SCENARIO 4: Cash Flow Recent ===' AS section;
SELECT * FROM cash_flow_actual ORDER BY flow_month DESC LIMIT 3;
-- Expected: closing_balance ~4,000-5,000

SELECT '=== SCENARIO 4: Critical Receivable ===' AS section;
SELECT project_id, milestone_name, amount, due_date, status, expected_collection_date, notes
FROM receivables
WHERE project_id = 'TC-003' AND amount >= 5000 AND status = 'du_kien';
-- Expected: 8,500 triệu, expected_date = NULL

SELECT '=== SCENARIO 4: Critical Payable ===' AS section;
SELECT project_id, category, description, amount, due_date, status
FROM payables
WHERE project_id = 'TC-003' AND amount >= 5000 AND due_date >= '2025-04-01';
-- Expected: 6,200 triệu, due 2025-05-10

-- SCENARIO 5: BĐS inventory
SELECT '=== SCENARIO 5: BĐS Inventory ===' AS section;
SELECT p.project_id, p.project_name, p.project_subtype,
       COUNT(CASE WHEN reu.status = 'chua_ban' THEN 1 END) AS unsold,
       p.total_units,
       ROUND(AVG(CASE WHEN reu.status = 'chua_ban' THEN DATEDIFF('2025-03-31', reu.listing_date) / 30 END), 1) AS avg_months_listed,
       SUM(CASE WHEN reu.status = 'chua_ban' THEN reu.listed_price ELSE 0 END) AS unsold_value
FROM real_estate_units reu
JOIN projects p ON reu.project_id = p.project_id
WHERE p.project_type = 'bat_dong_san'
GROUP BY p.project_id ORDER BY avg_months_listed DESC;
-- Expected: BDS-002 unsold=8, avg ~27 months, value ~12 tỷ

SELECT '=== SCENARIO 5: BDS-002 Sales Velocity ===' AS section;
SELECT sales_month, units_sold, units_available
FROM re_sales_monthly WHERE project_id = 'BDS-002' ORDER BY sales_month;
-- Expected: mostly 0-1 units/month, available starting ~12

SELECT '=== SCENARIO 5: Financing Cost ===' AS section;
SELECT project_id, loan_amount, interest_rate, monthly_interest
FROM project_financing WHERE project_id = 'BDS-002';
-- Expected: 12,000 triệu at 10%

-- =============================================================================
-- 4. FALLBACK CHECKS
-- =============================================================================

SELECT '=== FALLBACK: Normal project (TC-002) ===' AS section;
SELECT fin_month, revenue_recognized, cogs, gross_margin_pct
FROM project_financials WHERE project_id = 'TC-002' ORDER BY fin_month LIMIT 5;
-- Expected: margin 14-16%, stable

SELECT '=== FALLBACK: BDS-003 sales (no anomaly) ===' AS section;
SELECT COUNT(*) AS sold,
       (SELECT total_units FROM projects WHERE project_id='BDS-003') AS total,
       ROUND(AVG(actual_price),0) AS avg_price
FROM real_estate_units WHERE project_id = 'BDS-003' AND status IN ('da_ban','da_ban_giao');
-- Expected: ~58/80, reasonable price

SELECT '=== VALIDATION COMPLETE ===' AS section;
