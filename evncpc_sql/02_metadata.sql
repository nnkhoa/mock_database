-- ============================================================
-- evncpc_demo — Metadata
-- Exported: 2026-04-08 10:00:00
-- ============================================================

USE `evncpc_demo`;

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------------------
-- Table: _meta_tables
-- ----------------------------------------

INSERT INTO `_meta_tables` (`table_name`, `description_vi`, `description_en`, `business_context`, `row_count_estimate`) VALUES
('power_companies', 'Danh sách 8 công ty điện lực thành viên EVNCPC (cơ cấu mới từ 1/7/2025)', 'List of 8 EVNCPC subsidiary power companies (restructured from July 2025)', 'Dimension chính. Mỗi PC quản lý 1-3 tỉnh miền Trung. PC01 (Đà Nẵng) và PC02 (Khánh Hòa) là lớn nhất. Có cả TNHH MTV và cổ phần.', 8),
('provinces', '13 tỉnh/thành phố thuộc EVNCPC quản lý, từ Quảng Bình đến Khánh Hòa và Tây Nguyên', '13 provinces/cities managed by EVNCPC across Central Vietnam and Central Highlands', 'Phân theo vùng Duyên hải và Tây Nguyên. Mỗi tỉnh có mức rủi ro bão khác nhau — các tỉnh ven biển rủi ro cao hơn.', 13),
('districts', 'Quận/huyện — mức chi tiết nhất cho phân tích tổn thất và sự cố', 'Districts — most granular level for loss and incident analysis', 'Grain nhỏ nhất cho power_loss_detail. Khu vực đô thị thường có tổn thất thấp hơn nhưng sự cố ảnh hưởng nhiều KH hơn.', 150),
('substations', 'Trạm biến áp — mẫu đại diện phục vụ phân tích tổn thất và đầu tư', 'Substations — representative sample for loss analysis and investment planning', 'Gồm 3 cấp: 110kV, 22kV, 0.4kV. Trạm cũ (trước 2010) thường tổn thất cao hơn. load_rate_pct > 80% là quá tải.', 500),
('grid_assets', 'Tài sản lưới điện — MBA phân phối, recloser, đường dây, tụ bù', 'Grid assets — distribution transformers, reclosers, power lines, capacitor banks', 'Phục vụ phân tích đầu tư cải tạo. Thiết bị condition_rating = Kém cần ưu tiên thay thế.', 800),
('customer_segments', 'Cơ cấu khách hàng theo nhóm biểu giá, theo từng công ty điện lực', 'Customer mix by tariff group per power company', 'Công nghiệp-Xây dựng giá thấp nhất nhưng sản lượng lớn. Quản lý-Tiêu dùng số lượng KH đông nhất.', 40),
('loss_targets', 'Chỉ tiêu EVN giao cho từng PC theo năm — tổn thất, SAIDI, SAIFI', 'EVN-assigned targets per PC per year — loss rate, SAIDI, SAIFI', 'Benchmark chính để đánh giá hiệu quả. Nếu actual > target là không đạt. Mỗi PC có chỉ tiêu riêng tùy đặc thù địa bàn.', 24),
('weather_events', 'Sự kiện thời tiết ảnh hưởng đến vận hành lưới điện — bão, lũ, sạt lở', 'Weather events impacting grid operations — storms, floods, landslides', 'Mùa bão miền Trung: tháng 9-12. JOIN với grid_incidents qua weather_event_id để phân tích thiệt hại do thiên tai.', 30),
('monthly_kpi_summary', 'KPI vận hành tổng hợp theo công ty điện lực × tháng — fact table chính', 'Monthly operational KPIs per power company — primary fact table', 'Grain: 1 PC × 1 tháng. Bao gồm sản lượng, doanh thu, tổn thất, SAIDI/SAIFI, sự cố, nhân sự. Dùng cho dashboard tổng quan.', 288),
('power_loss_detail', 'Tổn thất điện năng chi tiết theo huyện × tháng — drill-down root cause', 'Power loss details by district per month — for root cause drill-down', 'Grain nhỏ hơn monthly_kpi_summary, cho phép xác định huyện nào tổn thất cao nhất. Tách riêng kỹ thuật trung thế, hạ thế, thương mại.', 5400),
('grid_incidents', 'Sự cố lưới điện từng vụ — chi tiết nhất, phục vụ phân tích rủi ro thiên tai', 'Individual grid incidents — most detailed, for disaster risk analysis', 'Mỗi dòng = 1 vụ sự cố. 8 nhóm nguyên nhân. Liên kết weather_events cho sự cố thiên tai. outage_duration_hours tính SAIDI.', 2000),
('investment_history', 'Lịch sử đầu tư xây dựng — phân tích ROI và tối ưu phân bổ ngân sách', 'Investment history — ROI analysis and budget allocation optimization', 'So sánh expected vs actual loss reduction để đánh giá hiệu quả đầu tư. Dự án Chậm tiến độ cần quan tâm.', 200),
('operating_costs', 'Chi phí vận hành theo PC × tháng × loại chi phí', 'Operating costs per PC per month per cost category', '8 loại chi phí. Khắc phục thiên tai tăng đột biến trong mùa bão. Sửa chữa thường xuyên chiếm tỷ trọng lớn nhất.', 2300),
('_meta_tables', 'Bảng metadata mô tả các bảng trong database', 'Metadata table describing all tables in the database', 'Dùng cho AI/chatbot hiểu cấu trúc database.', 17),
('_meta_columns', 'Bảng metadata mô tả chi tiết các cột quan trọng', 'Metadata table describing key columns', 'Dùng cho AI/chatbot hiểu ý nghĩa từng trường dữ liệu.', 70),
('_meta_kpi', 'Bảng metadata chứa công thức SQL cho các KPI chính', 'Metadata table with SQL formulas for key KPIs', 'Dùng cho AI/chatbot tự sinh SQL chính xác khi trả lời câu hỏi nghiệp vụ.', 14),
('_meta_glossary', 'Thuật ngữ ngành điện lực Việt-Anh', 'Vietnamese-English power industry glossary', 'Dùng cho AI/chatbot hiểu thuật ngữ chuyên ngành và ánh xạ ngôn ngữ tự nhiên → SQL.', 28);


