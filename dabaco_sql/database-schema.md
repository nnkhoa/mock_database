# DATA SCHEMA — DABACO | Chăn nuôi – Thức ăn chăn nuôi – Thực phẩm (chuỗi 3F+) BI
## Database: `dabaco_demo` (MySQL 8.0, utf8mb4_unicode_ci)
## Phạm vi: 01/01/2025 – 30/06/2026 (18 tháng) | "Hiện tại" = cuối 06/2026
## Grain trung tâm: **hai trục song song** — (1) BÁN HÀNG: ngày × sản phẩm × khách hàng; (2) VẬN HÀNH CHĂN NUÔI: trại × tuần
## Đặc thù: chuỗi khép kín có **tiêu thụ nội bộ ~39% tổng doanh thu** — mọi phân tích doanh thu/lợi nhuận phải phân biệt nội bộ vs ngoại bộ

---

## SƠ ĐỒ QUAN HỆ

```
dim_calendar (date_key PK)
  └── fact_sales.date_key
  └── fact_feed_production.date_key
  └── fact_material_purchase.date_key
  └── fact_market_price.date_key
  └── fact_transfer_pricing.date_key

dim_week (week_key PK)                    -- VD: '2026-W19'
  └── fact_farm_weekly.week_key

dim_segment (segment_id PK)               -- FEED / FARM / FOOD / FUTURE + sub-segment
  ├── dim_company.segment_id
  ├── dim_product.segment_id
  ├── fact_pnl_monthly.segment_id
  ├── fact_plan_monthly.segment_id
  └── fact_transfer_pricing.seller_segment_id
      fact_transfer_pricing.buyer_segment_id

dim_company (company_id PK)               -- 24 công ty thành viên
  ├── segment_id ────────────► dim_segment.segment_id
  ├── fact_sales.company_id
  ├── fact_pnl_monthly.company_id
  ├── fact_inventory_snapshot.company_id
  ├── fact_debt_snapshot.company_id
  ├── dim_farm.company_id
  ├── dim_customer.internal_company_id     (NULL nếu khách ngoại bộ)
  └── fact_transfer_pricing.seller_company_id
      fact_transfer_pricing.buyer_company_id

dim_region (region_id PK)                 -- Miền Bắc / Trung / Nam + sub-region
  ├── dim_farm.region_id
  ├── dim_customer.region_id
  ├── fact_sales.region_id
  └── fact_market_price.region_id          (NULL cho giá NVL toàn cầu)

dim_farm (farm_id PK)                     -- 68 trại (42 lợn thịt, 8 lợn nái, 18 gà)
  ├── company_id ────────────► dim_company.company_id
  ├── region_id  ────────────► dim_region.region_id
  ├── fact_farm_weekly.farm_id
  └── dim_herd_batch.farm_id

dim_herd_batch (batch_id PK)              -- ~2.400 lứa nuôi
  ├── farm_id ───────────────► dim_farm.farm_id
  └── fact_farm_weekly.batch_id            (NULL với trại gà đẻ vận hành liên tục)

dim_feed_mill (mill_id PK)                -- 6 nhà máy TĂCN
  └── fact_feed_production.mill_id

dim_product (product_id PK)               -- ~180 SKU
  ├── segment_id ────────────► dim_segment.segment_id
  ├── fact_sales.product_id
  └── fact_transfer_pricing.product_id

dim_customer (customer_id PK)             -- ~850 khách hàng (32 khách NỘI BỘ)
  ├── region_id ─────────────► dim_region.region_id
  ├── internal_company_id ───► dim_company.company_id  (NULL nếu ngoại bộ)
  └── fact_sales.customer_id

dim_channel (channel_id PK)               -- 8 kênh
  └── fact_sales.channel_id

dim_material (material_id PK)             -- 22 NVL TĂCN
  └── fact_material_purchase.material_id

_meta_tables / _meta_columns / _meta_kpi / _meta_glossary   -- nguồn truth mô tả schema
```

**Ba trục quan hệ chính:**
1. **Trục bán hàng:** `fact_sales` nối `dim_calendar` × `dim_product` × `dim_customer` × `dim_company` × `dim_channel` × `dim_region`. Cột `is_internal` chia đôi thế giới.
2. **Trục vận hành:** `fact_farm_weekly` nối `dim_week` × `dim_farm` × `dim_herd_batch`. Đây là nơi mọi vấn đề chăn nuôi lộ ra.
3. **Trục chuyển giá:** `fact_transfer_pricing` nối `dim_company` (hai lần: bên bán và bên mua) × `dim_product` × `dim_calendar`. Bảng cầu nối giữa hai trục trên.

---

## DIMENSION TABLES

### 1. `dim_calendar` (546 rows)
Lịch ngày, có đánh dấu mùa vụ Việt Nam.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `date_key` | DATE PK | Ngày | 2025-01-01 → 2026-06-30 |
| `year` | SMALLINT | Năm | |
| `quarter` | TINYINT | Quý 1–4 | |
| `month` | TINYINT | Tháng 1–12 | |
| `month_date` | DATE | Ngày đầu tháng | Dùng JOIN với `fact_pnl_monthly` |
| `week_of_year` | TINYINT | Tuần ISO | |
| `iso_week_key` | VARCHAR(8) | Khóa tuần | VD `2026-W19` → JOIN `dim_week` |
| `day_of_week` | VARCHAR(3) | Mon–Sun | |
| `is_weekend` | BOOLEAN | | |
| `is_tet_period` | BOOLEAN | Trong kỳ Tết Nguyên Đán | ±10 ngày quanh mùng 1 |
| `lunar_month` | TINYINT | Tháng âm lịch | |
| `season_phase` | VARCHAR(20) | Giai đoạn mùa vụ | 'Tết' / 'Sau Tết – tái đàn' / 'Mùa mưa – rủi ro dịch' / 'Tích đàn cuối năm' |

### 2. `dim_week` (78 rows)
Tuần ISO — grain của toàn bộ dữ liệu vận hành chăn nuôi.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `week_key` | VARCHAR(8) PK | Khóa tuần | `2026-W19` |
| `week_start_date` | DATE | Thứ Hai | |
| `week_end_date` | DATE | Chủ Nhật | |
| `year` | SMALLINT | | |
| `week_number` | TINYINT | 1–53 | |
| `month` | TINYINT | Tháng chứa phần lớn tuần | |
| `quarter` | TINYINT | | |

