# DATABASE SCHEMA — Asia Foods Sales BI
## Database: `asiafoods_sales_demo` (MySQL 8.0, utf8mb4_unicode_ci)
## Phạm vi: 01/11/2024 – 30/04/2026 (18 tháng) | "Hiện tại" = cuối 30/04/2026

---

## TỔNG QUAN

Schema thiết kế phục vụ mảng kinh doanh Asia Foods Corporation — track sales-in từ NPP đến điểm bán cuối, hỗ trợ phân tích từ Doanh số tổng đến từng line item.

**Cấu trúc 3 cụm bảng:**

| Cụm | Số bảng | Vai trò |
|---|---|---|
| **Dimension tables** | 13 | Master data, hierarchies (sản phẩm, địa lý, khách hàng, kênh, campaign) |
| **Fact tables** | 7 | Transaction & event data (orders, lines, targets, ASO, MCP, visits, tier history) |
| **Metadata tables** | 4 | Schema documentation, KPI definitions, glossary (cho AI engine) |

**Tổng: 24 tables.**

---

## SƠ ĐỒ QUAN HỆ

```
dim_calendar (date_id PK)
  ├── fact_sales_orders.order_date
  ├── fact_aso_daily.snapshot_date
  ├── fact_mcp_new.open_date
  └── fact_visits.visit_date

dim_region (region_id PK) [MT1, MT2, MT3, MT4]
  ├── dim_province.region_id
  ├── dim_distributor.region_id
  ├── fact_targets.region_id
  ├── fact_aso_daily.region_id
  └── fact_mcp_new.region_id

dim_province (province_id PK) [24 tỉnh]
  ├── dim_distributor.province_id
  └── dim_route.province_id

dim_distributor (distributor_id PK) [200 NPP]
  ├── dim_route.distributor_id
  ├── dim_salesperson.distributor_id
  ├── fact_sales_orders.distributor_id
  └── fact_mcp_new.distributor_id

dim_salesperson (salesperson_id PK) [200 DSR]
  ├── dim_route.salesperson_id
  ├── fact_sales_orders.salesperson_id
  ├── fact_mcp_new.opened_by_salesperson
  └── fact_visits.salesperson_id

dim_route (route_id PK) [200 tuyến]
  ├── dim_customer.route_id
  ├── fact_sales_orders.route_id
  └── fact_visits.route_id

dim_customer_tier (tier_id PK) [Kim cương, Vàng, Bạc, Thường]
  (link tới dim_customer.customer_tier_current bằng string match)

dim_channel (channel_id PK) [GT, MT, HoReCa, Online, Canteen]
  ├── dim_customer.channel_id
  └── fact_sales_orders.channel_id

dim_customer (customer_id PK) [3,500 outlets]
  ├── fact_sales_orders.customer_id
  ├── fact_mcp_new.customer_id
  ├── fact_visits.customer_id
  └── fact_customer_tier_history.customer_id

dim_product_supergroup (supergroup_id PK) [3 nhóm]
  ├── dim_product_category.supergroup_id
  ├── fact_sales_lines.supergroup_id (denormalized)
  └── fact_targets.supergroup_id

dim_product_category (category_id PK) [12 sản phẩm]
  ├── dim_product_sku.category_id
  ├── fact_sales_lines.category_id (denormalized)
  └── fact_targets.category_id

dim_product_sku (sku_id PK) [38 SKUs, có flag is_crn]
  └── fact_sales_lines.sku_id

dim_campaign (campaign_id PK) [8 campaigns]
  ├── fact_sales_orders.campaign_id (nullable)
  └── fact_mcp_new.campaign_id (nullable)

fact_sales_orders (order_id PK) ⭐
  └── fact_sales_lines.order_id
```

---

## DIMENSION TABLES

### 1. `dim_calendar` (546 rows)

Calendar dimension cho 01/11/2024 – 30/04/2026.

| Cột | Kiểu | Mô tả | Ghi chú |
|-----|------|-------|---------|
| `date_id` | DATE PK | Ngày YYYY-MM-DD | **Key dùng JOIN với order_date / snapshot_date** |
| `day_of_week` | TINYINT | 0=Mon, 6=Sun | |
| `day_of_week_name` | VARCHAR(10) | "Thứ Hai", "Thứ Ba"… "Chủ Nhật" | Tiếng Việt |
| `week_of_year` | TINYINT | 1-53 | ISO week |
| `month` | TINYINT | 1-12 | |
| `quarter` | TINYINT | 1-4 | |
| `year` | SMALLINT | 2024-2026 | |
| `is_business_day` | BOOLEAN | TRUE cho Mon-Sat, FALSE cho Sun | DSR làm việc Mon-Sat |
| `fiscal_period` | VARCHAR(10) | "2025-Q1", "2026-Q2" | |
| `season_label` | VARCHAR(40) | "Tết", "Hè", "Back-to-school", "Pre-Tết", "Pre-Tết peak", "Mùa mưa", "Post-Tết", "Thường" | Phân loại mùa vụ ngành mì gói |

**Lọc Tết:** `WHERE season_label IN ('Tết')` hoặc `WHERE month IN (1, 2)`. Không có cột boolean `is_tet_period` riêng.

### 2. `dim_region` (4 rows)

| Cột | Kiểu | Mô tả |
|-----|------|-------|
| `region_id` | TINYINT PK | 1-4 |
| `region_code` | VARCHAR(8) | MT1, MT2, MT3, MT4 |
| `region_name` | VARCHAR(80) | Tiếng Việt |
| `factory_location` | VARCHAR(100) | Nhà máy phục vụ |

**Sample data:**
| region_id | region_code | region_name | factory_location |
|---|---|---|---|
| 1 | MT1 | Miền Bắc | Bắc Ninh – Tiên Du |
| 2 | MT2 | Miền Trung | Đà Nẵng – Hòa Khánh |
| 3 | MT3 | Miền Đông Nam Bộ | Bình Dương – An Phú & Nam Tân Uyên |
| 4 | MT4 | Miền Tây Nam Bộ | Bình Dương – Nam Tân Uyên (chi nhánh phục vụ Tây NB) |

### 3. `dim_province` (24 rows)

