# DATA SCHEMA — LA VIE | NƯỚC KHOÁNG ĐÓNG CHAI BI
## Database: `lavie_water_demo` (MySQL 8.0, utf8mb4_unicode_ci)
## Phạm vi: 2024-07-01 → 2026-06-30 (24 tháng, 730 ngày) | "Hiện tại" = cuối tháng 6/2026
## Tổng: 16 bảng dữ liệu + 4 bảng metadata, ~113.000 dòng

> **Quy ước chung**
> - `fiscal_period` là `VARCHAR(7)` định dạng `'YYYY-MM'`, có mặt ở hầu hết fact table. So sánh chuỗi hoạt động đúng: `BETWEEN '2025-01' AND '2025-06'`.
> - Mọi cột tiền tệ có hậu tố `_vnd`, đơn vị **VND**, kiểu `BIGINT`.
> - Mọi cột thể tích có hậu tố `_liters`, đơn vị **lít**.
> - Giá trị master data bằng **tiếng Việt**; tên bảng và cột bằng **tiếng Anh**.
> - Địa giới hành chính: **34 tỉnh/thành sau sáp nhập 01/07/2025**.

---

## SƠ ĐỒ QUAN HỆ

```
dim_calendar (date_key PK)
  ├── fact_sales_out.period_end_date
  ├── fact_production.production_date
  └── fact_inventory.snapshot_date

dim_geography (geo_id PK, province_code UK, region_code)
  ├── dim_customer.province_code
  ├── dim_route.destination_province_code
  ├── dim_warehouse.province_code
  ├── dim_plant.province_code
  ├── fact_sales_out.province_code / .region_code   (denormalized để query nhanh)
  ├── fact_pnl_monthly.region_code
  └── self-reference: dim_geography.parent_geo_id → dim_geography.geo_id (Tỉnh → Vùng)

dim_channel (channel_id PK)
  ├── dim_customer.channel_id
  ├── fact_sales_out.channel_id
  ├── fact_trade_spend.channel_id
  └── fact_pnl_monthly.channel_id

dim_customer (customer_id PK)
  ├── fact_sales_out.customer_id
  ├── fact_trade_spend.customer_id
  ├── fact_container_cycle.customer_id
  └── dim_customer.source_warehouse_code → dim_warehouse.warehouse_code

dim_product (product_id PK)
  ├── fact_sales_out.product_id
  └── fact_inventory.product_id

dim_plant (plant_id PK, plant_code UK)
  ├── dim_production_line.plant_id
  ├── dim_warehouse.supplied_by_plant_code
  └── fact_production.plant_id

dim_production_line (line_id PK)
  └── fact_production.line_id

dim_warehouse (warehouse_id PK, warehouse_code UK)
  ├── dim_route.source_warehouse_code
  ├── dim_customer.source_warehouse_code
  └── fact_inventory.warehouse_id

dim_route (route_id PK)
  ├── fact_cost_to_serve.route_id
  └── fact_sales_out.route_id
```

**Đường drill-down chính cho ba anomaly:**

```
Anomaly A (miền Trung):
  fact_sales_out ──province_code──> dim_geography ──region_name
       │                                  │
       └──route_id──> dim_route ──source_warehouse_code──> dim_warehouse ──plant
                          │
                          └──> fact_cost_to_serve (logistics_cost_per_liter)

Anomaly B (vỏ bình):
  fact_container_cycle ──customer_id──> dim_customer ──onboard_date / contract_type

Anomaly C (kênh MT):
  fact_trade_spend ──customer_id──> dim_customer ──channel_id──> dim_channel
       │  (agg về fiscal_period × customer_id TRƯỚC KHI ghép)
       └──> fact_sales_out (agg cùng grain)
```

---

## DIMENSION TABLES

### 1. `dim_calendar` (730 rows)
Lịch ngày từ 2024-07-01 đến 2026-06-30, có đánh dấu cửa sổ Tết Nguyên Đán.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `date_key` | DATE PK | Ngày | |
| `year` | SMALLINT | Năm | 2024, 2025, 2026 |
| `quarter` | TINYINT | Quý | 1–4 |
| `month` | TINYINT | Tháng | 1–12 |
| `month_name_vi` | VARCHAR(20) | Tên tháng tiếng Việt | 'Tháng 1' … |
| `week_of_year` | TINYINT | Tuần trong năm | |
| `day_of_week` | TINYINT | Thứ | 1 = Thứ Hai … 7 = Chủ Nhật |
| `day_name_vi` | VARCHAR(15) | Tên thứ | 'Thứ Hai' … 'Chủ Nhật' |
| `is_weekend` | BOOLEAN | Cuối tuần | |
| `is_holiday` | BOOLEAN | Ngày lễ VN | |
| `holiday_name_vi` | VARCHAR(60) | Tên lễ | NULL nếu không phải lễ |
| `is_tet_window` | BOOLEAN | Nằm trong cửa sổ Tết | Tết 2025 mùng 1 = 2025-01-29; Tết 2026 mùng 1 = 2026-02-17 |
| `fiscal_period` | VARCHAR(7) | Kỳ báo cáo | 'YYYY-MM' — **khóa nối chính với các fact table grain tháng** |

---

### 2. `dim_geography` (37 rows: 3 vùng + 34 tỉnh/thành)
Cây địa lý hai cấp. **Đây là bảng trọng tâm cho Anomaly A.**

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `geo_id` | INT PK | ID | |
| `geo_level` | ENUM | Cấp | 'Vùng' hoặc 'Tỉnh' |
| `province_name` | VARCHAR(60) | Tên tỉnh/thành | NULL với dòng cấp Vùng |
| `province_code` | VARCHAR(10) UK | Mã tỉnh | VD: 'HCM', 'HN', 'HATINH', 'QUANGTRI', 'HUE', 'NGHEAN' |
| `region_name` | VARCHAR(20) | Tên vùng | 'Miền Bắc' / 'Miền Trung' / 'Miền Nam' |
| `region_code` | VARCHAR(6) | Mã vùng | 'BAC' / 'TRUNG' / 'NAM' |
| `population_weight_pct` | DECIMAL(6,3) | Trọng số dân số/sức mua trong vùng | Dùng để phân bổ doanh thu |
| `is_urban_core` | BOOLEAN | Đô thị lõi | TRUE với HCM, HN, HP, ĐN, Huế, Cần Thơ |
| `parent_geo_id` | INT FK | Vùng cha | → `dim_geography.geo_id`, NULL với dòng cấp Vùng |

**Ba vùng và 34 tỉnh:**
- **Miền Bắc (17):** Hà Nội, Hải Phòng, Quảng Ninh, Bắc Ninh, Hưng Yên, Ninh Bình, Phú Thọ, Thái Nguyên, Lào Cai, Tuyên Quang, Cao Bằng, Lạng Sơn, Sơn La, Điện Biên, Lai Châu, Thanh Hóa, **Nghệ An**
- **Miền Trung (9):** **Hà Tĩnh**, **Quảng Trị**, **Huế**, Đà Nẵng, Quảng Ngãi, Gia Lai, Khánh Hòa, Đắk Lắk, Lâm Đồng
- **Miền Nam (8):** TP.HCM, Đồng Nai, Tây Ninh, Cần Thơ, Vĩnh Long, Đồng Tháp, An Giang, Cà Mau

⚠️ **Nghệ An thuộc Miền Bắc, Hà Tĩnh thuộc Miền Trung — hai tỉnh liền kề nhưng khác vùng, khác kho nguồn, chênh 55% chi phí phục vụ.** Đây là điểm mấu chốt của Anomaly A.

⚠️ Không tồn tại 'Thừa Thiên Huế' (nay là 'Huế'), 'Quảng Bình' (đã nhập vào 'Quảng Trị'), 'Bình Dương' / 'Bà Rịa – Vũng Tàu' (đã nhập vào 'TP.HCM').