-- ----------------------------------------
-- Table: _meta_columns
-- ----------------------------------------

INSERT INTO `_meta_columns` (`id`, `table_name`, `column_name`, `data_type`, `description_vi`, `description_en`, `unit`, `example_values`) VALUES
-- power_companies
(1, 'power_companies', 'pc_id', 'VARCHAR(4)', 'Mã công ty điện lực', 'Power company ID', NULL, 'PC01, PC02, PC08'),
(2, 'power_companies', 'pc_name', 'VARCHAR(100)', 'Tên đầy đủ công ty điện lực', 'Full company name', NULL, 'Công ty Điện lực Đà Nẵng'),
(3, 'power_companies', 'num_customers', 'INT', 'Tổng số khách hàng sử dụng điện', 'Total electricity customers', 'khách hàng', '520000, 380000'),
(4, 'power_companies', 'total_line_length_km', 'DECIMAL(10,1)', 'Tổng chiều dài đường dây quản lý', 'Total managed line length', 'km', '12500.0, 8300.0'),
(5, 'power_companies', 'num_substations_110kv', 'INT', 'Số trạm biến áp 110kV', 'Number of 110kV substations', 'trạm', '15, 22'),
(6, 'power_companies', 'num_distribution_substations', 'INT', 'Số trạm biến áp phân phối (22kV, 0.4kV)', 'Number of distribution substations', 'trạm', '4500, 6200'),
(7, 'power_companies', 'is_joint_stock', 'BOOLEAN', 'Là công ty cổ phần (TRUE) hay TNHH MTV (FALSE)', 'Joint-stock company flag', NULL, 'TRUE, FALSE'),
-- provinces
(8, 'provinces', 'province_id', 'VARCHAR(4)', 'Mã tỉnh/thành phố', 'Province/city ID', NULL, 'P01, P13'),
(9, 'provinces', 'province_name', 'VARCHAR(50)', 'Tên tỉnh/thành phố', 'Province/city name', NULL, 'Đà Nẵng, Quảng Nam, Gia Lai'),
(10, 'provinces', 'region', 'VARCHAR(20)', 'Vùng miền', 'Region', NULL, 'Duyên hải, Tây Nguyên'),
(11, 'provinces', 'terrain_type', 'VARCHAR(30)', 'Địa hình chính', 'Main terrain type', NULL, 'Đồng bằng, Đồi núi, Ven biển, Hỗn hợp'),
(12, 'provinces', 'storm_risk_level', 'VARCHAR(10)', 'Mức rủi ro bão', 'Storm risk level', NULL, 'Cao, Trung bình, Thấp'),
-- districts
(13, 'districts', 'district_id', 'VARCHAR(6)', 'Mã huyện/quận', 'District ID', NULL, 'D00101, D00502'),
(14, 'districts', 'district_type', 'VARCHAR(20)', 'Loại đơn vị hành chính', 'Administrative unit type', NULL, 'Thành phố, Thị xã, Huyện'),
(15, 'districts', 'is_urban', 'BOOLEAN', 'Khu vực đô thị hoặc nông thôn', 'Urban (TRUE) or rural (FALSE)', NULL, 'TRUE, FALSE'),
(16, 'districts', 'num_customers', 'INT', 'Số khách hàng sử dụng điện tại huyện', 'Number of electricity customers in district', 'khách hàng', '45000, 12000'),
-- substations
(17, 'substations', 'substation_id', 'VARCHAR(10)', 'Mã trạm biến áp', 'Substation ID', NULL, 'S110-00101, S22-00203'),
(18, 'substations', 'voltage_level', 'VARCHAR(10)', 'Cấp điện áp', 'Voltage level', NULL, '110kV, 22kV, 0.4kV'),
(19, 'substations', 'substation_type', 'VARCHAR(30)', 'Loại trạm biến áp', 'Substation type', NULL, 'Trạm 110kV, Trạm treo, Trạm giàn, Trạm hợp bộ'),
(20, 'substations', 'capacity_kva', 'INT', 'Công suất định mức', 'Rated capacity', 'kVA', '40000, 560, 250'),
(21, 'substations', 'load_rate_pct', 'DECIMAL(5,2)', 'Tỷ lệ mang tải = tải thực tế / công suất định mức × 100', 'Load rate percentage', '%', '72.50, 85.30, 45.00'),
(22, 'substations', 'condition_rating', 'VARCHAR(20)', 'Tình trạng thiết bị', 'Equipment condition', NULL, 'Tốt, Trung bình, Kém, Cần thay thế'),
(23, 'substations', 'installed_year', 'INT', 'Năm lắp đặt', 'Installation year', NULL, '2005, 2015, 2022'),
-- grid_assets
(24, 'grid_assets', 'asset_type', 'VARCHAR(30)', 'Loại tài sản lưới điện', 'Grid asset type', NULL, 'MBA phân phối, Recloser, Đường dây trung thế'),
(25, 'grid_assets', 'capacity_or_length', 'DECIMAL(10,2)', 'Công suất hoặc chiều dài tùy loại tài sản', 'Capacity or length depending on asset type', 'kVA hoặc km', '560.00, 12.50'),
(26, 'grid_assets', 'condition_rating', 'VARCHAR(10)', 'Tình trạng tài sản', 'Asset condition', NULL, 'Tốt, Trung bình, Kém'),
(27, 'grid_assets', 'replacement_cost_million_vnd', 'DECIMAL(10,1)', 'Chi phí thay thế ước tính', 'Estimated replacement cost', 'triệu VND', '450.0, 2500.0'),
-- customer_segments
(28, 'customer_segments', 'segment_name', 'VARCHAR(50)', 'Nhóm khách hàng theo biểu giá', 'Customer segment by tariff group', NULL, 'Công nghiệp-Xây dựng, Quản lý-Tiêu dùng'),
(29, 'customer_segments', 'proportion_pct', 'DECIMAL(5,2)', 'Tỷ trọng sản lượng của nhóm KH', 'Segment share of commercial power', '%', '42.50, 35.00'),
(30, 'customer_segments', 'avg_price_vnd_per_kwh', 'DECIMAL(8,2)', 'Giá bán bình quân cho nhóm KH', 'Average selling price for segment', 'VND/kWh', '1780.00, 2050.00'),
-- loss_targets
(31, 'loss_targets', 'target_loss_rate_pct', 'DECIMAL(5,2)', 'Chỉ tiêu tổn thất EVN giao', 'EVN-assigned loss rate target', '%', '4.50, 5.20, 6.80'),
(32, 'loss_targets', 'target_saidi_minutes', 'DECIMAL(6,1)', 'Chỉ tiêu SAIDI', 'SAIDI target', 'phút/KH/năm', '350.0, 450.0'),
(33, 'loss_targets', 'target_saifi_times', 'DECIMAL(4,1)', 'Chỉ tiêu SAIFI', 'SAIFI target', 'lần/KH/năm', '6.0, 8.5'),
-- weather_events
(34, 'weather_events', 'event_type', 'VARCHAR(30)', 'Loại sự kiện thời tiết', 'Weather event type', NULL, 'Bão, Áp thấp nhiệt đới, Mưa lớn, Lũ lụt, Sạt lở'),
(35, 'weather_events', 'severity', 'VARCHAR(20)', 'Mức độ ảnh hưởng', 'Severity level', NULL, 'Nhẹ, Trung bình, Nặng, Rất nặng'),
(36, 'weather_events', 'max_wind_speed_kmh', 'INT', 'Tốc độ gió cực đại', 'Maximum wind speed', 'km/h', '120, 150, 180'),
(37, 'weather_events', 'affected_provinces', 'TEXT', 'Danh sách tỉnh bị ảnh hưởng (comma-separated province_id)', 'List of affected provinces', NULL, 'P03,P04,P05'),
-- monthly_kpi_summary
(38, 'monthly_kpi_summary', 'report_month', 'DATE', 'Tháng báo cáo (ngày 1 của tháng)', 'Report month (1st of month)', NULL, '2024-01-01, 2025-06-01'),
(39, 'monthly_kpi_summary', 'power_received_gwh', 'DECIMAL(10,3)', 'Điện nhận từ lưới truyền tải', 'Power received from transmission grid', 'GWh', '450.200, 380.100'),
(40, 'monthly_kpi_summary', 'commercial_power_gwh', 'DECIMAL(10,3)', 'Điện thương phẩm — sản lượng bán cho KH', 'Commercial power — power sold to customers', 'GWh', '425.500, 360.800'),
(41, 'monthly_kpi_summary', 'revenue_billion_vnd', 'DECIMAL(10,2)', 'Doanh thu phân phối điện', 'Power distribution revenue', 'tỷ VND', '850.50, 720.30'),
(42, 'monthly_kpi_summary', 'avg_selling_price_vnd', 'DECIMAL(8,2)', 'Giá bán bình quân', 'Average selling price', 'VND/kWh', '1950.00, 2010.50'),
(43, 'monthly_kpi_summary', 'loss_rate_pct', 'DECIMAL(5,2)', 'Tỷ lệ tổn thất điện năng tổng', 'Total power loss rate', '%', '5.20, 6.15, 4.80'),
(44, 'monthly_kpi_summary', 'technical_loss_mv_pct', 'DECIMAL(5,2)', 'Tổn thất kỹ thuật trung thế', 'Medium voltage technical loss', '%', '2.10, 2.50'),
(45, 'monthly_kpi_summary', 'technical_loss_lv_pct', 'DECIMAL(5,2)', 'Tổn thất kỹ thuật hạ thế', 'Low voltage technical loss', '%', '1.80, 2.30'),
(46, 'monthly_kpi_summary', 'commercial_loss_pct', 'DECIMAL(5,2)', 'Tổn thất thương mại (trộm điện, sai số công tơ)', 'Commercial loss (theft, meter errors)', '%', '0.80, 1.20'),
(47, 'monthly_kpi_summary', 'saidi_minutes', 'DECIMAL(8,2)', 'SAIDI — thời gian mất điện bình quân', 'SAIDI — system average interruption duration', 'phút/KH', '28.50, 45.00'),
(48, 'monthly_kpi_summary', 'saifi_times', 'DECIMAL(6,2)', 'SAIFI — số lần mất điện bình quân', 'SAIFI — system average interruption frequency', 'lần/KH', '0.55, 0.80'),
(49, 'monthly_kpi_summary', 'maifi_times', 'DECIMAL(6,2)', 'MAIFI — số lần mất điện thoáng qua bình quân', 'MAIFI — momentary average interruption frequency', 'lần/KH', '1.20, 2.50'),
(50, 'monthly_kpi_summary', 'num_incidents_total', 'INT', 'Tổng số sự cố trong tháng', 'Total incidents in month', 'vụ', '15, 35, 80'),
(51, 'monthly_kpi_summary', 'peak_load_mw', 'DECIMAL(8,1)', 'Công suất đỉnh tháng', 'Monthly peak load', 'MW', '850.5, 1200.0'),
(52, 'monthly_kpi_summary', 'num_overloaded_substations', 'INT', 'Số MBA quá tải (>80% công suất)', 'Number of overloaded transformers (>80% capacity)', 'trạm', '12, 25'),
(53, 'monthly_kpi_summary', 'collection_rate_pct', 'DECIMAL(5,2)', 'Tỷ lệ thu nộp tiền điện', 'Electricity bill collection rate', '%', '98.50, 99.20'),
(54, 'monthly_kpi_summary', 'productivity_kwh_per_employee', 'DECIMAL(10,1)', 'Năng suất lao động', 'Labor productivity', 'kWh/người/tháng', '125000.0, 98000.0'),
-- power_loss_detail
(55, 'power_loss_detail', 'power_received_mwh', 'DECIMAL(12,2)', 'Điện nhận tại huyện', 'Power received at district level', 'MWh', '45000.00, 12000.00'),
(56, 'power_loss_detail', 'commercial_power_mwh', 'DECIMAL(12,2)', 'Điện thương phẩm tại huyện', 'Commercial power at district level', 'MWh', '42500.00, 11200.00'),
(57, 'power_loss_detail', 'total_loss_rate_pct', 'DECIMAL(5,2)', 'Tổn thất tổng tại huyện', 'Total loss rate at district', '%', '5.55, 7.10, 4.20'),
(58, 'power_loss_detail', 'num_substations_overloaded', 'INT', 'Số MBA quá tải trong huyện', 'Overloaded transformers in district', 'trạm', '3, 8'),
-- grid_incidents
(59, 'grid_incidents', 'incident_date', 'DATE', 'Ngày xảy ra sự cố', 'Incident date', NULL, '2025-10-15, 2024-09-28'),
(60, 'grid_incidents', 'cause_category', 'VARCHAR(30)', 'Nguyên nhân sự cố', 'Incident cause category', NULL, 'Bão-Áp thấp, Cây đổ, Thiết bị hỏng, Quá tải'),
(61, 'grid_incidents', 'affected_customers', 'INT', 'Số khách hàng bị ảnh hưởng', 'Number of affected customers', 'khách hàng', '5000, 25000'),
(62, 'grid_incidents', 'outage_duration_hours', 'DECIMAL(6,2)', 'Thời gian mất điện', 'Outage duration', 'giờ', '4.50, 12.00, 72.00'),
(63, 'grid_incidents', 'restoration_time_hours', 'DECIMAL(6,2)', 'Thời gian phục hồi cấp điện', 'Power restoration time', 'giờ', '6.00, 18.00, 96.00'),
(64, 'grid_incidents', 'repair_cost_million_vnd', 'DECIMAL(10,1)', 'Chi phí sửa chữa/khắc phục', 'Repair cost', 'triệu VND', '150.0, 2500.0'),
(65, 'grid_incidents', 'equipment_damaged', 'TEXT', 'Thiết bị hư hỏng', 'Damaged equipment description', NULL, 'Gãy 3 cột bê tông, đứt 2km dây trung thế'),
-- investment_history
(66, 'investment_history', 'project_type', 'VARCHAR(50)', 'Loại dự án đầu tư', 'Investment project type', NULL, 'Cải tạo lưới trung thế, Thay MBA, Lắp recloser'),
(67, 'investment_history', 'investment_billion_vnd', 'DECIMAL(10,2)', 'Giá trị đầu tư', 'Investment value', 'tỷ VND', '25.50, 120.00'),
(68, 'investment_history', 'expected_loss_reduction_pct', 'DECIMAL(5,2)', 'Dự kiến giảm tổn thất', 'Expected loss reduction', 'điểm %', '0.50, 1.20'),
(69, 'investment_history', 'actual_loss_reduction_pct', 'DECIMAL(5,2)', 'Thực tế giảm tổn thất (NULL nếu chưa đánh giá)', 'Actual loss reduction (NULL if not yet evaluated)', 'điểm %', '0.45, 1.10, NULL'),
(70, 'investment_history', 'status', 'VARCHAR(20)', 'Trạng thái dự án', 'Project status', NULL, 'Đang triển khai, Hoàn thành, Chậm tiến độ'),
-- operating_costs
(71, 'operating_costs', 'cost_category', 'VARCHAR(50)', 'Loại chi phí vận hành', 'Operating cost category', NULL, 'Sửa chữa thường xuyên, Nhân công, Khắc phục thiên tai'),
(72, 'operating_costs', 'amount_million_vnd', 'DECIMAL(12,1)', 'Số tiền chi phí', 'Cost amount', 'triệu VND', '2500.0, 15000.0');


