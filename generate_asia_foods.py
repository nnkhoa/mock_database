#!/usr/bin/env python3
"""
Asia Foods (Instant Noodle) Mock Data Generator
Database: instant_noodle_demo
Phases: A (Schema) + B (Master Data) + C (Transaction Data)
"""

import mysql.connector
import random
import math
from datetime import date, timedelta, datetime
from decimal import Decimal

random.seed(42)

# ============================================================
# DATABASE CONNECTION
# ============================================================
def get_conn():
    return mysql.connector.connect(
        host='localhost', port=3306, user='root', password='root',
        charset='utf8mb4', collation='utf8mb4_unicode_ci'
    )

def exec_sql(cursor, sql):
    for stmt in sql.split(';'):
        stmt = stmt.strip()
        if stmt:
            cursor.execute(stmt)

# ============================================================
# PHASE A: SCHEMA (DDL)
# ============================================================
def create_schema(cursor):
    cursor.execute("DROP DATABASE IF EXISTS instant_noodle_demo")
    cursor.execute("CREATE DATABASE instant_noodle_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    cursor.execute("USE instant_noodle_demo")

    # -- DIMENSION TABLES --
    cursor.execute("""
    CREATE TABLE factories (
      factory_id VARCHAR(3) PRIMARY KEY COMMENT 'Ma nha may: F01-F05',
      factory_name VARCHAR(100) NOT NULL COMMENT 'Ten nha may',
      factory_short_name VARCHAR(50) NOT NULL COMMENT 'Ten viet tat',
      province VARCHAR(50) NOT NULL COMMENT 'Tinh/thanh pho',
      region VARCHAR(20) NOT NULL COMMENT 'Mien: Bac/Trung/Nam',
      area_sqm INT NOT NULL COMMENT 'Dien tich nha may (m2)',
      year_commissioned INT NOT NULL COMMENT 'Nam dua vao hoat dong',
      designed_capacity_million_packs_month DECIMAL(10,1) NOT NULL COMMENT 'Cong suat thiet ke (trieu goi/thang)',
      num_production_lines INT NOT NULL COMMENT 'So day chuyen san xuat',
      num_employees INT NOT NULL COMMENT 'So nhan vien',
      status VARCHAR(20) DEFAULT 'active' COMMENT 'Trang thai: active/inactive'
    ) COMMENT = 'Danh sach 5 nha may san xuat cua Asia Foods'
    """)

    cursor.execute("""
    CREATE TABLE production_lines (
      line_id VARCHAR(10) PRIMARY KEY COMMENT 'Ma day chuyen: L01-01, L02-01...',
      factory_id VARCHAR(3) NOT NULL COMMENT 'FK -> factories',
      line_name VARCHAR(100) NOT NULL COMMENT 'Ten day chuyen',
      product_type VARCHAR(50) NOT NULL COMMENT 'Loai SP: mi_goi, mi_ly, chao, pho_hu_tieu',
      capacity_packs_per_hour INT NOT NULL COMMENT 'Cong suat (goi/gio)',
      commissioned_date DATE NOT NULL COMMENT 'Ngay dua vao van hanh',
      status VARCHAR(20) DEFAULT 'active' COMMENT 'Trang thai',
      FOREIGN KEY (factory_id) REFERENCES factories(factory_id)
    ) COMMENT = 'Day chuyen san xuat tai moi nha may'
    """)

    cursor.execute("""
    CREATE TABLE product_categories (
      category_id VARCHAR(5) PRIMARY KEY COMMENT 'Ma danh muc: CAT01-CAT06',
      category_name VARCHAR(100) NOT NULL COMMENT 'Ten danh muc tieng Viet',
      category_name_en VARCHAR(100) NOT NULL COMMENT 'Ten tieng Anh',
      price_segment VARCHAR(20) NOT NULL COMMENT 'Phan khuc gia: binh_dan, trung_cap, cao_cap',
      avg_margin_pct DECIMAL(5,2) NOT NULL COMMENT 'Bien loi nhuan gop trung binh (%)',
      volume_share_pct DECIMAL(5,2) NOT NULL COMMENT 'Ty trong san luong (%)',
      description TEXT COMMENT 'Mo ta danh muc'
    ) COMMENT = 'Phan loai san pham: Mi goi, Mi ly, Chao, JOMO, Pho/HT, Khac'
    """)

    cursor.execute("""
    CREATE TABLE products (
      product_id VARCHAR(10) PRIMARY KEY COMMENT 'Ma SKU: SKU001-SKU050',
      product_name VARCHAR(200) NOT NULL COMMENT 'Ten san pham tieng Viet',
      category_id VARCHAR(5) NOT NULL COMMENT 'FK -> product_categories',
      brand VARCHAR(50) NOT NULL COMMENT 'Thuong hieu',
      flavor VARCHAR(100) COMMENT 'Huong vi',
      pack_weight_g INT NOT NULL COMMENT 'Trong luong goi (gram)',
      unit_price_vnd DECIMAL(12,0) NOT NULL COMMENT 'Gia ban le de xuat (VND/goi)',
      cost_per_pack_vnd DECIMAL(12,0) NOT NULL COMMENT 'Gia thanh san xuat uoc tinh (VND/goi)',
      is_export TINYINT(1) DEFAULT 0 COMMENT '1 = co xuat khau',
      launch_year INT COMMENT 'Nam ra mat',
      popularity_weight DECIMAL(5,3) DEFAULT 1.000 COMMENT 'Trong so pho bien (Pareto): 0.001-1.000',
      status VARCHAR(20) DEFAULT 'active',
      FOREIGN KEY (category_id) REFERENCES product_categories(category_id)
    ) COMMENT = 'Danh muc ~50 SKU san pham cua Asia Foods'
    """)

    cursor.execute("""
    CREATE TABLE material_types (
      material_type_id VARCHAR(5) PRIMARY KEY COMMENT 'Ma NL: MAT01-MAT05',
      material_name VARCHAR(100) NOT NULL COMMENT 'Ten nguyen lieu',
      material_name_en VARCHAR(100) COMMENT 'Ten tieng Anh',
      unit VARCHAR(10) NOT NULL COMMENT 'Don vi: kg, lit, tan',
      is_imported TINYINT(1) DEFAULT 0 COMMENT '1 = nhap khau',
      import_origin VARCHAR(50) COMMENT 'Nguon nhap',
      cogs_share_pct DECIMAL(5,2) NOT NULL COMMENT 'Ty trong trong COGS (%)',
      price_volatility VARCHAR(20) COMMENT 'Muc bien dong gia: high/medium/low'
    ) COMMENT = 'Loai nguyen lieu dau vao'
    """)

    cursor.execute("""
    CREATE TABLE suppliers (
      supplier_id VARCHAR(5) PRIMARY KEY COMMENT 'Ma NCC: SUP01-SUP15',
      supplier_name VARCHAR(200) NOT NULL COMMENT 'Ten nha cung cap',
      material_type_id VARCHAR(5) NOT NULL COMMENT 'FK -> material_types',
      country VARCHAR(50) NOT NULL COMMENT 'Quoc gia',
      is_primary TINYINT(1) DEFAULT 0 COMMENT '1 = NCC chinh',
      FOREIGN KEY (material_type_id) REFERENCES material_types(material_type_id)
    ) COMMENT = 'Nha cung cap nguyen lieu'
    """)

    cursor.execute("""
    CREATE TABLE sales_channels (
      channel_id VARCHAR(5) PRIMARY KEY COMMENT 'Ma kenh: CH01-CH04',
      channel_name VARCHAR(50) NOT NULL COMMENT 'Ten kenh ban',
      channel_name_en VARCHAR(50) COMMENT 'Ten tieng Anh',
      revenue_share_pct DECIMAL(5,2) NOT NULL COMMENT 'Ty trong doanh thu (%)',
      description TEXT
    ) COMMENT = 'Kenh phan phoi: GT, MT, Xuat khau, Online'
    """)

    cursor.execute("""
    CREATE TABLE regions (
      region_id VARCHAR(5) PRIMARY KEY COMMENT 'Ma vung: REG01-REG05',
      region_name VARCHAR(50) NOT NULL COMMENT 'Ten khu vuc',
      population_million DECIMAL(5,1) COMMENT 'Dan so uoc tinh (trieu)',
      revenue_share_pct DECIMAL(5,2) NOT NULL COMMENT 'Ty trong doanh thu (%)',
      primary_factory_id VARCHAR(3) COMMENT 'NM phuc vu chinh'
    ) COMMENT = 'Khu vuc thi truong'
    """)

    cursor.execute("""
    CREATE TABLE cost_categories (
      cost_category_id VARCHAR(5) PRIMARY KEY COMMENT 'Ma loai CP: CC01-CC06',
      category_name VARCHAR(100) NOT NULL COMMENT 'Ten loai chi phi',
      category_name_en VARCHAR(100) COMMENT 'Ten tieng Anh',
      is_fixed TINYINT(1) DEFAULT 0 COMMENT '1 = chi phi co dinh',
      typical_cogs_share_pct DECIMAL(5,2) COMMENT 'Ty trong COGS dien hinh (%)'
    ) COMMENT = 'Phan loai chi phi san xuat'
    """)

    # -- FACT TABLES --
    cursor.execute("""
    CREATE TABLE material_purchases (
      purchase_id INT AUTO_INCREMENT PRIMARY KEY,
      factory_id VARCHAR(3) NOT NULL,
      material_type_id VARCHAR(5) NOT NULL,
      supplier_id VARCHAR(5) NOT NULL,
      purchase_date DATE NOT NULL,
      quantity_kg DECIMAL(12,2) NOT NULL COMMENT 'So luong (kg)',
      unit_price_vnd DECIMAL(12,2) NOT NULL COMMENT 'Don gia (VND/kg)',
      total_amount_vnd DECIMAL(15,0) NOT NULL COMMENT 'Tong tien (VND)',
      delivery_date DATE COMMENT 'Ngay giao hang',
      quality_grade VARCHAR(5) COMMENT 'Cap chat luong: A/B/C',
      FOREIGN KEY (factory_id) REFERENCES factories(factory_id),
      FOREIGN KEY (material_type_id) REFERENCES material_types(material_type_id),
      FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),
      INDEX idx_purchase_factory_date (factory_id, purchase_date),
      INDEX idx_purchase_material (material_type_id, purchase_date)
    ) COMMENT = 'Don mua nguyen lieu'
    """)

    cursor.execute("""
    CREATE TABLE production_orders (
      production_order_id INT AUTO_INCREMENT PRIMARY KEY,
      factory_id VARCHAR(3) NOT NULL,
      line_id VARCHAR(10) NOT NULL,
      product_id VARCHAR(10) NOT NULL,
      production_date DATE NOT NULL,
      shift VARCHAR(10) NOT NULL COMMENT 'Ca san xuat: ca_1, ca_2, ca_3',
      planned_qty_packs INT NOT NULL,
      actual_qty_packs INT NOT NULL,
      wastage_qty_packs INT NOT NULL DEFAULT 0,
      material_used_kg DECIMAL(12,2) COMMENT 'Nguyen lieu su dung (kg)',
      labor_hours DECIMAL(8,2) COMMENT 'Gio cong lao dong',
      energy_kwh DECIMAL(10,2) COMMENT 'Dien nang tieu thu (kWh)',
      gas_m3 DECIMAL(10,2) COMMENT 'Gas tieu thu (m3)',
      quality_pass_rate DECIMAL(5,2) COMMENT 'Ty le dat chat luong (%)',
      FOREIGN KEY (factory_id) REFERENCES factories(factory_id),
      FOREIGN KEY (line_id) REFERENCES production_lines(line_id),
      FOREIGN KEY (product_id) REFERENCES products(product_id),
      INDEX idx_prod_factory_date (factory_id, production_date),
      INDEX idx_prod_product_date (product_id, production_date),
      INDEX idx_prod_line_date (line_id, production_date)
    ) COMMENT = 'Lenh san xuat hang ngay — 1 dong = 1 ca SX tren 1 day chuyen'
    """)

    cursor.execute("""
    CREATE TABLE cost_allocations (
      allocation_id INT AUTO_INCREMENT PRIMARY KEY,
      factory_id VARCHAR(3) NOT NULL,
      cost_category_id VARCHAR(5) NOT NULL,
      month_date DATE NOT NULL COMMENT 'Thang phan bo (ngay 1)',
      amount_vnd DECIMAL(15,0) NOT NULL COMMENT 'So tien (VND)',
      notes TEXT COMMENT 'Ghi chu',
      FOREIGN KEY (factory_id) REFERENCES factories(factory_id),
      FOREIGN KEY (cost_category_id) REFERENCES cost_categories(cost_category_id),
      INDEX idx_cost_factory_month (factory_id, month_date)
    ) COMMENT = 'Phan bo chi phi san xuat theo NM x thang x loai CP'
    """)

    cursor.execute("""
    CREATE TABLE sales_orders (
      order_id INT AUTO_INCREMENT PRIMARY KEY,
      order_date DATE NOT NULL,
      factory_id VARCHAR(3) NOT NULL,
      channel_id VARCHAR(5) NOT NULL,
      region_id VARCHAR(5) NOT NULL,
      customer_name VARCHAR(200) COMMENT 'Ten khach hang/nha phan phoi',
      total_quantity_packs INT NOT NULL,
      total_revenue_vnd DECIMAL(15,0) NOT NULL,
      total_cogs_vnd DECIMAL(15,0) NOT NULL,
      FOREIGN KEY (factory_id) REFERENCES factories(factory_id),
      FOREIGN KEY (channel_id) REFERENCES sales_channels(channel_id),
      FOREIGN KEY (region_id) REFERENCES regions(region_id),
      INDEX idx_sales_factory_date (factory_id, order_date),
      INDEX idx_sales_channel_date (channel_id, order_date),
      INDEX idx_sales_region_date (region_id, order_date)
    ) COMMENT = 'Don ban hang tong hop'
    """)

    cursor.execute("""
    CREATE TABLE sales_order_items (
      item_id INT AUTO_INCREMENT PRIMARY KEY,
      order_id INT NOT NULL,
      product_id VARCHAR(10) NOT NULL,
      quantity_packs INT NOT NULL,
      unit_price_vnd DECIMAL(12,0) NOT NULL,
      line_revenue_vnd DECIMAL(15,0) NOT NULL,
      line_cogs_vnd DECIMAL(15,0) NOT NULL,
      FOREIGN KEY (order_id) REFERENCES sales_orders(order_id),
      FOREIGN KEY (product_id) REFERENCES products(product_id),
      INDEX idx_item_product (product_id),
      INDEX idx_item_order (order_id)
    ) COMMENT = 'Chi tiet line item trong don ban hang'
    """)

    # -- METADATA TABLES --
    cursor.execute("""
    CREATE TABLE _meta_tables (
      table_name VARCHAR(100) PRIMARY KEY,
      description_vi TEXT NOT NULL,
      description_en TEXT,
      business_context TEXT,
      row_count_estimate INT
    ) COMMENT = 'Metadata: mo ta business context tung bang'
    """)

    cursor.execute("""
    CREATE TABLE _meta_columns (
      id INT AUTO_INCREMENT PRIMARY KEY,
      table_name VARCHAR(100) NOT NULL,
      column_name VARCHAR(100) NOT NULL,
      data_type VARCHAR(50),
      description_vi TEXT NOT NULL,
      description_en TEXT,
      unit VARCHAR(50),
      example_values TEXT
    ) COMMENT = 'Metadata: mo ta y nghia tung cot'
    """)

    cursor.execute("""
    CREATE TABLE _meta_kpi (
      kpi_name VARCHAR(100) PRIMARY KEY,
      formula_sql TEXT NOT NULL,
      description_vi TEXT NOT NULL,
      related_questions TEXT
    ) COMMENT = 'Metadata: cong thuc SQL cho cac KPI'
    """)

    cursor.execute("""
    CREATE TABLE _meta_glossary (
      term_vi VARCHAR(100) PRIMARY KEY,
      term_en VARCHAR(100),
      definition TEXT NOT NULL,
      related_table VARCHAR(100)
    ) COMMENT = 'Metadata: thuat ngu nganh mi an lien'
    """)

    print("Schema created: 17 tables")


# ============================================================
# PHASE B: MASTER DATA
# ============================================================
def insert_master_data(cursor):
    # --- Factories ---
    factories = [
        ('F01', 'NM An Phú', 'An Phú', 'Bình Dương', 'Nam', 35000, 2003, 105.0, 5, 850, 'active'),
        ('F02', 'NM Nam Tân Uyên', 'Nam Tân Uyên', 'Bình Dương', 'Nam', 100000, 2017, 130.0, 4, 920, 'active'),
        ('F03', 'NM Bắc Ninh', 'Bắc Ninh', 'Bắc Ninh', 'Bắc', 57000, 2011, 65.0, 3, 580, 'active'),
        ('F04', 'NM Đà Nẵng', 'Đà Nẵng', 'Đà Nẵng', 'Trung', 20000, 2012, 35.0, 2, 320, 'active'),
        ('F05', 'NM Gò Vấp (Legacy)', 'Gò Vấp', 'TP.HCM', 'Nam', 13000, 1990, 25.0, 2, 330, 'active'),
    ]
    cursor.executemany(
        "INSERT INTO factories VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", factories
    )
    print(f"  factories: {len(factories)} rows")

    # --- Production Lines ---
    lines = [
        ('L01-01', 'F01', 'An Phú - DC Mì gói 1', 'mi_goi', 25000, '2003-06-01', 'active'),
        ('L01-02', 'F01', 'An Phú - DC Mì gói 2', 'mi_goi', 25000, '2005-03-01', 'active'),
        ('L01-03', 'F01', 'An Phú - DC Mì ly 1', 'mi_ly', 15000, '2015-01-01', 'active'),
        ('L01-04', 'F01', 'An Phú - DC Mì ly 2 (Mới)', 'mi_ly', 18000, '2025-04-15', 'active'),
        ('L01-05', 'F01', 'An Phú - DC Cháo', 'chao', 12000, '2018-06-01', 'active'),
        ('L02-01', 'F02', 'Nam Tân Uyên - DC Mì gói 1', 'mi_goi', 30000, '2017-09-01', 'active'),
        ('L02-02', 'F02', 'Nam Tân Uyên - DC Mì gói 2', 'mi_goi', 30000, '2019-01-01', 'active'),
        ('L02-03', 'F02', 'Nam Tân Uyên - DC Mì ly', 'mi_ly', 18000, '2020-06-01', 'active'),
        ('L02-04', 'F02', 'Nam Tân Uyên - DC JOMO', 'mi_goi', 20000, '2021-03-01', 'active'),
        ('L03-01', 'F03', 'Bắc Ninh - DC Mì gói 1', 'mi_goi', 22000, '2011-08-01', 'active'),
        ('L03-02', 'F03', 'Bắc Ninh - DC Mì gói 2', 'mi_goi', 22000, '2014-05-01', 'active'),
        ('L03-03', 'F03', 'Bắc Ninh - DC Cháo', 'chao', 10000, '2016-11-01', 'active'),
        ('L04-01', 'F04', 'Đà Nẵng - DC Mì gói 1', 'mi_goi', 18000, '2012-10-01', 'active'),
        ('L04-02', 'F04', 'Đà Nẵng - DC Mì gói 2', 'mi_goi', 15000, '2015-04-01', 'active'),
        ('L05-01', 'F05', 'Gò Vấp - DC Phở/HT', 'pho_hu_tieu', 10000, '2010-01-01', 'active'),
        ('L05-02', 'F05', 'Gò Vấp - DC Mì đặc biệt', 'mi_goi', 12000, '2008-06-01', 'active'),
    ]
    cursor.executemany(
        "INSERT INTO production_lines VALUES (%s,%s,%s,%s,%s,%s,%s)", lines
    )
    print(f"  production_lines: {len(lines)} rows")

    # --- Product Categories ---
    categories = [
        ('CAT01', 'Mì gói Gấu Đỏ', 'Instant Noodle Pack', 'binh_dan', 19.0, 55.0, 'Dòng mì gói truyền thống, chủ lực của Asia Foods'),
        ('CAT02', 'Mì Ly Gấu Đỏ', 'Cup Noodle', 'binh_dan', 23.0, 18.0, 'Mì ly tiện lợi, phân khúc bình dân'),
        ('CAT03', 'JOMO (Mì Khoai Tây)', 'JOMO Potato Noodle', 'trung_cap', 27.0, 10.0, 'Dòng mì khoai tây trung cấp, thương hiệu riêng'),
        ('CAT04', 'Cháo Gấu Đỏ', 'Instant Porridge', 'binh_dan', 30.0, 8.0, 'Cháo ăn liền, margin cao, bán mạnh mùa lạnh'),
        ('CAT05', 'Phở & Hủ tiếu ăn liền', 'Instant Pho & Rice Noodle', 'binh_dan', 21.0, 5.0, 'Phở và hủ tiếu ăn liền'),
        ('CAT06', 'Mì Trứng Vàng & Mộc Việt', 'Egg Noodle & Moc Viet', 'binh_dan', 20.0, 4.0, 'Dòng mì trứng và mì chay/đặc biệt'),
    ]
    cursor.executemany(
        "INSERT INTO product_categories VALUES (%s,%s,%s,%s,%s,%s,%s)", categories
    )
    print(f"  product_categories: {len(categories)} rows")

    # --- Products (50 SKUs) ---
    products = [
        # CAT01 - Mì gói Gấu Đỏ (10 SKU)
        ('SKU001', 'Mì Gấu Đỏ Tôm Chua Cay', 'CAT01', 'Gấu Đỏ', 'Tôm chua cay', 75, 3500, 2835, 1, 2005, 1.000),
        ('SKU002', 'Mì Gấu Đỏ Bò Hầm Rau Thơm', 'CAT01', 'Gấu Đỏ', 'Bò hầm', 75, 3500, 2835, 1, 2005, 0.850),
        ('SKU003', 'Mì Gấu Đỏ Gà Hầm Ngũ Vị', 'CAT01', 'Gấu Đỏ', 'Gà hầm', 75, 3500, 2835, 1, 2006, 0.700),
        ('SKU004', 'Mì Gấu Đỏ Lẩu Thái', 'CAT01', 'Gấu Đỏ', 'Lẩu Thái', 75, 3800, 3078, 0, 2010, 0.600),
        ('SKU005', 'Mì Gấu Đỏ Sườn Hầm Ngũ Quả', 'CAT01', 'Gấu Đỏ', 'Sườn hầm', 75, 3500, 2835, 0, 2008, 0.500),
        ('SKU006', 'Mì Gấu Đỏ Hải Sản', 'CAT01', 'Gấu Đỏ', 'Hải sản', 75, 3500, 2835, 0, 2012, 0.350),
        ('SKU007', 'Mì Gấu Đỏ Chay Rau Nấm', 'CAT01', 'Gấu Đỏ', 'Chay rau nấm', 75, 3200, 2592, 0, 2015, 0.200),
        ('SKU008', 'Mì Gấu Đỏ Thịt Bằm', 'CAT01', 'Gấu Đỏ', 'Thịt bằm', 75, 3500, 2835, 0, 2011, 0.300),
        ('SKU009', 'Mì Gấu Đỏ Kim Chi', 'CAT01', 'Gấu Đỏ', 'Kim chi', 75, 3800, 3078, 0, 2018, 0.150),
        ('SKU00A', 'Mì Gấu Đỏ Sa Tế', 'CAT01', 'Gấu Đỏ', 'Sa tế', 75, 3500, 2835, 0, 2014, 0.100),
        # CAT02 - Mì Ly Gấu Đỏ (8 SKU)
        ('SKU010', 'Mì Ly Gấu Đỏ Tôm Chua Cay', 'CAT02', 'Gấu Đỏ', 'Tôm chua cay', 65, 7000, 5390, 1, 2012, 0.900),
        ('SKU011', 'Mì Ly Gấu Đỏ Bò Hầm', 'CAT02', 'Gấu Đỏ', 'Bò hầm', 65, 7000, 5390, 1, 2012, 0.750),
        ('SKU012', 'Mì Ly Gấu Đỏ Lẩu Tôm', 'CAT02', 'Gấu Đỏ', 'Lẩu tôm', 65, 7000, 5390, 0, 2015, 0.550),
        ('SKU013', 'Mì Ly Gấu Đỏ Gà Hầm', 'CAT02', 'Gấu Đỏ', 'Gà hầm', 65, 7000, 5390, 0, 2014, 0.400),
        ('SKU014', 'Mì Ly Gấu Đỏ Bò Viên', 'CAT02', 'Gấu Đỏ', 'Bò viên', 65, 7500, 5775, 0, 2017, 0.300),
        ('SKU015', 'Mì Ly Gấu Đỏ Hải Sản', 'CAT02', 'Gấu Đỏ', 'Hải sản', 65, 7000, 5390, 0, 2016, 0.200),
        ('SKU016', 'Mì Ly Gấu Đỏ Lẩu Thái', 'CAT02', 'Gấu Đỏ', 'Lẩu Thái', 65, 7500, 5775, 0, 2019, 0.150),
        ('SKU017', 'Mì Ly Gấu Đỏ Sườn Hầm', 'CAT02', 'Gấu Đỏ', 'Sườn hầm', 65, 7000, 5390, 0, 2020, 0.100),
        # CAT03 - JOMO (7 SKU)
        ('SKU020', 'Mì JOMO Khoai Tây Vị Bò', 'CAT03', 'JOMO', 'Khoai tây bò', 80, 5500, 4015, 0, 2019, 0.800),
        ('SKU021', 'Mì JOMO Khoai Tây Vị Gà', 'CAT03', 'JOMO', 'Khoai tây gà', 80, 5500, 4015, 0, 2019, 0.650),
        ('SKU022', 'Mì JOMO Khoai Tây Vị Tôm', 'CAT03', 'JOMO', 'Khoai tây tôm', 80, 5500, 4015, 0, 2020, 0.450),
        ('SKU023', 'Mì JOMO Khoai Tây Sườn Hầm', 'CAT03', 'JOMO', 'Khoai tây sườn', 80, 5800, 4234, 0, 2021, 0.300),
        ('SKU024', 'Mì JOMO Khoai Tây Lẩu Thái', 'CAT03', 'JOMO', 'Khoai tây lẩu Thái', 80, 5800, 4234, 0, 2022, 0.200),
        ('SKU025', 'Mì JOMO Khoai Tây Hải Sản', 'CAT03', 'JOMO', 'Khoai tây hải sản', 80, 5500, 4015, 0, 2023, 0.120),
        ('SKU026', 'Mì JOMO Khoai Tây Chay', 'CAT03', 'JOMO', 'Khoai tây chay', 80, 5200, 3796, 0, 2023, 0.080),
        # CAT04 - Cháo Gấu Đỏ (8 SKU)
        ('SKU030', 'Cháo Gấu Đỏ Thịt Bằm', 'CAT04', 'Gấu Đỏ', 'Thịt bằm', 50, 6000, 4200, 0, 2014, 0.700),
        ('SKU031', 'Cháo Gấu Đỏ Tổ Yến Thịt Bằm', 'CAT04', 'Gấu Đỏ', 'Tổ yến thịt bằm', 50, 8000, 5600, 0, 2018, 0.500),
        ('SKU032', 'Cháo Gấu Đỏ Gà', 'CAT04', 'Gấu Đỏ', 'Gà', 50, 6000, 4200, 0, 2014, 0.600),
        ('SKU033', 'Cháo Gấu Đỏ Cá Hồi', 'CAT04', 'Gấu Đỏ', 'Cá hồi', 50, 8500, 5950, 0, 2020, 0.350),
        ('SKU034', 'Cháo Gấu Đỏ Tôm', 'CAT04', 'Gấu Đỏ', 'Tôm', 50, 6000, 4200, 0, 2015, 0.250),
        ('SKU035', 'Cháo Gấu Đỏ Sườn Non', 'CAT04', 'Gấu Đỏ', 'Sườn non', 50, 6500, 4550, 0, 2017, 0.180),
        ('SKU036', 'Cháo Gấu Đỏ Lươn', 'CAT04', 'Gấu Đỏ', 'Lươn', 50, 7000, 4900, 0, 2021, 0.100),
        ('SKU037', 'Cháo Gấu Đỏ Đậu Xanh', 'CAT04', 'Gấu Đỏ', 'Đậu xanh', 50, 5500, 3850, 0, 2016, 0.080),
        # CAT05 - Phở & Hủ tiếu (7 SKU)
        ('SKU040', 'Phở Gấu Đỏ Bò', 'CAT05', 'Gấu Đỏ', 'Bò', 65, 5000, 3950, 1, 2013, 0.600),
        ('SKU041', 'Phở Gấu Đỏ Gà', 'CAT05', 'Gấu Đỏ', 'Gà', 65, 5000, 3950, 0, 2013, 0.400),
        ('SKU042', 'Hủ Tiếu Gấu Đỏ Nam Vang', 'CAT05', 'Gấu Đỏ', 'Nam Vang', 65, 5000, 3950, 0, 2015, 0.300),
        ('SKU043', 'Phở Gấu Đỏ Bò Viên', 'CAT05', 'Gấu Đỏ', 'Bò viên', 65, 5500, 4345, 0, 2018, 0.200),
        ('SKU044', 'Hủ Tiếu Gấu Đỏ Mì', 'CAT05', 'Gấu Đỏ', 'Hủ tiếu mì', 65, 4500, 3555, 0, 2016, 0.150),
        ('SKU045', 'Phở Gấu Đỏ Chay', 'CAT05', 'Gấu Đỏ', 'Chay', 65, 4800, 3792, 0, 2020, 0.080),
        ('SKU046', 'Bún Bò Gấu Đỏ', 'CAT05', 'Gấu Đỏ', 'Bún bò', 65, 5000, 3950, 0, 2022, 0.060),
        # CAT06 - Mì Trứng Vàng & Mộc Việt (10 SKU)
        ('SKU050', 'Mì Trứng Vàng Tôm Hành', 'CAT06', 'Trứng Vàng', 'Tôm hành', 65, 3000, 2400, 0, 2010, 0.400),
        ('SKU051', 'Mì Trứng Vàng Bò Hầm', 'CAT06', 'Trứng Vàng', 'Bò hầm', 65, 3000, 2400, 0, 2010, 0.300),
        ('SKU052', 'Mì Trứng Vàng Gà Hầm', 'CAT06', 'Trứng Vàng', 'Gà hầm', 65, 3000, 2400, 0, 2011, 0.200),
        ('SKU053', 'Mì Trứng Vàng Hải Sản', 'CAT06', 'Trứng Vàng', 'Hải sản', 65, 3200, 2560, 0, 2015, 0.100),
        ('SKU054', 'Mì Mộc Việt Chay', 'CAT06', 'Mộc Việt', 'Chay', 65, 3500, 2800, 0, 2018, 0.150),
        ('SKU055', 'Mì Mộc Việt Rau Nấm', 'CAT06', 'Mộc Việt', 'Rau nấm', 65, 3500, 2800, 0, 2019, 0.120),
        ('SKU056', 'Mì Mộc Việt Tôm', 'CAT06', 'Mộc Việt', 'Tôm', 65, 3500, 2800, 0, 2020, 0.080),
        ('SKU057', 'Mì Trứng Vàng Sườn Hầm', 'CAT06', 'Trứng Vàng', 'Sườn hầm', 65, 3000, 2400, 0, 2013, 0.070),
        ('SKU058', 'Mì Mộc Việt Gà Hầm', 'CAT06', 'Mộc Việt', 'Gà hầm', 65, 3500, 2800, 0, 2021, 0.050),
        ('SKU059', 'Mì Trứng Vàng Kim Chi', 'CAT06', 'Trứng Vàng', 'Kim chi', 65, 3200, 2560, 0, 2022, 0.040),
    ]
    cursor.executemany(
        "INSERT INTO products VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'active')", products
    )
    print(f"  products: {len(products)} rows")

    # --- Material Types ---
    materials = [
        ('MAT01', 'Bột mì', 'Wheat Flour', 'kg', 1, 'Úc', 40.0, 'high'),
        ('MAT02', 'Dầu cọ', 'Palm Oil', 'kg', 1, 'Indonesia', 18.0, 'high'),
        ('MAT03', 'Gia vị & phụ gia', 'Seasoning & Additives', 'kg', 0, 'Nội địa', 12.0, 'medium'),
        ('MAT04', 'Bao bì', 'Packaging', 'đơn vị', 0, 'Nội địa', 10.0, 'low'),
        ('MAT05', 'Năng lượng (gas + điện)', 'Energy', 'kWh_eq', 0, 'Nội địa', 8.0, 'medium'),
    ]
    cursor.executemany(
        "INSERT INTO material_types VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", materials
    )
    print(f"  material_types: {len(materials)} rows")

    # --- Suppliers ---
    suppliers = [
        ('SUP01', 'Interflour Vietnam', 'MAT01', 'Úc/VN', 1),
        ('SUP02', 'Vimaflour', 'MAT01', 'VN', 0),
        ('SUP03', 'Bunge Loders Croklaan', 'MAT02', 'Indonesia', 1),
        ('SUP04', 'Wilmar International VN', 'MAT02', 'Indonesia/VN', 0),
        ('SUP05', 'Công ty Gia vị Việt Ấn', 'MAT03', 'VN', 1),
        ('SUP06', 'Ajinomoto VN', 'MAT03', 'VN', 0),
        ('SUP07', 'Tân Tiến Packaging', 'MAT04', 'VN', 1),
        ('SUP08', 'Liksin', 'MAT04', 'VN', 0),
        ('SUP09', 'Mekong Flour Mills', 'MAT01', 'VN', 0),
        ('SUP10', 'Golden Agri-Resources VN', 'MAT02', 'Indonesia/VN', 0),
        ('SUP11', 'Công ty Gia vị Đồng Nai', 'MAT03', 'VN', 0),
        ('SUP12', 'Bao Bì Sài Gòn', 'MAT04', 'VN', 0),
        ('SUP13', 'PV Gas South', 'MAT05', 'VN', 1),
        ('SUP14', 'EVN Southern', 'MAT05', 'VN', 0),
    ]
    cursor.executemany(
        "INSERT INTO suppliers VALUES (%s,%s,%s,%s,%s)", suppliers
    )
    print(f"  suppliers: {len(suppliers)} rows")

    # --- Sales Channels ---
    channels = [
        ('CH01', 'Kênh truyền thống (GT)', 'General Trade', 60.0, 'Tạp hóa, đại lý, chợ truyền thống — kênh chủ lực'),
        ('CH02', 'Kênh hiện đại (MT)', 'Modern Trade', 25.0, 'Siêu thị, CVSL: Co.opmart, Bách Hóa Xanh, WinMart'),
        ('CH03', 'Xuất khẩu', 'Export', 12.0, 'Cambodia, Đông Âu, Cuba'),
        ('CH04', 'Online / E-commerce', 'Online', 3.0, 'Shopee, Lazada, TikTok Shop'),
    ]
    cursor.executemany(
        "INSERT INTO sales_channels VALUES (%s,%s,%s,%s,%s)", channels
    )
    print(f"  sales_channels: {len(channels)} rows")

    # --- Regions ---
    regions = [
        ('REG01', 'Miền Bắc', 35.0, 28.0, 'F03'),
        ('REG02', 'Miền Trung', 20.0, 12.0, 'F04'),
        ('REG03', 'Miền Nam (TP.HCM & Đông Nam Bộ)', 22.0, 32.0, 'F01'),
        ('REG04', 'Tây Nam Bộ', 18.0, 16.0, 'F02'),
        ('REG05', 'Xuất khẩu', None, 12.0, 'F01'),
    ]
    cursor.executemany(
        "INSERT INTO regions VALUES (%s,%s,%s,%s,%s)", regions
    )
    print(f"  regions: {len(regions)} rows")

    # --- Cost Categories ---
    cost_cats = [
        ('CC01', 'Nguyên vật liệu', 'Raw Materials', 0, 70.0),
        ('CC02', 'Nhân công trực tiếp', 'Direct Labor', 0, 7.0),
        ('CC03', 'Năng lượng (gas + điện)', 'Energy', 0, 8.0),
        ('CC04', 'Khấu hao máy móc & nhà xưởng', 'Depreciation', 1, 8.0),
        ('CC05', 'Nhân công gián tiếp & quản lý NM', 'Indirect Labor & Mgmt', 1, 4.0),
        ('CC06', 'Chi phí sản xuất khác', 'Other Manufacturing', 0, 3.0),
    ]
    cursor.executemany(
        "INSERT INTO cost_categories VALUES (%s,%s,%s,%s,%s)", cost_cats
    )
    print(f"  cost_categories: {len(cost_cats)} rows")

    return products, lines


# ============================================================
# PHASE C: TRANSACTION DATA
# ============================================================

# --- Configuration ---
START_DATE = date(2024, 1, 1)
END_DATE = date(2025, 6, 30)

# Factory utilization targets
FACTORY_UTILIZATION = {
    'F01': 0.82, 'F02': 0.75, 'F03': 0.68, 'F04': 0.37, 'F05': 0.72
}
FACTORY_CAPACITY = {
    'F01': 105.0, 'F02': 130.0, 'F03': 65.0, 'F04': 35.0, 'F05': 25.0
}

# Product mix per factory
FACTORY_PRODUCT_MIX = {
    'F01': {'CAT01': 0.45, 'CAT02': 0.25, 'CAT03': 0.10, 'CAT04': 0.12, 'CAT05': 0.05, 'CAT06': 0.03},
    'F02': {'CAT01': 0.55, 'CAT02': 0.15, 'CAT03': 0.15, 'CAT04': 0.05, 'CAT05': 0.05, 'CAT06': 0.05},
    'F03': {'CAT01': 0.60, 'CAT02': 0.12, 'CAT03': 0.05, 'CAT04': 0.15, 'CAT05': 0.03, 'CAT06': 0.05},
    'F04': {'CAT01': 0.70, 'CAT02': 0.10, 'CAT03': 0.05, 'CAT04': 0.05, 'CAT05': 0.05, 'CAT06': 0.05},
    'F05': {'CAT01': 0.20, 'CAT02': 0.10, 'CAT03': 0.05, 'CAT04': 0.05, 'CAT05': 0.40, 'CAT06': 0.20},
}

# Seasonality
MONTHLY_SEASONALITY = [1.05, 0.88, 0.93, 0.94, 0.98, 1.00, 1.02, 1.01, 0.99, 1.03, 1.08, 1.12]

CATEGORY_SEASONALITY = {
    'CAT01': [1.0]*12,
    'CAT02': [0.95, 0.90, 0.95, 0.98, 1.02, 1.08, 1.10, 1.08, 1.02, 0.98, 0.95, 0.95],
    'CAT03': [1.0]*12,
    'CAT04': [1.20, 1.25, 1.05, 0.90, 0.80, 0.75, 0.75, 0.80, 0.85, 1.00, 1.15, 1.25],
    'CAT05': [1.0]*12,
    'CAT06': [1.0]*12,
}

WEEKLY_PATTERN = [1.05, 1.02, 1.00, 0.98, 1.03, 1.08, 0.84]

# Factory→lines mapping
FACTORY_LINES = {
    'F01': ['L01-01', 'L01-02', 'L01-03', 'L01-04', 'L01-05'],
    'F02': ['L02-01', 'L02-02', 'L02-03', 'L02-04'],
    'F03': ['L03-01', 'L03-02', 'L03-03'],
    'F04': ['L04-01', 'L04-02'],
    'F05': ['L05-01', 'L05-02'],
}

LINE_PRODUCT_TYPE = {
    'L01-01': 'mi_goi', 'L01-02': 'mi_goi', 'L01-03': 'mi_ly', 'L01-04': 'mi_ly', 'L01-05': 'chao',
    'L02-01': 'mi_goi', 'L02-02': 'mi_goi', 'L02-03': 'mi_ly', 'L02-04': 'mi_goi',
    'L03-01': 'mi_goi', 'L03-02': 'mi_goi', 'L03-03': 'chao',
    'L04-01': 'mi_goi', 'L04-02': 'mi_goi',
    'L05-01': 'pho_hu_tieu', 'L05-02': 'mi_goi',
}

LINE_CAPACITY_PER_HOUR = {
    'L01-01': 25000, 'L01-02': 25000, 'L01-03': 15000, 'L01-04': 18000, 'L01-05': 12000,
    'L02-01': 30000, 'L02-02': 30000, 'L02-03': 18000, 'L02-04': 20000,
    'L03-01': 22000, 'L03-02': 22000, 'L03-03': 10000,
    'L04-01': 18000, 'L04-02': 15000,
    'L05-01': 10000, 'L05-02': 12000,
}

# Commissioned dates for filtering
LINE_COMMISSIONED = {
    'L01-04': date(2025, 4, 15),  # New line - anomaly source
}

# Product type → category mapping
PRODUCT_TYPE_CATEGORIES = {
    'mi_goi': ['CAT01', 'CAT03', 'CAT06'],  # mì gói lines can make standard, JOMO, Trứng Vàng
    'mi_ly': ['CAT02'],
    'chao': ['CAT04'],
    'pho_hu_tieu': ['CAT05'],
}

# Channel distribution weights
CHANNEL_WEIGHTS = {'CH01': 0.60, 'CH02': 0.25, 'CH03': 0.12, 'CH04': 0.03}

# Region distribution weights
REGION_WEIGHTS = {'REG01': 0.28, 'REG02': 0.12, 'REG03': 0.32, 'REG04': 0.16, 'REG05': 0.12}

# Factory → primary region mapping
FACTORY_REGIONS = {
    'F01': {'REG03': 0.45, 'REG04': 0.20, 'REG05': 0.15, 'REG02': 0.10, 'REG01': 0.10},
    'F02': {'REG04': 0.40, 'REG03': 0.30, 'REG05': 0.10, 'REG01': 0.10, 'REG02': 0.10},
    'F03': {'REG01': 0.70, 'REG02': 0.10, 'REG03': 0.10, 'REG04': 0.05, 'REG05': 0.05},
    'F04': {'REG02': 0.60, 'REG03': 0.15, 'REG01': 0.10, 'REG04': 0.10, 'REG05': 0.05},
    'F05': {'REG03': 0.50, 'REG04': 0.15, 'REG05': 0.20, 'REG01': 0.10, 'REG02': 0.05},
}

# Customer name pools by channel
CUSTOMER_NAMES = {
    'CH01': [
        'Đại lý Minh Phát', 'Tạp hóa Hồng Phúc', 'Đại lý Thành Công', 'NPP Phương Nam',
        'Đại lý Bảo Long', 'Tạp hóa Thanh Hà', 'NPP Đại Phong', 'Đại lý Quốc Hưng',
        'Tạp hóa Ngọc Lan', 'NPP Hoàng Gia', 'Đại lý Tân Phát', 'Tạp hóa Kim Liên',
        'NPP Trường An', 'Đại lý Việt Hưng', 'Tạp hóa Phú Quý',
    ],
    'CH02': [
        'Co.opmart', 'Bách Hóa Xanh', 'WinMart', 'Circle K VN', 'Big C / GO!',
        'Lotte Mart', 'AEON VN', 'Mega Market', 'Saigon Co.op', 'Family Mart VN',
    ],
    'CH03': [
        'Cambodia Dist. Co.', 'Prague Trading s.r.o.', 'Warsaw Import Sp.', 'Moscow Food LLC',
        'Cuba Import Agency', 'Phnom Penh Foods', 'EurAsia Trading GmbH',
    ],
    'CH04': [
        'Shopee Mall', 'Lazada Official Store', 'TikTok Shop', 'Tiki Official', 'Sendo',
    ],
}

# Wastage rates by factory (base, before anomaly)
FACTORY_WASTAGE = {'F01': 0.022, 'F02': 0.025, 'F03': 0.030, 'F04': 0.028, 'F05': 0.032}

# Factory COGS multiplier: adjusts product base cost to create margin differentiation
# Base product cost/price ratio ~0.81. These multipliers create target margins per factory.
FACTORY_COGS_MULT = {
    'F01': 0.945,  # Lower COGS → margin ~23%
    'F02': 0.967,  # Slightly lower → margin ~21%
    'F03': 1.058,  # Higher COGS → margin ~14%
    'F04': 1.115,  # Much higher COGS (low utilization) → margin ~8% base, ~5% with anomaly
    'F05': 1.030,  # Slightly higher → margin ~16%
}


def month_offset(d):
    """Months since Jan 2024"""
    return (d.year - 2024) * 12 + (d.month - 1)

def growth_factor(mo):
    """YoY +5% linear"""
    return 1.0 + 0.05 * (mo / 12.0)

def noise(low=0.88, high=1.12):
    return random.uniform(low, high)

def get_month_range(year, month):
    """Return (first_day, last_day, num_days) for a month"""
    first = date(year, month, 1)
    if month == 12:
        last = date(year, 12, 31)
    else:
        last = date(year, month + 1, 1) - timedelta(days=1)
    return first, last, (last - first).days + 1


def generate_production_orders(cursor, products_list):
    """Generate production_orders for 18 months"""
    print("  Generating production_orders...")

    # Build product lookup by category
    products_by_cat = {}
    for p in products_list:
        cat = p[2]
        if cat not in products_by_cat:
            products_by_cat[cat] = []
        products_by_cat[cat].append((p[0], p[10]))  # (product_id, popularity_weight)

    # Normalize popularity weights per category
    for cat in products_by_cat:
        total_w = sum(w for _, w in products_by_cat[cat])
        products_by_cat[cat] = [(pid, w/total_w) for pid, w in products_by_cat[cat]]

    def pick_product(category_id):
        prods = products_by_cat.get(category_id, [])
        if not prods:
            return None
        pids, weights = zip(*prods)
        return random.choices(pids, weights=weights, k=1)[0]

    # Map product_type to categories for each factory+line
    def get_line_categories(factory_id, line_id):
        pt = LINE_PRODUCT_TYPE[line_id]
        base_cats = PRODUCT_TYPE_CATEGORIES[pt]
        fmix = FACTORY_PRODUCT_MIX[factory_id]
        # Filter to categories that this factory actually produces
        cats_with_weight = [(c, fmix.get(c, 0)) for c in base_cats if fmix.get(c, 0) > 0]
        if not cats_with_weight:
            return [(base_cats[0], 1.0)]
        total = sum(w for _, w in cats_with_weight)
        return [(c, w/total) for c, w in cats_with_weight]

    rows = []
    shifts = ['ca_1', 'ca_2']  # Most lines run 2 shifts; some busy ones 3

    current = START_DATE
    while current <= END_DATE:
        mo = month_offset(current)
        month_idx = current.month - 1
        dow = current.weekday()
        base_seasonal = MONTHLY_SEASONALITY[month_idx]
        weekly_mult = WEEKLY_PATTERN[dow]
        gf = growth_factor(mo)

        for fid in ['F01', 'F02', 'F03', 'F04', 'F05']:
            util = FACTORY_UTILIZATION[fid]

            # Anomaly 1: F04 utilization declining from Feb 2025
            if fid == 'F04' and current >= date(2025, 2, 1):
                months_from_feb = (current.year - 2025) * 12 + current.month - 2
                util = max(0.30, util - 0.02 * months_from_feb)

            for line_id in FACTORY_LINES[fid]:
                # Check if line is commissioned
                comm_date = LINE_COMMISSIONED.get(line_id)
                if comm_date and current < comm_date:
                    continue

                cap_per_hour = LINE_CAPACITY_PER_HOUR[line_id]
                hours_per_shift = 8
                line_cats = get_line_categories(fid, line_id)

                for shift in shifts:
                    # Pick category for this shift
                    cat_ids, cat_weights = zip(*line_cats)
                    cat_id = random.choices(cat_ids, weights=cat_weights, k=1)[0]

                    product_id = pick_product(cat_id)
                    if not product_id:
                        continue

                    cat_seasonal = CATEGORY_SEASONALITY[cat_id][month_idx]

                    planned = int(cap_per_hour * hours_per_shift * util * base_seasonal * cat_seasonal * gf)
                    actual = int(planned * noise(0.92, 1.02))

                    # Wastage
                    wastage_rate = FACTORY_WASTAGE[fid]

                    # Anomaly 3: L01-04 wastage spike May-Jun 2025
                    if line_id == 'L01-04' and current >= date(2025, 5, 1):
                        wastage_rate = 0.04
                    elif line_id == 'L01-04':
                        wastage_rate = 0.025  # New line, slightly higher

                    wastage = int(actual * wastage_rate)

                    # Material usage: ~0.08 kg per pack (75g pack + waste)
                    material_kg = round(actual * 0.082 * noise(0.97, 1.03), 2)
                    labor_hrs = round(hours_per_shift * random.uniform(8, 15), 2)
                    energy = round(actual * 0.0015 * noise(0.95, 1.05), 2)
                    gas = round(actual * 0.0008 * noise(0.95, 1.05), 2)
                    quality_rate = round(random.uniform(96.0, 99.5), 2)

                    rows.append((
                        fid, line_id, product_id, current.isoformat(), shift,
                        planned, actual, wastage,
                        material_kg, labor_hrs, energy, gas, quality_rate
                    ))

        current += timedelta(days=1)

    # Batch insert
    batch_size = 5000
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i+batch_size]
        cursor.executemany("""
            INSERT INTO production_orders
            (factory_id, line_id, product_id, production_date, shift,
             planned_qty_packs, actual_qty_packs, wastage_qty_packs,
             material_used_kg, labor_hours, energy_kwh, gas_m3, quality_pass_rate)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, batch)

    print(f"    production_orders: {len(rows)} rows")
    return len(rows)


def generate_material_purchases(cursor):
    """Generate material purchase records: ~3 purchases/factory/material/month"""
    print("  Generating material_purchases...")

    # Suppliers by material type
    suppliers_by_mat = {
        'MAT01': ['SUP01', 'SUP02', 'SUP09'],
        'MAT02': ['SUP03', 'SUP04', 'SUP10'],
        'MAT03': ['SUP05', 'SUP06', 'SUP11'],
        'MAT04': ['SUP07', 'SUP08', 'SUP12'],
        'MAT05': ['SUP13', 'SUP14'],
    }

    # Base prices (Jan 2024)
    base_prices = {
        'MAT01': 9500,   # VND/kg, wheat
        'MAT02': 19000,  # VND/kg, palm oil
        'MAT03': 35000,  # VND/kg, seasoning
        'MAT04': 1200,   # VND/unit, packaging
        'MAT05': 2800,   # VND/kWh_eq, energy
    }

    # Monthly price increments (Anomaly 4: imported materials rising)
    price_increment = {
        'MAT01': 100,   # +100 VND/kg/month → 9500 → 11200 in 17 months
        'MAT02': 206,   # +206 VND/kg/month → 19000 → 22500
        'MAT03': 50,    # mild increase
        'MAT04': 15,    # mild
        'MAT05': 30,    # mild
    }

    # Monthly purchase volume proportional to factory output (tons)
    factory_monthly_volume = {
        'F01': {'MAT01': 4200, 'MAT02': 1900, 'MAT03': 600, 'MAT04': 500, 'MAT05': 400},
        'F02': {'MAT01': 4800, 'MAT02': 2100, 'MAT03': 680, 'MAT04': 570, 'MAT05': 450},
        'F03': {'MAT01': 2200, 'MAT02': 950,  'MAT03': 310, 'MAT04': 260, 'MAT05': 210},
        'F04': {'MAT01': 650,  'MAT02': 280,  'MAT03': 90,  'MAT04': 76,  'MAT05': 60},
        'F05': {'MAT01': 880,  'MAT02': 390,  'MAT03': 125, 'MAT04': 105, 'MAT05': 85},
    }

    rows = []
    current_month = date(2024, 1, 1)
    while current_month <= date(2025, 6, 1):
        mo = month_offset(current_month)
        seasonal = MONTHLY_SEASONALITY[current_month.month - 1]

        for fid in ['F01', 'F02', 'F03', 'F04', 'F05']:
            for mat_id in ['MAT01', 'MAT02', 'MAT03', 'MAT04', 'MAT05']:
                base_vol = factory_monthly_volume[fid][mat_id]
                base_price = base_prices[mat_id] + price_increment[mat_id] * mo

                num_purchases = random.randint(2, 4)

                for p_idx in range(num_purchases):
                    # Purchase date spread across month
                    day = min(28, random.randint(1, 28))
                    purchase_date = date(current_month.year, current_month.month, day)

                    vol_share = random.uniform(0.2, 0.5) if num_purchases > 1 else 1.0
                    qty = round(base_vol * seasonal * growth_factor(mo) * vol_share * noise(0.90, 1.10), 2)

                    # Price with noise
                    unit_price = round(base_price * noise(0.97, 1.03), 2)

                    # Anomaly 2: F03 pays 8% more for wheat in Apr-Jun 2025
                    if fid == 'F03' and mat_id == 'MAT01' and current_month >= date(2025, 4, 1):
                        unit_price = round(unit_price * 1.08, 2)

                    total = round(qty * unit_price)

                    # Pick supplier
                    sup_list = suppliers_by_mat[mat_id]
                    supplier = sup_list[0] if random.random() < 0.6 else random.choice(sup_list[1:])

                    delivery_date = purchase_date + timedelta(days=random.randint(3, 14))
                    grade = random.choices(['A', 'A', 'A', 'B', 'B', 'C'], weights=[40, 25, 15, 10, 7, 3])[0]

                    rows.append((
                        fid, mat_id, supplier, purchase_date.isoformat(),
                        qty, unit_price, total,
                        delivery_date.isoformat(), grade
                    ))

        # Next month
        if current_month.month == 12:
            current_month = date(current_month.year + 1, 1, 1)
        else:
            current_month = date(current_month.year, current_month.month + 1, 1)

    cursor.executemany("""
        INSERT INTO material_purchases
        (factory_id, material_type_id, supplier_id, purchase_date,
         quantity_kg, unit_price_vnd, total_amount_vnd, delivery_date, quality_grade)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, rows)
    print(f"    material_purchases: {len(rows)} rows")
    return len(rows)


