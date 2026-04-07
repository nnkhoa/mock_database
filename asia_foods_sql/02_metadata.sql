-- ============================================================
-- instant_noodle_demo — Metadata
-- Exported: 2026-04-07 20:59:00
-- ============================================================

USE `instant_noodle_demo`;

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------------------
-- Table: _meta_tables
-- ----------------------------------------

INSERT INTO `_meta_tables` (`table_name`, `description_vi`, `description_en`, `business_context`, `row_count_estimate`) VALUES
('cost_allocations', 'Phân bổ chi phí sản xuất theo nhà máy × tháng × loại chi phí', 'Monthly cost allocations by factory and category', 'Dùng breakdown cost structure. NM Đà Nẵng có tỷ trọng chi phí cố định cao do utilization thấp.', 540),
('cost_categories', 'Phân loại chi phí sản xuất: nguyên liệu, nhân công, năng lượng, khấu hao, khác', 'Manufacturing cost categories', 'Nguyên vật liệu chiếm ~70% COGS. Khấu hao là chi phí cố định lớn nhất.', 6),
('factories', 'Danh sách 5 nhà máy sản xuất của Asia Foods, phân bổ 3 miền Bắc-Trung-Nam', 'List of 5 Asia Foods manufacturing plants across 3 regions', 'Mỗi nhà máy có công suất thiết kế, vị trí, và vai trò riêng. An Phú là trụ sở chính, Nam Tân Uyên mới nhất, Gò Vấp sản xuất dòng đặc biệt.', 5),
('material_purchases', 'Đơn mua nguyên liệu — track giá mua theo thời gian, nhà máy, NCC', 'Material purchase orders tracking price over time', 'Dùng phân tích procurement efficiency giữa các nhà máy. Giá bột mì tăng ~18% trong 18 tháng.', 1350),
('material_types', 'Loại nguyên liệu đầu vào: bột mì, dầu cọ, gia vị, bao bì, năng lượng', 'Raw material types with import status and COGS share', 'Bột mì (40% COGS, nhập Úc) và dầu cọ (18% COGS, nhập Indonesia) là hai nguyên liệu biến động giá mạnh nhất.', 5),
('product_categories', 'Phân loại sản phẩm: Mì gói, Mì ly, Cháo, JOMO, Phở/HT, Mì Trứng Vàng & Mộc Việt', 'Product categories with margin profiles and volume shares', 'Cháo margin cao nhất (~30%), Mì gói volume lớn nhất (~55%). JOMO là dòng trung cấp.', 6),
('production_lines', 'Dây chuyền sản xuất tại mỗi nhà máy, mỗi dây chuyền chuyên 1 loại sản phẩm', 'Production lines per factory, each specialized for one product type', 'Mỗi dây chuyền có công suất riêng. L01-04 là dây chuyền mì ly mới tại An Phú (commissioned 2025-04-15).', 16),
('production_orders', 'Lệnh sản xuất hàng ngày — 1 dòng = 1 ca sản xuất trên 1 dây chuyền', 'Daily production orders per shift per line', 'Track input/output/wastage. Dùng tính capacity utilization, wastage rate, labor productivity.', 28000),
('products', 'Danh mục ~50 SKU sản phẩm, bao gồm tất cả dòng mì-cháo-phở của Asia Foods', '~50 SKUs with Pareto-distributed popularity weights', 'Top 20% SKU chiếm ~80% doanh số. Mì Gấu Đỏ Tôm Chua Cay là SKU bán chạy nhất.', 50),
('regions', 'Khu vực thị trường: Miền Bắc, Miền Trung, Miền Nam, Tây Nam Bộ, Xuất khẩu', 'Market regions', 'Miền Nam 32% doanh thu (lớn nhất). Xuất khẩu chủ yếu sang Cambodia, Đông Âu.', 5),
('sales_channels', 'Kênh phân phối: GT (tạp hóa), MT (siêu thị), Xuất khẩu, Online', 'Distribution channels', 'GT chiếm 60% doanh thu, là kênh mạnh nhất của Gấu Đỏ ở nông thôn.', 4),
('sales_order_items', 'Chi tiết line item trong đơn bán hàng — 1 dòng = 1 SKU trong 1 đơn', 'Line items in sales orders', 'Drill-down từ sales_orders để phân tích theo từng SKU cụ thể.', 150000),
('sales_orders', 'Đơn bán hàng tổng hợp — phân tích doanh thu theo kênh/vùng/nhà máy', 'Sales orders with revenue and COGS', 'Grain: 1 đơn hàng. Cross với factories, channels, regions để phân tích đa chiều.', 40000),
('suppliers', 'Nhà cung cấp nguyên liệu, bao gồm cả nhập khẩu và nội địa', 'Suppliers for raw materials', 'Interflour Vietnam là NCC bột mì chính, Bunge là NCC dầu cọ chính.', 14);


-- ----------------------------------------
-- Table: _meta_columns
-- ----------------------------------------

