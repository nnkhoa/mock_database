# `coteccons_demo` — Coteccons (HOSE: CTD) | Tổng thầu xây dựng

Database mock dùng cho demo AI-for-BI. Người dùng demo là ban lãnh đạo Coteccons.
AI engine kết nối MySQL qua MCP ở chế độ READ-ONLY, nhận câu hỏi tiếng Việt, tự viết SQL rồi trả lời kèm phân tích và biểu đồ.

| | |
|---|---|
| Phạm vi dữ liệu | **01/07/2024 → 30/09/2026** (27 tháng, Q1 NĐTC 2025 → Q1 NĐTC 2027). "Hiện tại" = 30/09/2026 |
| Niên độ | 01/07 – 30/06. NĐTC 2026 = 7/2025–6/2026; NĐTC 2027 = 7/2026–6/2027 |
| Kế hoạch | Chỉ có 2 phiên bản: `KH_NDTC_2026` và `KH_NDTC_2027` |
| Tên thật | Coteccons, Unicons, BU01 |
| Tên giả định | Toàn bộ CĐT, dự án, TVGS, thầu phụ, tổ đội. Không dùng tên sân bay thật |
| Tiền | VND (cột `*_vnd`). Báo cáo tỷ đồng = giá trị / 1e9 |
| Schema | 29 bảng nghiệp vụ và 4 bảng metadata, **khớp y hệt [database-schema.md](database-schema.md)** về tên, thứ tự cột, kiểu, PK và FK (đã kiểm tra bằng `verify_schema.py`) |
| Kết quả kiểm tra | **77/79 PASS** (chi tiết trong [validation_report.txt](validation_report.txt)). Hai mục FAIL là sát ngưỡng, xem mục 6 |
| Seed | `20261112` (sinh lại cho ra kết quả y hệt) |

---

## 1. Nạp dữ liệu

### Cách nhanh nhất (container `mock_database` đang chạy)

```bash
./populate.sh coteccons   # chạy từ thư mục gốc repo; tự xóa và tạo lại database coteccons_demo
```

### Làm từ đầu với container mới

```bash
# 1. Khởi tạo MySQL container
docker run --name mock_database \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=coteccons_demo \
  -p 3306:3306 \
  -d mysql:8.0 \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_unicode_ci

# 2. Chờ MySQL sẵn sàng
docker exec mock_database mysqladmin ping -uroot -proot --wait=30

# 3. Populate data theo thứ tự
docker exec -i mock_database mysql -uroot -proot --default-character-set=utf8mb4 < coteccons_sql/01_ddl_schema.sql
docker exec -i mock_database mysql -uroot -proot --default-character-set=utf8mb4 < coteccons_sql/02_metadata.sql
docker exec -i mock_database mysql -uroot -proot --default-character-set=utf8mb4 < coteccons_sql/03_master_data.sql
docker exec -i mock_database mysql -uroot -proot --default-character-set=utf8mb4 < coteccons_sql/04_transaction_data.sql

# 4. Verify
docker exec -i mock_database mysql -uroot -proot --default-character-set=utf8mb4 < coteccons_sql/05_validation_queries.sql

# 5. Reset (nếu cần làm lại)
docker exec -i mock_database mysql -uroot -proot -e \
  "DROP DATABASE IF EXISTS coteccons_demo; CREATE DATABASE coteccons_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
# Rồi chạy lại bước 3-4
```

Thông tin kết nối: `localhost:3306`, user `root`, mật khẩu `root`, database `coteccons_demo`. Nạp toàn bộ mất vài giây.

## 2. Các file

