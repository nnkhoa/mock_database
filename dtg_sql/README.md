# Đại Thuận Group (DTG) — Demo Database

## Quick populate (via populate.sh)

```bash
# From repo root
./populate.sh dtg
```

## Manual populate

```bash
# 1. Start container (if not already)
docker run --name mock_database \
  -e MYSQL_ROOT_PASSWORD=root \
  -p 3306:3306 -d mysql:8.0 \
  --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci

# 2. Wait until ready
docker exec mock_database mysqladmin ping -uroot -proot --wait=30

# 3. Populate
for f in dtg_sql/01_*.sql dtg_sql/02_*.sql dtg_sql/03_*.sql dtg_sql/04_*.sql; do
  docker exec -i mock_database mysql -uroot -proot < "$f"
done

# 4. Verify
docker exec -i mock_database mysql -uroot -proot dtg_distribution_demo < dtg_sql/05_validation_queries.sql

# 5. Reset
docker exec mock_database mysql -uroot -proot -e \
  "DROP DATABASE IF EXISTS dtg_distribution_demo;"
```

## Schema
- 11 dimension tables (dim_*)
- 8 fact tables (fact_sales, fact_sales_out, fact_inventory, fact_fx_rate,
  fact_trade_promotion, fact_operating_cost, fact_budget, fact_route_coverage)
- 4 metadata tables (_meta_tables, _meta_columns, _meta_kpi, _meta_glossary)

## Data range
2023-10-01 → 2025-09-30 (24 months). Demo "current" = 30/09/2025.

## Scenario catalog
7 scenarios covered. See `_meta_kpi.related_questions` for mapping.
