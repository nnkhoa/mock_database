# DATA SCHEMA — COTECCONS XÂY DỰNG BI
## Database: coteccons_demo (MySQL 8.0, utf8mb4_unicode_ci)
## Phạm vi: 01/07/2024 – 30/09/2026 (27 tháng, Q1 NĐTC 2025 – Q1 NĐTC 2027) | "Hiện tại" = 30/09/2026 | Niên độ 01/07 – 30/06

---

## SƠ ĐỒ QUAN HỆ

```
dim_calendar (date_key PK)                    ← JOIN logic: period_month, change_date, submitted_date...
  (không khai báo FK; bảng theo tháng JOIN date_key = period_month)

dim_business_units (business_unit_id PK)
  ├── dim_projects.business_unit_id
  └── fact_bids.business_unit_id

dim_segments (sub_segment_code PK; segment_code = mã mảng)
  ├── dim_projects.sub_segment_code
  ├── fact_bids.sub_segment_code
  └── fact_plan_segment_monthly.segment_code      (logic, theo segment_code)

dim_locations (location_id PK)
  ├── dim_projects.location_id
  └── fact_bids.location_id

dim_clients (client_id PK; client_group = tập đoàn)
  ├── dim_projects.client_id
  └── fact_bids.client_id

dim_consultants (consultant_id PK)
  ├── dim_projects.consultant_id                  (TVGS hiện tại)
  └── fact_payment_applications.consultant_id     (TVGS xử lý từng hồ sơ)

dim_subcontractors (subcontractor_id PK)
  ├── fact_subcontract_packages.subcontractor_id
  └── fact_site_workforce_monthly.labor_subcontractor_id

dim_cost_elements (cost_element_code PK)
  ├── fact_project_costs.cost_element_code
  └── fact_subcontract_packages.cost_element_code

dim_projects (project_id PK)
  ├── fact_contract_changes.project_id
  ├── fact_variation_orders.project_id
  ├── fact_project_baseline_plan.project_id        (project_id, period_month)
  ├── fact_project_monthly.project_id              (project_id, period_month) ⭐
  ├── fact_project_costs.project_id                (project_id, period_month, cost_element_code, cost_scope)
  ├── fact_project_forecast_snapshots.project_id   (snapshot_date, project_id)  SNAPSHOT
  ├── fact_backlog_snapshots.project_id            (snapshot_date, project_id)  SNAPSHOT
  ├── fact_payment_applications.project_id
  ├── fact_receivable_snapshots.project_id         (snapshot_date, project_id)  SNAPSHOT
  ├── fact_project_cashflows_monthly.project_id    (project_id, period_month)
  ├── fact_subcontract_packages.project_id
  ├── fact_subcontract_variations.project_id
  ├── fact_site_workforce_monthly.project_id       (project_id, period_month, trade)
  └── fact_site_safety_monthly.project_id          (project_id, period_month)

fact_subcontract_packages (subcontract_id PK)
  └── fact_subcontract_variations.subcontract_id

Liên kết logic (không khai báo FK):
  fact_bids.project_id                         → dim_projects.project_id (gói trúng thầu)
  fact_contract_changes.variation_order_id     → fact_variation_orders.variation_order_id
  fact_subcontract_variations.linked_variation_order_id → fact_variation_orders.variation_order_id
  fact_input_prices_monthly (period_month, region) ↔ dim_locations.region của dự án
  fact_corporate_pnl_monthly, fact_treasury_monthly: cấp doanh nghiệp, theo period_month
  fact_plan_segment_monthly / fact_plan_corporate_quarterly: theo plan_version + kỳ
```

---

## DIMENSION TABLES

### 1. dim_calendar (~2.010 dòng)
Lịch ngày 01/07/2024 – 31/12/2029, có nhãn niên độ tài chính. Mọi bảng theo tháng JOIN qua `date_key` = `period_month` (ngày đầu tháng).

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `date_key` | DATE PK | Ngày |  |
| `calendar_year` | SMALLINT | Năm dương lịch |  |
| `calendar_month` | TINYINT | Tháng dương lịch 1-12 |  |
| `month_start_date` | DATE | Ngày đầu tháng, dùng JOIN với period_month của các bảng fact theo tháng |  |
| `fiscal_year` | SMALLINT | Niên độ tài chính Coteccons: 2027 = 01/07/2026 - 30/06/2027 |  |
| `fiscal_quarter` | TINYINT | Quý theo niên độ: 1 = T7-T9, 2 = T10-T12, 3 = T1-T3, 4 = T4-T6 |  |
| `fiscal_quarter_label` | VARCHAR(16) | Nhãn quý, ví dụ Q1 NĐTC 2027 |  |
| `fiscal_month_no` | TINYINT | Thứ tự tháng trong niên độ: 1 = tháng 7 ... 12 = tháng 6 |  |
| `day_of_week` | TINYINT | 1 = Thứ Hai ... 7 = Chủ Nhật |  |
| `is_working_day` | TINYINT | 1 nếu là ngày làm việc công trường (Thứ Hai - Thứ Bảy, trừ ngày lễ) |  |
| `is_holiday` | TINYINT | 1 nếu là ngày lễ |  |
| `holiday_name` | VARCHAR(50) | Tên ngày lễ |  |
| `is_tet_period` | TINYINT | 1 nếu trong khoảng 10 ngày trước đến 10 ngày sau mùng 1 Tết |  |
| `is_rainy_season_south` | TINYINT | 1 nếu thuộc mùa mưa miền Nam (tháng 5 - tháng 10) |  |

⚠️ **Niên độ: tháng 7–12 thuộc NĐTC năm sau (07/2026 → NĐTC 2027). Quý 1 = T7–T9, Quý 2 = T10–T12, Quý 3 = T1–T3, Quý 4 = T4–T6.**
⚠️ Bảng chỉ có các ngày từ 01/07/2024. Dòng 'Ký mới HĐ' của hợp đồng ký trước 7/2024 không JOIN được với lịch.

### 2. dim_business_units (5 dòng)
Khối và đơn vị kinh doanh phụ trách dự án.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `business_unit_id` | VARCHAR(10) PK | Mã khối/BU: BU-DDN, BU-DDB, BU01, UNC, INTL |  |
| `business_unit_name` | VARCHAR(150) | Tên khối/BU |  |
| `legal_entity` | VARCHAR(150) | Pháp nhân ký hợp đồng |  |
| `focus_area` | VARCHAR(255) | Mảng phụ trách chính |  |
| `head_office` | VARCHAR(60) | Nơi đặt văn phòng điều hành |  |

| business_unit_id | business_unit_name | Mảng phụ trách chính |
|---|---|---|
| BU-DDN | Khối Dân dụng phía Nam | Dân dụng phía Nam và miền Trung; một phần nghỉ dưỡng |
| BU-DDB | Khối Dân dụng phía Bắc | Dân dụng phía Bắc |
| BU01 | Business Unit 01 – Hạ tầng, đầu tư công & FDI | Hạ tầng; phần lớn công nghiệp (nhà máy, kho, trung tâm dữ liệu) |
| UNC | Unicons | Dân dụng, nghỉ dưỡng, D&B; một phần công nghiệp nội địa |
| INTL | Coteccons Quốc tế | Dự án ở nước ngoài |

### 3. dim_segments (15 dòng)
Mảng (`segment_code`) và phân khúc (`sub_segment_code`) công trình.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `sub_segment_code` | VARCHAR(10) PK | Mã phân khúc, ví dụ DD-CT, CN-NM, HT-SB |  |
| `sub_segment_name` | VARCHAR(100) | Tên phân khúc |  |
| `segment_code` | VARCHAR(5) | Mã mảng: DD, CN, HT, ND, QT |  |
| `segment_name` | VARCHAR(50) | Tên mảng: Dân dụng, Công nghiệp, Hạ tầng, Nghỉ dưỡng, Quốc tế |  |

| segment_code / segment_name | sub_segment_code – sub_segment_name |
|---|---|
| DD – Dân dụng | DD-CT Nhà ở cao tầng; DD-KDT Khu đô thị & nhà thấp tầng; DD-VP Văn phòng & trung tâm thương mại; DD-CC Bệnh viện, trường học & công trình công cộng |
| CN – Công nghiệp | CN-NM Nhà máy; CN-KHO Kho logistics; CN-DC Trung tâm dữ liệu |
| HT – Hạ tầng | HT-SB Sân bay & nhà ga; HT-HTKT Hạ tầng kỹ thuật & đô thị; HT-DS Đường sắt & nhà ga đường sắt; HT-TD Công trình trọng điểm (hội nghị, triển lãm) |
| ND – Nghỉ dưỡng | ND-RS Resort & khách sạn; ND-GT Tổ hợp vui chơi giải trí |
| QT – Quốc tế | QT-CN Quốc tế – công nghiệp; QT-DD Quốc tế – dân dụng |

⚠️ `segment_code` không phải khóa chính — `fact_plan_segment_monthly.segment_code` nối logic với `dim_segments.segment_code` (một mã mảng có nhiều dòng phân khúc; lấy DISTINCT trước khi JOIN).

### 4. dim_locations (~24 dòng)
Địa điểm công trình: tỉnh/thành trong nước (địa giới từ 01/07/2025) hoặc quốc gia.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `location_id` | VARCHAR(10) PK | Mã địa điểm |  |
| `province_name` | VARCHAR(60) | Tỉnh/thành theo địa giới từ 01/07/2025, hoặc tên quốc gia/vùng với công trình nước ngoài |  |
| `region` | VARCHAR(20) | Miền Bắc / Miền Trung / Miền Nam / Nước ngoài |  |
| `country` | VARCHAR(50) | Quốc gia |  |
| `merged_from` | VARCHAR(200) | Các tỉnh cũ hợp nhất vào tỉnh này từ 01/07/2025 |  |

