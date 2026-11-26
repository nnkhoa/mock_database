# `tht_textile_demo` — Dệt Trần Hiệp Thành (THT Textile Corp) | Dệt nhuộm vải

Database mock cho demo AI-for-BI. Người dùng demo là Tổng Giám đốc THT, trình bày với HĐQT.
AI engine (Open WebUI + LLM) kết nối MySQL qua MCP ở chế độ READ-ONLY. AI nhận câu hỏi tiếng Việt, tự viết SQL, rồi trả lời kèm phân tích và biểu đồ.

| | |
|---|---|
| Phạm vi dữ liệu | **01/01/2025 → 31/10/2026** (22 tháng). "Hiện tại" = 31/10/2026 |
| Đơn mở | Ngày cam kết xuất xưởng đến 03/2027. Có một ít đơn đặt từ 10–12/2024 (backlog đầu kỳ) |
| Forecast | Snapshot 15/10/2026, cho 11/2026 – 03/2027 |
| Kế hoạch | Chỉ có `KH_2026` |
| Tên thật | THT / Trần Hiệp Thành, địa danh |
| Tên giả định | Toàn bộ brand, xưởng may, nhà cung cấp hóa chất |
| Schema | 26 bảng nghiệp vụ và 4 bảng metadata, **khớp y hệt [database-schema.md](database-schema.md)** về tên, thứ tự cột, kiểu, PK, FK và NULL. Đã kiểm tra bằng `tht_scripts/verify_schema.py` |
| Kết quả kiểm tra | **191/203 PASS**, toàn bộ kiểm tra kỹ thuật PASS. Chi tiết trong [validation_report.txt](validation_report.txt) |
| Seed | `20261126`. Chạy lại `tht_scripts/run_all.sh` cho ra kết quả y hệt |

## 1. Nạp dữ liệu

Nếu container `mock_database` đang chạy: `./populate.sh tht` (chạy từ thư mục gốc repo).

Làm từ đầu với container mới:

```bash
# 1. Khởi tạo MySQL container
docker run --name mock_database \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=tht_textile_demo \
  -p 3306:3306 \
  -d mysql:8.0 \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_unicode_ci

# 2. Chờ MySQL sẵn sàng
docker exec mock_database mysqladmin ping -uroot -proot --wait=30

# 3. Populate data theo thứ tự
docker exec -i mock_database mysql -uroot -proot --default-character-set=utf8mb4 < tht_sql/01_ddl_schema.sql
docker exec -i mock_database mysql -uroot -proot --default-character-set=utf8mb4 < tht_sql/02_metadata.sql
docker exec -i mock_database mysql -uroot -proot --default-character-set=utf8mb4 < tht_sql/03_master_data.sql
docker exec -i mock_database mysql -uroot -proot --default-character-set=utf8mb4 < tht_sql/04_transaction_data.sql

# 4. Verify
docker exec -i mock_database mysql -uroot -proot --default-character-set=utf8mb4 < tht_sql/05_validation_queries.sql

# 5. Reset (nếu cần làm lại)
docker exec -i mock_database mysql -uroot -proot -e \
  "DROP DATABASE IF EXISTS tht_textile_demo; CREATE DATABASE tht_textile_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
# Rồi chạy lại bước 3-4
```

## 2. Các file

| File | Nội dung |
|---|---|
| `01_ddl_schema.sql` | CREATE DATABASE, 30 bảng, FK, index, COMMENT |
| `02_metadata.sql` | `_meta_tables` (30), `_meta_columns` (258), `_meta_kpi` (32), `_meta_glossary` (49) |
| `03_master_data.sql` | 8 bảng dim: lịch 1.095 ngày, 6 nhóm vải, 4 dây chuyền nhuộm, 72 máy/nhóm máy, 180 mã vải, 33 brand, 32 khách hàng, 8 nhà cung cấp |
| `04_transaction_data.sql` | 18 bảng fact (~40 MB): ~35K dòng đơn, ~52K dòng hóa đơn, ~85K mẻ nhuộm, ~43K yêu cầu báo giá, ~4,4K mẫu phát triển, ~6,6K lab dip… |
| `05_validation_queries.sql` | Kiểm tra kỹ thuật và dry-run S1–S5, fallback |
| `validation_report.txt` | Báo cáo PASS/FAIL so với mốc C0 của brief |

