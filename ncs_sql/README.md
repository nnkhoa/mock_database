# NCS — Suất Ăn Hàng không Nội Bài | Mock BI Database

Bộ dữ liệu demo cho **Công ty Cổ phần Suất Ăn Hàng không Nội Bài (NCS, UPCoM: NCS)**,
phục vụ demo BI hỏi–đáp tiếng Việt qua AI engine (Claude) kết nối MySQL bằng MCP.

- **Database:** `ncs_catering_demo` (MySQL 8.0, `utf8mb4_unicode_ci`)
- **Phạm vi dữ liệu:** 01/01/2025 → 30/06/2026 (18 tháng, 546 ngày). **"Hiện tại" = cuối ngày 30/06/2026.**
- **Quy mô:** 22 bảng · ~222.000 bản ghi · `fact_meal_uplift` 215.619 dòng
- **Grain trung tâm:** 1 chuyến bay × 1 hạng ghế × 1 loại suất ăn — **không phải** giao dịch POS.

---

## 1. Populate vào container mới

```bash
# 1. Khởi tạo MySQL container
docker run --name mock_database \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=ncs_catering_demo \
  -p 3306:3306 \
  -d mysql:8.0 \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_unicode_ci

# 2. Chờ MySQL sẵn sàng
docker exec mock_database mysqladmin ping -uroot -proot --wait=30

# 3. Populate theo đúng thứ tự
docker exec -i mock_database mysql -uroot -proot < ncs_sql/01_ddl_schema.sql
docker exec -i mock_database mysql -uroot -proot < ncs_sql/02_metadata.sql
docker exec -i mock_database mysql -uroot -proot < ncs_sql/03_master_data.sql
docker exec -i mock_database mysql -uroot -proot < ncs_sql/04_transaction_data.sql

# 4. Verify
docker exec -i mock_database mysql -uroot -proot --default-character-set=utf8mb4 \
  --table < ncs_sql/05_validation_queries.sql

# 5. Reset (nếu cần làm lại)
docker exec -i mock_database mysql -uroot -proot -e \
  "DROP DATABASE IF EXISTS ncs_catering_demo; CREATE DATABASE ncs_catering_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

`01_ddl_schema.sql` đã tự `DROP DATABASE IF EXISTS` nên chạy lại từ đầu là an toàn.
Mỗi file đều bắt đầu bằng `USE ncs_catering_demo;` và chạy độc lập theo thứ tự.

| File | Nội dung | Kích thước |
|---|---|---|
| `01_ddl_schema.sql` | CREATE DATABASE, 22 CREATE TABLE, index, COMMENT từng bảng/cột | 28 KB |
| `02_metadata.sql` | `_meta_tables`, `_meta_columns` (181 cột), `_meta_kpi` (16), `_meta_glossary` (20) | 49 KB |
| `03_master_data.sql` | 9 bảng dimension | 71 KB |
| `04_transaction_data.sql` | 9 bảng fact, batch INSERT 1000 dòng/statement | 19 MB |
| `05_validation_queries.sql` | Technical / Statistical / Demo scenario / Fallback dry-run | 22 KB |
| `database-schema.md` | Đặc tả schema — **nguồn chuẩn**, DDL khớp y hệt tài liệu này | 34 KB |

---

## 2. Ba đặc thù nghiệp vụ phải giữ đúng khi đọc dữ liệu

1. **Order ≠ Produced ≠ Uplift.** Hãng đặt (`meals_ordered`), NCS sản xuất dư phòng
   (`meals_produced`), số thực giao lên tàu bay (`meals_uplifted`) thấp hơn do đổi tải,
   hủy chuyến, giảm khách phút chót. Phần chênh là **hao hụt mất trắng** — suất ăn tươi
   shelf-life 4–8 giờ, không bán lại được.
   → **Doanh thu tính trên `meals_uplifted`, giá vốn tính trên `meals_produced`.**
2. **Giá bán cố định theo hợp đồng năm, giá NVL biến động hàng tháng.** Đây là nguồn gốc
   bào mòn biên. Cột then chốt: `dim_customers.has_price_escalation`.
3. **Hai mảng biên rất khác nhau:** Hàng không ~12–15%, Phi hàng không ~26–29%.

---

## 3. Sáu kịch bản demo & số liệu thực tế trong database

| # | Câu hỏi | Số chốt (đã verify trên DB) |
|---|---|---|
| 1 | Doanh thu / chi phí / lợi nhuận gộp T6/2026, tách 2 mảng, so kế hoạch | DT **96,5 tỷ** (104,8% KH 92,1 tỷ) · HK 84,2 tỷ biên **12,7%** · Phi HK 12,3 tỷ (**+29,5% KH**) biên 28,3% · LN gộp **14,2 tỷ**, biên **14,7%** vs KH 18,5% |
| 1b | Biên gộp mỏng đi từ tháng nào? | Đường gãy đúng tại **T3/2026**: 17,8 → 17,5 → **16,1** → 15,6 → 15,1 → 14,7 |
| 2 | Hôm nay có chỉ tiêu nào bất thường? (30/06/2026) | Gas/suất **1.180đ** vs nền **834đ** (+41%), lệch ~3,5σ, đã lệch **6 ngày liên tiếp** 25–30/06 (980→1.180). Hao hụt **4,8–4,9%** vs KH 3,7%. Điện/nước bình thường. |
| 2b | Gas tăng ở khu chế biến nào? | **Bếp nóng Á**: gas T6 +**45,0%** so T5 trong khi sản lượng chỉ +7,2% |
| 3 | Bảng điều hành chỉ tiêu trọng yếu T6/2026 | DT 96,5/92,1 🟢 · Sản lượng 911.687/882.990 🟢 · NVL/suất **52.799đ** vs ĐM **50.200đ** 🔴 · Năng lượng 4,14/3,73 tỷ 🟡 · LN gộp 14,2/17,0 🔴 · Biên 14,7% vs 18,5% 🔴 |
| 4 | Doanh thu HK 6 tháng theo hãng → top 5 chặng | VN **61,3%** · KE 7,8% · QR 5,9% · JL 5,1% · SQ 4,4% · HX 3,8% · CZ 3,4% · FD 3,0% · CX 2,4% · AF 1,8%. Top chặng T6: HAN-ICN 9,1 tỷ · HAN-SGN 6,2 · HAN-NRT 5,8 · HAN-SIN 5,6 · HAN-HKG 5,4 |
| 4b | (AI tự phát hiện) | **Hong Kong Airlines**: sản lượng 6T **+14,3%** nhưng doanh thu chỉ **+5,9%** — đơn giá BQ tụt từ 96.877đ xuống 89.810đ do mix hạng ghế C dịch sang Y, hợp đồng **không có trượt giá** |
| 4c | Hãng nào doanh thu/suất cao nhất – thấp nhất? | Qatar Airways **143.728đ** (mix C/F dày) ↔ Thai AirAsia **54.334đ** (LCC) |
| 5 | Bóc tách NVL Q2/2026 theo nhóm và mã | NVL chính 105,8 tỷ vs ĐM 98,8 tỷ (**+7,0%** 🔴) · NVL phụ +0,6% 🟢 · Hàng hóa PVSX +3,5% 🟡. Ba mã chi phối: **Bò thăn +23,4%**, **Cá hồi +14,1%**, **Tôm sú +9,2%** — bắt đầu lệch từ **T3/2026** |
| 5b | Do giá hay do lãng phí? | `quantity_variance_vnd = 0` cho cả 3 mã → **thuần chênh lệch GIÁ**, không phải bếp dùng vượt định mức |
| 6 | ★ Vì sao lợi nhuận thấp hơn kế hoạch? | LN gộp **14,18 tỷ** vs KH **17,02 tỷ** → chênh **−2,84 tỷ**. Profit bridge **đóng khít** (xem DS6b/DS6c trong `05_validation_queries.sql`) |
| 6b | Cần làm gì để về đúng kế hoạch? | Nhóm 3 hãng biên < 10%: **HX 8,6% · CZ 9,3% · FD 9,8%** (tổng ~9,6% doanh thu HK) → ứng viên tái đàm phán đơn giá. Nghẽn khung **20-24h và 00-04h** (util **96,0%**, hao hụt **7,4%** vs 2,9% các khung khác) |

### Profit bridge T6/2026 (dạng phân rã đóng, tổng = đúng mức chênh)

| Yếu tố | Tác động |
|---|---|
| Sản lượng Hàng không vượt kế hoạch | **+2,68 tỷ** |
| Giá bán & cơ cấu hãng bay (mix) | −1,06 tỷ |
| Phi hàng không vượt kế hoạch | **+2,80 tỷ** |
| Chi phí NVL (giá + vượt định mức) | **−5,22 tỷ** |
| Chi phí nhân công & làm thêm giờ | −1,34 tỷ |
| Chi phí năng lượng | −0,42 tỷ |
| Giá vốn khác | −0,28 tỷ |
| **TỔNG** | **−2,84 tỷ** ✔ khớp tuyệt đối |

> Bridge trên tách doanh thu thành **sản lượng** và **giá/mix**, chi phí tách theo khoản mục,
> nên tổng 7 yếu tố **bằng đúng** mức chênh lợi nhuận gộp (check `DS6c` trả về `PASS`).
> Kết luận nghiệp vụ: **hụt lợi nhuận KHÔNG đến từ bán hàng** — sản lượng vượt kế hoạch và
> phi hàng không tăng tốt; toàn bộ mức hụt đến từ **chi phí đầu vào và cơ cấu khách hàng**.

---

## 4. Anomaly đã cài (A1–A7)

| Mã | Nội dung | Nơi quan sát được |
|---|---|---|
| A1 | Hong Kong Airlines: sản lượng +14,3% nhưng doanh thu +5,9%, mix C 14% → 6% | `fact_meal_uplift` (customer_id 6) × `dim_cabin_classes` |
| A2 | China Southern & Thai AirAsia đơn giá cố định → biên 9,3% / 9,8% | `fact_meal_uplift` × `dim_customers.has_price_escalation` |
| A3 | 3 mã NVL vượt giá từ T3/2026 (bò thăn, cá hồi, tôm sú), **chỉ lệch giá** | `fact_material_consumption_monthly.price_variance_vnd` |
| A4 | Sự cố gas Bếp nóng Á 25–30/06/2026, gas/suất 980 → 1.180đ | `fact_daily_operations` + `fact_kitchen_line_monthly` |
| A5 | Nghẽn công suất khung 20-24h & 00-04h từ T4/2026 → hao hụt và OT tăng | `fact_kitchen_capacity_daily` + `fact_meal_uplift.departure_hour` |
| A6 | Điểm gãy biên gộp tại **T3/2026** | `fact_monthly_pnl` |
| A7 | Phi hàng không vượt kế hoạch T4–T6/2026 (+14% / +21% / **+29,5%**) — **yếu tố DƯƠNG** | `fact_non_aviation_sales` |

---

## 5. Kiểm tra chất lượng dữ liệu

Toàn bộ check trong `05_validation_queries.sql` đều **PASS**:

- **T1** toàn vẹn tham chiếu — 0 lỗi trên 10 quan hệ FK
- **T2** ràng buộc `produced ≥ uplifted`, `wasted = produced − uplifted`,
  `revenue = uplifted × unit_price` (sai số < 1đ), `ordered ≤ produced` — 0 lỗi / 215.619 dòng
- **T3** không ngày trống — đủ 546/546 ngày
- **T4 / T4b** miền giá trị & toàn vẹn nội bộ P&L, NVL, phi hàng không — 0 lỗi
- **T5** đối chiếu **3 nguồn doanh thu Hàng không** (`fact_meal_uplift` ↔ `fact_monthly_pnl`
  ↔ `fact_daily_operations`) — **khớp tuyệt đối cả 18 tháng**, lệch 0,0000%
- **T5b** doanh thu Phi hàng không khớp `fact_non_aviation_sales` ↔ `fact_monthly_pnl`
- **S4** DT FY2025 **912 tỷ** (mốc ~897 tỷ, +1,7%) · 6T/2026 **504 tỷ** (mốc ~492 tỷ, +2,5%)
- **DS6c** profit bridge đóng khít: tổng 7 yếu tố = −2,843 tỷ = đúng mức chênh

Đối chiếu schema với tài liệu:

```bash
python3.12 ncs_scripts/verify_schema.py
# → 22/22 bảng, 181/181 cột khớp y hệt database-schema.md (kể cả thứ tự cột)
```

### Bảng đối chiếu 20 chỉ tiêu target T6/2026

| Chỉ tiêu | Target | Thực tế | KQ |
|---|---|---|---|
| Doanh thu tổng | 96,4 tỷ | 96,5 tỷ | PASS |
| — Hàng không | 84,1 tỷ | 84,2 tỷ | PASS |
| — Phi hàng không | 12,3 tỷ | 12,3 tỷ | PASS |
| Giá vốn tổng | 82,2 tỷ | 82,3 tỷ | PASS |
| Lợi nhuận gộp | 14,2 tỷ | 14,2 tỷ | PASS |
| Biên gộp | 14,7% | 14,7% | PASS |
| Kế hoạch doanh thu | 92,1 tỷ | 92,1 tỷ | PASS |
| Kế hoạch biên gộp | 18,5% | 18,5% | PASS |
| Suất giao (uplifted) | 911.200 | 911.687 | PASS |
| Suất sản xuất (produced) | 958.100 | 958.231 | PASS |
| Tỷ lệ hao hụt | 4,9% | 4,9% | PASS |
| NVL/suất thực tế | 52.800đ | 52.799đ | PASS |
| NVL/suất định mức KH | 50.200đ | 50.200đ | PASS |
| Đơn giá BQ thực tế | 92.300đ | 92.334đ | PASS |
| Đơn giá BQ kế hoạch | 93.500đ | 93.500đ | PASS |
| Chi phí năng lượng | 4,1 tỷ | 4,14 tỷ | PASS |
| — trong đó Gas | 1,15 tỷ | 0,86 tỷ | **FAIL** — xem mục 6 |
| Gas/suất ngày 30/06 | 1.180đ | 1.180đ | PASS |
| Gas/suất nền trước sự cố | 830đ | 834đ | PASS |
| Giờ làm thêm (tiền) | 2,4 tỷ | 2,4 tỷ | PASS |

**19/20 PASS.**

---

## 6. Sai lệch có chủ đích so với đặc tả gốc (đã cân nhắc, không phải lỗi)

Một số con số trong đặc tả gốc **mâu thuẫn với nhau về mặt số học**; ở mỗi chỗ đã chọn giữ
con số nào chi phối kịch bản demo và ghi rõ ở đây.

1. **Tổng chi phí gas T6/2026 — 0,86 tỷ thay vì 1,15 tỷ.**
   Đặc tả vừa yêu cầu *gas/suất nền = 830đ* vừa yêu cầu *gas cả tháng = 1,15 tỷ*, trong khi
   sản lượng sản xuất là 958.100 suất → 1,15 tỷ ⇒ **1.200đ/suất**, mâu thuẫn trực tiếp với
   mức nền 830đ. Đã **giữ 830đ/suất** vì đó là con số Scenario 2 dùng để so sánh
   (1.180đ vs 830đ = +42%) — tức là chi tiết tạo ra "wow moment". Hệ quả: gas cả tháng
   0,86 tỷ, và tỷ trọng gas trên doanh thu ~0,9% thay vì 1,2%. Tổng chi phí năng lượng vẫn
   đúng 4,1 tỷ (đã bù bằng điện 2,8% + nước 0,6% doanh thu).

2. **"21 bảng: 9 dimension + 8 fact + 4 metadata" → thực tế 22 bảng (9 + 9 + 4).**
   Phần thân `database-schema.md` liệt kê **đủ 9 bảng fact**, đánh số 10–18; chỉ dòng tiêu đề
   cộng nhầm. Đã tạo đủ 9 bảng fact theo đúng phần thân — **danh sách bảng và toàn bộ 181 cột
   khớp y hệt tài liệu**.

3. **NVL/suất định mức 50.200đ và "NVL chính Q2/2026 vượt 6,8%" là hai gốc so sánh khác nhau.**
   Hai yêu cầu này không thể đồng thời đúng với biên độ anomaly đã cho (đã kiểm chứng bằng
   đại số). Đã tách bạch đúng như thực tế doanh nghiệp:
   - **50.200đ** = định mức **KẾ HOẠCH** (`fact_plan_monthly.plan_material_cost_vnd`) — con số
     trên thẻ KPI của Ban TGĐ ⇒ Scenario 3 hiển thị 52.799đ vs 50.200đ = **+5,2%** ✔
   - **+7,0%** = vượt so với **định mức kỹ thuật từng mã NVL**
     (`fact_material_consumption_monthly.standard_cost_vnd`) ⇒ Scenario 5 ✔

4. **Tỷ lệ hao hụt ngày 30/06 so "TB30 = 3,6%".** Không thể đạt vì chính đặc tả A5 đặt hao hụt
   tháng T4/T5/T6 = 3,85 / 4,35 / **4,90%** — trung bình 30 ngày trước 30/06 tất yếu ≈ 4,7%.
   Đã giữ **đường dốc hao hụt theo A5** (vì nó tạo ra con số −0,6 tỷ trong profit bridge);
   cảnh báo trong Scenario 2 vì vậy nên phát biểu là **4,9% vs KẾ HOẠCH 3,7%**.

5. **Tăng trưởng: 1,0%/tháng trong 2025 và 1,9%/tháng trong 2026** (thay vì 1,4%/tháng đều).
   Cần thiết để đồng thời đạt DT FY2025 ≈ 897 tỷ, 6T/2026 ≈ 492 tỷ và sản lượng T6/2026
   = 911.200 suất. Có căn cứ nghiệp vụ: **Nhà ga T2 mở rộng hoàn thành 19/12/2025**.
   Kết quả: **YoY sản lượng T6/2026 = +19,0%** (mốc +18,2% ✔).
   YoY *doanh thu* cao hơn (+23,3%) do A7 đẩy phi hàng không vượt kế hoạch 29,5%.

6. **Công suất bếp 35.000 suất/ngày là mức 2025**; trong 2026 nâng dần lên 37.500 suất/ngày.
   Không nâng thì sản lượng T6/2026 (31.900 suất/ngày sản xuất) sẽ đẩy mọi khung giờ lên
   >90%, mất khả năng thể hiện "khung đêm nghẽn còn khung ngày 68–82%" của A5.

7. **Top 5 chặng**: thực tế ra HAN-ICN, HAN-SGN, HAN-NRT, HAN-SIN, HAN-HKG (đặc tả kỳ vọng
   ICN, NRT, SGN, DOH, SIN — trùng 4/5). HAN-HKG lọt vào vì **hai hãng cùng khai thác**
   (Hong Kong Airlines + Cathay Pacific), đây là kết quả tự nhiên của cơ cấu khách hàng.

8. **`fact_non_aviation_sales` có 397 dòng** (đặc tả ghi ~420) — hệ quả của việc bảng
   **sparse theo mùa**: bánh trung thu chỉ phát sinh T8–T9, giò chả Tết chỉ T12–T2.

---

## 7. Lưu ý cho người kết nối AI engine

- **Đọc `_meta_*` trước khi sinh SQL.** `_meta_columns` (181 cột, có đơn vị + ví dụ giá trị)
  và `_meta_kpi` (16 công thức chuẩn) là nguồn truth; `_meta_tables.business_context` chứa
  cảnh báo JOIN của từng bảng.
- **11 cảnh báo JOIN** ở cuối `database-schema.md` — đặc biệt:
  - đếm chuyến bay phải `COUNT(DISTINCT CONCAT(flight_date, flight_number))`;
  - `fact_monthly_pnl` × `fact_plan_monthly` phải JOIN **cả hai** khóa;
  - không JOIN `fact_daily_operations` với `fact_meal_uplift` rồi SUM (cộng trùng);
  - `fact_kitchen_capacity_daily` luôn `GROUP BY time_slot`.
- **Biên gộp theo từng hãng bay là số ƯỚC LƯỢNG.** `fact_meal_uplift` chỉ có giá vốn NVL;
  công thức chuẩn trong `_meta_kpi` quy đổi bằng tỷ trọng NVL trong giá vốn mảng Hàng không
  (≈ 0,623). Khi trả lời phải nói rõ đây là phân bổ, không phải số đo trực tiếp.
- **Giới hạn đã biết:** chỉ có lợi nhuận **GỘP** (không có chi phí bán hàng/quản lý/tài chính/
  thuế → không tính được LNST); `fact_material_consumption_monthly` không nối được xuống
  chuyến bay hay hãng (chỉ suy luận gián tiếp qua mix hạng ghế); không mô hình hóa mảng
  vệ sinh máy bay, kho ngoại quan, logistics.
- **Fallback coverage** — data trả lời được nhiều câu ngoài 6 kịch bản: doanh thu theo vùng/
  chặng/hạng ghế/nhóm sản phẩm, mùa vụ trung thu & Tết, tỷ trọng Vietnam Airlines theo tháng,
  sự vụ chất lượng theo hãng và mức độ nghiêm trọng, công suất bếp theo khung giờ ở bất kỳ
  tháng nào, YoY cùng kỳ, giờ làm thêm, chi phí năng lượng theo dây chuyền.

---

## 8. Tái sinh dữ liệu

```bash
python3.12 ncs_scripts/generate.py       # 03 + 04 + báo cáo đối chiếu 20 target
python3.12 ncs_scripts/gen_metadata.py   # 02 (parse cột từ 01_ddl_schema.sql + lấy mẫu từ DB)
python3.12 ncs_scripts/verify_schema.py  # đối chiếu DB thật với database-schema.md
```

Script dùng seed cố định (`SEED = 20260630`) nên kết quả tái lập được.
`generate.py` giải **điểm bất động** cho 4 đại lượng phụ thuộc lẫn nhau — tỷ trọng sản lượng
theo hãng, mức giá chung, mức giá vốn NVL, và hệ số giá riêng của HX/CZ/FD — nên mọi chỉ tiêu
target T6/2026 đạt được đồng thời thay vì phải chỉnh tay.