---

### 3. `dim_channel` (5 rows)
Năm kênh phân phối với kinh tế học rất khác nhau.

| Cột | Kiểu | Mô tả |
|---|---|---|
| `channel_id` | INT PK | ID |
| `channel_code` | VARCHAR(6) UK | 'GT' / 'HOD' / 'MT' / 'HRC' / 'ECM' |
| `channel_name_vi` | VARCHAR(60) | Tên tiếng Việt |
| `channel_name_en` | VARCHAR(60) | Tên tiếng Anh |
| `description_vi` | VARCHAR(255) | Mô tả kênh |
| `typical_gross_margin_pct` | DECIMAL(5,2) | Gross margin điển hình |
| `typical_trade_spend_pct` | DECIMAL(5,2) | Trade spend / DT điển hình |

| Mã | Tên | %DT FY2025 | Gross margin | Trade spend/DT | **Net margin** |
|---|---|---|---|---|---|
| GT | Kênh truyền thống | 44,8% | 26,6% | 14,2% | **12,4%** |
| HOD | Giao nhà & văn phòng | 27,2% | 24,5% | 9,4% | **15,1%** 🟢 |
| MT | Kênh hiện đại | 16,3% | **33,0%** | **26,8%** | **6,2%** 🔴 |
| HRC | HORECA | 8,3% | 25,0% | 11,6% | **13,4%** |
| ECM | Thương mại điện tử | 3,4% | 32,1% | 18,3% | **13,8%** |

⚠️ **Gross margin cao nhất (MT) đi kèm net margin thấp nhất.** Không bao giờ so sánh kênh bằng gross margin.

---

### 4. `dim_customer` (380 rows) — **BẢNG TRỌNG TÂM CHO ANOMALY B**

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `customer_id` | INT PK | ID | |
| `customer_code` | VARCHAR(16) UK | Mã khách hàng | |
| `customer_name` | VARCHAR(120) | Tên khách hàng | Tiếng Việt, tên thật với khách MT |
| `channel_id` | INT FK | Kênh | → `dim_channel` |
| `province_code` | VARCHAR(10) FK | Tỉnh | → `dim_geography` |
| `region_code` | VARCHAR(6) | Vùng | Denormalized |
| `customer_tier` | ENUM | Quy mô | 'Lớn' / 'Trung' / 'Nhỏ' |
| `onboard_date` | DATE | Ngày bắt đầu hợp tác | ⚠️ **Cột then chốt cho Anomaly B** |
| `contract_type` | ENUM | Loại hợp đồng | 'CHUAN' / **'MOI_2025'** / 'MT_KEY' / 'HORECA' / 'ECOM' |
| `handles_19l` | BOOLEAN | Có kinh doanh bình 19L | TRUE với 218 khách hàng |
| `source_warehouse_code` | VARCHAR(12) FK | Kho cấp hàng | → `dim_warehouse` |
| `base_volume_share_pct` | DECIMAL(8,5) | Trọng số quy mô | Power law, top 20% ≈ 80% DT |
| `is_active` | BOOLEAN | Đang hoạt động | |

**Phân bổ theo kênh:** GT 185 · HOD 120 · MT 32 · HORECA 30 · E-commerce 13.

**Phân nhóm HOD theo `onboard_date` — đây là cách phát hiện Anomaly B:**

| Nhóm | Số đại lý | `contract_type` | Tỷ lệ thu hồi vỏ TB H1/2026 |
|---|---|---|---|
| Onboard ≥ 3 năm (trước 2023) | 78 | 'CHUAN' | **93,1%** 🟢 |
| Onboard năm 2024 | 28 | 'CHUAN' | 90,4% 🟡 |
| **Onboard sau 2025-01** | **14** | **'MOI_2025'** | **78,3%** 🔴 |

14 đại lý `MOI_2025` tập trung ở TP.HCM (vùng ven) và Đồng Nai. Hợp đồng mẫu mới của họ có **tiền cọc cố định, không ràng buộc theo sản lượng** — đó là nguyên nhân gốc.

**Khách hàng MT (32) — dùng tên thật:** Bách Hóa Xanh, WinMart, WinMart+, Co.opmart, Co.op Food, Circle K, GS25, MM Mega Market, GO!, Big C, AEON, FamilyMart, Ministop, Lotte Mart, Emart, Satrafoods, Kingfoodmart và các chuỗi nhỏ khác.

---

### 5. `dim_product` (11 rows)

| Cột | Kiểu | Mô tả |
|---|---|---|
| `product_id` | INT PK | ID |
| `sku_code` | VARCHAR(16) UK | Mã SKU |
| `product_name` | VARCHAR(80) | Tên sản phẩm |
| `brand` | ENUM | 'La Vie' / 'Viva' |
| `volume_liters` | DECIMAL(6,3) | Dung tích mỗi đơn vị (lít) |
| `pack_size` | SMALLINT | Số đơn vị/thùng |
| `product_group` | VARCHAR(30) | 'Chai nhỏ' / 'Chai vừa' / 'Chai lớn' / 'Cao cấp' / 'Trẻ em' / 'Bình lớn' |
| `is_returnable_container` | BOOLEAN | Có vỏ hoàn trả | TRUE với LV-19000, VV-19000 |
| `base_price_vnd` | INT | Giá bán cho kênh, chưa VAT (đ/đơn vị) |
| `contribution_margin_pct` | DECIMAL(5,2) | Biên đóng góp chuẩn (%) |
| `shelf_life_months` | TINYINT | Hạn sử dụng (tháng) | Chai PET 12, bình 19L 3 |
| `launch_date` | DATE | Ngày ra mắt |

| SKU | Tên | Lít | Giá (đ) | %DT FY2025 | CM% | HSD |
|---|---|---|---|---|---|---|
| LV-350 | La Vie chai 350ml | 0,35 | 3.900 | 9,0% | 37,5% | 12t |
| LV-500 | La Vie chai 500ml | 0,50 | 4.600 | **24,0%** | 35,8% | 12t |
| LV-750 | La Vie Sport chai 750ml | 0,75 | 6.300 | 1,5% | 34,0% | 12t |
| LV-1500 | La Vie chai 1,5L | 1,50 | 8.900 | 13,0% | 28,6% | 12t |
| LV-6000 | La Vie chai 6L | 6,00 | 26.500 | 7,0% | 23,4% | 12t |
| LV-PRE400 | La Vie Premium 400ml | 0,40 | 8.200 | 3,0% | **41,2%** 🟢 | 12t |
| LV-KID330 | La Vie Kid 330ml | 0,33 | 5.400 | 2,5% | 38,4% | 12t |
| LV-5000 | La Vie bình 5L | 5,00 | 22.000 | 0,8% | 24,8% | 12t |
| VV-5000 | Viva bình 5L | 5,00 | 19.500 | 1,2% | 22,6% | 12t |
| **LV-19000** | **La Vie bình 19L (bình úp)** | 19,00 | 58.000 | **29,0%** | **19,2%** 🔴 | 3t |
| **VV-19000** | **Viva bình 19L (bình vòi)** | 19,00 | 52.000 | **9,0%** | **17,4%** 🔴 | 3t |

⚠️ **Hai SKU 19L = 38,0% doanh thu nhưng có biên đóng góp thấp nhất.** Bất kỳ vùng nào có tỷ trọng 19L tăng đều đang bị pha loãng biên lợi nhuận. Đây là nửa đầu của Anomaly A.

---

### 6. `dim_plant` (2 rows)

