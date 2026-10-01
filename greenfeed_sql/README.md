# `greenfeed_feed_demo` — GreenFeed Việt Nam | Bán hàng thức ăn chăn nuôi (Feed)

Database mock cho demo AI-for-BI. Người dùng demo là **Tổng Giám đốc GreenFeed Việt Nam**, dùng để trình bày trước Hội đồng Quản trị.
AI engine (Claude) kết nối MySQL qua MCP, nhận câu hỏi tiếng Việt, tự viết SQL và trả lời kèm insight, biểu đồ.

| | |
|---|---|
| Phạm vi dữ liệu | **01/10/2024 → 30/09/2026** (24 tháng). "Hiện tại" = 30/09/2026. Kế hoạch có đến 12/2026 |
| Phạm vi nghiệp vụ | TACN thành phẩm bán ra ngoài tại Việt Nam qua 2 kênh: đại lý cấp 1 và trang trại mua trực tiếp |
| Không bao gồm | Cám cấp cho trang trại nội bộ, mảng Farm, mảng Food (G Kitchen), thị trường Lào/Campuchia/Myanmar, dữ liệu đối thủ |
| Tiền / khối lượng | VND trước thuế GTGT; kg (báo cáo tấn = kg/1000) |
| Schema | 15 bảng nghiệp vụ + 4 bảng metadata, **khớp y hệt [database-schema.md](database-schema.md)** (tên, thứ tự cột, kiểu dữ liệu, PK, FK — kiểm bằng `verify_schema.py`) |

---

## 1. Nạp dữ liệu

### Nhanh nhất — container `mock_database` đang chạy

```bash
./populate.sh greenfeed        # chạy từ thư mục gốc repo; tự xóa và tạo lại database
```

### Từ đầu — container mới

```bash
# 1. Khởi tạo MySQL container
docker run --name mock_database \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=greenfeed_feed_demo \
  -p 3306:3306 \
  -d mysql:8.0 \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_unicode_ci

# 2. Chờ MySQL sẵn sàng
docker exec mock_database mysqladmin ping -uroot -proot --wait=30

# 3. Populate data theo thứ tự
docker exec -i mock_database mysql -uroot -proot < greenfeed_sql/01_ddl_schema.sql
docker exec -i mock_database mysql -uroot -proot < greenfeed_sql/02_metadata.sql
docker exec -i mock_database mysql -uroot -proot < greenfeed_sql/03_master_data.sql
docker exec -i mock_database mysql -uroot -proot < greenfeed_sql/04_transaction_data.sql

# 4. Verify
docker exec -i mock_database mysql -uroot -proot < greenfeed_sql/05_validation_queries.sql

# 5. Reset (nếu cần làm lại)
docker exec -i mock_database mysql -uroot -proot -e \
  "DROP DATABASE IF EXISTS greenfeed_feed_demo; CREATE DATABASE greenfeed_feed_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
# Rồi chạy lại bước 3-4
```

Nạp 4 file mất khoảng 10 giây. File 04 nặng 46 MB.

## 2. Các file

| File | Dung lượng | Nội dung |
|---|---|---|
| `01_ddl_schema.sql` | 18 KB | CREATE DATABASE, 19 CREATE TABLE, FK, index, COMMENT cho mọi bảng và cột |
| `02_metadata.sql` | 29 KB | `_meta_tables` (15), `_meta_columns` (118), `_meta_kpi` (19), `_meta_glossary` (28) |
| `03_master_data.sql` | 0,7 MB | 8 bảng `dim_*` |
| `04_transaction_data.sql` | 46 MB | `fact_*` và `ext_*`; INSERT theo lô ≤ 1.000 dòng; `sales_line_id` do AUTO_INCREMENT cấp |
| `05_validation_queries.sql` | 13 KB | 9 query kiểm tra kỹ thuật, dry-run 6 scenario, 3 câu fallback; danh sách 38 đại lý nhóm A đã thay bằng id thực |
| `validation_report.txt` | 14 KB | Report Phase D: 101 check, mỗi check PASS/FAIL kèm số thực tế |
| `dryrun_output.txt` | 14 KB | Kết quả chạy các query dry-run S1–S6, F1–F3 |
| `database-schema.md` | 30 KB | Tài liệu schema cho AI engine (nguồn chuẩn) |

