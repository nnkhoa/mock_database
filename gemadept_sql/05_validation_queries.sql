-- ============================================================
-- Gemadept Seaport Demo — Validation Queries
-- Database: seaport_demo
-- Purpose:  Verify data integrity, completeness, and demo
--           scenario readiness after populating all tables.
-- ============================================================

USE seaport_demo;

-- ============================================================
-- SECTION A: TECHNICAL CHECKS
-- ============================================================

-- 1. Referential integrity
SELECT 'orphan_port_revenue' AS check_name, COUNT(*) AS issues
FROM port_revenue pr LEFT JOIN ports p ON pr.port_id = p.port_id WHERE p.port_id IS NULL;

SELECT 'orphan_shipping_line_rev' AS check_name, COUNT(*)
FROM shipping_line_revenue slr LEFT JOIN shipping_lines sl ON slr.shipping_line_id = sl.shipping_line_id WHERE sl.shipping_line_id IS NULL;

SELECT 'orphan_operating_costs' AS check_name, COUNT(*)
FROM operating_costs oc LEFT JOIN cost_types ct ON oc.cost_type_id = ct.cost_type_id WHERE ct.cost_type_id IS NULL;

-- 2. Completeness: each port must have 18 months of data
SELECT 'port_revenue_completeness' AS check_name, port_id, COUNT(DISTINCT month) AS months FROM port_revenue GROUP BY port_id;
SELECT 'operating_costs_completeness' AS check_name, port_id, COUNT(DISTINCT month) AS months FROM operating_costs GROUP BY port_id;

-- 3. No negative values
SELECT 'negative_revenue' AS check_name, COUNT(*) FROM port_revenue WHERE total_revenue_vnd < 0;
SELECT 'negative_cost' AS check_name, COUNT(*) FROM operating_costs WHERE cost_amount_vnd < 0;

-- 4. Record counts
SELECT 'port_revenue' AS tbl, COUNT(*) AS cnt FROM port_revenue
UNION ALL SELECT 'container_throughput', COUNT(*) FROM container_throughput
UNION ALL SELECT 'operating_costs', COUNT(*) FROM operating_costs
UNION ALL SELECT 'shipping_line_revenue', COUNT(*) FROM shipping_line_revenue
UNION ALL SELECT 'vessel_calls', COUNT(*) FROM vessel_calls
UNION ALL SELECT 'equipment_utilization', COUNT(*) FROM equipment_utilization
UNION ALL SELECT 'equipment_maintenance', COUNT(*) FROM equipment_maintenance
UNION ALL SELECT 'customer_revenue', COUNT(*) FROM customer_revenue;

-- ============================================================
-- SECTION B: STATISTICAL CHECKS
-- ============================================================

-- 5. Revenue by year (2024 target: 4,200-4,800 ty)
SELECT YEAR(month) AS yr, ROUND(SUM(total_revenue_vnd)/1e9, 0) AS revenue_bn
FROM port_revenue GROUP BY YEAR(month);

-- 6. Revenue by port
SELECT port_id, YEAR(month) as yr, ROUND(SUM(total_revenue_vnd)/1e9, 0) AS revenue_bn
FROM port_revenue GROUP BY port_id, YEAR(month) ORDER BY port_id, yr;

-- 7. Monthly seasonality check (should see dip in Jan-Feb, peak Jul-Sep)
SELECT MONTH(month) AS m, ROUND(AVG(total_revenue_vnd)/1e9, 1) AS avg_rev_bn
FROM port_revenue WHERE port_id='NDV' GROUP BY MONTH(month) ORDER BY m;

-- 8. Pareto check: top 3 shipping lines per port ~ 55% revenue
SELECT port_id, shipping_line_id,
  ROUND(SUM(revenue_vnd)/1e9, 1) AS rev_bn,
  ROUND(SUM(revenue_vnd)*100.0 / SUM(SUM(revenue_vnd)) OVER (PARTITION BY port_id), 1) AS pct
FROM shipping_line_revenue GROUP BY port_id, shipping_line_id ORDER BY port_id, rev_bn DESC;

-- ============================================================
-- SECTION C: DEMO SCENARIO DRY-RUNS
-- ============================================================

