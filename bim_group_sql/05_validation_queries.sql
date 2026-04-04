-- ============================================================================
-- BIM Group Real Estate & Construction Demo - Validation Queries
-- Mo ta: Kiem tra referential integrity, value ranges, completeness, anomalies
-- Database: bim_realestate_demo
-- ============================================================================

USE bim_realestate_demo;

-- ============================================================================
-- TECHNICAL CHECKS
-- ============================================================================

-- 1. Referential integrity
SELECT 'budget_disbursements orphan' AS check_name, COUNT(*) AS issues
FROM budget_disbursements bd
LEFT JOIN projects p ON bd.project_id = p.project_id
WHERE p.project_id IS NULL;

SELECT 'construction_costs orphan project' AS check_name, COUNT(*) AS issues
FROM construction_costs cc
LEFT JOIN projects p ON cc.project_id = p.project_id
WHERE p.project_id IS NULL;

SELECT 'construction_costs orphan contractor' AS check_name, COUNT(*) AS issues
FROM construction_costs cc
LEFT JOIN contractors c ON cc.contractor_id = c.contractor_id
WHERE c.contractor_id IS NULL;

SELECT 'construction_costs orphan work_package' AS check_name, COUNT(*) AS issues
FROM construction_costs cc
LEFT JOIN work_packages wp ON cc.work_package_id = wp.work_package_id
WHERE wp.work_package_id IS NULL;

SELECT 'hospitality_revenue orphan' AS check_name, COUNT(*) AS issues
FROM hospitality_revenue hr
LEFT JOIN properties p ON hr.property_id = p.property_id
WHERE p.property_id IS NULL;

SELECT 'hospitality_costs orphan' AS check_name, COUNT(*) AS issues
FROM hospitality_costs hc
LEFT JOIN properties p ON hc.property_id = p.property_id
WHERE p.property_id IS NULL;

SELECT 'occupancy_daily orphan' AS check_name, COUNT(*) AS issues
FROM occupancy_daily od
LEFT JOIN properties p ON od.property_id = p.property_id
WHERE p.property_id IS NULL;

SELECT 'change_orders orphan project' AS check_name, COUNT(*) AS issues
FROM change_orders co
LEFT JOIN projects p ON co.project_id = p.project_id
WHERE p.project_id IS NULL;

-- 2. Value ranges
SELECT 'negative budget amounts' AS check_name, COUNT(*) AS issues
FROM budget_disbursements WHERE actual_amount < 0 OR planned_amount < 0;

SELECT 'negative revenue' AS check_name, COUNT(*) AS issues
FROM hospitality_revenue WHERE total_revenue < 0;

SELECT 'occupancy > 100%' AS check_name, COUNT(*) AS issues
FROM occupancy_daily WHERE rooms_sold > rooms_available;

SELECT 'negative construction costs' AS check_name, COUNT(*) AS issues
FROM construction_costs WHERE actual_cost < 0 OR budgeted_cost < 0;

-- 3. Completeness
SELECT 'projects without budgets' AS check_name, COUNT(*) AS issues
FROM projects p
LEFT JOIN budget_disbursements bd ON p.project_id = bd.project_id
WHERE bd.project_id IS NULL AND p.status != 'Chuẩn bị';

SELECT 'properties without revenue' AS check_name, COUNT(*) AS issues
FROM properties p
LEFT JOIN hospitality_revenue hr ON p.property_id = hr.property_id
WHERE hr.property_id IS NULL;

-- 4. Record counts
SELECT 'budget_disbursements' AS table_name, COUNT(*) AS row_count FROM budget_disbursements
UNION ALL SELECT 'construction_costs', COUNT(*) FROM construction_costs
UNION ALL SELECT 'change_orders', COUNT(*) FROM change_orders
UNION ALL SELECT 'material_prices', COUNT(*) FROM material_prices
UNION ALL SELECT 'hospitality_revenue', COUNT(*) FROM hospitality_revenue
UNION ALL SELECT 'hospitality_costs', COUNT(*) FROM hospitality_costs
UNION ALL SELECT 'occupancy_daily', COUNT(*) FROM occupancy_daily
UNION ALL SELECT 'project_milestones', COUNT(*) FROM project_milestones
UNION ALL SELECT 'project_financials', COUNT(*) FROM project_financials
UNION ALL SELECT 'project_commitments', COUNT(*) FROM project_commitments
UNION ALL SELECT 'financing', COUNT(*) FROM financing;

-- ============================================================================
-- STATISTICAL CHECKS
-- ============================================================================

