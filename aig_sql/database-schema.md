# DATA SCHEMA — AIG TẬP ĐOÀN NGUYÊN LIỆU Á CHÂU BI
## Database: aig_demo (MySQL 8.0, utf8mb4_unicode_ci)
## Phạm vi: 01/01/2024 – 30/09/2026 (33 tháng) | "Hiện tại" = 30/09/2026 | Kế hoạch & dự báo: 2026

---

## SƠ ĐỒ QUAN HỆ

```
dim_calendar (date_key PK)
  └── fact_sales.invoice_date

dim_entities (entity_id PK)
  ├── dim_warehouses.entity_id
  ├── dim_customers.primary_entity_id
  ├── dim_products.entity_id
  ├── fact_sales.entity_id
  ├── fact_export_contracts.entity_id
  ├── fact_contract_terms.entity_id
  ├── fact_purchases.entity_id
  ├── fact_inventory_snapshots.entity_id
  ├── fact_receivable_snapshots.entity_id
  ├── fact_production.entity_id
  ├── fact_pnl_monthly.entity_id
  └── fact_plan_monthly.entity_id

dim_export_markets (market_id PK)
  ├── dim_customers.export_market_id
  ├── fact_sales.export_market_id
  └── fact_export_contracts.export_market_id

dim_principals (principal_id PK)
  ├── dim_products.principal_id
  └── fact_purchases.principal_id

dim_warehouses (warehouse_id PK)
  ├── fact_sales.warehouse_id
  ├── fact_purchases.warehouse_id
  └── fact_inventory_snapshots.warehouse_id

dim_customers (customer_id PK)
  ├── fact_sales.customer_id
  ├── fact_export_contracts.customer_id
  ├── fact_contract_terms.customer_id
  └── fact_receivable_snapshots.customer_id

dim_products (product_id PK)
  ├── fact_sales.product_id
  ├── fact_export_contracts.product_id
  ├── fact_purchases.product_id
  └── fact_inventory_snapshots.product_id

fact_export_contracts (contract_id PK)
  └── fact_sales.export_contract_id   (không khai báo FK, NULL với hàng không theo hợp đồng)

Liên kết logic (không có FK):
  fact_purchases.lot_no            ↔ fact_inventory_snapshots.lot_no
  fact_production.product_group    ↔ dim_products.category_l2 (hàng tự sản xuất)
  fact_production.main_raw_material↔ fact_commodity_prices.commodity_code (DUA_KHO, SAN_TUOI)
  fact_purchases.raw_material_code ↔ fact_commodity_prices.commodity_code
  fact_plan_monthly / fact_le_assumptions: theo period_month + entity_id / scenario
```

---

## DIMENSION TABLES

### 1. dim_calendar (~1.096 dòng)
Lịch ngày 01/01/2024 – 31/12/2026.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `date_key` | DATE PK | Ngày | |
| `year` | SMALLINT | Năm | Bọc backtick khi query |
| `quarter` | TINYINT | Quý 1–4 | Bọc backtick |
| `month` | TINYINT | Tháng 1–12 | Bọc backtick |
| `month_label` | CHAR(7) | Năm-tháng, ví dụ `2026-09` | Dùng làm nhãn trục chart |
| `month_name_vi` | VARCHAR(20) | "Tháng 9" | |
| `week_of_year` | TINYINT | Tuần ISO | |
| `day_of_week` | TINYINT | 1 = Thứ Hai … 7 = Chủ Nhật | |
| `day_name_vi` | VARCHAR(15) | Thứ Hai … Chủ Nhật | |
| `is_working_day` | TINYINT | 1 = ngày làm việc (T2–T7, trừ lễ) | Chủ Nhật không có hóa đơn |
| `is_holiday` | TINYINT | 1 = ngày lễ | |
| `holiday_name` | VARCHAR(50) | Tên ngày lễ | NULL nếu không phải lễ |
| `is_tet_period` | TINYINT | 1 = trong ±7 ngày quanh mùng 1 Tết | Tết 2024: 10/02; 2025: 29/01; 2026: 17/02 |

### 2. dim_entities (8 dòng)
Công ty thành viên của tập đoàn.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `entity_id` | VARCHAR(10) PK | AIG, ACC, AFI, ACP, GCF, AHS, ASI, MDG | |
| `entity_name` | VARCHAR(150) | Tên pháp nhân | |
| `short_name` | VARCHAR(50) | Tên ngắn | |
| `segment` | ENUM | 'Holding' / 'Phân phối' / 'Sản xuất' | ACC = Phân phối; AIG = Holding; còn lại = Sản xuất |
| `main_business` | VARCHAR(255) | Hoạt động chính | |
| `region` | VARCHAR(20) | Miền Bắc / Miền Trung / Miền Nam | |
| `province` | VARCHAR(50) | Tỉnh/thành | NULL với AFI, GCF |
| `consolidation_start_date` | DATE | Ngày bắt đầu hợp nhất | GCF = 2025-08-01 |
| `is_active` | TINYINT | | |

| entity_id | Tên | Mảng |
|---|---|---|
| AIG | CTCP Nguyên liệu Á Châu AIG | Holding |
| ACC | CTCP Hóa Chất Á Châu | Phân phối |
| AFI | CTCP Nguyên liệu Thực phẩm Á Châu Sài Gòn | Sản xuất |
| ACP | CTCP Chế biến Dừa Á Châu | Sản xuất |
| GCF | CTCP Thực phẩm G.C (GC Food) | Sản xuất |
| AHS | CTCP Á Châu Hoa Sơn | Sản xuất |
| ASI | Asia Specialty Ingredients | Sản xuất |
| MDG | Mekong Delta Gourmet | Sản xuất |

