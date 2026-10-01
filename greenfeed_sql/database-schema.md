# DATA SCHEMA — GREENFEED VIỆT NAM | BÁN HÀNG THỨC ĂN CHĂN NUÔI
## Database: greenfeed_feed_demo (MySQL 8.0, utf8mb4_unicode_ci)
## Phạm vi: 01/10/2024 – 30/09/2026 (24 tháng) | "Hiện tại" = 30/09/2026

Phạm vi nghiệp vụ: bán thức ăn chăn nuôi thành phẩm ra bên ngoài tại Việt Nam, qua 2 kênh đại lý cấp 1 và trang trại mua trực tiếp. Không gồm cám cấp cho trang trại nội bộ, mảng Farm, mảng Food (G Kitchen), thị trường ngoài Việt Nam. Không có dữ liệu của đối thủ.

Tiền tệ: VND, trước thuế GTGT. Khối lượng lưu theo kg; báo cáo quy ra tấn = kg / 1000.

---

## SƠ ĐỒ QUAN HỆ

```
dim_regions (region_id PK)
  ├── dim_areas.region_id
  ├── dim_provinces.region_id
  ├── dim_customers.region_id
  └── ext_live_hog_prices.region_id

dim_areas (area_id PK)
  ├── dim_provinces.area_id
  ├── dim_customers.area_id
  ├── dim_sales_reps.area_id
  └── fact_sales_targets.area_id

dim_provinces (province_id PK)
  ├── dim_customers.province_id
  └── dim_plants.province_id

dim_dates (date_key PK)
  └── fact_sales_lines.invoice_date

dim_customers (customer_id PK)
  ├── fact_sales_lines.customer_id
  └── fact_ar_snapshots.customer_id

dim_products (product_id PK)
  ├── fact_sales_lines.product_id
  ├── fact_list_prices.product_id
  └── fact_product_costs.product_id

dim_plants (plant_id PK)
  └── fact_sales_lines.plant_id

dim_sales_reps (sales_rep_id PK)
  ├── dim_customers.sales_rep_id      (người phụ trách HIỆN TẠI)
  └── fact_sales_lines.sales_rep_id   (người phụ trách TẠI THỜI ĐIỂM BÁN)

fact_sales_targets: khóa logic (target_month, area_id, species_group)
  └── đối chiếu với fact_sales_lines sau khi gộp về tháng × dim_customers.area_id × dim_products.species_group

ext_raw_material_prices: (price_month, material_name) — không nối trực tiếp với bảng nào
```

Bảng metadata trong cùng database: `_meta_tables`, `_meta_columns`, `_meta_kpi`, `_meta_glossary`.

---

## DIMENSION TABLES

### 1. dim_dates (822 dòng)
Lịch ngày 01/10/2024 – 31/12/2026, có âm lịch và cửa sổ Tết. Dữ liệu bán hàng chỉ đến 30/09/2026; các ngày sau đó dùng cho kế hoạch.

| Cột | Kiểu | Mô tả | Ghi chú |
|-----|------|-------|---------|
| `date_key` | DATE PK | Ngày dương lịch | |
| `year` | SMALLINT | Năm | |
| `quarter` | TINYINT | Quý 1–4 | |
| `month` | TINYINT | Tháng 1–12 | |
| `calendar_month` | CHAR(7) | 'YYYY-MM' | Dùng group theo tháng |
| `month_name` | VARCHAR(20) | 'Tháng 1' … 'Tháng 12' | |
| `week_of_year` | TINYINT | Tuần ISO | |
| `day_of_week` | TINYINT | 1 = Thứ Hai … 7 = Chủ nhật | |
| `day_name` | VARCHAR(15) | 'Thứ Hai' … 'Chủ nhật' | |
| `is_weekend` | TINYINT(1) | 1 nếu Chủ nhật | Đại lý TACN vẫn làm Thứ Bảy |
| `lunar_year` | SMALLINT | Năm âm lịch | Có thể NULL |
| `lunar_month` | TINYINT | Tháng âm lịch | Có thể NULL |
| `lunar_day` | TINYINT | Ngày âm lịch | Có thể NULL |
| `tet_window` | VARCHAR(20) | 'Trước Tết' (−35 đến −8 ngày), 'Tết' (−7 đến +7), 'Sau Tết' (+8 đến +30), NULL | Tết 2025: 29/01/2025; Tết 2026: 17/02/2026 |

### 2. dim_regions (4 dòng)
4 vùng kinh doanh mảng Feed.

| Cột | Kiểu | Mô tả | Ghi chú |
|-----|------|-------|---------|
| `region_id` | TINYINT PK | | 1 = MB, 2 = MTTN, 3 = DNB, 4 = MT |
| `region_code` | VARCHAR(10) | MB, MTTN, DNB, MT | |
| `region_name` | VARCHAR(50) | Miền Bắc, Miền Trung – Tây Nguyên, Đông Nam Bộ, Miền Tây | Miền Tây = Đồng bằng sông Cửu Long |
| `regional_director_name` | VARCHAR(80) | Giám đốc kinh doanh vùng | |