-- 5. Verify Phu Quoc seasonality (peak Q4-Q1)
SELECT 'Phu Quoc seasonality' AS check_name;
SELECT MONTH(date) AS m, ROUND(AVG(rooms_sold/rooms_available)*100, 1) AS avg_occ_pct
FROM occupancy_daily
WHERE property_id IN ('PR-PQ01','PR-PQ02','PR-PQ03')
GROUP BY MONTH(date) ORDER BY m;

-- 6. Verify Ha Long seasonality (peak Q2-Q3)
SELECT 'Ha Long seasonality' AS check_name;
SELECT MONTH(date) AS m, ROUND(AVG(rooms_sold/rooms_available)*100, 1) AS avg_occ_pct
FROM occupancy_daily
WHERE property_id = 'PR-HL01'
GROUP BY MONTH(date) ORDER BY m;

-- 7. Total hospitality revenue 12 months (2023)
SELECT 'Total hospitality revenue 2023 (ty VND)' AS check_name,
       ROUND(SUM(total_revenue)/1e9, 1) AS value
FROM hospitality_revenue
WHERE period BETWEEN '2023-01' AND '2023-12';

-- 8. Total active project budgets
SELECT 'Total active project budgets (ty VND)' AS check_name,
       ROUND(SUM(total_budget)/1e9, 1) AS value
FROM projects WHERE status != 'Chuẩn bị';

-- ============================================================================
-- DEMO SCENARIO DRY-RUN
-- ============================================================================

-- SCENARIO 1: Tong quan portfolio
SELECT '--- SCENARIO 1: Tong quan portfolio ---' AS section;
SELECT p.project_id, p.project_name, p.cluster_id,
       ROUND(p.total_budget/1e9, 0) AS budget_ty,
       ROUND(SUM(bd.actual_amount)/1e9, 0) AS disbursed_ty,
       ROUND(SUM(bd.actual_amount)/p.total_budget*100, 1) AS disbursed_pct,
       p.actual_progress_pct,
       ROUND(SUM(bd.actual_amount)/p.total_budget*100 - p.actual_progress_pct, 1) AS gap_pct,
       CASE
           WHEN SUM(bd.actual_amount)/p.total_budget*100 - p.actual_progress_pct > 10 THEN 'DO'
           WHEN SUM(bd.actual_amount)/p.total_budget*100 - p.actual_progress_pct > 5 THEN 'VANG'
           ELSE 'XANH'
       END AS rag_status
FROM projects p
LEFT JOIN budget_disbursements bd ON p.project_id = bd.project_id
WHERE p.status != 'Chuẩn bị'
GROUP BY p.project_id
ORDER BY gap_pct DESC;

-- SCENARIO 2: Drill down Ha Long construction costs
SELECT '--- SCENARIO 2: Drill down PJ-HL01 construction costs ---' AS section;
SELECT wp.category_vi AS hang_muc,
       ROUND(SUM(cc.budgeted_cost)/1e9, 1) AS du_toan_ty,
       ROUND(SUM(cc.actual_cost)/1e9, 1) AS thuc_te_ty,
       ROUND((SUM(cc.actual_cost) - SUM(cc.budgeted_cost))/1e9, 1) AS chenh_lech_ty,
       ROUND((SUM(cc.actual_cost)/SUM(cc.budgeted_cost) - 1)*100, 1) AS chenh_lech_pct
FROM construction_costs cc
JOIN work_packages wp ON cc.work_package_id = wp.work_package_id
WHERE cc.project_id = 'PJ-HL01'
GROUP BY wp.work_package_id, wp.category_vi
ORDER BY chenh_lech_ty DESC;

-- Change orders for PJ-HL01
SELECT '--- Change Orders PJ-HL01 ---' AS section;
SELECT change_order_id, reason_category, reason,
       ROUND(amount/1e9, 1) AS amount_ty, order_date
FROM change_orders
WHERE project_id = 'PJ-HL01'
ORDER BY order_date;

-- SCENARIO 3: Resort margins
SELECT '--- SCENARIO 3: Resort margins ---' AS section;
SELECT p.property_name,
       ROUND(SUM(hr.total_revenue)/1e9, 1) AS revenue_ty,
       ROUND(total_cost/1e9, 1) AS opex_ty,
       ROUND((SUM(hr.total_revenue) - total_cost)/SUM(hr.total_revenue)*100, 1) AS gop_margin_pct
FROM properties p
JOIN hospitality_revenue hr ON p.property_id = hr.property_id
JOIN (SELECT property_id, SUM(cost_amount) AS total_cost
      FROM hospitality_costs GROUP BY property_id) hc
     ON p.property_id = hc.property_id
