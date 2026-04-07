#!/usr/bin/env python3
"""Export Nova Consumer demo database to SQL files."""

import mysql.connector
import os

conn = mysql.connector.connect(
    host='localhost', port=3306, user='root', password='root',
    database='nova_consumer_demo', charset='utf8mb4'
)
cur = conn.cursor()

OUT_DIR = '/Users/vincenzo/Documents/Demo Data/nova_consumer_sql'
os.makedirs(OUT_DIR, exist_ok=True)

def escape_val(val):
    if val is None:
        return 'NULL'
    if isinstance(val, (int, float)):
        return str(val)
    s = str(val).replace("\\", "\\\\").replace("'", "\\'")
    return f"'{s}'"

def export_table(table_name, file_handle, generated_cols=None):
    """Export a table's data as INSERT statements."""
    # Get column info
    cur.execute(f"SHOW COLUMNS FROM `{table_name}`")
    columns = []
    for row in cur.fetchall():
        col_name = row[0]
        extra = row[5] if len(row) > 5 else ''
        # Skip auto_increment PKs and generated columns
        if 'auto_increment' in str(extra).lower():
            continue
        if generated_cols and col_name in generated_cols:
            continue
        columns.append(col_name)

    col_list = ', '.join(f'`{c}`' for c in columns)

    cur.execute(f"SELECT {col_list} FROM `{table_name}`")
    rows = cur.fetchall()

    if not rows:
        file_handle.write(f"-- {table_name}: no data\n\n")
        return 0

    # Batch INSERT (max 500 rows per statement)
    batch_size = 500
    total = 0
    for b in range(0, len(rows), batch_size):
        batch = rows[b:b+batch_size]
        file_handle.write(f"INSERT INTO `{table_name}` ({col_list}) VALUES\n")
        values = []
        for row in batch:
            vals = ', '.join(escape_val(v) for v in row)
            values.append(f"  ({vals})")
        file_handle.write(',\n'.join(values))
        file_handle.write(';\n\n')
        total += len(batch)

    return total

# ============================================
# 02_metadata.sql
# ============================================
print("Exporting 02_metadata.sql...")
with open(os.path.join(OUT_DIR, '02_metadata.sql'), 'w', encoding='utf-8') as f:
    f.write("-- ============================================================\n")
    f.write("-- Nova Consumer Demo — Metadata Tables\n")
    f.write("-- Bảng mô tả cấu trúc database cho AI engine\n")
    f.write("-- ============================================================\n\n")
    f.write("USE nova_consumer_demo;\n\n")

    for t in ['_meta_tables', '_meta_columns', '_meta_kpi', '_meta_glossary']:
        cnt = export_table(t, f)
        print(f"  {t}: {cnt} records")

# ============================================
# 03_master_data.sql
# ============================================
print("Exporting 03_master_data.sql...")
with open(os.path.join(OUT_DIR, '03_master_data.sql'), 'w', encoding='utf-8') as f:
    f.write("-- ============================================================\n")
    f.write("-- Nova Consumer Demo — Master Data (Dimension Tables)\n")
    f.write("-- Dữ liệu tham chiếu: mảng KD, nhà máy, sản phẩm, NVL, khách hàng\n")
    f.write("-- ============================================================\n\n")
    f.write("USE nova_consumer_demo;\n\n")

    master_tables = [
        'business_segments', 'subsidiaries', 'regions', 'factories', 'farms',
        'product_categories', 'products', 'raw_materials', 'suppliers',
        'distribution_channels', 'customers'
    ]
    for t in master_tables:
        cnt = export_table(t, f)
        print(f"  {t}: {cnt} records")

# ============================================
# 04_transaction_data.sql
# ============================================
print("Exporting 04_transaction_data.sql...")
with open(os.path.join(OUT_DIR, '04_transaction_data.sql'), 'w', encoding='utf-8') as f:
    f.write("-- ============================================================\n")
    f.write("-- Nova Consumer Demo — Transaction Data (Fact Tables)\n")
    f.write("-- 18 tháng: 07/2024 - 12/2025\n")
    f.write("-- ============================================================\n\n")
    f.write("USE nova_consumer_demo;\n\n")

    # Tables with generated columns to skip
    generated = {
        'segment_financials': ['gross_profit', 'gross_margin_pct'],
        'production_monthly': ['utilization_pct', 'total_production_cost', 'cost_per_ton'],
        'material_purchases': ['total_amount'],
    }

    fact_tables = [
        'segment_financials', 'production_monthly', 'material_purchases',
        'bill_of_materials', 'sales_transactions', 'production_orders',
        'farm_operations', 'logistics_costs'
    ]
    for t in fact_tables:
        cnt = export_table(t, f, generated_cols=generated.get(t))
        print(f"  {t}: {cnt} records")