### 3. dim_areas (11 dòng)
Khu vực kinh doanh — cấp giao kế hoạch, do ASM quản lý.

| Cột | Kiểu | Mô tả | Ghi chú |
|-----|------|-------|---------|
| `area_id` | SMALLINT PK | | |
| `area_code` | VARCHAR(10) | Mã khu vực | |
| `area_name` | VARCHAR(80) | Tên khu vực | Xem bảng dưới |
| `region_id` | TINYINT FK | | → dim_regions |
| `area_manager_name` | VARCHAR(80) | Quản lý khu vực (ASM) | |

| area_id | area_name | Vùng | Tỉnh |
|---|---|---|---|
| 1 | Đồng bằng sông Hồng 1 | Miền Bắc | Hưng Yên, Hải Phòng, Bắc Ninh |
| 2 | Đồng bằng sông Hồng 2 | Miền Bắc | Ninh Bình, Hà Nội |
| 3 | Trung du & Bắc Trung Bộ | Miền Bắc | Phú Thọ, Thái Nguyên, Thanh Hóa, Nghệ An |
| 4 | Gia Lai – Quảng Ngãi | Miền Trung – Tây Nguyên | Gia Lai, Quảng Ngãi |
| 5 | Đắk Lắk – Lâm Đồng | Miền Trung – Tây Nguyên | Đắk Lắk, Lâm Đồng |
| 6 | Đà Nẵng – Khánh Hòa | Miền Trung – Tây Nguyên | Đà Nẵng, Khánh Hòa |
| 7 | Đồng Nai | Đông Nam Bộ | Đồng Nai |
| 8 | TP.HCM – Tây Ninh | Đông Nam Bộ | TP. Hồ Chí Minh, Tây Ninh |
| 9 | Tiền Giang – Bến Tre | Miền Tây | Đồng Tháp, Vĩnh Long |
| 10 | Cần Thơ – An Giang | Miền Tây | Cần Thơ, An Giang |
| 11 | Cà Mau | Miền Tây | Cà Mau |

### 4. dim_provinces (23 dòng)
Tỉnh/thành có phát sinh bán hàng, theo đơn vị hành chính sau 01/07/2025.

| Cột | Kiểu | Mô tả | Ghi chú |
|-----|------|-------|---------|
| `province_id` | SMALLINT PK | | |
| `province_name` | VARCHAR(50) | Tên tỉnh mới | Ví dụ: Tây Ninh |
| `former_provinces` | VARCHAR(150) | Các tỉnh cũ đã hợp nhất | Ví dụ: 'Tây Ninh, Long An'. NULL nếu không sáp nhập |
| `area_id` | SMALLINT FK | | → dim_areas |
| `region_id` | TINYINT FK | | → dim_regions |

Khi người dùng nói tên tỉnh cũ (Long An, Bình Định, Hà Nam, Tiền Giang, Bến Tre…), tìm trong `former_provinces` bằng `LIKE '%Long An%'`.

### 5. dim_plants (6 dòng)
Nhà máy TACN tại Việt Nam.

| Cột | Kiểu | Mô tả | Ghi chú |
|-----|------|-------|---------|
| `plant_id` | TINYINT PK | | |
| `plant_code` | VARCHAR(10) | BLU, DNA, VLG, GLA, HNM, HYN | |
| `plant_name` | VARCHAR(80) | Nhà máy Bến Lức, Đồng Nai, Vĩnh Long, Gia Lai, Hà Nam, Hưng Yên | |
| `province_id` | SMALLINT FK | Tỉnh đặt nhà máy | → dim_provinces |
| `design_capacity_tons_year` | INT | Công suất thiết kế (tấn/năm) | Gồm cả phần cấp cho trang trại nội bộ. Số tham chiếu — KHÔNG dùng để tính hiệu suất từ dữ liệu bán ngoài |
| `product_scope` | VARCHAR(80) | Nhóm sản phẩm sản xuất được | DNA, GLA, HYN không làm thủy sản |
| `note` | VARCHAR(200) | Ghi chú | GLA: đang mở rộng từ 3/2026, mục tiêu ~700.000 tấn/năm |

### 6. dim_products (83 dòng)
Danh mục SKU thức ăn chăn nuôi.

