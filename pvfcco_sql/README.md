# pvfcco_demo — Mock Database

**Khách hàng:** Tổng CTy Phân bón & Hóa chất Dầu khí (PVFCCo — DPM — Đạm Phú Mỹ)
**Phạm vi:** 2024-01-01 → 2025-12-31 (24 tháng) • "Hiện tại" = cuối 2025-12-31
**Charset:** utf8mb4_unicode_ci

## Files

| File | Mô tả |
|---|---|
| `01_ddl_schema.sql` | DROP+CREATE database `pvfcco_demo` và 13 tables |
| `02_metadata.sql` | INSERT `_meta_tables`, `_meta_columns`, `_meta_kpi`, `_meta_glossary` |
| `03_master_data.sql` | INSERT 5 dim_* + `_ref_gas_price` |
| `04_transaction_data.sql` | INSERT `fact_sales` (~321K), `fact_production` (~3.6K), `fact_inventory` (~1.3K) |
| `05_validation_queries.sql` | Câu query verify magnitude + 5 scenario dry-run |

## Reproduce — populate vào Docker container mới

```bash
# 1. Khởi tạo MySQL container
docker run --name mock_database \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=pvfcco_demo \
  -p 3306:3306 \
  -d mysql:8.0 \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_unicode_ci

# 2. Chờ MySQL sẵn sàng
docker exec mock_database mysqladmin ping -uroot -proot --wait=30

# 3. Populate theo thứ tự
docker exec -i mock_database mysql -uroot -proot < 01_ddl_schema.sql
docker exec -i mock_database mysql -uroot -proot < 02_metadata.sql
docker exec -i mock_database mysql -uroot -proot < 03_master_data.sql
docker exec -i mock_database mysql -uroot -proot < 04_transaction_data.sql

# 4. Verify
docker exec -i mock_database mysql -uroot -proot < 05_validation_queries.sql

# 5. Reset (nếu cần)
docker exec -i mock_database mysql -uroot -proot -e \
  "DROP DATABASE IF EXISTS pvfcco_demo; CREATE DATABASE pvfcco_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

## Schema tổng quan

```
DIM (5):    dim_calendar(731) • dim_regions(5) • dim_products(11)
            dim_distributors(40) • dim_workshops(3)
REF (1):    _ref_gas_price(24 tháng)
FACT (3):   fact_sales(321K) • fact_production(3.6K) • fact_inventory(1.3K)
META (4):   _meta_tables(13) • _meta_columns(64) • _meta_kpi(15) • _meta_glossary(21)
```

## 3 Anomaly nhúng

1. **Giá khí Q4/2025** → margin urê giảm 22% (T9) → 16% (T12). Bằng chứng: `_ref_gas_price` + `fact_production.gas_cost_vnd`.
2. **NPK OEE drop H2/2025** → 86% (T1-T6) → 68% (T7-T12). Bằng chứng: `fact_production` với `unplanned_downtime_hours` tăng vọt.
3. **Nam Trung Bộ & Tây Nguyên Q4/2025** → vùng giảm ~14% YoY trong khi các vùng khác +10%. Root cause: 2 NPP cấp 1 (`Đại lý Tây Nguyên Đắk Lắk`, `NPP Bình Định Miền Trung`) offtake ×0.70.

## 5 Demo Scenarios

| # | Câu hỏi (rút gọn) | KPI chính | Anomaly liên quan |
|---|---|---|---|
| 1 | Tổng quan T12/2025 vs cùng kỳ | Doanh thu, sản lượng SX | — (mở màn) |
| 2 ⭐ | Margin urê T12 giảm vì sao | gross_margin urê + gas_price | #1 |
| 3 ⭐ | Vùng nào kéo tụt tăng trưởng | Region YoY + distributor drill | #3 |
| 4 | OEE 3 xưởng, đâu là nghẽn | OEE + downtime split | #2 |
| 5 ⭐ | Ưu tiên dòng SP nào | margin + headroom by category | (tổng hợp) |

## Lưu ý khi join

- `fact_sales` và `fact_production` **khác grain** — KHÔNG JOIN trực tiếp.
- `fact_inventory` là **SNAPSHOT** cuối tháng — KHÔNG SUM nhiều snapshot.
- `_ref_gas_price` theo **tháng** — JOIN bằng `DATE_FORMAT(date,'%Y-%m-01') = month_date`.
- **Margin urê:** `cogs_vnd` đã gồm chi phí khí → KHÔNG cộng thêm `gas_cost_vnd` từ `fact_production` (double count).
- **NH₃ thương mại** chỉ từ `fact_sales`; `fact_production.actual_output_ton` của Xưởng NH₃ là TỔNG (gồm nội bộ làm urê).

## Đơn vị tiền tệ

Mọi cột `*_vnd` là **VND**. Format hiển thị:
- > 1 tỷ: "1.650 tỷ"
- < 1 tỷ: "XXX triệu"
- Phần trăm: 1 chữ số thập phân ("16,2%")

## Sinh ra bởi

Scripts ở `pvfcco_scripts/` của repo `mock_database`.