| Cột | Kiểu | Mô tả |
|---|---|---|
| `plant_id` | INT PK | ID |
| `plant_code` | VARCHAR(4) UK | 'LA' / 'HY' |
| `plant_name` | VARCHAR(60) | Tên nhà máy |
| `province_code` | VARCHAR(10) FK | Tỉnh |
| `annual_capacity_liters` | BIGINT | Công suất năm (lít) |
| `monthly_capacity_liters` | BIGINT | Công suất tháng (lít) |
| `water_source_desc_vi` | VARCHAR(200) | Mô tả nguồn nước |
| `commissioned_year` | SMALLINT | Năm vận hành |

| Mã | Tên | Tỉnh | Công suất/năm | Công suất/tháng | Utilization T6/2026 |
|---|---|---|---|---|---|
| LA | Nhà máy Long An | Long An | 630 triệu lít | 52,5 triệu lít | **91,4%** 🟡 |
| HY | Nhà máy Hưng Yên | Hưng Yên | 420 triệu lít | 35,0 triệu lít | **84,7%** 🟢 |

---

### 7. `dim_production_line` (9 rows)

| Cột | Kiểu | Mô tả |
|---|---|---|
| `line_id` | INT PK | ID |
| `line_code` | VARCHAR(8) UK | 'LA-L1' … 'HY-L4' |
| `plant_id` | INT FK | → `dim_plant` |
| `line_type_vi` | VARCHAR(40) | Loại dây chuyền |
| `primary_sku_codes` | VARCHAR(120) | SKU chạy chính, phân cách dấu phẩy |
| `machine_hour_share_pct` | DECIMAL(5,2) | % giờ máy trong nhà máy |
| `daily_capacity_liters` | INT | Công suất ngày (lít) |
| `installed_year` | SMALLINT | Năm lắp đặt |

| Mã | Nhà máy | Loại | SKU chính | %giờ máy | CS/ngày (lít) |
|---|---|---|---|---|---|
| LA-L1 | LA | PET chai nhỏ | LV-350, LV-KID330 | 14% | 320.000 |
| **LA-L2** | LA | **PET chai nhỏ** | **LV-500** | **47%** ⚠️ | 780.000 |
| LA-L3 | LA | PET chai vừa/lớn | LV-1500, LV-6000, LV-5000 | 18% | 410.000 |
| LA-L4 | LA | Bình 19L | LV-19000 | 16% | 520.000 |
| LA-L5 | LA | Cao cấp | LV-PRE400, LV-750 | 5% | 120.000 |
| HY-L1 | HY | PET chai nhỏ | LV-500, LV-350 | 38% | 540.000 |
| HY-L2 | HY | PET chai vừa | LV-1500, LV-6000 | 21% | 330.000 |
| HY-L3 | HY | Bình 19L | LV-19000 | 27% | 410.000 |
| HY-L4 | HY | Viva | VV-19000, VV-5000 | 14% | 260.000 |

⚠️ **LA-L2 là bottleneck** — một dây chuyền gánh 47% giờ máy Long An và chạy SKU chiếm 24% doanh thu toàn công ty.

---

### 8. `dim_warehouse` (6 rows)

| Cột | Kiểu | Mô tả |
|---|---|---|
| `warehouse_id` | INT PK | ID |
| `warehouse_code` | VARCHAR(12) UK | Mã kho |
| `warehouse_name` | VARCHAR(60) | Tên kho |
| `province_code` | VARCHAR(10) FK | Tỉnh |
| `warehouse_type` | ENUM | 'Kho nhà máy' / 'Trung tâm phân phối' |
| `supplied_by_plant_code` | VARCHAR(4) FK | Nhà máy cấp hàng → `dim_plant` |
| `storage_capacity_liters` | BIGINT | Sức chứa (lít) |

| Mã | Tên | Tỉnh | Loại | Nguồn cấp |
|---|---|---|---|---|
| WH-LA | Kho thành phẩm Long An | Long An | Kho nhà máy | LA |
| WH-HY | Kho thành phẩm Hưng Yên | Hưng Yên | Kho nhà máy | HY |
| DC-HCM | DC Hồ Chí Minh | TP.HCM | Trung tâm phân phối | LA |
| DC-CT | DC Cần Thơ | Cần Thơ | Trung tâm phân phối | LA |
| **DC-DN** | **DC Đà Nẵng** | Đà Nẵng | Trung tâm phân phối | **LA** ⚠️ |
| DC-HN | DC Hà Nội | Hà Nội | Trung tâm phân phối | HY |

⚠️ **DC Đà Nẵng lấy hàng từ nhà máy Long An (cách ~850 km), không phải Hưng Yên.** Toàn bộ miền Trung — kể cả ba tỉnh Bắc Trung Bộ vốn gần Hưng Yên hơn — đều đi qua DC-DN. Đây là gốc rễ cấu trúc của Anomaly A.

---

### 9. `dim_route` (96 rows) — **BẢNG TRỌNG TÂM CHO ANOMALY A**

| Cột | Kiểu | Mô tả |
|---|---|---|
| `route_id` | INT PK | ID |
| `route_code` | VARCHAR(20) UK | Mã tuyến |
| `source_warehouse_code` | VARCHAR(12) FK | Kho nguồn → `dim_warehouse` |
| `destination_province_code` | VARCHAR(10) FK | Tỉnh đích → `dim_geography` |
| `route_cluster_vi` | VARCHAR(60) | Cụm tuyến |
| `distance_km` | INT | Khoảng cách (km) |
| `base_logistics_cost_per_liter` | DECIMAL(8,2) | Chi phí logistics gốc (đ/lít) |
| `requires_transshipment` | BOOLEAN | Có trung chuyển không |
| `transshipment_via_warehouse` | VARCHAR(12) | Trung chuyển qua kho nào |

**Bảng cụm tuyến và chi phí phục vụ:**

| Cụm tuyến | Kho nguồn | Khoảng cách | đ/lít | Trung chuyển |
|---|---|---|---|---|
| Nội vùng ĐBSH | DC-HN ← HY | 25–110 km | **470** | Không |
| Nội vùng Đông Nam Bộ | DC-HCM ← LA | 45–90 km | **490** | Không |
| Đồng bằng sông Cửu Long | DC-CT ← LA | 130–290 km | 640 | Không |
| **Thanh Hóa – Nghệ An** | **DC-HN ← HY** | 160–300 km | **760** 🟢 | Không |
| Nam Trung Bộ | DC-DN ← LA | 430–780 km | 870 | Qua DC-DN |
| Trung du & miền núi Bắc | DC-HN ← HY | 120–560 km | 910 | Không |
| Tây Nguyên | DC-HCM ← LA | 310–560 km | 980 | Không |
| Trung Trung Bộ | DC-DN ← LA | 850 km | 1.050 | Qua DC-DN |
| **Bắc Trung Bộ** | **DC-DN ← LA** | **930–1.250 km** | **1.180** 🔴 | Qua DC-DN |

⚠️⚠️ **LỖI CẤU TRÚC CẦN PHÁT HIỆN:**

| Tỉnh | Vùng | Kho nguồn | KC từ Hưng Yên | KC từ Long An | đ/lít | CM% H1/2026 |
|---|---|---|---|---|---|---|
| **Nghệ An** | Miền Bắc | DC-HN ← HY | ~300 km | ~1.150 km | **760** | **+17,2%** 🟢 |
| **Hà Tĩnh** | Miền Trung | DC-DN ← LA | ~350 km | ~1.250 km | **1.180** | **−3,4%** 🔴 |

Hai tỉnh liền kề. Hà Tĩnh gần Hưng Yên hơn Nghệ An... không, gần tương đương — nhưng lại đang được cấp hàng từ **Long An qua DC Đà Nẵng**, tức đi ngược 1.250 km rồi vòng lên. Nguyên nhân: ranh giới phân vùng bán hàng vẽ theo địa lý hành chính "Bắc Trung Bộ thuộc miền Trung", không theo logistics. Kết quả: chênh **55% chi phí phục vụ** giữa hai tỉnh sát vách.

