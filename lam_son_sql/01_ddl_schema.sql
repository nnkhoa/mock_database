-- =============================================================================
-- Lam Sơn Invest — Construction & Real Estate Demo Database
-- DDL Schema: 7 dimension + 12 fact + 4 metadata = 23 tables
-- Database: construction_re_demo
-- Data range: 10/2023 – 03/2025 (18 tháng)
-- =============================================================================

CREATE DATABASE IF NOT EXISTS construction_re_demo
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE construction_re_demo;

-- =============================================================================
-- DIMENSION TABLES
-- =============================================================================

-- 1. Khu vực (huyện/thành phố trong Thái Bình)
CREATE TABLE regions (
  region_id INT PRIMARY KEY,
  region_name VARCHAR(100) NOT NULL COMMENT 'Tên khu vực (huyện/TP)',
  region_type ENUM('thanh_pho','huyen') NOT NULL COMMENT 'Loại: thành phố hoặc huyện',
  notes VARCHAR(200) COMMENT 'Ghi chú đặc điểm khu vực',
  INDEX idx_region_type (region_type)
) COMMENT = 'Danh mục khu vực hành chính tỉnh Thái Bình — nơi triển khai dự án';

-- 2. Hạng mục chi phí xây dựng
CREATE TABLE cost_categories (
  category_id INT PRIMARY KEY,
  category_name_vi VARCHAR(100) NOT NULL COMMENT 'Tên tiếng Việt',
  category_name_en VARCHAR(100) NOT NULL COMMENT 'Tên tiếng Anh',
  typical_pct_min DECIMAL(5,2) COMMENT 'Tỷ trọng điển hình tối thiểu. Đơn vị: %',
  typical_pct_max DECIMAL(5,2) COMMENT 'Tỷ trọng điển hình tối đa. Đơn vị: %'
) COMMENT = 'Phân loại 5 hạng mục chi phí trong thi công xây dựng';

-- 3. Danh mục nguyên vật liệu
CREATE TABLE materials (
  material_id INT PRIMARY KEY,
  material_name VARCHAR(100) NOT NULL COMMENT 'Tên vật liệu',
  unit VARCHAR(20) NOT NULL COMMENT 'Đơn vị tính (kg, tấn, m³, viên)',
  base_price BIGINT NOT NULL COMMENT 'Giá tham chiếu ban đầu. Đơn vị: VND/đơn vị',
  material_group VARCHAR(50) COMMENT 'Nhóm vật liệu (thep, xi_mang, cat, da, gach, be_tong)'
) COMMENT = 'Danh mục nguyên vật liệu xây dựng chính';

-- 4. Nhà thầu phụ
CREATE TABLE subcontractors (
  subcontractor_id INT PRIMARY KEY,
  subcontractor_name VARCHAR(200) NOT NULL COMMENT 'Tên công ty thầu phụ',
  specialization VARCHAR(200) COMMENT 'Chuyên môn / năng lực',
  rating DECIMAL(3,1) COMMENT 'Đánh giá năng lực (1-5)',
  phone VARCHAR(20),
  address VARCHAR(300)
) COMMENT = 'Danh mục nhà thầu phụ hợp tác với Lam Sơn Invest';

-- 5. Đối tác (chủ đầu tư, NTP, supplier)
CREATE TABLE counterparties (
  counterparty_id INT PRIMARY KEY,
  counterparty_name VARCHAR(200) NOT NULL COMMENT 'Tên đối tác',
  counterparty_type ENUM('chu_dau_tu','nha_thau_phu','nha_cung_cap','khach_hang','ngan_hang') NOT NULL COMMENT 'Loại đối tác',
  tax_code VARCHAR(20) COMMENT 'Mã số thuế',
  address VARCHAR(300),
  contact_person VARCHAR(100),
  phone VARCHAR(20)
) COMMENT = 'Danh mục đối tác kinh doanh — chủ đầu tư, NTP, NCC, khách hàng';

-- 6. Phân loại sản phẩm BĐS
CREATE TABLE re_unit_types (
  unit_type_id INT PRIMARY KEY,
  unit_type_code VARCHAR(30) NOT NULL COMMENT 'Mã loại: shophouse, dat_nen, nha_lien_ke, biet_thu, dat_cong_nghiep',
  unit_type_name VARCHAR(100) NOT NULL COMMENT 'Tên tiếng Việt',
  description VARCHAR(300) COMMENT 'Mô tả'
) COMMENT = 'Phân loại sản phẩm bất động sản';

