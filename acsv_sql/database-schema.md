# DATA SCHEMA — ACSV | NHÀ GA HÀNG HÓA HÀNG KHÔNG BI
## Database: `acsv_aircargo_demo` (MySQL 8.0, utf8mb4_unicode_ci)
## Phạm vi: 2025-01-01 → 2026-06-30 (18 tháng, 546 ngày) | "Hiện tại" = cuối tháng 6/2026

> Tài liệu tham chiếu cho AI engine. Mọi tên bảng/cột dưới đây khớp 100% với DDL đã tạo.
> Quy ước: tên bảng & cột **tiếng Anh snake_case**; giá trị enum & master data **tiếng Việt có dấu**.

---

## SƠ ĐỒ QUAN HỆ

```
dim_calendar (date_key PK)
  ├── fact_shipments.handling_date
  ├── fact_service_charges.charge_date
  ├── fact_flights.flight_date
  ├── fact_service_level.sla_date
  └── fact_zone_utilization.snapshot_date

dim_airlines (airline_id PK)
  ├── fact_shipments.airline_id
  ├── fact_flights.airline_id
  ├── fact_service_level.airline_id
  └── dim_contracts.airline_id

dim_agents (agent_id PK)
  └── fact_shipments.agent_id

dim_stations (station_code PK)
  ├── fact_shipments.origin_station_code
  ├── fact_shipments.destination_station_code
  ├── fact_flights.counterpart_station_code
  └── dim_airlines.hub_station_code          (soft reference, không FK cứng)

dim_commodities (commodity_id PK)
  └── fact_shipments.commodity_id

dim_zones (zone_id PK)
  ├── fact_shipments.zone_id
  ├── fact_zone_utilization.zone_id
  └── fact_leasing_revenue.zone_id

dim_services (service_id PK)
  └── fact_service_charges.service_id

dim_contracts (contract_id PK)
  └── (lookup theo airline_id + khoảng effective_from/effective_to — KHÔNG có FK từ fact)

fact_shipments (shipment_id PK)  ⭐ FACT CHÍNH
  └── fact_service_charges.shipment_id       (1 shipment → 0..n dòng phí)

fact_monthly_financials (financial_id PK)    (độc lập, grain = tháng × hạng mục chi phí)
fact_leasing_revenue   (leasing_id PK)       (độc lập, grain = tháng × khu × tenant)

_meta_tables · _meta_columns · _meta_kpi · _meta_glossary   (metadata, không có FK)
```

**Tóm tắt grain của từng fact table:**

| Bảng | Grain (1 dòng = ...) | Số dòng ~ |
|---|---|---|
| `fact_shipments` ⭐ | 1 AWB (Master Air Waybill) được xử lý | 310.000 |
| `fact_service_charges` | 1 dòng phí dịch vụ phụ trợ của 1 AWB | 1.100.000 |
| `fact_flights` | 1 chuyến bay (chiều đến hoặc đi) trong 1 ngày | 43.000 |
| `fact_service_level` | 1 ngày × 1 hãng bay | 9.828 |
| `fact_zone_utilization` | 1 ngày × 1 khu kho (SNAPSHOT) | 2.730 |
| `fact_monthly_financials` | 1 tháng × 1 hạng mục chi phí | 162 |
| `fact_leasing_revenue` | 1 tháng × 1 khu × 1 tenant | 108 |

---

## DIMENSION TABLES

### 1. `dim_calendar` (546 rows)
Lịch ngày từ 2025-01-01 đến 2026-06-30, có gắn cờ mùa vụ đặc thù Việt Nam.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `date_key` | DATE PK | Ngày | |
| `year` | SMALLINT | Năm | 2025 hoặc 2026 |
| `quarter` | TINYINT | Quý 1–4 | |
| `month` | TINYINT | Tháng 1–12 | |
| `month_name_vi` | VARCHAR(20) | Tên tháng tiếng Việt | 'Tháng 1'… 'Tháng 12' |
| `fiscal_period` | CHAR(7) | Kỳ báo cáo | 'YYYY-MM' — dùng để JOIN với `fact_monthly_financials` và `fact_leasing_revenue` |
| `week_of_year` | TINYINT | Tuần trong năm | |
| `day_of_week` | TINYINT | 1 = Thứ Hai … 7 = Chủ Nhật | |
| `day_name_vi` | VARCHAR(20) | Tên thứ | 'Thứ Hai'… 'Chủ Nhật' |
| `day_of_month` | TINYINT | Ngày trong tháng | |
| `is_weekend` | TINYINT(1) | Thứ 7 / Chủ nhật | Sản lượng cuối tuần chỉ bằng 70–82% ngày thường |
| `is_tet_period` | TINYINT(1) | Trong cửa sổ nghỉ + phục hồi Tết | Tết 2025 mùng 1 = 29/01; Tết 2026 mùng 1 = 17/02 |
| `is_peak_season` | TINYINT(1) | Tháng 10, 11, 12 | Mùa cao điểm Âu-Mỹ |
| `is_lychee_season` | TINYINT(1) | 01/06 – 20/07 | Mùa vải thiều — hàng FPER tăng đột biến |
| `season_note_vi` | VARCHAR(100) | Ghi chú mùa vụ | 'Cao điểm cuối năm', 'Nghỉ Tết Nguyên Đán', 'Phục hồi hậu Tết', 'Mùa vải thiều'… |

### 2. `dim_airlines` (18 rows)
Danh mục hãng hàng không là khách hàng của ACSV.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `airline_id` | INT PK | | |
| `iata_code` | CHAR(2) | Mã IATA | 'FX', 'CV', 'NH'… |
| `icao_code` | CHAR(3) | Mã ICAO | 'FDX', 'CLX'… |
| `airline_name` | VARCHAR(120) | Tên hãng | Giữ tên quốc tế |
| `country_name_vi` | VARCHAR(60) | Quốc gia (tiếng Việt) | 'Hoa Kỳ', 'Luxembourg', 'Nhật Bản'… |
| `carrier_type` | ENUM | Loại hãng | 'Freighter chuyên dụng' / 'Integrator' / 'Bellyhold quốc tế' / 'Bellyhold nội địa' |
| `hub_station_code` | CHAR(3) | Sân bay hub | Soft reference tới `dim_stations` |
| `is_key_account` | TINYINT(1) | Khách hàng trọng điểm | 6 hãng = 1 |
| `service_since_date` | DATE | Bắt đầu hợp tác | |
| `base_volume_share_pct` | DECIMAL(5,2) | Tỷ trọng sản lượng chuẩn (%) | Tổng = 100,00 |

**Danh sách đầy đủ (theo tỷ trọng giảm dần):**

| IATA | Hãng | Quốc gia | Loại | Key | Share % |
|---|---|---|---|---|---|
| FX | FedEx Express | Hoa Kỳ | Integrator | ✓ | 15,50 |
| CV | Cargolux Airlines | Luxembourg | Freighter chuyên dụng | ✓ | 12,80 |
| NH | All Nippon Airways Cargo | Nhật Bản | Bellyhold quốc tế | ✓ | 9,40 |
| LH | Lufthansa Cargo | Đức | Freighter chuyên dụng | ✓ | 8,20 |
| RU | AirBridgeCargo Airlines | UAE | Freighter chuyên dụng | ✓ | 7,60 |
| VJ | Vietjet Air Cargo | Việt Nam | Bellyhold nội địa | ✓ | 7,10 |
| RH | Hong Kong Air Cargo | Hong Kong | Freighter chuyên dụng | | 5,80 |
| UA | United Airlines Cargo | Hoa Kỳ | Bellyhold quốc tế | | 5,20 |
| MH | Malaysia Airlines Cargo | Malaysia | Bellyhold quốc tế | | 4,60 |
| PR | Philippine Airlines Cargo | Philippines | Bellyhold quốc tế | | 3,90 |
| HX | Hong Kong Airlines | Hong Kong | Bellyhold quốc tế | | 3,50 |
| CI | China Airlines Cargo | Đài Loan | Freighter chuyên dụng | | 3,20 |
| KE | Korean Air Cargo | Hàn Quốc | Bellyhold quốc tế | | 2,90 |
| CZ | China Southern Cargo | Trung Quốc | Bellyhold quốc tế | | 2,60 |
| SQ | Singapore Airlines Cargo | Singapore | Bellyhold quốc tế | | 2,40 |
| QR | Qatar Airways Cargo | Qatar | Freighter chuyên dụng | | 2,10 |
| BL | Pacific Airlines | Việt Nam | Bellyhold nội địa | | 1,90 |
| 5X | UPS Airlines | Hoa Kỳ | Integrator | | 1,30 |