`region` ∈ 'Miền Bắc', 'Miền Trung', 'Miền Nam', 'Nước ngoài'. Tỉnh/thành chính: TP.HCM (gồm Bình Dương, Bà Rịa – Vũng Tàu cũ), Hà Nội, Đồng Nai, Bắc Ninh (gồm Bắc Giang), Hưng Yên (gồm Thái Bình), Hải Phòng (gồm Hải Dương), Đà Nẵng (gồm Quảng Nam), Khánh Hòa (gồm Ninh Thuận), Gia Lai (gồm Bình Định), An Giang (gồm Kiên Giang), Tây Ninh (gồm Long An)... Nước ngoài: Đài Loan, Ấn Độ, Kazakhstan, Campuchia, Hoa Kỳ.

### 5. dim_clients (~65 dòng)
Chủ đầu tư (pháp nhân ký hợp đồng, thường là công ty dự án). Tên giả định.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `client_id` | VARCHAR(12) PK | Mã chủ đầu tư |  |
| `client_name` | VARCHAR(200) | Tên pháp nhân chủ đầu tư (công ty dự án) - tên giả định |  |
| `client_group` | VARCHAR(150) | Tập đoàn/nhóm chủ đầu tư; CĐT độc lập thì trùng client_name |  |
| `client_type` | ENUM | Loại chủ đầu tư | BĐS tư nhân / FDI / Nhà nước hoặc đầu tư công / Doanh nghiệp nội địa / Khách hàng quốc tế |
| `origin_country` | VARCHAR(50) | Quốc gia gốc của CĐT (FDI, quốc tế) |  |
| `is_strategic` | TINYINT | 1 nếu thuộc nhóm khách hàng chiến lược |  |
| `relationship_since` | SMALLINT | Năm bắt đầu hợp tác |  |
| `standard_payment_term_days` | SMALLINT | Thời hạn thanh toán tiêu chuẩn sau hóa đơn, ngày |  |
| `credit_rating` | ENUM | Xếp hạng tín nhiệm nội bộ | A / B / C / D |

⚠️ **Một tập đoàn có nhiều pháp nhân CĐT. Phân tích mức độ phụ thuộc, công nợ, hành vi nghiệm thu theo `client_group`.** `is_strategic` = 1: nhóm tập đoàn khách hàng chiến lược.

### 6. dim_consultants (~22 dòng)
Đơn vị tư vấn giám sát (TVGS) / quản lý dự án do CĐT chỉ định. Tên giả định.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `consultant_id` | VARCHAR(10) PK | Mã đơn vị tư vấn |  |
| `consultant_name` | VARCHAR(200) | Tên đơn vị tư vấn giám sát / quản lý dự án - tên giả định |  |
| `consultant_type` | ENUM | Loại tư vấn | Tư vấn giám sát / Quản lý dự án / Tư vấn giám sát và quản lý dự án |
| `origin` | VARCHAR(50) | Trong nước / nước ngoài |  |

⚠️ `dim_projects.consultant_id` là TVGS hiện tại. TVGS xử lý từng hồ sơ nằm ở `fact_payment_applications.consultant_id` — dùng cột này khi phân tích thay đổi TVGS theo thời gian.

### 7. dim_subcontractors (~130 dòng)
Thầu phụ chuyên ngành và tổ đội nhân công. Tên giả định.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `subcontractor_id` | VARCHAR(10) PK | Mã thầu phụ / tổ đội |  |
| `subcontractor_name` | VARCHAR(200) | Tên thầu phụ / tổ đội - tên giả định |  |
| `trade` | VARCHAR(60) | Chuyên ngành: Cọc và nền móng, Kết cấu thép, Cơ điện MEP, Hoàn thiện và mặt dựng, Nhân công kết cấu, Nhân công hoàn thiện... |  |
| `subcontractor_type` | ENUM | Loại | Thầu phụ chuyên ngành / Tổ đội nhân công |
| `home_region` | VARCHAR(20) | Vùng hoạt động chính |  |
| `relationship_since` | SMALLINT | Năm bắt đầu hợp tác |  |

### 8. dim_cost_elements (12 dòng)
Hạng mục chi phí dự án.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `cost_element_code` | VARCHAR(12) PK | Mã hạng mục chi phí |  |
| `cost_element_name` | VARCHAR(100) | Tên hạng mục chi phí |  |
| `cost_group` | ENUM | Nhóm chi phí | Vật tư / Thầu phụ / Nhân công / Máy và thiết bị / Chi phí chung công trường |
| `quantity_unit` | VARCHAR(10) | Đơn vị khối lượng nếu theo dõi khối lượng (tấn, m3) |  |

| cost_element_code | cost_element_name | cost_group |
|---|---|---|
| VT-THEP | Thép xây dựng (tấn) | Vật tư |
| VT-BETONG | Bê tông thương phẩm (m3) | Vật tư |
| VT-HOANTHIEN | Vật tư hoàn thiện | Vật tư |
| VT-KHAC | Vật tư khác (cốp pha, phụ gia, vật tư phụ) | Vật tư |
| TP-COC | Thầu phụ cọc & nền móng | Thầu phụ |
| TP-KCT | Thầu phụ kết cấu thép | Thầu phụ |
| TP-MEP | Thầu phụ cơ điện (MEP) | Thầu phụ |
| TP-HOANTHIEN | Thầu phụ hoàn thiện & mặt dựng | Thầu phụ |
| TP-KHAC | Thầu phụ khác | Thầu phụ |
| NC-TODOI | Nhân công tổ đội | Nhân công |
| MTB | Máy & thiết bị | Máy và thiết bị |
| CPC | Chi phí chung công trường | Chi phí chung công trường |

### 9. dim_projects (~190 dòng)
Dự án / hợp đồng thi công. 1 dòng = 1 hợp đồng. Tên dự án giả định.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `project_id` | VARCHAR(12) PK | Mã dự án dạng {mảng}-{yymm} theo tháng ký, ví dụ CN-2510 |  |
| `project_name` | VARCHAR(255) | Tên dự án / gói thầu - tên giả định |  |
| `contract_no` | VARCHAR(30) | Số hợp đồng |  |
| `client_id` | VARCHAR(12) FK | Chủ đầu tư | → dim_clients |
| `business_unit_id` | VARCHAR(10) FK | Khối/BU phụ trách | → dim_business_units |
| `sub_segment_code` | VARCHAR(10) FK | Phân khúc | → dim_segments |
| `location_id` | VARCHAR(10) FK | Địa điểm | → dim_locations |
| `consultant_id` | VARCHAR(10) FK | Đơn vị TVGS hiện tại | → dim_consultants |
| `contract_type` | ENUM | Loại hợp đồng | Tổng thầu thi công / Thiết kế và thi công (D&B) / Thi công kết cấu / Thi công cơ điện (MEP) / Thi công hạ tầng |
| `pricing_type` | ENUM | Hình thức giá hợp đồng | Trọn gói / Đơn giá cố định / Đơn giá điều chỉnh |
| `price_adjustment_clause` | ENUM | Có điều khoản điều chỉnh giá vật tư chính khi biến động vượt ngưỡng | Có / Không |
| `price_adjustment_threshold_pct` | DECIMAL(5,2) | Ngưỡng biến động giá để được điều chỉnh, % |  |
| `award_date` | DATE | Ngày trúng thầu |  |
| `sign_date` | DATE | Ngày ký hợp đồng |  |
| `start_date` | DATE | Ngày khởi công |  |
| `planned_end_date` | DATE | Ngày hoàn thành theo hợp đồng |  |
| `forecast_end_date` | DATE | Ngày hoàn thành dự báo tại 30/09/2026 |  |
| `actual_end_date` | DATE | Ngày bàn giao thực tế |  |
| `planned_duration_months` | TINYINT | Thời gian thi công theo hợp đồng, tháng |  |
| `original_contract_value_vnd` | DECIMAL(18,0) | Giá trị hợp đồng ký ban đầu, VND |  |
| `budget_gross_margin_pct` | DECIMAL(5,2) | Biên gộp dự toán khi ký, % |  |
| `advance_pct` | DECIMAL(5,2) | Tỷ lệ tạm ứng theo hợp đồng, % |  |
| `retention_pct` | DECIMAL(5,2) | Tỷ lệ giữ lại bảo hành trên mỗi lần thanh toán, % |  |
| `payment_term_days` | SMALLINT | Thời hạn thanh toán sau hóa đơn, ngày |  |
| `contract_currency` | CHAR(3) | Tiền tệ hợp đồng; mọi số tiền trong database đã quy VND |  |
| `project_status` | ENUM | Trạng thái tại 30/09/2026 | Chưa khởi công / Đang thi công / Đã bàn giao / Tạm dừng |
| `cumulative_revenue_before_period_vnd` | DECIMAL(18,0) | Doanh thu lũy kế đã ghi nhận trước 01/07/2024, VND |  |

⚠️ **Giá trị HĐ hiện hành (gồm phụ lục, phát sinh đã duyệt, điều chỉnh giá) KHÔNG nằm ở bảng này — lấy từ `fact_backlog_snapshots.current_contract_value_vnd` hoặc cộng `fact_contract_changes`.**
⚠️ `budget_gross_margin_pct` là mốc so sánh biên thực tế của dự án. `cumulative_revenue_before_period_vnd` là DT đã ghi nhận trước 01/07/2024 (HĐ đang chạy khi bắt đầu kỳ dữ liệu).

---

## FACT TABLES

#### Nhóm: ĐẤU THẦU & HỢP ĐỒNG

