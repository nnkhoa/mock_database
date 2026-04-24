# Traphaco Demo SQL Dataset

`traphaco_demo` — 24 tháng dữ liệu (T1/2023 – T12/2024) cho demo CEO Traphaco
pitching HĐQT (Mirae Asset context).

## Files
| File | Nội dung |
|---|---|
| `01_ddl_schema.sql` | CREATE DATABASE + 9 dim + 6 fact + 4 metadata tables |
| `02_metadata.sql`   | INSERT vào `_meta_tables`, `_meta_columns`, `_meta_kpi`, `_meta_glossary` |
| `03_master_data.sql`| INSERT vào dim tables (calendar 852, branch 28, product 130, customer 500, tdv ~620, hospital 200, ...) |
| `04_transaction_data.sql` | INSERT vào fact tables (sales ~250K, inventory ~30K, tender ~330, delivery ~700, raw_mat_price 360, plan_actual ~700) |
| `05_validation_queries.sql` | SELECT để verify aggregate + scenarios |
| `README.md` | (file này) |

## Reproduce trên Docker container mới

```bash
# 1) Khởi MySQL
docker run --name mock_database \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=traphaco_demo \
  -p 3306:3306 -d mysql:8.0 \
  --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci

# 2) Chờ ready
docker exec mock_database mysqladmin ping -uroot -proot --wait=30

# 3) Populate (theo thứ tự)
docker exec -i mock_database mysql -uroot -proot < traphaco_sql/01_ddl_schema.sql
docker exec -i mock_database mysql -uroot -proot < traphaco_sql/02_metadata.sql
docker exec -i mock_database mysql -uroot -proot < traphaco_sql/03_master_data.sql
docker exec -i mock_database mysql -uroot -proot < traphaco_sql/04_transaction_data.sql

# 4) Verify
docker exec -i mock_database mysql -uroot -proot < traphaco_sql/05_validation_queries.sql

# 5) Reset (nếu cần)
docker exec -i mock_database mysql -uroot -proot -e \
  "DROP DATABASE IF EXISTS traphaco_demo; CREATE DATABASE traphaco_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

Hoặc dùng helper script trong repo:

```bash
./populate.sh traphaco
```

## Demo Scenarios

1. **Tổng quan Q4/2024** — flag 3 anomaly (Premium DoH, dược liệu giá quay đầu, Bexita tồn cao).
2. **Đấu thầu + cung ứng BV 2024** — pipeline 4 status, delivery rate per SP, cross-reference Bexita OTC vs ETC.
3. **What-if hạn chế 10% dược liệu nội** — quantify tác động × 3 giải pháp priority.

## Aggregate targets (vs Traphaco thực tế)

| Metric | Target | |
|---|---:|---|
| DT 2024 | 2,340 tỷ | ±5% |
| LNST 2024 (proxy: GP × ratio) | 239 tỷ | ±10% |
| Biên gộp 2024 | 51.2% | ±1pp |
| Q1/2024 biên đáy | 45.8% | ±1pp |
| Q4/2024 biên hồi phục | 52.1% | ±1pp |
| ETC tender won 2024 | 268 tỷ | ±15% |
