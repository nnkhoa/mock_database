-- ============================================================
-- 01_ddl_schema.sql
-- Database: dtg_distribution_demo
-- Đại Thuận Group (DTG) — Phân phối thực phẩm đông lạnh
-- Schema: 11 dim_* + 8 fact_* + 4 _meta_* = 23 tables
-- ============================================================


DROP DATABASE IF EXISTS `dtg_distribution_demo`;
CREATE DATABASE `dtg_distribution_demo` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `dtg_distribution_demo`;

CREATE TABLE dim_calendar (
  `date` DATE PRIMARY KEY,
  year SMALLINT NOT NULL,
  quarter TINYINT NOT NULL,
  month TINYINT NOT NULL,
  week TINYINT NOT NULL,
  day_of_week TINYINT NOT NULL,
  is_tet_period TINYINT(1) NOT NULL DEFAULT 0,
  is_weekend TINYINT(1) NOT NULL DEFAULT 0,
  lunar_date VARCHAR(20),
  season VARCHAR(20)
) ENGINE=InnoDB COMMENT='Bảng lịch, 730 ngày, flag Tết và cuối tuần';

CREATE TABLE dim_currency (
  currency_code CHAR(3) PRIMARY KEY,
  currency_name VARCHAR(50) NOT NULL,
  country VARCHAR(50)
) ENGINE=InnoDB COMMENT='Tiền tệ: VND/KRW/EUR';

CREATE TABLE dim_principal (
  principal_id INT PRIMARY KEY,
  principal_name VARCHAR(100) NOT NULL,
  country VARCHAR(50),
  source_currency CHAR(3),
  imported_content_pct DECIMAL(5,2) COMMENT 'Tỷ lệ nguyên liệu nhập khẩu, %',
  partnership_since YEAR,
  FOREIGN KEY (source_currency) REFERENCES dim_currency(currency_code)
) ENGINE=InnoDB COMMENT='6 nhà cung cấp chính (Binggrae, CJ Food, Ammerland, DongWon, Tashun, M.Ngon)';

CREATE TABLE dim_product_category (
  category_id INT PRIMARY KEY,
  category_name_vi VARCHAR(100) NOT NULL,
  category_name_en VARCHAR(100),
  parent_category VARCHAR(50)
) ENGINE=InnoDB COMMENT='Danh mục sản phẩm';

CREATE TABLE dim_product (
  product_id INT PRIMARY KEY,
  sku_code VARCHAR(30) NOT NULL UNIQUE,
  product_name_vi VARCHAR(200) NOT NULL,
  category_id INT NOT NULL,
  principal_id INT NOT NULL,
  unit_size VARCHAR(30),
  package_type VARCHAR(30),
  shelf_life_days INT COMMENT 'Hạn sử dụng, ngày',
  retail_price_base DECIMAL(12,2) COMMENT 'Giá bán base, VND',
  cogs_baseline DECIMAL(12,2) COMMENT 'Giá vốn base tại FX baseline, VND',
  launch_date DATE,
  discontinue_date DATE NULL,
  is_active TINYINT(1) DEFAULT 1,
  popularity_weight DECIMAL(4,2) DEFAULT 1.00,
  FOREIGN KEY (category_id) REFERENCES dim_product_category(category_id),
  FOREIGN KEY (principal_id) REFERENCES dim_principal(principal_id)
) ENGINE=InnoDB COMMENT='~115 SKUs, giá VND, shelf_life ngày';

CREATE TABLE dim_region (
  region_id INT PRIMARY KEY,
  region_name VARCHAR(50) NOT NULL UNIQUE,
  region_code VARCHAR(10)
) ENGINE=InnoDB COMMENT='6 vùng kinh tế';

CREATE TABLE dim_province (
  province_id INT PRIMARY KEY,
  province_name VARCHAR(100) NOT NULL,
  region_id INT NOT NULL,
  population INT COMMENT 'Dân số',
  gdp_per_capita DECIMAL(12,2) COMMENT 'GDP/capita triệu VND',
  pos_potential_count INT COMMENT 'Số POS tiềm năng',
  FOREIGN KEY (region_id) REFERENCES dim_region(region_id)
) ENGINE=InnoDB COMMENT='63 tỉnh thành';

CREATE TABLE dim_branch (
  branch_id INT PRIMARY KEY,
  branch_name VARCHAR(100) NOT NULL,
  branch_code VARCHAR(20) NOT NULL UNIQUE,
  province_id INT NOT NULL,
  branch_type VARCHAR(30) COMMENT 'HO/Regional/Satellite',
  monthly_opex_vnd DECIMAL(15,2) COMMENT 'OpEx tháng, VND',
  staff_count INT,
  year_opened YEAR,
  warehouse_capacity_m3 INT,
  FOREIGN KEY (province_id) REFERENCES dim_province(province_id)
) ENGINE=InnoDB COMMENT='7 chi nhánh DTG';