### 10. fact_bids ⭐ (~700 dòng)
Pipeline đấu thầu. 1 dòng = 1 gói thầu, trạng thái tại 30/09/2026.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `bid_id` | VARCHAR(15) PK | Mã gói thầu |  |
| `bid_name` | VARCHAR(255) | Tên gói thầu |  |
| `client_id` | VARCHAR(12) FK | Chủ đầu tư mời thầu | → dim_clients |
| `sub_segment_code` | VARCHAR(10) FK | Phân khúc | → dim_segments |
| `location_id` | VARCHAR(10) FK | Địa điểm | → dim_locations |
| `business_unit_id` | VARCHAR(10) FK | Khối/BU chủ trì dự thầu | → dim_business_units |
| `invitation_date` | DATE | Ngày nhận hồ sơ mời thầu |  |
| `submission_date` | DATE | Ngày nộp thầu (NULL nếu đang chuẩn bị) |  |
| `expected_decision_date` | DATE | Ngày dự kiến có kết quả |  |
| `result_date` | DATE | Ngày có kết quả |  |
| `bid_status` | ENUM | Trạng thái tại 30/09/2026 | Đang chuẩn bị / Chờ kết quả / Đang đàm phán / Trúng thầu / Trượt thầu / Hủy hoặc không tham gia |
| `estimated_contract_value_vnd` | DECIMAL(18,0) | Giá trị gói thầu ước tính, VND |  |
| `internal_cost_estimate_vnd` | DECIMAL(18,0) | Dự toán chi phí nội bộ, VND |  |
| `bid_price_vnd` | DECIMAL(18,0) | Giá chào thầu, VND (NULL nếu chưa nộp) |  |
| `markup_pct` | DECIMAL(5,2) | Markup = (giá chào - dự toán nội bộ) / dự toán nội bộ, % |  |
| `planned_duration_months` | TINYINT | Thời gian thi công dự kiến, tháng |  |
| `lost_reason` | VARCHAR(60) | Lý do trượt thầu: Giá / Tiến độ đề xuất / Năng lực, kinh nghiệm tương tự / Điều khoản thanh toán / CĐT hoãn hoặc hủy / Khác |  |
| `project_id` | VARCHAR(12) | Dự án hình thành nếu trúng thầu |  |

⚠️ **Tỷ lệ thắng: chỉ tính gói 'Trúng thầu' + 'Trượt thầu', theo `result_date`. Mặc định theo giá trị `bid_price_vnd`; nêu thêm theo số gói.**
⚠️ Gói 'Đang chuẩn bị' có `submission_date`, `bid_price_vnd`, `markup_pct` NULL — dùng `estimated_contract_value_vnd` khi cộng pipeline.
⚠️ Không có thông tin đơn vị trúng thầu khác hay giá trúng của đối thủ.

### 11. fact_contract_changes (~900 dòng)
Sổ thay đổi giá trị hợp đồng. Mỗi HĐ có đúng 1 dòng 'Ký mới HĐ' (= giá trị ký ban đầu), kể cả HĐ ký trước 7/2024.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `change_id` | INT PK |  |  |
| `project_id` | VARCHAR(12) FK | Dự án | → dim_projects |
| `change_date` | DATE | Ngày ký / ngày hiệu lực của thay đổi |  |
| `change_type` | ENUM | Loại thay đổi giá trị hợp đồng | Ký mới HĐ / Phụ lục mở rộng phạm vi / Phát sinh được duyệt / Điều chỉnh giá vật tư / Giảm phạm vi hoặc thanh lý |
| `change_value_vnd` | DECIMAL(18,0) | Giá trị thay đổi, VND (âm khi giảm phạm vi) |  |
| `variation_order_id` | VARCHAR(20) | Mã phát sinh tương ứng (với loại Phát sinh được duyệt) |  |
| `note` | VARCHAR(255) | Ghi chú |  |

⚠️ **Ký mới = `change_type` = 'Ký mới HĐ'. Các loại khác (phụ lục, phát sinh được duyệt, điều chỉnh giá vật tư, giảm phạm vi) làm thay đổi backlog nhưng không phải ký mới.**
⚠️ Giá trị HĐ hiện hành tại ngày X = SUM(change_value_vnd) với change_date ≤ X.

### 12. fact_variation_orders (~560 dòng)
Phát sinh (VO) Coteccons đề nghị CĐT duyệt. Trạng thái tại 30/09/2026.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `variation_order_id` | VARCHAR(20) PK | Mã phát sinh đề nghị CĐT |  |
| `project_id` | VARCHAR(12) FK | Dự án | → dim_projects |
| `submitted_date` | DATE | Ngày nộp đề nghị phát sinh |  |
| `cause` | ENUM | Nguyên nhân phát sinh | Địa chất hoặc điều kiện hiện trường / Thay đổi thiết kế / Yêu cầu bổ sung của CĐT / Biến động giá / Khác |
| `description` | VARCHAR(255) | Nội dung phát sinh |  |
| `submitted_value_vnd` | DECIMAL(18,0) | Giá trị đề nghị, VND |  |
| `cost_incurred_to_date_vnd` | DECIMAL(18,0) | Chi phí đã bỏ ra cho phần phát sinh tính đến 30/09/2026, VND |  |
| `vo_status` | ENUM | Trạng thái tại 30/09/2026 | Chờ duyệt / Đã duyệt / Duyệt một phần / Từ chối |
| `approved_value_vnd` | DECIMAL(18,0) | Giá trị được duyệt, VND |  |
| `approved_date` | DATE | Ngày CĐT duyệt |  |

⚠️ `submitted_value_vnd` là giá trị toàn bộ phạm vi phát sinh; `cost_incurred_to_date_vnd` là chi phí đã bỏ ra đến 30/09/2026. Phát sinh 'Chờ duyệt' chưa ghi nhận doanh thu.
⚠️ VO được duyệt có dòng tương ứng ở `fact_contract_changes` ('Phát sinh được duyệt', cùng `variation_order_id`) — không cộng hai bảng với nhau.

#### Nhóm: TIẾN ĐỘ, DOANH THU, CHI PHÍ

### 13. fact_project_monthly ⭐ FACT CHÍNH (~3.300 dòng)
Kết quả dự án theo tháng: kế hoạch, sản lượng, doanh thu, giá vốn, LN gộp, SPI. Nguồn chuẩn cho doanh thu và LN gộp theo dự án/mảng/BU/vùng.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `project_id` | VARCHAR(12) PK FK | Dự án | → dim_projects |
| `period_month` | DATE PK | Tháng (ngày đầu tháng) |  |
| `planned_value_vnd` | DECIMAL(18,0) | Giá trị kế hoạch trong tháng (PV), VND |  |
| `earned_value_vnd` | DECIMAL(18,0) | Sản lượng: giá trị khối lượng thực hiện trong tháng thuộc phạm vi đã duyệt (EV), VND |  |
| `vo_pending_work_value_vnd` | DECIMAL(18,0) | Giá trị khối lượng phát sinh đã thi công nhưng CĐT chưa duyệt - không ghi nhận doanh thu, VND |  |
| `price_adjustment_revenue_vnd` | DECIMAL(18,0) | Doanh thu điều chỉnh giá vật tư được ghi nhận trong tháng, VND |  |
| `revenue_recognized_vnd` | DECIMAL(18,0) | Doanh thu ghi nhận = earned_value_vnd + price_adjustment_revenue_vnd, VND |  |
| `actual_cost_vnd` | DECIMAL(18,0) | Giá vốn thực tế trong tháng (gồm chi phí phần phát sinh chờ duyệt), VND |  |
| `budget_cost_vnd` | DECIMAL(18,0) | Chi phí dự toán tương ứng khối lượng thực hiện trong tháng, VND |  |
| `gross_profit_vnd` | DECIMAL(18,0) | LN gộp = revenue_recognized_vnd - actual_cost_vnd, VND |  |
| `cumulative_pv_vnd` | DECIMAL(18,0) | PV lũy kế từ khởi công, VND |  |
| `cumulative_ev_vnd` | DECIMAL(18,0) | EV lũy kế từ khởi công, VND |  |
| `spi_period` | DECIMAL(6,3) | Chỉ số tiến độ trong tháng = EV / PV |  |
| `spi_cumulative` | DECIMAL(6,3) | Chỉ số tiến độ lũy kế = EV lũy kế / PV lũy kế |  |
| `percent_complete_actual` | DECIMAL(5,2) | Tiến độ thực tế lũy kế, % giá trị hợp đồng hiện hành |  |

⚠️ **SUM(revenue_recognized_vnd) theo tháng = fact_corporate_pnl_monthly.net_revenue_vnd; SUM(actual_cost_vnd) = cogs_vnd.**
⚠️ `revenue_recognized_vnd` = `earned_value_vnd` + `price_adjustment_revenue_vnd`. `vo_pending_work_value_vnd` KHÔNG thuộc doanh thu, nhưng chi phí tương ứng đã nằm trong `actual_cost_vnd`.
⚠️ SPI quý = SUM(earned_value_vnd)/SUM(planned_value_vnd) trong quý — không AVG(spi_period).

### 14. fact_project_baseline_plan (~5.500 dòng)
Kế hoạch tiến độ (baseline S-curve) theo tháng của từng HĐ, từ khởi công đến hoàn thành theo kế hoạch — gồm các tháng sau 09/2026.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `project_id` | VARCHAR(12) PK FK | Dự án | → dim_projects |
| `period_month` | DATE PK | Tháng (ngày đầu tháng), từ khởi công đến hoàn thành theo kế hoạch, gồm cả các tháng sau 09/2026 |  |
| `planned_value_vnd` | DECIMAL(18,0) | Giá trị khối lượng kế hoạch trong tháng (PV), VND |  |
| `planned_cumulative_pct` | DECIMAL(5,2) | Tiến độ kế hoạch lũy kế, % giá trị hợp đồng hiện hành |  |

⚠️ **Dùng bảng này cho PV tương lai khi dự báo doanh thu.** Các tháng ≤ 09/2026: `planned_value_vnd` = `fact_project_monthly.planned_value_vnd`.
⚠️ Có tháng tới 2029; `dim_calendar` phủ tới 31/12/2029.

### 15. fact_project_costs (~40.000 dòng)
Chi phí dự án theo tháng × hạng mục × phạm vi (hợp đồng / phát sinh chờ duyệt / phát sinh đã duyệt): dự toán vs thực tế.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `project_id` | VARCHAR(12) PK FK | Dự án | → dim_projects |
| `period_month` | DATE PK | Tháng (ngày đầu tháng) |  |
| `cost_element_code` | VARCHAR(12) PK FK | Hạng mục chi phí | → dim_cost_elements |
| `cost_scope` | ENUM PK | Chi phí thuộc phạm vi hợp đồng hay phần phát sinh | Phạm vi hợp đồng / Phát sinh chờ duyệt / Phát sinh đã duyệt |
| `budget_cost_vnd` | DECIMAL(18,0) | Chi phí dự toán tương ứng khối lượng thực hiện, VND (= 0 với Phát sinh chờ duyệt) |  |
| `actual_cost_vnd` | DECIMAL(18,0) | Chi phí thực tế, VND |  |
| `quantity` | DECIMAL(14,2) | Khối lượng (thép: tấn; bê tông: m3) |  |
| `budget_unit_price_vnd` | DECIMAL(14,2) | Đơn giá dự toán, VND/kg (thép) hoặc VND/m3 (bê tông) |  |
| `actual_unit_price_vnd` | DECIMAL(14,2) | Đơn giá thực tế, VND/kg (thép) hoặc VND/m3 (bê tông) |  |

