# DATA SCHEMA — DỆT TRẦN HIỆP THÀNH (THT TEXTILE) BI
## Database: tht_textile_demo (MySQL 8.0, utf8mb4_unicode_ci)
## Phạm vi: 01/01/2025 – 31/10/2026 (22 tháng) | "Hiện tại" = 31/10/2026
## Đơn hàng mở có ngày cam kết đến 03/2027 | Forecast brand (snapshot 15/10/2026): 11/2026 – 03/2027 | Kế hoạch: KH_2026

---

## SƠ ĐỒ QUAN HỆ

```
dim_calendar (date_key PK; month_start_date dùng JOIN với period_month)
  └── mọi cột ngày / period_month của các bảng fact (không khai báo FK)

dim_product_lines (product_line_code PK)
  ├── dim_articles.product_line_code
  ├── fact_developments.product_line_code
  ├── fact_order_inquiries.product_line_code
  ├── fact_sales_orders.product_line_code
  ├── fact_sales_invoices.product_line_code
  ├── fact_claims.product_line_code
  ├── fact_dye_batches.product_line_code
  ├── fact_quality_daily.product_line_code
  ├── fact_weaving_daily.product_line_code
  ├── fact_cost_monthly.product_line_code
  ├── fact_plan_product_monthly.product_line_code
  └── fact_brand_forecasts.product_line_code

dim_dye_lines (dye_line_id PK)
  ├── dim_machines.dye_line_id
  ├── dim_articles.default_dye_line_id
  ├── fact_dye_batches.dye_line_id
  ├── fact_quality_daily.dye_line_id
  └── fact_capacity_monthly.unit_id  (giá trị DL1-DL4 khi process = 'Nhuộm'; không khai báo FK)

dim_machines (machine_id PK)
  ├── fact_dye_batches.machine_id
  └── fact_weaving_daily.machine_id

dim_articles (article_code PK)
  ├── fact_developments.article_code (có thể NULL)
  ├── fact_order_inquiries.article_code (có thể NULL)
  ├── fact_sales_orders.article_code
  ├── fact_sales_invoices.article_code
  └── fact_dye_batches.article_code

dim_brands (brand_id PK)
  ├── fact_developments.brand_id
  ├── fact_lab_dips.brand_id
  ├── fact_order_inquiries.brand_id
  ├── fact_sales_orders.brand_id
  ├── fact_sales_invoices.brand_id
  ├── fact_claims.brand_id
  ├── fact_brand_forecasts.brand_id
  └── fact_plan_brand_monthly.plan_brand_key  (= brand_id của brand trọng điểm, hoặc 'KHAC'; không khai báo FK)

dim_customers (customer_id PK)
  ├── fact_order_inquiries.customer_id
  ├── fact_sales_orders.customer_id
  ├── fact_sales_invoices.customer_id
  ├── fact_claims.customer_id
  └── fact_ar_snapshots.customer_id

dim_chemical_suppliers (supplier_id PK)
  ├── fact_dye_batches.dye_supplier_id
  └── fact_dye_batches.auxiliary_supplier_id

fact_developments (development_id PK)
  ├── fact_lab_dips.development_id
  └── fact_sales_orders.development_id (đơn mới)

fact_sales_orders (order_line_id PK)
  ├── fact_sales_invoices.order_line_id   (1 dòng đơn → 1-3 lần giao)
  ├── fact_claims.order_line_id
  ├── fact_dye_batches.order_line_id      (1 dòng đơn → nhiều mẻ, kể cả nhuộm lại)
  └── fact_order_inquiries.order_line_id  (inquiry 'Đã thành đơn')

fact_dye_batches.parent_batch_id → fact_dye_batches.batch_id (lần nhuộm trước)

Bảng độc lập theo tháng: fact_pnl_monthly, fact_capacity_monthly, fact_cost_monthly,
fact_input_prices_monthly, fact_fx_monthly, fact_plan_product_monthly, fact_plan_brand_monthly
```

Luồng nghiệp vụ: brand gửi yêu cầu mẫu (`fact_developments`) → lab dip (`fact_lab_dips`) → xưởng may gửi yêu cầu đặt hàng (`fact_order_inquiries`) → đơn hàng (`fact_sales_orders`) → nhuộm (`fact_dye_batches`) → kiểm phẩm (`fact_quality_daily`) → xuất hàng, ghi nhận doanh thu (`fact_sales_invoices`) → khiếu nại nếu có (`fact_claims`) → công nợ (`fact_ar_snapshots`).

---

## DIMENSION TABLES

### 1. dim_calendar (1.095 dòng)
Lịch ngày 01/01/2025 – 31/12/2027.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `date_key` | DATE PK | Ngày | |
| `calendar_year` | SMALLINT | Năm | |
| `calendar_quarter` | TINYINT | Quý 1–4 | |
| `calendar_month` | TINYINT | Tháng 1–12 | |
| `month_start_date` | DATE | Ngày đầu tháng | JOIN với `period_month` |
| `iso_week` | TINYINT | Tuần ISO | |
| `day_of_week` | TINYINT | 1 = Thứ Hai … 7 = Chủ Nhật | |
| `is_working_day` | TINYINT | 1 nếu văn phòng và kho xuất hàng làm việc (T2–T7, trừ lễ) | Không xuất hàng ngày Chủ Nhật, ngày lễ |
| `is_holiday` | TINYINT | 1 nếu ngày lễ | |
| `holiday_name` | VARCHAR(50) | Tên ngày lễ | |
| `is_tet_shutdown` | TINYINT | 1 nếu nhà máy dừng dệt nhuộm dịp Tết | 2025: 28/01–03/02; 2026: 16/02–22/02; 2027: 05/02–11/02 |
| `season_code` | VARCHAR(6) | Mùa hàng theo ngày xuất xưởng | T7 năm N – T1 năm N+1 = SS(N+1); T2–T6 năm N = FW(N) |

### 2. dim_product_lines (6 dòng)
Nhóm vải.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `product_line_code` | VARCHAR(4) PK | Mã nhóm vải | PB, NY, ST, KN, RC, FN |
| `product_line_name` | VARCHAR(80) | Tên nhóm vải | |
| `fabric_construction` | ENUM | 'Dệt thoi', 'Dệt kim', 'Dệt thoi và dệt kim' | |
| `main_fiber` | VARCHAR(80) | Nguyên liệu chính | |
| `primary_dye_line_id` | VARCHAR(4) | Dây chuyền nhuộm chính | |
| `typical_end_use` | VARCHAR(200) | Ứng dụng chính | |

| product_line_code | product_line_name | primary_dye_line_id |
|---|---|---|
| PB | Poly dệt thoi cơ bản | DL1 |
| NY | Nylon dệt thoi | DL2 |
| ST | Dệt thoi co giãn | DL3 |
| KN | Dệt kim | DL2 |
| RC | Vải tái chế RPET | DL4 |
| FN | Vải chức năng / tráng phủ | DL4 |

