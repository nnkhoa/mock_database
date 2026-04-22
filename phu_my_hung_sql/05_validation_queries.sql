-- =============================================================================
-- Phú Mỹ Hưng Development — Validation Queries
-- Run after loading 01-04 to verify data correctness
-- =============================================================================

USE phu_my_hung_demo;

-- =============================================================================
-- 1. TABLE ROW COUNTS
-- =============================================================================
SELECT '=== TABLE ROW COUNTS ===' AS section;

SELECT 'projects' AS tbl, COUNT(*) AS cnt FROM projects UNION ALL
SELECT 'project_phases', COUNT(*) FROM project_phases UNION ALL
SELECT 'contractors', COUNT(*) FROM contractors UNION ALL
SELECT 'unit_types', COUNT(*) FROM unit_types UNION ALL
SELECT 'cost_categories', COUNT(*) FROM cost_categories UNION ALL
SELECT 'management_zones', COUNT(*) FROM management_zones UNION ALL
SELECT 'commercial_tenants', COUNT(*) FROM commercial_tenants UNION ALL
SELECT 'project_financials', COUNT(*) FROM project_financials UNION ALL
SELECT 'project_budgets', COUNT(*) FROM project_budgets UNION ALL
SELECT 'unit_sales', COUNT(*) FROM unit_sales UNION ALL
SELECT 'payment_schedules', COUNT(*) FROM payment_schedules UNION ALL
SELECT 'payment_collections', COUNT(*) FROM payment_collections UNION ALL
SELECT 'revenue_recognition', COUNT(*) FROM revenue_recognition UNION ALL
SELECT 'construction_costs', COUNT(*) FROM construction_costs UNION ALL
SELECT 'contractor_invoices', COUNT(*) FROM contractor_invoices UNION ALL
SELECT 'contract_milestones', COUNT(*) FROM contract_milestones UNION ALL
SELECT 'project_assignments', COUNT(*) FROM project_assignments UNION ALL
SELECT 'change_orders', COUNT(*) FROM change_orders UNION ALL
SELECT 'material_prices', COUNT(*) FROM material_prices UNION ALL
SELECT 'debt_schedule', COUNT(*) FROM debt_schedule UNION ALL
SELECT 'debt_payments', COUNT(*) FROM debt_payments UNION ALL
SELECT 'unsold_inventory', COUNT(*) FROM unsold_inventory UNION ALL
SELECT 'project_permits', COUNT(*) FROM project_permits UNION ALL
SELECT 'construction_payment_schedule', COUNT(*) FROM construction_payment_schedule UNION ALL
SELECT 'management_costs', COUNT(*) FROM management_costs UNION ALL
SELECT 'management_revenue', COUNT(*) FROM management_revenue UNION ALL
SELECT 'maintenance_tickets', COUNT(*) FROM maintenance_tickets UNION ALL
SELECT 'lease_income', COUNT(*) FROM lease_income UNION ALL
SELECT 'management_fees_monthly', COUNT(*) FROM management_fees_monthly UNION ALL
SELECT '_meta_tables', COUNT(*) FROM _meta_tables UNION ALL
SELECT '_meta_columns', COUNT(*) FROM _meta_columns UNION ALL
SELECT '_meta_kpi', COUNT(*) FROM _meta_kpi UNION ALL
SELECT '_meta_glossary', COUNT(*) FROM _meta_glossary;

-- =============================================================================
-- 2. REFERENTIAL INTEGRITY
-- =============================================================================
SELECT '=== REFERENTIAL INTEGRITY ===' AS section;

SELECT 'unit_sales → projects' AS fk_check,
       COUNT(*) AS orphan_count
FROM unit_sales us LEFT JOIN projects p ON us.project_id = p.project_id
WHERE p.project_id IS NULL
UNION ALL
SELECT 'payment_collections → unit_sales',
       COUNT(*) FROM payment_collections pc LEFT JOIN unit_sales us ON pc.sale_id = us.sale_id WHERE us.sale_id IS NULL
UNION ALL
SELECT 'construction_costs → projects',
       COUNT(*) FROM construction_costs cc LEFT JOIN projects p ON cc.project_id = p.project_id WHERE p.project_id IS NULL
UNION ALL
SELECT 'management_costs → zones',
       COUNT(*) FROM management_costs mc LEFT JOIN management_zones mz ON mc.zone_id = mz.zone_id WHERE mz.zone_id IS NULL