### 3. dim_export_markets (8 dòng)

| Cột | Kiểu | Mô tả |
|---|---|---|
| `market_id` | VARCHAR(10) PK | US, EU, CN, JP, KR, ME, AU, ASEAN |
| `market_name` | VARCHAR(50) | Mỹ, Liên minh châu Âu, Trung Quốc, Nhật Bản, Hàn Quốc, Trung Đông, Úc, ASEAN |
| `region_group` | VARCHAR(50) | Bắc Mỹ, Châu Âu, Đông Á, Trung Đông, Châu Đại Dương, Đông Nam Á |

### 4. dim_principals (12 dòng)
Hãng nguyên liệu nước ngoài mà ACC làm đại diện phân phối (tên giả định).

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `principal_id` | VARCHAR(10) PK | PR01 … PR12 | |
| `principal_name` | VARCHAR(150) | Tên principal | |
| `country` | VARCHAR(50) | Quốc gia | |
| `currency_code` | CHAR(3) | USD / EUR | Tiền tệ thanh toán khi nhập |
| `main_categories` | VARCHAR(255) | Nhóm hàng chính | |
| `partnership_since` | SMALLINT | Năm bắt đầu hợp tác | |

### 5. dim_warehouses (10 dòng)

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `warehouse_id` | VARCHAR(10) PK | WH-TT, WH-BD, WH-BN, WH-DN, WH-AFI, WH-ACP, WH-GCF, WH-AHS, WH-ASI, WH-MDG | |
| `warehouse_name` | VARCHAR(100) | Tên kho | |
| `entity_id` | VARCHAR(10) FK | Công ty quản lý | → dim_entities |
| `warehouse_type` | ENUM | 'Kho phân phối' / 'Kho nhà máy' | 4 kho phân phối thuộc ACC |
| `region` | VARCHAR(20) | Vùng | |
| `province` | VARCHAR(50) | Tỉnh/thành | |

### 6. dim_customers (~475 dòng)
Khách hàng B2B nội địa và nhà nhập khẩu nước ngoài (tên giả định).

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `customer_id` | VARCHAR(15) PK | Mã khách hàng | |
| `customer_name` | VARCHAR(200) | Tên khách hàng | |
| `customer_type` | ENUM | 'Nội địa' / 'Xuất khẩu' | |
| `industry_segment` | VARCHAR(50) | Ngành khách hàng | Sữa & sản phẩm sữa; Bánh kẹo; Đồ uống; Mì gói & thực phẩm tiện lợi; Thịt & thủy sản chế biến; Food service & chuỗi F&B; Dược & thực phẩm chức năng; Mỹ phẩm & hóa chất CN; Nhà nhập khẩu thực phẩm |
| `region` | VARCHAR(20) | Vùng | NULL với khách xuất khẩu |
| `province` | VARCHAR(50) | Tỉnh/thành | NULL với khách xuất khẩu |
| `export_market_id` | VARCHAR(10) FK | Thị trường | → dim_export_markets; NULL với khách nội địa |
| `primary_entity_id` | VARCHAR(10) FK | Công ty thành viên mua nhiều nhất | Một khách có thể mua từ nhiều entity |
| `customer_tier` | ENUM | 'Key Account' / 'Trung bình' / 'Nhỏ' | |
| `standard_payment_term_days` | SMALLINT | Thời hạn thanh toán tiêu chuẩn ban đầu | Điều khoản hiện hành: xem fact_contract_terms |
| `credit_limit_vnd` | DECIMAL(18,0) | Hạn mức tín dụng | VND |
| `first_order_date` | DATE | Ngày đơn hàng đầu tiên | |
| `is_active` | TINYINT | | |

### 7. dim_products (~380 dòng)
Danh mục hàng phân phối (ACC) và hàng tự sản xuất (nhà máy).

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `product_id` | VARCHAR(15) PK | Mã sản phẩm | |
| `product_name` | VARCHAR(200) | Tên sản phẩm | |
| `entity_id` | VARCHAR(10) FK | Công ty bán | ACC cho hàng phân phối |
| `product_source` | ENUM | 'Phân phối' / 'Tự sản xuất' | |
| `category_l1` | VARCHAR(80) | Nhóm hàng cấp 1 | Ví dụ: Nguyên liệu sữa; Chất béo & creamer; Sản phẩm từ dừa |
| `category_l2` | VARCHAR(80) | Nhóm hàng cấp 2 | Ví dụ: Bột sữa gầy SMP; Nước cốt dừa; Tinh bột sắn |
| `principal_id` | VARCHAR(10) FK | Principal | → dim_principals; NULL với hàng tự sản xuất |
| `unit` | VARCHAR(10) | Đơn vị | 'kg' |
| `pack_size_kg` | DECIMAL(8,2) | Quy cách đóng gói | kg/bao, kg/thùng |
| `shelf_life_months` | TINYINT | Hạn dùng tiêu chuẩn từ ngày sản xuất | tháng |
| `purchase_currency` | CHAR(3) | Tiền tệ mua | Hàng nhập |
| `main_raw_material` | VARCHAR(50) | Nguyên liệu chính | DUA_KHO, SAN_TUOI, NHA_DAM, NUOC_DUA, TRAI_CAY, QUE_HOI, DAU_THUC_VAT, SUA_BOT |
| `is_active` | TINYINT | | |