### 3. dim_dye_lines (4 dòng)
Dây chuyền nhuộm.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `dye_line_id` | VARCHAR(4) PK | Mã dây chuyền | DL1–DL4 |
| `dye_line_name` | VARCHAR(100) | Tên dây chuyền | |
| `machine_count` | TINYINT | Số máy nhuộm | DL1 12, DL2 12, DL3 16, DL4 10 |
| `machine_type` | VARCHAR(100) | Loại máy | |
| `dye_classes` | VARCHAR(60) | Loại thuốc nhuộm xử lý được | 'Phân tán', 'Acid' |
| `compatible_product_lines` | VARCHAR(60) | Nhóm vải nhuộm được, phân cách dấu phẩy | Dùng khi xét chuyển đơn giữa dây chuyền |
| `nominal_capacity_m_per_month` | INT | Năng lực danh định, mét/tháng | Năng lực thực tế xem `fact_capacity_monthly.output_qty` |

| dye_line_id | dye_line_name | compatible_product_lines | nominal_capacity_m_per_month |
|---|---|---|---|
| DL1 | Dây chuyền nhuộm 1 – polyester khổ lớn | PB,RC,FN,KN | 2.400.000 |
| DL2 | Dây chuyền nhuộm 2 – nylon và dệt kim | NY,KN | 1.700.000 |
| DL3 | Dây chuyền nhuộm 3 – vải co giãn | ST,RC,NY | 1.600.000 |
| DL4 | Dây chuyền nhuộm 4 – tái chế và chức năng | RC,FN | 1.200.000 |

### 4. dim_machines (~72 dòng)
Máy nhuộm, máy hoàn tất (từng máy) và nhóm máy dệt.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `machine_id` | VARCHAR(12) PK | Mã máy hoặc nhóm máy | DL3-J07, WV-WJ3, KT-CR2, FIN-ST04 |
| `process` | ENUM | 'Dệt thoi', 'Dệt kim', 'Nhuộm', 'Định hình - hoàn tất', 'Tráng phủ - cán màng' | |
| `machine_group` | VARCHAR(60) | Nhóm máy | |
| `dye_line_id` | VARCHAR(4) FK NULL | Dây chuyền nhuộm | → dim_dye_lines; chỉ với máy nhuộm |
| `machine_model` | VARCHAR(80) | Loại máy (mô tả chung) | |
| `unit_count` | SMALLINT | Số máy trong nhóm | Dệt: 20–50 máy/nhóm; máy nhuộm, hoàn tất = 1 |
| `max_batch_kg` | SMALLINT NULL | Tải tối đa mỗi mẻ, kg | Máy nhuộm |
| `install_year` | SMALLINT | Năm lắp đặt | |

### 5. dim_articles (~180 dòng)
Danh mục mã vải.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `article_code` | VARCHAR(20) PK | Mã vải nội bộ | Dạng {nhóm}-{kiểu}-{gsm}, ví dụ ST-NS4W-120 |
| `article_name` | VARCHAR(120) | Tên mã vải | |
| `product_line_code` | VARCHAR(4) FK | Nhóm vải | → dim_product_lines |
| `construction` | VARCHAR(60) | Kiểu dệt | Taffeta 190T, Ripstop, Taslan, Single jersey, Mesh... |
| `composition` | VARCHAR(80) | Thành phần | Ví dụ 88% nylon 12% spandex |
| `weight_gsm` | SMALLINT | Định lượng, g/m² | |
| `width_cm` | SMALLINT | Khổ vải, cm | |
| `dye_class` | ENUM | 'Phân tán' (polyester) / 'Acid' (nylon, nylon-spandex) | Dùng khi phân tích chất lượng nhuộm |
| `is_stretch` | TINYINT | 1 nếu vải co giãn | |
| `is_recycled` | TINYINT | 1 nếu dùng sợi tái chế | |
| `functional_finish` | VARCHAR(100) NULL | Hoàn tất chức năng | |
| `certifications` | VARCHAR(60) NULL | GRS, RCS, OEKO-TEX 100 | |
| `default_dye_line_id` | VARCHAR(4) FK | Dây chuyền nhuộm mặc định | → dim_dye_lines |
| `list_price_usd_per_m` | DECIMAL(8,3) | Giá niêm yết tham chiếu, USD/m | Giá thực hiện xem hóa đơn |
| `article_status` | ENUM | 'Đang bán', 'Ngừng' | |

### 6. dim_brands (~33 dòng)
Brand chỉ định vải — tên giả định.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `brand_id` | VARCHAR(10) PK | Mã brand | |
| `brand_name` | VARCHAR(100) | Tên brand | |
| `brand_region` | ENUM | 'Châu Âu', 'Bắc Mỹ', 'Nhật Bản', 'Hàn Quốc', 'Úc', 'Việt Nam' | |
| `brand_segment` | ENUM | 'Chuỗi bán lẻ thể thao', 'Thời trang cơ bản', 'Thời trang thể thao', 'Outdoor', 'Bảo hộ lao động', 'Thương hiệu nội địa' | |
| `is_key_account` | TINYINT | 1 nếu brand trọng điểm | 8 brand; có kế hoạch riêng trong fact_plan_brand_monthly |
| `nomination_type` | ENUM | 'Chỉ định nhà máy vải', 'Không chỉ định' | Thương hiệu nội địa: không chỉ định |
| `lab_dip_sla_days` | TINYINT | SLA trả lab dip, ngày | 5–10 |
| `otd_requirement_pct` | DECIMAL(5,2) | Mức OTD brand yêu cầu, % | |
| `relationship_since` | SMALLINT | Năm bắt đầu hợp tác | |

8 brand trọng điểm: BR-NDV Nordvik Sport (Châu Âu, chuỗi bán lẻ thể thao), BR-KZN Kazeno (Nhật Bản, thời trang cơ bản), BR-VLR Veloria Sport (Châu Âu), BR-CSR Cascade Ridge (Bắc Mỹ, outdoor), BR-PCV Pacevolt (Bắc Mỹ), BR-MRL Mirelle Active (Châu Âu), BR-HNL Haneul Outdoor (Hàn Quốc), BR-BST Bastion Workwear (Châu Âu, bảo hộ lao động).