def generate_cost_allocations(cursor):
    """Generate cost allocations: 5 factories × 6 categories × 18 months"""
    print("  Generating cost_allocations...")

    # Monthly COGS target per factory (billions VND) - derived from revenue and margin
    # Revenue shares: F01~33%, F02~35%, F03~17%, F04~5%, F05~10%
    # Monthly revenue ~483 billion → COGS ~80% = ~387 billion
    factory_monthly_cogs_base = {
        'F01': 127e9,  # ~33% of 387B, margin ~23% → COGS = revenue * 0.77
        'F02': 135e9,  # ~35%
        'F03':  70e9,  # ~17%, margin ~14% → higher COGS ratio
        'F04':  22e9,  # ~5%, margin ~5-8% → very high COGS ratio
        'F05':  33e9,  # ~10%, margin ~16%
    }

    # Cost category shares differ by factory (key anomaly: F04 high fixed costs)
    factory_cost_shares = {
        'F01': {'CC01': 0.72, 'CC02': 0.07, 'CC03': 0.08, 'CC04': 0.06, 'CC05': 0.04, 'CC06': 0.03},
        'F02': {'CC01': 0.70, 'CC02': 0.07, 'CC03': 0.08, 'CC04': 0.07, 'CC05': 0.05, 'CC06': 0.03},
        'F03': {'CC01': 0.68, 'CC02': 0.07, 'CC03': 0.08, 'CC04': 0.08, 'CC05': 0.05, 'CC06': 0.04},
        'F04': {'CC01': 0.55, 'CC02': 0.07, 'CC03': 0.08, 'CC04': 0.18, 'CC05': 0.08, 'CC06': 0.04},  # High fixed!
        'F05': {'CC01': 0.65, 'CC02': 0.08, 'CC03': 0.09, 'CC04': 0.09, 'CC05': 0.05, 'CC06': 0.04},
    }

    rows = []
    current_month = date(2024, 1, 1)
    while current_month <= date(2025, 6, 1):
        mo = month_offset(current_month)
        seasonal = MONTHLY_SEASONALITY[current_month.month - 1]
        gf = growth_factor(mo)

        # Material cost inflation (Anomaly 4)
        mat_inflation = 1.0 + 0.006 * mo  # ~0.6% per month for materials

        for fid in ['F01', 'F02', 'F03', 'F04', 'F05']:
            base_cogs = factory_monthly_cogs_base[fid]
            shares = factory_cost_shares[fid]

            for cc_id in ['CC01', 'CC02', 'CC03', 'CC04', 'CC05', 'CC06']:
                share = shares[cc_id]
                is_fixed = cc_id in ('CC04', 'CC05')

                if is_fixed:
                    # Fixed costs don't vary with volume
                    amount = base_cogs * share * gf * noise(0.97, 1.03)
                elif cc_id == 'CC01':
                    # Materials: affected by price inflation
                    amount = base_cogs * share * seasonal * gf * mat_inflation * noise(0.95, 1.05)
                else:
                    # Variable costs scale with volume
                    amount = base_cogs * share * seasonal * gf * noise(0.95, 1.05)

                rows.append((
                    fid, cc_id, current_month.isoformat(), round(amount), None
                ))

        if current_month.month == 12:
            current_month = date(current_month.year + 1, 1, 1)
        else:
            current_month = date(current_month.year, current_month.month + 1, 1)

    cursor.executemany("""
        INSERT INTO cost_allocations (factory_id, cost_category_id, month_date, amount_vnd, notes)
        VALUES (%s,%s,%s,%s,%s)
    """, rows)
    print(f"    cost_allocations: {len(rows)} rows")
    return len(rows)