⚠️ **Mốc tuần quan trọng:** `2026-W19` = 04/05/2026 (điểm khởi phát bất thường đàn miền Trung) · `2026-W24` = 08/06/2026 (ASF được ghi nhận chính thức) · `2026-W26` = 22/06/2026 (tuần dữ liệu cuối cùng).

### 3. `dim_segment` (12 rows)
Bốn khối của chuỗi 3F+ và các sub-segment.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `segment_id` | INT PK | | |
| `segment_code` | VARCHAR(10) | FEED / FARM / FOOD / FUTURE | Dùng filter, không dùng tên tiếng Việt |
| `segment_name_vi` | VARCHAR(50) | 'Thức ăn chăn nuôi' / 'Chăn nuôi' / 'Thực phẩm' / 'Thương mại – Dịch vụ – Đầu tư' | |
| `sub_segment_name_vi` | VARCHAR(60) | VD 'Chăn nuôi lợn', 'Chăn nuôi gà', 'Dầu thực vật', 'Bất động sản' | |
| `display_order` | TINYINT | | |

### 4. `dim_company` (24 rows)
Công ty thành viên trong tập đoàn.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `company_id` | INT PK | | |
| `company_name_vi` | VARCHAR(120) | Tên đầy đủ | |
| `company_short_name` | VARCHAR(40) | VD 'Dabaco Thanh Hóa' | |
| `segment_id` | INT FK | → `dim_segment` | |
| `province` | VARCHAR(50) | | |
| `is_consolidated` | BOOLEAN | Có hợp nhất vào BCTC không | Tất cả = TRUE trong mock data |
| `established_year` | SMALLINT | | |

### 5. `dim_region` (12 rows)

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `region_id` | INT PK | | |
| `region_name_vi` | VARCHAR(30) | 'Miền Bắc' / 'Miền Trung' / 'Miền Nam' | |
| `sub_region_name_vi` | VARCHAR(50) | VD 'Đồng bằng sông Hồng', 'Bắc Trung Bộ', 'Đông Nam Bộ' | |
| `province_list` | TEXT | Danh sách tỉnh thuộc vùng | |

⚠️ Giá lợn hơi khác nhau theo vùng: Miền Nam ≈ Miền Bắc × 1,035; Miền Trung ≈ Miền Bắc × 0,975. Không dùng một giá bình quân cả nước cho phân tích cấp trại.

### 6. `dim_farm` (68 rows)
Trại chăn nuôi — bảng quan trọng nhất cho phân tích vận hành.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `farm_id` | INT PK | | |
| `farm_name_vi` | VARCHAR(80) | VD 'Trại lợn Dabaco Thanh Hóa 2' | |
| `farm_type` | VARCHAR(20) | LON_THIT (42) / LON_NAI (8) / GA_THIT / GA_DE / GA_GIONG (18 tổng) | |
| `company_id` | INT FK | → `dim_company` | |
| `region_id` | INT FK | → `dim_region` | |
| `province` | VARCHAR(50) | | |
| `design_capacity_head` | INT | Sức chứa thiết kế (con/lứa) | Trại lớn 12.000–18.000 |
| `commissioned_year` | SMALLINT | Năm đưa vào vận hành | **Tương quan mạnh với hiệu suất** |
| `biosecurity_level` | CHAR(1) | A (cao nhất) / B / C | **Chỉ báo rủi ro dịch bệnh — luôn kiểm tra khi thấy hao hụt bất thường** |
| `is_closed_system` | BOOLEAN | Chuồng kín có điều hòa | |
| `notes_vi` | VARCHAR(200) | Ghi chú vận hành | Có thể chứa thông tin vị trí địa lý hữu ích |

⚠️ **Phân tầng giá thành (đã thiết kế sẵn trong data):** 11 trại nhóm A (<52.000 đ/kg) · 22 trại nhóm B (52.000–58.000) · 9 trại nhóm C (>58.000). Dùng cho phân tích điểm hòa vốn.

### 7. `dim_feed_mill` (6 rows)

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `mill_id` | INT PK | | |
| `mill_name_vi` | VARCHAR(80) | | |
| `province` | VARCHAR(50) | | |
| `capacity_tons_per_year` | INT | Công suất thiết kế | Tổng 6 nhà máy = 1.500.000 tấn/năm |
| `commissioned_year` | SMALLINT | | |
| `automation_level` | VARCHAR(20) | 'Cao' / 'Trung bình' / 'Cơ bản' | |

### 8. `dim_product` (~180 rows)

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `product_id` | INT PK | | |
| `product_code` | VARCHAR(20) | VD 'DL15', 'DG12' | |
| `product_name_vi` | VARCHAR(120) | VD 'Dabaco DL15 Cám lợn thịt 30-60kg' | |
| `product_group` | VARCHAR(30) | CAM_LON / CAM_GA / CAM_VIT / LON_HOI / GA_THIT / GA_GIONG / TRUNG / THUC_PHAM_CHE_BIEN / DAU_AN / KHAC | |
| `product_category` | VARCHAR(50) | Phân nhóm chi tiết hơn | |
| `segment_id` | INT FK | → `dim_segment` | |
| `unit` | VARCHAR(10) | kg / tấn / con / quả / lít | ⚠️ **Không SUM `quantity` xuyên nhóm sản phẩm khác đơn vị** |
| `standard_price_vnd` | DECIMAL(15,2) | Giá niêm yết | Giá thực tế trong `fact_sales` khác do chiết khấu |
| `popularity_weight` | DECIMAL(6,4) | Trọng số Pareto | Top 20% SKU ≈ 80% doanh thu |

### 9. `dim_customer` (~850 rows)

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `customer_id` | INT PK | | |
| `customer_name_vi` | VARCHAR(120) | | |
| `customer_type` | VARCHAR(20) | DAI_LY_C1 / DAI_LY_C2 / TRANG_TRAI / LO_MO / SIEU_THI / CHO_DAU_MOI / XUAT_KHAU / **NOI_BO** | |
| `region_id` | INT FK | → `dim_region` | |
| `province` | VARCHAR(50) | | |
| `is_internal` | BOOLEAN | **Khách hàng nội bộ trong chuỗi** | 32 records = TRUE |
| `internal_company_id` | INT FK NULL | → `dim_company` khi `is_internal = 1` | **NULL với mọi khách ngoại bộ — dùng COALESCE khi JOIN** |
| `credit_limit_vnd` | DECIMAL(20,2) | Hạn mức công nợ | |
| `first_order_date` | DATE | | |