| Cột | Kiểu | Mô tả |
|-----|------|-------|
| `province_id` | SMALLINT PK | |
| `province_code` | VARCHAR(8) | HN, HCM, DNG, BD, HUE, KH, … |
| `province_name` | VARCHAR(80) | Tiếng Việt |
| `region_id` | TINYINT FK | → dim_region |
| `tier_city` | VARCHAR(10) | "Tier1", "Tier2", "Tier3" |
| `population` | INT | Dân số ước tính (người) |

**Province codes (lưu ý unique):**
- MT1: HN, HP, BN, BG, NDH, TH, NA, HT
- MT2: DNG (Đà Nẵng), QNM (Quảng Nam), KH (Khánh Hòa), HUE (Thừa Thiên Huế)
- MT3: HCM, BD, DNI (Đồng Nai), VT (Bà Rịa-Vũng Tàu), TN, LA, BP
- MT4: CT, AG, KG, ST, BL

### 4. `dim_distributor` (200 rows)

| Cột | Kiểu | Mô tả |
|-----|------|-------|
| `distributor_id` | SMALLINT PK | |
| `distributor_code` | VARCHAR(20) | NPP-MT3-HCM001, … |
| `distributor_name` | VARCHAR(150) | "NPP Á Châu Hà Nội", … |
| `region_id` | TINYINT FK | |
| `province_id` | SMALLINT FK | |
| `address` | VARCHAR(255) | |
| `start_date` | DATE | Ngày bắt đầu hợp tác |
| `status` | VARCHAR(20) | "Active" / "Inactive" |

**Phân bổ:** MT1:54 / MT2:30 / MT3:70 / MT4:46.

### 5. `dim_salesperson` (200 rows)

| Cột | Kiểu | Mô tả |
|-----|------|-------|
| `salesperson_id` | SMALLINT PK | |
| `employee_code` | VARCHAR(20) | EMP00001… |
| `salesperson_name` | VARCHAR(100) | Tên Việt |
| `distributor_id` | SMALLINT FK | DSR thuộc NPP |
| `hire_date` | DATE | |
| `status` | VARCHAR(20) | |

### 6. `dim_route` (200 rows)

| Cột | Kiểu | Mô tả | Ghi chú |
|-----|------|-------|---------|
| `route_id` | SMALLINT PK | | |
| `route_code` | VARCHAR(30) | "T1-HN-DX001", "T3-HCM-Q1003" | Format: T{region}-{province}-{area}{seq} |
| `route_name` | VARCHAR(150) | Tiếng Việt | |
| `distributor_id` | SMALLINT FK | | |
| `province_id` | SMALLINT FK | | |
| `salesperson_id` | SMALLINT FK | 1 DSR / tuyến | |
| `frequency` | VARCHAR(8) | "F4" / "F8" / "F12" | **Tần suất viếng thăm: F4=1 lần/tuần, F8=2 lần/tuần, F12=3 lần/tuần** |
| `area_type` | VARCHAR(20) | "urban" / "suburban" / "rural" | |

### 7. `dim_customer_tier` (4 rows)

| Cột | Kiểu | Mô tả |
|-----|------|-------|
| `tier_id` | TINYINT PK | |
| `tier_name` | VARCHAR(20) | "Kim cương" / "Vàng" / "Bạc" / "Thường" |
| `tier_rank` | TINYINT | 1=cao nhất, 4=thấp nhất |
| `min_monthly_revenue_vnd` | BIGINT | Ngưỡng doanh số/tháng |
| `min_visit_frequency` | VARCHAR(8) | "F12" / "F8" / "F4" / "F2" |

**Sample data:**
| tier_id | tier_name | tier_rank | min_monthly_revenue_vnd | min_visit_frequency |
|---|---|---|---|---|
| 1 | Kim cương | 1 | 50,000,000 | F12 |
| 2 | Vàng | 2 | 15,000,000 | F8 |
| 3 | Bạc | 3 | 5,000,000 | F4 |
| 4 | Thường | 4 | 0 | F2 |

### 8. `dim_channel` (5 rows)

| Cột | Kiểu | Mô tả |
|-----|------|-------|
| `channel_id` | TINYINT PK | |
| `channel_code` | VARCHAR(20) | "GT" / "MT" / "HoReCa" / "Online" / "Canteen" |
| `channel_name` | VARCHAR(50) | |
| `channel_type` | VARCHAR(30) | "General Trade" / "Modern Trade" / "Food Service" / "Online" |

**Sample data:**
| channel_id | channel_code | channel_name | channel_type |
|---|---|---|---|
| 1 | GT | General Trade | General Trade |
| 2 | MT | Modern Trade | Modern Trade |
| 3 | HoReCa | Hotel/Restaurant/Cafe | Food Service |
| 4 | Online | Online E-commerce | Online |
| 5 | Canteen | Canteen/B2B | Food Service |

### 9. `dim_customer` (3,500 rows)

Điểm bán (Outlet) — KH cuối của Asia Foods qua NPP.

| Cột | Kiểu | Mô tả | Ghi chú |
|-----|------|-------|---------|
| `customer_id` | INT PK | | |
| `customer_code` | VARCHAR(20) | KH000001, … | |
| `customer_name` | VARCHAR(255) | "Co.opmart Đà Nẵng", "Tạp hóa Chị Lan" | Tên thực |
| `route_id` | SMALLINT FK | | |
| `channel_id` | TINYINT FK | | |
| `customer_tier_current` | VARCHAR(20) | "Kim cương"/"Vàng"/"Bạc"/"Thường" | Tier hiện tại (string match với dim_customer_tier.tier_name) |
| `customer_tier_at_open` | VARCHAR(20) | Tier lúc mở mới | |
| `open_date` | DATE | Ngày mở mới (MCP date) | |
| `address` | VARCHAR(255) | | |
| `district` | VARCHAR(100) | Lưu province_code (HN, HCM, DNG…) | **JOIN với `dim_province.province_code`** |
| `latitude` | DECIMAL(10,7) | | |
| `longitude` | DECIMAL(10,7) | | |
| `status` | VARCHAR(20) | "Active" / "Inactive" / "Churn" | |

⚠️ **Khi lọc KH "Kim cương":** dùng `customer_tier_current = 'Kim cương'`. Để xem KH "đã từng Kim cương" → JOIN với `fact_customer_tier_history`.

### 10. `dim_product_supergroup` (3 rows)

