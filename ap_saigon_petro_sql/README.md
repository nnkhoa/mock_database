# AP Saigon Petro — Lubricants Demo Database

## Tổng quan
Database demo cho **Công ty CP AP Saigon Petro** — ngành dầu nhớt (lubricants).  
Dữ liệu mock phục vụ demo AI engine (Claude via MCP) cho CEO/Board.

- **Database:** `ap_saigon_petro_demo`
- **Engine:** MySQL 8.0 (utf8mb4)
- **Data range:** 10/2024 – 03/2026 (18 tháng)
- **4 brands:** Saigon Petro, AP OIL, Sino, Polaris

## Cấu trúc files

| File | Mô tả |
|---|---|
| `01_ddl_schema.sql` | CREATE DATABASE, CREATE TABLE, indexes, constraints |
| `02_metadata.sql` | Metadata cho AI engine (_meta_tables, _meta_columns, _meta_kpi, _meta_glossary) |
| `03_master_data.sql` | Dimension tables: regions, channels, suppliers, production_lines, distributors, products |
| `04_transaction_data.sql` | Fact tables: sales_orders, payments, production_batches, raw_material_costs |
| `05_validation_queries.sql` | SELECT queries để verify data |

## Populate vào Docker container mới

```bash
# 1. Khởi tạo MySQL container
docker run --name mock_database \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=ap_saigon_petro_demo \
  -p 3306:3306 \
  -d mysql:8.0 \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_unicode_ci

# 2. Chờ MySQL sẵn sàng
docker exec mock_database mysqladmin ping -uroot -proot --wait=30

# 3. Populate data theo thứ tự
docker exec -i mock_database mysql -uroot -proot < ap_saigon_petro_sql/01_ddl_schema.sql
docker exec -i mock_database mysql -uroot -proot < ap_saigon_petro_sql/02_metadata.sql
docker exec -i mock_database mysql -uroot -proot < ap_saigon_petro_sql/03_master_data.sql
docker exec -i mock_database mysql -uroot -proot < ap_saigon_petro_sql/04_transaction_data.sql

# 4. Verify
docker exec -i mock_database mysql -uroot -proot < ap_saigon_petro_sql/05_validation_queries.sql

# 5. Reset (nếu cần làm lại)
docker exec -i mock_database mysql -uroot -proot -e \
  "DROP DATABASE IF EXISTS ap_saigon_petro_demo; CREATE DATABASE ap_saigon_petro_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
# Rồi chạy lại bước 3-4
```

## Thống kê data

| Table | Records | Mô tả |
|---|---|---|
| regions | 62 | 7 vùng, 62 tỉnh/thành |
| channels | 6 | B2B/B2C channels |
| distributors | 100 | 16 Tổng đại lý + 44 Cấp 1 + 40 Cấp 2 |
| products | 199 | 4 brands, 7 product groups |
| suppliers | 15 | Dầu gốc + phụ gia |
| production_lines | 5 | Nhà máy Cát Lái |
| sales_orders | ~122K | 18 tháng sell-in data |
| payments | ~115K | Thanh toán từ NPP |
| production_batches | ~6K | Batch sản xuất |
| raw_material_costs | 270 | Giá NVL theo tháng |

## Demo Scenarios (6 câu hỏi)

1. **Doanh thu & margin tổng quan** — DT ~800 tỷ/năm, margin giảm từ 28.3% → 25.7%
2. **Margin bị ăn mòn ở đâu** — ĐBSCL margin chỉ 19% (transport +50%, mineral 72%)
3. **NPP hiệu quả nhất/kém nhất** — 3 NPP DSO tăng dần, 1 NPP tăng trưởng 45%
4. **Hiệu suất nhà máy** — LINE-02 yield giảm 97.5% → 94.8%
5. **Dự báo margin** — Raw material price trend tăng
6. **Tổng hợp 3 vấn đề lớn nhất** — Cross-domain analysis

## Lưu ý cho AI engine

- Query `_meta_tables`, `_meta_columns` để hiểu schema
- Query `_meta_kpi` để biết cách tính KPI
- Query `_meta_glossary` để hiểu thuật ngữ tiếng Việt
- Data range: 10/2024 – 03/2026
- Chỉ có sell-in data (bán cho NPP), không có sell-out
- Giá dầu gốc là giá mock, không phản ánh giá thực tế
- "Cùng kỳ năm trước" = Oct 2024 – Mar 2025
- "6 tháng gần nhất" = Oct 2025 – Mar 2026
