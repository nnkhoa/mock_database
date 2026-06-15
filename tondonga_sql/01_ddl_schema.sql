-- =====================================================================
-- 01_ddl_schema.sql — TÔN ĐÔNG Á (GDA) | tondonga_demo
-- CREATE DATABASE, tables (dim_/fact_/_meta_), indexes, COMMENTs
-- MySQL 8.0 | utf8mb4_unicode_ci
-- =====================================================================
CREATE DATABASE IF NOT EXISTS tondonga_demo
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE tondonga_demo;

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS fact_cogs;
DROP TABLE IF EXISTS fact_sales;
DROP TABLE IF EXISTS dim_target;
DROP TABLE IF EXISTS dim_hrc_price;
DROP TABLE IF EXISTS dim_customer;
DROP TABLE IF EXISTS dim_product;
DROP TABLE IF EXISTS dim_channel;
DROP TABLE IF EXISTS dim_region;
DROP TABLE IF EXISTS dim_calendar;
DROP TABLE IF EXISTS _meta_tables;
DROP TABLE IF EXISTS _meta_columns;
DROP TABLE IF EXISTS _meta_kpi;
DROP TABLE IF EXISTS _meta_glossary;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE dim_calendar (
  date          DATE PRIMARY KEY COMMENT 'Ngày',
  year          INT NOT NULL COMMENT 'Năm',
  quarter       INT NOT NULL COMMENT 'Quý (1-4)',
  month         INT NOT NULL COMMENT 'Tháng (1-12)',
  month_name_vi VARCHAR(20) COMMENT 'Tên tháng tiếng Việt',
  week          INT COMMENT 'Tuần trong năm',
  day_of_week   VARCHAR(12) COMMENT 'Thứ trong tuần',
  is_holiday    TINYINT(1) DEFAULT 0 COMMENT 'Ngày lễ/Tết (1=có)',
  season        VARCHAR(12) COMMENT 'Mùa: Mùa khô / Mùa mưa',
  KEY idx_cal_ym (year, month),
  KEY idx_cal_q (year, quarter)
) ENGINE=InnoDB COMMENT='Bảng lịch — phân tích thời gian/seasonality/YoY';

CREATE TABLE dim_region (
  region_id   INT PRIMARY KEY COMMENT 'Mã vùng',
  region_name VARCHAR(64) NOT NULL COMMENT 'Tên tỉnh/quốc gia',
  macro_area  VARCHAR(16) COMMENT 'Bắc/Trung/Nam/Nước ngoài',
  region_type VARCHAR(16) COMMENT 'Nội địa / Xuất khẩu',
  country     VARCHAR(32) COMMENT 'Quốc gia',
  KEY idx_region_area (macro_area),
  KEY idx_region_type (region_type)
) ENGINE=InnoDB COMMENT='Vùng địa lý nội địa (tỉnh) + xuất khẩu (quốc gia)';

CREATE TABLE dim_channel (
  channel_id   INT PRIMARY KEY COMMENT 'Mã kênh',
  channel_name VARCHAR(16) COMMENT 'Nội địa / Xuất khẩu',
  sub_channel  VARCHAR(32) COMMENT 'Đại lý cấp 1 / Nhà phân phối vùng / Dự án-Công trình / Xuất khẩu trực tiếp'
) ENGINE=InnoDB COMMENT='Kênh bán hàng';

CREATE TABLE dim_product (
  product_id                INT PRIMARY KEY COMMENT 'Mã sản phẩm',
  product_name              VARCHAR(96) NOT NULL COMMENT 'Tên SKU',
  product_group             VARCHAR(32) COMMENT 'Tôn màu/Tôn lạnh/Tôn kẽm/CRC/Thép hộp mạ kẽm',
  thickness_mm              DECIMAL(4,2) COMMENT 'Độ dày (mm)',
  asp_benchmark_vnd_per_ton DECIMAL(15,2) COMMENT 'ASP tham chiếu (VND/tấn)',
  margin_tier               VARCHAR(8) COMMENT 'Cao/Trung/Thấp',
  popularity_weight         DECIMAL(6,3) COMMENT 'Trọng số Pareto phân bổ volume',
  KEY idx_prod_group (product_group)
) ENGINE=InnoDB COMMENT='Danh mục sản phẩm, hierarchy group -> SKU';

CREATE TABLE dim_customer (
  customer_id   INT PRIMARY KEY COMMENT 'Mã khách hàng/đại lý',
  customer_name VARCHAR(128) NOT NULL COMMENT 'Tên đại lý/khách',
  region_id     INT COMMENT 'FK dim_region',
  channel_id    INT COMMENT 'FK dim_channel',
  customer_tier VARCHAR(8) COMMENT 'Lớn/Vừa/Nhỏ',
  KEY idx_cust_region (region_id),
  KEY idx_cust_channel (channel_id),
  CONSTRAINT fk_cust_region FOREIGN KEY (region_id) REFERENCES dim_region(region_id),
  CONSTRAINT fk_cust_channel FOREIGN KEY (channel_id) REFERENCES dim_channel(channel_id)
) ENGINE=InnoDB COMMENT='Khách hàng/đại lý';