3 nhóm sản phẩm theo cấu trúc báo cáo Asia Foods.

| Cột | Kiểu | Mô tả |
|-----|------|-------|
| `supergroup_id` | TINYINT PK | 1-3 |
| `supergroup_name` | VARCHAR(150) | Tên đầy đủ (đã gộp mô tả) |
| `report_label` | VARCHAR(60) | "Nhóm 1" / "Nhóm 2" / "Nhóm 3" (hiển thị cấu trúc báo cáo) |

**Sample data (ACTUAL):**
| supergroup_id | supergroup_name | report_label |
|---|---|---|
| 1 | Mì chủ lực (Mì Gấu, Mì Trứng Vàng) | Nhóm 1 |
| 2 | Cháo cao cấp (Cháo Gấu Trừ CRN, Cháo Yến, Cháo Ly Yến) | Nhóm 2 |
| 3 | Sản phẩm tiềm năng | Nhóm 3 |

⚠️ **Khi báo cáo theo supergroup 2 ("Cháo Gấu Trừ CRN, …"):** filter `dim_product_sku.is_crn = 0` cho Cháo Gấu. CRN bị exclude khỏi nhóm 2.

### 11. `dim_product_category` (12 rows)

| Cột | Kiểu | Mô tả |
|-----|------|-------|
| `category_id` | TINYINT PK | 1-12 |
| `category_name` | VARCHAR(100) | "Mì Gấu", "Mì Gấu Cay", "Mì Trứng Vàng", … |
| `supergroup_id` | TINYINT FK | |
| `launch_date` | DATE | Mì Gấu Cay = 2025-11-01 (mới) |
| `status` | VARCHAR(20) | |

**Sample data (mapping category → supergroup):**
| category_id | category_name | supergroup_id (label) |
|---|---|---|
| 1 | Mì Gấu | 1 (Nhóm 1) |
| 2 | Mì Gấu Cay | 1 (Nhóm 1) |
| 3 | Mì Trứng Vàng | 1 (Nhóm 1) |
| 4 | Mì Ly Gấu | 1 (Nhóm 1) |
| 5 | Cháo Gấu | 2 (Nhóm 2) |
| 6 | Cháo Asim | 3 (Nhóm 3) |
| 7 | Cháo Yến | 2 (Nhóm 2) |
| 8 | Cháo Dinh Dưỡng | 3 (Nhóm 3) |
| 9 | Cháo Ly Yến | 2 (Nhóm 2) |
| 10 | Cháo Ly Asim | 3 (Nhóm 3) |
| 11 | Phở Gấu | 3 (Nhóm 3) |
| 12 | Hủ Tiếu Gấu | 3 (Nhóm 3) |

### 12. `dim_product_sku` (38 rows)

| Cột | Kiểu | Mô tả | Ghi chú |
|-----|------|-------|---------|
| `sku_id` | SMALLINT PK | | |
| `sku_code` | VARCHAR(30) | "SKU00001" … | |
| `sku_name` | VARCHAR(150) | "Mì Gấu Bò 65g" … | |
| `category_id` | TINYINT FK | | |
| `is_crn` | BOOLEAN | TRUE cho 2 SKU Cháo Gấu CRN (Cá Hồi, Yến Sào) | **Quan trọng filter Nhóm 2** |
| `pack_size_g` | SMALLINT | 50, 65, 70, 75, 40 | gram |
| `unit_price_vnd` | INT | Giá lẻ tham khảo | VND |
| `launch_date` | DATE | | |
| `status` | VARCHAR(20) | | |

### 13. `dim_campaign` (8 rows)

| Cột | Kiểu | Mô tả |
|-----|------|-------|
| `campaign_id` | SMALLINT PK | |
| `campaign_code` | VARCHAR(30) | "CAMP-2026-TET" … |
| `campaign_name` | VARCHAR(150) | "Tết Sum Vầy Cùng Gấu Đỏ 2026" … |
| `campaign_type` | VARCHAR(30) | "Tết" / "Hè" / "BTS" / "Tactical" / "Launch" |
| `start_date` | DATE | |
| `end_date` | DATE | |
| `total_budget_vnd` | BIGINT | Tổng ngân sách VND |
| `target_regions` | VARCHAR(60) | Comma-separated: "MT1,MT2,MT3,MT4" hoặc subset |
| `target_categories` | VARCHAR(255) | "ALL" hoặc comma-separated category_name |
| `status` | VARCHAR(20) | "Completed" / "Running" |

**Note:** Không có breakdown ngân sách thành discount / display / KOL ở mức database — chỉ có `total_budget_vnd`. Nếu cần breakdown, xem campaign business context riêng.

**Sample data:**
| campaign_code | campaign_name | type | period | budget (tỷ) | target_regions |
|---|---|---|---|---|---|
| CAMP-2025-TET | Khai Xuân May Mắn 2025 | Tết | T1-T2/2025 | 9.8 | All |
| CAMP-2025-SUM | Hè Sảng Khoái 2025 | Hè | T5-T6/2025 | 4.5 | MT3,MT4 |
| CAMP-2025-BTS | Back to School 2025 | BTS | T8-T9/2025 | 3.8 | All |
| CAMP-2025-BD | Sinh Nhật Asia Foods | Tactical | T10/2025 | 2.2 | All |
| CAMP-2025-LAU | Mì Gấu Cay Launch | Launch | T11-T12/2025 | 5.5 | All |
| CAMP-2026-TET | Tết Sum Vầy Cùng Gấu Đỏ 2026 | Tết | T1-T2/2026 | 12.0 | All |
| CAMP-2026-CLY | Cháo Ly Yến Premium Push | Tactical | T3/2026 | 1.8 | MT3 |
| CAMP-2026-Q2 | Tháng Khuyến Mãi Q2 | Tactical | T4/2026 | 2.5 | MT1,MT2 |

---

## FACT TABLES

### 14. `fact_sales_orders` ⭐ (297,075 rows)

Đơn hàng đặt từ điểm bán (1 dòng = 1 đơn).

