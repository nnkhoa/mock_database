-- ============================================================================
-- GEMADEPT SEAPORT DEMO — Metadata
-- Database: seaport_demo
-- Description: Metadata tables cho AI engine hiểu cấu trúc database
-- ============================================================================

USE seaport_demo;

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================================
-- 1. _meta_tables — Mô tả tất cả 20 bảng
-- ============================================================================

INSERT INTO `_meta_tables` (`table_name`, `description_vi`, `description_en`, `business_context`) VALUES
-- Dimension tables
('ports',
 'Danh sách 4 cảng thuộc hệ thống Gemadept: NDV, GML, PHL, DQT',
 'Master list of Gemadept ports with capacity, berth and draft specifications',
 'NDV (Nam Đình Vũ, Hải Phòng) — cảng biển miền Bắc; GML (Gemalink, Cái Mép) — cảng nước sâu duy nhất, tiếp tàu mẹ; PHL (Phước Long, TP.HCM) — cảng sông nội thành; DQT (Dung Quất, Quảng Ngãi) — cảng biển miền Trung, hàng rời. design_capacity_teu là mốc tính capacity_utilization.'),

('shipping_lines',
 'Danh sách 15 hãng tàu đối tác hoạt động tại các cảng Gemadept',
 'Shipping line partners with alliance membership and market share',
 'CMA-CGM là đối tác chiến lược (#1 tại GML). alliance cho biết nhóm hãng tàu (Ocean Alliance, THE Alliance, 2M). market_share_pct dùng phát hiện mức độ tập trung hãng tàu (scenario churn).'),

('cost_types',
 'Danh mục 6 loại chi phí vận hành cảng',
 'Operating cost categories: labor, depreciation, energy, maintenance, land lease, other',
 '6 loại: LABOR (~32%), DEPRECIATION (~23%), ENERGY (~13%), MAINT (~10%), LAND_LEASE (~7%), OTHER (~15%). typical_pct_of_total là tỷ trọng chuẩn, dùng so sánh phát hiện bất thường chi phí.'),

('cargo_types',
 'Danh mục 6 loại hàng hóa qua cảng',
 'Cargo type classification with standard revenue per unit',
 'CONT_DRY (container khô), CONT_REEFER (container lạnh), CONT_OOG (hàng quá khổ), BULK (hàng rời), BREAKBULK (bách hóa), LIQUID (hàng lỏng). avg_revenue_per_unit_vnd khác biệt lớn giữa loại hàng: OOG cao nhất, BULK thấp nhất.'),

('equipment',
 'Danh sách ~35 thiết bị xếp dỡ tại 4 cảng',
 'Port equipment inventory: STS cranes, RTGs, reach stackers, forklifts',
 'equipment_type gồm: QC (quay crane/STS), RTG, Reach Stacker, Forklift, MHC. capacity_tons là sức nâng tối đa. year_acquired dùng đánh giá tuổi thiết bị và nhu cầu đại tu.'),

('customers',
 'Danh sách ~40 khách hàng xuất nhập khẩu sử dụng dịch vụ cảng',
 'Import/export customers with industry and preferred port/cargo',
 'primary_port_id là cảng sử dụng chính. cargo_type_preference là loại hàng ưu tiên. Top 20% khách hàng chiếm ~80% doanh thu (quy luật Pareto). Dùng phân tích customer concentration.'),

('regions',
 '7 khu vực địa lý phục vụ phân tích hậu phương cảng',
 'Geographic regions for hinterland analysis',
 'Gồm 3 vùng nội địa (Miền Bắc, Miền Trung, Miền Nam) và 4 vùng quốc tế. provinces_included liệt kê tỉnh/thành thuộc vùng. Dùng liên kết với customers.'),

('investment_projects',
 'Danh sách dự án đầu tư mở rộng cảng',
 'Capital investment projects with cost, capacity, and depreciation details',
 'GML 2A là dự án trọng điểm: ~150M USD, +600K TEU. annual_depreciation_vnd và estimated_annual_opex_vnd dùng tính breakeven volume. status theo dõi tiến độ dự án.'),

-- Fact tables
('port_revenue',
 'Doanh thu cảng theo tháng, loại hàng — grain: port × month × cargo_type',
 'Monthly port revenue by cargo type, 18 months (2024-01 to 2025-06)',
 'total_revenue_vnd là tổng doanh thu. volume_teu cho container, volume_tons cho hàng rời/bách hóa. revenue_per_unit_vnd là đơn giá. JOIN với operating_costs trên (port_id, month) để tính gross margin.'),

('container_throughput',
 'Sản lượng xếp dỡ qua cảng theo tháng — grain: port × month × cargo_type',
 'Monthly container/cargo throughput by type',
 'volume_teu là sản lượng quy TEU, volume_tons cho hàng đo bằng tấn. JOIN với ports.design_capacity_teu để tính capacity_utilization. Dùng so sánh YoY và phát hiện xu hướng sản lượng.'),

('operating_costs',
 'Chi phí vận hành theo cảng, tháng, loại chi phí — grain: port × month × cost_type',
 'Monthly operating costs by cost type',
 'cost_amount_vnd là số tiền chi phí. JOIN với port_revenue trên (port_id, month) để tính gross margin. JOIN với container_throughput để tính cost_per_teu. Phát hiện bất thường khi tỷ trọng chi phí lệch chuẩn.'),

('shipping_line_revenue',
 'Doanh thu và sản lượng theo hãng tàu — grain: port × month × shipping_line',
 'Revenue and volume by shipping line, used to detect churn and concentration',
 'revenue_vnd + volume_teu cho mỗi hãng tàu tại mỗi cảng. num_vessel_calls là số chuyến tàu. Dùng tính shipping_line_concentration và phát hiện churn (hãng tàu giảm sản lượng đột ngột).'),

('vessel_calls',
 'Chi tiết từng chuyến tàu cập cảng — event-level',
 'Individual vessel call events with turnaround time and cargo handled',
 'Mỗi record = 1 lượt tàu ghé. turnaround_hours = departure_time - arrival_time. actual_volume_teu là sản lượng xếp dỡ. vessel_capacity_teu là sức chứa tàu. Dùng tính vessel_turnaround và berth_occupancy.'),

('equipment_utilization',
 'Hiệu suất sử dụng thiết bị theo tháng — grain: equipment × month',
 'Monthly equipment utilization metrics: hours, moves, availability',
 'total_hours mặc định 720h/tháng. operating_hours + idle_hours + maintenance_hours = total_hours. moves_count là số lượt nâng hạ. availability_pct = (total_hours - maintenance_hours) / total_hours × 100. productivity_moves_per_hour = moves_count / operating_hours.'),

('equipment_maintenance',
 'Lịch sử bảo trì và sửa chữa thiết bị — event-level',
 'Equipment maintenance log with type, duration, and cost',
 'maintenance_type: routine (định kỳ), major_overhaul (đại tu), emergency (khẩn cấp), inspection (kiểm tra). cost_vnd đại tu STS crane ~8-9 tỷ VND/đợt. Dùng phân tích xu hướng chi phí bảo trì và downtime.'),

