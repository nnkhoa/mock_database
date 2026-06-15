# PV OIL — Demo Database (Bán lẻ Xăng dầu)

Mock database cho **Tổng Công ty Dầu Việt Nam – CTCP (PV OIL)** — pitch CEO/HĐQT
về câu chuyện chiến lược **non-oil**: phát triển mảng phi xăng dầu, hiệu quả vận hành
cửa hàng, tối ưu margin, tăng trưởng doanh thu.

## Thông tin

- **Database:** `pvoil_retail_demo` (MySQL 8.0, utf8mb4_unicode_ci)
- **Phạm vi:** 2024-12-01 .. 2026-05-31 (18 tháng) | "Hiện tại" = cuối 05/2026
- **Đơn vị tiền tệ:** VND
- **Tables:** 5 dimension + 3 fact + 4 meta (12 tables)
- **Phạm vi mock:** CHỈ mảng **bán lẻ qua cửa hàng** (~29.000 tỷ DT/năm, ~1,25 triệu m³/năm).
  KHÔNG gồm bán buôn / xuất khẩu / Jet A1 / condensate.

## Magnitude anchors (khớp số thật PV OIL)

| Chỉ số | 12 tháng gần nhất |
|--------|-------------------|
| DT bán lẻ (tỷ) | ~29.700 |
| Sản lượng (triệu m³) | ~1,25 |
| Tỷ trọng non-oil DT | ~1,6% |
| Margin/lít | ~720đ (đầu kỳ) → ~600đ (gần nhất) |
| Số cửa hàng | 2.640 (840 COCO + 1.800 DODO) |
| Cửa hàng có non-oil | ~340 |

## 5 Demo Scenarios + Anomalies

| # | Scenario | Tầng | Anomaly |
|---|----------|------|---------|
| C1 | Bức tranh tổng & xếp hạng cửa hàng (lợi nhuận/m²) | Descriptive | C: 95 cửa hàng mới ramp-up lỗ (12 mở <3 tháng) |
| C3 | Lookalike: nhân rộng non-oil ở đâu | Predictive | D: ~187 cửa hàng cùng DNA chưa có non-oil |
| C4 | Nghịch lý sản lượng tăng / lợi nhuận giảm | Diagnostic | B: margin/lít 720→600 (Miền Trung nặng nhất) |
| C2 | Non-oil bán tốt ở đâu & vì sao (LÕI) | Diagnostic | A: non-oil ~1,6% DT nhưng ~11% LN; tương quan dwell_time |
| C5 | Danh sách hành động cho board | Strategic | tổng hợp C1-C4 + payback |

Thứ tự demo: **C1 → C3 → C4 → C2 → C5**.

## Reproduce (Docker MySQL 8.0)

```bash
# Cách 1 — dùng populate.sh ở thư mục gốc repo (container 'mock_database')
docker compose up -d
./populate.sh pvoil

# Cách 2 — thủ công
docker run --name pvoil_db -e MYSQL_ROOT_PASSWORD=root -e MYSQL_DATABASE=pvoil_retail_demo \
  -p 3306:3306 -d mysql:8.0 --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
docker exec pvoil_db mysqladmin ping -uroot -proot --wait=30
docker exec -i pvoil_db mysql -uroot -proot < pvoil_sql/01_ddl_schema.sql
docker exec -i pvoil_db mysql -uroot -proot < pvoil_sql/02_metadata.sql
docker exec -i pvoil_db mysql -uroot -proot < pvoil_sql/03_master_data.sql
docker exec -i pvoil_db mysql -uroot -proot < pvoil_sql/04_transaction_data.sql
docker exec -i pvoil_db mysql -uroot -proot < pvoil_sql/05_validation_queries.sql
```

## Lưu ý cho AI engine

- **Metadata tables** (`_meta_*`) là nguồn truth schema cho LLM.
- **Grain:** `fact_sales_daily` = COCO × ngày × sản phẩm; `fact_sales_monthly` = DODO × tháng × sản phẩm.
  Muốn TOÀN MẠNG: quy daily → tháng (GROUP BY) rồi UNION ALL với monthly.
- **Margin/lít** chỉ tính trên `product_category='oil' AND unit='lít'`.
- **Non-oil** chỉ có ở ~340 store (`has_nonoil=1`).
- **fact_store_opex_monthly** grain THÁNG — aggregate sales về tháng trước khi ghép, tránh nhân theo số ngày.
- **Cửa hàng mới** (open_date gần): dùng `TIMESTAMPDIFF(MONTH, open_date, ...)` để tránh kết luận "kém" oan.

## Files

| File | Mô tả |
|------|-------|
| 01_ddl_schema.sql | CREATE DATABASE + 12 tables |
| 02_metadata.sql | INSERT _meta_* |
| 03_master_data.sql | INSERT 5 dimension tables |
| 04_transaction_data.sql | INSERT 3 fact tables (batch ≤1000 rows) |
| 05_validation_queries.sql | SELECT verify |
