# Asia Foods — asia_foods_demo

MySQL demo database for an instant noodle manufacturer with 5 factories across Vietnam.

## Files

| File | Description |
|------|-------------|
| `01_ddl_schema.sql` | DDL — DROP + CREATE DATABASE, all CREATE TABLE statements |
| `02_metadata.sql` | Metadata tables (`_meta_tables`, `_meta_columns`, `_meta_kpi`, `_meta_glossary`) |
| `03_master_data.sql` | Dimension / master data (factories, products, suppliers, etc.) |
| `04_transaction_data.sql` | Fact / transaction data (purchases, production, costs, sales) |
| `05_validation_queries.sql` | Analytical queries to verify data integrity and explore scenarios |

## Quick Start

```bash
# 1. Start MySQL container
docker run --name mock_database \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=asia_foods_demo \
  -p 3306:3306 \
  -d mysql:8.0 \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_unicode_ci

# 2. Wait for MySQL
docker exec mock_database mysqladmin ping -uroot -proot --wait=30

# 3. Populate
docker exec -i mock_database mysql -uroot -proot < asia_foods_sql/01_ddl_schema.sql
docker exec -i mock_database mysql -uroot -proot < asia_foods_sql/02_metadata.sql
docker exec -i mock_database mysql -uroot -proot < asia_foods_sql/03_master_data.sql
docker exec -i mock_database mysql -uroot -proot < asia_foods_sql/04_transaction_data.sql

# 4. Verify
docker exec -i mock_database mysql -uroot -proot < asia_foods_sql/05_validation_queries.sql

# 5. Reset
docker exec -i mock_database mysql -uroot -proot -e \
  "DROP DATABASE IF EXISTS asia_foods_demo; CREATE DATABASE asia_foods_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

## Encoding

All files use UTF-8 (`utf8mb4`). Vietnamese names and text display correctly.
