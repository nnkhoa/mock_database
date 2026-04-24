-- 05_validation_queries.sql — Traphaco Demo verification
USE `traphaco_demo`;

-- =====================================================================
-- TECHNICAL CHECKS
-- =====================================================================
SELECT 'Row counts' AS check_name;
SELECT 'fact_sales' AS tbl, COUNT(*) AS rows FROM fact_sales
UNION ALL SELECT 'fact_inventory_snapshot', COUNT(*) FROM fact_inventory_snapshot
UNION ALL SELECT 'fact_plan_actual',        COUNT(*) FROM fact_plan_actual
UNION ALL SELECT 'fact_tender',             COUNT(*) FROM fact_tender
UNION ALL SELECT 'fact_tender_delivery',    COUNT(*) FROM fact_tender_delivery
UNION ALL SELECT 'fact_raw_material_price', COUNT(*) FROM fact_raw_material_price
UNION ALL SELECT 'dim_branch',  COUNT(*) FROM dim_branch
UNION ALL SELECT 'dim_product', COUNT(*) FROM dim_product
UNION ALL SELECT 'dim_customer',COUNT(*) FROM dim_customer
UNION ALL SELECT 'dim_tdv',     COUNT(*) FROM dim_tdv
UNION ALL SELECT 'dim_hospital',COUNT(*) FROM dim_hospital;

-- =====================================================================
-- AGGREGATE CHECKS — should match Traphaco BCTC
-- =====================================================================
SELECT 'Annual revenue (target 2024 ≈ 2,340 tỷ; 2023 ≈ 2,294 tỷ)' AS check_name;
SELECT YEAR(sale_date) AS yr, ROUND(SUM(net_amount_vnd)/1e9, 1) AS rev_ty,
       ROUND(SUM(net_amount_vnd-cogs_amount_vnd)/1e9, 1) AS gp_ty,
       ROUND(100*SUM(net_amount_vnd-cogs_amount_vnd)/SUM(net_amount_vnd), 1) AS margin_pct
FROM fact_sales GROUP BY yr;

-- =====================================================================
-- SCENARIO ① — Tổng quan Q4/2024
-- =====================================================================
SELECT 'Q4/2024 overview' AS check_name;
SELECT ROUND(SUM(net_amount_vnd)/1e9, 1) AS dt_ty,
       ROUND(SUM(net_amount_vnd-cogs_amount_vnd)/1e9, 1) AS gp_ty,
       ROUND(100*SUM(net_amount_vnd-cogs_amount_vnd)/SUM(net_amount_vnd), 1) AS margin_pct
FROM fact_sales WHERE sale_date BETWEEN '2024-10-01' AND '2024-12-31';

SELECT 'Q1/2024 margin đáy' AS check_name;
SELECT ROUND(100*SUM(net_amount_vnd-cogs_amount_vnd)/SUM(net_amount_vnd), 1) AS margin_pct_q1
FROM fact_sales WHERE sale_date BETWEEN '2024-01-01' AND '2024-03-31';

SELECT 'Premium Day-on-hand 5 CN lớn 31/12/2024' AS check_name;
SELECT b.branch_name, p.product_name, i.quantity_on_hand,
       ROUND(i.days_on_hand, 1) AS days_on_hand
FROM fact_inventory_snapshot i
JOIN dim_branch b ON b.branch_id=i.branch_id
JOIN dim_product p ON p.product_id=i.product_id
WHERE i.snapshot_date='2024-12-31'
  AND p.strategic_tier='Premium'
  AND b.branch_name IN ('CN Hồ Chí Minh','CN Hà Nội','CN Đà Nẵng','CN Hải Phòng','CN Cần Thơ')
ORDER BY days_on_hand;

SELECT 'Bexita Day-on-hand >90 ngày — số CN ảnh hưởng' AS check_name;
SELECT COUNT(*) AS n_rows_high
FROM fact_inventory_snapshot i
JOIN dim_product p ON p.product_id=i.product_id
WHERE i.snapshot_date='2024-12-31'
  AND p.product_name LIKE 'Bexita%'
  AND i.days_on_hand > 90;

-- =====================================================================
-- SCENARIO ② — Đấu thầu BV 2024
-- =====================================================================
SELECT 'Tender 2024 — pipeline by status' AS check_name;
SELECT status, COUNT(*) AS n, ROUND(SUM(bid_value_vnd)/1e9, 1) AS value_ty
FROM fact_tender WHERE YEAR(submit_date)=2024
GROUP BY status;

