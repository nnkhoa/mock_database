-- =====================================================================
-- 05_validation_queries.sql
-- Sanity / scenario / fallback queries for vri_services_demo
-- Chạy: docker exec -i mock_database mysql -uroot -proot < 05_validation_queries.sql
-- =====================================================================

USE vri_services_demo;
SET NAMES utf8mb4;

-- ============================================================
-- 1. TECHNICAL — basic counts
-- ============================================================
SELECT '=== TECHNICAL ===' AS check_name;

SELECT 'fact_room_revenue_daily' AS tbl, COUNT(*) AS row_count, MIN(date) AS min_d, MAX(date) AS max_d FROM fact_room_revenue_daily;
SELECT 'fact_occupancy_daily', COUNT(*), MIN(date), MAX(date) FROM fact_occupancy_daily;
SELECT 'fact_fnb_revenue_daily', COUNT(*), MIN(date), MAX(date) FROM fact_fnb_revenue_daily;
SELECT 'fact_other_revenue_daily', COUNT(*), MIN(date), MAX(date) FROM fact_other_revenue_daily;
SELECT 'fact_weather_daily', COUNT(*), MIN(date), MAX(date) FROM fact_weather_daily;
SELECT 'fact_cost_monthly', COUNT(*), MIN(ym), MAX(ym) FROM fact_cost_monthly;
SELECT 'fact_cosmos_revenue_monthly', COUNT(*), MIN(ym), MAX(ym) FROM fact_cosmos_revenue_monthly;
SELECT 'fact_cosmos_sponsorship', COUNT(*) FROM fact_cosmos_sponsorship;

-- Referential integrity
SELECT 'orphans_room_property' AS chk, COUNT(*) AS n FROM fact_room_revenue_daily f
  LEFT JOIN dim_property p ON f.property_id=p.property_id WHERE p.property_id IS NULL;
SELECT 'orphans_room_channel' AS chk, COUNT(*) AS n FROM fact_room_revenue_daily f
  LEFT JOIN dim_channel c ON f.channel_id=c.channel_id WHERE c.channel_id IS NULL;
SELECT 'orphans_sponsorship_event' AS chk, COUNT(*) AS n FROM fact_cosmos_sponsorship f
  LEFT JOIN dim_event e ON f.event_id=e.event_id WHERE e.event_id IS NULL;

-- ============================================================
-- 2. STATISTICAL
-- ============================================================
SELECT '=== STATISTICAL ===' AS check_name;

-- Monthly portfolio Hotels revenue
SELECT
  DATE_FORMAT(f.date, '%Y-%m') AS ym,
  ROUND(SUM(f.room_revenue)/1e9, 2) AS room_b,
  ROUND(IFNULL(fb.fnb_b,0), 2) AS fnb_b,
  ROUND(IFNULL(ot.ot_b,0), 2) AS other_b
FROM fact_room_revenue_daily f
LEFT JOIN (
  SELECT DATE_FORMAT(date, '%Y-%m') ym, SUM(fnb_revenue)/1e9 AS fnb_b
  FROM fact_fnb_revenue_daily GROUP BY ym
) fb ON fb.ym = DATE_FORMAT(f.date, '%Y-%m')
LEFT JOIN (
  SELECT DATE_FORMAT(date, '%Y-%m') ym, SUM(other_revenue)/1e9 AS ot_b
  FROM fact_other_revenue_daily GROUP BY ym
) ot ON ot.ym = DATE_FORMAT(f.date, '%Y-%m')
WHERE f.is_cancelled = 0
GROUP BY DATE_FORMAT(f.date, '%Y-%m'), fb.fnb_b, ot.ot_b
ORDER BY ym;

-- Cosmos monthly revenue
SELECT ym, ROUND(SUM(amount)/1e9, 2) AS revenue_b
FROM fact_cosmos_revenue_monthly
GROUP BY ym ORDER BY ym;

-- YoY (matched months 2024 vs 2025)
SELECT
  MONTH(date) AS m,
  ROUND(SUM(CASE WHEN YEAR(date)=2024 THEN room_revenue ELSE 0 END)/1e9, 1) AS y2024_b,
  ROUND(SUM(CASE WHEN YEAR(date)=2025 THEN room_revenue ELSE 0 END)/1e9, 1) AS y2025_b