-- SCENARIO 1: 6-month overview H1/2025 vs H1/2024
SELECT p.port_name_short,
  ROUND(SUM(CASE WHEN pr.month BETWEEN '2025-01-01' AND '2025-06-30' THEN pr.total_revenue_vnd ELSE 0 END)/1e9, 0) AS rev_h1_2025,
  ROUND(SUM(CASE WHEN pr.month BETWEEN '2024-01-01' AND '2024-06-30' THEN pr.total_revenue_vnd ELSE 0 END)/1e9, 0) AS rev_h1_2024,
  ROUND((SUM(CASE WHEN pr.month BETWEEN '2025-01-01' AND '2025-06-30' THEN pr.total_revenue_vnd ELSE 0 END) /
    NULLIF(SUM(CASE WHEN pr.month BETWEEN '2024-01-01' AND '2024-06-30' THEN pr.total_revenue_vnd ELSE 0 END), 0) - 1) * 100, 1) AS yoy_pct
FROM port_revenue pr JOIN ports p ON pr.port_id = p.port_id
GROUP BY p.port_name_short;

-- SCENARIO 2: NDV margin trend (should see ~49% -> ~40% in May-Jun)
SELECT pr.month,
  ROUND(pr.rev/1e9, 1) AS rev_bn,
  ROUND(oc.cost/1e9, 1) AS cost_bn,
  ROUND((pr.rev - oc.cost)*100.0/pr.rev, 1) AS gross_margin_pct
FROM (SELECT month, SUM(total_revenue_vnd) as rev FROM port_revenue WHERE port_id='NDV' GROUP BY month) pr
JOIN (SELECT month, SUM(cost_amount_vnd) as cost FROM operating_costs WHERE port_id='NDV' GROUP BY month) oc ON pr.month = oc.month
WHERE pr.month >= '2025-01-01' ORDER BY pr.month;

-- SCENARIO 2: Maintenance spike
SELECT month, ROUND(cost_amount_vnd/1e9, 1) AS maint_bn
FROM operating_costs WHERE port_id='NDV' AND cost_type_id='maintenance' AND month >= '2024-07-01' ORDER BY month;

-- SCENARIO 2: Bulk mix change
SELECT month, volume_tons FROM container_throughput
WHERE port_id='NDV' AND cargo_type_id='bulk' AND month >= '2024-07-01' ORDER BY month;

-- SCENARIO 3: NDV vs GML head-to-head (latest 6 months)
SELECT p.port_name_short,
  ROUND(SUM(pr.total_revenue_vnd)/1e9, 0) AS rev_bn,
  ROUND(SUM(oc.cost)/1e9, 0) AS cost_bn,
  ROUND((SUM(pr.total_revenue_vnd) - SUM(oc.cost))*100.0/SUM(pr.total_revenue_vnd), 1) AS margin_pct
FROM (SELECT port_id, SUM(total_revenue_vnd) as total_revenue_vnd FROM port_revenue WHERE month >= '2025-01-01' GROUP BY port_id) pr
JOIN (SELECT port_id, SUM(cost_amount_vnd) as cost FROM operating_costs WHERE month >= '2025-01-01' GROUP BY port_id) oc ON pr.port_id = oc.port_id
JOIN ports p ON pr.port_id = p.port_id
WHERE pr.port_id IN ('NDV', 'GML')
GROUP BY p.port_name_short;

-- SCENARIO 4: Maersk at NDV (should decline Apr-Jun 2025)
SELECT month, volume_teu, ROUND(revenue_vnd/1e9, 1) AS rev_bn
FROM shipping_line_revenue
WHERE shipping_line_id='MAERSK' AND port_id='NDV' AND month >= '2025-01-01' ORDER BY month;

-- SCENARIO 4: Maersk at GML (should be stable)
SELECT month, volume_teu, ROUND(revenue_vnd/1e9, 1) AS rev_bn
FROM shipping_line_revenue
WHERE shipping_line_id='MAERSK' AND port_id='GML' AND month >= '2025-01-01' ORDER BY month;

-- SCENARIO 6: Gemalink 2A investment data
SELECT * FROM investment_projects WHERE project_id = 'GML_2A';

-- FALLBACK: Top 5 customers at GML
SELECT c.customer_name, ROUND(SUM(cr.revenue_vnd)/1e9, 1) AS total_rev_bn
FROM customer_revenue cr JOIN customers c ON cr.customer_id = c.customer_id
WHERE cr.port_id='GML' AND cr.month >= '2025-01-01'
GROUP BY c.customer_name ORDER BY total_rev_bn DESC LIMIT 5;

-- FALLBACK: Equipment availability PHL
SELECT e.equipment_name, ROUND(AVG(eu.availability_pct), 1) AS avg_availability
FROM equipment_utilization eu JOIN equipment e ON eu.equipment_id = e.equipment_id
WHERE e.port_id='PHL' AND eu.month >= '2025-01-01'
GROUP BY e.equipment_name;
