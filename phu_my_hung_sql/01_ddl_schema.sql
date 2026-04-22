-- =============================================================================
-- Phú Mỹ Hưng Development — Real Estate Demo Database
-- DDL Schema: 7 dimension + 22 fact + 4 metadata = 33 tables
-- Database: phu_my_hung_demo
-- Data range: 01/2024 – 06/2025 (18 months)
-- =============================================================================

CREATE DATABASE IF NOT EXISTS phu_my_hung_demo
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE phu_my_hung_demo;

-- =============================================================================
-- DIMENSION TABLES
-- =============================================================================

-- 1. Projects — PMH development projects
CREATE TABLE projects (
  project_id VARCHAR(20) PRIMARY KEY COMMENT 'Mã dự án: PRJ-001, PRJ-002...',
  name VARCHAR(200) NOT NULL COMMENT 'Tên dự án tiếng Anh',
  name_vi VARCHAR(200) NOT NULL COMMENT 'Tên dự án tiếng Việt',
  location VARCHAR(200) COMMENT 'Vị trí cụ thể',
  city VARCHAR(100) NOT NULL COMMENT 'Thành phố: HCMC, Bac Ninh',
  type ENUM('residential','commercial','mixed','infrastructure','township') NOT NULL COMMENT 'Loại dự án',
  segment ENUM('ultra_luxury','luxury','premium','mid_high','commercial') NOT NULL COMMENT 'Phân khúc thị trường',
  status ENUM('planning','infrastructure','construction','selling','delivered','completed') NOT NULL COMMENT 'Trạng thái hiện tại',
  total_units INT NOT NULL COMMENT 'Tổng số sản phẩm (căn/lô)',
  total_area_sqm DECIMAL(12,2) COMMENT 'Tổng diện tích sàn. Đơn vị: m²',
  launch_date DATE COMMENT 'Ngày mở bán',
  expected_completion DATE COMMENT 'Ngày dự kiến hoàn thành',
  actual_completion DATE COMMENT 'Ngày hoàn thành thực tế (NULL nếu chưa xong)',
  total_investment_vnd BIGINT COMMENT 'Tổng mức đầu tư. Đơn vị: VND',
  INDEX idx_status (status),
  INDEX idx_city (city),
  INDEX idx_segment (segment)
) COMMENT = 'Danh mục dự án phát triển của Phú Mỹ Hưng — 6 dự án chính';

-- 2. Project Phases — sub-phases within projects
CREATE TABLE project_phases (
  phase_id VARCHAR(20) PRIMARY KEY COMMENT 'Mã giai đoạn: PH-001...',
  project_id VARCHAR(20) NOT NULL COMMENT 'FK → projects',
  name VARCHAR(200) NOT NULL COMMENT 'Tên giai đoạn',
  status ENUM('planned','in_progress','completed','delayed') NOT NULL COMMENT 'Trạng thái',
  planned_start DATE COMMENT 'Ngày bắt đầu kế hoạch',
  planned_end DATE COMMENT 'Ngày kết thúc kế hoạch',
  actual_start DATE COMMENT 'Ngày bắt đầu thực tế',
  actual_end DATE COMMENT 'Ngày kết thúc thực tế',
  FOREIGN KEY (project_id) REFERENCES projects(project_id),
  INDEX idx_project (project_id)
) COMMENT = 'Các giai đoạn thi công trong từng dự án (đặc biệt Hồng Hạc)';

-- 3. Contractors — contractor/vendor master
CREATE TABLE contractors (
  contractor_id VARCHAR(20) PRIMARY KEY COMMENT 'Mã nhà thầu: CTR-001...',
  name VARCHAR(200) NOT NULL COMMENT 'Tên công ty nhà thầu',
  specialization VARCHAR(100) NOT NULL COMMENT 'Chuyên môn: foundation, structure, mep, finishing, landscaping',
  rating DECIMAL(3,1) COMMENT 'Đánh giá năng lực (1.0-5.0)',
  active_since DATE COMMENT 'Hợp tác từ năm',
  company_size ENUM('large','medium','specialized') COMMENT 'Quy mô doanh nghiệp',
  INDEX idx_specialization (specialization)
) COMMENT = 'Danh mục nhà thầu thi công và cung cấp dịch vụ — 12 nhà thầu';

