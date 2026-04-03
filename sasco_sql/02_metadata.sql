-- ============================================================================
-- SASCO Demo Database - Metadata Tables
-- Mo ta: Populate _meta_tables, _meta_columns, _meta_kpi, _meta_glossary
-- ============================================================================

USE sasco_demo;

-- ============================================================================
-- _meta_tables
-- ============================================================================
INSERT INTO _meta_tables (table_name, description_vi, description_en, business_context, record_count_estimate) VALUES
('terminals', 'Nhà ga / sân bay nơi SASCO vận hành dịch vụ', 'Terminals / airports where SASCO operates', 'SASCO hoạt động tại 3 nhà ga TSN (T1 nội địa, T2 quốc tế, T3 hỗn hợp mới), Cam Ranh quốc tế, và Phú Quốc hỗn hợp.', 5),
('business_lines', 'Các mảng kinh doanh chính của SASCO', 'Main business lines of SASCO', '4 mảng: Phòng chờ thương gia (~30% DT, margin ~80%), Miễn thuế (~35% DT, margin ~67%), F&B & Bán lẻ (~25% DT, margin ~75%), Dịch vụ khác (~10% DT).', 4),
('locations', 'Các điểm kinh doanh cụ thể', 'Specific business locations', 'Bao gồm 15 phòng chờ, 5 cửa hàng miễn thuế, 12 nhà hàng/café/shop, 5 điểm dịch vụ. T3 mở từ 04/2025.', 37),
('lounges', 'Thông tin chi tiết phòng chờ thương gia', 'Lounge details (extends locations)', 'Phòng chờ là mảng margin cao nhất (~80%). 2 thương hiệu: Lotus Lounge và The SENS. Capacity 50-120 ghế.', 15),
('nationality_groups', 'Nhóm quốc tịch hành khách', 'Passenger nationality groups', 'Top 10 quốc tịch + Châu Âu khác + Khác + Nội địa. Dùng để phân tích spend/PAX theo quốc tịch. Hàn Quốc chi tiêu cao nhất, Ấn Độ đang tăng mạnh.', 13),
('product_categories', 'Danh mục sản phẩm/dịch vụ (2 cấp)', 'Product/service categories (2-level hierarchy)', 'Hierarchy: top-level → sub-category. Miễn thuế: Mỹ phẩm, Rượu, Thời trang, Đặc sản, Bánh kẹo, Điện tử. F&B: Phở, Á, Âu, Café, Ăn nhanh.', 25),
('products', 'Sản phẩm/dịch vụ cụ thể (~400 SKU)', 'Specific products/services', 'Pareto: top 20% SKU chiếm ~80% doanh thu. Tên sản phẩm thực tế. nationality_preference cho biết quốc tịch nào ưa thích sản phẩm.', 400),
('passenger_traffic', 'Lưu lượng hành khách theo ngày × nhà ga × quốc tịch', 'Daily passenger traffic by terminal and nationality', 'Grain: 1 dòng = 1 ngày × 1 terminal × 1 nationality. TSN ~80K PAX/ngày (30K QT + 50K NĐ). Dùng để tính spend/PAX, conversion rate.', 120000),
('sales_transactions', 'Giao dịch bán hàng chi tiết (line item)', 'Sales transactions at line item level', 'Grain: 1 dòng = 1 line item. Bao gồm tất cả mảng KD. Denormalized business_line_id và terminal_id để query nhanh. Data 18 tháng (01/2024-06/2025).', 1000000),
('lounge_visits', 'Lượt sử dụng phòng chờ theo giờ', 'Hourly lounge visits', 'Grain: 1 dòng = 1 phòng chờ × 1 ngày × 1 khung giờ (0-23). Utilization_rate = guest_count/capacity. Dùng cho heatmap phân tích hiệu suất.', 180000),
('_meta_tables', 'Metadata mô tả các bảng trong database', 'Table-level metadata', 'AI engine dùng để hiểu cấu trúc database trước khi query.', 14),
('_meta_columns', 'Metadata mô tả các cột trong từng bảng', 'Column-level metadata', 'AI engine dùng để hiểu ý nghĩa, đơn vị, ví dụ của từng cột.', 80),
('_meta_kpi', 'Công thức KPI cốt lõi', 'Core KPI formulas', 'AI engine dùng để tính toán KPI chính xác thay vì đoán.', 15),
('_meta_glossary', 'Thuật ngữ ngành hàng không sân bay', 'Aviation/airport industry glossary', 'AI engine dùng để hiểu câu hỏi tiếng Việt chứa thuật ngữ chuyên ngành.', 25);