('customer_revenue',
 'Doanh thu theo khách hàng — grain: port × month × customer × cargo_type',
 'Revenue by customer with volume, used for customer concentration analysis',
 'revenue_vnd + volume_teu + volume_tons cho mỗi khách hàng. JOIN với customers để lấy industry. Top customers chiếm phần lớn doanh thu (Pareto analysis).'),

-- Metadata tables
('_meta_tables',
 'Bảng metadata mô tả tất cả các bảng trong database',
 'Metadata: table descriptions for AI engine',
 'AI engine đọc bảng này để hiểu mục đích và ngữ cảnh nghiệp vụ của từng bảng.'),

('_meta_columns',
 'Bảng metadata mô tả tất cả các cột trong database',
 'Metadata: column descriptions with data types and examples',
 'AI engine đọc bảng này để hiểu ý nghĩa, đơn vị, và giá trị mẫu của từng cột. Là tham chiếu chính khi viết SQL.'),

('_meta_kpi',
 'Định nghĩa KPI nghiệp vụ cảng với công thức SQL',
 'Metadata: KPI definitions with working SQL formulas',
 'Mỗi KPI có formula_sql copy-paste được. AI engine dùng để trả lời câu hỏi về chỉ tiêu kinh doanh.'),

('_meta_glossary',
 'Từ điển thuật ngữ ngành cảng biển',
 'Metadata: port industry glossary for AI engine',
 'AI engine tra cứu thuật ngữ chuyên ngành khi gặp từ không quen. Gồm 25+ thuật ngữ Việt-Anh.');


-- ============================================================================
-- 2. _meta_columns — Mô tả tất cả cột trong 20 bảng
-- ============================================================================

INSERT INTO `_meta_columns` (`table_name`, `column_name`, `data_type`, `description_vi`, `description_en`, `unit`, `example_values`) VALUES
-- ── ports ──────────────────────────────────────────────────────────────────
('ports', 'port_id',              'VARCHAR(5)',    'Mã cảng duy nhất',                          'Unique port identifier',                    NULL,       'NDV, GML, PHL, DQT'),
('ports', 'port_name',            'VARCHAR(100)',  'Tên cảng đầy đủ',                           'Full port name',                            NULL,       'Cảng Nam Đình Vũ, Cảng Gemalink'),
('ports', 'port_name_short',      'VARCHAR(50)',   'Tên cảng viết tắt',                         'Short port name',                           NULL,       'Nam Đình Vũ, Gemalink'),
('ports', 'region',               'VARCHAR(20)',   'Khu vực địa lý',                            'Geographic region',                         NULL,       'Miền Nam, Miền Trung, Miền Bắc'),
('ports', 'port_type',            'ENUM',          'Loại cảng',                                 'Port type classification',                  NULL,       'river_port, deep_sea_port, icd, sea_port'),
('ports', 'design_capacity_teu',  'INT',           'Công suất thiết kế hàng năm',               'Annual design capacity in TEU',             'TEU/năm',  '1500000, 800000, 300000'),
('ports', 'design_capacity_tons', 'INT',           'Công suất thiết kế hàng năm (tấn)',         'Annual design capacity in tons',            'tấn/năm',  '2000000, 500000'),
('ports', 'quay_length_m',        'INT',           'Chiều dài cầu tàu',                         'Total quay length',                         'm',        '890, 1150, 480'),
('ports', 'water_depth_m',        'DECIMAL(4,1)',  'Độ sâu luồng tàu',                          'Channel water depth / max draft',           'm',        '14.0, 16.0, 8.5'),
('ports', 'num_berths',           'INT',           'Số bến tàu',                                'Number of berths',                          'bến',      '2, 4, 6'),
('ports', 'status',               'ENUM',          'Trạng thái hoạt động',                      'Operational status',                        NULL,       'active, inactive, under_construction'),
('ports', 'created_at',           'TIMESTAMP',     'Thời điểm tạo bản ghi',                    'Record creation timestamp',                 NULL,       '2024-01-01 00:00:00'),

-- ── shipping_lines ─────────────────────────────────────────────────────────
('shipping_lines', 'shipping_line_id',   'VARCHAR(10)',   'Mã hãng tàu',                        'Shipping line identifier',                  NULL,       'MSK, CMA, OOCL, HPL'),
('shipping_lines', 'shipping_line_name', 'VARCHAR(100)',  'Tên hãng tàu đầy đủ',                'Full shipping line name',                   NULL,       'Maersk Line, CMA-CGM, OOCL'),
('shipping_lines', 'alliance',           'VARCHAR(50)',   'Liên minh hãng tàu',                  'Shipping alliance membership',              NULL,       '2M, THE Alliance, Ocean Alliance'),
('shipping_lines', 'country',            'VARCHAR(50)',   'Quốc gia đăng ký',                    'Country of registration',                   NULL,       'Đan Mạch, Pháp, Hồng Kông'),
('shipping_lines', 'market_share_pct',   'DECIMAL(4,1)', 'Thị phần tại Gemadept',                'Market share at Gemadept ports',             '%',        '18.5, 12.3, 8.7'),

-- ── cost_types ─────────────────────────────────────────────────────────────
('cost_types', 'cost_type_id',          'VARCHAR(20)',   'Mã loại chi phí',                     'Cost type identifier',                      NULL,       'LABOR, FUEL, MAINT, DEPR, LAND, OTHER'),
('cost_types', 'cost_type_name_vi',     'VARCHAR(100)',  'Tên loại chi phí tiếng Việt',          'Cost type name in Vietnamese',              NULL,       'Nhân công, Nhiên liệu, Bảo trì'),
('cost_types', 'cost_type_name_en',     'VARCHAR(100)',  'Tên loại chi phí tiếng Anh',           'Cost type name in English',                 NULL,       'Labor, Fuel/Energy, Maintenance'),
('cost_types', 'typical_pct_of_total',  'DECIMAL(4,1)', 'Tỷ trọng điển hình trong tổng chi phí', 'Typical share of total operating cost',      '%',        '32.0, 23.0, 13.0, 10.0'),

-- ── cargo_types ────────────────────────────────────────────────────────────
('cargo_types', 'cargo_type_id',             'VARCHAR(20)',   'Mã loại hàng',                    'Cargo type identifier',                     NULL,       'CONT_DRY, BULK, LIQUID, CONT_REEFER'),
('cargo_types', 'cargo_type_name_vi',        'VARCHAR(100)',  'Tên loại hàng tiếng Việt',         'Cargo type name in Vietnamese',             NULL,       'Container khô, Hàng rời, Hàng lạnh'),
('cargo_types', 'cargo_type_name_en',        'VARCHAR(100)',  'Tên loại hàng tiếng Anh',          'Cargo type name in English',                NULL,       'Dry Container, Bulk, Reefer'),
('cargo_types', 'unit',                      'VARCHAR(10)',   'Đơn vị tính',                      'Unit of measure',                           NULL,       'TEU, tấn, m3'),
('cargo_types', 'avg_revenue_per_unit_vnd',  'BIGINT',        'Doanh thu trung bình trên đơn vị', 'Average revenue per unit',                  'VND',      '850000, 1600000, 2200000'),