⚠️ **SUM(actual_cost_vnd) theo dự án × tháng = fact_project_monthly.actual_cost_vnd.** 'Phát sinh chờ duyệt' có `budget_cost_vnd` = 0.
⚠️ `quantity` và đơn giá chỉ có với VT-THEP (tấn; đơn giá VND/kg) và VT-BETONG (m3; đơn giá VND/m3). Đơn giá bình quân = SUM(đơn giá × quantity)/SUM(quantity).
⚠️ Hạng mục NC-TODOI đã gồm chi phí nhân công ở `fact_site_workforce_monthly` — không cộng hai bảng.

### 16. fact_project_forecast_snapshots (~3.300 dòng)
Dự báo kết quả cuối hợp đồng (EAC) do ban chỉ huy / kiểm soát chi phí cập nhật mỗi cuối tháng. SNAPSHOT.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `snapshot_date` | DATE PK | Ngày chốt dự báo - ngày cuối tháng |  |
| `project_id` | VARCHAR(12) PK FK | Dự án | → dim_projects |
| `eac_contract_value_vnd` | DECIMAL(18,0) | Giá trị hợp đồng dự kiến khi hoàn thành, chỉ gồm phạm vi đã duyệt, VND |  |
| `eac_cost_vnd` | DECIMAL(18,0) | Tổng chi phí dự kiến khi hoàn thành (EAC), VND |  |
| `eac_gross_margin_pct` | DECIMAL(5,2) | Biên gộp dự kiến khi hoàn thành, % |  |
| `budget_gross_margin_pct` | DECIMAL(5,2) | Biên gộp dự toán khi ký, % |  |
| `forecast_end_date` | DATE | Ngày hoàn thành dự báo |  |
| `forecast_note` | VARCHAR(255) | Ghi chú của ban chỉ huy / kiểm soát chi phí |  |

⚠️ **SNAPSHOT — luôn lọc một `snapshot_date` (ngày cuối tháng). Xem xu hướng của một dự án: lọc project_id qua nhiều snapshot.** EAC chỉ gồm phạm vi đã duyệt (chưa tính phát sinh chờ duyệt).

### 17. fact_backlog_snapshots (~3.800 dòng)
Backlog theo dự án tại cuối tháng, từ 30/06/2024. SNAPSHOT.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `snapshot_date` | DATE PK | Ngày chốt - ngày cuối tháng |  |
| `project_id` | VARCHAR(12) PK FK | Dự án | → dim_projects |
| `current_contract_value_vnd` | DECIMAL(18,0) | Giá trị hợp đồng hiện hành (ký ban đầu + các thay đổi đến ngày chốt), VND |  |
| `cumulative_revenue_vnd` | DECIMAL(18,0) | Doanh thu lũy kế đã ghi nhận đến ngày chốt, VND |  |
| `backlog_vnd` | DECIMAL(18,0) | Giá trị hợp đồng còn lại chưa thực hiện = current_contract_value_vnd - cumulative_revenue_vnd, VND |  |

⚠️ **SNAPSHOT — luôn lọc một `snapshot_date`. Không SUM qua nhiều tháng.** So sánh hai thời điểm → lấy hai snapshot riêng.
⚠️ Gồm cả HĐ đã ký nhưng chưa khởi công.

#### Nhóm: NGHIỆM THU, PHẢI THU, DÒNG TIỀN

### 18. fact_payment_applications ⭐ (~3.300 dòng)
Hồ sơ đề nghị nghiệm thu – thanh toán theo kỳ khối lượng, từ nộp → ký nghiệm thu → hóa đơn → thanh toán.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `application_id` | VARCHAR(20) PK | Mã hồ sơ đề nghị nghiệm thu - thanh toán |  |
| `project_id` | VARCHAR(12) FK | Dự án | → dim_projects |
| `consultant_id` | VARCHAR(10) FK | Đơn vị TVGS xử lý hồ sơ | → dim_consultants |
| `work_period_month` | DATE | Kỳ khối lượng (ngày đầu tháng) |  |
| `submitted_date` | DATE | Ngày nộp hồ sơ lần đầu |  |
| `submitted_value_vnd` | DECIMAL(18,0) | Giá trị khối lượng đề nghị nghiệm thu, VND |  |
| `application_status` | ENUM | Trạng thái tại 30/09/2026 | Đã ký nghiệm thu / Đang chờ ký / Bị trả lại |
| `return_count` | TINYINT | Số lần hồ sơ bị trả lại |  |
| `last_return_reason` | VARCHAR(100) | Lý do trả hồ sơ gần nhất |  |
| `certified_date` | DATE | Ngày CĐT/TVGS ký nghiệm thu |  |
| `certified_value_vnd` | DECIMAL(18,0) | Giá trị được nghiệm thu, VND |  |
| `days_to_certify` | SMALLINT | Số ngày từ nộp lần đầu đến ký nghiệm thu |  |
| `invoice_date` | DATE | Ngày xuất hóa đơn |  |
| `invoice_value_vnd` | DECIMAL(18,0) | Giá trị hóa đơn chưa VAT, VND |  |
| `advance_recovered_vnd` | DECIMAL(18,0) | Tạm ứng thu hồi trừ vào lần thanh toán này, VND |  |
| `retention_withheld_vnd` | DECIMAL(18,0) | Tiền giữ lại bảo hành, VND |  |
| `payment_due_date` | DATE | Hạn thanh toán |  |
| `paid_date` | DATE | Ngày CĐT thanh toán |  |
| `paid_value_vnd` | DECIMAL(18,0) | Số tiền CĐT đã thanh toán, VND |  |

⚠️ Hồ sơ chưa ký có `certified_date`, `days_to_certify`, `invoice_*`, `paid_*` NULL. Tuổi hồ sơ chưa ký = DATEDIFF('2026-09-30', submitted_date).
⚠️ `invoice_value_vnd`, `paid_value_vnd` chưa gồm VAT; `paid_value_vnd` đã trừ tạm ứng thu hồi và tiền giữ lại bảo hành.

### 19. fact_receivable_snapshots (~4.000 dòng)
Phải thu theo dự án tại cuối tháng, tách theo khâu. SNAPSHOT.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `snapshot_date` | DATE PK | Ngày chốt - ngày cuối tháng |  |
| `project_id` | VARCHAR(12) PK FK | Dự án | → dim_projects |
| `unbilled_wip_vnd` | DECIMAL(18,0) | Khối lượng đã thực hiện, đã ghi nhận doanh thu nhưng chưa được nghiệm thu, VND |  |
| `billed_not_due_vnd` | DECIMAL(18,0) | Đã xuất hóa đơn, chưa đến hạn, VND |  |
| `overdue_1_30_vnd` | DECIMAL(18,0) | Quá hạn 1-30 ngày, VND |  |
| `overdue_31_90_vnd` | DECIMAL(18,0) | Quá hạn 31-90 ngày, VND |  |
| `overdue_over_90_vnd` | DECIMAL(18,0) | Quá hạn trên 90 ngày, VND |  |
| `retention_receivable_vnd` | DECIMAL(18,0) | Tiền giữ lại bảo hành chưa thu, VND |  |
| `total_receivable_vnd` | DECIMAL(18,0) | Tổng phải thu = unbilled + billed + overdue + retention, VND |  |
| `doubtful_provision_vnd` | DECIMAL(18,0) | Số dư dự phòng phải thu khó đòi, VND |  |
| `advance_balance_vnd` | DECIMAL(18,0) | Tạm ứng của CĐT chưa thu hồi (nợ phải trả), VND |  |

⚠️ **SNAPSHOT — luôn lọc một `snapshot_date`.**
⚠️ `unbilled_wip_vnd` = DT đã ghi nhận nhưng chưa được nghiệm thu (chưa xuất hóa đơn) — khác với nợ quá hạn.
⚠️ `advance_balance_vnd` là tạm ứng CĐT chưa thu hồi (nợ phải trả) — không cộng vào phải thu. `doubtful_provision_vnd` là số dư dự phòng, đã nằm trong các khoản quá hạn.

### 20. fact_project_cashflows_monthly (~3.300 dòng)
Dòng tiền thu – chi theo dự án × tháng.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `project_id` | VARCHAR(12) PK FK | Dự án | → dim_projects |
| `period_month` | DATE PK | Tháng (ngày đầu tháng) |  |
| `cash_in_advance_vnd` | DECIMAL(18,0) | Tiền tạm ứng nhận từ CĐT, VND |  |
| `cash_in_progress_vnd` | DECIMAL(18,0) | Tiền thanh toán khối lượng nhận từ CĐT, VND |  |
| `cash_in_retention_vnd` | DECIMAL(18,0) | Tiền giữ lại bảo hành thu hồi, VND |  |
| `cash_out_subcontractors_vnd` | DECIMAL(18,0) | Chi trả thầu phụ chuyên ngành, VND |  |
| `cash_out_materials_vnd` | DECIMAL(18,0) | Chi mua vật tư, VND |  |
| `cash_out_labor_vnd` | DECIMAL(18,0) | Chi trả tổ đội nhân công, VND |  |
| `cash_out_equipment_overhead_vnd` | DECIMAL(18,0) | Chi máy, thiết bị và chi phí chung công trường, VND |  |
| `net_project_cash_flow_vnd` | DECIMAL(18,0) | Dòng tiền thuần của dự án = tổng thu - tổng chi, VND |  |

