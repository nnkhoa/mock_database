-- ============================================================
-- 01_ddl_schema.sql
-- Database: canifa_retail_demo
-- CANIFA Retail Fashion — Schema Definition
-- ============================================================


CREATE DATABASE IF NOT EXISTS canifa_retail_demo
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE canifa_retail_demo;

-- DIMENSION TABLES

CREATE TABLE regions (
  region_id VARCHAR(10) PRIMARY KEY,
  region_name VARCHAR(50) NOT NULL,
  region_name_en VARCHAR(50),
  description VARCHAR(200)
) COMMENT='Bảng khu vực địa lý';

CREATE TABLE stores (
  store_id VARCHAR(15) PRIMARY KEY,
  store_name VARCHAR(100) NOT NULL,
  region_id VARCHAR(10) NOT NULL,
  province VARCHAR(50) NOT NULL,
  district VARCHAR(50),
  address VARCHAR(200),
  store_type ENUM('Flagship','Standard','Outlet','TTTM') NOT NULL DEFAULT 'Standard',
  area_sqm DECIMAL(8,2) NOT NULL,
  monthly_rent DECIMAL(15,0),
  open_date DATE NOT NULL,
  status ENUM('Active','Closed','Renovating') DEFAULT 'Active',
  INDEX idx_region (region_id),
  INDEX idx_province (province),
  FOREIGN KEY (region_id) REFERENCES regions(region_id)
) COMMENT='Bảng cửa hàng — 110 cửa hàng Canifa toàn quốc';

CREATE TABLE categories (
  category_id VARCHAR(10) PRIMARY KEY,
  category_group VARCHAR(50) NOT NULL,
  category_name VARCHAR(50) NOT NULL,
  subcategory VARCHAR(50),
  description VARCHAR(200)
) COMMENT='Bảng phân loại sản phẩm';

CREATE TABLE products (
  product_id VARCHAR(15) PRIMARY KEY,
  product_name VARCHAR(150) NOT NULL,
  category_id VARCHAR(10) NOT NULL,
  season ENUM('Xuân-Hè','Thu-Đông','4 Mùa') NOT NULL,
  product_line VARCHAR(50),
  material VARCHAR(100),
  color VARCHAR(30),
  size_range VARCHAR(30),
  retail_price DECIMAL(12,0) NOT NULL,
  cost_price DECIMAL(12,0) NOT NULL,
  cost_price_new DECIMAL(12,0),
  popularity_weight DECIMAL(5,3) DEFAULT 1.000,
  launch_date DATE,
  status ENUM('Active','Discontinued','Seasonal') DEFAULT 'Active',
  INDEX idx_category (category_id),
  INDEX idx_season (season),
  INDEX idx_product_line (product_line),
  FOREIGN KEY (category_id) REFERENCES categories(category_id)
) COMMENT='Bảng sản phẩm — ~500 SKU';

CREATE TABLE channels (
  channel_id VARCHAR(10) PRIMARY KEY,
  channel_name VARCHAR(50) NOT NULL,
  channel_type ENUM('Offline','Online') NOT NULL,
  commission_rate DECIMAL(5,2) DEFAULT 0,
  shipping_subsidy_rate DECIMAL(5,2) DEFAULT 0
) COMMENT='Bảng kênh bán hàng';

CREATE TABLE promotions (
  promo_id VARCHAR(10) PRIMARY KEY,
  promo_name VARCHAR(100) NOT NULL,
  promo_type ENUM('Flash Sale','Seasonal','Bundle','Clearance','Member') NOT NULL,
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  discount_percent_min DECIMAL(5,2),
  discount_percent_max DECIMAL(5,2),
  applicable_channels VARCHAR(100),
  applicable_categories VARCHAR(200),
  marketing_spend DECIMAL(15,0) DEFAULT 0,
  platform_fee DECIMAL(15,0) DEFAULT 0,
  description VARCHAR(300),
  INDEX idx_dates (start_date, end_date)
) COMMENT='Bảng chương trình khuyến mại';

-- FACT TABLES

