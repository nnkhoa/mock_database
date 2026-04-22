"""
generate_dtg.py — Mock data generator for Đại Thuận Group (DTG) demo DB.
Populates MySQL directly, validates, then exports to dtg_sql/.
"""

import os
import random
import math
from datetime import date, datetime, timedelta
from collections import defaultdict

import mysql.connector
import numpy as np
from dateutil.relativedelta import relativedelta

random.seed(42)
np.random.seed(42)

# ------------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------------
DB_NAME = "dtg_distribution_demo"
DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "root"
DB_PASS = "root"

START_DATE = date(2023, 10, 1)
END_DATE = date(2025, 9, 30)
BASELINE_FX_EUR = 25_800
BASELINE_FX_KRW = 18.5
BASELINE_FX_VND = 1.0

# Global COGS uplift — pushes baseline margin from ~25% to ~17-18% (cold-chain overhead baked in)
COGS_OVERHEAD_MULT = 1.12

OUT_DIR = "dtg_sql"

# ------------------------------------------------------------------
# SEASONALITY + GROWTH
# ------------------------------------------------------------------
MONTHLY_SEASONALITY = {1:1.25,2:0.75,3:0.90,4:1.10,5:1.18,6:1.22,7:1.20,8:1.12,9:1.00,10:0.95,11:1.05,12:1.30}
ICE_CREAM_SEASONAL = {1:0.60,2:0.50,3:0.80,4:1.20,5:1.50,6:1.70,7:1.75,8:1.50,9:1.10,10:0.90,11:0.75,12:0.85}
FROZEN_SEASONAL   = {1:1.35,2:0.70,3:0.95,4:1.00,5:1.00,6:0.95,7:0.95,8:1.00,9:1.05,10:1.05,11:1.15,12:1.40}
DAIRY_SEASONAL    = {1:1.30,2:0.75,3:0.95,4:1.00,5:1.00,6:1.00,7:1.00,8:1.15,9:1.10,10:1.00,11:1.05,12:1.25}
SEAFOOD_SEASONAL  = {1:1.40,2:0.65,3:0.95,4:1.05,5:1.05,6:1.00,7:1.00,8:1.00,9:1.00,10:1.00,11:1.10,12:1.35}
WEEKLY_PATTERN    = {0:1.00,1:1.05,2:1.08,3:1.12,4:1.18,5:0.95,6:0.62}

# Approx Tet dates (VN lunar new year)
TET_DATES = {2024: date(2024,2,10), 2025: date(2025,1,29), 2026: date(2026,2,17)}

def tet_factor(d):
    for y, td in TET_DATES.items():
        days_before = (td - d).days
        days_after = (d - td).days
        if 0 < days_before <= 7:
            return 1.6
        if 0 <= days_after <= 5:
            return 0.35
    return 1.0

def yoy_factor(d):
    years = (d - date(2024,1,1)).days / 365.0
    return (1.077) ** years

# ------------------------------------------------------------------
# CONNECTIONS
# ------------------------------------------------------------------
def connect(db=None):
    return mysql.connector.connect(
        host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS,
        database=db, autocommit=False, charset='utf8mb4',
        use_unicode=True, use_pure=True,
    )

# ------------------------------------------------------------------
# PHASE A — SCHEMA DDL
# ------------------------------------------------------------------
DDL = r"""
DROP DATABASE IF EXISTS `{db}`;
CREATE DATABASE `{db}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `{db}`;

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
"""


def apply_ddl(cur):
    for stmt in DDL.format(db=DB_NAME).split(";\n"):
        s = stmt.strip()
        if s:
            cur.execute(s)


# ------------------------------------------------------------------
# PHASE B — MASTER DATA
# ------------------------------------------------------------------
REGIONS = [
    (1, "Miền Bắc", "MB"),
    (2, "Miền Trung", "MT"),
    (3, "Tây Nguyên", "TN"),
    (4, "Đông Nam Bộ", "DNB"),
    (5, "ĐBSCL", "MN"),
    (6, "Duyên hải Nam Trung Bộ", "DHNTB"),
]

# 63 provinces with (name, region_id, population, gdp_per_capita_million_vnd)
PROVINCES_DATA = [
    # Miền Bắc (1)
    ("Hà Nội", 1, 8_400_000, 180), ("Hải Phòng", 1, 2_100_000, 150),
    ("Quảng Ninh", 1, 1_370_000, 200), ("Bắc Ninh", 1, 1_460_000, 250),
    ("Hải Dương", 1, 1_950_000, 110), ("Hưng Yên", 1, 1_270_000, 115),
    ("Vĩnh Phúc", 1, 1_190_000, 135), ("Thái Nguyên", 1, 1_330_000, 105),
    ("Phú Thọ", 1, 1_520_000, 75), ("Bắc Giang", 1, 1_890_000, 95),
    ("Hà Nam", 1, 870_000, 95), ("Nam Định", 1, 1_870_000, 75),
    ("Thái Bình", 1, 1_880_000, 72), ("Ninh Bình", 1, 1_010_000, 88),
    ("Hòa Bình", 1, 870_000, 65), ("Sơn La", 1, 1_280_000, 50),
    ("Lào Cai", 1, 770_000, 90), ("Yên Bái", 1, 840_000, 52),
    ("Tuyên Quang", 1, 810_000, 55), ("Lạng Sơn", 1, 800_000, 60),
    ("Cao Bằng", 1, 550_000, 45), ("Bắc Kạn", 1, 330_000, 44),
    ("Hà Giang", 1, 880_000, 38), ("Điện Biên", 1, 620_000, 42),
    ("Lai Châu", 1, 480_000, 44),
    # Miền Trung (2)
    ("Thanh Hóa", 2, 3_720_000, 70), ("Nghệ An", 2, 3_400_000, 62),
    ("Hà Tĩnh", 2, 1_310_000, 88), ("Quảng Bình", 2, 910_000, 75),
    ("Quảng Trị", 2, 650_000, 70), ("Thừa Thiên Huế", 2, 1_160_000, 82),
    ("Đà Nẵng", 2, 1_220_000, 130), ("Quảng Nam", 2, 1_510_000, 85),
    ("Quảng Ngãi", 2, 1_250_000, 92),
    # Duyên hải Nam Trung Bộ (6)
    ("Bình Định", 6, 1_500_000, 80), ("Phú Yên", 6, 880_000, 68),
    ("Khánh Hòa", 6, 1_240_000, 95), ("Ninh Thuận", 6, 600_000, 72),
    ("Bình Thuận", 6, 1_250_000, 75),
    # Tây Nguyên (3)
    ("Đắk Lắk", 3, 1_930_000, 62), ("Đắk Nông", 3, 660_000, 55),
    ("Gia Lai", 3, 1_580_000, 58), ("Kon Tum", 3, 560_000, 50),
    ("Lâm Đồng", 3, 1_310_000, 75),
    # Đông Nam Bộ (4)
    ("TP.HCM", 4, 9_200_000, 195), ("Bình Dương", 4, 2_600_000, 170),
    ("Đồng Nai", 4, 3_200_000, 140), ("Bà Rịa - Vũng Tàu", 4, 1_160_000, 280),
    ("Tây Ninh", 4, 1_180_000, 110), ("Bình Phước", 4, 1_030_000, 95),
    # ĐBSCL (5)
    ("Long An", 5, 1_720_000, 105), ("Tiền Giang", 5, 1_770_000, 80),
    ("Bến Tre", 5, 1_290_000, 70), ("Trà Vinh", 5, 1_010_000, 75),
    ("Vĩnh Long", 5, 1_030_000, 72), ("Đồng Tháp", 5, 1_600_000, 70),
    ("An Giang", 5, 1_900_000, 65), ("Kiên Giang", 5, 1_740_000, 82),
    ("Cần Thơ", 5, 1_240_000, 95), ("Hậu Giang", 5, 730_000, 72),
    ("Sóc Trăng", 5, 1_200_000, 72), ("Bạc Liêu", 5, 920_000, 78),
    ("Cà Mau", 5, 1_200_000, 72),
]

# Special override for pos_potential_count (spec values)
POS_POTENTIAL_OVERRIDE = {
    "TP.HCM": 2300, "Hà Nội": 2100, "Bình Dương": 650, "Đồng Nai": 800,
    "Hải Phòng": 525, "Đà Nẵng": 300, "Cần Thơ": 300, "Khánh Hòa": 300,
    "Đắk Lắk": 475,
}

BRANCHES = [
    # (id, name, code, province_name, type, opex_monthly_vnd, staff, year_opened, capacity_m3)
    (1, "CN HCM", "CN-HCM", "TP.HCM", "HO-Commercial", 1_100_000_000, 85, 1998, 8000),
    (2, "CN Hà Nội", "CN-HN", "Hà Nội", "Regional", 670_000_000, 45, 2005, 5000),
    (3, "CN Đà Nẵng", "CN-DN", "Đà Nẵng", "Regional", 335_000_000, 22, 2008, 2200),
    (4, "CN Nha Trang (HO)", "CN-NT", "Khánh Hòa", "HO-Corporate", 420_000_000, 60, 1992, 3500),
    (5, "CN Cần Thơ", "CN-CT", "Cần Thơ", "Regional", 210_000_000, 14, 2012, 1600),
    (6, "CN Hải Phòng", "CN-HP", "Hải Phòng", "Satellite", 170_000_000, 10, 2015, 900),
    (7, "CN Buôn Ma Thuột", "CN-BMT", "Đắk Lắk", "Satellite", 185_000_000, 9, 2018, 700),
]

# Primary branch assignment — satellites checked FIRST so HP/BMT get their own stores.
BRANCH_SERVES = {
    6: ["Hải Phòng","Quảng Ninh"],                              # Satellite HP (primary)
    7: ["Đắk Lắk","Gia Lai","Kon Tum","Đắk Nông"],              # Satellite BMT (primary)
    3: ["Đà Nẵng","Quảng Nam","Quảng Ngãi","Thừa Thiên Huế","Quảng Bình","Quảng Trị","Hà Tĩnh","Nghệ An","Thanh Hóa","Bình Định"],
    4: ["Khánh Hòa","Ninh Thuận","Bình Thuận","Phú Yên","Lâm Đồng"],
    5: ["Cần Thơ","Sóc Trăng","Hậu Giang","Bạc Liêu","Cà Mau","Kiên Giang","An Giang","Đồng Tháp","Vĩnh Long","Trà Vinh"],
    1: ["TP.HCM","Bình Dương","Đồng Nai","Long An","Bà Rịa - Vũng Tàu","Tây Ninh","Bình Phước","Tiền Giang","Bến Tre"],
    2: ["Hà Nội","Vĩnh Phúc","Bắc Ninh","Hưng Yên","Hà Nam","Hải Dương","Bắc Giang","Thái Nguyên","Phú Thọ","Hòa Bình","Nam Định","Thái Bình","Ninh Bình","Lào Cai","Yên Bái","Tuyên Quang","Lạng Sơn","Cao Bằng","Bắc Kạn","Hà Giang","Điện Biên","Lai Châu","Sơn La"],
}

# Branch-level PRICE multiplier — simulates mix/positioning differences
# (HCM: premium mix + HORECA-heavy → higher realized price; BMT: discounts to move stock → lower)
# Applied to unit_price so COGS stays clean (FX impact remains visible).
BRANCH_PRICE_MULT = {
    1: 1.33,  # HCM — premium HORECA mix, MT scale
    2: 1.15,  # HN
    3: 1.12,  # ĐN
    4: 1.05,  # NT (local market, Tashun factory pass-through)
    5: 1.08,  # CT
    6: 0.97,  # HP — discount positioning, low scale
    7: 0.94,  # BMT — deep discount to move product in rural
}

CHANNELS = [
    (1, "MT", "Modern Trade — siêu thị, CVS, chuỗi có tủ đông"),
    (2, "HORECA", "Khách sạn, nhà hàng, bếp CN"),
    (3, "GT", "Tạp hóa, chợ đầu mối có tủ đông"),
    (4, "Online", "Shopee, Tiki, GrabMart, Baemin"),
]

CURRENCIES = [("VND","Việt Nam Đồng","Việt Nam"),("KRW","Korean Won","Hàn Quốc"),("EUR","Euro","Đức")]

PRINCIPALS = [
    (1, "Binggrae",    "Hàn Quốc", "KRW", 95.0, 2005),
    (2, "CJ Food",     "Hàn Quốc", "KRW", 85.0, 2010),
    (3, "Ammerland",   "Đức",      "EUR", 100.0, 2012),
    (4, "DongWon",     "Hàn Quốc", "KRW", 90.0, 2014),
    (5, "Tashun Food", "Việt Nam", "VND", 10.0, 1995),
    (6, "M.Ngon",      "Việt Nam", "VND", 5.0,  2015),
]

# Category schema
CATEGORIES = [
    (1,  "Kem cây",        "Ice cream bar",   "Kem"),
    (2,  "Kem hộp",        "Ice cream tub",   "Kem"),
    (3,  "Sữa trái cây",   "Fruit milk",      "Sữa"),
    (4,  "Snack",          "Snack",           "Snack"),
    (5,  "Há cảo/Mandu",   "Dumpling",        "Đông lạnh chế biến"),
    (6,  "Sốt",            "Sauce",           "Gia vị"),
    (7,  "Thực phẩm đông lạnh ăn liền", "Frozen ready meal", "Đông lạnh chế biến"),
    (8,  "Sữa tươi UHT",   "UHT Milk",        "Sữa"),
    (9,  "Bơ",             "Butter",          "Sữa"),
    (10, "Phô mai",        "Cheese",          "Sữa"),
    (11, "Yogurt",         "Yogurt",          "Sữa"),
    (12, "Cá hộp",         "Canned fish",     "Thủy sản"),
    (13, "Há cảo premium", "Premium dumpling","Đông lạnh chế biến"),
    (14, "Hải sản đông IQF",   "IQF seafood", "Thủy sản"),
    (15, "Thực phẩm chế biến sẵn", "Ready meal", "Đông lạnh chế biến"),
    (16, "Gia vị chế biến sẵn",    "Seasoning", "Gia vị"),
]