---

## FACT TABLES

### 8. fact_sales ⭐ (FACT CHÍNH — ~400–500K dòng)
Doanh số bán hàng. 1 dòng = 1 dòng hàng trên hóa đơn. Doanh thu đã loại giao dịch nội bộ tập đoàn.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `sales_line_id` | BIGINT PK | | |
| `invoice_no` | VARCHAR(20) | Số hóa đơn | |
| `invoice_date` | DATE FK | Ngày hóa đơn | → dim_calendar |
| `entity_id` | VARCHAR(10) FK | Công ty xuất hóa đơn | |
| `customer_id` | VARCHAR(15) FK | Khách hàng | |
| `product_id` | VARCHAR(15) FK | Sản phẩm | |
| `warehouse_id` | VARCHAR(10) FK | Kho xuất | |
| `sale_type` | ENUM | 'Nội địa' / 'Xuất khẩu' | |
| `export_market_id` | VARCHAR(10) FK | Thị trường | NULL với bán nội địa |
| `export_contract_id` | VARCHAR(20) | Hợp đồng xuất khẩu | NULL nếu bán lẻ đơn / nội địa |
| `sales_team` | VARCHAR(50) | Nhóm kinh doanh | Ngành Sữa, Ngành Bánh kẹo, Ngành Đồ uống, Ngành Thực phẩm tiện lợi, Ngành Thịt & Thủy sản, Food Service, Dược – Mỹ phẩm, Hóa chất CN, Xuất khẩu, Kinh doanh nội địa – Nhà máy |
| `quantity_kg` | DECIMAL(12,2) | Sản lượng | kg |
| `list_price_vnd` | DECIMAL(14,2) | Giá niêm yết tại thời điểm bán | VND/kg |
| `discount_pct` | DECIMAL(5,2) | Chiết khấu so với giá niêm yết | % |
| `unit_price_vnd` | DECIMAL(14,2) | Giá bán thực tế | VND/kg |
| `currency_code` | CHAR(3) | Tiền tệ hóa đơn | VND / USD |
| `unit_price_fc` | DECIMAL(12,4) | Giá bán ngoại tệ | USD/kg; NULL với hóa đơn VND |
| `fx_rate` | DECIMAL(10,2) | Tỷ giá quy đổi | VND/USD; NULL với hóa đơn VND |
| `net_revenue_vnd` | DECIMAL(18,0) | Doanh thu thuần | VND |
| `cogs_vnd` | DECIMAL(18,0) | Giá vốn (chưa gồm dự phòng HTK) | VND |
| `gross_profit_vnd` | DECIMAL(18,0) | LN gộp trước dự phòng | VND |

⚠️ **fact_sales không chứa dự phòng giảm giá HTK. Biên gộp báo cáo lấy từ fact_pnl_monthly.**
⚠️ **SUM(net_revenue_vnd) theo entity × tháng = fact_pnl_monthly.net_revenue_vnd.**

### 9. fact_pnl_monthly ⭐ (~245 dòng)
Kết quả kinh doanh theo tháng × công ty thành viên. Nguồn chuẩn cho doanh thu, LN gộp báo cáo, LNST.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `period_month` | DATE PK | Tháng (ngày đầu tháng) | |
| `entity_id` | VARCHAR(10) PK, FK | Công ty thành viên | |
| `net_revenue_vnd` | DECIMAL(18,0) | Doanh thu thuần | VND |
| `cogs_vnd` | DECIMAL(18,0) | Giá vốn chưa gồm dự phòng | VND |
| `inventory_provision_vnd` | DECIMAL(18,0) | Trích lập (+) / hoàn nhập (−) dự phòng giảm giá HTK trong tháng | VND |
| `gross_profit_vnd` | DECIMAL(18,0) | LN gộp báo cáo = DT − giá vốn − dự phòng | VND |
| `selling_expense_vnd` | DECIMAL(18,0) | Chi phí bán hàng (gồm cước xuất khẩu) | VND |
| `admin_expense_vnd` | DECIMAL(18,0) | Chi phí quản lý doanh nghiệp | VND |
| `financial_income_vnd` | DECIMAL(18,0) | Doanh thu tài chính | VND |
| `financial_expense_vnd` | DECIMAL(18,0) | Chi phí lãi vay | VND |
| `fx_gain_loss_vnd` | DECIMAL(18,0) | Lãi (+) / lỗ (−) tỷ giá | VND |
| `other_income_net_vnd` | DECIMAL(18,0) | Thu nhập khác thuần | VND |
| `profit_before_tax_vnd` | DECIMAL(18,0) | LN trước thuế | VND |
| `income_tax_vnd` | DECIMAL(18,0) | Thuế TNDN | VND |
| `profit_after_tax_vnd` | DECIMAL(18,0) | LNST hợp nhất (trước lợi ích thiểu số) | VND |

⚠️ **LN trước thuế = gross_profit − selling − admin + financial_income − financial_expense + fx_gain_loss + other_income_net.**
⚠️ **Entity AIG: net_revenue = 0 — loại AIG khi tính biên theo entity.**
⚠️ **GCF chỉ có dòng từ 2025-08-01.**