-- ============================================================================
-- _meta_columns (key columns for AI understanding)
-- ============================================================================
INSERT INTO _meta_columns (table_name, column_name, data_type, description_vi, description_en, unit, example_values) VALUES
-- terminals
('terminals', 'terminal_id', 'TINYINT', 'Mã nhà ga', 'Terminal ID', NULL, '1=T1, 2=T2, 3=T3, 4=CR, 5=PQ'),
('terminals', 'terminal_name', 'VARCHAR(100)', 'Tên nhà ga tiếng Việt', 'Terminal name in Vietnamese', NULL, 'Nhà ga T1 Quốc nội, Nhà ga T2 Quốc tế'),
('terminals', 'terminal_code', 'VARCHAR(10)', 'Mã viết tắt nhà ga', 'Short code', NULL, 'T1, T2, T3, CR, PQ'),
('terminals', 'terminal_type', 'ENUM', 'Loại nhà ga', 'Terminal type', NULL, 'Quốc tế, Nội địa, Hỗn hợp'),
('terminals', 'open_date', 'DATE', 'Ngày bắt đầu khai thác', 'Opening date', NULL, 'T3: 2025-04-01, PQ: 2024-11-01'),
-- business_lines
('business_lines', 'business_line_id', 'TINYINT', 'Mã mảng kinh doanh', 'Business line ID', NULL, '1=Phòng chờ, 2=Miễn thuế, 3=F&B, 4=Dịch vụ'),
('business_lines', 'business_line_name', 'VARCHAR(100)', 'Tên mảng kinh doanh', 'Business line name', NULL, 'Phòng chờ thương gia, Cửa hàng miễn thuế'),
-- locations
('locations', 'location_id', 'SMALLINT', 'Mã điểm kinh doanh', 'Location ID', NULL, '101-115: phòng chờ, 201-205: DF, 301-312: F&B, 401-405: DV'),
('locations', 'location_name', 'VARCHAR(150)', 'Tên điểm kinh doanh', 'Location name', NULL, 'Lotus Lounge Quốc tế 1 (T2), SASCO Duty Free T3'),
('locations', 'open_date', 'DATE', 'Ngày bắt đầu hoạt động', 'Opening date', NULL, 'T3 locations: 2025-04-01'),
-- lounges
('lounges', 'lounge_type', 'ENUM', 'Loại phòng chờ', 'Lounge type', NULL, 'Quốc tế, Nội địa, Hỗn hợp'),
('lounges', 'max_capacity_per_hour', 'INT', 'Sức chứa tối đa mỗi giờ', 'Max capacity per hour', 'lượt khách', '60-120'),
('lounges', 'base_price_vnd', 'INT', 'Giá phòng chờ chuẩn', 'Standard lounge price', 'VND/khách', '350000-850000'),
-- nationality_groups
('nationality_groups', 'nationality_group_id', 'TINYINT', 'Mã nhóm quốc tịch (0=Nội địa)', 'Nationality group ID', NULL, '0=NĐ, 1=Hàn, 2=TQ, 3=ĐL, 4=Nhật, 5=Mỹ, 6=ẤnĐộ'),
('nationality_groups', 'avg_spend_per_pax_vnd', 'INT', 'Chi tiêu trung bình/khách tại SASCO', 'Average spend per PAX at SASCO', 'VND', 'Hàn: 850000, Ấn Độ: 280000'),
('nationality_groups', 'pax_share_pct', 'DECIMAL(5,2)', 'Tỷ trọng PAX tại TSN - baseline đầu kỳ', 'PAX share baseline', '%', 'Hàn: 28%, TQ: 18%'),
-- product_categories
('product_categories', 'category_id', 'SMALLINT', 'Mã danh mục', 'Category ID', NULL, '10-60: miễn thuế, 70-74: F&B, 80-82: lounge, 90-93: DV'),
('product_categories', 'parent_category_id', 'SMALLINT', 'Danh mục cha (NULL nếu top-level)', 'Parent category', NULL, '11→10 (Nước hoa → Mỹ phẩm & Nước hoa)'),
-- products
('products', 'unit_price_vnd', 'DECIMAL(12,0)', 'Giá bán', 'Selling price', 'VND', 'DF: 200K-15M, F&B: 40K-350K, Lounge: 350K-850K'),
('products', 'cost_price_vnd', 'DECIMAL(12,0)', 'Giá vốn', 'Cost price', 'VND', 'Margin: DF ~33%, Lounge ~20%, F&B ~25%'),
('products', 'popularity_weight', 'DECIMAL(5,4)', 'Trọng số phổ biến (Pareto)', 'Popularity weight', NULL, 'Top SKU: 0.08-0.15, thấp: 0.001-0.005'),
('products', 'nationality_preference', 'VARCHAR(100)', 'Quốc tịch ưa thích (JSON)', 'Preferred nationalities', NULL, '[1,3,4] = Hàn, Đài, Nhật ưa thích'),
-- passenger_traffic
('passenger_traffic', 'traffic_date', 'DATE', 'Ngày', 'Date', NULL, '2024-01-01 đến 2025-06-30'),
('passenger_traffic', 'passenger_type', 'ENUM', 'Loại hành khách', 'Passenger type', NULL, 'Quốc tế, Nội địa'),
('passenger_traffic', 'pax_count', 'INT', 'Số lượng hành khách', 'Passenger count', 'lượt', 'TSN QT: ~2500/ngày/quốc tịch lớn'),
-- sales_transactions
('sales_transactions', 'transaction_date', 'DATE', 'Ngày giao dịch', 'Transaction date', NULL, '2024-01-01 đến 2025-06-30'),
('sales_transactions', 'total_revenue_vnd', 'DECIMAL(15,0)', 'Doanh thu = quantity × unit_price', 'Revenue', 'VND', 'DF: 200K-15M, F&B: 40K-350K'),
('sales_transactions', 'cost_vnd', 'DECIMAL(15,0)', 'Giá vốn', 'COGS', 'VND', 'Dùng tính biên lợi nhuận gộp'),
('sales_transactions', 'nationality_group_id', 'TINYINT', 'Quốc tịch khách (NULL nếu nội địa/unknown)', 'Customer nationality', NULL, 'Có giá trị cho duty-free, NULL cho nội địa'),
-- lounge_visits
('lounge_visits', 'hour_slot', 'TINYINT', 'Khung giờ 0-23', 'Hour slot', 'giờ', '6=6AM, 18=6PM. Peak: 6-9 (NĐ), 18-21 (QT)'),
('lounge_visits', 'guest_count', 'INT', 'Số lượt khách trong khung giờ', 'Guest count per hour', 'lượt', '5-100 tùy phòng chờ và giờ'),
('lounge_visits', 'utilization_rate', 'DECIMAL(5,2)', 'Tỷ lệ sử dụng = guest/capacity × 100', 'Utilization rate', '%', 'Tốt: >70%, Thấp: <40%, Peak: >90%');

