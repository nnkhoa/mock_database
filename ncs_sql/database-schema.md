# DATA SCHEMA — NCS SUẤT ĂN HÀNG KHÔNG BI
## Database: `ncs_catering_demo` (MySQL 8.0, utf8mb4_unicode_ci)
## Phạm vi: 01/01/2025 – 30/06/2026 (18 tháng) | "Hiện tại" = cuối 30/06/2026
## 21 bảng: 9 dimension + 8 fact + 4 metadata

---

## SƠ ĐỒ QUAN HỆ

```
dim_calendar (date PK)
  ├── fact_meal_uplift.flight_date
  ├── fact_daily_operations.ops_date
  ├── fact_kitchen_capacity_daily.ops_date
  └── fact_quality_incidents.incident_date

dim_business_lines (business_line_id PK)
  ├── dim_customers.business_line_id
  ├── dim_products.business_line_id
  ├── fact_monthly_pnl.business_line_id
  └── fact_plan_monthly.business_line_id

dim_customers (customer_id PK)
  ├── fact_meal_uplift.customer_id
  ├── fact_non_aviation_sales.customer_id
  └── fact_quality_incidents.customer_id

dim_routes (route_id PK)
  └── fact_meal_uplift.route_id

dim_cabin_classes (cabin_class_id PK)
  ├── dim_products.cabin_class_id        (NULL cho sản phẩm phi hàng không)
  └── fact_meal_uplift.cabin_class_id

dim_products (product_id PK)
  ├── fact_meal_uplift.product_id        (chỉ sản phẩm business_line_id = 1)
  └── fact_non_aviation_sales.product_id (chỉ sản phẩm business_line_id = 2)

dim_materials (material_id PK)
  └── fact_material_consumption_monthly.material_id

dim_kitchen_lines (kitchen_line_id PK)
  └── fact_kitchen_line_monthly.kitchen_line_id

dim_cost_categories (cost_category_id PK)
  └── (bảng tham chiếu — dùng để diễn giải tên khoản mục chi phí
       trong fact_daily_operations và fact_monthly_pnl, KHÔNG có FK trực tiếp)

METADATA (không có FK, tra cứu bằng tên bảng/cột dạng chuỗi)
  _meta_tables · _meta_columns · _meta_kpi · _meta_glossary
```

**Hai fact tổng hợp không có FK tới fact chi tiết** nhưng phải khớp số:
```
fact_meal_uplift  ──(aggregate theo tháng)──►  fact_monthly_pnl (business_line_id = 1)
fact_non_aviation_sales ──(aggregate)────────►  fact_monthly_pnl (business_line_id = 2)
fact_meal_uplift  ──(aggregate theo ngày)───►  fact_daily_operations.revenue_aviation_vnd
```

---

## DIMENSION TABLES

### 1. `dim_calendar` (546 rows)
Lịch ngày phủ toàn bộ phạm vi data, có cờ lễ Tết Việt Nam.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `date` | DATE PK | Ngày | 2025-01-01 → 2026-06-30 |
| `year` | SMALLINT | Năm | |
| `quarter` | TINYINT | Quý 1–4 | |
| `month` | TINYINT | Tháng 1–12 | |
| `month_name_vi` | VARCHAR(20) | 'Tháng 1' … 'Tháng 12' | |
| `week_of_year` | TINYINT | Tuần trong năm | |
| `day_of_week` | TINYINT | 1=Thứ Hai … 7=Chủ Nhật | |
| `day_name_vi` | VARCHAR(20) | 'Thứ Hai' … 'Chủ Nhật' | |
| `is_weekend` | TINYINT(1) | 1 nếu T7/CN | |
| `is_holiday` | TINYINT(1) | 1 nếu lễ VN | |
| `holiday_name_vi` | VARCHAR(60) | Tên ngày lễ | NULL nếu không |
| `is_tet_period` | TINYINT(1) | 1 nếu trong cao điểm Tết | 10 ngày trước → 7 ngày sau mùng 1 |
| `season_phase_vi` | VARCHAR(30) | 'Cao điểm hè', 'Cao điểm Tết', 'Thấp điểm', 'Bình thường' | |

Tết Âm lịch trong phạm vi: mùng 1 Tết 2025 = **29/01/2025**; mùng 1 Tết 2026 = **17/02/2026**.

### 2. `dim_business_lines` (2 rows)
Hai mảng kinh doanh có biên lợi nhuận chênh nhau ~15 điểm.

| Cột | Kiểu | Mô tả |
|---|---|---|
| `business_line_id` | INT PK | 1 hoặc 2 |
| `business_line_name` | VARCHAR(40) | 'Hàng không' / 'Phi hàng không' |
| `target_gross_margin_pct` | DECIMAL(6,2) | 15,0 / 28,0 |
| `description_vi` | VARCHAR(255) | Mô tả mảng |

### 3. `dim_customers` (26 rows)
18 khách hàng không (hãng bay + chuyên cơ) + 8 khách phi hàng không.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `customer_id` | INT PK | | |
| `customer_name` | VARCHAR(120) | Tên khách hàng | 'Vietnam Airlines', 'Cụm trường liên cấp khu vực Hà Nội'… |
| `iata_code` | VARCHAR(4) | Mã IATA hãng bay | NULL với khách phi hàng không |
| `customer_type` | VARCHAR(40) | 'Hãng hàng không', 'Chuyên cơ & VIP', 'Trường học', 'Khu công nghiệp', 'Bán lẻ', 'Sự kiện & hội nghị', 'Phòng chờ' | |
| `country` | VARCHAR(50) | Quốc gia | |
| `business_line_id` | INT FK | | → `dim_business_lines` |
| `contract_type` | VARCHAR(50) | 'Hợp đồng năm có trượt giá', 'Hợp đồng năm cố định', 'Theo vụ việc' | |
| `has_price_escalation` | TINYINT(1) | **1 = hợp đồng có điều khoản trượt giá** | ⚠️ Cột then chốt phân tích rủi ro biên |
| `contract_start_date` | DATE | Ngày bắt đầu hợp đồng hiện hành | |
| `contract_end_date` | DATE | Ngày hết hạn | |
| `is_related_party` | TINYINT(1) | 1 = bên liên quan (Vietnam Airlines) | |

