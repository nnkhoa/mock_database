-- ============================================================
-- instant_noodle_demo — Master Data
-- Exported: 2026-04-07 20:59:00
-- ============================================================

USE `instant_noodle_demo`;

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------------------
-- Table: factories
-- ----------------------------------------

INSERT INTO `factories` (`factory_id`, `factory_name`, `factory_short_name`, `province`, `region`, `area_sqm`, `year_commissioned`, `designed_capacity_million_packs_month`, `num_production_lines`, `num_employees`, `status`) VALUES
('F01', 'NM An Phú', 'An Phú', 'Bình Dương', 'Nam', 35000, 2003, 105.0, 5, 850, 'active'),
('F02', 'NM Nam Tân Uyên', 'Nam Tân Uyên', 'Bình Dương', 'Nam', 100000, 2017, 130.0, 4, 920, 'active'),
('F03', 'NM Bắc Ninh', 'Bắc Ninh', 'Bắc Ninh', 'Bắc', 57000, 2011, 65.0, 3, 580, 'active'),
('F04', 'NM Đà Nẵng', 'Đà Nẵng', 'Đà Nẵng', 'Trung', 20000, 2012, 35.0, 2, 320, 'active'),
('F05', 'NM Gò Vấp (Legacy)', 'Gò Vấp', 'TP.HCM', 'Nam', 13000, 1990, 25.0, 2, 330, 'active');


-- ----------------------------------------
-- Table: production_lines
-- ----------------------------------------

INSERT INTO `production_lines` (`line_id`, `factory_id`, `line_name`, `product_type`, `capacity_packs_per_hour`, `commissioned_date`, `status`) VALUES
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
('L05-02', 'F05', 'Gò Vấp - DC Mì đặc biệt', 'mi_goi', 12000, '2008-06-01', 'active');


-- ----------------------------------------
-- Table: product_categories
-- ----------------------------------------

INSERT INTO `product_categories` (`category_id`, `category_name`, `category_name_en`, `price_segment`, `avg_margin_pct`, `volume_share_pct`, `description`) VALUES
('CAT01', 'Mì gói Gấu Đỏ', 'Instant Noodle Pack', 'binh_dan', 19.00, 55.00, 'Dòng mì gói truyền thống, chủ lực của Asia Foods'),
('CAT02', 'Mì Ly Gấu Đỏ', 'Cup Noodle', 'binh_dan', 23.00, 18.00, 'Mì ly tiện lợi, phân khúc bình dân'),
('CAT03', 'JOMO (Mì Khoai Tây)', 'JOMO Potato Noodle', 'trung_cap', 27.00, 10.00, 'Dòng mì khoai tây trung cấp, thương hiệu riêng'),
('CAT04', 'Cháo Gấu Đỏ', 'Instant Porridge', 'binh_dan', 30.00, 8.00, 'Cháo ăn liền, margin cao, bán mạnh mùa lạnh'),
('CAT05', 'Phở & Hủ tiếu ăn liền', 'Instant Pho & Rice Noodle', 'binh_dan', 21.00, 5.00, 'Phở và hủ tiếu ăn liền'),
('CAT06', 'Mì Trứng Vàng & Mộc Việt', 'Egg Noodle & Moc Viet', 'binh_dan', 20.00, 4.00, 'Dòng mì trứng và mì chay/đặc biệt');


-- ----------------------------------------
-- Table: products
-- ----------------------------------------