-- ============================================================================
-- _meta_kpi
-- ============================================================================
INSERT INTO _meta_kpi (kpi_name, formula_sql, description_vi, related_questions) VALUES
('Tổng doanh thu', 'SUM(total_revenue_vnd)', 'Tổng doanh thu tất cả mảng kinh doanh', 'Doanh thu tháng/quý/năm? Doanh thu theo mảng?'),
('Doanh thu theo mảng', 'SUM(total_revenue_vnd) GROUP BY business_line_id', 'Doanh thu phân theo 4 mảng kinh doanh', 'Mảng nào đóng góp nhiều nhất? Mảng nào tăng trưởng?'),
('Lợi nhuận gộp', 'SUM(total_revenue_vnd) - SUM(cost_vnd)', 'Lợi nhuận gộp = Doanh thu - Giá vốn', 'Biên lợi nhuận gộp? Mảng nào margin cao?'),
('Biên lợi nhuận gộp', '(SUM(total_revenue_vnd) - SUM(cost_vnd)) / SUM(total_revenue_vnd) * 100', 'Tỷ lệ lợi nhuận gộp trên doanh thu (%)', 'Biên lợi nhuận bao nhiêu? Cải thiện hay giảm?'),
('YoY Growth', '(SUM(revenue_kỳ_này) / SUM(revenue_cùng_kỳ) - 1) * 100', 'Tăng trưởng so với cùng kỳ năm trước (%)', 'Tăng trưởng bao nhiêu? So với năm ngoái?'),
('Spend per PAX', 'SUM(total_revenue_vnd WHERE business_line_id=2) / SUM(pax_count WHERE passenger_type=Quốc tế)', 'Chi tiêu trung bình mỗi hành khách quốc tế tại cửa hàng miễn thuế', 'Khách chi bao nhiêu? Quốc tịch nào chi nhiều?'),
('Conversion rate miễn thuế', 'COUNT(DISTINCT transaction_id WHERE bl=2) / SUM(pax_count WHERE QT) * 100', 'Tỷ lệ hành khách quốc tế mua hàng miễn thuế (%)', 'Bao nhiêu % khách mua? Conversion có tăng?'),
('Basket size', 'SUM(total_revenue_vnd) / COUNT(DISTINCT transaction_group)', 'Giá trị trung bình mỗi đơn hàng', 'Giá trị đơn hàng trung bình? Basket tăng hay giảm?'),
('Utilization rate phòng chờ', 'AVG(guest_count / capacity * 100)', 'Tỷ lệ sử dụng phòng chờ trung bình (%)', 'Phòng chờ nào hiệu quả? Utilization bao nhiêu?'),
('RevPASH', 'SUM(revenue) / (capacity * operating_hours)', 'Revenue per Available Seat Hour - doanh thu trên mỗi ghế-giờ', 'Hiệu suất phòng chờ? RevPASH bao nhiêu?'),
('Revenue per terminal', 'SUM(total_revenue_vnd) GROUP BY terminal_id', 'Doanh thu phân theo nhà ga', 'Nhà ga nào đóng góp nhiều? T3 đóng góp bao nhiêu?'),
('T3 ramp-up rate', 'SUM(revenue_week_n) / SUM(revenue_week_n-1) - 1', 'Tốc độ tăng trưởng doanh thu T3 theo tuần', 'T3 tăng bao nhiêu mỗi tuần? Đúng kỳ vọng?'),
('PAX share by nationality', 'pax_count_nationality / SUM(pax_count) * 100', 'Tỷ trọng hành khách theo quốc tịch (%)', 'Quốc tịch nào đông nhất? Cơ cấu thay đổi?'),
('Spend per PAX per nationality', 'SUM(revenue WHERE nationality=X) / SUM(pax WHERE nationality=X)', 'Chi tiêu trung bình theo từng quốc tịch', 'Khách Hàn chi bao nhiêu? Ấn Độ chi bao nhiêu?');