⚠️ **`has_price_escalation = 0` là nhóm rủi ro biên.** Các hãng này chịu toàn bộ biến động giá NVL mà không được điều chỉnh đơn giá.

### 4. `dim_routes` (42 rows)
Chặng bay xuất phát từ Nội Bài (HAN).

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `route_id` | INT PK | | |
| `route_code` | VARCHAR(10) | 'HAN-ICN' | |
| `origin_code` | VARCHAR(4) | Luôn là 'HAN' | |
| `destination_code` | VARCHAR(4) | Mã IATA điểm đến | |
| `destination_city_vi` | VARCHAR(60) | 'Seoul', 'Tokyo', 'TP. Hồ Chí Minh' | |
| `destination_country` | VARCHAR(50) | | |
| `region_group` | VARCHAR(30) | 'Nội địa', 'Đông Bắc Á', 'Đông Nam Á', 'Châu Âu', 'Trung Đông', 'Châu Úc' | |
| `flight_duration_hours` | DECIMAL(4,1) | Thời gian bay | Quyết định số lượt phục vụ |
| `haul_type` | VARCHAR(10) | 'Ngắn' (<3h), 'Trung' (3–6h), 'Dài' (>6h) | Quyết định mix hạng ghế |

### 5. `dim_cabin_classes` (4 rows)
Hạng ghế quyết định đơn giá suất ăn — chênh lệch tới 5,4 lần.

| Cột | Kiểu | Mô tả |
|---|---|---|
| `cabin_class_id` | INT PK | 1–4 |
| `cabin_class_name` | VARCHAR(40) | 'Hạng nhất', 'Thương gia', 'Phổ thông đặc biệt', 'Phổ thông' |
| `cabin_class_code` | VARCHAR(2) | 'F', 'C', 'W', 'Y' |
| `typical_unit_price_vnd` | DECIMAL(12,2) | 420.000 / 215.000 / 118.000 / 78.000 (mức 2026) |
| `typical_share_pct` | DECIMAL(6,2) | 0,4 / 8,0 / 5,0 / 86,6 |

### 6. `dim_products` (68 rows)
48 loại suất ăn hàng không + 20 sản phẩm phi hàng không.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `product_id` | INT PK | | |
| `product_name_vi` | VARCHAR(150) | 'Cơm bò sốt tiêu đen', 'Bánh trung thu hộp cao cấp' | |
| `product_group` | VARCHAR(60) | Xem danh mục bên dưới | |
| `business_line_id` | INT FK | 1 = Hàng không, 2 = Phi hàng không | |
| `cabin_class_id` | INT FK | Hạng ghế áp dụng | **NULL với sản phẩm phi hàng không** |
| `menu_cycle_code` | VARCHAR(20) | 'MC-2025A', 'MC-2025B', 'MC-2026A', 'MC-2026B' | Thực đơn đổi 6 tháng/lần |
| `standard_material_cost_vnd` | DECIMAL(12,2) | Định mức NVL/suất | VND |

`product_group` — **Hàng không:** 'Suất ăn nóng', 'Suất ăn lạnh', 'Suất ăn nhẹ & snack', 'Đồ uống', 'Suất ăn đặc biệt (chay/halal/trẻ em)', 'Suất ăn chuyên cơ'.
`product_group` — **Phi hàng không:** 'Bánh trung thu', 'Giò chả Tết', 'Trà sữa & đồ uống', 'Suất ăn trường học', 'Suất ăn công nghiệp', 'Catering sự kiện', 'Phòng chờ thương gia', 'Bán lẻ tại quầy'.

### 7. `dim_materials` (85 rows)
Danh mục nguyên vật liệu, phân theo loại và nhóm.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `material_id` | INT PK | | |
| `material_code` | VARCHAR(20) | 'NVL-M001', 'HH-G001' | |
| `material_name_vi` | VARCHAR(120) | 'Bò thăn nhập khẩu' | |
| `material_type` | VARCHAR(40) | **'NVL chính' / 'NVL phụ' / 'Hàng hóa phục vụ sản xuất'** | ⚠️ Trục bóc tách bắt buộc |
| `material_group` | VARCHAR(60) | 'Thịt & gia cầm', 'Thủy hải sản', 'Rau củ quả', 'Gạo & tinh bột', 'Sữa & trứng', 'Gia vị & dầu ăn', 'Bao bì & dụng cụ', 'Đồ uống đóng gói', 'Hóa chất vệ sinh & vật tư' | |
| `unit` | VARCHAR(20) | 'kg', 'lít', 'quả', 'cái', 'bộ', 'hộp', 'gói', 'chai', 'cuộn' | |
| `standard_price_vnd` | DECIMAL(14,2) | Đơn giá định mức | VND/đơn vị |
| `supplier_origin` | VARCHAR(60) | 'Nhập khẩu', 'Nội địa' | |

### 8. `dim_kitchen_lines` (8 rows)
Dây chuyền / khu chế biến — dùng để drill nguyên nhân sự cố năng lượng và nghẽn công suất.

