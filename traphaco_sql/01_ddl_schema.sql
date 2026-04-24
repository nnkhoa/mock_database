-- ============================================================
-- 01_ddl_schema.sql
-- Database: traphaco_demo
-- Traphaco Demo — CEO persona (Board pitch, Mirae Asset context)
-- Schema: 9 dimension + 6 fact + 4 metadata = 19 tables
-- ============================================================

DROP DATABASE IF EXISTS `traphaco_demo`;
CREATE DATABASE `traphaco_demo` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `traphaco_demo`;

-- ----- DIMENSIONS -----

CREATE TABLE `dim_calendar` (
  `date`           DATE PRIMARY KEY COMMENT 'Ngày (PK)',
  `year`           SMALLINT NOT NULL,
  `quarter`        TINYINT  NOT NULL,
  `month`          TINYINT  NOT NULL,
  `week_of_year`   TINYINT  NOT NULL,
  `day_of_month`   TINYINT  NOT NULL,
  `day_of_week`    TINYINT  NOT NULL COMMENT '0=Mon ... 6=Sun',
  `is_weekend`     TINYINT(1) NOT NULL DEFAULT 0,
  `is_holiday`     TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'Ngày nghỉ lễ VN',
  `is_tet`         TINYINT(1) NOT NULL DEFAULT 0 COMMENT '7 ngày quanh mùng 1 Tết âm',
  `tet_offset`     SMALLINT  NULL COMMENT 'Số ngày tính từ mùng 1 Tết (âm=trước, dương=sau)',
  INDEX `idx_year_month` (`year`, `month`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Bảng lịch 2022-12 → 2025-03';

CREATE TABLE `dim_region` (
  `region_id`      TINYINT PRIMARY KEY,
  `region_name`    VARCHAR(30) NOT NULL UNIQUE COMMENT 'Miền Bắc/Trung/Nam'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `dim_branch` (
  `branch_id`       SMALLINT PRIMARY KEY,
  `branch_code`     VARCHAR(10) NOT NULL UNIQUE,
  `branch_name`     VARCHAR(100) NOT NULL COMMENT 'VD: CN Hà Nội',
  `region_id`       TINYINT  NOT NULL,
  `province`        VARCHAR(50) NOT NULL,
  `city_tier`       TINYINT  NOT NULL COMMENT '1=TP lớn, 2=TP tỉnh, 3=thị xã/huyện',
  `population_tier` VARCHAR(20) NOT NULL COMMENT 'cao/trung bình/thấp',
  `size_weight`     TINYINT  NOT NULL COMMENT 'Trọng số mô hình base volume (1-10)',
  `active_date`     DATE NOT NULL,
  FOREIGN KEY (`region_id`) REFERENCES `dim_region`(`region_id`),
  INDEX `idx_region` (`region_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='28 chi nhánh Traphaco';

CREATE TABLE `dim_raw_material` (
  `raw_material_id` SMALLINT PRIMARY KEY,
  `material_name`   VARCHAR(100) NOT NULL UNIQUE COMMENT 'Đinh lăng / Tam thất / API Ursodeoxycholic / ...',
  `material_type`   VARCHAR(50) NOT NULL COMMENT 'Dược liệu nội / API nhập khẩu / Tá dược',
  `source_country`  VARCHAR(50) NOT NULL COMMENT 'Việt Nam / Hàn Quốc / Ấn Độ / Trung Quốc / ...',
  INDEX `idx_type` (`material_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='~15 nguyên liệu chính';

CREATE TABLE `dim_product` (
  `product_id`                SMALLINT PRIMARY KEY,
  `product_code`              VARCHAR(20) NOT NULL UNIQUE,
  `product_name`              VARCHAR(200) NOT NULL,
  `brand`                     VARCHAR(100) NOT NULL,
  `category`                  VARCHAR(50) NOT NULL COMMENT 'Đông dược / Tân dược / TPCN / Mỹ phẩm / TBYT',
  `sub_category`              VARCHAR(100) NOT NULL,
  `strategic_tier`            VARCHAR(50) NOT NULL COMMENT 'Premium / Tân dược CL cao / Đông dược thường / Tân dược thường / TPCN',
  `dosage_form`               VARCHAR(50) NOT NULL COMMENT 'Viên nang / Viên nén / Nước / Kem / ...',
  `pack_size`                 VARCHAR(30) NOT NULL COMMENT 'VD: 40 viên, 100ml',
  `unit_price_vnd`            BIGINT  NOT NULL COMMENT 'Giá bán 1 hộp (VND)',
  `unit_cogs_vnd`             BIGINT  NOT NULL COMMENT 'Giá vốn 1 hộp baseline (VND)',
  `raw_material_primary`      VARCHAR(100) NOT NULL COMMENT 'Nguyên liệu chính (link dim_raw_material.material_name)',
  `raw_material_dependency_pct` DECIMAL(5,2) NOT NULL COMMENT '% giá vốn từ nguyên liệu chính (0-100)',
  `is_rx`                     TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'Thuốc kê đơn?',
  `launch_date`               DATE NOT NULL,
  `popularity_weight`         TINYINT  NOT NULL COMMENT 'Trọng số Pareto (1-100)',
  INDEX `idx_tier` (`strategic_tier`),
  INDEX `idx_category` (`category`),
  INDEX `idx_material` (`raw_material_primary`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='~130 SKU';

CREATE TABLE `dim_channel` (
  `channel_id`   TINYINT PRIMARY KEY,
  `channel_name` VARCHAR(50) NOT NULL UNIQUE COMMENT 'OTC truyền thống / OTC chuỗi / ETC / Xuất khẩu',
  `channel_type` VARCHAR(30) NOT NULL COMMENT 'OTC / ETC / EXPORT'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `dim_customer` (
  `customer_id`   INT PRIMARY KEY,
  `customer_code` VARCHAR(20) NOT NULL UNIQUE,
  `customer_name` VARCHAR(200) NOT NULL,
  `customer_type` VARCHAR(50) NOT NULL COMMENT 'nhà thuốc truyền thống / chuỗi hiện đại / bệnh viện / phòng khám / đại lý',
  `province`      VARCHAR(50) NOT NULL,
  `branch_id`     SMALLINT NOT NULL,
  `tier`          CHAR(1) NOT NULL COMMENT 'A/B/C theo doanh số',
  `chain_name`    VARCHAR(50) NULL COMMENT 'Long Châu / Pharmacity / An Khang / Trung Sơn (nếu applicable)',
  FOREIGN KEY (`branch_id`) REFERENCES `dim_branch`(`branch_id`),
  INDEX `idx_branch` (`branch_id`),
  INDEX `idx_type` (`customer_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='~500 customers';

CREATE TABLE `dim_tdv` (
  `tdv_id`    SMALLINT PRIMARY KEY,
  `full_name` VARCHAR(100) NOT NULL COMMENT 'Tên TDV tiếng Việt',
  `branch_id` SMALLINT NOT NULL,
  `region_id` TINYINT  NOT NULL,
  `hire_date` DATE NOT NULL,
  `status`    VARCHAR(20) NOT NULL DEFAULT 'active',
  `specialty` VARCHAR(30) NOT NULL COMMENT 'đông dược / tân dược / hỗn hợp',
  FOREIGN KEY (`branch_id`) REFERENCES `dim_branch`(`branch_id`),
  FOREIGN KEY (`region_id`) REFERENCES `dim_region`(`region_id`),
  INDEX `idx_branch` (`branch_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='~620 trình dược viên';

CREATE TABLE `dim_hospital` (
  `hospital_id`  SMALLINT PRIMARY KEY,
  `customer_id`  INT NULL COMMENT 'Link dim_customer (subset)',
  `hospital_name` VARCHAR(200) NOT NULL,
  `tier`         VARCHAR(30) NOT NULL COMMENT 'Trung ương / Tỉnh / Chuyên khoa tỉnh / Huyện / Tư nhân',
  `province`     VARCHAR(50) NOT NULL,
  `specialty`    VARCHAR(100) NOT NULL,
  FOREIGN KEY (`customer_id`) REFERENCES `dim_customer`(`customer_id`),
  INDEX `idx_tier` (`tier`),
  INDEX `idx_province` (`province`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='~200 bệnh viện';


-- ----- FACTS -----

CREATE TABLE `fact_sales` (
  `sale_id`             BIGINT PRIMARY KEY AUTO_INCREMENT,
  `sale_date`           DATE NOT NULL,
  `branch_id`           SMALLINT NOT NULL,
  `product_id`          SMALLINT NOT NULL,
  `customer_id`         INT NOT NULL,
  `channel_id`          TINYINT  NOT NULL,
  `tdv_id`              SMALLINT NULL,
  `quantity`            INT NOT NULL,
  `unit_price_vnd`      BIGINT NOT NULL,
  `gross_amount_vnd`    BIGINT NOT NULL COMMENT 'quantity * unit_price',
  `discount_amount_vnd` BIGINT NOT NULL DEFAULT 0,
  `net_amount_vnd`      BIGINT NOT NULL COMMENT 'gross - discount',
  `cogs_amount_vnd`     BIGINT NOT NULL,
  `gross_profit_vnd`    BIGINT NOT NULL COMMENT 'net - cogs',
  INDEX `idx_date` (`sale_date`),
  INDEX `idx_branch_date` (`branch_id`, `sale_date`),
  INDEX `idx_product_date` (`product_id`, `sale_date`),
  INDEX `idx_channel` (`channel_id`),
  INDEX `idx_customer` (`customer_id`),
  INDEX `idx_tdv` (`tdv_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Transaction-level sales';

CREATE TABLE `fact_inventory_snapshot` (
  `snapshot_id`           BIGINT PRIMARY KEY AUTO_INCREMENT,
  `snapshot_date`         DATE NOT NULL COMMENT 'Cuối mỗi tháng',
  `branch_id`             SMALLINT NOT NULL,
  `product_id`            SMALLINT NOT NULL,
  `quantity_on_hand`      INT NOT NULL,
  `avg_daily_sales_30d`   DECIMAL(12,4) NOT NULL DEFAULT 0,
  `days_on_hand`          DECIMAL(8,2) NOT NULL DEFAULT 0 COMMENT 'qty / avg_daily_sales_30d',
  INDEX `idx_date` (`snapshot_date`),
  INDEX `idx_branch_product` (`branch_id`, `product_id`, `snapshot_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Monthly inventory snapshots';

CREATE TABLE `fact_plan_actual` (
  `plan_actual_id`   INT PRIMARY KEY AUTO_INCREMENT,
  `month`            DATE NOT NULL COMMENT 'First day of month',
  `branch_id`        SMALLINT NULL COMMENT 'NULL = company-level',
  `product_id`       SMALLINT NULL COMMENT 'NULL = all products',
  `metric_type`      VARCHAR(30) NOT NULL COMMENT 'revenue / profit / cogs',
  `plan_value_vnd`   BIGINT NOT NULL,
  `actual_value_vnd` BIGINT NOT NULL,
  INDEX `idx_month` (`month`),
  INDEX `idx_branch` (`branch_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Kế hoạch vs thực tế';

CREATE TABLE `fact_tender` (
  `tender_id`           INT PRIMARY KEY AUTO_INCREMENT,
  `tender_code`         VARCHAR(30) NOT NULL UNIQUE,
  `hospital_id`         SMALLINT NOT NULL,
  `product_id`          SMALLINT NOT NULL,
  `submit_date`         DATE NOT NULL,
  `result_date`         DATE NULL,
  `contract_start_date` DATE NULL,
  `contract_end_date`   DATE NULL,
  `bid_value_vnd`       BIGINT NOT NULL,
  `contracted_quantity` INT NOT NULL,
  `status`              VARCHAR(20) NOT NULL COMMENT 'submitting / pending / won / lost',
  `tender_round`        TINYINT NOT NULL DEFAULT 1,
  FOREIGN KEY (`hospital_id`) REFERENCES `dim_hospital`(`hospital_id`),
  FOREIGN KEY (`product_id`) REFERENCES `dim_product`(`product_id`),
  INDEX `idx_status` (`status`),
  INDEX `idx_hospital` (`hospital_id`),
  INDEX `idx_product` (`product_id`),
  INDEX `idx_submit` (`submit_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Hồ sơ đấu thầu BV';

CREATE TABLE `fact_tender_delivery` (
  `delivery_id`           INT PRIMARY KEY AUTO_INCREMENT,
  `tender_id`             INT NOT NULL,
  `delivery_date`         DATE NOT NULL,
  `delivered_quantity`    INT NOT NULL,
  `delivered_amount_vnd`  BIGINT NOT NULL,
  FOREIGN KEY (`tender_id`) REFERENCES `fact_tender`(`tender_id`),
  INDEX `idx_tender` (`tender_id`),
  INDEX `idx_date` (`delivery_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Batch giao hàng tender';

CREATE TABLE `fact_raw_material_price` (
  `price_id`              INT PRIMARY KEY AUTO_INCREMENT,
  `month`                 DATE NOT NULL,
  `raw_material_id`       SMALLINT NOT NULL,
  `avg_price_vnd_per_kg`  BIGINT NOT NULL,
  `yoy_change_pct`        DECIMAL(7,2) NOT NULL DEFAULT 0,
  FOREIGN KEY (`raw_material_id`) REFERENCES `dim_raw_material`(`raw_material_id`),
  UNIQUE KEY `uq_month_material` (`month`, `raw_material_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Giá nguyên liệu theo tháng';


-- ----- METADATA -----

CREATE TABLE `_meta_tables` (
  `table_name`       VARCHAR(100) PRIMARY KEY,
  `description_vi`   VARCHAR(500),
  `description_en`   VARCHAR(500),
  `business_context` TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `_meta_columns` (
  `id`             INT AUTO_INCREMENT PRIMARY KEY,
  `table_name`     VARCHAR(100) NOT NULL,
  `column_name`    VARCHAR(100) NOT NULL,
  `data_type`      VARCHAR(50),
  `description_vi` VARCHAR(500),
  `description_en` VARCHAR(500),
  `unit`           VARCHAR(50),
  `example_values` VARCHAR(500),
  INDEX `idx_table` (`table_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `_meta_kpi` (
  `kpi_name`          VARCHAR(100) PRIMARY KEY,
  `formula_sql`       TEXT,
  `description_vi`    TEXT,
  `related_questions` TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `_meta_glossary` (
  `term_vi`    VARCHAR(100) PRIMARY KEY,
  `term_en`    VARCHAR(100),
  `definition` TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