CREATE TABLE dim_channel (
  channel_id INT PRIMARY KEY,
  channel_name VARCHAR(30) NOT NULL UNIQUE,
  channel_description_vi VARCHAR(255)
) ENGINE=InnoDB COMMENT='MT/HORECA/GT/Online';

CREATE TABLE dim_store (
  store_id INT PRIMARY KEY,
  store_name VARCHAR(200) NOT NULL,
  store_code VARCHAR(30) NOT NULL,
  channel_id INT NOT NULL,
  chain_name VARCHAR(100),
  province_id INT NOT NULL,
  district VARCHAR(100),
  branch_id INT NOT NULL,
  opened_date DATE,
  competitor_present TINYINT(1) NOT NULL DEFAULT 0,
  store_tier CHAR(1) NOT NULL,
  is_active TINYINT(1) DEFAULT 1,
  FOREIGN KEY (channel_id) REFERENCES dim_channel(channel_id),
  FOREIGN KEY (province_id) REFERENCES dim_province(province_id),
  FOREIGN KEY (branch_id) REFERENCES dim_branch(branch_id),
  INDEX idx_store_prov (province_id),
  INDEX idx_store_branch (branch_id),
  INDEX idx_store_channel (channel_id)
) ENGINE=InnoDB COMMENT='~5.000 POS';

CREATE TABLE dim_warehouse (
  warehouse_id INT PRIMARY KEY,
  warehouse_name VARCHAR(100) NOT NULL,
  branch_id INT NOT NULL,
  storage_type VARCHAR(20) COMMENT 'Frozen/Chilled/Ambient',
  capacity_m3 INT,
  FOREIGN KEY (branch_id) REFERENCES dim_branch(branch_id)
) ENGINE=InnoDB COMMENT='Kho lạnh theo branch';

CREATE TABLE fact_sales (
  sales_id BIGINT PRIMARY KEY,
  `date` DATE NOT NULL,
  store_id INT NOT NULL,
  product_id INT NOT NULL,
  branch_id INT NOT NULL,
  channel_id INT NOT NULL,
  quantity INT NOT NULL,
  unit_price_vnd DECIMAL(12,2) NOT NULL,
  gross_amount_vnd DECIMAL(15,2) NOT NULL,
  discount_vnd DECIMAL(15,2) NOT NULL DEFAULT 0,
  net_amount_vnd DECIMAL(15,2) NOT NULL,
  cogs_unit_vnd DECIMAL(12,2) NOT NULL,
  cogs_total_vnd DECIMAL(15,2) NOT NULL,
  fx_rate_used DECIMAL(12,4),
  INDEX idx_fs_date (`date`),
  INDEX idx_fs_store_date (store_id,`date`),
  INDEX idx_fs_product_date (product_id,`date`),
  INDEX idx_fs_branch_date (branch_id,`date`),
  INDEX idx_fs_channel_date (channel_id,`date`),
  FOREIGN KEY (`date`) REFERENCES dim_calendar(`date`),
  FOREIGN KEY (store_id) REFERENCES dim_store(store_id),
  FOREIGN KEY (product_id) REFERENCES dim_product(product_id),
  FOREIGN KEY (branch_id) REFERENCES dim_branch(branch_id),
  FOREIGN KEY (channel_id) REFERENCES dim_channel(channel_id)
) ENGINE=InnoDB COMMENT='Sell-in transaction-level';

CREATE TABLE fact_sales_out (
  out_id BIGINT PRIMARY KEY,
  `date` DATE NOT NULL,
  store_id INT NOT NULL,
  product_id INT NOT NULL,
  quantity_sold INT NOT NULL,
  revenue_vnd DECIMAL(15,2) NOT NULL,
  INDEX idx_so_date (`date`),
  INDEX idx_so_store_date (store_id,`date`),
  INDEX idx_so_product_date (product_id,`date`),
  FOREIGN KEY (store_id) REFERENCES dim_store(store_id),
  FOREIGN KEY (product_id) REFERENCES dim_product(product_id)
) ENGINE=InnoDB COMMENT='Sell-out POS scan (weekly granularity)';

CREATE TABLE fact_inventory (
  inv_id BIGINT PRIMARY KEY,
  snapshot_date DATE NOT NULL,
  product_id INT NOT NULL,
  warehouse_id INT NOT NULL,
  quantity_on_hand INT NOT NULL,
  unit_cost_vnd DECIMAL(12,2) NOT NULL,
  total_value_vnd DECIMAL(15,2) NOT NULL,
  manufactured_date DATE,
  expiry_date DATE,
  days_to_expire INT,
  INDEX idx_inv_snap (snapshot_date),
  INDEX idx_inv_prod_snap (product_id,snapshot_date),
  INDEX idx_inv_wh_snap (warehouse_id,snapshot_date),
  FOREIGN KEY (product_id) REFERENCES dim_product(product_id),
  FOREIGN KEY (warehouse_id) REFERENCES dim_warehouse(warehouse_id)
) ENGINE=InnoDB COMMENT='Tồn kho weekly snapshot';