---

## FACT TABLES

### 10. `fact_sales_out` ⭐ (FACT CHÍNH — ~82.000 rows)
Doanh thu bán ra từ La Vie tới khách hàng kênh. **Grain: tháng × khách hàng × SKU.**

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `sales_id` | BIGINT PK | ID | |
| `fiscal_period` | VARCHAR(7) | Kỳ báo cáo 'YYYY-MM' | |
| `period_end_date` | DATE FK | Ngày cuối kỳ → `dim_calendar` | |
| `customer_id` | INT FK | → `dim_customer` | |
| `product_id` | INT FK | → `dim_product` | |
| `channel_id` | INT FK | → `dim_channel` (denormalized) | |
| `province_code` | VARCHAR(10) | Tỉnh (denormalized) | |
| `region_code` | VARCHAR(6) | Vùng (denormalized) | |
| `quantity_units` | INT | Số đơn vị bán | chai/bình |
| `volume_liters` | DECIMAL(14,2) | Thể tích | lít |
| `gross_revenue_vnd` | BIGINT | Doanh thu gộp | VND |
| `trade_discount_vnd` | BIGINT | Chiết khấu thương mại trừ trên hóa đơn | VND |
| `net_revenue_vnd` | BIGINT | **Doanh thu thuần** | VND |
| `cogs_vnd` | BIGINT | Giá vốn hàng bán | VND |
| `logistics_cost_vnd` | BIGINT | Chi phí logistics phân bổ | VND |
| `contribution_margin_vnd` | BIGINT | Biên đóng góp | VND |
| `route_id` | INT FK | Tuyến giao hàng → `dim_route` | |

⚠️ **Luôn dùng `net_revenue_vnd` cho mọi câu hỏi về "doanh thu".** `gross_revenue_vnd` chỉ dùng khi cần tách riêng phần chiết khấu.

⚠️ **`contribution_margin_vnd = net_revenue_vnd − cogs_vnd − logistics_cost_vnd`.** Chi phí logistics ĐÃ được trừ. Không trừ lại lần nữa từ `fact_cost_to_serve`.

⚠️ **Grain là THÁNG, không phải ngày.** Không trả lời được câu hỏi doanh thu theo ngày.

---

### 11. `fact_cost_to_serve` (2.304 rows)
Chi phí phục vụ theo tuyến. **Grain: tháng × tuyến.** Dùng để **giải thích** biên đóng góp, không để tính lại nó.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `cts_id` | INT PK | ID | |
| `fiscal_period` | VARCHAR(7) | Kỳ | |
| `route_id` | INT FK | → `dim_route` | |
| `total_volume_liters` | DECIMAL(14,2) | Sản lượng giao trên tuyến | lít |
| `logistics_cost_per_liter` | DECIMAL(8,2) | Chi phí vận chuyển | đ/lít |
| `transshipment_cost_per_liter` | DECIMAL(8,2) | Phụ phí trung chuyển | đ/lít, = 85 với Bắc Trung Bộ, 0 với tuyến trực tiếp |
| `total_logistics_cost_vnd` | BIGINT | Tổng chi phí | VND |
| `delivery_trips` | INT | Số chuyến giao | chuyến |
| `avg_drop_size_liters` | DECIMAL(10,2) | Quy mô giao trung bình mỗi điểm | lít |

⚠️ Chi phí phục vụ trượt **+0,6%/tháng** theo giá nhiên liệu và nhân công. Khi so sánh giữa hai kỳ xa nhau, tính tới yếu tố này.

⚠️ **`avg_drop_size_liters` là đòn bẩy hành động quan trọng** — tăng drop size là cách giảm chi phí/lít mà không cần đổi tuyến.

---

### 12. `fact_container_cycle` (5.232 rows) — **BẢNG ĐẶC THÙ NGÀNH NƯỚC**
Vòng đời vỏ bình 19L. **Grain: tháng × khách hàng có kinh doanh 19L (218 khách hàng).**

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `cycle_id` | INT PK | ID | |
| `fiscal_period` | VARCHAR(7) | Kỳ | |
| `customer_id` | INT FK | → `dim_customer` | |
| `containers_issued` | INT | Vỏ xuất đi trong kỳ | vỏ |
| `containers_returned` | INT | Vỏ thu về trong kỳ | vỏ |
| `containers_lost` | INT | Vỏ mất = issued − returned | vỏ |
| `return_rate_pct` | DECIMAL(6,3) | Tỷ lệ thu hồi | % (0–100) |
| `containers_at_customer_eop` | INT | Tồn vỏ tại khách cuối kỳ | vỏ |
| `container_turns_annualized` | DECIMAL(5,2) | Vòng quay vỏ quy năm | lượt/năm |
| `asset_loss_vnd` | BIGINT | Hao hụt tài sản = lost × 77.000 | VND |
| `deposit_outstanding_vnd` | BIGINT | Tiền cọc treo lũy kế = lũy kế lost × 50.000 | VND |

⚠️ **Thất thoát vỏ có HAI lớp tiền — luôn báo cáo cả hai:** hao hụt tài sản (`asset_loss_vnd`, ghi nhận theo kỳ) và tiền cọc kẹt trong công nợ (`deposit_outstanding_vnd`, **lũy kế** — không SUM qua các kỳ, lấy giá trị kỳ cuối).

⚠️ **`deposit_outstanding_vnd` là cột LŨY KẾ.** SUM qua nhiều kỳ sẽ ra số sai gấp nhiều lần. Dùng `MAX()` hoặc lọc `fiscal_period = '2026-06'`.

**Chuẩn tham chiếu:** tỷ lệ thu hồi ≥93%, vòng quay ≥5,5 lượt/năm. Giá thành vỏ PC 19L: **77.000 đ/vỏ**. Tiền cọc khách: **50.000 đ/vỏ**. Tổng vỏ trong hệ thống ~1,42 triệu.

---

### 13. `fact_trade_spend` (9.720 rows)
Chi phí thương mại ngoài hóa đơn. **Grain: tháng × khách hàng × loại chi.** Chỉ có với 135 khách hàng thuộc MT, GT lớn, HORECA và E-commerce.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `spend_id` | INT PK | ID | |
| `fiscal_period` | VARCHAR(7) | Kỳ | |
| `customer_id` | INT FK | → `dim_customer` | |
| `channel_id` | INT FK | → `dim_channel` | |
| `spend_type` | ENUM | 'Chiết khấu thương mại' / 'Phí trưng bày & niêm yết' / 'Khuyến mãi & hỗ trợ bán hàng' | |
| `spend_amount_vnd` | BIGINT | Số tiền | VND |
| `store_count` | INT | Số điểm bán | điểm — **chỉ có với kênh MT, NULL với kênh khác** |
| `campaign_name_vi` | VARCHAR(120) | Tên chương trình | |

⚠️⚠️ **KHÔNG JOIN trực tiếp `fact_trade_spend` với `fact_sales_out`.** Hai bảng khác grain (SKU vs khách hàng × loại chi) → JOIN trực tiếp sẽ nhân bội số dòng. **Phải aggregate cả hai về `(fiscal_period, customer_id)` trước.**

⚠️ **`store_count` lặp lại ở cả 3 dòng `spend_type` của cùng một khách hàng trong cùng kỳ.** Dùng `MAX(store_count)` hoặc `AVG()`, **không SUM**.

---