# Build SKU list: (sku_code, name_vi, category_id, principal_id, unit_size, pkg, shelf_life, retail_base, cogs_pct, popularity, launch, discontinue)
def build_products():
    prods = []
    pid = 0
    # BINGGRAE (35 SKUs)
    bing_flavors_samanco = [("Chocolate",75),("Strawberry",80),("Vanilla",78),("Matcha",65),("Oreo",82),("Mango",70)]
    for fv,pop in bing_flavors_samanco:
        pid += 1
        margin = 0.18 if fv != "Mango" else 0.22
        retail = 11_500
        prods.append((pid, f"BG-SAM-{fv[:3].upper()}", f"Binggrae Samanco {fv} cây", 1, 1, "80ml", "Cây kem", 365, retail, retail*(1-margin), pop/100, date(2015,6,1), None))
    # Samanco Lemon — failed launch
    pid += 1
    prods.append((pid, "BG-SAM-LEM", "Binggrae Samanco Lemon cây", 1, 1, "80ml", "Cây kem", 365, 11_500, 11_500*0.82, 0.35, date(2025,5,1), None))
    SAMANCO_LEMON_ID = pid
    # Melona
    for fv,pop in [("Melon",90),("Banana",85),("Mango",82),("Strawberry",80),("Coconut",68)]:
        pid += 1
        prods.append((pid, f"BG-MEL-{fv[:3].upper()}", f"Binggrae Melona {fv} cây", 1, 1, "80ml", "Cây kem", 365, 13_000, 13_000*0.75, pop/100, date(2015,6,1), None))
    # Malaka cones
    for fv,pop in [("Chocolate",72),("Vanilla",70),("Strawberry",68),("Matcha",60),("Caramel",62)]:
        pid += 1
        prods.append((pid, f"BG-MAL-{fv[:3].upper()}", f"Binggrae Malaka Cone {fv}", 1, 1, "125ml", "Ốc quế", 365, 18_000, 18_000*0.73, pop/100, date(2015,6,1), None))
    # BB Bonbon tub
    for fv,size,pop in [("Vanilla","500ml",65),("Cookie","500ml",62),("Mint","1L",58),("Strawberry","1L",55),("Chocolate","1L",60)]:
        pid += 1
        prods.append((pid, f"BG-BON-{fv[:3].upper()}-{size[:-2]}", f"Binggrae BB Bonbon {fv} {size}", 2, 1, size, "Hộp kem", 365, 65_000 if "1L" in size else 35_000, (65_000 if "1L" in size else 35_000)*0.75, pop/100, date(2017,3,1), None))
    # Fruit milk 200ml
    for fv,pop in [("Banana",88),("Strawberry",82),("Melon",75),("Chocolate",78),("Coffee",70)]:
        pid += 1
        prods.append((pid, f"BG-MLK-{fv[:3].upper()}", f"Binggrae Sữa {fv} 200ml", 3, 1, "200ml", "Chai", 120, 14_000, 14_000*0.78, pop/100, date(2016,1,1), None))
    # Snacks
    for fv,pop in [("Rice Cracker",60),("Shrimp Cracker",58),("Cheese Ball",55),("Potato Stick",52)]:
        pid += 1
        prods.append((pid, f"BG-SNK-{fv[:3].upper()}", f"Binggrae {fv}", 4, 1, "60g", "Gói", 270, 22_000, 22_000*0.77, pop/100, date(2018,3,1), None))

    # CJ FOOD (28 SKUs)
    # Dumpling/Mandu
    cj_dump = [("Tôm",95,45_000,0.30),("Thịt heo",92,38_000,0.30),("Kingsize",85,68_000,0.35),("Kimchi",60,42_000,0.30),("Gà",78,40_000,0.30),("Tôm Hàn Quốc",75,52_000,0.32),("Bò",70,48_000,0.30),("Hải sản",72,50_000,0.30)]
    for fv,pop,retail,margin in cj_dump:
        pid += 1
        prods.append((pid, f"CJ-DUM-{fv[:3].upper()}-{pid}", f"CJ Bibigo {fv}", 5, 2, "400g", "Túi đông", 180, retail, retail*(1-margin), pop/100, date(2018,1,1), None))
    CJ_KIMCHI_ID = None
    for p in prods:
        if "Kimchi" in p[2]:
            CJ_KIMCHI_ID = p[0]
            break
    # Sauces
    for fv,pop,retail in [("Gochujang",68,85_000),("Bibimbap Sauce",60,75_000),("BBQ Sauce",65,72_000),("Ssamjang",55,82_000),("Hot Pot Sauce",58,78_000)]:
        pid += 1
        prods.append((pid, f"CJ-SAU-{fv[:3].upper()}", f"CJ {fv}", 6, 2, "500g", "Hũ", 540, retail, retail*0.70, pop/100, date(2018,6,1), None))
    # Ready meals
    for fv,pop,retail in [("Ramyun cốc Kimchi",70,28_000),("Ramyun cốc Bò",68,28_000),("Ramyun cốc Gà",62,28_000),("Bibigo Cơm gà",60,45_000),("Bibigo Cơm bò",58,48_000),("Bibigo Jjajang",55,52_000)]:
        pid += 1
        prods.append((pid, f"CJ-RDY-{pid}", f"CJ {fv}", 7, 2, "—", "Hộp/cốc", 365, retail, retail*0.72, pop/100, date(2019,1,1), None))
    # Filler CJ
    while pid - len([p for p in prods if p[3]==2 or p[2].startswith("CJ")]) < 0:
        pass
    # Add 9 more CJ to hit 28
    for fv,pop,retail in [("Bibigo Tokbokki Cay",55,35_000),("Bibigo Chả cá Hàn",52,42_000),("Bibigo Cơm chiên Hải sản",50,55_000),("Bibigo Canh Kim chi",48,38_000),("Bibigo Japchae đông",45,65_000),("Bibigo Bánh bao Thịt",50,32_000),("Bibigo Bánh bao Kim chi",45,32_000),("Bibigo Sauce Gà chiên",48,78_000),("Bibigo Sauce Teriyaki",50,72_000)]:
        pid += 1
        prods.append((pid, f"CJ-EXT-{pid}", f"CJ {fv}", 7, 2, "—", "Hộp", 365, retail, retail*0.71, pop/100, date(2020,1,1), None))

    # AMMERLAND (20 SKUs)
    # UHT Milk
    for fv,vol,pop,retail in [("Full Fat","1L",88,42_000),("Low Fat","1L",72,42_000),("Skimmed","1L",58,42_000),("Full Fat","2L",65,78_000),("Low Fat","2L",55,78_000)]:
        pid += 1
        prods.append((pid, f"AM-MLK-{fv[:3].upper()}-{vol[:-1]}", f"Ammerland Sữa tươi {fv} {vol}", 8, 3, vol, "Hộp giấy", 180, retail, retail*0.72, pop/100, date(2016,3,1), None))
    # Butter
    for fv,size,pop,retail,margin in [("UHT","1L",70,185_000,0.12),("Butter","200g",80,68_000,0.28),("Butter","500g",65,145_000,0.26)]:
        pid += 1
        prods.append((pid, f"AM-BUT-{size[:-1]}-{pid}", f"Ammerland Bơ {fv} {size}", 9, 3, size, "Hộp", 180, retail, retail*(1-margin), pop/100, date(2015,1,1), None))
    # Cheese
    for fv,size,pop,retail,margin in [("Slice","200g",82,95_000,0.15),("Cream","150g",72,82_000,0.30),("Mozzarella Block","400g",65,135_000,0.28),("Cheddar Block","400g",60,148_000,0.29)]:
        pid += 1
        prods.append((pid, f"AM-CHS-{fv[:3].upper()}", f"Ammerland Phô mai {fv} {size}", 10, 3, size, "Hộp", 240, retail, retail*(1-margin), pop/100, date(2017,2,1), None))
    # Yogurt
    yog = [("Raspberry",85,18_500,0.30),("Strawberry",88,18_500,0.30),("Plain",78,16_500,0.30),("Blueberry",72,19_000,0.30),("Mango",75,18_500,0.30),("Peach",68,18_500,0.30),("Vanilla",80,17_500,0.30),("Mixed Berry",72,19_500,0.30)]
    for fv,pop,retail,margin in yog:
        pid += 1
        prods.append((pid, f"AM-YOG-{fv[:3].upper()}", f"Ammerland Yogurt {fv} 125g", 11, 3, "125g", "Hũ nhựa", 45, retail, retail*(1-margin), pop/100, date(2018,5,1), None))
    # Store Yogurt Raspberry ID (first matching)
    YOG_RASP_ID = None
    for p in prods:
        if "Ammerland Yogurt Raspberry" in p[2]:
            YOG_RASP_ID = p[0]
            break

    # DONGWON (8 SKUs)
    for fv,pop,retail in [("Dumpling Gà+Tôm",65,58_000),("Dumpling Thịt heo Premium",60,55_000),("Dumpling Tôm King",58,75_000),("Dumpling Bò Hàn",52,72_000)]:
        pid += 1
        prods.append((pid, f"DW-DUM-{pid}", f"DongWon {fv}", 13, 4, "500g", "Túi đông", 180, retail, retail*0.78, pop/100, date(2019,4,1), None))
    for fv,pop,retail in [("Tuna trong dầu 150g",72,38_000),("Tuna nước muối 150g",68,38_000),("Cá thu sốt cà 180g",60,42_000),("Cá hồi hộp 150g",58,52_000)]:
        pid += 1
        prods.append((pid, f"DW-CAN-{pid}", f"DongWon {fv}", 12, 4, "—", "Hộp", 720, retail, retail*0.78, pop/100, date(2016,1,1), None))

    # TASHUN (18 SKUs)
    for size,pop,retail in [("Tôm IQF size 13/15",72,320_000),("Tôm IQF size 16/20",78,245_000),("Tôm IQF size 21/25",82,195_000),("Tôm IQF size 26/30",75,165_000)]:
        pid += 1
        prods.append((pid, f"TS-TOM-{pid}", f"Tashun {size} 500g", 14, 5, "500g", "Túi đông", 365, retail, retail*0.86, pop/100, date(2014,1,1), None))
    for fv,pop,retail in [("Mực ống IQF 500g",68,165_000),("Mực sữa IQF 500g",62,145_000),("Mực lá IQF 500g",55,125_000)]:
        pid += 1
        prods.append((pid, f"TS-MUC-{pid}", f"Tashun {fv}", 14, 5, "500g", "Túi đông", 365, retail, retail*0.86, pop/100, date(2014,1,1), None))
    for fv,pop,retail in [("Cá thu phi lê 500g",60,95_000),("Cá ngừ phi lê 500g",65,125_000),("Cá hồi phi lê 500g",58,245_000),("Cá basa phi lê 500g",72,65_000)]:
        pid += 1
        prods.append((pid, f"TS-CA-{pid}", f"Tashun {fv}", 14, 5, "500g", "Túi đông", 365, retail, retail*0.86, pop/100, date(2014,1,1), None))
    for fv,pop,retail in [("Ghẹ IQF nguyên con 400g",55,185_000),("Ghẹ xanh lột mai 400g",52,225_000)]:
        pid += 1
        prods.append((pid, f"TS-GHE-{pid}", f"Tashun {fv}", 14, 5, "400g", "Túi đông", 365, retail, retail*0.86, pop/100, date(2014,1,1), None))
    for fv,pop,retail in [("Sò điệp đông",45,145_000),("Bạch tuộc IQF 500g",48,155_000),("Chả cá viên đông 500g",55,75_000),("Tôm nõn đông 300g",58,185_000),("Hải sản mix 500g",52,125_000)]:
        pid += 1
        prods.append((pid, f"TS-MIX-{pid}", f"Tashun {fv}", 14, 5, "500g", "Túi đông", 365, retail, retail*0.86, pop/100, date(2014,1,1), None))

    # M.NGON (6)
    for fv,pop,retail in [("Cá kho tộ 300g",55,68_000),("Thịt kho trứng 400g",58,72_000),("Sườn xào chua ngọt 400g",52,75_000),("Bò kho 400g",48,82_000)]:
        pid += 1
        prods.append((pid, f"MN-RDY-{pid}", f"M.Ngon {fv}", 15, 6, "—", "Hộp", 365, retail, retail*0.80, pop/100, date(2019,1,1), None))
    for fv,pop,retail in [("Muối ớt chanh 100g",50,28_000),("Gia vị phở 250g",48,35_000)]:
        pid += 1
        prods.append((pid, f"MN-SEA-{pid}", f"M.Ngon {fv}", 16, 6, "—", "Túi", 540, retail, retail*0.80, pop/100, date(2020,1,1), None))

    return prods, SAMANCO_LEMON_ID, YOG_RASP_ID, CJ_KIMCHI_ID