-- ── equipment ──────────────────────────────────────────────────────────────
('equipment', 'equipment_id',   'VARCHAR(15)',   'Mã thiết bị duy nhất',                  'Unique equipment identifier',               NULL,       'QC-NDV-01, RTG-GML-03'),
('equipment', 'equipment_name', 'VARCHAR(100)',  'Tên thiết bị',                          'Equipment name / label',                    NULL,       'STS Crane #1 - NDV, RTG #3 - GML'),
('equipment', 'equipment_type', 'VARCHAR(30)',   'Loại thiết bị',                         'Equipment type',                            NULL,       'QC, RTG, Reach Stacker, Forklift, MHC'),
('equipment', 'port_id',        'VARCHAR(5)',    'Mã cảng đặt thiết bị (FK → ports)',     'Port where equipment is located',           NULL,       'NDV, GML, PHL, DQT'),
('equipment', 'capacity_tons',  'DECIMAL(6,1)', 'Sức nâng tối đa',                       'Maximum lifting capacity',                  'tấn',      '65.0, 40.0, 100.0'),
('equipment', 'year_acquired',  'INT',           'Năm mua / đưa vào sử dụng',            'Year acquired / commissioned',              NULL,       '2018, 2021, 2023'),
('equipment', 'status',         'ENUM',          'Trạng thái thiết bị',                   'Equipment operational status',              NULL,       'active, maintenance, retired'),

-- ── customers ──────────────────────────────────────────────────────────────
('customers', 'customer_id',           'VARCHAR(20)',   'Mã khách hàng',                     'Customer identifier',                       NULL,       'CUS001, CUS040'),
('customers', 'customer_name',         'VARCHAR(150)',  'Tên công ty khách hàng',             'Customer company name',                     NULL,       'Samsung Electronics VN, Vinamilk'),
('customers', 'industry',              'VARCHAR(50)',   'Ngành nghề của khách hàng',          'Customer industry sector',                  NULL,       'Xuất khẩu nông sản, Điện tử, Dệt may'),
('customers', 'primary_port_id',       'VARCHAR(5)',    'Cảng sử dụng chính (FK → ports)',    'Primary port used',                         NULL,       'NDV, GML, PHL'),
('customers', 'cargo_type_preference', 'VARCHAR(20)',   'Loại hàng ưu tiên (FK → cargo_types)', 'Preferred cargo type',                    NULL,       'CONT_DRY, BULK, CONT_REEFER'),

-- ── regions ────────────────────────────────────────────────────────────────
('regions', 'region_id',          'VARCHAR(10)',  'Mã khu vực',                            'Region identifier',                         NULL,       'MN, MT, MB'),
('regions', 'region_name',        'VARCHAR(50)',  'Tên khu vực',                            'Region name',                               NULL,       'Miền Nam, Miền Trung, Đông Bắc Á'),
('regions', 'provinces_included', 'TEXT',          'Danh sách tỉnh/thành thuộc khu vực',    'List of provinces in region',               NULL,       'Hà Nội, Hải Phòng, Quảng Ninh'),

-- ── investment_projects ────────────────────────────────────────────────────
('investment_projects', 'project_id',               'VARCHAR(10)',   'Mã dự án đầu tư',                      'Investment project identifier',              NULL,       'IP01, IP05'),
('investment_projects', 'project_name',             'VARCHAR(200)',  'Tên dự án',                              'Project name',                               NULL,       'Gemalink giai đoạn 2A, Mở rộng bãi NDV'),
('investment_projects', 'port_id',                  'VARCHAR(5)',    'Cảng liên quan (FK → ports)',             'Related port',                               NULL,       'GML, NDV'),
('investment_projects', 'total_investment_usd',     'BIGINT',        'Tổng vốn đầu tư bằng USD',              'Total investment in USD',                    'USD',      '150000000, 35000000'),
('investment_projects', 'total_investment_vnd',     'BIGINT',        'Tổng vốn đầu tư bằng VND',              'Total investment in VND',                    'VND',      '3750000000000'),
('investment_projects', 'additional_capacity_teu',  'INT',           'Công suất tăng thêm',                    'Additional capacity from project',           'TEU/năm',  '600000, 200000'),
('investment_projects', 'depreciation_years',       'INT',           'Số năm khấu hao',                        'Depreciation period',                        'năm',      '20, 25, 30'),
('investment_projects', 'annual_depreciation_vnd',  'BIGINT',        'Khấu hao hàng năm',                      'Annual depreciation amount',                 'VND',      '150000000000, 50000000000'),
('investment_projects', 'estimated_annual_opex_vnd','BIGINT',        'Chi phí vận hành ước tính mỗi năm',      'Estimated annual operating cost',            'VND',      '80000000000, 30000000000'),
('investment_projects', 'construction_start',       'DATE',          'Ngày khởi công',                          'Construction start date',                    NULL,       '2023-06-01, 2024-01-15'),
('investment_projects', 'expected_completion',      'DATE',          'Ngày dự kiến hoàn thành',                 'Expected completion date',                   NULL,       '2026-12-31, 2025-06-30'),
('investment_projects', 'status',                   'ENUM',          'Trạng thái dự án',                        'Project status',                             NULL,       'planning, under_construction, completed'),

-- ── port_revenue (fact) ────────────────────────────────────────────────────
('port_revenue', 'id',                   'INT AUTO_INCREMENT', 'Khóa chính tự tăng',                 'Auto-increment primary key',                NULL,       '1, 2, 3'),
('port_revenue', 'port_id',              'VARCHAR(5)',         'Mã cảng (FK → ports)',                'Port identifier',                           NULL,       'NDV, GML, PHL, DQT'),
('port_revenue', 'month',                'DATE',               'Tháng báo cáo (ngày 1 của tháng)',   'Report month (1st day of month)',            NULL,       '2024-01-01, 2025-06-01'),
('port_revenue', 'cargo_type_id',        'VARCHAR(20)',        'Mã loại hàng (FK → cargo_types)',     'Cargo type identifier',                     NULL,       'CONT_DRY, BULK, CONT_REEFER'),
('port_revenue', 'volume_teu',           'INT',                'Sản lượng quy TEU',                   'Volume in TEU equivalent',                  'TEU',      '12500, 8300'),
('port_revenue', 'volume_tons',          'INT',                'Sản lượng tấn (hàng rời/bách hóa)',  'Volume in tons for bulk/breakbulk',         'tấn',      '45000, 120000'),
('port_revenue', 'revenue_per_unit_vnd', 'BIGINT',             'Đơn giá doanh thu trên đơn vị',      'Revenue per unit',                          'VND',      '850000, 1600000'),
('port_revenue', 'total_revenue_vnd',    'BIGINT',             'Tổng doanh thu trong tháng',          'Total monthly revenue',                     'VND',      '18300000000, 25000000000'),