INSERT INTO `products` (`product_id`, `product_name`, `category_id`, `brand`, `flavor`, `pack_weight_g`, `unit_price_vnd`, `cost_per_pack_vnd`, `is_export`, `launch_year`, `popularity_weight`, `status`) VALUES
('SKU001', 'Mì Gấu Đỏ Tôm Chua Cay', 'CAT01', 'Gấu Đỏ', 'Tôm chua cay', 75, 3500, 2835, 1, 2005, 1.000, 'active'),
('SKU002', 'Mì Gấu Đỏ Bò Hầm Rau Thơm', 'CAT01', 'Gấu Đỏ', 'Bò hầm', 75, 3500, 2835, 1, 2005, 0.850, 'active'),
('SKU003', 'Mì Gấu Đỏ Gà Hầm Ngũ Vị', 'CAT01', 'Gấu Đỏ', 'Gà hầm', 75, 3500, 2835, 1, 2006, 0.700, 'active'),
('SKU004', 'Mì Gấu Đỏ Lẩu Thái', 'CAT01', 'Gấu Đỏ', 'Lẩu Thái', 75, 3800, 3078, 0, 2010, 0.600, 'active'),
('SKU005', 'Mì Gấu Đỏ Sườn Hầm Ngũ Quả', 'CAT01', 'Gấu Đỏ', 'Sườn hầm', 75, 3500, 2835, 0, 2008, 0.500, 'active'),
('SKU006', 'Mì Gấu Đỏ Hải Sản', 'CAT01', 'Gấu Đỏ', 'Hải sản', 75, 3500, 2835, 0, 2012, 0.350, 'active'),
('SKU007', 'Mì Gấu Đỏ Chay Rau Nấm', 'CAT01', 'Gấu Đỏ', 'Chay rau nấm', 75, 3200, 2592, 0, 2015, 0.200, 'active'),
('SKU008', 'Mì Gấu Đỏ Thịt Bằm', 'CAT01', 'Gấu Đỏ', 'Thịt bằm', 75, 3500, 2835, 0, 2011, 0.300, 'active'),
('SKU009', 'Mì Gấu Đỏ Kim Chi', 'CAT01', 'Gấu Đỏ', 'Kim chi', 75, 3800, 3078, 0, 2018, 0.150, 'active'),
('SKU00A', 'Mì Gấu Đỏ Sa Tế', 'CAT01', 'Gấu Đỏ', 'Sa tế', 75, 3500, 2835, 0, 2014, 0.100, 'active'),
('SKU010', 'Mì Ly Gấu Đỏ Tôm Chua Cay', 'CAT02', 'Gấu Đỏ', 'Tôm chua cay', 65, 7000, 5390, 1, 2012, 0.900, 'active'),
('SKU011', 'Mì Ly Gấu Đỏ Bò Hầm', 'CAT02', 'Gấu Đỏ', 'Bò hầm', 65, 7000, 5390, 1, 2012, 0.750, 'active'),
('SKU012', 'Mì Ly Gấu Đỏ Lẩu Tôm', 'CAT02', 'Gấu Đỏ', 'Lẩu tôm', 65, 7000, 5390, 0, 2015, 0.550, 'active'),
('SKU013', 'Mì Ly Gấu Đỏ Gà Hầm', 'CAT02', 'Gấu Đỏ', 'Gà hầm', 65, 7000, 5390, 0, 2014, 0.400, 'active'),
('SKU014', 'Mì Ly Gấu Đỏ Bò Viên', 'CAT02', 'Gấu Đỏ', 'Bò viên', 65, 7500, 5775, 0, 2017, 0.300, 'active'),
('SKU015', 'Mì Ly Gấu Đỏ Hải Sản', 'CAT02', 'Gấu Đỏ', 'Hải sản', 65, 7000, 5390, 0, 2016, 0.200, 'active'),
('SKU016', 'Mì Ly Gấu Đỏ Lẩu Thái', 'CAT02', 'Gấu Đỏ', 'Lẩu Thái', 65, 7500, 5775, 0, 2019, 0.150, 'active'),
('SKU017', 'Mì Ly Gấu Đỏ Sườn Hầm', 'CAT02', 'Gấu Đỏ', 'Sườn hầm', 65, 7000, 5390, 0, 2020, 0.100, 'active'),
('SKU020', 'Mì JOMO Khoai Tây Vị Bò', 'CAT03', 'JOMO', 'Khoai tây bò', 80, 5500, 4015, 0, 2019, 0.800, 'active'),
('SKU021', 'Mì JOMO Khoai Tây Vị Gà', 'CAT03', 'JOMO', 'Khoai tây gà', 80, 5500, 4015, 0, 2019, 0.650, 'active'),
('SKU022', 'Mì JOMO Khoai Tây Vị Tôm', 'CAT03', 'JOMO', 'Khoai tây tôm', 80, 5500, 4015, 0, 2020, 0.450, 'active'),
('SKU023', 'Mì JOMO Khoai Tây Sườn Hầm', 'CAT03', 'JOMO', 'Khoai tây sườn', 80, 5800, 4234, 0, 2021, 0.300, 'active'),
('SKU024', 'Mì JOMO Khoai Tây Lẩu Thái', 'CAT03', 'JOMO', 'Khoai tây lẩu Thái', 80, 5800, 4234, 0, 2022, 0.200, 'active'),
('SKU025', 'Mì JOMO Khoai Tây Hải Sản', 'CAT03', 'JOMO', 'Khoai tây hải sản', 80, 5500, 4015, 0, 2023, 0.120, 'active'),
('SKU026', 'Mì JOMO Khoai Tây Chay', 'CAT03', 'JOMO', 'Khoai tây chay', 80, 5200, 3796, 0, 2023, 0.080, 'active'),
('SKU030', 'Cháo Gấu Đỏ Thịt Bằm', 'CAT04', 'Gấu Đỏ', 'Thịt bằm', 50, 6000, 4200, 0, 2014, 0.700, 'active'),
('SKU031', 'Cháo Gấu Đỏ Tổ Yến Thịt Bằm', 'CAT04', 'Gấu Đỏ', 'Tổ yến thịt bằm', 50, 8000, 5600, 0, 2018, 0.500, 'active'),
('SKU032', 'Cháo Gấu Đỏ Gà', 'CAT04', 'Gấu Đỏ', 'Gà', 50, 6000, 4200, 0, 2014, 0.600, 'active'),
('SKU033', 'Cháo Gấu Đỏ Cá Hồi', 'CAT04', 'Gấu Đỏ', 'Cá hồi', 50, 8500, 5950, 0, 2020, 0.350, 'active'),
('SKU034', 'Cháo Gấu Đỏ Tôm', 'CAT04', 'Gấu Đỏ', 'Tôm', 50, 6000, 4200, 0, 2015, 0.250, 'active'),
('SKU035', 'Cháo Gấu Đỏ Sườn Non', 'CAT04', 'Gấu Đỏ', 'Sườn non', 50, 6500, 4550, 0, 2017, 0.180, 'active'),
('SKU036', 'Cháo Gấu Đỏ Lươn', 'CAT04', 'Gấu Đỏ', 'Lươn', 50, 7000, 4900, 0, 2021, 0.100, 'active'),
('SKU037', 'Cháo Gấu Đỏ Đậu Xanh', 'CAT04', 'Gấu Đỏ', 'Đậu xanh', 50, 5500, 3850, 0, 2016, 0.080, 'active'),
('SKU040', 'Phở Gấu Đỏ Bò', 'CAT05', 'Gấu Đỏ', 'Bò', 65, 5000, 3950, 1, 2013, 0.600, 'active'),
('SKU041', 'Phở Gấu Đỏ Gà', 'CAT05', 'Gấu Đỏ', 'Gà', 65, 5000, 3950, 0, 2013, 0.400, 'active'),
('SKU042', 'Hủ Tiếu Gấu Đỏ Nam Vang', 'CAT05', 'Gấu Đỏ', 'Nam Vang', 65, 5000, 3950, 0, 2015, 0.300, 'active'),
('SKU043', 'Phở Gấu Đỏ Bò Viên', 'CAT05', 'Gấu Đỏ', 'Bò viên', 65, 5500, 4345, 0, 2018, 0.200, 'active'),
('SKU044', 'Hủ Tiếu Gấu Đỏ Mì', 'CAT05', 'Gấu Đỏ', 'Hủ tiếu mì', 65, 4500, 3555, 0, 2016, 0.150, 'active'),
('SKU045', 'Phở Gấu Đỏ Chay', 'CAT05', 'Gấu Đỏ', 'Chay', 65, 4800, 3792, 0, 2020, 0.080, 'active'),
('SKU046', 'Bún Bò Gấu Đỏ', 'CAT05', 'Gấu Đỏ', 'Bún bò', 65, 5000, 3950, 0, 2022, 0.060, 'active'),
('SKU050', 'Mì Trứng Vàng Tôm Hành', 'CAT06', 'Trứng Vàng', 'Tôm hành', 65, 3000, 2400, 0, 2010, 0.400, 'active'),
('SKU051', 'Mì Trứng Vàng Bò Hầm', 'CAT06', 'Trứng Vàng', 'Bò hầm', 65, 3000, 2400, 0, 2010, 0.300, 'active'),
('SKU052', 'Mì Trứng Vàng Gà Hầm', 'CAT06', 'Trứng Vàng', 'Gà hầm', 65, 3000, 2400, 0, 2011, 0.200, 'active'),
('SKU053', 'Mì Trứng Vàng Hải Sản', 'CAT06', 'Trứng Vàng', 'Hải sản', 65, 3200, 2560, 0, 2015, 0.100, 'active'),
('SKU054', 'Mì Mộc Việt Chay', 'CAT06', 'Mộc Việt', 'Chay', 65, 3500, 2800, 0, 2018, 0.150, 'active'),
('SKU055', 'Mì Mộc Việt Rau Nấm', 'CAT06', 'Mộc Việt', 'Rau nấm', 65, 3500, 2800, 0, 2019, 0.120, 'active'),
('SKU056', 'Mì Mộc Việt Tôm', 'CAT06', 'Mộc Việt', 'Tôm', 65, 3500, 2800, 0, 2020, 0.080, 'active'),
('SKU057', 'Mì Trứng Vàng Sườn Hầm', 'CAT06', 'Trứng Vàng', 'Sườn hầm', 65, 3000, 2400, 0, 2013, 0.070, 'active'),
('SKU058', 'Mì Mộc Việt Gà Hầm', 'CAT06', 'Mộc Việt', 'Gà hầm', 65, 3500, 2800, 0, 2021, 0.050, 'active'),
('SKU059', 'Mì Trứng Vàng Kim Chi', 'CAT06', 'Trứng Vàng', 'Kim chi', 65, 3200, 2560, 0, 2022, 0.040, 'active');