### 3. `dim_agents` (120 rows)
Forwarder / đại lý giao nhận — khách hàng trực tiếp gửi và nhận hàng tại nhà ga.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `agent_id` | INT PK | | |
| `agent_code` | VARCHAR(12) | Mã đại lý | 'AGT-001'… 'AGT-120' |
| `agent_name` | VARCHAR(150) | Tên đại lý (tiếng Việt) | |
| `agent_tier` | ENUM | Phân hạng | 'Top-tier' (10 đv, 47% SL) / 'Trung bình' (30 đv, 33%) / 'Nhỏ' (80 đv, 20%) |
| `parent_country_vi` | VARCHAR(60) | Quốc gia công ty mẹ | |
| `is_own_uld_capable` | TINYINT(1) | Tự build-up ULD được | **Cột then chốt** — quyết định có phát sinh phí SVC-ULD-01/02 hay không |
| `has_bonded_warehouse` | TINYINT(1) | Có kho ngoại quan riêng | Ảnh hưởng thời gian lưu kho tại ACSV |
| `onboarding_date` | DATE | Ngày bắt đầu hợp tác | |
| `base_volume_share_pct` | DECIMAL(6,3) | Tỷ trọng sản lượng chuẩn (%) | Phân bố Pareto |

**10 đại lý Top-tier:** DHL Global Forwarding Việt Nam · Kuehne + Nagel Việt Nam · Expeditors Việt Nam · Nippon Express Việt Nam · Yusen Logistics Việt Nam · DB Schenker Việt Nam · Kerry Express Việt Nam · Agility Logistics Việt Nam · Bee Logistics Corporation · ITL Corporation (Indo Trans Logistics). Tất cả có `is_own_uld_capable = 1`.

### 4. `dim_stations` (42 rows) — **BẢNG TRỌNG TÂM CHO PHÂN TÍCH THỊ TRƯỜNG**
Sân bay đối tác. `HAN` (Nội Bài) là gốc; 41 station còn lại là đầu đối tác.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `station_code` | CHAR(3) PK | Mã IATA sân bay | 'HAN','HKG','JFK'… |
| `station_name` | VARCHAR(120) | Tên sân bay | |
| `city_name` | VARCHAR(80) | Thành phố | |
| `country_code` | CHAR(2) | Mã quốc gia ISO | |
| `country_name_vi` | VARCHAR(60) | Quốc gia (tiếng Việt) | 'Hoa Kỳ','Trung Quốc','Hàn Quốc'… |
| `market_region` | ENUM | **Khu vực thị trường** | 'Đông Bắc Á' / 'Đông Nam Á' / 'Bắc Mỹ' / 'Châu Âu' / 'Trung Đông - Nam Á' / 'Châu Úc' / 'Nội địa' |
| `is_domestic` | TINYINT(1) | Tuyến nội địa | |
| `ancillary_intensity_vnd_per_kg` | DECIMAL(10,2) | **Cường độ dịch vụ phụ trợ chuẩn của tuyến (đ/kg)** | Giải thích vì sao yield khác nhau giữa các thị trường — xem ghi chú dưới |
| `avg_flight_hours_from_han` | DECIMAL(4,1) | Thời gian bay trung bình từ HAN | |
| `base_volume_share_pct` | DECIMAL(5,2) | Tỷ trọng sản lượng chuẩn (%) | |

⚠️ **`ancillary_intensity_vnd_per_kg` là chìa khóa hiệu chênh lệch yield giữa các thị trường:**

| Market region | Ancillary đ/kg | Lý do |
|---|---|---|
| Bắc Mỹ | ~2.150 | Kiểm tra an ninh tăng cường TSA + ULD build-up cho freighter + lưu kho lâu do cut-off sớm |
| Châu Âu | ~1.980 | ACC3/EU security + ULD build-up + vật tư |
| Châu Úc | ~1.750 | Kiểm dịch + xử lý đặc biệt nông sản |
| Trung Đông - Nam Á | ~1.480 | Transit hub, một phần ULD |
| Đông Bắc Á | ~880 | Chủ yếu bellyhold, turnaround nhanh, ít ULD |
| Đông Nam Á | ~790 | Chặng ngắn, hàng lẻ, ít dịch vụ |
| Nội địa | ~320 | Không hải quan, soi chiếu đơn giản, không ULD quốc tế |

**Danh sách 42 station:**

| Code | Sân bay | Thành phố | Quốc gia | Market region |
|---|---|---|---|---|
| HAN | Nội Bài | Hà Nội | Việt Nam | Nội địa (gốc) |
| HKG | Hong Kong Intl | Hong Kong | Hong Kong | Đông Bắc Á |
| PVG | Phố Đông | Thượng Hải | Trung Quốc | Đông Bắc Á |
| PEK | Thủ Đô | Bắc Kinh | Trung Quốc | Đông Bắc Á |
| CAN | Bạch Vân | Quảng Châu | Trung Quốc | Đông Bắc Á |
| SZX | Bảo An | Thâm Quyến | Trung Quốc | Đông Bắc Á |
| TPE | Đào Viên | Đài Bắc | Đài Loan | Đông Bắc Á |
| NRT | Narita | Tokyo | Nhật Bản | Đông Bắc Á |
| KIX | Kansai | Osaka | Nhật Bản | Đông Bắc Á |
| ICN | Incheon | Seoul | Hàn Quốc | Đông Bắc Á |
| JFK | John F. Kennedy | New York | Hoa Kỳ | Bắc Mỹ |
| LAX | Los Angeles Intl | Los Angeles | Hoa Kỳ | Bắc Mỹ |
| ORD | O'Hare | Chicago | Hoa Kỳ | Bắc Mỹ |
| ANC | Ted Stevens | Anchorage | Hoa Kỳ | Bắc Mỹ |
| SFO | San Francisco Intl | San Francisco | Hoa Kỳ | Bắc Mỹ |
| MEM | Memphis Intl | Memphis | Hoa Kỳ | Bắc Mỹ |
| YYZ | Pearson | Toronto | Canada | Bắc Mỹ |
| FRA | Frankfurt am Main | Frankfurt | Đức | Châu Âu |
| LUX | Findel | Luxembourg | Luxembourg | Châu Âu |
| AMS | Schiphol | Amsterdam | Hà Lan | Châu Âu |
| CDG | Charles de Gaulle | Paris | Pháp | Châu Âu |
| LHR | Heathrow | London | Anh | Châu Âu |
| LGG | Liège | Liège | Bỉ | Châu Âu |
| BUD | Ferenc Liszt | Budapest | Hungary | Châu Âu |
| MAD | Barajas | Madrid | Tây Ban Nha | Châu Âu |
| SIN | Changi | Singapore | Singapore | Đông Nam Á |
| BKK | Suvarnabhumi | Bangkok | Thái Lan | Đông Nam Á |
| KUL | Kuala Lumpur Intl | Kuala Lumpur | Malaysia | Đông Nam Á |
| MNL | Ninoy Aquino | Manila | Philippines | Đông Nam Á |
| CGK | Soekarno-Hatta | Jakarta | Indonesia | Đông Nam Á |
| PNH | Phnom Penh Intl | Phnom Penh | Campuchia | Đông Nam Á |
| DXB | Dubai Intl | Dubai | UAE | Trung Đông - Nam Á |
| DOH | Hamad Intl | Doha | Qatar | Trung Đông - Nam Á |
| IST | Istanbul | Istanbul | Thổ Nhĩ Kỳ | Trung Đông - Nam Á |
| DEL | Indira Gandhi | New Delhi | Ấn Độ | Trung Đông - Nam Á |
| BOM | Chhatrapati Shivaji | Mumbai | Ấn Độ | Trung Đông - Nam Á |
| SYD | Kingsford Smith | Sydney | Úc | Châu Úc |
| MEL | Tullamarine | Melbourne | Úc | Châu Úc |
| SGN | Tân Sơn Nhất | TP. Hồ Chí Minh | Việt Nam | Nội địa |
| DAD | Đà Nẵng | Đà Nẵng | Việt Nam | Nội địa |
| CXR | Cam Ranh | Nha Trang | Việt Nam | Nội địa |
| PQC | Phú Quốc | Phú Quốc | Việt Nam | Nội địa |
| VCA | Cần Thơ | Cần Thơ | Việt Nam | Nội địa |

