-- ============================================================
-- 02_metadata.sql
-- CANIFA Retail Fashion — Metadata
-- ============================================================

USE canifa_retail_demo;

INSERT INTO `_meta_tables` (table_name, description_vi, description_en, business_context, row_count_approx) VALUES
('categories', 'Bảng phân loại sản phẩm', 'Product categories hierarchy', '11 category: Essentials, Smart Casual, Jeans-Kaki, Thu-Đông, Activewear, Kids, Phụ kiện', 11),
('channels', 'Bảng kênh bán hàng', 'Sales channels (offline + online)', '5 kênh: Cửa hàng, Website, Shopee, TikTok, Lazada', 5),
('inventory_snapshots', 'Bảng snapshot tồn kho cuối tháng', 'Monthly inventory snapshots per store × product', 'Grain: store × product × month', NULL),
('products', 'Bảng sản phẩm — ~500 SKU', '~500 SKUs with pricing and attributes', 'Giá bán, giá vốn, mùa, popularity weight cho mô phỏng Pareto', 500),
('promotions', 'Bảng chương trình khuyến mại', '8 promotional campaigns', 'Bao gồm flash sale, seasonal, bundle, clearance', 8),
('regions', 'Bảng khu vực địa lý — phân vùng kinh doanh', 'Geographic regions for business segmentation', '6 khu vực: HN, MB, MT, HCM, MN, TN', 6),
('returns', 'Bảng trả hàng', 'Product returns', 'Return rate: offline 3%, online 8-14%', NULL),
('sales_transactions', 'Bảng giao dịch bán hàng — grain: 1 line item', 'Sales transactions at line item level', '21 tháng data (07/2023–03/2025), offline + online', NULL),
('store_costs', 'Bảng chi phí vận hành cửa hàng theo tháng', 'Monthly store operating costs', 'Rent, staff, utilities, other', NULL),
('stores', 'Bảng cửa hàng — 110 cửa hàng toàn quốc', '110 retail stores nationwide', 'Chứa thông tin vị trí, diện tích, loại hình, tiền thuê', 110);

INSERT INTO `_meta_columns` (id, table_name, column_name, data_type, description_vi, description_en, unit, example_values) VALUES
(1, 'sales_transactions', 'transaction_date', 'DATE', 'Ngày giao dịch', 'Transaction date', 'ngày', '2024-06-15'),
(2, 'sales_transactions', 'store_id', 'VARCHAR(15)', 'Mã cửa hàng (NULL nếu online)', 'Store ID', '', 'STR-HN-001'),
(3, 'sales_transactions', 'channel_id', 'VARCHAR(10)', 'Mã kênh bán hàng', 'Channel ID', '', 'CH-STORE'),
(4, 'sales_transactions', 'product_id', 'VARCHAR(15)', 'Mã sản phẩm', 'Product ID', '', 'PRD-EM-001'),
(5, 'sales_transactions', 'promo_id', 'VARCHAR(10)', 'Mã KM (NULL nếu không KM)', 'Promotion ID', '', 'PRM-001'),
(6, 'sales_transactions', 'quantity', 'INT', 'Số lượng bán', 'Quantity sold', 'units', '5'),
(7, 'sales_transactions', 'unit_price', 'DECIMAL(12,0)', 'Đơn giá bán thực tế sau giảm', 'Actual selling price', 'VND', '299000'),
(8, 'sales_transactions', 'original_price', 'DECIMAL(12,0)', 'Giá niêm yết gốc', 'Original listed price', 'VND', '399000'),
(9, 'sales_transactions', 'discount_amount', 'DECIMAL(12,0)', 'Tổng tiền giảm giá', 'Total discount amount', 'VND', '500000'),
(10, 'sales_transactions', 'cost_price', 'DECIMAL(12,0)', 'Giá vốn tại thời điểm bán', 'Cost price at time of sale', 'VND', '120000'),
(11, 'sales_transactions', 'revenue', 'DECIMAL(15,0)', 'Doanh thu = quantity × unit_price', 'Revenue', 'VND', '1495000'),
(12, 'sales_transactions', 'gross_profit', 'DECIMAL(15,0)', 'LN gộp = revenue - qty × cost', 'Gross profit', 'VND', '895000'),
(13, 'sales_transactions', 'order_id', 'VARCHAR(20)', 'Mã đơn hàng (nhóm line items)', 'Order ID', '', 'ORD-20240615-001-000123'),
(14, 'products', 'retail_price', 'DECIMAL(12,0)', 'Giá bán lẻ niêm yết', 'Retail price', 'VND', '299000'),
(15, 'products', 'cost_price', 'DECIMAL(12,0)', 'Giá vốn', 'Cost price', 'VND', '95000'),
(16, 'products', 'cost_price_new', 'DECIMAL(12,0)', 'Giá vốn mới từ T9/2024 (cotton +8%)', 'New cost price since Sep 2024', 'VND', '103000'),
(17, 'products', 'popularity_weight', 'DECIMAL(5,3)', 'Trọng số Pareto: >1 bán chạy, <1 chậm', 'Popularity weight for simulation', '', '2.500'),
(18, 'stores', 'area_sqm', 'DECIMAL(8,2)', 'Diện tích mặt bằng', 'Store floor area', 'm²', '120.00'),
(19, 'stores', 'monthly_rent', 'DECIMAL(15,0)', 'Tiền thuê mặt bằng/tháng', 'Monthly rent', 'VND', '80000000'),
(20, 'inventory_snapshots', 'quantity_on_hand', 'INT', 'Số lượng tồn kho', 'Stock on hand', 'units', '150'),
(21, 'inventory_snapshots', 'quantity_received', 'INT', 'Số lượng nhập trong tháng', 'Quantity received this month', 'units', '200'),
(22, 'inventory_snapshots', 'quantity_sold', 'INT', 'Số lượng bán trong tháng', 'Quantity sold this month', 'units', '180'),
(23, 'inventory_snapshots', 'last_received_date', 'DATE', 'Ngày nhập hàng gần nhất', 'Last stock receipt date', 'ngày', '2024-11-15'),
(24, 'store_costs', 'rent', 'DECIMAL(15,0)', 'Tiền thuê mặt bằng', 'Rent', 'VND', '80000000'),
(25, 'store_costs', 'staff_cost', 'DECIMAL(15,0)', 'Chi phí nhân sự (lương+BHXH)', 'Staff cost', 'VND', '35000000'),
(26, 'store_costs', 'total_cost', 'DECIMAL(15,0)', 'Tổng chi phí vận hành', 'Total operating cost', 'VND', '125000000'),
(27, 'returns', 'return_amount', 'DECIMAL(15,0)', 'Giá trị hoàn trả', 'Return amount', 'VND', '299000'),
(28, 'returns', 'reason', 'ENUM', 'Lý do trả hàng', 'Return reason', '', 'Size không vừa');