# ============================================
# 05_validation_queries.sql
# ============================================
print("Writing 05_validation_queries.sql...")
with open(os.path.join(OUT_DIR, '05_validation_queries.sql'), 'w', encoding='utf-8') as f:
    f.write("""-- ============================================================
-- Nova Consumer Demo — Validation Queries
-- Chạy sau khi populate để verify dữ liệu
-- ============================================================

USE nova_consumer_demo;

-- 1. Record counts
SELECT 'business_segments' as tbl, COUNT(*) as cnt FROM business_segments
UNION ALL SELECT 'subsidiaries', COUNT(*) FROM subsidiaries
UNION ALL SELECT 'regions', COUNT(*) FROM regions
UNION ALL SELECT 'factories', COUNT(*) FROM factories
UNION ALL SELECT 'farms', COUNT(*) FROM farms
UNION ALL SELECT 'product_categories', COUNT(*) FROM product_categories
UNION ALL SELECT 'products', COUNT(*) FROM products
UNION ALL SELECT 'raw_materials', COUNT(*) FROM raw_materials
UNION ALL SELECT 'suppliers', COUNT(*) FROM suppliers
UNION ALL SELECT 'distribution_channels', COUNT(*) FROM distribution_channels
UNION ALL SELECT 'customers', COUNT(*) FROM customers
UNION ALL SELECT 'segment_financials', COUNT(*) FROM segment_financials
UNION ALL SELECT 'production_monthly', COUNT(*) FROM production_monthly
UNION ALL SELECT 'material_purchases', COUNT(*) FROM material_purchases
UNION ALL SELECT 'bill_of_materials', COUNT(*) FROM bill_of_materials
UNION ALL SELECT 'sales_transactions', COUNT(*) FROM sales_transactions
UNION ALL SELECT 'production_orders', COUNT(*) FROM production_orders
UNION ALL SELECT 'farm_operations', COUNT(*) FROM farm_operations
UNION ALL SELECT 'logistics_costs', COUNT(*) FROM logistics_costs
UNION ALL SELECT '_meta_tables', COUNT(*) FROM _meta_tables
UNION ALL SELECT '_meta_columns', COUNT(*) FROM _meta_columns
UNION ALL SELECT '_meta_kpi', COUNT(*) FROM _meta_kpi
UNION ALL SELECT '_meta_glossary', COUNT(*) FROM _meta_glossary;

-- 2. Total revenue check (target: ~6000-6500 tỷ VND over 18 months)
SELECT 'Total Revenue (tỷ VND)' as metric, ROUND(SUM(total_revenue)/1000, 1) as value
FROM segment_financials;

-- 3. Revenue & margin by segment
SELECT bs.segment_name,
       ROUND(SUM(sf.total_revenue)/1000, 1) as revenue_ty_vnd,
       ROUND(AVG(sf.gross_margin_pct), 2) as avg_margin_pct
FROM segment_financials sf
JOIN business_segments bs ON sf.segment_id = bs.segment_id
GROUP BY bs.segment_name;

-- 4. S1 ANOMALY: TACN margin erosion (last 6 months)
SELECT `year_month`, total_revenue, total_cogs, gross_margin_pct
FROM segment_financials WHERE segment_id = 2
ORDER BY `year_month` DESC LIMIT 6;

-- 5. S2 ANOMALY: Đồng Nai utilization drop + cost increase
SELECT f.factory_name, pm.`year_month`, pm.actual_output_tons, pm.utilization_pct, pm.cost_per_ton
FROM production_monthly pm JOIN factories f ON pm.factory_id = f.factory_id
WHERE f.factory_code = 'NM_TACN_DN'
ORDER BY pm.`year_month` DESC LIMIT 6;

-- 6. S2 COUNTER: Hưng Yên utilization increase
SELECT f.factory_name, pm.`year_month`, pm.utilization_pct, pm.cost_per_ton
FROM production_monthly pm JOIN factories f ON pm.factory_id = f.factory_id
WHERE f.factory_code = 'NM_TACN_HY'
ORDER BY pm.`year_month` DESC LIMIT 6;

-- 7. S3 ANOMALY: Corn price trend (last 8 months)
SELECT DATE_FORMAT(purchase_date, '%Y-%m') as month,
       ROUND(AVG(unit_price), 0) as avg_corn_price_per_kg
FROM material_purchases mp
JOIN raw_materials rm ON mp.material_id = rm.material_id
WHERE rm.material_code = 'NVL_NGO'
GROUP BY month ORDER BY month DESC LIMIT 8;

-- 8. S3: Corn price by factory (Hưng Yên should be ~5% cheaper)
SELECT f.factory_name, ROUND(AVG(mp.unit_price), 0) as avg_corn_price
FROM material_purchases mp
JOIN factories f ON mp.factory_id = f.factory_id
JOIN raw_materials rm ON mp.material_id = rm.material_id
WHERE rm.material_code = 'NVL_NGO' AND mp.purchase_date >= '2025-10-01'
GROUP BY f.factory_name;

-- 9. S4: Factory utilization comparison (latest month)
SELECT f.factory_name, pm.actual_output_tons, pm.max_capacity_tons, pm.utilization_pct,
       (pm.max_capacity_tons - pm.actual_output_tons) as spare_capacity_tons, pm.cost_per_ton
FROM production_monthly pm JOIN factories f ON pm.factory_id = f.factory_id
WHERE pm.`year_month` = '2025-12-01' AND f.factory_type = 'Thức ăn chăn nuôi';

-- 10. S5: Vaccine premium products (high margin)
SELECT p.product_name, p.margin_pct, p.unit_price, pc.category_name
FROM products p
JOIN product_categories pc ON p.category_id = pc.category_id
WHERE pc.category_code = 'AH_VAC_IMPORT';
""")

print("\nAll SQL files exported!")

cur.close()
conn.close()
