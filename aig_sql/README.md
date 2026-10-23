# `aig_demo` — Tập đoàn Nguyên liệu Á Châu (AIG) | Nguyên liệu thực phẩm & Khoa học đời sống

Database mock cho demo AI-for-BI. Người dùng demo là **Tổng Giám đốc AIG**, dùng để trình Hội đồng Quản trị.
AI engine kết nối MySQL qua MCP (READ-ONLY), nhận câu hỏi tiếng Việt, tự viết SQL và trả lời kèm phân tích, biểu đồ.

| | |
|---|---|
| Phạm vi dữ liệu | **01/01/2024 → 30/09/2026** (33 tháng). "Hiện tại" = 30/09/2026 |
| Kế hoạch / dự báo | `KH_2026` T1–T12/2026; `LE_T9_2026` chỉ T10–T12/2026 |
| Đơn vị thành viên | AIG (holding), ACC (phân phối), AFI, ACP, GCF (hợp nhất từ 01/08/2025), AHS, ASI, MDG — tên thật |
| Principal, khách hàng | Tên giả định (không dùng thương hiệu thật) |
| Tiền / khối lượng | VND (trừ cột ghi rõ ngoại tệ); kg (báo cáo tấn = kg/1.000) |
| Schema | 18 bảng nghiệp vụ + 4 bảng metadata, **khớp y hệt [database-schema.md](database-schema.md)** (tên, thứ tự cột, kiểu, PK, FK — kiểm bằng `verify_schema.py`) |
| Kết quả kiểm tra | Validation **52/53 PASS**, chạy thử kịch bản **39/41 PASS** — các mục FAIL đều do mâu thuẫn nội tại của brief, xem mục 7 |

---

## 1. Nạp dữ liệu

### Nhanh nhất — container `mock_database` đang chạy

```bash
./populate.sh aig        # chạy từ thư mục gốc repo; tự xóa và tạo lại database aig_demo
```

### Từ đầu — container mới

```bash
# 1. Khởi tạo MySQL container
docker run --name mock_database \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=aig_demo \
  -p 3306:3306 \
  -d mysql:8.0 \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_unicode_ci

# 2. Chờ MySQL sẵn sàng
docker exec mock_database mysqladmin ping -uroot -proot --wait=30

# 3. Populate data theo thứ tự
docker exec -i mock_database mysql -uroot -proot < aig_sql/01_ddl_schema.sql
docker exec -i mock_database mysql -uroot -proot < aig_sql/02_metadata.sql
docker exec -i mock_database mysql -uroot -proot < aig_sql/03_master_data.sql
docker exec -i mock_database mysql -uroot -proot < aig_sql/04_a_fact_sales_2024.sql
docker exec -i mock_database mysql -uroot -proot < aig_sql/04_b_fact_sales_2025.sql
docker exec -i mock_database mysql -uroot -proot < aig_sql/04_c_fact_sales_2026.sql
docker exec -i mock_database mysql -uroot -proot < aig_sql/04_d_fact_other.sql

# 4. Verify
docker exec -i mock_database mysql -uroot -proot < aig_sql/05_validation_queries.sql

# 5. Reset (nếu cần làm lại)
docker exec -i mock_database mysql -uroot -proot -e \
  "DROP DATABASE IF EXISTS aig_demo; CREATE DATABASE aig_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
# Rồi chạy lại bước 3-4
```

Nạp toàn bộ mất khoảng 10–15 giây. File 04 được tách thành 4 phần (mỗi phần < 100 MB để đẩy được lên GitHub);
tên dạng `04_a_…` để `populate.sh` (mẫu `0{1,2,3,4}_*.sql`) nhận đủ và chạy đúng thứ tự. Các file 04 độc lập với nhau.

## 2. Các file