| Cột | Kiểu | Mô tả | Ghi chú |
|-----|------|-------|---------|
| `product_id` | SMALLINT PK | | |
| `sku_code` | VARCHAR(20) | Mã SKU | GF…, GT…, AQ…, PN…, SW… |
| `product_name` | VARCHAR(150) | Tên SKU | Ví dụ: 'GreenFeed 1043 – Heo thịt (60 – 90 kg)' |
| `brand` | VARCHAR(30) | GreenFeed, G.TEK, Aquagreen, Superwhite, Panafeed | |
| `species_group` | VARCHAR(20) | Heo, Gia cầm, Thủy sản | Cấp giao kế hoạch |
| `species` | VARCHAR(30) | Heo, Gà, Vịt, Cút, Cá tra, Cá rô phi – điêu hồng, Cá có vảy, Tôm thẻ, Tôm sú | |
| `product_line` | VARCHAR(50) | Dòng theo giai đoạn nuôi | Heo con tập ăn, Heo cai sữa, Heo thịt, Heo nái, Đậm đặc heo, Gà thịt, Gà đẻ, Vịt thịt, Vịt đẻ, Cút, Đậm đặc gia cầm, Cá tra, Cá rô phi – điêu hồng, Cá có vảy, Tôm thẻ chân trắng, Tôm sú |
| `feed_type` | VARCHAR(30) | Hỗn hợp hoàn chỉnh / Đậm đặc | Đậm đặc giá/kg cao hơn vì người nuôi tự trộn thêm ngô, cám |
| `is_premium` | TINYINT(1) | 1 = dòng cao cấp G.TEK | Chỉ có ở nhóm Heo |
| `pack_size_kg` | DECIMAL(4,1) | Quy cách bao | 25 kg (heo, gia cầm, cá); 20 kg (tôm) |
| `launch_date` | DATE | Ngày ra mắt | G.TEK: 01/06/2024 |
| `status` | VARCHAR(20) | Đang kinh doanh / Ngưng kinh doanh | |

Cơ cấu: Heo 36 SKU (12 SKU G.TEK), Gia cầm 22, Thủy sản 25.

### 7. dim_sales_reps (~165 dòng)

| Cột | Kiểu | Mô tả | Ghi chú |
|-----|------|-------|---------|
| `sales_rep_id` | SMALLINT PK | | |
| `rep_code` | VARCHAR(10) | Mã NV | NV0001… |
| `rep_name` | VARCHAR(80) | Họ tên | |
| `position` | VARCHAR(40) | Nhân viên kinh doanh / Giám sát kinh doanh | |
| `area_id` | SMALLINT FK | Khu vực | → dim_areas |
| `hire_date` | DATE | Ngày vào làm | |
| `status` | VARCHAR(20) | Đang làm việc / Nghỉ việc | |

### 8. dim_customers (~2.900 dòng)
Khách hàng mảng Feed.

| Cột | Kiểu | Mô tả | Ghi chú |
|-----|------|-------|---------|
| `customer_id` | INT PK | | |
| `customer_code` | VARCHAR(15) | Mã khách hàng | |
| `customer_name` | VARCHAR(150) | Tên đại lý / trang trại | |
| `customer_type` | VARCHAR(30) | 'Đại lý cấp 1' / 'Trang trại trực tiếp' | Kênh bán |
| `customer_tier` | VARCHAR(20) | Hạng đại lý: Kim cương, Vàng, Bạc, Tiêu chuẩn | NULL với trang trại |
| `farm_scale` | VARCHAR(30) | Dưới 500 nái, 500–2.000 nái, Trên 2.000 nái, Gia cầm – thủy sản | NULL với đại lý |
| `main_species_group` | VARCHAR(20) | Nhóm vật nuôi chính | Khách hàng vẫn có thể mua nhóm khác |
| `contact_name` | VARCHAR(80) | Chủ đại lý / người liên hệ | |
| `province_id` | SMALLINT FK | Tỉnh của khách hàng | → dim_provinces |
| `area_id` | SMALLINT FK | Khu vực | Denormalized |
| `region_id` | TINYINT FK | Vùng | Denormalized — dùng cột này để lọc vùng |
| `sales_rep_id` | SMALLINT FK | NVKD phụ trách hiện tại | → dim_sales_reps |
| `payment_term_days` | SMALLINT | Số ngày được nợ | Đại lý 30 (Kim cương 45), trang trại 45 |
| `credit_limit_vnd` | DECIMAL(16,0) | Hạn mức tín dụng | VND |
| `start_date` | DATE | Ngày bắt đầu giao dịch | Khách hàng mới có start_date trong kỳ dữ liệu |
| `status` | VARCHAR(20) | Đang giao dịch / Ngưng giao dịch | Trạng thái hành chính |
| `end_date` | DATE | Ngày ngưng giao dịch | NULL nếu còn giao dịch |

Định nghĩa "đại lý đang hoạt động" trong phân tích: có hóa đơn trong 90 ngày tính đến ngày phân tích (không dựa vào cột `status`).

---

## FACT TABLES

### 9. fact_sales_lines ⭐ (FACT CHÍNH — ~1,2–1,6 triệu dòng)
Dòng hóa đơn bán TACN. 1 dòng = 1 SKU trên 1 hóa đơn.