## 3. Số dòng

| Bảng | Dòng | Bảng | Dòng |
|---|---:|---|---:|
| dim_dates | 822 | fact_sales_lines | 349.228 |
| dim_regions | 4 | fact_list_prices | 166 |
| dim_areas | 11 | fact_product_costs | 1.992 |
| dim_provinces | 23 | fact_ar_snapshots | 62.338 |
| dim_plants | 6 | fact_sales_targets | 792 |
| dim_products | 83 | ext_live_hog_prices | 420 |
| dim_sales_reps | 160 | ext_raw_material_prices | 120 |
| dim_customers | 2.881 | _meta_* | 15 / 118 / 19 / 28 |

`fact_sales_lines` gồm 168.051 hóa đơn, trung bình 2,1 dòng mỗi hóa đơn. Bảng đã được thu gọn so với brief (1,2–1,6 triệu dòng) để file 04 nhỏ hơn 50 MB; xem mục 7.

## 4. Mốc tổng thể (năm 2025)

- Sản lượng **1.300.003 tấn**; doanh thu thuần **16.171 tỷ** (bình quân 1.348 tỷ/tháng); giá thực **12.439 đ/kg**; biên lãi gộp **11,9%**.
- Tỷ trọng sản lượng theo vùng: MB 29% · MTTN 16% · ĐNB 23% · MT 32%.
- Theo nhóm vật nuôi: Heo 57,2% · Gia cầm 29,9% · Thủy sản 13,0%. Kênh đại lý chiếm 73,1%.
- Top 20% SKU (17/83) chiếm 77,0% sản lượng.
- Q4/2024: 352.992 tấn. Q4/2025: 380.387 tấn.

## 5. Sáu demo scenario — số thực tế trong data (dùng cho Demo Briefing)

| # | Câu hỏi | Số thực tế |
|---|---|---|
| S1 | Bán hàng 9 tháng 2026 so với kế hoạch và cùng kỳ | Sản lượng 975.848 tấn, **+6,1%** so với 9T/2025; doanh thu thuần +6,7%; **đạt 97,6% kế hoạch 9 tháng**. Theo vùng: MB +11,0% · MTTN +18,0% · ĐNB +1,2% · MT −0,5% |
| S2 | Vì sao thức ăn heo miền Tây giảm | Thức ăn heo MT Q3/2026 **−10,0%** so với cùng kỳ (9T: −2,5%). **38 đại lý** ở Đồng Tháp, Vĩnh Long, Cần Thơ (22,5% sản lượng heo MT) giải thích ~95% mức giảm; sản lượng heo tháng 9 của nhóm này chỉ bằng **48,9%** tháng 3. Các khách heo MT khác giảm ~2%. Giá heo hơi MT: 68.980 (03/2026) → **58.825 đ/kg** (09/2026). Nợ quá hạn >30 ngày của nhóm: **2,1 tỷ** (31/03) → **63,7 tỷ** (30/09); DSO 35 → 110 ngày; **6 đại lý vượt hạn mức** tại 31/08 và 30/09 |
| S3 | Miền Bắc tăng trưởng có chất lượng không | Sản lượng 9T **+11,0%**, doanh thu thuần +9,5%. Chiết khấu đặc biệt/doanh thu gộp: **2,07%** (2025) → **5,61%** (Q2–Q3/2026). **25 đại lý** ở Hưng Yên, Ninh Bình, Hải Phòng, Bắc Ninh nhận **47,5%** tổng chiết khấu đặc biệt; các đại lý khác cùng 4 tỉnh giảm nhập 1,6%. Giá thực heo thịt GreenFeed Q3/2026 thấp hơn Q4/2025 **471 đ/kg**. **Lãi gộp MB Q2–Q3/2026 chỉ +0,5%**, trong khi MTTN +54%, ĐNB +30%, MT +24% |
| S4 | Điểm sáng | MTTN 9T **+18,0%**, Q3 **+23,0%**. **62 trang trại mới** (16 bắt đầu năm 2025, 46 năm 2026) ở Gia Lai, Đắk Lắk, Lâm Đồng; tháng 9/2026 mua 3.851 tấn, 40% là G.TEK. Tỷ trọng G.TEK trong heo MTTN: **9,5%** (6T/2025) → **19,2%** (Q3/2026). Tỷ lệ xuất từ nhà máy Đồng Nai: **8,9% → 22,8%**; vận chuyển bình quân 245 → **287 đ/kg** |
| S5 | What-if tăng giá 200 đ/kg từ tháng 10 | Lần tăng **+300 đ/kg ngày 01/06/2025** (58 SKU heo, gia cầm) có trong `fact_list_prices`. Sau lần tăng: kênh trang trại giảm ~8%, kênh đại lý ~3% trong tháng 6–7/2025, hồi phục từ tháng 9. Độ nhạy: trang trại ~−2,7%/100 đ, đại lý ~−1%/100 đ. Giá vốn chuẩn heo thịt tháng 9/2026 cao hơn tháng 6/2026 **2,4%** |
| S6 | Q4 phải bù bao nhiêu để đạt kế hoạch năm | Kế hoạch 2026: **1.413.493 tấn**; thực hiện 9T: 975.848 tấn → Q4 cần **437.646 tấn**. Theo nhịp Q4/2025 (380.387 tấn) cộng tăng trưởng nền 6,1% thì Q4 dự kiến đạt 403.646 tấn → **thiếu ~34.000 tấn** |

