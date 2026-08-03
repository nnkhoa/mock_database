# ACSV — `acsv_aircargo_demo` | Bộ dữ liệu demo BI Nhà ga Hàng hóa Hàng không

Dữ liệu mô phỏng cho **CTCP Dịch vụ Hàng hóa Hàng không Việt Nam (ACSV)** — nhà khai thác nhà ga
hàng hóa tại Cảng HKQT Nội Bài. Phạm vi **2025-01-01 → 2026-06-30** (18 tháng, 546 ngày).
MySQL 8.0, charset `utf8mb4` / collation `utf8mb4_unicode_ci`.

## Nội dung thư mục

| File | Mô tả |
|---|---|
| `01_ddl_schema.sql` | CREATE DATABASE, 19 bảng, index, FK, COMMENT (VI) từng bảng & cột |
| `02_metadata.sql` | Nạp `_meta_tables`, `_meta_columns`, `_meta_kpi`, `_meta_glossary` (nguồn truth cho AI engine) |
| `03_master_data.sql` | Master data: dim_calendar (546), dim_airlines (18), dim_agents (120), dim_stations (42), dim_commodities (14), dim_services (12), dim_zones (5), dim_contracts (22) |
| `04_transaction_data.sql` | Fact data: shipments (~310K), service_charges (~1,1M), flights (~43K), service_level (9.828), zone_utilization (2.730), monthly_financials (162), leasing_revenue (108) |
| `05_validation_queries.sql` | Kiểm tra toàn vẹn kỹ thuật + thống kê + dry-run 6 demo scenario + fallback |
| `database-schema.md` | Tài liệu schema tham chiếu cho AI engine (SQL templates, join warnings, đơn vị, sanity check) |
| `generate.py` | Script sinh 03 + 04 (deterministic, seed cố định) |
| `gen_metadata.py` | Script sinh 02 từ information_schema |

## Populate vào Docker container mới

```bash
# 1. Khởi tạo MySQL container
docker run --name mock_database \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=acsv_aircargo_demo \
  -p 3306:3306 \
  -d mysql:8.0 \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_unicode_ci

# 2. Chờ MySQL sẵn sàng
docker exec mock_database mysqladmin ping -uroot -proot --wait=30

# 3. Populate data theo thứ tự
docker exec -i mock_database mysql -uroot -proot < acsv_sql/01_ddl_schema.sql
docker exec -i mock_database mysql -uroot -proot < acsv_sql/02_metadata.sql
docker exec -i mock_database mysql -uroot -proot < acsv_sql/03_master_data.sql
docker exec -i mock_database mysql -uroot -proot < acsv_sql/04_transaction_data.sql

# 4. Verify (đối chiếu ngưỡng ghi trong comment mỗi query)
docker exec -i mock_database mysql --default-character-set=utf8mb4 \
  -uroot -proot acsv_aircargo_demo < acsv_sql/05_validation_queries.sql

# 5. Reset (nếu cần làm lại)
docker exec -i mock_database mysql -uroot -proot -e \
  "DROP DATABASE IF EXISTS acsv_aircargo_demo; CREATE DATABASE acsv_aircargo_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
# Rồi chạy lại bước 3-4
```

> Có thể dùng `./populate.sh acsv` từ thư mục gốc repo (đọc `-- Database:` header, chạy 01→04 tự động).
> Riêng `02_metadata.sql` cần chạy thủ công (populate.sh chỉ chạy 01/03/04).

## Sinh lại data từ đầu (Python 3.10+, numpy, pandas, mysql-connector-python)

```bash
cd acsv_sql
python generate.py --stats     # build in-memory, in báo cáo validation (không ghi file)
python generate.py --write     # ghi 03_master_data.sql + 04_transaction_data.sql
python gen_metadata.py          # sinh 02_metadata.sql từ DB đã nạp 01+03+04
```
Seed cố định (`SEED = 20260630`) → tái lập 100%.

## Mô hình doanh thu

