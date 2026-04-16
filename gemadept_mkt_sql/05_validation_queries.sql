-- 05_validation_queries.sql | Database: gemadept_bi_demo
-- 8 demo scenario dry-runs + magnitude/integrity checks
USE `gemadept_bi_demo`;

-- ===========================================================================
-- TECHNICAL CHECKS
-- ===========================================================================
-- TC-1: Row counts
SELECT 'ports' tbl, COUNT(*) n FROM ports
UNION ALL SELECT 'shipping_lines', COUNT(*) FROM shipping_lines
UNION ALL SELECT 'alliances', COUNT(*) FROM alliances
UNION ALL SELECT 'alliance_membership_history', COUNT(*) FROM alliance_membership_history
UNION ALL SELECT 'vessels', COUNT(*) FROM vessels
UNION ALL SELECT 'services', COUNT(*) FROM services
UNION ALL SELECT 'news_events', COUNT(*) FROM news_events
UNION ALL SELECT 'customers_shippers', COUNT(*) FROM customers_shippers
UNION ALL SELECT 'port_calls', COUNT(*) FROM port_calls
UNION ALL SELECT 'port_vessel_schedule_external', COUNT(*) FROM port_vessel_schedule_external
UNION ALL SELECT 'daily_port_stats', COUNT(*) FROM daily_port_stats
UNION ALL SELECT 'pricing_tariff', COUNT(*) FROM pricing_tariff;

-- TC-2: Referential integrity
SELECT 'orphan_port_calls_port' anomaly, COUNT(*) cnt FROM port_calls pc LEFT JOIN ports p ON pc.port_id=p.port_id WHERE p.port_id IS NULL
UNION ALL SELECT 'orphan_port_calls_vessel', COUNT(*) FROM port_calls pc LEFT JOIN vessels v ON pc.vessel_id=v.vessel_id WHERE v.vessel_id IS NULL
UNION ALL SELECT 'orphan_port_calls_line', COUNT(*) FROM port_calls pc LEFT JOIN shipping_lines sl ON pc.shipping_line_id=sl.line_id WHERE sl.line_id IS NULL;

-- TC-3: Business logic (eta < etb < etd)
SELECT 'eta_etb_violation' anomaly, COUNT(*) cnt FROM port_calls WHERE eta >= etb
UNION ALL SELECT 'etb_etd_violation', COUNT(*) FROM port_calls WHERE etb >= etd
UNION ALL SELECT 'teu_negative', COUNT(*) FROM port_calls WHERE total_teu_handled <= 0
UNION ALL SELECT 'revenue_negative', COUNT(*) FROM port_calls WHERE revenue_vnd <= 0;

-- ===========================================================================
-- STATISTICAL — magnitude + Pareto + seasonality
-- ===========================================================================
-- ST-1: Annual TEU magnitude
SELECT YEAR(eta) yr, FORMAT(SUM(total_teu_handled),0) total_teu,
       COUNT(*) calls, FORMAT(SUM(revenue_vnd)/1e9,1) revenue_bil_vnd
FROM port_calls GROUP BY yr;
-- Expect 2024 (9mo): ~3-4M TEU, 2025: ~5-6M, 2026 (3mo): ~1-1.5M

-- ST-2: Monthly trend (seasonality check — Tết trough Jan-Feb, peak Sep-Oct)
SELECT DATE_FORMAT(eta,'%Y-%m') mo, SUM(total_teu_handled) teu
FROM port_calls GROUP BY mo ORDER BY mo;

-- ST-3: Pareto top 5 lines at Gemalink (target ~72%)
WITH line_teu AS (
  SELECT sl.line_name, SUM(pc.total_teu_handled) teu
  FROM port_calls pc JOIN shipping_lines sl ON pc.shipping_line_id=sl.line_id
  WHERE pc.port_id='P006'
  GROUP BY sl.line_name
)
SELECT line_name, FORMAT(teu,0) teu,
       ROUND(100*teu/SUM(teu) OVER (),1) pct,
       ROUND(100*SUM(teu) OVER (ORDER BY teu DESC) / SUM(teu) OVER (),1) cum_pct
FROM line_teu ORDER BY teu DESC LIMIT 8;

-- ===========================================================================
-- DEMO SCENARIO DRY-RUNS
-- ===========================================================================

-- ===== Scenario 1: Mar 2026 by line+alliance, vs Mar 2025 =====
SELECT YEAR(pc.eta) yr, sl.line_name,
       a.alliance_name AS alliance_then,
       SUM(pc.total_teu_handled) teu, COUNT(*) calls