FROM fact_room_revenue_daily
WHERE is_cancelled=0 AND MONTH(date) BETWEEN 6 AND 11
GROUP BY MONTH(date) ORDER BY m;

-- OTA share by property (last 12 months Dec24-Nov25)
SELECT
  p.property_name,
  p.ota_dependency_baseline AS target_baseline,
  ROUND(SUM(CASE WHEN c.channel_category='OTA' THEN room_revenue ELSE 0 END)/SUM(room_revenue)*100, 1) AS actual_pct
FROM fact_room_revenue_daily f
JOIN dim_property p ON f.property_id=p.property_id
JOIN dim_channel c ON f.channel_id=c.channel_id
WHERE is_cancelled=0 AND date BETWEEN '2024-12-01' AND '2025-11-30'
GROUP BY p.property_id, p.property_name, p.ota_dependency_baseline
ORDER BY actual_pct;

-- ============================================================
-- 3. SCENARIO 1 — Khối DV 11/2025 vs 11/2024
-- ============================================================
SELECT '=== S1 — Khối DV Nov 2025 vs Nov 2024 ===' AS check_name;

-- Hotels portfolio revenue Nov 2024 vs 2025
SELECT
  rr.ym,
  ROUND((rr.room_b + IFNULL(fb.fnb_b,0) + IFNULL(ot.other_b,0)), 1) AS hotels_b,
  rr.room_b, IFNULL(fb.fnb_b,0) AS fnb_b, IFNULL(ot.other_b,0) AS other_b
FROM (
  SELECT DATE_FORMAT(date, '%Y-%m') AS ym, SUM(room_revenue)/1e9 AS room_b
  FROM fact_room_revenue_daily WHERE is_cancelled=0 AND MONTH(date)=11 AND YEAR(date) IN (2024, 2025)
  GROUP BY ym
) rr
LEFT JOIN (
  SELECT DATE_FORMAT(date, '%Y-%m') AS ym, SUM(fnb_revenue)/1e9 AS fnb_b
  FROM fact_fnb_revenue_daily WHERE MONTH(date)=11 AND YEAR(date) IN (2024, 2025) GROUP BY ym
) fb ON fb.ym = rr.ym
LEFT JOIN (
  SELECT DATE_FORMAT(date, '%Y-%m') AS ym, SUM(other_revenue)/1e9 AS other_b
  FROM fact_other_revenue_daily WHERE MONTH(date)=11 AND YEAR(date) IN (2024, 2025) GROUP BY ym
) ot ON ot.ym = rr.ym
ORDER BY rr.ym;

-- Cosmos Nov vs Nov
SELECT ym, ROUND(SUM(amount)/1e9, 1) AS cosmos_b
FROM fact_cosmos_revenue_monthly WHERE ym IN ('2024-11','2025-11')
GROUP BY ym ORDER BY ym;

-- Per property Nov 2025 (full revenue including F&B + Other)
SELECT
  p.property_name,
  ROUND(IFNULL(rr.room_b,0) + IFNULL(fb.fnb_b,0) + IFNULL(ot.other_b,0), 1) AS total_nov2025_b
FROM dim_property p
LEFT JOIN (
  SELECT property_id, SUM(room_revenue)/1e9 AS room_b
  FROM fact_room_revenue_daily WHERE is_cancelled=0 AND date BETWEEN '2025-11-01' AND '2025-11-30'
  GROUP BY property_id
) rr ON rr.property_id = p.property_id
LEFT JOIN (
  SELECT property_id, SUM(fnb_revenue)/1e9 AS fnb_b
  FROM fact_fnb_revenue_daily WHERE date BETWEEN '2025-11-01' AND '2025-11-30'
  GROUP BY property_id
) fb ON fb.property_id = p.property_id
LEFT JOIN (
  SELECT property_id, SUM(other_revenue)/1e9 AS other_b
  FROM fact_other_revenue_daily WHERE date BETWEEN '2025-11-01' AND '2025-11-30'
  GROUP BY property_id
) ot ON ot.property_id = p.property_id
ORDER BY p.property_id;