CREATE TABLE sales_transactions (
  transaction_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  transaction_date DATE NOT NULL,
  store_id VARCHAR(15),
  channel_id VARCHAR(10) NOT NULL,
  product_id VARCHAR(15) NOT NULL,
  promo_id VARCHAR(10),
  quantity INT NOT NULL,
  unit_price DECIMAL(12,0) NOT NULL,
  original_price DECIMAL(12,0) NOT NULL,
  discount_amount DECIMAL(12,0) DEFAULT 0,
  cost_price DECIMAL(12,0) NOT NULL,
  revenue DECIMAL(15,0) NOT NULL,
  gross_profit DECIMAL(15,0) NOT NULL,
  order_id VARCHAR(35),
  INDEX idx_date (transaction_date),
  INDEX idx_store (store_id),
  INDEX idx_channel (channel_id),
  INDEX idx_product (product_id),
  INDEX idx_promo (promo_id),
  INDEX idx_order (order_id),
  INDEX idx_date_store (transaction_date, store_id),
  INDEX idx_date_channel (transaction_date, channel_id),
  FOREIGN KEY (store_id) REFERENCES stores(store_id),
  FOREIGN KEY (channel_id) REFERENCES channels(channel_id),
  FOREIGN KEY (product_id) REFERENCES products(product_id),
  FOREIGN KEY (promo_id) REFERENCES promotions(promo_id)
) COMMENT='Bảng giao dịch bán hàng — grain: 1 dòng = 1 line item';

CREATE TABLE returns (
  return_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  return_date DATE NOT NULL,
  original_transaction_id BIGINT,
  store_id VARCHAR(15),
  channel_id VARCHAR(10) NOT NULL,
  product_id VARCHAR(15) NOT NULL,
  quantity INT NOT NULL,
  return_amount DECIMAL(15,0) NOT NULL,
  reason ENUM('Size không vừa','Lỗi sản phẩm','Không đúng mô tả','Đổi ý','Khác'),
  INDEX idx_date (return_date),
  INDEX idx_channel (channel_id),
  INDEX idx_product (product_id),
  FOREIGN KEY (product_id) REFERENCES products(product_id),
  FOREIGN KEY (channel_id) REFERENCES channels(channel_id)
) COMMENT='Bảng trả hàng';

CREATE TABLE inventory_snapshots (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  snapshot_date DATE NOT NULL,
  store_id VARCHAR(15) NOT NULL,
  product_id VARCHAR(15) NOT NULL,
  quantity_on_hand INT NOT NULL DEFAULT 0,
  quantity_received INT DEFAULT 0,
  quantity_sold INT DEFAULT 0,
  last_received_date DATE,
  INDEX idx_date (snapshot_date),
  INDEX idx_store_product (store_id, product_id),
  INDEX idx_snapshot (snapshot_date, store_id),
  UNIQUE KEY uk_snapshot (snapshot_date, store_id, product_id),
  FOREIGN KEY (store_id) REFERENCES stores(store_id),
  FOREIGN KEY (product_id) REFERENCES products(product_id)
) COMMENT='Bảng snapshot tồn kho cuối mỗi tháng';

CREATE TABLE store_costs (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  month_date DATE NOT NULL,
  store_id VARCHAR(15) NOT NULL,
  rent DECIMAL(15,0) NOT NULL,
  staff_cost DECIMAL(15,0) NOT NULL,
  utilities DECIMAL(15,0) DEFAULT 0,
  other_costs DECIMAL(15,0) DEFAULT 0,
  total_cost DECIMAL(15,0) NOT NULL,
  INDEX idx_month (month_date),
  INDEX idx_store (store_id),
  UNIQUE KEY uk_month_store (month_date, store_id),
  FOREIGN KEY (store_id) REFERENCES stores(store_id)
) COMMENT='Bảng chi phí vận hành cửa hàng theo tháng';

-- METADATA TABLES

CREATE TABLE _meta_tables (
  table_name VARCHAR(50) PRIMARY KEY,
  description_vi VARCHAR(500) NOT NULL,
  description_en VARCHAR(500),
  business_context VARCHAR(500),
  row_count_approx INT
) COMMENT='Metadata: mô tả các bảng';

CREATE TABLE _meta_columns (
  id INT AUTO_INCREMENT PRIMARY KEY,
  table_name VARCHAR(50) NOT NULL,
  column_name VARCHAR(50) NOT NULL,
  data_type VARCHAR(50),
  description_vi VARCHAR(300) NOT NULL,
  description_en VARCHAR(300),
  unit VARCHAR(30),
  example_values VARCHAR(200),
  INDEX idx_table (table_name)
) COMMENT='Metadata: mô tả chi tiết từng cột';

CREATE TABLE _meta_kpi (
  kpi_name VARCHAR(100) PRIMARY KEY,
  formula_sql TEXT NOT NULL,
  description_vi VARCHAR(300),
  related_questions VARCHAR(500)
) COMMENT='Metadata: định nghĩa KPI';

CREATE TABLE _meta_glossary (
  term_vi VARCHAR(100) PRIMARY KEY,
  term_en VARCHAR(100),
  definition VARCHAR(500) NOT NULL
) COMMENT='Metadata: thuật ngữ ngành';