### 7. dim_customers (~32 dòng)
Khách hàng mua hàng (bill-to): xưởng may và khách nội địa — tên giả định.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `customer_id` | VARCHAR(10) PK | Mã khách hàng | |
| `customer_name` | VARCHAR(200) | Tên khách hàng | |
| `customer_type` | ENUM | 'Xưởng may xuất khẩu', 'Thương hiệu nội địa', 'Nhà buôn vải nội địa' | |
| `country` | VARCHAR(40) | Quốc gia | Việt Nam, Campuchia, Indonesia, Bangladesh, Ấn Độ, Sri Lanka |
| `province_city` | VARCHAR(60) | Tỉnh/thành | Việt Nam theo địa giới từ 01/07/2025 |
| `sales_channel` | ENUM | 'Xuất khẩu trực tiếp', 'Xuất khẩu tại chỗ', 'Nội địa' | Xuất khẩu tại chỗ = xưởng may trong nước làm hàng xuất khẩu |
| `invoice_currency` | CHAR(3) | USD / VND | |
| `payment_term_days` | SMALLINT | Thời hạn thanh toán, ngày | 30–60 |
| `credit_limit_vnd` | DECIMAL(18,0) | Hạn mức tín dụng, VND | |
| `relationship_since` | SMALLINT | Năm bắt đầu giao dịch | |

### 8. dim_chemical_suppliers (8 dòng)
Nhà cung cấp thuốc nhuộm và hóa chất — tên giả định.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `supplier_id` | VARCHAR(8) PK | Mã nhà cung cấp | SUP-D.. thuốc nhuộm; SUP-A.. trợ nhuộm; SUP-F.. hoàn tất |
| `supplier_name` | VARCHAR(150) | Tên | |
| `supply_category` | ENUM | 'Thuốc nhuộm', 'Hóa chất trợ nhuộm', 'Hóa chất hoàn tất' | |
| `country` | VARCHAR(40) | Quốc gia | |
| `contract_start_date` | DATE | Ngày bắt đầu hợp đồng cung cấp hiện hành | |
| `price_index_vs_benchmark` | DECIMAL(5,1) | Chỉ số giá so với mặt bằng cùng nhóm (100 = bình quân) | |

---

## FACT TABLES

### 9. fact_sales_invoices ⭐ (FACT CHÍNH — ~55K dòng)
Doanh thu theo dòng hóa đơn xuất hàng. Grain: 1 dòng = 1 lần xuất của 1 dòng đơn.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `invoice_line_id` | BIGINT PK | Mã dòng | |
| `invoice_no` | VARCHAR(20) | Số hóa đơn / chứng từ xuất | |
| `invoice_date` | DATE | Ngày xuất hàng, ghi nhận doanh thu | |
| `order_line_id` | VARCHAR(16) FK | Dòng đơn hàng | → fact_sales_orders |
| `customer_id` | VARCHAR(10) FK | Khách hàng mua | → dim_customers |
| `brand_id` | VARCHAR(10) FK | Brand chỉ định | → dim_brands |
| `article_code` | VARCHAR(20) FK | Mã vải | → dim_articles |
| `product_line_code` | VARCHAR(4) FK | Nhóm vải | → dim_product_lines |
| `sales_channel` | ENUM | Kênh bán | |
| `ship_to_country` | VARCHAR(40) | Quốc gia nhận hàng | |
| `shipped_meters` | INT | Số mét xuất | mét |
| `unit_price_usd` | DECIMAL(8,3) | Đơn giá | USD/m |
| `amount_usd` | DECIMAL(14,2) | Thành tiền | USD |
| `fx_rate` | DECIMAL(10,2) | Tỷ giá USD/VND áp dụng | VND/USD |
| `invoice_amount_vnd` | DECIMAL(18,0) | Doanh thu hóa đơn, chưa trừ khiếu nại | VND |
| `cogs_vnd` | DECIMAL(18,0) | Giá vốn hàng xuất | VND |
| `gross_profit_before_claims_vnd` | DECIMAL(18,0) | invoice_amount_vnd − cogs_vnd | VND |

⚠️ **Doanh thu thuần = SUM(invoice_amount_vnd) − SUM(fact_claims.claim_amount_vnd). Tổng theo tháng bằng fact_pnl_monthly.net_revenue_vnd.**
⚠️ **Đơn nội địa xuất hóa đơn VND; `amount_usd` là giá trị quy đổi. Luôn dùng `invoice_amount_vnd` khi cộng doanh thu.**

### 10. fact_sales_orders (~35K dòng)
Sổ đơn hàng. Grain: 1 dòng = 1 mã vải × 1 màu trong một PO. Gồm đơn đã giao, đơn mở (đến hạn đến 03/2027) và đơn hủy.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `order_line_id` | VARCHAR(16) PK | Mã dòng đơn | |
| `po_no` | VARCHAR(20) | Số PO của khách | |
| `order_date` | DATE | Ngày xác nhận đơn | |
| `customer_id` | VARCHAR(10) FK | Xưởng may | → dim_customers |
| `brand_id` | VARCHAR(10) FK | Brand chỉ định | → dim_brands |
| `article_code` | VARCHAR(20) FK | Mã vải | → dim_articles |
| `product_line_code` | VARCHAR(4) FK | Nhóm vải | → dim_product_lines |
| `season_code` | VARCHAR(6) | Mùa hàng | SS26, FW26, SS27... |
| `order_type` | ENUM | 'Đơn mới', 'Đơn lặp lại' | |
| `development_id` | VARCHAR(14) FK NULL | Yêu cầu phát triển mẫu tương ứng | → fact_developments; NULL với đơn lặp lại |
| `color_code` | VARCHAR(20) | Mã màu | |
| `shade_group` | ENUM | 'Nhạt', 'Trung bình', 'Đậm', 'Đen' | |
| `ordered_meters` | INT | Số mét đặt | mét |
| `unit_price_usd` | DECIMAL(8,3) | Đơn giá | USD/m |
| `order_value_usd` | DECIMAL(14,2) | Giá trị đơn | USD |
| `order_value_vnd` | DECIMAL(18,0) | Giá trị đơn theo tỷ giá tháng đặt | VND |
| `requested_exmill_date` | DATE | Ngày cam kết xuất xưởng | |
| `planned_production_month` | DATE NULL | Tháng đã xếp lịch nhuộm (đơn chưa giao đủ) | ngày đầu tháng |
| `order_status` | ENUM | 'Đã giao đủ', 'Giao một phần', 'Đang sản xuất', 'Chờ sản xuất', 'Đã hủy' | tại 31/10/2026 |
| `shipped_meters` | INT | Số mét đã xuất | mét |
| `first_ship_date` | DATE NULL | Ngày xuất lần đầu | |
| `final_ship_date` | DATE NULL | Ngày xuất đủ | NULL nếu chưa giao đủ |
| `days_late` | SMALLINT NULL | final_ship_date − requested_exmill_date | ngày; âm = sớm |
| `otd_flag` | TINYINT NULL | 1 nếu giao đủ trong 3 ngày sau ngày cam kết | NULL nếu chưa giao đủ |

⚠️ **OTD = AVG(otd_flag) trên dòng đã giao đủ, nhóm theo final_ship_date. Không tính dòng 'Đã hủy'.**
⚠️ **Đơn quá hạn chưa giao: requested_exmill_date ≤ '2026-10-31' AND order_status IN ('Giao một phần','Đang sản xuất','Chờ sản xuất'). Giá trị phần chưa giao = (ordered_meters − shipped_meters) × order_value_vnd / ordered_meters.**