| Cột | Kiểu | Mô tả | Đơn vị |
|-----|------|-------|--------|
| `order_id` | BIGINT PK | | |
| `order_code` | VARCHAR(30) | "ORD00000001" … | |
| `order_date` | DATE | → dim_calendar.date_id | |
| `customer_id` | INT FK | | |
| `distributor_id` | SMALLINT FK | | |
| `route_id` | SMALLINT FK | | |
| `salesperson_id` | SMALLINT FK | DSR tạo đơn | |
| `channel_id` | TINYINT FK | | |
| `campaign_id` | SMALLINT FK NULL | NULL nếu đơn không thuộc campaign | |
| `order_status` | VARCHAR(20) | "ĐHTC" / "Pending" / "Cancelled" | **LUÔN filter ĐHTC khi tính DT** |
| `total_amount_vnd` | BIGINT | **Doanh số NET (đã trừ chiết khấu)** | VND |
| `total_volume_packs` | INT | Tổng số gói trong đơn | |
| `total_skus` | TINYINT | Số SKU khác nhau trong đơn (KPI SKU/đơn) | |
| `created_at` | DATETIME | | |

⚠️ **Cột `total_amount_vnd` ĐÃ là NET (sau chiết khấu).** Không có cột gross / discount riêng ở order header — drill xuống `fact_sales_lines` nếu cần breakdown gross/discount.

### 15. `fact_sales_lines` ⭐⭐ (1,454,104 rows — FACT CHÍNH)

Chi tiết từng line trong đơn (1 dòng = 1 SKU trong 1 đơn).

| Cột | Kiểu | Mô tả | Đơn vị |
|-----|------|-------|--------|
| `line_id` | BIGINT PK | | |
| `order_id` | BIGINT FK | → fact_sales_orders | |
| `sku_id` | SMALLINT FK | | |
| `category_id` | TINYINT FK | **Denormalized** for performance | |
| `supergroup_id` | TINYINT FK | **Denormalized** for performance | |
| `quantity_packs` | INT | Số gói | |
| `unit_price_vnd` | INT | Đơn giá (có biến động theo vùng/thời gian, ±5%) | VND |
| `line_amount_vnd` | BIGINT | = quantity × unit_price (GROSS, trước chiết khấu) | VND |
| `discount_amount_vnd` | BIGINT | Chiết khấu line | VND |
| `net_amount_vnd` | BIGINT | = line_amount - discount (đã apply campaign lift nếu có) | VND |

⚠️ **CHÍNH:** Luôn dùng `net_amount_vnd` cho doanh thu thuần. `line_amount_vnd` là gross trước chiết khấu.

### 16. `fact_targets` (888 rows)

Chỉ tiêu (CT) theo tháng × miền × category (hoặc region-level khi category NULL).

| Cột | Kiểu | Mô tả |
|-----|------|-------|
| `target_id` | INT PK | |
| `period_year` | SMALLINT | 2024-2026 |
| `period_month` | TINYINT | 1-12 |
| `region_id` | TINYINT FK | (NOT NULL) |
| `category_id` | TINYINT FK NULL | NULL = region-level target |
| `supergroup_id` | TINYINT FK NULL | NULL (chưa dùng — supergroup target derive từ category) |
| `target_revenue_vnd` | BIGINT | CT doanh thu VND |
| `target_volume_packs` | INT | CT volume gói |
| `target_mcp_new` | SMALLINT | CT mở mới KH (chỉ ở row region-level) |
| `target_aso_pct` | DECIMAL(5,2) | CT ASO % (chỉ ở row region-level) |

⚠️ **2 grain riêng biệt — tránh double count:**
- Region-level: `region_id` NOT NULL, `category_id` IS NULL → dùng cho %TH tổng miền
- Category-level: `region_id` NOT NULL, `category_id` NOT NULL → dùng cho %TH category × region

### 17. `fact_aso_daily` (1,872 rows)

Snapshot daily về ASO và operational KPIs theo (date × region).

| Cột | Kiểu | Mô tả | Đơn vị |
|-----|------|-------|--------|
| `aso_id` | INT PK | Surrogate | |
| `snapshot_date` | DATE | → dim_calendar | |
| `region_id` | TINYINT FK | | |
| `total_outlets` | INT | Tổng outlets thuộc region | |
| `active_outlets` | INT | Outlets có giao dịch ngày đó | |
| `aso_pct` | DECIMAL(5,2) | = active / total × 100 | % |
| `dhtc_count` | INT | ĐHTC trong ngày | |
| `sku_per_order_avg` | DECIMAL(4,2) | BQ SKU/đơn trong ngày | |

⚠️ **Không có cột `bq_dhtc_per_dsr` riêng** — compute on-the-fly:
```sql
SELECT region_id, SUM(dhtc_count)/COUNT(DISTINCT snapshot_date) / 
       (SELECT COUNT(*) FROM dim_salesperson WHERE distributor_id IN 
        (SELECT distributor_id FROM dim_distributor WHERE region_id = X)) AS bq_dhtc_per_dsr
FROM fact_aso_daily WHERE snapshot_date BETWEEN ... GROUP BY region_id;
```

⚠️ **`fact_aso_daily` là SNAPSHOT, không cumulative.** Filter theo `snapshot_date`, không SUM nhiều ngày.

### 18. `fact_mcp_new` (182 rows)

KH mới mở (MCP — Master Coverage Planning).

| Cột | Kiểu | Mô tả |
|-----|------|-------|
| `mcp_id` | INT PK | |
| `open_date` | DATE | Ngày mở |
| `customer_id` | INT FK | |
| `distributor_id` | SMALLINT FK | |
| `region_id` | TINYINT FK | |
| `opened_by_salesperson` | SMALLINT FK | DSR mở |
| `first_order_amount_vnd` | BIGINT | Doanh số đơn đầu tiên (NULL → 0 nếu chưa có đơn) | VND |
| `campaign_id` | SMALLINT FK NULL | Attribution campaign (NULL nếu không) |

⚠️ **Không có cột `is_active_60d` hoặc `first_order_date` riêng** — compute on-the-fly:
```sql
-- MCP "active 60d" = có ít nhất 1 ĐHTC trong 60 ngày từ open_date
SELECT mcp.* FROM fact_mcp_new mcp
WHERE EXISTS (
  SELECT 1 FROM fact_sales_orders o
  WHERE o.customer_id = mcp.customer_id
    AND o.order_date BETWEEN mcp.open_date AND DATE_ADD(mcp.open_date, INTERVAL 60 DAY)
    AND o.order_status = 'ĐHTC'
);
```