| File | Dung lượng | Nội dung |
|---|---:|---|
| `01_ddl_schema.sql` | 35 KB | CREATE DATABASE, 33 CREATE TABLE gồm FK, index và COMMENT cho mọi bảng, mọi cột |
| `02_metadata.sql` | 75 KB | `_meta_tables` (33), `_meta_columns` (288), `_meta_kpi` (29), `_meta_glossary` (44) |
| `03_master_data.sql` | 245 KB | 9 bảng `dim_*` |
| `04_transaction_data.sql` | 6,6 MB | 20 bảng `fact_*`, nạp theo thứ tự bảng cha → bảng con |
| `05_validation_queries.sql` | 12 KB | Kiểm tra kỹ thuật, mốc calibration, SQL chạy thử S1–S6 và các câu fallback |
| `validation_report.txt` | 15 KB | Báo cáo Phase D gồm 79 mục, mỗi mục ghi PASS/FAIL kèm giá trị thực tế |
| `database-schema.md` | 63 KB | Tài liệu schema cho AI engine (nguồn chuẩn) |

Quy cách chung:
- Mỗi lệnh INSERT tối đa 1.000 dòng.
- Mã hóa UTF-8.
- Đầu mỗi file có comment mô tả, `SET NAMES utf8mb4;` và `USE coteccons_demo;`.

## 3. Số dòng

| Bảng | Dòng | Bảng | Dòng |
|---|---:|---|---:|
| dim_business_units | 5 | fact_project_monthly | 2.405 |
| dim_segments | 15 | fact_project_costs | 29.450 |
| dim_locations | 25 | fact_project_forecast_snapshots | 2.405 |
| dim_clients | 71 | fact_backlog_snapshots | 2.942 |
| dim_consultants | 22 | fact_payment_applications | 2.581 |
| dim_subcontractors | 134 | fact_receivable_snapshots | 3.269 |
| dim_cost_elements | 12 | fact_project_cashflows_monthly | 3.083 |
| dim_calendar | 2.010 | fact_subcontract_packages | 810 |
| dim_projects | 187 | fact_subcontract_variations | 287 |
| fact_bids | 656 | fact_site_workforce_monthly | 13.806 |
| fact_contract_changes | 923 | fact_site_safety_monthly | 2.398 |
| fact_variation_orders | 616 | fact_input_prices_monthly | 891 |
| fact_project_baseline_plan | 5.656 | fact_corporate_pnl_monthly | 27 |
| fact_plan_segment_monthly | 120 | fact_treasury_monthly | 27 |
| fact_plan_corporate_quarterly | 8 | | |

Trạng thái 187 dự án tại 30/09/2026: 105 đang thi công, 70 đã bàn giao, 9 chưa khởi công, 3 tạm dừng.

## 4. Mốc calibration: mục tiêu và thực tế

**C0.1. Kết quả hợp nhất theo quý** (tỷ VND, %; lấy từ `fact_corporate_pnl_monthly`)

| Quý | DT mục tiêu | DT thực tế | Biên gộp MT | Biên gộp TT | LNST MT | LNST TT |
|---|---:|---:|---:|---:|---:|---:|
| Q1 NĐTC 2025 | 4.644 | 4.644 | 3,29 | 3,26 | 93 | 93,0 |
| Q2 NĐTC 2025 | 6.886 | 6.886 | 2,90 | 2,93 | 106 | 106,0 |
| Q3 NĐTC 2025 | 5.004 | 5.004 | 3,60 | 3,60 | 57 | 57,0 |
| Q4 NĐTC 2025 | 8.351 | 8.351 | 3,70 | 3,73 | 200 | 200,0 |
| Q1 NĐTC 2026 | 7.452 | 7.452 | 4,63 | 4,63 | 293 | 293,0 |
| Q2 NĐTC 2026 | 10.007 | 10.007 | 4,30 | 4,31 | 228 | 228,0 |
| Q3 NĐTC 2026 | 6.409 | 6.409 | 4,49 | 4,49 | 119 | 119,0 |
| Q4 NĐTC 2026 | 10.471 | 10.471 | 4,40 | 4,42 | 148 | 148,0 |
| Q1 NĐTC 2027 | 11.269 | 11.269 | 4,99 | 4,99 | 305 | 305,0 |