⚠️ Tổng dòng tiền dự án chưa gồm CP QLDN, lãi vay, thuế, DT tài chính ở cấp doanh nghiệp — không bằng lưu chuyển tiền HĐKD. Lưu chuyển tiền HĐKD hợp nhất: `fact_treasury_monthly.operating_cash_flow_vnd`.

#### Nhóm: THẦU PHỤ, NHÂN CÔNG, AN TOÀN, GIÁ ĐẦU VÀO

### 21. fact_subcontract_packages (~1.100 dòng)
Hợp đồng thầu phụ chuyên ngành theo dự án.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `subcontract_id` | VARCHAR(20) PK | Mã hợp đồng thầu phụ |  |
| `project_id` | VARCHAR(12) FK | Dự án | → dim_projects |
| `subcontractor_id` | VARCHAR(10) FK | Thầu phụ | → dim_subcontractors |
| `cost_element_code` | VARCHAR(12) FK | Hạng mục chi phí tương ứng | → dim_cost_elements |
| `award_date` | DATE | Ngày giao thầu phụ |  |
| `original_value_vnd` | DECIMAL(18,0) | Giá trị hợp đồng thầu phụ ban đầu, VND |  |
| `approved_variation_value_vnd` | DECIMAL(18,0) | Phát sinh thầu phụ đã được Coteccons duyệt lũy kế đến 30/09/2026, VND |  |
| `paid_to_date_vnd` | DECIMAL(18,0) | Đã thanh toán cho thầu phụ lũy kế đến 30/09/2026, VND |  |
| `package_status` | ENUM | Trạng thái | Đang thực hiện / Đã hoàn thành / Chưa triển khai |

### 22. fact_subcontract_variations (~250 dòng)
Phát sinh với thầu phụ đã được Coteccons duyệt.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `sub_variation_id` | VARCHAR(20) PK | Mã phát sinh thầu phụ |  |
| `subcontract_id` | VARCHAR(20) FK | Hợp đồng thầu phụ | → fact_subcontract_packages |
| `project_id` | VARCHAR(12) FK | Dự án | → dim_projects |
| `approved_date` | DATE | Ngày Coteccons duyệt phát sinh cho thầu phụ |  |
| `variation_value_vnd` | DECIMAL(18,0) | Giá trị phát sinh thầu phụ được duyệt, VND |  |
| `reason` | VARCHAR(255) | Nội dung / lý do |  |
| `linked_variation_order_id` | VARCHAR(20) | Phát sinh tương ứng đề nghị CĐT (nếu có) |  |

⚠️ Đối chiếu back-to-back: `linked_variation_order_id` → `fact_variation_orders` (phát sinh tương ứng đề nghị CĐT và trạng thái duyệt).

### 23. fact_site_workforce_monthly (~19.000 dòng)
Nhân công công trường theo dự án × tháng × nghề: kế hoạch vs thực tế.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `project_id` | VARCHAR(12) PK FK | Dự án | → dim_projects |
| `period_month` | DATE PK | Tháng (ngày đầu tháng) |  |
| `trade` | VARCHAR(40) PK | Nghề: Cốp pha, Cốt thép, Bê tông, Xây tô hoàn thiện, Cơ điện MEP, Lao động phổ thông |  |
| `labor_subcontractor_id` | VARCHAR(10) FK | Tổ đội chính cung cấp nhân công | → dim_subcontractors |
| `planned_headcount` | INT | Nhân công kế hoạch bình quân ngày, người |  |
| `actual_headcount` | INT | Nhân công thực tế bình quân ngày, người |  |
| `man_days` | INT | Tổng ngày công trong tháng |  |
| `labor_cost_vnd` | DECIMAL(18,0) | Chi phí nhân công tổ đội, VND (đã nằm trong fact_project_costs hạng mục NC-TODOI) |  |

⚠️ Grain dự án × tháng × nghề — SUM theo nghề trước khi JOIN với bảng dự án × tháng. `actual_headcount` là bình quân ngày; tổng công nhân toàn công ty trong tháng = SUM(actual_headcount).

### 24. fact_site_safety_monthly (~3.300 dòng)
An toàn lao động theo dự án × tháng.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `project_id` | VARCHAR(12) PK FK | Dự án | → dim_projects |
| `period_month` | DATE PK | Tháng (ngày đầu tháng) |  |
| `man_hours` | INT | Tổng giờ công an toàn trong tháng |  |
| `lti_count` | TINYINT | Số sự cố mất ngày công (LTI) |  |
| `recordable_incident_count` | TINYINT | Số sự cố phải ghi nhận |  |
| `near_miss_count` | SMALLINT | Số báo cáo suýt xảy ra sự cố |  |
| `safety_audit_score` | DECIMAL(5,1) | Điểm đánh giá an toàn nội bộ, thang 100 |  |

LTIFR = SUM(lti_count)/SUM(man_hours) × 1.000.000.

### 25. fact_input_prices_monthly (~890 dòng)
Giá vật tư chính và đơn giá ngày công theo tháng × miền (số liệu mô phỏng).

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `period_month` | DATE PK | Tháng (ngày đầu tháng) |  |
| `item_code` | VARCHAR(20) PK | Mã vật tư / nghề |  |
| `region` | VARCHAR(20) PK | Miền Bắc / Miền Trung / Miền Nam |  |
| `item_name` | VARCHAR(100) | Tên vật tư / nghề |  |
| `item_type` | ENUM | Loại | Vật tư / Nhân công |
| `unit` | VARCHAR(20) | VND/kg, VND/m3, VND/tấn, VND/ngày công |  |
| `price_vnd` | DECIMAL(14,2) | Giá bình quân tháng, VND theo đơn vị |  |

| item_code | item_name | unit |
|---|---|---|
| THEP_CB400 | Thép cốt bê tông CB400 | VND/kg |
| BETONG_M350 | Bê tông thương phẩm M350 | VND/m3 |
| XIMANG_PCB40 | Xi măng PCB40 | VND/tấn |
| CAT_XAYDUNG | Cát xây dựng | VND/m3 |
| DA_1X2 | Đá 1x2 | VND/m3 |
| NC_COPPHA, NC_COTTHEP, NC_BETONG, NC_HOANTHIEN, NC_MEP, NC_PHOTHONG | Đơn giá ngày công theo nghề | VND/ngày công |

⚠️ Dự án nước ngoài không có giá trong bảng này.

#### Nhóm: CẤP DOANH NGHIỆP & KẾ HOẠCH

### 26. fact_corporate_pnl_monthly ⭐ (27 dòng)
Kết quả kinh doanh hợp nhất theo tháng. Nguồn chuẩn cho LNST và các dòng dưới LN gộp.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `period_month` | DATE PK | Tháng (ngày đầu tháng) |  |
| `net_revenue_vnd` | DECIMAL(18,0) | Doanh thu thuần hợp nhất = SUM(fact_project_monthly.revenue_recognized_vnd), VND |  |
| `cogs_vnd` | DECIMAL(18,0) | Giá vốn = SUM(fact_project_monthly.actual_cost_vnd), VND |  |
| `gross_profit_vnd` | DECIMAL(18,0) | LN gộp, VND |  |
| `admin_expense_vnd` | DECIMAL(18,0) | Chi phí quản lý doanh nghiệp (gồm chi phí bán hàng và trích lập/hoàn nhập dự phòng phải thu), VND |  |
| `financial_income_vnd` | DECIMAL(18,0) | Doanh thu tài chính (lãi tiền gửi, đầu tư tài chính), VND |  |
| `interest_expense_vnd` | DECIMAL(18,0) | Chi phí lãi vay, VND |  |
| `other_financial_expense_vnd` | DECIMAL(18,0) | Chi phí tài chính khác (phí, chênh lệch tỷ giá), VND |  |
| `other_income_net_vnd` | DECIMAL(18,0) | Thu nhập khác thuần, VND |  |
| `profit_before_tax_vnd` | DECIMAL(18,0) | LN trước thuế, VND |  |
| `income_tax_vnd` | DECIMAL(18,0) | Chi phí thuế TNDN, VND |  |
| `profit_after_tax_vnd` | DECIMAL(18,0) | LNST hợp nhất, VND |  |

⚠️ **LN trước thuế = gross_profit − admin_expense + financial_income − interest_expense − other_financial_expense + other_income_net.**
⚠️ CP QLDN, DT tài chính, lãi vay, thuế không phân bổ xuống dự án / mảng.

### 27. fact_treasury_monthly (27 dòng)
Tiền, nợ vay, lãi suất và lưu chuyển tiền HĐKD hợp nhất theo tháng.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `period_month` | DATE PK | Tháng (ngày đầu tháng) |  |
| `cash_and_deposits_vnd` | DECIMAL(18,0) | Tiền và tiền gửi cuối tháng, VND (số dư) |  |
| `short_term_debt_vnd` | DECIMAL(18,0) | Vay ngắn hạn cuối tháng, VND (số dư) |  |
| `long_term_debt_and_bonds_vnd` | DECIMAL(18,0) | Vay dài hạn và trái phiếu cuối tháng, VND (số dư) |  |
| `total_debt_vnd` | DECIMAL(18,0) | Tổng nợ vay cuối tháng, VND (số dư) |  |
| `avg_interest_rate_pct` | DECIMAL(5,2) | Lãi suất vay bình quân trong tháng, %/năm |  |
| `operating_cash_flow_vnd` | DECIMAL(18,0) | Lưu chuyển tiền thuần từ hoạt động kinh doanh trong tháng, VND (phát sinh) |  |

⚠️ **Cột số dư (`cash_and_deposits_vnd`, `*_debt_*`) là số cuối tháng — lấy tháng cuối kỳ, không SUM. `operating_cash_flow_vnd` là phát sinh trong tháng — SUM theo kỳ.**

