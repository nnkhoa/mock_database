# `dabaco_demo` — CTCP Tập đoàn Dabaco Việt Nam (DBC)

Mock BI database cho demo AI-for-BI: chuỗi khép kín **3F+ (Feed – Farm – Food – Future)**.
Phạm vi dữ liệu **01/01/2025 → 30/06/2026** (18 tháng · 546 ngày · 78 tuần ISO).
"Hiện tại" trong mọi kịch bản = cuối ngày **30/06/2026**.

Schema trong thư mục này **khớp y hệt `database-schema.md`** (kèm bên cạnh): đúng 22 bảng
nghiệp vụ với đúng tên cột, đúng kiểu, đúng thứ tự cột, đúng ràng buộc NULL — cộng 4 bảng
metadata. Có script kiểm chứng tự động: `dabaco_scripts/verify_schema.py`.

---

## 1. Nạp dữ liệu

### Cách nhanh nhất (container `mock_database` đang chạy)

```bash
./populate.sh dabaco          # chạy từ thư mục gốc của repo, ~25 giây
```

### Từ đầu, container mới

```bash
# 1. Khởi tạo MySQL container
docker run --name mock_database \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=dabaco_demo \
  -p 3306:3306 \
  -d mysql:8.0 \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_unicode_ci

# 2. Chờ MySQL sẵn sàng
docker exec mock_database mysqladmin ping -uroot -proot --wait=30

# 3. Populate theo thứ tự
docker exec -i mock_database mysql -uroot -proot < dabaco_sql/01_ddl_schema.sql
docker exec -i mock_database mysql -uroot -proot < dabaco_sql/02_metadata.sql
docker exec -i mock_database mysql -uroot -proot < dabaco_sql/03_master_data.sql
docker exec -i mock_database mysql -uroot -proot < dabaco_sql/04_transaction_data.sql

# 4. Verify
docker exec -i mock_database mysql --default-character-set=utf8mb4 -uroot -proot \
  < dabaco_sql/05_validation_queries.sql

# 5. Reset (nếu cần làm lại)
docker exec -i mock_database mysql -uroot -proot -e \
  "DROP DATABASE IF EXISTS dabaco_demo; CREATE DATABASE dabaco_demo \
   CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

`01_ddl_schema.sql` tự `DROP DATABASE IF EXISTS` rồi tạo lại, nên chạy lại từ đầu luôn sạch.

### Files

| File | Dung lượng | Nội dung |
|---|---:|---|
| `01_ddl_schema.sql` | 37 KB | CREATE DATABASE + 26 CREATE TABLE + index + COMMENT từng bảng, từng cột |
| `02_metadata.sql` | 61 KB | `_meta_tables` (26) · `_meta_columns` (245) · `_meta_kpi` (19) · `_meta_glossary` (33) |
| `03_master_data.sql` | 457 KB | 12 bảng dimension |
| `04_transaction_data.sql` | 160 MB | 10 bảng fact (~1,46 triệu dòng) |
| `05_validation_queries.sql` | 27 KB | Query kiểm chứng: ràng buộc neo · kỹ thuật · thống kê · dry-run 6 scenario · fallback |
| `database-schema.md` | 39 KB | Tài liệu schema — nguồn truth, bản gốc không sửa |

> Tổng `04` là 160 MB (< ngưỡng 200 MB) nên giữ **một file duy nhất** thay vì tách
> `04a/04b/04c`. Repo dùng git-lfs cho `*.sql`.

---

## 2. Bảng và số dòng thực tế

**12 DIMENSION**

| Bảng | Rows | | Bảng | Rows |
|---|---:|---|---|---:|
| `dim_calendar` | 546 | | `dim_feed_mill` | 6 |
| `dim_week` | 78 | | `dim_product` | 180 |
| `dim_segment` | 12 | | `dim_customer` | 850 |
| `dim_company` | 24 | | `dim_channel` | 8 |
| `dim_region` | 12 | | `dim_material` | 22 |
| `dim_farm` | 68 | | `dim_herd_batch` | 2.487 |

**10 FACT**

| Bảng | Rows | Grain |
|---|---:|---|
| `fact_sales` ⭐ | 1.409.352 | ngày × sản phẩm × khách hàng (1.353.845 ngoại bộ + 55.507 nội bộ) |
| `fact_farm_weekly` ⭐ | 5.304 | trại × tuần ISO (68 × 78) |
| `fact_transfer_pricing` ⭐ | 23.743 | ngày × SKU × cặp công ty bán–mua |
| `fact_feed_production` | 8.049 | nhà máy × ngày × dòng sản phẩm |
| `fact_market_price` | 4.914 | ngày × mã giá × vùng |
| `fact_material_purchase` | 4.708 | ngày × nguyên vật liệu |
| `fact_pnl_monthly` ⭐ | 432 | công ty × tháng (24 × 18) |
| `fact_plan_monthly` | 288 | sub-segment × tháng kế hoạch (12 × 24) |
| `fact_inventory_snapshot` | 1.404 | cuối tháng × công ty × nhóm SP |
| `fact_debt_snapshot` | 432 | cuối tháng × công ty (24 × 18) |

**4 METADATA:** `_meta_tables` 26 · `_meta_columns` 245 · `_meta_kpi` 19 · `_meta_glossary` 33.

**Master data đáng chú ý:** 42 trại lợn thịt (11 nhóm A < 52.000 đ/kg · 22 nhóm B · 9 nhóm C > 58.000)
+ 8 trại lợn nái + 18 trại gà · 6 nhà máy cám tổng 1,5 triệu tấn/năm · 180 SKU (Pareto: top 20% ≈ 78%
doanh thu) · 850 khách hàng trong đó 32 khách **NỘI BỘ**.

---

## 3. Ràng buộc neo — tất cả đã khớp

Chạy `python3.12 dabaco_scripts/validate.py` → **75 PASS · 0 FAIL**.

| Chỉ tiêu | Neo | Thực tế |
|---|---|---|
| DT thuần ngoại bộ 2025 | 14.897,7 tỷ | 14.897,7 |
| DT thuần ngoại bộ 6T/2026 | 8.377,0 tỷ | 8.377,0 |
| DT thuần ngoại bộ Q2/2026 | 4.252,8 tỷ | 4.252,8 |
| LNST 2025 | 1.506,8 tỷ | 1.506,8 |
| LNST 6T/2026 (Q1 374,1 · Q2 289,1) | 663,2 tỷ | 663,2 |
| Biên LN gộp Q2/2025 · Q2/2026 | 21,6% · 15,4% | 21,6% · 15,4% |
| DT nội bộ 6T/2026 | 5.400,0 tỷ | 5.400,0 |
| Hơi lợn thịt 6T/2026 | 115.700.000 kg | 115.700.000 |
| Sản lượng cám 2025 · 6T/2026 | 1.385.000 · 742.000 tấn | khớp |
| Chênh giá chuyển giao Feed→Farm 6T/2026 | 247,3 tỷ | 247,3 |
| Dư nợ vay cuối T6/2026 | 7.241,2 tỷ | 7.241,2 |
| KH LNST 2026 · KH DT tổng 2026 | 1.117,0 tỷ · 29.311 tỷ | khớp |

Ngoài ra: giá thành bq hệ thống **54.800 đ/kg** · FCR bq lợn thịt **2,680** · giá cám nội bộ
**9.720 đ/kg** vs thị trường **9.180 đ/kg** · giá lợn hơi bq Miền Bắc Q2/2025 **68.500**, Q2/2026 **63.200**.

---

## 4. Sáu demo scenario — trạng thái validation

| # | Câu hỏi trigger | Bằng chứng trong data | Status |
|---|---|---|---|
| **S1** | *"6 tháng đầu năm tập đoàn đang đứng ở đâu so với kế hoạch?"* | Feed 2.850 · Farm 3.900 · Food 1.180 · Future 447 = 8.377 tỷ ngoại bộ; nội bộ 5.400 tỷ (39,2% toàn chuỗi 13.777 tỷ); LNST 663,2 = 59,4% KH. Farm LN gộp 1.180 → 585 tỷ (−50,4%) | **PASS** |
| **S2** | *"Doanh thu quý 2 tăng 11% mà lợi nhuận giảm 43%. Tiền chảy đi đâu?"* | Bridge 506,0 → 289,1 tỷ. Giá heo 68.500 → 63.200 đ/kg · NVL (giá USD + tỷ giá) · lãi vay 65,8 → 85,4 tỷ · CPBH+QLDN 245,4 → 282,1 tỷ · **hao hụt bất thường cụm miền Trung 25,0 tỷ** | **PASS** |
| **S3** ⭐ | *"Mảng Feed lãi thật hay lãi chuyển giá từ Farm sang?"* | 458.000 tấn cám nội bộ · 9.720 vs 9.180 đ/kg · chênh 540 → **247,3 tỷ = 40,4% LN gộp Feed 612 tỷ**. Quy về lợn hơi: **+1.446 đ/kg** giá thành bị thổi phồng. Cross-check giá ngoại bộ độc lập từ `fact_sales` | **PASS** |
| **S4** ⭐ | *"Trại nào đang ăn mòn lợi nhuận của tập đoàn?"* | Top 3 Q2/2026 đúng Thanh Hóa 2 · Nghệ An 1 · Hà Tĩnh ở **64.935 đ/kg** (bio `C`, vận hành 2014–2016). Hao hụt **3,2 → 4,9 (W19) → 6,4 (W20) → 7,8% (W21)**, FCR 2,66 → 2,91, ADG 726 → 654, thú y ×2,4 từ W20. **ASF công bố W24 — dữ liệu báo động trước 3 tuần** | **PASS** |
| **S4 f/u** ⭐ | *"Hiện có trại nào đang có tín hiệu tương tự không?"* | Query xu hướng 3 tuần liên tiếp lọc ra **đúng 2 trại: Bình Phước 1 và Bình Phước 3** (3,6 → 4,1 → 4,6% trong W24–W26, FCR 2,66 → 2,73), không có nhiễu | **PASS** |
| **S5** | *"Nếu giá heo hơi rơi về 55.000 đ/kg thì tập đoàn ra sao?"* | Phân tầng **11 / 22 / 9 trại**; độ nhạy **115,7 tỷ / 1.000 đ/kg**; giá hòa vốn **60.500 đ/kg** | **PASS** |
| **S6** 🎯 | *"Còn thiếu 454 tỷ để về đích 1.117 tỷ. Kịch bản nào khả thi?"* | 1.117,0 − 663,2 = **453,8 tỷ**. Đòn bẩy FCR 2,68 → 2,60 tiết kiệm ~8.900 tấn cám; danh sách 8 trại FCR cao nhất; dư nợ + lãi suất bq để tính phương án cơ cấu nợ | **PASS** |

### Fallback coverage — câu hỏi NGOÀI kịch bản vẫn trả lời được

Doanh thu/giá trứng theo tháng · top đại lý cấp 1 kèm chiết khấu và hạn mức công nợ ·
hiệu suất 18 trại gà (tỷ lệ đẻ 87,8%, FCR gà thịt 1,70, FCR gà giống 2,81) ·
tồn kho cuối tháng theo khối · doanh thu theo kênh × vùng · giá NVL nhập khẩu tách
giá quốc tế / tỷ giá · giá lợn hơi theo ngày cho 3 miền suốt 18 tháng (mọi câu what-if
trong dải 55.000–78.000 đ/kg) · so sánh YoY bất kỳ kỳ nào trong phạm vi 18 tháng.

Các query mẫu nằm ở phần **E** của `05_validation_queries.sql`.

---

## 5. Lưu ý cho người kết nối AI engine

- **Metadata ở đâu:** `_meta_tables` → bảng nào trả lời loại câu hỏi nào · `_meta_columns`
  → ý nghĩa + **đơn vị đo** từng cột · `_meta_kpi` → 19 công thức SQL chạy được kèm benchmark
  · `_meta_glossary` → 33 thuật ngữ ngành. Nên cho AI query `_meta_tables` và `_meta_columns`
  **trước khi** viết SQL.
- **Ba bẫy lớn nhất** (đã ghi trong COMMENT của bảng và trong `_meta_*`):
  1. `fact_sales` — **luôn nêu rõ `is_internal`**. Doanh thu công bố = chỉ `is_internal = 0`;
     cộng cả hai thổi phồng doanh thu ~64%.
  2. `fact_farm_weekly` — **không dùng `AVG()`** cho `fcr`, `cost_per_kg_live_vnd`,
     `mortality_rate_pct` khi gộp nhiều trại; phải tính lại từ tử số và mẫu số.
  3. `fact_inventory_snapshot` và `fact_debt_snapshot` là **SNAPSHOT** — không SUM qua nhiều
     tháng (ngoại lệ: `interest_expense_month_vnd` là dòng chảy).
- **Không SUM `quantity` xuyên `product_group`** — kg / tấn / con / quả / lít trộn lẫn.
- **`fact_market_price`**: giá lợn hơi có 3 dòng/ngày (Bắc/Trung/Nam) → luôn lọc `region_id`;
  giá gà, trứng và NVL nhập khẩu để `region_id` NULL (giá toàn quốc / toàn cầu).
- **Định dạng số cho board:** phân cách nghìn bằng dấu chấm, thập phân bằng dấu phẩy
  ("63.200 đ/kg", "15,4%", "FCR 2,68", "8.377 tỷ").

### Giới hạn đã biết (có chủ đích, hoặc do ràng buộc trong brief xung đột nhau)

1. **Khối FUTURE chỉ ở mức tổng hợp tháng.** Có doanh thu và LN gộp trong `fact_pnl_monthly`
   và line item trong `fact_sales`, nhưng **không drill xuống dự án / lô đất / căn hộ**. Với
   các SKU bất động sản, cột `quantity` và `unit` **không mang ý nghĩa vật lý** — chỉ cột tiền
   là có nghĩa.
2. **`fact_farm_weekly.live_weight_sold_kg` = khối lượng hơi XUẤT CHUỒNG toàn hệ thống**
   (115.700 tấn trong 6T/2026, theo ràng buộc neo), trong khi `fact_sales` chỉ ghi nhận phần đã
   bán ra ngoài và bán nội bộ chuỗi. Nhân sản lượng xuất chuồng với giá thị trường sẽ **không**
   ra doanh thu khối Farm. Hai con số này đến từ hai ràng buộc neo khác nhau trong brief và
   không tương thích với nhau ở mức số học; ưu tiên đã dành cho bảng ràng buộc neo vì mọi
   scenario S3/S5 đều tính trên 115.700 tấn.
3. **Cơ cấu giá thành lợn hơi:** cám ~47,5% · con giống ~25% (nằm trong `overhead_cost_vnd`) ·
   khấu hao + điện nước ~15% · nhân công 7% · thú y 5,5%. Brief ghi "cám ~66%", nhưng 66% mâu
   thuẫn với chính phép tính của Scenario 3 (310.000 tấn cám × 9.720 đ/kg ÷ 115.700 tấn hơi =
   26.050 đ/kg = 47,5% của 54.800). Đã theo phép tính của S3.
4. **`mortality_rate_pct` là tỷ lệ TUẦN** theo đúng các con số bắt buộc trong brief (nền 3,2–3,3%,
   đỉnh 7,8%). Phần lớn là **loại thải** (lợn còi, lợn loại — vẫn bán được), phần chết chiếm ~33%
   ở trạng thái bình thường và ~55% trong ổ dịch.
5. **Tổng doanh thu 2025 gồm nội bộ ≈ 23.700 tỷ**, thấp hơn ước tính "~26.100 tỷ" trong brief.
   Con số này bị chặn bởi ràng buộc neo cứng `revenue_internal` 6T/2026 = 5.400 tỷ: giữ neo đó
   thì luồng nội bộ không thể lớn hơn. Neo được ưu tiên.
6. **Chuyển giá Farm → Food 6T/2026 = 16,2 tỷ** (brief nêu 34,6 tỷ). Với chênh +820 đ/kg lợn hơi
   theo brief và trần doanh thu nội bộ 5.400 tỷ, 34,6 tỷ là bất khả thi. Đây là số fallback,
   không nằm trong bảng ràng buộc neo.
7. **`season_phase`** dùng `'Mùa mưa – dịch bệnh'` (19 ký tự) thay vì ví dụ
   `'Mùa mưa – rủi ro dịch'` (21 ký tự) trong tài liệu — vì tài liệu khai báo cột là
   `VARCHAR(20)`, không chứa nổi chính ví dụ của nó. **Kiểu cột giữ nguyên đúng tài liệu.**
8. **`fact_plan_monthly` 288 dòng** (tài liệu ghi ~216): cần đủ 12 tháng cho cả hai năm kế
   hoạch × 12 sub-segment thì goal-seek của S6 (`WHERE plan_year = 2026`) mới ra đúng 1.117 tỷ.
9. **`fact_feed_production` 8.049 dòng** (tài liệu ghi ~11.000): nhà máy nghỉ Chủ Nhật và có
   ngày bảo dưỡng, nên không phát sinh dòng sản xuất. Công suất huy động bq 6T/2026 = 92,0%.
10. **FCR trại gà thịt ~1,70** — nằm ngoài dải kiểm tra `[2,1; 3,2]` của brief vì dải đó dành
    cho lợn. 1,6–1,8 mới là chuẩn ngành của gà lông trắng. Kiểm tra dải được áp riêng cho
    `farm_type = 'LON_THIT'`.

---

## 6. Sinh lại dữ liệu

Scripts nằm ở `dabaco_scripts/` (không được git theo dõi vì `.gitignore` loại `*.py`):

```bash
python3.12 dabaco_scripts/gen_master.py      # → 03_master_data.sql
python3.12 dabaco_scripts/gen_facts.py       # → 04_transaction_data.sql
python3.12 dabaco_scripts/gen_metadata.py    # → 02_metadata.sql  (đọc schema từ DB đang chạy)
python3.12 dabaco_scripts/verify_schema.py   # so DDL với database-schema.md
python3.12 dabaco_scripts/validate.py        # báo cáo 75 check PASS/FAIL
```

Yêu cầu: Python 3.10+ với `numpy`. Seed cố định (`SEED = 20260630`) nên kết quả tái lập được.
