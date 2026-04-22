-- ============================================================
-- evncpc_demo — Validation Queries
-- ============================================================

USE `evncpc_demo`;

-- 1. REFERENTIAL INTEGRITY
SELECT 'FK provinces->power_companies' AS check_name, COUNT(*) AS orphans
FROM provinces p LEFT JOIN power_companies pc ON p.pc_id = pc.pc_id WHERE pc.pc_id IS NULL
UNION ALL
SELECT 'FK districts->provinces', COUNT(*) FROM districts d LEFT JOIN provinces p ON d.province_id = p.province_id WHERE p.province_id IS NULL
UNION ALL
SELECT 'FK districts->power_companies', COUNT(*) FROM districts d LEFT JOIN power_companies pc ON d.pc_id = pc.pc_id WHERE pc.pc_id IS NULL
UNION ALL
SELECT 'FK substations->districts', COUNT(*) FROM substations s LEFT JOIN districts d ON s.district_id = d.district_id WHERE d.district_id IS NULL
UNION ALL
SELECT 'FK kpi->power_companies', COUNT(*) FROM monthly_kpi_summary k LEFT JOIN power_companies pc ON k.pc_id = pc.pc_id WHERE pc.pc_id IS NULL
UNION ALL
SELECT 'FK loss->districts', COUNT(*) FROM power_loss_detail l LEFT JOIN districts d ON l.district_id = d.district_id WHERE d.district_id IS NULL
UNION ALL
SELECT 'FK incidents->power_companies', COUNT(*) FROM grid_incidents i LEFT JOIN power_companies pc ON i.pc_id = pc.pc_id WHERE pc.pc_id IS NULL;

-- 2. COMPLETENESS
SELECT pc_id, COUNT(DISTINCT report_month) AS months
FROM monthly_kpi_summary GROUP BY pc_id;

-- 3. VALUE RANGES
SELECT 'Negative revenue' AS check_name, COUNT(*) AS violations FROM monthly_kpi_summary WHERE revenue_billion_vnd < 0
UNION ALL SELECT 'Loss rate out of range', COUNT(*) FROM monthly_kpi_summary WHERE loss_rate_pct < 0 OR loss_rate_pct > 15
UNION ALL SELECT 'Negative SAIDI', COUNT(*) FROM monthly_kpi_summary WHERE saidi_minutes < 0;

-- 4. AGGREGATE STATS
SELECT 'Total Year2 Power GWh' AS metric, ROUND(SUM(commercial_power_gwh), 0) AS value
FROM monthly_kpi_summary WHERE report_month >= '2024-10-01';

SELECT 'Weighted Avg Loss pct' AS metric,
  ROUND(SUM(power_received_gwh - commercial_power_gwh) / SUM(power_received_gwh) * 100, 2) AS value
FROM monthly_kpi_summary WHERE report_month >= '2024-10-01';

SELECT pc_id, ROUND(SUM(commercial_power_gwh), 0) AS total_gwh,
  ROUND(SUM(commercial_power_gwh) / (SELECT SUM(commercial_power_gwh) FROM monthly_kpi_summary) * 100, 1) AS share_pct
FROM monthly_kpi_summary GROUP BY pc_id ORDER BY total_gwh DESC;

-- 5. SCENARIO DRY-RUNS

-- Scenario 1: KPI Overview
SELECT pc.pc_short_name,
  cur.commercial_power_gwh AS power_sep25, cur.loss_rate_pct AS loss_sep25, cur.saidi_minutes AS saidi_sep25
FROM monthly_kpi_summary cur JOIN power_companies pc ON cur.pc_id = pc.pc_id
WHERE cur.report_month = '2025-09-01' ORDER BY cur.loss_rate_pct DESC;

-- Scenario 2: PC05 loss by district
SELECT d.district_name,
  ROUND(AVG(pld.technical_loss_lv_pct), 2) AS avg_lv_loss,
  ROUND(AVG(pld.total_loss_rate_pct), 2) AS avg_total_loss
FROM power_loss_detail pld JOIN districts d ON pld.district_id = d.district_id
WHERE pld.pc_id = 'PC05' AND pld.report_month >= '2025-04-01'
GROUP BY d.district_name ORDER BY avg_lv_loss DESC;

-- Scenario 3: Q3 incidents
SELECT '2025 Q3' AS period, COUNT(*) AS n FROM grid_incidents WHERE incident_date BETWEEN '2025-07-01' AND '2025-09-30'
UNION ALL SELECT '2024 Q3', COUNT(*) FROM grid_incidents WHERE incident_date BETWEEN '2024-07-01' AND '2024-09-30';

-- Scenario 4: PC05 loss trend
SELECT report_month, loss_rate_pct FROM monthly_kpi_summary
WHERE pc_id = 'PC05' AND report_month >= '2025-04-01' ORDER BY report_month;

-- Scenario 5: Substations condition
SELECT pc_id, COUNT(*) AS total,
  SUM(CASE WHEN condition_rating IN ('Kém', 'Cần thay thế') THEN 1 ELSE 0 END) AS poor
FROM substations WHERE voltage_level != '110kV' GROUP BY pc_id ORDER BY poor DESC;