### 10. fact_plan_monthly (~120 dòng)
Kế hoạch 2026 và dự báo cập nhật Q4/2026.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `period_month` | DATE PK | Tháng | |
| `entity_id` | VARCHAR(10) PK, FK | Công ty thành viên | |
| `scenario` | ENUM PK | 'KH_2026' / 'LE_T9_2026' | |
| `net_revenue_vnd` | DECIMAL(18,0) | Doanh thu thuần | VND |
| `inventory_provision_vnd` | DECIMAL(18,0) | Dự phòng HTK dự kiến | VND |
| `gross_profit_vnd` | DECIMAL(18,0) | LN gộp sau dự phòng | VND |
| `operating_expense_vnd` | DECIMAL(18,0) | CP bán hàng + QLDN | VND |
| `financial_net_vnd` | DECIMAL(18,0) | Tài chính thuần ± tỷ giá ± khác | VND |
| `profit_before_tax_vnd` | DECIMAL(18,0) | LN trước thuế | VND |
| `profit_after_tax_vnd` | DECIMAL(18,0) | LNST | VND |

⚠️ **KH_2026: T1–T12/2026. LE_T9_2026: CHỈ T10–T12/2026. Ước tính cả năm = fact_pnl_monthly (T1–T9/2026) + LE (T10–T12).**

### 11. fact_le_assumptions (~10 dòng)
Giả định dùng lập LE_T9_2026.

| Cột | Kiểu | Mô tả |
|---|---|---|
| `assumption_id` | INT PK | |
| `scenario` | VARCHAR(20) | 'LE_T9_2026' |
| `assumption_code` | VARCHAR(40) | DUA_KHO_AVG, USD_VND_AVG, EUR_VND_AVG, ACC_FX_COGS_SHARE, ACC_PRICE_PASS_LAG_DAYS, ACC_USD_PAYABLES, ACP_COCONUT_COST_SHARE, ACP_FIXED_PRICE_EXPORT_SHARE, SMP_SECOND_PROVISION, CIT_RATE |
| `description_vi` | VARCHAR(255) | Diễn giải |
| `period_label` | VARCHAR(20) | 'Q4/2026' |
| `assumption_value` | DECIMAL(18,4) | Giá trị |
| `unit` | VARCHAR(30) | VND/trái, VND, USD, tỷ lệ, ngày |

### 12. fact_export_contracts (~60 dòng)
Hợp đồng xuất khẩu kỳ hạn của các nhà máy.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `contract_id` | VARCHAR(20) PK | Mã hợp đồng | |
| `entity_id` | VARCHAR(10) FK | Nhà máy | |
| `customer_id` | VARCHAR(15) FK | Nhà nhập khẩu | |
| `export_market_id` | VARCHAR(10) FK | Thị trường | |
| `product_id` | VARCHAR(15) FK | Sản phẩm | |
| `sign_date` | DATE | Ngày ký | |
| `start_date` | DATE | Bắt đầu giao hàng | |
| `end_date` | DATE | Kết thúc | |
| `contract_qty_tons` | DECIMAL(10,2) | Sản lượng cam kết | tấn |
| `fixed_price_usd_per_ton` | DECIMAL(10,2) | Giá FOB cố định | USD/tấn |
| `has_price_adjustment_clause` | TINYINT | 1 = có điều khoản điều chỉnh giá theo nguyên liệu | |
| `note` | VARCHAR(255) | Ghi chú | |

### 13. fact_contract_terms (~500 dòng)
Lịch sử điều khoản thương mại (thời hạn thanh toán, chiết khấu đặc biệt) với khách hàng.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `term_id` | INT PK | | |
| `customer_id` | VARCHAR(15) FK | Khách hàng | |
| `entity_id` | VARCHAR(10) FK | Công ty thành viên | |
| `effective_date` | DATE | Ngày hiệu lực | |
| `end_date` | DATE | Ngày hết hiệu lực | NULL = đang hiệu lực |
| `payment_term_days` | SMALLINT | Thời hạn thanh toán | ngày |
| `special_discount_pct` | DECIMAL(5,2) | Chiết khấu đặc biệt trên giá niêm yết | % |
| `approved_by_role` | VARCHAR(100) | Chức danh người duyệt | |
| `approval_date` | DATE | Ngày duyệt | |
| `note` | VARCHAR(255) | Ghi chú | |

### 14. fact_purchases (~25–35K dòng)
Nhập hàng phân phối (từ principal) và nguyên liệu sản xuất (nông sản, NCC nội địa). 1 dòng = 1 lô nhập.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `purchase_line_id` | BIGINT PK | | |
| `po_no` | VARCHAR(20) | Số đơn mua / tờ khai | |
| `receipt_date` | DATE | Ngày nhập kho | |
| `entity_id` | VARCHAR(10) FK | Công ty mua | |
| `supplier_type` | ENUM | 'Principal nhập khẩu' / 'Nông sản trong nước' / 'Nhà cung cấp nội địa' | |
| `principal_id` | VARCHAR(10) FK | Principal | NULL nếu không phải hàng principal |
| `product_id` | VARCHAR(15) FK | Hàng phân phối | NULL nếu mua nguyên liệu sản xuất |
| `raw_material_code` | VARCHAR(20) | Nguyên liệu sản xuất | NULL nếu mua hàng phân phối |
| `warehouse_id` | VARCHAR(10) FK | Kho nhập | |
| `lot_no` | VARCHAR(30) | Số lô | Nối với fact_inventory_snapshots.lot_no |
| `quantity` | DECIMAL(14,2) | Số lượng | |
| `quantity_unit` | VARCHAR(10) | kg / trái | Dừa tính theo trái |
| `currency_code` | CHAR(3) | Tiền tệ mua | VND / USD / EUR |
| `unit_price_fc` | DECIMAL(14,4) | Đơn giá theo tiền tệ mua | |
| `fx_rate` | DECIMAL(10,2) | Tỷ giá ngày nhập | VND; = 1 với hàng VND |
| `total_value_vnd` | DECIMAL(18,0) | Giá trị nhập kho đã gồm chi phí nhập khẩu | VND |
| `manufacturing_date` | DATE | Ngày sản xuất | |
| `expiry_date` | DATE | Hạn sử dụng | |