### 10. `dim_channel` (8 rows)

| Cột | Kiểu | Mô tả |
|---|---|---|
| `channel_id` | INT PK | |
| `channel_name_vi` | VARCHAR(50) | 'Đại lý cấp 1', 'Đại lý cấp 2', 'Trang trại trực tiếp', 'Lò mổ – thương lái', 'Siêu thị – MT', 'Chợ đầu mối', 'Xuất khẩu', 'Nội bộ chuỗi' |
| `channel_type` | VARCHAR(20) | GT / MT / DIRECT / EXPORT / INTERNAL |
| `is_internal` | BOOLEAN | |

### 11. `dim_material` (22 rows)
Nguyên vật liệu sản xuất thức ăn chăn nuôi.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `material_id` | INT PK | | |
| `material_name_vi` | VARCHAR(60) | 'Ngô hạt', 'Khô đậu tương', 'Cám mì', 'DDGS'... | |
| `material_code` | VARCHAR(20) | | |
| `material_group` | VARCHAR(20) | NANG_LUONG / DAM / PHU_GIA / PREMIX | |
| `origin_country` | VARCHAR(40) | Brazil / Argentina / Hoa Kỳ / Việt Nam / Peru | |
| `is_imported` | BOOLEAN | | ~85% chi phí NVL là hàng nhập |
| `currency` | CHAR(3) | USD / VND | Quyết định có chịu rủi ro tỷ giá không |
| `unit` | VARCHAR(10) | tấn / kg | |

### 12. `dim_herd_batch` (~2.400 rows)
Lứa nuôi — đơn vị quản lý đàn.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `batch_id` | INT PK | | |
| `farm_id` | INT FK | → `dim_farm` | |
| `batch_code` | VARCHAR(30) | VD 'TH2-2026-L03' | |
| `species` | VARCHAR(10) | LON / GA | |
| `start_date` | DATE | Ngày vào đàn | |
| `expected_end_date` | DATE | Dự kiến xuất | Lợn thịt: +165 ngày |
| `actual_end_date` | DATE NULL | Thực tế xuất | **NULL = lứa đang nuôi** |
| `initial_head` | INT | Số con vào đàn | |
| `breed_name` | VARCHAR(50) | 'Landrace × Yorkshire', 'Duroc lai 3 máu', 'Ross 308', 'Lohmann Brown'... | |

---

## FACT TABLES

### 13. `fact_sales` ⭐ (FACT CHÍNH — ~1.400.000 rows)
Giao dịch bán hàng chi tiết, **bao gồm CẢ bán ngoại bộ và bán nội bộ trong chuỗi**. Grain: 1 dòng = 1 line item.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `sale_id` | BIGINT PK | | |
| `date_key` | DATE FK | → `dim_calendar` | |
| `company_id` | INT FK | Công ty bán | |
| `product_id` | INT FK | → `dim_product` | |
| `customer_id` | INT FK | → `dim_customer` | |
| `channel_id` | INT FK | → `dim_channel` | |
| `region_id` | INT FK | Vùng của khách hàng | |
| `quantity` | DECIMAL(15,3) | Số lượng | theo `dim_product.unit` |
| `unit` | VARCHAR(10) | kg/tấn/con/quả/lít | |
| `unit_price_vnd` | DECIMAL(15,2) | Đơn giá trước chiết khấu | VND |
| `gross_amount_vnd` | DECIMAL(20,2) | Thành tiền gộp | VND |
| `discount_vnd` | DECIMAL(20,2) | Chiết khấu | VND |
| `net_amount_vnd` | DECIMAL(20,2) | **Doanh thu thuần** | VND |
| `cogs_vnd` | DECIMAL(20,2) | Giá vốn | VND |
| `gross_profit_vnd` | DECIMAL(20,2) | Lợi nhuận gộp | VND |
| `is_internal` | BOOLEAN | **0 = bán ra ngoài · 1 = bán nội bộ chuỗi** | |

⚠️ **LUÔN dùng `net_amount_vnd` cho doanh thu, KHÔNG dùng `gross_amount_vnd`.**

⚠️⚠️ **LUÔN nêu rõ `is_internal` trong WHERE.** Doanh thu thuần hợp nhất công bố = chỉ `is_internal = 0`. Cộng cả hai sẽ thổi phồng doanh thu ~65% và không khớp bất kỳ con số nào trên báo cáo tài chính.

⚠️ **Không SUM `quantity` xuyên nhóm sản phẩm** — cám tính bằng kg, lợn tính bằng con, trứng tính bằng quả, dầu ăn tính bằng lít.

### 14. `fact_farm_weekly` ⭐ (FACT VẬN HÀNH CHÍNH — ~5.300 rows)
Chỉ số vận hành đàn theo trại × tuần. **Đây là nơi mọi vấn đề chăn nuôi lộ ra trước khi nó xuất hiện trên báo cáo tài chính.**

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `record_id` | BIGINT PK | | |
| `week_key` | VARCHAR(8) FK | → `dim_week` | |
| `farm_id` | INT FK | → `dim_farm` | |
| `batch_id` | INT FK NULL | → `dim_herd_batch`. **NULL với trại gà đẻ vận hành liên tục** | |
| `opening_head` | INT | Đàn đầu tuần | con |
| `intake_head` | INT | Nhập đàn trong tuần | con |
| `sold_head` | INT | Xuất bán | con |
| `mortality_head` | INT | Chết | con |
| `culled_head` | INT | Loại thải | con |
| `closing_head` | INT | Đàn cuối tuần | con |
| `mortality_rate_pct` | DECIMAL(6,3) | **(chết + loại thải) / đầu đàn** | % |
| `feed_consumed_kg` | DECIMAL(15,2) | Cám tiêu thụ | kg |
| `feed_cost_vnd` | DECIMAL(20,2) | Chi phí cám | VND |
| `weight_gain_kg` | DECIMAL(15,2) | Tăng trọng trong tuần | kg |
| `fcr` | DECIMAL(5,3) | **Hệ số chuyển đổi thức ăn** = cám / tăng trọng | |
| `adg_gram` | INT | Tăng trọng bình quân ngày | g/con/ngày |
| `avg_weight_kg` | DECIMAL(6,2) | Trọng lượng bình quân đàn | kg |
| `live_weight_sold_kg` | DECIMAL(15,2) | **Khối lượng hơi xuất bán** | kg |
| `medication_cost_vnd` | DECIMAL(20,2) | Chi phí thú y, vaccine | VND |
| `labor_cost_vnd` | DECIMAL(20,2) | Nhân công | VND |
| `overhead_cost_vnd` | DECIMAL(20,2) | Khấu hao, điện nước | VND |
| `total_cost_vnd` | DECIMAL(20,2) | Tổng chi phí | VND |
| `cost_per_kg_live_vnd` | DECIMAL(15,2) | **Giá thành / kg hơi** | VND/kg |
| `laying_rate_pct` | DECIMAL(6,3) NULL | Tỷ lệ đẻ | % — **chỉ trại GA_DE, NULL với trại khác** |
| `eggs_produced` | INT NULL | Sản lượng trứng | quả — **NULL với trại khác** |

