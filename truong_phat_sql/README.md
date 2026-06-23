# truong_phat_sql — Database `wood_export_demo` (CTCP Gỗ Trường Phát, hypothetical)

Demo **AI-for-BI** cho ngành chế biến gỗ xuất khẩu Việt Nam. Database MySQL 8.0
(utf8mb4) mô phỏng 24 tháng dữ liệu (2024-06-01 → 2026-05-31), "hiện tại" = cuối 5/2026.

## Nội dung

| File | Mô tả |
|------|-------|
| `01_ddl_schema.sql` | DROP/CREATE DATABASE, CREATE TABLE, index, FK, COMMENT |
| `02_metadata.sql`   | `_meta_tables`, `_meta_columns`, `_meta_kpi`, `_meta_glossary` |
| `03_master_data.sql`| Dimension: calendar, market, customer (24), product (40), factory, fx |
| `04_transaction_data.sql` | `fact_sales` (41,444 dòng) + `fact_production` (192 dòng), batch ≤1000 |
| `05_validation_queries.sql` | Query kiểm tra + dry-run 6 demo scenarios |

## Reproduce vào Docker container mới

```bash
# 1. Khởi tạo MySQL container
docker run --name mock_database \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=wood_export_demo \
  -p 3306:3306 \
  -d mysql:8.0 \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_unicode_ci

# 2. Chờ MySQL sẵn sàng
docker exec mock_database mysqladmin ping -uroot -proot --wait=30

# 3. Populate (theo thứ tự). Các file đã tự `SET NAMES utf8mb4` nên nạp đúng tiếng Việt
#    kể cả khi client mặc định latin1; flag dưới là belt-and-suspenders.
docker exec -i mock_database mysql -uroot -proot --default-character-set=utf8mb4 < 01_ddl_schema.sql
docker exec -i mock_database mysql -uroot -proot --default-character-set=utf8mb4 < 02_metadata.sql
docker exec -i mock_database mysql -uroot -proot --default-character-set=utf8mb4 < 03_master_data.sql
docker exec -i mock_database mysql -uroot -proot --default-character-set=utf8mb4 < 04_transaction_data.sql

# 4. Verify
docker exec -i mock_database mysql -uroot -proot --default-character-set=utf8mb4 < 05_validation_queries.sql

# 5. Reset (nếu cần)
docker exec -i mock_database mysql -uroot -proot -e \
  "DROP DATABASE IF EXISTS wood_export_demo; CREATE DATABASE wood_export_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

`01_ddl_schema.sql` đã tự `DROP DATABASE IF EXISTS` + `CREATE DATABASE` + `USE`,
nên có thể chạy lại sạch sẽ bất cứ lúc nào.

## Lưu ý cho người kết nối AI engine (MCP)

- **Metadata = nguồn truth**: AI nên đọc `_meta_tables` / `_meta_columns` / `_meta_kpi`
  / `_meta_glossary` để hiểu schema, đơn vị (đều VND), và công thức KPI.
- **Data range**: 2024-06 → 2026-05 (24 tháng) — đủ cho trend ≥6 tháng & YoY.
- **Luôn dùng** `net_revenue_vnd` cho doanh thu; biên gộp =
  `SUM(gross_profit_vnd)/SUM(net_revenue_vnd)` (KHÔNG average dòng lẻ).
- **fact_production là snapshot tháng**: lấy "hiện tại" bằng `month >= '2026-03-01'`
  rồi `AVG(utilization_pct)`, KHÔNG SUM nhiều tháng.
- **dim_fx_monthly** join theo tháng: `DATE_FORMAT(order_date,'%Y-%m-01') = month`.
- **Exposure thuế** cần đủ 2 điều kiện: `is_section232_affected=1 AND market_name='Mỹ'`.

## Known limitations / simplifications

- `fact_production` ở grain factory × month × **category mà nhà máy thực sự sản xuất**
  (mỗi nhà máy 1–2 category) → ~192 dòng, thay vì ước lượng thô ~864 trong brief.
  units_produced được mô hình hóa để đạt đúng utilization mục tiêu (BĐ2 ~94%, BD3 ~71%),
  định hướng khớp công suất bán ra chứ không khớp tuyệt đối từng đơn.
- Mix khách × category lấy theo mix thị trường (proportional) để giữ đúng cả tỷ trọng
  khách lẫn tỷ trọng category; riêng anomaly Westwood được tăng giảm mạnh hơn ở
  sofa + tủ bếp cho drill-down.