CREATE TABLE dim_hrc_price (
  price_month     VARCHAR(7) PRIMARY KEY COMMENT 'Tháng YYYY-MM',
  hrc_usd_per_ton DECIMAL(10,2) COMMENT 'Giá HRC (USD/tấn)',
  usd_vnd_rate    DECIMAL(10,2) COMMENT 'Tỷ giá USD/VND',
  hrc_vnd_per_ton DECIMAL(15,2) COMMENT 'Giá HRC quy đổi (VND/tấn)'
) ENGINE=InnoDB COMMENT='Giá HRC nguyên liệu theo tháng (Scenario 3 & 6)';

CREATE TABLE dim_target (
  period             VARCHAR(7) PRIMARY KEY COMMENT 'Tháng YYYY-MM',
  target_volume_ton  DECIMAL(15,2) COMMENT 'Mục tiêu sản lượng (tấn)',
  target_revenue_vnd DECIMAL(20,2) COMMENT 'Mục tiêu doanh thu (VND)'
) ENGINE=InnoDB COMMENT='Kế hoạch năm phân bổ theo tháng (780k tấn / 18.000 tỷ)';

CREATE TABLE fact_sales (
  sale_id         BIGINT PRIMARY KEY COMMENT 'Mã giao dịch (1 dòng = 1 line item)',
  sale_date       DATE NOT NULL COMMENT 'Ngày bán -> dim_calendar',
  customer_id     INT NOT NULL COMMENT 'FK dim_customer',
  product_id      INT NOT NULL COMMENT 'FK dim_product',
  channel_id      INT NOT NULL COMMENT 'FK dim_channel',
  region_id       INT NOT NULL COMMENT 'FK dim_region',
  quantity_ton    DECIMAL(12,3) COMMENT 'Khối lượng (tấn)',
  asp_vnd_per_ton DECIMAL(15,2) COMMENT 'Giá bán net (VND/tấn, đã gồm chiết khấu)',
  net_revenue_vnd DECIMAL(20,2) COMMENT 'Doanh thu thuần (VND) = quantity x asp',
  KEY idx_sales_date (sale_date),
  KEY idx_sales_cust (customer_id),
  KEY idx_sales_prod (product_id),
  KEY idx_sales_chan (channel_id),
  KEY idx_sales_region (region_id),
  CONSTRAINT fk_sales_date FOREIGN KEY (sale_date) REFERENCES dim_calendar(date),
  CONSTRAINT fk_sales_cust FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id),
  CONSTRAINT fk_sales_prod FOREIGN KEY (product_id) REFERENCES dim_product(product_id),
  CONSTRAINT fk_sales_chan FOREIGN KEY (channel_id) REFERENCES dim_channel(channel_id),
  CONSTRAINT fk_sales_region FOREIGN KEY (region_id) REFERENCES dim_region(region_id)
) ENGINE=InnoDB COMMENT='FACT chính — bán hàng transaction-level';

CREATE TABLE fact_cogs (
  cogs_id                 BIGINT PRIMARY KEY COMMENT 'Mã COGS',
  sale_id                 BIGINT NOT NULL COMMENT 'FK fact_sales (1-1)',
  hrc_cost_vnd            DECIMAL(20,2) COMMENT 'Chi phí HRC (VND) ~65-72% total',
  other_material_cost_vnd DECIMAL(20,2) COMMENT 'Vật liệu khác: kẽm, sơn (VND)',
  conversion_cost_vnd     DECIMAL(20,2) COMMENT 'Chi phí gia công: năng lượng, nhân công (VND)',
  total_cogs_vnd          DECIMAL(20,2) COMMENT 'Tổng giá vốn = HRC + other + conversion',
  UNIQUE KEY uq_cogs_sale (sale_id),
  CONSTRAINT fk_cogs_sale FOREIGN KEY (sale_id) REFERENCES fact_sales(sale_id)
) ENGINE=InnoDB COMMENT='Giá vốn hàng bán, tách cấu trúc chi phí (1-1 với fact_sales)';

-- Metadata tables (nguồn truth cho AI engine hiểu schema)
CREATE TABLE _meta_tables (
  table_name      VARCHAR(64) PRIMARY KEY,
  description_vi  VARCHAR(255),
  description_en  VARCHAR(255),
  business_context TEXT
) ENGINE=InnoDB COMMENT='Metadata mô tả tables';

CREATE TABLE _meta_columns (
  id             INT AUTO_INCREMENT PRIMARY KEY,
  table_name     VARCHAR(64),
  column_name    VARCHAR(64),
  data_type      VARCHAR(32),
  description_vi VARCHAR(255),
  description_en VARCHAR(255),
  unit           VARCHAR(16),
  example_values VARCHAR(255),
  KEY idx_meta_col (table_name)
) ENGINE=InnoDB COMMENT='Metadata mô tả columns';

CREATE TABLE _meta_kpi (
  kpi_name          VARCHAR(64) PRIMARY KEY,
  formula_sql       TEXT,
  description_vi    VARCHAR(255),
  related_questions VARCHAR(255)
) ENGINE=InnoDB COMMENT='Định nghĩa KPI + formula';

CREATE TABLE _meta_glossary (
  term_vi    VARCHAR(64),
  term_en    VARCHAR(64),
  definition TEXT,
  PRIMARY KEY (term_vi)
) ENGINE=InnoDB COMMENT='Thuật ngữ ngành tôn mạ';
