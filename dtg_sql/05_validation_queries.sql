-- 05_validation_queries.sql — Verify data
USE `dtg_distribution_demo`;

-- S1: T9/2025 tổng quan
SELECT SUM(net_amount_vnd)/1e9 AS revenue_t9_ty,
       (SUM(net_amount_vnd - cogs_total_vnd) / SUM(net_amount_vnd))*100 AS margin_pct
FROM fact_sales WHERE `date` BETWEEN '2025-09-01' AND '2025-09-30';

-- S1: Plan T9/2025
SELECT target_value/1e9 AS plan_t9_ty FROM fact_budget
WHERE `year_month`='2025-09' AND dimension='total' AND metric='revenue';

-- S2: FX impact Ammerland T9
SELECT SUM(s.cogs_total_vnd - s.quantity*p.cogs_baseline)/1e6 AS fx_impact_m_vnd
FROM fact_sales s JOIN dim_product p ON s.product_id=p.product_id
JOIN dim_principal pr ON p.principal_id=pr.principal_id
WHERE s.`date` BETWEEN '2025-09-01' AND '2025-09-30' AND pr.principal_name='Ammerland';

-- S2: BOGO overspend Binggrae T9
SELECT (actual_amount_vnd - planned_amount_vnd)/1e6 AS overspend_m_vnd, description_vi
FROM fact_trade_promotion WHERE start_date >= '2025-09-01' AND principal_id=1;

-- S3: Imported content per principal
SELECT principal_name, source_currency, imported_content_pct FROM dim_principal;

-- S4: Binggrae MB Q3/2025 sell-in vs sell-out
SELECT 'sell_in' AS kind, SUM(s.net_amount_vnd)/1e9 AS ty
FROM fact_sales s JOIN dim_product p ON s.product_id=p.product_id
JOIN dim_principal pr ON p.principal_id=pr.principal_id
JOIN dim_store st ON s.store_id=st.store_id
JOIN dim_province prov ON st.province_id=prov.province_id
WHERE pr.principal_name='Binggrae' AND prov.region_id=1
  AND s.`date` BETWEEN '2025-07-01' AND '2025-09-30'
UNION ALL
SELECT 'sell_out' AS kind, SUM(so.revenue_vnd)/1e9 AS ty
FROM fact_sales_out so JOIN dim_product p ON so.product_id=p.product_id
JOIN dim_principal pr ON p.principal_id=pr.principal_id
JOIN dim_store st ON so.store_id=st.store_id
JOIN dim_province prov ON st.province_id=prov.province_id
WHERE pr.principal_name='Binggrae' AND prov.region_id=1
  AND so.`date` BETWEEN '2025-07-01' AND '2025-09-30';

-- S5: Branch CM FY 10/2024 - 09/2025
SELECT b.branch_name, SUM(s.net_amount_vnd)/1e9 AS revenue_ty,
  ((SUM(s.net_amount_vnd - s.cogs_total_vnd)) -
    (SELECT COALESCE(SUM(amount_vnd),0) FROM fact_operating_cost
     WHERE branch_id=b.branch_id AND `year_month` BETWEEN '2024-10' AND '2025-09')) / SUM(s.net_amount_vnd) * 100 AS cm_pct
FROM dim_branch b JOIN fact_sales s ON s.branch_id=b.branch_id
WHERE s.`date` BETWEEN '2024-10-01' AND '2025-09-30'
GROUP BY b.branch_id, b.branch_name ORDER BY cm_pct DESC;

-- S6: Near-expiry
SELECT p.product_name_vi, SUM(i.total_value_vnd)/1e9 AS value_ty, MIN(i.days_to_expire) AS min_days
FROM fact_inventory i JOIN dim_product p ON i.product_id=p.product_id
WHERE i.snapshot_date='2025-09-30' AND i.days_to_expire < 30
GROUP BY p.product_id, p.product_name_vi ORDER BY value_ty DESC;

-- S7: CJ HORECA growth
SELECT 'CJ HORECA 2024' AS period, SUM(s.net_amount_vnd)/1e9 AS ty FROM fact_sales s
JOIN dim_product p ON s.product_id=p.product_id JOIN dim_principal pr ON p.principal_id=pr.principal_id
WHERE pr.principal_name='CJ Food' AND s.channel_id=2 AND s.`date` BETWEEN '2023-10-01' AND '2024-09-30'
UNION ALL
SELECT 'CJ HORECA 2025', SUM(s.net_amount_vnd)/1e9 FROM fact_sales s
JOIN dim_product p ON s.product_id=p.product_id JOIN dim_principal pr ON p.principal_id=pr.principal_id
WHERE pr.principal_name='CJ Food' AND s.channel_id=2 AND s.`date` BETWEEN '2024-10-01' AND '2025-09-30';