### 11. fact_claims (~2K dòng)
Khiếu nại đã chấp nhận — giảm trừ doanh thu (credit note).

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `claim_id` | VARCHAR(14) PK | Mã khiếu nại | |
| `claim_date` | DATE | Ngày chấp nhận và ghi giảm trừ | |
| `order_line_id` | VARCHAR(16) FK | Dòng đơn liên quan | → fact_sales_orders |
| `customer_id` | VARCHAR(10) FK | Khách hàng | → dim_customers |
| `brand_id` | VARCHAR(10) FK | Brand | → dim_brands |
| `product_line_code` | VARCHAR(4) | Nhóm vải | |
| `claim_reason` | ENUM | 'Giao trễ', 'Lệch màu', 'Lỗi vải', 'Thiếu số lượng', 'Khác' | |
| `claim_amount_vnd` | DECIMAL(18,0) | Số tiền giảm trừ (số dương) | VND |

⚠️ **Khiếu nại ghi theo claim_date (thường 15–45 ngày sau ngày giao), không theo ngày hóa đơn.**

### 12. fact_order_inquiries (~45K dòng)
Yêu cầu báo giá / đề nghị đặt hàng, gồm yêu cầu bị từ chối.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `inquiry_id` | VARCHAR(14) PK | Mã yêu cầu | |
| `inquiry_date` | DATE | Ngày nhận | |
| `brand_id` | VARCHAR(10) FK | Brand | → dim_brands |
| `customer_id` | VARCHAR(10) FK | Xưởng may | → dim_customers |
| `product_line_code` | VARCHAR(4) FK | Nhóm vải | |
| `article_code` | VARCHAR(20) NULL | Mã vải | |
| `requested_meters` | INT | Số mét đề nghị | mét |
| `est_value_vnd` | DECIMAL(18,0) | Giá trị ước tính | VND |
| `requested_exmill_date` | DATE | Ngày xuất xưởng khách yêu cầu | |
| `inquiry_status` | ENUM | 'Đã thành đơn', 'Từ chối - không đủ năng lực', 'Từ chối - không đạt giá', 'Đang báo giá', 'Khách không xác nhận' | tại 31/10/2026 |
| `decided_date` | DATE NULL | Ngày có kết quả | |
| `order_line_id` | VARCHAR(16) NULL | Dòng đơn hình thành | |

⚠️ **Không cộng est_value_vnd với đơn hàng — inquiry 'Đã thành đơn' đã nằm trong fact_sales_orders.**

### 13. fact_developments (~3,3K dòng)
Pipeline phát triển mẫu. Grain: 1 dòng = 1 yêu cầu màu/vải của brand.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `development_id` | VARCHAR(14) PK | Mã yêu cầu | |
| `brand_id` | VARCHAR(10) FK | Brand | → dim_brands |
| `request_date` | DATE | Ngày nhận yêu cầu | |
| `product_line_code` | VARCHAR(4) FK | Nhóm vải | |
| `article_code` | VARCHAR(20) FK NULL | Mã vải | NULL nếu vải mới |
| `season_code` | VARCHAR(6) | Mùa hàng dự kiến | |
| `development_type` | ENUM | 'Màu mới trên vải có sẵn', 'Vải mới' | |
| `shade_group` | ENUM | Nhóm màu chính | |
| `est_annual_meters` | INT | Sản lượng ước tính/năm nếu được chọn | mét |
| `est_annual_value_vnd` | DECIMAL(18,0) | Giá trị ước tính/năm | VND |
| `current_stage` | ENUM | 'Đang làm lab dip', 'Đang làm mẫu thử', 'Mẫu duyệt - chờ PO', 'Đã có đơn bulk', 'Mất', 'Brand hủy' | tại 31/10/2026 |
| `stage_updated_date` | DATE | Ngày cập nhật giai đoạn gần nhất | |
| `lost_reason` | ENUM NULL | 'Lead time', 'Không đạt màu hoặc chất lượng', 'Giá', 'Khác' | khi current_stage = 'Mất' |
| `first_bulk_order_date` | DATE NULL | Ngày có đơn bulk đầu tiên | |

⚠️ **Tỷ lệ chuyển thành đơn = 'Đã có đơn bulk' / ('Đã có đơn bulk' + 'Mất'), nhóm theo request_date. Mẫu yêu cầu 1–2 tháng gần nhất phần lớn chưa có kết quả — nêu cỡ mẫu.**
⚠️ **est_annual_value_vnd là ước tính của brand khi gửi yêu cầu, không phải doanh thu.**

### 14. fact_lab_dips (~6K dòng)
Lab dip. Grain: 1 dòng = 1 lần gửi duyệt màu.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `lab_dip_id` | VARCHAR(16) PK | Mã lần gửi | |
| `development_id` | VARCHAR(14) FK | Yêu cầu phát triển | → fact_developments |
| `brand_id` | VARCHAR(10) FK | Brand | → dim_brands |
| `submission_no` | TINYINT | Lần gửi thứ mấy | 1 = lần đầu |
| `request_date` | DATE | Ngày yêu cầu (lần đầu) / ngày brand phản hồi chỉnh màu (lần sau) | |
| `submit_date` | DATE NULL | Ngày gửi cho brand | |
| `turnaround_days` | SMALLINT NULL | submit_date − request_date | ngày lịch |
| `sla_days` | TINYINT | SLA của brand | ngày |
| `within_sla` | TINYINT NULL | 1 nếu turnaround_days ≤ sla_days | |
| `shade_group` | ENUM | Nhóm màu | |
| `lab_dip_result` | ENUM | 'Duyệt', 'Không duyệt - chỉnh lại', 'Chờ phản hồi', 'Chưa gửi' | tại 31/10/2026 |
| `result_date` | DATE NULL | Ngày brand phản hồi | |

⚠️ **Thời gian trả lab dip và tỷ lệ duyệt lần đầu: lọc submission_no = 1. Lab dip 'Chưa gửi' có submit_date NULL — tính tuổi = '2026-10-31' − request_date nếu cần.**