### 19. `fact_visits` (114,848 rows)

Lịch sử viếng thăm DSR (chỉ KH Kim cương + Vàng được track ở granularity ngày).

| Cột | Kiểu | Mô tả |
|-----|------|-------|
| `visit_id` | BIGINT PK | |
| `visit_date` | DATE | |
| `customer_id` | INT FK | |
| `salesperson_id` | SMALLINT FK | DSR viếng thăm |
| `route_id` | SMALLINT FK | |
| `visit_result` | VARCHAR(30) | "Có đơn" / "Không đơn" / "Đóng cửa" |
| `order_id` | BIGINT FK NULL | Order tạo từ visit (NULL nếu Không đơn / Đóng cửa) |

⚠️ **Chỉ track Kim cương + Vàng** — KH Bạc/Thường viếng thăm theo F4/F2 nhưng không có row visit cụ thể. Tần suất đặt hàng cho Bạc/Thường suy từ khoảng cách giữa các `order_date` trong `fact_sales_orders`.

### 20. `fact_customer_tier_history` (50 rows)

Lịch sử thay đổi tier KH (rớt/lên hạng).

| Cột | Kiểu | Mô tả |
|-----|------|-------|
| `history_id` | INT PK | |
| `customer_id` | INT FK | |
| `change_date` | DATE | |
| `tier_before` | VARCHAR(20) | Tier cũ ("Kim cương" / "Vàng" / "Bạc" / "Thường") |
| `tier_after` | VARCHAR(20) | Tier mới |
| `change_reason` | VARCHAR(100) | Lý do, ví dụ "Doanh số 6 tháng vượt ngưỡng Kim cương" |
| `triggered_by` | VARCHAR(50) | "auto_review" / "manual" |

⚠️ **Không có cột `change_type` (Promotion/Demotion) riêng** — compute on-the-fly bằng cách so sánh tier_rank của `tier_before` vs `tier_after` qua dim_customer_tier:
```sql
SELECT h.*,
       CASE WHEN tb.tier_rank > ta.tier_rank THEN 'Promotion'
            WHEN tb.tier_rank < ta.tier_rank THEN 'Demotion'
            ELSE 'Lateral' END AS change_type
FROM fact_customer_tier_history h
JOIN dim_customer_tier tb ON h.tier_before = tb.tier_name
JOIN dim_customer_tier ta ON h.tier_after = ta.tier_name;
```
(tier_rank: 1=Kim cương, 2=Vàng, 3=Bạc, 4=Thường — số nhỏ = tier cao hơn.)

---

## METADATA TABLES

### 21. `_meta_tables` (24 rows)
| Cột | Kiểu |
|-----|------|
| `table_name` | VARCHAR(100) PK |
| `description_vi` | TEXT |
| `description_en` | TEXT |
| `business_context` | TEXT |
| `row_count_est` | INT |

### 22. `_meta_columns` (26 rows)
| Cột | Kiểu |
|-----|------|
| `id` | INT PK AUTO_INCREMENT |
| `table_name` | VARCHAR(100) |
| `column_name` | VARCHAR(100) |
| `data_type` | VARCHAR(50) |
| `description_vi` | TEXT |
| `description_en` | TEXT |
| `unit` | VARCHAR(50) |
| `example_values` | TEXT |

### 23. `_meta_kpi` (12 rows)
| Cột | Kiểu |
|-----|------|
| `kpi_name` | VARCHAR(100) PK |
| `kpi_name_en` | VARCHAR(100) |
| `formula_sql` | TEXT |
| `description_vi` | TEXT |
| `related_questions` | TEXT |
| `unit` | VARCHAR(50) |

### 24. `_meta_glossary` (23 rows)
| Cột | Kiểu |
|-----|------|
| `term_vi` | VARCHAR(100) PK |
| `term_en` | VARCHAR(100) |
| `definition` | TEXT |
| `abbreviation` | VARCHAR(20) |

---

## SQL TEMPLATES

### Template 1: Doanh số theo nhóm hàng / category vs CT trong tháng X

```sql
SELECT 
    sg.report_label,
    sg.supergroup_name,
    pc.category_name,
    ROUND(SUM(fsl.net_amount_vnd) / 1e9, 2) AS th_billion_vnd,
    ROUND((SELECT SUM(ft.target_revenue_vnd) / 1e9
           FROM fact_targets ft 
           WHERE ft.period_year=2026 AND ft.period_month=4 
             AND ft.category_id=pc.category_id), 2) AS ct_billion_vnd,
    ROUND(SUM(fsl.net_amount_vnd) /
          NULLIF((SELECT SUM(ft.target_revenue_vnd) 
                  FROM fact_targets ft 
                  WHERE ft.period_year=2026 AND ft.period_month=4 
                    AND ft.category_id=pc.category_id), 0) * 100, 1) AS pct_th
FROM fact_sales_lines fsl
JOIN fact_sales_orders fso ON fsl.order_id = fso.order_id
JOIN dim_product_category pc ON fsl.category_id = pc.category_id
JOIN dim_product_supergroup sg ON pc.supergroup_id = sg.supergroup_id
WHERE fso.order_date BETWEEN '2026-04-01' AND '2026-04-30'
  AND fso.order_status = 'ĐHTC'
GROUP BY sg.supergroup_id, pc.category_id
ORDER BY sg.supergroup_id, th_billion_vnd DESC;
```

### Template 2: Doanh số theo Miền vs CT region-level

```sql
SELECT 
    r.region_code, r.region_name,
    ROUND(SUM(fsl.net_amount_vnd) / 1e9, 1) AS th_billion,
    ROUND((SELECT SUM(ft.target_revenue_vnd) / 1e9
           FROM fact_targets ft 
           WHERE ft.period_year=2026 AND ft.period_month=4 
             AND ft.region_id=r.region_id 
             AND ft.category_id IS NULL), 1) AS ct_billion,
    ROUND(SUM(fsl.net_amount_vnd) /
          NULLIF((SELECT SUM(ft.target_revenue_vnd)
                  FROM fact_targets ft 
                  WHERE ft.period_year=2026 AND ft.period_month=4 
                    AND ft.region_id=r.region_id 
                    AND ft.category_id IS NULL), 0) * 100, 1) AS pct_th
FROM fact_sales_lines fsl
JOIN fact_sales_orders fso ON fsl.order_id = fso.order_id
JOIN dim_distributor d ON fso.distributor_id = d.distributor_id
JOIN dim_region r ON d.region_id = r.region_id
WHERE fso.order_date BETWEEN '2026-04-01' AND '2026-04-30'
  AND fso.order_status = 'ĐHTC'
GROUP BY r.region_id
ORDER BY r.region_id;
```