-- ── container_throughput (fact) ────────────────────────────────────────────
('container_throughput', 'id',            'INT AUTO_INCREMENT', 'Khóa chính tự tăng',                'Auto-increment primary key',                NULL,       '1, 2, 3'),
('container_throughput', 'port_id',       'VARCHAR(5)',         'Mã cảng (FK → ports)',               'Port identifier',                           NULL,       'NDV, GML, PHL, DQT'),
('container_throughput', 'month',         'DATE',               'Tháng báo cáo',                      'Report month',                              NULL,       '2024-01-01, 2025-06-01'),
('container_throughput', 'cargo_type_id', 'VARCHAR(20)',        'Mã loại hàng (FK → cargo_types)',    'Cargo type identifier',                     NULL,       'CONT_DRY, BULK'),
('container_throughput', 'volume_teu',    'INT',                'Sản lượng xếp dỡ quy TEU',          'Throughput in TEU equivalent',              'TEU',      '15000, 9200'),
('container_throughput', 'volume_tons',   'INT',                'Sản lượng xếp dỡ tấn',              'Throughput in tons',                        'tấn',      '50000, 135000'),

-- ── operating_costs (fact) ─────────────────────────────────────────────────
('operating_costs', 'id',              'INT AUTO_INCREMENT', 'Khóa chính tự tăng',                   'Auto-increment primary key',                NULL,       '1, 2, 3'),
('operating_costs', 'port_id',         'VARCHAR(5)',         'Mã cảng (FK → ports)',                  'Port identifier',                           NULL,       'NDV, GML, PHL, DQT'),
('operating_costs', 'month',           'DATE',               'Tháng báo cáo',                         'Report month',                              NULL,       '2024-01-01, 2025-06-01'),
('operating_costs', 'cost_type_id',    'VARCHAR(20)',        'Mã loại chi phí (FK → cost_types)',     'Cost type identifier',                      NULL,       'LABOR, FUEL, MAINT, DEPR'),
('operating_costs', 'cost_amount_vnd', 'BIGINT',             'Số tiền chi phí',                       'Cost amount',                               'VND',      '8500000000, 3200000000'),

-- ── shipping_line_revenue (fact) ───────────────────────────────────────────
('shipping_line_revenue', 'id',               'INT AUTO_INCREMENT', 'Khóa chính tự tăng',             'Auto-increment primary key',                NULL,       '1, 2, 3'),
('shipping_line_revenue', 'port_id',          'VARCHAR(5)',         'Mã cảng (FK → ports)',            'Port identifier',                           NULL,       'NDV, GML'),
('shipping_line_revenue', 'month',            'DATE',               'Tháng báo cáo',                   'Report month',                              NULL,       '2024-01-01, 2025-06-01'),
('shipping_line_revenue', 'shipping_line_id', 'VARCHAR(10)',        'Mã hãng tàu (FK → shipping_lines)', 'Shipping line identifier',               NULL,       'MSK, CMA, OOCL'),
('shipping_line_revenue', 'volume_teu',       'INT',                'Sản lượng TEU của hãng tàu',      'TEU volume from shipping line',             'TEU',      '8500, 3200'),
('shipping_line_revenue', 'revenue_vnd',      'BIGINT',             'Doanh thu từ hãng tàu',           'Revenue from shipping line',                'VND',      '12000000000, 5000000000'),
('shipping_line_revenue', 'num_vessel_calls', 'INT',                'Số chuyến tàu cập cảng',          'Number of vessel calls',                    'lượt',     '12, 8, 4'),

-- ── vessel_calls (fact) ────────────────────────────────────────────────────
('vessel_calls', 'id',                  'INT AUTO_INCREMENT', 'Khóa chính tự tăng',                  'Auto-increment primary key',                NULL,       '1, 2, 3'),
('vessel_calls', 'port_id',             'VARCHAR(5)',         'Mã cảng (FK → ports)',                 'Port identifier',                           NULL,       'NDV, GML, PHL, DQT'),
('vessel_calls', 'shipping_line_id',    'VARCHAR(10)',        'Mã hãng tàu (FK → shipping_lines)',    'Shipping line identifier',                  NULL,       'MSK, CMA'),
('vessel_calls', 'vessel_name',         'VARCHAR(100)',       'Tên tàu',                               'Vessel name',                               NULL,       'CMA CGM MARCO POLO, EVER GIVEN'),
('vessel_calls', 'vessel_capacity_teu', 'INT',                'Sức chứa tàu',                         'Vessel TEU capacity',                       'TEU',      '18000, 8500, 2500'),
('vessel_calls', 'actual_volume_teu',   'INT',                'Sản lượng thực tế xếp dỡ',            'Actual TEU handled',                        'TEU',      '1200, 850, 350'),
('vessel_calls', 'arrival_time',        'DATETIME',           'Thời gian tàu cập cảng',               'Vessel arrival time',                       NULL,       '2024-03-15 08:30:00'),
('vessel_calls', 'departure_time',      'DATETIME',           'Thời gian tàu rời cảng',               'Vessel departure time',                     NULL,       '2024-03-16 22:15:00'),
('vessel_calls', 'turnaround_hours',    'DECIMAL(5,1)',       'Thời gian quay vòng tàu',              'Turnaround time (arrival to departure)',     'giờ',      '36.5, 24.0, 18.8'),
('vessel_calls', 'cargo_types_handled', 'VARCHAR(200)',       'Danh sách loại hàng xử lý',           'Cargo types handled (comma-separated)',     NULL,       'CONT_DRY,CONT_REEFER'),

-- ── equipment_utilization (fact) ───────────────────────────────────────────
('equipment_utilization', 'id',                          'INT AUTO_INCREMENT', 'Khóa chính tự tăng',         'Auto-increment primary key',                NULL,       '1, 2, 3'),
('equipment_utilization', 'equipment_id',                'VARCHAR(15)',        'Mã thiết bị (FK → equipment)', 'Equipment identifier',                    NULL,       'QC-NDV-01, RTG-GML-03'),
('equipment_utilization', 'port_id',                     'VARCHAR(5)',         'Mã cảng (FK → ports)',        'Port identifier',                           NULL,       'NDV, GML'),
('equipment_utilization', 'month',                       'DATE',               'Tháng báo cáo',               'Report month',                              NULL,       '2024-01-01, 2025-06-01'),
('equipment_utilization', 'total_hours',                 'INT',                'Tổng số giờ trong tháng',     'Total hours in month (default 720)',         'giờ',      '720, 744'),
('equipment_utilization', 'operating_hours',             'INT',                'Số giờ vận hành thực tế',     'Actual operating hours',                    'giờ',      '520, 680'),
('equipment_utilization', 'idle_hours',                  'INT',                'Số giờ chờ / không tải',      'Idle / waiting hours',                      'giờ',      '150, 20'),
('equipment_utilization', 'maintenance_hours',           'INT',                'Số giờ bảo trì',              'Maintenance hours',                         'giờ',      '50, 20, 120'),
('equipment_utilization', 'moves_count',                 'INT',                'Số lượt nâng hạ / di chuyển', 'Number of moves (lifts)',                   'lượt',     '15600, 8400, 21000'),
('equipment_utilization', 'availability_pct',            'DECIMAL(5,2)',       'Tỷ lệ sẵn sàng',              'Availability rate',                         '%',        '95.50, 88.00, 72.00'),
('equipment_utilization', 'productivity_moves_per_hour', 'DECIMAL(5,1)',       'Năng suất (lượt/giờ)',        'Productivity in moves per operating hour',   'lượt/giờ', '28.0, 32.5, 22.0'),