### 15. fact_inventory_snapshots (~80–120K dòng)
Tồn kho cuối tháng theo lô. SNAPSHOT.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `snapshot_id` | BIGINT PK | | |
| `snapshot_date` | DATE | Ngày cuối tháng | |
| `entity_id` | VARCHAR(10) FK | | |
| `warehouse_id` | VARCHAR(10) FK | | |
| `product_id` | VARCHAR(15) FK | | |
| `lot_no` | VARCHAR(30) | Số lô | |
| `quantity_kg` | DECIMAL(14,2) | Số lượng tồn | kg |
| `inventory_value_vnd` | DECIMAL(18,0) | Giá trị tồn theo giá gốc | VND |
| `expiry_date` | DATE | Hạn sử dụng | |
| `days_to_expiry` | INT | Số ngày còn lại tới hạn tại snapshot_date | ngày |
| `provision_balance_vnd` | DECIMAL(18,0) | Số dư dự phòng của lô | VND |

⚠️ **Luôn lọc một snapshot_date. Giá trị tồn thuần = inventory_value_vnd − provision_balance_vnd.**

### 16. fact_receivable_snapshots (~14–16K dòng)
Công nợ phải thu cuối tháng theo khách hàng × công ty thành viên. SNAPSHOT.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `snapshot_date` | DATE PK | Ngày cuối tháng | |
| `customer_id` | VARCHAR(15) PK, FK | | |
| `entity_id` | VARCHAR(10) PK, FK | | |
| `closing_balance_vnd` | DECIMAL(18,0) | Dư nợ cuối kỳ (gồm VAT) | VND |
| `not_due_vnd` | DECIMAL(18,0) | Chưa đến hạn | VND |
| `overdue_1_30_vnd` | DECIMAL(18,0) | Quá hạn 1–30 ngày | VND |
| `overdue_31_60_vnd` | DECIMAL(18,0) | Quá hạn 31–60 ngày | VND |
| `overdue_over_60_vnd` | DECIMAL(18,0) | Quá hạn > 60 ngày | VND |
| `revenue_last_90d_vnd` | DECIMAL(18,0) | Doanh thu 90 ngày gần nhất (gồm VAT nội địa) | VND |
| `dso_days` | DECIMAL(6,1) | DSO = dư nợ / DT 90 ngày × 90 | ngày |
| `payment_term_days` | SMALLINT | Thời hạn thanh toán hiện hành | ngày |

⚠️ **DSO nhiều khách: tính lại bằng SUM(closing_balance)/SUM(revenue_last_90d)×90, không AVG(dso_days).**

### 17. fact_production (~1.200 dòng)
Sản xuất theo tháng × nhà máy × nhóm sản phẩm.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `production_month` | DATE PK | Tháng (ngày đầu tháng) | |
| `entity_id` | VARCHAR(10) PK, FK | Nhà máy | AFI, ACP, GCF, AHS, ASI, MDG |
| `product_group` | VARCHAR(80) PK | Nhóm sản phẩm | = dim_products.category_l2 |
| `output_kg` | DECIMAL(14,2) | Sản lượng thành phẩm | kg |
| `capacity_kg` | DECIMAL(14,2) | Công suất thiết kế trong tháng | kg |
| `utilization_pct` | DECIMAL(5,2) | Hiệu suất công suất | % |
| `main_raw_material` | VARCHAR(20) | Nguyên liệu chính | mã |
| `raw_material_qty` | DECIMAL(16,2) | Lượng nguyên liệu tiêu hao | trái / kg |
| `raw_material_unit` | VARCHAR(10) | Đơn vị | |
| `raw_material_cost_vnd` | DECIMAL(18,0) | Chi phí nguyên liệu chính | VND |
| `conversion_cost_vnd` | DECIMAL(18,0) | Chi phí chế biến | VND |
| `unit_cost_vnd_per_kg` | DECIMAL(14,2) | Giá thành đơn vị | VND/kg |

### 18. fact_commodity_prices (~860 dòng)
Giá nguyên liệu đầu vào và tỷ giá theo tuần (số liệu mô phỏng).

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `price_date` | DATE PK | Thứ Hai đầu tuần | |
| `commodity_code` | VARCHAR(20) PK | DUA_KHO, SAN_TUOI, SMP_GLOBAL, WHEY_GLOBAL, USD_VND, EUR_VND | |
| `commodity_name` | VARCHAR(100) | Tên | |
| `price` | DECIMAL(14,2) | Giá | |
| `unit` | VARCHAR(20) | VND/trái (dừa), VND/kg (sắn), USD/tấn (SMP, whey), VND (tỷ giá) | |

