USE lc_aibi;
-- MySQL dump 10.13  Distrib 8.0.45, for Linux (aarch64)
--
-- Host: localhost    Database: lc_aibi
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
-- Table structure for table `view_genie_person`
--

DROP TABLE IF EXISTS `view_genie_person`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `view_genie_person` (
  `lcv_id` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'MÃ£ Ä‘á»‹nh danh ngÆ°á»i thá»¥ hÆ°á»Ÿng (báº¯t Ä‘áº§u báº±ng LCV)',
  `customer_id` varchar(24) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'MÃ£ Ä‘á»‹nh danh ngÆ°á»i mua Ä‘Æ¡n hÃ ng (24 kÃ½ tá»± alphanumeric)',
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Há» vÃ  tÃªn Ä‘áº§y Ä‘á»§ (tiáº¿ng Viá»‡t, duy nháº¥t)',
  `date_of_birth` date NOT NULL COMMENT 'NgÃ y sinh (YYYY-MM-DD)',
  `gender` tinyint NOT NULL COMMENT '0=Nam, 1=Ná»¯, 2=KhÃ¡c',
  `note` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT 'Ghi chÃº bá»• sung (thÆ°á»ng null)',
  PRIMARY KEY (`customer_id`),
  UNIQUE KEY `uq_lcv_id` (`lcv_id`),
  KEY `idx_dob` (`date_of_birth`),
  KEY `idx_gender` (`gender`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Báº£ng chiá»u thÃ´ng tin khÃ¡ch hÃ ng thá»¥ hÆ°á»Ÿng ngÆ°á»i tiÃªm';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `view_genie_shop`
--

DROP TABLE IF EXISTS `view_genie_shop`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `view_genie_shop` (
  `shop_code` varchar(5) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'MÃ£ cá»­a hÃ ng duy nháº¥t (5 chá»¯ sá»‘)',
  `province_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'TÃªn tá»‰nh/thÃ nh phá»‘ (63 tá»‰nh thÃ nh VN)',
  `district_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'TÃªn quáº­n/huyá»‡n',
  `ward_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'TÃªn phÆ°á»ng/xÃ£',
  `address` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Äá»‹a chá»‰ Ä‘áº§y Ä‘á»§',
  `area_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'VÃ¹ng kinh táº¿ (7 vÃ¹ng)',
  `region_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Miá»n Ä‘á»‹a lÃ½: Miá»n Báº¯c | Miá»n Trung | Miá»n Nam',
  PRIMARY KEY (`shop_code`),
  KEY `idx_province` (`province_name`),
  KEY `idx_region` (`region_name`),
  KEY `idx_area` (`area_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Báº£ng chiá»u thÃ´ng tin cá»­a hÃ ng tiÃªm chá»§ng';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `view_genie_vaccine_product`
--

DROP TABLE IF EXISTS `view_genie_vaccine_product`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `view_genie_vaccine_product` (
  `sku` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'MÃ£ SKU sáº£n pháº©m duy nháº¥t',
  `disease_group_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'NhÃ³m bá»‡nh (null vá»›i combo/dá»‹ch vá»¥/test)',
  `product_name` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'TÃªn Ä‘áº§y Ä‘á»§ sáº£n pháº©m vaccine',
  PRIMARY KEY (`sku`),
  KEY `idx_disease_group` (`disease_group_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Báº£ng chiá»u danh má»¥c sáº£n pháº©m vaccine';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `view_genie_vaccine_returned_order_detail`
--

DROP TABLE IF EXISTS `view_genie_vaccine_returned_order_detail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `view_genie_vaccine_returned_order_detail` (
  `attachment_code` varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'FK liÃªn káº¿t vá» Ä‘Æ¡n hÃ ng gá»‘c',
  `customer_id` varchar(24) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'MÃ£ ngÆ°á»i mua (báº¯t buá»™c)',
  `lcv_id` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'MÃ£ ngÆ°á»i thá»¥ hÆ°á»Ÿng (cÃ³ thá»ƒ null ~1%)',
  `sku` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'MÃ£ sáº£n pháº©m vaccine',
  `package_type` varchar(3) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Loáº¡i mua: LE | GOI',
  `return_line_item_amount_after_discount` bigint NOT NULL COMMENT 'GiÃ¡ trá»‹ hoÃ n tráº£ sau chiáº¿t kháº¥u (VND)',
  `return_date` date NOT NULL COMMENT 'NgÃ y tráº£ hÃ ng',
  PRIMARY KEY (`attachment_code`),
  KEY `fk_return_sku` (`sku`),
  KEY `idx_return_date` (`return_date`),
  KEY `idx_return_customer` (`customer_id`),
  CONSTRAINT `fk_return_attachment` FOREIGN KEY (`attachment_code`) REFERENCES `view_genie_vaccine_sales_order_detail` (`attachment_code`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_return_customer` FOREIGN KEY (`customer_id`) REFERENCES `view_genie_person` (`customer_id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_return_sku` FOREIGN KEY (`sku`) REFERENCES `view_genie_vaccine_product` (`sku`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `chk_return_package` CHECK ((`package_type` in (_latin1'LE',_latin1'GOI')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Báº£ng fact chi tiáº¿t Ä‘Æ¡n hÃ ng tráº£ láº¡i vaccine';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `view_genie_vaccine_sales_order_detail`
--

DROP TABLE IF EXISTS `view_genie_vaccine_sales_order_detail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `view_genie_vaccine_sales_order_detail` (
  `attachment_code` varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'MÃ£ duy nháº¥t cá»§a line item (PK)',
  `customer_id` varchar(24) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'MÃ£ ngÆ°á»i mua',
  `lcv_id` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'MÃ£ ngÆ°á»i thá»¥ hÆ°á»Ÿng mÅ©i tiÃªm',
  `shop_code` varchar(5) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'MÃ£ cá»­a hÃ ng',
  `order_code` varchar(23) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'MÃ£ Ä‘Æ¡n hÃ ng (23 chá»¯ sá»‘, 1 order cÃ³ thá»ƒ nhiá»u line item)',
  `sku` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'MÃ£ sáº£n pháº©m vaccine',
  `package_type` varchar(3) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Loáº¡i mua: LE (láº») | GOI (gÃ³i, +5%)',
  `line_item_amount_after_discount` bigint NOT NULL COMMENT 'Doanh thu line item sau chiáº¿t kháº¥u (VND)',
  `line_item_quantity` tinyint NOT NULL COMMENT 'Sá»‘ lÆ°á»£ng mÅ©i tiÃªm (1-3)',
  `order_completion_date` date NOT NULL COMMENT 'NgÃ y hoÃ n thÃ nh Ä‘Æ¡n hÃ ng',
  `order_creation_date` date NOT NULL COMMENT 'NgÃ y táº¡o Ä‘Æ¡n hÃ ng',
  PRIMARY KEY (`attachment_code`),
  KEY `fk_sales_sku` (`sku`),
  KEY `idx_order_code` (`order_code`),
  KEY `idx_shop_date` (`shop_code`,`order_completion_date`),
  KEY `idx_completion_date` (`order_completion_date`),
  KEY `idx_customer` (`customer_id`),
  KEY `idx_lcv` (`lcv_id`),
  CONSTRAINT `fk_sales_customer` FOREIGN KEY (`customer_id`) REFERENCES `view_genie_person` (`customer_id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_sales_shop` FOREIGN KEY (`shop_code`) REFERENCES `view_genie_shop` (`shop_code`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_sales_sku` FOREIGN KEY (`sku`) REFERENCES `view_genie_vaccine_product` (`sku`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `chk_package_type` CHECK ((`package_type` in (_latin1'LE',_latin1'GOI'))),
  CONSTRAINT `chk_quantity` CHECK ((`line_item_quantity` between 1 and 10))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Báº£ng fact chi tiáº¿t Ä‘Æ¡n hÃ ng bÃ¡n vaccine';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `view_genie_vaccine_shop_target`
--

DROP TABLE IF EXISTS `view_genie_vaccine_shop_target`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `view_genie_vaccine_shop_target` (
  `shop_code` varchar(5) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'MÃ£ cá»­a hÃ ng',
  `month` tinyint NOT NULL COMMENT 'ThÃ¡ng (1-12)',
  `year` smallint NOT NULL COMMENT 'NÄƒm (2024-2025)',
  `target_sales` bigint NOT NULL COMMENT 'Doanh thu má»¥c tiÃªu (VND)',
  PRIMARY KEY (`shop_code`,`month`,`year`),
  KEY `idx_year_month` (`year`,`month`),
  CONSTRAINT `fk_target_shop` FOREIGN KEY (`shop_code`) REFERENCES `view_genie_shop` (`shop_code`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Báº£ng KPI doanh thu má»¥c tiÃªu theo thÃ¡ng cá»§a tá»«ng cá»­a hÃ ng';
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
