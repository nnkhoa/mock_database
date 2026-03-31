-- ============================================================
-- PTSC M&C Demo Database — Validation Queries
-- Chạy sau khi populate để verify data
-- ============================================================

USE ptsc_mc_demo;

-- ============================================================
-- 1. RECORD COUNTS
-- ============================================================
SELECT 'Record Counts' AS section;
SELECT 'clients' AS tbl, COUNT(*) AS cnt FROM clients
UNION ALL SELECT 'projects', COUNT(*) FROM projects
UNION ALL SELECT 'disciplines', COUNT(*) FROM disciplines
UNION ALL SELECT 'cost_categories', COUNT(*) FROM cost_categories
UNION ALL SELECT 'suppliers', COUNT(*) FROM suppliers
UNION ALL SELECT 'work_areas', COUNT(*) FROM work_areas
UNION ALL SELECT 'workforce', COUNT(*) FROM workforce
UNION ALL SELECT 'project_progress', COUNT(*) FROM project_progress
UNION ALL SELECT 'discipline_progress', COUNT(*) FROM discipline_progress
UNION ALL SELECT 'manhour_logs', COUNT(*) FROM manhour_logs
UNION ALL SELECT 'project_costs', COUNT(*) FROM project_costs
UNION ALL SELECT 'material_deliveries', COUNT(*) FROM material_deliveries
UNION ALL SELECT 'quality_records', COUNT(*) FROM quality_records
UNION ALL SELECT 'safety_incidents', COUNT(*) FROM safety_incidents
UNION ALL SELECT '_meta_tables', COUNT(*) FROM _meta_tables
UNION ALL SELECT '_meta_columns', COUNT(*) FROM _meta_columns
UNION ALL SELECT '_meta_kpi', COUNT(*) FROM _meta_kpi
UNION ALL SELECT '_meta_glossary', COUNT(*) FROM _meta_glossary;

-- ============================================================
-- 2. SCENARIO 1: Portfolio Overview (SPI)
-- Expected: PJ-003 SPI~0.84, PJ-001~0.95, others~1.0
-- ============================================================
SELECT 'Scenario 1: Portfolio SPI (March 2025)' AS section;
SELECT p.project_id, p.project_name, p.project_type,
       pp.planned_pct, pp.actual_pct,
       ROUND(pp.actual_pct / NULLIF(pp.planned_pct, 0), 2) AS spi
FROM projects p
JOIN project_progress pp ON p.project_id = pp.project_id
WHERE pp.report_month = '2025-03-01'
ORDER BY spi ASC;

-- ============================================================
-- 3. SCENARIO 2: Root Cause PJ-003 — Discipline Gaps
-- Expected: PIPING gap~15%, ELECT gap~7%, STRUCT gap~0%
-- ============================================================
SELECT 'Scenario 2: PJ-003 Discipline Gaps (March 2025)' AS section;
SELECT dp.discipline_id, dp.planned_pct, dp.actual_pct,
       ROUND(dp.planned_pct - dp.actual_pct, 1) AS gap
FROM discipline_progress dp
WHERE dp.project_id = 'PJ-003' AND dp.report_month = '2025-03-01'
ORDER BY gap DESC;

-- ============================================================
-- 4. SCENARIO 2: Material Delay — Duplex SS PJ-003
-- Expected: 3 POs with delay 22-28 days
-- ============================================================
SELECT 'Scenario 2: Duplex SS Material Delays' AS section;
SELECT po_number, material_type, supplier_id,
       planned_delivery_date, actual_delivery_date,
       DATEDIFF(actual_delivery_date, planned_delivery_date) AS delay_days
FROM material_deliveries
WHERE project_id = 'PJ-003' AND material_type LIKE '%Duplex%'
ORDER BY delay_days DESC;

-- ============================================================
-- 5. SCENARIO 2: Weld Rejection Rate — Piping
-- Expected: PJ-003~6.2%, others 2.5-4.5%
-- ============================================================
SELECT 'Scenario 2: Piping Rejection Rates (March 2025)' AS section;
SELECT project_id, rejection_rate
FROM quality_records
WHERE discipline_id = 'PIPING' AND report_month = '2025-03-01'
ORDER BY rejection_rate DESC;

-- ============================================================
-- 6. SCENARIO 3: Cost Overrun PJ-001
-- Expected: LABOR-WELD~+18%, SUBCON-BP~+11%, MAT-PIPE~+5%
-- ============================================================
SELECT 'Scenario 3: PJ-001 Cost Overrun by Category' AS section;
SELECT cc.category_name,
       ROUND(SUM(pc.budgeted_amount), 0) AS total_budget,
       ROUND(SUM(pc.actual_amount), 0) AS total_actual,
       ROUND((SUM(pc.actual_amount) / SUM(pc.budgeted_amount) - 1) * 100, 1) AS overrun_pct