### 19. Metadata
`_meta_tables`, `_meta_columns`, `_meta_kpi`, `_meta_glossary` — mô tả bảng, cột, công thức KPI và thuật ngữ. Dùng khi cần xác nhận ý nghĩa một cột hoặc thuật ngữ.

---

## SQL TEMPLATES

### T1. Doanh thu, biên gộp, LNST theo quý và công ty thành viên
```sql
-- Biên gộp báo cáo và trước dự phòng theo entity × quý
SELECT p.entity_id, e.segment,
       YEAR(p.period_month) AS nam, QUARTER(p.period_month) AS quy,
       SUM(p.net_revenue_vnd)/1e9                                         AS dt_ty,
       SUM(p.gross_profit_vnd)/NULLIF(SUM(p.net_revenue_vnd),0)*100        AS bien_gop_bc,
       SUM(p.net_revenue_vnd - p.cogs_vnd)/NULLIF(SUM(p.net_revenue_vnd),0)*100 AS bien_gop_truoc_dp,
       SUM(p.inventory_provision_vnd)/1e9                                 AS du_phong_ty,
       SUM(p.profit_after_tax_vnd)/1e9                                    AS lnst_ty
FROM fact_pnl_monthly p
JOIN dim_entities e ON e.entity_id = p.entity_id
WHERE p.period_month BETWEEN '2025-01-01' AND '2026-09-01'
GROUP BY p.entity_id, e.segment, nam, quy
ORDER BY p.entity_id, nam, quy;
```

### T2. Thực hiện lũy kế vs kế hoạch vs cùng kỳ; ước tính cả năm theo LE
```sql
SELECT
  (SELECT SUM(net_revenue_vnd) FROM fact_pnl_monthly WHERE period_month BETWEEN '2026-01-01' AND '2026-09-01')/1e9 AS dt_9t_2026,
  (SELECT SUM(net_revenue_vnd) FROM fact_pnl_monthly WHERE period_month BETWEEN '2025-01-01' AND '2025-09-01')/1e9 AS dt_9t_2025,
  (SELECT SUM(profit_after_tax_vnd) FROM fact_pnl_monthly WHERE period_month BETWEEN '2026-01-01' AND '2026-09-01')/1e9 AS lnst_9t_2026,
  (SELECT SUM(profit_after_tax_vnd) FROM fact_pnl_monthly WHERE period_month BETWEEN '2025-01-01' AND '2025-09-01')/1e9 AS lnst_9t_2025,
  (SELECT SUM(net_revenue_vnd) FROM fact_plan_monthly WHERE scenario='KH_2026')/1e9      AS dt_kh_2026,
  (SELECT SUM(profit_after_tax_vnd) FROM fact_plan_monthly WHERE scenario='KH_2026')/1e9 AS lnst_kh_2026,
  ((SELECT SUM(profit_after_tax_vnd) FROM fact_pnl_monthly WHERE period_month BETWEEN '2026-01-01' AND '2026-09-01')
   + (SELECT SUM(profit_after_tax_vnd) FROM fact_plan_monthly WHERE scenario='LE_T9_2026'))/1e9 AS lnst_ca_nam_le;
```

### T3. Tách biến động biên gộp (giá – sản lượng – cơ cấu) theo entity, 6T/2026 vs 6T/2025
```sql
-- Bước 1: DT, giá vốn, sản lượng theo entity × category_l2 cho 2 kỳ
WITH base AS (
  SELECT s.entity_id, p.category_l2,
         CASE WHEN s.invoice_date BETWEEN '2025-01-01' AND '2025-06-30' THEN 'K0' ELSE 'K1' END AS ky,
         SUM(s.quantity_kg) AS kg, SUM(s.net_revenue_vnd) AS dt, SUM(s.cogs_vnd) AS gv
  FROM fact_sales s JOIN dim_products p ON p.product_id = s.product_id
  WHERE s.invoice_date BETWEEN '2025-01-01' AND '2025-06-30'
     OR s.invoice_date BETWEEN '2026-01-01' AND '2026-06-30'
  GROUP BY s.entity_id, p.category_l2, ky
)
SELECT entity_id, category_l2,
       MAX(CASE WHEN ky='K0' THEN dt/kg END) AS gia_ban_k0, MAX(CASE WHEN ky='K1' THEN dt/kg END) AS gia_ban_k1,
       MAX(CASE WHEN ky='K0' THEN gv/kg END) AS gia_von_k0, MAX(CASE WHEN ky='K1' THEN gv/kg END) AS gia_von_k1,
       MAX(CASE WHEN ky='K0' THEN kg END)/1000 AS tan_k0,   MAX(CASE WHEN ky='K1' THEN kg END)/1000 AS tan_k1
FROM base GROUP BY entity_id, category_l2;
-- Bước 2 (trong phân tích): hiệu ứng giá vốn = (gia_von_k0 - gia_von_k1) × kg_k1; hiệu ứng giá bán = (gia_ban_k1 - gia_ban_k0) × kg_k1;
-- hiệu ứng cơ cấu = chênh biên gộp còn lại sau khi tách giá. Đối chiếu đơn giá nguyên liệu ở fact_production / fact_commodity_prices.
```