| Cột | Kiểu | Mô tả | Đơn vị |
|-----|------|-------|--------|
| `sales_line_id` | BIGINT PK | | |
| `invoice_no` | VARCHAR(20) | Số hóa đơn, dạng GFyymm-nnnnnn | |
| `invoice_date` | DATE FK | Ngày hóa đơn | → dim_dates |
| `due_date` | DATE | Hạn thanh toán | = invoice_date + payment_term_days |
| `customer_id` | INT FK | | → dim_customers |
| `product_id` | SMALLINT FK | | → dim_products |
| `plant_id` | TINYINT FK | Nhà máy xuất hàng | → dim_plants |
| `sales_rep_id` | SMALLINT FK | NVKD tại thời điểm bán | → dim_sales_reps |
| `quantity_kg` | DECIMAL(12,1) | Khối lượng | kg |
| `quantity_bags` | INT | Số bao | bao |
| `list_price_per_kg` | DECIMAL(10,0) | Giá niêm yết tại ngày hóa đơn | VND/kg |
| `gross_amount_vnd` | DECIMAL(16,0) | = quantity_kg × list_price_per_kg | VND |
| `standard_discount_vnd` | DECIMAL(16,0) | Chiết khấu theo chính sách chuẩn (hạng đại lý, quy mô trang trại) | VND |
| `special_discount_vnd` | DECIMAL(16,0) | Chiết khấu đặc biệt ngoài chính sách (hỗ trợ giá, khuyến mãi vùng) | VND |
| `net_amount_vnd` | DECIMAL(16,0) | Doanh thu thuần = gross − standard_discount − special_discount | VND |
| `standard_cost_vnd` | DECIMAL(16,0) | Giá vốn chuẩn = quantity_kg × giá vốn chuẩn/kg của tháng | VND |
| `delivery_cost_vnd` | DECIMAL(14,0) | Chi phí vận chuyển công ty chịu | VND |

⚠️ **Doanh thu mặc định = `net_amount_vnd`.** `gross_amount_vnd` chỉ dùng khi phân tích giá niêm yết và chiết khấu.
⚠️ **Sản lượng là thước đo chính của ngành.** Luôn báo cả tấn và doanh thu.
⚠️ **Lãi gộp = `net_amount_vnd − standard_cost_vnd`.** Giá vốn đã có sẵn trên từng dòng, không tính lại.
⚠️ Chiết khấu chuẩn thông thường: đại lý 2–5% gross theo hạng; trang trại 4–8% theo quy mô.

### 10. fact_list_prices (~170 dòng)
Lịch sử bảng giá niêm yết toàn quốc theo ngày hiệu lực.

| Cột | Kiểu | Mô tả | Đơn vị |
|-----|------|-------|--------|
| `list_price_id` | INT PK | | |
| `product_id` | SMALLINT FK | | → dim_products |
| `effective_from` | DATE | Ngày bắt đầu hiệu lực | |
| `effective_to` | DATE | Ngày hết hiệu lực; NULL = đang áp dụng | |
| `list_price_per_kg` | DECIMAL(10,0) | Giá niêm yết | VND/kg |
| `change_reason` | VARCHAR(150) | Lý do điều chỉnh | |

Dùng bảng này để biết **khi nào** giá thay đổi và thay đổi bao nhiêu — cơ sở cho phân tích phản ứng của sản lượng với giá.

### 11. fact_product_costs (~2.000 dòng)
Giá vốn chuẩn theo SKU theo tháng. Phản ánh giá nguyên liệu của tháng trước.

| Cột | Kiểu | Mô tả | Đơn vị |
|-----|------|-------|--------|
| `product_id` | SMALLINT PK, FK | | → dim_products |
| `cost_month` | DATE PK | Ngày đầu tháng | |
| `standard_cost_per_kg` | DECIMAL(10,0) | Giá vốn chuẩn | VND/kg |

### 12. fact_ar_snapshots (~62.000 dòng) — SNAPSHOT
Công nợ phải thu cuối tháng theo khách hàng, từ 31/10/2024 đến 30/09/2026.

| Cột | Kiểu | Mô tả | Đơn vị |
|-----|------|-------|--------|
| `snapshot_date` | DATE PK | Ngày cuối tháng | |
| `customer_id` | INT PK, FK | | → dim_customers |
| `credit_limit_vnd` | DECIMAL(16,0) | Hạn mức tại thời điểm snapshot | VND |
| `outstanding_vnd` | DECIMAL(16,0) | Tổng dư nợ | VND |
| `not_due_vnd` | DECIMAL(16,0) | Chưa đến hạn | VND |
| `overdue_1_30_vnd` | DECIMAL(16,0) | Quá hạn 1–30 ngày | VND |
| `overdue_31_60_vnd` | DECIMAL(16,0) | Quá hạn 31–60 ngày | VND |
| `overdue_61_90_vnd` | DECIMAL(16,0) | Quá hạn 61–90 ngày | VND |
| `overdue_over_90_vnd` | DECIMAL(16,0) | Quá hạn trên 90 ngày | VND |

⚠️ **outstanding = not_due + 4 bucket quá hạn.**
⚠️ **Không SUM nhiều snapshot_date với nhau.** Muốn xem xu hướng thì GROUP BY snapshot_date.
⚠️ "Nợ quá hạn trên 30 ngày" = overdue_31_60 + overdue_61_90 + overdue_over_90.

### 13. fact_sales_targets (792 dòng)
Kế hoạch bán hàng năm 2025 và 2026.