UNION ALL
SELECT 'lease_income → tenants',
       COUNT(*) FROM lease_income li LEFT JOIN commercial_tenants ct ON li.tenant_id = ct.tenant_id WHERE ct.tenant_id IS NULL;

-- =============================================================================
-- 3. SCENARIO 1: Portfolio Performance (Q2 2025)
-- =============================================================================
SELECT '=== SCENARIO 1: Portfolio Performance ===' AS section;

SELECT p.name,
       ROUND(SUM(pf.revenue_vnd)/1e9, 1) AS revenue_bn,
       ROUND(SUM(pf.cost_vnd)/1e9, 1) AS cost_bn,
       ROUND((SUM(pf.revenue_vnd) - SUM(pf.cost_vnd)) / NULLIF(SUM(pf.revenue_vnd), 0) * 100, 1) AS margin_pct
FROM project_financials pf
JOIN projects p ON pf.project_id = p.project_id
WHERE pf.month_date BETWEEN '2025-04-01' AND '2025-06-01'
GROUP BY p.name
ORDER BY revenue_bn DESC;

-- L'Arcade recognition gap
SELECT '=== L''Arcade Recognition Gap ===' AS section;
SELECT month_date, sell_through_pct, recognized_pct, construction_completion_pct
FROM revenue_recognition
WHERE project_id = 'PRJ-002'
ORDER BY month_date DESC LIMIT 6;

-- =============================================================================
-- 4. SCENARIO 2: The Horizon Cost Overrun
-- =============================================================================
SELECT '=== SCENARIO 2: The Horizon Cost Overrun ===' AS section;

SELECT cc.category,
       ROUND(SUM(cc.actual_cost_vnd)/1e9, 1) AS actual_bn,
       ROUND(SUM(cc.budgeted_cost_vnd)/1e9, 1) AS budget_bn,
       ROUND((SUM(cc.actual_cost_vnd) - SUM(cc.budgeted_cost_vnd)) / NULLIF(SUM(cc.budgeted_cost_vnd), 0) * 100, 1) AS variance_pct
FROM construction_costs cc
WHERE cc.project_id = 'PRJ-004'
GROUP BY cc.category
ORDER BY variance_pct DESC;

-- Total Horizon overrun
SELECT ROUND(SUM(actual_cost_vnd)/1e9, 1) AS total_actual_bn,
       ROUND(SUM(budgeted_cost_vnd)/1e9, 1) AS total_budget_bn,
       ROUND((SUM(actual_cost_vnd) - SUM(budgeted_cost_vnd)) / NULLIF(SUM(budgeted_cost_vnd), 0) * 100, 1) AS overrun_pct
FROM construction_costs WHERE project_id = 'PRJ-004';

-- Steel price trend
SELECT month_date, price_index FROM material_prices
WHERE material_type = 'steel_rebar' ORDER BY month_date;

-- =============================================================================
-- 5. SCENARIO 3: Contractor OTD
-- =============================================================================
SELECT '=== SCENARIO 3: Contractor OTD Ranking ===' AS section;