### 5. `dim_commodities` (14 rows)
Nhóm mặt hàng, kết hợp mã xử lý IATA và nhóm hàng thương mại.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `commodity_id` | INT PK | | |
| `iata_code` | CHAR(4) | Mã xử lý IATA | FGCR/FPER/FVUN/FAVI/FVAL/FDGR/FHEA |
| `commodity_name_vi` | VARCHAR(120) | Tên nhóm hàng | |
| `commercial_group` | ENUM | Nhóm hàng thương mại | 'Điện tử & linh kiện' / 'E-commerce & chuyển phát nhanh' / 'Dệt may & da giày' / 'Dược phẩm & thiết bị y tế' / 'Nông sản tươi' / 'Máy móc & khác' |
| `thc_rate_import_vnd_per_kg` | DECIMAL(8,2) | Đơn giá THC hàng nhập | VND/kg |
| `thc_rate_export_vnd_per_kg` | DECIMAL(8,2) | Đơn giá THC hàng xuất | VND/kg |
| `min_charge_import_vnd` | DECIMAL(12,2) | Cước tối thiểu/lô, hàng nhập | VND |
| `min_charge_export_vnd` | DECIMAL(12,2) | Cước tối thiểu/lô, hàng xuất | VND |
| `requires_cold_chain` | TINYINT(1) | Yêu cầu kho lạnh 2–8°C | |
| `requires_special_handling` | TINYINT(1) | Yêu cầu xử lý đặc biệt | Kéo theo phí SVC-SPL-01 |
| `base_volume_share_pct` | DECIMAL(5,2) | Tỷ trọng sản lượng chuẩn (%) | Tổng = 100,00 |

| ID | IATA | Tên hàng | Nhóm thương mại | Nhập | Xuất | Share % |
|---|---|---|---|---|---|---|
| 1 | FGCR | Linh kiện điện tử | Điện tử & linh kiện | 1.360 | 1.130 | 33,0 |
| 2 | FVAL | Điện thoại & thiết bị giá trị cao | Điện tử & linh kiện | 1.450 | 1.270 | 21,0 |
| 3 | FGCR | Hàng TMĐT thông thường | E-commerce & chuyển phát nhanh | 1.360 | 1.130 | 12,5 |
| 4 | FHEA | Kiện TMĐT nặng (≥150kg) | E-commerce & chuyển phát nhanh | 1.530 | 1.420 | 4,5 |
| 5 | FGCR | Hàng may mặc | Dệt may & da giày | 1.360 | 1.130 | 6,5 |
| 6 | FGCR | Giày dép & phụ kiện | Dệt may & da giày | 1.360 | 1.130 | 3,5 |
| 7 | FPER | Vắc-xin & sinh phẩm lạnh | Dược phẩm & thiết bị y tế | 1.660 | 1.400 | 1,5 |
| 8 | FVAL | Dược phẩm & thiết bị y tế | Dược phẩm & thiết bị y tế | 1.450 | 1.270 | 2,5 |
| 9 | FPER | Vải thiều & trái cây tươi | Nông sản tươi | 1.660 | 1.400 | 1,8 |
| 10 | FPER | Hoa tươi & rau quả | Nông sản tươi | 1.660 | 1.400 | 0,9 |
| 11 | FAVI | Động vật sống | Nông sản tươi | 1.600 | 1.310 | 0,3 |
| 12 | FGCR | Máy móc & phụ tùng | Máy móc & khác | 1.360 | 1.130 | 8,0 |
| 13 | FDGR | Hàng nguy hiểm (pin, hóa chất) | Máy móc & khác | 1.810 | 1.540 | 2,5 |
| 14 | FVUN | Hàng khó bảo quản | Máy móc & khác | 1.600 | 1.420 | 1,5 |

⚠️ **Giá NHẬP luôn cao hơn giá XUẤT 15–20%** — đặc thù ngành, không phải lỗi data.
⚠️ **Hàng nội địa (`scope_type = 'Nội địa'`) áp dụng 55% mức giá trên.**

### 6. `dim_services` (12 rows)
Danh mục dịch vụ phụ trợ ngoài THC. **THC KHÔNG nằm trong bảng này** — THC nằm trực tiếp trên `fact_shipments`.

| Cột | Kiểu | Mô tả |
|---|---|---|
| `service_id` | INT PK | |
| `service_code` | VARCHAR(15) | 'SVC-STO-01'… |
| `service_name_vi` | VARCHAR(120) | Tên dịch vụ |
| `service_category` | ENUM | 'Lưu kho' / 'Soi chiếu & an ninh' / 'ULD & vật tư' / 'Xử lý đặc biệt' / 'Thiết bị & nhân công' / 'Hành chính & hải quan' |
| `default_unit` | ENUM | 'kg' / 'giờ' / 'lô' / 'ULD' / 'lần' |
| `default_unit_price_vnd` | DECIMAL(12,2) | Đơn giá chuẩn (VND) |
| `is_waivable` | TINYINT(1) | Có thể miễn giảm hay không |

| ID | Code | Dịch vụ | Nhóm | Đơn vị | Giá (VND) | Waivable | Điều kiện phát sinh |
|---|---|---|---|---|---|---|---|
| 1 | SVC-STO-01 | Lưu kho tiêu chuẩn (48h đầu) | Lưu kho | kg | 180 | ✓ | Mọi AWB |
| 2 | SVC-STO-02 | Lưu kho quá hạn (sau 48h) | Lưu kho | kg | 420 | ✓ | `storage_hours > 48` |
| 3 | SVC-STO-03 | Lưu kho lạnh (2–8°C) | Lưu kho | kg | 950 | | `requires_cold_chain = 1` |
| 4 | SVC-SEC-01 | Soi chiếu X-ray | Soi chiếu & an ninh | kg | 520 | | Mọi AWB quốc tế |
| 5 | SVC-SEC-02 | Kiểm tra an ninh tăng cường (tuyến Mỹ/EU) | Soi chiếu & an ninh | kg | 380 | | `market_region ∈ {Bắc Mỹ, Châu Âu}` |
| 6 | SVC-ULD-01 | Build-up ULD | ULD & vật tư | ULD | 1.850.000 | | Xuất, `uld_count > 0`, agent KHÔNG tự làm được |
| 7 | SVC-ULD-02 | Break-down ULD | ULD & vật tư | ULD | 1.450.000 | | Nhập, `uld_count > 0`, agent KHÔNG tự làm được |
| 8 | SVC-ULD-03 | Vật tư đóng gói (lưới, film, nẹp) | ULD & vật tư | lô | 320.000 | ✓ | ~34% AWB xuất |
| 9 | SVC-SPL-01 | Phụ phí hàng đặc biệt (DGR/AVI/PER) | Xử lý đặc biệt | lô | 1.250.000 | | `requires_special_handling = 1` |
| 10 | SVC-EQP-01 | Thuê thiết bị nâng hàng nặng (>7 tấn) | Thiết bị & nhân công | lần | 2.400.000 | | `chargeable_weight_kg > 7.000` |
| 11 | SVC-ADM-01 | Phụ phí ngoài giờ / ngày lễ | Hành chính & hải quan | lô | 680.000 | ✓ | ~21% AWB (32% mùa cao điểm) |
| 12 | SVC-ADM-02 | Dịch vụ khai báo & chứng từ | Hành chính & hải quan | lô | 450.000 | ✓ | ~46% AWB, chỉ ~9% với agent Top-tier |