| Cột | Kiểu | Mô tả | Đơn vị |
|-----|------|-------|--------|
| `target_id` | INT PK | | |
| `target_month` | DATE | Ngày đầu tháng | |
| `area_id` | SMALLINT FK | Khu vực | → dim_areas |
| `species_group` | VARCHAR(20) | Heo, Gia cầm, Thủy sản | |
| `target_quantity_tons` | DECIMAL(12,1) | Kế hoạch sản lượng | tấn |
| `target_net_revenue_vnd` | DECIMAL(18,0) | Kế hoạch doanh thu thuần | VND |

⚠️ Kế hoạch chỉ có ở cấp **tháng × khu vực × nhóm vật nuôi**. Không có kế hoạch theo khách hàng, SKU, kênh hay nhà máy.
⚠️ Kế hoạch có cho cả tháng 10–12/2026 — dùng để tính phần còn phải đạt trong Q4.

### 14. ext_live_hog_prices (~420 dòng)
Giá heo hơi thị trường theo vùng, tổng hợp hằng tuần.

| Cột | Kiểu | Mô tả | Đơn vị |
|-----|------|-------|--------|
| `week_start_date` | DATE PK | Thứ Hai đầu tuần | |
| `region_id` | TINYINT PK, FK | | → dim_regions |
| `avg_price_per_kg` | DECIMAL(8,0) | Giá heo hơi bình quân tuần | VND/kg |

Dữ liệu tham chiếu thị trường, dùng để giải thích biến động nhu cầu thức ăn heo.

### 15. ext_raw_material_prices (120 dòng)
Giá nguyên liệu chính về nhà máy, bình quân tháng.

| Cột | Kiểu | Mô tả | Đơn vị |
|-----|------|-------|--------|
| `price_month` | DATE PK | Ngày đầu tháng | |
| `material_name` | VARCHAR(40) PK | Ngô hạt, Khô đậu tương, Lúa mì, Cám gạo, Bột cá | |
| `price_per_kg_vnd` | DECIMAL(10,0) | Giá về nhà máy | VND/kg |

---

## SQL TEMPLATES

### T1. Sản lượng, doanh thu theo vùng — kỳ này so với cùng kỳ
```sql
-- Đổi khoảng ngày theo câu hỏi. Ví dụ: 9 tháng 2026 vs 9 tháng 2025
SELECT r.region_name,
       ROUND(SUM(CASE WHEN s.invoice_date BETWEEN '2026-01-01' AND '2026-09-30' THEN s.quantity_kg ELSE 0 END)/1000, 0) AS tan_ky_nay,
       ROUND(SUM(CASE WHEN s.invoice_date BETWEEN '2025-01-01' AND '2025-09-30' THEN s.quantity_kg ELSE 0 END)/1000, 0) AS tan_cung_ky,
       ROUND(SUM(CASE WHEN s.invoice_date BETWEEN '2026-01-01' AND '2026-09-30' THEN s.net_amount_vnd ELSE 0 END)/1e9, 1) AS dt_ty_ky_nay,
       ROUND(SUM(CASE WHEN s.invoice_date BETWEEN '2025-01-01' AND '2025-09-30' THEN s.net_amount_vnd ELSE 0 END)/1e9, 1) AS dt_ty_cung_ky
FROM `fact_sales_lines` s
JOIN `dim_customers` c ON c.customer_id = s.customer_id
JOIN `dim_regions` r   ON r.region_id = c.region_id
WHERE s.invoice_date BETWEEN '2025-01-01' AND '2026-09-30'
GROUP BY r.region_name
ORDER BY tan_ky_nay DESC;
```

### T2. Thực hiện so với kế hoạch theo khu vực × nhóm vật nuôi
```sql
-- Gộp thực hiện về đúng grain của kế hoạch TRƯỚC khi JOIN
WITH actual AS (
  SELECT c.area_id, p.species_group,
         SUM(s.quantity_kg)/1000 AS tan_thuc_hien,
         SUM(s.net_amount_vnd)   AS dt_thuc_hien
  FROM `fact_sales_lines` s
  JOIN `dim_customers` c ON c.customer_id = s.customer_id
  JOIN `dim_products`  p ON p.product_id  = s.product_id
  WHERE s.invoice_date BETWEEN '2026-01-01' AND '2026-09-30'
  GROUP BY c.area_id, p.species_group
),
plan AS (
  SELECT area_id, species_group,
         SUM(target_quantity_tons)   AS tan_ke_hoach,
         SUM(target_net_revenue_vnd) AS dt_ke_hoach
  FROM `fact_sales_targets`
  WHERE target_month BETWEEN '2026-01-01' AND '2026-09-01'
  GROUP BY area_id, species_group
)
SELECT a.area_name, pl.species_group,
       ROUND(COALESCE(ac.tan_thuc_hien,0)) AS tan_thuc_hien,
       ROUND(pl.tan_ke_hoach)              AS tan_ke_hoach,
       ROUND(COALESCE(ac.tan_thuc_hien,0)/pl.tan_ke_hoach*100, 1) AS pct_dat_san_luong,
       ROUND(COALESCE(ac.dt_thuc_hien,0)/pl.dt_ke_hoach*100, 1)   AS pct_dat_doanh_thu
FROM plan pl
JOIN `dim_areas` a ON a.area_id = pl.area_id
LEFT JOIN actual ac ON ac.area_id = pl.area_id AND ac.species_group = pl.species_group
ORDER BY pct_dat_san_luong;
```