-- ── equipment_maintenance (fact) ───────────────────────────────────────────
('equipment_maintenance', 'id',               'INT AUTO_INCREMENT', 'Khóa chính tự tăng',            'Auto-increment primary key',                NULL,       '1, 2, 3'),
('equipment_maintenance', 'equipment_id',     'VARCHAR(15)',        'Mã thiết bị (FK → equipment)',   'Equipment identifier',                      NULL,       'QC-NDV-01, RTG-GML-03'),
('equipment_maintenance', 'port_id',          'VARCHAR(5)',         'Mã cảng (FK → ports)',           'Port identifier',                           NULL,       'NDV, GML'),
('equipment_maintenance', 'maintenance_type', 'ENUM',               'Loại bảo trì',                   'Maintenance type classification',           NULL,       'routine, major_overhaul, emergency, inspection'),
('equipment_maintenance', 'start_date',       'DATE',               'Ngày bắt đầu bảo trì',          'Maintenance start date',                    NULL,       '2024-06-15, 2025-01-20'),
('equipment_maintenance', 'end_date',         'DATE',               'Ngày kết thúc bảo trì',         'Maintenance end date',                      NULL,       '2024-06-16, 2025-02-10'),
('equipment_maintenance', 'cost_vnd',         'BIGINT',             'Chi phí bảo trì',                'Maintenance cost',                          'VND',      '150000000, 8500000000'),
('equipment_maintenance', 'description',      'TEXT',               'Mô tả công việc bảo trì',       'Maintenance work description',              NULL,       'Thay cáp thép STS Crane #2, Đại tu động cơ RTG'),

-- ── customer_revenue (fact) ────────────────────────────────────────────────
('customer_revenue', 'id',            'INT AUTO_INCREMENT', 'Khóa chính tự tăng',                   'Auto-increment primary key',                NULL,       '1, 2, 3'),
('customer_revenue', 'port_id',       'VARCHAR(5)',         'Mã cảng (FK → ports)',                  'Port identifier',                           NULL,       'NDV, GML, PHL, DQT'),
('customer_revenue', 'month',         'DATE',               'Tháng báo cáo',                         'Report month',                              NULL,       '2024-01-01, 2025-06-01'),
('customer_revenue', 'customer_id',   'VARCHAR(20)',        'Mã khách hàng (FK → customers)',        'Customer identifier',                       NULL,       'CUS001, CUS040'),
('customer_revenue', 'cargo_type_id', 'VARCHAR(20)',        'Mã loại hàng (FK → cargo_types)',       'Cargo type identifier',                     NULL,       'CONT_DRY, BULK'),
('customer_revenue', 'volume_teu',    'INT',                'Sản lượng TEU',                         'Volume in TEU',                             'TEU',      '3500, 800'),
('customer_revenue', 'volume_tons',   'INT',                'Sản lượng tấn',                         'Volume in tons',                            'tấn',      '15000, 45000'),
('customer_revenue', 'revenue_vnd',   'BIGINT',             'Doanh thu từ khách hàng',               'Revenue from customer',                     'VND',      '5500000000, 1200000000'),

-- ── _meta_tables (metadata) ───────────────────────────────────────────────
('_meta_tables', 'table_name',       'VARCHAR(50)', 'Tên bảng trong database',                'Table name',                                NULL,       'ports, port_revenue'),
('_meta_tables', 'description_vi',   'TEXT',         'Mô tả bảng tiếng Việt',                  'Table description in Vietnamese',           NULL,       NULL),
('_meta_tables', 'description_en',   'TEXT',         'Mô tả bảng tiếng Anh',                   'Table description in English',              NULL,       NULL),
('_meta_tables', 'business_context', 'TEXT',         'Ngữ cảnh nghiệp vụ cho AI engine',      'Business context for AI engine',            NULL,       NULL),

-- ── _meta_columns (metadata) ──────────────────────────────────────────────
('_meta_columns', 'id',             'INT AUTO_INCREMENT', 'Khóa chính tự tăng',                 'Auto-increment primary key',                NULL,       '1, 2, 3'),
('_meta_columns', 'table_name',     'VARCHAR(50)',        'Tên bảng chứa cột',                  'Parent table name',                         NULL,       'ports, port_revenue'),
('_meta_columns', 'column_name',    'VARCHAR(50)',        'Tên cột',                              'Column name',                               NULL,       'port_id, month, total_revenue_vnd'),
('_meta_columns', 'data_type',      'VARCHAR(50)',        'Kiểu dữ liệu',                        'Data type',                                 NULL,       'VARCHAR(5), INT, BIGINT, DATE'),
('_meta_columns', 'description_vi', 'TEXT',               'Mô tả cột tiếng Việt',                'Column description in Vietnamese',          NULL,       NULL),
('_meta_columns', 'description_en', 'TEXT',               'Mô tả cột tiếng Anh',                 'Column description in English',             NULL,       NULL),
('_meta_columns', 'unit',           'VARCHAR(20)',        'Đơn vị đo',                            'Unit of measure',                           NULL,       'VND, TEU, tấn, %, giờ'),
('_meta_columns', 'example_values', 'TEXT',               'Giá trị mẫu',                          'Example values for AI context',             NULL,       NULL),

-- ── _meta_kpi (metadata) ──────────────────────────────────────────────────
('_meta_kpi', 'kpi_id',            'VARCHAR(30)',  'Mã KPI',                                 'KPI identifier',                            NULL,       'gross_margin, crane_productivity'),
('_meta_kpi', 'kpi_name_vi',       'VARCHAR(100)', 'Tên KPI tiếng Việt',                     'KPI name in Vietnamese',                    NULL,       'Biên lợi nhuận gộp'),
('_meta_kpi', 'kpi_name_en',       'VARCHAR(100)', 'Tên KPI tiếng Anh',                      'KPI name in English',                       NULL,       'Gross Margin'),
('_meta_kpi', 'formula_sql',       'TEXT',          'Công thức SQL tính KPI',                 'SQL formula to calculate KPI',              NULL,       NULL),
('_meta_kpi', 'description_vi',    'TEXT',          'Giải thích KPI tiếng Việt',              'KPI description in Vietnamese',             NULL,       NULL),
('_meta_kpi', 'related_questions', 'TEXT',          'Câu hỏi mẫu liên quan đến KPI',         'Example questions related to this KPI',     NULL,       NULL),

-- ── _meta_glossary (metadata) ─────────────────────────────────────────────
('_meta_glossary', 'term_id',    'VARCHAR(30)',  'Mã thuật ngữ',                           'Term identifier',                           NULL,       'teu, sts_crane, berth'),
('_meta_glossary', 'term_vi',    'VARCHAR(100)', 'Thuật ngữ tiếng Việt',                    'Term in Vietnamese',                        NULL,       'Cẩu giàn bờ, Cầu cảng'),
('_meta_glossary', 'term_en',    'VARCHAR(100)', 'Thuật ngữ tiếng Anh',                     'Term in English',                           NULL,       'STS Crane, Berth'),
('_meta_glossary', 'definition', 'TEXT',          'Định nghĩa / giải thích',                'Definition / explanation',                  NULL,       NULL);