### Template 3: Cháo Gấu (Trừ CRN) — filter is_crn=0

```sql
SELECT 
    pc.category_name,
    ROUND(SUM(CASE WHEN sku.is_crn = 0 THEN fsl.net_amount_vnd ELSE 0 END) / 1e9, 2) AS chao_gau_exc_crn_billion,
    ROUND(SUM(CASE WHEN sku.is_crn = 1 THEN fsl.net_amount_vnd ELSE 0 END) / 1e9, 2) AS chao_gau_crn_only_billion,
    ROUND(SUM(fsl.net_amount_vnd) / 1e9, 2) AS chao_gau_total_billion
FROM fact_sales_lines fsl
JOIN fact_sales_orders fso ON fsl.order_id = fso.order_id
JOIN dim_product_sku sku ON fsl.sku_id = sku.sku_id
JOIN dim_product_category pc ON fsl.category_id = pc.category_id
WHERE pc.category_name = 'Cháo Gấu'
  AND fso.order_date BETWEEN '2026-04-01' AND '2026-04-30'
  AND fso.order_status = 'ĐHTC'
GROUP BY pc.category_id;
```

### Template 4: KH chuyển từ SKU A sang SKU B (cannibalization detection)

```sql
-- Scenario 2: 12 KH chuyển từ Mì Trứng Vàng sang Mì Gấu Cay
WITH customer_shift AS (
    SELECT 
        c.customer_id, c.customer_name, c.customer_tier_current,
        SUM(CASE WHEN pc.category_name='Mì Trứng Vàng' 
                  AND fso.order_date < '2025-11-01' 
            THEN fsl.quantity_packs ELSE 0 END) AS mtv_before_nov2025,
        SUM(CASE WHEN pc.category_name='Mì Trứng Vàng' 
                  AND fso.order_date >= '2025-11-01' 
            THEN fsl.quantity_packs ELSE 0 END) AS mtv_after_nov2025,
        SUM(CASE WHEN pc.category_name='Mì Gấu Cay' 
                  AND fso.order_date >= '2025-11-01' 
            THEN fsl.quantity_packs ELSE 0 END) AS mgc_after_nov2025
    FROM dim_customer c
    JOIN fact_sales_orders fso ON c.customer_id = fso.customer_id
    JOIN fact_sales_lines fsl ON fso.order_id = fsl.order_id
    JOIN dim_product_category pc ON fsl.category_id = pc.category_id
    WHERE c.customer_tier_current IN ('Kim cương', 'Vàng')
      AND fso.order_status = 'ĐHTC'
    GROUP BY c.customer_id
    HAVING mtv_before_nov2025 > 100 
       AND mtv_after_nov2025 < mtv_before_nov2025 * 0.2
       AND mgc_after_nov2025 > mtv_before_nov2025 * 0.5
)
SELECT * FROM customer_shift ORDER BY mtv_before_nov2025 DESC;
```

### Template 5: Phân tích nguồn growth — MCP mới vs KH cũ vs Spike

```sql
-- MT3 vs MT1 → breakdown growth source
SELECT 
    r.region_code,
    ROUND(SUM(fsl.net_amount_vnd) / 1e9, 1) AS total_billion,
    ROUND(SUM(CASE WHEN c.open_date >= '2026-01-01' 
        THEN fsl.net_amount_vnd ELSE 0 END) / 1e9, 1) AS new_outlet_billion,
    ROUND(SUM(CASE WHEN c.open_date < '2026-01-01' 
        THEN fsl.net_amount_vnd ELSE 0 END) / 1e9, 1) AS existing_outlet_billion,
    COUNT(DISTINCT CASE WHEN c.open_date BETWEEN '2026-01-01' AND '2026-04-30' 
        THEN c.customer_id END) AS new_outlets_q1
FROM fact_sales_lines fsl
JOIN fact_sales_orders fso ON fsl.order_id = fso.order_id
JOIN dim_customer c ON fso.customer_id = c.customer_id
JOIN dim_distributor d ON fso.distributor_id = d.distributor_id
JOIN dim_region r ON d.region_id = r.region_id
WHERE fso.order_date BETWEEN '2026-04-01' AND '2026-04-30'
  AND fso.order_status = 'ĐHTC'
  AND r.region_code IN ('MT1', 'MT3')
GROUP BY r.region_id
ORDER BY r.region_code;

-- Single-day spike: tìm các ngày có volume bất thường (>2× daily avg)
SELECT order_date, SUM(total_amount_vnd) / 1e9 AS daily_billion
FROM fact_sales_orders
WHERE order_date BETWEEN '2026-04-01' AND '2026-04-30'
  AND order_status = 'ĐHTC'
GROUP BY order_date
ORDER BY daily_billion DESC LIMIT 5;
```

### Template 6: Campaign ROI comparison

```sql
WITH campaign_perf AS (
    SELECT 
        cam.campaign_id, cam.campaign_name,
        cam.total_budget_vnd / 1e9 AS budget_billion,
        cam.start_date, cam.end_date,
        SUM(fsl.net_amount_vnd) / 1e9 AS revenue_during_billion,
        -- Baseline: 2 tháng trước campaign (proportional cho campaign duration)
        (SELECT SUM(fsl2.net_amount_vnd) / 1e9
         FROM fact_sales_lines fsl2
         JOIN fact_sales_orders fso2 ON fsl2.order_id = fso2.order_id
         WHERE fso2.order_date BETWEEN 
            DATE_SUB(cam.start_date, INTERVAL 2 MONTH) 
            AND DATE_SUB(cam.start_date, INTERVAL 1 DAY)
           AND fso2.order_status = 'ĐHTC'
        ) AS baseline_2m_billion
    FROM dim_campaign cam
    LEFT JOIN fact_sales_orders fso ON fso.campaign_id = cam.campaign_id
    LEFT JOIN fact_sales_lines fsl ON fso.order_id = fsl.order_id
    WHERE cam.campaign_type = 'Tết'
    GROUP BY cam.campaign_id
)
SELECT 
    campaign_name,
    budget_billion,
    revenue_during_billion,
    ROUND(revenue_during_billion - baseline_2m_billion * 
          DATEDIFF(end_date, start_date)/60, 1) AS incremental_billion,
    ROUND((revenue_during_billion - baseline_2m_billion * 
           DATEDIFF(end_date, start_date)/60) / NULLIF(budget_billion, 0), 1) AS roi_x
FROM campaign_perf
ORDER BY start_date DESC;
```