## 3. Lưu ý cho người kết nối AI engine

- Đọc metadata (`_meta_*`) và `database-schema.md`, nhất là phần JOIN WARNINGS.
- **Doanh thu thuần = hóa đơn − khiếu nại.** Nguồn chuẩn cấp công ty là `fact_pnl_monthly`.
- Hai bảng snapshot: `fact_brand_forecasts` (lọc `forecast_snapshot_date = '2026-10-15'`) và `fact_ar_snapshots` (lọc một `snapshot_date`).
- `fact_dye_batches`: chỉ cộng `attempt_no = 1` khi tính số mét đã nhuộm. Có ~1% mẻ hàng tồn/mẫu với `order_line_id` NULL. Mẻ nhuộm bắt đầu từ 01/01/2025, nên các đơn giao đầu tháng 1/2025 không có mẻ tương ứng.
- `fact_developments` có mẫu yêu cầu từ 10/2024. Đây là nguồn của các đơn mới giao đầu 2025.

## 4. Khác biệt so với brief

| Hạng mục | Brief | Thực tế | Lý do |
|---|---|---|---|
| Cột `fact_brand_forecasts` | DDL đặt `forecast_confidence` cuối bảng | Theo đúng database-schema.md (sau `period_month`) | Yêu cầu schema giống hệt md |
| Biên gộp theo nhóm vải | Bảng C0.2 | Mỗi nhóm +0,5 điểm | Để biên toàn công ty sau khiếu nại và LNST khớp C0.3 (đã báo ở checkpoint 1) |
| Cỡ dòng đơn | Median PB 9.000 m… | × 0,65 | Để có ~1.400–1.700 dòng đơn/tháng |
| Cỡ mẻ nhuộm | Median PB 6.500 m… | ~1.000–3.900 m theo nhóm × dây chuyền | Để mức sử dụng nhuộm khớp C0.5 và mốc S3 (đã chốt ở checkpoint 1) |
| 'Đã có PO' trong forecast | 45–60% T11–T12 | = sổ đơn tại 15/10 | Đã chốt ở checkpoint 1 |
| RFT toàn nhà máy T7–T10 | ~83% | ~86–87% | Riêng DL3 × Acid × Đậm/Đen (~70%) chỉ kéo RFT toàn nhà máy xuống ~2 điểm; các DL khác giữ 86–90% theo brief |
| Pareto mã vải | top 20% ≈ 70–75% mét | ~87% | Đơn mới gom theo chương trình mẫu dồn vào mã chủ lực |
| Nordvik chuyển đổi mẫu 5–8/2026 | ~22% | ~29% (48% trước đó) | Số yêu cầu mẫu tháng 5–7 tăng lên 33–38 để giữ xu hướng; tháng 8 còn ~15 |
| Đơn nhận 10T tăng trưởng | +9% ±2 | ~+14% | Đặt hàng sớm cho mùa SS và đơn mở dài hạn (cần cho đơn mở T11–T12 ~428 tỷ) |
| Sản lượng nhuộm T8–T10 | ~6,4 tr m/tháng | ~6,9 tr m/tháng | Gồm hao hụt nhuộm 2–4% và nhuộm trước cho đơn T11 |
| Giá USD/m 2026 so với 2025 | PB, NY, KN thấp hơn 0,5–1% | Thấp hơn ~3% | Giữ đúng giá VND/m ở C0.2, vì tỷ giá tăng ~2,3% |

## 5. Sinh lại dữ liệu

`tht_scripts/run_all.sh` chạy lần lượt các bước: master → targets → sales_orders → ops → calibrate → devs → finance → write_sql → nạp DB → verify_schema → validate. Tham số vận hành đã hiệu chỉnh nằm trong `tht_scripts/ops_tune.json`. Chạy `tune_ops.py` nếu cần hiệu chỉnh lại.