FROM project_costs pc
JOIN cost_categories cc ON pc.cost_category_id = cc.cost_category_id
WHERE pc.project_id = 'PJ-001'
GROUP BY cc.category_name
ORDER BY overrun_pct DESC;

-- ============================================================
-- 7. SCENARIO 3: Overtime by Area PJ-001
-- Expected: AREA-SV-3~30%, others 15-19%
-- ============================================================
SELECT 'Scenario 3: PJ-001 Overtime by Area (from Aug 2024)' AS section;
SELECT work_area_id,
       ROUND(SUM(overtime_mh), 0) AS total_ot,
       ROUND(SUM(actual_mh), 0) AS total_actual,
       ROUND(SUM(overtime_mh) / SUM(actual_mh) * 100, 1) AS ot_rate_pct
FROM manhour_logs
WHERE project_id = 'PJ-001' AND report_month >= '2024-08-01'
GROUP BY work_area_id
ORDER BY ot_rate_pct DESC;

-- ============================================================
-- 8. SCENARIO 4: Productivity by Project
-- Expected: PJ-003~0.76, PJ-001~0.88, PJ-004~0.95, PJ-002~0.98, PJ-005~1.05
-- ============================================================
SELECT 'Scenario 4: Productivity by Project' AS section;
SELECT project_id,
       ROUND(SUM(earned_mh) / SUM(actual_mh), 2) AS productivity_ratio
FROM manhour_logs
GROUP BY project_id
ORDER BY productivity_ratio ASC;

-- ============================================================
-- 9. SCENARIO 4: PJ-003 Piping Learning Curve
-- Expected: 0.50 -> 0.72 over 9 months
-- ============================================================
SELECT 'Scenario 4: PJ-003 Piping Monthly Productivity' AS section;
SELECT report_month,
       ROUND(SUM(earned_mh) / SUM(actual_mh), 2) AS productivity
FROM manhour_logs
WHERE project_id = 'PJ-003' AND discipline_id = 'PIPING'
GROUP BY report_month
ORDER BY report_month;

-- ============================================================
-- 10. SCENARIO 6: Safety — Near-Miss March 2025
-- Expected: PJ-003 = 4 near-miss, others 1-2
-- ============================================================
SELECT 'Scenario 6: Safety Near-Miss (March 2025)' AS section;
SELECT project_id,
       COUNT(*) AS total_incidents,
       SUM(CASE WHEN severity = 'Near Miss' THEN 1 ELSE 0 END) AS near_miss_count
FROM safety_incidents
WHERE incident_date >= '2025-03-01' AND incident_date < '2025-04-01'
GROUP BY project_id
ORDER BY near_miss_count DESC;

-- ============================================================
-- 11. FALLBACK: PJ-004 On-Track Check
-- Expected: SPI ~1.0, nothing dramatic
-- ============================================================
SELECT 'Fallback: PJ-004 On-Track' AS section;
SELECT p.project_name, pp.planned_pct, pp.actual_pct,
       ROUND(pp.actual_pct / pp.planned_pct, 2) AS spi
FROM projects p
JOIN project_progress pp ON p.project_id = pp.project_id
WHERE p.project_id = 'PJ-004' AND pp.report_month = '2025-03-01';

-- ============================================================
-- 12. FALLBACK: Supplier Delay Ranking
-- Expected: Hyundai Steel (KR-SUP-002) top delay
-- ============================================================
SELECT 'Fallback: Supplier Delay Ranking' AS section;
SELECT s.supplier_name,
       COUNT(*) AS total_pos,
       ROUND(AVG(DATEDIFF(md.actual_delivery_date, md.planned_delivery_date)), 1) AS avg_delay_days
FROM material_deliveries md
JOIN suppliers s ON md.supplier_id = s.supplier_id
WHERE md.actual_delivery_date IS NOT NULL
GROUP BY s.supplier_name
ORDER BY avg_delay_days DESC;

-- ============================================================
-- 13. INTEGRITY CHECKS
-- ============================================================
SELECT 'Integrity: Orphan Records' AS section;
SELECT 'manhour_logs -> work_areas' AS fk_check,
       COUNT(*) AS orphans
FROM manhour_logs ml
LEFT JOIN work_areas wa ON ml.work_area_id = wa.area_id
WHERE wa.area_id IS NULL;

SELECT 'discipline_progress -> disciplines' AS fk_check,
       COUNT(*) AS orphans
FROM discipline_progress dp
LEFT JOIN disciplines d ON dp.discipline_id = d.discipline_id
WHERE d.discipline_id IS NULL;

SELECT 'project_costs -> cost_categories' AS fk_check,
       COUNT(*) AS orphans
FROM project_costs pc
LEFT JOIN cost_categories cc ON pc.cost_category_id = cc.cost_category_id
WHERE cc.cost_category_id IS NULL;

SELECT 'VALIDATION COMPLETE' AS status;