| File | Dung lượng | Nội dung |
|---|---|---|
| `01_ddl_schema.sql` | 24 KB | CREATE DATABASE, 22 CREATE TABLE, FK, index, COMMENT cho mọi bảng và cột |
| `02_metadata.sql` | 38 KB | `_meta_tables` (18), `_meta_columns` (195), `_meta_kpi` (19), `_meta_glossary` (33) — không nhắc tới anomaly |
| `03_master_data.sql` | 0,2 MB | 7 bảng `dim_*` |
| `04_a_fact_sales_2024.sql` | 30 MB | `fact_sales` năm 2024 |
| `04_b_fact_sales_2025.sql` | 33 MB | `fact_sales` năm 2025 |
| `04_c_fact_sales_2026.sql` | 26 MB | `fact_sales` T1–T9/2026 |
| `04_d_fact_other.sql` | 16 MB | 10 bảng fact còn lại |
| `05_validation_queries.sql` | 15 KB | Kiểm tra kỹ thuật, mốc calibration, SQL chạy thử S1–S6, câu fallback |
| `validation_report.txt` | 8 KB | Report Phase D: 53 check, mỗi check PASS/FAIL kèm giá trị thực tế |
| `dryrun_output.txt` | 14 KB | Kết quả chạy các SQL kịch bản demo |
| `database-schema.md` | 33 KB | Tài liệu schema cho AI engine (nguồn chuẩn) |

INSERT theo lô ≤ 1.000 dòng/lệnh; UTF-8; mỗi file có comment đầu và `USE aig_demo;`.

## 3. Số dòng

| Bảng | Dòng | Bảng | Dòng |
|---|---:|---|---:|
| dim_calendar | 1.096 | fact_sales | 437.773 |
| dim_entities | 8 | fact_purchases | 24.343 |
| dim_export_markets | 8 | fact_inventory_snapshots | 80.785 |
| dim_principals | 12 | fact_receivable_snapshots | 17.176 |
| dim_warehouses | 10 | fact_production | 977 |
| dim_customers | 475 | fact_commodity_prices | 864 |
| dim_products | 383 | fact_pnl_monthly | 245 |
| fact_export_contracts | 59 | fact_plan_monthly | 120 |
| fact_contract_terms | 588 | fact_le_assumptions | 10 |

## 4. Mốc calibration — mục tiêu vs thực tế

**Doanh thu thuần, biên gộp trước dự phòng, LNST theo quý** (tỷ VND, %; từ `fact_pnl_monthly`)

| Quý | DT mục tiêu | DT thực tế | Biên ACC | Biên ACP | Biên SX khác | Biên TĐ trước DP | Biên TĐ báo cáo | LNST mục tiêu | LNST thực tế |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Q1/2024 | 2.780 | 2.780 | 12,1 | 30,4 | 23,3 | 16,34 | 16,18 | 205 | 205,0 |
| Q2/2024 | 2.997 | 2.997 | 12,1 | 30,2 | 23,1 | 16,28 | 16,30 | 227 | 227,0 |
| Q3/2024 | 3.114 | 3.114 | 11,6 | 29,8 | 22,9 | 15,84 | 15,76 | 203 | 203,0 |
| Q4/2024 | 3.495 | 3.495 | 11,4 | 29,6 | 22,7 | 15,58 | 15,54 | 207 | 207,0 |
| Q1/2025 | 3.392 | 3.392 | 11,8 | 26,2 | 23,1 | 15,66 | 15,56 | 263 | 263,0 |
| Q2/2025 | 3.622 | 3.622 | 11,3 | 22,0 | 24,1 | 15,06 | 15,02 | 237 | 237,0 |
| Q3/2025 | 4.105 | 4.105 | 11,6 | 22,0 | 28,7 | 16,29 | 16,28 | 270 | 270,0 |
| Q4/2025 | 4.340 | 4.340 | 11,4 | 22,8 | 29,8 | 16,58 | 16,50 | 289 | 289,0 |
| Q1/2026 | 3.984 | 3.984 | 12,2 | 36,0 | 31,0 | 19,13 | 19,09 | 398 | 398,0 |
| Q2/2026 | 4.237 | 4.237 | 12,4 | 38,0 | 31,5 | 19,81 | 19,76 | 446 | 446,0 |
| Q3/2026 | 4.280 | 4.280 | 10,2 | 10,0 | 29,0 | 14,13 | 13,01 | 172 | 172,0 |