| Cột | Kiểu | Mô tả |
|---|---|---|
| `kitchen_line_id` | INT PK | 1–8 |
| `kitchen_line_name` | VARCHAR(60) | 'Bếp nóng Á', 'Bếp nóng Âu', 'Bếp lạnh & salad', 'Bánh & tráng miệng', 'Khu soạn khay', 'Khu rửa & vệ sinh dụng cụ', 'Kho lạnh & bảo quản', 'Khu sản xuất phi hàng không' |
| `line_type` | VARCHAR(30) | 'Chế biến nóng', 'Chế biến lạnh', 'Chế biến', 'Đóng gói', 'Hỗ trợ' |
| `daily_capacity_meals` | INT | Công suất suất/ngày (NULL với khu hỗ trợ) |

### 9. `dim_cost_categories` (12 rows)
Bảng tham chiếu diễn giải khoản mục chi phí.

| Cột | Kiểu | Mô tả |
|---|---|---|
| `cost_category_id` | INT PK | |
| `cost_category_name_vi` | VARCHAR(60) | 'NVL chính', 'NVL phụ', 'Hàng hóa phục vụ sản xuất', 'Nhân công trực tiếp', 'Làm thêm giờ', 'Điện', 'Nước', 'Gas', 'Vận chuyển & xe nâng suất', 'Khấu hao thiết bị', 'Kiểm nghiệm & an toàn thực phẩm', 'Chi phí sản xuất khác' |
| `cost_group_vi` | VARCHAR(40) | 'Nguyên vật liệu', 'Nhân công', 'Năng lượng', 'Chi phí sản xuất chung' |
| `typical_pct_of_revenue` | DECIMAL(6,2) | Tỷ trọng điển hình trên doanh thu |
| `mapped_column` | VARCHAR(60) | Tên cột tương ứng trong `fact_daily_operations` |

---

## FACT TABLES

### 10. `fact_meal_uplift` ★ (FACT CHÍNH — ~215.000 rows)
Grain: **1 dòng = 1 chuyến bay × 1 hạng ghế × 1 loại suất ăn**. Đây là bảng duy nhất có granularity tới chuyến bay.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `uplift_id` | BIGINT PK | | |
| `flight_date` | DATE FK | Ngày bay | → `dim_calendar.date` |
| `flight_number` | VARCHAR(10) | 'VN416', 'KE480' | |
| `customer_id` | INT FK | Hãng bay | → `dim_customers` |
| `route_id` | INT FK | Chặng | → `dim_routes` |
| `cabin_class_id` | INT FK | Hạng ghế | → `dim_cabin_classes` |
| `product_id` | INT FK | Loại suất | → `dim_products` |
| `departure_hour` | TINYINT | Giờ cất cánh 0–23 | Dùng phân tích khung giờ |
| `meals_ordered` | INT | Số suất hãng đặt | suất |
| `meals_produced` | INT | Số suất NCS sản xuất | suất |
| `meals_uplifted` | INT | **Số suất thực giao lên máy bay** | suất |
| `meals_wasted` | INT | = produced − uplifted | suất |
| `unit_price_vnd` | DECIMAL(12,2) | Đơn giá hợp đồng/suất | VND |
| `revenue_vnd` | DECIMAL(18,2) | = meals_uplifted × unit_price_vnd | VND |
| `material_cost_vnd` | DECIMAL(18,2) | Giá vốn NVL thực tế, tính trên **produced** | VND |
| `standard_material_cost_vnd` | DECIMAL(18,2) | Giá vốn NVL theo định mức, trên **produced** | VND |

⚠️ **Doanh thu LUÔN tính trên `meals_uplifted`, giá vốn LUÔN tính trên `meals_produced`.** Đây là nguồn gốc của hao hụt ăn vào lợi nhuận.
⚠️ **Bảng này chỉ chứa mảng Hàng không.** Doanh thu phi hàng không nằm ở `fact_non_aviation_sales`.

### 11. `fact_daily_operations` (546 rows)
Grain: **1 dòng = 1 ngày**. Bảng phục vụ phát hiện bất thường theo ngày.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `ops_date` | DATE PK | Ngày | |
| `total_flights_served` | INT | Số chuyến phục vụ | chuyến |
| `total_meals_produced` | INT | Tổng suất sản xuất | suất |
| `total_meals_uplifted` | INT | Tổng suất thực giao | suất |
| `waste_rate_pct` | DECIMAL(6,2) | Tỷ lệ hao hụt | % |
| `revenue_aviation_vnd` | DECIMAL(18,2) | Doanh thu hàng không | VND |
| `revenue_non_aviation_vnd` | DECIMAL(18,2) | Doanh thu phi hàng không | VND |
| `plan_meals` | INT | **Kế hoạch sản lượng ngày** | suất |
| `plan_revenue_vnd` | DECIMAL(18,2) | **Kế hoạch doanh thu ngày** | VND |
| `material_cost_main_vnd` | DECIMAL(18,2) | NVL chính | VND |
| `material_cost_aux_vnd` | DECIMAL(18,2) | NVL phụ | VND |
| `material_cost_goods_vnd` | DECIMAL(18,2) | Hàng hóa phục vụ sản xuất | VND |
| `energy_electricity_vnd` | DECIMAL(18,2) | Điện | VND |
| `energy_water_vnd` | DECIMAL(18,2) | Nước | VND |
| `energy_gas_vnd` | DECIMAL(18,2) | Gas | VND |
| `labor_regular_vnd` | DECIMAL(18,2) | Nhân công trực tiếp | VND |
| `labor_overtime_vnd` | DECIMAL(18,2) | Làm thêm giờ | VND |
| `labor_hours` | DECIMAL(10,1) | Tổng giờ công | giờ |
| `overtime_hours` | DECIMAL(10,1) | Giờ làm thêm | giờ |

⚠️ **Kế hoạch NGÀY nằm trong chính bảng này** (`plan_meals`, `plan_revenue_vnd`), không ở `fact_plan_monthly`.