### 7. `dim_zones` (5 rows)
Khu vực kho trong 2 nhà ga CT1 và CT2.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `zone_id` | INT PK | | |
| `terminal_code` | ENUM('CT1','CT2') | Nhà ga | |
| `zone_name_vi` | VARCHAR(80) | Tên khu | |
| `area_sqm` | INT | Diện tích | m² |
| `design_capacity_tons_year` | INT | Công suất thiết kế | tấn/năm |
| `flow_scope` | ENUM | Phạm vi khai thác | 'Xuất quốc tế' / 'Nhập quốc tế' / 'Nội địa' / 'Hỗn hợp quốc tế' / 'Nội địa & cho thuê' |

| ID | Terminal | Khu | Diện tích m² | Công suất t/năm | Phạm vi |
|---|---|---|---|---|---|
| 1 | CT1 | CT1 - Khu xuất quốc tế | 6.500 | 62.000 | Xuất quốc tế |
| 2 | CT1 | CT1 - Khu nhập quốc tế | 5.000 | 48.000 | Nhập quốc tế |
| 3 | CT1 | CT1 - Khu nội địa | 2.200 | 20.000 | Nội địa |
| 4 | CT2 | CT2 - Tầng 1 quốc tế | 8.000 | **155.000** | Hỗn hợp quốc tế |
| 5 | CT2 | CT2 - Tầng 2 nội địa & cho thuê | 6.500 | 45.000 | Nội địa & cho thuê |

*Tổng công suất thiết kế 330.000 tấn/năm. CT2 = 200.000 tấn/năm (khớp số liệu công bố của ACSV).*

### 8. `dim_contracts` (22 rows)
Hợp đồng giá với từng hãng bay. **Có tính lịch sử** — một hãng có thể có nhiều hợp đồng theo thời gian.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `contract_id` | INT PK | | |
| `airline_id` | INT FK | → `dim_airlines` | |
| `contract_code` | VARCHAR(20) | Mã hợp đồng | |
| `effective_from` | DATE | Hiệu lực từ | |
| `effective_to` | DATE NULL | Hiệu lực đến | **NULL = còn hiệu lực** |
| `thc_discount_pct` | DECIMAL(5,2) | Chiết khấu THC (%) | 0–20 |
| `committed_volume_tons_year` | INT | Cam kết sản lượng | tấn/năm |
| `contract_note_vi` | VARCHAR(255) | Ghi chú | |

⚠️ **Cargolux (CV) có 2 hợp đồng — đây là thông tin quan trọng khi phân tích biến động yield năm 2026:**

| effective_from | effective_to | discount | committed | Ghi chú |
|---|---|---|---|---|
| 2024-01-01 | 2025-12-31 | 6,00% | 26.000 t | Hợp đồng khung 2024-2025 |
| 2026-01-01 | NULL | **14,00%** | 34.000 t | Tái đàm phán 2026 - giảm đơn giá đổi lấy cam kết sản lượng +31% |

---

## FACT TABLES

### 9. `fact_shipments` ⭐ (FACT CHÍNH — ~310K rows)
Mỗi dòng = 1 AWB (Master Air Waybill) được ACSV xử lý tại nhà ga.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `shipment_id` | BIGINT PK | | |
| `awb_number` | VARCHAR(20) | Số vận đơn hàng không | Định dạng `'{prefix}-{8 số}'` |
| `handling_date` | DATE FK | Ngày xử lý tại nhà ga | → `dim_calendar.date_key` |
| `handling_datetime` | DATETIME | Thời điểm xử lý | |
| `flow_type` | ENUM | Chiều hàng | 'Xuất' (53%) / 'Nhập' (43%) / 'Trung chuyển' (4%) |
| `scope_type` | ENUM | Phạm vi | 'Quốc tế' (~89%) / 'Nội địa' (~11%) |
| `airline_id` | INT FK | Hãng vận chuyển | |
| `agent_id` | INT FK | Forwarder / đại lý | |
| `origin_station_code` | CHAR(3) FK | Sân bay đi | 'HAN' nếu là hàng xuất |
| `destination_station_code` | CHAR(3) FK | Sân bay đến | 'HAN' nếu là hàng nhập |
| `market_region` | VARCHAR(30) | **Khu vực thị trường đối tác** (denormalized) | Của station ≠ HAN. Nếu cả 2 đều VN → 'Nội địa' |
| `counterpart_country_vi` | VARCHAR(60) | **Quốc gia đối tác** (denormalized) | Của station ≠ HAN |
| `commodity_id` | INT FK | Nhóm mặt hàng | |
| `zone_id` | INT FK | Khu kho xử lý | |
| `flight_number` | VARCHAR(10) | Số hiệu chuyến bay | |
| `pieces` | INT | Số kiện | kiện |
| `gross_weight_kg` | DECIMAL(12,2) | Trọng lượng thực | kg |
| `chargeable_weight_kg` | DECIMAL(12,2) | **Trọng lượng tính cước** | kg — **DÙNG CỘT NÀY CHO SẢN LƯỢNG** |
| `volume_cbm` | DECIMAL(10,3) | Thể tích | m³ |
| `uld_count` | INT | Số ULD | 0 nếu hàng lẻ |
| `storage_hours` | DECIMAL(8,2) | Số giờ lưu kho | giờ — >48 thì phát sinh phí quá hạn |
| `thc_rate_vnd_per_kg` | DECIMAL(10,2) | Đơn giá THC áp dụng | VND/kg — đã tính hệ số nội địa 0,55 nếu có |
| `thc_discount_pct` | DECIMAL(5,2) | Chiết khấu hợp đồng | % — **đã áp vào `thc_revenue_vnd`, KHÔNG trừ lại** |
| `thc_revenue_vnd` | DECIMAL(15,2) | Doanh thu THC | VND |
| `ancillary_revenue_vnd` | DECIMAL(15,2) | Doanh thu dịch vụ phụ trợ | VND — = SUM(`fact_service_charges.amount_vnd`) của shipment này |
| `ancillary_service_count` | INT | Số dịch vụ phụ trợ | **cơ sở tính attach rate** |
| `total_revenue_vnd` | DECIMAL(15,2) | **TỔNG DOANH THU** | VND — = `thc_revenue_vnd + ancillary_revenue_vnd` |
| `is_on_time` | TINYINT(1) | Xử lý đúng hạn | |
| `handling_minutes` | INT | Thời gian xử lý | phút |

⚠️ **LUÔN DÙNG `total_revenue_vnd` CHO DOANH THU.** Không cộng thêm `fact_service_charges.amount_vnd` — đã nằm trong `ancillary_revenue_vnd` rồi.
⚠️ **LUÔN DÙNG `chargeable_weight_kg` CHO SẢN LƯỢNG**, không dùng `gross_weight_kg`.
⚠️ **`market_region` và `counterpart_country_vi` đã denormalized** — dùng trực tiếp thay vì JOIN `dim_stations`, nhanh hơn và tránh nhầm chiều.

**Indexes:** `(handling_date)` · `(airline_id, handling_date)` · `(agent_id, handling_date)` · `(market_region, handling_date)` · `(commodity_id, handling_date)` · `(zone_id, handling_date)` · `(flow_type, scope_type)`