INSERT INTO `_meta_kpi` (kpi_name, formula_sql, description_vi, related_questions) VALUES
('APT (Average Per Transaction)', 'SELECT SUM(revenue) / COUNT(DISTINCT order_id) FROM sales_transactions', 'Giá trị trung bình mỗi đơn hàng', 'Câu 6'),
('Biên lợi nhuận gộp (Gross Margin %)', 'SELECT (SUM(revenue) - SUM(quantity * cost_price)) / SUM(revenue) * 100 FROM sales_transactions', 'Tỷ lệ lợi nhuận gộp trên doanh thu', 'Câu 5'),
('Discount Depth', 'SELECT AVG(discount_amount / (original_price * quantity)) * 100 FROM sales_transactions WHERE discount_amount > 0', 'Mức giảm giá trung bình khi có KM', 'Câu 2,5'),
('Doanh thu gộp (Gross Revenue)', 'SELECT SUM(quantity * original_price) FROM sales_transactions', 'Tổng doanh thu trước giảm giá', 'Câu 1'),
('Doanh thu thuần (Net Revenue)', 'SELECT SUM(revenue) - COALESCE((SELECT SUM(return_amount) FROM returns),0) FROM sales_transactions', 'Tổng doanh thu sau trừ giảm giá và trả hàng', 'Câu 1,2,5,6'),
('DT/m² (Revenue per sqm)', 'SELECT SUM(s.revenue)/st.area_sqm FROM sales_transactions s JOIN stores st ON s.store_id=st.store_id GROUP BY st.store_id', 'Doanh thu trên mỗi m² mặt bằng, đơn vị VND/m²/tháng', 'Câu 6'),
('Inventory Days', 'SELECT (AVG(quantity_on_hand * p.cost_price) / (SUM(s.quantity * s.cost_price)/30)) FROM inventory_snapshots i JOIN products p ON i.product_id=p.product_id JOIN sales_transactions s ON s.product_id=p.product_id', 'Số ngày quay vòng tồn kho', 'Câu 4'),
('Promotion ROI', 'SELECT (SUM(s.revenue) - p.marketing_spend - p.platform_fee) / (p.marketing_spend + p.platform_fee) FROM sales_transactions s JOIN promotions p ON s.promo_id=p.promo_id GROUP BY p.promo_id', 'ROI của từng chương trình khuyến mại', 'Câu 2'),
('Return Rate', 'SELECT COUNT(*) / (SELECT COUNT(*) FROM sales_transactions) * 100 FROM returns', 'Tỷ lệ trả hàng theo channel', 'Câu 3 follow-up'),
('Sell-through Rate', 'SELECT SUM(quantity_sold) / (SUM(quantity_sold) + SUM(quantity_on_hand)) * 100 FROM inventory_snapshots', 'Tỷ lệ bán hết so với tồn kho', 'Câu 3'),
('SSSG (Same-Store Sales Growth)', 'SELECT (SUM(CASE WHEN YEAR(transaction_date)=2025 THEN revenue END) - SUM(CASE WHEN YEAR(transaction_date)=2024 THEN revenue END)) / SUM(CASE WHEN YEAR(transaction_date)=2024 THEN revenue END) * 100 FROM sales_transactions WHERE store_id IS NOT NULL', 'Tăng trưởng doanh thu cùng cửa hàng so với cùng kỳ', 'Câu 6'),
('UPT (Units Per Transaction)', 'SELECT SUM(quantity) / COUNT(DISTINCT order_id) FROM sales_transactions', 'Số sản phẩm trung bình mỗi đơn hàng', 'Câu 2,6');