INSERT INTO `_meta_columns` (`id`, `table_name`, `column_name`, `data_type`, `description_vi`, `description_en`, `unit`, `example_values`) VALUES
(1, 'factories', 'factory_id', 'VARCHAR(3)', 'Mã nhà máy', 'Factory ID', NULL, 'F01, F02, F03, F04, F05'),
(2, 'factories', 'designed_capacity_million_packs_month', 'DECIMAL(10,1)', 'Công suất thiết kế', 'Designed capacity', 'triệu gói/tháng', '105.0, 130.0, 65.0, 35.0, 25.0'),
(3, 'production_orders', 'actual_qty_packs', 'INT', 'Sản lượng thực tế', 'Actual output', 'gói', '150000, 200000'),
(4, 'production_orders', 'wastage_qty_packs', 'INT', 'Số lượng hao hụt/phế phẩm', 'Wastage quantity', 'gói', '3000, 5000'),
(5, 'material_purchases', 'unit_price_vnd', 'DECIMAL(12,2)', 'Đơn giá mua nguyên liệu', 'Unit purchase price', 'VND/kg', '9500, 11200'),
(6, 'cost_allocations', 'amount_vnd', 'DECIMAL(15,0)', 'Số tiền chi phí phân bổ', 'Cost amount', 'VND', '80000000000'),
(7, 'sales_orders', 'total_revenue_vnd', 'DECIMAL(15,0)', 'Tổng doanh thu đơn hàng', 'Order revenue', 'VND', '250000000'),
(8, 'sales_orders', 'total_cogs_vnd', 'DECIMAL(15,0)', 'Tổng giá vốn đơn hàng', 'Order COGS', 'VND', '200000000'),
(9, 'sales_order_items', 'unit_price_vnd', 'DECIMAL(12,0)', 'Đơn giá bán sản phẩm', 'Selling unit price', 'VND/gói', '3500, 7000, 5500'),
(10, 'products', 'popularity_weight', 'DECIMAL(5,3)', 'Trọng số phổ biến (Pareto 80/20)', 'Popularity weight', NULL, '1.000, 0.500, 0.100');


-- ----------------------------------------
-- Table: _meta_kpi
-- ----------------------------------------

INSERT INTO `_meta_kpi` (`kpi_name`, `formula_sql`, `description_vi`, `related_questions`) VALUES
('Capacity Utilization %', 'ROUND(SUM(actual_qty_packs) / (designed_capacity_million_packs_month * 1000000 / 30 * COUNT(DISTINCT production_date)) * 100, 1)', 'Tỷ lệ sử dụng công suất = Sản lượng thực tế / Công suất thiết kế × 100.', 'Câu 2, 4, 5'),
('Gross Margin %', 'ROUND((SUM(total_revenue_vnd) - SUM(total_cogs_vnd)) / SUM(total_revenue_vnd) * 100, 1)', 'Biên lợi nhuận gộp = (Doanh thu - Giá vốn) / Doanh thu × 100. Target toàn hệ thống ~20%.', 'Câu 1, 2, 5'),
('Labor Productivity', 'ROUND(SUM(actual_qty_packs) / SUM(labor_hours), 0)', 'Năng suất lao động = Sản lượng / Giờ công. Đơn vị: gói/giờ công.', 'Câu 4'),
('Material Cost per Million Packs', 'ROUND(SUM(total_amount_vnd) / (SUM(quantity_kg) / avg_kg_per_million_packs) / 1e6, 0)', 'Chi phí nguyên liệu trên 1 triệu gói sản phẩm.', 'Câu 3, 5'),
('Revenue per Factory per Month', 'SUM(total_revenue_vnd) GROUP BY factory_id, DATE_FORMAT(order_date, \'%Y-%m\')', 'Doanh thu theo nhà máy theo tháng.', 'Câu 1'),
('Wastage Rate %', 'ROUND(SUM(wastage_qty_packs) / (SUM(actual_qty_packs) + SUM(wastage_qty_packs)) * 100, 2)', 'Tỷ lệ hao hụt = Số lượng phế phẩm / (Sản lượng + Phế phẩm) × 100.', 'Câu 4, 5');


-- ----------------------------------------
-- Table: _meta_glossary
-- ----------------------------------------

INSERT INTO `_meta_glossary` (`term_vi`, `term_en`, `definition`, `related_table`) VALUES
('ASP', 'Average Selling Price', 'Giá bán bình quân trên mỗi đơn vị sản phẩm (VND/gói).', 'sales_order_items'),
('Biên lợi nhuận gộp', 'Gross Margin', 'Tỷ lệ phần trăm lợi nhuận gộp trên doanh thu. Gross Margin % = (Revenue - COGS) / Revenue × 100.', 'sales_orders'),
('Công suất thiết kế', 'Designed Capacity', 'Sản lượng tối đa mà nhà máy có thể sản xuất, đơn vị: triệu gói/tháng.', 'factories'),
('Giá vốn hàng bán', 'COGS', 'Chi phí trực tiếp sản xuất sản phẩm, bao gồm nguyên liệu, nhân công, năng lượng, khấu hao.', 'cost_allocations'),
('Kênh hiện đại (MT)', 'Modern Trade', 'Hệ thống siêu thị, cửa hàng tiện lợi: Co.opmart, Bách Hóa Xanh, WinMart, Circle K.', 'sales_channels'),
('Kênh truyền thống (GT)', 'General Trade', 'Hệ thống phân phối qua tạp hóa, đại lý, chợ truyền thống. Chiếm ~60% doanh thu.', 'sales_channels'),
('Năng suất lao động', 'Labor Productivity', 'Số gói sản phẩm sản xuất trên mỗi giờ công lao động.', 'production_orders'),
('NVL nhập khẩu', 'Imported Raw Materials', 'Nguyên vật liệu nhập từ nước ngoài: bột mì (Úc), dầu cọ (Indonesia). Chiếm ~58% COGS.', 'material_purchases'),
('Phân khúc bình dân', 'Value Segment', 'Sản phẩm giá 1.500-3.500 VND/gói, phục vụ khách hàng nhạy giá. Gấu Đỏ là thương hiệu chủ lực.', 'product_categories'),
('Tỷ lệ hao hụt', 'Wastage Rate', 'Phần trăm sản phẩm bị loại trong quá trình sản xuất do lỗi chất lượng.', 'production_orders');


SET FOREIGN_KEY_CHECKS = 1;
