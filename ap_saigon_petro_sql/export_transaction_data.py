#!/usr/bin/env python3
"""
Export transaction/fact table data from ap_saigon_petro_demo MySQL database
into 04_transaction_data.sql with batch INSERT statements.
"""

import mysql.connector
import os
import datetime
from decimal import Decimal

# --- Configuration ---
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "root",
    "database": "ap_saigon_petro_demo",
}

TABLES = ["raw_material_costs", "production_batches", "sales_orders", "payments"]
BATCH_SIZE = 1000
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "04_transaction_data.sql")


def sql_escape(value):
    """Escape a Python value for SQL INSERT."""
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, float):
        return repr(value)
    if isinstance(value, (datetime.date, datetime.datetime)):
        return "'" + value.strftime("%Y-%m-%d") + "'"
    if isinstance(value, datetime.timedelta):
        # MySQL returns BOOLEAN as tinyint; connector may return timedelta for TIME cols
        total_seconds = int(value.total_seconds())
        return str(total_seconds)
    if isinstance(value, bytes):
        return "X'" + value.hex() + "'"
    # String
    s = str(value)
    s = s.replace("\\", "\\\\")
    s = s.replace("'", "\\'")
    s = s.replace("\n", "\\n")
    s = s.replace("\r", "\\r")
    s = s.replace("\0", "\\0")
    return "'" + s + "'"


def export_table(cursor, table_name, f):
    """Export one table's data as batch INSERT statements."""
    # Get column names
    cursor.execute(f"SHOW COLUMNS FROM `{table_name}`")
    columns = [row[0] for row in cursor.fetchall()]
    col_list = ", ".join(f"`{c}`" for c in columns)

    # Count rows
    cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
    row_count = cursor.fetchone()[0]

    f.write(f"\n-- ------------------------------------------------------------\n")
    f.write(f"-- {table_name}  ({row_count:,} rows)\n")
    f.write(f"-- ------------------------------------------------------------\n\n")
    f.write(f"DELETE FROM `{table_name}`;\n\n")

    if row_count == 0:
        f.write(f"-- (no data)\n")
        print(f"  {table_name}: 0 rows (empty)")
        return row_count

    # Fetch all rows (streaming via SSCursor-like approach for large tables)
    cursor.execute(f"SELECT * FROM `{table_name}`")

    batch = []
    total_written = 0

    while True:
        row = cursor.fetchone()
        if row is None:
            # Flush remaining batch
            if batch:
                _write_insert(f, table_name, col_list, batch)
                total_written += len(batch)
            break

        values = "(" + ", ".join(sql_escape(v) for v in row) + ")"
        batch.append(values)

        if len(batch) >= BATCH_SIZE:
            _write_insert(f, table_name, col_list, batch)
            total_written += len(batch)
            batch = []

    f.write(f"\n-- {table_name}: {total_written:,} rows inserted\n")
    print(f"  {table_name}: {total_written:,} rows exported")
    return total_written


def _write_insert(f, table_name, col_list, values_list):
    """Write a single INSERT statement with multiple value tuples."""
    f.write(f"INSERT INTO `{table_name}` ({col_list}) VALUES\n")
    f.write(",\n".join(values_list))
    f.write(";\n\n")


def main():
    print(f"Connecting to MySQL {DB_CONFIG['host']}:{DB_CONFIG['port']} ...")
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    print("Connected.\n")

    total_rows = 0

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        # Header
        f.write("-- ============================================================\n")
        f.write("-- 04_transaction_data.sql\n")
        f.write("-- AP Saigon Petro — Lubricants Demo Database\n")
        f.write("-- TRANSACTION / FACT TABLE DATA\n")
        f.write("-- Tables: " + ", ".join(TABLES) + "\n")
        f.write(f"-- Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("-- ============================================================\n\n")

        f.write("USE ap_saigon_petro_demo;\n\n")
        f.write("SET FOREIGN_KEY_CHECKS = 0;\n")

        for table in TABLES:
            print(f"Exporting {table} ...")
            count = export_table(cursor, table, f)
            total_rows += count

        f.write("\nSET FOREIGN_KEY_CHECKS = 1;\n")
        f.write(f"\n-- ============================================================\n")
        f.write(f"-- Total rows exported: {total_rows:,}\n")
        f.write(f"-- ============================================================\n")

    cursor.close()
    conn.close()

    file_size_mb = os.path.getsize(OUTPUT_FILE) / (1024 * 1024)
    print(f"\nDone. Output: {OUTPUT_FILE}")
    print(f"Total rows: {total_rows:,}")
    print(f"File size: {file_size_mb:.1f} MB")


if __name__ == "__main__":
    main()
