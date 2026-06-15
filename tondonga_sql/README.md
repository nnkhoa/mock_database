# tondonga_demo — Mock data TÔN ĐÔNG Á (GDA)

Bộ dữ liệu mô phỏng **18 tháng** (2024-01 .. 2025-06)
cho demo AI-for-BI (CEO Tôn Đông Á). Tổng quan ngành tôn mạ midstream: Revenue = sản lượng × ASP,
biên mỏng, nhạy với giá HRC.

> Sinh bởi `generate_data.py` (Python stdlib, seed cố định -> tái lập 100%). KHÔNG cần Docker để sinh data;
> các file SQL dưới đây dùng để nạp vào MySQL khi cần.

## Files
| File | Nội dung |
|------|----------|
| `01_ddl_schema.sql` | CREATE DATABASE + tables (dim_/fact_/_meta_) + indexes + COMMENT |
| `02_metadata.sql` | _meta_tables / _meta_columns / _meta_kpi / _meta_glossary (tiếng Việt) |
| `03_master_data.sql` | dimension tables (calendar, region, channel, product, customer, hrc_price, target) |
| `04_transaction_data.sql` | fact_sales + fact_cogs (249,994 dòng mỗi bảng, batch 1000) |
| `05_validation_queries.sql` | query kiểm tra + dry-run 6 scenarios |
| `VALIDATION_REPORT.txt` | báo cáo validation (magnitude, YoY, margin, Pareto, integrity) |

## Nạp vào MySQL (Docker) — khi cần
```bash
docker run --name mock_database -e MYSQL_ROOT_PASSWORD=root -e MYSQL_DATABASE=tondonga_demo \
  -p 3306:3306 -d mysql:8.0 --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
docker exec mock_database mysqladmin ping -uroot -proot --wait=30
for f in 01_ddl_schema 02_metadata 03_master_data 04_transaction_data; do
  docker exec -i mock_database mysql -uroot -proot < tondonga_sql/$f.sql
done
docker exec -i mock_database mysql -uroot -proot tondonga_demo < tondonga_sql/05_validation_queries.sql
```
Reset: `DROP DATABASE IF EXISTS tondonga_demo; CREATE DATABASE tondonga_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;`

## Đặc tả & anomaly có chủ đích
- **S1 Tổng quan/YoY:** quý gần nhất (Q2/2025) ~199k tấn / ~5.000 tỷ; DT YoY > SL YoY (ASP cải thiện).
- **S2 Kênh×Vùng:** Nội địa +~24% DT, Xuất khẩu -~6%; Nam +25%, Bắc +23%, **Trung âm (~-7%)**; **XK EU ~-21%**.
- **S3/S6 Margin & HRC:** gross margin ~11.6% -> 3 tháng cuối ~10.3% (HRC +7%, giá bán +3% — lag). HRC ~70% COGS.
- **S4 Cao cấp hoá:** Tôn màu +~30% (mix ~19%->23%), thép hộp giảm nhẹ.
- **S5 Kế hoạch:** dim_target theo tháng (780.000 tấn / 18.000 tỷ) cho projection + seasonality.

## Lưu ý cho AI engine (MCP)
- Luôn dùng `fact_sales.net_revenue_vnd` cho doanh thu (đã gồm chiết khấu).
- `fact_cogs` 1-1 `fact_sales` qua `sale_id`; `hrc_cost_vnd` đã nằm trong `total_cogs_vnd`.
- `dim_hrc_price`/`dim_target` join theo chuỗi 'YYYY-MM' (LEFT JOIN). KHÔNG SUM giá đơn vị HRC.
- Metadata tables (_meta_*) là nguồn mô tả schema bằng tiếng Việt.
- Known limitations: data mock (số phân rã là ước lượng theo benchmark ngành); phản ánh 2 nhà máy hiện hữu,
  chưa gồm Nhà máy 4 (vận hành 2026).