-- ============================================================
-- 4. SCENARIO 2 — Royal Beach NT diagnostic
-- ============================================================
SELECT '=== S2 — Royal Beach NT decomposition ===' AS check_name;

-- ADR / Revenue / Rooms decomposition
SELECT
  DATE_FORMAT(date, '%Y-%m') AS ym,
  ROUND(SUM(room_revenue)/1e9, 2) AS rev_b,
  ROUND(SUM(room_revenue)/SUM(rooms_sold)/1e6, 2) AS adr_eff_m,
  SUM(rooms_sold) AS total_rooms
FROM fact_room_revenue_daily
WHERE property_id=4 AND is_cancelled=0
  AND ((YEAR(date)=2024 AND MONTH(date)=11) OR (YEAR(date)=2025 AND MONTH(date)=11))
GROUP BY ym ORDER BY ym;

-- Channel mix Nov 2024 vs Nov 2025
SELECT
  m.ym,
  m.channel_category,
  ROUND(m.rooms*100.0/t.tot, 1) AS pct
FROM (
  SELECT DATE_FORMAT(date, '%Y-%m') AS ym, c.channel_category, SUM(rooms_sold) AS rooms
  FROM fact_room_revenue_daily f JOIN dim_channel c ON f.channel_id=c.channel_id
  WHERE property_id=4 AND is_cancelled=0
    AND ((YEAR(date)=2024 AND MONTH(date)=11) OR (YEAR(date)=2025 AND MONTH(date)=11))
  GROUP BY ym, c.channel_category
) m
JOIN (
  SELECT DATE_FORMAT(date, '%Y-%m') AS ym, SUM(rooms_sold) AS tot
  FROM fact_room_revenue_daily
  WHERE property_id=4 AND is_cancelled=0
    AND ((YEAR(date)=2024 AND MONTH(date)=11) OR (YEAR(date)=2025 AND MONTH(date)=11))
  GROUP BY ym
) t ON t.ym = m.ym
ORDER BY m.ym, m.channel_category;

-- Source market shift CN/KR/VN
SELECT
  s.source_market_name_vi,
  SUM(CASE WHEN YEAR(date)=2024 THEN rooms_sold ELSE 0 END) AS rooms_2024,
  SUM(CASE WHEN YEAR(date)=2025 THEN rooms_sold ELSE 0 END) AS rooms_2025,
  ROUND((SUM(CASE WHEN YEAR(date)=2025 THEN rooms_sold ELSE 0 END)
       - SUM(CASE WHEN YEAR(date)=2024 THEN rooms_sold ELSE 0 END))*100.0
       / NULLIF(SUM(CASE WHEN YEAR(date)=2024 THEN rooms_sold ELSE 0 END),0), 1) AS yoy_pct
FROM fact_room_revenue_daily f
JOIN dim_source_market s ON f.source_market_id=s.source_market_id
WHERE property_id=4 AND is_cancelled=0 AND MONTH(date)=11
  AND s.source_market_id IN ('VN','CN','KR','JP','RU')
GROUP BY s.source_market_id, s.source_market_name_vi
ORDER BY rooms_2025 DESC;

-- Weather Nov 2025 NTB
SELECT weather_indicator, COUNT(*) AS days
FROM fact_weather_daily
WHERE region_id=4 AND date BETWEEN '2025-11-01' AND '2025-11-30'
GROUP BY weather_indicator ORDER BY days DESC;

-- ============================================================
-- 5. SCENARIO 3 — OTA dependency simulation prep
-- ============================================================
SELECT '=== S3 — OTA dependency by property ===' AS check_name;

SELECT
  p.property_name,
  p.category_vi,
  p.ota_dependency_baseline AS target_pct,
  ROUND(SUM(CASE WHEN c.channel_category='OTA' THEN room_revenue ELSE 0 END)/1e9, 1) AS ota_rev_b,
  ROUND(SUM(CASE WHEN c.channel_category='OTA' THEN room_revenue ELSE 0 END)/SUM(room_revenue)*100, 1) AS actual_pct,
  ROUND(SUM(commission_amount)/1e9, 2) AS total_commission_b