FROM port_calls pc
JOIN shipping_lines sl ON pc.shipping_line_id=sl.line_id
LEFT JOIN alliance_membership_history m
  ON m.line_id=pc.shipping_line_id
  AND m.from_date<=DATE(pc.eta)
  AND (m.to_date IS NULL OR m.to_date>=DATE(pc.eta))
LEFT JOIN alliances a ON m.alliance_id=a.alliance_id
WHERE MONTH(pc.eta)=3 AND YEAR(pc.eta) IN (2025, 2026)
GROUP BY yr, sl.line_name, a.alliance_name
ORDER BY sl.line_name, yr;

-- ===== Scenario 2 (WOW): Maersk @ Gemalink decline + TCIT increase =====
SELECT 'INTERNAL Gemalink' src, DATE_FORMAT(eta,'%Y-%m') mo,
       COUNT(*) calls, SUM(total_teu_handled) teu
FROM port_calls pc JOIN shipping_lines sl ON pc.shipping_line_id=sl.line_id
WHERE sl.line_name='Maersk' AND pc.port_id='P006' AND eta>='2025-07-01'
GROUP BY mo
UNION ALL
SELECT 'EXTERNAL TCIT' src, DATE_FORMAT(eta,'%Y-%m') mo,
       COUNT(*) calls, SUM(teu_capacity_est) teu
FROM port_vessel_schedule_external pvs
JOIN shipping_lines sl ON pvs.shipping_line_id=sl.line_id
WHERE sl.line_name='Maersk' AND pvs.port_id='P010' AND eta>='2025-07-01'
GROUP BY mo
ORDER BY src, mo;
-- Expect: Gemalink Maersk drops from 4→2 calls Q1 2026, TCIT rises from 4→8

-- News context for scenario 2
SELECT event_date, title_vi, source FROM news_events
WHERE event_date BETWEEN '2024-06-01' AND '2026-03-31'
  AND (JSON_CONTAINS(affected_lines, '"L02"') OR JSON_CONTAINS(affected_lines, '"L05"'))
  AND category IN ('alliance','route','competitor')
ORDER BY event_date;

-- ===== Scenario 3: CM-TV competitive (Gemalink vs others, vessels >50k DWT) =====
SELECT p.port_name, COUNT(*) port_calls,
       SUM(v.teu_capacity) total_teu_capacity,
       AVG(v.dwt) avg_dwt
FROM port_vessel_schedule_external pvs
JOIN ports p ON pvs.port_id=p.port_id
JOIN vessels v ON pvs.vessel_id=v.vessel_id
WHERE p.cluster='CM-TV' AND v.dwt>=50000
  AND eta>='2025-10-01'
GROUP BY p.port_name ORDER BY 2 DESC;

-- ===== Scenario 4: BD opportunity — lines at CM-TV not at Gemalink =====
WITH cm_tv_calls AS (
  SELECT pvs.shipping_line_id, sl.line_name, COUNT(*) calls_cm_tv
  FROM port_vessel_schedule_external pvs
  JOIN shipping_lines sl ON pvs.shipping_line_id=sl.line_id
  JOIN ports p ON pvs.port_id=p.port_id
  WHERE p.cluster='CM-TV' AND p.port_name<>'Gemalink'
    AND eta>='2025-10-01'
  GROUP BY pvs.shipping_line_id, sl.line_name
),
gml AS (
  SELECT shipping_line_id, COUNT(*) calls_gml FROM port_calls
  WHERE port_id='P006' AND eta>='2025-10-01'
  GROUP BY shipping_line_id
)
SELECT c.line_name, c.calls_cm_tv, COALESCE(g.calls_gml,0) calls_gml,
       c.calls_cm_tv-COALESCE(g.calls_gml,0) gap
FROM cm_tv_calls c LEFT JOIN gml g USING(shipping_line_id)
WHERE c.calls_cm_tv>=8
ORDER BY gap DESC LIMIT 8;

-- News context for ZIM/Wan Hai
SELECT event_date, title_vi FROM news_events
WHERE (JSON_CONTAINS(affected_lines,'"L10"') OR JSON_CONTAINS(affected_lines,'"L11"') OR JSON_CONTAINS(affected_lines,'"L08"'))
  AND event_date>='2024-10-01'
ORDER BY event_date;