### 28. fact_plan_segment_monthly (120 dòng)
Kế hoạch theo mảng × tháng: doanh thu, phần DT từ HĐ ký mới, LN gộp, ký mới.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `plan_version` | VARCHAR(20) PK | KH_NDTC_2026 hoặc KH_NDTC_2027 |  |
| `period_month` | DATE PK | Tháng (ngày đầu tháng) |  |
| `segment_code` | VARCHAR(5) PK | Mã mảng: DD, CN, HT, ND, QT |  |
| `revenue_plan_vnd` | DECIMAL(18,0) | Doanh thu kế hoạch, VND |  |
| `revenue_from_new_contracts_plan_vnd` | DECIMAL(18,0) | Phần doanh thu kế hoạch dự kiến đến từ hợp đồng ký mới trong niên độ, VND |  |
| `gross_profit_plan_vnd` | DECIMAL(18,0) | LN gộp kế hoạch, VND |  |
| `new_contract_plan_vnd` | DECIMAL(18,0) | Giá trị ký mới kế hoạch, VND |  |

⚠️ **Luôn lọc `plan_version`.** `revenue_from_new_contracts_plan_vnd` là phần của `revenue_plan_vnd` (không cộng thêm).

### 29. fact_plan_corporate_quarterly (8 dòng)
Kế hoạch hợp nhất theo quý niên độ, đến LNST.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `plan_version` | VARCHAR(20) PK | KH_NDTC_2026 hoặc KH_NDTC_2027 |  |
| `fiscal_year` | SMALLINT PK | Niên độ tài chính |  |
| `fiscal_quarter` | TINYINT PK | Quý theo niên độ 1-4 |  |
| `revenue_plan_vnd` | DECIMAL(18,0) | Doanh thu kế hoạch, VND |  |
| `gross_profit_plan_vnd` | DECIMAL(18,0) | LN gộp kế hoạch, VND |  |
| `admin_expense_plan_vnd` | DECIMAL(18,0) | Chi phí QLDN kế hoạch, VND |  |
| `financial_income_plan_vnd` | DECIMAL(18,0) | Doanh thu tài chính kế hoạch, VND |  |
| `interest_expense_plan_vnd` | DECIMAL(18,0) | Chi phí lãi vay kế hoạch, VND |  |
| `other_income_plan_vnd` | DECIMAL(18,0) | Thu nhập khác thuần kế hoạch, VND |  |
| `profit_before_tax_plan_vnd` | DECIMAL(18,0) | LN trước thuế kế hoạch, VND |  |
| `income_tax_plan_vnd` | DECIMAL(18,0) | Thuế TNDN kế hoạch, VND |  |
| `profit_after_tax_plan_vnd` | DECIMAL(18,0) | LNST kế hoạch, VND |  |

⚠️ **Luôn lọc `plan_version`.** KH_NDTC_2027: DT 42.000 tỷ, LNST 1.050 tỷ. KH_NDTC_2026: DT 30.000 tỷ, LNST 700 tỷ.

### 30. Metadata
`_meta_tables`, `_meta_columns`, `_meta_kpi`, `_meta_glossary` — mô tả bảng, cột, công thức KPI và thuật ngữ ngành xây dựng. Dùng khi cần xác nhận ý nghĩa một cột hoặc thuật ngữ.

---

## SQL TEMPLATES

Các template dưới đây chạy được nguyên văn trên `coteccons_demo`. Đổi khoảng thời gian, `snapshot_date`, `plan_version` theo câu hỏi.


### T1. Doanh thu, LN gộp, biên gộp theo mảng × quý niên độ
```sql
-- Dùng cho câu tổng quan; so cùng kỳ = cùng fiscal_quarter của fiscal_year trước
SELECT c.fiscal_year, c.fiscal_quarter, s.segment_name,
       SUM(m.revenue_recognized_vnd)/1e9                                        AS dt_ty,
       SUM(m.gross_profit_vnd)/1e9                                              AS ln_gop_ty,
       SUM(m.gross_profit_vnd)/NULLIF(SUM(m.revenue_recognized_vnd),0)*100      AS bien_gop_pct
FROM fact_project_monthly m
JOIN dim_projects p  ON p.project_id = m.project_id
JOIN dim_segments s  ON s.sub_segment_code = p.sub_segment_code
JOIN dim_calendar c  ON c.date_key = m.period_month
WHERE m.period_month BETWEEN '2024-07-01' AND '2026-09-01'
GROUP BY c.fiscal_year, c.fiscal_quarter, s.segment_name
ORDER BY c.fiscal_year, c.fiscal_quarter, dt_ty DESC;
```

### T2. Thực hiện vs kế hoạch hợp nhất theo quý NĐTC 2027 (đến LNST)
```sql
WITH thuc_hien AS (
  SELECT c.fiscal_year, c.fiscal_quarter,
         SUM(p.net_revenue_vnd) AS dt, SUM(p.gross_profit_vnd) AS lng, SUM(p.profit_after_tax_vnd) AS lnst
  FROM fact_corporate_pnl_monthly p
  JOIN dim_calendar c ON c.date_key = p.period_month
  GROUP BY c.fiscal_year, c.fiscal_quarter
),
ke_hoach AS (
  SELECT fiscal_year, fiscal_quarter, revenue_plan_vnd AS dt_kh, profit_after_tax_plan_vnd AS lnst_kh
  FROM fact_plan_corporate_quarterly
  WHERE plan_version = 'KH_NDTC_2027'
)
SELECT k.fiscal_year, k.fiscal_quarter,
       t.dt/1e9 AS dt_ty, k.dt_kh/1e9 AS dt_kh_ty, t.dt/k.dt_kh*100 AS dat_kh_quy_pct,
       t.lnst/1e9 AS lnst_ty, k.lnst_kh/1e9 AS lnst_kh_ty,
       (SELECT SUM(revenue_plan_vnd) FROM fact_plan_corporate_quarterly WHERE plan_version='KH_NDTC_2027')/1e9 AS dt_kh_nam_ty,
       (SELECT SUM(profit_after_tax_plan_vnd) FROM fact_plan_corporate_quarterly WHERE plan_version='KH_NDTC_2027')/1e9 AS lnst_kh_nam_ty
FROM ke_hoach k
LEFT JOIN thuc_hien t ON t.fiscal_year = k.fiscal_year AND t.fiscal_quarter = k.fiscal_quarter
ORDER BY k.fiscal_quarter;
```

### T3. Dự án hụt LN gộp so với dự toán trong một quý, và chi phí theo hạng mục của các dự án hụt nhiều nhất
```sql
SELECT p.project_id, p.project_name, s.segment_name, cl.client_group, p.pricing_type, p.price_adjustment_clause,
       SUM(m.revenue_recognized_vnd)/1e9                                          AS dt_ty,
       p.budget_gross_margin_pct                                                  AS bien_du_toan_pct,
       SUM(m.gross_profit_vnd)/NULLIF(SUM(m.revenue_recognized_vnd),0)*100        AS bien_thuc_te_pct,
       (SUM(m.revenue_recognized_vnd)*p.budget_gross_margin_pct/100 - SUM(m.gross_profit_vnd))/1e9 AS ln_gop_hut_ty
FROM fact_project_monthly m
JOIN dim_projects p  ON p.project_id = m.project_id
JOIN dim_segments s  ON s.sub_segment_code = p.sub_segment_code
JOIN dim_clients cl  ON cl.client_id = p.client_id
WHERE m.period_month BETWEEN '2026-07-01' AND '2026-09-01'
GROUP BY p.project_id, p.project_name, s.segment_name, cl.client_group, p.pricing_type, p.price_adjustment_clause, p.budget_gross_margin_pct
HAVING SUM(m.revenue_recognized_vnd) > 0
ORDER BY ln_gop_hut_ty DESC
LIMIT 15;

WITH top_hut AS (
  SELECT m.project_id
  FROM fact_project_monthly m JOIN dim_projects p ON p.project_id = m.project_id
  WHERE m.period_month BETWEEN '2026-07-01' AND '2026-09-01'
  GROUP BY m.project_id, p.budget_gross_margin_pct
  ORDER BY SUM(m.revenue_recognized_vnd)*p.budget_gross_margin_pct/100 - SUM(m.gross_profit_vnd) DESC
  LIMIT 5
)
SELECT pc.project_id, ce.cost_group, ce.cost_element_name, pc.cost_scope,
       SUM(pc.budget_cost_vnd)/1e9                              AS du_toan_ty,
       SUM(pc.actual_cost_vnd)/1e9                              AS thuc_te_ty,
       (SUM(pc.actual_cost_vnd) - SUM(pc.budget_cost_vnd))/1e9  AS vuot_ty,
       SUM(pc.quantity)                                         AS khoi_luong,
       SUM(pc.actual_unit_price_vnd*pc.quantity)/NULLIF(SUM(pc.quantity),0) AS don_gia_thuc_te,
       SUM(pc.budget_unit_price_vnd*pc.quantity)/NULLIF(SUM(pc.quantity),0) AS don_gia_du_toan
FROM fact_project_costs pc
JOIN top_hut th           ON th.project_id = pc.project_id
JOIN dim_cost_elements ce ON ce.cost_element_code = pc.cost_element_code
WHERE pc.period_month BETWEEN '2026-07-01' AND '2026-09-01'
GROUP BY pc.project_id, ce.cost_group, ce.cost_element_name, pc.cost_scope
ORDER BY pc.project_id, vuot_ty DESC;
```

### T4. Phát sinh đang chờ CĐT duyệt, đối chiếu phát sinh đã duyệt cho thầu phụ (back-to-back)
```sql
SELECT vo.project_id, p.project_name, vo.variation_order_id, vo.submitted_date, vo.cause, vo.vo_status,
       vo.submitted_value_vnd/1e9        AS de_nghi_ty,
       vo.cost_incurred_to_date_vnd/1e9  AS chi_phi_da_bo_ty,
       DATEDIFF('2026-09-30', vo.submitted_date) AS so_ngay_cho,
       (SELECT SUM(sv.variation_value_vnd) FROM fact_subcontract_variations sv
         WHERE sv.linked_variation_order_id = vo.variation_order_id)/1e9 AS phat_sinh_thau_phu_da_duyet_ty
FROM fact_variation_orders vo
JOIN dim_projects p ON p.project_id = vo.project_id
WHERE vo.vo_status IN ('Chờ duyệt','Duyệt một phần')
ORDER BY vo.submitted_value_vnd DESC
LIMIT 20;
```