FROM fact_room_revenue_daily f
JOIN dim_property p ON f.property_id=p.property_id
JOIN dim_channel c ON f.channel_id=c.channel_id
WHERE is_cancelled=0 AND date BETWEEN '2024-12-01' AND '2025-11-30'
GROUP BY p.property_id, p.property_name, p.category_vi, p.ota_dependency_baseline
ORDER BY actual_pct;

-- ============================================================
-- 6. FALLBACK QUERIES (bonus questions)
-- ============================================================
SELECT '=== FALLBACK — F&B contribution / ALOS / Sponsor ===' AS check_name;

-- F&B contribution per property (2025 YTD)
SELECT
  p.property_name,
  ROUND(IFNULL(rr.room_b,0), 1) AS room_b,
  ROUND(IFNULL(fb.fnb_b,0), 1) AS fnb_b,
  ROUND(IFNULL(ot.other_b,0), 1) AS other_b,
  ROUND(IFNULL(fb.fnb_b,0)*100/(IFNULL(rr.room_b,0)+IFNULL(fb.fnb_b,0)+IFNULL(ot.other_b,0)), 1) AS fnb_pct
FROM dim_property p
LEFT JOIN (SELECT property_id, SUM(room_revenue)/1e9 AS room_b FROM fact_room_revenue_daily WHERE is_cancelled=0 AND date BETWEEN '2025-01-01' AND '2025-11-30' GROUP BY property_id) rr ON rr.property_id=p.property_id
LEFT JOIN (SELECT property_id, SUM(fnb_revenue)/1e9 AS fnb_b FROM fact_fnb_revenue_daily WHERE date BETWEEN '2025-01-01' AND '2025-11-30' GROUP BY property_id) fb ON fb.property_id=p.property_id
LEFT JOIN (SELECT property_id, SUM(other_revenue)/1e9 AS other_b FROM fact_other_revenue_daily WHERE date BETWEEN '2025-01-01' AND '2025-11-30' GROUP BY property_id) ot ON ot.property_id=p.property_id
ORDER BY p.property_id;

-- ALOS by source market
SELECT s.source_market_name_vi, ROUND(AVG(stay_nights), 2) AS alos
FROM fact_room_revenue_daily f
JOIN dim_source_market s ON f.source_market_id=s.source_market_id
WHERE f.is_cancelled=0
GROUP BY s.source_market_id, s.source_market_name_vi
ORDER BY alos DESC;

-- Cosmos sponsor concentration MCO2024 (top 5)
SELECT
  s.sponsor_name,
  t.tier_name_vi,
  ROUND(f.contract_amount/1e9, 1) AS amount_b
FROM fact_cosmos_sponsorship f
JOIN dim_sponsor s ON f.sponsor_id=s.sponsor_id
JOIN dim_sponsor_tier t ON f.tier_id=t.tier_id
WHERE f.event_id='MCO2024' AND f.installment_no=1
ORDER BY f.contract_amount DESC LIMIT 10;

-- Sponsor anomalies
SELECT
  e.event_id,
  s.sponsor_name,
  f.installment_no,
  f.payment_status,
  ROUND(f.contract_amount/1e9, 1) AS amount_b,
  f.notes_vi
FROM fact_cosmos_sponsorship f
JOIN dim_sponsor s ON f.sponsor_id=s.sponsor_id
JOIN dim_event e ON f.event_id=e.event_id
WHERE f.payment_status IN ('overdue','cancelled') OR f.notes_vi IS NOT NULL
ORDER BY e.start_date, s.sponsor_name;

-- NCA Diamond not renewed in 2025
SELECT 'NCA contracts by year' AS chk;
SELECT
  e.event_id, e.season_year, ROUND(f.contract_amount/1e9,1) amount_b
FROM fact_cosmos_sponsorship f
JOIN dim_sponsor s ON f.sponsor_id=s.sponsor_id
JOIN dim_event e ON f.event_id=e.event_id
WHERE s.sponsor_code='SP_NCA' AND f.installment_no=1
ORDER BY e.season_year;