-- ----------------------------------------
-- Table: _meta_kpi
-- ----------------------------------------

INSERT INTO `_meta_kpi` (`kpi_name`, `formula_sql`, `description_vi`, `related_questions`, `benchmark_good`, `benchmark_warning`, `benchmark_alert`) VALUES
('Tổn thất điện năng',
 'ROUND((power_received_gwh - commercial_power_gwh) / power_received_gwh * 100, 2)',
 'Tỷ lệ tổn thất điện năng tổng = (Điện nhận - Điện thương phẩm) / Điện nhận × 100. Bao gồm tổn thất kỹ thuật (trung thế + hạ thế) và tổn thất thương mại.',
 'Tổn thất điện năng của PC nào cao nhất? Xu hướng tổn thất qua các tháng? So sánh tổn thất với chỉ tiêu EVN giao?',
 '< 5.0%', '5.0% - 6.5%', '> 6.5%'),

('SAIDI',
 'SUM(saidi_minutes) -- cộng dồn theo tháng trong năm cho SAIDI năm',
 'System Average Interruption Duration Index — Thời gian mất điện bình quân mỗi khách hàng. Đơn vị: phút/KH/năm. SAIDI thấp = độ tin cậy cao.',
 'SAIDI của EVNCPC so với chỉ tiêu? PC nào SAIDI cao nhất? SAIDI có cải thiện so với năm trước?',
 '< 300 phút/năm', '300 - 500 phút/năm', '> 500 phút/năm'),

