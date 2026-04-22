-- ============================================================
-- 01_ddl_schema.sql
-- Database: menas_demo
-- Menas Group — Multi-Business Demo Schema
-- ============================================================

USE menas_demo;

-- ============================================================
-- DIMENSION TABLES
-- ============================================================

CREATE TABLE business_units (
  id VARCHAR(20) PRIMARY KEY,
  name VARCHAR(100) NOT NULL COMMENT 'Tên mảng kinh doanh',
  description TEXT COMMENT 'Mô tả',
  revenue_model VARCHAR(100) COMMENT 'Mô hình doanh thu'
) COMMENT='Các mảng kinh doanh của Menas Group';

CREATE TABLE locations (
  id VARCHAR(10) PRIMARY KEY,
  name VARCHAR(200) NOT NULL,
  business_unit_id VARCHAR(20) NOT NULL,
  location_type VARCHAR(50) COMMENT 'TTTM/Siêu thị/F&B/Duty Free/Beauty',
  address TEXT,
  city VARCHAR(50),
  district VARCHAR(50),
  sqm DECIMAL(10,2) COMMENT 'Diện tích (m²)',
  opening_date DATE,
  status VARCHAR(20) DEFAULT 'active',
  FOREIGN KEY (business_unit_id) REFERENCES business_units(id)
) COMMENT='Tất cả địa điểm kinh doanh';

CREATE TABLE product_categories (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL COMMENT 'Tên nhóm hàng',
  description TEXT,
  base_margin_pct DECIMAL(5,2) COMMENT 'Biên lợi nhuận gộp cơ bản (%)'
) COMMENT='Nhóm hàng siêu thị';

CREATE TABLE products (
  id INT AUTO_INCREMENT PRIMARY KEY,
  sku VARCHAR(20) UNIQUE NOT NULL,
  name VARCHAR(200) NOT NULL COMMENT 'Tên sản phẩm',
  category_id INT NOT NULL,
  origin VARCHAR(20) COMMENT 'domestic/imported',
  base_price_vnd DECIMAL(15,2) COMMENT 'Giá bán cơ bản (VND)',
  cost_price_vnd DECIMAL(15,2) COMMENT 'Giá vốn (VND)',
  popularity_weight DECIMAL(5,3) COMMENT 'Trọng số phổ biến (Pareto)',
  FOREIGN KEY (category_id) REFERENCES product_categories(id)
) COMMENT='Danh mục sản phẩm siêu thị (~500 SKU)';

CREATE TABLE fb_outlets (
  id VARCHAR(10) PRIMARY KEY,
  location_id VARCHAR(10) NOT NULL,
  name VARCHAR(200) NOT NULL,
  cuisine_type VARCHAR(100),
  avg_check_per_person_vnd DECIMAL(15,2),
  seats INT,
  sqm DECIMAL(10,2),
  opening_date DATE,
  FOREIGN KEY (location_id) REFERENCES locations(id)
) COMMENT='Chi tiết các outlet F&B';

CREATE TABLE tenants (
  id VARCHAR(10) PRIMARY KEY,
  name VARCHAR(200) NOT NULL,
  category VARCHAR(100) COMMENT 'Ngành hàng tenant',
  floor VARCHAR(10),
  sqm_rented DECIMAL(10,2) COMMENT 'Diện tích thuê (m²)',
  rent_per_sqm_monthly DECIMAL(15,2) COMMENT 'Giá thuê/m²/tháng (VND)',
  lease_start DATE,
  lease_end DATE,
  lease_type VARCHAR(20) DEFAULT 'variable' COMMENT 'fixed/variable',
  revenue_share_pct DECIMAL(5,2) COMMENT 'Tỷ lệ chia doanh thu (%)',
  estimated_operating_margin_pct DECIMAL(5,2) COMMENT 'Ước tính biên LN hoạt động (%)',
  location_id VARCHAR(10) NOT NULL,
  FOREIGN KEY (location_id) REFERENCES locations(id)
) COMMENT='Tenant thuê mặt bằng tại TTTM';