```
total_revenue_vnd = thc_revenue_vnd + ancillary_revenue_vnd          (trên fact_shipments)
Doanh thu toàn công ty = SUM(fact_shipments.total_revenue_vnd)
                       + SUM(fact_leasing_revenue.monthly_rent_vnd)
```
- **THC** = Terminal Handling Charge (đ/kg theo mã IATA × chiều, ×0,55 nếu nội địa, trừ chiết khấu hợp đồng).
- **Phụ trợ** = lưu kho, soi chiếu, ULD build-up/break-down, xử lý đặc biệt, hành chính — chiếm ~52-53% doanh thu.
- `ancillary_revenue_vnd = SUM(fact_service_charges.amount_vnd)`; `amount_vnd = 0` khi `is_waived = 1`.

## 6 Demo scenario (đã dry-run PASS trong 05)

| # | Câu hỏi | Điểm nhấn |
|---|---|---|
| S1 | Bức tranh 6T/2026 vs 6T/2025 | Sản lượng **+13,8%** nhưng doanh thu chỉ **+9,0%**, yield **−4,2%** — AI tự flag nghịch lý |
| S2 | Cơ cấu doanh thu theo thị trường | Bắc Mỹ yield ~3.815 đ/kg vs Đông Bắc Á ~1.484 đ/kg; tăng trưởng đến từ thị trường yield thấp |
| S3 ⭐ | Yield giảm dù sản lượng tăng hai chữ số | Tách **hiệu ứng mix thị trường ≈ −113 đ/kg** (chính) + Cargolux tái đàm phán THC 6%→14% (phụ) |
| S4 | Churn hãng bay | Hong Kong Air Cargo giảm 5 tháng liên tiếp (T6 ≈ 60% mức T1); OTD rớt 96,5%→87,2%, khiếu nại đỉnh T11-T12 |
| S5 ⭐ | Doanh thu ngoài THC & dư địa | Phụ trợ ~53%; thất thu miễn giảm **~11,5 tỷ/12T**, ~81% thuộc Top-tier |
| S6 | Roadmap công suất | CT2-Tầng 1 quốc tế cạm **~87%** T11/2025; CT1 xuất/nhập đã sát công suất |

## Anomaly cài cắm

- **A** — Dịch chuyển mix thị trường 2025-10→2026-06 (Bắc Mỹ 18%→14%, Đông Bắc Á 34%→40%): nguồn gốc yield erosion.
- **B** — Cargolux đổi hợp đồng THC 6%→14% từ 2026-01-01 (`dim_contracts` 2 dòng) + sản lượng +19%.
- **C** — Hong Kong Air Cargo (RH) churn: OTD giảm, khiếu nại tăng, số chuyến giảm 5→2/tuần.
- **D** — Chênh lệch attach rate & miễn giảm phí theo tier forwarder (`is_own_uld_capable`, `is_waived`).
- **E** — Áp lực công suất mùa cao điểm (`fact_zone_utilization`).

## Lưu ý cho người kết nối AI engine

- Nguồn truth về schema: 4 bảng `_meta_*`. AI query các bảng này để hiểu database.
- Data range: **2025-01-01 → 2026-06-30**; "hiện tại" = 30/06/2026.
- **Known reconciliation:** `ancillary_service_count = COUNT(fact_service_charges)` (giữ toàn vẹn kỹ thuật:
  `ancillary_revenue = SUM(amount_vnd)`). Do các dịch vụ per-kg (soi chiếu X-ray, lưu kho tiêu chuẩn) được
  ghi thành dòng phí riêng cho mọi AWB quốc tế, attach rate tuyệt đối ~3-4 dòng/AWB; **chênh lệch giữa các
  tier (Top-tier < Trung bình < Nhỏ) mới là insight** của scenario S5, cùng với thất thu miễn giảm.
- Xem `database-schema.md` cho SQL templates (T1–T12), join warnings, đơn vị, và mốc sanity check.
```