('SAIFI',
 'SUM(saifi_times) -- cộng dồn theo tháng trong năm cho SAIFI năm',
 'System Average Interruption Frequency Index — Số lần mất điện bình quân mỗi khách hàng. Đơn vị: lần/KH/năm. SAIFI thấp = ít sự cố.',
 'Số lần mất điện bình quân? PC nào SAIFI cao nhất? Mùa bão SAIFI tăng bao nhiêu?',
 '< 5 lần/năm', '5 - 8 lần/năm', '> 8 lần/năm'),

('MAIFI',
 'SUM(maifi_times) -- cộng dồn theo tháng trong năm cho MAIFI năm',
 'Momentary Average Interruption Frequency Index — Số lần mất điện thoáng qua (< 5 phút) bình quân mỗi KH. Phản ánh hiệu quả recloser/thiết bị tự đóng lại.',
 'MAIFI bao nhiêu? PC nào có nhiều mất điện thoáng qua nhất? Lắp recloser có giảm MAIFI?',
 '< 8 lần/năm', '8 - 15 lần/năm', '> 15 lần/năm'),

('Sản lượng thương phẩm',
 'SUM(commercial_power_gwh)',
 'Tổng sản lượng điện thương phẩm (bán cho khách hàng). Đơn vị: GWh. Là chỉ tiêu doanh thu cốt lõi.',
 'Sản lượng thương phẩm tháng này bao nhiêu? Tăng trưởng so với cùng kỳ? PC nào sản lượng lớn nhất?',
 'Tăng trưởng > 8%/năm', 'Tăng trưởng 3-8%/năm', 'Tăng trưởng < 3%/năm'),