### T5. Backlog tại một ngày theo mảng và tập đoàn CĐT; ký mới và các thay đổi HĐ theo quý
```sql
SELECT s.segment_name, cl.client_group,
       SUM(b.backlog_vnd)/1e9 AS backlog_ty,
       SUM(b.backlog_vnd)/(SELECT SUM(backlog_vnd) FROM fact_backlog_snapshots WHERE snapshot_date='2026-09-30')*100 AS ty_trong_pct
FROM fact_backlog_snapshots b
JOIN dim_projects p ON p.project_id = b.project_id
JOIN dim_segments s ON s.sub_segment_code = p.sub_segment_code
JOIN dim_clients cl ON cl.client_id = p.client_id
WHERE b.snapshot_date = '2026-09-30'
GROUP BY s.segment_name, cl.client_group
ORDER BY backlog_ty DESC
LIMIT 20;

SELECT c.fiscal_year, c.fiscal_quarter, s.segment_name, cc.change_type,
       SUM(cc.change_value_vnd)/1e9 AS gia_tri_ty, COUNT(*) AS so_dong
FROM fact_contract_changes cc
JOIN dim_projects p ON p.project_id = cc.project_id
JOIN dim_segments s ON s.sub_segment_code = p.sub_segment_code
JOIN dim_calendar c ON c.date_key = cc.change_date
GROUP BY c.fiscal_year, c.fiscal_quarter, s.segment_name, cc.change_type
ORDER BY c.fiscal_year, c.fiscal_quarter, s.segment_name, cc.change_type;
```

### T6. Dự báo DT phần còn lại của niên độ theo baseline × SPI quý gần nhất, theo dự án
```sql
WITH spi_q AS (
  SELECT project_id,
         SUM(earned_value_vnd)/NULLIF(SUM(planned_value_vnd),0) AS spi_quy
  FROM fact_project_monthly
  WHERE period_month BETWEEN '2026-07-01' AND '2026-09-01'
  GROUP BY project_id
),
pv_con_lai AS (
  SELECT project_id, SUM(planned_value_vnd) AS pv_q2_q4
  FROM fact_project_baseline_plan
  WHERE period_month BETWEEN '2026-10-01' AND '2027-06-01'
  GROUP BY project_id
)
SELECT p.project_id, p.project_name, l.region, s.segment_name,
       q.spi_quy,
       v.pv_q2_q4/1e9                                        AS pv_q2_q4_ty,
       v.pv_q2_q4*LEAST(COALESCE(q.spi_quy,1),1.05)/1e9      AS du_bao_theo_spi_ty,
       v.pv_q2_q4*(1-LEAST(COALESCE(q.spi_quy,1),1.05))/1e9  AS chenh_lech_ty
FROM pv_con_lai v
JOIN dim_projects p  ON p.project_id = v.project_id
JOIN dim_locations l ON l.location_id = p.location_id
JOIN dim_segments s  ON s.sub_segment_code = p.sub_segment_code
LEFT JOIN spi_q q    ON q.project_id = v.project_id
ORDER BY chenh_lech_ty DESC
LIMIT 20;
```

### T7. Tốc độ ghi nhận DT của HĐ ký mới theo mảng (HĐ ký trong một quý đã ghi nhận bao nhiêu % sau N tháng)
```sql
-- Ví dụ: HĐ ký 10–12/2025, DT ghi nhận đến hết 6/2026
SELECT s.segment_name,
       COUNT(*)                                                   AS so_hd,
       SUM(p.original_contract_value_vnd)/1e9                     AS gia_tri_ky_ty,
       SUM(COALESCE(r.dt,0))/1e9                                  AS dt_den_30_6_2026_ty,
       SUM(COALESCE(r.dt,0))/SUM(p.original_contract_value_vnd)*100 AS ty_le_ghi_nhan_pct
FROM dim_projects p
JOIN dim_segments s ON s.sub_segment_code = p.sub_segment_code
LEFT JOIN (SELECT project_id, SUM(revenue_recognized_vnd) AS dt
           FROM fact_project_monthly
           WHERE period_month <= '2026-06-01'
           GROUP BY project_id) r ON r.project_id = p.project_id
WHERE p.sign_date BETWEEN '2025-10-01' AND '2025-12-31'
GROUP BY s.segment_name;
```

### T8. Phải thu theo tập đoàn CĐT tại hai thời điểm
```sql
SELECT cl.client_group, r.snapshot_date,
       SUM(r.unbilled_wip_vnd)/1e9 AS chua_nghiem_thu_ty,
       SUM(r.billed_not_due_vnd + r.overdue_1_30_vnd + r.overdue_31_90_vnd + r.overdue_over_90_vnd)/1e9 AS da_xuat_hd_ty,
       SUM(r.overdue_31_90_vnd + r.overdue_over_90_vnd)/1e9 AS qua_han_tren_30_ngay_ty,
       SUM(r.retention_receivable_vnd)/1e9 AS giu_lai_bao_hanh_ty,
       SUM(r.total_receivable_vnd)/1e9 AS tong_phai_thu_ty
FROM fact_receivable_snapshots r
JOIN dim_projects p ON p.project_id = r.project_id
JOIN dim_clients cl ON cl.client_id = p.client_id
WHERE r.snapshot_date IN ('2026-06-30','2026-09-30')
GROUP BY cl.client_group, r.snapshot_date
ORDER BY cl.client_group, r.snapshot_date;
```

### T9. Nghiệm thu theo tập đoàn CĐT × TVGS × tháng nộp; tuổi hồ sơ chưa ký tại 30/09/2026
```sql
SELECT cl.client_group, cs.consultant_name,
       DATE_FORMAT(a.submitted_date,'%Y-%m') AS thang_nop,
       COUNT(*) AS so_ho_so,
       SUM(a.submitted_value_vnd)/1e9 AS gia_tri_nop_ty,
       AVG(a.days_to_certify) AS so_ngay_ky_bq,
       SUM(a.return_count > 0)/COUNT(*)*100 AS ty_le_bi_tra_pct,
       SUM(CASE WHEN a.application_status <> 'Đã ký nghiệm thu' THEN a.submitted_value_vnd ELSE 0 END)/1e9 AS chua_ky_ty,
       AVG(CASE WHEN a.application_status <> 'Đã ký nghiệm thu' THEN DATEDIFF('2026-09-30', a.submitted_date) END) AS tuoi_hs_chua_ky_bq
FROM fact_payment_applications a
JOIN dim_projects p     ON p.project_id = a.project_id
JOIN dim_clients cl     ON cl.client_id = p.client_id
JOIN dim_consultants cs ON cs.consultant_id = a.consultant_id
WHERE a.submitted_date >= '2026-01-01'
GROUP BY cl.client_group, cs.consultant_name, thang_nop
ORDER BY cl.client_group, thang_nop;

SELECT a.last_return_reason, COUNT(*) AS so_ho_so, SUM(a.submitted_value_vnd)/1e9 AS gia_tri_ty
FROM fact_payment_applications a
WHERE a.return_count > 0 AND a.submitted_date >= '2026-07-01'
GROUP BY a.last_return_reason
ORDER BY so_ho_so DESC;
```

### T10. Dòng tiền dự án theo quý và lưu chuyển tiền HĐKD, lãi vay, nợ vay
```sql
SELECT c.fiscal_year, c.fiscal_quarter,
       SUM(f.cash_in_advance_vnd)/1e9 AS tam_ung_ty,
       SUM(f.cash_in_progress_vnd)/1e9 AS thu_khoi_luong_ty,
       SUM(f.cash_out_subcontractors_vnd + f.cash_out_materials_vnd + f.cash_out_labor_vnd + f.cash_out_equipment_overhead_vnd)/1e9 AS tong_chi_ty,
       SUM(f.net_project_cash_flow_vnd)/1e9 AS dong_tien_du_an_ty
FROM fact_project_cashflows_monthly f
JOIN dim_calendar c ON c.date_key = f.period_month
GROUP BY c.fiscal_year, c.fiscal_quarter
ORDER BY c.fiscal_year, c.fiscal_quarter;

WITH q AS (
  SELECT c.fiscal_year, c.fiscal_quarter, MAX(p.period_month) AS thang_cuoi,
         SUM(p.net_revenue_vnd) AS dt, SUM(p.gross_profit_vnd) AS lng, SUM(p.admin_expense_vnd) AS cpql,
         SUM(p.financial_income_vnd) AS dttc, SUM(p.interest_expense_vnd) AS lai_vay, SUM(p.profit_after_tax_vnd) AS lnst
  FROM fact_corporate_pnl_monthly p
  JOIN dim_calendar c ON c.date_key = p.period_month
  GROUP BY c.fiscal_year, c.fiscal_quarter
),
cf AS (
  SELECT c.fiscal_year, c.fiscal_quarter, SUM(t.operating_cash_flow_vnd) AS cfo
  FROM fact_treasury_monthly t
  JOIN dim_calendar c ON c.date_key = t.period_month
  GROUP BY c.fiscal_year, c.fiscal_quarter
)
SELECT q.fiscal_year, q.fiscal_quarter,
       q.dt/1e9 AS dt_ty, q.lng/1e9 AS ln_gop_ty, q.cpql/1e9 AS cpql_ty, q.dttc/1e9 AS dt_tai_chinh_ty,
       q.lai_vay/1e9 AS lai_vay_ty, q.lai_vay/NULLIF(q.lng,0)*100 AS lai_vay_tren_ln_gop_pct,
       q.lnst/1e9 AS lnst_ty,
       t.total_debt_vnd/1e9 AS no_vay_cuoi_quy_ty, t.avg_interest_rate_pct,
       cf.cfo/1e9 AS luu_chuyen_tien_hdkd_ty
FROM q
LEFT JOIN fact_treasury_monthly t ON t.period_month = q.thang_cuoi
LEFT JOIN cf ON cf.fiscal_year = q.fiscal_year AND cf.fiscal_quarter = q.fiscal_quarter
ORDER BY q.fiscal_year, q.fiscal_quarter;
```