CREATE TABLE fact_fx_rate (
  `date` DATE NOT NULL,
  currency_code CHAR(3) NOT NULL,
  rate_to_vnd DECIMAL(14,4) NOT NULL,
  PRIMARY KEY (`date`, currency_code),
  FOREIGN KEY (currency_code) REFERENCES dim_currency(currency_code)
) ENGINE=InnoDB COMMENT='Tỷ giá ngoại tệ → VND theo ngày';

CREATE TABLE fact_trade_promotion (
  promo_id INT PRIMARY KEY,
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  store_id INT NULL,
  region_id INT NULL,
  product_id INT NULL,
  principal_id INT NULL,
  promo_type VARCHAR(30) NOT NULL COMMENT 'BOGO/price_down/display_fee/loyalty',
  planned_amount_vnd DECIMAL(15,2) NOT NULL,
  actual_amount_vnd DECIMAL(15,2) NOT NULL,
  status VARCHAR(20) NOT NULL,
  description_vi VARCHAR(500),
  INDEX idx_tp_start (start_date, end_date),
  INDEX idx_tp_principal (principal_id),
  INDEX idx_tp_product (product_id)
) ENGINE=InnoDB COMMENT='Trade promotion campaigns';

CREATE TABLE fact_operating_cost (
  cost_id INT PRIMARY KEY,
  `year_month` CHAR(7) NOT NULL COMMENT 'YYYY-MM',
  branch_id INT NOT NULL,
  cost_category VARCHAR(30) NOT NULL COMMENT 'rent/staff/fuel_logistics/utility/marketing/admin',
  amount_vnd DECIMAL(15,2) NOT NULL,
  INDEX idx_oc_branch (branch_id, `year_month`),
  FOREIGN KEY (branch_id) REFERENCES dim_branch(branch_id)
) ENGINE=InnoDB COMMENT='Chi phí vận hành tháng × chi nhánh × loại';

CREATE TABLE fact_budget (
  budget_id INT PRIMARY KEY,
  `year_month` CHAR(7) NOT NULL,
  dimension VARCHAR(30) NOT NULL COMMENT 'total/principal/region/branch/channel',
  dimension_value VARCHAR(100) NOT NULL,
  metric VARCHAR(30) NOT NULL COMMENT 'revenue/gross_profit/margin_pct/units',
  target_value DECIMAL(18,4) NOT NULL,
  INDEX idx_bg_dim (`year_month`, dimension, metric)
) ENGINE=InnoDB COMMENT='Kế hoạch tháng theo dimension';

CREATE TABLE fact_route_coverage (
  coverage_id INT PRIMARY KEY,
  branch_id INT NOT NULL,
  store_id INT NOT NULL,
  distance_km DECIMAL(6,1) NOT NULL,
  route_cost_per_visit_vnd DECIMAL(10,2),
  is_primary TINYINT(1) NOT NULL DEFAULT 1,
  INDEX idx_rc_branch (branch_id),
  INDEX idx_rc_store (store_id),
  FOREIGN KEY (branch_id) REFERENCES dim_branch(branch_id),
  FOREIGN KEY (store_id) REFERENCES dim_store(store_id)
) ENGINE=InnoDB COMMENT='Map chi nhánh → store, distance, cost — phân tích overlap';

CREATE TABLE _meta_tables (
  table_name VARCHAR(64) PRIMARY KEY,
  description_vi VARCHAR(500),
  description_en VARCHAR(500),
  business_context VARCHAR(1000),
  row_count_approx INT
) ENGINE=InnoDB;

CREATE TABLE _meta_columns (
  table_name VARCHAR(64) NOT NULL,
  column_name VARCHAR(64) NOT NULL,
  data_type VARCHAR(50),
  description_vi VARCHAR(500),
  unit VARCHAR(30),
  example_values VARCHAR(500),
  PRIMARY KEY (table_name, column_name)
) ENGINE=InnoDB;

CREATE TABLE _meta_kpi (
  kpi_name_vi VARCHAR(100) PRIMARY KEY,
  kpi_name_en VARCHAR(100),
  formula_sql TEXT,
  description_vi VARCHAR(1000),
  related_questions VARCHAR(50)
) ENGINE=InnoDB;

CREATE TABLE _meta_glossary (
  term_vi VARCHAR(100) PRIMARY KEY,
  term_en VARCHAR(100),
  definition VARCHAR(1000),
  related_tables VARCHAR(500)
) ENGINE=InnoDB;

