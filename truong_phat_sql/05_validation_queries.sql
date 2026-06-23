-- ============================================================
-- 05_*.sql  |  wood_export_demo  |  Gỗ Trường Phát (demo)
-- Database: wood_export_demo
-- VALIDATION QUERIES — SELECT kiểm tra dữ liệu & dry-run 6 demo scenarios.
-- Encode: UTF-8 (utf8mb4). Chạy theo thứ tự 01→05.
-- ============================================================

/*!40101 SET NAMES utf8mb4 */;
SET NAMES utf8mb4;

USE `wood_export_demo`;

-- ── Đếm bản ghi ───────────────────────────────────────────────────────────
SELECT 'dim_calendar' t, COUNT(*) n FROM dim_calendar
UNION ALL SELECT 'dim_market', COUNT(*) FROM dim_market
UNION ALL SELECT 'dim_customer', COUNT(*) FROM dim_customer
UNION ALL SELECT 'dim_product', COUNT(*) FROM dim_product
UNION ALL SELECT 'dim_factory', COUNT(*) FROM dim_factory
UNION ALL SELECT 'dim_fx_monthly', COUNT(*) FROM dim_fx_monthly
UNION ALL SELECT 'fact_sales', COUNT(*) FROM fact_sales
UNION ALL SELECT 'fact_production', COUNT(*) FROM fact_production;

-- ── Technical: business logic ─────────────────────────────────────────────
SELECT COUNT(*) AS sai_gross_profit FROM fact_sales
 WHERE gross_profit_vnd <> net_revenue_vnd - cogs_total_vnd;
SELECT COUNT(*) AS sai_cogs_total FROM fact_sales
 WHERE cogs_total_vnd <> cogs_material_imported_vnd+cogs_material_domestic_vnd+cogs_labor_vnd+cogs_overhead_vnd;
SELECT COUNT(*) AS gia_tri_am FROM fact_sales WHERE net_revenue_vnd<=0 OR quantity<=0;

-- ── Magnitude & YoY ────────────────────────────────────────────────────────
SELECT SUM(net_revenue_vnd)/1e9 AS dt_12m_gan_nhat_ty
  FROM fact_sales WHERE order_date BETWEEN '2025-06-01' AND '2026-05-31';

-- T1. Doanh thu XK theo thị trường + YoY Q2 (Scenario 4)
SELECT m.market_name,
       SUM(CASE WHEN c.year=2026 AND c.quarter=2 THEN s.net_revenue_vnd END) AS dt_q2_2026,
       SUM(CASE WHEN c.year=2025 AND c.quarter=2 THEN s.net_revenue_vnd END) AS dt_q2_2025
FROM fact_sales s JOIN dim_calendar c ON s.order_date=c.date JOIN dim_market m ON s.market_id=m.market_id
WHERE s.channel='Xuất khẩu' AND ((c.year=2026 AND c.quarter=2) OR (c.year=2025 AND c.quarter=2))
GROUP BY m.market_name ORDER BY dt_q2_2026 DESC;

-- Market YoY (12 tháng) — Mỹ chậm, EU/Nhật tăng tốt
SELECT m.market_name,
   SUM(CASE WHEN s.order_date BETWEEN '2025-06-01' AND '2026-05-31' THEN s.net_revenue_vnd END)/1e9 AS y2_ty,
   SUM(CASE WHEN s.order_date BETWEEN '2024-06-01' AND '2025-05-31' THEN s.net_revenue_vnd END)/1e9 AS y1_ty
FROM fact_sales s JOIN dim_market m ON s.market_id=m.market_id
WHERE s.channel='Xuất khẩu' GROUP BY m.market_name ORDER BY y2_ty DESC;

-- T2. Biên gộp theo tháng + COGS nhập (Scenario 2 — margin erosion)
SELECT DATE_FORMAT(s.order_date,'%Y-%m') AS thang,
       SUM(s.net_revenue_vnd)/1e9 AS doanh_thu_ty,
       SUM(s.gross_profit_vnd)/SUM(s.net_revenue_vnd)*100 AS bien_gop_pct,
       SUM(s.cogs_material_imported_vnd)/SUM(s.net_revenue_vnd)*100 AS ty_le_go_nhap_pct,
       SUM(s.net_revenue_vnd)/SUM(s.quantity)/1e6 AS asp_trieu, fx.usd_vnd_avg