def build_stores(provinces_idx):
    """Generate ~5000 stores distributed by province population.
    provinces_idx: dict province_name -> (province_id, region_id, population, pos_potential_count)
    """
    # Distribution hot spots (percentages of stores)
    hotspots = {"TP.HCM":0.22,"Hà Nội":0.18,"Đà Nẵng":0.07,"Bình Dương":0.05,"Đồng Nai":0.04,"Hải Phòng":0.04,"Cần Thơ":0.04,"Khánh Hòa":0.03}
    total_target = 5000
    hot_count = int(total_target * sum(hotspots.values()))  # ~3350
    rest_count = total_target - hot_count
    stores_per = {}
    for p,pct in hotspots.items():
        stores_per[p] = int(total_target * pct)
    other_provs = [p for p in provinces_idx if p not in hotspots]
    # Distribute rest proportional to population
    total_other_pop = sum(provinces_idx[p][2] for p in other_provs)
    for p in other_provs:
        stores_per[p] = max(8, int(rest_count * provinces_idx[p][2] / total_other_pop))
    # Tune to exactly ~5000
    _total = sum(stores_per.values())

    MT_CHAINS = [("7-Eleven","MT"),("Circle K","MT"),("Co.op Mart","MT"),("AEON","MT"),("WinMart","MT"),("Bách Hóa Xanh","MT"),("FamilyMart","MT"),("GS25","MT"),("Lotte Mart","MT"),("Big C","MT"),("Go!","MT"),("MM Mega Market","MT"),("Satra","MT"),("Ministop","MT"),("VinMart+","MT")]
    HORECA_CHAINS = [("Sheraton","HORECA"),("Caravelle","HORECA"),("Lotte Hotel","HORECA"),("Melia","HORECA"),("Pullman","HORECA"),("Nhà hàng Ngon","HORECA"),("Bếp CN Samsung","HORECA"),("Bếp CN Vingroup","HORECA"),("Bếp CN Sungroup","HORECA"),("Bếp CN LG","HORECA"),("King BBQ","HORECA"),("Gogi House","HORECA"),("Pizza Hut","HORECA"),("Jollibee","HORECA"),("KFC","HORECA")]
    GT_NAMES = ["Tạp hóa Cô Ba","Cửa hàng Bà Bảy","Tạp hóa Anh Tư","Cửa hàng Chị Sáu","Tạp hóa Chú Năm","Cửa hàng Dì Út","Tạp hóa Ông Tám"]
    DISTRICTS = ["Q.1","Q.2","Q.3","Q.4","Q.5","Q.Bình Thạnh","Q.Gò Vấp","Q.Tân Bình","Q.Phú Nhuận","Q.Thủ Đức","Q.7","Q.10","Q.Hoàn Kiếm","Q.Đống Đa","Q.Cầu Giấy","Q.Hai Bà Trưng","Q.Hà Đông","Q.Hoàng Mai","H.Hóc Môn","H.Củ Chi","H.Bình Chánh","H.Long Biên","H.Đông Anh"]

    stores = []
    store_id = 0
    for prov_name, count in stores_per.items():
        prov_id, region_id, pop, pos_pot = provinces_idx[prov_name]
        # channel mix: MT 40%, HORECA 25%, GT 30%, Online 5%
        n_mt = int(count * 0.40)
        n_hor = int(count * 0.25)
        n_gt = int(count * 0.30)
        n_on = count - n_mt - n_hor - n_gt
        # Miền Bắc 30% competitor, Miền Nam 20%, else 25%
        if region_id == 1:
            comp_prob = 0.30
        elif region_id in (4,5):
            comp_prob = 0.20
        else:
            comp_prob = 0.25
        # Tier distribution: A 10%, B 50%, C 40%
        def mk(chain, channel_id, chain_label=None):
            nonlocal store_id
            store_id += 1
            tier = np.random.choice(["A","B","C"], p=[0.10,0.50,0.40])
            comp = 1 if random.random() < comp_prob else 0
            district = random.choice(DISTRICTS)
            chain_name = chain_label if chain_label else chain
            store_name = f"{chain} {district} {prov_name[:15]}"
            # Branch — primary branch servicing this province
            branch = None
            for bid,plist in BRANCH_SERVES.items():
                if prov_name in plist:
                    branch = bid
                    break
            if branch is None:
                branch = 1  # fallback
            opened = date(random.randint(2015,2024), random.randint(1,12), random.randint(1,28))
            return (store_id, store_name, f"ST{store_id:06d}", channel_id, chain_name, prov_id, district, branch, opened, comp, tier, 1)
        for _ in range(n_mt):
            ch, _ = random.choice(MT_CHAINS)
            stores.append(mk(ch, 1, ch))
        for _ in range(n_hor):
            ch, _ = random.choice(HORECA_CHAINS)
            stores.append(mk(ch, 2, ch))
        for _ in range(n_gt):
            ch = random.choice(GT_NAMES)
            stores.append(mk(ch, 3, "GT"))
        for _ in range(n_on):
            ch = random.choice(["Shopee Fresh","Tiki Fresh","GrabMart","Baemin","Lazada Mart"])
            stores.append(mk(ch, 4, ch))
    return stores


def build_warehouses():
    # 2 warehouses per major branch, 1 for satellites
    whs = []
    wid = 0
    for b in BRANCHES:
        bid, name, code, prov, btype, opex, staff, yr, cap = b
        layout = [("Frozen", int(cap*0.7)),("Chilled", int(cap*0.2)),("Ambient", int(cap*0.1))]
        for stype, subcap in layout:
            wid += 1
            whs.append((wid, f"Kho {stype} {name}", bid, stype, subcap))
    return whs


# ------------------------------------------------------------------
# PHASE C — TRANSACTIONS
# ------------------------------------------------------------------
def category_seasonal_for(cat_id):
    if cat_id in (1,2):  # kem
        return ICE_CREAM_SEASONAL
    if cat_id in (5,7,13,14,15):  # đông lạnh, há cảo, hải sản
        if cat_id == 14:
            return SEAFOOD_SEASONAL
        return FROZEN_SEASONAL
    if cat_id in (3,4,6,8,9,10,11,12,16):  # sữa, snack, gia vị
        return DAIRY_SEASONAL
    return DAIRY_SEASONAL


def fx_rate(d, currency, fx_map):
    """fx_map: {(date, currency): rate}. Returns rate at date d."""
    if currency == "VND":
        return 1.0
    # find closest date
    key = (d, currency)
    if key in fx_map:
        return fx_map[key]
    # linear fallback
    if currency == "EUR":
        return BASELINE_FX_EUR
    if currency == "KRW":
        return BASELINE_FX_KRW
    return 1.0


def build_fx_rates():
    """Generate daily FX with EUR spike in Aug-Sep 2025."""
    rates = {}
    d = START_DATE
    eur_base = 25_800
    krw_base = 18.5
    while d <= END_DATE:
        # Normal drift ±0.3%
        drift_eur = 1.0 + np.random.normal(0, 0.003)
        drift_krw = 1.0 + np.random.normal(0, 0.003)
        eur_base = eur_base * drift_eur
        krw_base = krw_base * drift_krw
        # Enforce mean reversion
        eur_base = max(24_500, min(26_500, eur_base))
        krw_base = max(17.2, min(19.2, krw_base))
        eur_rate = eur_base
        krw_rate = krw_base
        # FX spike anomaly
        if d.year == 2025 and d.month == 8:
            eur_rate = 26_500 + (d.day / 31.0) * 400  # ramp to ~26_900
        if d.year == 2025 and d.month == 9:
            eur_rate = 27_400 + (d.day / 30.0) * 500  # ramp to avg 27_775
        rates[(d, "EUR")] = round(eur_rate, 2)
        rates[(d, "KRW")] = round(krw_rate, 4)
        rates[(d, "VND")] = 1.0
        d += timedelta(days=1)
    return rates


# ------------------------------------------------------------------
# MAIN WORKFLOW
# ------------------------------------------------------------------
def phase_a_schema(cur):
    print("[Phase A] Creating schema…")
    apply_ddl(cur)
    print("[Phase A] Schema created.")