⚠️ **Đây là bảng WEEKLY.** Không trả lời được câu hỏi ở mức ngày về chỉ số đàn.

⚠️ **KHÔNG dùng `AVG(fcr)` hay `AVG(cost_per_kg_live_vnd)` khi tổng hợp nhiều trại.** Phải tính có trọng số: `SUM(feed_consumed_kg)/SUM(weight_gain_kg)` và `SUM(total_cost_vnd)/SUM(live_weight_sold_kg)`. Bình quân số học sẽ cho trại nhỏ trọng số ngang trại lớn.

⚠️ **`cost_per_kg_live_vnd` đã bao gồm giá cám NỘI BỘ.** Nếu giá chuyển giao cao hơn thị trường, giá thành này bị thổi phồng. Xem `fact_transfer_pricing` để quy đổi về giá cám thị trường trước khi so sánh với benchmark ngành.

⚠️ **Ràng buộc số học từng dòng:** `closing_head = opening_head + intake_head − sold_head − mortality_head − culled_head`.

### 15. `fact_feed_production` (~11.000 rows)
Sản xuất thức ăn chăn nuôi theo nhà máy × ngày × dòng sản phẩm.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `production_id` | BIGINT PK | | |
| `date_key` | DATE FK | | |
| `mill_id` | INT FK | → `dim_feed_mill` | |
| `product_group` | VARCHAR(30) | CAM_LON / CAM_GA / CAM_VIT | |
| `output_tons` | DECIMAL(12,3) | Sản lượng | tấn |
| `material_cost_vnd` | DECIMAL(20,2) | Chi phí NVL | VND |
| `processing_cost_vnd` | DECIMAL(20,2) | Chi phí chế biến | VND |
| `energy_cost_vnd` | DECIMAL(20,2) | Năng lượng | VND |
| `total_cost_vnd` | DECIMAL(20,2) | Tổng | VND |
| `cost_per_ton_vnd` | DECIMAL(15,2) | Giá thành/tấn | VND/tấn |
| `capacity_utilization_pct` | DECIMAL(6,3) | Công suất huy động | % |

### 16. `fact_material_purchase` (~4.800 rows)
Mua nguyên vật liệu — nơi rủi ro giá hàng hóa và tỷ giá giao nhau.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `purchase_id` | BIGINT PK | | |
| `date_key` | DATE FK | | |
| `material_id` | INT FK | → `dim_material` | |
| `quantity_tons` | DECIMAL(12,3) | | tấn |
| `unit_price_original` | DECIMAL(15,4) | Giá gốc theo `currency` | USD hoặc VND |
| `currency` | CHAR(3) | USD / VND | |
| `fx_rate` | DECIMAL(12,2) | Tỷ giá áp dụng | VND/USD |
| `unit_price_vnd` | DECIMAL(15,2) | Giá quy đổi | VND/tấn |
| `total_amount_vnd` | DECIMAL(20,2) | | VND |
| `supplier_country` | VARCHAR(40) | | |
| `is_spot` | BOOLEAN | Mua giao ngay hay hợp đồng kỳ hạn | |

⚠️ **Khi phân tích biến động chi phí NVL, phải TÁCH hai thành phần:** biến động giá quốc tế (`unit_price_original`) và biến động tỷ giá (`fx_rate`). Chúng đòi hỏi hai loại hành động phòng ngừa khác nhau.

### 17. `fact_market_price` (~4.900 rows)
Giá tham chiếu thị trường theo ngày. **Không phải giá bán của Dabaco** — đây là giá thị trường bên ngoài dùng để benchmark.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `price_id` | BIGINT PK | | |
| `date_key` | DATE FK | | |
| `price_code` | VARCHAR(20) | LON_HOI / GA_CN / GA_TA / TRUNG / NGO / KHO_DAU / CAM_MI | |
| `region_id` | INT FK NULL | **NULL với giá NVL toàn cầu** | |
| `price_vnd` | DECIMAL(15,2) | | VND theo `unit` |
| `unit` | VARCHAR(10) | kg / tấn / quả | |
| `source_note` | VARCHAR(100) | | |

⚠️ **Giá lợn hơi có 3 dòng mỗi ngày** (Bắc/Trung/Nam). Lọc `region_id` hoặc sẽ nhân ba số liệu.

### 18. `fact_pnl_monthly` ⭐ (~432 rows)
Báo cáo kết quả kinh doanh theo công ty × tháng. **Nguồn truth cho mọi con số tài chính cấp tập đoàn.**

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `pnl_id` | INT PK | | |
| `month_date` | DATE | Ngày đầu tháng | |
| `company_id` | INT FK | | |
| `segment_id` | INT FK | | |
| `revenue_external_vnd` | DECIMAL(20,2) | **Doanh thu ngoại bộ** | VND |
| `revenue_internal_vnd` | DECIMAL(20,2) | Doanh thu nội bộ | VND |
| `revenue_total_vnd` | DECIMAL(20,2) | Tổng | VND |
| `cogs_vnd` | DECIMAL(20,2) | Giá vốn | VND |
| `gross_profit_vnd` | DECIMAL(20,2) | Lợi nhuận gộp | VND |
| `gross_margin_pct` | DECIMAL(6,3) | Biên gộp | % |
| `selling_expense_vnd` | DECIMAL(20,2) | Chi phí bán hàng | VND |
| `admin_expense_vnd` | DECIMAL(20,2) | Chi phí QLDN | VND |
| `financial_expense_vnd` | DECIMAL(20,2) | Chi phí tài chính (chủ yếu lãi vay) | VND |
| `financial_income_vnd` | DECIMAL(20,2) | Doanh thu tài chính | VND |
| `other_income_vnd` | DECIMAL(20,2) | Thu nhập khác | VND |
| `profit_before_tax_vnd` | DECIMAL(20,2) | LNTT | VND |
| `tax_vnd` | DECIMAL(20,2) | Thuế TNDN | VND |
| `profit_after_tax_vnd` | DECIMAL(20,2) | **LNST** | VND |

