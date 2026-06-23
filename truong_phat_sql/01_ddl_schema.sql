-- ============================================================
-- 01_*.sql  |  wood_export_demo  |  Gỗ Trường Phát (demo)
-- Database: wood_export_demo
-- DDL — CREATE DATABASE, CREATE TABLE, indexes, constraints, COMMENT.
-- Encode: UTF-8 (utf8mb4). Chạy theo thứ tự 01→05.
-- ============================================================

/*!40101 SET NAMES utf8mb4 */;
SET NAMES utf8mb4;

DROP DATABASE IF EXISTS `wood_export_demo`;
CREATE DATABASE `wood_export_demo` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `wood_export_demo`;

CREATE TABLE `dim_calendar` (
  `date` DATE NOT NULL COMMENT 'Ngày [date]',
  `year` INT NOT NULL COMMENT 'Năm [year]',
  `quarter` INT NOT NULL COMMENT 'Quý (1-4) [quarter]',
  `month` INT NOT NULL COMMENT 'Tháng (1-12) [month]',
  `month_name_vi` VARCHAR(20) NOT NULL COMMENT 'Tên tháng tiếng Việt',
  `week` INT NOT NULL COMMENT 'Tuần ISO trong năm [week]',
  `day_of_week` INT NOT NULL COMMENT 'Thứ (1=T2 .. 7=CN)',
  `day_of_month` INT NOT NULL COMMENT 'Ngày trong tháng',
  `is_weekend` TINYINT NOT NULL COMMENT '1 nếu T7/CN [bool]',
  `is_tet_season` TINYINT NOT NULL COMMENT '1 nếu tháng 1-2 (mùa Tết, SX chậm) [bool]',
  PRIMARY KEY (`date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Bảng lịch ngày, phủ kín 2024-06-01..2026-05-31. Dùng cho mọi phân tích theo thời gian, YoY, seasonality.';

CREATE TABLE `dim_market` (
  `market_id` INT NOT NULL COMMENT 'ID thị trường',
  `market_name` VARCHAR(30) NOT NULL COMMENT 'Tên thị trường',
  `region_type` VARCHAR(20) NOT NULL COMMENT 'Loại: Xuất khẩu / Nội địa',
  `currency_code` VARCHAR(5) NOT NULL COMMENT 'Tiền tệ gốc đơn hàng',
  `default_tariff_note` VARCHAR(255) COMMENT 'Ghi chú thuế',
  PRIMARY KEY (`market_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Thị trường tiêu thụ (6 thị trường).';

CREATE TABLE `dim_customer` (
  `customer_id` INT NOT NULL COMMENT 'ID khách',
  `customer_name` VARCHAR(80) NOT NULL COMMENT 'Tên khách',
  `market_id` INT NOT NULL COMMENT 'Thị trường (FK dim_market)',
  `customer_type` VARCHAR(30) NOT NULL COMMENT 'Nhà nhập khẩu/Chuỗi bán lẻ/Dự án',
  `country` VARCHAR(40) NOT NULL COMMENT 'Quốc gia',
  `is_key_account` TINYINT NOT NULL COMMENT '1 nếu key account [bool]',
  `onboard_date` DATE NOT NULL COMMENT 'Ngày bắt đầu hợp tác [date]',
  PRIMARY KEY (`customer_id`),
  KEY `idx_cust_market` (`market_id`),
  CONSTRAINT `fk_cust_market` FOREIGN KEY (`market_id`) REFERENCES `dim_market` (`market_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Khách hàng (nhà nhập khẩu / chuỗi bán lẻ / dự án). ~24 khách.';

CREATE TABLE `dim_product` (
  `product_id` INT NOT NULL COMMENT 'ID sản phẩm',
  `sku_code` VARCHAR(20) NOT NULL COMMENT 'Mã SKU',
  `product_name` VARCHAR(120) NOT NULL COMMENT 'Tên sản phẩm (tiếng Việt)',
  `product_category` VARCHAR(40) NOT NULL COMMENT 'Nhóm chính (5 nhóm)',
  `product_subcategory` VARCHAR(40) NOT NULL COMMENT 'Nhóm con',
  `wood_species` VARCHAR(20) NOT NULL COMMENT 'Loại gỗ (Sồi/Óc chó = nhập)',
  `is_section232_affected` TINYINT NOT NULL COMMENT '1 nếu chịu rủi ro thuế Mỹ 232 [bool]',
  `section232_tariff_type` ENUM('none','sofa_30pct','cabinet_50pct') NOT NULL COMMENT 'Mức thuế dự kiến từ 1/1/2027',
  `base_asp_vnd` DECIMAL(15,2) NOT NULL COMMENT 'Giá bán bình quân tham chiếu [VND]',
  `popularity_weight` DECIMAL(9,6) NOT NULL COMMENT 'Trọng số Pareto (top 20% ~ 80% volume)',
  PRIMARY KEY (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Danh mục sản phẩm, hierarchy category → subcategory → SKU (~40 SKU).';

CREATE TABLE `dim_factory` (
  `factory_id` INT NOT NULL COMMENT 'ID nhà máy',
  `factory_name` VARCHAR(60) NOT NULL COMMENT 'Tên nhà máy',
  `location` VARCHAR(20) NOT NULL COMMENT 'Địa điểm',
  `primary_category` VARCHAR(40) NOT NULL COMMENT 'Nhóm SP chính',
  `monthly_capacity_units` INT NOT NULL COMMENT 'Công suất tháng (sản phẩm) [sản phẩm/tháng]',
  `opened_date` DATE NOT NULL COMMENT 'Ngày vận hành [date]',
  PRIMARY KEY (`factory_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Nhà máy sản xuất (6 nhà máy tại Bình Dương + Bình Định).';

CREATE TABLE `dim_fx_monthly` (
  `month` DATE NOT NULL COMMENT 'Đầu tháng (YYYY-MM-01) [date]',
  `usd_vnd_avg` DECIMAL(10,2) NOT NULL COMMENT 'Tỷ giá USD/VND bình quân tháng [VND/USD]',
  `eur_vnd_avg` DECIMAL(10,2) NOT NULL COMMENT 'Tỷ giá EUR/VND bình quân tháng [VND/EUR]',
  `note` VARCHAR(255) COMMENT 'Ghi chú',
  PRIMARY KEY (`month`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Tỷ giá bình quân theo tháng. Bảng tra cứu chính cho phân tích FX margin.';

CREATE TABLE `fact_sales` (
  `sale_id` BIGINT NOT NULL COMMENT 'ID dòng bán',
  `order_id` BIGINT NOT NULL COMMENT 'ID đơn hàng (gom nhiều line)',
  `order_date` DATE NOT NULL COMMENT 'Ngày đặt (FK dim_calendar) [date]',
  `customer_id` INT NOT NULL COMMENT 'Khách (FK dim_customer)',
  `product_id` INT NOT NULL COMMENT 'Sản phẩm (FK dim_product)',
  `market_id` INT NOT NULL COMMENT 'Thị trường (FK dim_market)',
  `factory_id` INT NOT NULL COMMENT 'Nhà máy SX (FK dim_factory)',
  `channel` VARCHAR(20) NOT NULL COMMENT 'Xuất khẩu / Nội địa',
  `quantity` INT NOT NULL COMMENT 'Số lượng [sản phẩm]',
  `unit_price_vnd` DECIMAL(15,2) NOT NULL COMMENT 'Đơn giá (ASP) [VND]',
  `net_revenue_vnd` DECIMAL(18,2) NOT NULL COMMENT 'Doanh thu thuần dòng [VND]',
  `cogs_material_imported_vnd` DECIMAL(18,2) NOT NULL COMMENT 'Giá vốn gỗ nhập (chịu FX) [VND]',
  `cogs_material_domestic_vnd` DECIMAL(18,2) NOT NULL COMMENT 'Giá vốn gỗ nội địa [VND]',
  `cogs_labor_vnd` DECIMAL(18,2) NOT NULL COMMENT 'Giá vốn nhân công [VND]',
  `cogs_overhead_vnd` DECIMAL(18,2) NOT NULL COMMENT 'Chi phí SX chung [VND]',
  `cogs_total_vnd` DECIMAL(18,2) NOT NULL COMMENT 'Tổng giá vốn (= 4 thành phần) [VND]',
  `gross_profit_vnd` DECIMAL(18,2) NOT NULL COMMENT 'Lợi nhuận gộp (= net_revenue - cogs_total) [VND]',
  PRIMARY KEY (`sale_id`),
  KEY `idx_fs_order_date` (`order_date`),
  KEY `idx_fs_customer` (`customer_id`),
  KEY `idx_fs_product` (`product_id`),
  KEY `idx_fs_market` (`market_id`),
  KEY `idx_fs_factory` (`factory_id`),
  CONSTRAINT `fk_fs_date` FOREIGN KEY (`order_date`) REFERENCES `dim_calendar` (`date`),
  CONSTRAINT `fk_fs_customer` FOREIGN KEY (`customer_id`) REFERENCES `dim_customer` (`customer_id`),
  CONSTRAINT `fk_fs_product` FOREIGN KEY (`product_id`) REFERENCES `dim_product` (`product_id`),
  CONSTRAINT `fk_fs_market` FOREIGN KEY (`market_id`) REFERENCES `dim_market` (`market_id`),
  CONSTRAINT `fk_fs_factory` FOREIGN KEY (`factory_id`) REFERENCES `dim_factory` (`factory_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='FACT CHÍNH — doanh thu bán hàng, grain = transaction line item (1 dòng = 1 line item của 1 đơn).';

CREATE TABLE `fact_production` (
  `production_id` INT NOT NULL COMMENT 'ID dòng sản xuất',
  `factory_id` INT NOT NULL COMMENT 'Nhà máy (FK dim_factory)',
  `month` DATE NOT NULL COMMENT 'Đầu tháng (YYYY-MM-01) [date]',
  `product_category` VARCHAR(40) NOT NULL COMMENT 'Nhóm SP sản xuất',
  `units_produced` INT NOT NULL COMMENT 'Số SP sản xuất trong tháng [sản phẩm]',
  `capacity_units` INT NOT NULL COMMENT 'Công suất khả dụng tháng (theo category) [sản phẩm]',
  `utilization_pct` DECIMAL(6,2) NOT NULL COMMENT 'units_produced / capacity_units × 100 [%]',
  PRIMARY KEY (`production_id`),
  KEY `idx_fp_factory_month` (`factory_id`, `month`),
  CONSTRAINT `fk_fp_factory` FOREIGN KEY (`factory_id`) REFERENCES `dim_factory` (`factory_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Sản xuất & công suất, grain = factory × month × category. SNAPSHOT theo tháng.';

CREATE TABLE `_meta_tables` (
  `table_name` VARCHAR(64) NOT NULL COMMENT 'Tên bảng',
  `description_vi` TEXT COMMENT 'Mô tả tiếng Việt',
  `description_en` TEXT COMMENT 'Mô tả tiếng Anh',
  `business_context` TEXT COMMENT 'Bối cảnh nghiệp vụ',
  PRIMARY KEY (`table_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Metadata: mô tả từng bảng (AI đọc để hiểu DB)';

CREATE TABLE `_meta_columns` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `table_name` VARCHAR(64) NOT NULL COMMENT 'Tên bảng',
  `column_name` VARCHAR(64) NOT NULL COMMENT 'Tên cột',
  `data_type` VARCHAR(64) NOT NULL COMMENT 'Kiểu dữ liệu',
  `description_vi` TEXT COMMENT 'Mô tả tiếng Việt',
  `description_en` TEXT COMMENT 'Mô tả tiếng Anh',
  `unit` VARCHAR(40) COMMENT 'Đơn vị',
  `example_values` VARCHAR(255) COMMENT 'Giá trị ví dụ',
  PRIMARY KEY (`id`),
  KEY `idx_mc_table` (`table_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Metadata: mô tả từng cột';

CREATE TABLE `_meta_kpi` (
  `kpi_name` VARCHAR(80) NOT NULL COMMENT 'Tên KPI',
  `formula_sql` TEXT COMMENT 'Công thức SQL',
  `description_vi` TEXT COMMENT 'Mô tả',
  `related_questions` VARCHAR(120) COMMENT 'Câu hỏi liên quan',
  PRIMARY KEY (`kpi_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Metadata: KPI tree';

CREATE TABLE `_meta_glossary` (
  `term_vi` VARCHAR(80) NOT NULL COMMENT 'Thuật ngữ tiếng Việt',
  `term_en` VARCHAR(80) COMMENT 'Thuật ngữ tiếng Anh',
  `definition` TEXT COMMENT 'Định nghĩa',
  PRIMARY KEY (`term_vi`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Metadata: từ điển thuật ngữ';