### T11. Đấu thầu: tỷ lệ thắng, markup, lý do trượt theo phân khúc × giai đoạn; pipeline đang mở
```sql
SELECT s.segment_name, s.sub_segment_name,
       CASE WHEN b.result_date < '2026-04-01' THEN 'Trước 04/2026' ELSE 'Từ 04/2026' END AS giai_doan,
       COUNT(*) AS so_goi_co_ket_qua,
       SUM(b.bid_status='Trúng thầu') AS so_goi_trung,
       SUM(CASE WHEN b.bid_status='Trúng thầu' THEN b.bid_price_vnd ELSE 0 END)/SUM(b.bid_price_vnd)*100 AS ty_le_thang_gia_tri_pct,
       AVG(b.markup_pct) AS markup_bq_pct,
       SUM(b.bid_status='Trượt thầu' AND b.lost_reason='Giá')/NULLIF(SUM(b.bid_status='Trượt thầu'),0)*100 AS truot_vi_gia_pct
FROM fact_bids b
JOIN dim_segments s ON s.sub_segment_code = b.sub_segment_code
WHERE b.bid_status IN ('Trúng thầu','Trượt thầu')
  AND b.result_date BETWEEN '2025-07-01' AND '2026-09-30'
GROUP BY s.segment_name, s.sub_segment_name, giai_doan
ORDER BY s.segment_name, s.sub_segment_name, giai_doan;

SELECT s.segment_name, s.sub_segment_name, b.bid_status,
       COUNT(*) AS so_goi,
       SUM(b.estimated_contract_value_vnd)/1e9 AS gia_tri_ty,
       SUM(CASE WHEN b.expected_decision_date <= '2026-12-31' THEN b.estimated_contract_value_vnd ELSE 0 END)/1e9 AS co_ket_qua_trong_q2_ty,
       SUM(CASE WHEN b.expected_decision_date <= '2027-03-31' THEN b.estimated_contract_value_vnd ELSE 0 END)/1e9 AS co_ket_qua_truoc_31_3_ty
FROM fact_bids b
JOIN dim_segments s ON s.sub_segment_code = b.sub_segment_code
WHERE b.bid_status IN ('Đang chuẩn bị','Chờ kết quả','Đang đàm phán')
GROUP BY s.segment_name, s.sub_segment_name, b.bid_status
ORDER BY gia_tri_ty DESC;
```

### T12. Quan hệ markup ↔ tỷ lệ thắng theo dải markup (dùng cho what-if về giá chào)
```sql
SELECT b.sub_segment_code,
       CASE WHEN b.markup_pct < 5.5 THEN '< 5,5%'
            WHEN b.markup_pct < 6.5 THEN '5,5–6,5%'
            WHEN b.markup_pct < 7.5 THEN '6,5–7,5%'
            ELSE '≥ 7,5%' END AS dai_markup,
       COUNT(*) AS so_goi,
       SUM(b.bid_status='Trúng thầu')/COUNT(*)*100 AS ty_le_thang_so_goi_pct,
       SUM(CASE WHEN b.bid_status='Trúng thầu' THEN b.bid_price_vnd ELSE 0 END)/SUM(b.bid_price_vnd)*100 AS ty_le_thang_gia_tri_pct
FROM fact_bids b
WHERE b.bid_status IN ('Trúng thầu','Trượt thầu')
GROUP BY b.sub_segment_code, dai_markup
ORDER BY b.sub_segment_code, dai_markup;
```

### T13. Nhân công kế hoạch vs thực tế theo miền × tháng × nghề, so với đơn giá ngày công thị trường
```sql
SELECT l.region, w.period_month, w.trade,
       SUM(w.planned_headcount) AS ke_hoach, SUM(w.actual_headcount) AS thuc_te,
       SUM(w.actual_headcount)/NULLIF(SUM(w.planned_headcount),0)*100 AS dat_pct,
       SUM(w.labor_cost_vnd)/NULLIF(SUM(w.man_days),0) AS don_gia_ngay_cong_bq,
       (SELECT AVG(ip.price_vnd) FROM fact_input_prices_monthly ip
         WHERE ip.period_month = w.period_month AND ip.region = l.region AND ip.item_type = 'Nhân công') AS don_gia_thi_truong_bq
FROM fact_site_workforce_monthly w
JOIN dim_projects p  ON p.project_id = w.project_id
JOIN dim_locations l ON l.location_id = p.location_id
WHERE w.period_month BETWEEN '2026-01-01' AND '2026-09-01' AND l.region <> 'Nước ngoài'
GROUP BY l.region, w.period_month, w.trade
ORDER BY l.region, w.period_month, w.trade;
```

---

## JOIN WARNINGS

1. **Niên độ:** luôn quy đổi kỳ qua `dim_calendar` (`fiscal_year`, `fiscal_quarter`). "Quý 1 niên độ 2027" = 7–9/2026, không phải 1–3/2027.
2. **Bảng SNAPSHOT** (`fact_backlog_snapshots`, `fact_receivable_snapshots`, `fact_project_forecast_snapshots`): luôn `WHERE snapshot_date = 'YYYY-MM-DD'` (ngày cuối tháng). Không SUM qua nhiều snapshot. So sánh hai thời điểm → lấy hai snapshot riêng.
3. **Ngày tháng:** bảng theo tháng dùng `period_month` = ngày đầu tháng (2026-09-01 là tháng 9/2026); bảng snapshot dùng ngày cuối tháng (2026-09-30). Không JOIN trực tiếp `period_month` với `snapshot_date`.
4. **fact_project_costs ↔ fact_project_monthly:** khác grain (thêm hạng mục × phạm vi). Aggregate chi phí lên dự án × tháng trước khi JOIN, nếu không sẽ nhân dòng doanh thu.
5. **fact_site_workforce_monthly:** grain dự án × tháng × nghề. SUM theo nghề trước khi JOIN với dự án × tháng. `labor_cost_vnd` đã nằm trong NC-TODOI của `fact_project_costs` — không cộng hai nguồn.
6. **Doanh thu vs sản lượng vs phát sinh chờ duyệt:** `revenue_recognized_vnd` = `earned_value_vnd` + `price_adjustment_revenue_vnd`. `vo_pending_work_value_vnd` không phải doanh thu. Không cộng `planned_value_vnd` với doanh thu.
7. **LNST và các dòng dưới LN gộp** chỉ có ở `fact_corporate_pnl_monthly`. Không phân bổ hay tự tính LNST từ bảng dự án.
8. **Ký mới:** chỉ `change_type` = 'Ký mới HĐ'. Các loại thay đổi khác không phải ký mới. Phát sinh được duyệt xuất hiện ở cả `fact_variation_orders` và `fact_contract_changes` — không cộng hai bảng.
9. **Giá trị HĐ hiện hành:** không có ở `dim_projects` (chỉ có giá trị ký ban đầu). Dùng `fact_backlog_snapshots.current_contract_value_vnd` hoặc SUM `fact_contract_changes` đến ngày cần xem.
10. **Baseline tương lai:** PV các tháng sau 09/2026 chỉ có ở `fact_project_baseline_plan`. `fact_project_monthly` chỉ có đến 09/2026.
11. **Phải thu:** `advance_balance_vnd` là nợ phải trả (tạm ứng chưa thu hồi) — không cộng vào phải thu. `total_receivable_vnd` đã gồm chưa nghiệm thu, đã xuất hóa đơn, quá hạn và giữ lại bảo hành.
12. **CĐT và tập đoàn:** nhiều `client_id` thuộc cùng `client_group`. Phân tích theo tập đoàn thì GROUP BY `client_group`.
13. **Đấu thầu:** tỷ lệ thắng loại gói đang mở và 'Hủy hoặc không tham gia' khỏi mẫu số. Gói 'Đang chuẩn bị' có `bid_price_vnd` NULL.
14. **fact_treasury_monthly:** cột số dư lấy tháng cuối kỳ; `operating_cash_flow_vnd` SUM theo kỳ.
15. **fact_plan_*:** luôn lọc `plan_version`. `fact_plan_segment_monthly.segment_code` nối với `dim_segments.segment_code` (không phải khóa chính) — dùng DISTINCT segment_code, segment_name.
16. **Dự án nước ngoài:** số tiền đã quy VND; `dim_projects.contract_currency` là tiền tệ gốc. Không có giá đầu vào và nhân công theo miền cho dự án nước ngoài.
17. **Hợp đồng ký trước 07/2024:** có dòng 'Ký mới HĐ' với ngày trước 2024-07-01 (ngoài `dim_calendar`); DT trước kỳ ở `dim_projects.cumulative_revenue_before_period_vnd`.

---

## ĐƠN VỊ TIỀN TỆ

| Bảng | Cột | Đơn vị |
|---|---|---|
| Mọi bảng fact, dim_projects | các cột `*_vnd` | VND |
| fact_project_costs | `budget_unit_price_vnd`, `actual_unit_price_vnd` | VND/kg (thép), VND/m3 (bê tông) |
| fact_project_costs | `quantity` | tấn (thép), m3 (bê tông) |
| fact_input_prices_monthly | `price_vnd` | theo cột `unit`: VND/kg, VND/m3, VND/tấn, VND/ngày công |
| fact_bids | `markup_pct` | % trên dự toán chi phí nội bộ |
| dim_projects | `budget_gross_margin_pct`, `advance_pct`, `retention_pct` | % |
| fact_project_forecast_snapshots | `eac_gross_margin_pct` | % |
| fact_treasury_monthly | `avg_interest_rate_pct` | %/năm |
| fact_project_monthly | `spi_period`, `spi_cumulative` | chỉ số (1,000 = đúng tiến độ) |
| fact_site_safety_monthly | `man_hours` | giờ công |

Format hiển thị cho lãnh đạo:
- ≥ 1 tỷ: "X.XXX tỷ" hoặc "X,X tỷ" (ví dụ 11.269 tỷ; 92,3 tỷ)
- < 1 tỷ: "XXX triệu"
- Phần trăm: 1 chữ số thập phân (biên gộp có thể 2 chữ số); thay đổi biên dùng "điểm %"
- SPI: 2 chữ số thập phân (0,84)
- Thép: tấn; đơn giá thép: đ/kg