### 12. `fact_monthly_pnl` (36 rows)
Grain: **1 dòng = 1 tháng × 1 mảng kinh doanh**. Nguồn chuẩn cho báo cáo lợi nhuận gộp.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `period_month` | DATE | Ngày đầu tháng ('2026-06-01') | PK (cùng business_line_id) |
| `business_line_id` | INT FK | 1 hoặc 2 | PK |
| `revenue_vnd` | DECIMAL(18,2) | Doanh thu | VND |
| `material_cost_vnd` | DECIMAL(18,2) | Tổng NVL (chính + phụ + hàng hóa) | VND |
| `labor_cost_vnd` | DECIMAL(18,2) | Nhân công + làm thêm giờ | VND |
| `energy_cost_vnd` | DECIMAL(18,2) | Điện + nước + gas | VND |
| `other_cogs_vnd` | DECIMAL(18,2) | Vận chuyển, khấu hao, kiểm nghiệm, khác | VND |
| `total_cogs_vnd` | DECIMAL(18,2) | Tổng giá vốn | VND |
| `gross_profit_vnd` | DECIMAL(18,2) | = revenue − total_cogs | VND |
| `gross_margin_pct` | DECIMAL(6,2) | = gross_profit / revenue × 100 | % |

⚠️ **Chỉ có lợi nhuận GỘP.** Không có chi phí bán hàng, quản lý, tài chính, thuế → không tính được LNST.

### 13. `fact_plan_monthly` (36 rows)
Grain: **1 dòng = 1 tháng × 1 mảng kinh doanh**. Kế hoạch cấp tháng.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `period_month` | DATE | | PK |
| `business_line_id` | INT FK | | PK |
| `plan_revenue_vnd` | DECIMAL(18,2) | Kế hoạch doanh thu | VND |
| `plan_meals` | INT | Kế hoạch sản lượng (NULL với phi hàng không) | suất |
| `plan_material_cost_vnd` | DECIMAL(18,2) | Kế hoạch NVL | VND |
| `plan_labor_cost_vnd` | DECIMAL(18,2) | Kế hoạch nhân công | VND |
| `plan_energy_cost_vnd` | DECIMAL(18,2) | Kế hoạch năng lượng | VND |
| `plan_gross_profit_vnd` | DECIMAL(18,2) | Kế hoạch lợi nhuận gộp | VND |
| `plan_gross_margin_pct` | DECIMAL(6,2) | Kế hoạch biên gộp | % |
| `plan_unit_price_vnd` | DECIMAL(12,2) | Đơn giá bình quân kế hoạch | VND/suất |
| `plan_waste_rate_pct` | DECIMAL(6,2) | Tỷ lệ hao hụt kế hoạch | % |

### 14. `fact_material_consumption_monthly` (~1.530 rows)
Grain: **1 dòng = 1 tháng × 1 mã NVL**. Nguồn cho bóc tách chênh lệch giá/lượng.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `period_month` | DATE | | PK |
| `material_id` | INT FK | | PK |
| `quantity_consumed` | DECIMAL(14,2) | Lượng tiêu thụ thực tế | theo `dim_materials.unit` |
| `unit_price_actual_vnd` | DECIMAL(14,2) | Đơn giá thực tế | VND |
| `total_cost_vnd` | DECIMAL(18,2) | = quantity × unit_price_actual | VND |
| `standard_quantity` | DECIMAL(14,2) | Lượng theo định mức | |
| `standard_price_vnd` | DECIMAL(14,2) | Đơn giá định mức | VND |
| `standard_cost_vnd` | DECIMAL(18,2) | = standard_quantity × standard_price | VND |
| `price_variance_vnd` | DECIMAL(18,2) | **(giá TT − giá ĐM) × lượng TT** → nguyên nhân thị trường | VND |
| `quantity_variance_vnd` | DECIMAL(18,2) | **(lượng TT − lượng ĐM) × giá ĐM** → nguyên nhân bếp | VND |

⚠️ **`total_cost_vnd − standard_cost_vnd ≈ price_variance + quantity_variance`.** Luôn tách hai vế khi giải thích nguyên nhân — chúng dẫn tới hai hành động khác nhau.

### 15. `fact_non_aviation_sales` (~420 rows)
Grain: **1 dòng = 1 tháng × 1 sản phẩm × 1 khách hàng**. Toàn bộ mảng phi hàng không.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `period_month` | DATE | | |
| `product_id` | INT FK | → `dim_products` (business_line_id = 2) | |
| `customer_id` | INT FK | → `dim_customers` (business_line_id = 2) | |
| `quantity_sold` | INT | Sản lượng | suất/hộp/cây |
| `unit_price_vnd` | DECIMAL(12,2) | Đơn giá | VND |
| `revenue_vnd` | DECIMAL(18,2) | Doanh thu | VND |
| `cogs_vnd` | DECIMAL(18,2) | Giá vốn | VND |
| `gross_profit_vnd` | DECIMAL(18,2) | Lợi nhuận gộp | VND |

⚠️ **Bảng này SPARSE theo mùa.** Bánh trung thu chỉ có dòng T8–T9; giò chả Tết chỉ T12–T2; suất ăn trường học không có T6–T8. Khi tính trung bình tháng, dùng `COALESCE(..., 0)` hoặc lọc kỳ có phát sinh — nếu không sẽ ra trung bình sai.