Fallback đã kiểm:
- Thủy sản đạt đỉnh tháng 5–7, đáy tháng 12–2.
- Khách hàng lớn nhất ĐNB chỉ chiếm 2,8% sản lượng vùng.
- BLU là nhà máy xuất nhiều nhất (309k tấn năm 2025); không nhà máy nào vượt công suất thiết kế.
- Không có ô vùng × nhóm vật nuôi × tháng nào bị trống.

## 6. Lưu ý cho người kết nối AI engine

- Metadata nằm trong `_meta_tables`, `_meta_columns`, `_meta_kpi` (công thức SQL chuẩn) và `_meta_glossary`. Gửi kèm `database-schema.md` (có SQL template và JOIN warning) vào system prompt.
- "Hiện tại" = 30/09/2026. Không dùng `CURDATE()`. Năm 2024 chỉ có Q4. Tết lệch tháng: 29/01/2025 và 17/02/2026.
- `fact_ar_snapshots` là snapshot: không SUM qua nhiều `snapshot_date`.
- Kế hoạch chỉ có ở cấp **tháng × khu vực × nhóm vật nuôi**, không có theo khách hàng, SKU, kênh hay nhà máy.
- Vùng của doanh số là vùng của khách hàng (`dim_customers.region_id`), không phải vùng đặt nhà máy.
- Toàn bộ tên khách hàng, NVKD, mã SKU là dữ liệu minh họa (mock).

## 7. Khác biệt so với brief gốc

Schema **không đổi tên hay kiểu** bất kỳ bảng, cột nào. Chỉ bổ sung COMMENT cho các cột A.3 còn thiếu, `ENGINE=InnoDB`, và 2 index phụ: `dim_dates(calendar_month)`, `dim_customers(region_id, customer_type)`.

Một số mốc calibration trong brief mâu thuẫn nhau. Hướng xử lý đã được duyệt ở Checkpoint 2 và 3:

1. **Giá nguyên liệu 2026 (phương án B).** Bảng C.9 gốc làm giá vốn 2026 thấp hơn 2025 khoảng 6,5%, khiến lãi gộp mọi vùng tăng 35–50% và phá anomaly B. Đã nâng mặt bằng giá 2026 lên ×1,06 từ tháng 3 (tăng dần qua tháng 1–2), tháng 8/2026 ×0,995; giữ nguyên hình dạng đường giá. Giá 2024–2025 giữ nguyên.
2. **Hai mốc doanh thu không đạt.**
   - Doanh thu 9T toàn công ty +6,7%, tức *cao hơn* sản lượng 0,6 điểm (brief: thấp hơn 1–2 điểm).
   - Doanh thu MB 9T +9,5% (brief: +5,5% đến +7,5%).
   - Nguyên nhân: lần tăng giá 300 đ/kg từ 06/2025 làm giá niêm yết tháng 1–5/2026 cao hơn cùng kỳ. Không thể sửa mà không phá mốc giá thực heo thịt (−450 đến −550 đ/kg).
