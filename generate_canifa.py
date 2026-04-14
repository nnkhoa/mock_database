#!/usr/bin/env python3
"""
CANIFA Retail Fashion — Demo Database Generator
Generates 21 months of data (07/2023 – 03/2025) for canifa_retail_demo database.
3 layers: Base volume → Seasonality → Anomaly injection

Output:
  1. Direct MySQL population
  2. SQL files: canifa_sql/
"""

import random
import math
import os
import sys
from datetime import date, timedelta
from collections import defaultdict

import mysql.connector

random.seed(42)

# =============================================================================
# CONFIG
# =============================================================================
DB_CONFIG = dict(host='127.0.0.1', port=3306, user='root', password='root')
DB_NAME = 'canifa_retail_demo'
SQL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'canifa_sql')
BATCH = 1000

START_DATE = date(2023, 7, 1)
END_DATE = date(2025, 3, 31)

# Revenue calibration
# Target: ~1,600 tỷ VND/year (2024)
# base_records = avg records/store/day before multiplier
BASE_RECORDS_PER_STORE = 7
BASE_QTY_MEAN = 8  # avg units per record (daily product aggregate)

# =============================================================================
# DDL
# =============================================================================
DDL_SQL = """
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
"""

# =============================================================================
# SEASONALITY
# =============================================================================
MONTH_MULT = {1:1.45, 2:1.25, 3:0.85, 4:0.75, 5:0.70, 6:0.72, 7:0.78, 8:0.85, 9:0.90, 10:1.10, 11:1.30, 12:1.35}
DOW_MULT = {0:0.85, 1:0.80, 2:0.85, 3:0.90, 4:1.05, 5:1.30, 6:1.25}

CAT_SEASON = {
    'CAT-FW-M':  {1:1.5,2:1.2,3:0.5,4:0.2,5:0.1,6:0.1,7:0.1,8:0.2,9:0.5,10:1.3,11:1.6,12:1.7},
    'CAT-FW-F':  {1:1.5,2:1.2,3:0.5,4:0.2,5:0.1,6:0.1,7:0.1,8:0.2,9:0.5,10:1.3,11:1.6,12:1.7},
    'CAT-ESS-M': {1:1.0,2:0.9,3:0.9,4:1.1,5:1.2,6:1.3,7:1.3,8:1.2,9:1.1,10:0.9,11:0.9,12:0.9},
    'CAT-ESS-F': {1:1.0,2:0.9,3:0.9,4:1.1,5:1.2,6:1.3,7:1.3,8:1.2,9:1.1,10:0.9,11:0.9,12:0.9},
    'CAT-ACT':   {1:0.8,2:0.9,3:1.0,4:1.2,5:1.3,6:1.4,7:1.4,8:1.3,9:1.2,10:1.0,11:0.8,12:0.7},
    'CAT-KID':   {1:1.3,2:1.0,3:0.8,4:0.8,5:0.9,6:1.0,7:1.0,8:1.3,9:1.2,10:0.9,11:1.0,12:1.1},
}

CHANNEL_MIX = {
    'CH-STORE': 0.83,
    'CH-WEB':   0.07,
    'CH-SHOPEE': 0.05,
    'CH-TIKTOK': 0.03,
    'CH-LAZADA': 0.02,
}

RETURN_RATES = {'CH-STORE':0.03, 'CH-WEB':0.08, 'CH-SHOPEE':0.12, 'CH-TIKTOK':0.14, 'CH-LAZADA':0.10}
RETURN_REASONS = [('Size không vừa',0.45),('Đổi ý',0.25),('Không đúng mô tả',0.15),('Lỗi sản phẩm',0.10),('Khác',0.05)]

# =============================================================================
# MASTER DATA — REGIONS
# =============================================================================
REGIONS = [
    ('REG-HN',  'Hà Nội',                     'Hanoi',                'Thủ đô Hà Nội — 25 cửa hàng'),
    ('REG-MB',  'Miền Bắc',                    'Northern',             'Các tỉnh phía Bắc trừ Hà Nội — 22 cửa hàng'),
    ('REG-MT',  'Miền Trung',                  'Central',              'Các tỉnh miền Trung — 15 cửa hàng'),
    ('REG-HCM', 'TP. Hồ Chí Minh',            'Ho Chi Minh City',     'Thành phố Hồ Chí Minh — 22 cửa hàng'),
    ('REG-MN',  'Miền Nam',                    'Southern',             'Các tỉnh phía Nam trừ TP.HCM — 16 cửa hàng'),
    ('REG-TN',  'Tây Nguyên & Tây Nam Bộ',    'Highlands & Southwest','Tây Nguyên và các tỉnh xa — 10 cửa hàng'),
]

# =============================================================================
# MASTER DATA — CHANNELS
# =============================================================================
CHANNELS = [
    ('CH-STORE',  'Cửa hàng',          'Offline', 0, 0),
    ('CH-WEB',    'Website canifa.com', 'Online',  0, 3),
    ('CH-SHOPEE', 'Shopee',             'Online',  8, 5),
    ('CH-TIKTOK', 'TikTok Shop',        'Online',  6, 4),
    ('CH-LAZADA', 'Lazada',             'Online',  7, 4),
]

# =============================================================================
# MASTER DATA — PROMOTIONS
# =============================================================================
PROMOTIONS = [
    ('PRM-001','Flash Sale 11/11','Flash Sale','2024-11-09','2024-11-12',30,50,'Online','All',800000000,500000000,'Flash sale 11/11 trên sàn TMĐT'),
    ('PRM-002','Black Friday','Seasonal','2024-11-22','2024-11-26',20,40,'All','All',1500000000,300000000,'Black Friday giảm 20-40% toàn hệ thống'),
    ('PRM-003','Flash Sale 12/12','Flash Sale','2024-12-10','2024-12-13',40,60,'Online','All',1200000000,2500000000,'Flash Sale 12/12 Shopee+TikTok giảm sâu 40-60%'),
    ('PRM-004','Giáng Sinh & Năm Mới','Seasonal','2024-12-20','2025-01-02',15,25,'All','All',2000000000,200000000,'Giáng Sinh & Năm Mới giảm 15-25%'),
    ('PRM-005','Tết Nguyên Đán','Seasonal','2025-01-10','2025-02-10',20,30,'All','All',3000000000,0,'Tết Nguyên Đán mua sắm quần áo mới'),
    ('PRM-006','Mua 3 Tặng 1 Essentials','Bundle','2025-02-01','2025-02-28',25,25,'All','CAT-ESS-M,CAT-ESS-F',500000000,0,'Mua 3 tặng 1 hàng Essentials'),
    ('PRM-007','Xuân Hè Early Bird','Seasonal','2025-03-01','2025-03-15',10,15,'All','All',800000000,0,'Ưu đãi đầu mùa Xuân Hè 10-15%'),
    ('PRM-008','Sale cuối mùa Đông','Clearance','2025-02-15','2025-03-15',40,70,'All','CAT-FW-M,CAT-FW-F',300000000,0,'Clearance hàng Thu-Đông giảm 40-70%'),
]

