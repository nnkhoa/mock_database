-- =====================================================================
-- 05_validation_queries.sql — kiểm tra dữ liệu & dry-run 6 demo scenarios
-- Chạy sau khi populate 01->04.
-- =====================================================================
USE tondonga_demo;

-- [TECH] Row counts
SELECT 'fact_sales' t, COUNT(*) n FROM fact_sales
UNION ALL SELECT 'fact_cogs', COUNT(*) FROM fact_cogs
UNION ALL SELECT 'dim_customer', COUNT(*) FROM dim_customer
UNION ALL SELECT 'dim_product', COUNT(*) FROM dim_product
UNION ALL SELECT 'dim_region', COUNT(*) FROM dim_region;

-- [TECH] Referential integrity (kỳ vọng 0 dòng)
SELECT COUNT(*) AS orphan_cogs FROM fact_cogs g
  LEFT JOIN fact_sales s ON g.sale_id = s.sale_id WHERE s.sale_id IS NULL;
SELECT COUNT(*) AS bad_revenue FROM fact_sales
  WHERE net_revenue_vnd <= 0 OR quantity_ton <= 0;

-- [TECH] net_revenue ≈ quantity × asp (sai số nhỏ do làm tròn)
SELECT MAX(ABS(net_revenue_vnd - quantity_ton*asp_vnd_per_ton)) AS max_diff FROM fact_sales;

-- [S1] Tổng quan SL & DT theo quý + YoY
SELECT c.year, c.quarter,
       ROUND(SUM(s.quantity_ton)) AS total_ton,
       ROUND(SUM(s.net_revenue_vnd)/1e9,1) AS revenue_ty,
       ROUND(SUM(s.net_revenue_vnd)/SUM(s.quantity_ton)/1e6,2) AS asp_trieu
FROM fact_sales s JOIN dim_calendar c ON s.sale_date=c.date
GROUP BY c.year, c.quarter ORDER BY c.year, c.quarter;

-- [S2] Kênh x miền theo năm (drill nội địa/XK, phát hiện miền Trung & EU)
SELECT ch.channel_name, r.macro_area, c.year,
       ROUND(SUM(s.net_revenue_vnd)/1e9,1) AS revenue_ty,
       ROUND(SUM(s.quantity_ton)) AS ton
FROM fact_sales s
JOIN dim_calendar c ON s.sale_date=c.date
JOIN dim_channel ch ON s.channel_id=ch.channel_id
JOIN dim_region  r ON s.region_id=r.region_id
GROUP BY ch.channel_name, r.macro_area, c.year
ORDER BY ch.channel_name, r.macro_area, c.year;

-- [S2] XK theo quốc gia (EU giảm)
SELECT r.country, c.year, ROUND(SUM(s.net_revenue_vnd)/1e9,1) AS revenue_ty
FROM fact_sales s JOIN dim_calendar c ON s.sale_date=c.date
JOIN dim_region r ON s.region_id=r.region_id
WHERE r.region_type='Xuất khẩu'
GROUP BY r.country, c.year ORDER BY r.country, c.year;

-- [S2] Đại lý miền Trung tụt mạnh nhất (drill customer)
SELECT cu.customer_name, c.year, ROUND(SUM(s.net_revenue_vnd)/1e9,2) AS revenue_ty
FROM fact_sales s JOIN dim_calendar c ON s.sale_date=c.date
JOIN dim_customer cu ON s.customer_id=cu.customer_id
JOIN dim_region r ON s.region_id=r.region_id
WHERE r.macro_area='Trung'
GROUP BY cu.customer_name, c.year ORDER BY cu.customer_name, c.year;

-- [S3] Margin & tác động HRC theo tháng (3 tháng cuối margin giảm)
SELECT c.year, c.month,
       ROUND(SUM(s.net_revenue_vnd)/1e9,1) AS revenue_ty,
       ROUND(SUM(g.total_cogs_vnd)/1e9,1)  AS cogs_ty,
       ROUND((SUM(s.net_revenue_vnd)-SUM(g.total_cogs_vnd))/SUM(s.net_revenue_vnd)*100,1) AS gross_margin_pct,
       ROUND(SUM(g.hrc_cost_vnd)/SUM(g.total_cogs_vnd)*100,1) AS hrc_share_pct,
       h.hrc_vnd_per_ton
FROM fact_sales s JOIN fact_cogs g ON s.sale_id=g.sale_id
JOIN dim_calendar c ON s.sale_date=c.date
LEFT JOIN dim_hrc_price h ON DATE_FORMAT(s.sale_date,'%Y-%m')=h.price_month
GROUP BY c.year, c.month, h.hrc_vnd_per_ton ORDER BY c.year, c.month;

-- [S4] Nhóm sản phẩm theo năm + ASP (tôn màu tăng, mix dịch chuyển)
SELECT p.product_group, c.year,
       ROUND(SUM(s.net_revenue_vnd)/1e9,1) AS revenue_ty,
       ROUND(SUM(s.quantity_ton)) AS ton,
       ROUND(SUM(s.net_revenue_vnd)/SUM(s.quantity_ton)/1e6,2) AS asp_trieu
FROM fact_sales s JOIN dim_product p ON s.product_id=p.product_id
JOIN dim_calendar c ON s.sale_date=c.date
GROUP BY p.product_group, c.year ORDER BY p.product_group, c.year;

-- [S5] Lũy kế vs kế hoạch theo tháng
SELECT t.period, t.target_volume_ton,
       ROUND(SUM(s.quantity_ton)) AS actual_ton,
       ROUND(SUM(s.quantity_ton)/t.target_volume_ton*100,1) AS achievement_pct
FROM dim_target t
LEFT JOIN fact_sales s ON DATE_FORMAT(s.sale_date,'%Y-%m')=t.period
GROUP BY t.period, t.target_volume_ton ORDER BY t.period;

-- [S6] Cấu trúc COGS 3 tháng gần nhất cho what-if HRC +10%
SELECT
  ROUND(SUM(g.hrc_cost_vnd)/SUM(g.total_cogs_vnd)*100,1)    AS hrc_share_cogs_pct,
  ROUND(SUM(g.total_cogs_vnd)/SUM(s.net_revenue_vnd)*100,1) AS cogs_to_revenue_pct,
  ROUND((SUM(s.net_revenue_vnd)-SUM(g.total_cogs_vnd))/SUM(s.net_revenue_vnd)*100,1) AS current_margin_pct
FROM fact_sales s JOIN fact_cogs g ON s.sale_id=g.sale_id
WHERE s.sale_date >= DATE_SUB((SELECT MAX(date) FROM dim_calendar), INTERVAL 3 MONTH);
-- What-if: HRC +10% => margin giảm ≈ hrc_share_cogs * cogs_to_revenue * 10%.

-- [FALLBACK] Miền Bắc theo tháng (không có anomaly)
SELECT c.year, c.month, ROUND(SUM(s.quantity_ton)) AS ton
FROM fact_sales s JOIN dim_calendar c ON s.sale_date=c.date
JOIN dim_region r ON s.region_id=r.region_id
WHERE r.macro_area='Bắc' GROUP BY c.year, c.month ORDER BY c.year, c.month;

-- [FALLBACK] Kênh Dự án/Công trình
SELECT c.year, ROUND(SUM(s.net_revenue_vnd)/1e9,1) AS revenue_ty
FROM fact_sales s JOIN dim_calendar c ON s.sale_date=c.date
JOIN dim_channel ch ON s.channel_id=ch.channel_id
WHERE ch.sub_channel='Dự án/Công trình' GROUP BY c.year ORDER BY c.year;