Cả năm: NĐTC 2025 DT 24.885, LNST 456. NĐTC 2026 DT 34.339, LNST 788.

| Mốc | Mục tiêu | Thực tế | |
|---|---|---|---|
| C0.2 Tỷ trọng và biên theo mảng | bảng brief, 9 quý | khớp cả 9 quý. Q1 NĐTC 2027: DD 41,5% / 4,88; CN 29% / 6,43; HT 17% / 2,82; ND 9,5% / 4,20; QT 3% / 7,42 | ✅ |
| C0.3 Ký mới theo quý | 6.500 … 14.500 | khớp cả 9 quý. NĐTC 2026 có 70 HĐ, trong đó 48 HĐ của 3 tập đoàn | ✅ |
| C0.4 Backlog | 28.000 / 35.500 / 51.600 / 62.500 / 65.500 / 69.500 / 73.300 | 28.055 / 35.555 / 51.653 / 62.546 / 65.547 / 69.547 / 73.379 | ✅ |
| C0.5 Baseline 10/2026–6/2027 | 28.700 ±3% | 28.799 | ✅ |
| C0.6 Lãi vay NĐTC 2026 / Q1 NĐTC 2027 | 351 / 158 | 351,0 / 158,0 | ✅ |
| C0.6 CP QLDN NĐTC 2026 / Q4 | 676 / 271 | 676,0 / 269,5 | ✅ |
| C0.7 Tiền, vay ngắn hạn, vay dài hạn, lãi suất tại 30/09/2026 | 7.800 / 4.300 / 2.750 / 8,9% | khớp (khớp cả các mốc 6/2025, 9/2025, 6/2026) | ✅ |
| C0.7 LCTT HĐKD Q1 NĐTC 2026 / NĐTC 2026 / Q1 NĐTC 2027 | −838,1 / +815,8 / −774,5 | −838,1 / +815,8 / −774,5 | ✅ |
| C0.8 Phải thu 30/06/2026 (tổng, chưa NT, đã HĐ, giữ lại, dự phòng) | 14.170; 3.120 / 9.400 / 1.650 / 1.400 | 14.089; 3.047 / 9.392 / 1.650 / 1.400 | ✅ |
| C0.8 Phải thu 30/09/2026 | 16.050; 4.650 / 9.650 / 1.750 / 1.400 | 16.151; 4.790 / 9.611 / 1.750 / 1.400 | ✅ (±5%) |
| C0.9 KH_NDTC_2027 (DT / LN gộp / LNST) | 42.000 / 2.055 / 1.050 | 42.000 / 2.055 / 1.050 | ✅ |
| C0.9 KH_NDTC_2026 | 30.000 / 1.290 / 700 | 30.000 / 1.290 / 700 | ✅ |

Nhịp mùa vụ:
- Tháng 2 thấp nhất (Tết), tháng 6 cao nhất mỗi niên độ.
- Q3 là quý thấp nhất của NĐTC 2026.
- Kỹ thuật (11/11 PASS): không có orphan. DT và giá vốn dự án cộng lại bằng P&L hợp nhất, lệch 0 đồng. Chi phí theo hạng mục cộng lại đúng giá vốn dự án. Backlog = HĐ hiện hành − DT lũy kế.

## 5. Kịch bản demo (dry-run)