-- ============================================================================
-- 3. _meta_kpi — 10 KPI nghiệp vụ cảng với công thức SQL
-- ============================================================================

INSERT INTO `_meta_kpi` (`kpi_id`, `kpi_name_vi`, `kpi_name_en`, `formula_sql`, `description_vi`, `related_questions`) VALUES

('gross_margin',
 'Biên lợi nhuận gộp',
 'Gross Margin',
 'SELECT
    r.port_id,
    r.month,
    SUM(r.total_revenue_vnd) AS total_revenue,
    SUM(c.cost_amount_vnd)   AS total_cost,
    ROUND(
      (SUM(r.total_revenue_vnd) - SUM(c.cost_amount_vnd)) * 100.0
      / NULLIF(SUM(r.total_revenue_vnd), 0), 1
    ) AS gross_margin_pct
FROM (
    SELECT port_id, month, SUM(total_revenue_vnd) AS total_revenue_vnd
    FROM port_revenue
    GROUP BY port_id, month
) r
JOIN (
    SELECT port_id, month, SUM(cost_amount_vnd) AS cost_amount_vnd
    FROM operating_costs
    GROUP BY port_id, month
) c ON r.port_id = c.port_id AND r.month = c.month
GROUP BY r.port_id, r.month
ORDER BY r.port_id, r.month;',
 'Tỷ lệ lợi nhuận gộp = (Doanh thu - Chi phí vận hành) / Doanh thu × 100. Phản ánh hiệu quả khai thác cảng trước chi phí tài chính. Benchmark ngành: 25-35%.',
 'Biên lợi nhuận gộp của từng cảng là bao nhiêu? | Cảng nào có margin cao nhất? | Margin thay đổi thế nào theo thời gian? | So sánh gross margin giữa các cảng'),

('revenue_per_teu',
 'Doanh thu trên TEU',
 'Revenue per TEU',
 'SELECT
    port_id,
    month,
    SUM(total_revenue_vnd) AS total_revenue,
    SUM(volume_teu)        AS total_teu,
    ROUND(SUM(total_revenue_vnd) / NULLIF(SUM(volume_teu), 0), 0) AS revenue_per_teu
FROM port_revenue
WHERE volume_teu > 0
GROUP BY port_id, month
ORDER BY port_id, month;',
 'Doanh thu trung bình trên mỗi TEU xếp dỡ. Phản ánh đơn giá dịch vụ và cơ cấu hàng hóa. Cảng có nhiều hàng lạnh/OOG sẽ có revenue_per_teu cao hơn.',
 'Doanh thu trên mỗi TEU của từng cảng? | So sánh đơn giá giữa các cảng | Revenue per TEU tăng hay giảm?'),

('cost_per_teu',
 'Chi phí trên TEU',
 'Cost per TEU',
 'SELECT
    oc.port_id,
    oc.month,
    SUM(oc.cost_amount_vnd) AS total_cost,
    SUM(ct.volume_teu)      AS total_teu,
    ROUND(SUM(oc.cost_amount_vnd) / NULLIF(SUM(ct.volume_teu), 0), 0) AS cost_per_teu
FROM (
    SELECT port_id, month, SUM(cost_amount_vnd) AS cost_amount_vnd
    FROM operating_costs
    GROUP BY port_id, month
) oc
JOIN (
    SELECT port_id, month, SUM(volume_teu) AS volume_teu
    FROM container_throughput
    WHERE volume_teu > 0
    GROUP BY port_id, month
) ct ON oc.port_id = ct.port_id AND oc.month = ct.month
GROUP BY oc.port_id, oc.month
ORDER BY oc.port_id, oc.month;',
 'Chi phí vận hành trung bình trên mỗi TEU. Kết hợp với revenue_per_teu để đánh giá lợi nhuận trên đơn vị. Cost/TEU giảm khi sản lượng tăng (economies of scale).',
 'Chi phí trên mỗi TEU của từng cảng? | Cảng nào có cost/TEU thấp nhất? | Chi phí trên TEU thay đổi theo thời gian?'),

('crane_productivity',
 'Năng suất cẩu',
 'Crane Productivity',
 'SELECT
    eu.equipment_id,
    e.equipment_name,
    e.port_id,
    eu.month,
    eu.moves_count,
    eu.operating_hours,
    ROUND(eu.moves_count / NULLIF(eu.operating_hours, 0), 1) AS moves_per_hour
FROM equipment_utilization eu
JOIN equipment e ON eu.equipment_id = e.equipment_id
WHERE e.equipment_type IN (''QC'', ''STS'')
   OR e.equipment_type LIKE ''%crane%''
ORDER BY e.port_id, eu.month;',
 'Số lượt nâng hạ (moves) trên giờ vận hành của cẩu giàn bờ STS. Benchmark Việt Nam: 25-32 moves/h. GML dẫn đầu ~32 moves/h, NDV ~28 moves/h.',
 'Năng suất cẩu của từng cảng? | Cẩu nào hiệu quả nhất? | Năng suất cẩu thay đổi theo thời gian? | So sánh moves/hour giữa các cảng'),

('vessel_turnaround',
 'Thời gian quay vòng tàu',
 'Vessel Turnaround Time',
 'SELECT
    port_id,
    DATE_FORMAT(arrival_time, ''%Y-%m'') AS report_month,
    COUNT(*)                             AS num_calls,
    ROUND(AVG(turnaround_hours), 1)      AS avg_turnaround_hours,
    ROUND(MIN(turnaround_hours), 1)      AS min_turnaround_hours,
    ROUND(MAX(turnaround_hours), 1)      AS max_turnaround_hours
FROM vessel_calls
WHERE turnaround_hours IS NOT NULL
GROUP BY port_id, DATE_FORMAT(arrival_time, ''%Y-%m'')
ORDER BY port_id, report_month;',
 'Thời gian trung bình từ lúc tàu cập bến đến khi rời bến. Bao gồm chờ cầu, xếp dỡ, làm thủ tục. Turnaround thấp = hiệu quả cao, hãng tàu ưa thích.',
 'Thời gian quay vòng tàu trung bình? | Cảng nào có turnaround nhanh nhất? | Turnaround time thay đổi thế nào? | So sánh turnaround giữa các cảng'),

('berth_occupancy',
 'Tỷ lệ sử dụng cầu cảng',
 'Berth Occupancy Rate',
 'SELECT
    vc.port_id,
    DATE_FORMAT(vc.arrival_time, ''%Y-%m'') AS report_month,
    SUM(vc.turnaround_hours)                AS total_berth_hours,
    p.num_berths,
    720                                      AS hours_per_month,
    ROUND(
      SUM(vc.turnaround_hours) * 100.0
      / (p.num_berths * 720), 1
    ) AS berth_occupancy_pct
FROM vessel_calls vc
JOIN ports p ON vc.port_id = p.port_id
WHERE vc.turnaround_hours IS NOT NULL
GROUP BY vc.port_id, DATE_FORMAT(vc.arrival_time, ''%Y-%m''), p.num_berths
ORDER BY vc.port_id, report_month;',
 'Tỷ lệ thời gian bến có tàu neo đậu trên tổng thời gian khả dụng (num_berths × 720h/tháng). BOR > 70% là cao, có thể gây chờ đợi. BOR < 40% cho thấy dư thừa.',
 'Tỷ lệ sử dụng cầu cảng của từng cảng? | Cảng nào đang quá tải? | Berth occupancy thay đổi theo mùa? | Cảng nào cần thêm cầu?'),