-- ============================================================================
-- _meta_glossary
-- ============================================================================
INSERT INTO _meta_glossary (term_vi, term_en, definition) VALUES
('PAX', 'PAX (Passengers)', 'Số lượt hành khách. 1 PAX = 1 lượt đi qua nhà ga (không phân biệt chiều đi/đến).'),
('Hành khách quốc tế', 'International passenger', 'Hành khách trên các chuyến bay quốc tế. Có quyền mua hàng miễn thuế.'),
('Hành khách nội địa', 'Domestic passenger', 'Hành khách trên các chuyến bay nội địa Việt Nam.'),
('Miễn thuế', 'Duty-free', 'Hàng hóa bán tại khu vực cách ly sân bay quốc tế, không chịu thuế GTGT và thuế nhập khẩu.'),
('Phòng chờ thương gia', 'Business lounge', 'Khu vực phòng chờ cao cấp tại sân bay, cung cấp đồ ăn, thức uống, WiFi, ghế massage. Khách trả phí hoặc dùng thẻ ưu tiên.'),
('Utilization rate', 'Utilization rate', 'Tỷ lệ sử dụng phòng chờ = số khách thực tế / sức chứa × 100%. >70% là tốt, >90% là quá tải.'),
('RevPASH', 'Revenue per Available Seat Hour', 'Doanh thu trên mỗi ghế-giờ khả dụng. KPI đo hiệu suất phòng chờ. = Doanh thu / (Số ghế × Số giờ mở cửa).'),
('Spend per PAX', 'Spend per passenger', 'Chi tiêu trung bình mỗi hành khách = Tổng doanh thu / Tổng PAX. Dùng cho mảng miễn thuế.'),
('Conversion rate', 'Conversion rate', 'Tỷ lệ chuyển đổi = Số khách mua hàng / Tổng khách đi qua × 100%.'),
('Basket size', 'Average basket size', 'Giá trị trung bình mỗi đơn hàng. = Tổng doanh thu / Số đơn hàng.'),
('YoY', 'Year-over-Year', 'So với cùng kỳ năm trước. VD: Q1/2025 vs Q1/2024.'),
('QoQ', 'Quarter-over-Quarter', 'So với quý trước. VD: Q1/2025 vs Q4/2024.'),
('MoM', 'Month-over-Month', 'So với tháng trước.'),
('Biên lợi nhuận gộp', 'Gross margin', 'Tỷ lệ lợi nhuận gộp = (Doanh thu - Giá vốn) / Doanh thu × 100%. SASCO trung bình ~64%.'),
('COGS', 'Cost of Goods Sold', 'Giá vốn hàng bán. Chi phí trực tiếp để có hàng hóa/dịch vụ bán ra.'),
('Concession', 'Concession', 'Mô hình nhận quyền khai thác mặt bằng thương mại trong sân bay. SASCO trả phí thuê cho ACV.'),
('TSN', 'Tan Son Nhat', 'Sân bay Quốc tế Tân Sơn Nhất (SGN), TP.HCM. Hub lớn nhất Việt Nam, ~40 triệu khách/năm.'),
('T1', 'Terminal 1', 'Nhà ga T1 Quốc nội tại sân bay Tân Sơn Nhất.'),
('T2', 'Terminal 2', 'Nhà ga T2 Quốc tế tại sân bay Tân Sơn Nhất.'),
('T3', 'Terminal 3', 'Nhà ga T3 mới tại sân bay Tân Sơn Nhất, khai trương 04/2025. Hỗn hợp quốc tế + nội địa.'),
('Ramp-up', 'Ramp-up', 'Giai đoạn tăng trưởng ban đầu khi một điểm kinh doanh mới mở. Thường mất 3-6 tháng để đạt công suất ổn định.'),
('SKU', 'Stock Keeping Unit', 'Mã đơn vị lưu kho. Mỗi SKU = 1 sản phẩm cụ thể (tên, kích cỡ, mẫu mã).'),
('IATA', 'International Air Transport Association', 'Hiệp hội Vận tải Hàng không Quốc tế. Mã sân bay IATA: SGN (TSN), CXR (Cam Ranh), PQC (Phú Quốc).'),
('ACV', 'Airports Corporation of Vietnam', 'Tổng công ty Cảng hàng không Việt Nam. Cổ đông lớn của SASCO (~49%).'),
('IPPG', 'Imex Pan Pacific Group', 'Tập đoàn Liên Thái Bình Dương. Chủ tịch Johnathan Hạnh Nguyễn. Cổ đông chiến lược của SASCO (~45%).');