### 16. `fact_kitchen_capacity_daily` (3.276 rows)
Grain: **1 dòng = 1 ngày × 1 khung giờ (6 khung)**. Nguồn duy nhất cho phân tích nghẽn công suất.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `ops_date` | DATE | | PK |
| `time_slot` | VARCHAR(20) | '00-04', '04-08', '08-12', '12-16', '16-20', '20-24' | PK |
| `meals_produced` | INT | Sản lượng khung giờ | suất |
| `capacity_meals` | INT | Công suất khung giờ | suất |
| `utilization_pct` | DECIMAL(6,2) | = produced / capacity × 100 | % |
| `staff_on_duty` | INT | Nhân sự trực | người |
| `overtime_hours` | DECIMAL(8,1) | Giờ làm thêm khung giờ | giờ |
| `waste_rate_pct` | DECIMAL(6,2) | Tỷ lệ hao hụt khung giờ | % |

⚠️ **KHÔNG bình quân cả ngày khi phân tích nghẽn** — bình quân sẽ che mất khung cao điểm. Luôn `GROUP BY time_slot`.

### 17. `fact_kitchen_line_monthly` (144 rows)
Grain: **1 dòng = 1 tháng × 1 dây chuyền**. Dùng để drill nguyên nhân sự cố xuống đúng khu chế biến.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `period_month` | DATE | | PK |
| `kitchen_line_id` | INT FK | | PK |
| `meals_produced` | INT | Sản lượng | suất |
| `labor_cost_vnd` | DECIMAL(18,2) | Chi phí nhân công | VND |
| `energy_electricity_vnd` | DECIMAL(18,2) | Điện | VND |
| `energy_gas_vnd` | DECIMAL(18,2) | Gas | VND |
| `energy_water_vnd` | DECIMAL(18,2) | Nước | VND |
| `defect_count` | INT | Số lỗi sản xuất ghi nhận | vụ |

### 18. `fact_quality_incidents` (~420 rows)
Grain: **1 dòng = 1 sự vụ chất lượng/dịch vụ**. Phục vụ câu hỏi ngoài kịch bản về chất lượng và rủi ro hợp đồng.

| Cột | Kiểu | Mô tả |
|---|---|---|
| `incident_id` | INT PK | |
| `incident_date` | DATE FK | → `dim_calendar.date` |
| `customer_id` | INT FK | Hãng bị ảnh hưởng |
| `incident_type` | VARCHAR(50) | 'Giao chậm', 'Sai số lượng', 'Khiếu nại chất lượng', 'Sai thực đơn', 'Lỗi nhiệt độ bảo quản' |
| `severity` | VARCHAR(20) | 'Nhẹ', 'Trung bình', 'Nghiêm trọng' |
| `flight_number` | VARCHAR(10) | Chuyến liên quan (có thể NULL) |
| `description_vi` | VARCHAR(255) | Mô tả ngắn |

---

## METADATA TABLES

| Bảng | Cột | Mục đích |
|---|---|---|
| `_meta_tables` | table_name, description_vi, description_en, business_context | Mô tả từng bảng |
| `_meta_columns` | table_name, column_name, data_type, description_vi, description_en, unit, example_values | Mô tả từng cột + đơn vị |
| `_meta_kpi` | kpi_name, formula_sql, description_vi, related_questions | Công thức KPI chuẩn |
| `_meta_glossary` | term_vi, term_en, definition | Thuật ngữ ngành |

Khi không chắc ý nghĩa một cột, query `_meta_columns` trước khi đoán.

---

## SQL TEMPLATES

### T1 — Bức tranh tổng theo mảng, so kế hoạch (Scenario 1)
```sql
SELECT b.business_line_name AS mang,
       ROUND(p.revenue_vnd/1e9, 1)              AS dt_ty,
       ROUND(pl.plan_revenue_vnd/1e9, 1)        AS kh_dt_ty,
       ROUND(p.revenue_vnd/pl.plan_revenue_vnd*100, 1) AS pct_kh,
       ROUND(p.total_cogs_vnd/1e9, 1)           AS gia_von_ty,
       ROUND(p.gross_profit_vnd/1e9, 1)         AS ln_gop_ty,
       ROUND(p.gross_margin_pct, 1)             AS bien_pct,
       ROUND(pl.plan_gross_margin_pct, 1)       AS kh_bien_pct
FROM fact_monthly_pnl p
JOIN dim_business_lines b USING (business_line_id)
JOIN fact_plan_monthly pl
     ON pl.period_month = p.period_month
    AND pl.business_line_id = p.business_line_id
WHERE p.period_month = '2026-06-01';
```

### T2 — Trend doanh thu & biên gộp 18 tháng (tìm điểm gãy)
```sql
SELECT DATE_FORMAT(period_month, '%Y-%m')                  AS thang,
       ROUND(SUM(revenue_vnd)/1e9, 1)                      AS dt_ty,
       ROUND(SUM(gross_profit_vnd)/1e9, 1)                 AS ln_gop_ty,
       ROUND(SUM(gross_profit_vnd)/SUM(revenue_vnd)*100,1) AS bien_pct
FROM fact_monthly_pnl
GROUP BY 1
ORDER BY 1;
```

### T3 — Phát hiện bất thường ngày so trung bình 30 ngày (Scenario 2)
```sql
WITH daily AS (
  SELECT ops_date,
         total_meals_produced,
         ROUND(energy_gas_vnd / NULLIF(total_meals_produced,0), 0) AS gas_moi_suat,
         waste_rate_pct,
         ROUND(revenue_aviation_vnd + revenue_non_aviation_vnd, 0)  AS dt_ngay,
         plan_revenue_vnd,
         ROUND(overtime_hours / NULLIF(labor_hours,0) * 100, 1)     AS ot_pct
  FROM fact_daily_operations
  WHERE ops_date BETWEEN '2026-05-31' AND '2026-06-30'
)
SELECT ops_date, gas_moi_suat, waste_rate_pct, ot_pct,
       ROUND(AVG(gas_moi_suat)  OVER (ORDER BY ops_date ROWS BETWEEN 30 PRECEDING AND 1 PRECEDING), 0) AS gas_tb30,
       ROUND(AVG(waste_rate_pct) OVER (ORDER BY ops_date ROWS BETWEEN 30 PRECEDING AND 1 PRECEDING), 2) AS waste_tb30
FROM daily
ORDER BY ops_date;
```