('Doanh thu',
 'SUM(revenue_billion_vnd)',
 'Tổng doanh thu phân phối điện. Đơn vị: tỷ VND. Doanh thu = Sản lượng thương phẩm × Giá bán bình quân.',
 'Doanh thu tháng/quý/năm? PC nào doanh thu cao nhất? Xu hướng doanh thu?',
 NULL, NULL, NULL),

('Giá bán bình quân',
 'ROUND(SUM(revenue_billion_vnd) * 1000 / SUM(commercial_power_gwh), 2)',
 'Giá bán điện bình quân = Doanh thu / Sản lượng thương phẩm. Đơn vị: VND/kWh. Phụ thuộc cơ cấu KH (CN giá thấp, sinh hoạt giá cao).',
 'Giá bán bình quân bao nhiêu? PC nào giá bán cao nhất? Giá bán thay đổi thế nào?',
 '> 2000 VND/kWh', '1800 - 2000 VND/kWh', '< 1800 VND/kWh'),

('Suất sự cố',
 'ROUND(SUM(num_incidents_total) / SUM(total_line_length_km) * 100, 2)',
 'Suất sự cố = Tổng số sự cố / Chiều dài đường dây × 100 (vụ/100km). Chuẩn hóa theo quy mô lưới điện để so sánh công bằng giữa các PC.',
 'Suất sự cố PC nào cao nhất? Suất sự cố mùa bão vs mùa khô? Xu hướng suất sự cố?',
 '< 5 vụ/100km/năm', '5 - 10 vụ/100km/năm', '> 10 vụ/100km/năm'),