-- 7. Danh mục dự án (thi công + BĐS) — bảng chính
CREATE TABLE projects (
  project_id VARCHAR(10) PRIMARY KEY COMMENT 'Mã dự án: TC-xxx (thi công), BDS-xxx (bất động sản)',
  project_name VARCHAR(200) NOT NULL COMMENT 'Tên dự án đầy đủ',
  project_type ENUM('thi_cong','bat_dong_san') NOT NULL COMMENT 'Loại: thi công xây dựng hoặc đầu tư BĐS',
  project_subtype VARCHAR(50) NOT NULL COMMENT 'Phân loại chi tiết: giao_thong, dan_dung, thuy_loi, ha_tang, khu_do_thi, shophouse, dat_nen, khu_dan_cu, khu_cong_nghiep',
  region_id INT COMMENT 'FK → regions',
  client VARCHAR(200) COMMENT 'Chủ đầu tư / Khách hàng',
  contract_value BIGINT COMMENT 'Giá trị hợp đồng / Tổng mức đầu tư. Đơn vị: triệu VND',
  planned_budget BIGINT COMMENT 'Tổng dự toán chi phí. Đơn vị: triệu VND',
  actual_cost_to_date BIGINT DEFAULT 0 COMMENT 'Chi phí thực tế lũy kế đến hiện tại. Đơn vị: triệu VND',
  planned_start DATE COMMENT 'Ngày bắt đầu kế hoạch',
  planned_end DATE COMMENT 'Ngày kết thúc kế hoạch',
  actual_start DATE COMMENT 'Ngày bắt đầu thực tế',
  actual_end DATE DEFAULT NULL COMMENT 'Ngày kết thúc thực tế (NULL nếu chưa xong)',
  planned_progress_pct DECIMAL(5,2) DEFAULT 0 COMMENT 'Tiến độ kế hoạch hiện tại. Đơn vị: %',
  actual_progress_pct DECIMAL(5,2) DEFAULT 0 COMMENT 'Tiến độ thực tế hiện tại. Đơn vị: %',
  status ENUM('chuan_bi','dang_thi_cong','tam_dung','hoan_thanh','bao_hanh') DEFAULT 'dang_thi_cong' COMMENT 'Trạng thái dự án',
  total_units INT DEFAULT NULL COMMENT 'Tổng số sản phẩm BĐS (căn/lô). NULL nếu thi công.',
  sold_units INT DEFAULT NULL COMMENT 'Số sản phẩm đã bán. NULL nếu thi công.',
  sales_start_date DATE DEFAULT NULL COMMENT 'Ngày mở bán. NULL nếu thi công.',
  notes TEXT COMMENT 'Ghi chú',
  INDEX idx_type (project_type),
  INDEX idx_subtype (project_subtype),
  INDEX idx_status (status),
  FOREIGN KEY (region_id) REFERENCES regions(region_id)
) COMMENT = 'Danh mục tất cả dự án đang triển khai của Lam Sơn Invest (thi công + BĐS)';

-- =============================================================================
-- FACT TABLES
-- =============================================================================

-- 1. Tiến độ theo phase/mốc
CREATE TABLE project_milestones (
  milestone_id INT AUTO_INCREMENT PRIMARY KEY,
  project_id VARCHAR(10) NOT NULL,
  milestone_name VARCHAR(200) NOT NULL COMMENT 'Tên giai đoạn / mốc tiến độ',
  milestone_order INT NOT NULL COMMENT 'Thứ tự giai đoạn',
  planned_start DATE COMMENT 'Ngày bắt đầu kế hoạch',
  planned_end DATE COMMENT 'Ngày kết thúc kế hoạch',
  actual_start DATE COMMENT 'Ngày bắt đầu thực tế',
  actual_end DATE COMMENT 'Ngày kết thúc thực tế (NULL nếu chưa xong)',
  weight_pct DECIMAL(5,2) COMMENT 'Trọng số tiến độ của milestone. Đơn vị: %',
  status ENUM('chua_bat_dau','dang_thuc_hien','hoan_thanh','cham_tien_do') DEFAULT 'chua_bat_dau',
  notes TEXT,
  INDEX idx_project (project_id),
  FOREIGN KEY (project_id) REFERENCES projects(project_id)
) COMMENT = 'Mốc tiến độ / giai đoạn của từng dự án — so sánh kế hoạch vs thực tế';