### T3. Giá thực và cơ cấu chiết khấu theo vùng, theo quý
```sql
SELECT r.region_name, d.year, d.quarter,
       ROUND(SUM(s.quantity_kg)/1000) AS tan,
       ROUND(SUM(s.gross_amount_vnd)/SUM(s.quantity_kg))   AS gia_niem_yet_bq,
       ROUND(SUM(s.net_amount_vnd)/SUM(s.quantity_kg))     AS gia_thuc_bq,
       ROUND(SUM(s.standard_discount_vnd)/SUM(s.gross_amount_vnd)*100, 2) AS ck_chuan_pct,
       ROUND(SUM(s.special_discount_vnd)/SUM(s.gross_amount_vnd)*100, 2)  AS ck_dac_biet_pct
FROM `fact_sales_lines` s
JOIN `dim_dates` d     ON d.date_key = s.invoice_date
JOIN `dim_customers` c ON c.customer_id = s.customer_id
JOIN `dim_regions` r   ON r.region_id = c.region_id
GROUP BY r.region_name, d.year, d.quarter
ORDER BY r.region_name, d.year, d.quarter;
-- Lưu ý: giá thực bình quân bị ảnh hưởng bởi cơ cấu sản phẩm.
-- So sánh giá giữa các kỳ nên lọc theo cùng product_line (ví dụ 'Heo thịt').
```

### T4. Lãi gộp và lãi gộp/tấn theo vùng × dòng sản phẩm
```sql
SELECT r.region_name, p.product_line,
       ROUND(SUM(s.quantity_kg)/1000) AS tan,
       ROUND(SUM(s.net_amount_vnd - s.standard_cost_vnd)/1e9, 1) AS lai_gop_ty,
       ROUND(SUM(s.net_amount_vnd - s.standard_cost_vnd)/SUM(s.net_amount_vnd)*100, 1) AS bien_lai_gop_pct,
       ROUND(SUM(s.net_amount_vnd - s.standard_cost_vnd)/(SUM(s.quantity_kg)/1000)) AS lai_gop_moi_tan,
       ROUND(SUM(s.net_amount_vnd - s.standard_cost_vnd - s.delivery_cost_vnd)/(SUM(s.quantity_kg)/1000)) AS lai_gop_sau_vc_moi_tan
FROM `fact_sales_lines` s
JOIN `dim_customers` c ON c.customer_id = s.customer_id
JOIN `dim_regions` r   ON r.region_id = c.region_id
JOIN `dim_products` p  ON p.product_id = s.product_id
WHERE s.invoice_date BETWEEN '2026-07-01' AND '2026-09-30'
GROUP BY r.region_name, p.product_line
ORDER BY r.region_name, tan DESC;
```

### T5. Công nợ theo tuổi nợ và khách hàng vượt hạn mức tại một snapshot
```sql
-- Chọn đúng 1 snapshot_date
SELECT r.region_name,
       ROUND(SUM(a.outstanding_vnd)/1e9, 1) AS du_no_ty,
       ROUND(SUM(a.overdue_1_30_vnd)/1e9, 1) AS qh_1_30_ty,
       ROUND(SUM(a.overdue_31_60_vnd + a.overdue_61_90_vnd + a.overdue_over_90_vnd)/1e9, 1) AS qh_tren_30_ty,
       ROUND(SUM(a.overdue_31_60_vnd + a.overdue_61_90_vnd + a.overdue_over_90_vnd)
             / NULLIF(SUM(a.outstanding_vnd),0)*100, 1) AS ty_le_qh_tren_30_pct,
       SUM(a.outstanding_vnd > a.credit_limit_vnd) AS so_kh_vuot_han_muc
FROM `fact_ar_snapshots` a
JOIN `dim_customers` c ON c.customer_id = a.customer_id
JOIN `dim_regions` r   ON r.region_id = c.region_id
WHERE a.snapshot_date = '2026-09-30'
GROUP BY r.region_name;

-- Xu hướng theo tháng: GROUP BY a.snapshot_date (không cộng dồn các tháng)
```