('Thời gian phục hồi',
 'ROUND(AVG(restoration_time_hours), 2)',
 'Thời gian trung bình phục hồi cấp điện sau sự cố. Đơn vị: giờ. Phản ánh năng lực ứng cứu của PC.',
 'Thời gian phục hồi trung bình? Sự cố nào phục hồi lâu nhất? PC nào phục hồi nhanh nhất?',
 '< 4 giờ', '4 - 12 giờ', '> 12 giờ'),

('Chi phí khắc phục',
 'SUM(repair_cost_million_vnd)',
 'Tổng chi phí sửa chữa/khắc phục sự cố. Đơn vị: triệu VND. Sự cố thiên tai thường chi phí rất lớn.',
 'Chi phí khắc phục tổng bao nhiêu? Sự cố thiên tai chiếm bao nhiêu %? Chi phí khắc phục theo PC?',
 NULL, NULL, NULL),

('Tỷ lệ MBA quá tải',
 'ROUND(SUM(num_overloaded_substations) / (SELECT COUNT(*) FROM substations WHERE pc_id = k.pc_id) * 100, 2)',
 'Tỷ lệ máy biến áp quá tải (mang tải > 80% công suất định mức). Chỉ tiêu: < 5%. MBA quá tải → tổn thất cao + nguy cơ cháy nổ.',
 'Bao nhiêu % MBA quá tải? Huyện nào nhiều MBA quá tải nhất? Xu hướng quá tải?',
 '< 5%', '5% - 10%', '> 10%'),

('Năng suất lao động',
 'ROUND(SUM(commercial_power_gwh) * 1000000 / SUM(num_employees), 1)',
 'Năng suất lao động = Sản lượng thương phẩm / Số CBCNV. Đơn vị: kWh/người/tháng. Phản ánh hiệu quả sử dụng nhân lực.',
 'Năng suất lao động PC nào cao nhất? Xu hướng năng suất? So sánh giữa các PC?',
 '> 120000 kWh/người/tháng', '80000 - 120000 kWh/người/tháng', '< 80000 kWh/người/tháng'),