GROUP BY p.property_id, p.property_name, total_cost
ORDER BY gop_margin_pct ASC;

-- Staff cost ratio for Citadines
SELECT '--- Staff cost ratio Citadines HL ---' AS section;
SELECT hc.property_id,
       ROUND(SUM(CASE WHEN hc.cost_category = 'Nhân sự' THEN hc.cost_amount ELSE 0 END)/1e9, 1) AS staff_cost_ty,
       ROUND(SUM(hr.total_revenue)/1e9, 1) AS revenue_ty,
       ROUND(SUM(CASE WHEN hc.cost_category = 'Nhân sự' THEN hc.cost_amount ELSE 0 END)
             / SUM(hr.total_revenue) * 100, 1) AS staff_pct
FROM hospitality_costs hc
JOIN hospitality_revenue hr ON hc.property_id = hr.property_id AND hc.period = hr.period
WHERE hc.property_id IN ('PR-HL01', 'PR-PQ01', 'PR-PQ02')
GROUP BY hc.property_id;

-- SCENARIO 4: Cluster comparison
SELECT '--- SCENARIO 4: Cluster comparison ---' AS section;
SELECT c.cluster_name,
       ROUND(AVG(pf.construction_cost_per_sqm)/1e6, 1) AS cost_per_sqm_trieu,
       ROUND(AVG(pf.expected_margin_pct), 1) AS avg_margin_pct,
       ROUND(AVG(pf.cost_variance_pct), 1) AS avg_variance_pct,
       ROUND(AVG(pf.estimated_irr_pct), 1) AS avg_irr_pct
FROM clusters c
JOIN projects p ON c.cluster_id = p.cluster_id
JOIN project_financials pf ON p.project_id = pf.project_id
WHERE p.status != 'Chuẩn bị'
GROUP BY c.cluster_name;

-- SCENARIO 5: Budget remaining
SELECT '--- SCENARIO 5: Budget remaining ---' AS section;
SELECT p.project_id, p.project_name,
       ROUND(p.total_budget/1e9, 0) AS budget_ty,
       ROUND(COALESCE(SUM(bd.actual_amount), 0)/1e9, 0) AS spent_ty,
       ROUND((p.total_budget - COALESCE(SUM(bd.actual_amount), 0))/1e9, 0) AS remaining_ty,
       p.status,
       pc.commitment_date, pc.has_penalty,
       f.loan_outstanding, f.annual_interest_rate_pct
FROM projects p
LEFT JOIN budget_disbursements bd ON p.project_id = bd.project_id
LEFT JOIN project_commitments pc ON p.project_id = pc.project_id
LEFT JOIN financing f ON p.project_id = f.project_id
GROUP BY p.project_id, pc.commitment_date, pc.has_penalty, f.loan_outstanding, f.annual_interest_rate_pct
ORDER BY remaining_ty DESC;

-- ============================================================================
-- FALLBACK CHECKS
-- ============================================================================

-- Fallback 1: Revenue Phu Quoc Q1/2024
SELECT '--- Fallback 1: Revenue PQ Q1/2024 ---' AS section;
SELECT p.property_name, ROUND(SUM(hr.total_revenue)/1e9, 1) AS revenue_ty
FROM hospitality_revenue hr
JOIN properties p ON hr.property_id = p.property_id
WHERE p.cluster_id = 'CL-PQ' AND hr.period BETWEEN '2024-01' AND '2024-03'
GROUP BY p.property_name;

-- Fallback 2: Contractor performance
SELECT '--- Fallback 2: Contractor performance ---' AS section;
SELECT c.contractor_name,
       COUNT(*) AS months_active,
       ROUND(AVG((cc.actual_cost - cc.budgeted_cost)/NULLIF(cc.budgeted_cost,0)*100), 1) AS avg_variance_pct
FROM construction_costs cc
JOIN contractors c ON cc.contractor_id = c.contractor_id
GROUP BY c.contractor_name
ORDER BY avg_variance_pct DESC
LIMIT 10;

-- Fallback 3: Project progress Phu Quoc
SELECT '--- Fallback 3: Project progress PQ ---' AS section;
SELECT project_name, actual_progress_pct, status
FROM projects WHERE cluster_id = 'CL-PQ';

-- Steel price trend
SELECT '--- Steel price trend ---' AS section;
SELECT period, price AS price_vnd_per_kg
FROM material_prices
WHERE material_id = 'MAT-01'
ORDER BY period;
