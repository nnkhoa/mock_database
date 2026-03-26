USE textile_tcm_demo;
-- MySQL dump 10.13  Distrib 8.0.45, for Linux (aarch64)
--
-- Host: localhost    Database: textile_tcm_demo
-- ------------------------------------------------------
-- Server version	8.0.45

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `_meta_columns`
--

DROP TABLE IF EXISTS `_meta_columns`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `_meta_columns` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID tự tăng',
  `table_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Tên bảng',
  `column_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Tên cột',
  `data_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Kiểu dữ liệu',
  `description_vi` text COLLATE utf8mb4_unicode_ci COMMENT 'Mô tả tiếng Việt',
  `description_en` text COLLATE utf8mb4_unicode_ci COMMENT 'Mô tả tiếng Anh',
  `unit` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Đơn vị',
  `example_values` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Ví dụ giá trị',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_meta_col` (`table_name`,`column_name`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Mô tả metadata các cột';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `_meta_glossary`
--

DROP TABLE IF EXISTS `_meta_glossary`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `_meta_glossary` (
  `term_id` int NOT NULL AUTO_INCREMENT COMMENT 'ID thuật ngữ',
  `term_vi` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Thuật ngữ tiếng Việt',
  `term_en` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Thuật ngữ tiếng Anh',
  `definition` text COLLATE utf8mb4_unicode_ci COMMENT 'Định nghĩa',
  PRIMARY KEY (`term_id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Bảng thuật ngữ ngành dệt may';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `_meta_kpi`
--

DROP TABLE IF EXISTS `_meta_kpi`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `_meta_kpi` (
  `kpi_id` int NOT NULL AUTO_INCREMENT COMMENT 'ID KPI',
  `kpi_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Tên KPI',
  `formula_sql` text COLLATE utf8mb4_unicode_ci COMMENT 'Công thức SQL',
  `description_vi` text COLLATE utf8mb4_unicode_ci COMMENT 'Mô tả tiếng Việt',
  `related_questions` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Câu hỏi liên quan',
  PRIMARY KEY (`kpi_id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Định nghĩa KPI và công thức tính';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `_meta_tables`
--

DROP TABLE IF EXISTS `_meta_tables`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `_meta_tables` (
  `table_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Tên bảng',
  `description_vi` text COLLATE utf8mb4_unicode_ci COMMENT 'Mô tả tiếng Việt',
  `description_en` text COLLATE utf8mb4_unicode_ci COMMENT 'Mô tả tiếng Anh',
  `business_context` text COLLATE utf8mb4_unicode_ci COMMENT 'Ngữ cảnh nghiệp vụ',
  PRIMARY KEY (`table_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Mô tả metadata các bảng';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `buyers`
--

DROP TABLE IF EXISTS `buyers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `buyers` (
  `buyer_id` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Mã khách hàng',
  `buyer_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Tên khách hàng',
  `market_id` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Mã thị trường',
  `country` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Quốc gia',
  `order_type` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'CMT|FOB|ODM',
  `annual_volume_estimate` int DEFAULT NULL COMMENT 'Ước tính sản lượng/năm',
  PRIMARY KEY (`buyer_id`),
  KEY `idx_buyers_market` (`market_id`),
  CONSTRAINT `fk_buyers_market` FOREIGN KEY (`market_id`) REFERENCES `markets` (`market_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Khách hàng / nhà mua hàng';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `cost_breakdown`
--

DROP TABLE IF EXISTS `cost_breakdown`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cost_breakdown` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID tự tăng',
  `order_id` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Mã lệnh sản xuất',
  `material_cost_vnd` decimal(18,2) DEFAULT NULL COMMENT 'Chi phí nguyên vật liệu VND',
  `labor_cost_vnd` decimal(18,2) DEFAULT NULL COMMENT 'Chi phí nhân công VND',
  `overhead_cost_vnd` decimal(18,2) DEFAULT NULL COMMENT 'Chi phí overhead VND',
  `overtime_hours` decimal(8,2) DEFAULT NULL COMMENT 'Giờ tăng ca',
  `yarn_yield_pct` decimal(5,2) DEFAULT NULL COMMENT 'Only for SEG-SOI orders - hiệu suất sợi',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_cb_order` (`order_id`),
  CONSTRAINT `fk_cb_order` FOREIGN KEY (`order_id`) REFERENCES `production_orders` (`order_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4167 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Phân tích chi phí sản xuất';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `exchange_rates`
--

DROP TABLE IF EXISTS `exchange_rates`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exchange_rates` (
  `rate_month` date NOT NULL COMMENT 'First day of month',
  `usd_vnd_rate` decimal(10,2) DEFAULT NULL COMMENT 'Tỷ giá USD/VND',
  PRIMARY KEY (`rate_month`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Tỷ giá ngoại tệ USD/VND theo tháng';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `factories`
--

DROP TABLE IF EXISTS `factories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `factories` (
  `factory_id` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Mã nhà máy',
  `factory_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Tên nhà máy',
  `location` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Địa chỉ',
  `factory_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'May | Sợi',
  `capacity_note` varchar(300) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Ghi chú năng suất',
  PRIMARY KEY (`factory_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Danh sách nhà máy sản xuất';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `factory_capacity`
--

DROP TABLE IF EXISTS `factory_capacity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `factory_capacity` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID tự tăng',
  `factory_id` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Mã nhà máy',
  `month` date DEFAULT NULL COMMENT 'Tháng',
  `max_capacity_units` int DEFAULT NULL COMMENT 'Năng suất tối đa sản phẩm/tháng',
  `current_utilization_pct` decimal(5,2) DEFAULT NULL COMMENT 'Tỷ lệ sử dụng hiện tại %',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_factory_month` (`factory_id`,`month`),
  KEY `idx_fc_factory` (`factory_id`),
  CONSTRAINT `fk_fc_factory` FOREIGN KEY (`factory_id`) REFERENCES `factories` (`factory_id`)
) ENGINE=InnoDB AUTO_INCREMENT=73 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Công suất nhà máy theo tháng';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `factory_kpi_monthly`
--

DROP TABLE IF EXISTS `factory_kpi_monthly`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `factory_kpi_monthly` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID tự tăng',
  `factory_id` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Mã nhà máy',
  `month` date DEFAULT NULL COMMENT 'Tháng',
  `line_efficiency_pct` decimal(5,2) DEFAULT NULL COMMENT 'Hiệu suất chuyền %',
  `otd_rate_pct` decimal(5,2) DEFAULT NULL COMMENT 'Tỷ lệ giao hàng đúng hạn %',
  `dhu_rate_pct` decimal(5,2) DEFAULT NULL COMMENT 'Tỷ lệ lỗi DHU %',
  `cost_per_unit_vnd` decimal(10,2) DEFAULT NULL COMMENT 'Chi phí/sản phẩm VND',
  `sam_achievement_pct` decimal(5,2) DEFAULT NULL COMMENT 'Đạt SAM %',
  `fabric_utilization_pct` decimal(5,2) DEFAULT NULL COMMENT 'Hiệu suất sử dụng vải %',
  `yarn_yield_pct` decimal(5,2) DEFAULT NULL COMMENT 'Hiệu suất sợi % (chỉ FAC-SP)',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_fac_kpi_month` (`factory_id`,`month`),
  KEY `idx_fkm_factory` (`factory_id`),
  CONSTRAINT `fk_fkm_factory` FOREIGN KEY (`factory_id`) REFERENCES `factories` (`factory_id`)
) ENGINE=InnoDB AUTO_INCREMENT=73 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='KPI nhà máy theo tháng';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `machine_downtime`
--

DROP TABLE IF EXISTS `machine_downtime`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `machine_downtime` (
  `downtime_id` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Mã sự cố máy',
  `machine_id` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Mã máy',
  `line_id` varchar(15) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Mã chuyền',
  `downtime_date` date DEFAULT NULL COMMENT 'Ngày xảy ra sự cố',
  `downtime_hours` decimal(6,2) DEFAULT NULL COMMENT 'Số giờ ngừng máy',
  `reason_code` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Mã/lý do sự cố',
  `shift` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Ca làm việc',
  PRIMARY KEY (`downtime_id`),
  KEY `idx_dt_machine` (`machine_id`),
  KEY `idx_dt_line` (`line_id`),
  KEY `idx_dt_date` (`downtime_date`),
  CONSTRAINT `fk_dt_line` FOREIGN KEY (`line_id`) REFERENCES `production_lines` (`line_id`),
  CONSTRAINT `fk_dt_machine` FOREIGN KEY (`machine_id`) REFERENCES `machines` (`machine_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Sự cố ngừng máy';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `machines`
--

DROP TABLE IF EXISTS `machines`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `machines` (
  `machine_id` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Mã máy',
  `line_id` varchar(15) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Mã chuyền',
  `machine_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'SEW|OVL|BTH|DYE|KNT',
  `machine_name` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Tên máy',
  PRIMARY KEY (`machine_id`),
  KEY `idx_mach_line` (`line_id`),
  CONSTRAINT `fk_mach_line` FOREIGN KEY (`line_id`) REFERENCES `production_lines` (`line_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Máy móc thiết bị trong chuyền';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `markets`
--

DROP TABLE IF EXISTS `markets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `markets` (
  `market_id` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Mã thị trường',
  `market_name` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Tên thị trường',
  `region` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Khu vực',
  PRIMARY KEY (`market_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Thị trường xuất khẩu';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `material_prices`
--

DROP TABLE IF EXISTS `material_prices`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `material_prices` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID tự tăng',
  `material_type_id` varchar(15) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Mã loại nguyên liệu',
  `price_month` date DEFAULT NULL COMMENT 'First day of month',
  `unit_price_usd` decimal(8,3) DEFAULT NULL COMMENT 'Giá USD/đơn vị',
  PRIMARY KEY (`id`),
  KEY `idx_mp_material` (`material_type_id`),
  KEY `idx_mp_month` (`price_month`),
  CONSTRAINT `fk_mp_material` FOREIGN KEY (`material_type_id`) REFERENCES `material_types` (`material_type_id`)
) ENGINE=InnoDB AUTO_INCREMENT=145 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Giá nguyên liệu theo tháng';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `material_receipts`
--

DROP TABLE IF EXISTS `material_receipts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `material_receipts` (
  `receipt_id` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Mã phiếu nhập nguyên liệu',
  `supplier_id` varchar(15) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Mã nhà cung cấp',
  `material_type_id` varchar(15) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Mã loại nguyên liệu',
  `planned_date` date DEFAULT NULL COMMENT 'Ngày nhập kế hoạch',
  `actual_date` date DEFAULT NULL COMMENT 'Ngày nhập thực tế',
  `quantity` decimal(12,2) DEFAULT NULL COMMENT 'Số lượng',
  `unit` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Đơn vị',
  `source_factory_id` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'If internal transfer',
  `destination_line_id` varchar(15) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Chuyền nhận hàng',
  PRIMARY KEY (`receipt_id`),
  KEY `idx_mr_supplier` (`supplier_id`),
  KEY `idx_mr_material` (`material_type_id`),
  KEY `idx_mr_date` (`planned_date`),
  KEY `fk_mr_dest_line` (`destination_line_id`),
  CONSTRAINT `fk_mr_dest_line` FOREIGN KEY (`destination_line_id`) REFERENCES `production_lines` (`line_id`),
  CONSTRAINT `fk_mr_material` FOREIGN KEY (`material_type_id`) REFERENCES `material_types` (`material_type_id`),
  CONSTRAINT `fk_mr_supplier` FOREIGN KEY (`supplier_id`) REFERENCES `material_suppliers` (`supplier_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Phiếu nhập nguyên vật liệu';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `material_suppliers`
--

DROP TABLE IF EXISTS `material_suppliers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `material_suppliers` (
  `supplier_id` varchar(15) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Mã nhà cung cấp',
  `supplier_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Tên nhà cung cấp',
  `material_type_id` varchar(15) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Mã loại nguyên liệu',
  `origin` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Xuất xứ',
  `effective_from` date DEFAULT NULL COMMENT 'Ngày bắt đầu hiệu lực',
  `effective_to` date DEFAULT NULL COMMENT 'NULL = currently active',
  PRIMARY KEY (`supplier_id`),
  KEY `idx_ms_material` (`material_type_id`),
  CONSTRAINT `fk_ms_material` FOREIGN KEY (`material_type_id`) REFERENCES `material_types` (`material_type_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Nhà cung cấp nguyên liệu';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `material_types`
--

DROP TABLE IF EXISTS `material_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `material_types` (
  `material_type_id` varchar(15) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Mã loại nguyên liệu',
  `material_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Tên nguyên liệu',
  `unit` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Đơn vị tính',
  `avg_price_usd` decimal(8,2) DEFAULT NULL COMMENT 'Giá trung bình USD',
  PRIMARY KEY (`material_type_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Loại nguyên liệu, vật tư';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `order_backlog`
--

DROP TABLE IF EXISTS `order_backlog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_backlog` (
  `backlog_id` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Mã đơn hàng tồn',
  `buyer_id` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Mã khách hàng',
  `style_id` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Mã mẫu mã',
  `planned_factory_id` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Nhà máy dự kiến',
  `value_vnd` decimal(18,2) DEFAULT NULL COMMENT 'Giá trị đơn hàng VND',
  `quantity` int DEFAULT NULL COMMENT 'Số lượng',
  `status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Pending|Confirmed',
  `planned_month` date DEFAULT NULL COMMENT 'Tháng sản xuất dự kiến',
  `created_date` date DEFAULT NULL COMMENT 'Ngày tạo',
  PRIMARY KEY (`backlog_id`),
  KEY `idx_ob_buyer` (`buyer_id`),
  KEY `idx_ob_style` (`style_id`),
  KEY `idx_ob_factory` (`planned_factory_id`),
  CONSTRAINT `fk_ob_buyer` FOREIGN KEY (`buyer_id`) REFERENCES `buyers` (`buyer_id`),
  CONSTRAINT `fk_ob_factory` FOREIGN KEY (`planned_factory_id`) REFERENCES `factories` (`factory_id`),
  CONSTRAINT `fk_ob_style` FOREIGN KEY (`style_id`) REFERENCES `production_styles` (`style_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Đơn hàng tồn chờ sản xuất';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `product_categories`
--

DROP TABLE IF EXISTS `product_categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `product_categories` (
  `category_id` varchar(15) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Mã danh mục',
  `segment_id` varchar(15) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Mã phân khúc',
  `category_name` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Tên danh mục',
  PRIMARY KEY (`category_id`),
  KEY `idx_pc_segment` (`segment_id`),
  CONSTRAINT `fk_pc_segment` FOREIGN KEY (`segment_id`) REFERENCES `product_segments` (`segment_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Danh mục sản phẩm';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `product_segments`
--

DROP TABLE IF EXISTS `product_segments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `product_segments` (
  `segment_id` varchar(15) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Mã phân khúc',
  `segment_name` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Tên phân khúc',
  `revenue_pct` decimal(5,2) DEFAULT NULL COMMENT 'Target % of total revenue',
  PRIMARY KEY (`segment_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Phân khúc sản phẩm';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `production_lines`
--

DROP TABLE IF EXISTS `production_lines`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `production_lines` (
  `line_id` varchar(15) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Mã chuyền sản xuất',
  `factory_id` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Mã nhà máy',
  `line_name` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Tên chuyền',
  `operator_count` int DEFAULT NULL COMMENT 'Số công nhân',
  `machine_count` int DEFAULT NULL COMMENT 'Số máy',
  `line_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Loại chuyền',
  PRIMARY KEY (`line_id`),
  KEY `idx_pl_factory` (`factory_id`),
  CONSTRAINT `fk_pl_factory` FOREIGN KEY (`factory_id`) REFERENCES `factories` (`factory_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Chuyền sản xuất trong nhà máy';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `production_orders`
--

DROP TABLE IF EXISTS `production_orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `production_orders` (
  `order_id` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Mã lệnh sản xuất',
  `factory_id` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Mã nhà máy',
  `line_id` varchar(15) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Mã chuyền',
  `style_id` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Mã mẫu mã',
  `buyer_id` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Mã khách hàng',
  `quantity` int DEFAULT NULL COMMENT 'Số lượng sản phẩm',
  `planned_delivery_date` date DEFAULT NULL COMMENT 'Ngày giao hàng kế hoạch',
  `actual_delivery_date` date DEFAULT NULL COMMENT 'Ngày giao hàng thực tế',
  `order_date` date DEFAULT NULL COMMENT 'Ngày đặt lệnh sản xuất',
  `status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Completed|In Progress|Delayed',
  `sam_minutes` decimal(5,1) DEFAULT NULL COMMENT 'SAM phút/sản phẩm',
  `line_efficiency_pct` decimal(5,2) DEFAULT NULL COMMENT 'Hiệu suất chuyền %',
  PRIMARY KEY (`order_id`),
  KEY `idx_po_factory` (`factory_id`),
  KEY `idx_po_line` (`line_id`),
  KEY `idx_po_style` (`style_id`),
  KEY `idx_po_buyer` (`buyer_id`),
  KEY `idx_po_delivery` (`planned_delivery_date`),
  CONSTRAINT `fk_po_buyer` FOREIGN KEY (`buyer_id`) REFERENCES `buyers` (`buyer_id`),
  CONSTRAINT `fk_po_factory` FOREIGN KEY (`factory_id`) REFERENCES `factories` (`factory_id`),
  CONSTRAINT `fk_po_line` FOREIGN KEY (`line_id`) REFERENCES `production_lines` (`line_id`),
  CONSTRAINT `fk_po_style` FOREIGN KEY (`style_id`) REFERENCES `production_styles` (`style_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Lệnh sản xuất';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `production_plan`
--

DROP TABLE IF EXISTS `production_plan`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `production_plan` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID tự tăng',
  `factory_id` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Mã nhà máy',
  `plan_month` date DEFAULT NULL COMMENT 'Tháng kế hoạch',
  `target_revenue_vnd` decimal(18,2) DEFAULT NULL COMMENT 'Doanh thu mục tiêu VND',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_plan` (`factory_id`,`plan_month`),
  KEY `idx_pp_factory` (`factory_id`),
  CONSTRAINT `fk_pp_factory` FOREIGN KEY (`factory_id`) REFERENCES `factories` (`factory_id`)
) ENGINE=InnoDB AUTO_INCREMENT=73 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Kế hoạch sản xuất theo tháng';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `production_styles`
--

DROP TABLE IF EXISTS `production_styles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `production_styles` (
  `style_id` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Mã mẫu mã sản phẩm',
  `style_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Tên mẫu',
  `fabric_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Loại vải',
  `buyer_id` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Mã khách hàng',
  `category_id` varchar(15) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Mã danh mục',
  `sam_minutes` decimal(5,1) DEFAULT NULL COMMENT 'Standard Allowed Minutes to make 1 product',
  `target_price_usd` decimal(8,2) DEFAULT NULL COMMENT 'Giá mục tiêu USD',
  PRIMARY KEY (`style_id`),
  KEY `idx_ps_buyer` (`buyer_id`),
  KEY `idx_ps_category` (`category_id`),
  CONSTRAINT `fk_ps_buyer` FOREIGN KEY (`buyer_id`) REFERENCES `buyers` (`buyer_id`),
  CONSTRAINT `fk_ps_category` FOREIGN KEY (`category_id`) REFERENCES `product_categories` (`category_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Mẫu mã sản phẩm';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `quality_inspections`
--

DROP TABLE IF EXISTS `quality_inspections`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `quality_inspections` (
  `inspection_id` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Mã kiểm tra chất lượng',
  `style_id` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Mã mẫu mã',
  `production_order_id` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Mã lệnh sản xuất',
  `line_id` varchar(15) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Mã chuyền',
  `inspection_date` date DEFAULT NULL COMMENT 'Ngày kiểm tra',
  `process_stage` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Cắt|May|Nhuộm|Hoàn tất',
  `defect_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Loại lỗi',
  `defect_count` int DEFAULT NULL COMMENT 'Số lỗi',
  `total_inspected` int DEFAULT NULL COMMENT 'Tổng số kiểm tra',
  `dhu_rate` decimal(5,2) DEFAULT NULL COMMENT 'Defects per Hundred Units',
  PRIMARY KEY (`inspection_id`),
  KEY `idx_qi_style` (`style_id`),
  KEY `idx_qi_order` (`production_order_id`),
  KEY `idx_qi_line` (`line_id`),
  KEY `idx_qi_date` (`inspection_date`),
  CONSTRAINT `fk_qi_line` FOREIGN KEY (`line_id`) REFERENCES `production_lines` (`line_id`),
  CONSTRAINT `fk_qi_order` FOREIGN KEY (`production_order_id`) REFERENCES `production_orders` (`order_id`),
  CONSTRAINT `fk_qi_style` FOREIGN KEY (`style_id`) REFERENCES `production_styles` (`style_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Kiểm tra chất lượng sản phẩm';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sales_orders`
--

DROP TABLE IF EXISTS `sales_orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sales_orders` (
  `order_id` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Mã đơn hàng bán',
  `buyer_id` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Mã khách hàng',
  `market_id` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Mã thị trường',
  `style_id` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Mã mẫu mã',
  `production_order_id` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Links to production_orders',
  `quantity` int DEFAULT NULL COMMENT 'Số lượng',
  `unit_price_usd` decimal(8,2) DEFAULT NULL COMMENT 'Đơn giá USD',
  `revenue_usd` decimal(15,2) DEFAULT NULL COMMENT 'Doanh thu USD',
  `revenue_vnd` decimal(18,2) DEFAULT NULL COMMENT 'Doanh thu VND',
  `delivery_month` date DEFAULT NULL COMMENT 'First day of delivery month',
  `created_at` date DEFAULT NULL COMMENT 'Ngày tạo đơn hàng',
  PRIMARY KEY (`order_id`),
  KEY `idx_so_buyer` (`buyer_id`),
  KEY `idx_so_market` (`market_id`),
  KEY `idx_so_style` (`style_id`),
  KEY `idx_so_delivery` (`delivery_month`),
  CONSTRAINT `fk_so_buyer` FOREIGN KEY (`buyer_id`) REFERENCES `buyers` (`buyer_id`),
  CONSTRAINT `fk_so_market` FOREIGN KEY (`market_id`) REFERENCES `markets` (`market_id`),
  CONSTRAINT `fk_so_style` FOREIGN KEY (`style_id`) REFERENCES `production_styles` (`style_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Đơn hàng bán / xuất khẩu';
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-03-26  6:57:38
