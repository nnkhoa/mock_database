-- ============================================================
-- 05_validation_queries.sql
-- Database: menas_demo
-- Menas Group — Validation & Sanity Check Queries
-- ============================================================

USE menas_demo;

-- 1. Row counts per table
SELECT 'business_units' AS tbl, COUNT(*) AS cnt FROM business_units
UNION ALL SELECT 'locations', COUNT(*) FROM locations
UNION ALL SELECT 'product_categories', COUNT(*) FROM product_categories
UNION ALL SELECT 'products', COUNT(*) FROM products
UNION ALL SELECT 'fb_outlets', COUNT(*) FROM fb_outlets
UNION ALL SELECT 'tenants', COUNT(*) FROM tenants
UNION ALL SELECT 'planned_locations', COUNT(*) FROM planned_locations
UNION ALL SELECT 'employees_summary', COUNT(*) FROM employees_summary
UNION ALL SELECT 'monthly_revenue', COUNT(*) FROM monthly_revenue
UNION ALL SELECT 'supermarket_daily_sales', COUNT(*) FROM supermarket_daily_sales
UNION ALL SELECT 'supermarket_shrinkage', COUNT(*) FROM supermarket_shrinkage
UNION ALL SELECT 'fb_monthly_revenue', COUNT(*) FROM fb_monthly_revenue
UNION ALL SELECT 'fb_monthly_costs', COUNT(*) FROM fb_monthly_costs
UNION ALL SELECT 'tenant_monthly_revenue', COUNT(*) FROM tenant_monthly_revenue
UNION ALL SELECT 'promotions', COUNT(*) FROM promotions
UNION ALL SELECT 'mall_events', COUNT(*) FROM mall_events
UNION ALL SELECT 'mall_daily_footfall', COUNT(*) FROM mall_daily_footfall
UNION ALL SELECT 'airport_daily_passengers', COUNT(*) FROM airport_daily_passengers;

-- 2. Total revenue by business unit (last 3 months)
SELECT business_unit_id,
       SUM(revenue_vnd) AS total_revenue,
       SUM(profit_vnd) AS total_profit,
       ROUND(SUM(profit_vnd)/SUM(revenue_vnd)*100, 2) AS margin_pct
FROM monthly_revenue
WHERE month >= '2026-01-01'
GROUP BY business_unit_id
ORDER BY total_revenue DESC;

-- 3. Supermarket gross margin trend
SELECT DATE_FORMAT(date, '%Y-%m') AS ym,
       location_id,
       SUM(selling_price_vnd * quantity - discount_amount_vnd) AS gross_sales,
       SUM(cost_price_vnd * quantity) AS total_cost,
       ROUND((SUM(selling_price_vnd * quantity - discount_amount_vnd) - SUM(cost_price_vnd * quantity))
             / SUM(selling_price_vnd * quantity - discount_amount_vnd) * 100, 2) AS margin_pct
FROM supermarket_daily_sales
GROUP BY ym, location_id
ORDER BY ym, location_id;

-- 4. F&B cost structure by outlet (latest month)
SELECT o.name, c.cost_type,
       SUM(c.amount_vnd) AS total_cost,
       ROUND(SUM(c.amount_vnd) / r.revenue_vnd * 100, 2) AS pct_of_revenue
FROM fb_monthly_costs c
JOIN fb_outlets o ON o.id = c.outlet_id
JOIN fb_monthly_revenue r ON r.outlet_id = c.outlet_id AND r.month = c.month
WHERE c.month = '2026-03-01'
GROUP BY o.name, c.cost_type, r.revenue_vnd
ORDER BY o.name, c.cost_type;

-- 5. Tenant revenue per sqm ranking
SELECT t.name, t.sqm_rented,
       ROUND(tmr.gross_revenue_vnd / t.sqm_rented, 0) AS rev_per_sqm,
       t.estimated_operating_margin_pct
FROM tenants t
JOIN tenant_monthly_revenue tmr ON tmr.tenant_id = t.id
WHERE tmr.month = '2026-03-01'
  AND t.location_id = 'LOC01'
ORDER BY rev_per_sqm DESC;

-- 6. Shrinkage rates by location and category (latest quarter)
SELECT s.location_id, pc.name AS category,
       ROUND(AVG(s.shrinkage_rate_pct), 2) AS avg_shrinkage_pct
FROM supermarket_shrinkage s
JOIN product_categories pc ON pc.id = s.category_id
WHERE s.month >= '2026-01-01'
GROUP BY s.location_id, pc.name
ORDER BY avg_shrinkage_pct DESC;

-- 7. Imported product mix trend (Anomaly 3 check)
SELECT DATE_FORMAT(date, '%Y-%m') AS ym,
       ROUND(SUM(CASE WHEN p.origin = 'imported' THEN sds.selling_price_vnd * sds.quantity ELSE 0 END)
             / SUM(sds.selling_price_vnd * sds.quantity) * 100, 2) AS imported_mix_pct
FROM supermarket_daily_sales sds
JOIN products p ON p.id = sds.product_id
GROUP BY ym
ORDER BY ym;

-- 8. F&B outlet performance comparison
SELECT o.name,
       ROUND(AVG(r.revenue_vnd), 0) AS avg_monthly_revenue,
       ROUND(AVG(r.avg_check_vnd), 0) AS avg_check,
       ROUND(AVG(r.covers), 0) AS avg_covers,
       ROUND((AVG(r.revenue_vnd) - (
         SELECT SUM(c.amount_vnd) FROM fb_monthly_costs c
         WHERE c.outlet_id = o.id AND c.month = r.month
       )) / AVG(r.revenue_vnd) * 100, 2) AS est_margin_pct
FROM fb_monthly_revenue r
JOIN fb_outlets o ON o.id = r.outlet_id
WHERE r.month >= '2025-10-01'
GROUP BY o.id, o.name
ORDER BY avg_monthly_revenue DESC;
