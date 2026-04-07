-- ============================================================
-- instant_noodle_demo — Validation Queries
-- ============================================================

USE `instant_noodle_demo`;

-- ============================================================
-- Record counts per table
-- ============================================================
SELECT 'factories' AS tbl, COUNT(*) AS cnt FROM factories
UNION ALL SELECT 'production_lines', COUNT(*) FROM production_lines
UNION ALL SELECT 'product_categories', COUNT(*) FROM product_categories
UNION ALL SELECT 'products', COUNT(*) FROM products
UNION ALL SELECT 'material_types', COUNT(*) FROM material_types
UNION ALL SELECT 'suppliers', COUNT(*) FROM suppliers
UNION ALL SELECT 'sales_channels', COUNT(*) FROM sales_channels
UNION ALL SELECT 'regions', COUNT(*) FROM regions
UNION ALL SELECT 'cost_categories', COUNT(*) FROM cost_categories
UNION ALL SELECT 'material_purchases', COUNT(*) FROM material_purchases
UNION ALL SELECT 'production_orders', COUNT(*) FROM production_orders
UNION ALL SELECT 'cost_allocations', COUNT(*) FROM cost_allocations
UNION ALL SELECT 'sales_orders', COUNT(*) FROM sales_orders
UNION ALL SELECT 'sales_order_items', COUNT(*) FROM sales_order_items
UNION ALL SELECT '_meta_tables', COUNT(*) FROM _meta_tables
UNION ALL SELECT '_meta_columns', COUNT(*) FROM _meta_columns
UNION ALL SELECT '_meta_kpi', COUNT(*) FROM _meta_kpi
UNION ALL SELECT '_meta_glossary', COUNT(*) FROM _meta_glossary;

-- ============================================================
-- Scenario 1: Factory overview — Revenue, COGS, Margin (H1/2025)
-- Expected: An Phú ~23%, Nam Tân Uyên ~21%, Gò Vấp ~15%, Bắc Ninh ~14%, Đà Nẵng ~5-7%
-- ============================================================
SELECT
    f.factory_name,
    ROUND(SUM(so.total_revenue_vnd) / 1e9, 1) AS revenue_ty_vnd,
    ROUND(SUM(so.total_cogs_vnd) / 1e9, 1) AS cogs_ty_vnd,
    ROUND((SUM(so.total_revenue_vnd) - SUM(so.total_cogs_vnd)) / 1e9, 1) AS gross_profit_ty_vnd,
    ROUND((SUM(so.total_revenue_vnd) - SUM(so.total_cogs_vnd)) / SUM(so.total_revenue_vnd) * 100, 1) AS gross_margin_pct
FROM sales_orders so
JOIN factories f ON so.factory_id = f.factory_id
WHERE so.order_date >= '2025-01-01'
GROUP BY f.factory_name
ORDER BY gross_margin_pct DESC;

-- ============================================================
-- Scenario 2: Cost breakdown — Đà Nẵng vs An Phú (H1/2025)
-- Expected: Đà Nẵng fixed costs (khấu hao+NC gián tiếp) ~26% vs An Phú ~10%
-- ============================================================
SELECT
    f.factory_short_name,
    cc.category_name,
    ROUND(SUM(ca.amount_vnd) / 1e9, 1) AS cost_ty_vnd,
    ROUND(SUM(ca.amount_vnd) / SUM(SUM(ca.amount_vnd)) OVER (PARTITION BY f.factory_id) * 100, 1) AS pct_of_total
FROM cost_allocations ca
JOIN factories f ON ca.factory_id = f.factory_id
JOIN cost_categories cc ON ca.cost_category_id = cc.cost_category_id
WHERE ca.month_date >= '2025-01-01' AND f.factory_id IN ('F01', 'F04')
GROUP BY f.factory_short_name, f.factory_id, cc.category_name
ORDER BY f.factory_short_name, pct_of_total DESC;

-- ============================================================
-- Scenario 3: Wheat price by factory (Q2/2025)
-- Expected: Bắc Ninh ~8% higher than An Phú
-- ============================================================
SELECT
    f.factory_short_name,
    ROUND(AVG(mp.unit_price_vnd), 0) AS avg_wheat_price_vnd_per_kg,
    ROUND(SUM(mp.quantity_kg), 0) AS total_purchased_kg
FROM material_purchases mp
JOIN factories f ON mp.factory_id = f.factory_id
WHERE mp.material_type_id = 'MAT01'
  AND mp.purchase_date >= '2025-04-01'
GROUP BY f.factory_short_name
ORDER BY avg_wheat_price_vnd_per_kg;