('capacity_utilization',
 'Tỷ lệ sử dụng công suất',
 'Capacity Utilization',
 'SELECT
    ct.port_id,
    YEAR(ct.month)            AS report_year,
    SUM(ct.volume_teu)        AS actual_teu,
    p.design_capacity_teu,
    ROUND(
      SUM(ct.volume_teu) * 100.0
      / NULLIF(p.design_capacity_teu, 0), 1
    ) AS utilization_pct
FROM container_throughput ct
JOIN ports p ON ct.port_id = p.port_id
WHERE ct.volume_teu > 0
GROUP BY ct.port_id, YEAR(ct.month), p.design_capacity_teu
ORDER BY ct.port_id, report_year;',
 'Tỷ lệ sản lượng thực tế so với công suất thiết kế hàng năm. > 85% cần mở rộng, < 50% cần tối ưu khai thác. Dùng kết hợp với investment_projects để đánh giá nhu cầu đầu tư.',
 'Tỷ lệ sử dụng công suất của từng cảng? | Cảng nào sắp hết công suất? | Bao giờ cần mở rộng? | Capacity utilization trend'),

('equipment_availability',
 'Khả dụng thiết bị',
 'Equipment Availability',
 'SELECT
    eu.equipment_id,
    e.equipment_name,
    e.equipment_type,
    e.port_id,
    eu.month,
    eu.total_hours,
    eu.maintenance_hours,
    ROUND(
      (eu.total_hours - eu.maintenance_hours) * 100.0
      / NULLIF(eu.total_hours, 0), 1
    ) AS availability_pct
FROM equipment_utilization eu
JOIN equipment e ON eu.equipment_id = e.equipment_id
ORDER BY e.port_id, eu.month, e.equipment_type;',
 'Tỷ lệ thời gian thiết bị sẵn sàng hoạt động = (Tổng giờ - Giờ bảo trì) / Tổng giờ × 100. Availability < 80% cần kiểm tra lý do. Liên hệ với equipment_maintenance để xem lịch sử sửa chữa.',
 'Tỷ lệ khả dụng thiết bị? | Thiết bị nào thường xuyên hỏng? | Availability theo loại thiết bị? | So sánh availability giữa các cảng'),

('yoy_growth',
 'Tăng trưởng YoY',
 'Year-over-Year Growth',
 'SELECT
    cur.port_id,
    cur.month                                    AS current_month,
    cur.revenue                                  AS current_revenue,
    prev.revenue                                 AS previous_year_revenue,
    ROUND(
      (cur.revenue - prev.revenue) * 100.0
      / NULLIF(prev.revenue, 0), 1
    ) AS yoy_growth_pct
FROM (
    SELECT port_id, month, SUM(total_revenue_vnd) AS revenue
    FROM port_revenue
    GROUP BY port_id, month
) cur
JOIN (
    SELECT port_id, month, SUM(total_revenue_vnd) AS revenue
    FROM port_revenue
    GROUP BY port_id, month
) prev
  ON cur.port_id = prev.port_id
 AND prev.month  = DATE_SUB(cur.month, INTERVAL 12 MONTH)
ORDER BY cur.port_id, cur.month;',
 'So sánh doanh thu cùng tháng giữa 2 năm liên tiếp. Loại trừ ảnh hưởng mùa vụ. YoY âm liên tục nhiều tháng là tín hiệu cảnh báo. Áp dụng tương tự cho sản lượng TEU.',
 'Tăng trưởng doanh thu YoY? | Cảng nào tăng trưởng tốt nhất? | Tháng nào sụt giảm YoY? | So sánh tăng trưởng giữa các cảng'),

('shipping_line_concentration',
 'Mức độ tập trung hãng tàu',
 'Shipping Line Concentration (Top 3 Share)',
 'SELECT
    port_id,
    ROUND(
      SUM(CASE WHEN rn <= 3 THEN rev_share_pct ELSE 0 END), 1
    ) AS top3_share_pct
FROM (
    SELECT
        port_id,
        shipping_line_id,
        SUM(revenue_vnd) * 100.0
          / SUM(SUM(revenue_vnd)) OVER (PARTITION BY port_id) AS rev_share_pct,
        ROW_NUMBER() OVER (
            PARTITION BY port_id
            ORDER BY SUM(revenue_vnd) DESC
        ) AS rn
    FROM shipping_line_revenue
    GROUP BY port_id, shipping_line_id
) ranked
GROUP BY port_id
ORDER BY port_id;',
 'Tỷ trọng doanh thu của top 3 hãng tàu tại mỗi cảng. Top 3 chiếm > 60% là mức tập trung cao, rủi ro nếu 1 hãng rời đi. Dùng phát hiện rủi ro churn hãng tàu.',
 'Top 3 hãng tàu chiếm bao nhiêu % doanh thu? | Mức độ tập trung hãng tàu? | Cảng nào phụ thuộc nhiều nhất vào 1 hãng tàu? | Rủi ro mất hãng tàu lớn');


-- ============================================================================
-- 4. _meta_glossary — Từ điển thuật ngữ ngành cảng (25 thuật ngữ)
-- ============================================================================

INSERT INTO `_meta_glossary` (`term_id`, `term_vi`, `term_en`, `definition`) VALUES

('teu',
 'TEU',
 'Twenty-foot Equivalent Unit',
 'Đơn vị đo lường tiêu chuẩn trong vận tải container. 1 TEU = 1 container 20 feet (dài 6.1m × rộng 2.44m × cao 2.59m). Container 40 feet = 2 TEU. Sản lượng cảng thường đo bằng TEU/năm.'),

('feu',
 'FEU',
 'Forty-foot Equivalent Unit',
 'Đơn vị đo container 40 feet. 1 FEU = 2 TEU. Container 40ft phổ biến hơn 20ft trong thương mại quốc tế (chiếm ~70% lượng container lưu thông).'),

('sts_crane',
 'Cẩu giàn bờ (STS)',
 'Ship-to-Shore Crane (STS / Quay Crane)',
 'Cẩu cỡ lớn lắp cố định trên cầu cảng, dùng xếp dỡ container từ tàu lên bờ và ngược lại. Năng suất đo bằng moves/hour. Benchmark VN: 25-32 moves/h. GML dẫn đầu ~32 moves/h, NDV ~28 moves/h.'),

('rtg_crane',
 'Cẩu giàn bãi (RTG)',
 'Rubber Tyred Gantry Crane (RTG)',
 'Cẩu di chuyển trên bánh lốp trong bãi container, dùng xếp chồng và sắp xếp container trong bãi. RTG thường xếp được 5-6 tầng container, quản lý tối ưu diện tích bãi.'),

('mhc',
 'Cẩu di động (MHC)',
 'Mobile Harbour Crane (MHC)',
 'Cẩu di động đa năng trên bánh lốp, linh hoạt xử lý nhiều loại hàng (container, hàng rời, hàng siêu trường siêu trọng). Phù hợp cảng đa năng như DQT.'),