-- 2. Chi phí phát sinh theo hạng mục × dự án × tháng
CREATE TABLE cost_items (
  cost_item_id INT AUTO_INCREMENT PRIMARY KEY,
  project_id VARCHAR(10) NOT NULL,
  category_id INT NOT NULL,
  cost_month DATE NOT NULL COMMENT 'Tháng phát sinh (ngày đầu tháng). Đơn vị: YYYY-MM-01',
  planned_amount BIGINT NOT NULL COMMENT 'Chi phí kế hoạch. Đơn vị: triệu VND',
  actual_amount BIGINT NOT NULL COMMENT 'Chi phí thực tế. Đơn vị: triệu VND',
  item_description VARCHAR(300) COMMENT 'Mô tả chi tiết (nếu phát sinh)',
  INDEX idx_project_month (project_id, cost_month),
  INDEX idx_category (category_id),
  FOREIGN KEY (project_id) REFERENCES projects(project_id),
  FOREIGN KEY (category_id) REFERENCES cost_categories(category_id)
) COMMENT = 'Chi phí phát sinh theo dự án × hạng mục × tháng — so sánh planned vs actual';

-- 3. Mua vật liệu (PO line)
CREATE TABLE material_purchases (
  purchase_id INT AUTO_INCREMENT PRIMARY KEY,
  project_id VARCHAR(10) NOT NULL,
  material_id INT NOT NULL,
  supplier_name VARCHAR(200) COMMENT 'Tên nhà cung cấp',
  purchase_date DATE NOT NULL COMMENT 'Ngày mua',
  unit_price BIGINT NOT NULL COMMENT 'Đơn giá mua. Đơn vị: VND/đơn vị',
  quantity DECIMAL(12,2) NOT NULL COMMENT 'Số lượng mua (theo đơn vị của vật liệu)',
  total_amount BIGINT NOT NULL COMMENT 'Thành tiền. Đơn vị: triệu VND',
  notes VARCHAR(300),
  INDEX idx_project (project_id),
  INDEX idx_material_date (material_id, purchase_date),
  FOREIGN KEY (project_id) REFERENCES projects(project_id),
  FOREIGN KEY (material_id) REFERENCES materials(material_id)
) COMMENT = 'Chi tiết từng lần mua nguyên vật liệu — theo dõi giá mua so với thị trường';

-- 4. Giá thị trường vật liệu theo tháng
CREATE TABLE material_price_index (
  price_id INT AUTO_INCREMENT PRIMARY KEY,
  material_id INT NOT NULL,
  price_month DATE NOT NULL COMMENT 'Tháng (ngày đầu tháng)',
  market_avg_price BIGINT NOT NULL COMMENT 'Giá trung bình thị trường. Đơn vị: VND/đơn vị',
  market_min_price BIGINT NOT NULL COMMENT 'Giá thấp nhất. Đơn vị: VND/đơn vị',
  market_max_price BIGINT NOT NULL COMMENT 'Giá cao nhất. Đơn vị: VND/đơn vị',
  INDEX idx_material_month (material_id, price_month),
  UNIQUE KEY uk_material_month (material_id, price_month),
  FOREIGN KEY (material_id) REFERENCES materials(material_id)
) COMMENT = 'Chỉ số giá vật liệu xây dựng theo tháng — benchmark so sánh giá mua';

-- 5. P&L theo dự án × tháng
CREATE TABLE project_financials (
  financial_id INT AUTO_INCREMENT PRIMARY KEY,
  project_id VARCHAR(10) NOT NULL,
  fin_month DATE NOT NULL COMMENT 'Tháng tài chính (ngày đầu tháng)',
  revenue_recognized BIGINT NOT NULL COMMENT 'Doanh thu ghi nhận trong tháng. Đơn vị: triệu VND',
  cogs BIGINT NOT NULL COMMENT 'Giá vốn / chi phí trực tiếp. Đơn vị: triệu VND',
  gross_profit BIGINT NOT NULL COMMENT 'Lợi nhuận gộp = revenue - cogs. Đơn vị: triệu VND',
  gross_margin_pct DECIMAL(5,2) NOT NULL COMMENT 'Biên lợi nhuận gộp. Đơn vị: %',
  INDEX idx_project_month (project_id, fin_month),
  UNIQUE KEY uk_project_month (project_id, fin_month),
  FOREIGN KEY (project_id) REFERENCES projects(project_id)
) COMMENT = 'Kết quả tài chính (P&L) theo dự án × tháng — theo dõi margin';