### 15. fact_dye_batches (~40K dòng)
Mẻ nhuộm. Grain: 1 dòng = 1 lần nhuộm (lần đầu hoặc nhuộm lại).

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `batch_id` | VARCHAR(16) PK | Mã lần nhuộm | |
| `dye_start_date` | DATE | Ngày bắt đầu nhuộm | |
| `dye_line_id` | VARCHAR(4) FK | Dây chuyền | → dim_dye_lines |
| `machine_id` | VARCHAR(12) FK | Máy nhuộm | → dim_machines |
| `order_line_id` | VARCHAR(16) FK NULL | Dòng đơn | → fact_sales_orders; NULL nếu hàng tồn/mẫu |
| `article_code` | VARCHAR(20) FK | Mã vải | → dim_articles (lấy dye_class) |
| `product_line_code` | VARCHAR(4) FK | Nhóm vải | |
| `color_code` | VARCHAR(20) | Mã màu | |
| `shade_group` | ENUM | 'Nhạt', 'Trung bình', 'Đậm', 'Đen' | |
| `attempt_no` | TINYINT | 1 = lần đầu; ≥ 2 = nhuộm lại | |
| `parent_batch_id` | VARCHAR(16) NULL | Lần nhuộm trước | |
| `batch_meters` | INT | Số mét trong mẻ | mét |
| `batch_kg` | DECIMAL(8,1) | Khối lượng mẻ | kg |
| `cycle_hours` | DECIMAL(5,2) | Thời gian chiếm máy | giờ |
| `idle_wait_hours` | DECIMAL(5,2) | Giờ máy chờ trước mẻ (chờ chỉnh công thức, chờ duyệt màu) | giờ |
| `steam_ton` | DECIMAL(7,2) | Hơi tiêu thụ | tấn |
| `electricity_kwh` | DECIMAL(9,1) | Điện tiêu thụ | kWh |
| `water_m3` | DECIMAL(8,1) | Nước tiêu thụ | m³ |
| `dye_chem_cost_vnd` | DECIMAL(14,0) | Chi phí thuốc nhuộm và hóa chất | VND |
| `dye_supplier_id` | VARCHAR(8) FK | Nhà cung cấp thuốc nhuộm | → dim_chemical_suppliers |
| `auxiliary_supplier_id` | VARCHAR(8) FK | Nhà cung cấp hóa chất trợ nhuộm | → dim_chemical_suppliers |
| `run_result` | ENUM | 'Đạt', 'Không đạt - nhuộm lại', 'Không đạt - hạ loại' | |
| `lab_correction_required` | TINYINT | 1 nếu lab phải chỉnh công thức trước khi nhuộm lại | |

⚠️ **RFT = SUM(attempt_no=1 AND run_result='Đạt') / SUM(attempt_no=1). Tỷ lệ nhuộm lại = SUM(attempt_no>=2) / SUM(attempt_no=1).**
⚠️ **Sản lượng mét đã nhuộm: chỉ cộng attempt_no = 1. Cộng mọi dòng sẽ đếm trùng số mét nhuộm lại.**

### 16. fact_quality_daily (~10K dòng)
Kiểm phẩm vải thành phẩm theo ngày × nhóm vải × dây chuyền nhuộm.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `inspection_date` | DATE PK | Ngày kiểm phẩm | |
| `product_line_code` | VARCHAR(4) PK FK | Nhóm vải | |
| `dye_line_id` | VARCHAR(4) PK FK | Dây chuyền nhuộm | |
| `inspected_meters` | INT | Số mét kiểm | mét |
| `grade_a_meters` | INT | Loại A | mét |
| `grade_b_meters` | INT | Loại B (bán giảm giá) | mét |
| `reject_meters` | INT | Loại bỏ | mét |
| `avg_defect_points_100m2` | DECIMAL(5,2) | Điểm lỗi bình quân trên 100 m² (hệ 4 điểm) | điểm |

### 17. fact_weaving_daily (~9K dòng)
Sản lượng dệt (vải mộc) theo ngày × nhóm máy × nhóm vải.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `production_date` | DATE PK | Ngày sản xuất | |
| `machine_id` | VARCHAR(12) PK FK | Nhóm máy dệt | → dim_machines (WV-*, KT-*) |
| `product_line_code` | VARCHAR(4) PK FK | Nhóm vải | |
| `available_hours` | DECIMAL(8,1) | Giờ máy khả dụng của nhóm | giờ |
| `running_hours` | DECIMAL(8,1) | Giờ máy chạy | giờ |
| `efficiency_pct` | DECIMAL(5,2) | running / available | % |
| `greige_meters` | INT | Sản lượng vải mộc | mét |

⚠️ **Hiệu suất nhiều ngày/nhóm máy: SUM(running_hours)/SUM(available_hours), không AVG(efficiency_pct).**

### 18. fact_capacity_monthly (~250 dòng)
Công suất và mức sử dụng theo tháng × công đoạn × đơn vị.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `period_month` | DATE PK | Tháng | ngày đầu tháng |
| `process` | ENUM PK | 'Dệt thoi', 'Dệt kim', 'Nhuộm', 'Định hình - hoàn tất', 'Phòng lab' | |
| `unit_id` | VARCHAR(10) PK | DL1–DL4 (nhuộm), WV (dệt thoi), KT (dệt kim), FIN (hoàn tất), LAB (phòng lab) | |
| `available_hours` | DECIMAL(10,1) | Giờ khả dụng (lab: giờ công kỹ thuật viên) | giờ |
| `productive_hours` | DECIMAL(10,1) | Giờ sản xuất lần đầu (lab: giờ làm lab dip) | giờ |
| `rework_hours` | DECIMAL(10,1) | Giờ làm lại và chờ (nhuộm: nhuộm lại + chờ; lab: chỉnh công thức cho sản xuất) | giờ |
| `utilization_pct` | DECIMAL(5,2) | (productive + rework) / available | % |
| `output_qty` | INT | Sản lượng đầu ra | |
| `output_unit` | VARCHAR(20) | 'mét' hoặc 'lab dip' | |

⚠️ **Mức sử dụng toàn nhuộm: SUM(productive_hours + rework_hours) / SUM(available_hours) trên DL1–DL4, không AVG(utilization_pct).**

### 19. fact_cost_monthly (~920 dòng)
Giá vốn hàng bán theo tháng × nhóm vải × yếu tố chi phí.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `period_month` | DATE PK | Tháng | |
| `product_line_code` | VARCHAR(4) PK FK | Nhóm vải | |
| `cost_element` | ENUM PK | 'Sợi', 'Thuốc nhuộm và hóa chất', 'Năng lượng', 'Nhân công trực tiếp', 'Khấu hao', 'Sản xuất chung khác', 'Nhuộm lại và hạ loại' | |
| `cost_vnd` | DECIMAL(18,0) | Giá vốn phân theo yếu tố | VND |

⚠️ **Tổng theo tháng × nhóm vải = SUM(fact_sales_invoices.cogs_vnd) cùng tháng × nhóm vải. Không cộng hai bảng với nhau.**