### 14. `fact_production` (6.570 rows)
Sản lượng sản xuất. **Grain: ngày × dây chuyền.** Đây là bảng duy nhất có grain ngày.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `production_id` | INT PK | ID | |
| `production_date` | DATE FK | → `dim_calendar` | |
| `line_id` | INT FK | → `dim_production_line` | |
| `plant_id` | INT FK | → `dim_plant` | |
| `planned_output_liters` | INT | Sản lượng kế hoạch | lít |
| `actual_output_liters` | INT | Sản lượng thực tế | lít |
| `downtime_minutes` | INT | Thời gian dừng máy | phút |
| `downtime_reason_vi` | VARCHAR(80) | Lý do dừng | 'Thay khuôn / Đổi SKU', 'Bảo trì định kỳ', 'Sự cố cơ khí', 'Chờ nguyên vật liệu', 'Vệ sinh CIP', 'Sự cố điện' |
| `capacity_liters` | INT | Công suất ngày | lít |
| `utilization_pct` | DECIMAL(6,3) | Tỷ lệ khai thác | % (0–100) |
| `overtime_hours` | DECIMAL(5,2) | Giờ tăng ca | giờ |

⚠️ **`utilization_pct` phải được tính theo trọng số sản lượng, không phải trung bình cộng.** Dùng `SUM(actual_output_liters) / SUM(capacity_liters)`, không dùng `AVG(utilization_pct)`.

---

### 15. `fact_inventory` (~5.600 rows) — ⚠️ **BẢNG SNAPSHOT**
Tồn kho thành phẩm. **Grain: tuần (thứ Sáu) × kho × SKU.**

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `inventory_id` | INT PK | ID | |
| `snapshot_date` | DATE FK | Ngày chốt (thứ Sáu) → `dim_calendar` | |
| `warehouse_id` | INT FK | → `dim_warehouse` | |
| `product_id` | INT FK | → `dim_product` | |
| `closing_stock_liters` | DECIMAL(14,2) | Tồn cuối kỳ | lít |
| `days_of_cover` | DECIMAL(6,2) | Số ngày tồn đủ bán | ngày |
| `stock_value_vnd` | BIGINT | Giá trị tồn | VND |
| `nearest_expiry_date` | DATE | Hạn dùng gần nhất trong lô tồn | |

⚠️⚠️ **ĐÂY LÀ BẢNG SNAPSHOT — TUYỆT ĐỐI KHÔNG SUM NHIỀU SNAPSHOT.** Luôn dùng `WHERE snapshot_date = 'ngày cụ thể'` hoặc lấy snapshot mới nhất. SUM 104 tuần sẽ ra tồn kho gấp hơn 100 lần thực tế.

⚠️ Bình 19L có hạn dùng chỉ **3 tháng** — tồn kho cao ở SKU này rủi ro hơn nhiều so với chai PET (12 tháng).

---

### 16. `fact_pnl_monthly` (360 rows)
P&L tổng hợp. **Grain: tháng × kênh × vùng.** Được tính từ `fact_sales_out` + `fact_trade_spend`, không sinh độc lập.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `pnl_id` | INT PK | ID | |
| `fiscal_period` | VARCHAR(7) | Kỳ | |
| `channel_id` | INT FK | → `dim_channel` | |
| `region_code` | VARCHAR(6) | Vùng | |
| `gross_revenue_vnd` | BIGINT | Doanh thu gộp | VND |
| `trade_discount_vnd` | BIGINT | Chiết khấu trên hóa đơn | VND |
| `net_revenue_vnd` | BIGINT | Doanh thu thuần | VND |
| `cogs_vnd` | BIGINT | Giá vốn | VND |
| `gross_profit_vnd` | BIGINT | Lợi nhuận gộp | VND |
| `gross_margin_pct` | DECIMAL(6,3) | Biên gộp | % |
| `logistics_cost_vnd` | BIGINT | Chi phí logistics | VND |
| `trade_spend_vnd` | BIGINT | Trade spend ngoài hóa đơn | VND |
| `contribution_margin_vnd` | BIGINT | Biên đóng góp | VND |
| `contribution_margin_pct` | DECIMAL(6,3) | Biên đóng góp % | % |
| `allocated_opex_vnd` | BIGINT | Chi phí hoạt động phân bổ | VND |
| `ebit_vnd` | BIGINT | EBIT | VND |
| `ebit_margin_pct` | DECIMAL(6,3) | Biên EBIT | % |

⚠️ **Đây là bảng chuẩn cho mọi câu hỏi về EBIT và net margin theo kênh.** Tổng `net_revenue_vnd` ở đây khớp `fact_sales_out` trong sai số 0,5%.

---

### 17–20. Metadata tables

| Bảng | Nội dung |
|---|---|
| `_meta_tables` | `table_name`, `description_vi`, `description_en`, `business_context`, `row_count` |
| `_meta_columns` | `table_name`, `column_name`, `data_type`, `description_vi`, `description_en`, `unit`, `example_values` |
| `_meta_kpi` | `kpi_name`, `formula_sql`, `description_vi`, `related_questions` |
| `_meta_glossary` | `term_vi`, `term_en`, `definition` — GT, MT, HOD, HORECA, cost-to-serve, contribution margin, trade spend, cọc vỏ, vòng quay vỏ, drop size, days of cover, sell-out, yield |

Có thể query trực tiếp các bảng này khi cần biết ý nghĩa một cột hoặc thuật ngữ.

---

## SQL TEMPLATES

### T1 — Doanh thu và tăng trưởng theo tháng (24 điểm)

```sql
SELECT
    f.fiscal_period,
    ROUND(SUM(f.net_revenue_vnd) / 1e9, 1)            AS doanh_thu_ty,
    ROUND(SUM(f.volume_liters) / 1e6, 2)              AS san_luong_trieu_lit,
    ROUND(SUM(f.net_revenue_vnd) / SUM(f.volume_liters), 0) AS yield_dong_tren_lit,
    ROUND(100.0 * SUM(f.contribution_margin_vnd) / SUM(f.net_revenue_vnd), 1) AS cm_pct
FROM `fact_sales_out` f
GROUP BY f.fiscal_period
ORDER BY f.fiscal_period;
-- Kỳ vọng: đỉnh 2026-06 (~291 tỷ), đáy 2025-11 (~167 tỷ), yield ~3.564 đ/lít
```

### T2 — So sánh H1/2026 vs H1/2025 theo KÊNH (revenue bridge)

```sql
SELECT
    c.channel_name_vi,
    ROUND(SUM(CASE WHEN f.fiscal_period BETWEEN '2025-01' AND '2025-06'
                   THEN f.net_revenue_vnd END) / 1e9, 1) AS h1_2025_ty,
    ROUND(SUM(CASE WHEN f.fiscal_period BETWEEN '2026-01' AND '2026-06'
                   THEN f.net_revenue_vnd END) / 1e9, 1) AS h1_2026_ty,
    ROUND(100.0 * (
        SUM(CASE WHEN f.fiscal_period BETWEEN '2026-01' AND '2026-06' THEN f.net_revenue_vnd END)
      / NULLIF(SUM(CASE WHEN f.fiscal_period BETWEEN '2025-01' AND '2025-06' THEN f.net_revenue_vnd END), 0)
      - 1), 1) AS yoy_pct
FROM `fact_sales_out` f
JOIN `dim_channel` c ON c.channel_id = f.channel_id
WHERE f.fiscal_period BETWEEN '2025-01' AND '2026-06'
GROUP BY c.channel_name_vi
ORDER BY h1_2026_ty DESC;
-- Kỳ vọng: GT +2,1% (dưới lạm phát ~3,5% → suy giảm thực) | HOD +13,2% | MT +19,0% | ECM +34,1%
```

### T3 — Biên đóng góp theo VÙNG, hai kỳ (phát hiện Anomaly A)