-- 6. Lịch sử đấu thầu
CREATE TABLE bid_history (
  bid_id INT AUTO_INCREMENT PRIMARY KEY,
  project_id VARCHAR(10) COMMENT 'FK → projects (NULL nếu thất bại / dự án không trong danh mục)',
  tender_name VARCHAR(300) NOT NULL COMMENT 'Tên gói thầu',
  tender_owner VARCHAR(200) COMMENT 'Chủ đầu tư / Bên mời thầu',
  project_subtype VARCHAR(50) COMMENT 'Loại công trình: giao_thong, dan_dung, thuy_loi, ha_tang',
  estimated_value BIGINT NOT NULL COMMENT 'Giá gói thầu (giá dự toán). Đơn vị: triệu VND',
  bid_price BIGINT NOT NULL COMMENT 'Giá dự thầu của Lam Sơn. Đơn vị: triệu VND',
  bid_ratio DECIMAL(5,4) NOT NULL COMMENT 'Tỷ lệ giá thầu = bid_price / estimated_value',
  competitors_count INT COMMENT 'Số nhà thầu cạnh tranh',
  result ENUM('trung_thau','that_bai') NOT NULL COMMENT 'Kết quả đấu thầu',
  bid_date DATE NOT NULL COMMENT 'Ngày nộp hồ sơ thầu',
  award_date DATE COMMENT 'Ngày công bố kết quả',
  notes VARCHAR(300),
  INDEX idx_project (project_id),
  INDEX idx_subtype (project_subtype),
  INDEX idx_date (bid_date),
  FOREIGN KEY (project_id) REFERENCES projects(project_id)
) COMMENT = 'Lịch sử đấu thầu — phân tích chiến lược giá thầu và tỷ lệ trúng';

-- 7. Công nợ phải thu
CREATE TABLE receivables (
  receivable_id INT AUTO_INCREMENT PRIMARY KEY,
  project_id VARCHAR(10) NOT NULL,
  counterparty_id INT COMMENT 'FK → counterparties',
  milestone_name VARCHAR(200) COMMENT 'Mốc nghiệm thu / đợt thanh toán',
  amount BIGINT NOT NULL COMMENT 'Số tiền phải thu. Đơn vị: triệu VND',
  due_date DATE NOT NULL COMMENT 'Ngày đáo hạn thanh toán',
  expected_collection_date DATE COMMENT 'Ngày dự kiến thu được (NULL nếu chưa chắc)',
  actual_paid_date DATE COMMENT 'Ngày thực thu (NULL nếu chưa thu)',
  status ENUM('chua_thanh_toan','da_thanh_toan','qua_han','du_kien') NOT NULL COMMENT 'Trạng thái',
  notes VARCHAR(300),
  INDEX idx_project (project_id),
  INDEX idx_due_date (due_date),
  INDEX idx_status (status),
  FOREIGN KEY (project_id) REFERENCES projects(project_id),
  FOREIGN KEY (counterparty_id) REFERENCES counterparties(counterparty_id)
) COMMENT = 'Công nợ phải thu — theo dõi khoản thu từ chủ đầu tư / khách hàng';

-- 8. Công nợ phải trả
CREATE TABLE payables (
  payable_id INT AUTO_INCREMENT PRIMARY KEY,
  project_id VARCHAR(10) NOT NULL,
  counterparty_id INT COMMENT 'FK → counterparties',
  category ENUM('nha_thau_phu','vat_lieu','nhan_cong','thue','lai_vay','khac') NOT NULL COMMENT 'Loại chi phí',
  description VARCHAR(300) COMMENT 'Mô tả khoản trả',
  amount BIGINT NOT NULL COMMENT 'Số tiền phải trả. Đơn vị: triệu VND',
  due_date DATE NOT NULL COMMENT 'Ngày đáo hạn',
  actual_paid_date DATE COMMENT 'Ngày thực trả (NULL nếu chưa trả)',
  status ENUM('chua_thanh_toan','da_thanh_toan','qua_han') NOT NULL COMMENT 'Trạng thái',
  INDEX idx_project (project_id),
  INDEX idx_due_date (due_date),
  INDEX idx_status (status),
  FOREIGN KEY (project_id) REFERENCES projects(project_id),
  FOREIGN KEY (counterparty_id) REFERENCES counterparties(counterparty_id)
) COMMENT = 'Công nợ phải trả — NTP, NCC, nhân công, thuế, lãi vay';