3. **Trần xuất bán của nhà máy GLA** là 14.500 tấn/tháng (brief: 17.000). Với 17.000, tỷ lệ xuất từ DNA ở Q3/2026 chỉ khoảng 10%.
4. **Gán nhà máy (B.4)** chỉnh để VLG không vượt công suất và BLU là nhà máy lớn nhất:
   - Đồng Tháp: heo, gia cầm 100% từ BLU (brief: 50/50)
   - Cần Thơ: heo, gia cầm 50/50 BLU/VLG (brief: 100% VLG)
   - Thủy sản Miền Tây: 60/40 BLU/VLG (brief: 40/60)
5. **Chiết khấu đặc biệt MB từ 04/2026:** đại lý ngoài nhóm B ~4,2% (brief ~3,5%); nhóm B 11,5–12%. Mức này cần để tỷ lệ toàn MB đạt 5,5–6,0% và giá thực heo thịt giảm 450–550 đ/kg.
6. **Nhóm A:**
   - Hệ số giảm tháng 7/8/9-2026 là 0,63/0,53/0,44 (brief: 0,67/0,58/0,50), để sản lượng heo tháng 9 ≈ 50% tháng 3. Tháng 3 bị cửa sổ "Sau Tết" kéo thấp.
   - Với hóa đơn từ 06/2026: trung vị trễ thanh toán ×1,5 (25% không trả, đúng brief), để nợ quá hạn >30 ngày đạt ~65 tỷ.
7. **Tăng trưởng nền sau calibrate:** MB +4,6%, MTTN +1,5%, ĐNB +0,4%, MT −0,9%. Phần tăng trưởng còn lại đến từ khách hàng mới và từ việc 2025 bị kéo thấp bởi phản ứng tăng giá. Mặt bằng Q4/2024 ×0,946 để đạt 345–360k tấn.
8. **Công nợ nền:** 4% hóa đơn trễ nặng 35–90 ngày (brief: 3%, 35–80 ngày) để tỷ lệ quá hạn >30 ngày đạt 3–5%.
9. **Hạn mức tín dụng** = max(1,5 × doanh thu thuần tháng bình quân; 1,1 × dư nợ đỉnh), làm tròn lên 100 triệu. Nhờ vậy chỉ đúng 6 đại lý nhóm A vượt hạn mức, và chỉ tại 31/08 và 30/09/2026.
10. **Kế hoạch 2025** = sản lượng kỳ vọng không biến động × 0,9925, để 2025 đạt 100,75%.
11. **Thu gọn fact_sales_lines** (yêu cầu sau Phase E: file 04 < 50 MB), còn 349 nghìn dòng thay vì 1,2–1,6 triệu:
    - Mỗi khách hàng mua 2–8 SKU ưa dùng (brief: 4–12).
    - Số hóa đơn/tháng giảm khoảng một nửa: Kim cương 4–6, Vàng 3–4, Bạc 2–3, Tiêu chuẩn 1–2; trang trại 2–6.
    - Tổng sản lượng, doanh thu và mọi anomaly được calibrate lại và vẫn đạt mốc.
    - Để giữ cơ cấu giá và Pareto: SKU ưa dùng chọn theo `zipf^1,6 × tỷ trọng dòng^0,8`; tỷ trọng giữa các SKU trong dòng theo `zipf^2,4`.

## 8. Sinh lại dữ liệu

Script nằm ở `greenfeed_scripts/` (Python 3.12, numpy, lunarcalendar; seed 2026, chạy lại ra đúng bộ dữ liệu):

```bash
cd greenfeed_scripts
python3.12 gen_master.py          # Phase B: dim_* → 03, anomaly_groups.json
python3.12 gen_facts.py --load    # Phase C: calibrate + hóa đơn + công nợ → 04, cập nhật 03, nạp 01–04
python3.12 gen_metadata.py        # 02_metadata.sql (lấy COMMENT từ DB đã nạp)
python3.12 validate.py            # Phase D: validation_report.txt
python3.12 dryrun.py              # dryrun_output.txt + 05_validation_queries.sql
```

`model.py` chứa mô hình sản lượng theo khách hàng × SKU × tháng và vòng calibrate; `econ.py` chứa giá, chiết khấu, giá vốn và logic tràn công suất GLA→DNA. Danh sách id của 3 nhóm anomaly lưu ở `greenfeed_scripts/anomaly_groups.json` (không export vào SQL).