def generate_sales_orders(cursor, products_list):
    """Generate sales_orders and sales_order_items"""
    print("  Generating sales_orders + sales_order_items...")

    # Product lookup
    product_info = {}
    products_by_cat = {}
    for p in products_list:
        pid, pname, cat, brand, flavor, weight, price, cost, is_exp, launch_yr, pop_w = p
        product_info[pid] = {
            'category_id': cat, 'unit_price': float(price),
            'cost_per_pack': float(cost), 'is_export': is_exp, 'popularity': float(pop_w)
        }
        if cat not in products_by_cat:
            products_by_cat[cat] = []
        products_by_cat[cat].append(pid)

    # Pre-compute category total popularity for weighted selection
    cat_pop = {}
    for cat, pids in products_by_cat.items():
        cat_pop[cat] = [(pid, product_info[pid]['popularity']) for pid in pids]

    def pick_products_for_order(cat_weights, num_items):
        """Pick num_items products weighted by category mix and popularity"""
        selected = []
        for _ in range(num_items):
            cats, cw = zip(*cat_weights)
            cat = random.choices(cats, weights=cw, k=1)[0]
            pids, pops = zip(*cat_pop[cat])
            pid = random.choices(pids, weights=pops, k=1)[0]
            selected.append(pid)
        return selected

    # Target: ~5800B VND / year 2024 → ~483B/month
    # Per factory monthly revenue targets (VND)
    factory_monthly_revenue = {
        'F01': 160e9,  # ~33%
        'F02': 170e9,  # ~35%
        'F03':  82e9,  # ~17%
        'F04':  23e9,  # ~5%
        'F05':  48e9,  # ~10%
    }

    order_rows = []
    item_rows = []
    order_id_counter = 0

    current = START_DATE
    while current <= END_DATE:
        mo = month_offset(current)
        month_idx = current.month - 1
        dow = current.weekday()
        base_seasonal = MONTHLY_SEASONALITY[month_idx]
        weekly_mult = WEEKLY_PATTERN[dow]
        gf = growth_factor(mo)

        # Price inflation (selling price): +5% over 18 months
        price_inflation = 1.0 + 0.005 * mo / 1.5  # slow price rise

        for fid in ['F01', 'F02', 'F03', 'F04', 'F05']:
            monthly_target = factory_monthly_revenue[fid]
            daily_target = monthly_target / 30.0 * base_seasonal * weekly_mult * gf

            # Number of orders per day
            if fid in ('F01', 'F02'):
                num_orders = random.randint(12, 20)
            elif fid == 'F03':
                num_orders = random.randint(8, 14)
            elif fid == 'F04':
                num_orders = random.randint(4, 8)
            else:
                num_orders = random.randint(5, 10)

            avg_order_value = daily_target / num_orders
            cat_weights = [(cat, share) for cat, share in FACTORY_PRODUCT_MIX[fid].items()]

            # Region weights for this factory
            region_items = list(FACTORY_REGIONS[fid].items())
            region_ids, region_wts = zip(*region_items)

            for _ in range(num_orders):
                order_id_counter += 1

                # Channel selection
                ch_ids = list(CHANNEL_WEIGHTS.keys())
                ch_wts = list(CHANNEL_WEIGHTS.values())
                channel = random.choices(ch_ids, weights=ch_wts, k=1)[0]

                # Region selection
                region = random.choices(region_ids, weights=region_wts, k=1)[0]

                # Export channel forces export region
                if channel == 'CH03':
                    region = 'REG05'
                elif region == 'REG05' and channel != 'CH03':
                    region = random.choices(
                        [r for r in region_ids if r != 'REG05'],
                        weights=[w for r, w in region_items if r != 'REG05'],
                        k=1
                    )[0]

                # Customer name
                customer = random.choice(CUSTOMER_NAMES.get(channel, ['Khách lẻ']))

                # Items per order
                num_items = random.randint(2, 5)
                selected_products = pick_products_for_order(cat_weights, num_items)

                total_qty = 0
                total_rev = 0
                total_cogs = 0
                items = []

                for pid in selected_products:
                    info = product_info[pid]

                    # Order quantity: log-normal, median ~15000 packs
                    qty = int(math.exp(random.gauss(math.log(15000), 0.6)))
                    qty = max(2000, min(80000, qty))

                    # Price adjustments
                    unit_price = info['unit_price'] * price_inflation
                    if channel == 'CH02':
                        unit_price *= 0.98  # MT discount
                    elif channel == 'CH03':
                        unit_price *= 0.90  # Export discount
                    unit_price = round(unit_price)

                    # COGS: factory-specific multiplier + material cost inflation over time
                    cost_inflation = 1.0 + 0.006 * mo  # ~0.6%/month → ~10.8% over 18 months
                    factory_cost_mult = FACTORY_COGS_MULT[fid]
                    # F04 additional margin erosion from Feb 2025 (Anomaly 1)
                    if fid == 'F04' and current >= date(2025, 2, 1):
                        months_from_feb = (current.year - 2025) * 12 + current.month - 2
                        factory_cost_mult += 0.006 * months_from_feb  # COGS creep
                    unit_cost = round(info['cost_per_pack'] * cost_inflation * factory_cost_mult)

                    line_rev = qty * unit_price
                    line_cogs = qty * unit_cost

                    items.append((pid, qty, unit_price, line_rev, line_cogs))
                    total_qty += qty
                    total_rev += line_rev
                    total_cogs += line_cogs

                order_rows.append((
                    current.isoformat(), fid, channel, region,
                    customer, total_qty, total_rev, total_cogs
                ))

                for pid, qty, uprice, lrev, lcogs in items:
                    item_rows.append((
                        order_id_counter, pid, qty, uprice, lrev, lcogs
                    ))

        current += timedelta(days=1)

    # Batch insert orders
    print(f"    Inserting {len(order_rows)} sales_orders...")
    batch_size = 5000
    for i in range(0, len(order_rows), batch_size):
        batch = order_rows[i:i+batch_size]
        cursor.executemany("""
            INSERT INTO sales_orders
            (order_date, factory_id, channel_id, region_id,
             customer_name, total_quantity_packs, total_revenue_vnd, total_cogs_vnd)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, batch)

    # Batch insert items
    print(f"    Inserting {len(item_rows)} sales_order_items...")
    for i in range(0, len(item_rows), batch_size):
        batch = item_rows[i:i+batch_size]
        cursor.executemany("""
            INSERT INTO sales_order_items
            (order_id, product_id, quantity_packs, unit_price_vnd, line_revenue_vnd, line_cogs_vnd)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, batch)

    print(f"    sales_orders: {len(order_rows)} rows")
    print(f"    sales_order_items: {len(item_rows)} rows")
    return len(order_rows), len(item_rows)