-- ----------------------------------------
-- Table: material_types
-- ----------------------------------------

INSERT INTO `material_types` (`material_type_id`, `material_name`, `material_name_en`, `unit`, `is_imported`, `import_origin`, `cogs_share_pct`, `price_volatility`) VALUES
('MAT01', 'Bột mì', 'Wheat Flour', 'kg', 1, 'Úc', 40.00, 'high'),
('MAT02', 'Dầu cọ', 'Palm Oil', 'kg', 1, 'Indonesia', 18.00, 'high'),
('MAT03', 'Gia vị & phụ gia', 'Seasoning & Additives', 'kg', 0, 'Nội địa', 12.00, 'medium'),
('MAT04', 'Bao bì', 'Packaging', 'đơn vị', 0, 'Nội địa', 10.00, 'low'),
('MAT05', 'Năng lượng (gas + điện)', 'Energy', 'kWh_eq', 0, 'Nội địa', 8.00, 'medium');


-- ----------------------------------------
-- Table: suppliers
-- ----------------------------------------

INSERT INTO `suppliers` (`supplier_id`, `supplier_name`, `material_type_id`, `country`, `is_primary`) VALUES
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
('SUP14', 'EVN Southern', 'MAT05', 'VN', 0);


-- ----------------------------------------
-- Table: sales_channels
-- ----------------------------------------