### 20. fact_input_prices_monthly (~220 dòng)
Giá mua đầu vào chính theo tháng.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `period_month` | DATE PK | Tháng | |
| `item_code` | VARCHAR(20) PK | Mã đầu vào | POLY_FDY_75D, POLY_DTY_150D, NYLON_FDY_70D, SPANDEX_40D, RPET_DTY_75D, DISPERSE_DYE_IDX, ACID_DYE_IDX, AUX_DL3_LEVELING, STEAM, ELECTRIC |
| `item_name` | VARCHAR(100) | Tên | |
| `unit` | VARCHAR(20) | Đơn vị giá | VND/kg, VND/tấn hơi, VND/kWh, chỉ số |
| `price_vnd` | DECIMAL(14,2) | Giá mua bình quân | VND theo đơn vị |
| `price_usd` | DECIMAL(10,4) NULL | Giá USD (hàng nhập) | USD theo đơn vị |

### 21. fact_fx_monthly (22 dòng)

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `period_month` | DATE PK | Tháng | |
| `usd_vnd_avg` | DECIMAL(10,2) | Tỷ giá bình quân tháng | VND/USD |
| `usd_vnd_end` | DECIMAL(10,2) | Tỷ giá cuối tháng | VND/USD |

### 22. fact_pnl_monthly (22 dòng)
Kết quả kinh doanh theo tháng.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `period_month` | DATE PK | Tháng | |
| `gross_invoiced_vnd` | DECIMAL(18,0) | Doanh thu hóa đơn = SUM(fact_sales_invoices.invoice_amount_vnd) | VND |
| `claims_vnd` | DECIMAL(18,0) | Giảm trừ khiếu nại = SUM(fact_claims.claim_amount_vnd) | VND |
| `net_revenue_vnd` | DECIMAL(18,0) | Doanh thu thuần | VND |
| `cogs_vnd` | DECIMAL(18,0) | Giá vốn | VND |
| `gross_profit_vnd` | DECIMAL(18,0) | LN gộp = net_revenue − cogs | VND |
| `selling_expense_vnd` | DECIMAL(18,0) | Chi phí bán hàng | VND |
| `admin_expense_vnd` | DECIMAL(18,0) | Chi phí quản lý | VND |
| `interest_expense_vnd` | DECIMAL(18,0) | Lãi vay | VND |
| `fx_gain_loss_vnd` | DECIMAL(18,0) | Lãi (+) / lỗ (−) tỷ giá | VND |
| `other_income_net_vnd` | DECIMAL(18,0) | Thu nhập khác thuần | VND |
| `profit_before_tax_vnd` | DECIMAL(18,0) | LN trước thuế | VND |
| `income_tax_vnd` | DECIMAL(18,0) | Thuế TNDN | VND |
| `profit_after_tax_vnd` | DECIMAL(18,0) | LN sau thuế | VND |

⚠️ **Đây là nguồn chuẩn cho doanh thu thuần, LN gộp, LNST cấp công ty. Không tự tính LNST từ bảng chi tiết.**

### 23. fact_plan_product_monthly (72 dòng)
Kế hoạch theo nhóm vải × tháng.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `plan_version` | VARCHAR(10) PK | 'KH_2026' | |
| `period_month` | DATE PK | Tháng | |
| `product_line_code` | VARCHAR(4) PK FK | Nhóm vải | |
| `revenue_plan_vnd` | DECIMAL(18,0) | Doanh thu thuần kế hoạch | VND |
| `meters_plan` | INT | Sản lượng kế hoạch | mét |
| `gross_profit_plan_vnd` | DECIMAL(18,0) | LN gộp kế hoạch | VND |

### 24. fact_plan_brand_monthly (108 dòng)
Kế hoạch doanh thu theo brand trọng điểm × tháng.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `plan_version` | VARCHAR(10) PK | 'KH_2026' | |
| `period_month` | DATE PK | Tháng | |
| `plan_brand_key` | VARCHAR(10) PK | brand_id (8 brand trọng điểm) hoặc 'KHAC' | JOIN dim_brands.brand_id khi khác 'KHAC' |
| `revenue_plan_vnd` | DECIMAL(18,0) | Doanh thu thuần kế hoạch | VND |

⚠️ **Hai bảng kế hoạch cùng tổng (= KH công ty 2.640 tỷ năm 2026). Dùng một trong hai tùy câu hỏi, không cộng với nhau.**

### 25. fact_brand_forecasts (~1,5K dòng)
Forecast nhu cầu brand gửi — SNAPSHOT.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `forecast_snapshot_date` | DATE PK | Ngày nhận forecast | 2026-10-15 |
| `brand_id` | VARCHAR(10) PK FK | Brand | |
| `product_line_code` | VARCHAR(4) PK FK | Nhóm vải | |
| `period_month` | DATE PK | Tháng xuất xưởng dự kiến | 2026-11 → 2027-03 |
| `forecast_confidence` | ENUM PK | 'Đã có PO', 'Cam kết', 'Dự kiến' | |
| `forecast_meters` | INT | Sản lượng dự kiến | mét |
| `forecast_value_vnd` | DECIMAL(18,0) | Giá trị dự kiến | VND |

⚠️ **Phần 'Đã có PO' trùng với đơn mở trong fact_sales_orders. Không cộng cả hai.**

### 26. fact_ar_snapshots (~700 dòng)
Công nợ phải thu theo khách hàng tại cuối tháng — SNAPSHOT.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `snapshot_date` | DATE PK | Ngày cuối tháng | |
| `customer_id` | VARCHAR(10) PK FK | Khách hàng | |
| `not_due_vnd` | DECIMAL(18,0) | Chưa đến hạn | VND |
| `overdue_1_30_vnd` | DECIMAL(18,0) | Quá hạn 1–30 ngày | VND |
| `overdue_31_60_vnd` | DECIMAL(18,0) | Quá hạn 31–60 ngày | VND |
| `overdue_over_60_vnd` | DECIMAL(18,0) | Quá hạn trên 60 ngày | VND |
| `total_ar_vnd` | DECIMAL(18,0) | Tổng phải thu | VND |

### Bảng metadata
`_meta_tables`, `_meta_columns`, `_meta_kpi`, `_meta_glossary` — mô tả bảng, cột, KPI (kèm công thức SQL) và thuật ngữ. Đọc khi cần xác nhận ý nghĩa cột hoặc định nghĩa KPI.

---

## SQL TEMPLATES

### 1. Thực hiện so với kế hoạch và cùng kỳ (10 tháng)
```sql
-- Doanh thu thuần, khiếu nại, biên gộp, LNST: 10 tháng 2025 vs 2026
SELECT YEAR(period_month) AS nam,
       SUM(net_revenue_vnd)/1e9 AS dt_thuan_ty,
       SUM(claims_vnd)/SUM(gross_invoiced_vnd)*100 AS khieu_nai_pct,
       SUM(gross_profit_vnd)/SUM(net_revenue_vnd)*100 AS bien_gop_pct,
       SUM(profit_after_tax_vnd)/1e9 AS lnst_ty
FROM fact_pnl_monthly
WHERE MONTH(period_month) <= 10
GROUP BY nam;

-- Kế hoạch lũy kế 10 tháng và cả năm
SELECT SUM(CASE WHEN period_month <= '2026-10-01' THEN revenue_plan_vnd END)/1e9 AS kh_10t_ty,
       SUM(revenue_plan_vnd)/1e9 AS kh_nam_ty
FROM fact_plan_product_monthly
WHERE plan_version = 'KH_2026';
```

