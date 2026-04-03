-- ============================================================================
-- SASCO Demo Database - Validation Queries
-- Mo ta: SELECT queries de verify data integrity va business logic
-- ============================================================================

USE sasco_demo;

-- ============================================================================
-- 1. TECHNICAL VALIDATION
-- ============================================================================

-- 1.1 Record counts
SELECT 'Record Counts' AS section;
SELECT 'terminals' AS tbl, COUNT(*) AS cnt FROM terminals
UNION ALL SELECT 'business_lines', COUNT(*) FROM business_lines
UNION ALL SELECT 'locations', COUNT(*) FROM locations
UNION ALL SELECT 'lounges', COUNT(*) FROM lounges
UNION ALL SELECT 'nationality_groups', COUNT(*) FROM nationality_groups
UNION ALL SELECT 'product_categories', COUNT(*) FROM product_categories
UNION ALL SELECT 'products', COUNT(*) FROM products
UNION ALL SELECT 'passenger_traffic', COUNT(*) FROM passenger_traffic
UNION ALL SELECT 'lounge_visits', COUNT(*) FROM lounge_visits
UNION ALL SELECT 'sales_transactions', COUNT(*) FROM sales_transactions
UNION ALL SELECT '_meta_tables', COUNT(*) FROM _meta_tables
UNION ALL SELECT '_meta_columns', COUNT(*) FROM _meta_columns
UNION ALL SELECT '_meta_kpi', COUNT(*) FROM _meta_kpi
UNION ALL SELECT '_meta_glossary', COUNT(*) FROM _meta_glossary;

-- 1.2 Orphan checks
SELECT 'Orphan Checks' AS section;
SELECT 'Orphan sales.location_id' AS check_name, COUNT(*) AS cnt
FROM sales_transactions st LEFT JOIN locations l ON st.location_id = l.location_id WHERE l.location_id IS NULL
UNION ALL
SELECT 'Orphan sales.product_id', COUNT(*)
FROM sales_transactions st LEFT JOIN products p ON st.product_id = p.product_id WHERE p.product_id IS NULL;

-- 1.3 Revenue ranges
SELECT 'Revenue Ranges' AS section;
SELECT business_line_id,
       MIN(total_revenue_vnd) AS min_rev,
       MAX(total_revenue_vnd) AS max_rev,
       ROUND(AVG(total_revenue_vnd)) AS avg_rev
FROM sales_transactions
GROUP BY business_line_id;

-- ============================================================================
-- 2. STATISTICAL VALIDATION
-- ============================================================================

-- 2.1 Revenue by business line (2024)
SELECT 'Revenue by BL 2024' AS section;
SELECT bl.business_line_name,
       ROUND(SUM(st.total_revenue_vnd)/1e9, 1) AS revenue_ty,
       ROUND(SUM(st.total_revenue_vnd)/(SELECT SUM(total_revenue_vnd) FROM sales_transactions WHERE YEAR(transaction_date)=2024)*100, 1) AS pct
FROM sales_transactions st
JOIN business_lines bl ON st.business_line_id = bl.business_line_id
WHERE YEAR(st.transaction_date) = 2024
GROUP BY bl.business_line_name;

-- 2.2 YoY growth Q1
SELECT 'YoY Growth Q1' AS section;
SELECT bl.business_line_name,
       ROUND(SUM(CASE WHEN st.transaction_date BETWEEN '2025-01-01' AND '2025-03-31' THEN st.total_revenue_vnd ELSE 0 END)/1e9, 1) AS q1_2025_ty,
       ROUND(SUM(CASE WHEN st.transaction_date BETWEEN '2024-01-01' AND '2024-03-31' THEN st.total_revenue_vnd ELSE 0 END)/1e9, 1) AS q1_2024_ty,
       ROUND((SUM(CASE WHEN st.transaction_date BETWEEN '2025-01-01' AND '2025-03-31' THEN st.total_revenue_vnd ELSE 0 END) /
       NULLIF(SUM(CASE WHEN st.transaction_date BETWEEN '2024-01-01' AND '2024-03-31' THEN st.total_revenue_vnd ELSE 0 END), 0) - 1) * 100, 1) AS yoy_pct
FROM sales_transactions st
JOIN business_lines bl ON st.business_line_id = bl.business_line_id
GROUP BY bl.business_line_name;

-- 2.3 Gross margin
SELECT 'Gross Margin' AS section;
SELECT ROUND((1 - SUM(cost_vnd) / NULLIF(SUM(total_revenue_vnd), 0)) * 100, 1) AS gross_margin_pct
FROM sales_transactions WHERE YEAR(transaction_date) = 2024;

-- ============================================================================
-- 3. DEMO SCENARIO DRY-RUNS
-- ============================================================================

-- 3.1 Scenario 2: Nationality mix shift
SELECT 'Nationality Mix Shift' AS section;
SELECT ng.nationality_name,
       ROUND(q1_24.pax / t24.total * 100, 1) AS share_q1_2024,
       ROUND(q1_25.pax / t25.total * 100, 1) AS share_q1_2025
FROM nationality_groups ng
LEFT JOIN (SELECT nationality_group_id, SUM(pax_count) AS pax FROM passenger_traffic WHERE traffic_date BETWEEN '2024-01-01' AND '2024-03-31' AND passenger_type='Quoc te' GROUP BY nationality_group_id) q1_24 ON ng.nationality_group_id = q1_24.nationality_group_id
LEFT JOIN (SELECT nationality_group_id, SUM(pax_count) AS pax FROM passenger_traffic WHERE traffic_date BETWEEN '2025-01-01' AND '2025-03-31' AND passenger_type='Quoc te' GROUP BY nationality_group_id) q1_25 ON ng.nationality_group_id = q1_25.nationality_group_id
CROSS JOIN (SELECT SUM(pax_count) AS total FROM passenger_traffic WHERE traffic_date BETWEEN '2024-01-01' AND '2024-03-31' AND passenger_type='Quoc te') t24
CROSS JOIN (SELECT SUM(pax_count) AS total FROM passenger_traffic WHERE traffic_date BETWEEN '2025-01-01' AND '2025-03-31' AND passenger_type='Quoc te') t25
WHERE ng.nationality_group_id > 0
ORDER BY share_q1_2025 DESC;

-- 3.2 Scenario 3: Lounge utilization heatmap (Domestic T1)
SELECT 'Lounge Heatmap T1 Domestic' AS section;
SELECT lv.hour_slot,
       ROUND(AVG(lv.utilization_rate), 1) AS avg_util_pct
FROM lounge_visits lv
WHERE lv.lounge_id = 105
  AND lv.visit_date BETWEEN '2025-04-01' AND '2025-06-30'
GROUP BY lv.hour_slot
ORDER BY lv.hour_slot;

-- 3.3 Scenario 4: T3 weekly ramp-up
SELECT 'T3 Ramp-up' AS section;
SELECT YEARWEEK(transaction_date, 1) AS yw,
       MIN(transaction_date) AS week_start,
       ROUND(SUM(total_revenue_vnd)/1e9, 2) AS revenue_ty
FROM sales_transactions
WHERE terminal_id = 3
GROUP BY yw
ORDER BY yw;