### 10. `fact_service_charges` (~1,1M rows)
Chi tiết từng dòng phí dịch vụ phụ trợ. Quan hệ 1-nhiều với `fact_shipments`.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `charge_id` | BIGINT PK | | |
| `shipment_id` | BIGINT FK | → `fact_shipments` | |
| `service_id` | INT FK | → `dim_services` | |
| `charge_date` | DATE FK | Ngày phát sinh phí | |
| `quantity` | DECIMAL(12,2) | Số lượng | theo `default_unit` của dịch vụ |
| `unit_price_vnd` | DECIMAL(12,2) | Đơn giá áp dụng | VND |
| `gross_amount_vnd` | DECIMAL(15,2) | **Số tiền lẽ ra phải thu** | VND |
| `is_waived` | TINYINT(1) | Có được miễn giảm không | |
| `waive_reason_vi` | VARCHAR(120) NULL | Lý do miễn giảm | 'Ưu đãi khách hàng chiến lược' / 'Miễn theo thỏa thuận khung' / 'Bù trừ sự cố khai thác' / 'Ưu đãi theo sản lượng' |
| `amount_vnd` | DECIMAL(15,2) | **Số tiền thực thu** | VND — **= 0 khi `is_waived = 1`** |

⚠️ **Doanh thu dùng `amount_vnd`. Thất thu / dư địa dùng `gross_amount_vnd WHERE is_waived = 1`.** Nhầm hai cột này sẽ làm sai toàn bộ phân tích doanh thu phụ trợ.

**Indexes:** `(shipment_id)` · `(service_id, charge_date)` · `(charge_date)` · `(is_waived)`

### 11. `fact_flights` (~43K rows)
Chuyến bay được ACSV phục vụ mặt đất. ~80 chuyến/ngày (cả 2 chiều).

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `flight_record_id` | BIGINT PK | | |
| `flight_date` | DATE FK | | |
| `airline_id` | INT FK | | |
| `flight_number` | VARCHAR(10) | | |
| `aircraft_type` | VARCHAR(20) | Loại tàu bay | 'B747-8F','B777F','A330-300','A321','MD-11F','B767-300F' |
| `is_freighter` | TINYINT(1) | Tàu bay chuyên chở hàng | 0 = bellyhold (khoang bụng máy bay chở khách) |
| `direction` | ENUM('Đến','Đi') | Chiều chuyến bay | |
| `counterpart_station_code` | CHAR(3) FK | Sân bay đầu kia | |
| `scheduled_time` | TIME | Giờ dự kiến | |
| `actual_time` | TIME | Giờ thực tế | |
| `delay_minutes` | INT | Chậm trễ | phút |
| `cargo_capacity_kg` | DECIMAL(12,2) | Sức chở hàng | kg |
| `cargo_handled_kg` | DECIMAL(12,2) | Hàng thực xử lý | kg |
| `load_factor_pct` | DECIMAL(5,2) | Hệ số tải hàng | % |
| `ground_handling_minutes` | INT | Thời gian phục vụ mặt đất | phút |

⚠️ **Khác grain với `fact_shipments`.** Một chuyến bay chở nhiều AWB, một AWB không nhất thiết ánh xạ 1-1 với một chuyến. `SUM(cargo_handled_kg)` KHÔNG bằng `SUM(chargeable_weight_kg)` — dùng bảng này cho phân tích năng lực vận chuyển và tần suất chuyến, không dùng cho doanh thu.

### 12. `fact_service_level` (9.828 rows)
Chất lượng dịch vụ theo ngày × hãng bay.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `sla_id` | BIGINT PK | | |
| `sla_date` | DATE FK | | |
| `airline_id` | INT FK | | |
| `shipments_handled` | INT | Số AWB xử lý | |
| `tonnage_handled` | DECIMAL(12,2) | Sản lượng xử lý | kg |
| `on_time_delivery_pct` | DECIMAL(5,2) | **OTD — tỷ lệ giao đúng hạn** | % |
| `avg_breakdown_minutes` | DECIMAL(6,2) | Thời gian rã hàng TB | phút |
| `damage_claims` | INT | Số vụ khiếu nại hư hỏng | vụ |
| `customer_complaints` | INT | Số phàn nàn khác | vụ |
| `sla_penalty_vnd` | DECIMAL(15,2) | Tiền phạt SLA | VND |

⚠️ **`on_time_delivery_pct` là tỷ lệ — dùng `AVG`, KHÔNG dùng `SUM`.** Nếu muốn OTD chuẩn theo trọng số sản lượng, hãy dùng `SUM(on_time_delivery_pct * tonnage_handled) / SUM(tonnage_handled)`.

### 13. `fact_zone_utilization` (2.730 rows) — ⚠️ BẢNG SNAPSHOT
Tình trạng khai thác khu kho, chốt theo NGÀY.

| Cột | Kiểu | Mô tả | Đơn vị | Cộng dồn được? |
|---|---|---|---|---|
| `utilization_id` | BIGINT PK | | | |
| `snapshot_date` | DATE FK | Ngày chốt | | |
| `zone_id` | INT FK | | | |
| `tonnage_throughput` | DECIMAL(12,2) | Sản lượng thông qua trong ngày | kg | ✅ SUM được |
| `tonnage_in_storage` | DECIMAL(12,2) | Tồn kho tại thời điểm chốt | kg | ❌ KHÔNG SUM |
| `occupied_sqm` | DECIMAL(10,2) | Diện tích đang chiếm dụng | m² | ❌ KHÔNG SUM |
| `utilization_pct` | DECIMAL(5,2) | **Tỷ lệ khai thác so với công suất thiết kế** | % | ❌ dùng AVG hoặc MAX |
| `peak_hour_throughput_tons` | DECIMAL(8,2) | Sản lượng giờ cao điểm | tấn | ❌ dùng MAX |
| `staff_on_duty` | INT | Nhân sự trực ca | người | ❌ dùng AVG |

⚠️ **Đây là bảng SNAPSHOT.** Dùng `WHERE snapshot_date = 'ngày cụ thể'` hoặc `AVG`/`MAX` trên một khoảng. `SUM(utilization_pct)` là vô nghĩa. Chỉ `tonnage_throughput` là cộng dồn được.

### 14. `fact_monthly_financials` (162 rows)
Chi phí theo tháng × hạng mục. Grain = tháng, KHÔNG có chi tiết theo khu/hãng/tuyến.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `financial_id` | INT PK | | |
| `period_month` | CHAR(7) | Kỳ | 'YYYY-MM' — JOIN với `dim_calendar.fiscal_period` |
| `cost_category` | ENUM | Hạng mục chi phí | 9 giá trị, xem dưới |
| `amount_vnd` | DECIMAL(15,2) | Số tiền | VND |
| `is_variable_cost` | TINYINT(1) | Chi phí biến đổi | |

9 hạng mục và tỷ trọng chuẩn: **Nhân công trực tiếp** 34% (biến đổi) · **Thuê đất & hạ tầng ACV** 16% (cố định) · **Khấu hao thiết bị & nhà ga** 14% (cố định) · **Điện, nước, nhiên liệu** 9% (biến đổi) · **Nhân công gián tiếp & quản lý** 7% (cố định) · **Bảo trì & sửa chữa** 7% (cố định) · **An ninh & tuân thủ** 6% (biến đổi) · **Vật tư & tiêu hao** 5% (biến đổi) · **Chi phí khác** 2% (cố định).

Biên lợi nhuận gộp dao động **44,5%–48,5%** — cao vào T10–T12 (operating leverage), thấp vào T2 (chi phí cố định không giảm theo sản lượng).

### 15. `fact_leasing_revenue` (108 rows)
Doanh thu cho thuê kho & văn phòng. **KHÔNG gắn với shipment nào.**

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `leasing_id` | INT PK | | |
| `period_month` | CHAR(7) | Kỳ | 'YYYY-MM' |
| `zone_id` | INT FK | Khu cho thuê | |
| `tenant_name` | VARCHAR(120) | Bên thuê | |
| `leased_sqm` | DECIMAL(10,2) | Diện tích thuê | m² |
| `monthly_rent_vnd` | DECIMAL(15,2) | Tiền thuê tháng | VND |