### 2. Tách doanh thu thành sản lượng × giá theo nhóm vải
```sql
SELECT pl.product_line_name, YEAR(i.invoice_date) AS nam,
       SUM(i.shipped_meters)/1e6 AS trieu_m,
       SUM(i.invoice_amount_vnd)/SUM(i.shipped_meters) AS gia_bq_dong_m,
       SUM(i.amount_usd)/SUM(i.shipped_meters) AS gia_bq_usd_m,
       SUM(i.invoice_amount_vnd)/1e9 AS dt_hoa_don_ty,
       SUM(i.gross_profit_before_claims_vnd)/SUM(i.invoice_amount_vnd)*100 AS bien_pct
FROM fact_sales_invoices i
JOIN dim_product_lines pl ON pl.product_line_code = i.product_line_code
WHERE MONTH(i.invoice_date) <= 10
GROUP BY pl.product_line_name, nam
ORDER BY pl.product_line_name, nam;
```

### 3. Doanh thu thuần theo brand và quý, so cùng kỳ
```sql
WITH inv AS (
  SELECT brand_id, YEAR(invoice_date) nam, QUARTER(invoice_date) quy, SUM(invoice_amount_vnd) dt
  FROM fact_sales_invoices GROUP BY brand_id, nam, quy),
clm AS (
  SELECT brand_id, YEAR(claim_date) nam, QUARTER(claim_date) quy, SUM(claim_amount_vnd) kn
  FROM fact_claims GROUP BY brand_id, nam, quy)
SELECT b.brand_name, inv.nam, inv.quy,
       (inv.dt - COALESCE(clm.kn,0))/1e9 AS dt_thuan_ty
FROM inv
JOIN dim_brands b ON b.brand_id = inv.brand_id
LEFT JOIN clm ON clm.brand_id = inv.brand_id AND clm.nam = inv.nam AND clm.quy = inv.quy
WHERE b.is_key_account = 1
ORDER BY b.brand_name, inv.nam, inv.quy;
```

### 4. Pipeline mẫu của một brand: lab dip và chuyển đổi
```sql
-- Lab dip lần gửi đầu theo tháng yêu cầu
SELECT DATE_FORMAT(request_date,'%Y-%m') AS thang,
       COUNT(*) AS so_lab_dip,
       AVG(turnaround_days) AS ngay_tra_bq,
       AVG(within_sla)*100 AS trong_sla_pct,
       SUM(lab_dip_result='Duyệt')/NULLIF(SUM(lab_dip_result IN ('Duyệt','Không duyệt - chỉnh lại')),0)*100 AS duyet_lan_dau_pct
FROM fact_lab_dips
WHERE brand_id = 'BR-NDV' AND submission_no = 1
GROUP BY thang ORDER BY thang;

-- Chuyển đổi mẫu → đơn bulk và lý do mất, theo quý yêu cầu
SELECT CONCAT(YEAR(request_date),'-Q',QUARTER(request_date)) AS quy_yeu_cau,
       COUNT(*) AS so_mau,
       SUM(current_stage='Đã có đơn bulk') AS co_don,
       SUM(current_stage='Mất') AS mat,
       SUM(current_stage='Đã có đơn bulk')/NULLIF(SUM(current_stage IN ('Đã có đơn bulk','Mất')),0)*100 AS chuyen_doi_pct,
       SUM(lost_reason='Lead time') AS mat_vi_lead_time
FROM fact_developments
WHERE brand_id = 'BR-NDV'
GROUP BY quy_yeu_cau ORDER BY quy_yeu_cau;
```

### 5. OTD theo tháng và nhóm vải
```sql
SELECT DATE_FORMAT(final_ship_date,'%Y-%m') AS thang, product_line_code,
       COUNT(*) AS so_dong_giao_du, AVG(otd_flag)*100 AS otd_pct, AVG(days_late) AS tre_bq_ngay
FROM fact_sales_orders
WHERE order_status = 'Đã giao đủ' AND final_ship_date >= '2025-01-01'
GROUP BY thang, product_line_code
ORDER BY thang, product_line_code;
```

### 6. Khoanh vùng chất lượng nhuộm
```sql
-- RFT, nhuộm lại, chu kỳ theo dây chuyền × loại thuốc nhuộm × nhóm màu × tháng
SELECT DATE_FORMAT(b.dye_start_date,'%Y-%m') AS thang, b.dye_line_id, a.dye_class, b.shade_group,
       SUM(b.attempt_no = 1) AS me_dau,
       SUM(b.attempt_no = 1 AND b.run_result = 'Đạt')/NULLIF(SUM(b.attempt_no = 1),0)*100 AS rft_pct,
       SUM(b.attempt_no >= 2)/NULLIF(SUM(b.attempt_no = 1),0)*100 AS nhuom_lai_pct,
       AVG(CASE WHEN b.attempt_no = 1 THEN b.cycle_hours END) AS chu_ky_bq,
       SUM(b.cycle_hours * (b.attempt_no >= 2) + b.idle_wait_hours) AS gio_lam_lai_va_cho
FROM fact_dye_batches b
JOIN dim_articles a ON a.article_code = b.article_code
WHERE b.dye_start_date >= '2026-01-01'
GROUP BY thang, b.dye_line_id, a.dye_class, b.shade_group
ORDER BY thang, b.dye_line_id;

-- Đối chiếu nhà cung cấp hóa chất theo dây chuyền và thời gian
SELECT b.dye_line_id, s.supplier_name, MIN(b.dye_start_date) AS tu_ngay, MAX(b.dye_start_date) AS den_ngay,
       SUM(b.attempt_no = 1 AND b.run_result = 'Đạt')/NULLIF(SUM(b.attempt_no = 1),0)*100 AS rft_pct
FROM fact_dye_batches b
JOIN dim_chemical_suppliers s ON s.supplier_id = b.auxiliary_supplier_id
GROUP BY b.dye_line_id, s.supplier_name
ORDER BY b.dye_line_id, tu_ngay;
```