-- 4. Unit Types — property product types
CREATE TABLE unit_types (
  unit_type_id VARCHAR(20) PRIMARY KEY COMMENT 'Mã loại sản phẩm: UT-001...',
  name VARCHAR(100) NOT NULL COMMENT 'Tên loại sản phẩm',
  category ENUM('apartment_1br','apartment_2br','apartment_3br','penthouse','villa','townhouse','shop','office') NOT NULL COMMENT 'Phân loại',
  typical_area_min_sqm DECIMAL(8,2) COMMENT 'Diện tích tối thiểu. Đơn vị: m²',
  typical_area_max_sqm DECIMAL(8,2) COMMENT 'Diện tích tối đa. Đơn vị: m²',
  typical_price_min_per_sqm BIGINT COMMENT 'Giá tối thiểu/m². Đơn vị: VND',
  typical_price_max_per_sqm BIGINT COMMENT 'Giá tối đa/m². Đơn vị: VND'
) COMMENT = 'Phân loại sản phẩm bất động sản theo loại hình';

-- 5. Cost Categories — construction cost breakdown
CREATE TABLE cost_categories (
  category_id VARCHAR(20) PRIMARY KEY COMMENT 'Mã hạng mục: CAT-001...',
  name VARCHAR(100) NOT NULL COMMENT 'Tên hạng mục tiếng Anh',
  name_vi VARCHAR(100) NOT NULL COMMENT 'Tên hạng mục tiếng Việt',
  parent_category VARCHAR(20) COMMENT 'Hạng mục cha (NULL nếu cấp 1)',
  is_material BOOLEAN DEFAULT FALSE COMMENT 'Có phải hạng mục vật tư không'
) COMMENT = 'Phân loại hạng mục chi phí xây dựng — 8 hạng mục chính';

-- 6. Management Zones — property management zones
CREATE TABLE management_zones (
  zone_id VARCHAR(20) PRIMARY KEY COMMENT 'Mã khu vực: ZON-001...',
  name VARCHAR(100) NOT NULL COMMENT 'Tên khu vực tiếng Anh',
  name_vi VARCHAR(100) NOT NULL COMMENT 'Tên khu vực tiếng Việt',
  area_description VARCHAR(300) COMMENT 'Mô tả khu vực',
  total_units INT NOT NULL COMMENT 'Tổng số căn hộ/đơn vị quản lý',
  avg_unit_area_sqm DECIMAL(8,2) COMMENT 'Diện tích trung bình mỗi căn. Đơn vị: m²',
  zone_type ENUM('residential','commercial','mixed') NOT NULL COMMENT 'Loại khu vực',
  year_established INT COMMENT 'Năm hình thành',
  INDEX idx_zone_type (zone_type)
) COMMENT = 'Các khu vực quản lý trong khu đô thị PMH tại Quận 7, HCMC — 8 khu';

-- 7. Commercial Tenants — tenants in commercial properties
CREATE TABLE commercial_tenants (
  tenant_id VARCHAR(20) PRIMARY KEY COMMENT 'Mã khách thuê: TNT-001...',
  name VARCHAR(200) NOT NULL COMMENT 'Tên doanh nghiệp thuê',
  zone_id VARCHAR(20) NOT NULL COMMENT 'FK → management_zones',
  unit_description VARCHAR(200) COMMENT 'Mô tả mặt bằng thuê',
  tenant_type ENUM('retail','fnb','bank','service','office','education','healthcare') NOT NULL COMMENT 'Loại hình kinh doanh',
  lease_start DATE NOT NULL COMMENT 'Ngày bắt đầu hợp đồng thuê',
  lease_end DATE NOT NULL COMMENT 'Ngày kết thúc hợp đồng thuê',
  monthly_rent_vnd BIGINT NOT NULL COMMENT 'Tiền thuê hàng tháng. Đơn vị: VND',
  leased_area_sqm DECIMAL(8,2) COMMENT 'Diện tích thuê. Đơn vị: m²',
  FOREIGN KEY (zone_id) REFERENCES management_zones(zone_id),
  INDEX idx_zone (zone_id),
  INDEX idx_type (tenant_type)
) COMMENT = 'Danh mục khách thuê mặt bằng thương mại tại Crescent Mall và khu CBD';

-- =============================================================================
-- FACT TABLES
-- =============================================================================

-- 8. Project Financials — monthly project P&L
CREATE TABLE project_financials (
  id INT AUTO_INCREMENT PRIMARY KEY,
  project_id VARCHAR(20) NOT NULL COMMENT 'FK → projects',
  month_date DATE NOT NULL COMMENT 'Tháng báo cáo (ngày 1 của tháng)',
  revenue_vnd BIGINT NOT NULL DEFAULT 0 COMMENT 'Doanh thu tháng. Đơn vị: VND',
  cost_vnd BIGINT NOT NULL DEFAULT 0 COMMENT 'Chi phí tháng (COGS). Đơn vị: VND',
  gross_profit_vnd BIGINT GENERATED ALWAYS AS (revenue_vnd - cost_vnd) STORED COMMENT 'Lợi nhuận gộp. Đơn vị: VND',
  sga_vnd BIGINT NOT NULL DEFAULT 0 COMMENT 'Chi phí bán hàng & quản lý. Đơn vị: VND',
  FOREIGN KEY (project_id) REFERENCES projects(project_id),
  UNIQUE KEY uk_project_month (project_id, month_date),
  INDEX idx_month (month_date)
) COMMENT = 'Báo cáo tài chính hàng tháng theo dự án — grain: 1 dự án × 1 tháng';

