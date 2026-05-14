# EC Distribution Demo — Mock Database

Mock data cho **Công ty Cổ phần EC** (EC Joint Stock Company, MST 0103563163) — nhà phân phối B2B vật liệu công nghiệp (nhôm, nhựa kỹ thuật, ESD, cách điện, que hàn).

**Database name:** `ec_distribution_demo`
**Time range:** 2024-05-01 → 2026-04-30 (24 tháng, "hiện tại" = cuối T4/2026)
**Total SQL size:** ~20 MB

## Cấu trúc dữ liệu

| Layer | Tables |
|---|---|
| Dimensions (6) | dim_calendar, dim_warehouse, dim_customer, dim_supplier, dim_product, dim_fx_rate |
| Facts (3) | fact_sales (~52K rows), fact_inventory_snapshot (~26K rows), fact_purchase (~7.5K rows) |
| Metadata (4) | _meta_tables, _meta_columns, _meta_kpi, _meta_glossary |

## File order

```
01_ddl_schema.sql           ~16 KB   CREATE DATABASE + CREATE TABLE × 13
02_metadata.sql             ~18 KB   INSERT INTO _meta_* (descriptions + KPIs)
03_master_data.sql         ~482 KB   INSERT INTO dim_* (calendar + 150 customers + 577 SKUs + 30 suppliers + 3650 FX rates)
04_a_fact_sales.sql         ~16 MB   INSERT INTO fact_sales (~52K transactions)
04_b_fact_inventory.sql    ~1.9 MB   INSERT INTO fact_inventory_snapshot
04_c_fact_purchase.sql     ~0.9 MB   INSERT INTO fact_purchase
05_validation_queries.sql    ~4 KB   SELECT queries để verify 5 demo scenarios
```

## Reproduce trên máy mới (Docker)

```bash
# 1. Khởi tạo MySQL container (nếu chưa có)
docker run --name mock_database \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=ec_distribution_demo \
  -p 3306:3306 \
  -d mysql:8.0 \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_unicode_ci

# 2. Chờ MySQL sẵn sàng
docker exec mock_database mysqladmin ping -uroot -proot --wait=30

# 3. Populate theo thứ tự
docker exec -i mock_database mysql -uroot -proot < ec_sql/01_ddl_schema.sql
docker exec -i mock_database mysql -uroot -proot < ec_sql/02_metadata.sql
docker exec -i mock_database mysql -uroot -proot < ec_sql/03_master_data.sql
docker exec -i mock_database mysql -uroot -proot < ec_sql/04_a_fact_sales.sql
docker exec -i mock_database mysql -uroot -proot < ec_sql/04_b_fact_inventory.sql
docker exec -i mock_database mysql -uroot -proot < ec_sql/04_c_fact_purchase.sql

# 4. Verify
docker exec -i mock_database mysql -uroot -proot < ec_sql/05_validation_queries.sql

# 5. Reset (nếu cần làm lại)
docker exec -i mock_database mysql -uroot -proot -e \
  "DROP DATABASE IF EXISTS ec_distribution_demo; CREATE DATABASE ec_distribution_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

## Hoặc dùng populate.sh (shortcut)

```bash
./populate.sh ec
```

## 5 demo scenarios

1. **Bức tranh T4/2026** — Revenue 16 tỷ, margin 21.85%, YoY +47%. Cảnh báo Samsung Display giảm.
2. **Margin erosion -2pp** — Breakdown: FX (KR -4.3pp do KRW +8%), mix shift, discount escalation top 10.
3. **Customer concentration + Samsung slow decline** — Top 10 = 54.5%. Samsung Display T4/2026 = -20% vs baseline. Hyundai/LG growth bù.
4. **Forecast cuối năm** — YTD 45 tỷ → projection 184 tỷ → miss target 280 tỷ (-96 tỷ). PEEK/PTFE +74% YoY là cơ hội.
5. **Stress test +10% COGS** — High margin (PEEK 32%, ULTEM 32%) chịu được; Low margin (PVC 16.5%, PP 16.2%) nguy hiểm.

## Connection để query

```python
import mysql.connector
conn = mysql.connector.connect(
    host='localhost', port=3306,
    user='root', password='root',
    database='ec_distribution_demo'
)
```

## Lưu ý

- Dữ liệu là **mock** — không phản ánh thực tế hoạt động của EC.
- Tên khách hàng dùng các doanh nghiệp thực tế tại VN làm reference (Samsung, LG, Hyundai, Foxconn, VinFast...) không có quan hệ kinh doanh thực với EC.
- FX rate là mock dựa trên trend Vietcombank reference.
- Encoding UTF-8 — đảm bảo MySQL container chạy với `--character-set-server=utf8mb4` để tiếng Việt hiển thị đúng.