-- 9. Dòng tiền thực tế theo tháng
CREATE TABLE cash_flow_actual (
  cash_flow_id INT AUTO_INCREMENT PRIMARY KEY,
  flow_month DATE NOT NULL COMMENT 'Tháng (ngày đầu tháng)',
  opening_balance BIGINT NOT NULL COMMENT 'Số dư đầu kỳ. Đơn vị: triệu VND',
  total_inflow BIGINT NOT NULL COMMENT 'Tổng dòng tiền vào. Đơn vị: triệu VND',
  total_outflow BIGINT NOT NULL COMMENT 'Tổng dòng tiền ra. Đơn vị: triệu VND',
  net_cash_flow BIGINT NOT NULL COMMENT 'Dòng tiền thuần = inflow - outflow. Đơn vị: triệu VND',
  closing_balance BIGINT NOT NULL COMMENT 'Số dư cuối kỳ = opening + net. Đơn vị: triệu VND',
  UNIQUE KEY uk_month (flow_month),
  INDEX idx_month (flow_month)
) COMMENT = 'Dòng tiền thực tế theo tháng — tổng hợp tất cả dự án';

-- 10. Từng unit BĐS (căn/lô)
CREATE TABLE real_estate_units (
  unit_id INT AUTO_INCREMENT PRIMARY KEY,
  project_id VARCHAR(10) NOT NULL,
  unit_type_id INT NOT NULL,
  unit_code VARCHAR(30) NOT NULL COMMENT 'Mã căn/lô (VD: SH-01, LK-A12, DN-015)',
  area_m2 DECIMAL(10,2) NOT NULL COMMENT 'Diện tích. Đơn vị: m²',
  listed_price BIGINT NOT NULL COMMENT 'Giá niêm yết. Đơn vị: triệu VND',
  actual_price BIGINT COMMENT 'Giá bán thực tế (NULL nếu chưa bán). Đơn vị: triệu VND',
  status ENUM('chua_ban','dat_coc','da_ban','da_ban_giao') NOT NULL DEFAULT 'chua_ban' COMMENT 'Trạng thái bán hàng',
  listing_date DATE NOT NULL COMMENT 'Ngày đưa vào danh mục bán',
  reservation_date DATE COMMENT 'Ngày đặt cọc',
  sale_date DATE COMMENT 'Ngày ký hợp đồng mua bán',
  handover_date DATE COMMENT 'Ngày bàn giao',
  buyer_type ENUM('ca_nhan','dau_tu','doanh_nghiep') COMMENT 'Loại khách mua',
  floor_number INT COMMENT 'Tầng (shophouse/liền kề)',
  block VARCHAR(20) COMMENT 'Block/phân khu',
  position VARCHAR(50) COMMENT 'Vị trí (góc, mặt đường, trong...)',
  INDEX idx_project (project_id),
  INDEX idx_status (status),
  INDEX idx_unit_type (unit_type_id),
  INDEX idx_sale_date (sale_date),
  FOREIGN KEY (project_id) REFERENCES projects(project_id),
  FOREIGN KEY (unit_type_id) REFERENCES re_unit_types(unit_type_id)
) COMMENT = 'Chi tiết từng sản phẩm BĐS (căn/lô) — theo dõi bán hàng và tồn kho';

-- 11. Doanh số BĐS theo tháng (aggregated)
CREATE TABLE re_sales_monthly (
  sales_monthly_id INT AUTO_INCREMENT PRIMARY KEY,
  project_id VARCHAR(10) NOT NULL,
  sales_month DATE NOT NULL COMMENT 'Tháng (ngày đầu tháng)',
  units_sold INT NOT NULL DEFAULT 0 COMMENT 'Số sản phẩm bán được trong tháng',
  revenue BIGINT NOT NULL DEFAULT 0 COMMENT 'Doanh thu bán hàng trong tháng. Đơn vị: triệu VND',
  units_available INT NOT NULL COMMENT 'Số sản phẩm còn lại cuối tháng',
  INDEX idx_project_month (project_id, sales_month),
  UNIQUE KEY uk_project_month (project_id, sales_month),
  FOREIGN KEY (project_id) REFERENCES projects(project_id)
) COMMENT = 'Thống kê bán hàng BĐS theo dự án × tháng — theo dõi tốc độ hấp thụ';