```sql
SELECT
    g.region_name,
    ROUND(SUM(CASE WHEN f.fiscal_period BETWEEN '2025-01' AND '2025-06'
                   THEN f.net_revenue_vnd END) / 1e9, 1) AS dt_h1_2025_ty,
    ROUND(SUM(CASE WHEN f.fiscal_period BETWEEN '2026-01' AND '2026-06'
                   THEN f.net_revenue_vnd END) / 1e9, 1) AS dt_h1_2026_ty,
    ROUND(100.0 * SUM(CASE WHEN f.fiscal_period BETWEEN '2025-01' AND '2025-06'
                           THEN f.contribution_margin_vnd END)
                / NULLIF(SUM(CASE WHEN f.fiscal_period BETWEEN '2025-01' AND '2025-06'
                                  THEN f.net_revenue_vnd END), 0), 1) AS cm_h1_2025_pct,
    ROUND(100.0 * SUM(CASE WHEN f.fiscal_period BETWEEN '2026-01' AND '2026-06'
                           THEN f.contribution_margin_vnd END)
                / NULLIF(SUM(CASE WHEN f.fiscal_period BETWEEN '2026-01' AND '2026-06'
                                  THEN f.net_revenue_vnd END), 0), 1) AS cm_h1_2026_pct
FROM `fact_sales_out` f
JOIN `dim_geography` g
      ON g.province_code = f.province_code AND g.geo_level = 'Tỉnh'
WHERE f.fiscal_period BETWEEN '2025-01' AND '2026-06'
GROUP BY g.region_name
ORDER BY dt_h1_2026_ty DESC;
-- Kỳ vọng: Miền Trung doanh thu +18,4% nhưng CM rơi 21,4% → 13,2%
```

### T4 — Drill xuống TỈNH kèm chi phí phục vụ và kho nguồn (root cause Anomaly A)

```sql
SELECT
    g.region_name,
    g.province_name,
    ROUND(SUM(f.net_revenue_vnd) / 1e9, 1)  AS doanh_thu_ty,
    ROUND(100.0 * SUM(f.contribution_margin_vnd)
                / NULLIF(SUM(f.net_revenue_vnd), 0), 1) AS cm_pct,
    ROUND(SUM(f.logistics_cost_vnd) / NULLIF(SUM(f.volume_liters), 0), 0) AS chi_phi_phuc_vu_dong_lit,
    MAX(r.source_warehouse_code)             AS kho_nguon,
    MAX(w.supplied_by_plant_code)            AS nha_may,
    MAX(r.route_cluster_vi)                  AS cum_tuyen,
    MAX(r.distance_km)                       AS khoang_cach_km
FROM `fact_sales_out` f
JOIN `dim_geography` g ON g.province_code = f.province_code AND g.geo_level = 'Tỉnh'
JOIN `dim_route`     r ON r.route_id = f.route_id
JOIN `dim_warehouse` w ON w.warehouse_code = r.source_warehouse_code
WHERE f.fiscal_period BETWEEN '2026-01' AND '2026-06'
  AND g.province_name IN ('Nghệ An','Hà Tĩnh','Quảng Trị','Huế','Đà Nẵng','Thanh Hóa')
GROUP BY g.region_name, g.province_name
ORDER BY cm_pct ASC;
-- Kỳ vọng: Hà Tĩnh −3,4% / 1.180 đ/lít / DC-DN ← LA
--          Nghệ An +17,2% / 760 đ/lít / DC-HN ← HY   → hai tỉnh liền kề, chênh 55% chi phí
```

### T5 — Dịch chuyển SKU mix theo vùng (nửa còn lại của Anomaly A)

```sql
SELECT
    f.fiscal_period,
    ROUND(100.0 * SUM(CASE WHEN p.is_returnable_container THEN f.net_revenue_vnd ELSE 0 END)
                / NULLIF(SUM(f.net_revenue_vnd), 0), 1) AS ty_trong_19l_pct,
    ROUND(100.0 * SUM(f.contribution_margin_vnd)
                / NULLIF(SUM(f.net_revenue_vnd), 0), 1) AS cm_pct
FROM `fact_sales_out` f
JOIN `dim_product`   p ON p.product_id = f.product_id
JOIN `dim_geography` g ON g.province_code = f.province_code AND g.geo_level = 'Tỉnh'
WHERE g.region_code = 'TRUNG'
  AND f.fiscal_period BETWEEN '2025-01' AND '2026-06'
GROUP BY f.fiscal_period
ORDER BY f.fiscal_period;
-- Kỳ vọng: tỷ trọng 19L tăng đều 31,0% → 46,0%, CM giảm đối xứng 21,4% → 13,2%
```

### T6 — Tỷ lệ thu hồi vỏ theo QUÝ (phát hiện Anomaly B)

```sql
SELECT
    CONCAT(LEFT(cc.fiscal_period, 4), '-Q',
           QUARTER(STR_TO_DATE(CONCAT(cc.fiscal_period, '-01'), '%Y-%m-%d'))) AS quy,
    SUM(cc.containers_issued)   AS vo_xuat,
    SUM(cc.containers_returned) AS vo_thu_ve,
    SUM(cc.containers_lost)     AS vo_mat,
    ROUND(100.0 * SUM(cc.containers_returned)
                / NULLIF(SUM(cc.containers_issued), 0), 1) AS ty_le_thu_hoi_pct,
    ROUND(SUM(cc.asset_loss_vnd) / 1e9, 2) AS hao_hut_tai_san_ty
FROM `fact_container_cycle` cc
WHERE cc.fiscal_period BETWEEN '2025-01' AND '2026-06'
GROUP BY quy
ORDER BY quy;
-- Kỳ vọng: 94,2 / 92,8 / 91,5 / 89,9 / 88,4 / 86,8 → giảm đều 6 quý liên tiếp
```

### T7 — Truy nguồn rò rỉ vỏ theo nhóm ONBOARD (root cause Anomaly B)

```sql
SELECT
    CASE
      WHEN c.onboard_date >= '2025-01-01' THEN 'Onboard sau 2025-01'
      WHEN c.onboard_date >= '2024-01-01' THEN 'Onboard năm 2024'
      ELSE 'Onboard trước 2024'
    END                                      AS nhom_dai_ly,
    c.contract_type,
    COUNT(DISTINCT c.customer_id)            AS so_dai_ly,
    ROUND(100.0 * SUM(cc.containers_returned)
                / NULLIF(SUM(cc.containers_issued), 0), 1) AS ty_le_thu_hoi_pct,
    SUM(cc.containers_lost)                  AS vo_mat,
    ROUND(SUM(cc.asset_loss_vnd) / 1e9, 2)   AS hao_hut_ty,
    ROUND(MAX(cc.deposit_outstanding_vnd) / 1e9, 2) AS coc_treo_ty
FROM `fact_container_cycle` cc
JOIN `dim_customer` c ON c.customer_id = cc.customer_id
JOIN `dim_channel`  ch ON ch.channel_id = c.channel_id
WHERE ch.channel_code = 'HOD'
  AND cc.fiscal_period BETWEEN '2026-01' AND '2026-06'
GROUP BY nhom_dai_ly, c.contract_type
ORDER BY ty_le_thu_hoi_pct ASC;
-- Kỳ vọng: MOI_2025 (14 đại lý) 78,3% | 2024 (28) 90,4% | trước 2024 (78) 93,1%
-- ⚠️ deposit_outstanding_vnd là cột LŨY KẾ → dùng MAX, không SUM
```

### T8 — Gross margin vs NET margin theo kênh (Anomaly C)

