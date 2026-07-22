# nhabe_bi_demo — Tổng Công ty May Nhà Bè (NBC / mảng Nhà Bè Trading) | BI Kiểm soát biên lợi nhuận

Database mock cho demo BI ngành **may mặc xuất khẩu** (FOB/CM/ODM + gia công ngoài GCN).
Phạm vi **2025-01-01 .. 2026-06-30 (18 tháng)**. "Hiện tại" = cuối **30/06/2026**.
Tỷ giá quy đổi demo: **1 USD = 26.000 VND**.

Data schema chi tiết: [database-schema_2.md](database-schema_2.md) · System prompt: [system-prompt_2.md](system-prompt_2.md)

## Populate vào Docker container `mock_database` (đang chạy)

```bash
./populate.sh nhabe          # từ thư mục gốc repo — tự đọc '-- Database:' và nạp 01→04
```

Hoặc chạy tay:

```bash
docker exec -i mock_database mysql -uroot -proot < nhabe_sql/01_ddl_schema.sql
docker exec -i mock_database mysql -uroot -proot < nhabe_sql/02_metadata.sql
docker exec -i mock_database mysql -uroot -proot < nhabe_sql/03_master_data.sql
docker exec -i mock_database mysql -uroot -proot < nhabe_sql/04_transaction_data.sql
docker exec -i mock_database mysql -uroot -proot < nhabe_sql/05_validation_queries.sql
```

## Khởi tạo container mới (nếu chưa có)

```bash
docker run --name nhabe_db -e MYSQL_ROOT_PASSWORD=root -e MYSQL_DATABASE=nhabe_bi_demo \
  -p 3306:3306 -d mysql:8.0 --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
docker exec nhabe_db mysqladmin ping -uroot -proot --wait=30
# rồi nạp 01→05 như trên (đổi mock_database -> nhabe_db)
```

## Reset

```bash
docker exec -i mock_database mysql -uroot -proot -e \
  "DROP DATABASE IF EXISTS nhabe_bi_demo; CREATE DATABASE nhabe_bi_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

## Số liệu

| Bảng | Rows |
|---|---|
| dim_calendar | 546 |
| dim_sales_team | 6 |
| dim_customer | 30 |
| dim_product_category | 10 |
| dim_factory | 15 |
| fact_pnl | 2.628 |
| fact_gcn | 314 |
| fact_sample_cost | 1.189 |
| fact_customer_yearly | 90 |
| _meta_* | 4 bảng metadata |

## 6 Demo scenarios (neo số — verify bằng 05_validation_queries.sql)

| # | Câu hỏi | Neo số |
|---|---|---|
| Q1 | Tổng quan 6T/2026 | DT **1.270 tỷ** · gộp **11,2%** · net **3,4% (~43 tỷ)** |
| Q2 | Team nào net thấp nhất | **Sale 5 ~1,7%** (thấp nhất) dù DT cao |
| Q3 | Khách ăn mòn lợi nhuận | **MANGO** DT 135 tỷ nhưng net **1,5%**; nhóm rui_ro net **~ -9 tỷ** |
| Q3b | Khách lỗ nhiều năm | **BESTSELLER** lỗ 3 năm: 2024 -3,2 · 2025 -3,5 · 2026H1 -1,16 tỷ |
| Q4 | Đơn GCN nguy cơ lỗ | 4 đơn âm biên (nhà máy `xa`), tổng **~ -2,8 tỷ** |
| Q5 | Team may mẫu phình | **Sale 6 ~1,8 tỷ** (cao nhất, ~3× Sale 1); order-rate thấp nhất |
| Q6 | Goal-seek net 3,4%→5% | Gap **~20,5 tỷ** = cắt lỗ rủi ro (+9) + tái ĐP khách <2% (+6) + siết GCN (+2,8) + cắt may mẫu (+1,2) |

## Lưu ý cho người kết nối AI engine
- Metadata tables `_meta_tables/_meta_columns/_meta_kpi/_meta_glossary` là nguồn truth cho AI.
- Data range 2025-01 → 2026-06; "hiện tại" = 30/06/2026; tỷ giá 26.000 VND/USD.
- `fact_pnl` grain = tháng×team×khách×hình thức → coi chừng nhân đôi khi JOIN khác grain.
- `fact_gcn` chỉ là tập con đơn GCN, KHÔNG cộng `fob_revenue_vnd` vào `revenue_vnd`.
- Mock data — không phản ánh số thật của May Nhà Bè.