INSERT INTO `_meta_glossary` (term_vi, term_en, definition) VALUES
('Aging Stock', 'Hàng tồn lâu', 'Hàng tồn kho >90 ngày kể từ lần nhập cuối — rủi ro lỗi mốt, cần markdown'),
('APT', 'Average Per Transaction', 'Giá trị trung bình mỗi giao dịch = Tổng DT / Số đơn hàng'),
('Biên lợi nhuận gộp', 'Gross Margin', 'Tỷ lệ (Doanh thu - Giá vốn) / Doanh thu, thể hiện hiệu quả kinh doanh cốt lõi'),
('Bundle', 'Combo khuyến mại', 'Chương trình mua nhiều tặng thêm, ví dụ: Mua 3 Tặng 1'),
('Clearance', 'Xả hàng cuối mùa', 'Giảm giá 40-70% để giải phóng hàng seasonal tồn kho'),
('COGS', 'Cost of Goods Sold', 'Giá vốn hàng bán — chi phí sản xuất và nguyên liệu'),
('CR', 'Conversion Rate', 'Tỷ lệ khách vào cửa hàng thực hiện mua hàng'),
('Doanh thu thuần', 'Net Revenue', 'Doanh thu sau khi trừ giảm giá và giá trị hàng trả lại'),
('Flagship', 'Flagship Store', 'Cửa hàng trọng điểm, diện tích lớn, vị trí đắc địa, thể hiện hình ảnh thương hiệu'),
('Flash Sale', 'Flash Sale', 'Chương trình giảm giá ngắn hạn (1-4 ngày) trên kênh online, thường discount sâu 30-60%'),
('Inventory Days', 'Days of Inventory', 'Số ngày trung bình để bán hết tồn kho hiện tại, = (Tồn kho TB / COGS ngày) × 30'),
('Markdown', 'Markdown', 'Giảm giá sản phẩm — thường áp dụng cuối mùa để giải phóng tồn kho'),
('MoM', 'Month-over-Month', 'So sánh tháng trước'),
('Omnichannel', 'Đa kênh', 'Mô hình bán hàng tích hợp offline + online'),
('QoQ', 'Quarter-over-Quarter', 'So sánh quý trước'),
('Season', 'Mùa hàng', 'Phân loại theo mùa: Xuân-Hè (SS), Thu-Đông (FW), 4 Mùa (year-round)'),
('Sell-through Rate', 'Sell-through Rate', 'Tỷ lệ hàng bán được so với tổng hàng nhập, công thức: Sold / (Sold + On-hand)'),
('SKU', 'Stock Keeping Unit', 'Đơn vị quản lý hàng tồn kho — 1 SKU = 1 sản phẩm cụ thể (màu + size)'),
('SSSG', 'Same-Store Sales Growth', 'Tăng trưởng doanh thu của các cửa hàng đã hoạt động ≥12 tháng so với cùng kỳ năm trước'),
('TTTM', 'Shopping Mall Store', 'Cửa hàng trong trung tâm thương mại'),
('UPT', 'Units Per Transaction', 'Số sản phẩm trung bình trong mỗi đơn hàng'),
('YoY', 'Year-over-Year', 'So sánh cùng kỳ năm trước');

