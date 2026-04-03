-- ============================================================
-- KN Holdings - Bất Động Sản Demo Database
-- 05_validation.sql - Validation Queries
-- ============================================================

USE kn_realestate_demo;


-- ============================================================
-- VALIDATION QUERIES
-- ============================================================

-- === TECHNICAL VALIDATION ===

-- 1. FK integrity check: orphan products
SELECT 'Orphan products' AS check_name,
       COUNT(*) AS orphan_count
FROM products p
LEFT JOIN sub_zones sz ON p.sub_zone_id = sz.sub_zone_id
WHERE sz.sub_zone_id IS NULL;

-- 2. Date ordering: booking <= deposit <= contract <= handover
SELECT 'Date order violations' AS check_name,
       COUNT(*) AS violation_count
FROM sales_transactions
WHERE (deposit_date IS NOT NULL AND booking_date IS NOT NULL AND deposit_date < booking_date)
   OR (contract_date IS NOT NULL AND deposit_date IS NOT NULL AND contract_date < deposit_date)
   OR (handover_date IS NOT NULL AND contract_date IS NOT NULL AND handover_date < contract_date);

-- 3. Price check: all prices > 0
SELECT 'Negative prices' AS check_name,
       COUNT(*) AS violation_count
FROM products WHERE listed_price_billion <= 0;

-- 4. Absorption rate range 0-100
SELECT 'Absorption out of range' AS check_name,
       COUNT(*) AS violation_count
FROM inventory_snapshots WHERE absorption_rate < 0 OR absorption_rate > 100;

-- === STATISTICAL VALIDATION ===

-- 5. Seasonality: peak T11-T12, low T1-T2
SELECT MONTH(booking_date) AS month_num,
       COUNT(*) AS transactions,
       ROUND(SUM(actual_price_billion), 1) AS revenue_billion
FROM sales_transactions
WHERE transaction_status != 'cancelled'
GROUP BY MONTH(booking_date)
ORDER BY month_num;

-- 6. Pareto: top 20% agents sales share
SELECT CONCAT(
    ROUND(
        (SELECT SUM(actual_price_billion)
         FROM sales_transactions
         WHERE transaction_status != 'cancelled'
           AND agent_id IN (
               SELECT agent_id FROM (
                   SELECT agent_id, SUM(actual_price_billion) AS rev
                   FROM sales_transactions
                   WHERE transaction_status != 'cancelled'
                   GROUP BY agent_id
                   ORDER BY rev DESC
                   LIMIT 10
               ) top10
           )
        ) / SUM(actual_price_billion) * 100, 1
    ), '%'
) AS top_20pct_share
FROM sales_transactions
WHERE transaction_status != 'cancelled';

-- === DEMO DRY-RUN QUERIES ===

-- S1: Q4/2024 tổng quan
SELECT
    p.project_name,
    COUNT(*) AS num_sales,
    ROUND(SUM(st.actual_price_billion), 1) AS revenue_billion
FROM sales_transactions st
JOIN products pr ON st.product_id = pr.product_id
JOIN sub_zones sz ON pr.sub_zone_id = sz.sub_zone_id
JOIN projects p ON sz.project_id = p.project_id
WHERE st.transaction_status != 'cancelled'
  AND st.booking_date >= '2024-10-01'
  AND st.booking_date <= '2024-12-31'
GROUP BY p.project_name
ORDER BY revenue_billion DESC;

-- S2: Para Grus vs Sông Town comparison
SELECT
    sz.sub_zone_id, sz.sub_zone_name,
    sz.avg_price_per_sqm_million,
    sz.distance_to_beach_m
FROM sub_zones sz
WHERE sz.sub_zone_id IN ('SZ-ST', 'SZ-PG');

-- S2: Para Grus conversion rate
SELECT
    sz.sub_zone_id,
    COUNT(CASE WHEN l.current_stage = 'contracted' THEN 1 END) AS contracted,
    COUNT(CASE WHEN l.current_stage IN ('deposited','contracted') THEN 1 END) AS deposited_plus,
    COUNT(*) AS total_leads,
    ROUND(COUNT(CASE WHEN l.current_stage = 'contracted' THEN 1 END) / COUNT(*) * 100, 1) AS conv_pct
FROM leads_pipeline l
JOIN sub_zones sz ON l.sub_zone_id = sz.sub_zone_id
WHERE sz.sub_zone_id IN ('SZ-ST', 'SZ-PG')
  AND l.lead_date >= '2024-09-01'
GROUP BY sz.sub_zone_id;

-- S2: Para Grus channel conversion
SELECT
    sc.channel_type,
    COUNT(CASE WHEN l.current_stage = 'contracted' THEN 1 END) AS contracted,
    COUNT(*) AS total,
    ROUND(COUNT(CASE WHEN l.current_stage = 'contracted' THEN 1 END) / COUNT(*) * 100, 1) AS conv_pct
FROM leads_pipeline l
JOIN sales_channels sc ON l.channel_id = sc.channel_id
WHERE l.sub_zone_id = 'SZ-PG'
  AND l.lead_date >= '2024-09-01'
GROUP BY sc.channel_type;

-- S3: Inventory status latest
SELECT
    sz.sub_zone_id, sz.sub_zone_name,
    inv.available_units, inv.absorption_rate,
    inv.monthly_sell_rate, inv.months_of_inventory
FROM inventory_snapshots inv
JOIN sub_zones sz ON inv.sub_zone_id = sz.sub_zone_id
WHERE inv.snapshot_date = (SELECT MAX(snapshot_date) FROM inventory_snapshots)
ORDER BY inv.available_units DESC;

-- S4: SZ-ST before/after price cut (T6/2024)
SELECT
    CASE WHEN booking_date < '2024-06-01' THEN 'Before' ELSE 'After' END AS period,
    COUNT(*) AS num_sales,
    ROUND(AVG(actual_price_billion), 2) AS avg_price,
    ROUND(SUM(actual_price_billion), 1) AS total_revenue
FROM sales_transactions st
JOIN products p ON st.product_id = p.product_id
WHERE p.sub_zone_id = 'SZ-ST'
  AND st.transaction_status != 'cancelled'
  AND st.booking_date >= '2024-01-01'
GROUP BY CASE WHEN booking_date < '2024-06-01' THEN 'Before' ELSE 'After' END;

-- S5: Q4/2024 target vs actual for CW
SELECT
    rt.year, rt.quarter,
    rt.target_revenue_billion,
    ROUND(COALESCE(actual.revenue, 0), 1) AS actual_revenue_billion,
    ROUND(COALESCE(actual.revenue, 0) / rt.target_revenue_billion * 100, 1) AS achievement_pct
FROM revenue_targets rt
LEFT JOIN (
    SELECT
        YEAR(st.booking_date) AS yr,
        QUARTER(st.booking_date) AS qtr,
        SUM(st.actual_price_billion) AS revenue
    FROM sales_transactions st
    JOIN products p ON st.product_id = p.product_id
    JOIN sub_zones sz ON p.sub_zone_id = sz.sub_zone_id
    WHERE sz.project_id = 'PRJ-CW'
      AND st.transaction_status != 'cancelled'
    GROUP BY YEAR(st.booking_date), QUARTER(st.booking_date)
) actual ON rt.year = actual.yr AND rt.quarter = actual.qtr
WHERE rt.project_id = 'PRJ-CW'
ORDER BY rt.year, rt.quarter;