SELECT c.name,
       COUNT(*) AS total_milestones,
       SUM(CASE WHEN cm.actual_date <= cm.planned_date THEN 1 ELSE 0 END) AS on_time,
       ROUND(SUM(CASE WHEN cm.actual_date <= cm.planned_date THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) AS otd_pct
FROM contract_milestones cm
JOIN contractors c ON cm.contractor_id = c.contractor_id
WHERE cm.actual_date IS NOT NULL
GROUP BY c.name
ORDER BY otd_pct ASC;

-- Delta future assignment warning
SELECT pa.project_id, p.name AS project_name, pa.scope_description, pa.status
FROM project_assignments pa
JOIN projects p ON pa.project_id = p.project_id
WHERE pa.contractor_id = 'CTR-005' AND pa.status = 'planned';

-- =============================================================================
-- 6. SCENARIO 4: Cash Flow Projection
-- =============================================================================
SELECT '=== SCENARIO 4: Cash Flow Q2 2025 ===' AS section;

SELECT 'Inflow (Collections)' AS type, ROUND(SUM(amount_vnd)/1e9, 1) AS total_bn
FROM payment_collections WHERE payment_date BETWEEN '2025-04-01' AND '2025-06-30'
UNION ALL
SELECT 'Construction Outflow', ROUND(SUM(planned_amount_vnd)/1e9, 1)
FROM construction_payment_schedule WHERE month_date BETWEEN '2025-04-01' AND '2025-06-01'
UNION ALL
SELECT 'Debt Service', ROUND(SUM(interest_amount_vnd + principal_amount_vnd)/1e9, 1)
FROM debt_payments WHERE payment_date BETWEEN '2025-04-01' AND '2025-06-30';

-- =============================================================================
-- 7. SCENARIO 5: Risk Briefing
-- =============================================================================
SELECT '=== SCENARIO 5: Debt Maturities ===' AS section;

SELECT instrument_name, currency, principal_amount, maturity_date, status
FROM debt_schedule
WHERE status = 'active'
ORDER BY maturity_date;

-- Unsold inventory aging
SELECT '=== Unsold Inventory Aging ===' AS section;
SELECT unit_id, listing_date, DATEDIFF(CURDATE(), listing_date) AS days_listed,
       ROUND(monthly_carrying_cost_vnd/1e6, 1) AS carrying_mn
FROM unsold_inventory
ORDER BY days_listed DESC;

-- Hồng Hạc pre-sale permit
SELECT '=== Hồng Hạc Permit Status ===' AS section;
SELECT project_id, permit_type, status, expected_date, actual_date
FROM project_permits
WHERE project_id = 'PRJ-005';

-- =============================================================================
-- 8. SCENARIO 6: Property Management Costs
-- =============================================================================
SELECT '=== SCENARIO 6: Management Cost per Unit by Zone ===' AS section;

SELECT mz.name,
       ROUND(SUM(mc.cost_vnd) / mz.total_units / 18 / 1e6, 1) AS avg_cost_per_unit_mn
FROM management_costs mc
JOIN management_zones mz ON mc.zone_id = mz.zone_id
GROUP BY mz.name, mz.total_units
ORDER BY avg_cost_per_unit_mn DESC;

-- Cảnh Đồi elevator maintenance trend
SELECT '=== Cảnh Đồi Elevator Maintenance Trend ===' AS section;
SELECT month_date, ROUND(cost_vnd/1e6, 1) AS cost_mn
FROM management_costs
WHERE zone_id = 'ZON-002' AND cost_category = 'elevator_maintenance'
ORDER BY month_date;

-- =============================================================================
-- 9. OFF-SCRIPT QUERIES
-- =============================================================================
SELECT '=== OFF-SCRIPT: Revenue by Segment ===' AS section;
SELECT p.segment, ROUND(SUM(pf.revenue_vnd)/1e9, 0) AS total_revenue_bn
FROM project_financials pf JOIN projects p ON pf.project_id = p.project_id
GROUP BY p.segment ORDER BY total_revenue_bn DESC;

SELECT '=== OFF-SCRIPT: Management Revenue by Zone ===' AS section;
SELECT mz.name, ROUND(SUM(mr.revenue_vnd)/1e9, 1) AS total_bn
FROM management_revenue mr JOIN management_zones mz ON mr.zone_id = mz.zone_id
GROUP BY mz.name ORDER BY total_bn DESC;

SELECT '=== OFF-SCRIPT: Lease Income by Tenant Type ===' AS section;
SELECT ct.tenant_type, ROUND(SUM(li.monthly_rent_vnd)/1e9, 1) AS total_rent_bn
FROM lease_income li JOIN commercial_tenants ct ON li.tenant_id = ct.tenant_id
GROUP BY ct.tenant_type ORDER BY total_rent_bn DESC;

-- =============================================================================
-- 10. ANNUAL REVENUE MAGNITUDE CHECK
-- =============================================================================
SELECT '=== ANNUAL REVENUE CHECK ===' AS section;
SELECT YEAR(month_date) AS yr, ROUND(SUM(revenue_vnd)/1e9, 0) AS total_revenue_bn
FROM project_financials
GROUP BY YEAR(month_date);

-- Seasonality pattern
SELECT '=== SEASONALITY PATTERN ===' AS section;
SELECT MONTH(month_date) AS mo, ROUND(AVG(revenue_vnd)/1e9, 1) AS avg_revenue_bn
FROM project_financials
WHERE project_id != 'PRJ-005'
GROUP BY MONTH(month_date)
ORDER BY mo;