-- 9. Project Budgets — baseline budget by project × cost category
CREATE TABLE project_budgets (
  id INT AUTO_INCREMENT PRIMARY KEY,
  project_id VARCHAR(20) NOT NULL COMMENT 'FK → projects',
  category VARCHAR(50) NOT NULL COMMENT 'Hạng mục chi phí: foundation, structure, mep, finishing, facade, landscaping, infrastructure, contingency',
  budgeted_cost_vnd BIGINT NOT NULL COMMENT 'Ngân sách dự toán. Đơn vị: VND',
  FOREIGN KEY (project_id) REFERENCES projects(project_id),
  UNIQUE KEY uk_project_category (project_id, category)
) COMMENT = 'Ngân sách dự toán theo dự án và hạng mục — baseline để so sánh thực tế';

-- 10. Unit Sales — individual unit sale records
CREATE TABLE unit_sales (
  sale_id VARCHAR(20) PRIMARY KEY COMMENT 'Mã giao dịch bán: SAL-0001...',
  project_id VARCHAR(20) NOT NULL COMMENT 'FK → projects',
  unit_type_id VARCHAR(20) NOT NULL COMMENT 'FK → unit_types',
  unit_code VARCHAR(50) NOT NULL COMMENT 'Mã căn hộ/lô (VD: A-1201, V-05)',
  floor_level INT COMMENT 'Tầng (nếu apartment)',
  area_sqm DECIMAL(8,2) NOT NULL COMMENT 'Diện tích thực. Đơn vị: m²',
  price_per_sqm BIGINT NOT NULL COMMENT 'Đơn giá/m². Đơn vị: VND',
  total_price_vnd BIGINT NOT NULL COMMENT 'Tổng giá trị hợp đồng. Đơn vị: VND',
  sale_date DATE NOT NULL COMMENT 'Ngày ký hợp đồng mua bán',
  buyer_type ENUM('individual','corporate','foreign') NOT NULL DEFAULT 'individual' COMMENT 'Loại khách mua',
  status ENUM('reserved','contracted','paying','handed_over','cancelled') NOT NULL COMMENT 'Trạng thái giao dịch',
  FOREIGN KEY (project_id) REFERENCES projects(project_id),
  FOREIGN KEY (unit_type_id) REFERENCES unit_types(unit_type_id),
  INDEX idx_project (project_id),
  INDEX idx_sale_date (sale_date),
  INDEX idx_status (status)
) COMMENT = 'Giao dịch bán từng căn hộ/sản phẩm — grain: 1 căn 1 dòng';

-- 11. Payment Schedules — installment plan per sold unit
CREATE TABLE payment_schedules (
  schedule_id INT AUTO_INCREMENT PRIMARY KEY,
  sale_id VARCHAR(20) NOT NULL COMMENT 'FK → unit_sales',
  installment_no INT NOT NULL COMMENT 'Số thứ tự đợt thanh toán',
  due_date DATE NOT NULL COMMENT 'Ngày đến hạn',
  amount_vnd BIGINT NOT NULL COMMENT 'Số tiền phải thanh toán. Đơn vị: VND',
  description VARCHAR(200) COMMENT 'Mô tả đợt (đặt cọc, đợt 1, bàn giao...)',
  FOREIGN KEY (sale_id) REFERENCES unit_sales(sale_id),
  INDEX idx_sale (sale_id),
  INDEX idx_due_date (due_date)
) COMMENT = 'Lịch thanh toán theo đợt cho từng căn — grain: 1 đợt 1 dòng';

-- 12. Payment Collections — actual payments received
CREATE TABLE payment_collections (
  collection_id INT AUTO_INCREMENT PRIMARY KEY,
  sale_id VARCHAR(20) NOT NULL COMMENT 'FK → unit_sales',
  schedule_id INT COMMENT 'FK → payment_schedules (NULL nếu thanh toán ngoài lịch)',
  payment_date DATE NOT NULL COMMENT 'Ngày thực nhận tiền',
  amount_vnd BIGINT NOT NULL COMMENT 'Số tiền thực thu. Đơn vị: VND',
  payment_method ENUM('bank_transfer','cash','mortgage') NOT NULL DEFAULT 'bank_transfer' COMMENT 'Hình thức thanh toán',
  FOREIGN KEY (sale_id) REFERENCES unit_sales(sale_id),
  INDEX idx_payment_date (payment_date),
  INDEX idx_sale (sale_id)
) COMMENT = 'Thực thu từng khoản thanh toán từ khách mua — grain: 1 khoản thu 1 dòng';

