USE `sotrans_demo`;

-- ============================================================
-- SCENARIO 1: Báo cáo tổng quan T9/2024
-- ============================================================
SELECT 'Freight' as service,
       ROUND(SUM(revenue_vnd)/1e9,2) as rev_ty,
       ROUND(SUM(gross_profit_vnd)/1e9,2) as gp_ty,
       ROUND(AVG(gross_margin_pct),2) as margin_pct
FROM freight_shipments
WHERE shipment_date BETWEEN '2024-09-01' AND '2024-09-30';
-- Expected: ~85-95 tỷ revenue, ~8-10% margin (thấp hơn bình thường)

-- ============================================================
-- SCENARIO 2: Freight margin by route T7-T9/2024
-- ============================================================
SELECT r.route_code,
       ROUND(SUM(s.revenue_vnd)/1e6,0) as rev_tr,
       ROUND(AVG(s.gross_margin_pct),2) as margin_pct
FROM freight_shipments s
JOIN freight_routes r ON s.route_id = r.route_id
WHERE s.shipment_date >= '2024-07-01'
GROUP BY r.route_id, r.route_code ORDER BY margin_pct;
-- Expected: HCM-NRT-SEA ở bottom với margin ~3-4%

-- ============================================================
-- SCENARIO 2b: Texhong trên route HCM-NRT T7-T9/2024
-- ============================================================
SELECT c.customer_name,
       ROUND(SUM(s.revenue_vnd)/1e6,0) as rev_tr,
       ROUND(AVG(s.gross_margin_pct),2) as margin_pct,
       ROUND(SUM(s.revenue_vnd)*100.0 / (
           SELECT SUM(revenue_vnd) FROM freight_shipments
           WHERE route_id=1 AND shipment_date>='2024-07-01'
       ),1) as share_pct
FROM freight_shipments s
JOIN customers c ON s.customer_id=c.customer_id
WHERE s.route_id=1 AND s.shipment_date>='2024-07-01'
GROUP BY c.customer_id, c.customer_name ORDER BY rev_tr DESC;
-- Expected: Texhong ~65-67% share, margin ~3%

-- ============================================================
-- SCENARIO 3: Kho utilization T9/2024
-- ============================================================
SELECT w.warehouse_name, w.capacity_sqm,
       COALESCE(SUM(o.occupied_sqm),0) as occupied,
       ROUND(COALESCE(SUM(o.occupied_sqm),0)*100.0/w.capacity_sqm,1) as util_pct
FROM warehouses w
LEFT JOIN warehouse_occupancy o
  ON w.warehouse_id=o.warehouse_id AND o.occupancy_month='2024-09-01'
GROUP BY w.warehouse_id, w.warehouse_name, w.capacity_sqm
ORDER BY util_pct;
-- Expected: WH_LAN (Long An) util ~52-56% ở bottom

-- ============================================================
-- SCENARIO 3b: Uni-President trend tại Long An
-- ============================================================
SELECT o.occupancy_month, o.occupied_sqm,
       ROUND(o.revenue_vnd/1e6,1) as rev_tr
FROM warehouse_occupancy o
WHERE o.warehouse_id=4 AND o.customer_id=9
ORDER BY o.occupancy_month;
-- Expected: giảm dần từ 3700m² (T4/2024) → 900m² (T9/2024)

-- ============================================================
-- SCENARIO 4: Pace analysis 2024
-- ============================================================
SELECT 'FF' as service,
       ROUND(SUM(revenue_vnd)/1e9,1) as ytd_ty,
       1050 as target_ty,
       ROUND(SUM(revenue_vnd)/1050e9*100,1) as pace_pct
FROM freight_shipments WHERE YEAR(shipment_date)=2024
UNION ALL
SELECT 'WH',
       ROUND(SUM(revenue_vnd)/1e9,1),
       680,
       ROUND(SUM(revenue_vnd)/680e9*100,1)
FROM warehouse_occupancy WHERE YEAR(occupancy_month)=2024;
-- Expected FF: ~700-720 tỷ, pace 67-69%

-- ============================================================
-- SCENARIO 5: Customer profitability cross-service
-- ============================================================
SELECT c.customer_name, c.tier,
       ROUND(COALESCE(ff.rev,0)/1e9,1) as ff_rev_ty,
       ROUND(COALESCE(wh.rev,0)/1e9,1) as wh_rev_ty,
       ROUND((COALESCE(ff.gp,0)+COALESCE(wh.gp,0)) /
       NULLIF(COALESCE(ff.rev,0)+COALESCE(wh.rev,0),0)*100,1) as total_margin_pct
FROM customers c
LEFT JOIN (
    SELECT customer_id, SUM(revenue_vnd) rev, SUM(gross_profit_vnd) gp
    FROM freight_shipments WHERE YEAR(shipment_date)=2024 GROUP BY customer_id
) ff ON c.customer_id=ff.customer_id
LEFT JOIN (
    SELECT customer_id, SUM(revenue_vnd) rev, SUM(revenue_vnd-cost_vnd) gp
    FROM warehouse_occupancy WHERE YEAR(occupancy_month)=2024 GROUP BY customer_id
) wh ON c.customer_id=wh.customer_id
WHERE COALESCE(ff.rev,0)+COALESCE(wh.rev,0) > 0
ORDER BY (COALESCE(ff.rev,0)+COALESCE(wh.rev,0)) DESC LIMIT 20;
-- Expected: Texhong top revenue, margin ~5-8%; FrieslandCampina WH only

-- ============================================================
-- FALLBACK: ICD throughput trend
-- ============================================================
SELECT DATE_FORMAT(throughput_month,'%Y-%m') ym,
       SUM(teu_count) teu,
       ROUND(SUM(revenue_vnd)/1e9,2) rev_ty
FROM icd_teu_throughput GROUP BY ym ORDER BY ym;
-- Expected: ~6.000-8.000 TEU/tháng