⚠️ **Bảng này đã ELIMINATE giao dịch nội bộ ở cấp hợp nhất.** `SUM(profit_after_tax_vnd)` toàn tập đoàn = lợi nhuận hợp nhất công bố. Nhưng `profit_after_tax_vnd` của TỪNG công ty vẫn chứa phần lợi nhuận dịch chuyển qua giá chuyển giao — đây là lý do phải đọc kèm `fact_transfer_pricing`.

⚠️ `gross_margin_pct` tính trên `revenue_external_vnd`, không phải `revenue_total_vnd`.

### 19. `fact_plan_monthly` (~216 rows)
Kế hoạch năm đã phân bổ theo tháng.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `plan_id` | INT PK | | |
| `month_date` | DATE | | |
| `segment_id` | INT FK | | |
| `plan_year` | SMALLINT | | |
| `plan_revenue_total_vnd` | DECIMAL(20,2) | **Gồm tiêu thụ nội bộ** | VND |
| `plan_revenue_external_vnd` | DECIMAL(20,2) | Chỉ ngoại bộ | VND |
| `plan_gross_profit_vnd` | DECIMAL(20,2) | | VND |
| `plan_profit_after_tax_vnd` | DECIMAL(20,2) | | VND |

⚠️ **Kế hoạch KHÔNG chia đều 12 tháng.** Đã phân bổ theo mùa vụ — H2 có tỷ trọng cao hơn H1. Khi đánh giá tiến độ, so với `SUM(plan_*)` của các tháng đã qua, không phải với 50% kế hoạch năm.

⚠️ **`plan_revenue_total_vnd` cả năm 2026 = 29.311 tỷ (gồm nội bộ)**, trong khi doanh thu thuần công bố chỉ tính ngoại bộ. Đây là nguồn gây nhầm lẫn phổ biến nhất khi so kế hoạch với thực hiện.

### 20. `fact_transfer_pricing` ⭐ (~26.000 rows)
**Giao dịch chuyển giao nội bộ giữa các khối trong chuỗi 3F.** Bảng đặc thù nhất của Dabaco — không tồn tại ở doanh nghiệp không tích hợp dọc.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `tp_id` | BIGINT PK | | |
| `date_key` | DATE FK | | |
| `seller_company_id` | INT FK | → `dim_company` | |
| `buyer_company_id` | INT FK | → `dim_company` | |
| `seller_segment_id` | INT FK | → `dim_segment` | |
| `buyer_segment_id` | INT FK | → `dim_segment` | |
| `product_id` | INT FK | → `dim_product` | |
| `quantity` | DECIMAL(15,3) | | theo `unit` |
| `unit` | VARCHAR(10) | kg / con | |
| `internal_price_vnd` | DECIMAL(15,2) | **Giá chuyển giao nội bộ** | VND/đơn vị |
| `market_reference_price_vnd` | DECIMAL(15,2) | **Giá thị trường tham chiếu cùng SKU cùng kỳ** | VND/đơn vị |
| `price_gap_vnd` | DECIMAL(15,2) | Chênh lệch = nội bộ − thị trường | VND/đơn vị |
| `internal_amount_vnd` | DECIMAL(20,2) | Giá trị theo giá nội bộ | VND |
| `market_equivalent_amount_vnd` | DECIMAL(20,2) | Giá trị nếu tính theo giá thị trường | VND |
| `transfer_margin_vnd` | DECIMAL(20,2) | **Phần lợi nhuận dịch chuyển** = internal − market_equivalent | VND |

⚠️ **`market_reference_price_vnd` là giá bán ngoại bộ bình quân cùng SKU cùng tháng, ĐÃ TRỪ chiết khấu đại lý bình quân 4,2%.** Có thể kiểm chứng độc lập từ `fact_sales WHERE is_internal = 0` — nên làm, vì cross-validation này là bằng chứng mạnh nhất khi trình bày với lãnh đạo.

⚠️ **`transfer_margin_vnd` dương nghĩa là bên BÁN đang hưởng lợi nhuận vốn thuộc về bên MUA.** Nó KHÔNG phải lợi nhuận tạo thêm cho tập đoàn — ở cấp hợp nhất, toàn bộ khoản này bị eliminate.

⚠️ **Hai luồng chuyển giao chính:** FEED → FARM (cám, chiếm phần lớn giá trị) và FARM → FOOD (lợn hơi, gà). Luôn lọc theo cặp segment khi phân tích.

### 21. `fact_inventory_snapshot` (~3.240 rows)
Tồn kho cuối tháng theo công ty × nhóm sản phẩm.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `snapshot_id` | INT PK | | |
| `snapshot_date` | DATE | **Ngày cuối tháng** | |
| `company_id` | INT FK | | |
| `product_group` | VARCHAR(30) | | |
| `quantity` | DECIMAL(15,3) | | theo `unit` |
| `unit` | VARCHAR(10) | | |
| `value_vnd` | DECIMAL(20,2) | Giá trị tồn | VND |
| `days_on_hand` | DECIMAL(8,2) | Số ngày tồn kho | ngày |

⚠️ **ĐÂY LÀ SNAPSHOT.** Dùng `WHERE snapshot_date = 'ngày cụ thể'`. **KHÔNG SUM nhiều snapshot** — sẽ cộng dồn cùng một lượng hàng nhiều lần.

### 22. `fact_debt_snapshot` (~432 rows)
Dư nợ vay cuối tháng theo công ty.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `debt_id` | INT PK | | |
| `snapshot_date` | DATE | Ngày cuối tháng | |
| `company_id` | INT FK | | |
| `short_term_debt_vnd` | DECIMAL(20,2) | Vay ngắn hạn | VND |
| `long_term_debt_vnd` | DECIMAL(20,2) | Vay dài hạn | VND |
| `total_debt_vnd` | DECIMAL(20,2) | Tổng dư nợ | VND |
| `avg_interest_rate_pct` | DECIMAL(6,3) | Lãi suất bình quân | %/năm |
| `interest_expense_month_vnd` | DECIMAL(20,2) | Chi phí lãi vay trong tháng | VND |