CREATE TABLE planned_locations (
  id VARCHAR(10) PRIMARY KEY,
  address TEXT,
  district VARCHAR(50),
  city VARCHAR(50),
  sqm DECIMAL(10,2),
  estimated_monthly_rent_vnd DECIMAL(15,2),
  population_density VARCHAR(20) COMMENT 'Cao/Trung bình/Thấp',
  avg_income_level VARCHAR(20) COMMENT 'Rất cao/Cao/Trung bình',
  competitor_count INT,
  competitor_notes TEXT
) COMMENT='Địa điểm dự kiến mở rộng';

CREATE TABLE employees_summary (
  id INT AUTO_INCREMENT PRIMARY KEY,
  location_id VARCHAR(10) NOT NULL,
  month DATE NOT NULL COMMENT 'Tháng (YYYY-MM-01)',
  headcount INT NOT NULL,
  total_labor_cost_vnd DECIMAL(15,2) COMMENT 'Tổng chi phí nhân sự (VND)',
  FOREIGN KEY (location_id) REFERENCES locations(id),
  UNIQUE KEY (location_id, month)
) COMMENT='Headcount theo location theo tháng';

-- ============================================================
-- FACT TABLES
-- ============================================================

CREATE TABLE monthly_revenue (
  id INT AUTO_INCREMENT PRIMARY KEY,
  business_unit_id VARCHAR(20) NOT NULL,
  location_id VARCHAR(10) NOT NULL,
  month DATE NOT NULL COMMENT 'Tháng (YYYY-MM-01)',
  revenue_vnd DECIMAL(18,2) NOT NULL COMMENT 'Doanh thu (VND)',
  cost_vnd DECIMAL(18,2) COMMENT 'Chi phí (VND)',
  profit_vnd DECIMAL(18,2) COMMENT 'Lợi nhuận (VND)',
  FOREIGN KEY (business_unit_id) REFERENCES business_units(id),
  FOREIGN KEY (location_id) REFERENCES locations(id),
  UNIQUE KEY (business_unit_id, location_id, month),
  INDEX idx_month (month),
  INDEX idx_bu (business_unit_id)
) COMMENT='Doanh thu tổng hợp theo mảng, địa điểm, tháng';

CREATE TABLE supermarket_daily_sales (
  id INT AUTO_INCREMENT PRIMARY KEY,
  date DATE NOT NULL,
  location_id VARCHAR(10) NOT NULL,
  product_id INT NOT NULL,
  quantity INT NOT NULL COMMENT 'Số lượng',
  selling_price_vnd DECIMAL(15,2) NOT NULL COMMENT 'Giá bán (VND)',
  cost_price_vnd DECIMAL(15,2) NOT NULL COMMENT 'Giá vốn (VND)',
  discount_amount_vnd DECIMAL(15,2) DEFAULT 0 COMMENT 'Giảm giá (VND)',
  FOREIGN KEY (location_id) REFERENCES locations(id),
  FOREIGN KEY (product_id) REFERENCES products(id),
  INDEX idx_date (date),
  INDEX idx_location (location_id),
  INDEX idx_product (product_id)
) COMMENT='Bán hàng siêu thị chi tiết theo ngày, sản phẩm';

CREATE TABLE supermarket_shrinkage (
  id INT AUTO_INCREMENT PRIMARY KEY,
  location_id VARCHAR(10) NOT NULL,
  category_id INT NOT NULL,
  month DATE NOT NULL,
  shrinkage_amount_vnd DECIMAL(15,2) NOT NULL COMMENT 'Giá trị hao hụt (VND)',
  shrinkage_rate_pct DECIMAL(5,2) COMMENT 'Tỷ lệ hao hụt (%)',
  FOREIGN KEY (location_id) REFERENCES locations(id),
  FOREIGN KEY (category_id) REFERENCES product_categories(id),
  UNIQUE KEY (location_id, category_id, month)
) COMMENT='Hao hụt hàng hóa siêu thị theo tháng';

