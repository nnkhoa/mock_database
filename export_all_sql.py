#!/usr/bin/env python3
"""Export all data from lubricants_demo to SQL files."""

import mysql.connector

conn = mysql.connector.connect(
    host='localhost', port=3306, user='root', password='root',
    database='lubricants_demo', charset='utf8mb4'
)
cur = conn.cursor()

def escape_val(v):
    if v is None:
        return 'NULL'
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, bool):
        return '1' if v else '0'
    s = str(v).replace("\\", "\\\\").replace("'", "\\'")
    return f"'{s}'"

def export_table(cur, table_name, batch_size=100):
    """Returns list of INSERT statements."""
    cur.execute(f"SELECT * FROM `{table_name}`")
    rows = cur.fetchall()
    if not rows:
        return []

    cur.execute(f"DESCRIBE `{table_name}`")
    columns = [col[0] for col in cur.fetchall()]
    col_list = ', '.join(columns)

    statements = []
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i+batch_size]
        values = []
        for row in batch:
            vals = ', '.join(escape_val(v) for v in row)
            values.append(f"({vals})")
        stmt = f"INSERT INTO `{table_name}` ({col_list}) VALUES\n" + ",\n".join(values) + ";"
        statements.append(stmt)

    return statements

# ============================================================
# 03_master_data.sql
# ============================================================
print("Exporting 03_master_data.sql...")
master_tables = ['regions', 'channels', 'suppliers', 'production_lines', 'distributors', 'products']

with open('/Users/vincenzo/Documents/Demo Data/ap_saigon_petro_sql/03_master_data.sql', 'w', encoding='utf-8') as f:
    f.write("-- ============================================================\n")
    f.write("-- 03_master_data.sql\n")
    f.write("-- AP Saigon Petro — Master/Dimension Data\n")
    f.write("-- ============================================================\n\n")
    f.write("USE lubricants_demo;\n\n")
    f.write("SET FOREIGN_KEY_CHECKS = 0;\n\n")

    for table in master_tables:
        cur.execute(f"SELECT COUNT(*) FROM `{table}`")
        count = cur.fetchone()[0]
        f.write(f"-- {table}: {count} records\n")
        f.write(f"DELETE FROM `{table}`;\n")
        stmts = export_table(cur, table, batch_size=50)
        for stmt in stmts:
            f.write(stmt + "\n\n")

    f.write("SET FOREIGN_KEY_CHECKS = 1;\n")

print("  Done: 03_master_data.sql")

# ============================================================
# 04_transaction_data.sql
# ============================================================
print("Exporting 04_transaction_data.sql...")
fact_tables = ['raw_material_costs', 'production_batches', 'sales_orders', 'payments']

with open('/Users/vincenzo/Documents/Demo Data/ap_saigon_petro_sql/04_transaction_data.sql', 'w', encoding='utf-8') as f:
    f.write("-- ============================================================\n")
    f.write("-- 04_transaction_data.sql\n")
    f.write("-- AP Saigon Petro — Transaction/Fact Data\n")
    f.write("-- WARNING: Large file. May take several minutes to import.\n")
    f.write("-- ============================================================\n\n")
    f.write("USE lubricants_demo;\n\n")
    f.write("SET FOREIGN_KEY_CHECKS = 0;\n")
    f.write("SET autocommit = 0;\n\n")

    for table in fact_tables:
        cur.execute(f"SELECT COUNT(*) FROM `{table}`")
        count = cur.fetchone()[0]
        f.write(f"-- {table}: {count} records\n")
        f.write(f"TRUNCATE TABLE `{table}`;\n\n")

        batch_size = 500 if table in ('sales_orders', 'payments') else 100
        stmts = export_table(cur, table, batch_size=batch_size)
        for idx, stmt in enumerate(stmts):
            f.write(stmt + "\n")
            if (idx + 1) % 10 == 0:
                f.write("COMMIT;\n\n")
        f.write("COMMIT;\n\n")

    f.write("SET FOREIGN_KEY_CHECKS = 1;\n")
    f.write("SET autocommit = 1;\n")

print("  Done: 04_transaction_data.sql")

# Check file sizes
import os
for fname in ['01_ddl_schema.sql', '03_master_data.sql', '04_transaction_data.sql', '05_validation_queries.sql']:
    fpath = f'/Users/vincenzo/Documents/Demo Data/ap_saigon_petro_sql/{fname}'
    if os.path.exists(fpath):
        size = os.path.getsize(fpath)
        if size > 1024*1024:
            print(f"  {fname}: {size/1024/1024:.1f} MB")
        else:
            print(f"  {fname}: {size/1024:.1f} KB")

cur.close()
conn.close()
print("\nExport complete!")
