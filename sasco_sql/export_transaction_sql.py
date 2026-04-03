#!/usr/bin/env python3
"""Export transaction data (passenger_traffic, lounge_visits, sales_transactions)
to 04_transaction_data.sql in batch INSERT statements (max 1000 rows each)."""

import mysql.connector

db = mysql.connector.connect(
    host="127.0.0.1", port=3306, user="root", password="root",
    database="sasco_demo", charset="utf8mb4"
)
cursor = db.cursor()

def escape_str(val):
    if val is None:
        return "NULL"
    if isinstance(val, str):
        return "'" + val.replace("\\", "\\\\").replace("'", "\\'") + "'"
    return str(val)

def write_table(f, table_name, columns, batch_size=1000):
    """Export a table as batch INSERT statements."""
    col_list = ", ".join(columns)
    cursor.execute(f"SELECT {col_list} FROM {table_name}")

    batch = []
    total = 0
    for row in cursor:
        vals = []
        for v in row:
            if v is None:
                vals.append("NULL")
            elif isinstance(v, str):
                vals.append(escape_str(v))
            else:
                vals.append(str(v))
        batch.append("(" + ", ".join(vals) + ")")

        if len(batch) >= batch_size:
            f.write(f"INSERT INTO {table_name} ({col_list}) VALUES\n")
            f.write(",\n".join(batch) + ";\n\n")
            total += len(batch)
            batch = []

    if batch:
        f.write(f"INSERT INTO {table_name} ({col_list}) VALUES\n")
        f.write(",\n".join(batch) + ";\n\n")
        total += len(batch)

    return total

with open("/Users/vincenzo/sasco_sql/04_transaction_data.sql", "w", encoding="utf-8") as f:
    f.write("-- ============================================================================\n")
    f.write("-- SASCO Demo Database - Transaction Data\n")
    f.write("-- Mo ta: INSERT fact tables (passenger_traffic, lounge_visits, sales_transactions)\n")
    f.write("-- Note: Batch INSERT, max 1000 rows per statement\n")
    f.write("-- ============================================================================\n\n")
    f.write("USE sasco_demo;\n\n")

    # Disable FK checks and autocommit for speed
    f.write("SET FOREIGN_KEY_CHECKS = 0;\n")
    f.write("SET AUTOCOMMIT = 0;\n\n")

    # passenger_traffic
    print("Exporting passenger_traffic...")
    f.write("-- ============================================================================\n")
    f.write("-- passenger_traffic\n")
    f.write("-- ============================================================================\n\n")
    n = write_table(f, "passenger_traffic",
                    ["traffic_date", "terminal_id", "nationality_group_id", "passenger_type", "pax_count"])
    f.write("COMMIT;\n\n")
    print(f"  passenger_traffic: {n:,} rows")

    # lounge_visits
    print("Exporting lounge_visits...")
    f.write("-- ============================================================================\n")
    f.write("-- lounge_visits\n")
    f.write("-- ============================================================================\n\n")
    n = write_table(f, "lounge_visits",
                    ["visit_date", "hour_slot", "lounge_id", "terminal_id", "guest_count", "capacity", "utilization_rate"])
    f.write("COMMIT;\n\n")
    print(f"  lounge_visits: {n:,} rows")

    # sales_transactions
    print("Exporting sales_transactions...")
    f.write("-- ============================================================================\n")
    f.write("-- sales_transactions\n")
    f.write("-- ============================================================================\n\n")
    n = write_table(f, "sales_transactions",
                    ["transaction_date", "transaction_time", "location_id", "business_line_id",
                     "terminal_id", "product_id", "nationality_group_id", "quantity",
                     "unit_price_vnd", "total_revenue_vnd", "cost_vnd"])
    f.write("COMMIT;\n\n")
    print(f"  sales_transactions: {n:,} rows")

    # Re-enable
    f.write("SET FOREIGN_KEY_CHECKS = 1;\n")
    f.write("SET AUTOCOMMIT = 1;\n")

cursor.close()
db.close()
print("Export DONE: 04_transaction_data.sql")
