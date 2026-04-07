-- ============================================================
-- 01_ddl_schema.sql
-- AP Saigon Petro — Lubricants Demo Database
-- DDL: CREATE DATABASE, CREATE TABLES, INDEXES, CONSTRAINTS
-- ============================================================

CREATE DATABASE IF NOT EXISTS lubricants_demo
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE lubricants_demo;

-- ============================================================
-- DIMENSION TABLES
-- ============================================================

CREATE TABLE IF NOT EXISTS regions (
  region_id VARCHAR(10) PRIMARY KEY COMMENT 'Ma khu vuc, vi du: RG-01',
  region_name VARCHAR(100) NOT NULL COMMENT 'Ten vung: Dong Nam Bo, DBSCL, Tay Nguyen...',
  macro_region VARCHAR(50) NOT NULL COMMENT 'Mien: Mien Bac, Mien Trung, Mien Nam',
  province VARCHAR(100) COMMENT 'Tinh/thanh pho',
  population_index DECIMAL(5,2) COMMENT 'Chi so dan so tuong doi (HCM=1.0, tinh nho=0.1)',
  INDEX idx_macro (macro_region)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT 'Khu vuc dia ly — hierarchy: Mien > Vung > Tinh';

CREATE TABLE IF NOT EXISTS channels (
  channel_id VARCHAR(10) PRIMARY KEY COMMENT 'Ma kenh, vi du: CH-01',
  channel_name VARCHAR(100) NOT NULL COMMENT 'Ten kenh ban hang',
  channel_type VARCHAR(20) NOT NULL COMMENT 'B2B hoac B2C',
  typical_margin_pct DECIMAL(5,2) COMMENT 'Bien loi nhuan gop dien hinh cua kenh, %'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT 'Kenh ban hang';

CREATE TABLE IF NOT EXISTS distributors (
  distributor_id VARCHAR(10) PRIMARY KEY COMMENT 'Ma NPP, vi du: NPP-001',
  distributor_name VARCHAR(200) NOT NULL COMMENT 'Ten nha phan phoi',
  region_id VARCHAR(10) NOT NULL COMMENT 'FK → regions',
  channel_id VARCHAR(10) NOT NULL COMMENT 'FK → channels (kenh chinh)',
  tier VARCHAR(20) NOT NULL COMMENT 'Tier: Tong dai ly, Dai ly cap 1, Dai ly cap 2',
  city VARCHAR(100) COMMENT 'Thanh pho/tinh cu the',
  credit_limit_vnd BIGINT COMMENT 'Han muc tin dung, VND',
  payment_term_days INT DEFAULT 30 COMMENT 'Ky han thanh toan mac dinh, ngay',
  status VARCHAR(20) DEFAULT 'active' COMMENT 'active/inactive',
  onboarded_date DATE COMMENT 'Ngay bat dau hop tac',
  FOREIGN KEY (region_id) REFERENCES regions(region_id),
  FOREIGN KEY (channel_id) REFERENCES channels(channel_id),
  INDEX idx_region (region_id),
  INDEX idx_tier (tier)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT 'Nha phan phoi — 100 NPP phu 63 tinh thanh';

CREATE TABLE IF NOT EXISTS products (
  product_id VARCHAR(15) PRIMARY KEY COMMENT 'Ma san pham, vi du: PRD-001',
  product_name VARCHAR(200) NOT NULL COMMENT 'Ten san pham day du',
  brand VARCHAR(50) NOT NULL COMMENT 'Thuong hieu: Saigon Petro, AP OIL, Sino, Polaris',
  product_group VARCHAR(100) NOT NULL COMMENT 'Nhom: Dau xe may, Dau o to, Dau xe tai, Dau hang hai, Dau cong nghiep, Mo boi tron, Dau nong nghiep',
  product_category VARCHAR(100) NOT NULL COMMENT 'Danh muc chi tiet: Dau 4T, Dau 2T, Dau tay ga, Dau diesel...',
  product_type VARCHAR(30) NOT NULL COMMENT 'Loai dau goc: mineral, semi_synthetic, full_synthetic, grease',
  viscosity_grade VARCHAR(30) COMMENT 'Cap do nhot: 10W-40, 15W-40, 20W-50...',
  volume_ml INT COMMENT 'Dung tich dong goi, ml',
  unit_price_vnd BIGINT COMMENT 'Gia ban le de xuat, VND/lit',
  cost_per_liter_vnd BIGINT COMMENT 'Gia von chuan/lit, VND (base cost, chua tinh transport)',
  popularity_weight DECIMAL(5,3) DEFAULT 1.000 COMMENT 'Trong so ban chay — Pareto: top 20% SKU weight cao',
  api_grade VARCHAR(20) COMMENT 'Tieu chuan API: SN, SL, CI-4, CH-4...',
  status VARCHAR(20) DEFAULT 'active',
  INDEX idx_brand (brand),
  INDEX idx_group (product_group),
  INDEX idx_type (product_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT 'Danh muc san pham dau mo nhon — ~200 SKU active';

CREATE TABLE IF NOT EXISTS suppliers (
  supplier_id VARCHAR(10) PRIMARY KEY COMMENT 'Ma nha cung cap',
  supplier_name VARCHAR(200) NOT NULL COMMENT 'Ten nha cung cap',
  country VARCHAR(50) NOT NULL COMMENT 'Quoc gia',
  material_type VARCHAR(50) NOT NULL COMMENT 'Loai NVL: base_oil_group_I/II/III/IV, additive, naphthenic_base_oil',
  lead_time_days INT COMMENT 'Thoi gian giao hang, ngay'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT 'Nha cung cap dau goc va phu gia';

CREATE TABLE IF NOT EXISTS production_lines (
  line_id VARCHAR(10) PRIMARY KEY COMMENT 'Ma day chuyen',
  line_name VARCHAR(100) NOT NULL COMMENT 'Ten day chuyen',
  line_type VARCHAR(50) NOT NULL COMMENT 'Loai: blending, filling_small, filling_large, filling_drum, grease',
  max_capacity_liters_per_month BIGINT COMMENT 'Cong suat toi da/thang, lit',
  target_yield_rate DECIMAL(5,3) DEFAULT 0.975 COMMENT 'Yield rate muc tieu'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT 'Day chuyen san xuat nha may Cat Lai — 5 lines';

-- ============================================================
-- FACT TABLES
-- ============================================================

CREATE TABLE IF NOT EXISTS sales_orders (
  order_id VARCHAR(20) PRIMARY KEY COMMENT 'Ma don hang, vi du: SO-2024-000001',
  order_date DATE NOT NULL COMMENT 'Ngay dat hang',
  distributor_id VARCHAR(10) NOT NULL COMMENT 'FK → distributors',
  product_id VARCHAR(15) NOT NULL COMMENT 'FK → products',
  quantity_liters DECIMAL(12,2) NOT NULL COMMENT 'So luong ban, lit',
  unit_price_vnd BIGINT NOT NULL COMMENT 'Don gia ban thuc te, VND/lit',
  total_revenue_vnd BIGINT NOT NULL COMMENT 'Doanh thu = quantity x unit_price, VND',
  cogs_material_vnd BIGINT NOT NULL COMMENT 'Gia von nguyen vat lieu, VND',
  cogs_production_vnd BIGINT NOT NULL COMMENT 'Chi phi san xuat, VND',
  cogs_transport_vnd BIGINT NOT NULL COMMENT 'Chi phi van chuyen den NPP, VND',
  total_cogs_vnd BIGINT NOT NULL COMMENT 'Tong COGS = material + production + transport, VND',
  gross_profit_vnd BIGINT NOT NULL COMMENT 'Loi nhuan gop = revenue - COGS, VND',
  gross_margin_pct DECIMAL(5,2) COMMENT 'Bien LN gop = gross_profit / revenue x 100, %',
  invoice_date DATE COMMENT 'Ngay xuat hoa don',
  due_date DATE COMMENT 'Ngay den han thanh toan',
  payment_status VARCHAR(20) DEFAULT 'pending' COMMENT 'pending, partial, paid, overdue',
  FOREIGN KEY (distributor_id) REFERENCES distributors(distributor_id),
  FOREIGN KEY (product_id) REFERENCES products(product_id),
  INDEX idx_date (order_date),
  INDEX idx_distributor (distributor_id),
  INDEX idx_product (product_id),
  INDEX idx_payment_status (payment_status),
  INDEX idx_date_distributor (order_date, distributor_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT 'Don hang ban cho NPP — grain: 1 line item per order. 18 thang data.';

CREATE TABLE IF NOT EXISTS payments (
  payment_id VARCHAR(20) PRIMARY KEY COMMENT 'Ma thanh toan',
  order_id VARCHAR(20) NOT NULL COMMENT 'FK → sales_orders',
  distributor_id VARCHAR(10) NOT NULL COMMENT 'FK → distributors',
  payment_date DATE NOT NULL COMMENT 'Ngay thanh toan thuc te',
  amount_vnd BIGINT NOT NULL COMMENT 'So tien thanh toan, VND',
  payment_method VARCHAR(30) COMMENT 'Chuyen khoan, Tien mat, LC',
  days_from_invoice INT COMMENT 'So ngay ke tu invoice_date (de tinh DSO)',
  is_overdue BOOLEAN DEFAULT FALSE COMMENT 'Tra sau due_date hay khong',
  FOREIGN KEY (order_id) REFERENCES sales_orders(order_id),
  FOREIGN KEY (distributor_id) REFERENCES distributors(distributor_id),
  INDEX idx_date (payment_date),
  INDEX idx_distributor (distributor_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT 'Thanh toan tu NPP — track DSO va overdue';

CREATE TABLE IF NOT EXISTS production_batches (
  batch_id VARCHAR(20) PRIMARY KEY COMMENT 'Ma batch san xuat',
  batch_date DATE NOT NULL COMMENT 'Ngay san xuat',
  line_id VARCHAR(10) NOT NULL COMMENT 'FK → production_lines',
  product_id VARCHAR(15) NOT NULL COMMENT 'FK → products (san pham chinh cua batch)',
  input_quantity_liters DECIMAL(12,2) NOT NULL COMMENT 'Luong nguyen lieu dau vao, lit',
  output_quantity_liters DECIMAL(12,2) NOT NULL COMMENT 'Luong thanh pham dau ra, lit',
  yield_rate DECIMAL(5,3) NOT NULL COMMENT 'Ty le thanh pham = output/input',
  material_cost_vnd BIGINT COMMENT 'Chi phi NVL cho batch, VND',
  labor_cost_vnd BIGINT COMMENT 'Chi phi nhan cong, VND',
  overhead_cost_vnd BIGINT COMMENT 'Chi phi overhead (dien, nuoc, khau hao), VND',
  total_production_cost_vnd BIGINT COMMENT 'Tong chi phi SX = material + labor + overhead, VND',
  cost_per_liter_vnd BIGINT COMMENT 'Chi phi SX/lit = total_cost / output_qty, VND',
  FOREIGN KEY (line_id) REFERENCES production_lines(line_id),
  FOREIGN KEY (product_id) REFERENCES products(product_id),
  INDEX idx_date (batch_date),
  INDEX idx_line (line_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT 'Batch san xuat nha may Cat Lai — track yield, cost per liter';

CREATE TABLE IF NOT EXISTS raw_material_costs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  month_date DATE NOT NULL COMMENT 'Thang (ngay 1 cua thang)',
  supplier_id VARCHAR(10) NOT NULL COMMENT 'FK → suppliers',
  material_type VARCHAR(50) NOT NULL COMMENT 'base_oil_group_I, base_oil_group_II, ..., additive',
  price_per_liter_vnd BIGINT NOT NULL COMMENT 'Gia mua/lit, VND',
  volume_purchased_liters DECIMAL(12,2) COMMENT 'Luong mua trong thang, lit',
  total_cost_vnd BIGINT COMMENT 'Tong chi phi = price x volume, VND',
  FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),
  INDEX idx_month (month_date),
  INDEX idx_supplier (supplier_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT 'Gia nguyen vat lieu theo thang — track trend gia dau goc';

-- ============================================================
-- METADATA TABLES
-- ============================================================

CREATE TABLE IF NOT EXISTS _meta_tables (
  table_name VARCHAR(100) PRIMARY KEY,
  description_vi TEXT,
  description_en TEXT,
  business_context TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS _meta_columns (
  id INT AUTO_INCREMENT PRIMARY KEY,
  table_name VARCHAR(100),
  column_name VARCHAR(100),
  data_type VARCHAR(50),
  description_vi TEXT,
  description_en TEXT,
  unit VARCHAR(50),
  example_values TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS _meta_kpi (
  kpi_name VARCHAR(100) PRIMARY KEY,
  formula_sql TEXT,
  description_vi TEXT,
  related_questions TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS _meta_glossary (
  term_vi VARCHAR(200) PRIMARY KEY,
  term_en VARCHAR(200),
  definition TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