### T4 — Thẻ KPI trọng yếu tháng (Scenario 3)
```sql
SELECT
  ROUND(SUM(o.revenue_aviation_vnd + o.revenue_non_aviation_vnd)/1e9, 1) AS dt_ty,
  SUM(o.total_meals_uplifted)                                            AS suat_giao,
  SUM(o.total_meals_produced)                                            AS suat_san_xuat,
  ROUND((SUM(o.total_meals_produced) - SUM(o.total_meals_uplifted))
        / SUM(o.total_meals_produced) * 100, 2)                          AS hao_hut_pct,
  ROUND(SUM(o.material_cost_main_vnd + o.material_cost_aux_vnd + o.material_cost_goods_vnd)
        / SUM(o.total_meals_produced), 0)                                AS nvl_moi_suat,
  ROUND(SUM(o.energy_electricity_vnd + o.energy_water_vnd + o.energy_gas_vnd)/1e9, 2) AS nang_luong_ty,
  ROUND(SUM(o.overtime_hours)/SUM(o.labor_hours)*100, 1)                 AS ot_pct
FROM fact_daily_operations o
WHERE o.ops_date BETWEEN '2026-06-01' AND '2026-06-30';
```

### T5 — Doanh thu & biên theo hãng, 6 tháng (Scenario 4)
```sql
SELECT c.customer_name                                        AS hang,
       c.iata_code,
       c.has_price_escalation                                 AS co_truot_gia,
       SUM(u.meals_uplifted)                                  AS suat_giao,
       ROUND(SUM(u.revenue_vnd)/1e9, 2)                       AS dt_ty,
       ROUND(SUM(u.revenue_vnd)*100/SUM(SUM(u.revenue_vnd)) OVER (), 1) AS ty_trong_pct,
       ROUND(SUM(u.revenue_vnd)/SUM(u.meals_uplifted), 0)     AS don_gia_bq,
       ROUND((SUM(u.revenue_vnd) - SUM(u.material_cost_vnd))
             / SUM(u.revenue_vnd) * 100, 1)                   AS bien_nvl_pct
FROM fact_meal_uplift u
JOIN dim_customers c USING (customer_id)
WHERE u.flight_date BETWEEN '2026-01-01' AND '2026-06-30'
GROUP BY 1,2,3
ORDER BY dt_ty DESC;
```

### T6 — Top chặng đóng góp doanh thu tháng gần nhất (Scenario 4 follow-up)
```sql
SELECT r.route_code, r.destination_city_vi, r.region_group, r.haul_type,
       SUM(u.meals_uplifted)             AS suat,
       ROUND(SUM(u.revenue_vnd)/1e9, 2)  AS dt_ty
FROM fact_meal_uplift u
JOIN dim_routes r USING (route_id)
WHERE u.flight_date BETWEEN '2026-06-01' AND '2026-06-30'
GROUP BY 1,2,3,4
ORDER BY dt_ty DESC
LIMIT 5;
```

### T7 — Bóc tách NVL theo loại → nhóm → mã, đánh dấu vượt định mức (Scenario 5)
```sql
SELECT m.material_type                                  AS loai_nvl,
       m.material_group                                 AS nhom,
       m.material_name_vi                               AS ma_nvl,
       ROUND(SUM(f.total_cost_vnd)/1e9, 2)              AS thuc_te_ty,
       ROUND(SUM(f.standard_cost_vnd)/1e9, 2)           AS dinh_muc_ty,
       ROUND((SUM(f.total_cost_vnd)/SUM(f.standard_cost_vnd) - 1)*100, 1) AS vuot_pct,
       ROUND(SUM(f.price_variance_vnd)/1e9, 2)          AS chenh_do_gia_ty,
       ROUND(SUM(f.quantity_variance_vnd)/1e9, 2)       AS chenh_do_luong_ty
FROM fact_material_consumption_monthly f
JOIN dim_materials m USING (material_id)
WHERE f.period_month BETWEEN '2026-04-01' AND '2026-06-01'
GROUP BY 1,2,3
HAVING vuot_pct > 3
ORDER BY (SUM(f.total_cost_vnd) - SUM(f.standard_cost_vnd)) DESC;
```