-- 13. Revenue Recognition — monthly revenue recognition by project
CREATE TABLE revenue_recognition (
  id INT AUTO_INCREMENT PRIMARY KEY,
  project_id VARCHAR(20) NOT NULL COMMENT 'FK → projects',
  month_date DATE NOT NULL COMMENT 'Tháng ghi nhận (ngày 1 của tháng)',
  total_contract_value_vnd BIGINT NOT NULL COMMENT 'Tổng giá trị HĐ lũy kế. Đơn vị: VND',
  recognized_revenue_vnd BIGINT NOT NULL COMMENT 'Doanh thu đã ghi nhận lũy kế. Đơn vị: VND',
  recognized_pct DECIMAL(5,2) NOT NULL COMMENT 'Tỷ lệ ghi nhận. Đơn vị: %',
  sell_through_pct DECIMAL(5,2) NOT NULL COMMENT 'Tỷ lệ bán hàng. Đơn vị: %',
  construction_completion_pct DECIMAL(5,2) COMMENT 'Tiến độ thi công. Đơn vị: %',
  FOREIGN KEY (project_id) REFERENCES projects(project_id),
  UNIQUE KEY uk_project_month (project_id, month_date),
  INDEX idx_month (month_date)
) COMMENT = 'Ghi nhận doanh thu hàng tháng theo tiến độ — grain: 1 dự án × 1 tháng';

-- 14. Construction Costs — line-item construction costs
CREATE TABLE construction_costs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  project_id VARCHAR(20) NOT NULL COMMENT 'FK → projects',
  contractor_id VARCHAR(20) COMMENT 'FK → contractors (NULL nếu chi phí nội bộ)',
  category VARCHAR(50) NOT NULL COMMENT 'Hạng mục: foundation, structure, mep, finishing, facade, landscaping, infrastructure, contingency',
  description VARCHAR(300) COMMENT 'Mô tả chi tiết hạng mục',
  month_date DATE NOT NULL COMMENT 'Tháng phát sinh (ngày 1 của tháng)',
  budgeted_cost_vnd BIGINT NOT NULL COMMENT 'Chi phí dự toán. Đơn vị: VND',
  actual_cost_vnd BIGINT NOT NULL COMMENT 'Chi phí thực tế. Đơn vị: VND',
  FOREIGN KEY (project_id) REFERENCES projects(project_id),
  INDEX idx_project_month (project_id, month_date),
  INDEX idx_category (category),
  INDEX idx_contractor (contractor_id)
) COMMENT = 'Chi phí xây dựng chi tiết — grain: 1 dự án × 1 nhà thầu × 1 hạng mục × 1 tháng';

-- 15. Contractor Invoices — individual contractor invoices
CREATE TABLE contractor_invoices (
  invoice_id VARCHAR(20) PRIMARY KEY COMMENT 'Mã hóa đơn: INV-0001...',
  contractor_id VARCHAR(20) NOT NULL COMMENT 'FK → contractors',
  project_id VARCHAR(20) NOT NULL COMMENT 'FK → projects',
  invoice_date DATE NOT NULL COMMENT 'Ngày hóa đơn',
  amount_vnd BIGINT NOT NULL COMMENT 'Giá trị hóa đơn. Đơn vị: VND',
  category VARCHAR(50) COMMENT 'Hạng mục liên quan',
  description VARCHAR(300) COMMENT 'Mô tả công việc',
  status ENUM('pending','approved','paid','disputed') NOT NULL DEFAULT 'pending' COMMENT 'Trạng thái',
  FOREIGN KEY (contractor_id) REFERENCES contractors(contractor_id),
  FOREIGN KEY (project_id) REFERENCES projects(project_id),
  INDEX idx_contractor (contractor_id),
  INDEX idx_project (project_id),
  INDEX idx_date (invoice_date)
) COMMENT = 'Hóa đơn từng nhà thầu — grain: 1 hóa đơn 1 dòng';

-- 16. Contract Milestones — planned vs actual milestone dates
CREATE TABLE contract_milestones (
  milestone_id INT AUTO_INCREMENT PRIMARY KEY,
  contractor_id VARCHAR(20) NOT NULL COMMENT 'FK → contractors',
  project_id VARCHAR(20) NOT NULL COMMENT 'FK → projects',
  milestone_name VARCHAR(200) NOT NULL COMMENT 'Tên mốc tiến độ',
  planned_date DATE NOT NULL COMMENT 'Ngày kế hoạch',
  actual_date DATE COMMENT 'Ngày thực tế (NULL nếu chưa hoàn thành)',
  status ENUM('pending','completed','delayed','cancelled') NOT NULL DEFAULT 'pending' COMMENT 'Trạng thái',
  FOREIGN KEY (contractor_id) REFERENCES contractors(contractor_id),
  FOREIGN KEY (project_id) REFERENCES projects(project_id),
  INDEX idx_contractor (contractor_id),
  INDEX idx_project (project_id)
) COMMENT = 'Mốc tiến độ theo hợp đồng nhà thầu — grain: 1 mốc 1 dòng';