def generate_metadata(cursor):
    """Insert metadata tables"""
    print("  Generating metadata...")

    # _meta_tables
    meta_tables = [
        ('factories', 'Danh sách 5 nhà máy sản xuất của Asia Foods, phân bổ 3 miền Bắc-Trung-Nam',
         'List of 5 Asia Foods manufacturing plants across 3 regions',
         'Mỗi nhà máy có công suất thiết kế, vị trí, và vai trò riêng. An Phú là trụ sở chính, Nam Tân Uyên mới nhất, Gò Vấp sản xuất dòng đặc biệt.', 5),
        ('production_lines', 'Dây chuyền sản xuất tại mỗi nhà máy, mỗi dây chuyền chuyên 1 loại sản phẩm',
         'Production lines per factory, each specialized for one product type',
         'Mỗi dây chuyền có công suất riêng. L01-04 là dây chuyền mì ly mới tại An Phú (commissioned 2025-04-15).', 16),
        ('product_categories', 'Phân loại sản phẩm: Mì gói, Mì ly, Cháo, JOMO, Phở/HT, Mì Trứng Vàng & Mộc Việt',
         'Product categories with margin profiles and volume shares',
         'Cháo margin cao nhất (~30%), Mì gói volume lớn nhất (~55%). JOMO là dòng trung cấp.', 6),
        ('products', 'Danh mục ~50 SKU sản phẩm, bao gồm tất cả dòng mì-cháo-phở của Asia Foods',
         '~50 SKUs with Pareto-distributed popularity weights',
         'Top 20% SKU chiếm ~80% doanh số. Mì Gấu Đỏ Tôm Chua Cay là SKU bán chạy nhất.', 50),
        ('material_types', 'Loại nguyên liệu đầu vào: bột mì, dầu cọ, gia vị, bao bì, năng lượng',
         'Raw material types with import status and COGS share',
         'Bột mì (40% COGS, nhập Úc) và dầu cọ (18% COGS, nhập Indonesia) là hai nguyên liệu biến động giá mạnh nhất.', 5),
        ('suppliers', 'Nhà cung cấp nguyên liệu, bao gồm cả nhập khẩu và nội địa',
         'Suppliers for raw materials', 'Interflour Vietnam là NCC bột mì chính, Bunge là NCC dầu cọ chính.', 14),
        ('sales_channels', 'Kênh phân phối: GT (tạp hóa), MT (siêu thị), Xuất khẩu, Online',
         'Distribution channels', 'GT chiếm 60% doanh thu, là kênh mạnh nhất của Gấu Đỏ ở nông thôn.', 4),
        ('regions', 'Khu vực thị trường: Miền Bắc, Miền Trung, Miền Nam, Tây Nam Bộ, Xuất khẩu',
         'Market regions', 'Miền Nam 32% doanh thu (lớn nhất). Xuất khẩu chủ yếu sang Cambodia, Đông Âu.', 5),
        ('cost_categories', 'Phân loại chi phí sản xuất: nguyên liệu, nhân công, năng lượng, khấu hao, khác',
         'Manufacturing cost categories', 'Nguyên vật liệu chiếm ~70% COGS. Khấu hao là chi phí cố định lớn nhất.', 6),
        ('material_purchases', 'Đơn mua nguyên liệu — track giá mua theo thời gian, nhà máy, NCC',
         'Material purchase orders tracking price over time',
         'Dùng phân tích procurement efficiency giữa các nhà máy. Giá bột mì tăng ~18% trong 18 tháng.', 1350),
        ('production_orders', 'Lệnh sản xuất hàng ngày — 1 dòng = 1 ca sản xuất trên 1 dây chuyền',
         'Daily production orders per shift per line',
         'Track input/output/wastage. Dùng tính capacity utilization, wastage rate, labor productivity.', 28000),
        ('cost_allocations', 'Phân bổ chi phí sản xuất theo nhà máy × tháng × loại chi phí',
         'Monthly cost allocations by factory and category',
         'Dùng breakdown cost structure. NM Đà Nẵng có tỷ trọng chi phí cố định cao do utilization thấp.', 540),
        ('sales_orders', 'Đơn bán hàng tổng hợp — phân tích doanh thu theo kênh/vùng/nhà máy',
         'Sales orders with revenue and COGS',
         'Grain: 1 đơn hàng. Cross với factories, channels, regions để phân tích đa chiều.', 40000),
        ('sales_order_items', 'Chi tiết line item trong đơn bán hàng — 1 dòng = 1 SKU trong 1 đơn',
         'Line items in sales orders',
         'Drill-down từ sales_orders để phân tích theo từng SKU cụ thể.', 150000),
    ]
    cursor.executemany(
        "INSERT INTO _meta_tables VALUES (%s,%s,%s,%s,%s)", meta_tables
    )

    # _meta_kpi
    kpis = [
        ('Gross Margin %',
         "ROUND((SUM(total_revenue_vnd) - SUM(total_cogs_vnd)) / SUM(total_revenue_vnd) * 100, 1)",
         'Biên lợi nhuận gộp = (Doanh thu - Giá vốn) / Doanh thu × 100. Target toàn hệ thống ~20%.',
         'Câu 1, 2, 5'),
        ('Capacity Utilization %',
         "ROUND(SUM(actual_qty_packs) / (designed_capacity_million_packs_month * 1000000 / 30 * COUNT(DISTINCT production_date)) * 100, 1)",
         'Tỷ lệ sử dụng công suất = Sản lượng thực tế / Công suất thiết kế × 100.',
         'Câu 2, 4, 5'),
        ('Wastage Rate %',
         "ROUND(SUM(wastage_qty_packs) / (SUM(actual_qty_packs) + SUM(wastage_qty_packs)) * 100, 2)",
         'Tỷ lệ hao hụt = Số lượng phế phẩm / (Sản lượng + Phế phẩm) × 100.',
         'Câu 4, 5'),
        ('Labor Productivity',
         "ROUND(SUM(actual_qty_packs) / SUM(labor_hours), 0)",
         'Năng suất lao động = Sản lượng / Giờ công. Đơn vị: gói/giờ công.',
         'Câu 4'),
        ('Material Cost per Million Packs',
         "ROUND(SUM(total_amount_vnd) / (SUM(quantity_kg) / avg_kg_per_million_packs) / 1e6, 0)",
         'Chi phí nguyên liệu trên 1 triệu gói sản phẩm.',
         'Câu 3, 5'),
        ('Revenue per Factory per Month',
         "SUM(total_revenue_vnd) GROUP BY factory_id, DATE_FORMAT(order_date, '%Y-%m')",
         'Doanh thu theo nhà máy theo tháng.',
         'Câu 1'),
    ]
    cursor.executemany(
        "INSERT INTO _meta_kpi VALUES (%s,%s,%s,%s)", kpis
    )

    # _meta_glossary
    glossary = [
        ('Biên lợi nhuận gộp', 'Gross Margin', 'Tỷ lệ phần trăm lợi nhuận gộp trên doanh thu. Gross Margin % = (Revenue - COGS) / Revenue × 100.', 'sales_orders'),
        ('Giá vốn hàng bán', 'COGS', 'Chi phí trực tiếp sản xuất sản phẩm, bao gồm nguyên liệu, nhân công, năng lượng, khấu hao.', 'cost_allocations'),
        ('Công suất thiết kế', 'Designed Capacity', 'Sản lượng tối đa mà nhà máy có thể sản xuất, đơn vị: triệu gói/tháng.', 'factories'),
        ('Tỷ lệ hao hụt', 'Wastage Rate', 'Phần trăm sản phẩm bị loại trong quá trình sản xuất do lỗi chất lượng.', 'production_orders'),
        ('Kênh truyền thống (GT)', 'General Trade', 'Hệ thống phân phối qua tạp hóa, đại lý, chợ truyền thống. Chiếm ~60% doanh thu.', 'sales_channels'),
        ('Kênh hiện đại (MT)', 'Modern Trade', 'Hệ thống siêu thị, cửa hàng tiện lợi: Co.opmart, Bách Hóa Xanh, WinMart, Circle K.', 'sales_channels'),
        ('ASP', 'Average Selling Price', 'Giá bán bình quân trên mỗi đơn vị sản phẩm (VND/gói).', 'sales_order_items'),
        ('Năng suất lao động', 'Labor Productivity', 'Số gói sản phẩm sản xuất trên mỗi giờ công lao động.', 'production_orders'),
        ('NVL nhập khẩu', 'Imported Raw Materials', 'Nguyên vật liệu nhập từ nước ngoài: bột mì (Úc), dầu cọ (Indonesia). Chiếm ~58% COGS.', 'material_purchases'),
        ('Phân khúc bình dân', 'Value Segment', 'Sản phẩm giá 1.500-3.500 VND/gói, phục vụ khách hàng nhạy giá. Gấu Đỏ là thương hiệu chủ lực.', 'product_categories'),
    ]
    cursor.executemany(
        "INSERT INTO _meta_glossary VALUES (%s,%s,%s,%s)", glossary
    )

    # _meta_columns (key columns only)
    meta_cols = [
        ('factories', 'factory_id', 'VARCHAR(3)', 'Mã nhà máy', 'Factory ID', None, 'F01, F02, F03, F04, F05'),
        ('factories', 'designed_capacity_million_packs_month', 'DECIMAL(10,1)', 'Công suất thiết kế', 'Designed capacity', 'triệu gói/tháng', '105.0, 130.0, 65.0, 35.0, 25.0'),
        ('production_orders', 'actual_qty_packs', 'INT', 'Sản lượng thực tế', 'Actual output', 'gói', '150000, 200000'),
        ('production_orders', 'wastage_qty_packs', 'INT', 'Số lượng hao hụt/phế phẩm', 'Wastage quantity', 'gói', '3000, 5000'),
        ('material_purchases', 'unit_price_vnd', 'DECIMAL(12,2)', 'Đơn giá mua nguyên liệu', 'Unit purchase price', 'VND/kg', '9500, 11200'),
        ('cost_allocations', 'amount_vnd', 'DECIMAL(15,0)', 'Số tiền chi phí phân bổ', 'Cost amount', 'VND', '80000000000'),
        ('sales_orders', 'total_revenue_vnd', 'DECIMAL(15,0)', 'Tổng doanh thu đơn hàng', 'Order revenue', 'VND', '250000000'),
        ('sales_orders', 'total_cogs_vnd', 'DECIMAL(15,0)', 'Tổng giá vốn đơn hàng', 'Order COGS', 'VND', '200000000'),
        ('sales_order_items', 'unit_price_vnd', 'DECIMAL(12,0)', 'Đơn giá bán sản phẩm', 'Selling unit price', 'VND/gói', '3500, 7000, 5500'),
        ('products', 'popularity_weight', 'DECIMAL(5,3)', 'Trọng số phổ biến (Pareto 80/20)', 'Popularity weight', None, '1.000, 0.500, 0.100'),
    ]
    cursor.executemany(
        "INSERT INTO _meta_columns (table_name, column_name, data_type, description_vi, description_en, unit, example_values) VALUES (%s,%s,%s,%s,%s,%s,%s)",
        meta_cols
    )

    print(f"    _meta_tables: {len(meta_tables)} rows")
    print(f"    _meta_kpi: {len(kpis)} rows")
    print(f"    _meta_glossary: {len(glossary)} rows")
    print(f"    _meta_columns: {len(meta_cols)} rows")