⚠️ **SNAPSHOT** — không SUM `total_debt_vnd` qua nhiều tháng. Nhưng `interest_expense_month_vnd` LÀ dòng chảy, được phép SUM.

### 23–26. Metadata tables
`_meta_tables` · `_meta_columns` · `_meta_kpi` · `_meta_glossary` — query trực tiếp khi cần xác minh ý nghĩa cột hoặc thuật ngữ ngành (FCR, ADG, ASF, GGP/GP/PS, cám đậm đặc, tỷ lệ đẻ...).

---

## SQL TEMPLATES

### T1 — Bức tranh tài chính theo khối, một kỳ bất kỳ
```sql
SELECT s.segment_code,
       s.segment_name_vi,
       ROUND(SUM(p.revenue_external_vnd)/1e9, 1)  AS dt_ngoai_bo_ty,
       ROUND(SUM(p.revenue_internal_vnd)/1e9, 1)  AS dt_noi_bo_ty,
       ROUND(SUM(p.gross_profit_vnd)/1e9, 1)      AS ln_gop_ty,
       ROUND(SUM(p.gross_profit_vnd)/NULLIF(SUM(p.revenue_external_vnd),0)*100, 1) AS bien_gop_pct,
       ROUND(SUM(p.profit_after_tax_vnd)/1e9, 1)  AS lnst_ty
FROM `fact_pnl_monthly` p
JOIN `dim_segment` s ON s.segment_id = p.segment_id
WHERE p.month_date BETWEEN '2026-01-01' AND '2026-06-30'
GROUP BY s.segment_code, s.segment_name_vi
ORDER BY dt_ngoai_bo_ty DESC;
```

### T2 — So sánh hai kỳ (YoY) và tính chênh lệch
```sql
SELECT s.segment_name_vi,
       ROUND(SUM(CASE WHEN YEAR(p.month_date)=2025 THEN p.revenue_external_vnd END)/1e9,1) AS dt_2025,
       ROUND(SUM(CASE WHEN YEAR(p.month_date)=2026 THEN p.revenue_external_vnd END)/1e9,1) AS dt_2026,
       ROUND(SUM(CASE WHEN YEAR(p.month_date)=2025 THEN p.profit_after_tax_vnd END)/1e9,1) AS lnst_2025,
       ROUND(SUM(CASE WHEN YEAR(p.month_date)=2026 THEN p.profit_after_tax_vnd END)/1e9,1) AS lnst_2026
FROM `fact_pnl_monthly` p
JOIN `dim_segment` s ON s.segment_id = p.segment_id
WHERE MONTH(p.month_date) BETWEEN 4 AND 6          -- Q2 hai năm
GROUP BY s.segment_name_vi
ORDER BY dt_2026 DESC;
```

### T3 — Giá lợn hơi bình quân theo tháng và vùng (gia quyền sản lượng)
```sql
SELECT DATE_FORMAT(mp.date_key, '%Y-%m') AS thang,
       r.region_name_vi,
       ROUND(AVG(mp.price_vnd), 0) AS gia_bq_dong_kg,
       ROUND(MIN(mp.price_vnd), 0) AS gia_thap_nhat,
       ROUND(MAX(mp.price_vnd), 0) AS gia_cao_nhat
FROM `fact_market_price` mp
JOIN `dim_region` r ON r.region_id = mp.region_id
WHERE mp.price_code = 'LON_HOI'
  AND mp.date_key BETWEEN '2025-01-01' AND '2026-06-30'
GROUP BY thang, r.region_name_vi
ORDER BY thang, r.region_name_vi;
```

### T4 — Xếp hạng trại lợn theo giá thành (có trọng số đúng)
```sql
SELECT f.farm_name_vi,
       f.province,
       f.biosecurity_level,
       f.commissioned_year,
       ROUND(SUM(w.total_cost_vnd)/NULLIF(SUM(w.live_weight_sold_kg),0), 0) AS gia_thanh_dong_kg,
       ROUND(SUM(w.feed_consumed_kg)/NULLIF(SUM(w.weight_gain_kg),0), 3)    AS fcr,
       ROUND(SUM(w.mortality_head + w.culled_head)/NULLIF(SUM(w.opening_head),0)*100, 2) AS hao_hut_pct,
       ROUND(SUM(w.live_weight_sold_kg)/1000, 0) AS san_luong_tan
FROM `fact_farm_weekly` w
JOIN `dim_farm` f ON f.farm_id = w.farm_id
JOIN `dim_week` k ON k.week_key = w.week_key
WHERE f.farm_type = 'LON_THIT'
  AND k.week_start_date BETWEEN '2026-04-01' AND '2026-06-30'
GROUP BY f.farm_id, f.farm_name_vi, f.province, f.biosecurity_level, f.commissioned_year
ORDER BY gia_thanh_dong_kg DESC;
```

### T5 — Phát hiện trại có hao hụt bất thường (so với chính lịch sử của nó)
```sql
WITH baseline AS (
  SELECT w.farm_id,
         AVG(w.mortality_rate_pct)    AS bq_lich_su,
         STDDEV(w.mortality_rate_pct) AS do_lech
  FROM `fact_farm_weekly` w
  JOIN `dim_week` k ON k.week_key = w.week_key
  WHERE k.week_start_date < '2026-04-01'
  GROUP BY w.farm_id
)
SELECT f.farm_name_vi, f.province, f.biosecurity_level,
       w.week_key,
       w.mortality_rate_pct,
       ROUND(b.bq_lich_su, 2) AS bq_lich_su,
       ROUND((w.mortality_rate_pct - b.bq_lich_su)/NULLIF(b.do_lech,0), 2) AS so_do_lech_chuan,
       w.fcr, w.adg_gram
FROM `fact_farm_weekly` w
JOIN `dim_farm` f  ON f.farm_id  = w.farm_id
JOIN baseline  b   ON b.farm_id  = w.farm_id
JOIN `dim_week` k  ON k.week_key = w.week_key
WHERE k.week_start_date >= '2026-04-01'
  AND w.mortality_rate_pct > b.bq_lich_su + 1.5 * b.do_lech
ORDER BY f.farm_name_vi, w.week_key;
```