-- 17. Project Assignments — contractor-project-phase mapping
CREATE TABLE project_assignments (
  assignment_id INT AUTO_INCREMENT PRIMARY KEY,
  contractor_id VARCHAR(20) NOT NULL COMMENT 'FK → contractors',
  project_id VARCHAR(20) NOT NULL COMMENT 'FK → projects',
  phase_id VARCHAR(20) COMMENT 'FK → project_phases (NULL nếu toàn dự án)',
  role VARCHAR(100) NOT NULL COMMENT 'Vai trò: main_contractor, sub_contractor, supplier',
  scope_description VARCHAR(300) COMMENT 'Phạm vi công việc',
  contract_value_vnd BIGINT COMMENT 'Giá trị hợp đồng. Đơn vị: VND',
  start_date DATE COMMENT 'Ngày bắt đầu',
  end_date DATE COMMENT 'Ngày kết thúc dự kiến',
  status ENUM('planned','active','completed','terminated') NOT NULL DEFAULT 'active' COMMENT 'Trạng thái',
  FOREIGN KEY (contractor_id) REFERENCES contractors(contractor_id),
  FOREIGN KEY (project_id) REFERENCES projects(project_id),
  INDEX idx_contractor (contractor_id),
  INDEX idx_project (project_id),
  INDEX idx_status (status)
) COMMENT = 'Phân công nhà thầu theo dự án/giai đoạn — grain: 1 phân công 1 dòng';

-- 18. Change Orders — design/scope change cost impacts
CREATE TABLE change_orders (
  change_order_id VARCHAR(20) PRIMARY KEY COMMENT 'Mã thay đổi: CO-001...',
  project_id VARCHAR(20) NOT NULL COMMENT 'FK → projects',
  order_date DATE NOT NULL COMMENT 'Ngày phát sinh',
  description VARCHAR(500) NOT NULL COMMENT 'Mô tả thay đổi thiết kế/phạm vi',
  category VARCHAR(50) COMMENT 'Hạng mục ảnh hưởng',
  cost_impact_vnd BIGINT NOT NULL COMMENT 'Tác động chi phí (dương = tăng). Đơn vị: VND',
  status ENUM('proposed','approved','rejected','implemented') NOT NULL COMMENT 'Trạng thái',
  approved_by VARCHAR(100) COMMENT 'Người phê duyệt',
  FOREIGN KEY (project_id) REFERENCES projects(project_id),
  INDEX idx_project (project_id),
  INDEX idx_date (order_date)
) COMMENT = 'Phát sinh thay đổi thiết kế/phạm vi — ảnh hưởng chi phí dự án';

-- 19. Material Prices — monthly material price index
CREATE TABLE material_prices (
  id INT AUTO_INCREMENT PRIMARY KEY,
  material_type VARCHAR(50) NOT NULL COMMENT 'Loại vật tư: steel_rebar, cement, glass_aluminum, electrical_cable, plumbing_pipe, finishing_material',
  month_date DATE NOT NULL COMMENT 'Tháng (ngày 1 của tháng)',
  price_index DECIMAL(8,2) NOT NULL COMMENT 'Chỉ số giá (100 = tháng gốc)',
  unit_price_vnd BIGINT COMMENT 'Đơn giá tham khảo. Đơn vị: VND',
  UNIQUE KEY uk_material_month (material_type, month_date),
  INDEX idx_month (month_date)
) COMMENT = 'Chỉ số giá vật tư xây dựng hàng tháng — grain: 1 vật tư × 1 tháng';

-- 20. Debt Schedule — bond/loan details
CREATE TABLE debt_schedule (
  instrument_id VARCHAR(20) PRIMARY KEY COMMENT 'Mã công cụ nợ: DEBT-001...',
  instrument_name VARCHAR(200) NOT NULL COMMENT 'Tên khoản nợ/trái phiếu',
  instrument_type ENUM('bond_usd','bond_vnd','bank_loan','credit_line') NOT NULL COMMENT 'Loại: trái phiếu USD, vay ngân hàng...',
  currency ENUM('VND','USD') NOT NULL DEFAULT 'VND' COMMENT 'Đồng tiền',
  principal_amount BIGINT NOT NULL COMMENT 'Giá trị gốc (theo đồng tiền gốc)',
  principal_amount_vnd BIGINT NOT NULL COMMENT 'Giá trị gốc quy VND. Đơn vị: VND',
  interest_rate_pct DECIMAL(5,2) NOT NULL COMMENT 'Lãi suất/năm. Đơn vị: %',
  issue_date DATE NOT NULL COMMENT 'Ngày phát hành/giải ngân',
  maturity_date DATE NOT NULL COMMENT 'Ngày đáo hạn',
  status ENUM('active','matured','refinanced','prepaid') NOT NULL COMMENT 'Trạng thái',
  INDEX idx_maturity (maturity_date),
  INDEX idx_status (status)
) COMMENT = 'Danh mục nợ — trái phiếu quốc tế, vay ngân hàng, hạn mức tín dụng';