### T8 — Profit bridge: các cấu phần chênh lệch lợi nhuận (Scenario 6)
```sql
-- Bước 1: khung tổng
SELECT ROUND(SUM(p.gross_profit_vnd)/1e9, 2)      AS ln_thuc_te_ty,
       ROUND(SUM(pl.plan_gross_profit_vnd)/1e9,2) AS ln_ke_hoach_ty,
       ROUND((SUM(p.gross_profit_vnd) - SUM(pl.plan_gross_profit_vnd))/1e9, 2) AS chenh_ty
FROM fact_monthly_pnl p
JOIN fact_plan_monthly pl
     ON pl.period_month = p.period_month AND pl.business_line_id = p.business_line_id
WHERE p.period_month = '2026-06-01';

-- Bước 2: yếu tố SẢN LƯỢNG và GIÁ/MIX (mảng hàng không)
SELECT SUM(u.meals_uplifted)                          AS suat_tt,
       pl.plan_meals                                  AS suat_kh,
       ROUND(SUM(u.revenue_vnd)/SUM(u.meals_uplifted),0) AS don_gia_tt,
       pl.plan_unit_price_vnd                         AS don_gia_kh,
       ROUND((SUM(u.meals_uplifted) - pl.plan_meals)
             * (pl.plan_unit_price_vnd - 50200 - 12000)/1e9, 2) AS tac_dong_san_luong_ty,
       ROUND(SUM(u.meals_uplifted)
             * (SUM(u.revenue_vnd)/SUM(u.meals_uplifted) - pl.plan_unit_price_vnd)/1e9, 2) AS tac_dong_gia_mix_ty
FROM fact_meal_uplift u
JOIN fact_plan_monthly pl
     ON pl.period_month = '2026-06-01' AND pl.business_line_id = 1
WHERE u.flight_date BETWEEN '2026-06-01' AND '2026-06-30'
GROUP BY pl.plan_meals, pl.plan_unit_price_vnd;

-- Bước 3: yếu tố NVL vượt định mức
SELECT ROUND(SUM(total_cost_vnd - standard_cost_vnd)/1e9, 2) AS tac_dong_nvl_ty
FROM fact_material_consumption_monthly
WHERE period_month = '2026-06-01';

-- Bước 4: yếu tố HAO HỤT
SELECT ROUND((SUM(o.total_meals_produced) - SUM(o.total_meals_uplifted)
              - SUM(o.total_meals_produced) * pl.plan_waste_rate_pct/100)
             * 52800 / 1e9, 2) AS tac_dong_hao_hut_ty
FROM fact_daily_operations o
JOIN fact_plan_monthly pl
     ON pl.period_month = '2026-06-01' AND pl.business_line_id = 1
WHERE o.ops_date BETWEEN '2026-06-01' AND '2026-06-30'
GROUP BY pl.plan_waste_rate_pct;

-- Bước 5: yếu tố NĂNG LƯỢNG & LÀM THÊM GIỜ
SELECT ROUND((SUM(o.energy_electricity_vnd + o.energy_water_vnd + o.energy_gas_vnd)
              - pl.plan_energy_cost_vnd)/1e9, 2) AS tac_dong_nang_luong_ty,
       ROUND((SUM(o.labor_regular_vnd + o.labor_overtime_vnd)
              - pl.plan_labor_cost_vnd)/1e9, 2)  AS tac_dong_nhan_cong_ty
FROM fact_daily_operations o
JOIN fact_plan_monthly pl
     ON pl.period_month = '2026-06-01' AND pl.business_line_id = 1
WHERE o.ops_date BETWEEN '2026-06-01' AND '2026-06-30'
GROUP BY pl.plan_energy_cost_vnd, pl.plan_labor_cost_vnd;
```

### T9 — Nghẽn công suất theo khung giờ
```sql
SELECT time_slot,
       ROUND(AVG(utilization_pct), 1)  AS util_pct,
       ROUND(AVG(waste_rate_pct), 2)   AS hao_hut_pct,
       ROUND(SUM(overtime_hours), 0)   AS gio_lam_them,
       ROUND(AVG(staff_on_duty), 0)    AS nhan_su_bq
FROM fact_kitchen_capacity_daily
WHERE ops_date BETWEEN '2026-06-01' AND '2026-06-30'
GROUP BY 1
ORDER BY util_pct DESC;
```

### T10 — Mảng phi hàng không theo nhóm sản phẩm
```sql
SELECT DATE_FORMAT(f.period_month, '%Y-%m')          AS thang,
       p.product_group                               AS nhom_sp,
       ROUND(SUM(f.revenue_vnd)/1e9, 2)              AS dt_ty,
       ROUND(SUM(f.gross_profit_vnd)/SUM(f.revenue_vnd)*100, 1) AS bien_pct
FROM fact_non_aviation_sales f
JOIN dim_products p USING (product_id)
WHERE f.period_month BETWEEN '2025-07-01' AND '2026-06-01'
GROUP BY 1,2
ORDER BY 1, dt_ty DESC;
```

### T11 — So sánh YoY cùng kỳ
```sql
SELECT MONTH(period_month) AS thang,
       ROUND(SUM(CASE WHEN YEAR(period_month)=2025 THEN revenue_vnd END)/1e9, 1) AS nam_2025_ty,
       ROUND(SUM(CASE WHEN YEAR(period_month)=2026 THEN revenue_vnd END)/1e9, 1) AS nam_2026_ty,
       ROUND((SUM(CASE WHEN YEAR(period_month)=2026 THEN revenue_vnd END)
            / SUM(CASE WHEN YEAR(period_month)=2025 THEN revenue_vnd END) - 1)*100, 1) AS yoy_pct
FROM fact_monthly_pnl
WHERE MONTH(period_month) <= 6
GROUP BY 1
ORDER BY 1;
```

---

## JOIN WARNINGS

1. **`fact_meal_uplift` × `dim_products` — chỉ mảng Hàng không.** `dim_products` chứa cả 68 sản phẩm của 2 mảng. JOIN không lọc `business_line_id = 1` vẫn chạy nhưng nếu bạn cố tính "tổng doanh thu theo product_group" bằng bảng này thì sẽ thiếu toàn bộ phi hàng không. Muốn tổng 2 mảng → dùng `fact_monthly_pnl`, hoặc UNION với `fact_non_aviation_sales`.

2. **`dim_products.cabin_class_id` có NULL.** Sản phẩm phi hàng không không có hạng ghế. JOIN `dim_products` × `dim_cabin_classes` bằng INNER JOIN sẽ âm thầm loại bỏ 20 sản phẩm. Dùng LEFT JOIN.

3. **`fact_meal_uplift` grain là chuyến × hạng ghế × loại suất.** Một chuyến bay có nhiều dòng. Đếm số chuyến phải dùng `COUNT(DISTINCT CONCAT(flight_date, flight_number))`, KHÔNG dùng `COUNT(*)`.