def phase_b_master(cur):
    print("[Phase B] Loading master data…")
    # Calendar
    cal = []
    d = START_DATE
    while d <= END_DATE:
        q = (d.month - 1) // 3 + 1
        dow = d.weekday()
        iso = d.isocalendar()
        is_tet = 0
        for y, td in TET_DATES.items():
            if -7 <= (d - td).days <= 5:
                is_tet = 1
                break
        is_weekend = 1 if dow >= 5 else 0
        season = ("Spring" if d.month in (2,3,4) else "Summer" if d.month in (5,6,7,8) else "Autumn" if d.month in (9,10,11) else "Winter")
        cal.append((d, d.year, q, d.month, iso.week, dow, is_tet, is_weekend, None, season))
        d += timedelta(days=1)
    cur.executemany("INSERT INTO dim_calendar VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", cal)

    # Currencies
    cur.executemany("INSERT INTO dim_currency VALUES (%s,%s,%s)", CURRENCIES)
    # Principals
    cur.executemany("INSERT INTO dim_principal VALUES (%s,%s,%s,%s,%s,%s)", PRINCIPALS)
    # Categories
    cur.executemany("INSERT INTO dim_product_category VALUES (%s,%s,%s,%s)", CATEGORIES)
    # Regions
    cur.executemany("INSERT INTO dim_region VALUES (%s,%s,%s)", REGIONS)

    # Provinces
    prov_rows = []
    prov_idx = {}
    for i, (name, region_id, pop, gdp) in enumerate(PROVINCES_DATA, start=1):
        pos_pot = POS_POTENTIAL_OVERRIDE.get(name, max(10, pop // 4000))
        prov_rows.append((i, name, region_id, pop, gdp, pos_pot))
        prov_idx[name] = (i, region_id, pop, pos_pot)
    cur.executemany("INSERT INTO dim_province VALUES (%s,%s,%s,%s,%s,%s)", prov_rows)

    # Branches
    br_rows = []
    for bid, name, code, prov_name, btype, opex, staff, yr, cap in BRANCHES:
        br_rows.append((bid, name, code, prov_idx[prov_name][0], btype, opex, staff, yr, cap))
    cur.executemany("INSERT INTO dim_branch VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)", br_rows)

    # Channels
    cur.executemany("INSERT INTO dim_channel VALUES (%s,%s,%s)", CHANNELS)

    # Products — apply global COGS uplift so baseline margin ~ 17%
    prods_raw, SAM_LEM_ID, YOG_RASP_ID, CJ_KIM_ID = build_products()
    prods = []
    for p in prods_raw:
        new_cogs = round(float(p[9]) * COGS_OVERHEAD_MULT, 2)
        prods.append((p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8], new_cogs, p[10], p[11], p[12]))
    cur.executemany("""INSERT INTO dim_product
        (product_id, sku_code, product_name_vi, category_id, principal_id, unit_size, package_type,
         shelf_life_days, retail_price_base, cogs_baseline, popularity_weight, launch_date, discontinue_date, is_active)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,1)""",
        [(p[0],p[1],p[2],p[3],p[4],p[5],p[6],p[7],p[8],p[9],p[10],p[11],p[12]) for p in prods])

    # Stores
    stores = build_stores(prov_idx)
    cur.executemany("""INSERT INTO dim_store
        (store_id, store_name, store_code, channel_id, chain_name, province_id, district,
         branch_id, opened_date, competitor_present, store_tier, is_active)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", stores)

    # Warehouses
    whs = build_warehouses()
    cur.executemany("INSERT INTO dim_warehouse VALUES (%s,%s,%s,%s,%s)", whs)

    # Route coverage
    # Primary: each store → its branch_id (already set). Compute distance.
    coverage = []
    cov_id = 0
    for st in stores:
        (sid, name, code, ch, chain, pid, dist, bid, opened, comp, tier, active) = st
        dist_km = round(random.uniform(5, 250), 1)
        cost_visit = round(50_000 + dist_km * 1200, 2)
        cov_id += 1
        coverage.append((cov_id, bid, sid, dist_km, cost_visit, 1))
        # If store in Hải Phòng province → also secondary route from HN branch (overlap anomaly)
        prov_name_rev = None
        for pn,(ppid,_,_,_) in prov_idx.items():
            if ppid == pid:
                prov_name_rev = pn
                break
        if prov_name_rev == "Hải Phòng" and random.random() < 0.80:
            cov_id += 1
            coverage.append((cov_id, 2, sid, round(dist_km + random.uniform(90,130),1), cost_visit + 150_000, 0))
    cur.executemany("INSERT INTO fact_route_coverage VALUES (%s,%s,%s,%s,%s,%s)", coverage)

    print(f"[Phase B] Master data loaded: {len(cal)} days, {len(prov_rows)} provinces, {len(BRANCHES)} branches, {len(prods)} SKUs, {len(stores)} stores, {len(whs)} warehouses, {len(coverage)} coverage rows.")
    return prods, stores, whs, prov_idx, (SAM_LEM_ID, YOG_RASP_ID, CJ_KIM_ID)


def phase_b_checkpoint(prods, stores, prov_idx, whs):
    """Print summary for user confirmation."""
    print("\n=== CHECKPOINT 2 — MASTER DATA SUMMARY ===")
    print(f"Principals: {len(PRINCIPALS)}")
    for p in PRINCIPALS:
        print(f"  - #{p[0]} {p[1]} ({p[2]}) {p[3]} imp_content={p[4]}%")
    by_principal = defaultdict(int)
    for p in prods:
        by_principal[p[4]] += 1
    print(f"\nSKUs: {len(prods)} total")
    name_map = {p[0]:p[1] for p in PRINCIPALS}
    for pid,cnt in by_principal.items():
        print(f"  - {name_map[pid]}: {cnt} SKUs")
    print(f"\nProvinces: {len(prov_idx)} (expected 63)")
    print(f"Branches: {len(BRANCHES)}")
    for b in BRANCHES:
        print(f"  - #{b[0]} {b[1]} opex={b[5]/1e6:.0f}M staff={b[6]}")
    print(f"\nStores: {len(stores)}")
    by_ch = defaultdict(int)
    by_tier = defaultdict(int)
    by_comp = defaultdict(int)
    for s in stores:
        by_ch[s[3]] += 1
        by_tier[s[10]] += 1
        by_comp[s[9]] += 1
    ch_name = {1:"MT",2:"HORECA",3:"GT",4:"Online"}
    for ch,cnt in sorted(by_ch.items()):
        print(f"  - Channel {ch_name[ch]}: {cnt} ({cnt/len(stores)*100:.0f}%)")
    for t,c in sorted(by_tier.items()):
        print(f"  - Tier {t}: {c} ({c/len(stores)*100:.0f}%)")
    print(f"  - competitor_present=TRUE: {by_comp[1]} ({by_comp[1]/len(stores)*100:.0f}%)")
    print(f"\nWarehouses: {len(whs)} ({len(BRANCHES)} branches × 3 types)")
    print("\nSample SKUs:")
    for p in random.sample(prods, 5):
        print(f"  - {p[1]} · {p[2]} · retail={p[8]:,.0f}")
    print("\nSample stores:")
    for s in random.sample(stores, 5):
        print(f"  - {s[1]} · tier {s[10]} · comp={s[9]}")


# ==================================================================
# PHASE C — TRANSACTIONS
# ==================================================================
TARGET_REV_2024 = 975e9
TARGET_REV_2025_YTD = 790e9  # Jan-Sep 2025

BRANCH_SHARE = {1: 0.45, 2: 0.22, 3: 0.12, 4: 0.08, 5: 0.07, 6: 0.04, 7: 0.02}


def insert_fx_rates(cur, fx_map):
    rows = [(d, ccy, rate) for (d, ccy), rate in fx_map.items()]
    cur.executemany("INSERT INTO fact_fx_rate (`date`, currency_code, rate_to_vnd) VALUES (%s,%s,%s)", rows)
    print(f"[Phase C] fact_fx_rate: {len(rows)} rows")


def generate_sales(prods, stores, prov_idx, fx_map, sam_lem_id):
    """Generate ~500K sales line items. Return list of tuples."""
    print("[Phase C] Generating sales lines…")

    # index products by principal
    prods_by_principal = defaultdict(list)
    for p in prods:
        prods_by_principal[p[4]].append(p)  # principal_id at index 4
    principal_weight = {1:0.38, 2:0.25, 3:0.20, 4:0.05, 5:0.10, 6:0.02}
    # currency per principal
    principal_ccy = {1:"KRW", 2:"KRW", 3:"EUR", 4:"KRW", 5:"VND", 6:"VND"}
    principal_imp_content = {1:0.95, 2:0.85, 3:1.0, 4:0.90, 5:0.10, 6:0.05}

    # Per-store tier params for Poisson monthly orders
    tier_lambda = {"A": 7.0, "B": 2.2, "C": 0.7}
    tier_qty_mult = {"A": 1.5, "B": 1.0, "C": 0.55}

    # Channel qty multiplier (HORECA orders larger)
    channel_qty_mult = {1: 1.0, 2: 1.6, 3: 0.8, 4: 0.6}
    # Channel price multiplier
    channel_price_mult = {1: 1.0, 2: 1.10, 3: 0.96, 4: 1.0}

    # Province → region
    prov_region = {pid: rid for pn,(pid,rid,_,_) in prov_idx.items()}
    # Province -> name
    pid_to_name = {v[0]: k for k,v in prov_idx.items()}
    # Store lookup
    store_attr = {}
    for s in stores:
        (sid, name, code, ch, chain, pid, dist, bid, opened, comp, tier, active) = s
        store_attr[sid] = (ch, pid, bid, comp, tier, prov_region[pid])

    # Build product arrays for faster sampling per principal
    prod_samplers = {}
    for p_id, plist in prods_by_principal.items():
        weights = np.array([p[10] for p in plist], dtype=float)
        weights = weights / weights.sum()
        prod_samplers[p_id] = (plist, weights)

    sales_id = 0
    rows = []  # in-memory buffer
    current_year = 2024
    # iterate month by month 2023-10 → 2025-09
    months = []
    y, m = START_DATE.year, START_DATE.month
    while date(y, m, 1) <= END_DATE:
        months.append((y, m))
        m += 1
        if m > 12:
            m = 1
            y += 1

    np_rng = np.random.default_rng(42)

    for (yr, mo) in months:
        mnth_start = date(yr, mo, 1)
        mnth_end = (mnth_start + relativedelta(months=1)) - timedelta(days=1)
        if mnth_end > END_DATE:
            mnth_end = END_DATE
        month_len = (mnth_end - mnth_start).days + 1

        # Distribute orders per store via Poisson based on tier
        for s in stores:
            (sid, name, code, ch, chain, prov_id, dist_name, bid, opened, comp, tier, active) = s
            # Skip if store opened after month
            if opened > mnth_end:
                continue
            n_orders = np_rng.poisson(tier_lambda[tier])
            if n_orders == 0:
                continue

            # Pick order days biased by weekday pattern
            candidate_days = [(mnth_start + timedelta(days=i)) for i in range(month_len)]
            dow_wts = np.array([WEEKLY_PATTERN[d.weekday()] for d in candidate_days])
            dow_wts = dow_wts / dow_wts.sum()
            order_days = np_rng.choice(candidate_days, size=n_orders, p=dow_wts, replace=True)

            for d in order_days:
                d = d.item() if hasattr(d, 'item') else d
                # Pick principal for this order
                pr_id = int(np_rng.choice(list(principal_weight.keys()),
                                          p=list(principal_weight.values())))
                plist, pweights = prod_samplers[pr_id]
                n_sku = max(1, int(np_rng.normal(3.0, 1.0)))
                n_sku = min(n_sku, 5)
                picks = np_rng.choice(len(plist), size=n_sku, p=pweights, replace=False if n_sku<=len(plist) else True)
                for idx in picks:
                    prod = plist[idx]
                    (prod_id, sku, pname, cat_id, p_principal, unit_size, pkg, shelf, retail, cogs_base, popw, launch, disc) = prod
                    # Skip if before launch
                    if launch > d:
                        continue
                    # Samanco Lemon failed launch: after 2 weeks, sales drop
                    failed_mult = 1.0
                    if prod_id == sam_lem_id:
                        days_since = (d - launch).days
                        if days_since <= 14:
                            failed_mult = 1.3
                        elif days_since <= 30:
                            failed_mult = 0.6
                        elif days_since <= 60:
                            failed_mult = 0.35
                        else:
                            failed_mult = 0.18

                    # Base quantity
                    base_qty = 28.0 * tier_qty_mult[tier] * channel_qty_mult[ch] * popw

                    # Seasonality factors
                    m_fac = MONTHLY_SEASONALITY[d.month]
                    cat_fac = category_seasonal_for(cat_id)[d.month]
                    w_fac = WEEKLY_PATTERN[d.weekday()]
                    tet_fac = tet_factor(d)
                    yoy_fac = yoy_factor(d)
                    noise = np.random.uniform(0.88, 1.12)
                    qty = base_qty * m_fac * cat_fac * w_fac * tet_fac * yoy_fac * failed_mult * noise

                    # Anomaly 10: Bình Dương +28% YoY in 2025 (vs avg 7.7%)
                    if pid_to_name.get(prov_id) == "Bình Dương" and d.year == 2025:
                        qty *= (1.28/1.077)
                    # Anomaly 11: CJ HORECA growth +18% (vs 10%) in 2025
                    if pr_id == 2 and ch == 2 and d.year == 2025:
                        qty *= (1.18/1.077)
                    # Anomaly 4: Mix shift T9/2025 — Tashun share +
                    if pr_id == 5 and d.year == 2025 and d.month == 9:
                        qty *= 1.35

                    qty = max(1, int(round(qty)))

                    # Price (channel × branch)
                    price = retail * channel_price_mult[ch] * BRANCH_PRICE_MULT.get(bid, 1.0)
                    gross = qty * price
                    disc_v = 0.0
                    # Small random discount ~3% of gross for MT
                    if ch == 1 and np.random.random() < 0.3:
                        disc_v = round(gross * np.random.uniform(0.02, 0.06), 2)
                    net = gross - disc_v

                    # FX applied on COGS based on imported content
                    ccy = principal_ccy[pr_id]
                    baseline = BASELINE_FX_EUR if ccy == "EUR" else (BASELINE_FX_KRW if ccy == "KRW" else 1.0)
                    cur_rate = fx_map.get((d, ccy), baseline)
                    imp = principal_imp_content[pr_id]
                    fx_ratio = (cur_rate / baseline) * imp + (1.0 - imp)
                    cogs_unit = round(cogs_base * fx_ratio, 2)
                    cogs_total = round(cogs_unit * qty, 2)

                    sales_id += 1
                    rows.append((sales_id, d, sid, prod_id, bid, ch,
                                 qty, round(price,2), round(gross,2), disc_v, round(net,2),
                                 cogs_unit, cogs_total, round(cur_rate,4)))

    print(f"[Phase C] Generated {len(rows)} sales lines (pre-scale).")
    return rows


def scale_sales(rows):
    """Apply uniform scale factor per-year to hit target annual revenues."""
    from collections import defaultdict as dd
    by_year = dd(float)
    for r in rows:
        by_year[r[1].year] += r[10]
    # Compute scale factors: 2024 → 975 tỷ, 2025 YTD → 790 tỷ (approx),
    # 2023 (only Oct-Dec) → ~240 tỷ (proportional to 975*3/12*0.93 /yoy ~ 220 tỷ)
    tgt = {2023: 220e9, 2024: TARGET_REV_2024, 2025: TARGET_REV_2025_YTD}
    scale = {y: tgt[y] / by_year[y] if by_year[y] > 0 else 1.0 for y in by_year}
    print(f"[Phase C] Revenue scale factors: {scale}")
    scaled = []
    for r in rows:
        sf = scale[r[1].year]
        # Keep qty integer, scale by changing quantity proportionally
        new_qty = max(1, int(round(r[6] * sf)))
        unit_price = r[7]
        gross = new_qty * unit_price
        # discount pct preserved
        disc_pct = r[9] / r[8] if r[8] > 0 else 0
        disc = round(gross * disc_pct, 2)
        net = gross - disc
        cogs_unit = r[11]
        cogs_total = round(cogs_unit * new_qty, 2)
        scaled.append((r[0], r[1], r[2], r[3], r[4], r[5],
                       new_qty, unit_price, round(gross,2), disc, round(net,2),
                       cogs_unit, cogs_total, r[13]))
    return scaled


def insert_sales(cur, rows, batch=2000):
    print(f"[Phase C] Inserting {len(rows)} fact_sales rows…")
    sql = """INSERT INTO fact_sales
        (sales_id, `date`, store_id, product_id, branch_id, channel_id,
         quantity, unit_price_vnd, gross_amount_vnd, discount_vnd, net_amount_vnd,
         cogs_unit_vnd, cogs_total_vnd, fx_rate_used)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    for i in range(0, len(rows), batch):
        cur.executemany(sql, rows[i:i+batch])


def generate_sell_out(sales_rows, store_attr, sam_lem_id):
    """Aggregate sales weekly per (store, product) and compute sell-out with multipliers.
    - Default sell-through: 0.95
    - Binggrae MB Q3/2025 competitor=TRUE: 0.75; no-comp: 0.92 (gap 2.2 tỷ sell-in vs sell-out)
    - Samanco Lemon: even lower sell-through in later months (mock failed launch).
    """
    from collections import defaultdict as dd
    agg = dd(lambda: [0, 0.0])  # (store, product, week_start_date) → [qty, revenue]
    for r in sales_rows:
        (sid, d, store_id, prod_id, bid, ch, qty, price, gross, disc, net, cu, ct, fx) = r
        wstart = d - timedelta(days=d.weekday())
        key = (store_id, prod_id, wstart)
        agg[key][0] += qty
        agg[key][1] += float(net)
    out_rows = []
    out_id = 0
    for (store_id, prod_id, wstart), (qty, rev) in agg.items():
        ch, prov_id, bid, comp, tier, region_id = store_attr[store_id]
        # Default sell-through
        st = np.random.uniform(0.93, 0.98)
        # Binggrae MB Q3/2025 cannibalization
        # Need principal=1 check: we don't have it in store_attr. Pass via prod_id via external lookup later.
        # We'll apply product-side check with a lookup dict passed separately.
        multiplier = st
        qsold = max(1, int(round(qty * multiplier)))
        rev_out = round(rev * multiplier, 2)
        out_id += 1
        out_rows.append((out_id, wstart, store_id, prod_id, qsold, rev_out))
    return out_rows


def generate_sell_out_v2(sales_rows, store_attr, prod_principal, prod_cat, sam_lem_id):
    """Second version with principal/category-aware adjustments."""
    from collections import defaultdict as dd
    agg = dd(lambda: [0, 0.0])
    for r in sales_rows:
        (sid, d, store_id, prod_id, bid, ch, qty, price, gross, disc, net, cu, ct, fx) = r
        wstart = d - timedelta(days=d.weekday())
        key = (store_id, prod_id, wstart)
        agg[key][0] += qty
        agg[key][1] += float(net)
    out_rows = []
    oid = 0
    for (store_id, prod_id, wstart), (qty, rev) in agg.items():
        ch, prov_id, bid, comp, tier, region_id = store_attr[store_id]
        p_id = prod_principal[prod_id]
        st = np.random.uniform(0.93, 0.98)
        # Binggrae MB Q3/2025: comp=1→ st=0.75, comp=0→ st=0.92
        if p_id == 1 and region_id == 1 and wstart.year == 2025 and wstart.month in (7,8,9):
            base_mult = 0.75 if comp == 1 else 0.92
            # Channel differential: MT less hit, HORECA more hit
            ch_fac = {1:1.00, 2:0.88, 3:0.92, 4:1.00}.get(ch, 1.0)
            st = base_mult * ch_fac
        qsold = max(1, int(round(qty * st)))
        rev_out = round(rev * st, 2)
        oid += 1
        out_rows.append((oid, wstart, store_id, prod_id, qsold, rev_out))
    return out_rows


def insert_sell_out(cur, rows, batch=2000):
    print(f"[Phase C] Inserting {len(rows)} fact_sales_out rows…")
    sql = "INSERT INTO fact_sales_out VALUES (%s,%s,%s,%s,%s,%s)"
    for i in range(0, len(rows), batch):
        cur.executemany(sql, rows[i:i+batch])


def build_trade_promotions(prod_ids_binggrae):
    """Generate ~500 trade promos across 24 months. Include the T9/2025 overspend anomaly."""
    promos = []
    pid = 0
    # Regular TPN: 1-2 per principal per month, planned ~200-600M, actual ~0.9-1.1×
    for y, m_start in [(2023,10),(2024,1),(2024,4),(2024,7),(2024,10),(2025,1),(2025,4),(2025,7)]:
        # iterate months in this quarter
        for dm in range(3):
            md = date(y, m_start, 1) + relativedelta(months=dm)
            if md > END_DATE:
                break
            for principal_id in [1,2,3,4,5,6]:
                n_camp = np.random.choice([1,2,3])
                for _ in range(n_camp):
                    start = md.replace(day=np.random.randint(1, 20))
                    end = start + timedelta(days=np.random.randint(7, 28))
                    planned = int(np.random.uniform(150e6, 650e6))
                    actual = int(planned * np.random.uniform(0.85, 1.08))
                    pid += 1
                    region_id = np.random.choice([1,2,3,4,5,6,None])
                    if region_id is not None:
                        region_id = int(region_id)
                    promo_type = np.random.choice(['BOGO','price_down','display_fee','loyalty'])
                    desc = f"{promo_type} TPN {principal_id}-{md.strftime('%Y%m')}"
                    promos.append((pid, start, end, None, region_id, None, principal_id,
                                  promo_type, planned, actual, 'completed', desc))
    # ANOMALY: T9/2025 Binggrae BOGO HCM+ĐN overspend
    pid += 1
    promos.append((pid, date(2025,9,1), date(2025,9,30), None, 4, None, 1,
                  'BOGO', 690_000_000, 1_300_000_000, 'completed',
                  'BOGO Samanco + Melona response Nutifood cạnh tranh HCM+ĐN'))
    return promos


def insert_trade_promotions(cur, rows):
    print(f"[Phase C] Inserting {len(rows)} fact_trade_promotion rows…")
    sql = """INSERT INTO fact_trade_promotion
        (promo_id, start_date, end_date, store_id, region_id, product_id, principal_id,
         promo_type, planned_amount_vnd, actual_amount_vnd, status, description_vi)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    cur.executemany(sql, rows)


def build_operating_cost():
    """Monthly OpEx per branch by category. Include T9/2025 fuel spike anomaly."""
    categories = ['rent','staff','fuel_logistics','utility','marketing','admin']
    # Category allocation ratio of monthly opex
    alloc = {'rent': 0.22, 'staff': 0.40, 'fuel_logistics': 0.17, 'utility': 0.06, 'marketing': 0.08, 'admin': 0.07}
    rows = []
    cid = 0
    # Iterate months
    y, m = START_DATE.year, START_DATE.month
    while date(y, m, 1) <= END_DATE:
        for b in BRANCHES:
            bid, _, _, _, _, opex_m, _, _, _ = b
            # Slight growth over time
            months_since = (y - 2023) * 12 + (m - 10)
            growth = 1.0 + 0.003 * months_since
            for cat in categories:
                amount = round(opex_m * alloc[cat] * growth * np.random.uniform(0.95, 1.05), 2)
                # T9/2025 fuel spike: +15% vs 6-month avg
                if cat == 'fuel_logistics' and y == 2025 and m == 9:
                    amount = round(amount * 1.15, 2)
                cid += 1
                rows.append((cid, f"{y}-{m:02d}", bid, cat, amount))
        m += 1
        if m > 12:
            m = 1
            y += 1
    return rows


def insert_operating_cost(cur, rows):
    print(f"[Phase C] Inserting {len(rows)} fact_operating_cost rows…")
    sql = "INSERT INTO fact_operating_cost VALUES (%s,%s,%s,%s,%s)"
    cur.executemany(sql, rows)


def build_budget():
    """Monthly targets. T9/2025 total revenue = 96.1 tỷ, GP = 17.8 tỷ, margin = 18.5%."""
    rows = []
    bid = 0
    y, m = START_DATE.year, START_DATE.month
    # Default monthly target scaled by seasonality
    while date(y, m, 1) <= END_DATE:
        ym = f"{y}-{m:02d}"
        # Base monthly revenue target
        yoy = 1.077 ** ((y - 2023) + (m / 12.0))
        base = 80e9 * MONTHLY_SEASONALITY[m] * yoy
        # Override T9/2025 — plan margin > actual so narrative "below plan" works
        if y == 2025 and m == 9:
            rev = 96.1e9
            gp = 25.7e9        # Plan GP → actual ≈ 24.2 tỷ, variance −1.5 tỷ
            margin = 26.7       # Plan margin
        else:
            rev = round(base, 2)
            gp = round(rev * 0.265, 2)
            margin = 26.5
        # Total dimension
        bid += 1; rows.append((bid, ym, 'total', 'ALL', 'revenue', rev))
        bid += 1; rows.append((bid, ym, 'total', 'ALL', 'gross_profit', gp))
        bid += 1; rows.append((bid, ym, 'total', 'ALL', 'margin_pct', margin))
        # Per principal
        pshare = {'Binggrae':0.38,'CJ Food':0.25,'Ammerland':0.20,'DongWon':0.05,'Tashun Food':0.10,'M.Ngon':0.02}
        for pname, share in pshare.items():
            bid += 1; rows.append((bid, ym, 'principal', pname, 'revenue', round(rev*share,2)))
        # Per branch
        for branch, share in BRANCH_SHARE.items():
            bname = [b[1] for b in BRANCHES if b[0]==branch][0]
            bid += 1; rows.append((bid, ym, 'branch', bname, 'revenue', round(rev*share,2)))
        # Per region
        region_share = {'Miền Bắc':0.22,'Miền Trung':0.12,'Tây Nguyên':0.04,'Đông Nam Bộ':0.45,'ĐBSCL':0.10,'Duyên hải Nam Trung Bộ':0.07}
        for rname, share in region_share.items():
            bid += 1; rows.append((bid, ym, 'region', rname, 'revenue', round(rev*share,2)))
        # Per channel
        ch_share = {'MT':0.55,'HORECA':0.28,'GT':0.12,'Online':0.05}
        for cname, share in ch_share.items():
            bid += 1; rows.append((bid, ym, 'channel', cname, 'revenue', round(rev*share,2)))
        m += 1
        if m > 12:
            m = 1
            y += 1
    return rows


def insert_budget(cur, rows):
    print(f"[Phase C] Inserting {len(rows)} fact_budget rows…")
    sql = "INSERT INTO fact_budget VALUES (%s,%s,%s,%s,%s,%s)"
    cur.executemany(sql, rows)


def build_inventory(prods, whs, sales_rows, anomaly_ids):
    """Weekly snapshot ~ 2023-10-07 → 2025-09-30, ~104 weeks × subset.
    Include the 3 near-expiry anomalies at snapshot_date=2025-09-30.
    """
    SAM_LEM_ID, YOG_RASP_ID, CJ_KIM_ID = anomaly_ids
    # Warehouse → branch
    wh_branch = {w[0]: w[2] for w in whs}
    # Branch → list of Frozen/Chilled warehouses
    branch_whs = defaultdict(list)
    for w in whs:
        branch_whs[w[2]].append(w)
    # Daily COGS estimate: sum by date
    by_date = defaultdict(float)
    for r in sales_rows:
        by_date[r[1]] += float(r[12])
    # daily COGS ≈ 400M → 30-day average ~ 12B cogs → inventory ~48B for DOH 120
    rows = []
    inv_id = 0
    # Build random-ish stock levels proportional to sales velocity per product
    prod_velocity = defaultdict(float)
    for r in sales_rows:
        prod_velocity[r[3]] += r[6]  # qty
    total_days = (END_DATE - START_DATE).days + 1
    velocity = {pid: q/total_days for pid, q in prod_velocity.items()}

    # Total target inventory value at each snapshot ≈ 48B, distributed across warehouses weighted by branch share
    # and across products weighted by velocity
    # Snapshot every 7 days from first Sunday
    snap_date = START_DATE + timedelta(days=(6 - START_DATE.weekday()) % 7)
    snaps = []
    while snap_date <= END_DATE:
        snaps.append(snap_date)
        snap_date += timedelta(days=7)

    prod_lookup = {p[0]: p for p in prods}

    # For each snap, for each warehouse, stock top N products
    # Keep it compact: top 60 products per warehouse
    top_prods = sorted(velocity.items(), key=lambda x: -x[1])[:70]

    # Branch name → branch_id
    branch_name_to_id = {b[1]: b[0] for b in BRANCHES}

    for snap in snaps:
        # Random target inventory growth over time (slight)
        total_target = 48e9 * (1.0 + 0.002 * ((snap - START_DATE).days))
        # Allocate per branch via BRANCH_SHARE
        for bid, share in BRANCH_SHARE.items():
            whs_list = [w for w in whs if w[2] == bid]
            # Split across Frozen/Chilled/Ambient (70/20/10)
            total_branch = total_target * share
            split = {"Frozen":0.72, "Chilled":0.20, "Ambient":0.08}
            for w in whs_list:
                w_target = total_branch * split.get(w[3], 0.1)
                # Pick products that fit this storage type
                # Frozen: kem, frozen dumpling, hải sản (cat 1,2,5,7,13,14,15)
                # Chilled: dairy 8-11 (sữa, bơ, phô mai, yogurt)
                # Ambient: sauces, seasoning, canned 4,6,12,16
                if w[3] == "Frozen":
                    allowed_cats = {1,2,5,7,13,14,15}
                elif w[3] == "Chilled":
                    allowed_cats = {8,9,10,11}
                else:
                    allowed_cats = {3,4,6,12,16}
                cand = [(pid, v) for pid, v in top_prods if prod_lookup[pid][3] in allowed_cats]
                if not cand:
                    continue
                # Allocate inventory across candidate products weighted by velocity
                vsum = sum(v for _,v in cand)
                for pid, v in cand:
                    alloc = w_target * (v / vsum) * np.random.uniform(0.7, 1.3)
                    if alloc < 50_000:
                        continue
                    p = prod_lookup[pid]
                    unit_cost = float(p[9])  # cogs_baseline
                    qty = int(round(alloc / unit_cost))
                    if qty < 1:
                        continue
                    # Derive manufactured/expiry
                    shelf = p[7] or 365
                    # Batch manufactured ~ days ago (safe bounds)
                    lo = max(1, min(shelf // 6, 20))
                    hi = max(lo + 10, min(shelf // 2, 120))
                    mfg = snap - timedelta(days=int(np.random.randint(lo, hi)))
                    expiry = mfg + timedelta(days=shelf)
                    dte = (expiry - snap).days
                    inv_id += 1
                    rows.append((inv_id, snap, pid, w[0], qty, round(unit_cost,2),
                                 round(qty*unit_cost,2), mfg, expiry, dte))
    # ANOMALY: near-expiry rows at 2025-09-30
    # 1) Ammerland Yogurt Raspberry: 2.1B value, batch 2025-08-18, expire ~2025-10-02 (18 days)
    snap = date(2025,9,30)
    # Split across 2 warehouses: DC HCM + DC HN (Chilled types, branch 1 and 2)
    # Find Chilled warehouses
    hcm_chilled = [w for w in whs if w[2]==1 and w[3]=="Chilled"][0]
    hn_chilled  = [w for w in whs if w[2]==2 and w[3]=="Chilled"][0]
    yog_prod = prod_lookup[YOG_RASP_ID]
    yog_unit_cost = float(yog_prod[9])
    # 1.4B at HCM, 700M at HN
    for wh, val in [(hcm_chilled, 1_400_000_000), (hn_chilled, 700_000_000)]:
        q = int(val / yog_unit_cost)
        mfg = date(2025,8,18)
        expiry = mfg + timedelta(days=45)
        dte = (expiry - snap).days
        inv_id += 1
        rows.append((inv_id, snap, YOG_RASP_ID, wh[0], q, round(yog_unit_cost,2),
                     round(q*yog_unit_cost,2), mfg, expiry, dte))
    # 2) Binggrae Samanco Lemon: 800M at DC HN (Frozen)
    hn_frozen = [w for w in whs if w[2]==2 and w[3]=="Frozen"][0]
    sam_prod = prod_lookup[SAM_LEM_ID]
    sam_unit_cost = float(sam_prod[9])
    q = int(800_000_000 / sam_unit_cost)
    mfg = date(2025, 6, 1)
    expiry = mfg + timedelta(days=365)
    inv_id += 1
    rows.append((inv_id, snap, SAM_LEM_ID, hn_frozen[0], q, round(sam_unit_cost,2),
                 round(q*sam_unit_cost,2), mfg, expiry, (expiry-snap).days))
    # 3) CJ Bibigo Kimchi: 300M at DC Đà Nẵng (Frozen), batch 2025-08-05
    dn_frozen = [w for w in whs if w[2]==3 and w[3]=="Frozen"][0]
    kim_prod = prod_lookup[CJ_KIM_ID]
    kim_unit_cost = float(kim_prod[9])
    q = int(300_000_000 / kim_unit_cost)
    mfg = date(2025, 8, 5)
    expiry = mfg + timedelta(days=180)  # CJ shelf 180
    # But we want days_to_expire ~25. 2025-08-05 + 180 = 2026-02-01 → 124 days. Need shorter shelf here
    # Adjust to 55 days shelf for demo purpose - make it hot
    expiry = mfg + timedelta(days=52)  # expire 2025-09-26 ... but snap is 09-30, then expired
    # Actually spec says "expire ~2025-10-25" which is 25 days after 09-30
    expiry = date(2025, 10, 25)
    inv_id += 1
    rows.append((inv_id, snap, CJ_KIM_ID, dn_frozen[0], q, round(kim_unit_cost,2),
                 round(q*kim_unit_cost,2), mfg, expiry, (expiry-snap).days))
    return rows


def insert_inventory(cur, rows, batch=2000):
    print(f"[Phase C] Inserting {len(rows)} fact_inventory rows…")
    sql = "INSERT INTO fact_inventory VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    for i in range(0, len(rows), batch):
        cur.executemany(sql, rows[i:i+batch])


def populate_metadata(cur):
    """Insert _meta_* rows."""
    tables = [
        ('dim_calendar', 'Bảng lịch 730 ngày, chứa year/quarter/month/week/day_of_week, cờ is_tet_period cho mùa Tết, is_weekend, lunar_date', 'Calendar dimension', 'Dùng để join mọi fact theo date, hỗ trợ filter theo mùa và Tết', 731),
        ('dim_currency', 'Tiền tệ: VND, KRW, EUR', 'Currency dimension', 'Master ngoại tệ', 3),
        ('dim_principal', '6 nhà cung cấp: Binggrae (kem, KRW), CJ Food (há cảo, KRW), Ammerland (sữa, EUR), DongWon (há cảo premium, KRW), Tashun (hải sản, VND), M.Ngon (nhãn riêng, VND)', 'Principal suppliers', 'Có imported_content_pct và source_currency để tính FX impact', 6),
        ('dim_product_category', 'Danh mục sản phẩm (Kem, Sữa, Bơ, Há cảo...)', 'Product categories', 'Hỗ trợ rollup doanh thu theo danh mục', 16),
        ('dim_product', '~111 SKUs với giá base, COGS base, shelf life', 'Product master', 'Quan trọng: cogs_baseline dùng làm tham chiếu tính FX impact', 111),
        ('dim_region', '6 miền kinh tế Việt Nam', 'Region dimension', 'Rollup từ tỉnh', 6),
        ('dim_province', '63 tỉnh thành + dân số + GDP + POS potential', 'Province dimension', 'pos_potential_count dùng để tính market coverage', 63),
        ('dim_branch', '7 chi nhánh DTG + monthly_opex + staff count + năm thành lập', 'Branch/depot master', 'Dùng Scenario 5 phân tích footprint', 7),
        ('dim_channel', '4 kênh: MT/HORECA/GT/Online', 'Channel dimension', 'Mix kênh khác FMCG thường (HORECA cao)', 4),
        ('dim_store', '~5000 điểm bán. Cột competitor_present flag Nutifood-KIDO', 'Store/POS master', 'Quan trọng cho Scenario 4 (Binggrae miền Bắc)', 5000),
        ('dim_warehouse', '21 kho: Frozen/Chilled/Ambient × 7 branches', 'Warehouse', 'Phân kho lạnh theo branch', 21),
        ('fact_sales', 'Sell-in transaction level — 1 dòng = 1 line item. Có fx_rate_used denormalized', 'Sales sell-in', 'KPI gốc: net_amount_vnd, cogs_total_vnd. Scenario 1,2,3,5,7', 450000),
        ('fact_sales_out', 'Sell-out POS scan theo tuần. Chênh với sell-in cho biết tồn dealer', 'Sell-out POS', 'Scenario 4 — gap sell-in/sell-out tại Binggrae miền Bắc', 350000),
        ('fact_inventory', 'Tồn kho weekly snapshot với manufactured_date + expiry_date', 'Inventory snapshot', 'Scenario 6 — near-expiry alert', 150000),
        ('fact_fx_rate', 'Tỷ giá EUR/KRW/VND theo ngày', 'FX rate daily', 'Scenario 2 — EUR spike T8-T9/2025', 2193),
        ('fact_trade_promotion', 'Trade promo campaigns với planned và actual amount', 'Trade promo', 'Scenario 2 — BOGO Binggrae overspend T9/2025', 500),
        ('fact_operating_cost', 'Chi phí vận hành theo tháng × chi nhánh × loại', 'OpEx monthly', 'Scenario 2 (fuel spike T9), Scenario 5 (branch CM)', 1008),
        ('fact_budget', 'Kế hoạch theo tháng × dimension × metric', 'Budget targets', 'Scenario 1 — so sánh actual vs plan', 2500),
        ('fact_route_coverage', 'Map branch → store với distance và cost per visit, is_primary flag', 'Route coverage', 'Scenario 5 — phát hiện overlap HN-HP', 5000),
    ]
    cur.executemany("INSERT INTO _meta_tables VALUES (%s,%s,%s,%s,%s)", tables)

    columns = [
        # Fact sales key columns
        ('fact_sales', 'sales_id', 'BIGINT', 'Primary key tự tăng', '—', '1,2,3…'),
        ('fact_sales', 'date', 'DATE', 'Ngày giao dịch sell-in', 'date', '2025-09-15'),
        ('fact_sales', 'quantity', 'INT', 'Số lượng đơn vị (cây kem, túi, hộp)', 'units', '30, 80, 120'),
        ('fact_sales', 'unit_price_vnd', 'DECIMAL', 'Đơn giá tại thời điểm, có điều chỉnh theo channel', 'VND', '13000, 45000'),
        ('fact_sales', 'gross_amount_vnd', 'DECIMAL', 'Doanh thu gross = qty × unit_price', 'VND', '-'),
        ('fact_sales', 'discount_vnd', 'DECIMAL', 'Chiết khấu', 'VND', '-'),
        ('fact_sales', 'net_amount_vnd', 'DECIMAL', 'Doanh thu thuần = gross - discount', 'VND', 'KPI gốc'),
        ('fact_sales', 'cogs_unit_vnd', 'DECIMAL', 'Giá vốn/đơn vị đã áp FX tại ngày', 'VND', '—'),
        ('fact_sales', 'cogs_total_vnd', 'DECIMAL', 'Giá vốn tổng = qty × cogs_unit', 'VND', '—'),
        ('fact_sales', 'fx_rate_used', 'DECIMAL', 'FX rate đã dùng (1 cho VND)', '—', '25800, 18.5, 1.0'),
        ('dim_principal', 'imported_content_pct', 'DECIMAL', 'Tỷ lệ nguyên liệu nhập khẩu', '%', '100 (Ammerland), 5 (M.Ngon)'),
        ('dim_principal', 'source_currency', 'CHAR(3)', 'Đồng tiền gốc COGS', '—', 'EUR, KRW, VND'),
        ('dim_product', 'cogs_baseline', 'DECIMAL', 'Giá vốn base tại FX baseline', 'VND', '—'),
        ('dim_product', 'retail_price_base', 'DECIMAL', 'Giá bán lẻ base MT', 'VND', '—'),
        ('dim_product', 'shelf_life_days', 'INT', 'Hạn sử dụng', 'days', '45, 180, 365'),
        ('dim_store', 'competitor_present', 'TINYINT(1)', '1 nếu có Merino/Celano (Nutifood-KIDO) cùng tủ đông', '0/1', '0, 1'),
        ('dim_store', 'store_tier', 'CHAR(1)', 'Phân tầng store A/B/C theo volume', '—', 'A, B, C'),
        ('dim_branch', 'monthly_opex_vnd', 'DECIMAL', 'Chi phí vận hành tháng', 'VND', '170M-1.1B'),
        ('fact_inventory', 'days_to_expire', 'INT', 'Số ngày đến hạn (snapshot - expiry)', 'days', '18, 25, 90'),
        ('fact_trade_promotion', 'planned_amount_vnd', 'DECIMAL', 'Ngân sách promo đã duyệt', 'VND', '690M'),
        ('fact_trade_promotion', 'actual_amount_vnd', 'DECIMAL', 'Thực chi promo', 'VND', '1.2B'),
        ('fact_operating_cost', 'cost_category', 'VARCHAR', 'Phân loại chi phí', '—', 'rent/staff/fuel_logistics/utility/marketing/admin'),
        ('fact_budget', 'dimension', 'VARCHAR', 'Chiều kế hoạch', '—', 'total/principal/region/branch/channel'),
        ('fact_budget', 'metric', 'VARCHAR', 'Đại lượng kế hoạch', '—', 'revenue/gross_profit/margin_pct/units'),
        ('fact_route_coverage', 'is_primary', 'TINYINT(1)', '1 nếu là route chính của branch → store', '0/1', '0, 1'),
    ]
    cur.executemany("INSERT INTO _meta_columns VALUES (%s,%s,%s,%s,%s,%s)", columns)

    kpis = [
        ('Doanh thu thuần', 'Net Revenue', 'SUM(net_amount_vnd)', 'Tổng doanh thu đã trừ chiết khấu', '1,2,5,7'),
        ('Biên lợi nhuận gộp', 'Gross Margin %', '(SUM(net_amount_vnd - cogs_total_vnd) / SUM(net_amount_vnd)) * 100', 'Biên LN gộp, đơn vị %', '1,2,3,5,7'),
        ('Lợi nhuận gộp', 'Gross Profit', 'SUM(net_amount_vnd - cogs_total_vnd)', 'Lợi nhuận gộp VND', '1,2,3,5,7'),
        ('Branch Contribution Margin', 'Branch CM %', '(SUM(GP_from_sales) - SUM(amount_vnd from fact_operating_cost)) / SUM(net_amount_vnd) * 100', 'CM chi nhánh %', '5,7'),
        ('Days of Inventory', 'DOH', 'SUM(total_value_vnd) / avg_daily_cogs', 'Số ngày tồn kho', '6,7'),
        ('Sell-through Rate', 'Sell-through %', '(fact_sales_out.quantity_sold / fact_sales.quantity) * 100', 'Tỷ lệ sell-out trên sell-in', '4,6'),
        ('FX Impact', 'FX Impact VND', 'SUM(cogs_total_vnd) - SUM(quantity * cogs_baseline)', 'Chênh COGS do FX', '2,3,7'),
        ('Budget Variance', 'Budget Variance', 'actual - target (từ fact_budget)', 'Chênh thực tế vs kế hoạch', '1,2,7'),
        ('Near-Expiry Value', 'Near-Expiry Value', 'SUM(total_value_vnd WHERE days_to_expire < 30)', 'Giá trị tồn gần date', '6,7'),
    ]
    cur.executemany("INSERT INTO _meta_kpi VALUES (%s,%s,%s,%s,%s)", kpis)

    glossary = [
        ('Principal', 'Principal/Supplier', 'Nhà cung cấp độc quyền — DTG phân phối độc quyền tại VN', 'dim_principal'),
        ('POS', 'Point of Sale', 'Điểm bán — cửa hàng/quầy bán cuối cùng đến người tiêu dùng', 'dim_store'),
        ('MT', 'Modern Trade', 'Kênh siêu thị, CVS chuỗi (7-Eleven, Circle K, Co.op Mart…)', 'dim_channel,dim_store'),
        ('HORECA', 'HORECA', 'Hotel/Restaurant/Catering — khách sạn, nhà hàng, bếp CN', 'dim_channel,dim_store'),
        ('GT', 'General Trade', 'Chợ đầu mối, tạp hóa truyền thống có tủ đông', 'dim_channel,dim_store'),
        ('Sell-in', 'Sell-in', 'Hàng DTG bán ra cho dealer/POS — fact_sales', 'fact_sales'),
        ('Sell-out', 'Sell-out', 'Hàng POS bán cho người tiêu dùng — fact_sales_out', 'fact_sales_out'),
        ('COGS', 'Cost of Goods Sold', 'Giá vốn hàng bán', 'fact_sales,dim_product'),
        ('Biên LN gộp', 'Gross Margin', '(Doanh thu - COGS) / Doanh thu', 'fact_sales'),
        ('CM', 'Contribution Margin', 'Biên đóng góp = GP - OpEx của branch', 'fact_sales,fact_operating_cost'),
        ('TPN', 'Trade Promotion', 'Chi phí khuyến mãi kênh (BOGO, price down, display fee)', 'fact_trade_promotion'),
        ('Shelf life', 'Shelf life', 'Hạn sử dụng', 'dim_product'),
        ('Pareto 80/20', '80/20 Rule', '20% SKUs đóng góp ~80% doanh thu', 'dim_product,fact_sales'),
        ('Tết', 'Lunar New Year', 'Tết Nguyên đán — peak tiêu dùng mạnh nhất năm', 'dim_calendar'),
        ('Cold-chain', 'Cold Chain', 'Chuỗi cung ứng lạnh -18°C cho kem/đông lạnh', 'dim_warehouse,fact_operating_cost'),
        ('DC', 'Distribution Center', 'Kho phân phối của branch', 'dim_warehouse'),
        ('FX', 'Foreign Exchange', 'Tỷ giá ngoại tệ', 'fact_fx_rate'),
        ('BOGO', 'Buy One Get One', 'Mua 1 tặng 1 — promo type', 'fact_trade_promotion'),
        ('DOH', 'Days of Inventory', 'Số ngày tồn kho = total_value / daily_cogs', 'fact_inventory'),
        ('YoY', 'Year-over-Year', 'Tăng trưởng so với cùng kỳ năm trước', 'fact_sales'),
        ('Tier', 'Store Tier', 'Phân tầng store A/B/C theo volume', 'dim_store'),
        ('Cannibalization', 'Cannibalization', 'Cạnh tranh giành share giữa sản phẩm cùng kênh', 'dim_store.competitor_present'),
        ('MOQ', 'Minimum Order Quantity', 'Đơn đặt hàng tối thiểu với principal', '—'),
    ]
    cur.executemany("INSERT INTO _meta_glossary VALUES (%s,%s,%s,%s)", glossary)

    print(f"[Phase C] _meta_tables: {len(tables)}, _meta_columns: {len(columns)}, _meta_kpi: {len(kpis)}, _meta_glossary: {len(glossary)}")


# ==================================================================
# PHASE D — VALIDATION
# ==================================================================
def phase_d_validate(cur):
    print("\n=== PHASE D — VALIDATION ===")
    checks = []

    # Technical
    cur.execute("SELECT COUNT(*) FROM fact_sales WHERE store_id NOT IN (SELECT store_id FROM dim_store)")
    checks.append(("FK integrity fact_sales.store_id", cur.fetchone()[0], 0, "="))

    cur.execute("SELECT COUNT(DISTINCT `date`) FROM fact_sales")
    checks.append(("Date coverage fact_sales", cur.fetchone()[0], 700, ">="))

    cur.execute("SELECT COUNT(*) FROM fact_sales WHERE net_amount_vnd IS NULL OR cogs_total_vnd IS NULL")
    checks.append(("Null net_amount or cogs", cur.fetchone()[0], 0, "="))

    cur.execute("SELECT COUNT(*) FROM fact_sales WHERE cogs_total_vnd <= 0")
    checks.append(("COGS > 0", cur.fetchone()[0], 0, "="))

    # Statistical
    cur.execute("SELECT SUM(net_amount_vnd)/1e9 FROM fact_sales WHERE YEAR(`date`)=2024")
    rev_2024 = float(cur.fetchone()[0] or 0)
    checks.append(("Total revenue 2024 (tỷ)", f"{rev_2024:.1f}", "900-1050", "range"))

    cur.execute("SELECT SUM(net_amount_vnd)/1e9 FROM fact_sales WHERE `date` BETWEEN '2025-01-01' AND '2025-09-30'")
    rev_2025 = float(cur.fetchone()[0] or 0)
    checks.append(("Total revenue 2025 YTD (tỷ)", f"{rev_2025:.1f}", "700-850", "range"))

    cur.execute("SELECT SUM(net_amount_vnd) FROM fact_sales WHERE MONTH(`date`)=1")
    jan_rev = float(cur.fetchone()[0] or 0)
    cur.execute("SELECT SUM(net_amount_vnd) FROM fact_sales WHERE MONTH(`date`)=2")
    feb_rev = float(cur.fetchone()[0] or 1)
    checks.append(("Jan/Feb ratio (Tết effect > 1.5)", f"{jan_rev/feb_rev:.2f}", "1.5+", "ratio"))

    cur.execute("""SELECT SUM(s.net_amount_vnd) FROM fact_sales s JOIN dim_product p ON s.product_id=p.product_id
                   WHERE p.category_id IN (1,2) AND MONTH(s.`date`)=6""")
    jun_ic = float(cur.fetchone()[0] or 0)
    cur.execute("""SELECT SUM(s.net_amount_vnd) FROM fact_sales s JOIN dim_product p ON s.product_id=p.product_id
                   WHERE p.category_id IN (1,2) AND MONTH(s.`date`)=1""")
    jan_ic = float(cur.fetchone()[0] or 1)
    checks.append(("Jun/Jan ice-cream ratio > 2.5", f"{jun_ic/jan_ic:.2f}", "2.5+", "ratio"))

    # Demo scenarios
    cur.execute("SELECT SUM(net_amount_vnd)/1e9, (SUM(net_amount_vnd-cogs_total_vnd)/SUM(net_amount_vnd))*100 FROM fact_sales WHERE `date` BETWEEN '2025-09-01' AND '2025-09-30'")
    r = cur.fetchone()
    t9_rev, t9_mgn = float(r[0] or 0), float(r[1] or 0)
    checks.append(("S1 T9/2025 revenue (tỷ)", f"{t9_rev:.1f}", "85-100", "range"))
    checks.append(("S1 T9/2025 margin %", f"{t9_mgn:.1f}", "14-20", "range"))

    cur.execute("SELECT target_value/1e9 FROM fact_budget WHERE `year_month`='2025-09' AND metric='revenue' AND dimension='total'")
    plan = float(cur.fetchone()[0] or 0)
    checks.append(("S1 T9/2025 plan (tỷ)", f"{plan:.1f}", "96.1", "="))

    # S2: FX impact T9
    cur.execute("""SELECT SUM(s.cogs_total_vnd)/1e6 - SUM(s.quantity*p.cogs_baseline)/1e6
                   FROM fact_sales s JOIN dim_product p ON s.product_id=p.product_id
                   JOIN dim_principal pr ON p.principal_id=pr.principal_id
                   WHERE s.`date` BETWEEN '2025-09-01' AND '2025-09-30' AND pr.principal_name='Ammerland'""")
    fx_imp = float(cur.fetchone()[0] or 0)
    checks.append(("S2 FX impact Ammerland T9 (M VND)", f"{fx_imp:.0f}", "500-1000", "range"))

    # S2: TPN overspend
    cur.execute("""SELECT SUM(actual_amount_vnd - planned_amount_vnd)/1e6
                   FROM fact_trade_promotion
                   WHERE start_date >= '2025-09-01' AND start_date < '2025-10-01'
                     AND principal_id = 1""")
    tpn_over = float(cur.fetchone()[0] or 0)
    checks.append(("S2 Binggrae TPN overspend T9 (M VND)", f"{tpn_over:.0f}", "400-700", "range"))

    # S4: Binggrae miền Bắc sell-in Q3/2025
    cur.execute("""SELECT SUM(s.net_amount_vnd)/1e9
                   FROM fact_sales s JOIN dim_product p ON s.product_id=p.product_id
                   JOIN dim_principal pr ON p.principal_id=pr.principal_id
                   JOIN dim_store st ON s.store_id=st.store_id
                   JOIN dim_province prov ON st.province_id=prov.province_id
                   WHERE pr.principal_name='Binggrae' AND prov.region_id=1
                     AND s.`date` BETWEEN '2025-07-01' AND '2025-09-30'""")
    mb_bg_in = float(cur.fetchone()[0] or 0)
    checks.append(("S4 Binggrae MB Q3 sell-in (tỷ)", f"{mb_bg_in:.2f}", "10-16", "range"))

    # Sell-out
    cur.execute("""SELECT SUM(so.revenue_vnd)/1e9
                   FROM fact_sales_out so JOIN dim_product p ON so.product_id=p.product_id
                   JOIN dim_principal pr ON p.principal_id=pr.principal_id
                   JOIN dim_store st ON so.store_id=st.store_id
                   JOIN dim_province prov ON st.province_id=prov.province_id
                   WHERE pr.principal_name='Binggrae' AND prov.region_id=1
                     AND so.`date` BETWEEN '2025-07-01' AND '2025-09-30'""")
    mb_bg_out = float(cur.fetchone()[0] or 0)
    checks.append(("S4 Binggrae MB Q3 sell-out (tỷ)", f"{mb_bg_out:.2f}", f"{mb_bg_in*0.75:.1f}-{mb_bg_in*0.90:.1f}", "range"))
    checks.append(("S4 Sell-in/out gap (tỷ)", f"{mb_bg_in - mb_bg_out:.2f}", "1.5-3.0", "range"))

    # S5: Branch CM
    cur.execute("""SELECT b.branch_name, SUM(s.net_amount_vnd)/1e9,
                   ((SUM(s.net_amount_vnd - s.cogs_total_vnd)) -
                    COALESCE((SELECT SUM(amount_vnd) FROM fact_operating_cost oc
                              WHERE oc.branch_id=b.branch_id AND oc.`year_month` BETWEEN '2024-10' AND '2025-09'),0))
                    / SUM(s.net_amount_vnd) * 100 AS cm_pct
                   FROM dim_branch b JOIN fact_sales s ON s.branch_id=b.branch_id
                   WHERE s.`date` BETWEEN '2024-10-01' AND '2025-09-30'
                   GROUP BY b.branch_id, b.branch_name ORDER BY cm_pct DESC""")
    branch_cm = cur.fetchall()

    # S6: Near-expiry
    cur.execute("""SELECT p.product_name_vi, SUM(i.total_value_vnd)/1e9, MIN(i.days_to_expire)
                   FROM fact_inventory i JOIN dim_product p ON i.product_id=p.product_id
                   WHERE i.snapshot_date='2025-09-30' AND i.days_to_expire < 30
                   GROUP BY p.product_id, p.product_name_vi ORDER BY 2 DESC LIMIT 5""")
    near_exp = cur.fetchall()

    # CJ HORECA growth
    cur.execute("""SELECT SUM(s.net_amount_vnd)/1e9 FROM fact_sales s JOIN dim_product p ON s.product_id=p.product_id
                   JOIN dim_principal pr ON p.principal_id=pr.principal_id
                   WHERE pr.principal_name='CJ Food' AND s.channel_id=2 AND s.`date` BETWEEN '2024-10-01' AND '2025-09-30'""")
    cj_ho_cur = float(cur.fetchone()[0] or 0)
    cur.execute("""SELECT SUM(s.net_amount_vnd)/1e9 FROM fact_sales s JOIN dim_product p ON s.product_id=p.product_id
                   JOIN dim_principal pr ON p.principal_id=pr.principal_id
                   WHERE pr.principal_name='CJ Food' AND s.channel_id=2 AND s.`date` BETWEEN '2023-10-01' AND '2024-09-30'""")
    cj_ho_prev = float(cur.fetchone()[0] or 1)
    cj_growth = (cj_ho_cur / cj_ho_prev - 1) * 100 if cj_ho_prev > 0 else 0
    checks.append(("S7 CJ HORECA YoY growth %", f"{cj_growth:.1f}", "12-25", "range"))

    # Print report
    print("\n[TECHNICAL + STATISTICAL]")
    for name, val, tgt, op in checks:
        status = "✓"
        if op == "=":
            if isinstance(val, (int, float)) and val != tgt:
                status = "✗"
        elif op == ">=":
            if isinstance(val, (int, float)) and val < tgt:
                status = "✗"
        print(f"  {status} {name:55s} actual={val!s:<10}  target={tgt}")

    print("\n[S5 — BRANCH CM] (FY 10/2024-9/2025)")
    for bn, rev, cm in branch_cm:
        print(f"  {bn:25s} rev={float(rev):.1f} tỷ   CM={float(cm):.1f}%")

    print("\n[S6 — NEAR-EXPIRY at 2025-09-30]")
    for nm, val, dte in near_exp:
        print(f"  {nm:45s} {float(val):.2f} tỷ (min {dte} ngày)")


# ==================================================================
# PHASE E — EXPORT SQL FILES
# ==================================================================
def sql_escape(v):
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "1" if v else "0"
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, (date, datetime)):
        return f"'{v.isoformat()[:10]}'"
    s = str(v).replace("\\", "\\\\").replace("'", "''")
    return f"'{s}'"


def write_inserts(f, table, columns, rows, batch=500):
    if not rows:
        return
    cols_sql = ",".join(f"`{c}`" for c in columns)
    for i in range(0, len(rows), batch):
        chunk = rows[i:i+batch]
        values_sql = ",\n".join("(" + ",".join(sql_escape(v) for v in row) + ")" for row in chunk)
        f.write(f"INSERT INTO `{table}` ({cols_sql}) VALUES\n{values_sql};\n")


def phase_e_export(cur):
    print(f"\n=== PHASE E — EXPORT TO {OUT_DIR}/ ===")
    os.makedirs(OUT_DIR, exist_ok=True)

    # 01_ddl_schema.sql
    ddl_path = os.path.join(OUT_DIR, "01_ddl_schema.sql")
    with open(ddl_path, "w", encoding="utf-8") as f:
        f.write(f"-- ============================================================\n")
        f.write(f"-- 01_ddl_schema.sql\n")
        f.write(f"-- Database: {DB_NAME}\n")
        f.write(f"-- Đại Thuận Group (DTG) — Phân phối thực phẩm đông lạnh\n")
        f.write(f"-- Schema: 11 dim_* + 8 fact_* + 4 _meta_* = 23 tables\n")
        f.write(f"-- ============================================================\n\n")
        f.write(DDL.format(db=DB_NAME))
        f.write("\n")

    # 02_metadata.sql
    meta_path = os.path.join(OUT_DIR, "02_metadata.sql")
    with open(meta_path, "w", encoding="utf-8") as f:
        f.write(f"-- 02_metadata.sql — Metadata tables\n")
        f.write(f"USE `{DB_NAME}`;\n\n")
        for tbl, cols in [
            ("_meta_tables", ["table_name","description_vi","description_en","business_context","row_count_approx"]),
            ("_meta_columns", ["table_name","column_name","data_type","description_vi","unit","example_values"]),
            ("_meta_kpi", ["kpi_name_vi","kpi_name_en","formula_sql","description_vi","related_questions"]),
            ("_meta_glossary", ["term_vi","term_en","definition","related_tables"]),
        ]:
            cur.execute(f"SELECT {','.join(cols)} FROM {tbl}")
            rows = cur.fetchall()
            f.write(f"-- {tbl}: {len(rows)} rows\n")
            write_inserts(f, tbl, cols, rows, batch=200)
            f.write("\n")

    # 03_master_data.sql
    mst_path = os.path.join(OUT_DIR, "03_master_data.sql")
    with open(mst_path, "w", encoding="utf-8") as f:
        f.write(f"-- 03_master_data.sql — Dimension rows\n")
        f.write(f"USE `{DB_NAME}`;\n\n")
        dim_specs = [
            ("dim_calendar", ["date","year","quarter","month","week","day_of_week","is_tet_period","is_weekend","lunar_date","season"]),
            ("dim_currency", ["currency_code","currency_name","country"]),
            ("dim_principal", ["principal_id","principal_name","country","source_currency","imported_content_pct","partnership_since"]),
            ("dim_product_category", ["category_id","category_name_vi","category_name_en","parent_category"]),
            ("dim_region", ["region_id","region_name","region_code"]),
            ("dim_province", ["province_id","province_name","region_id","population","gdp_per_capita","pos_potential_count"]),
            ("dim_branch", ["branch_id","branch_name","branch_code","province_id","branch_type","monthly_opex_vnd","staff_count","year_opened","warehouse_capacity_m3"]),
            ("dim_channel", ["channel_id","channel_name","channel_description_vi"]),
            ("dim_product", ["product_id","sku_code","product_name_vi","category_id","principal_id","unit_size","package_type","shelf_life_days","retail_price_base","cogs_baseline","launch_date","discontinue_date","is_active","popularity_weight"]),
            ("dim_store", ["store_id","store_name","store_code","channel_id","chain_name","province_id","district","branch_id","opened_date","competitor_present","store_tier","is_active"]),
            ("dim_warehouse", ["warehouse_id","warehouse_name","branch_id","storage_type","capacity_m3"]),
        ]
        for tbl, cols in dim_specs:
            cur.execute(f"SELECT {','.join('`'+c+'`' for c in cols)} FROM {tbl}")
            rows = cur.fetchall()
            f.write(f"-- {tbl}: {len(rows)} rows\n")
            write_inserts(f, tbl, cols, rows, batch=500)
            f.write("\n")

    # 04_*.sql — split into sub-files for GitHub 100MB limit
    # Keep populate.sh pattern `0{1,2,3,4}_*.sql` compatible.
    fact_file_groups = [
        ("04_a_support_facts.sql",
         "Support facts: FX, route coverage, operating cost, budget, trade promotion",
         [
             ("fact_fx_rate", ["date","currency_code","rate_to_vnd"]),
             ("fact_route_coverage", ["coverage_id","branch_id","store_id","distance_km","route_cost_per_visit_vnd","is_primary"]),
             ("fact_operating_cost", ["cost_id","year_month","branch_id","cost_category","amount_vnd"]),
             ("fact_budget", ["budget_id","year_month","dimension","dimension_value","metric","target_value"]),
             ("fact_trade_promotion", ["promo_id","start_date","end_date","store_id","region_id","product_id","principal_id","promo_type","planned_amount_vnd","actual_amount_vnd","status","description_vi"]),
         ]),
        ("04_b_inventory.sql",
         "Inventory weekly snapshots + near-expiry anomalies",
         [
             ("fact_inventory", ["inv_id","snapshot_date","product_id","warehouse_id","quantity_on_hand","unit_cost_vnd","total_value_vnd","manufactured_date","expiry_date","days_to_expire"]),
         ]),
        ("04_c_sales_out.sql",
         "Sell-out POS scan (weekly)",
         [
             ("fact_sales_out", ["out_id","date","store_id","product_id","quantity_sold","revenue_vnd"]),
         ]),
        ("04_d_sales_part1.sql", "Sell-in sales — part 1 (2023-10 to 2024-09)", [("fact_sales", "__SALES_PART_1__")]),
        ("04_e_sales_part2.sql", "Sell-in sales — part 2 (2024-10 to 2025-09)", [("fact_sales", "__SALES_PART_2__")]),
    ]
    sales_cols = ["sales_id","date","store_id","product_id","branch_id","channel_id","quantity","unit_price_vnd","gross_amount_vnd","discount_vnd","net_amount_vnd","cogs_unit_vnd","cogs_total_vnd","fx_rate_used"]

    for filename, desc, specs in fact_file_groups:
        path = os.path.join(OUT_DIR, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"-- {filename} — {desc}\n")
            f.write(f"USE `{DB_NAME}`;\n\n")
            for tbl, cols in specs:
                if cols == "__SALES_PART_1__":
                    cur.execute(f"SELECT {','.join('`'+c+'`' for c in sales_cols)} FROM fact_sales WHERE `date` < '2024-10-01'")
                    rows = cur.fetchall()
                    f.write(f"-- fact_sales part 1: {len(rows)} rows\n")
                    write_inserts(f, "fact_sales", sales_cols, rows, batch=1000)
                elif cols == "__SALES_PART_2__":
                    cur.execute(f"SELECT {','.join('`'+c+'`' for c in sales_cols)} FROM fact_sales WHERE `date` >= '2024-10-01'")
                    rows = cur.fetchall()
                    f.write(f"-- fact_sales part 2: {len(rows)} rows\n")
                    write_inserts(f, "fact_sales", sales_cols, rows, batch=1000)
                else:
                    cur.execute(f"SELECT {','.join('`'+c+'`' for c in cols)} FROM {tbl}")
                    rows = cur.fetchall()
                    f.write(f"-- {tbl}: {len(rows)} rows\n")
                    write_inserts(f, tbl, cols, rows, batch=1000)
                f.write("\n")

    # 05_validation_queries.sql
    val_path = os.path.join(OUT_DIR, "05_validation_queries.sql")
    with open(val_path, "w", encoding="utf-8") as f:
        f.write(f"""-- 05_validation_queries.sql — Verify data
USE `{DB_NAME}`;

-- S1: T9/2025 tổng quan
SELECT SUM(net_amount_vnd)/1e9 AS revenue_t9_ty,
       (SUM(net_amount_vnd - cogs_total_vnd) / SUM(net_amount_vnd))*100 AS margin_pct
FROM fact_sales WHERE `date` BETWEEN '2025-09-01' AND '2025-09-30';

-- S1: Plan T9/2025
SELECT target_value/1e9 AS plan_t9_ty FROM fact_budget
WHERE `year_month`='2025-09' AND dimension='total' AND metric='revenue';

-- S2: FX impact Ammerland T9
SELECT SUM(s.cogs_total_vnd - s.quantity*p.cogs_baseline)/1e6 AS fx_impact_m_vnd
FROM fact_sales s JOIN dim_product p ON s.product_id=p.product_id
JOIN dim_principal pr ON p.principal_id=pr.principal_id
WHERE s.`date` BETWEEN '2025-09-01' AND '2025-09-30' AND pr.principal_name='Ammerland';

-- S2: BOGO overspend Binggrae T9
SELECT (actual_amount_vnd - planned_amount_vnd)/1e6 AS overspend_m_vnd, description_vi
FROM fact_trade_promotion WHERE start_date >= '2025-09-01' AND principal_id=1;

-- S3: Imported content per principal
SELECT principal_name, source_currency, imported_content_pct FROM dim_principal;

-- S4: Binggrae MB Q3/2025 sell-in vs sell-out
SELECT 'sell_in' AS kind, SUM(s.net_amount_vnd)/1e9 AS ty
FROM fact_sales s JOIN dim_product p ON s.product_id=p.product_id
JOIN dim_principal pr ON p.principal_id=pr.principal_id
JOIN dim_store st ON s.store_id=st.store_id
JOIN dim_province prov ON st.province_id=prov.province_id
WHERE pr.principal_name='Binggrae' AND prov.region_id=1
  AND s.`date` BETWEEN '2025-07-01' AND '2025-09-30'
UNION ALL
SELECT 'sell_out' AS kind, SUM(so.revenue_vnd)/1e9 AS ty
FROM fact_sales_out so JOIN dim_product p ON so.product_id=p.product_id
JOIN dim_principal pr ON p.principal_id=pr.principal_id
JOIN dim_store st ON so.store_id=st.store_id
JOIN dim_province prov ON st.province_id=prov.province_id
WHERE pr.principal_name='Binggrae' AND prov.region_id=1
  AND so.`date` BETWEEN '2025-07-01' AND '2025-09-30';

-- S5: Branch CM FY 10/2024 - 09/2025
SELECT b.branch_name, SUM(s.net_amount_vnd)/1e9 AS revenue_ty,
  ((SUM(s.net_amount_vnd - s.cogs_total_vnd)) -
    (SELECT COALESCE(SUM(amount_vnd),0) FROM fact_operating_cost
     WHERE branch_id=b.branch_id AND `year_month` BETWEEN '2024-10' AND '2025-09')) / SUM(s.net_amount_vnd) * 100 AS cm_pct
FROM dim_branch b JOIN fact_sales s ON s.branch_id=b.branch_id
WHERE s.`date` BETWEEN '2024-10-01' AND '2025-09-30'
GROUP BY b.branch_id, b.branch_name ORDER BY cm_pct DESC;

-- S6: Near-expiry
SELECT p.product_name_vi, SUM(i.total_value_vnd)/1e9 AS value_ty, MIN(i.days_to_expire) AS min_days
FROM fact_inventory i JOIN dim_product p ON i.product_id=p.product_id
WHERE i.snapshot_date='2025-09-30' AND i.days_to_expire < 30
GROUP BY p.product_id, p.product_name_vi ORDER BY value_ty DESC;

-- S7: CJ HORECA growth
SELECT 'CJ HORECA 2024' AS period, SUM(s.net_amount_vnd)/1e9 AS ty FROM fact_sales s
JOIN dim_product p ON s.product_id=p.product_id JOIN dim_principal pr ON p.principal_id=pr.principal_id
WHERE pr.principal_name='CJ Food' AND s.channel_id=2 AND s.`date` BETWEEN '2023-10-01' AND '2024-09-30'
UNION ALL
SELECT 'CJ HORECA 2025', SUM(s.net_amount_vnd)/1e9 FROM fact_sales s
JOIN dim_product p ON s.product_id=p.product_id JOIN dim_principal pr ON p.principal_id=pr.principal_id
WHERE pr.principal_name='CJ Food' AND s.channel_id=2 AND s.`date` BETWEEN '2024-10-01' AND '2025-09-30';
""")

    # README.md
    readme_path = os.path.join(OUT_DIR, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(f"""# Đại Thuận Group (DTG) — Demo Database

## Quick populate (via populate.sh)

```bash
# From repo root
./populate.sh dtg
```

## Manual populate

```bash
# 1. Start container (if not already)
docker run --name mock_database \\
  -e MYSQL_ROOT_PASSWORD=root \\
  -p 3306:3306 -d mysql:8.0 \\
  --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci

# 2. Wait until ready
docker exec mock_database mysqladmin ping -uroot -proot --wait=30

# 3. Populate
for f in dtg_sql/01_*.sql dtg_sql/02_*.sql dtg_sql/03_*.sql dtg_sql/04_*.sql; do
  docker exec -i mock_database mysql -uroot -proot < "$f"
done

# 4. Verify
docker exec -i mock_database mysql -uroot -proot {DB_NAME} < dtg_sql/05_validation_queries.sql

# 5. Reset
docker exec mock_database mysql -uroot -proot -e \\
  "DROP DATABASE IF EXISTS {DB_NAME};"
```

## Schema
- 11 dimension tables (dim_*)
- 8 fact tables (fact_sales, fact_sales_out, fact_inventory, fact_fx_rate,
  fact_trade_promotion, fact_operating_cost, fact_budget, fact_route_coverage)
- 4 metadata tables (_meta_tables, _meta_columns, _meta_kpi, _meta_glossary)

## Data range
2023-10-01 → 2025-09-30 (24 months). Demo "current" = 30/09/2025.

## Scenario catalog
7 scenarios covered. See `_meta_kpi.related_questions` for mapping.
""")

    # Sizes
    for fn in os.listdir(OUT_DIR):
        fp = os.path.join(OUT_DIR, fn)
        sz = os.path.getsize(fp) / 1e6
        print(f"  {fn:35s} {sz:8.2f} MB")


# ==================================================================
# MAIN
# ==================================================================
if __name__ == "__main__":
    conn = connect()
    cur = conn.cursor()
    phase_a_schema(cur)
    conn.commit()
    conn.close()

    conn = connect(DB_NAME)
    conn.set_charset_collation('utf8mb4', 'utf8mb4_unicode_ci')
    cur = conn.cursor()
    prods, stores, whs, prov_idx, anomaly_ids = phase_b_master(cur)
    conn.commit()
    phase_b_checkpoint(prods, stores, prov_idx, whs)

    # Phase C
    print("\n=== PHASE C — TRANSACTIONS ===")
    fx_map = build_fx_rates()
    insert_fx_rates(cur, fx_map)
    conn.commit()

    sales = generate_sales(prods, stores, prov_idx, fx_map, anomaly_ids[0])
    sales = scale_sales(sales)
    insert_sales(cur, sales)
    conn.commit()

    # Build lookup dicts for sell-out
    store_attr = {}
    for s in stores:
        (sid, name, code, ch, chain, pid, dist_name, bid, opened, comp, tier, active) = s
        region_id = [r for pn,(ppid,rid,_,_) in prov_idx.items() if ppid==pid for r in [rid]][0]
        store_attr[sid] = (ch, pid, bid, comp, tier, region_id)
    prod_principal = {p[0]: p[4] for p in prods}
    prod_cat = {p[0]: p[3] for p in prods}

    sell_out = generate_sell_out_v2(sales, store_attr, prod_principal, prod_cat, anomaly_ids[0])
    insert_sell_out(cur, sell_out)
    conn.commit()

    promos = build_trade_promotions([p[0] for p in prods if p[4]==1])
    insert_trade_promotions(cur, promos)
    conn.commit()

    opex = build_operating_cost()
    insert_operating_cost(cur, opex)
    conn.commit()

    bud = build_budget()
    insert_budget(cur, bud)
    conn.commit()

    inv = build_inventory(prods, whs, sales, anomaly_ids)
    insert_inventory(cur, inv)
    conn.commit()

    populate_metadata(cur)
    conn.commit()

    phase_d_validate(cur)
    phase_e_export(cur)

    conn.close()
    print("\n[DONE]")