### T6 — Bóc tách chênh lệch giá chuyển giao Feed → Farm
```sql
SELECT DATE_FORMAT(tp.date_key, '%Y-%m') AS thang,
       ROUND(SUM(tp.quantity)/1000, 0)                                        AS cam_noi_bo_tan,
       ROUND(SUM(tp.internal_amount_vnd)/NULLIF(SUM(tp.quantity),0), 0)        AS gia_noi_bo_dong_kg,
       ROUND(SUM(tp.market_equivalent_amount_vnd)/NULLIF(SUM(tp.quantity),0),0) AS gia_thi_truong_dong_kg,
       ROUND(SUM(tp.transfer_margin_vnd)/NULLIF(SUM(tp.quantity),0), 0)        AS chenh_dong_kg,
       ROUND(SUM(tp.transfer_margin_vnd)/1e9, 1)                               AS lai_dich_chuyen_ty
FROM `fact_transfer_pricing` tp
JOIN `dim_segment` ss ON ss.segment_id = tp.seller_segment_id
JOIN `dim_segment` bs ON bs.segment_id = tp.buyer_segment_id
WHERE ss.segment_code = 'FEED'
  AND bs.segment_code = 'FARM'
  AND tp.date_key BETWEEN '2026-01-01' AND '2026-06-30'
GROUP BY thang WITH ROLLUP;
```

### T7 — Kiểm chứng độc lập giá cám ngoại bộ (cross-validate T6)
```sql
-- Tính giá bán cám ra ngoài từ fact_sales, so với market_reference_price trong T6
SELECT DATE_FORMAT(s.date_key, '%Y-%m') AS thang,
       p.product_group,
       ROUND(SUM(s.quantity)/1000, 0)                              AS san_luong_tan,
       ROUND(SUM(s.net_amount_vnd)/NULLIF(SUM(s.quantity),0), 0)    AS gia_ban_thuc_te_dong_kg
FROM `fact_sales` s
JOIN `dim_product` p ON p.product_id = s.product_id
WHERE s.is_internal = 0
  AND p.product_group IN ('CAM_LON','CAM_GA','CAM_VIT')
  AND s.date_key BETWEEN '2026-01-01' AND '2026-06-30'
GROUP BY thang, p.product_group
ORDER BY thang, p.product_group;
```

### T8 — Tiến độ kế hoạch: thực hiện vs kế hoạch đã phân bổ theo tháng
```sql
SELECT DATE_FORMAT(pl.month_date, '%Y-%m') AS thang,
       ROUND(SUM(pl.plan_profit_after_tax_vnd)/1e9, 1) AS ke_hoach_ty,
       ROUND(SUM(ac.profit_after_tax_vnd)/1e9, 1)      AS thuc_hien_ty,
       ROUND(SUM(ac.profit_after_tax_vnd)/NULLIF(SUM(pl.plan_profit_after_tax_vnd),0)*100, 1) AS pct_hoan_thanh
FROM `fact_plan_monthly` pl
LEFT JOIN (
    SELECT month_date, SUM(profit_after_tax_vnd) AS profit_after_tax_vnd
    FROM `fact_pnl_monthly` GROUP BY month_date
) ac ON ac.month_date = pl.month_date
WHERE pl.plan_year = 2026
GROUP BY thang
ORDER BY thang;
```

### T9 — Phân tầng trại theo điểm hòa vốn (what-if giá lợn)
```sql
WITH gia_thanh AS (
  SELECT f.farm_id, f.farm_name_vi, f.region_id,
         SUM(w.total_cost_vnd)/NULLIF(SUM(w.live_weight_sold_kg),0) AS cost_kg,
         SUM(w.live_weight_sold_kg) AS san_luong_kg
  FROM `fact_farm_weekly` w
  JOIN `dim_farm` f ON f.farm_id = w.farm_id
  JOIN `dim_week` k ON k.week_key = w.week_key
  WHERE f.farm_type = 'LON_THIT'
    AND k.week_start_date BETWEEN '2026-01-01' AND '2026-06-30'
  GROUP BY f.farm_id, f.farm_name_vi, f.region_id
)
SELECT CASE WHEN cost_kg < 52000 THEN 'A – Lãi ở mọi kịch bản'
            WHEN cost_kg < 58000 THEN 'B – Hòa vốn mỏng'
            ELSE 'C – Lỗ ngay khi giá dưới 58.000' END AS nhom,
       COUNT(*)                              AS so_trai,
       ROUND(AVG(cost_kg), 0)                AS gia_thanh_bq,
       ROUND(SUM(san_luong_kg)/1000, 0)      AS san_luong_tan,
       ROUND(SUM(san_luong_kg)/(SELECT SUM(san_luong_kg) FROM gia_thanh)*100, 1) AS ty_trong_dan_pct
FROM gia_thanh
GROUP BY nhom
ORDER BY gia_thanh_bq;
```

### T10 — Chi phí nguyên vật liệu: tách tác động giá quốc tế vs tỷ giá
```sql
SELECT DATE_FORMAT(mp.date_key, '%Y-%m') AS thang,
       m.material_name_vi,
       ROUND(SUM(mp.quantity_tons), 0)                                    AS luong_tan,
       ROUND(SUM(mp.quantity_tons*mp.unit_price_original)/NULLIF(SUM(mp.quantity_tons),0), 2) AS gia_goc_bq,
       mp.currency,
       ROUND(AVG(mp.fx_rate), 0)                                          AS ty_gia_bq,
       ROUND(SUM(mp.total_amount_vnd)/1e9, 2)                             AS tong_chi_ty
FROM `fact_material_purchase` mp
JOIN `dim_material` m ON m.material_id = mp.material_id
WHERE m.material_group IN ('NANG_LUONG','DAM')
  AND mp.date_key BETWEEN '2025-01-01' AND '2026-06-30'
GROUP BY thang, m.material_name_vi, mp.currency
ORDER BY thang, tong_chi_ty DESC;
```

---

## JOIN WARNINGS

1. **`fact_sales` ↔ `fact_transfer_pricing` — KHÁC GRAIN.** `fact_sales` là line item bán hàng; `fact_transfer_pricing` là giao dịch chuyển giao đã tổng hợp theo ngày × SKU × cặp công ty. JOIN trực tiếp sẽ nhân đôi dòng. **Aggregate cả hai về cùng cấp (tháng × product_group) TRƯỚC khi JOIN.**

2. **`fact_sales` ↔ `fact_pnl_monthly` — KHÁC GRAIN.** Một là ngày, một là tháng. JOIN qua `dim_calendar.month_date`. Và lưu ý: tổng `fact_sales` có thể lệch nhẹ so với `fact_pnl_monthly` do các khoản điều chỉnh cuối kỳ — **`fact_pnl_monthly` là nguồn truth cho con số tài chính công bố**.