4. **`fact_non_aviation_sales` SPARSE theo mùa.** Bánh trung thu chỉ có T8–T9, giò chả Tết chỉ T12–T2, suất ăn trường học không có T6–T8. `AVG(revenue_vnd)` theo tháng sẽ sai vì mẫu số chỉ đếm tháng có phát sinh. Dùng LEFT JOIN từ `dim_calendar` hoặc chuỗi tháng đầy đủ, rồi `COALESCE(..., 0)`.

5. **`fact_monthly_pnl` × `fact_plan_monthly` phải JOIN trên CẢ HAI khóa.** JOIN chỉ bằng `period_month` sẽ nhân đôi dòng (2 mảng × 2 mảng = 4). Luôn `ON period_month AND business_line_id`.

6. **`fact_daily_operations` là bảng NGÀY ĐÃ tổng hợp, `fact_meal_uplift` là chi tiết.** KHÔNG JOIN hai bảng này rồi SUM — sẽ cộng trùng doanh thu. Chọn một trong hai theo grain câu hỏi.

7. **`fact_kitchen_capacity_daily` — không bình quân cả ngày.** `AVG(utilization_pct)` toàn ngày cho ra ~78% ngay cả khi khung đêm đã chạm 96%. Luôn `GROUP BY time_slot` khi phân tích nghẽn.

8. **`fact_kitchen_line_monthly` × `fact_daily_operations` — hai nguồn năng lượng khác grain.** Tổng gas theo dây chuyền (tháng) ≈ tổng gas theo ngày (tháng), sai số < 2% do phân bổ. Đừng cộng cả hai.

9. **`fact_material_consumption_monthly` KHÔNG nối được xuống chuyến bay.** Bảng này grain tháng × mã NVL, không có customer_id hay route_id. Câu hỏi "hãng nào dùng nhiều bò thăn nhất" chỉ trả lời được **gián tiếp** qua `dim_products.product_group` + mix hạng ghế của hãng đó → phải nói rõ đây là suy luận, không phải số đo trực tiếp.

10. **`dim_customers` phục vụ cả 2 mảng.** 18 dòng business_line_id = 1, 8 dòng = 2. JOIN với `fact_meal_uplift` chỉ trả về nhóm hàng không; JOIN với `fact_non_aviation_sales` chỉ trả về nhóm phi hàng không. Không có khách hàng nào thuộc cả hai.

11. **Doanh thu ≠ suất × đơn giá bình quân.** Đơn giá khác nhau theo hãng và hạng ghế. Nhân ngược sẽ ra số sai. Luôn `SUM(revenue_vnd)`.

---

## ĐƠN VỊ TIỀN TỆ & QUY ƯỚC HIỂN THỊ

Toàn bộ số tiền trong database là **VND**. Không có cột ngoại tệ.

| Bảng | Cột tiền | Đơn vị |
|---|---|---|
| `fact_meal_uplift` | unit_price_vnd, revenue_vnd, material_cost_vnd, standard_material_cost_vnd | VND |
| `fact_daily_operations` | revenue_*, material_cost_*, energy_*, labor_*, plan_revenue_vnd | VND |
| `fact_monthly_pnl` | revenue_vnd, *_cost_vnd, gross_profit_vnd | VND |
| `fact_plan_monthly` | plan_*_vnd | VND |
| `fact_material_consumption_monthly` | unit_price_actual_vnd, total_cost_vnd, standard_price_vnd, standard_cost_vnd, price_variance_vnd, quantity_variance_vnd | VND |
| `fact_non_aviation_sales` | unit_price_vnd, revenue_vnd, cogs_vnd, gross_profit_vnd | VND |
| `fact_kitchen_line_monthly` | labor_cost_vnd, energy_*_vnd | VND |
| `dim_materials` | standard_price_vnd | VND / đơn vị |
| `dim_products` | standard_material_cost_vnd | VND / suất |
| `dim_cabin_classes` | typical_unit_price_vnd | VND / suất |

**Format hiển thị cho lãnh đạo:**
- ≥ 1 tỷ: "96,4 tỷ" (1 chữ số thập phân)
- < 1 tỷ: "870 triệu"
- Đơn giá/suất, chi phí/suất: "52.800đ" (đồng, có dấu chấm phân cách nghìn)
- Phần trăm: 1 chữ số thập phân → "14,7%"
- Chênh lệch biên: dùng "điểm" → "giảm 3,8 điểm", KHÔNG viết "giảm 3,8%"
- Sản lượng: "911.200 suất"

---

## MỐC SANITY CHECK NHANH

| Chỉ tiêu | Mức tham chiếu |
|---|---|
| Doanh thu năm 2025 | ~897 tỷ |
| Doanh thu 6T/2026 | ~492 tỷ |
| Doanh thu tháng 2026 | 76–97 tỷ tùy mùa |
| Sản lượng/ngày 2025 | 24.000–26.000 suất |
| Sản lượng/ngày 2026 | 29.000–31.000 suất |
| Công suất trần | 35.000 suất/ngày |
| Đơn giá bình quân 2026 | ~92.300đ/suất |
| NVL/suất 2026 | ~52.800đ (định mức 50.200đ) |
| Biên gộp toàn công ty | 14,7–17,9% (18 tháng) |
| Biên mảng Hàng không | 12–15% |
| Biên mảng Phi hàng không | 26–29% |
| Tỷ trọng Vietnam Airlines | ~61% doanh thu mảng Hàng không |
| Tỷ lệ hao hụt | 3,2–4,9% |

Nếu một con số lệch quá 30% khỏi các mốc trên → kiểm tra lại query (nhân dòng do JOIN? sai grain? quên WHERE?) trước khi trả lời.