### 7. Công suất theo công đoạn và nhu cầu bị từ chối
```sql
-- Mức sử dụng công suất theo công đoạn × tháng
SELECT DATE_FORMAT(period_month,'%Y-%m') AS thang, process,
       SUM(productive_hours + rework_hours)/SUM(available_hours)*100 AS su_dung_pct,
       SUM(rework_hours)/SUM(available_hours)*100 AS lam_lai_pct,
       SUM(output_qty) AS san_luong
FROM fact_capacity_monthly
WHERE period_month >= '2025-01-01'
GROUP BY thang, process ORDER BY thang, process;

-- Yêu cầu đặt hàng bị từ chối theo lý do × nhóm vải × tháng
SELECT DATE_FORMAT(inquiry_date,'%Y-%m') AS thang, product_line_code, inquiry_status,
       COUNT(*) AS so_yeu_cau, SUM(requested_meters)/1e6 AS trieu_m, SUM(est_value_vnd)/1e9 AS gia_tri_ty
FROM fact_order_inquiries
WHERE inquiry_status LIKE 'Từ chối%' AND inquiry_date >= '2026-01-01'
GROUP BY thang, product_line_code, inquiry_status
ORDER BY thang, gia_tri_ty DESC;
```

### 8. Đơn mở: quá hạn, đến hạn và lịch nhuộm
```sql
SELECT o.product_line_code,
       CASE WHEN o.requested_exmill_date <= '2026-10-31' THEN '1. Quá hạn'
            WHEN o.requested_exmill_date <= '2026-12-31' THEN '2. Đến hạn T11-T12/2026'
            ELSE '3. Đến hạn từ 2027' END AS nhom_han,
       o.planned_production_month,
       SUM(o.ordered_meters - o.shipped_meters)/1e6 AS trieu_m_chua_giao,
       SUM((o.ordered_meters - o.shipped_meters) * o.order_value_vnd / o.ordered_meters)/1e9 AS gia_tri_ty,
       AVG(o.unit_price_usd) AS gia_usd_bq
FROM fact_sales_orders o
WHERE o.order_status IN ('Giao một phần','Đang sản xuất','Chờ sản xuất')
GROUP BY o.product_line_code, nhom_han, o.planned_production_month
ORDER BY nhom_han, gia_tri_ty DESC;
```

---

## JOIN WARNINGS

1. **fact_sales_invoices ↔ fact_claims:** khiếu nại là bảng riêng, ghi theo `claim_date`. Doanh thu thuần theo brand/nhóm vải = hóa đơn − khiếu nại cùng chiều, aggregate từng bảng trước rồi mới JOIN (Template 3). JOIN trực tiếp theo `order_line_id` rồi SUM sẽ nhân khiếu nại theo số lần giao.
2. **fact_sales_orders ↔ fact_sales_invoices:** 1 dòng đơn có 1–3 dòng hóa đơn. Không SUM `ordered_meters` hay `order_value_vnd` sau khi JOIN hóa đơn.
3. **fact_sales_orders ↔ fact_dye_batches:** 1 dòng đơn có nhiều mẻ, gồm cả nhuộm lại. Aggregate mẻ theo `order_line_id` trước khi JOIN với đơn; khi tính mét, lọc `attempt_no` = 1.
4. **fact_dye_batches ↔ dim_articles:** `dye_class` chỉ có ở `dim_articles` — JOIN theo `article_code` khi phân tích theo loại thuốc nhuộm.
5. **fact_developments ↔ fact_lab_dips:** 1 yêu cầu có nhiều lần gửi. Chỉ số lab dip lọc `submission_no` = 1; số lần gửi đến khi duyệt = MAX(submission_no) theo development_id.
6. **fact_developments ↔ fact_sales_orders:** chỉ đơn mới có `development_id`; doanh thu từ đơn lặp lại không truy được về mẫu.
7. **fact_order_inquiries ↔ fact_sales_orders:** inquiry 'Đã thành đơn' đã có trong sổ đơn. Không cộng giá trị inquiry với đơn nhận.
8. **fact_brand_forecasts = SNAPSHOT:** lọc `forecast_snapshot_date` = '2026-10-15'; có 3 mức tin cậy trong khóa chính — SUM tất cả là tổng nhu cầu; phần 'Đã có PO' trùng với đơn mở.
9. **fact_ar_snapshots = SNAPSHOT:** lọc một `snapshot_date` (cuối tháng); không SUM nhiều snapshot.
10. **fact_plan_product_monthly ↔ fact_plan_brand_monthly:** cùng tổng; không cộng hai bảng. `plan_brand_key` = 'KHAC' không có trong dim_brands — dùng LEFT JOIN.
11. **fact_capacity_monthly:** `unit_id` không khai báo FK; nhuộm là DL1–DL4, dệt WV/KT, hoàn tất FIN, lab LAB. Tổng mức sử dụng tính từ giờ, không AVG phần trăm.
12. **fact_cost_monthly ↔ fact_sales_invoices:** cùng tổng giá vốn theo tháng × nhóm vải; dùng `fact_cost_monthly` cho cơ cấu yếu tố chi phí, `fact_sales_invoices` cho giá vốn theo brand/mã vải.
13. **Tết:** Tết 2025 cuối tháng 1, Tết 2026 giữa tháng 2. So sánh tháng 1, tháng 2 giữa hai năm phải nêu lệch Tết; ưu tiên so lũy kế T1–T2 hoặc theo quý.
14. **fact_dye_batches.order_line_id NULL:** ~3% mẻ nhuộm hàng tồn/mẫu; dùng LEFT JOIN khi nối sang đơn hàng.

---

## ĐƠN VỊ TIỀN TỆ

| Bảng | Cột | Đơn vị |
|---|---|---|
| fact_sales_invoices | invoice_amount_vnd, cogs_vnd, gross_profit_before_claims_vnd | VND |
| fact_sales_invoices | unit_price_usd / amount_usd | USD/m / USD |
| fact_sales_invoices | fx_rate | VND/USD |
| fact_sales_orders | order_value_vnd / order_value_usd, unit_price_usd | VND / USD, USD/m |
| fact_claims | claim_amount_vnd | VND |
| fact_order_inquiries, fact_developments | est_value_vnd, est_annual_value_vnd | VND (ước tính) |
| fact_dye_batches | dye_chem_cost_vnd | VND |
| fact_cost_monthly | cost_vnd | VND |
| fact_input_prices_monthly | price_vnd / price_usd | VND / USD theo `unit` |
| fact_pnl_monthly | mọi cột tiền | VND |
| fact_plan_product_monthly, fact_plan_brand_monthly | revenue_plan_vnd, gross_profit_plan_vnd | VND |
| fact_brand_forecasts | forecast_value_vnd | VND |
| fact_ar_snapshots | mọi cột tiền | VND |
| dim_customers | credit_limit_vnd | VND |
| dim_articles | list_price_usd_per_m | USD/m |

Format hiển thị cho lãnh đạo:
- ≥ 1 tỷ: "X,X tỷ" (ví dụ 2.118 tỷ, 42,3 tỷ)
- < 1 tỷ: "XXX triệu"
- Sản lượng: "60,2 triệu m"; giá: "35.180 đ/m" hoặc "1,34 USD/m"
- Phần trăm: 1 chữ số thập phân; thay đổi tỷ lệ dùng "điểm %"