Tổng năm: DT 2024 = 12.386, 2025 = 15.459; LNST 842 / 1.059 / 9T/2026 1.016. Biên gộp tất cả các quý trong ±0,3 điểm so với bảng C0.

| Mốc | Mục tiêu | Thực tế |
|---|---|---|
| 6T/2026 doanh thu / LNST / biên gộp báo cáo | 8.221 / 844 / 19,5% | 8.221 / 844,0 / 19,44% |
| 6T/2026 xuất khẩu (ACP/GCF/AFI/AHS/ASI/MDG) | 1.724 (850/350/210/130/95/89) | 1.724 (850/350/210/130/95/89) |
| Xuất khẩu 2024 / 2025 / 6T/2025 | ~2.050 / ~2.600 / ~1.157 | 2.074 / 2.647 / 1.108 |
| Dự phòng HTK ACC | 6–10 tỷ/năm; T8/2026 18, T9/2026 30 | 2024 7,6; 2025 8,4; T8 18,0; T9 30,0 |
| KH_2026 | DT 16.800, LNST 1.260 (quý 280/300/330/350) | khớp |
| LE_T9_2026 (Q4) | DT 4.480; LN gộp trước DP ~637; DP 15 (T11); LNST 209 | 4.480 / 637 / 15 / 209 |
| LNST cả năm theo LE | 1.225 (hụt ~35) | 1.225,0 |
| Pareto SKU ACC | top 20% ≈ 78–82% | 79,3% |
| DSO ACC / nhà máy nội địa / xuất khẩu | 50–55 / 35–45 / 35–50 | 50,5 / 41,0 / 48,9 |
| Tuổi nợ ACC (chưa hạn / 1–30 / 31–60 / >60) | 75–80 / 12–15 / 5–7 / 2–3 | 74,6 / 15,4 / 6,9 / 3,1 |
| DIO ACC BQ / nhà máy / tập đoàn 30/09/2026 | 65–80 / 45–60 / ~70–75 | 79 / 57 / 70 |
| Thuế TNDN hiệu dụng | 20,5–21,5% | 21,0% mọi quý |

## 5. Kịch bản demo — kết quả chạy thử