# =============================================================================
# MASTER DATA — STORES (110)
# (id, name, region_id, province, district, type, area_sqm, rent, open_date, rev_mult)
# rev_mult = revenue multiplier (1.0 = average store)
# =============================================================================
STORES_RAW = [
    # ── Hà Nội (25) ──
    ('STR-HN-001','Canifa Bà Triệu','REG-HN','Hà Nội','Hoàn Kiếm','Flagship',180,120000000,'2005-03-15',3.0),
    ('STR-HN-002','Canifa Chùa Bộc','REG-HN','Hà Nội','Đống Đa','Standard',120,80000000,'2008-06-01',1.8),
    ('STR-HN-003','Canifa Cầu Giấy','REG-HN','Hà Nội','Cầu Giấy','Standard',140,90000000,'2009-02-01',2.2),
    ('STR-HN-004','Canifa AEON Long Biên','REG-HN','Hà Nội','Long Biên','TTTM',100,70000000,'2015-10-01',1.8),
    ('STR-HN-005','Canifa Lotte Đống Đa','REG-HN','Hà Nội','Đống Đa','TTTM',90,65000000,'2016-03-01',1.6),
    ('STR-HN-006','Canifa BigC Thăng Long','REG-HN','Hà Nội','Cầu Giấy','TTTM',95,60000000,'2014-05-01',1.4),
    ('STR-HN-007','Canifa Savico Long Biên','REG-HN','Hà Nội','Long Biên','Standard',110,55000000,'2013-08-01',1.3),
    ('STR-HN-008','Canifa Phố Huế','REG-HN','Hà Nội','Hai Bà Trưng','Standard',100,75000000,'2010-04-01',1.7),
    ('STR-HN-009','Canifa Giảng Võ','REG-HN','Hà Nội','Ba Đình','Standard',90,70000000,'2011-06-01',1.5),
    ('STR-HN-010','Canifa Mỹ Đình','REG-HN','Hà Nội','Nam Từ Liêm','Standard',110,65000000,'2012-09-01',1.4),
    ('STR-HN-011','Canifa Royal City','REG-HN','Hà Nội','Thanh Xuân','TTTM',95,85000000,'2013-11-01',2.0),
    ('STR-HN-012','Canifa Vincom Bà Triệu','REG-HN','Hà Nội','Hai Bà Trưng','TTTM',100,110000000,'2014-01-01',2.2),
    ('STR-HN-013','Canifa Times City','REG-HN','Hà Nội','Hai Bà Trưng','TTTM',90,80000000,'2016-06-01',1.8),
    ('STR-HN-014','Canifa Hà Đông','REG-HN','Hà Nội','Hà Đông','Standard',100,50000000,'2017-03-01',1.2),
    ('STR-HN-015','Canifa Vincom Long Biên','REG-HN','Hà Nội','Long Biên','TTTM',85,70000000,'2018-05-01',1.5),
    ('STR-HN-016','Canifa Thanh Xuân','REG-HN','Hà Nội','Thanh Xuân','Standard',95,55000000,'2017-08-01',1.3),
    ('STR-HN-017','Canifa AEON Hà Đông','REG-HN','Hà Nội','Hà Đông','TTTM',90,65000000,'2019-11-01',1.5),
    ('STR-HN-018','Canifa Tây Hồ','REG-HN','Hà Nội','Tây Hồ','Standard',100,60000000,'2018-02-01',1.3),
    ('STR-HN-019','Canifa Trần Duy Hưng','REG-HN','Hà Nội','Cầu Giấy','Standard',110,80000000,'2010-07-01',1.9),
    ('STR-HN-020','Canifa Nguyễn Trãi HN','REG-HN','Hà Nội','Thanh Xuân','Standard',105,70000000,'2012-01-01',1.6),
    ('STR-HN-021','Canifa Mega Mall','REG-HN','Hà Nội','Hoàng Mai','TTTM',85,55000000,'2020-06-01',1.2),
    ('STR-HN-022','Canifa Hoàng Mai','REG-HN','Hà Nội','Hoàng Mai','Standard',100,45000000,'2024-07-15',0.4),  # NEW
    ('STR-HN-023','Canifa Đống Đa','REG-HN','Hà Nội','Đống Đa','Standard',90,50000000,'2019-04-01',1.2),
    ('STR-HN-024','Canifa Kim Mã','REG-HN','Hà Nội','Ba Đình','Standard',85,55000000,'2016-09-01',1.3),
    ('STR-HN-025','Canifa Outlet Long Biên','REG-HN','Hà Nội','Long Biên','Outlet',150,35000000,'2020-01-01',1.0),
    # ── TP. HCM (22) ──
    ('STR-HCM-001','Canifa Nguyễn Trãi Q1','REG-HCM','TP. Hồ Chí Minh','Quận 1','Flagship',200,150000000,'2006-05-01',3.2),
    ('STR-HCM-002','Canifa Vincom Đồng Khởi','REG-HCM','TP. Hồ Chí Minh','Quận 1','TTTM',110,130000000,'2014-07-01',2.5),
    ('STR-HCM-003','Canifa Nguyễn Trãi Q5','REG-HCM','TP. Hồ Chí Minh','Quận 5','Standard',130,85000000,'2009-03-01',1.6),
    ('STR-HCM-004','Canifa Crescent Mall Q7','REG-HCM','TP. Hồ Chí Minh','Quận 7','TTTM',100,95000000,'2011-09-01',1.8),
    ('STR-HCM-005','Canifa SC VivoCity Q7','REG-HCM','TP. Hồ Chí Minh','Quận 7','TTTM',95,100000000,'2016-01-01',1.9),
    ('STR-HCM-006','Canifa Gò Vấp','REG-HCM','TP. Hồ Chí Minh','Gò Vấp','Standard',110,60000000,'2012-04-01',1.4),
    ('STR-HCM-007','Canifa Tân Bình','REG-HCM','TP. Hồ Chí Minh','Tân Bình','Standard',100,55000000,'2013-06-01',1.3),
    ('STR-HCM-008','Canifa Thủ Đức','REG-HCM','TP. Hồ Chí Minh','Thủ Đức','Standard',110,50000000,'2015-02-01',1.3),
    ('STR-HCM-009','Canifa AEON Tân Phú','REG-HCM','TP. Hồ Chí Minh','Tân Phú','TTTM',95,75000000,'2016-10-01',1.7),
    ('STR-HCM-010','Canifa Vincom Thủ Đức','REG-HCM','TP. Hồ Chí Minh','Thủ Đức','TTTM',90,80000000,'2018-03-01',1.6),
    ('STR-HCM-011','Canifa Quận 3','REG-HCM','TP. Hồ Chí Minh','Quận 3','Standard',100,70000000,'2010-08-01',1.5),
    ('STR-HCM-012','Canifa Quận 10','REG-HCM','TP. Hồ Chí Minh','Quận 10','Standard',95,55000000,'2014-05-01',1.3),
    ('STR-HCM-013','Canifa Bình Thạnh','REG-HCM','TP. Hồ Chí Minh','Bình Thạnh','Standard',105,60000000,'2012-11-01',1.4),
    ('STR-HCM-014','Canifa Phú Nhuận','REG-HCM','TP. Hồ Chí Minh','Phú Nhuận','Standard',90,55000000,'2015-07-01',1.3),
    ('STR-HCM-015','Canifa Quận 9','REG-HCM','TP. Hồ Chí Minh','Quận 9','Standard',100,45000000,'2018-09-01',1.1),
    ('STR-HCM-016','Canifa Vincom Landmark','REG-HCM','TP. Hồ Chí Minh','Bình Thạnh','TTTM',85,120000000,'2019-04-01',2.0),
    ('STR-HCM-017','Canifa Lê Văn Sỹ','REG-HCM','TP. Hồ Chí Minh','Quận 3','Standard',90,65000000,'2011-03-01',1.4),
    ('STR-HCM-018','Canifa Emart Phan Văn Trị','REG-HCM','TP. Hồ Chí Minh','Gò Vấp','TTTM',95,55000000,'2020-02-01',1.3),
    ('STR-HCM-019','Canifa Bình Chánh','REG-HCM','TP. Hồ Chí Minh','Bình Chánh','Standard',110,40000000,'2021-06-01',0.9),
    ('STR-HCM-020','Canifa Satra Phạm Hùng','REG-HCM','TP. Hồ Chí Minh','Quận 8','TTTM',85,50000000,'2019-08-01',1.1),
    ('STR-HCM-021','Canifa Nguyễn Huệ','REG-HCM','TP. Hồ Chí Minh','Quận 1','Flagship',180,140000000,'2007-11-01',2.8),
    ('STR-HCM-022','Canifa Outlet Bình Tân','REG-HCM','TP. Hồ Chí Minh','Bình Tân','Outlet',140,35000000,'2020-09-01',0.9),
    # ── Miền Bắc (22) ──
    ('STR-HP-001','Canifa Hải Phòng Lạch Tray','REG-MB','Hải Phòng','Ngô Quyền','Standard',100,45000000,'2010-05-01',1.2),
    ('STR-HP-002','Canifa Hải Phòng Vincom','REG-MB','Hải Phòng','Lê Chân','TTTM',90,60000000,'2016-08-01',1.4),
    ('STR-HP-003','Canifa Hải Phòng Lê Hồng Phong','REG-MB','Hải Phòng','Ngô Quyền','Standard',85,40000000,'2014-02-01',1.0),
    ('STR-BN-001','Canifa Bắc Ninh','REG-MB','Bắc Ninh','TP Bắc Ninh','Standard',90,35000000,'2015-06-01',0.9),
    ('STR-BN-002','Canifa Bắc Ninh AEON','REG-MB','Bắc Ninh','TP Bắc Ninh','TTTM',85,50000000,'2019-03-01',1.1),
    ('STR-QNI-001','Canifa Quảng Ninh Hạ Long','REG-MB','Quảng Ninh','Hạ Long','Standard',95,40000000,'2013-04-01',1.0),
    ('STR-QNI-002','Canifa Quảng Ninh Vincom','REG-MB','Quảng Ninh','Hạ Long','TTTM',85,55000000,'2017-09-01',1.2),
    ('STR-HD-001','Canifa Hải Dương','REG-MB','Hải Dương','TP Hải Dương','Standard',80,30000000,'2016-01-01',0.7),
    ('STR-HD-002','Canifa Hải Dương Vincom','REG-MB','Hải Dương','TP Hải Dương','TTTM',75,40000000,'2024-08-01',0.3),  # NEW
    ('STR-TNG-001','Canifa Thái Nguyên','REG-MB','Thái Nguyên','TP Thái Nguyên','Standard',80,28000000,'2017-05-01',0.7),
    ('STR-VP-001','Canifa Vĩnh Phúc','REG-MB','Vĩnh Phúc','Vĩnh Yên','Standard',75,25000000,'2018-02-01',0.6),
    ('STR-PT-001','Canifa Phú Thọ','REG-MB','Phú Thọ','Việt Trì','Standard',70,22000000,'2019-06-01',0.5),
    ('STR-TH-001','Canifa Thanh Hoá TP','REG-MB','Thanh Hoá','TP Thanh Hoá','Standard',90,35000000,'2012-07-01',0.9),
    ('STR-TH-002','Canifa Thanh Hoá Vincom','REG-MB','Thanh Hoá','TP Thanh Hoá','TTTM',80,45000000,'2018-11-01',1.1),
    ('STR-NA-001','Canifa Nghệ An Vinh','REG-MB','Nghệ An','TP Vinh','Standard',90,35000000,'2013-09-01',0.9),
    ('STR-NA-002','Canifa Nghệ An Vincom','REG-MB','Nghệ An','TP Vinh','TTTM',80,45000000,'2019-05-01',1.0),
    ('STR-ND-001','Canifa Nam Định','REG-MB','Nam Định','TP Nam Định','Standard',75,25000000,'2017-03-01',0.6),
    ('STR-HY-001','Canifa Hưng Yên','REG-MB','Hưng Yên','TP Hưng Yên','Standard',70,22000000,'2020-01-01',0.5),
    ('STR-NB-001','Canifa Ninh Bình','REG-MB','Ninh Bình','TP Ninh Bình','Standard',75,25000000,'2018-08-01',0.6),
    ('STR-HB-001','Canifa Hoà Bình','REG-MB','Hoà Bình','TP Hoà Bình','Standard',70,20000000,'2019-11-01',0.45),
    ('STR-LS-001','Canifa Lạng Sơn','REG-MB','Lạng Sơn','TP Lạng Sơn','Standard',65,18000000,'2020-04-01',0.4),
    ('STR-SL-001','Canifa Sơn La','REG-MB','Sơn La','TP Sơn La','Standard',65,18000000,'2021-02-01',0.35),
    # ── Miền Trung (15) ──
    ('STR-DN-001','Canifa Đà Nẵng Nguyễn Văn Linh','REG-MT','Đà Nẵng','Thanh Khê','Flagship',160,80000000,'2008-10-01',2.5),
    ('STR-DN-002','Canifa Đà Nẵng Vincom','REG-MT','Đà Nẵng','Hải Châu','TTTM',95,65000000,'2015-12-01',1.6),
    ('STR-DN-003','Canifa Đà Nẵng Indochina','REG-MT','Đà Nẵng','Hải Châu','TTTM',85,55000000,'2017-04-01',1.3),
    ('STR-DN-004','Canifa Đà Nẵng Vincom Ngô Quyền','REG-MT','Đà Nẵng','Sơn Trà','TTTM',80,50000000,'2024-09-01',0.35),  # NEW
    ('STR-HUE-001','Canifa Huế Trần Hưng Đạo','REG-MT','Thừa Thiên Huế','TP Huế','Standard',90,35000000,'2012-05-01',0.9),
    ('STR-HUE-002','Canifa Huế Vincom','REG-MT','Thừa Thiên Huế','TP Huế','TTTM',80,40000000,'2019-01-01',1.0),
    ('STR-QB-001','Canifa Quảng Bình','REG-MT','Quảng Bình','Đồng Hới','Standard',70,22000000,'2020-03-01',0.45),
    ('STR-QNG-001','Canifa Quảng Ngãi','REG-MT','Quảng Ngãi','TP Quảng Ngãi','Standard',70,22000000,'2019-07-01',0.45),
    ('STR-BDI-001','Canifa Bình Định Quy Nhơn','REG-MT','Bình Định','Quy Nhơn','Standard',80,28000000,'2016-06-01',0.7),
    ('STR-NT-001','Canifa Nha Trang','REG-MT','Khánh Hoà','Nha Trang','Standard',90,35000000,'2013-02-01',0.9),
    ('STR-NT-002','Canifa Nha Trang Vincom','REG-MT','Khánh Hoà','Nha Trang','TTTM',85,50000000,'2018-06-01',1.1),
    ('STR-PY-001','Canifa Phú Yên','REG-MT','Phú Yên','Tuy Hoà','Standard',70,22000000,'2021-01-01',0.4),
    ('STR-QNM-001','Canifa Quảng Nam','REG-MT','Quảng Nam','Tam Kỳ','Standard',75,25000000,'2019-09-01',0.5),
    ('STR-QT-001','Canifa Quảng Trị','REG-MT','Quảng Trị','Đông Hà','Standard',65,20000000,'2020-08-01',0.4),
    ('STR-HT-001','Canifa Hà Tĩnh','REG-MT','Hà Tĩnh','TP Hà Tĩnh','Standard',70,22000000,'2020-05-01',0.45),
    # ── Miền Nam (16) ──
    ('STR-BDG-001','Canifa Bình Dương Thủ Dầu Một','REG-MN','Bình Dương','Thủ Dầu Một','Standard',95,40000000,'2013-03-01',1.0),
    ('STR-BDG-002','Canifa Bình Dương AEON','REG-MN','Bình Dương','Thuận An','TTTM',90,55000000,'2017-10-01',1.3),
    ('STR-BDG-003','Canifa Bình Dương Thuận An','REG-MN','Bình Dương','Thuận An','Standard',80,35000000,'2019-06-01',0.8),
    ('STR-DNI-001','Canifa Đồng Nai Biên Hoà','REG-MN','Đồng Nai','Biên Hoà','Standard',90,35000000,'2014-01-01',0.9),
    ('STR-DNI-002','Canifa Đồng Nai Vincom','REG-MN','Đồng Nai','Biên Hoà','TTTM',85,50000000,'2018-04-01',1.1),
    ('STR-DNI-003','Canifa Đồng Nai Long Khánh','REG-MN','Đồng Nai','Long Khánh','Standard',75,25000000,'2020-02-01',0.5),
    ('STR-VT-001','Canifa Vũng Tàu','REG-MN','Bà Rịa-Vũng Tàu','Vũng Tàu','Standard',85,30000000,'2015-05-01',0.7),
    ('STR-VT-002','Canifa Vũng Tàu Lotte','REG-MN','Bà Rịa-Vũng Tàu','Vũng Tàu','TTTM',80,45000000,'2019-12-01',1.0),
    ('STR-CT-001','Canifa Cần Thơ Ninh Kiều','REG-MN','Cần Thơ','Ninh Kiều','Standard',90,35000000,'2012-08-01',0.9),
    ('STR-CT-002','Canifa Cần Thơ Vincom','REG-MN','Cần Thơ','Ninh Kiều','TTTM',85,50000000,'2018-07-01',1.1),
    ('STR-LA-001','Canifa Long An','REG-MN','Long An','Tân An','Standard',75,25000000,'2019-03-01',0.5),
    ('STR-BTE-001','Canifa Bến Tre','REG-MN','Bến Tre','TP Bến Tre','Standard',70,22000000,'2020-06-01',0.4),
    ('STR-TG-001','Canifa Tiền Giang','REG-MN','Tiền Giang','Mỹ Tho','Standard',75,25000000,'2019-10-01',0.5),
    ('STR-KG-001','Canifa Kiên Giang','REG-MN','Kiên Giang','Rạch Giá','Standard',75,25000000,'2020-04-01',0.5),
    ('STR-AG-001','Canifa An Giang','REG-MN','An Giang','Long Xuyên','Standard',75,25000000,'2020-08-01',0.5),
    ('STR-BDG-004','Canifa Outlet Bình Dương','REG-MN','Bình Dương','Dĩ An','Outlet',160,30000000,'2021-03-01',0.8),
    # ── Tây Nguyên & Tây Nam Bộ (10) ──
    ('STR-DL-001','Canifa Đắk Lắk Buôn Ma Thuột','REG-TN','Đắk Lắk','Buôn Ma Thuột','Standard',80,25000000,'2017-07-01',0.6),
    ('STR-DL-002','Canifa Đắk Lắk Vincom','REG-TN','Đắk Lắk','Buôn Ma Thuột','TTTM',75,35000000,'2020-01-01',0.8),
    ('STR-GL-001','Canifa Gia Lai','REG-TN','Gia Lai','Pleiku','Standard',70,22000000,'2018-04-01',0.35),  # underperformer
    ('STR-LDG-001','Canifa Lâm Đồng Đà Lạt','REG-TN','Lâm Đồng','Đà Lạt','Standard',85,30000000,'2014-06-01',0.8),
    ('STR-LDG-002','Canifa Lâm Đồng Bảo Lộc','REG-TN','Lâm Đồng','Bảo Lộc','Standard',70,20000000,'2020-09-01',0.4),
    ('STR-BP-001','Canifa Bình Phước','REG-TN','Bình Phước','Đồng Xoài','Standard',65,18000000,'2019-05-01',0.3),  # underperformer
    ('STR-KT-001','Canifa Kon Tum','REG-TN','Kon Tum','TP Kon Tum','Standard',65,18000000,'2020-11-01',0.35),
    ('STR-DKN-001','Canifa Đắk Nông','REG-TN','Đắk Nông','Gia Nghĩa','Standard',65,18000000,'2021-04-01',0.3),
    ('STR-TV-001','Canifa Trà Vinh','REG-TN','Trà Vinh','TP Trà Vinh','Standard',65,18000000,'2020-06-01',0.25),  # underperformer
    ('STR-DB-001','Canifa Điện Biên','REG-TN','Điện Biên','TP Điện Biên Phủ','Standard',60,15000000,'2021-08-01',0.3),
]

# Stores that are anomaly targets
NEW_STORES = {'STR-HN-022', 'STR-HD-002', 'STR-DN-004'}  # ramp-up
UNDERPERFORMERS = {'STR-GL-001', 'STR-TV-001', 'STR-BP-001', 'STR-DKN-001', 'STR-KT-001',
                   'STR-DB-001', 'STR-LDG-002', 'STR-HB-001', 'STR-SL-001',
                   'STR-QT-001', 'STR-PY-001', 'STR-QB-001'}
OVERSTOCK_STORES = {'STR-HCM-003', 'STR-HN-007'}  # winter overstock anomaly