```sql
SELECT
    c.channel_name_vi,
    ROUND(SUM(p.net_revenue_vnd) / 1e9, 1)   AS doanh_thu_ty,
    ROUND(100.0 * SUM(p.gross_profit_vnd)
                / NULLIF(SUM(p.net_revenue_vnd), 0), 1) AS gross_margin_pct,
    ROUND(100.0 * SUM(p.trade_spend_vnd)
                / NULLIF(SUM(p.net_revenue_vnd), 0), 1) AS trade_spend_tren_dt_pct,
    ROUND(100.0 * (SUM(p.gross_profit_vnd) - SUM(p.trade_spend_vnd))
                / NULLIF(SUM(p.net_revenue_vnd), 0), 1) AS net_margin_pct
FROM `fact_pnl_monthly` p
JOIN `dim_channel` c ON c.channel_id = p.channel_id
WHERE p.fiscal_period BETWEEN '2026-01' AND '2026-06'
GROUP BY c.channel_name_vi
ORDER BY net_margin_pct DESC;
-- Kỳ vọng: HOD 15,1% > ECM 13,8% > HRC 13,4% > GT 12,4% >> MT 6,2%
--          MT có gross margin CAO NHẤT (33,0%) nhưng net margin THẤP NHẤT
```

### T9 — Bóc khách hàng MT: doanh thu, trade spend và doanh thu/điểm bán

```sql
WITH sales AS (
    SELECT f.customer_id, f.fiscal_period, SUM(f.net_revenue_vnd) AS rev,
           SUM(f.contribution_margin_vnd) AS cm
    FROM `fact_sales_out` f
    WHERE f.fiscal_period BETWEEN '2026-01' AND '2026-06'
    GROUP BY f.customer_id, f.fiscal_period
),
spend AS (
    SELECT t.customer_id, t.fiscal_period,
           SUM(t.spend_amount_vnd) AS spend,
           MAX(t.store_count)      AS stores    -- ⚠️ MAX chứ không SUM
    FROM `fact_trade_spend` t
    WHERE t.fiscal_period BETWEEN '2026-01' AND '2026-06'
    GROUP BY t.customer_id, t.fiscal_period
)
SELECT
    c.customer_name,
    ROUND(SUM(s.rev) / 1e9, 1)                      AS doanh_thu_ty,
    ROUND(SUM(sp.spend) / 1e9, 1)                   AS trade_spend_ty,
    ROUND(100.0 * SUM(sp.spend) / NULLIF(SUM(s.rev), 0), 1) AS spend_tren_dt_pct,
    ROUND(100.0 * (SUM(s.cm) - SUM(sp.spend))
                / NULLIF(SUM(s.rev), 0), 1)         AS net_margin_pct,
    MAX(sp.stores)                                  AS so_diem_ban,
    ROUND(SUM(s.rev) / NULLIF(MAX(sp.stores), 0) / 1e6, 1) AS dt_tren_diem_ban_trieu
FROM sales s
JOIN spend sp ON sp.customer_id = s.customer_id AND sp.fiscal_period = s.fiscal_period
JOIN `dim_customer` c  ON c.customer_id = s.customer_id
JOIN `dim_channel`  ch ON ch.channel_id = c.channel_id
WHERE ch.channel_code = 'MT'
GROUP BY c.customer_name
ORDER BY net_margin_pct ASC;
-- Kỳ vọng: Circle K −1,8% | GS25 −0,6% | các chuỗi còn lại dương 7–11%
-- ⚠️ ĐÂY LÀ CÁCH ĐÚNG để ghép fact_trade_spend với fact_sales_out: agg cả hai về
--    (fiscal_period, customer_id) TRƯỚC khi JOIN
```

### T10 — Khai thác công suất theo nhà máy và dây chuyền

```sql
SELECT
    pl.plant_name,
    l.line_code,
    l.line_type_vi,
    ROUND(SUM(fp.actual_output_liters) / 1e6, 2)  AS san_luong_trieu_lit,
    ROUND(100.0 * SUM(fp.actual_output_liters)
                / NULLIF(SUM(fp.capacity_liters), 0), 1) AS utilization_pct,
    ROUND(SUM(fp.downtime_minutes) / 60.0, 0)     AS tong_gio_dung_may,
    ROUND(SUM(fp.overtime_hours), 0)              AS tong_gio_tang_ca
FROM `fact_production` fp
JOIN `dim_production_line` l  ON l.line_id  = fp.line_id
JOIN `dim_plant`           pl ON pl.plant_id = fp.plant_id
WHERE fp.production_date BETWEEN '2026-06-01' AND '2026-06-30'
GROUP BY pl.plant_name, l.line_code, l.line_type_vi
ORDER BY utilization_pct DESC;
-- Kỳ vọng: nhà máy Long An 91,4%, Hưng Yên 84,7%; LA-L2 cao nhất
-- ⚠️ Dùng SUM/SUM, KHÔNG dùng AVG(utilization_pct)
```

### T11 — Tồn kho và số ngày đủ bán (snapshot mới nhất)

```sql
SELECT
    w.warehouse_name,
    p.product_name,
    ROUND(i.closing_stock_liters / 1000, 1) AS ton_nghin_lit,
    i.days_of_cover                          AS ngay_du_ban,
    i.nearest_expiry_date                    AS han_dung_gan_nhat,
    DATEDIFF(i.nearest_expiry_date, i.snapshot_date) AS con_lai_ngay
FROM `fact_inventory` i
JOIN `dim_warehouse` w ON w.warehouse_id = i.warehouse_id
JOIN `dim_product`   p ON p.product_id   = i.product_id
WHERE i.snapshot_date = (SELECT MAX(snapshot_date) FROM `fact_inventory`)
ORDER BY i.days_of_cover ASC
LIMIT 30;
-- Kỳ vọng: days_of_cover trung bình ~8,4 ngày tại 2026-06
-- ⚠️ LUÔN lọc snapshot_date — KHÔNG BAO GIỜ SUM nhiều snapshot
```

### T12 — EBIT baseline 12 tháng gần nhất (nền cho goal-seek)

```sql
SELECT
    ROUND(SUM(p.net_revenue_vnd) / 1e9, 1)  AS doanh_thu_ty,
    ROUND(SUM(p.gross_profit_vnd) / 1e9, 1) AS loi_nhuan_gop_ty,
    ROUND(SUM(p.trade_spend_vnd) / 1e9, 1)  AS trade_spend_ty,
    ROUND(SUM(p.contribution_margin_vnd) / 1e9, 1) AS bien_dong_gop_ty,
    ROUND(SUM(p.allocated_opex_vnd) / 1e9, 1) AS opex_ty,
    ROUND(SUM(p.ebit_vnd) / 1e9, 1)         AS ebit_ty,
    ROUND(100.0 * SUM(p.ebit_vnd) / NULLIF(SUM(p.net_revenue_vnd), 0), 1) AS ebit_margin_pct
FROM `fact_pnl_monthly` p
WHERE p.fiscal_period BETWEEN '2025-07' AND '2026-06';
-- Kỳ vọng: doanh thu 2.621 tỷ | EBIT 372 tỷ | EBIT margin 14,2%
```

### T13 — Chi phí phục vụ theo cụm tuyến kèm drop size

```sql
SELECT
    r.route_cluster_vi,
    r.source_warehouse_code,
    COUNT(DISTINCT r.route_id)                    AS so_tuyen,
    ROUND(SUM(cts.total_volume_liters) / 1e6, 2)  AS san_luong_trieu_lit,
    ROUND(SUM(cts.total_logistics_cost_vnd)
        / NULLIF(SUM(cts.total_volume_liters), 0), 0) AS chi_phi_dong_tren_lit,
    ROUND(AVG(cts.avg_drop_size_liters), 0)       AS drop_size_lit,
    ROUND(SUM(cts.total_logistics_cost_vnd) / 1e9, 1) AS tong_chi_phi_ty
FROM `fact_cost_to_serve` cts
JOIN `dim_route` r ON r.route_id = cts.route_id
WHERE cts.fiscal_period BETWEEN '2026-01' AND '2026-06'
GROUP BY r.route_cluster_vi, r.source_warehouse_code
ORDER BY chi_phi_dong_tren_lit DESC;
-- Kỳ vọng: Bắc Trung Bộ ~1.180 đ/lít (cao nhất) vs Nội vùng ĐBSH ~470 (thấp nhất) = 2,5×
```