| Kịch bản | Điểm then chốt trong dữ liệu |
|---|---|
| **S1** Bức tranh 9 tháng | DT 9T/2026 12.501 tỷ (74,4% KH, +12,4%); LNST 1.016 (80,6% KH, +31,9%). Q3/2026 LNST 172 (−36,3% YoY) dù DT +4,3%; biên gộp báo cáo Q3 13,0% (Q2 19,8%). ACP biên 38% → 10%; ACC trước DP 12,4% → 10,2%, trích lập 48 tỷ. Giá dừa T9 17.600 đ/trái (×3,9 đáy T3, +27% đỉnh 2025); ~78% sản lượng XK ACP Q3 chạy HĐ giá cố định ký Q2/2026 |
| **S2** Chất lượng lợi nhuận (A1) | 18 HĐ ACP ký T4–T6/2026 với 12 nhà nhập khẩu US/EU/JP/KR, không điều khoản điều chỉnh giá, giá FOB thấp hơn HĐ 2025 cùng sản phẩm ~8–9%, kết thúc 30/11/2026–30/06/2027. Biên ACP T7 21,5% / T8 8,5% / T9 0,0%. Sản lượng ACP Q3/2026 +6,2%, DT ±0%. GC Food biên 40,0% → 37,5%. Đơn giá dừa trong `fact_production` bám giá thị trường |
| **S3** Tăng trưởng mua bằng biên và tiền (A2) | KH-ACC-0007 CTCP Sữa Đồng Xanh: hạng 1 DT Q3/2026 (~200 tỷ, +18,6%); sản lượng T4 +15%, T5 +20%, T6–T9 +25–28%; biên 2025 11,6% → T4–T9/2026 7,4%, trừ chi phí vốn còn 5,5%; dư nợ 31/03 → 30/09 +99 tỷ; DSO ~45 → ~80. `fact_contract_terms` 2 dòng: 45 ngày/2,5% → 75 ngày/7,0%, duyệt 25/03/2026 bởi Giám đốc Ngành hàng Sữa – ACC. KH-ACC-0012/0019: DSO +11/+13 ngày từ T6/2026, không có điều khoản mới |
| **S4** Tồn kho cận date (A3) | Dòng đầu: Bột sữa gầy SMP / Nordvik Dairy / WH-BD — tồn 118 tỷ, cận date 66 tỷ, dự phòng 48 tỷ. 6 lô `ND-SMP-2602-01…ND-SMP-2603-03`, ~3.300 tấn, hạn 20/11/2026–31/01/2027; còn 2.008 tấn tại 30/09 (1.121 tấn hết hạn trước 31/12). DIO nhóm SMP 53 → 119 ngày. Khách Bánh kẹo mua SMP T4–T9 −17% YoY; SMP Nordvik bán ~160 tấn/tháng; xả hàng T8–T9 CK 8–12%. Tổng tồn kho tập đoàn 30/09 chỉ +4,7% so với 30/06 |
| **S5** What-if | LE Q4 LNST 209; 10 giả định trong `fact_le_assumptions` (dừa 16.400, USD 26.950, tỷ trọng dừa trong giá vốn ACP 0,55…); giá vốn ACP Q4 LE 475 tỷ × 55% × 7,3% ≈ 19 tỷ |
| **S6** Goal-seek | Cả năm theo LE 1.225 vs KH 1.260; 7 khách mua SMP ≥ 20 tấn/tháng (ứng viên giải phóng lô Nordvik) |

## 6. Ghi chú cho người kết nối AI engine

- Đọc `_meta_tables`, `_meta_columns`, `_meta_kpi`, `_meta_glossary` và `database-schema.md` (có SQL template T1–T8, 13 cảnh báo JOIN).
- "Hiện tại" = **30/09/2026**. LE chỉ có T10–T12/2026 → ước tính cả năm = thực hiện T1–T9 (`fact_pnl_monthly`) + LE.
- `fact_inventory_snapshots`, `fact_receivable_snapshots` là **snapshot cuối tháng** — luôn lọc một `snapshot_date`.
- Biên gộp báo cáo (sau dự phòng HTK) chỉ có ở `fact_pnl_monthly`; `fact_sales.gross_profit_vnd` là trước dự phòng.
- Công nợ gồm VAT 8% (khách nội địa); DSO nhiều khách = `SUM(closing_balance)/SUM(revenue_last_90d)*90`.
- Entity AIG doanh thu = 0; GCF chỉ có số từ 08/2025.
- Giá dừa tính VND/trái; `fact_purchases.quantity` của dừa đơn vị trái.

## 7. Khác biệt so với brief

Các mục dưới đã trao đổi ở 3 checkpoint; dữ liệu giữ trung thực với các mốc neo (doanh thu, biên, LNST).