# =============================================================================
# MASTER DATA — CATEGORIES & PRODUCT TEMPLATES
# =============================================================================
CATEGORIES = [
    ('CAT-ESS-M', 'Nam',     'Essentials Nam',     None, 'Áo phông, polo, basic nam'),
    ('CAT-ESS-F', 'Nữ',      'Essentials Nữ',      None, 'Áo phông, tank top, basic nữ'),
    ('CAT-SMC-M', 'Nam',     'Smart Casual Nam',   None, 'Sơ mi, áo khoác nhẹ nam'),
    ('CAT-SMC-F', 'Nữ',      'Smart Casual Nữ',    None, 'Sơ mi, váy, đầm nữ'),
    ('CAT-JKK-M', 'Nam',     'Jeans-Kaki Nam',     None, 'Jeans, kaki, jogger nam'),
    ('CAT-JKK-F', 'Nữ',      'Jeans-Kaki Nữ',      None, 'Jeans, kaki, chân váy nữ'),
    ('CAT-FW-M',  'Nam',     'Thu-Đông Nam',        None, 'Áo len, áo khoác dạ, phao nam'),
    ('CAT-FW-F',  'Nữ',      'Thu-Đông Nữ',         None, 'Áo len, áo khoác len, phao nữ'),
    ('CAT-ACT',   'Unisex',  'Activewear',          None, 'Áo Dry-Tech, quần thể thao'),
    ('CAT-KID',   'Trẻ em',  'Kids',                None, 'Áo phông, áo khoác, quần, set đồ trẻ em'),
    ('CAT-ACC',   'Unisex',  'Phụ kiện',            None, 'Khăn, mũ, tất, balo'),
]

# Product templates: (name_base, cat_id, num_variants, season, line, material,
#                     retail_min, retail_max, cost_min, cost_max, size_range, is_cotton)
# is_cotton => cost_price_new = cost_price * 1.08 from Sep 2024
PRODUCT_TEMPLATES = [
    # CAT-ESS-M (60 SKU)
    ('Áo phông cổ tròn nam','CAT-ESS-M',8,'4 Mùa','Essentials','Cotton USA',199000,249000,65000,85000,'S-XXL',True),
    ('Áo phông cổ V nam','CAT-ESS-M',5,'4 Mùa','Essentials','Cotton USA',199000,249000,65000,85000,'S-XXL',True),
    ('Áo phông in họa tiết nam','CAT-ESS-M',7,'4 Mùa','Essentials','Cotton blend',219000,279000,70000,95000,'S-XXL',True),
    ('Áo polo basic nam','CAT-ESS-M',6,'4 Mùa','Essentials','Cotton Pique',299000,349000,95000,120000,'S-XXL',True),
    ('Áo polo kẻ sọc nam','CAT-ESS-M',5,'4 Mùa','Essentials','Cotton Pique',329000,399000,100000,135000,'S-XXL',True),
    ('Áo polo thể thao nam','CAT-ESS-M',4,'4 Mùa','Essentials','Cotton Pique',329000,379000,100000,125000,'S-XXL',True),
    ('Áo tank top nam','CAT-ESS-M',4,'Xuân-Hè','Essentials','Cotton stretch',149000,199000,45000,65000,'S-XXL',True),
    ('Áo phông oversize nam','CAT-ESS-M',5,'4 Mùa','Essentials','Cotton USA',249000,299000,80000,100000,'M-XXL',True),
    ('Áo phông thể thao nam','CAT-ESS-M',4,'4 Mùa','Essentials','Cotton blend',229000,279000,75000,90000,'S-XXL',True),
    ('Áo phông Henley nam','CAT-ESS-M',4,'4 Mùa','Essentials','Cotton USA',249000,299000,80000,100000,'S-XXL',True),
    ('Áo lót cotton nam','CAT-ESS-M',4,'4 Mùa','Essentials','Cotton USA',99000,149000,30000,45000,'S-XXL',True),
    ('Áo phông raglan nam','CAT-ESS-M',4,'4 Mùa','Essentials','Cotton blend',219000,269000,70000,90000,'S-XXL',True),
    # CAT-ESS-F (55 SKU)
    ('Áo phông cổ tròn nữ','CAT-ESS-F',7,'4 Mùa','Essentials','Cotton USA',179000,229000,58000,75000,'S-XL',True),
    ('Áo phông cổ V nữ','CAT-ESS-F',5,'4 Mùa','Essentials','Cotton USA',179000,229000,58000,75000,'S-XL',True),
    ('Áo phông crop top nữ','CAT-ESS-F',5,'Xuân-Hè','Essentials','Cotton stretch',169000,219000,52000,70000,'S-L',True),
    ('Áo polo nữ','CAT-ESS-F',5,'4 Mùa','Essentials','Cotton Pique',279000,329000,88000,110000,'S-XL',True),
    ('Áo tank top nữ','CAT-ESS-F',5,'Xuân-Hè','Essentials','Cotton stretch',129000,179000,40000,58000,'S-XL',True),
    ('Áo phông in họa tiết nữ','CAT-ESS-F',6,'4 Mùa','Essentials','Cotton blend',199000,259000,65000,85000,'S-XL',True),
    ('Áo phông oversize nữ','CAT-ESS-F',5,'4 Mùa','Essentials','Cotton USA',229000,279000,72000,90000,'S-XL',True),
    ('Áo phông dài tay nữ','CAT-ESS-F',5,'4 Mùa','Essentials','Cotton USA',229000,279000,72000,90000,'S-XL',True),
    ('Áo thun body nữ','CAT-ESS-F',4,'4 Mùa','Essentials','Cotton stretch',169000,219000,52000,68000,'S-L',True),
    ('Áo lót cotton nữ','CAT-ESS-F',4,'4 Mùa','Essentials','Cotton USA',89000,129000,28000,40000,'S-XL',True),
    ('Áo phông raglan nữ','CAT-ESS-F',4,'4 Mùa','Essentials','Cotton blend',199000,249000,62000,80000,'S-XL',True),
    # CAT-SMC-M (40 SKU)
    ('Áo sơ mi dài tay nam','CAT-SMC-M',6,'4 Mùa','Smart Casual','Cotton poplin',399000,499000,130000,170000,'S-XXL',True),
    ('Áo sơ mi ngắn tay nam','CAT-SMC-M',5,'Xuân-Hè','Smart Casual','Cotton poplin',379000,449000,120000,150000,'S-XXL',True),
    ('Áo sơ mi kẻ sọc nam','CAT-SMC-M',5,'4 Mùa','Smart Casual','Cotton oxford',429000,529000,140000,180000,'S-XXL',True),
    ('Áo sơ mi công sở nam','CAT-SMC-M',5,'4 Mùa','Smart Casual','Cotton blend',449000,549000,145000,185000,'S-XXL',True),
    ('Áo khoác bomber nam','CAT-SMC-M',4,'4 Mùa','Smart Casual','Polyester lót cotton',599000,749000,200000,260000,'M-XXL',False),
    ('Áo khoác gió nam','CAT-SMC-M',4,'4 Mùa','Smart Casual','Nylon chống nước',499000,649000,165000,220000,'M-XXL',False),
    ('Áo blazer nam','CAT-SMC-M',4,'4 Mùa','Smart Casual','Polyester blend',699000,899000,230000,310000,'M-XXL',False),
    ('Áo vest nam','CAT-SMC-M',3,'4 Mùa','Smart Casual','Polyester blend',599000,799000,200000,270000,'M-XXL',False),
    ('Áo sơ mi linen nam','CAT-SMC-M',4,'Xuân-Hè','Smart Casual','Linen',449000,549000,148000,185000,'S-XXL',False),
    # CAT-SMC-F (45 SKU)
    ('Áo sơ mi nữ công sở','CAT-SMC-F',6,'4 Mùa','Smart Casual','Cotton poplin',379000,479000,120000,160000,'S-XL',True),
    ('Áo sơ mi nữ oversize','CAT-SMC-F',5,'4 Mùa','Smart Casual','Cotton blend',399000,499000,130000,168000,'S-XL',True),
    ('Váy liền thân','CAT-SMC-F',5,'Xuân-Hè','Smart Casual','Polyester chiffon',449000,599000,148000,200000,'S-XL',False),
    ('Đầm suông nữ','CAT-SMC-F',5,'4 Mùa','Smart Casual','Cotton blend',499000,649000,165000,220000,'S-XL',True),
    ('Áo khoác nhẹ nữ','CAT-SMC-F',4,'4 Mùa','Smart Casual','Polyester',499000,649000,165000,215000,'S-XL',False),
    ('Áo blazer nữ','CAT-SMC-F',4,'4 Mùa','Smart Casual','Polyester blend',649000,849000,215000,285000,'S-XL',False),
    ('Chân váy chữ A','CAT-SMC-F',4,'4 Mùa','Smart Casual','Cotton blend',349000,449000,115000,150000,'S-XL',True),
    ('Áo kiểu nữ','CAT-SMC-F',5,'4 Mùa','Smart Casual','Cotton voile',329000,429000,108000,142000,'S-XL',True),
    ('Áo sơ mi linen nữ','CAT-SMC-F',4,'Xuân-Hè','Smart Casual','Linen',429000,529000,140000,175000,'S-XL',False),
    ('Quần culottes nữ','CAT-SMC-F',3,'Xuân-Hè','Smart Casual','Cotton blend',349000,449000,115000,150000,'S-XL',True),
    # CAT-JKK-M (35 SKU)
    ('Quần jeans nam slim','CAT-JKK-M',5,'4 Mùa','Jeans-Kaki','Denim cotton',449000,549000,150000,185000,'29-36',True),
    ('Quần jeans nam regular','CAT-JKK-M',5,'4 Mùa','Jeans-Kaki','Denim cotton',399000,499000,135000,168000,'29-36',True),
    ('Quần kaki nam','CAT-JKK-M',5,'4 Mùa','Jeans-Kaki','Cotton twill',349000,449000,115000,150000,'29-36',True),
    ('Quần jogger nam','CAT-JKK-M',5,'4 Mùa','Jeans-Kaki','Cotton french terry',299000,399000,98000,132000,'S-XXL',True),
    ('Quần short nam','CAT-JKK-M',5,'Xuân-Hè','Jeans-Kaki','Cotton twill',249000,329000,82000,110000,'29-36',True),
    ('Quần tây nam','CAT-JKK-M',5,'4 Mùa','Jeans-Kaki','Polyester blend',399000,549000,130000,185000,'29-36',False),
    ('Quần jeans nam skinny','CAT-JKK-M',5,'4 Mùa','Jeans-Kaki','Denim stretch',479000,579000,158000,195000,'29-36',True),
    # CAT-JKK-F (35 SKU)
    ('Quần jeans nữ skinny','CAT-JKK-F',5,'4 Mùa','Jeans-Kaki','Denim stretch',399000,499000,132000,168000,'25-32',True),
    ('Quần jeans nữ straight','CAT-JKK-F',5,'4 Mùa','Jeans-Kaki','Denim cotton',379000,479000,125000,160000,'25-32',True),
    ('Quần kaki nữ','CAT-JKK-F',5,'4 Mùa','Jeans-Kaki','Cotton twill',329000,429000,108000,142000,'25-32',True),
    ('Quần short nữ','CAT-JKK-F',5,'Xuân-Hè','Jeans-Kaki','Cotton twill',229000,299000,75000,100000,'25-32',True),
    ('Quần jogger nữ','CAT-JKK-F',5,'4 Mùa','Jeans-Kaki','Cotton french terry',279000,369000,92000,122000,'S-XL',True),
    ('Chân váy jeans','CAT-JKK-F',5,'4 Mùa','Jeans-Kaki','Denim cotton',299000,399000,98000,132000,'25-32',True),
    ('Quần jeans nữ wide-leg','CAT-JKK-F',5,'4 Mùa','Jeans-Kaki','Denim cotton',429000,529000,140000,175000,'25-32',True),
    # CAT-FW-M (40 SKU)
    ('Áo len cổ tròn nam','CAT-FW-M',6,'Thu-Đông','Len truyền thống','Wool blend',499000,649000,180000,230000,'M-XXL',False),
    ('Áo len cổ lọ nam','CAT-FW-M',5,'Thu-Đông','Len truyền thống','Wool Merino',599000,749000,210000,270000,'M-XXL',False),
    ('Áo khoác phao nam','CAT-FW-M',5,'Thu-Đông','Thu-Đông','Polyester lót bông',699000,999000,280000,380000,'M-XXL',False),
    ('Áo khoác dạ nam','CAT-FW-M',4,'Thu-Đông','Thu-Đông','Wool blend',899000,1299000,350000,480000,'M-XXL',False),
    ('Áo len cardigan nam','CAT-FW-M',4,'Thu-Đông','Len truyền thống','Wool blend',549000,699000,195000,250000,'M-XXL',False),
    ('Áo hoodie nam','CAT-FW-M',5,'Thu-Đông','Thu-Đông','Cotton fleece',399000,499000,135000,170000,'M-XXL',True),
    ('Áo gilet phao nam','CAT-FW-M',4,'Thu-Đông','Thu-Đông','Polyester lót bông',499000,699000,175000,250000,'M-XXL',False),
    ('Áo nỉ cổ tròn nam','CAT-FW-M',5,'Thu-Đông','Thu-Đông','Cotton fleece',349000,449000,118000,152000,'M-XXL',True),
    ('Quần nỉ nam','CAT-FW-M',2,'Thu-Đông','Thu-Đông','Cotton fleece',299000,399000,98000,135000,'M-XXL',True),
    # CAT-FW-F (45 SKU)
    ('Áo len cổ tròn nữ','CAT-FW-F',6,'Thu-Đông','Len truyền thống','Wool blend',479000,629000,170000,225000,'S-XL',False),
    ('Áo len cổ lọ nữ','CAT-FW-F',5,'Thu-Đông','Len truyền thống','Wool Merino',579000,729000,200000,260000,'S-XL',False),
    ('Áo khoác len nữ dáng dài','CAT-FW-F',7,'Thu-Đông','Len truyền thống','Wool blend',899000,1499000,350000,550000,'S-XL',False),
    ('Áo khoác phao nữ','CAT-FW-F',5,'Thu-Đông','Thu-Đông','Polyester lót bông',649000,949000,260000,360000,'S-XL',False),
    ('Áo cardigan dài nữ','CAT-FW-F',4,'Thu-Đông','Len truyền thống','Wool blend',549000,749000,195000,270000,'S-XL',False),
    ('Áo hoodie nữ','CAT-FW-F',5,'Thu-Đông','Thu-Đông','Cotton fleece',379000,479000,128000,162000,'S-XL',True),
    ('Áo nỉ nữ','CAT-FW-F',5,'Thu-Đông','Thu-Đông','Cotton fleece',329000,429000,110000,145000,'S-XL',True),
    ('Áo khoác dạ nữ','CAT-FW-F',4,'Thu-Đông','Thu-Đông','Wool blend',899000,1299000,340000,470000,'S-XL',False),
    ('Quần nỉ nữ','CAT-FW-F',2,'Thu-Đông','Thu-Đông','Cotton fleece',279000,379000,92000,128000,'S-XL',True),
    ('Váy len nữ','CAT-FW-F',2,'Thu-Đông','Len truyền thống','Wool blend',499000,649000,175000,230000,'S-XL',False),
    # CAT-ACT (30 SKU)
    ('Áo phông Dry-Tech nam','CAT-ACT',4,'4 Mùa','Activewear','Polyester Dry-Tech',249000,349000,85000,120000,'S-XXL',False),
    ('Áo phông Dry-Tech nữ','CAT-ACT',4,'4 Mùa','Activewear','Polyester Dry-Tech',229000,329000,78000,112000,'S-XL',False),
    ('Quần thể thao nam','CAT-ACT',4,'4 Mùa','Activewear','Polyester stretch',299000,399000,98000,135000,'S-XXL',False),
    ('Quần thể thao nữ','CAT-ACT',4,'4 Mùa','Activewear','Polyester stretch',279000,379000,92000,128000,'S-XL',False),
    ('Áo khoác gió thể thao','CAT-ACT',4,'4 Mùa','Activewear','Nylon ripstop',399000,549000,132000,185000,'S-XXL',False),
    ('Set thể thao nam','CAT-ACT',3,'4 Mùa','Activewear','Polyester Dry-Tech',449000,599000,150000,200000,'S-XXL',False),
    ('Set thể thao nữ','CAT-ACT',3,'4 Mùa','Activewear','Polyester Dry-Tech',429000,579000,142000,192000,'S-XL',False),
    ('Quần short thể thao','CAT-ACT',4,'Xuân-Hè','Activewear','Polyester mesh',199000,279000,65000,92000,'S-XXL',False),
    # CAT-KID (70 SKU)
    ('Áo phông trẻ em nam','CAT-KID',6,'4 Mùa','Kids','Cotton USA',129000,179000,42000,58000,'1-14Y',True),
    ('Áo phông trẻ em nữ','CAT-KID',6,'4 Mùa','Kids','Cotton USA',129000,179000,42000,58000,'1-14Y',True),
    ('Áo polo trẻ em','CAT-KID',5,'4 Mùa','Kids','Cotton Pique',179000,249000,58000,82000,'1-14Y',True),
    ('Quần jeans trẻ em','CAT-KID',5,'4 Mùa','Kids','Denim stretch',199000,299000,65000,100000,'1-14Y',True),
    ('Quần kaki trẻ em','CAT-KID',4,'4 Mùa','Kids','Cotton twill',179000,249000,58000,82000,'1-14Y',True),
    ('Áo khoác phao trẻ em','CAT-KID',5,'Thu-Đông','Kids','Polyester lót bông',349000,499000,120000,170000,'1-14Y',False),
    ('Áo len trẻ em','CAT-KID',5,'Thu-Đông','Kids','Wool blend',249000,399000,85000,135000,'1-14Y',False),
    ('Áo hoodie trẻ em','CAT-KID',5,'Thu-Đông','Kids','Cotton fleece',229000,329000,75000,110000,'1-14Y',True),
    ('Set đồ trẻ em nam','CAT-KID',5,'4 Mùa','Kids','Cotton blend',249000,349000,82000,115000,'1-14Y',True),
    ('Set đồ trẻ em nữ','CAT-KID',5,'4 Mùa','Kids','Cotton blend',249000,349000,82000,115000,'1-14Y',True),
    ('Quần short trẻ em','CAT-KID',4,'Xuân-Hè','Kids','Cotton twill',129000,199000,42000,65000,'1-14Y',True),
    ('Váy trẻ em','CAT-KID',5,'4 Mùa','Kids','Cotton blend',179000,279000,58000,92000,'1-14Y',True),
    ('Áo phông Dry-Tech trẻ em','CAT-KID',4,'4 Mùa','Kids','Polyester Dry-Tech',149000,229000,48000,75000,'1-14Y',False),
    ('Quần jogger trẻ em','CAT-KID',4,'4 Mùa','Kids','Cotton french terry',179000,249000,58000,82000,'1-14Y',True),
    ('Áo khoác gió trẻ em','CAT-KID',2,'4 Mùa','Kids','Nylon',249000,349000,82000,118000,'1-14Y',False),
    # CAT-ACC (45 SKU)
    ('Khăn quàng cổ len','CAT-ACC',5,'Thu-Đông','Phụ kiện','Wool blend',199000,299000,65000,100000,'Free',False),
    ('Mũ len','CAT-ACC',5,'Thu-Đông','Phụ kiện','Wool blend',149000,229000,48000,75000,'Free',False),
    ('Tất nam','CAT-ACC',4,'4 Mùa','Phụ kiện','Cotton blend',49000,79000,15000,25000,'Free',True),
    ('Tất nữ','CAT-ACC',4,'4 Mùa','Phụ kiện','Cotton blend',49000,79000,15000,25000,'Free',True),
    ('Balo thời trang','CAT-ACC',3,'4 Mùa','Phụ kiện','Polyester',299000,449000,98000,150000,'Free',False),
    ('Túi tote','CAT-ACC',4,'4 Mùa','Phụ kiện','Canvas cotton',199000,299000,65000,100000,'Free',True),
    ('Thắt lưng nam','CAT-ACC',4,'4 Mùa','Phụ kiện','Da PU',179000,279000,58000,92000,'Free',False),
    ('Khẩu trang vải','CAT-ACC',3,'4 Mùa','Phụ kiện','Cotton kháng khuẩn',49000,89000,15000,28000,'Free',True),
    ('Mũ lưỡi trai','CAT-ACC',5,'4 Mùa','Phụ kiện','Cotton canvas',129000,179000,42000,58000,'Free',True),
    ('Găng tay len','CAT-ACC',4,'Thu-Đông','Phụ kiện','Wool blend',99000,149000,32000,48000,'Free',False),
    ('Khăn tay cotton','CAT-ACC',4,'4 Mùa','Phụ kiện','Cotton',39000,69000,12000,22000,'Free',True),
]