-- ===== Scenario 5: Alliance reshuffle Feb 2025 — Gemalink alliance share =====
WITH calls_with_alliance AS (
  SELECT
    CASE WHEN pc.eta<'2025-02-01' THEN 'PRE Feb 2025' ELSE 'POST Feb 2025' END AS period,
    a.alliance_name AS alliance,
    pc.total_teu_handled
  FROM port_calls pc
  JOIN alliance_membership_history m
    ON m.line_id=pc.shipping_line_id AND m.from_date<=DATE(pc.eta)
    AND (m.to_date IS NULL OR m.to_date>=DATE(pc.eta))
  JOIN alliances a ON m.alliance_id=a.alliance_id
  WHERE pc.port_id='P006'
),
agg AS (
  SELECT period, alliance, SUM(total_teu_handled) teu
  FROM calls_with_alliance GROUP BY period, alliance
)
SELECT period, alliance,
       ROUND(100*teu/SUM(teu) OVER (PARTITION BY period),1) pct
FROM agg ORDER BY period DESC, pct DESC;

-- ===== Scenario 6: Strategic top 3 candidates (data underlying) =====
-- Multi-turn, uses scenarios 4 + wallet share
SELECT sl.line_name, sl.fleet_capacity_teu, sl.global_rank,
       COALESCE(gemadept_teu, 0) gemadept_teu,
       COALESCE(vn_capacity_est, 0) vn_capacity_est,
       ROUND(100*COALESCE(gemadept_teu,0)/NULLIF(vn_capacity_est,0),1) wallet_pct
FROM shipping_lines sl
LEFT JOIN (SELECT shipping_line_id, SUM(total_teu_handled) gemadept_teu FROM port_calls WHERE eta>='2025-10-01' GROUP BY shipping_line_id) g ON g.shipping_line_id=sl.line_id
LEFT JOIN (SELECT shipping_line_id, SUM(teu_capacity_est) vn_capacity_est FROM port_vessel_schedule_external WHERE eta>='2025-10-01' GROUP BY shipping_line_id) v ON v.shipping_line_id=sl.line_id
WHERE sl.global_rank<=15
ORDER BY (vn_capacity_est-gemadept_teu) DESC LIMIT 5;

-- ===== Scenario 7: Pricing optimization — line tier mix at Gemalink =====
SELECT
  CASE
    WHEN sl.line_id IN ('L01','L02','L03','L04','L05') THEN 'TOP5'
    WHEN sl.line_id IN ('L06','L07','L08','L09','L16') THEN 'MEDIUM'
    ELSE 'SMALL'
  END tier,
  COUNT(*) calls, SUM(pc.total_teu_handled) teu,
  ROUND(100*SUM(pc.total_teu_handled)/SUM(SUM(pc.total_teu_handled)) OVER (),1) pct,
  AVG(pt.rate_per_teu_vnd) avg_rate
FROM port_calls pc
JOIN shipping_lines sl ON pc.shipping_line_id=sl.line_id
LEFT JOIN pricing_tariff pt ON pt.port_id=pc.port_id AND pt.line_id=pc.shipping_line_id
  AND DATE(pc.eta) BETWEEN pt.effective_from AND COALESCE(pt.effective_to,'9999-12-31')
WHERE pc.port_id='P006' AND pc.eta>='2025-04-01'
GROUP BY tier ORDER BY teu DESC;

-- Pricing change verification (deepsea +10% from Feb 2026)
SELECT p.port_name, sl.line_name, pt.rate_per_teu_vnd, pt.effective_from
FROM pricing_tariff pt JOIN ports p ON pt.port_id=p.port_id JOIN shipping_lines sl ON pt.line_id=sl.line_id
WHERE p.port_name IN ('Gemalink','Nam Đình Vũ') AND sl.line_name='Maersk'
ORDER BY p.port_name, pt.effective_from;

-- ===== Scenario 8: What-if — historical tariff context + US share =====
SELECT event_date, title_vi, sentiment FROM news_events
WHERE category='tariff' ORDER BY event_date;

-- ===== FALLBACK: Out-of-scenario queries =====
-- "CMA CGM at Nam Đình Vũ last 3 months"
SELECT DATE_FORMAT(eta,'%Y-%m') mo, COUNT(*) calls, SUM(total_teu_handled) teu
FROM port_calls pc JOIN shipping_lines sl ON pc.shipping_line_id=sl.line_id
JOIN ports p ON pc.port_id=p.port_id
WHERE sl.line_name='CMA CGM' AND p.port_name LIKE 'Nam %' AND eta>='2026-01-01'
GROUP BY mo;

-- "Cảng Dung Quất tháng 9/2025"
SELECT COUNT(*) calls, FORMAT(SUM(total_teu_handled),0) teu FROM port_calls pc
JOIN ports p ON pc.port_id=p.port_id
WHERE p.port_name='Cảng Dung Quất' AND DATE_FORMAT(eta,'%Y-%m')='2025-09';