INSERT INTO `sales_channels` (`channel_id`, `channel_name`, `channel_name_en`, `revenue_share_pct`, `description`) VALUES
('CH01', 'Kênh truyền thống (GT)', 'General Trade', 60.00, 'Tạp hóa, đại lý, chợ truyền thống — kênh chủ lực'),
('CH02', 'Kênh hiện đại (MT)', 'Modern Trade', 25.00, 'Siêu thị, CVSL: Co.opmart, Bách Hóa Xanh, WinMart'),
('CH03', 'Xuất khẩu', 'Export', 12.00, 'Cambodia, Đông Âu, Cuba'),
('CH04', 'Online / E-commerce', 'Online', 3.00, 'Shopee, Lazada, TikTok Shop');


-- ----------------------------------------
-- Table: regions
-- ----------------------------------------

INSERT INTO `regions` (`region_id`, `region_name`, `population_million`, `revenue_share_pct`, `primary_factory_id`) VALUES
('REG01', 'Miền Bắc', 35.0, 28.00, 'F03'),
('REG02', 'Miền Trung', 20.0, 12.00, 'F04'),
('REG03', 'Miền Nam (TP.HCM & Đông Nam Bộ)', 22.0, 32.00, 'F01'),
('REG04', 'Tây Nam Bộ', 18.0, 16.00, 'F02'),
('REG05', 'Xuất khẩu', NULL, 12.00, 'F01');


-- ----------------------------------------
-- Table: cost_categories
-- ----------------------------------------

INSERT INTO `cost_categories` (`cost_category_id`, `category_name`, `category_name_en`, `is_fixed`, `typical_cogs_share_pct`) VALUES
('CC01', 'Nguyên vật liệu', 'Raw Materials', 0, 70.00),
('CC02', 'Nhân công trực tiếp', 'Direct Labor', 0, 7.00),
('CC03', 'Năng lượng (gas + điện)', 'Energy', 0, 8.00),
('CC04', 'Khấu hao máy móc & nhà xưởng', 'Depreciation', 1, 8.00),
('CC05', 'Nhân công gián tiếp & quản lý NM', 'Indirect Labor & Mgmt', 1, 4.00),
('CC06', 'Chi phí sản xuất khác', 'Other Manufacturing', 0, 3.00);


SET FOREIGN_KEY_CHECKS = 1;