-- 21. Debt Payments — individual debt payments
CREATE TABLE debt_payments (
  payment_id INT AUTO_INCREMENT PRIMARY KEY,
  instrument_id VARCHAR(20) NOT NULL COMMENT 'FK → debt_schedule',
  payment_date DATE NOT NULL COMMENT 'Ngày thanh toán',
  payment_type ENUM('interest','principal','both') NOT NULL COMMENT 'Loại: trả lãi, trả gốc, hoặc cả hai',
  interest_amount_vnd BIGINT NOT NULL DEFAULT 0 COMMENT 'Số tiền lãi. Đơn vị: VND',
  principal_amount_vnd BIGINT NOT NULL DEFAULT 0 COMMENT 'Số tiền gốc. Đơn vị: VND',
  payment_amount_vnd BIGINT GENERATED ALWAYS AS (interest_amount_vnd + principal_amount_vnd) STORED COMMENT 'Tổng thanh toán. Đơn vị: VND',
  FOREIGN KEY (instrument_id) REFERENCES debt_schedule(instrument_id),
  INDEX idx_instrument (instrument_id),
  INDEX idx_date (payment_date)
) COMMENT = 'Chi tiết thanh toán nợ — lãi + gốc — grain: 1 khoản thanh toán 1 dòng';

-- 22. Unsold Inventory — units currently unsold
CREATE TABLE unsold_inventory (
  unit_id VARCHAR(20) PRIMARY KEY COMMENT 'Mã căn chưa bán: USI-001...',
  project_id VARCHAR(20) NOT NULL COMMENT 'FK → projects',
  unit_type_id VARCHAR(20) NOT NULL COMMENT 'FK → unit_types',
  unit_code VARCHAR(50) NOT NULL COMMENT 'Mã căn/lô',
  area_sqm DECIMAL(8,2) NOT NULL COMMENT 'Diện tích. Đơn vị: m²',
  listed_price_vnd BIGINT NOT NULL COMMENT 'Giá niêm yết. Đơn vị: VND',
  listing_date DATE NOT NULL COMMENT 'Ngày đăng bán',
  monthly_carrying_cost_vnd BIGINT NOT NULL COMMENT 'Chi phí giữ hàng tháng (thuế đất + bảo trì). Đơn vị: VND',
  status ENUM('available','reserved','negotiating') NOT NULL DEFAULT 'available' COMMENT 'Trạng thái',
  FOREIGN KEY (project_id) REFERENCES projects(project_id),
  FOREIGN KEY (unit_type_id) REFERENCES unit_types(unit_type_id),
  INDEX idx_project (project_id),
  INDEX idx_listing_date (listing_date)
) COMMENT = 'Hàng tồn kho chưa bán — căn hộ/shop đang chờ giao dịch';

-- 23. Project Permits — permit tracking
CREATE TABLE project_permits (
  permit_id INT AUTO_INCREMENT PRIMARY KEY,
  project_id VARCHAR(20) NOT NULL COMMENT 'FK → projects',
  permit_type VARCHAR(100) NOT NULL COMMENT 'Loại giấy phép: construction, pre_sale, fire_safety, environmental, completion',
  status ENUM('pending','approved','expired','rejected') NOT NULL COMMENT 'Trạng thái',
  application_date DATE COMMENT 'Ngày nộp hồ sơ',
  expected_date DATE COMMENT 'Ngày dự kiến được cấp',
  actual_date DATE COMMENT 'Ngày thực tế được cấp (NULL nếu chưa)',
  notes VARCHAR(300) COMMENT 'Ghi chú',
  FOREIGN KEY (project_id) REFERENCES projects(project_id),
  INDEX idx_project (project_id),
  INDEX idx_status (status)
) COMMENT = 'Theo dõi giấy phép dự án — xây dựng, mở bán, PCCC, môi trường...';

