-- ============================================================
-- instant_noodle_demo — DDL Schema
-- Exported: 2026-04-07 20:59:00
-- ============================================================

DROP DATABASE IF EXISTS `instant_noodle_demo`;
CREATE DATABASE IF NOT EXISTS `instant_noodle_demo` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `instant_noodle_demo`;

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- Table: _meta_columns
DROP TABLE IF EXISTS `_meta_columns`;
CREATE TABLE `_meta_columns` (
  `id` int NOT NULL AUTO_INCREMENT,
  `table_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `column_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `data_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description_vi` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `description_en` text COLLATE utf8mb4_unicode_ci,
  `unit` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `example_values` text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Metadata: mo ta y nghia tung cot';

-- Table: _meta_glossary
DROP TABLE IF EXISTS `_meta_glossary`;
CREATE TABLE `_meta_glossary` (
  `term_vi` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `term_en` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `definition` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `related_table` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`term_vi`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Metadata: thuat ngu nganh mi an lien';

-- Table: _meta_kpi
DROP TABLE IF EXISTS `_meta_kpi`;
CREATE TABLE `_meta_kpi` (
  `kpi_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `formula_sql` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `description_vi` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `related_questions` text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`kpi_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Metadata: cong thuc SQL cho cac KPI';

-- Table: _meta_tables
DROP TABLE IF EXISTS `_meta_tables`;
CREATE TABLE `_meta_tables` (
  `table_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description_vi` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `description_en` text COLLATE utf8mb4_unicode_ci,
  `business_context` text COLLATE utf8mb4_unicode_ci,
  `row_count_estimate` int DEFAULT NULL,
  PRIMARY KEY (`table_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Metadata: mo ta business context tung bang';

-- Table: cost_allocations
DROP TABLE IF EXISTS `cost_allocations`;
CREATE TABLE `cost_allocations` (
  `allocation_id` int NOT NULL AUTO_INCREMENT,
  `factory_id` varchar(3) COLLATE utf8mb4_unicode_ci NOT NULL,
  `cost_category_id` varchar(5) COLLATE utf8mb4_unicode_ci NOT NULL,
  `month_date` date NOT NULL COMMENT 'Thang phan bo (ngay 1)',
  `amount_vnd` decimal(15,0) NOT NULL COMMENT 'So tien (VND)',
  `notes` text COLLATE utf8mb4_unicode_ci COMMENT 'Ghi chu',
  PRIMARY KEY (`allocation_id`),
  KEY `cost_category_id` (`cost_category_id`),
  KEY `idx_cost_factory_month` (`factory_id`,`month_date`),
  CONSTRAINT `cost_allocations_ibfk_1` FOREIGN KEY (`factory_id`) REFERENCES `factories` (`factory_id`),
  CONSTRAINT `cost_allocations_ibfk_2` FOREIGN KEY (`cost_category_id`) REFERENCES `cost_categories` (`cost_category_id`)
) ENGINE=InnoDB AUTO_INCREMENT=541 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Phan bo chi phi san xuat theo NM x thang x loai CP';

-- Table: cost_categories
DROP TABLE IF EXISTS `cost_categories`;
CREATE TABLE `cost_categories` (
  `cost_category_id` varchar(5) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Ma loai CP: CC01-CC06',
  `category_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Ten loai chi phi',
  `category_name_en` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Ten tieng Anh',
  `is_fixed` tinyint(1) DEFAULT '0' COMMENT '1 = chi phi co dinh',
  `typical_cogs_share_pct` decimal(5,2) DEFAULT NULL COMMENT 'Ty trong COGS dien hinh (%)',
  PRIMARY KEY (`cost_category_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Phan loai chi phi san xuat';

-- Table: factories
DROP TABLE IF EXISTS `factories`;
CREATE TABLE `factories` (
  `factory_id` varchar(3) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Ma nha may: F01-F05',
  `factory_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Ten nha may',
  `factory_short_name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Ten viet tat',
  `province` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Tinh/thanh pho',
  `region` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Mien: Bac/Trung/Nam',
  `area_sqm` int NOT NULL COMMENT 'Dien tich nha may (m2)',
  `year_commissioned` int NOT NULL COMMENT 'Nam dua vao hoat dong',
  `designed_capacity_million_packs_month` decimal(10,1) NOT NULL COMMENT 'Cong suat thiet ke (trieu goi/thang)',
  `num_production_lines` int NOT NULL COMMENT 'So day chuyen san xuat',
  `num_employees` int NOT NULL COMMENT 'So nhan vien',
  `status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT 'active' COMMENT 'Trang thai: active/inactive',
  PRIMARY KEY (`factory_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Danh sach 5 nha may san xuat cua Asia Foods';

-- Table: material_purchases
DROP TABLE IF EXISTS `material_purchases`;
CREATE TABLE `material_purchases` (
  `purchase_id` int NOT NULL AUTO_INCREMENT,
  `factory_id` varchar(3) COLLATE utf8mb4_unicode_ci NOT NULL,
  `material_type_id` varchar(5) COLLATE utf8mb4_unicode_ci NOT NULL,
  `supplier_id` varchar(5) COLLATE utf8mb4_unicode_ci NOT NULL,
  `purchase_date` date NOT NULL,
  `quantity_kg` decimal(12,2) NOT NULL COMMENT 'So luong (kg)',
  `unit_price_vnd` decimal(12,2) NOT NULL COMMENT 'Don gia (VND/kg)',
  `total_amount_vnd` decimal(15,0) NOT NULL COMMENT 'Tong tien (VND)',
  `delivery_date` date DEFAULT NULL COMMENT 'Ngay giao hang',
  `quality_grade` varchar(5) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Cap chat luong: A/B/C',
  PRIMARY KEY (`purchase_id`),
  KEY `supplier_id` (`supplier_id`),
  KEY `idx_purchase_factory_date` (`factory_id`,`purchase_date`),
  KEY `idx_purchase_material` (`material_type_id`,`purchase_date`),
  CONSTRAINT `material_purchases_ibfk_1` FOREIGN KEY (`factory_id`) REFERENCES `factories` (`factory_id`),
  CONSTRAINT `material_purchases_ibfk_2` FOREIGN KEY (`material_type_id`) REFERENCES `material_types` (`material_type_id`),
  CONSTRAINT `material_purchases_ibfk_3` FOREIGN KEY (`supplier_id`) REFERENCES `suppliers` (`supplier_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1342 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Don mua nguyen lieu';

-- Table: material_types
DROP TABLE IF EXISTS `material_types`;
CREATE TABLE `material_types` (
  `material_type_id` varchar(5) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Ma NL: MAT01-MAT05',
  `material_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Ten nguyen lieu',
  `material_name_en` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Ten tieng Anh',
  `unit` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Don vi: kg, lit, tan',
  `is_imported` tinyint(1) DEFAULT '0' COMMENT '1 = nhap khau',
  `import_origin` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Nguon nhap',
  `cogs_share_pct` decimal(5,2) NOT NULL COMMENT 'Ty trong trong COGS (%)',
  `price_volatility` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Muc bien dong gia: high/medium/low',
  PRIMARY KEY (`material_type_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Loai nguyen lieu dau vao';

-- Table: product_categories
DROP TABLE IF EXISTS `product_categories`;
CREATE TABLE `product_categories` (
  `category_id` varchar(5) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Ma danh muc: CAT01-CAT06',
  `category_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Ten danh muc tieng Viet',
  `category_name_en` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Ten tieng Anh',
  `price_segment` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Phan khuc gia: binh_dan, trung_cap, cao_cap',
  `avg_margin_pct` decimal(5,2) NOT NULL COMMENT 'Bien loi nhuan gop trung binh (%)',
  `volume_share_pct` decimal(5,2) NOT NULL COMMENT 'Ty trong san luong (%)',
  `description` text COLLATE utf8mb4_unicode_ci COMMENT 'Mo ta danh muc',
  PRIMARY KEY (`category_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Phan loai san pham: Mi goi, Mi ly, Chao, JOMO, Pho/HT, Khac';

-- Table: production_lines
DROP TABLE IF EXISTS `production_lines`;
CREATE TABLE `production_lines` (
  `line_id` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Ma day chuyen: L01-01, L02-01...',
  `factory_id` varchar(3) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'FK -> factories',
  `line_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Ten day chuyen',
  `product_type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Loai SP: mi_goi, mi_ly, chao, pho_hu_tieu',
  `capacity_packs_per_hour` int NOT NULL COMMENT 'Cong suat (goi/gio)',
  `commissioned_date` date NOT NULL COMMENT 'Ngay dua vao van hanh',
  `status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT 'active' COMMENT 'Trang thai',
  PRIMARY KEY (`line_id`),
  KEY `factory_id` (`factory_id`),
  CONSTRAINT `production_lines_ibfk_1` FOREIGN KEY (`factory_id`) REFERENCES `factories` (`factory_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Day chuyen san xuat tai moi nha may';

-- Table: production_orders
DROP TABLE IF EXISTS `production_orders`;
CREATE TABLE `production_orders` (
  `production_order_id` int NOT NULL AUTO_INCREMENT,
  `factory_id` varchar(3) COLLATE utf8mb4_unicode_ci NOT NULL,
  `line_id` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `product_id` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `production_date` date NOT NULL,
  `shift` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Ca san xuat: ca_1, ca_2, ca_3',
  `planned_qty_packs` int NOT NULL,
  `actual_qty_packs` int NOT NULL,
  `wastage_qty_packs` int NOT NULL DEFAULT '0',
  `material_used_kg` decimal(12,2) DEFAULT NULL COMMENT 'Nguyen lieu su dung (kg)',
  `labor_hours` decimal(8,2) DEFAULT NULL COMMENT 'Gio cong lao dong',
  `energy_kwh` decimal(10,2) DEFAULT NULL COMMENT 'Dien nang tieu thu (kWh)',
  `gas_m3` decimal(10,2) DEFAULT NULL COMMENT 'Gas tieu thu (m3)',
  `quality_pass_rate` decimal(5,2) DEFAULT NULL COMMENT 'Ty le dat chat luong (%)',
  PRIMARY KEY (`production_order_id`),
  KEY `idx_prod_factory_date` (`factory_id`,`production_date`),
  KEY `idx_prod_product_date` (`product_id`,`production_date`),
  KEY `idx_prod_line_date` (`line_id`,`production_date`),
  CONSTRAINT `production_orders_ibfk_1` FOREIGN KEY (`factory_id`) REFERENCES `factories` (`factory_id`),
  CONSTRAINT `production_orders_ibfk_2` FOREIGN KEY (`line_id`) REFERENCES `production_lines` (`line_id`),
  CONSTRAINT `production_orders_ibfk_3` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`)
) ENGINE=InnoDB AUTO_INCREMENT=16565 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Lenh san xuat hang ngay — 1 dong = 1 ca SX tren 1 day chuyen';

-- Table: products
DROP TABLE IF EXISTS `products`;
CREATE TABLE `products` (
  `product_id` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Ma SKU: SKU001-SKU050',
  `product_name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Ten san pham tieng Viet',
  `category_id` varchar(5) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'FK -> product_categories',
  `brand` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Thuong hieu',
  `flavor` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Huong vi',
  `pack_weight_g` int NOT NULL COMMENT 'Trong luong goi (gram)',
  `unit_price_vnd` decimal(12,0) NOT NULL COMMENT 'Gia ban le de xuat (VND/goi)',
  `cost_per_pack_vnd` decimal(12,0) NOT NULL COMMENT 'Gia thanh san xuat uoc tinh (VND/goi)',
  `is_export` tinyint(1) DEFAULT '0' COMMENT '1 = co xuat khau',
  `launch_year` int DEFAULT NULL COMMENT 'Nam ra mat',
  `popularity_weight` decimal(5,3) DEFAULT '1.000' COMMENT 'Trong so pho bien (Pareto): 0.001-1.000',
  `status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT 'active',
  PRIMARY KEY (`product_id`),
  KEY `category_id` (`category_id`),
  CONSTRAINT `products_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `product_categories` (`category_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Danh muc ~50 SKU san pham cua Asia Foods';

-- Table: regions
DROP TABLE IF EXISTS `regions`;
CREATE TABLE `regions` (
  `region_id` varchar(5) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Ma vung: REG01-REG05',
  `region_name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Ten khu vuc',
  `population_million` decimal(5,1) DEFAULT NULL COMMENT 'Dan so uoc tinh (trieu)',
  `revenue_share_pct` decimal(5,2) NOT NULL COMMENT 'Ty trong doanh thu (%)',
  `primary_factory_id` varchar(3) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'NM phuc vu chinh',
  PRIMARY KEY (`region_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Khu vuc thi truong';

-- Table: sales_channels
DROP TABLE IF EXISTS `sales_channels`;
CREATE TABLE `sales_channels` (
  `channel_id` varchar(5) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Ma kenh: CH01-CH04',
  `channel_name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Ten kenh ban',
  `channel_name_en` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Ten tieng Anh',
  `revenue_share_pct` decimal(5,2) NOT NULL COMMENT 'Ty trong doanh thu (%)',
  `description` text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`channel_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Kenh phan phoi: GT, MT, Xuat khau, Online';

-- Table: sales_order_items
DROP TABLE IF EXISTS `sales_order_items`;
CREATE TABLE `sales_order_items` (
  `item_id` int NOT NULL AUTO_INCREMENT,
  `order_id` int NOT NULL,
  `product_id` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `quantity_packs` int NOT NULL,
  `unit_price_vnd` decimal(12,0) NOT NULL,
  `line_revenue_vnd` decimal(15,0) NOT NULL,
  `line_cogs_vnd` decimal(15,0) NOT NULL,
  PRIMARY KEY (`item_id`),
  KEY `idx_item_product` (`product_id`),
  KEY `idx_item_order` (`order_id`),
  CONSTRAINT `sales_order_items_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `sales_orders` (`order_id`),
  CONSTRAINT `sales_order_items_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`)
) ENGINE=InnoDB AUTO_INCREMENT=108743 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Chi tiet line item trong don ban hang';

-- Table: sales_orders
DROP TABLE IF EXISTS `sales_orders`;
CREATE TABLE `sales_orders` (
  `order_id` int NOT NULL AUTO_INCREMENT,
  `order_date` date NOT NULL,
  `factory_id` varchar(3) COLLATE utf8mb4_unicode_ci NOT NULL,
  `channel_id` varchar(5) COLLATE utf8mb4_unicode_ci NOT NULL,
  `region_id` varchar(5) COLLATE utf8mb4_unicode_ci NOT NULL,
  `customer_name` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Ten khach hang/nha phan phoi',
  `total_quantity_packs` int NOT NULL,
  `total_revenue_vnd` decimal(15,0) NOT NULL,
  `total_cogs_vnd` decimal(15,0) NOT NULL,
  PRIMARY KEY (`order_id`),
  KEY `idx_sales_factory_date` (`factory_id`,`order_date`),
  KEY `idx_sales_channel_date` (`channel_id`,`order_date`),
  KEY `idx_sales_region_date` (`region_id`,`order_date`),
  CONSTRAINT `sales_orders_ibfk_1` FOREIGN KEY (`factory_id`) REFERENCES `factories` (`factory_id`),
  CONSTRAINT `sales_orders_ibfk_2` FOREIGN KEY (`channel_id`) REFERENCES `sales_channels` (`channel_id`),
  CONSTRAINT `sales_orders_ibfk_3` FOREIGN KEY (`region_id`) REFERENCES `regions` (`region_id`)
) ENGINE=InnoDB AUTO_INCREMENT=31126 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Don ban hang tong hop';

-- Table: suppliers
DROP TABLE IF EXISTS `suppliers`;
CREATE TABLE `suppliers` (
  `supplier_id` varchar(5) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Ma NCC: SUP01-SUP15',
  `supplier_name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Ten nha cung cap',
  `material_type_id` varchar(5) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'FK -> material_types',
  `country` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Quoc gia',
  `is_primary` tinyint(1) DEFAULT '0' COMMENT '1 = NCC chinh',
  PRIMARY KEY (`supplier_id`),
  KEY `material_type_id` (`material_type_id`),
  CONSTRAINT `suppliers_ibfk_1` FOREIGN KEY (`material_type_id`) REFERENCES `material_types` (`material_type_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Nha cung cap nguyen lieu';

SET FOREIGN_KEY_CHECKS = 1;