3. **`fact_inventory_snapshot` và `fact_debt_snapshot` = SNAPSHOT.** Dùng `WHERE snapshot_date = 'YYYY-MM-DD'` cho một thời điểm. **KHÔNG SUM qua nhiều tháng** — sẽ cộng dồn cùng một lượng hàng/khoản nợ nhiều lần. Ngoại lệ: `interest_expense_month_vnd` là dòng chảy, được phép SUM.

4. **`dim_customer.internal_company_id` CÓ THỂ NULL** — NULL với mọi khách hàng ngoại bộ (~818/850 records). Dùng `LEFT JOIN` + `COALESCE`, không dùng `INNER JOIN`.

5. **`fact_farm_weekly.batch_id` CÓ THỂ NULL** — NULL với trại gà đẻ (vận hành liên tục, không chia lứa). `INNER JOIN dim_herd_batch` sẽ làm mất toàn bộ dữ liệu trại gà đẻ.

6. **`fact_farm_weekly.laying_rate_pct` và `eggs_produced` CHỈ có giá trị với `farm_type = 'GA_DE'`.** NULL với 50 trại còn lại. `AVG()` sẽ tự bỏ qua NULL — đúng ý muốn — nhưng `COUNT(*)` thì không.

7. **`fact_market_price.region_id` CÓ THỂ NULL** — NULL với giá NVL toàn cầu (ngô, khô đậu). `INNER JOIN dim_region` sẽ làm mất toàn bộ giá nguyên liệu.

8. **`fact_market_price` có nhiều dòng mỗi ngày** (3 vùng × nhiều price_code). **Luôn lọc cả `price_code` VÀ `region_id`**, nếu không sẽ nhân số liệu lên nhiều lần.

9. **`dim_product.unit` không đồng nhất.** Không `SUM(quantity)` xuyên `product_group` — kg, tấn, con, quả, lít trộn lẫn sẽ ra số vô nghĩa. Luôn `GROUP BY product_group` hoặc lọc một nhóm.

10. **`fact_farm_weekly` — không dùng AVG cho chỉ số tỷ lệ.** `AVG(fcr)`, `AVG(cost_per_kg_live_vnd)`, `AVG(mortality_rate_pct)` khi gộp nhiều trại/nhiều tuần sẽ cho trại nhỏ trọng số ngang trại lớn. Luôn tính lại từ tử số và mẫu số: `SUM(feed_consumed_kg)/SUM(weight_gain_kg)`.

11. **`fact_pnl_monthly` — `gross_margin_pct` không được AVG.** Tính lại: `SUM(gross_profit_vnd)/SUM(revenue_external_vnd)`.

12. **`fact_transfer_pricing` JOIN `dim_company` HAI LẦN** (bên bán và bên mua). Phải alias rõ ràng, nếu không MySQL sẽ báo lỗi ambiguous column.

13. **`fact_plan_monthly` grain là KHỐI × THÁNG, không có `company_id`.** Không JOIN trực tiếp với `fact_pnl_monthly` ở cấp công ty — phải aggregate `fact_pnl_monthly` lên cấp segment trước.

---

## ĐƠN VỊ TIỀN TỆ VÀ ĐO LƯỜNG

| Bảng | Cột | Đơn vị |
|---|---|---|
| `fact_sales` | `net_amount_vnd`, `gross_amount_vnd`, `cogs_vnd`, `gross_profit_vnd`, `discount_vnd` | VND |
| `fact_sales` | `unit_price_vnd` | VND / đơn vị sản phẩm |
| `fact_sales` | `quantity` | theo `dim_product.unit` (kg / tấn / con / quả / lít) |
| `fact_farm_weekly` | `total_cost_vnd`, `feed_cost_vnd`, `medication_cost_vnd`, `labor_cost_vnd`, `overhead_cost_vnd` | VND |
| `fact_farm_weekly` | `cost_per_kg_live_vnd` | VND / kg hơi |
| `fact_farm_weekly` | `feed_consumed_kg`, `weight_gain_kg`, `live_weight_sold_kg` | kg |
| `fact_farm_weekly` | `adg_gram` | gram / con / ngày |
| `fact_farm_weekly` | `fcr` | tỷ số (không đơn vị) |
| `fact_farm_weekly` | `mortality_rate_pct`, `laying_rate_pct` | % |
| `fact_feed_production` | `output_tons` | tấn |
| `fact_feed_production` | `cost_per_ton_vnd` | VND / tấn |
| `fact_material_purchase` | `unit_price_original` | USD/tấn hoặc VND/tấn (theo `currency`) |
| `fact_material_purchase` | `unit_price_vnd`, `total_amount_vnd` | VND |
| `fact_material_purchase` | `fx_rate` | VND / USD |
| `fact_market_price` | `price_vnd` | VND / kg (lợn, gà) · VND / quả (trứng) · VND / tấn (NVL) |
| `fact_pnl_monthly` | tất cả cột `_vnd` | VND |
| `fact_plan_monthly` | tất cả cột `_vnd` | VND |
| `fact_transfer_pricing` | `internal_price_vnd`, `market_reference_price_vnd`, `price_gap_vnd` | VND / đơn vị |
| `fact_transfer_pricing` | `internal_amount_vnd`, `market_equivalent_amount_vnd`, `transfer_margin_vnd` | VND |
| `fact_inventory_snapshot` | `value_vnd` | VND |
| `fact_debt_snapshot` | `short_term_debt_vnd`, `long_term_debt_vnd`, `total_debt_vnd`, `interest_expense_month_vnd` | VND |

**Format hiển thị cho board:**
- ≥ 1.000 tỷ: "X.XXX tỷ" (VD "8.377 tỷ")
- 1–1.000 tỷ: "XXX,X tỷ" (VD "289,1 tỷ")
- < 1 tỷ: "XXX triệu"
- Giá lợn hơi, giá cám: nguyên đồng/kg, có dấu chấm phân cách nghìn (VD "63.200 đ/kg")
- Sản lượng: "XXX.XXX tấn" hoặc "XXX nghìn tấn"
- Phần trăm: 1 chữ số thập phân (VD "15,4%")
- FCR: 2 chữ số thập phân (VD "2,68")
- Số quyết định phân cách thập phân là **dấu phẩy**, phân cách nghìn là **dấu chấm** (chuẩn Việt Nam)
