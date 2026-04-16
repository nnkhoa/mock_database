-- ============================================================
-- 01_ddl_schema.sql
-- Database: gemadept_bi_demo
-- Gemadept BI Demo — MKT Manager persona
-- Schema: 12 data tables + 4 metadata tables
-- ============================================================

DROP DATABASE IF EXISTS `gemadept_bi_demo`;
CREATE DATABASE `gemadept_bi_demo` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `gemadept_bi_demo`;

-- ----- Dimensions -----
CREATE TABLE `ports` (
  `port_id` VARCHAR(10) PRIMARY KEY,
  `port_name` VARCHAR(100) NOT NULL,
  `port_code` VARCHAR(10) NOT NULL,
  `is_gemadept` TINYINT(1) NOT NULL DEFAULT 0,
  `region` VARCHAR(20) NOT NULL,
  `cluster` VARCHAR(30) NOT NULL,
  `port_type` VARCHAR(20) NOT NULL,
  `capacity_teu_year` INT,
  `max_dwt` INT,
  `operator_company` VARCHAR(100),
  `latitude` DECIMAL(9,4),
  `longitude` DECIMAL(9,4)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `shipping_lines` (
  `line_id` VARCHAR(10) PRIMARY KEY,
  `line_name` VARCHAR(100) NOT NULL,
  `line_code` VARCHAR(10) NOT NULL,
  `country` VARCHAR(50),
  `fleet_size_vessels` INT,
  `fleet_capacity_teu` INT,
  `global_rank` INT,
  `vietnam_presence_since` INT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `alliances` (
  `alliance_id` VARCHAR(10) PRIMARY KEY,
  `alliance_name` VARCHAR(100) NOT NULL,
  `formed_date` DATE,
  `dissolved_date` DATE,
  `combined_teu` INT,
  `market_share_pct` DECIMAL(5,2),
  `trade_focus` VARCHAR(200),
  `status` VARCHAR(20)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `alliance_membership_history` (
  `membership_id` VARCHAR(10) PRIMARY KEY,
  `line_id` VARCHAR(10) NOT NULL,
  `alliance_id` VARCHAR(10) NOT NULL,
  `from_date` DATE NOT NULL,
  `to_date` DATE,
  FOREIGN KEY (`line_id`) REFERENCES `shipping_lines`(`line_id`),
  FOREIGN KEY (`alliance_id`) REFERENCES `alliances`(`alliance_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `vessels` (
  `vessel_id` VARCHAR(10) PRIMARY KEY,
  `vessel_name` VARCHAR(100) NOT NULL,
  `imo_number` INT,
  `flag` VARCHAR(30),
  `owner_line_id` VARCHAR(10),
  `dwt` INT,
  `teu_capacity` INT,
  `length_meters` INT,
  `year_built` INT,
  `vessel_type` VARCHAR(20),
  FOREIGN KEY (`owner_line_id`) REFERENCES `shipping_lines`(`line_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `services` (
  `service_id` VARCHAR(10) PRIMARY KEY,
  `service_name` VARCHAR(150) NOT NULL,
  `operator_alliance_id` VARCHAR(10),
  `trade_lane` VARCHAR(50),
  `frequency_weekly` INT,
  `port_rotation` TEXT,
  `active_from` DATE,
  `active_to` DATE,
  FOREIGN KEY (`operator_alliance_id`) REFERENCES `alliances`(`alliance_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `news_events` (
  `event_id` VARCHAR(10) PRIMARY KEY,
  `event_date` DATE NOT NULL,
  `title_vi` VARCHAR(500),
  `title_en` VARCHAR(500),
  `summary_vi` TEXT,
  `source` VARCHAR(100),
  `category` VARCHAR(30),
  `sentiment` VARCHAR(20),
  `affected_lines` JSON,
  `affected_ports` JSON,
  `affected_regions` JSON,
  INDEX `idx_date` (`event_date`),
  INDEX `idx_category` (`category`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `customers_shippers` (
  `customer_id` VARCHAR(10) PRIMARY KEY,
  `customer_name` VARCHAR(150) NOT NULL,
  `industry` VARCHAR(50),
  `primary_region` VARCHAR(20)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----- Facts -----
CREATE TABLE `port_calls` (
  `call_id` VARCHAR(15) PRIMARY KEY,
  `port_id` VARCHAR(10) NOT NULL,
  `vessel_id` VARCHAR(10) NOT NULL,
  `voyage_no` VARCHAR(20),
  `service_id` VARCHAR(10),
  `shipping_line_id` VARCHAR(10) NOT NULL,
  `eta` DATETIME NOT NULL,
  `etb` DATETIME,
  `etd` DATETIME,
  `ata` DATETIME,
  `atb` DATETIME,
  `atd` DATETIME,
  `berth_id` VARCHAR(10),
  `teu_discharged` INT,
  `teu_loaded` INT,
  `teu_transshipment` INT,
  `total_teu_handled` INT,
  `dwell_time_hours` DECIMAL(7,2),
  `revenue_vnd` BIGINT,
  `cost_vnd` BIGINT,
  `reefer_teu` INT,
  `vas_revenue_vnd` BIGINT,
  FOREIGN KEY (`port_id`) REFERENCES `ports`(`port_id`),
  FOREIGN KEY (`vessel_id`) REFERENCES `vessels`(`vessel_id`),
  FOREIGN KEY (`shipping_line_id`) REFERENCES `shipping_lines`(`line_id`),
  FOREIGN KEY (`service_id`) REFERENCES `services`(`service_id`),
  INDEX `idx_port_eta` (`port_id`, `eta`),
  INDEX `idx_line_eta` (`shipping_line_id`, `eta`),
  INDEX `idx_service_eta` (`service_id`, `eta`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `daily_port_stats` (
  `stat_id` VARCHAR(15) PRIMARY KEY,
  `port_id` VARCHAR(10) NOT NULL,
  `stat_date` DATE NOT NULL,
  `total_teu` INT,
  `total_calls` INT,
  `total_revenue_vnd` BIGINT,
  `unique_lines_count` INT,
  FOREIGN KEY (`port_id`) REFERENCES `ports`(`port_id`),
  UNIQUE KEY `uniq_port_date` (`port_id`, `stat_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `port_vessel_schedule_external` (
  `schedule_id` VARCHAR(15) PRIMARY KEY,
  `port_id` VARCHAR(10) NOT NULL,
  `vessel_id` VARCHAR(10),
  `shipping_line_id` VARCHAR(10) NOT NULL,
  `eta` DATETIME NOT NULL,
  `etd` DATETIME,
  `service_id` VARCHAR(10),
  `teu_capacity_est` INT,
  `source` VARCHAR(30),
  FOREIGN KEY (`port_id`) REFERENCES `ports`(`port_id`),
  FOREIGN KEY (`shipping_line_id`) REFERENCES `shipping_lines`(`line_id`),
  INDEX `idx_ext_port_eta` (`port_id`, `eta`),
  INDEX `idx_ext_line_eta` (`shipping_line_id`, `eta`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `pricing_tariff` (
  `tariff_id` VARCHAR(15) PRIMARY KEY,
  `port_id` VARCHAR(10) NOT NULL,
  `line_id` VARCHAR(10),
  `rate_per_teu_vnd` INT NOT NULL,
  `effective_from` DATE NOT NULL,
  `effective_to` DATE,
  FOREIGN KEY (`port_id`) REFERENCES `ports`(`port_id`),
  FOREIGN KEY (`line_id`) REFERENCES `shipping_lines`(`line_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----- Metadata -----
CREATE TABLE `_meta_tables` (
  `table_name` VARCHAR(50) PRIMARY KEY,
  `description_vi` TEXT,
  `description_en` TEXT,
  `business_context` TEXT,
  `data_source` VARCHAR(50)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `_meta_columns` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `table_name` VARCHAR(50) NOT NULL,
  `column_name` VARCHAR(50) NOT NULL,
  `data_type` VARCHAR(30),
  `description_vi` TEXT,
  `description_en` TEXT,
  `unit` VARCHAR(30),
  `example_values` TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `_meta_kpi` (
  `kpi_name` VARCHAR(100) PRIMARY KEY,
  `formula_sql` TEXT,
  `description_vi` TEXT,
  `related_questions` TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `_meta_glossary` (
  `term_vi` VARCHAR(100) PRIMARY KEY,
  `term_en` VARCHAR(100),
  `definition` TEXT,
  `related_tables` VARCHAR(200)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