-- 12. Tài chính dự án BĐS (vay vốn)
CREATE TABLE project_financing (
  financing_id INT AUTO_INCREMENT PRIMARY KEY,
  project_id VARCHAR(10) NOT NULL,
  bank_name VARCHAR(200) NOT NULL COMMENT 'Ngân hàng cho vay',
  loan_amount BIGINT NOT NULL COMMENT 'Hạn mức vay. Đơn vị: triệu VND',
  disbursed_amount BIGINT NOT NULL DEFAULT 0 COMMENT 'Đã giải ngân. Đơn vị: triệu VND',
  interest_rate DECIMAL(5,2) NOT NULL COMMENT 'Lãi suất năm. Đơn vị: %',
  disbursement_date DATE COMMENT 'Ngày giải ngân',
  maturity_date DATE COMMENT 'Ngày đáo hạn',
  monthly_interest BIGINT COMMENT 'Lãi vay hàng tháng ước tính. Đơn vị: triệu VND',
  status ENUM('dang_vay','da_tat_toan') DEFAULT 'dang_vay',
  INDEX idx_project (project_id),
  FOREIGN KEY (project_id) REFERENCES projects(project_id)
) COMMENT = 'Khoản vay ngân hàng theo dự án — tính chi phí vốn tồn kho BĐS';

-- =============================================================================
-- METADATA TABLES
-- =============================================================================

CREATE TABLE _meta_tables (
  table_name VARCHAR(64) PRIMARY KEY,
  table_type ENUM('dimension','fact','metadata') NOT NULL,
  description_vi VARCHAR(500) NOT NULL COMMENT 'Mô tả bảng bằng tiếng Việt',
  description_en VARCHAR(500) COMMENT 'Mô tả bảng bằng tiếng Anh',
  row_count_approx INT COMMENT 'Số dòng ước tính',
  grain VARCHAR(300) COMMENT 'Mức chi tiết: 1 dòng = ?'
) COMMENT = 'Metadata: mô tả tất cả bảng trong database';

CREATE TABLE _meta_columns (
  id INT AUTO_INCREMENT PRIMARY KEY,
  table_name VARCHAR(64) NOT NULL,
  column_name VARCHAR(64) NOT NULL,
  data_type VARCHAR(50) NOT NULL,
  description_vi VARCHAR(500) NOT NULL COMMENT 'Mô tả cột bằng tiếng Việt',
  unit VARCHAR(50) COMMENT 'Đơn vị (triệu VND, %, ngày, m², VND/kg...)',
  is_key TINYINT(1) DEFAULT 0 COMMENT '1 = PK hoặc FK',
  fk_references VARCHAR(100) COMMENT 'Bảng.cột tham chiếu (nếu FK)',
  INDEX idx_table (table_name)
) COMMENT = 'Metadata: mô tả tất cả cột quan trọng';

CREATE TABLE _meta_kpi (
  kpi_id INT AUTO_INCREMENT PRIMARY KEY,
  kpi_name VARCHAR(100) NOT NULL COMMENT 'Tên KPI (tiếng Anh)',
  kpi_name_vi VARCHAR(200) NOT NULL COMMENT 'Tên KPI (tiếng Việt)',
  formula_sql TEXT NOT NULL COMMENT 'Công thức SQL để tính KPI',
  description_vi TEXT NOT NULL COMMENT 'Giải thích ý nghĩa KPI',
  related_tables VARCHAR(300) COMMENT 'Các bảng liên quan',
  related_questions VARCHAR(100) COMMENT 'Câu hỏi liên quan (Q1-Q5)'
) COMMENT = 'Metadata: danh sách KPI và công thức tính';

CREATE TABLE _meta_glossary (
  term_id INT AUTO_INCREMENT PRIMARY KEY,
  term_vi VARCHAR(100) NOT NULL COMMENT 'Thuật ngữ tiếng Việt',
  term_en VARCHAR(100) COMMENT 'Thuật ngữ tiếng Anh',
  definition_vi TEXT NOT NULL COMMENT 'Giải thích tiếng Việt',
  domain ENUM('xay_dung','bat_dong_san','tai_chinh','chung') NOT NULL COMMENT 'Lĩnh vực'
) COMMENT = 'Metadata: từ điển thuật ngữ ngành xây dựng + BĐS Việt Nam';