CREATE TABLE fb_monthly_revenue (
  id INT AUTO_INCREMENT PRIMARY KEY,
  outlet_id VARCHAR(10) NOT NULL,
  month DATE NOT NULL,
  revenue_vnd DECIMAL(18,2) NOT NULL,
  covers INT COMMENT 'Số lượt khách',
  avg_check_vnd DECIMAL(15,2) COMMENT 'Giá trị trung bình/lượt',
  FOREIGN KEY (outlet_id) REFERENCES fb_outlets(id),
  UNIQUE KEY (outlet_id, month)
) COMMENT='Doanh thu F&B theo outlet theo tháng';

CREATE TABLE fb_monthly_costs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  outlet_id VARCHAR(10) NOT NULL,
  month DATE NOT NULL,
  cost_type VARCHAR(30) NOT NULL COMMENT 'labor/food_cost/rent/utilities/marketing',
  channel VARCHAR(30) COMMENT 'digital/offline/event (only for marketing)',
  amount_vnd DECIMAL(18,2) NOT NULL,
  FOREIGN KEY (outlet_id) REFERENCES fb_outlets(id),
  INDEX idx_outlet_month (outlet_id, month),
  INDEX idx_cost_type (cost_type)
) COMMENT='Chi phí F&B theo outlet, tháng, loại chi phí';

CREATE TABLE tenant_monthly_revenue (
  id INT AUTO_INCREMENT PRIMARY KEY,
  tenant_id VARCHAR(10) NOT NULL,
  month DATE NOT NULL,
  gross_revenue_vnd DECIMAL(18,2) NOT NULL COMMENT 'Doanh thu gộp của tenant (VND)',
  FOREIGN KEY (tenant_id) REFERENCES tenants(id),
  UNIQUE KEY (tenant_id, month),
  INDEX idx_month (month)
) COMMENT='Doanh thu tenant theo tháng';

CREATE TABLE promotions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(200) NOT NULL,
  location_id VARCHAR(10),
  business_unit_id VARCHAR(20),
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  discount_pct DECIMAL(5,2) COMMENT 'Tỷ lệ giảm giá (%)',
  description TEXT,
  FOREIGN KEY (location_id) REFERENCES locations(id),
  FOREIGN KEY (business_unit_id) REFERENCES business_units(id)
) COMMENT='Chương trình khuyến mãi';

CREATE TABLE mall_events (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(200) NOT NULL,
  location_id VARCHAR(10),
  event_date DATE NOT NULL,
  event_type VARCHAR(50) COMMENT 'grand_opening/seasonal/marketing/community/maintenance',
  estimated_footfall_impact_pct DECIMAL(5,2) COMMENT 'Tác động lượt khách (%)',
  description TEXT,
  FOREIGN KEY (location_id) REFERENCES locations(id)
) COMMENT='Sự kiện tại TTTM';

CREATE TABLE mall_daily_footfall (
  id INT AUTO_INCREMENT PRIMARY KEY,
  location_id VARCHAR(10) NOT NULL,
  date DATE NOT NULL,
  segment VARCHAR(20) NOT NULL COMMENT 'airport/local',
  total_count INT NOT NULL COMMENT 'Lượt khách',
  FOREIGN KEY (location_id) REFERENCES locations(id),
  UNIQUE KEY (location_id, date, segment),
  INDEX idx_date (date)
) COMMENT='Lượt khách TTTM hàng ngày theo phân khúc';

CREATE TABLE airport_daily_passengers (
  id INT AUTO_INCREMENT PRIMARY KEY,
  date DATE NOT NULL UNIQUE,
  arrivals INT NOT NULL COMMENT 'Lượt đến',
  departures INT NOT NULL COMMENT 'Lượt đi',
  total_passengers INT NOT NULL COMMENT 'Tổng lượt khách',
  INDEX idx_date (date)
) COMMENT='Lượng khách sân bay Tân Sơn Nhất hàng ngày';

