# nbc_garment_demo — Tổng Công ty May Nhà Bè (NBC) | Dệt may BI

Database mock cho demo BI ngành dệt may. Phạm vi 2024-07-01 .. 2026-06-30 (24 tháng).
"Hiện tại" = cuối tháng 06/2026.

## Populate vào Docker container mới

```bash
docker run --name mock_database \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=nbc_garment_demo \
  -p 3306:3306 \
  -d mysql:8.0 \
  --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci

docker exec mock_database mysqladmin ping -uroot -proot --wait=30

docker exec -i mock_database mysql -uroot -proot < nbc_sql/01_ddl_schema.sql
docker exec -i mock_database mysql -uroot -proot < nbc_sql/02_metadata.sql
docker exec -i mock_database mysql -uroot -proot < nbc_sql/03_master_data.sql
docker exec -i mock_database mysql -uroot -proot < nbc_sql/04_transaction_data.sql

docker exec -i mock_database mysql -uroot -proot < nbc_sql/05_validation_queries.sql
```

## Reset
```bash
docker exec -i mock_database mysql -uroot -proot -e \
  "DROP DATABASE IF EXISTS nbc_garment_demo; CREATE DATABASE nbc_garment_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

## Số liệu

| Bảng | Rows |
|---|---|
| dim_calendar | 730 |
| dim_factory | 10 |
| dim_line | 134 |
| dim_customer | 10 |
| dim_product | 64 |
| dim_store | 200 |
| dim_fx_rate | 24 |
| fact_orders | 45,068 |
| fact_order_cost | 45,068 |
| fact_production | 83,884 |
| fact_retail_sales | 14,354 |

## Demo scenarios
- **Scenario 1** — Tổng quan H1: DT ~2.680 tỷ (+12% YoY), biên gộp giảm (LN tăng chậm hơn DT).
- **Scenario 2** — OTD: Sóc Trăng ~84% (target 95%); 2 đơn Calvin Klein giao trễ (phạt ~0.8M USD); An Giang trống ~82%, Nhà Bè quá tải ~112%.
- **Scenario 3** — Biên gộp H1-2026 17.2% vs H1-2025 19.1% (FX/NPL + method mix CMT 44% + labor tỉnh).