6 tenant: DHL Global Forwarding Việt Nam · Kuehne + Nagel Việt Nam · Bee Logistics Corporation · ITL Corporation (Indo Trans Logistics) · Chi cục Hải quan CK sân bay Nội Bài · Vietnam Airlines Cargo Office.
Tổng ≈ **2,8–3,1 tỷ VND/tháng** (~35 tỷ/năm).

⚠️ **Doanh thu toàn công ty = `SUM(fact_shipments.total_revenue_vnd)` + `SUM(fact_leasing_revenue.monthly_rent_vnd)`.**

### 16–19. Metadata tables
`_meta_tables` (table_name, description_vi, description_en, business_context, row_count_estimate, is_fact) · `_meta_columns` (table_name, column_name, data_type, description_vi, description_en, unit, example_values) · `_meta_kpi` (kpi_name, formula_sql, description_vi, related_questions, benchmark_note) · `_meta_glossary` (term_vi, term_en, definition).

---

## SQL TEMPLATES

### T1 — Doanh thu & sản lượng theo tháng (kèm doanh thu cho thuê)
```sql
SELECT
  DATE_FORMAT(s.handling_date, '%Y-%m')                            AS ky,
  ROUND(SUM(s.chargeable_weight_kg)/1000, 0)                       AS san_luong_tan,
  ROUND(SUM(s.total_revenue_vnd)/1e9, 2)                           AS dt_shipment_ty,
  ROUND(COALESCE(l.rent, 0)/1e9, 2)                                AS dt_cho_thue_ty,
  ROUND((SUM(s.total_revenue_vnd) + COALESCE(l.rent,0))/1e9, 2)    AS tong_dt_ty,
  ROUND(SUM(s.total_revenue_vnd)/SUM(s.chargeable_weight_kg), 0)   AS yield_vnd_kg
FROM `fact_shipments` s
LEFT JOIN (
  SELECT `period_month`, SUM(`monthly_rent_vnd`) AS rent
  FROM `fact_leasing_revenue` GROUP BY `period_month`
) l ON l.`period_month` = DATE_FORMAT(s.`handling_date`, '%Y-%m')
GROUP BY ky, l.rent
ORDER BY ky;
```

### T2 — So sánh YoY 6 tháng đầu năm (revenue bridge)
```sql
SELECT
  CASE WHEN s.`handling_date` < '2026-01-01' THEN '6T/2025' ELSE '6T/2026' END AS ky,
  ROUND(SUM(s.`chargeable_weight_kg`)/1000, 0)                        AS san_luong_tan,
  ROUND(SUM(s.`total_revenue_vnd`)/1e9, 1)                            AS doanh_thu_ty,
  ROUND(SUM(s.`thc_revenue_vnd`)/1e9, 1)                              AS dt_thc_ty,
  ROUND(SUM(s.`ancillary_revenue_vnd`)/1e9, 1)                        AS dt_phu_tro_ty,
  ROUND(SUM(s.`ancillary_revenue_vnd`)/SUM(s.`total_revenue_vnd`)*100, 1) AS pct_phu_tro,
  ROUND(SUM(s.`total_revenue_vnd`)/SUM(s.`chargeable_weight_kg`), 0)  AS yield_vnd_kg
FROM `fact_shipments` s
WHERE (s.`handling_date` BETWEEN '2025-01-01' AND '2025-06-30')
   OR (s.`handling_date` BETWEEN '2026-01-01' AND '2026-06-30')
GROUP BY ky
ORDER BY ky;
```

### T3 — Cơ cấu doanh thu theo THỊ TRƯỜNG (market region), so sánh 2 kỳ
```sql
WITH base AS (
  SELECT
    `market_region`,
    CASE WHEN `handling_date` < '2026-01-01' THEN '6T2025' ELSE '6T2026' END AS ky,
    SUM(`chargeable_weight_kg`) AS kg,
    SUM(`total_revenue_vnd`)    AS dt
  FROM `fact_shipments`
  WHERE (`handling_date` BETWEEN '2025-01-01' AND '2025-06-30')
     OR (`handling_date` BETWEEN '2026-01-01' AND '2026-06-30')
  GROUP BY `market_region`, ky
)
SELECT
  `market_region`,
  ROUND(MAX(CASE WHEN ky='6T2025' THEN kg END)/1000, 0)  AS tan_6t2025,
  ROUND(MAX(CASE WHEN ky='6T2026' THEN kg END)/1000, 0)  AS tan_6t2026,
  ROUND(100*MAX(CASE WHEN ky='6T2025' THEN kg END)
        / SUM(MAX(CASE WHEN ky='6T2025' THEN kg END)) OVER (), 1) AS pct_sl_6t2025,
  ROUND(100*MAX(CASE WHEN ky='6T2026' THEN kg END)
        / SUM(MAX(CASE WHEN ky='6T2026' THEN kg END)) OVER (), 1) AS pct_sl_6t2026,
  ROUND(SUM(dt)/SUM(kg), 0)                                        AS yield_vnd_kg
FROM base
GROUP BY `market_region`
ORDER BY yield_vnd_kg DESC;
```

### T4 — Top quốc gia theo doanh thu và tăng trưởng
```sql
SELECT
  `counterpart_country_vi`                                                        AS quoc_gia,
  ROUND(SUM(CASE WHEN `handling_date`<'2026-01-01' THEN `chargeable_weight_kg` ELSE 0 END)/1000,0) AS tan_6t2025,
  ROUND(SUM(CASE WHEN `handling_date`>='2026-01-01' THEN `chargeable_weight_kg` ELSE 0 END)/1000,0) AS tan_6t2026,
  ROUND(100*(SUM(CASE WHEN `handling_date`>='2026-01-01' THEN `chargeable_weight_kg` ELSE 0 END)
       / NULLIF(SUM(CASE WHEN `handling_date`<'2026-01-01' THEN `chargeable_weight_kg` ELSE 0 END),0) - 1), 1) AS tang_truong_pct,
  ROUND(SUM(`total_revenue_vnd`)/1e9, 2)                                          AS dt_ty,
  ROUND(SUM(`total_revenue_vnd`)/SUM(`chargeable_weight_kg`), 0)                  AS yield_vnd_kg
FROM `fact_shipments`
WHERE (`handling_date` BETWEEN '2025-01-01' AND '2025-06-30')
   OR (`handling_date` BETWEEN '2026-01-01' AND '2026-06-30')
GROUP BY `counterpart_country_vi`
ORDER BY dt_ty DESC
LIMIT 20;
```

### T5 — Tách hiệu ứng MIX vs hiệu ứng GIÁ trong biến động yield
```sql
WITH y AS (
  SELECT
    `market_region`,
    SUM(CASE WHEN `handling_date` <  '2026-01-01' THEN `chargeable_weight_kg` ELSE 0 END) AS w25,
    SUM(CASE WHEN `handling_date` >= '2026-01-01' THEN `chargeable_weight_kg` ELSE 0 END) AS w26,
    SUM(CASE WHEN `handling_date` <  '2026-01-01' THEN `total_revenue_vnd` ELSE 0 END)
      / NULLIF(SUM(CASE WHEN `handling_date` < '2026-01-01' THEN `chargeable_weight_kg` ELSE 0 END),0) AS y25,
    SUM(CASE WHEN `handling_date` >= '2026-01-01' THEN `total_revenue_vnd` ELSE 0 END)
      / NULLIF(SUM(CASE WHEN `handling_date` >= '2026-01-01' THEN `chargeable_weight_kg` ELSE 0 END),0) AS y26
  FROM `fact_shipments`
  WHERE (`handling_date` BETWEEN '2025-01-01' AND '2025-06-30')
     OR (`handling_date` BETWEEN '2026-01-01' AND '2026-06-30')
  GROUP BY `market_region`
)
SELECT
  ROUND(SUM(w25*y25)/SUM(w25), 1)                        AS yield_6t2025,
  ROUND(SUM(w26*y26)/SUM(w26), 1)                        AS yield_6t2026,
  ROUND(SUM(w26*y25)/SUM(w26) - SUM(w25*y25)/SUM(w25), 1) AS hieu_ung_mix_vnd_kg,
  ROUND(SUM(w26*y26)/SUM(w26) - SUM(w26*y25)/SUM(w26), 1) AS hieu_ung_gia_vnd_kg
FROM y;
```