### T6. Khách hàng giảm mua giữa hai giai đoạn, kèm công nợ hiện tại
```sql
WITH sales AS (
  SELECT s.customer_id,
         SUM(CASE WHEN s.invoice_date BETWEEN '2026-01-01' AND '2026-03-31' THEN s.quantity_kg ELSE 0 END)/3 AS kg_thang_gd1,
         SUM(CASE WHEN s.invoice_date BETWEEN '2026-07-01' AND '2026-09-30' THEN s.quantity_kg ELSE 0 END)/3 AS kg_thang_gd2
  FROM `fact_sales_lines` s
  WHERE s.invoice_date BETWEEN '2026-01-01' AND '2026-09-30'
  GROUP BY s.customer_id
),
ar AS (
  SELECT customer_id, outstanding_vnd, credit_limit_vnd,
         overdue_31_60_vnd + overdue_61_90_vnd + overdue_over_90_vnd AS qh_tren_30
  FROM `fact_ar_snapshots`
  WHERE snapshot_date = '2026-09-30'
)
SELECT c.customer_name, c.customer_type, c.customer_tier, pr.province_name,
       ROUND(sa.kg_thang_gd1/1000, 1) AS tan_thang_gd1,
       ROUND(sa.kg_thang_gd2/1000, 1) AS tan_thang_gd2,
       ROUND((sa.kg_thang_gd2 - sa.kg_thang_gd1)/NULLIF(sa.kg_thang_gd1,0)*100, 1) AS thay_doi_pct,
       ROUND(COALESCE(ar.qh_tren_30,0)/1e6) AS qh_tren_30_trieu,
       ROUND(COALESCE(ar.outstanding_vnd,0)/NULLIF(ar.credit_limit_vnd,0)*100) AS du_no_tren_han_muc_pct
FROM sales sa
JOIN `dim_customers` c  ON c.customer_id = sa.customer_id
JOIN `dim_provinces` pr ON pr.province_id = c.province_id
LEFT JOIN ar ON ar.customer_id = sa.customer_id
WHERE sa.kg_thang_gd1 > 0
ORDER BY (sa.kg_thang_gd2 - sa.kg_thang_gd1) ASC
LIMIT 50;
-- Thêm điều kiện lọc vùng (c.region_id), nhóm vật nuôi (JOIN dim_products) tùy câu hỏi.
```

### T7. Sản lượng theo nhà máy xuất hàng và chi phí vận chuyển
```sql
SELECT r.region_name AS vung_khach_hang, pl.plant_name AS nha_may_xuat,
       d.year, d.quarter,
       ROUND(SUM(s.quantity_kg)/1000) AS tan,
       ROUND(SUM(s.delivery_cost_vnd)/SUM(s.quantity_kg)) AS van_chuyen_dong_kg
FROM `fact_sales_lines` s
JOIN `dim_dates` d     ON d.date_key = s.invoice_date
JOIN `dim_customers` c ON c.customer_id = s.customer_id
JOIN `dim_regions` r   ON r.region_id = c.region_id
JOIN `dim_plants` pl   ON pl.plant_id = s.plant_id
GROUP BY r.region_name, pl.plant_name, d.year, d.quarter
ORDER BY r.region_name, d.year, d.quarter, tan DESC;
```

### T8. Sản lượng quanh một lần điều chỉnh giá, theo kênh
```sql
-- Bước 1: tìm các lần điều chỉnh giá
SELECT p.species_group, lp.effective_from, lp.change_reason,
       COUNT(*) AS so_sku, ROUND(AVG(lp.list_price_per_kg)) AS gia_bq_moi
FROM `fact_list_prices` lp
JOIN `dim_products` p ON p.product_id = lp.product_id
GROUP BY p.species_group, lp.effective_from, lp.change_reason
ORDER BY lp.effective_from;

-- Bước 2: sản lượng theo tháng × kênh quanh ngày điều chỉnh (±3 tháng), so với nhịp mùa vụ
SELECT d.calendar_month, c.customer_type, ROUND(SUM(s.quantity_kg)/1000) AS tan
FROM `fact_sales_lines` s
JOIN `dim_dates` d     ON d.date_key = s.invoice_date
JOIN `dim_customers` c ON c.customer_id = s.customer_id
JOIN `dim_products` p  ON p.product_id = s.product_id
WHERE p.species_group IN ('Heo','Gia cầm')
  AND s.invoice_date BETWEEN '<ngày điều chỉnh − 3 tháng>' AND '<ngày điều chỉnh + 3 tháng>'
GROUP BY d.calendar_month, c.customer_type
ORDER BY d.calendar_month, c.customer_type;
-- Đối chiếu tỷ trọng từng kênh trước/sau; kết hợp ext_live_hog_prices để loại trừ ảnh hưởng của giá heo.
```

### T9. Giá heo hơi theo vùng theo tháng
```sql
SELECT DATE_FORMAT(h.week_start_date, '%Y-%m') AS thang, r.region_name,
       ROUND(AVG(h.avg_price_per_kg)) AS gia_heo_hoi
FROM `ext_live_hog_prices` h
JOIN `dim_regions` r ON r.region_id = h.region_id
GROUP BY thang, r.region_name
ORDER BY thang, r.region_name;
```

---

## JOIN WARNINGS