-- 24. Construction Payment Schedule — planned construction outflows
CREATE TABLE construction_payment_schedule (
  id INT AUTO_INCREMENT PRIMARY KEY,
  project_id VARCHAR(20) NOT NULL COMMENT 'FK → projects',
  month_date DATE NOT NULL COMMENT 'Tháng kế hoạch chi (ngày 1 của tháng)',
  planned_amount_vnd BIGINT NOT NULL COMMENT 'Số tiền dự kiến chi. Đơn vị: VND',
  actual_amount_vnd BIGINT COMMENT 'Số tiền thực chi. Đơn vị: VND',
  category VARCHAR(50) COMMENT 'Hạng mục chi phí',
  FOREIGN KEY (project_id) REFERENCES projects(project_id),
  UNIQUE KEY uk_project_month_cat (project_id, month_date, category),
  INDEX idx_month (month_date)
) COMMENT = 'Kế hoạch giải ngân xây dựng hàng tháng — grain: 1 dự án × 1 tháng × 1 hạng mục';

-- 25. Management Costs — monthly PM costs by zone × category
CREATE TABLE management_costs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  zone_id VARCHAR(20) NOT NULL COMMENT 'FK → management_zones',
  month_date DATE NOT NULL COMMENT 'Tháng (ngày 1 của tháng)',
  cost_category VARCHAR(50) NOT NULL COMMENT 'Hạng mục: staff, security, elevator_maintenance, waterproofing_repairs, landscaping, utilities, cleaning, other',
  cost_vnd BIGINT NOT NULL COMMENT 'Chi phí. Đơn vị: VND',
  FOREIGN KEY (zone_id) REFERENCES management_zones(zone_id),
  UNIQUE KEY uk_zone_month_cat (zone_id, month_date, cost_category),
  INDEX idx_month (month_date),
  INDEX idx_zone (zone_id)
) COMMENT = 'Chi phí quản lý bất động sản hàng tháng — grain: 1 khu × 1 hạng mục × 1 tháng';

-- 26. Management Revenue — monthly PM fee collections by zone
CREATE TABLE management_revenue (
  id INT AUTO_INCREMENT PRIMARY KEY,
  zone_id VARCHAR(20) NOT NULL COMMENT 'FK → management_zones',
  month_date DATE NOT NULL COMMENT 'Tháng (ngày 1 của tháng)',
  revenue_vnd BIGINT NOT NULL COMMENT 'Phí quản lý thu được. Đơn vị: VND',
  units_billed INT COMMENT 'Số căn tính phí',
  collection_rate DECIMAL(5,2) COMMENT 'Tỷ lệ thu. Đơn vị: %',
  FOREIGN KEY (zone_id) REFERENCES management_zones(zone_id),
  UNIQUE KEY uk_zone_month (zone_id, month_date),
  INDEX idx_month (month_date)
) COMMENT = 'Doanh thu phí quản lý BĐS hàng tháng — grain: 1 khu × 1 tháng';

-- 27. Maintenance Tickets — work order records
CREATE TABLE maintenance_tickets (
  ticket_id VARCHAR(20) PRIMARY KEY COMMENT 'Mã phiếu: TKT-00001...',
  zone_id VARCHAR(20) NOT NULL COMMENT 'FK → management_zones',
  ticket_date DATE NOT NULL COMMENT 'Ngày ghi nhận',
  category VARCHAR(50) NOT NULL COMMENT 'Loại: elevator, waterproofing, electrical, plumbing, hvac, general, landscaping',
  description VARCHAR(500) COMMENT 'Mô tả sự cố',
  priority ENUM('low','medium','high','critical') NOT NULL DEFAULT 'medium' COMMENT 'Mức ưu tiên',
  status ENUM('open','in_progress','resolved','closed') NOT NULL COMMENT 'Trạng thái',
  resolution_date DATE COMMENT 'Ngày xử lý xong',
  cost_vnd BIGINT COMMENT 'Chi phí xử lý. Đơn vị: VND',
  FOREIGN KEY (zone_id) REFERENCES management_zones(zone_id),
  INDEX idx_zone (zone_id),
  INDEX idx_date (ticket_date),
  INDEX idx_category (category)
) COMMENT = 'Phiếu yêu cầu bảo trì/sửa chữa — grain: 1 phiếu 1 dòng';

-- 28. Lease Income — monthly commercial lease income
CREATE TABLE lease_income (
  id INT AUTO_INCREMENT PRIMARY KEY,
  tenant_id VARCHAR(20) NOT NULL COMMENT 'FK → commercial_tenants',
  month_date DATE NOT NULL COMMENT 'Tháng (ngày 1 của tháng)',
  monthly_rent_vnd BIGINT NOT NULL COMMENT 'Tiền thuê phải thu. Đơn vị: VND',
  collected_vnd BIGINT NOT NULL COMMENT 'Tiền thuê thực thu. Đơn vị: VND',
  occupancy_status ENUM('occupied','vacant','maintenance') NOT NULL DEFAULT 'occupied' COMMENT 'Tình trạng sử dụng',
  FOREIGN KEY (tenant_id) REFERENCES commercial_tenants(tenant_id),
  UNIQUE KEY uk_tenant_month (tenant_id, month_date),
  INDEX idx_month (month_date)
) COMMENT = 'Doanh thu cho thuê mặt bằng thương mại — grain: 1 khách thuê × 1 tháng';