-- ============================================================
-- Scenario 4: Wastage rate by line at An Phú (May-Jun 2025)
-- Expected: L01-04 (new line) ~4%, others ~2.2%
-- ============================================================
SELECT
    pl.line_name,
    pl.product_type,
    pl.commissioned_date,
    ROUND(SUM(po.wastage_qty_packs) / (SUM(po.actual_qty_packs) + SUM(po.wastage_qty_packs)) * 100, 2) AS wastage_rate_pct
FROM production_orders po
JOIN production_lines pl ON po.line_id = pl.line_id
WHERE po.factory_id = 'F01' AND po.production_date >= '2025-05-01'
GROUP BY pl.line_name, pl.product_type, pl.commissioned_date
ORDER BY wastage_rate_pct DESC;

-- ============================================================
-- F04 Đà Nẵng monthly margin trend (Anomaly 1)
-- Expected: declining from ~8% (Jan) to ~5% (Jun 2025)
-- ============================================================
SELECT
    DATE_FORMAT(order_date, '%Y-%m') AS month,
    ROUND(SUM(total_revenue_vnd) / 1e9, 1) AS revenue_ty,
    ROUND((SUM(total_revenue_vnd) - SUM(total_cogs_vnd)) / SUM(total_revenue_vnd) * 100, 1) AS margin_pct
FROM sales_orders
WHERE factory_id = 'F04' AND order_date >= '2025-01-01'
GROUP BY month
ORDER BY month;

-- ============================================================
-- System margin trend (last 12 months)
-- Expected: declining from ~20% to ~18%
-- ============================================================
SELECT
    DATE_FORMAT(order_date, '%Y-%m') AS month,
    ROUND(SUM(total_revenue_vnd) / 1e9, 1) AS revenue_ty,
    ROUND((SUM(total_revenue_vnd) - SUM(total_cogs_vnd)) / SUM(total_revenue_vnd) * 100, 1) AS margin_pct
FROM sales_orders
WHERE order_date >= '2024-07-01'
GROUP BY month
ORDER BY month;

-- ============================================================
-- Channel distribution (H1/2025)
-- Expected: GT ~60%, MT ~25%, XK ~12%, Online ~3%
-- ============================================================
SELECT
    sc.channel_name,
    COUNT(*) AS num_orders,
    ROUND(SUM(so.total_revenue_vnd) / 1e9, 1) AS revenue_ty,
    ROUND(SUM(so.total_revenue_vnd) / (SELECT SUM(total_revenue_vnd) FROM sales_orders WHERE order_date >= '2025-01-01') * 100, 1) AS pct
FROM sales_orders so
JOIN sales_channels sc ON so.channel_id = sc.channel_id
WHERE so.order_date >= '2025-01-01'
GROUP BY sc.channel_name
ORDER BY pct DESC;

-- ============================================================
-- Region distribution (H1/2025)
-- Expected: Nam ~32%, Bắc ~28%, TNB ~16%, Trung ~12%, XK ~12%
-- ============================================================
SELECT
    r.region_name,
    ROUND(SUM(so.total_revenue_vnd) / 1e9, 1) AS revenue_ty,
    ROUND(SUM(so.total_revenue_vnd) / (SELECT SUM(total_revenue_vnd) FROM sales_orders WHERE order_date >= '2025-01-01') * 100, 1) AS pct
FROM sales_orders so
JOIN regions r ON so.region_id = r.region_id
WHERE so.order_date >= '2025-01-01'
GROUP BY r.region_name
ORDER BY pct DESC;

-- ============================================================
-- Top 10 SKU by revenue (Pareto check, H1/2025)
-- Expected: Top 10 (20%) dominate ~60-70% revenue
-- ============================================================
SELECT
    p.product_name,
    p.category_id,
    ROUND(SUM(soi.line_revenue_vnd) / 1e9, 1) AS revenue_ty,
    ROUND(SUM(soi.quantity_packs) / 1e6, 1) AS volume_million_packs
FROM sales_order_items soi
JOIN products p ON soi.product_id = p.product_id
JOIN sales_orders so ON soi.order_id = so.order_id
WHERE so.order_date >= '2025-01-01'
GROUP BY p.product_name, p.category_id
ORDER BY revenue_ty DESC
LIMIT 10;

-- ============================================================
-- Total revenue by year
-- Expected: 2024 ~5.8-6.1T, margin ~20%
-- ============================================================
SELECT
    YEAR(order_date) AS yr,
    ROUND(SUM(total_revenue_vnd) / 1e12, 2) AS revenue_nghin_ty,
    ROUND((SUM(total_revenue_vnd) - SUM(total_cogs_vnd)) / SUM(total_revenue_vnd) * 100, 1) AS margin_pct
FROM sales_orders
GROUP BY yr;