1. **fact_sales_lines ↔ fact_sales_targets — khác grain.** Kế hoạch ở cấp tháng × khu vực × nhóm vật nuôi. Gộp thực hiện về đúng grain đó (area qua `dim_customers.area_id`, nhóm qua `dim_products.species_group`) rồi mới JOIN. Không JOIN kế hoạch vào từng dòng hóa đơn.
2. **fact_ar_snapshots = SNAPSHOT.** Luôn lọc `snapshot_date = '...'` hoặc GROUP BY `snapshot_date`. Cộng nhiều tháng sẽ nhân dư nợ lên nhiều lần.
3. **fact_ar_snapshots ↔ fact_sales_lines.** Gộp doanh số theo customer_id trong subquery/CTE trước, rồi mới JOIN với snapshot. JOIN trực tiếp sẽ lặp dư nợ theo số dòng hóa đơn.
4. **Vùng/khu vực của doanh số = nơi khách hàng ở** (`dim_customers.region_id`, `area_id`), không phải nơi đặt nhà máy. Khách hàng miền Trung có thể được xuất hàng từ nhà máy Đồng Nai.
5. **NVKD:** `dim_customers.sales_rep_id` là người phụ trách hiện tại. Phân tích theo NVKD trong quá khứ dùng `fact_sales_lines.sales_rep_id`.
6. **ext_live_hog_prices** theo tuần × vùng. Gộp `AVG` về tháng trước khi so với doanh số tháng. Nối với khách hàng qua `region_id`.
7. **ext_raw_material_prices** không nối với sản phẩm. Giá vốn từng SKU nằm ở `fact_product_costs` và đã có sẵn trên `fact_sales_lines.standard_cost_vnd`.
8. **fact_list_prices** là bảng theo khoảng hiệu lực: `invoice_date BETWEEN effective_from AND COALESCE(effective_to, '9999-12-31')`. Thông thường không cần JOIN vì `list_price_per_kg` đã có trên dòng hóa đơn.
9. **fact_product_costs:** nếu cần JOIN, dùng `cost_month = DATE_FORMAT(invoice_date, '%Y-%m-01')`.
10. **Hiệu ứng cơ cấu:** giá thực bình quân/kg và lãi gộp/tấn giữa các vùng, các kỳ bị chi phối bởi tỷ trọng heo con, đậm đặc, G.TEK, thức ăn tôm (giá cao). So sánh giá nên lọc cùng `product_line`.
11. **Tết lệch tháng:** Tết 2025 rơi vào tháng 1, Tết 2026 rơi vào tháng 2. So sánh tháng 1 hoặc tháng 2 riêng lẻ giữa hai năm sẽ sai lệch; gộp tháng 1 + 2 hoặc dùng `tet_window`.
12. **Ngày "hiện tại" = 30/09/2026.** Không dùng `CURDATE()`. "90 ngày gần nhất" = 03/07/2026 – 30/09/2026.
13. **Năm 2024 chỉ có Q4.** So sánh cùng kỳ chỉ làm được với các tháng 10–12/2025 so với 10–12/2024 và các tháng 2026 so với 2025.
14. **dim_customers.region_id, area_id là denormalized** và khớp với `dim_provinces`. Dùng trực tiếp, không cần JOIN qua dim_provinces chỉ để lấy vùng.
15. **Khách hàng mới:** `start_date` trong kỳ dữ liệu. Tăng trưởng của khách hàng hiện hữu (like-for-like) = lọc `start_date < đầu kỳ so sánh`.

---

## ĐƠN VỊ TIỀN TỆ VÀ KHỐI LƯỢNG

| Bảng | Cột | Đơn vị |
|------|-----|--------|
| fact_sales_lines | gross_amount_vnd, standard_discount_vnd, special_discount_vnd, net_amount_vnd, standard_cost_vnd, delivery_cost_vnd | VND, trước thuế GTGT |
| fact_sales_lines | list_price_per_kg | VND/kg |
| fact_sales_lines | quantity_kg | kg |
| fact_list_prices | list_price_per_kg | VND/kg |
| fact_product_costs | standard_cost_per_kg | VND/kg |
| fact_ar_snapshots | credit_limit_vnd, outstanding_vnd, not_due_vnd, overdue_* | VND |
| fact_sales_targets | target_quantity_tons | tấn |
| fact_sales_targets | target_net_revenue_vnd | VND |
| dim_customers | credit_limit_vnd | VND |
| dim_plants | design_capacity_tons_year | tấn/năm |
| ext_live_hog_prices | avg_price_per_kg | VND/kg heo hơi |
| ext_raw_material_prices | price_per_kg_vnd | VND/kg |

Format hiển thị:
- Tiền > 1 tỷ: "X,X tỷ"; < 1 tỷ: "XXX triệu".
- Sản lượng: "X nghìn tấn" hoặc "X tấn"; năm: "X,XX triệu tấn".
- Giá: "12.350 đ/kg".
- Phần trăm: 1 chữ số thập phân; chênh lệch tỷ lệ ghi "điểm %".

Quy mô tham chiếu để tự kiểm tra kết quả: sản lượng ~100–125 nghìn tấn/tháng; doanh thu thuần ~1.200–1.550 tỷ/tháng; giá thực bình quân ~12.000–12.800 đ/kg; biên lãi gộp ~10–14%.