### Template 7: KH Kim cương declining 6 tháng

```sql
WITH monthly_vol AS (
    SELECT 
        c.customer_id, c.customer_name, r.region_code, ch.channel_code,
        DATE_FORMAT(fso.order_date, '%Y-%m') AS yyyymm,
        SUM(fsl.quantity_packs) AS monthly_packs,
        SUM(fsl.net_amount_vnd) / 1e6 AS monthly_revenue_million,
        AVG(fso.total_skus) AS avg_skus_per_order
    FROM dim_customer c
    JOIN fact_sales_orders fso ON c.customer_id = fso.customer_id
    JOIN fact_sales_lines fsl ON fso.order_id = fsl.order_id
    JOIN dim_distributor d ON fso.distributor_id = d.distributor_id
    JOIN dim_region r ON d.region_id = r.region_id
    JOIN dim_channel ch ON c.channel_id = ch.channel_id
    WHERE c.customer_tier_current = 'Kim cương'
      AND ch.channel_code = 'MT'                  -- ⚠️ Filter MT để loại random GT-Kim cương
      AND fso.order_status = 'ĐHTC'
    GROUP BY c.customer_id, yyyymm
),
trend AS (
    SELECT 
        customer_id, customer_name, region_code,
        AVG(CASE WHEN yyyymm BETWEEN '2025-09' AND '2025-10' THEN monthly_packs END) AS baseline_avg,
        AVG(CASE WHEN yyyymm BETWEEN '2026-03' AND '2026-04' THEN monthly_packs END) AS recent_avg,
        AVG(CASE WHEN yyyymm BETWEEN '2026-03' AND '2026-04' THEN avg_skus_per_order END) AS recent_skus
    FROM monthly_vol
    GROUP BY customer_id
)
SELECT 
    customer_id, customer_name, region_code,
    ROUND(baseline_avg, 0) AS baseline_packs,
    ROUND(recent_avg, 0) AS recent_packs,
    ROUND((recent_avg - baseline_avg) / NULLIF(baseline_avg, 0) * 100, 1) AS volume_change_pct,
    ROUND(recent_skus, 1) AS recent_sku_per_order
FROM trend
WHERE recent_avg < baseline_avg * 0.8
ORDER BY volume_change_pct ASC LIMIT 10;
```

### Template 8: ASO & ĐHTC theo Miền

```sql
-- ASO + ĐHTC + SKU/đơn theo Miền (snapshot trung bình tháng)
-- BQ ĐHTC/DSR computed on-the-fly
SELECT 
    r.region_code,
    AVG(faso.aso_pct) AS avg_aso_pct,
    SUM(faso.dhtc_count) AS total_dhtc,
    AVG(faso.sku_per_order_avg) AS avg_sku_per_order,
    -- BQ ĐHTC/Ngày/DSR
    SUM(faso.dhtc_count) / COUNT(DISTINCT faso.snapshot_date) /
        (SELECT COUNT(*) FROM dim_salesperson sp
         JOIN dim_distributor d ON sp.distributor_id = d.distributor_id
         WHERE d.region_id = r.region_id) AS bq_dhtc_per_dsr_per_day
FROM fact_aso_daily faso
JOIN dim_region r ON faso.region_id = r.region_id
WHERE faso.snapshot_date BETWEEN '2026-04-01' AND '2026-04-30'
GROUP BY r.region_id
ORDER BY r.region_id;
```

### Template 9: Tier change history với change_type computed

```sql
-- KH rớt hạng trong Q1/2026
SELECT 
    h.history_id, c.customer_name, h.change_date,
    h.tier_before, h.tier_after, h.change_reason,
    CASE WHEN tb.tier_rank > ta.tier_rank THEN 'Promotion'
         WHEN tb.tier_rank < ta.tier_rank THEN 'Demotion'
         ELSE 'Lateral' END AS change_type
FROM fact_customer_tier_history h
JOIN dim_customer c ON h.customer_id = c.customer_id
JOIN dim_customer_tier tb ON h.tier_before = tb.tier_name
JOIN dim_customer_tier ta ON h.tier_after = ta.tier_name
WHERE h.change_date BETWEEN '2026-01-01' AND '2026-03-31'
ORDER BY h.change_date DESC;
```

### Template 10: MCP active 60d (compute is_active_60d)

```sql
-- MCP mới mở trong tháng X có active trong 60 ngày
SELECT 
    r.region_code,
    COUNT(*) AS mcp_total,
    SUM(CASE WHEN EXISTS (
        SELECT 1 FROM fact_sales_orders o 
        WHERE o.customer_id = mcp.customer_id
          AND o.order_date BETWEEN mcp.open_date AND DATE_ADD(mcp.open_date, INTERVAL 60 DAY)
          AND o.order_status = 'ĐHTC'
    ) THEN 1 ELSE 0 END) AS mcp_active_60d
FROM fact_mcp_new mcp
JOIN dim_region r ON mcp.region_id = r.region_id
WHERE mcp.open_date BETWEEN '2026-01-01' AND '2026-03-31'
GROUP BY r.region_id;
```

---

## JOIN WARNINGS

### Warning 1: `fact_sales_orders` → `fact_sales_lines` — Grain Difference

`fact_sales_orders` 1 dòng = 1 đơn. `fact_sales_lines` 1 dòng = 1 SKU/đơn (multiple lines per order).

❌ **SAI:**
```sql
SELECT SUM(fso.total_amount_vnd) 
FROM fact_sales_orders fso 
JOIN fact_sales_lines fsl ON fso.order_id = fsl.order_id;
-- SAI vì SUM(total_amount_vnd) bị nhân với số lines/order
```