FROM fact_sales s JOIN dim_fx_monthly fx ON DATE_FORMAT(s.order_date,'%Y-%m-01')=fx.month
WHERE s.order_date>='2025-09-01' GROUP BY thang, fx.usd_vnd_avg ORDER BY thang;

-- T3. Westwood theo tháng (Scenario 3)
SELECT DATE_FORMAT(s.order_date,'%Y-%m') AS thang, SUM(s.net_revenue_vnd)/1e9 AS doanh_thu_ty
FROM fact_sales s JOIN dim_customer cu ON s.customer_id=cu.customer_id
WHERE cu.customer_name='Westwood Living' AND s.order_date>='2025-09-01'
GROUP BY thang ORDER BY thang;

-- T4. Mức tập trung khách hàng (Scenario 3)
SELECT cu.customer_name, SUM(s.net_revenue_vnd)/1e9 AS doanh_thu_ty,
   SUM(s.net_revenue_vnd)/(SELECT SUM(net_revenue_vnd) FROM fact_sales WHERE order_date>='2025-06-01')*100 AS ty_trong_pct
FROM fact_sales s JOIN dim_customer cu ON s.customer_id=cu.customer_id
WHERE s.order_date>='2025-06-01' GROUP BY cu.customer_name ORDER BY doanh_thu_ty DESC LIMIT 5;

-- T5. Exposure thuế Section 232 (Scenario 1)
SELECT p.product_category, p.section232_tariff_type, SUM(s.net_revenue_vnd)/1e9 AS dt_vao_my_12thang_ty
FROM fact_sales s JOIN dim_product p ON s.product_id=p.product_id JOIN dim_market m ON s.market_id=m.market_id
WHERE p.is_section232_affected=1 AND m.market_name='Mỹ' AND s.order_date>='2025-06-01'
GROUP BY p.product_category, p.section232_tariff_type ORDER BY dt_vao_my_12thang_ty DESC;

-- T6. Tăng trưởng + biên theo thị trường (Scenario 5)
SELECT m.market_name, SUM(s.net_revenue_vnd)/1e9 AS doanh_thu_12thang_ty,
       SUM(s.gross_profit_vnd)/SUM(s.net_revenue_vnd)*100 AS bien_gop_pct
FROM fact_sales s JOIN dim_market m ON s.market_id=m.market_id
WHERE s.channel='Xuất khẩu' AND s.order_date>='2025-06-01'
GROUP BY m.market_name ORDER BY doanh_thu_12thang_ty DESC;

-- T7. Công suất nhà máy gần nhất (Scenario 6)
SELECT f.factory_name, f.location, f.primary_category, AVG(pr.utilization_pct) AS utilization_tb
FROM fact_production pr JOIN dim_factory f ON pr.factory_id=f.factory_id
WHERE pr.month>='2026-03-01' GROUP BY f.factory_name, f.location, f.primary_category
ORDER BY utilization_tb DESC;

-- T8. Margin theo dòng SP (Scenario 6)
SELECT p.product_category, SUM(s.net_revenue_vnd)/1e9 AS doanh_thu_ty,
       SUM(s.gross_profit_vnd)/SUM(s.net_revenue_vnd)*100 AS bien_gop_pct
FROM fact_sales s JOIN dim_product p ON s.product_id=p.product_id
WHERE s.order_date>='2025-12-01' GROUP BY p.product_category ORDER BY bien_gop_pct DESC;

-- Pareto top 20% SKU
SELECT SUM(r) / (SELECT SUM(net_revenue_vnd) FROM fact_sales) * 100 AS top20pct_share
FROM (SELECT SUM(net_revenue_vnd) r FROM fact_sales GROUP BY product_id ORDER BY r DESC LIMIT 8) t;
