# tondonga_demo — dữ liệu mẫu Tôn Đông Á (lĩnh vực Doanh thu)

Phạm vi 01/2024 – 09/2026 (33 tháng). Tháng gần nhất: 09/2026.
Cấu trúc: `fact_sales`, 5 bảng chiều (`dim_date`, `dim_product`, `dim_customer`, `dim_market`, `dim_org`),
7 danh mục chuẩn (`m_*`) và 4 bảng `_meta_*`.

Sinh bởi `generate_data.py` (Python chuẩn, seed cố định, chạy lại ra cùng bộ số).

| File | Nội dung |
|---|---|
| `01_ddl_schema.sql` | Tạo database, xoá bảng cũ, tạo bảng mới |
| `02_metadata.sql` | Mô tả bảng, trường, chỉ số, thuật ngữ |
| `03_master_data.sql` | Danh mục chuẩn và bảng chiều |
| `04_transaction_data.sql` | `fact_sales` |
| `05_validation_queries.sql` | SQL cho 18 câu UAT, 4 câu theo công ty thành viên, kiểm tra toàn vẹn |
| `VALIDATION_REPORT.txt` | Kết quả đối chiếu với số mục tiêu |

## Nạp vào MySQL 8.0 (Docker)

```bash
docker run --name mock_database -e MYSQL_ROOT_PASSWORD=root -e MYSQL_DATABASE=tondonga_demo \
  -p 3306:3306 -d mysql:8.0 --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
docker exec mock_database mysqladmin ping -uroot -proot --wait=30
for f in 01_ddl_schema 02_metadata 03_master_data 04_transaction_data; do
  docker exec -i mock_database mysql -uroot -proot --default-character-set=utf8mb4 < tondonga_sql/$f.sql
done
docker exec -i mock_database mysql -uroot -proot --default-character-set=utf8mb4 --table < tondonga_sql/05_validation_queries.sql
```

Container đã có sẵn thì bỏ lệnh `docker run`; `01_ddl_schema.sql` tự xoá các bảng của bản cũ trong `tondonga_demo`.
Nếu repo có `populate.sh` thì chạy `./populate.sh tondonga` thay cho vòng lặp trên.

## Quy ước khi truy vấn

- Số toàn nhóm: lọc `dim_customer.is_internal = 0`. Giao dịch nội bộ là công ty mẹ bán cho công ty thành viên.
- Kênh bán hàng lấy từ `dim_customer.channel_group`.
- Các trường giá trị là VND; `quantity_base` là tấn; `currency` là loại tiền của chứng từ gốc.
- `m_region` là danh mục tham chiếu, không nối với `fact_sales`.