✅ **ĐÚNG:**
```sql
-- Cách 1: SUM net_amount_vnd từ fact_sales_lines (granular)
SELECT SUM(fsl.net_amount_vnd) FROM fact_sales_lines fsl 
JOIN fact_sales_orders fso ON fsl.order_id=fso.order_id
WHERE fso.order_status='ĐHTC' ...

-- Cách 2: SUM total_amount_vnd từ fact_sales_orders (đã net) — KHÔNG JOIN với lines
SELECT SUM(total_amount_vnd) FROM fact_sales_orders 
WHERE order_status='ĐHTC' ...
```

### Warning 2: `dim_customer.customer_tier_current` vs `fact_customer_tier_history`

`customer_tier_current` là tier HIỆN TẠI (snapshot). Nếu CEO hỏi "KH NÀO đã từng Kim cương rồi rớt xuống Vàng" — JOIN với `fact_customer_tier_history`:

✅ **KH vẫn Kim cương nhưng volume đang giảm (cảnh báo sớm):**
```sql
WHERE c.customer_tier_current = 'Kim cương'
  AND recent_volume < baseline_volume * 0.8;
```

✅ **KH đã thực sự bị demote:**
```sql
SELECT h.* FROM fact_customer_tier_history h
JOIN dim_customer_tier tb ON h.tier_before = tb.tier_name
JOIN dim_customer_tier ta ON h.tier_after = ta.tier_name
WHERE tb.tier_rank < ta.tier_rank  -- rớt hạng (rank tăng)
  AND h.change_date >= '2026-01-01';
```

### Warning 3: `fact_aso_daily` là SNAPSHOT

KHÔNG SUM nhiều snapshot — chỉ AVG hoặc filter ngày cụ thể.

❌ **SAI:** `SELECT SUM(active_outlets) FROM fact_aso_daily WHERE snapshot_date BETWEEN ...` 
✅ **ĐÚNG:** `SELECT AVG(aso_pct) FROM fact_aso_daily WHERE snapshot_date BETWEEN ...`

### Warning 4: `fact_sales_orders.campaign_id` có NULL

Không phải order nào cũng thuộc campaign. Dùng `LEFT JOIN` hoặc `COALESCE`.

### Warning 5: `fact_targets.category_id` và `supergroup_id` có NULL

CT có 2 grain:
- Region-level: `region_id` NOT NULL, `category_id` IS NULL
- Category-level: `region_id` NOT NULL, `category_id` NOT NULL

❌ **SAI:** SUM cả 2 grain → double count.
✅ **ĐÚNG:** Chọn 1 grain phù hợp với câu hỏi:
- Hỏi "CT tổng miền" → `WHERE category_id IS NULL`
- Hỏi "CT theo category" → `WHERE category_id IS NOT NULL`

### Warning 6: `dim_customer.district` lưu province_code

`district` không phải tên quận/huyện chi tiết mà là province_code (HN, HCM, DNG…). Để JOIN tỉnh:
```sql
JOIN dim_province p ON c.district = p.province_code
```

### Warning 7: `dim_customer.status = 'Churn'` (không phải 'Churned')

KH inactive có status `'Churn'`. Default filter:
```sql
WHERE c.status = 'Active'
```

### Warning 8: `fact_visits` chỉ track KC + Vàng

`fact_visits` chỉ có row cho KH Kim cương + Vàng (~745 KH × ~10 visits/tháng). KH Bạc/Thường không có visit records — frequency suy từ `order_date` intervals trong `fact_sales_orders`.

---

## ĐƠN VỊ TIỀN TỆ

| Bảng | Cột | Đơn vị |
|------|-----|--------|
| `fact_sales_orders` | `total_amount_vnd` | VND (net, đã trừ chiết khấu) |
| `fact_sales_lines` | `unit_price_vnd`, `line_amount_vnd` (gross), `discount_amount_vnd`, `net_amount_vnd` | VND |
| `fact_targets` | `target_revenue_vnd` | VND |
| `dim_campaign` | `total_budget_vnd` | VND |
| `dim_customer_tier` | `min_monthly_revenue_vnd` | VND |
| `dim_product_sku` | `unit_price_vnd` | VND |
| `fact_mcp_new` | `first_order_amount_vnd` | VND |

**Format hiển thị cho CEO/Board:**
- ≥ 1 tỷ VND: "X,X tỷ" (vd "92,3 tỷ", "1.425 tỷ")
- ≥ 1 triệu VND: "XXX triệu"
- < 1 triệu: số nguyên với phân cách
- Phần trăm: 1 chữ số thập phân ("55,9%")
- Volume: "X,XXX gói" / "X.X nghìn gói" / "XX triệu gói"

**Quy đổi nhanh:**
- 1 thùng mì = 30 gói (industry standard)
- Giá lẻ TB 1 gói ~4,500–9,000 VND

---

## TIME RANGE & FISCAL CALENDAR

- **Data range:** 01/11/2024 – 30/04/2026 (546 business+non-business days, ~468 business days, 18 months)
- **"Hiện tại" trong demo:** cuối 30/04/2026
- **Tết 2025:** 28/01/2025 (mùng 1)
- **Tết 2026:** 17/02/2026 (mùng 1)
- **Mì Gấu Cay launch date:** 2025-11-01 (quan trọng cho Scenario 2 cannibalization)
- **Fiscal year:** Dương lịch (Jan-Dec)

## ROW COUNTS THỰC TẾ

| Bảng | Rows |
|---|---|
| `dim_calendar` | 546 |
| `dim_region` | 4 |
| `dim_province` | 24 |
| `dim_distributor` | 200 |
| `dim_salesperson` | 200 |
| `dim_route` | 200 |
| `dim_channel` | 5 |
| `dim_customer_tier` | 4 |
| `dim_customer` | 3,500 |
| `dim_product_supergroup` | 3 |
| `dim_product_category` | 12 |
| `dim_product_sku` | 38 |
| `dim_campaign` | 8 |
| `fact_sales_orders` | 297,075 |
| `fact_sales_lines` | 1,454,104 |
| `fact_targets` | 888 |
| `fact_aso_daily` | 1,872 |
| `fact_mcp_new` | 182 |
| `fact_visits` | 114,848 |
| `fact_customer_tier_history` | 50 |
| `_meta_tables` | 24 |
| `_meta_columns` | 26 |
| `_meta_kpi` | 12 |
| `_meta_glossary` | 23 |