### T6 — Đóng góp & tăng trưởng theo hãng bay (phát hiện churn)
```sql
SELECT
  a.`airline_name`,
  a.`carrier_type`,
  ROUND(SUM(s.`total_revenue_vnd`)/1e9, 2)                                       AS dt_18t_ty,
  ROUND(100*SUM(s.`total_revenue_vnd`)/SUM(SUM(s.`total_revenue_vnd`)) OVER (),1) AS pct_dt,
  ROUND(SUM(CASE WHEN s.`handling_date` >= '2026-01-01'
                 THEN s.`chargeable_weight_kg` ELSE 0 END)/1000, 0)              AS tan_6t2026,
  ROUND(100*(SUM(CASE WHEN s.`handling_date` >= '2026-01-01' THEN s.`chargeable_weight_kg` ELSE 0 END)
       / NULLIF(SUM(CASE WHEN s.`handling_date` BETWEEN '2025-01-01' AND '2025-06-30'
                         THEN s.`chargeable_weight_kg` ELSE 0 END),0) - 1), 1)   AS tang_truong_sl_pct
FROM `fact_shipments` s
JOIN `dim_airlines` a ON a.`airline_id` = s.`airline_id`
GROUP BY a.`airline_name`, a.`carrier_type`
ORDER BY dt_18t_ty DESC;
```

### T7 — Diễn biến chất lượng dịch vụ theo hãng (root cause của churn)
```sql
SELECT
  a.`airline_name`,
  DATE_FORMAT(sl.`sla_date`, '%Y-%m')                                  AS ky,
  ROUND(SUM(sl.`on_time_delivery_pct` * sl.`tonnage_handled`)
        / NULLIF(SUM(sl.`tonnage_handled`),0), 1)                      AS otd_pct,
  SUM(sl.`damage_claims`)                                              AS khieu_nai_hu_hong,
  SUM(sl.`customer_complaints`)                                        AS phan_nan,
  ROUND(SUM(sl.`sla_penalty_vnd`)/1e6, 1)                              AS phat_sla_trieu
FROM `fact_service_level` sl
JOIN `dim_airlines` a ON a.`airline_id` = sl.`airline_id`
WHERE sl.`sla_date` >= '2025-07-01'
GROUP BY a.`airline_name`, ky
ORDER BY a.`airline_name`, ky;
```

### T8 — Attach rate & doanh thu phụ trợ theo tier forwarder
```sql
SELECT
  ag.`agent_tier`,
  COUNT(*)                                                                AS so_awb,
  ROUND(AVG(s.`ancillary_service_count`), 2)                              AS attach_rate,
  ROUND(SUM(s.`chargeable_weight_kg`)/1000, 0)                            AS san_luong_tan,
  ROUND(SUM(s.`ancillary_revenue_vnd`)/1e9, 2)                            AS dt_phu_tro_ty,
  ROUND(SUM(s.`ancillary_revenue_vnd`)/SUM(s.`total_revenue_vnd`)*100, 1) AS pct_phu_tro,
  ROUND(SUM(s.`ancillary_revenue_vnd`)/SUM(s.`chargeable_weight_kg`), 0)  AS phu_tro_vnd_kg
FROM `fact_shipments` s
JOIN `dim_agents` ag ON ag.`agent_id` = s.`agent_id`
WHERE s.`handling_date` >= '2025-07-01'
GROUP BY ag.`agent_tier`
ORDER BY attach_rate;
```

### T9 — Thất thu do miễn giảm phí
```sql
SELECT
  ag.`agent_tier`,
  sv.`service_name_vi`,
  COUNT(*)                                       AS so_dong_mien_giam,
  ROUND(SUM(sc.`gross_amount_vnd`)/1e9, 3)       AS that_thu_ty,
  sc.`waive_reason_vi`
FROM `fact_service_charges` sc
JOIN `fact_shipments` s  ON s.`shipment_id` = sc.`shipment_id`
JOIN `dim_agents`     ag ON ag.`agent_id`   = s.`agent_id`
JOIN `dim_services`   sv ON sv.`service_id` = sc.`service_id`
WHERE sc.`is_waived` = 1
  AND sc.`charge_date` >= '2025-07-01'
GROUP BY ag.`agent_tier`, sv.`service_name_vi`, sc.`waive_reason_vi`
ORDER BY that_thu_ty DESC;
```

### T10 — Khai thác công suất theo khu kho
```sql
SELECT
  z.`terminal_code`,
  z.`zone_name_vi`,
  z.`design_capacity_tons_year`,
  DATE_FORMAT(u.`snapshot_date`, '%Y-%m')          AS ky,
  ROUND(AVG(u.`utilization_pct`), 1)               AS util_tb_pct,   -- AVG, KHÔNG SUM
  ROUND(MAX(u.`utilization_pct`), 1)               AS util_dinh_pct,
  ROUND(SUM(u.`tonnage_throughput`)/1000, 0)       AS thong_qua_tan  -- throughput cộng dồn được
FROM `fact_zone_utilization` u
JOIN `dim_zones` z ON z.`zone_id` = u.`zone_id`
WHERE u.`snapshot_date` >= '2025-07-01'
GROUP BY z.`terminal_code`, z.`zone_name_vi`, z.`design_capacity_tons_year`, ky
ORDER BY z.`zone_id`, ky;
```

### T11 — Biên lợi nhuận gộp theo tháng
```sql
WITH dt AS (
  SELECT DATE_FORMAT(`handling_date`,'%Y-%m') AS ky, SUM(`total_revenue_vnd`) AS dt_ship
  FROM `fact_shipments` GROUP BY ky
), thue AS (
  SELECT `period_month` AS ky, SUM(`monthly_rent_vnd`) AS dt_thue
  FROM `fact_leasing_revenue` GROUP BY `period_month`
), cp AS (
  SELECT `period_month` AS ky, SUM(`amount_vnd`) AS chi_phi
  FROM `fact_monthly_financials` GROUP BY `period_month`
)
SELECT
  dt.ky,
  ROUND((dt.dt_ship + COALESCE(thue.dt_thue,0))/1e9, 2)                    AS tong_dt_ty,
  ROUND(cp.chi_phi/1e9, 2)                                                 AS chi_phi_ty,
  ROUND(100*(dt.dt_ship + COALESCE(thue.dt_thue,0) - cp.chi_phi)
        / (dt.dt_ship + COALESCE(thue.dt_thue,0)), 1)                      AS bien_gop_pct
FROM dt
LEFT JOIN thue ON thue.ky = dt.ky
LEFT JOIN cp   ON cp.ky   = dt.ky
ORDER BY dt.ky;
```

### T12 — Cơ cấu theo nhóm hàng thương mại (mùa vụ)
```sql
SELECT
  c.`commercial_group`,
  DATE_FORMAT(s.`handling_date`, '%Y-%m')                       AS ky,
  ROUND(SUM(s.`chargeable_weight_kg`)/1000, 1)                  AS tan,
  ROUND(SUM(s.`total_revenue_vnd`)/1e9, 2)                      AS dt_ty,
  ROUND(SUM(s.`total_revenue_vnd`)/SUM(s.`chargeable_weight_kg`), 0) AS yield_vnd_kg
FROM `fact_shipments` s
JOIN `dim_commodities` c ON c.`commodity_id` = s.`commodity_id`
GROUP BY c.`commercial_group`, ky
ORDER BY c.`commercial_group`, ky;
```