| | Kết quả | Con số chính |
|---|---|---|
| S1 | ✅ PASS | DT Q1 NĐTC 2027 = 11.269, biên 4,99%. Hạ tầng chiếm 17% DT, gấp 4,3 lần cùng kỳ; biên HT đi từ 6,2 → 5,9 → 5,8 → 4,9 → 2,8% |
| S2 | ✅ PASS | Hai gói sân bay HT-2601 và HT-2504 hụt 58,2 tỷ trên 1.050 tỷ DT, biên 0,46%. Phần vượt chi phí: cọc chờ duyệt 29,0, thép 18,2 (15.880 so với dự toán 14.600 đ/kg), CPC 11,1. 4 VO đề nghị 52 tỷ, đã bỏ chi phí 37 tỷ; thầu phụ đã được duyệt 46 tỷ. EAC còn 3,0% / 3,6%. Backlog HT-2603/05/08 = 7.708 |
| S3 | ⚠️ FAIL sát ngưỡng | Chưa nghiệm thu tăng 3.047 → 4.790; riêng Hải Âu 750 → 1.789. Thời gian ký nghiệm thu từ ~20 ngày (TVGS CS-03) lên 52 ngày (CS-11, hồ sơ nộp tháng 7/2026). Tỷ lệ bị trả 45%, 56% giá trị chưa ký. LCTT HĐKD −774,5 |
| S4 | ✅ PASS | PV còn lại 28.799, theo SPI còn 27.204 (−1.595: miền Bắc −1.066, sân bay −504). Nhân công T9 của 3 dự án miền Bắc đạt 75%. Dự báo NĐTC 2027 ≈ 40.700 (97% KH) |
| S5 | ✅ PASS | Gói nhà máy FDI (CN-NM): tỷ lệ thắng 38% → 18%, markup 6,0 → 7,8%, trượt vì giá 41% → 72%. Pipeline 68.000, trong đó 59.500 có kết quả trước 31/3/2027 |
| S6 | ✅ PASS | Q1: DT 11.269, LNST 305. KH 42.000 / 1.050. Backlog 73.379. HĐ công nghiệp ký Q2 NĐTC 2026 đã ghi nhận 33% DT đến 30/6/2026 (dân dụng 10%) |

**Fallback cho câu hỏi ngoài kịch bản** (đã chạy thử, ra đúng magnitude, không có NULL/0 bất thường):

| Chủ đề | Kết quả mẫu |
|---|---|
| DT và biên theo BU, NĐTC 2026 | BU01 12.454 (5,2%), DD phía Nam 9.931, Unicons 6.551, DD phía Bắc 4.373, Quốc tế 1.030 |
| Vùng và tỉnh | Nam 57%, Bắc 29%, Trung 14%. HCM 27,5%, Hà Nội 14,7% |
| Quốc tế theo quốc gia | Ấn Độ, Campuchia, Đài Loan |
| Theo CĐT và tập đoàn CĐT | Vạn Hưng, Thịnh An Land, Hải Âu và các CĐT FDI, đầu tư công |
| Top dự án | theo DT, theo backlog; dự án sắp bàn giao (`planned_end_date`) |
| An toàn lao động | LTIFR theo quý 0,16–0,28; công nhân bình quân 2026 khoảng 28.600, tháng 2 thấp nhất |
| Giá đầu vào | thép, bê tông, cát, ngày công theo tháng × vùng |
| Phát sinh | theo nguyên nhân (thay đổi thiết kế, yêu cầu CĐT, địa chất…); tỷ lệ duyệt theo giá trị 90% |
| Xu hướng và so sánh | 9 quý; so sánh NĐTC 2025 với 2026 |

## 6. Điểm lệch so với brief (đã báo ở các checkpoint)

Hai mục FAIL trong 79 mục kiểm tra:
1. **S3, chưa nghiệm thu tại 30/09/2026 là 4.790** (mốc 4.650, lệch +3%). Hải Âu chiếm 60% phần tăng (brief ~75%), do DT Hải Âu Q1 cao hơn brief để có đủ khối lượng cho ND-2402 (đã thống nhất ở Checkpoint 2).
2. **Top 10 dự án chiếm 43,4% DT Q1 NĐTC 2027** (brief 30–40%), vì 15 dự án bắt buộc trong brief đều là gói lớn.