('Tỷ lệ thu nộp',
 'ROUND(AVG(collection_rate_pct), 2)',
 'Tỷ lệ thu nộp tiền điện = Số tiền thu được / Số tiền phải thu × 100. Chỉ tiêu: > 99%. Tỷ lệ thấp → công nợ tăng.',
 'Tỷ lệ thu nộp bao nhiêu? PC nào thu nộp thấp? Xu hướng thu nộp theo mùa?',
 '> 99%', '97% - 99%', '< 97%'),

('Tổn thất thương mại',
 'ROUND(AVG(commercial_loss_pct), 2)',
 'Tổn thất thương mại = tổn thất do trộm cắp điện, sai số công tơ, sai sót ghi chỉ số. Tách riêng để phân biệt với tổn thất kỹ thuật.',
 'Tổn thất thương mại PC nào cao nhất? Huyện nào nghi ngờ trộm điện? Xu hướng tổn thất thương mại?',
 '< 0.5%', '0.5% - 1.0%', '> 1.0%');


-- ----------------------------------------
-- Table: _meta_glossary
-- ----------------------------------------

INSERT INTO `_meta_glossary` (`term_vi`, `term_en`, `abbreviation`, `definition`, `related_table`, `related_column`) VALUES
('Tổn thất điện năng', 'Power Loss', 'TTĐN',
 'Phần điện năng bị mất trong quá trình truyền tải và phân phối, tính bằng tỷ lệ phần trăm giữa điện nhận và điện thương phẩm. Bao gồm tổn thất kỹ thuật và tổn thất thương mại.',
 'monthly_kpi_summary', 'loss_rate_pct'),

('Điện thương phẩm', 'Commercial Power', 'ĐTP',
 'Sản lượng điện bán cho khách hàng sử dụng cuối cùng, sau khi trừ tổn thất và điện tự dùng. Đơn vị: GWh hoặc MWh.',
 'monthly_kpi_summary', 'commercial_power_gwh'),

('Điện nhận', 'Power Received', NULL,
 'Tổng sản lượng điện nhận từ lưới truyền tải quốc gia (EVN) vào lưới phân phối của công ty điện lực.',
 'monthly_kpi_summary', 'power_received_gwh'),

('SAIDI', 'System Average Interruption Duration Index', 'SAIDI',
 'Chỉ số thời gian mất điện bình quân hệ thống. SAIDI = Tổng (số KH bị ảnh hưởng × thời gian mất điện) / Tổng số KH. Đơn vị: phút/KH/năm.',
 'monthly_kpi_summary', 'saidi_minutes'),

('SAIFI', 'System Average Interruption Frequency Index', 'SAIFI',
 'Chỉ số tần suất mất điện bình quân hệ thống. SAIFI = Tổng số KH bị mất điện / Tổng số KH. Đơn vị: lần/KH/năm.',
 'monthly_kpi_summary', 'saifi_times'),

('MAIFI', 'Momentary Average Interruption Frequency Index', 'MAIFI',
 'Chỉ số tần suất mất điện thoáng qua (dưới 5 phút). Phản ánh hiệu quả hoạt động của thiết bị tự đóng lại (recloser).',
 'monthly_kpi_summary', 'maifi_times'),

('Máy biến áp', 'Transformer', 'MBA',
 'Thiết bị biến đổi điện áp. Trong lưới phân phối có MBA 110kV (trạm nguồn) và MBA phân phối (22/0.4kV). MBA quá tải khi mang tải > 80% công suất định mức.',
 'substations', 'capacity_kva'),

('Lưới trung thế', 'Medium Voltage Grid', 'MV',
 'Lưới điện cấp điện áp 22kV (một số vùng còn 10kV, 35kV). Truyền tải từ trạm 110kV đến các trạm biến áp phân phối.',
 'grid_assets', 'asset_type'),

('Lưới hạ thế', 'Low Voltage Grid', 'LV',
 'Lưới điện cấp điện áp 0.4kV (380/220V). Phân phối điện từ trạm biến áp đến khách hàng sử dụng cuối cùng.',
 'grid_assets', 'asset_type'),

('Sự cố', 'Incident / Outage', NULL,
 'Sự kiện gây mất điện ngoài kế hoạch trên lưới điện. Phân loại theo nguyên nhân: thiên tai, thiết bị, thi công bên thứ 3, v.v.',
 'grid_incidents', 'cause_category'),

('Biểu giá điện', 'Electricity Tariff', NULL,
 'Hệ thống giá bán điện do Chính phủ quy định, phân theo nhóm khách hàng: sinh hoạt (bậc thang), sản xuất, kinh doanh, hành chính sự nghiệp.',
 'customer_segments', 'avg_price_vnd_per_kwh'),

('Công suất đỉnh', 'Peak Load', 'Pmax',
 'Công suất tiêu thụ điện lớn nhất trong một khoảng thời gian. Thường xảy ra 11h-14h mùa hè. Đơn vị: MW.',
 'monthly_kpi_summary', 'peak_load_mw'),