# Color palette for product generation
COLORS_BASIC = ['Đen', 'Trắng', 'Xám', 'Navy', 'Be']
COLORS_EXT = ['Đen','Trắng','Xám','Navy','Be','Xanh rêu','Nâu','Đỏ đô','Xám nhạt']
COLORS_WINTER = ['Đen','Xám','Be','Navy','Nâu','Đỏ đô','Xám nhạt']
COLORS_KIDS = ['Xanh dương','Hồng','Vàng','Xanh lá','Cam','Navy','Đỏ','Trắng']
COLORS_ACC = ['Đen','Xám','Navy','Be','Nâu']


# =============================================================================
# GENERATOR CLASS
# =============================================================================
class CanifaGenerator:
    def __init__(self):
        self.stores = []  # list of dicts
        self.products = []  # list of dicts
        self.sales = []  # list of tuples for INSERT
        self.returns_data = []
        self.inventory = []
        self.store_costs_data = []
        self._build_stores()
        self._build_products()

    # ── Master Data Builders ──

    def _build_stores(self):
        for row in STORES_RAW:
            sid, name, reg, prov, dist, stype, area, rent, odate, mult = row
            self.stores.append({
                'store_id': sid, 'store_name': name, 'region_id': reg,
                'province': prov, 'district': dist, 'store_type': stype,
                'area_sqm': area, 'monthly_rent': int(rent),
                'open_date': date.fromisoformat(odate), 'status': 'Active',
                'rev_mult': mult,
            })

    def _build_products(self):
        """Generate ~500 products from templates."""
        pid_counter = defaultdict(int)
        prefix_map = {
            'CAT-ESS-M': 'EM', 'CAT-ESS-F': 'EF', 'CAT-SMC-M': 'SM',
            'CAT-SMC-F': 'SF', 'CAT-JKK-M': 'JM', 'CAT-JKK-F': 'JF',
            'CAT-FW-M': 'WM', 'CAT-FW-F': 'WF', 'CAT-ACT': 'AT',
            'CAT-KID': 'KD', 'CAT-ACC': 'AC',
        }

        for tmpl in PRODUCT_TEMPLATES:
            name_base, cat_id, n_variants, season, line, material, \
                rp_min, rp_max, cp_min, cp_max, size_range, is_cotton = tmpl

            pfx = prefix_map[cat_id]

            # Pick color palette
            if cat_id == 'CAT-KID':
                palette = COLORS_KIDS
            elif 'FW' in cat_id or season == 'Thu-Đông':
                palette = COLORS_WINTER
            elif cat_id == 'CAT-ACC':
                palette = COLORS_ACC
            elif n_variants > 5:
                palette = COLORS_EXT
            else:
                palette = COLORS_BASIC

            colors = random.sample(palette, min(n_variants, len(palette)))
            if len(colors) < n_variants:
                extras = [c for c in COLORS_EXT if c not in colors]
                colors += random.sample(extras, min(n_variants - len(colors), len(extras)))

            for color in colors[:n_variants]:
                pid_counter[pfx] += 1
                pid = f'PRD-{pfx}-{pid_counter[pfx]:03d}'
                retail = round(random.uniform(rp_min, rp_max) / 1000) * 1000
                cost = round(random.uniform(cp_min, cp_max) / 1000) * 1000
                cost_new = round(cost * 1.08 / 1000) * 1000 if is_cotton else None

                # Popularity weight (Pareto-like)
                pop = random.lognormvariate(0, 0.7)
                pop = max(0.1, min(5.0, pop))

                self.products.append({
                    'product_id': pid,
                    'product_name': f'{name_base} - {color}',
                    'category_id': cat_id,
                    'season': season,
                    'product_line': line,
                    'material': material,
                    'color': color,
                    'size_range': size_range,
                    'retail_price': retail,
                    'cost_price': cost,
                    'cost_price_new': cost_new,
                    'popularity_weight': round(pop, 3),
                    'launch_date': date(2020 + random.randint(0, 3), random.randint(1, 12), 1),
                    'status': 'Active',
                })

        # Override special SKUs for scenarios
        self._set_special_products()

    def _set_special_products(self):
        """Ensure scenario-specific products exist with correct attributes."""
        # PRD-MT-001 = Áo phông Dry-Tech nam - Đen (Scenario 1 surge)
        # Find the first Dry-Tech nam product and rename its ID
        for p in self.products:
            if 'Dry-Tech nam' in p['product_name'] and 'Đen' in p['product_name']:
                p['product_id'] = 'PRD-MT-001'
                p['popularity_weight'] = 4.5
                break

        # PRD-FW-045 = Áo sơ mi nữ công sở - declining
        for p in self.products:
            if 'sơ mi nữ công sở' in p['product_name'].lower() and p.get('_fw045') is None:
                p['product_id'] = 'PRD-FW-045'
                p['popularity_weight'] = 2.0
                p['_fw045'] = True
                break

        # PRD-FW-012/013/014 = Áo khoác len nữ dáng dài (top overstocked SKU)
        fw_coat_idx = 0
        for p in self.products:
            if 'khoác len nữ dáng dài' in p['product_name'].lower():
                fw_coat_idx += 1
                if fw_coat_idx <= 3:
                    p['product_id'] = f'PRD-FW-{fw_coat_idx + 11:03d}'
                    p['popularity_weight'] = 0.6  # slow seller

        # PRD-FW-008 = Áo len cổ lọ nam - Đen
        for p in self.products:
            if 'len cổ lọ nam' in p['product_name'].lower() and 'Đen' in p['product_name']:
                p['product_id'] = 'PRD-FW-008'
                p['popularity_weight'] = 0.7
                break

        # PRD-FW-022 = Áo phao nhẹ trẻ em - Xanh navy
        for p in self.products:
            if 'phao' in p['product_name'].lower() and 'trẻ em' in p['product_name'].lower():
                p['product_id'] = 'PRD-FW-022'
                p['popularity_weight'] = 0.5
                break

    # ── Transaction Generation ──

    def generate_transactions(self):
        """Generate all fact table data: sales, returns, inventory, store_costs."""
        print("Generating sales transactions...")
        self._generate_sales()
        print(f"  Sales: {len(self.sales):,} records")
        print("Generating returns...")
        self._generate_returns()
        print(f"  Returns: {len(self.returns_data):,} records")
        print("Generating inventory snapshots...")
        self._generate_inventory()
        print(f"  Inventory: {len(self.inventory):,} records")
        print("Generating store costs...")
        self._generate_store_costs()
        print(f"  Store costs: {len(self.store_costs_data):,} records")

    def _get_active_promo(self, d, channel_id, cat_id):
        """Return (promo_id, discount_pct) if a promotion is active, else (None, 0).
        Only ~35% of eligible transactions actually get the promo discount."""
        for prm in PROMOTIONS:
            pid, pname, ptype, sd, ed, dmin, dmax, channels, cats, _, _, _ = prm
            sd = date.fromisoformat(sd) if isinstance(sd, str) else sd
            ed = date.fromisoformat(ed) if isinstance(ed, str) else ed
            if not (sd <= d <= ed):
                continue
            ch_ok = (channels == 'All') or \
                    (channels == 'Online' and channel_id != 'CH-STORE') or \
                    (channels == 'Offline' and channel_id == 'CH-STORE')
            if not ch_ok:
                continue
            cat_ok = (cats == 'All') or (cat_id in cats)
            if not cat_ok:
                continue
            # Only apply promo to ~35% of eligible transactions
            if random.random() > 0.35:
                return None, 0
            disc = random.uniform(dmin, dmax) / 100
            return pid, disc
        return None, 0

    def _generate_sales(self):
        """Layer 1: Base volume, Layer 2: Seasonality, Layer 3: Anomalies."""
        all_days = []
        d = START_DATE
        while d <= END_DATE:
            all_days.append(d)
            d += timedelta(days=1)

        # Pre-compute product weights by category
        prod_by_cat = defaultdict(list)
        prod_weights_by_cat = defaultdict(list)
        prod_map = {p['product_id']: p for p in self.products}
        for p in self.products:
            prod_by_cat[p['category_id']].append(p)
            prod_weights_by_cat[p['category_id']].append(p['popularity_weight'])

        cat_ids = list(prod_by_cat.keys())
        # Category revenue share (approximate, for product selection)
        cat_share = {
            'CAT-ESS-M': 0.18, 'CAT-ESS-F': 0.15, 'CAT-SMC-M': 0.08, 'CAT-SMC-F': 0.10,
            'CAT-JKK-M': 0.07, 'CAT-JKK-F': 0.07, 'CAT-FW-M': 0.08, 'CAT-FW-F': 0.10,
            'CAT-ACT': 0.05, 'CAT-KID': 0.10, 'CAT-ACC': 0.02,
        }

        order_counter = 0
        tx_id = 0

        # Anomaly 1: Dry-Tech surge months
        drytech_surge_start = date(2024, 10, 1)
        # Anomaly 5: Sơ mi nữ decline start
        somi_decline_start = date(2024, 10, 1)

        for d in all_days:
            month = d.month
            dow = d.weekday()
            months_from_start = (d.year - START_DATE.year) * 12 + (d.month - START_DATE.month)
            growth = 1.0 + 0.10 * (months_from_start / 12)

            m_mult = MONTH_MULT[month]
            d_mult = DOW_MULT[dow]

            # ── Offline sales ──
            for store in self.stores:
                if store['open_date'] > d or store['status'] != 'Active':
                    continue

                s_mult = store['rev_mult']
                store_id = store['store_id']

                # Anomaly 6: New store ramp-up
                if store_id in NEW_STORES:
                    months_open = (d.year - store['open_date'].year) * 12 + (d.month - store['open_date'].month)
                    if months_open < 0:
                        continue
                    # Start at 30%, ramp +20%/month
                    ramp = min(1.0, 0.30 + 0.20 * months_open)
                    s_mult = store['rev_mult'] + (1.0 - store['rev_mult']) * ramp
                    # but cap to a reasonable level
                    s_mult = min(s_mult, 1.2)

                # Anomaly 6: Underperformer decline (last 6 months)
                if store_id in UNDERPERFORMERS and d >= date(2024, 10, 1):
                    months_decline = (d.year - 2024) * 12 + (d.month - 10)
                    s_mult *= (0.97 ** max(0, months_decline))

                base_n = BASE_RECORDS_PER_STORE
                n_records = max(1, round(base_n * s_mult * m_mult * d_mult * growth * random.uniform(0.85, 1.15)))

                # Distribute records across categories
                for _ in range(n_records):
                    # Pick category weighted by share × category_season
                    cat_weights = []
                    for cid in cat_ids:
                        cs = CAT_SEASON.get(cid, {}).get(month, 1.0)
                        cat_weights.append(cat_share.get(cid, 0.05) * cs)
                    cat = random.choices(cat_ids, weights=cat_weights, k=1)[0]

                    # Pick product within category
                    prods = prod_by_cat[cat]
                    weights = prod_weights_by_cat[cat]
                    product = random.choices(prods, weights=weights, k=1)[0]
                    pid = product['product_id']

                    # Quantity
                    qty = max(1, round(random.lognormvariate(math.log(BASE_QTY_MEAN), 0.5)))

                    # Anomaly 1: Dry-Tech surge
                    if pid == 'PRD-MT-001' and d >= drytech_surge_start:
                        mo = (d.year - 2024) * 12 + (d.month - 10)
                        qty = max(1, round(qty * (1.25 ** mo)))

                    # Anomaly 5: Sơ mi nữ decline
                    if pid == 'PRD-FW-045' and d >= somi_decline_start:
                        mo = (d.year - 2024) * 12 + (d.month - 10)
                        qty = max(1, round(qty * (0.95 ** mo)))

                    # Pricing
                    original_price = product['retail_price']
                    cost = product['cost_price']
                    # Use new cost from Sep 2024 for cotton products
                    if product['cost_price_new'] and d >= date(2024, 9, 1):
                        cost = product['cost_price_new']

                    # Promotion check
                    promo_id, disc_pct = self._get_active_promo(d, 'CH-STORE', product['category_id'])

                    # Baseline ad-hoc discounting (~25% of transactions, all periods)
                    if promo_id is None and random.random() < 0.25:
                        disc_pct = random.uniform(0.05, 0.15)

                    # Anomaly 5: More discounted sales in Q1/2025 (22%→31%)
                    if d >= date(2025, 1, 1) and d <= date(2025, 3, 31) and promo_id is None:
                        if random.random() < 0.10:  # extra discount on top of baseline
                            disc_pct = random.uniform(0.15, 0.30)

                    unit_price = round(original_price * (1 - disc_pct) / 1000) * 1000
                    if unit_price < 10000:
                        unit_price = 10000
                    discount_amount = (original_price - unit_price) * qty
                    revenue = qty * unit_price
                    gross_profit = revenue - qty * cost

                    # Order ID (group 2-3 records)
                    if random.random() < 0.45:  # ~45% chance of new order
                        order_counter += 1
                    oid = f'ORD-{d.strftime("%Y%m%d")}-{store_id[-3:]}-{order_counter:06d}'

                    tx_id += 1
                    self.sales.append((
                        d.isoformat(), store_id, 'CH-STORE', pid,
                        promo_id, qty, int(unit_price), int(original_price),
                        int(discount_amount), int(cost), int(revenue), int(gross_profit), oid
                    ))

            # ── Online sales ──
            online_channels = ['CH-WEB', 'CH-SHOPEE', 'CH-TIKTOK', 'CH-LAZADA']
            online_shares = [0.07, 0.05, 0.03, 0.02]

            # Anomaly 5: Increase online proportion in Q1/2025 (15%→18%)
            if d >= date(2025, 1, 1) and d <= date(2025, 3, 31):
                online_shares = [0.08, 0.055, 0.035, 0.025]  # total 19.5% vs 17%

            for ch_id, ch_share in zip(online_channels, online_shares):
                # Online volume relative to offline
                # Total offline records this day ≈ BASE * avg_mult * day_mults
                avg_store_mult = 1.0  # weighted average
                offline_estimate = BASE_RECORDS_PER_STORE * avg_store_mult * len(self.stores) * m_mult * d_mult * growth
                n_online = max(0, round(offline_estimate * ch_share / 0.83 * random.uniform(0.8, 1.2)))

                # Promo boost for online flash sales
                for prm in PROMOTIONS:
                    pid_prm, _, _, sd, ed, _, _, channels, _, _, _, _ = prm
                    sd = date.fromisoformat(sd) if isinstance(sd, str) else sd
                    ed = date.fromisoformat(ed) if isinstance(ed, str) else ed
                    if sd <= d <= ed:
                        if channels == 'Online' and ch_id in ('CH-SHOPEE', 'CH-TIKTOK', 'CH-LAZADA'):
                            n_online = round(n_online * 2.5)  # flash sale spike
                            break

                for _ in range(n_online):
                    cat_weights = []
                    for cid in cat_ids:
                        cs = CAT_SEASON.get(cid, {}).get(month, 1.0)
                        cat_weights.append(cat_share.get(cid, 0.05) * cs)
                    cat = random.choices(cat_ids, weights=cat_weights, k=1)[0]
                    prods = prod_by_cat[cat]
                    weights = prod_weights_by_cat[cat]
                    product = random.choices(prods, weights=weights, k=1)[0]
                    p_id = product['product_id']

                    qty = max(1, round(random.lognormvariate(math.log(max(1, BASE_QTY_MEAN - 2)), 0.5)))

                    # Anomaly 1: Dry-Tech surge (online too)
                    if p_id == 'PRD-MT-001' and d >= drytech_surge_start:
                        mo = (d.year - 2024) * 12 + (d.month - 10)
                        qty = max(1, round(qty * (1.25 ** mo)))

                    original_price = product['retail_price']
                    cost = product['cost_price']
                    if product['cost_price_new'] and d >= date(2024, 9, 1):
                        cost = product['cost_price_new']

                    promo_id, disc_pct = self._get_active_promo(d, ch_id, product['category_id'])

                    # Baseline ad-hoc discounting for online (~28%)
                    if promo_id is None and random.random() < 0.28:
                        disc_pct = random.uniform(0.05, 0.18)

                    # Anomaly 5: extra discounting Q1/2025
                    if d >= date(2025, 1, 1) and d <= date(2025, 3, 31) and promo_id is None:
                        if random.random() < 0.10:
                            disc_pct = random.uniform(0.15, 0.30)

                    unit_price = round(original_price * (1 - disc_pct) / 1000) * 1000
                    if unit_price < 10000:
                        unit_price = 10000
                    discount_amount = (original_price - unit_price) * qty
                    revenue = qty * unit_price
                    gross_profit = revenue - qty * cost

                    order_counter += 1
                    oid = f'ORD-{d.strftime("%Y%m%d")}-ONL-{order_counter:06d}'

                    tx_id += 1
                    self.sales.append((
                        d.isoformat(), None, ch_id, p_id,
                        promo_id, qty, int(unit_price), int(original_price),
                        int(discount_amount), int(cost), int(revenue), int(gross_profit), oid
                    ))

            if d.day == 1:
                print(f"  {d.strftime('%Y-%m')}: {len(self.sales):,} records so far")

    def _generate_returns(self):
        """Generate return records from sales (sampled by channel return rate)."""
        for s in self.sales:
            # s = (date, store_id, channel_id, product_id, promo_id, qty, unit_price, ...)
            ch = s[2]
            rate = RETURN_RATES.get(ch, 0.05)
            if random.random() < rate:
                ret_qty = max(1, random.randint(1, min(3, s[5])))
                ret_amount = ret_qty * s[6]  # unit_price
                ret_date = date.fromisoformat(s[0]) + timedelta(days=random.randint(1, 14))
                if ret_date > END_DATE:
                    ret_date = END_DATE
                reason = random.choices(
                    [r[0] for r in RETURN_REASONS],
                    weights=[r[1] for r in RETURN_REASONS], k=1
                )[0]
                # Boost "Không đúng mô tả" for online
                if ch in ('CH-TIKTOK', 'CH-SHOPEE') and random.random() < 0.3:
                    reason = 'Không đúng mô tả'

                self.returns_data.append((
                    ret_date.isoformat(), None, s[1], ch, s[3],
                    ret_qty, int(ret_amount), reason
                ))

    def _generate_inventory(self):
        """Generate monthly inventory snapshots for each store × top products."""
        # Only track top ~100 products per store (by popularity) to keep row count manageable
        top_n = 80
        prod_map = {p['product_id']: p for p in self.products}

        # Aggregate monthly sales by store × product
        monthly_sales = defaultdict(lambda: defaultdict(int))  # (store_id, ym) → {product_id: qty}
        for s in self.sales:
            if s[1] is None:  # online, no store
                continue
            ym = s[0][:7]  # YYYY-MM
            monthly_sales[(s[1], ym)][s[3]] += s[5]

        # Generate snapshots month by month
        d = date(2023, 7, 31)
        while d <= END_DATE:
            ym = d.strftime('%Y-%m')
            snapshot_date = d

            for store in self.stores:
                if store['open_date'] > d:
                    continue
                sid = store['store_id']

                # Get this store's top products (by total sales volume across all months)
                store_total = defaultdict(int)
                for ym2 in monthly_sales:
                    if ym2[0] == sid:
                        for pid, qty in monthly_sales[ym2].items():
                            store_total[pid] += qty

                if not store_total:
                    # New store with no sales yet — use random top products
                    sorted_prods = sorted(self.products, key=lambda x: x['popularity_weight'], reverse=True)[:top_n]
                else:
                    sorted_prods_ids = sorted(store_total, key=store_total.get, reverse=True)[:top_n]
                    sorted_prods = [prod_map[pid] for pid in sorted_prods_ids if pid in prod_map]

                for product in sorted_prods:
                    pid = product['product_id']
                    sold = monthly_sales.get((sid, ym), {}).get(pid, 0)

                    # Base inventory: 1.5-3x monthly sales
                    base_inv = max(5, round(sold * random.uniform(1.5, 3.0)))

                    # Seasonal products: high inventory in fall, low in spring
                    if product['season'] == 'Thu-Đông':
                        if d.month in (10, 11, 12, 1):
                            base_inv = round(base_inv * 2.0)
                        elif d.month in (3, 4, 5, 6, 7):
                            base_inv = max(0, round(base_inv * 0.3))

                    # Anomaly 3: Overstock at specific stores
                    if sid in OVERSTOCK_STORES and product['season'] == 'Thu-Đông':
                        if d.month in (12, 1, 2, 3):
                            base_inv = round(base_inv * 2.5)

                    # Anomaly 4: Inventory days increasing over time
                    months_in = (d.year - START_DATE.year) * 12 + (d.month - START_DATE.month)
                    inv_creep = 1.0 + 0.015 * months_in  # +1.5%/month
                    base_inv = round(base_inv * inv_creep)

                    received = max(0, round(sold * random.uniform(0.8, 1.5)))
                    # Last received date
                    if received > 0:
                        lr = d - timedelta(days=random.randint(1, 25))
                    else:
                        lr = d - timedelta(days=random.randint(30, 120))

                    # Anomaly 3: Overstock stores — aging stock
                    if sid in OVERSTOCK_STORES and product['season'] == 'Thu-Đông' and d.month in (1, 2, 3):
                        lr = d - timedelta(days=random.randint(90, 150))

                    # Anomaly 1: Dry-Tech inventory depleting
                    if pid == 'PRD-MT-001' and d >= date(2024, 12, 1):
                        mo = (d.year - 2024) * 12 + (d.month - 12)
                        base_inv = max(10, round(base_inv * (0.5 ** (mo + 1))))
                        if d >= date(2025, 3, 1):
                            base_inv = max(2, round(200 / len(self.stores) * random.uniform(0.5, 1.5)))

                    self.inventory.append((
                        snapshot_date.isoformat(), sid, pid,
                        base_inv, received, sold, lr.isoformat()
                    ))

            # Next month end
            if d.month == 12:
                d = date(d.year + 1, 1, 31)
            else:
                nm = d.month + 1
                ny = d.year
                if nm > 12:
                    nm = 1
                    ny += 1
                # Last day of next month
                if nm == 12:
                    d = date(ny, 12, 31)
                else:
                    d = date(ny, nm + 1, 1) - timedelta(days=1)
                    if nm + 1 > 12:
                        d = date(ny, 12, 31)

        print(f"  Inventory snapshots: {len(self.inventory):,}")

    def _generate_store_costs(self):
        """Generate monthly operating costs for each store."""
        d = date(2023, 7, 1)
        while d <= END_DATE:
            for store in self.stores:
                if store['open_date'] > d:
                    continue
                rent = store['monthly_rent']
                num_staff = max(4, int(store['area_sqm'] / 25))
                avg_salary = random.uniform(7000000, 10000000)
                staff = round(num_staff * avg_salary)
                utilities = round(random.uniform(3000000, 8000000))
                other = round(random.uniform(2000000, 5000000))
                total = rent + staff + utilities + other
                self.store_costs_data.append((
                    d.isoformat(), store['store_id'],
                    int(rent), int(staff), int(utilities), int(other), int(total)
                ))
            # Next month
            if d.month == 12:
                d = date(d.year + 1, 1, 1)
            else:
                d = date(d.year, d.month + 1, 1)

    # ── MySQL Population ──

    def populate_mysql(self, phase='all'):
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()

        if phase in ('all', 'schema'):
            print("Creating schema...")
            for stmt in DDL_SQL.split(';'):
                stmt = stmt.strip()
                if stmt:
                    try:
                        cur.execute(stmt)
                    except Exception as e:
                        if 'already exists' not in str(e).lower():
                            print(f"  DDL warning: {e}")
            conn.commit()

        cur.execute(f'USE {DB_NAME}')

        def batch_insert(table, columns, rows, on_dup=''):
            if not rows:
                return
            cols = ', '.join(columns)
            for i in range(0, len(rows), BATCH):
                batch = rows[i:i + BATCH]
                placeholders = ', '.join(['%s'] * len(columns))
                vals = ', '.join(
                    cur.mogrify(f'({placeholders})', row).decode('utf-8')
                    for row in batch
                )
                sql = f'INSERT INTO {table} ({cols}) VALUES {vals} {on_dup}'
                cur.execute(sql)
            conn.commit()

        def simple_insert(table, columns, rows):
            if not rows:
                return
            cols = ', '.join(columns)
            ph = ', '.join(['%s'] * len(columns))
            sql = f'INSERT INTO {table} ({cols}) VALUES ({ph})'
            for i in range(0, len(rows), BATCH):
                cur.executemany(sql, rows[i:i + BATCH])
            conn.commit()

        if phase in ('all', 'master'):
            print("Inserting master data...")

            # Regions
            simple_insert('regions',
                ['region_id','region_name','region_name_en','description'],
                REGIONS)

            # Channels
            simple_insert('channels',
                ['channel_id','channel_name','channel_type','commission_rate','shipping_subsidy_rate'],
                CHANNELS)

            # Categories
            simple_insert('categories',
                ['category_id','category_group','category_name','subcategory','description'],
                CATEGORIES)

            # Products
            prod_rows = [
                (p['product_id'], p['product_name'], p['category_id'], p['season'],
                 p['product_line'], p['material'], p['color'], p['size_range'],
                 p['retail_price'], p['cost_price'], p['cost_price_new'],
                 p['popularity_weight'], p['launch_date'].isoformat(), p['status'])
                for p in self.products
            ]
            simple_insert('products',
                ['product_id','product_name','category_id','season','product_line',
                 'material','color','size_range','retail_price','cost_price','cost_price_new',
                 'popularity_weight','launch_date','status'],
                prod_rows)

            # Stores
            store_rows = [
                (s['store_id'], s['store_name'], s['region_id'], s['province'],
                 s['district'], None, s['store_type'], s['area_sqm'],
                 s['monthly_rent'], s['open_date'].isoformat(), s['status'])
                for s in self.stores
            ]
            simple_insert('stores',
                ['store_id','store_name','region_id','province','district','address',
                 'store_type','area_sqm','monthly_rent','open_date','status'],
                store_rows)

            # Promotions
            promo_rows = [
                (p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8], int(p[9]), int(p[10]), p[11])
                for p in PROMOTIONS
            ]
            simple_insert('promotions',
                ['promo_id','promo_name','promo_type','start_date','end_date',
                 'discount_percent_min','discount_percent_max','applicable_channels',
                 'applicable_categories','marketing_spend','platform_fee','description'],
                promo_rows)

            # Metadata
            self._insert_metadata(cur, conn)

            print(f"  Regions: {len(REGIONS)}")
            print(f"  Stores: {len(self.stores)}")
            print(f"  Categories: {len(CATEGORIES)}")
            print(f"  Products: {len(self.products)}")
            print(f"  Channels: {len(CHANNELS)}")
            print(f"  Promotions: {len(PROMOTIONS)}")

        if phase in ('all', 'transactions'):
            print("Inserting transaction data...")

            # Sales
            print(f"  Inserting {len(self.sales):,} sales records...")
            simple_insert('sales_transactions',
                ['transaction_date','store_id','channel_id','product_id','promo_id',
                 'quantity','unit_price','original_price','discount_amount','cost_price',
                 'revenue','gross_profit','order_id'],
                self.sales)

            # Returns
            print(f"  Inserting {len(self.returns_data):,} returns...")
            simple_insert('returns',
                ['return_date','original_transaction_id','store_id','channel_id','product_id',
                 'quantity','return_amount','reason'],
                self.returns_data)

            # Inventory
            print(f"  Inserting {len(self.inventory):,} inventory snapshots...")
            simple_insert('inventory_snapshots',
                ['snapshot_date','store_id','product_id','quantity_on_hand',
                 'quantity_received','quantity_sold','last_received_date'],
                self.inventory)

            # Store costs
            print(f"  Inserting {len(self.store_costs_data):,} store cost records...")
            simple_insert('store_costs',
                ['month_date','store_id','rent','staff_cost','utilities','other_costs','total_cost'],
                self.store_costs_data)

        cur.close()
        conn.close()
        print("MySQL population complete.")

    def _insert_metadata(self, cur, conn):
        """Insert metadata tables."""
        meta_tables = [
            ('regions','Bảng khu vực địa lý — phân vùng kinh doanh','Geographic regions for business segmentation','6 khu vực: HN, MB, MT, HCM, MN, TN',6),
            ('stores','Bảng cửa hàng — 110 cửa hàng toàn quốc','110 retail stores nationwide','Chứa thông tin vị trí, diện tích, loại hình, tiền thuê',110),
            ('categories','Bảng phân loại sản phẩm','Product categories hierarchy','11 category: Essentials, Smart Casual, Jeans-Kaki, Thu-Đông, Activewear, Kids, Phụ kiện',11),
            ('products','Bảng sản phẩm — ~500 SKU','~500 SKUs with pricing and attributes','Giá bán, giá vốn, mùa, popularity weight cho mô phỏng Pareto',len(self.products)),
            ('channels','Bảng kênh bán hàng','Sales channels (offline + online)','5 kênh: Cửa hàng, Website, Shopee, TikTok, Lazada',5),
            ('promotions','Bảng chương trình khuyến mại','8 promotional campaigns','Bao gồm flash sale, seasonal, bundle, clearance',8),
            ('sales_transactions','Bảng giao dịch bán hàng — grain: 1 line item','Sales transactions at line item level','21 tháng data (07/2023–03/2025), offline + online',None),
            ('returns','Bảng trả hàng','Product returns','Return rate: offline 3%, online 8-14%',None),
            ('inventory_snapshots','Bảng snapshot tồn kho cuối tháng','Monthly inventory snapshots per store × product','Grain: store × product × month',None),
            ('store_costs','Bảng chi phí vận hành cửa hàng theo tháng','Monthly store operating costs','Rent, staff, utilities, other',None),
        ]
        cur.executemany(
            'INSERT INTO _meta_tables (table_name,description_vi,description_en,business_context,row_count_approx) VALUES (%s,%s,%s,%s,%s)',
            meta_tables
        )

        # KPI definitions
        kpis = [
            ('Doanh thu thuần (Net Revenue)','SELECT SUM(revenue) - COALESCE((SELECT SUM(return_amount) FROM returns),0) FROM sales_transactions','Tổng doanh thu sau trừ giảm giá và trả hàng','Câu 1,2,5,6'),
            ('Doanh thu gộp (Gross Revenue)','SELECT SUM(quantity * original_price) FROM sales_transactions','Tổng doanh thu trước giảm giá','Câu 1'),
            ('Biên lợi nhuận gộp (Gross Margin %)','SELECT (SUM(revenue) - SUM(quantity * cost_price)) / SUM(revenue) * 100 FROM sales_transactions','Tỷ lệ lợi nhuận gộp trên doanh thu','Câu 5'),
            ('DT/m² (Revenue per sqm)','SELECT SUM(s.revenue)/st.area_sqm FROM sales_transactions s JOIN stores st ON s.store_id=st.store_id GROUP BY st.store_id','Doanh thu trên mỗi m² mặt bằng, đơn vị VND/m²/tháng','Câu 6'),
            ('SSSG (Same-Store Sales Growth)','SELECT (SUM(CASE WHEN YEAR(transaction_date)=2025 THEN revenue END) - SUM(CASE WHEN YEAR(transaction_date)=2024 THEN revenue END)) / SUM(CASE WHEN YEAR(transaction_date)=2024 THEN revenue END) * 100 FROM sales_transactions WHERE store_id IS NOT NULL','Tăng trưởng doanh thu cùng cửa hàng so với cùng kỳ','Câu 6'),
            ('APT (Average Per Transaction)','SELECT SUM(revenue) / COUNT(DISTINCT order_id) FROM sales_transactions','Giá trị trung bình mỗi đơn hàng','Câu 6'),
            ('UPT (Units Per Transaction)','SELECT SUM(quantity) / COUNT(DISTINCT order_id) FROM sales_transactions','Số sản phẩm trung bình mỗi đơn hàng','Câu 2,6'),
            ('Sell-through Rate','SELECT SUM(quantity_sold) / (SUM(quantity_sold) + SUM(quantity_on_hand)) * 100 FROM inventory_snapshots','Tỷ lệ bán hết so với tồn kho','Câu 3'),
            ('Inventory Days','SELECT (AVG(quantity_on_hand * p.cost_price) / (SUM(s.quantity * s.cost_price)/30)) FROM inventory_snapshots i JOIN products p ON i.product_id=p.product_id JOIN sales_transactions s ON s.product_id=p.product_id','Số ngày quay vòng tồn kho','Câu 4'),
            ('Return Rate','SELECT COUNT(*) / (SELECT COUNT(*) FROM sales_transactions) * 100 FROM returns','Tỷ lệ trả hàng theo channel','Câu 3 follow-up'),
            ('Promotion ROI','SELECT (SUM(s.revenue) - p.marketing_spend - p.platform_fee) / (p.marketing_spend + p.platform_fee) FROM sales_transactions s JOIN promotions p ON s.promo_id=p.promo_id GROUP BY p.promo_id','ROI của từng chương trình khuyến mại','Câu 2'),
            ('Discount Depth','SELECT AVG(discount_amount / (original_price * quantity)) * 100 FROM sales_transactions WHERE discount_amount > 0','Mức giảm giá trung bình khi có KM','Câu 2,5'),
        ]
        cur.executemany(
            'INSERT INTO _meta_kpi (kpi_name,formula_sql,description_vi,related_questions) VALUES (%s,%s,%s,%s)',
            kpis
        )

        # Glossary
        glossary = [
            ('Doanh thu thuần','Net Revenue','Doanh thu sau khi trừ giảm giá và giá trị hàng trả lại'),
            ('Biên lợi nhuận gộp','Gross Margin','Tỷ lệ (Doanh thu - Giá vốn) / Doanh thu, thể hiện hiệu quả kinh doanh cốt lõi'),
            ('SSSG','Same-Store Sales Growth','Tăng trưởng doanh thu của các cửa hàng đã hoạt động ≥12 tháng so với cùng kỳ năm trước'),
            ('APT','Average Per Transaction','Giá trị trung bình mỗi giao dịch = Tổng DT / Số đơn hàng'),
            ('UPT','Units Per Transaction','Số sản phẩm trung bình trong mỗi đơn hàng'),
            ('CR','Conversion Rate','Tỷ lệ khách vào cửa hàng thực hiện mua hàng'),
            ('Sell-through Rate','Sell-through Rate','Tỷ lệ hàng bán được so với tổng hàng nhập, công thức: Sold / (Sold + On-hand)'),
            ('Inventory Days','Days of Inventory','Số ngày trung bình để bán hết tồn kho hiện tại, = (Tồn kho TB / COGS ngày) × 30'),
            ('Markdown','Markdown','Giảm giá sản phẩm — thường áp dụng cuối mùa để giải phóng tồn kho'),
            ('Season','Mùa hàng','Phân loại theo mùa: Xuân-Hè (SS), Thu-Đông (FW), 4 Mùa (year-round)'),
            ('SKU','Stock Keeping Unit','Đơn vị quản lý hàng tồn kho — 1 SKU = 1 sản phẩm cụ thể (màu + size)'),
            ('Flagship','Flagship Store','Cửa hàng trọng điểm, diện tích lớn, vị trí đắc địa, thể hiện hình ảnh thương hiệu'),
            ('TTTM','Shopping Mall Store','Cửa hàng trong trung tâm thương mại'),
            ('Aging Stock','Hàng tồn lâu','Hàng tồn kho >90 ngày kể từ lần nhập cuối — rủi ro lỗi mốt, cần markdown'),
            ('Bundle','Combo khuyến mại','Chương trình mua nhiều tặng thêm, ví dụ: Mua 3 Tặng 1'),
            ('Flash Sale','Flash Sale','Chương trình giảm giá ngắn hạn (1-4 ngày) trên kênh online, thường discount sâu 30-60%'),
            ('Clearance','Xả hàng cuối mùa','Giảm giá 40-70% để giải phóng hàng seasonal tồn kho'),
            ('YoY','Year-over-Year','So sánh cùng kỳ năm trước'),
            ('MoM','Month-over-Month','So sánh tháng trước'),
            ('QoQ','Quarter-over-Quarter','So sánh quý trước'),
            ('COGS','Cost of Goods Sold','Giá vốn hàng bán — chi phí sản xuất và nguyên liệu'),
            ('Omnichannel','Đa kênh','Mô hình bán hàng tích hợp offline + online'),
        ]
        cur.executemany(
            'INSERT INTO _meta_glossary (term_vi,term_en,definition) VALUES (%s,%s,%s)',
            glossary
        )

        # Meta columns (simplified — key columns only)
        meta_cols = [
            ('sales_transactions','transaction_date','DATE','Ngày giao dịch','Transaction date','ngày','2024-06-15'),
            ('sales_transactions','store_id','VARCHAR(15)','Mã cửa hàng (NULL nếu online)','Store ID','','STR-HN-001'),
            ('sales_transactions','channel_id','VARCHAR(10)','Mã kênh bán hàng','Channel ID','','CH-STORE'),
            ('sales_transactions','product_id','VARCHAR(15)','Mã sản phẩm','Product ID','','PRD-EM-001'),
            ('sales_transactions','promo_id','VARCHAR(10)','Mã KM (NULL nếu không KM)','Promotion ID','','PRM-001'),
            ('sales_transactions','quantity','INT','Số lượng bán','Quantity sold','units','5'),
            ('sales_transactions','unit_price','DECIMAL(12,0)','Đơn giá bán thực tế sau giảm','Actual selling price','VND','299000'),
            ('sales_transactions','original_price','DECIMAL(12,0)','Giá niêm yết gốc','Original listed price','VND','399000'),
            ('sales_transactions','discount_amount','DECIMAL(12,0)','Tổng tiền giảm giá','Total discount amount','VND','500000'),
            ('sales_transactions','cost_price','DECIMAL(12,0)','Giá vốn tại thời điểm bán','Cost price at time of sale','VND','120000'),
            ('sales_transactions','revenue','DECIMAL(15,0)','Doanh thu = quantity × unit_price','Revenue','VND','1495000'),
            ('sales_transactions','gross_profit','DECIMAL(15,0)','LN gộp = revenue - qty × cost','Gross profit','VND','895000'),
            ('sales_transactions','order_id','VARCHAR(20)','Mã đơn hàng (nhóm line items)','Order ID','','ORD-20240615-001-000123'),
            ('products','retail_price','DECIMAL(12,0)','Giá bán lẻ niêm yết','Retail price','VND','299000'),
            ('products','cost_price','DECIMAL(12,0)','Giá vốn','Cost price','VND','95000'),
            ('products','cost_price_new','DECIMAL(12,0)','Giá vốn mới từ T9/2024 (cotton +8%)','New cost price since Sep 2024','VND','103000'),
            ('products','popularity_weight','DECIMAL(5,3)','Trọng số Pareto: >1 bán chạy, <1 chậm','Popularity weight for simulation','','2.500'),
            ('stores','area_sqm','DECIMAL(8,2)','Diện tích mặt bằng','Store floor area','m²','120.00'),
            ('stores','monthly_rent','DECIMAL(15,0)','Tiền thuê mặt bằng/tháng','Monthly rent','VND','80000000'),
            ('inventory_snapshots','quantity_on_hand','INT','Số lượng tồn kho','Stock on hand','units','150'),
            ('inventory_snapshots','quantity_received','INT','Số lượng nhập trong tháng','Quantity received this month','units','200'),
            ('inventory_snapshots','quantity_sold','INT','Số lượng bán trong tháng','Quantity sold this month','units','180'),
            ('inventory_snapshots','last_received_date','DATE','Ngày nhập hàng gần nhất','Last stock receipt date','ngày','2024-11-15'),
            ('store_costs','rent','DECIMAL(15,0)','Tiền thuê mặt bằng','Rent','VND','80000000'),
            ('store_costs','staff_cost','DECIMAL(15,0)','Chi phí nhân sự (lương+BHXH)','Staff cost','VND','35000000'),
            ('store_costs','total_cost','DECIMAL(15,0)','Tổng chi phí vận hành','Total operating cost','VND','125000000'),
            ('returns','return_amount','DECIMAL(15,0)','Giá trị hoàn trả','Return amount','VND','299000'),
            ('returns','reason','ENUM','Lý do trả hàng','Return reason','','Size không vừa'),
        ]
        cur.executemany(
            'INSERT INTO _meta_columns (table_name,column_name,data_type,description_vi,description_en,unit,example_values) VALUES (%s,%s,%s,%s,%s,%s,%s)',
            meta_cols
        )

        conn.commit()
        print(f"  Metadata: {len(meta_tables)} tables, {len(kpis)} KPIs, {len(glossary)} glossary terms, {len(meta_cols)} column descriptions")

    # ── SQL Export ──

    def export_sql(self):
        """Export all data to SQL files in canifa_sql/."""
        os.makedirs(SQL_DIR, exist_ok=True)
        print(f"\nExporting SQL files to {SQL_DIR}/")

        # Helper
        def esc(v):
            if v is None:
                return 'NULL'
            if isinstance(v, (int, float)):
                return str(int(v)) if isinstance(v, float) and v == int(v) else str(v)
            s = str(v).replace("\\", "\\\\").replace("'", "\\'")
            return f"'{s}'"

        def write_inserts(f, table, columns, rows, batch=BATCH):
            if not rows:
                return
            col_str = ', '.join(columns)
            for i in range(0, len(rows), batch):
                chunk = rows[i:i + batch]
                vals = []
                for row in chunk:
                    vals.append('(' + ', '.join(esc(v) for v in row) + ')')
                f.write(f"INSERT INTO `{table}` ({col_str}) VALUES\n")
                f.write(',\n'.join(vals))
                f.write(';\n\n')

        # 01_ddl_schema.sql
        with open(os.path.join(SQL_DIR, '01_ddl_schema.sql'), 'w', encoding='utf-8') as f:
            f.write("-- ============================================================\n")
            f.write("-- 01_ddl_schema.sql\n")
            f.write("-- CANIFA Retail Fashion — Schema Definition\n")
            f.write("-- ============================================================\n\n")
            f.write(DDL_SQL)
            f.write("\n")
        print("  01_ddl_schema.sql")

        # 02_metadata.sql
        with open(os.path.join(SQL_DIR, '02_metadata.sql'), 'w', encoding='utf-8') as f:
            f.write("-- ============================================================\n")
            f.write("-- 02_metadata.sql\n")
            f.write("-- CANIFA Retail Fashion — Metadata\n")
            f.write("-- ============================================================\n\n")
            f.write("USE canifa_retail_demo;\n\n")
            # Export from MySQL
            conn = mysql.connector.connect(**DB_CONFIG, database=DB_NAME, charset='utf8mb4')
            cur = conn.cursor()
            for tbl in ['_meta_tables', '_meta_columns', '_meta_kpi', '_meta_glossary']:
                cur.execute(f"SELECT * FROM `{tbl}`")
                rows = cur.fetchall()
                cur.execute(f"DESCRIBE `{tbl}`")
                cols = [c[0] for c in cur.fetchall()]
                write_inserts(f, tbl, cols, rows, batch=100)
            cur.close()
            conn.close()
        print("  02_metadata.sql")

        # 03_master_data.sql
        with open(os.path.join(SQL_DIR, '03_master_data.sql'), 'w', encoding='utf-8') as f:
            f.write("-- ============================================================\n")
            f.write("-- 03_master_data.sql\n")
            f.write("-- CANIFA Retail Fashion — Master/Dimension Data\n")
            f.write("-- ============================================================\n\n")
            f.write("USE canifa_retail_demo;\n")
            f.write("SET FOREIGN_KEY_CHECKS = 0;\n\n")

            conn = mysql.connector.connect(**DB_CONFIG, database=DB_NAME, charset='utf8mb4')
            cur = conn.cursor()
            for tbl in ['regions', 'channels', 'categories', 'products', 'stores', 'promotions']:
                cur.execute(f"SELECT * FROM `{tbl}`")
                rows = cur.fetchall()
                cur.execute(f"DESCRIBE `{tbl}`")
                cols = [c[0] for c in cur.fetchall()]
                f.write(f"-- {tbl}: {len(rows)} records\n")
                write_inserts(f, tbl, cols, rows, batch=100)
            cur.close()
            conn.close()

            f.write("\nSET FOREIGN_KEY_CHECKS = 1;\n")
        print("  03_master_data.sql")

        # 04x_transaction_data — split per table to stay under GitHub 100MB limit
        conn = mysql.connector.connect(**DB_CONFIG, database=DB_NAME, charset='utf8mb4')
        cur = conn.cursor()

        # Split sales into 2 files to stay under GitHub 100MB limit
        tx_files = [
            (['04a_sales_1.sql', '04a_sales_2.sql'], 'sales_transactions'),
            (['04b_returns.sql'], 'returns'),
            (['04c_inventory.sql'], 'inventory_snapshots'),
            (['04d_store_costs.sql'], 'store_costs'),
        ]
        for fnames, tbl in tx_files:
            cur.execute(f"SELECT COUNT(*) FROM `{tbl}`")
            cnt = cur.fetchone()[0]
            cur.execute(f"DESCRIBE `{tbl}`")
            cols = [c[0] for c in cur.fetchall()]
            col_str = ', '.join(cols)

            rows_per_file = (cnt // len(fnames)) + 1
            cur.execute(f"SELECT * FROM `{tbl}`")

            for fi, fname in enumerate(fnames):
                with open(os.path.join(SQL_DIR, fname), 'w', encoding='utf-8') as f:
                    f.write(f"-- {fname}\n")
                    f.write(f"-- CANIFA Retail Fashion — {tbl} (part {fi+1}/{len(fnames)})\n\n")
                    f.write("USE canifa_retail_demo;\n")
                    f.write("SET FOREIGN_KEY_CHECKS = 0;\n")
                    f.write("SET autocommit = 0;\n\n")

                    written = 0
                    batch_rows = []
                    for row in cur:
                        batch_rows.append(row)
                        if len(batch_rows) >= BATCH:
                            vals = ['(' + ', '.join(esc(v) for v in r) + ')' for r in batch_rows]
                            f.write(f"INSERT INTO `{tbl}` ({col_str}) VALUES\n")
                            f.write(',\n'.join(vals))
                            f.write(';\n\n')
                            written += len(batch_rows)
                            batch_rows = []
                            if fi < len(fnames) - 1 and written >= rows_per_file:
                                break
                    if batch_rows:
                        vals = ['(' + ', '.join(esc(v) for v in r) + ')' for r in batch_rows]
                        f.write(f"INSERT INTO `{tbl}` ({col_str}) VALUES\n")
                        f.write(',\n'.join(vals))
                        f.write(';\n\n')

                    f.write("COMMIT;\n")
                    f.write("SET FOREIGN_KEY_CHECKS = 1;\n")
                    f.write("SET autocommit = 1;\n")
                print(f"  {fname}")

        cur.close()
        conn.close()

        # 05_validation_queries.sql
        self._write_validation_sql()
        print("  05_validation_queries.sql")

        # README.md
        self._write_readme()
        print("  README.md")

    def _write_validation_sql(self):
        path = os.path.join(SQL_DIR, '05_validation_queries.sql')
        with open(path, 'w', encoding='utf-8') as f:
            f.write("-- ============================================================\n")
            f.write("-- 05_validation_queries.sql\n")
            f.write("-- CANIFA Retail Fashion — Validation Queries\n")
            f.write("-- ============================================================\n\n")
            f.write("USE canifa_retail_demo;\n\n")
            f.write("""
-- 1. Referential integrity
SELECT 'orphan_sales_store' AS check_name, COUNT(*) AS issues
FROM sales_transactions s LEFT JOIN stores st ON s.store_id = st.store_id
WHERE s.store_id IS NOT NULL AND st.store_id IS NULL
UNION ALL
SELECT 'orphan_sales_product', COUNT(*)
FROM sales_transactions s LEFT JOIN products p ON s.product_id = p.product_id
WHERE p.product_id IS NULL
UNION ALL
SELECT 'orphan_sales_channel', COUNT(*)
FROM sales_transactions s LEFT JOIN channels c ON s.channel_id = c.channel_id
WHERE c.channel_id IS NULL
UNION ALL
SELECT 'orphan_sales_promo', COUNT(*)
FROM sales_transactions s LEFT JOIN promotions pr ON s.promo_id = pr.promo_id
WHERE s.promo_id IS NOT NULL AND pr.promo_id IS NULL;

-- 2. Revenue = quantity × unit_price
SELECT 'revenue_mismatch' AS check_name, COUNT(*) AS issues
FROM sales_transactions
WHERE ABS(revenue - quantity * unit_price) > 1;

-- 3. Gross profit check
SELECT 'profit_mismatch' AS check_name, COUNT(*) AS issues
FROM sales_transactions
WHERE ABS(gross_profit - (revenue - quantity * cost_price)) > 1;

-- 4. No negative values
SELECT 'negative_revenue' AS check_name, COUNT(*) AS issues
FROM sales_transactions WHERE revenue < 0
UNION ALL
SELECT 'negative_quantity', COUNT(*)
FROM sales_transactions WHERE quantity <= 0
UNION ALL
SELECT 'negative_inventory', COUNT(*)
FROM inventory_snapshots WHERE quantity_on_hand < 0;

-- 5. Monthly revenue trend (seasonality check)
SELECT DATE_FORMAT(transaction_date, '%Y-%m') AS month,
       ROUND(SUM(revenue) / 1e9, 2) AS revenue_billion_vnd,
       COUNT(DISTINCT order_id) AS num_orders,
       COUNT(*) AS num_records
FROM sales_transactions
GROUP BY 1
ORDER BY 1;

-- 6. Pareto check: top 20% SKU revenue share
SELECT
  CASE WHEN rn <= total * 0.2 THEN 'Top 20%' ELSE 'Bottom 80%' END AS segment,
  ROUND(SUM(sku_revenue) / 1e9, 2) AS revenue_bn,
  ROUND(SUM(sku_revenue) / (SELECT SUM(revenue) FROM sales_transactions) * 100, 1) AS pct
FROM (
    SELECT product_id, SUM(revenue) AS sku_revenue,
           ROW_NUMBER() OVER (ORDER BY SUM(revenue) DESC) AS rn,
           (SELECT COUNT(DISTINCT product_id) FROM sales_transactions) AS total
    FROM sales_transactions GROUP BY product_id
) t
GROUP BY 1;

-- 7. Scenario 1: Top 10 best sellers (3 months)
SELECT p.product_id, p.product_name, p.category_id,
       SUM(s.quantity) AS total_qty, ROUND(SUM(s.revenue)/1e6, 1) AS revenue_m
FROM sales_transactions s
JOIN products p ON s.product_id = p.product_id
WHERE s.transaction_date >= DATE_SUB((SELECT MAX(transaction_date) FROM sales_transactions), INTERVAL 3 MONTH)
GROUP BY 1,2,3
ORDER BY total_qty DESC
LIMIT 10;

-- 8. Scenario 2: Promotion ROI
SELECT pr.promo_id, pr.promo_name, pr.promo_type,
       ROUND(SUM(s.revenue)/1e6, 1) AS promo_revenue_m,
       ROUND(SUM(s.discount_amount)/1e6, 1) AS discount_cost_m,
       pr.marketing_spend / 1e6 AS mktg_m,
       pr.platform_fee / 1e6 AS platform_m
FROM sales_transactions s
JOIN promotions pr ON s.promo_id = pr.promo_id
GROUP BY pr.promo_id, pr.promo_name, pr.promo_type, pr.marketing_spend, pr.platform_fee
ORDER BY promo_revenue_m DESC;

-- 9. Scenario 5: Gross margin Q1/2025 vs Q1/2024
SELECT
  CASE
    WHEN transaction_date BETWEEN '2024-01-01' AND '2024-03-31' THEN 'Q1/2024'
    WHEN transaction_date BETWEEN '2025-01-01' AND '2025-03-31' THEN 'Q1/2025'
  END AS quarter,
  ROUND(SUM(revenue) / 1e9, 2) AS revenue_bn,
  ROUND(SUM(gross_profit) / 1e9, 2) AS gross_profit_bn,
  ROUND(SUM(gross_profit) / SUM(revenue) * 100, 2) AS gross_margin_pct
FROM sales_transactions
WHERE transaction_date BETWEEN '2024-01-01' AND '2024-03-31'
   OR transaction_date BETWEEN '2025-01-01' AND '2025-03-31'
GROUP BY 1
ORDER BY 1;

-- 10. Scenario 6: Store performance — DT/m²
SELECT st.store_id, st.store_name, st.province, st.area_sqm, st.store_type,
       ROUND(SUM(s.revenue) / st.area_sqm / 1e6, 1) AS rev_per_sqm_m,
       ROUND(SUM(s.revenue) / 1e9, 2) AS total_rev_bn
FROM sales_transactions s
JOIN stores st ON s.store_id = st.store_id
WHERE s.transaction_date >= '2024-10-01'
GROUP BY st.store_id, st.store_name, st.province, st.area_sqm, st.store_type
ORDER BY rev_per_sqm_m DESC
LIMIT 15;
""")

    def _write_readme(self):
        path = os.path.join(SQL_DIR, 'README.md')
        with open(path, 'w', encoding='utf-8') as f:
            f.write("""# CANIFA Retail Fashion — Demo Database

## Thông tin
- **Database:** canifa_retail_demo
- **Engine:** MySQL 8.0 (utf8mb4)
- **Data range:** 07/2023 – 03/2025 (21 tháng)
- **Stores:** 110 cửa hàng toàn quốc
- **Products:** ~500 SKU
- **Channels:** 5 (Cửa hàng, Website, Shopee, TikTok, Lazada)

## Populate

```bash
# 1. Khởi tạo MySQL container
docker run --name canifa_demo \\
  -e MYSQL_ROOT_PASSWORD=root \\
  -e MYSQL_DATABASE=canifa_retail_demo \\
  -p 3306:3306 \\
  -d mysql:8.0 \\
  --character-set-server=utf8mb4 \\
  --collation-server=utf8mb4_unicode_ci

# 2. Chờ MySQL sẵn sàng
docker exec canifa_demo mysqladmin ping -uroot -proot --wait=30

# 3. Populate data theo thứ tự
docker exec -i canifa_demo mysql -uroot -proot < canifa_sql/01_ddl_schema.sql
docker exec -i canifa_demo mysql -uroot -proot < canifa_sql/02_metadata.sql
docker exec -i canifa_demo mysql -uroot -proot < canifa_sql/03_master_data.sql
docker exec -i canifa_demo mysql -uroot -proot < canifa_sql/04a_sales_1.sql
docker exec -i canifa_demo mysql -uroot -proot < canifa_sql/04a_sales_2.sql
docker exec -i canifa_demo mysql -uroot -proot < canifa_sql/04b_returns.sql
docker exec -i canifa_demo mysql -uroot -proot < canifa_sql/04c_inventory.sql
docker exec -i canifa_demo mysql -uroot -proot < canifa_sql/04d_store_costs.sql

# 4. Verify
docker exec -i canifa_demo mysql -uroot -proot < canifa_sql/05_validation_queries.sql

# 5. Reset (nếu cần)
docker exec -i canifa_demo mysql -uroot -proot -e \\
  "DROP DATABASE IF EXISTS canifa_retail_demo; CREATE DATABASE canifa_retail_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

## Demo Scenarios
1. Top 10 sản phẩm bán chạy — Dry-Tech surge
2. Hiệu quả khuyến mại — Flash Sale 12/12 ROI âm
3. Tồn kho cuối mùa đông — 2 cửa hàng overstock
4. Inventory days tăng dần — len/sợi 105 ngày
5. Margin erosion Q1/2025 — 3 yếu tố
6. Hiệu quả cửa hàng — Star/Underperformer clusters
""")

    # ── Validation ──

    def validate(self):
        """Run validation queries and print results."""
        print("\n" + "=" * 60)
        print("VALIDATION REPORT")
        print("=" * 60)

        conn = mysql.connector.connect(**DB_CONFIG, database=DB_NAME, charset='utf8mb4')
        cur = conn.cursor()

        # Integrity checks
        checks = [
            ("Orphan sales→store", "SELECT COUNT(*) FROM sales_transactions s LEFT JOIN stores st ON s.store_id=st.store_id WHERE s.store_id IS NOT NULL AND st.store_id IS NULL"),
            ("Orphan sales→product", "SELECT COUNT(*) FROM sales_transactions s LEFT JOIN products p ON s.product_id=p.product_id WHERE p.product_id IS NULL"),
            ("Orphan sales→channel", "SELECT COUNT(*) FROM sales_transactions s LEFT JOIN channels c ON s.channel_id=c.channel_id WHERE c.channel_id IS NULL"),
            ("Orphan sales→promo", "SELECT COUNT(*) FROM sales_transactions s LEFT JOIN promotions pr ON s.promo_id=pr.promo_id WHERE s.promo_id IS NOT NULL AND pr.promo_id IS NULL"),
            ("Revenue mismatch", "SELECT COUNT(*) FROM sales_transactions WHERE ABS(revenue - quantity * unit_price) > 1"),
            ("Profit mismatch", "SELECT COUNT(*) FROM sales_transactions WHERE ABS(gross_profit - (revenue - quantity * cost_price)) > 1"),
            ("Negative revenue", "SELECT COUNT(*) FROM sales_transactions WHERE revenue < 0"),
            ("Negative quantity", "SELECT COUNT(*) FROM sales_transactions WHERE quantity <= 0"),
            ("Negative inventory", "SELECT COUNT(*) FROM inventory_snapshots WHERE quantity_on_hand < 0"),
        ]

        print("\n── Integrity Checks ──")
        all_ok = True
        for name, sql in checks:
            cur.execute(sql)
            val = cur.fetchone()[0]
            status = "✓" if val == 0 else f"✗ ({val:,})"
            if val > 0:
                all_ok = False
            print(f"  {name:30s} {status}")

        # Row counts
        print("\n── Row Counts ──")
        for tbl in ['regions','stores','categories','products','channels','promotions',
                     'sales_transactions','returns','inventory_snapshots','store_costs',
                     '_meta_tables','_meta_columns','_meta_kpi','_meta_glossary']:
            cur.execute(f"SELECT COUNT(*) FROM `{tbl}`")
            cnt = cur.fetchone()[0]
            print(f"  {tbl:30s} {cnt:>10,}")

        # Revenue summary
        print("\n── Revenue by Year ──")
        cur.execute("""
            SELECT YEAR(transaction_date) AS yr,
                   ROUND(SUM(revenue)/1e9, 2) AS rev_bn,
                   COUNT(*) AS records
            FROM sales_transactions GROUP BY 1 ORDER BY 1
        """)
        for row in cur.fetchall():
            print(f"  {row[0]}: {row[1]} tỷ VND ({row[2]:,} records)")

        # Gross margin check
        print("\n── Gross Margin Q1/2024 vs Q1/2025 ──")
        cur.execute("""
            SELECT
              CASE
                WHEN transaction_date BETWEEN '2024-01-01' AND '2024-03-31' THEN 'Q1/2024'
                WHEN transaction_date BETWEEN '2025-01-01' AND '2025-03-31' THEN 'Q1/2025'
              END AS q,
              ROUND(SUM(gross_profit)/SUM(revenue)*100, 2) AS gm_pct
            FROM sales_transactions
            WHERE transaction_date BETWEEN '2024-01-01' AND '2024-03-31'
               OR transaction_date BETWEEN '2025-01-01' AND '2025-03-31'
            GROUP BY 1 ORDER BY 1
        """)
        for row in cur.fetchall():
            print(f"  {row[0]}: {row[1]}%")

        # Scenario 1: Top sellers
        print("\n── Scenario 1: Top 5 Products (last 3 months) ──")
        cur.execute("""
            SELECT p.product_id, LEFT(p.product_name, 40), SUM(s.quantity) AS qty
            FROM sales_transactions s JOIN products p ON s.product_id=p.product_id
            WHERE s.transaction_date >= DATE_SUB((SELECT MAX(transaction_date) FROM sales_transactions), INTERVAL 3 MONTH)
            GROUP BY 1,2 ORDER BY qty DESC LIMIT 5
        """)
        for row in cur.fetchall():
            print(f"  {row[0]:15s} {row[1]:40s} qty={row[2]:,}")

        cur.close()
        conn.close()

        if all_ok:
            print("\n✓ All integrity checks passed")
        else:
            print("\n✗ Some integrity checks failed — review above")


# =============================================================================
# MAIN
# =============================================================================
def main():
    phase = sys.argv[1] if len(sys.argv) > 1 else 'all'

    gen = CanifaGenerator()
    print(f"Products generated: {len(gen.products)}")
    print(f"Stores: {len(gen.stores)}")

    if phase == 'master':
        gen.populate_mysql(phase='schema')
        gen.populate_mysql(phase='master')
        gen.print_master_summary()
    elif phase == 'transactions':
        gen.generate_transactions()
        gen.populate_mysql(phase='transactions')
    elif phase == 'export':
        gen.export_sql()
    elif phase == 'validate':
        gen.validate()
    elif phase == 'all':
        gen.populate_mysql(phase='schema')
        gen.populate_mysql(phase='master')
        gen.generate_transactions()
        gen.populate_mysql(phase='transactions')
        gen.export_sql()
        gen.validate()
    else:
        print(f"Unknown phase: {phase}")
        print("Usage: python generate_canifa.py [master|transactions|export|validate|all]")

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    tables = {
        'products': len(gen.products),
        'stores': len(gen.stores),
        'sales_transactions': len(gen.sales),
        'returns': len(gen.returns_data),
        'inventory_snapshots': len(gen.inventory),
        'store_costs': len(gen.store_costs_data),
    }
    total = 0
    for t, c in sorted(tables.items()):
        print(f"  {t:30s} {c:>10,}")
        total += c
    print(f"  {'TOTAL':30s} {total:>10,}")
    if gen.sales:
        print(f"\nSQL exported to: {SQL_DIR}/")


if __name__ == '__main__':
    main()