('berth',
 'Cầu cảng / Bến tàu',
 'Berth',
 'Vị trí neo đậu tàu dọc theo bờ kè cảng. Mỗi berth có chiều dài và mớn nước nhất định, phù hợp với cỡ tàu khác nhau. Số berth quyết định khả năng tiếp nhận đồng thời nhiều tàu.'),

('quay',
 'Bến cảng / Kè cảng',
 'Quay',
 'Kết cấu bờ kè dọc mép nước cho tàu cập, bao gồm đường ray cẩu STS, hệ thống chằng buộc và hạ tầng điện/nước. quay_length_m trong bảng ports đo tổng chiều dài kè.'),

('draft',
 'Mớn nước / Độ sâu luồng',
 'Draft / Water Depth',
 'Độ sâu ngập nước của tàu từ đường nước đến đáy tàu. Cảng phải có mớn nước lớn hơn draft tàu. GML (Cái Mép) mớn nước ~16m tiếp nhận tàu mẹ cỡ lớn. PHL (sông Sài Gòn) chỉ ~8.5m.'),

('feeder',
 'Tàu gom hàng',
 'Feeder Vessel',
 'Tàu cỡ nhỏ-trung (500-3000 TEU) chạy tuyến ngắn gom/rải hàng từ cảng nhỏ đến hub port, nơi hàng được chuyển sang tàu mẹ. Phổ biến tại NDV, PHL, DQT.'),

('mother_vessel',
 'Tàu mẹ',
 'Mother Vessel',
 'Tàu container cỡ lớn (>8000 TEU) chạy tuyến viễn dương trực tiếp (Á-Âu, xuyên Thái Bình Dương). Chỉ ghé cảng nước sâu. Tại Gemadept, chỉ GML (Cái Mép) tiếp nhận tàu mẹ.'),

('icd',
 'Cảng cạn / Cảng nội địa',
 'Inland Container Depot (ICD)',
 'Bãi container nội địa, làm thủ tục hải quan và trung chuyển hàng giữa các phương thức vận tải (đường bộ, đường sắt, đường thủy). Giúp giảm tải cho cảng biển.'),

('handling_fee',
 'Phí bốc xếp',
 'Handling Fee',
 'Phí thu cho dịch vụ xếp dỡ hàng hóa lên/xuống tàu và di chuyển trong cảng. Nguồn doanh thu chính của cảng (~70-75% tổng doanh thu). Đơn giá khác nhau theo loại hàng.'),

('dwell_time',
 'Thời gian lưu bãi',
 'Dwell Time',
 'Thời gian container lưu tại bãi cảng từ khi dỡ xuống đến khi được chở đi. Dwell time dài → tăng doanh thu lưu bãi nhưng giảm năng lực thông qua của cảng. Thường miễn phí 3-5 ngày đầu.'),

('turnaround_time',
 'Thời gian quay vòng tàu',
 'Turnaround Time',
 'Tổng thời gian tàu ở cảng từ lúc cập bến đến khi rời bến, bao gồm: chờ cầu, xếp dỡ hàng, làm thủ tục. Thấp hơn = hiệu quả hơn, hãng tàu ưa thích cảng có turnaround nhanh.'),

('throughput',
 'Sản lượng thông qua',
 'Throughput',
 'Tổng lượng hàng hóa xếp dỡ qua cảng trong một khoảng thời gian. Đo bằng TEU (container) hoặc tấn (hàng rời). Là chỉ tiêu cơ bản đánh giá quy mô hoạt động cảng.'),

('capacity_utilization',
 'Tỷ lệ sử dụng công suất',
 'Capacity Utilization',
 'Tỷ lệ sản lượng thực tế so với công suất thiết kế của cảng (%). > 85% cần xem xét mở rộng, < 50% cần tối ưu khai thác. Tính bằng: Actual TEU / design_capacity_teu × 100.'),

('breakbulk',
 'Hàng bách hóa',
 'Breakbulk Cargo',
 'Hàng đóng gói riêng lẻ (kiện, bao, cuộn) nhưng không vào container: thép cuộn, gỗ xẻ, máy móc. Tốn nhân công xếp dỡ hơn container, đo bằng tấn thay vì TEU.'),

('bulk',
 'Hàng rời',
 'Bulk Cargo',
 'Hàng hóa không đóng container, xếp rời trong hầm tàu: clinker, xi măng, thép, phân bón, ngũ cốc. Đo bằng tấn. DQT (Dung Quất) chuyên hàng rời, đặc biệt clinker xuất khẩu.'),

('reefer',
 'Hàng lạnh / Container lạnh',
 'Reefer Container',
 'Container có máy lạnh duy trì nhiệt độ (-25°C đến +25°C), dùng cho hàng thực phẩm, dược phẩm, hóa chất. Doanh thu/unit cao hơn container thường ~30-40%. Cần ổ cắm điện tại bãi.'),

('oog',
 'Hàng quá khổ',
 'Out of Gauge (OOG)',
 'Hàng hóa vượt kích thước container tiêu chuẩn, cần xử lý đặc biệt bằng flat rack hoặc open top container. Phí bốc xếp cao nhất trong các loại hàng. VD: máy móc công nghiệp, turbine.'),

('alliance',
 'Liên minh hãng tàu',
 'Shipping Alliance',
 'Nhóm hãng tàu hợp tác chia sẻ tuyến và slot tàu. 3 liên minh chính (tính đến 2025): Ocean Alliance (CMA-CGM, COSCO, Evergreen), THE Alliance (Hapag-Lloyd, ONE, Yang Ming, HMM), Gemini (Maersk, Hapag-Lloyd từ 2025).'),

('deep_sea_port',
 'Cảng nước sâu',
 'Deep-sea Port',
 'Cảng có mớn nước lớn (>14m) tiếp nhận được tàu mẹ viễn dương. Cái Mép - Thị Vải (GML/Gemalink) là cảng nước sâu duy nhất trong hệ thống Gemadept, mớn nước ~16m.'),

('river_port',
 'Cảng sông',
 'River Port',
 'Cảng nằm trên sông/kênh, mớn nước hạn chế (<10m), chủ yếu tiếp nhận tàu feeder và sà lan. VD: PHL (Phước Long) trên sông Sài Gòn. Chi phí vận hành thấp hơn cảng nước sâu.'),

('gross_margin',
 'Biên lợi nhuận gộp',
 'Gross Margin',
 'Tỷ lệ (Doanh thu - Chi phí vận hành) / Doanh thu × 100. Phản ánh hiệu quả khai thác cảng trước chi phí tài chính và thuế. Benchmark ngành cảng VN: 25-35%.'),

('opex',
 'Chi phí vận hành',
 'Operating Expenditure (OPEX)',
 'Tổng chi phí vận hành cảng hàng tháng, gồm: nhân công (~32%), khấu hao (~23%), năng lượng (~13%), bảo trì (~10%), thuê đất (~7%), khác (~15%). Dùng tính gross margin và cost/TEU. Lưu trong bảng operating_costs.');


SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================================
-- END OF METADATA
-- ============================================================================