('Trạm biến áp', 'Substation', 'TBA',
 'Công trình điện có chức năng biến đổi điện áp, phân phối điện năng. Gồm trạm 110kV (trạm nguồn), trạm treo, trạm giàn, trạm hợp bộ.',
 'substations', NULL),

('Recloser', 'Recloser / Auto-reclosing Circuit Breaker', NULL,
 'Thiết bị tự động đóng lại mạch điện sau khi sự cố thoáng qua. Giúp giảm MAIFI và thời gian mất điện.',
 'grid_assets', 'asset_type'),

('Tụ bù', 'Capacitor Bank', NULL,
 'Thiết bị bù công suất phản kháng, cải thiện hệ số công suất cos(phi) và giảm tổn thất kỹ thuật trên lưới trung thế.',
 'grid_assets', 'asset_type'),

('Tỷ lệ thu nộp', 'Collection Rate', NULL,
 'Tỷ lệ giữa số tiền thực thu và số tiền phải thu từ khách hàng sử dụng điện. Chỉ tiêu: > 99%.',
 'monthly_kpi_summary', 'collection_rate_pct'),

('Tổn thất kỹ thuật', 'Technical Loss', 'TTKT',
 'Tổn thất do các đặc tính vật lý của lưới điện (điện trở dây dẫn, từ hóa lõi MBA). Chia thành tổn thất trung thế và hạ thế.',
 'monthly_kpi_summary', 'technical_loss_mv_pct'),

('Tổn thất thương mại', 'Commercial Loss / Non-Technical Loss', 'TTTM',
 'Tổn thất do các nguyên nhân phi kỹ thuật: trộm cắp điện, sai số công tơ đo đếm, sai sót ghi chỉ số.',
 'monthly_kpi_summary', 'commercial_loss_pct'),

('Năng suất lao động', 'Labor Productivity', 'NSLĐ',
 'Sản lượng điện thương phẩm trên mỗi lao động. Đơn vị: kWh/người/tháng hoặc triệu kWh/người/năm.',
 'monthly_kpi_summary', 'productivity_kwh_per_employee'),

('Cải tạo lưới', 'Grid Upgrading / Renovation', NULL,
 'Dự án nâng cấp cơ sở hạ tầng lưới điện: thay dây, chuyển cáp ngầm, thay MBA, lắp thiết bị tự động hóa.',
 'investment_history', 'project_type'),

('EVNCPC', 'Central Power Corporation', 'EVNCPC',
 'Tổng Công ty Điện lực miền Trung — đơn vị thành viên EVN, quản lý phân phối điện 13 tỉnh/TP từ Quảng Bình đến Khánh Hòa và Tây Nguyên.',
 'power_companies', NULL),

('Công ty điện lực', 'Power Company', 'PC',
 'Đơn vị trực thuộc EVNCPC, quản lý phân phối điện tại 1-3 tỉnh. EVNCPC có 8 PC sau sáp nhập 1/7/2025.',
 'power_companies', 'pc_id'),

('Điện tự dùng', 'Auxiliary Power Consumption', NULL,
 'Sản lượng điện mà hệ thống điện tiêu thụ cho chính nhu cầu vận hành (bơm làm mát, chiếu sáng trạm, v.v.), không bán cho khách hàng.',
 NULL, NULL),

('Quá tải', 'Overload', NULL,
 'Trạng thái máy biến áp hoặc đường dây mang tải vượt quá 80% công suất định mức. Gây tổn thất cao và nguy cơ cháy nổ.',
 'substations', 'load_rate_pct'),

('Sạt lở', 'Landslide', NULL,
 'Hiện tượng đất đá trượt lở do mưa lớn, thường xảy ra ở vùng Tây Nguyên và miền núi ven biển. Gây đổ cột, đứt dây.',
 'weather_events', 'event_type'),

('Công suất định mức', 'Rated Capacity', NULL,
 'Công suất tối đa mà thiết bị (MBA, đường dây) có thể vận hành liên tục an toàn. Đơn vị: kVA hoặc MVA.',
 'substations', 'capacity_kva'),

('Cấp điện áp', 'Voltage Level', NULL,
 'Mức điện áp của lưới điện: 110kV (truyền tải khu vực), 22kV (trung thế / phân phối), 0.4kV (hạ thế / khách hàng).',
 'substations', 'voltage_level'),

('Thi công bên thứ 3', 'Third-party Construction', NULL,
 'Hoạt động thi công xây dựng của đơn vị ngoài ngành điện (xây nhà, đào đường) gây ảnh hưởng đến lưới điện, dẫn đến sự cố.',
 'grid_incidents', 'cause_category');


SET FOREIGN_KEY_CHECKS = 1;