SELECT 'Delivery rate by product 2024' AS check_name;
SELECT p.product_name,
       ROUND(t.bid_total/1e9, 1) AS contracted_ty,
       ROUND(COALESCE(d.delivered_total,0)/1e9, 1) AS delivered_ty,
       ROUND(100*COALESCE(d.delivered_total,0)/t.bid_total, 1) AS delivery_pct
FROM (
  SELECT product_id, SUM(bid_value_vnd) AS bid_total
  FROM fact_tender WHERE status='won' AND YEAR(submit_date)=2024
  GROUP BY product_id
) t
LEFT JOIN (
  SELECT t2.product_id, SUM(d2.delivered_amount_vnd) AS delivered_total
  FROM fact_tender t2 JOIN fact_tender_delivery d2 ON d2.tender_id=t2.tender_id
  WHERE t2.status='won' AND YEAR(t2.submit_date)=2024
  GROUP BY t2.product_id
) d ON t.product_id=d.product_id
JOIN dim_product p ON p.product_id=t.product_id
WHERE p.product_name IN ('Ursodeoxycholic 300mg 30v','TimaRo 10mg 30v','Cebraton 60v','Bexita 50mg 30v');

SELECT 'Hà Tĩnh ETC breakthrough' AS check_name;
SELECT h.hospital_name, p.product_name, t.submit_date, t.status,
       ROUND(t.bid_value_vnd/1e9, 1) AS bid_ty
FROM fact_tender t
JOIN dim_hospital h ON h.hospital_id=t.hospital_id
JOIN dim_product p ON p.product_id=t.product_id
WHERE h.province='Hà Tĩnh' AND t.status='won' AND YEAR(t.submit_date)=2024;

-- =====================================================================
-- SCENARIO ③ — What-if dược liệu shortage
-- =====================================================================
SELECT 'Top SP phụ thuộc dược liệu nội — DT 2024' AS check_name;
SELECT p.product_name,
       ROUND(SUM(s.net_amount_vnd)/1e9, 1) AS dt_2024_ty,
       p.raw_material_primary,
       p.raw_material_dependency_pct
FROM fact_sales s
JOIN dim_product p ON p.product_id=s.product_id
WHERE YEAR(s.sale_date)=2024
  AND p.raw_material_primary IN ('Đinh lăng','Tam thất','Ba kích','Diếp cá')
GROUP BY p.product_id
ORDER BY dt_2024_ty DESC
LIMIT 15;

SELECT 'Raw material price index — Đinh lăng / Tam thất / Ba kích' AS check_name;
SELECT m.material_name, p.month,
       ROUND(p.avg_price_vnd_per_kg/1000, 0) AS price_kVND_per_kg,
       p.yoy_change_pct
FROM fact_raw_material_price p
JOIN dim_raw_material m ON m.raw_material_id=p.raw_material_id
WHERE m.material_name IN ('Đinh lăng','Tam thất','Ba kích')
  AND p.month BETWEEN '2024-01-01' AND '2024-12-01'
ORDER BY m.material_name, p.month;

-- =====================================================================
-- FALLBACK CHECKS — coverage
-- =====================================================================
SELECT 'Mọi CN có sales mọi quý 2024' AS check_name;
SELECT b.branch_name, COUNT(DISTINCT QUARTER(sale_date)) AS q_with_sales
FROM dim_branch b LEFT JOIN fact_sales s ON s.branch_id=b.branch_id AND YEAR(sale_date)=2024
GROUP BY b.branch_id HAVING q_with_sales < 4;

SELECT 'Mọi SKU có ít nhất 1 transaction' AS check_name;
SELECT COUNT(*) AS skus_no_sales FROM dim_product p
WHERE NOT EXISTS (SELECT 1 FROM fact_sales s WHERE s.product_id=p.product_id);

SELECT 'CN Kon Tum 2024 monthly trend' AS check_name;
SELECT MONTH(sale_date) AS m, ROUND(SUM(net_amount_vnd)/1e9, 2) AS dt_ty
FROM fact_sales s
JOIN dim_branch b ON s.branch_id=b.branch_id
WHERE b.branch_name='CN Kon Tum' AND YEAR(sale_date)=2024
GROUP BY MONTH(sale_date) ORDER BY m;