Các lệch khác:
- **Tái lập tiến độ từ 10/2026 (phương án A) làm lùi ngày hoàn thành của 71 HĐ.** Mục đích là để baseline 10/2026–6/2027 đạt 28.700. Một số HĐ chạm trần 12/2029, gồm nhóm Hải Âu và HT-2603/05/08. Baseline có tháng tới 3/2030.
- **Doanh thu điều chỉnh giá vật tư chỉ ~84 tỷ** (brief ~400), vì công thức trong brief (thép, bê tông × 80%) chỉ cho ra mức này. Phần còn thiếu trong "thay đổi HĐ khác" được bù bằng VO duyệt, nên từng quý vẫn khớp C0.4.
- **CP tài chính khác Q4 NĐTC 2025 là 99 tỷ** (brief ~50). Cần mức này mới đạt được cùng lúc LNST 200 và CP QLDN −22.
- **Backlog 30/09/2026:**
  - Theo mảng: DD 52%, HT 26%, CN 12,5%, ND 6,5%, QT 3% (brief 44 / 24 / 17 / 10 / 5).
  - Theo tập đoàn: Vạn Hưng 36%, Thịnh An 14%, Hải Âu 10% (brief 26 / 14 / 12).
- **Doanh thu theo vùng:** miền Bắc 28,6% (brief 32%), Đồng Nai 14,7% (brief 4–7%).
- **Mảng ND theo quý** dao động 8,4–10,8%; cả NĐTC 2025 là 9,2% (brief 10%).
- **LCTT HĐKD theo quý:** các quý brief không cho số được tự đặt theo nhịp thu tiền. Tổng NĐTC 2026 vẫn đúng +815,8.
- **Dòng tiền thuần nhóm Hải Âu Q1 NĐTC 2027 là −638** (brief ~−900).

## 7. Lưu ý cho người kết nối AI engine

- **Đọc metadata trước.** Có 4 bảng metadata:
  - `_meta_tables`, `_meta_columns`: mô tả bảng, cột và giá trị mẫu.
  - `_meta_kpi`: 29 KPI kèm công thức SQL.
  - `_meta_glossary`: 44 thuật ngữ, ví dụ SPI, EAC, backlog, nghiệm thu, giữ lại bảo hành.
- **Phạm vi dữ liệu thực tế là 07/2024–09/2026.** "Hiện tại" = 30/09/2026. Niên độ 1/7–30/6: `dim_calendar.fiscal_year` / `fiscal_quarter` theo NĐTC, Q1 = tháng 7–9.
- **Các bảng snapshot cần lọc `snapshot_date`, không cộng dồn qua kỳ:**
  - `fact_backlog_snapshots`
  - `fact_receivable_snapshots`
  - `fact_project_forecast_snapshots`
- **`fact_project_baseline_plan` có tháng tương lai, tới 2030.** Đây là PV kế hoạch dùng cho câu hỏi "giá trị còn phải làm". Các bảng fact thực tế chỉ có dữ liệu tới 9/2026.
- **Kế hoạch chỉ có `KH_NDTC_2026` và `KH_NDTC_2027`** (cột `plan_version` trong `fact_plan_segment_monthly` và `fact_plan_corporate_quarterly`).
- **Đơn vị:**
  - Tiền tính bằng VND; chia 1e9 để ra tỷ đồng.
  - Doanh thu dự án = `fact_project_monthly.revenue_recognized_vnd`.
  - P&L hợp nhất = `fact_corporate_pnl_monthly`. DT và giá vốn ở bảng này bằng đúng tổng các dự án.
- **CP QLDN, lãi vay và thuế chỉ có ở cấp doanh nghiệp,** không phân bổ xuống dự án.

## 8. Sinh lại dữ liệu

Script nằm ở `coteccons_scripts/` (cần Python 3.12, numpy, scipy, lunardate). File `*.py` bị `.gitignore` loại khỏi git nên chỉ có ở máy local.

```bash
cd coteccons_scripts && bash run_all.sh   # mô phỏng → sinh SQL → populate → metadata → verify_schema
python validate.py                          # ghi lại validation_report.txt
```