### T4. Giá nguyên liệu chính và giá thành nhà máy theo tháng
```sql
SELECT pr.production_month, pr.entity_id,
       SUM(pr.raw_material_cost_vnd)/SUM(pr.raw_material_qty)              AS don_gia_nl,
       SUM(pr.raw_material_cost_vnd + pr.conversion_cost_vnd)/SUM(pr.output_kg) AS gia_thanh_vnd_kg,
       SUM(pr.output_kg)/SUM(pr.capacity_kg)*100                           AS hieu_suat_pct,
       (SELECT AVG(c.price) FROM fact_commodity_prices c
         WHERE c.commodity_code = 'DUA_KHO'
           AND c.price_date >= pr.production_month
           AND c.price_date <  DATE_ADD(pr.production_month, INTERVAL 1 MONTH)) AS gia_dua_thi_truong
FROM fact_production pr
WHERE pr.entity_id = 'ACP' AND pr.production_month >= '2025-01-01'
GROUP BY pr.production_month, pr.entity_id
ORDER BY pr.production_month;
```

### T5. Hiệu quả khách hàng: tăng trưởng, biên, DSO, chi phí vốn
```sql
WITH k1 AS (
  SELECT customer_id, SUM(net_revenue_vnd) dt, SUM(gross_profit_vnd) gp, SUM(quantity_kg) kg
  FROM fact_sales WHERE entity_id='ACC' AND invoice_date BETWEEN '2026-07-01' AND '2026-09-30'
  GROUP BY customer_id),
k0 AS (
  SELECT customer_id, SUM(net_revenue_vnd) dt, SUM(gross_profit_vnd) gp, SUM(quantity_kg) kg
  FROM fact_sales WHERE entity_id='ACC' AND invoice_date BETWEEN '2025-07-01' AND '2025-09-30'
  GROUP BY customer_id),
ar AS (
  SELECT customer_id, closing_balance_vnd, dso_days, payment_term_days
  FROM fact_receivable_snapshots WHERE entity_id='ACC' AND snapshot_date='2026-09-30')
SELECT c.customer_name, c.industry_segment, c.customer_tier,
       k1.dt/1e9 AS dt_q3_26_ty, (k1.dt/k0.dt - 1)*100 AS tang_dt_pct, (k1.kg/k0.kg - 1)*100 AS tang_sl_pct,
       k0.gp/k0.dt*100 AS bien_q3_25, k1.gp/k1.dt*100 AS bien_q3_26,
       ar.dso_days, ar.payment_term_days,
       ar.closing_balance_vnd/1e9 AS du_no_ty,
       ar.closing_balance_vnd*0.08/4/1e9 AS chi_phi_von_quy_ty,
       (k1.gp - ar.closing_balance_vnd*0.08/4)/k1.dt*100 AS bien_sau_chi_phi_von
FROM k1
JOIN k0 ON k0.customer_id = k1.customer_id
JOIN dim_customers c ON c.customer_id = k1.customer_id
LEFT JOIN ar ON ar.customer_id = k1.customer_id
ORDER BY k1.dt DESC
LIMIT 20;
```

### T6. Tồn kho theo nhóm hàng, principal, kho và hạn dùng tại một ngày
```sql
SELECT p.category_l2, COALESCE(pr.principal_name,'Tự sản xuất') AS principal, i.warehouse_id,
       SUM(i.quantity_kg)/1000                                                   AS ton_tan,
       SUM(i.inventory_value_vnd)/1e9                                            AS gia_tri_ty,
       SUM(CASE WHEN i.days_to_expiry < 90  THEN i.inventory_value_vnd ELSE 0 END)/1e9 AS han_duoi_90n_ty,
       SUM(CASE WHEN i.days_to_expiry < 180 THEN i.inventory_value_vnd ELSE 0 END)/1e9 AS han_duoi_180n_ty,
       SUM(i.provision_balance_vnd)/1e9                                          AS du_phong_ty
FROM fact_inventory_snapshots i
JOIN dim_products p ON p.product_id = i.product_id
LEFT JOIN dim_principals pr ON pr.principal_id = p.principal_id
WHERE i.snapshot_date = '2026-09-30'
GROUP BY p.category_l2, principal, i.warehouse_id
ORDER BY han_duoi_90n_ty DESC
LIMIT 20;
```

### T7. DIO theo nhóm hàng (ACC) tại cuối tháng
```sql
WITH inv AS (
  SELECT p.category_l2, SUM(i.inventory_value_vnd) AS ton
  FROM fact_inventory_snapshots i JOIN dim_products p ON p.product_id = i.product_id
  WHERE i.entity_id='ACC' AND i.snapshot_date='2026-09-30'
  GROUP BY p.category_l2),
cg AS (
  SELECT p.category_l2, SUM(s.cogs_vnd) AS gv90
  FROM fact_sales s JOIN dim_products p ON p.product_id = s.product_id
  WHERE s.entity_id='ACC' AND s.invoice_date BETWEEN '2026-07-03' AND '2026-09-30'
  GROUP BY p.category_l2)
SELECT inv.category_l2, inv.ton/1e9 AS ton_ty, inv.ton/NULLIF(cg.gv90,0)*90 AS dio_ngay
FROM inv LEFT JOIN cg ON cg.category_l2 = inv.category_l2
ORDER BY dio_ngay DESC;
```