---

## JOIN WARNINGS

1. **`fact_trade_spend` ↔ `fact_sales_out` — KHÁC GRAIN, NGUY HIỂM NHẤT.**
   `fact_sales_out` ở mức SKU; `fact_trade_spend` ở mức khách hàng × loại chi. JOIN trực tiếp nhân bội số dòng (mỗi dòng bán hàng khớp với 3 dòng chi phí, và ngược lại). **Bắt buộc aggregate cả hai về `(fiscal_period, customer_id)` trước khi ghép** — xem T9 để biết cách làm đúng.

2. **`fact_inventory` = SNAPSHOT.**
   Dùng `WHERE snapshot_date = 'ngày cụ thể'` hoặc `= (SELECT MAX(snapshot_date) ...)`. **KHÔNG SUM nhiều snapshot** — 104 tuần cộng lại sẽ ra tồn kho gấp hơn 100 lần thực tế.

3. **`fact_container_cycle.deposit_outstanding_vnd` = CỘT LŨY KẾ.**
   Đây là số dư cọc treo tích lũy tới cuối kỳ, không phải phát sinh trong kỳ. Dùng `MAX()` hoặc lọc kỳ cuối. `asset_loss_vnd` thì ngược lại — là phát sinh trong kỳ, SUM được.

4. **`fact_trade_spend.store_count` lặp lại theo `spend_type`.**
   Mỗi khách hàng MT có 3 dòng/tháng (3 loại chi), cả 3 đều mang cùng `store_count`. Dùng `MAX()` hoặc `AVG()`, **không SUM** — nếu SUM sẽ ra số điểm bán gấp 3.

5. **`dim_geography` có hai cấp trong cùng bảng.**
   Luôn thêm `AND geo_level = 'Tỉnh'` khi JOIN theo `province_code`, nếu không sẽ dính cả dòng cấp Vùng và nhân đôi kết quả.

6. **`fact_production` — dùng SUM/SUM, không AVG.**
   `AVG(utilization_pct)` cho kết quả sai vì các dây chuyền có công suất rất khác nhau (LA-L2 780.000 lít/ngày vs LA-L5 120.000). Luôn dùng `SUM(actual_output_liters) / SUM(capacity_liters)`.

7. **`fact_cost_to_serve` ↔ `fact_sales_out` — chi phí đã được trừ rồi.**
   `contribution_margin_vnd` trong `fact_sales_out` ĐÃ trừ `logistics_cost_vnd`. Dùng `fact_cost_to_serve` để **giải thích** chi phí (đ/lít, drop size, số chuyến), **không để trừ lại lần nữa** — nếu trừ hai lần sẽ ra biên đóng góp âm giả.

8. **`fact_container_cycle` chỉ có 218/380 khách hàng.**
   Chỉ khách hàng có `handles_19l = TRUE` mới xuất hiện. LEFT JOIN từ `dim_customer` sẽ ra NULL cho 162 khách hàng còn lại — dùng `COALESCE` hoặc INNER JOIN tùy mục đích.

9. **`fact_pnl_monthly` ↔ `fact_sales_out` — không JOIN, chỉ đối chiếu.**
   Hai bảng có grain khác nhau và `fact_pnl_monthly` được tính TỪ `fact_sales_out`. JOIN chúng sẽ đếm trùng doanh thu. Dùng một trong hai cho mỗi phân tích, không dùng cả hai cùng lúc.

10. **`dim_route` — một tỉnh có thể có nhiều tuyến.**
    Khi JOIN `fact_sales_out.route_id`, mỗi dòng bán hàng chỉ gắn một tuyến → an toàn. Nhưng nếu JOIN `dim_route` với `dim_geography` theo `destination_province_code` mà không aggregate thì sẽ nhân bội (2–4 tuyến/tỉnh).

---

## ĐƠN VỊ TIỀN TỆ & ĐO LƯỜNG

| Bảng | Cột | Đơn vị |
|---|---|---|
| `fact_sales_out` | `gross_revenue_vnd`, `trade_discount_vnd`, `net_revenue_vnd`, `cogs_vnd`, `logistics_cost_vnd`, `contribution_margin_vnd` | VND |
| `fact_sales_out` | `volume_liters` | lít |
| `fact_sales_out` | `quantity_units` | chai / bình |
| `fact_cost_to_serve` | `logistics_cost_per_liter`, `transshipment_cost_per_liter` | **đồng/lít** |
| `fact_cost_to_serve` | `total_logistics_cost_vnd` | VND |
| `fact_cost_to_serve` | `avg_drop_size_liters` | lít |
| `fact_container_cycle` | `containers_issued/returned/lost`, `containers_at_customer_eop` | **vỏ** |
| `fact_container_cycle` | `asset_loss_vnd`, `deposit_outstanding_vnd` | VND |
| `fact_container_cycle` | `container_turns_annualized` | lượt/năm |
| `fact_trade_spend` | `spend_amount_vnd` | VND |
| `fact_trade_spend` | `store_count` | điểm bán |
| `fact_production` | `planned_output_liters`, `actual_output_liters`, `capacity_liters` | lít |
| `fact_production` | `downtime_minutes` | phút |
| `fact_production` | `overtime_hours` | giờ |
| `fact_inventory` | `closing_stock_liters` | lít |
| `fact_inventory` | `days_of_cover` | ngày |
| `fact_pnl_monthly` | mọi cột `*_vnd` | VND |
| `dim_product` | `base_price_vnd` | VND/đơn vị, chưa VAT |

**Format hiển thị cho lãnh đạo:**
- \> 1 tỷ: "X,X tỷ" (VD: "222,4 tỷ")
- < 1 tỷ: "XXX triệu" (VD: "845 triệu")
- Đồng/lít: ghi nguyên có dấu phân cách nghìn (VD: "1.180 đ/lít")
- Phần trăm: 1 chữ số thập phân (VD: "13,2%")
- Sản lượng: "X,X triệu lít" hoặc "XXX nghìn lít"

---

## MỐC SANITY CHECK

Nếu kết quả query lệch khỏi các mốc dưới đây, kiểm tra lại query trước khi báo cáo.

| Chỉ số | Giá trị kỳ vọng |
|---|---|
| Doanh thu FY2025 (2025-01 → 2025-12) | **2.500 tỷ** |
| Doanh thu 12T gần nhất (2025-07 → 2026-06) | **2.621 tỷ** |
| Doanh thu toàn bộ 24 tháng | **5.030 tỷ** |
| Doanh thu tháng đỉnh (2026-06) | **~291 tỷ** |
| Doanh thu tháng đáy (2025-11) | **~167 tỷ** |
| Tăng trưởng H1/2026 vs H1/2025 | **+9,3%** |
| Sản lượng 12T gần nhất | **~735 triệu lít** |
| Yield trung bình | **~3.564 đ/lít** |
| Biên đóng góp toàn công ty | **29–31%** |
| EBIT 12T gần nhất | **372 tỷ (14,2%)** |
| Tỷ trọng doanh thu SKU 19L | **38,0%** |
| Tỷ lệ thu hồi vỏ (2026-Q2) | **86,8%** |
| Utilization Long An (2026-06) | **91,4%** |
| Utilization Hưng Yên (2026-06) | **84,7%** |
| Days of cover trung bình (2026-06) | **8,4 ngày** |
| Tổng số dòng toàn database | **~113.000** |