-- 29. Management Fees Monthly — aggregated management fee for cash flow
CREATE TABLE management_fees_monthly (
  id INT AUTO_INCREMENT PRIMARY KEY,
  month_date DATE NOT NULL COMMENT 'Tháng (ngày 1 của tháng)',
  total_fee_revenue_vnd BIGINT NOT NULL COMMENT 'Tổng phí quản lý thu được. Đơn vị: VND',
  total_fee_cost_vnd BIGINT NOT NULL COMMENT 'Tổng chi phí quản lý. Đơn vị: VND',
  net_fee_vnd BIGINT GENERATED ALWAYS AS (total_fee_revenue_vnd - total_fee_cost_vnd) STORED COMMENT 'Lãi/lỗ quản lý. Đơn vị: VND',
  UNIQUE KEY uk_month (month_date)
) COMMENT = 'Tổng hợp phí quản lý hàng tháng cho phân tích dòng tiền';

-- =============================================================================
-- METADATA TABLES
-- =============================================================================

-- 30. Meta Tables
CREATE TABLE _meta_tables (
  table_name VARCHAR(100) PRIMARY KEY COMMENT 'Tên bảng',
  description_vi VARCHAR(500) NOT NULL COMMENT 'Mô tả tiếng Việt',
  description_en VARCHAR(500) NOT NULL COMMENT 'Mô tả tiếng Anh',
  business_context VARCHAR(500) COMMENT 'Ngữ cảnh nghiệp vụ — khi nào cần truy vấn bảng này',
  record_count INT COMMENT 'Số dòng ước tính',
  grain VARCHAR(200) COMMENT 'Grain: mỗi dòng đại diện cho gì'
) COMMENT = 'Metadata: mô tả tất cả bảng trong database — AI engine đọc bảng này trước tiên';

-- 31. Meta Columns
CREATE TABLE _meta_columns (
  id INT AUTO_INCREMENT PRIMARY KEY,
  table_name VARCHAR(100) NOT NULL COMMENT 'Tên bảng',
  column_name VARCHAR(100) NOT NULL COMMENT 'Tên cột',
  data_type VARCHAR(50) NOT NULL COMMENT 'Kiểu dữ liệu',
  description_vi VARCHAR(300) NOT NULL COMMENT 'Mô tả tiếng Việt',
  description_en VARCHAR(300) NOT NULL COMMENT 'Mô tả tiếng Anh',
  unit VARCHAR(50) COMMENT 'Đơn vị: VND, m², %, ngày...',
  example_values VARCHAR(300) COMMENT 'Giá trị mẫu',
  UNIQUE KEY uk_table_column (table_name, column_name)
) COMMENT = 'Metadata: mô tả từng cột trong từng bảng — AI engine dùng để viết SQL chính xác';

-- 32. Meta KPI
CREATE TABLE _meta_kpi (
  kpi_id INT AUTO_INCREMENT PRIMARY KEY,
  kpi_name VARCHAR(100) NOT NULL COMMENT 'Tên KPI tiếng Anh',
  kpi_name_vi VARCHAR(100) NOT NULL COMMENT 'Tên KPI tiếng Việt',
  formula_sql TEXT NOT NULL COMMENT 'Công thức SQL để tính KPI',
  description_vi VARCHAR(500) NOT NULL COMMENT 'Mô tả tiếng Việt',
  description_en VARCHAR(500) NOT NULL COMMENT 'Mô tả tiếng Anh',
  related_tables VARCHAR(300) COMMENT 'Các bảng liên quan',
  related_questions VARCHAR(500) COMMENT 'Câu hỏi demo liên quan (Q1-Q6)'
) COMMENT = 'Metadata: danh sách KPI và công thức SQL — AI engine tính toán dựa trên bảng này';

-- 33. Meta Glossary
CREATE TABLE _meta_glossary (
  id INT AUTO_INCREMENT PRIMARY KEY,
  term_vi VARCHAR(100) NOT NULL COMMENT 'Thuật ngữ tiếng Việt',
  term_en VARCHAR(100) NOT NULL COMMENT 'Thuật ngữ tiếng Anh',
  definition VARCHAR(500) NOT NULL COMMENT 'Định nghĩa'
) COMMENT = 'Metadata: từ điển thuật ngữ ngành — AI engine dùng để hiểu câu hỏi tiếng Việt';