### T8. Xuất khẩu theo thị trường và đơn vị; hợp đồng đang hiệu lực
```sql
SELECT s.entity_id, m.market_name, YEAR(s.invoice_date) AS nam, QUARTER(s.invoice_date) AS quy,
       SUM(s.net_revenue_vnd)/1e9 AS dt_ty, SUM(s.quantity_kg)/1000 AS tan,
       SUM(s.net_revenue_vnd)/SUM(s.quantity_kg*s.fx_rate) AS gia_usd_kg_bq   -- xấp xỉ giá USD/kg
FROM fact_sales s JOIN dim_export_markets m ON m.market_id = s.export_market_id
WHERE s.sale_type='Xuất khẩu' AND s.invoice_date >= '2025-01-01'
GROUP BY s.entity_id, m.market_name, nam, quy;

SELECT entity_id, export_market_id, COUNT(*) AS so_hd, SUM(contract_qty_tons) AS tan,
       SUM(has_price_adjustment_clause=0) AS hd_gia_co_dinh, MIN(end_date), MAX(end_date)
FROM fact_export_contracts
WHERE start_date <= '2026-09-30' AND end_date >= '2026-10-01'
GROUP BY entity_id, export_market_id;
```

---

## JOIN WARNINGS

1. **fact_pnl_monthly ↔ fact_sales:** khác grain (tháng × entity vs dòng hóa đơn). Aggregate fact_sales lên tháng × entity trước khi so sánh. Dự phòng HTK chỉ có ở fact_pnl_monthly.
2. **fact_inventory_snapshots, fact_receivable_snapshots = SNAPSHOT:** luôn `WHERE snapshot_date = 'YYYY-MM-DD'` (ngày cuối tháng). Không SUM qua nhiều tháng. So sánh hai thời điểm → lấy hai snapshot riêng rồi so.
3. **fact_contract_terms ↔ fact_sales:** một khách có nhiều dòng điều khoản theo thời gian. JOIN theo khoảng hiệu lực: `s.invoice_date BETWEEN t.effective_date AND COALESCE(t.end_date,'2099-12-31')`, nếu không sẽ nhân dòng.
4. **fact_plan_monthly:** luôn lọc `scenario`. Không SUM hai scenario với nhau. LE chỉ có T10–T12/2026.
5. **fact_receivable_snapshots ↔ fact_sales:** công nợ gồm VAT, doanh thu fact_sales chưa VAT. Dùng `revenue_last_90d_vnd` trong cùng bảng để tính DSO.
6. **Một khách mua từ nhiều entity:** fact_receivable_snapshots có khóa (snapshot_date, customer_id, entity_id). Lọc entity khi phân tích một mảng.
7. **dim_products.principal_id NULL** với hàng tự sản xuất → dùng LEFT JOIN dim_principals.
8. **fact_sales.export_market_id, export_contract_id, unit_price_fc, fx_rate NULL** với bán nội địa.
9. **fact_production ↔ dim_products:** nối qua `product_group = category_l2` và `entity_id`; không có product_id.
10. **fact_commodity_prices:** theo tuần. Bình quân tháng: `price_date >= đầu tháng AND price_date < đầu tháng sau`. Dừa tính VND/trái, không phải VND/kg.
11. **fact_purchases.quantity:** dừa tính theo trái (`quantity_unit = 'trái'`), các nguyên liệu khác theo kg. Không SUM lẫn đơn vị.
12. **GCF:** chỉ có dữ liệu từ 01/08/2025. So sánh cùng kỳ cấp tập đoàn cần tách phần GCF.
13. **Entity AIG:** doanh thu = 0 — loại khỏi phép tính biên theo entity để tránh chia 0.

---

## ĐƠN VỊ TIỀN TỆ

| Bảng | Cột | Đơn vị |
|---|---|---|
| fact_sales | list_price_vnd, unit_price_vnd | VND/kg |
| fact_sales | unit_price_fc | USD/kg |
| fact_sales | net_revenue_vnd, cogs_vnd, gross_profit_vnd | VND |
| fact_pnl_monthly | tất cả cột *_vnd | VND |
| fact_plan_monthly | tất cả cột *_vnd | VND |
| fact_purchases | unit_price_fc | theo currency_code, trên 1 đơn vị quantity_unit |
| fact_purchases | total_value_vnd | VND |
| fact_inventory_snapshots | inventory_value_vnd, provision_balance_vnd | VND |
| fact_receivable_snapshots | các cột *_vnd | VND (gồm VAT) |
| fact_production | raw_material_cost_vnd, conversion_cost_vnd | VND |
| fact_production | unit_cost_vnd_per_kg | VND/kg |
| fact_export_contracts | fixed_price_usd_per_ton | USD/tấn |
| fact_commodity_prices | price | VND/trái (DUA_KHO), VND/kg (SAN_TUOI), USD/tấn (SMP_GLOBAL, WHEY_GLOBAL), VND (USD_VND, EUR_VND) |
| dim_customers | credit_limit_vnd | VND |

Format hiển thị cho lãnh đạo:
- ≥ 1 tỷ: "X,X tỷ" (ví dụ 1.225 tỷ; 92,3 tỷ)
- < 1 tỷ: "XXX triệu"
- Phần trăm: 1 chữ số thập phân; thay đổi biên dùng "điểm %"
- Sản lượng: tấn (chia kg cho 1.000)