---

## JOIN WARNINGS

1. **`fact_shipments` ↔ `fact_service_charges` — quan hệ 1-nhiều.** JOIN trực tiếp rồi `SUM(total_revenue_vnd)` sẽ **nhân doanh thu lên nhiều lần** (mỗi shipment lặp lại theo số dòng phí). Nếu cần cả hai: aggregate `fact_service_charges` trước rồi mới JOIN, hoặc dùng cột đã denormalized `ancillary_revenue_vnd` / `ancillary_service_count` trên `fact_shipments`.

2. **KHÔNG cộng `total_revenue_vnd` với `fact_service_charges.amount_vnd`.** `ancillary_revenue_vnd` (nằm trong `total_revenue_vnd`) đã là tổng của các dòng phí. Cộng thêm là tính trùng.

3. **`fact_zone_utilization` = SNAPSHOT.** `tonnage_in_storage`, `occupied_sqm`, `utilization_pct`, `staff_on_duty` **KHÔNG SUM qua nhiều ngày** — dùng `AVG`/`MAX`, hoặc `WHERE snapshot_date = 'ngày'`. Chỉ `tonnage_throughput` là cộng dồn được.

4. **`fact_flights` khác grain với `fact_shipments`.** Một chuyến bay chở nhiều AWB. `SUM(cargo_handled_kg)` ≠ `SUM(chargeable_weight_kg)`. Đừng JOIN 2 bảng này qua `flight_number` + ngày để tính doanh thu — sẽ sai. Dùng `fact_flights` cho phân tích tần suất chuyến, sức chở, load factor, đúng giờ cất/hạ cánh.

5. **`fact_service_level` là tỷ lệ theo ngày × hãng.** `on_time_delivery_pct` phải dùng `AVG`, hoặc chuẩn hơn là bình quân gia quyền theo `tonnage_handled`. `SUM(on_time_delivery_pct)` là vô nghĩa.

6. **`dim_contracts` không có FK từ fact.** Phải lookup theo `airline_id` VÀ khoảng thời gian: `WHERE c.airline_id = s.airline_id AND s.handling_date >= c.effective_from AND (c.effective_to IS NULL OR s.handling_date <= c.effective_to)`. Nếu quên điều kiện thời gian, Cargolux sẽ trả về 2 dòng và làm nhân đôi kết quả.

7. **`fact_shipments.origin_station_code` vs `destination_station_code`.** Với hàng Xuất thì origin = 'HAN'; với hàng Nhập thì destination = 'HAN'; với Trung chuyển thì cả hai đều ≠ 'HAN'. Nếu JOIN `dim_stations` mà không xét `flow_type`, bạn sẽ lấy nhầm đầu HAN và mọi phân tích thị trường sẽ ra 'Nội địa'. **Cách an toàn: dùng cột denormalized `market_region` và `counterpart_country_vi`.**

8. **`fact_monthly_financials` và `fact_leasing_revenue` dùng `period_month` CHAR(7), không phải DATE.** JOIN với `fact_shipments` phải qua `DATE_FORMAT(handling_date, '%Y-%m')` hoặc `dim_calendar.fiscal_period`. JOIN trực tiếp với `handling_date` sẽ không match.

9. **`fact_service_charges.amount_vnd` = 0 khi `is_waived = 1`.** Nếu muốn tính "lẽ ra thu được bao nhiêu", dùng `gross_amount_vnd`. Nếu tính doanh thu thực, dùng `amount_vnd`.

10. **`dim_agents` chỉ JOIN được với `fact_service_charges` thông qua `fact_shipments`.** Không có `agent_id` trên bảng charges.

11. **Doanh thu cho thuê không nằm trong bất kỳ fact shipment nào.** Báo cáo doanh thu toàn công ty mà quên `fact_leasing_revenue` sẽ thiếu ~35 tỷ/năm (~6% doanh thu).

12. **`dim_airlines.hub_station_code` là soft reference**, không có ràng buộc FK cứng — dùng để tham chiếu ngữ cảnh, không dùng làm khóa JOIN chính.

---

## ĐƠN VỊ TIỀN TỆ & ĐO LƯỜNG

| Bảng | Cột | Đơn vị |
|---|---|---|
| `fact_shipments` | `thc_revenue_vnd`, `ancillary_revenue_vnd`, `total_revenue_vnd` | VND |
| `fact_shipments` | `thc_rate_vnd_per_kg` | VND/kg |
| `fact_shipments` | `gross_weight_kg`, `chargeable_weight_kg` | kg |
| `fact_shipments` | `volume_cbm` | m³ |
| `fact_shipments` | `storage_hours` | giờ |
| `fact_shipments` | `handling_minutes` | phút |
| `fact_service_charges` | `gross_amount_vnd`, `amount_vnd`, `unit_price_vnd` | VND |
| `fact_flights` | `cargo_capacity_kg`, `cargo_handled_kg` | kg |
| `fact_flights` | `load_factor_pct`, `delay_minutes` | % / phút |
| `fact_service_level` | `tonnage_handled` | kg |
| `fact_service_level` | `on_time_delivery_pct` | % |
| `fact_service_level` | `sla_penalty_vnd` | VND |
| `fact_zone_utilization` | `tonnage_throughput`, `tonnage_in_storage` | kg |
| `fact_zone_utilization` | `peak_hour_throughput_tons` | tấn |
| `fact_zone_utilization` | `occupied_sqm` | m² |
| `fact_zone_utilization` | `utilization_pct` | % |
| `fact_monthly_financials` | `amount_vnd` | VND |
| `fact_leasing_revenue` | `monthly_rent_vnd` | VND |
| `fact_leasing_revenue` | `leased_sqm` | m² |
| `dim_commodities` | `thc_rate_*_vnd_per_kg` | VND/kg |
| `dim_commodities` | `min_charge_*_vnd` | VND |
| `dim_stations` | `ancillary_intensity_vnd_per_kg` | VND/kg |
| `dim_zones` | `area_sqm` / `design_capacity_tons_year` | m² / tấn/năm |

⚠️ **Trọng lượng lưu ở đơn vị kg. Muốn báo cáo theo tấn phải chia 1.000.**

**Format hiển thị cho lãnh đạo:**
- Tiền > 1 tỷ: "X,X tỷ" (ví dụ "276,0 tỷ") — 1 chữ số thập phân
- Tiền < 1 tỷ: "XXX triệu"
- Sản lượng: "111.500 tấn" — không thập phân khi > 1.000 tấn
- Yield: "2.309 đ/kg" — số nguyên
- Phần trăm: 1 chữ số thập phân ("+13,8%", "52,7%")
- Dấu thập phân là dấu **phẩy**, dấu phân cách hàng nghìn là dấu **chấm** (chuẩn Việt Nam)

---

## GHI CHÚ VỀ MỐC SANITY CHECK

Nếu kết quả query lệch xa các mốc dưới đây, hãy nghi ngờ query trước khi báo cáo:

| Chỉ số | Mốc bình thường |
|---|---|
| Doanh thu tháng | 44–52 tỷ VND (T11 cao điểm: 58–62 tỷ; T2 Tết: 32–36 tỷ) |
| Sản lượng tháng | 17.000–22.000 tấn (T2 Tết: 12.000–14.000 tấn) |
| Yield | 2.300–2.600 đ/kg |
| Tỷ trọng doanh thu phụ trợ | 50–53% |
| Biên lợi nhuận gộp | 44,5–48,5% |
| Số AWB/ngày | 500–800 |
| Trọng lượng trung bình 1 AWB | ~1.100 kg (trung vị ~630 kg) |
| Cơ cấu quốc tế/nội địa | ~89% / ~11% sản lượng |
| Tỷ trọng doanh thu top 5 hãng | ~59–63% |
| OTD trung bình | 94–98% |