1. **Giá bán SMP** suy từ giá vốn (SMP_GLOBAL + premium 3–8% + phí nhập 6–9%): ~85–90k đ/kg năm 2025, ~75–80k đ/kg 2026 (brief ghi 68–75k sẽ bán lỗ). *(checkpoint 1)*
2. **Lô SMP Nordvik (A3)** giữ mốc giá trị: 118 / 66 / 48 tỷ; số tấn còn lại ~2.008 / ~1.121 (brief ~1.870 / ~1.050). Ngày sản xuất lùi về T11/2024–T1/2025 để hạn dùng = SX + 24 tháng (brief ghi SX T3–T5/2025). Tổng nhập ~3.300 tấn (brief ~3.000). *(checkpoint 1–2)*
3. **Biên "Sản xuất khác"** đạt C0 (29–31,5% từ Q3/2025) nên biên từng đơn vị cao hơn khoảng tham khảo: AFI 23–32% (có dòng Creamer cao cấp từ 07/2025), AHS 16–19%, ASI 34–37,5%, MDG 22–27%. Q2/2025 dùng 24,1% và Q3/2025 28,7% (trong ±0,3).
4. **Q1/2025**: LNST 263 buộc chi phí hoạt động + tài chính thuần chỉ ~5,6% DT → thêm thu nhập khác một lần 19 tỷ (AIG, T2/2025) và biên gộp nâng +0,25 điểm (trong dung sai) để tổng chi phí đạt 6,3%.
5. **Xuất khẩu 2025** ~2.647 (brief ~2.600; tỷ lệ xuất khẩu từng đơn vị 2025 = 0,89 × tỷ lệ 2026).
6. **ACP**: định mức bình quân ~2,2 trái/kg (brief ~2,6) để chi phí chế biến không dao động quá ±20% khi ép biên C0; giá bán ACP cao hơn khung tham khảo ~6%.
7. **Westmoor Dairy** có thêm SMP (SMP03–05) để DIO nhóm SMP đạt ~55 → ~118 ngày (nếu chỉ có SMP Nordvik ~160 tấn/tháng thì DIO 30/09 ~350 ngày).
8. **S2 — tách biên +4,15 điểm**: theo cách tính thô, cơ cấu & hợp nhất GC Food +1,1, giá đầu vào ròng +3,7, giá bán/hiệu quả −0,6 → ~88% do yếu tố thị trường (brief ~55–60%). Nguyên nhân: mốc biên ACP Q1–Q2/2026 (36/38%) trong khi giá dừa giảm ~55% buộc chi phí chế biến ACP tăng ~15–20%. Giữ nguyên theo quyết định checkpoint 3.
9. **A2 — lộ trình DSO**: T4 50, T5 56, T6–T9 76/75/79/84 (brief ~55/~65/~75–78); dư nợ +99 tỷ. Giữ nguyên theo checkpoint 3.
10. **Magnitude DT ACC/tháng**: 525–1.011 tỷ — 3 tháng T2 (Tết) dưới 650 do hệ số mùa vụ T2 = 0,70 của chính brief.
11. **MDG** hiệu suất BQ ~44% (công suất 900 tấn/tháng nhưng doanh thu MDG 2026 giảm theo bảng C0).
12. Biên ACC theo tháng Q3/2026 đặt T7 11,4% → T8 10,0% → T9 9,3%; Q3/2026 ACC siết tồn các nhóm hàng khác ~10% để tổng tồn kho 30/09 chỉ tăng nhẹ so với 30/06.
13. `fact_purchases` có các lô tồn đầu kỳ nhập T12/2023 (để mọi lô trong `fact_inventory_snapshots` đều có phiếu nhập); ngành Ngũ cốc của AFI dùng mã nguyên liệu `NGU_COC`.

## 8. Tái tạo dữ liệu

Script nằm ở `aig_scripts/` (Python 3.12, numpy, pandas; `*.py` không đưa lên git theo `.gitignore`). Seed cố định `20261023`.

```bash
cd aig_scripts
./run_all.sh            # metadata → master → sales/định giá → nhà máy → lắp ráp fact → ghi SQL → nạp vào mock_database
python3.12 verify_schema.py   # so khớp schema với database-schema.md
python3.12 validate.py        # report Phase D
python3.12 dryrun.py          # chạy thử S1–S6 + fallback
```