# ============================================================
# MAIN
# ============================================================
def main():
    conn = get_conn()
    cursor = conn.cursor()

    print("=" * 60)
    print("PHASE A: Creating Schema")
    print("=" * 60)
    create_schema(cursor)
    conn.commit()

    print("\n" + "=" * 60)
    print("PHASE B: Inserting Master Data")
    print("=" * 60)
    products_list, lines_list = insert_master_data(cursor)
    conn.commit()

    print("\n" + "=" * 60)
    print("PHASE C: Generating Transaction Data")
    print("=" * 60)
    n_prod = generate_production_orders(cursor, products_list)
    conn.commit()

    n_purch = generate_material_purchases(cursor)
    conn.commit()

    n_cost = generate_cost_allocations(cursor)
    conn.commit()

    n_sales, n_items = generate_sales_orders(cursor, products_list)
    conn.commit()

    generate_metadata(cursor)
    conn.commit()

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  production_orders: {n_prod}")
    print(f"  material_purchases: {n_purch}")
    print(f"  cost_allocations: {n_cost}")
    print(f"  sales_orders: {n_sales}")
    print(f"  sales_order_items: {n_items}")
    print(f"  Total: ~{n_prod + n_purch + n_cost + n_sales + n_items} rows")

    cursor.close()
    conn.close()
    print("\nDone!")

if __name__ == '__main__':
    main()
