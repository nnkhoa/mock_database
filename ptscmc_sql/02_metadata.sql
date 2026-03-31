-- ============================================================
-- PTSC M&C Demo Database — Metadata
-- AI engine sử dụng metadata để hiểu schema và KPI
-- ============================================================

USE ptsc_mc_demo;

SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- _meta_tables: 14 records
INSERT INTO `_meta_tables` (`table_name`, `description_vi`, `description_en`, `business_context`, `row_count`) VALUES
('clients', 'Danh sách chủ đầu tư', 'Client/operator directory', 'Dùng để filter dự án theo chủ đầu tư, phân tích portfolio theo khách hàng', 4),
('cost_categories', '10 loại chi phí dự án', 'Project cost categories (10 types)', 'Phân loại chi phí theo nhóm LABOR/MATERIAL/SUBCON/OVERHEAD. Dùng cho phân tích cost overrun', 10),
('discipline_progress', 'Tiến độ theo chuyên ngành × tháng', 'Monthly discipline-level progress', 'Drill-down từ project_progress. Core table cho Scenario 2 (root cause)', NULL),
('disciplines', '7 chuyên ngành thi công', 'Construction disciplines (7 types)', 'Dùng để drill-down tiến độ và năng suất theo chuyên ngành. Sequence order phản ánh quy trình thi công', 7),
('manhour_logs', 'Manhour theo dự án × discipline × area × tháng', 'Detailed manhour logs', 'Granular nhất — tính productivity, overtime rate, headcount. Core cho Scenario 3-4', NULL),
('material_deliveries', 'Theo dõi PO vật tư', 'Purchase order tracking', 'PO-level: supplier, dates, prices. Core cho Scenario 2 (material delay root cause)', NULL),
('project_costs', 'Chi phí theo loại × tháng', 'Monthly cost tracking by category', 'Budget vs actual vs committed. Core cho Scenario 3 (margin & cost overrun)', NULL),
('project_progress', 'Tiến độ dự án theo tháng', 'Monthly project progress snapshots', 'planned_pct vs actual_pct → tính SPI. Core table cho Scenario 1 (portfolio overview)', NULL),
('projects', '5 dự án EPC/EPCIC đang chạy', 'Active project portfolio (5 projects)', 'Bảng trung tâm — mọi fact table đều JOIN qua project_id. Chứa thông tin hợp đồng, timeline, loại dự án', 5),
('quality_records', 'Chất lượng hàn theo tháng', 'Monthly quality metrics', 'Weld rejection rate, rework hours. Core cho Scenario 2 (quality root cause)', NULL),
('safety_incidents', 'Sự cố an toàn lao động', 'HSE incident records', 'Individual incidents. Core cho Scenario 1 (HSE flag) và Scenario 6 (portfolio health)', NULL),
('suppliers', '10 nhà cung cấp vật tư', 'Material suppliers (10 vendors)', 'Theo dõi performance nhà cung cấp: on-time delivery, giá. Liên kết với material_deliveries', 10),
('work_areas', 'Khu vực thi công trong yard', 'Yard work areas per project', 'Mỗi dự án chia 3-5 khu vực. Dùng để phân tích manhour và overtime theo khu vực', 17),
('workforce', '200 nhân sự mẫu', 'Workforce directory (200 workers)', 'Phân bổ nhân lực theo dự án, kỹ năng, chứng chỉ. Dùng cho resource planning', 200);

-- _meta_columns: 39 records
INSERT INTO `_meta_columns` (`id`, `table_name`, `column_name`, `data_type`, `description_vi`, `description_en`, `unit`, `example_values`) VALUES
(1, 'projects', 'project_id', 'VARCHAR(10)', 'Mã dự án', 'Project ID', NULL, 'PJ-001, PJ-002, PJ-003'),
(2, 'projects', 'project_name', 'VARCHAR(200)', 'Tên dự án đầy đủ', 'Full project name', NULL, 'Sao Vàng CPP'),
(3, 'projects', 'project_type', 'ENUM', 'Loại dự án', 'Project type', NULL, 'O&G, Renewables'),
(4, 'projects', 'contract_value_usd', 'DECIMAL(15,2)', 'Giá trị hợp đồng', 'Contract value', 'triệu USD', '280.00, 145.00'),
(5, 'projects', 'start_date', 'DATE', 'Ngày bắt đầu', 'Project start date', NULL, '2024-01-15'),
(6, 'projects', 'planned_end_date', 'DATE', 'Ngày kết thúc dự kiến', 'Planned end date', NULL, '2026-06-30'),
(7, 'project_progress', 'report_month', 'DATE', 'Tháng báo cáo (ngày 1)', 'Report month (1st day)', NULL, '2025-03-01'),
(8, 'project_progress', 'planned_pct', 'DECIMAL(5,2)', 'Tiến độ kế hoạch lũy kế', 'Cumulative planned progress', '%', '76.00'),
(9, 'project_progress', 'actual_pct', 'DECIMAL(5,2)', 'Tiến độ thực tế lũy kế', 'Cumulative actual progress', '%', '72.00'),
(10, 'project_progress', 'earned_value_usd', 'DECIMAL(15,2)', 'Earned Value (EVM)', 'Earned Value', 'USD', '195000000'),
(11, 'discipline_progress', 'discipline_id', 'VARCHAR(10)', 'Mã chuyên ngành', 'Discipline ID', NULL, 'PIPING, STRUCT'),
(12, 'discipline_progress', 'planned_pct', 'DECIMAL(5,2)', 'Tiến độ KH discipline', 'Discipline planned progress', '%', '53.00'),
(13, 'discipline_progress', 'actual_pct', 'DECIMAL(5,2)', 'Tiến độ TT discipline', 'Discipline actual progress', '%', '38.00'),
(14, 'discipline_progress', 'earned_mh', 'DECIMAL(12,2)', 'Manhour earned tháng', 'Monthly earned manhours', 'giờ', '15000'),
(15, 'discipline_progress', 'actual_mh', 'DECIMAL(12,2)', 'Manhour thực tế tháng', 'Monthly actual manhours', 'giờ', '18000'),
(16, 'manhour_logs', 'work_area_id', 'VARCHAR(20)', 'Mã khu vực thi công', 'Work area ID', NULL, 'AREA-SV-3'),
(17, 'manhour_logs', 'planned_mh', 'DECIMAL(12,2)', 'Manhour kế hoạch', 'Planned manhours', 'giờ', '5000'),
(18, 'manhour_logs', 'actual_mh', 'DECIMAL(12,2)', 'Manhour thực tế', 'Actual manhours', 'giờ', '5500'),
(19, 'manhour_logs', 'overtime_mh', 'DECIMAL(12,2)', 'Manhour tăng ca', 'Overtime manhours', 'giờ', '1200'),
(20, 'manhour_logs', 'earned_mh', 'DECIMAL(12,2)', 'Manhour earned', 'Earned manhours', 'giờ', '4800'),
(21, 'project_costs', 'cost_category_id', 'VARCHAR(20)', 'Mã loại chi phí', 'Cost category ID', NULL, 'LABOR-WELD'),
(22, 'project_costs', 'budgeted_amount', 'DECIMAL(15,2)', 'Ngân sách tháng', 'Monthly budget', 'USD', '500000'),
(23, 'project_costs', 'actual_amount', 'DECIMAL(15,2)', 'Chi phí thực tế tháng', 'Monthly actual cost', 'USD', '550000'),
(24, 'project_costs', 'committed_amount', 'DECIMAL(15,2)', 'Chi phí đã cam kết', 'Committed cost', 'USD', '520000'),
(25, 'material_deliveries', 'po_number', 'VARCHAR(30)', 'Số Purchase Order', 'PO number', NULL, 'PO-HP-031'),
(26, 'material_deliveries', 'material_type', 'VARCHAR(100)', 'Loại vật tư', 'Material type', NULL, 'Duplex SS Pipe, Carbon Steel Plate'),
(27, 'material_deliveries', 'planned_delivery_date', 'DATE', 'Ngày giao dự kiến', 'Planned delivery date', NULL, '2024-10-15'),
(28, 'material_deliveries', 'actual_delivery_date', 'DATE', 'Ngày giao thực tế', 'Actual delivery date', NULL, '2024-11-08'),
(29, 'material_deliveries', 'budgeted_unit_price', 'DECIMAL(12,2)', 'Đơn giá dự toán', 'Budgeted unit price', 'USD', '2500.00'),
(30, 'material_deliveries', 'actual_unit_price', 'DECIMAL(12,2)', 'Đơn giá thực tế', 'Actual unit price', 'USD', '2625.00'),
(31, 'quality_records', 'total_welds', 'INT', 'Tổng mối hàn kiểm tra', 'Total welds inspected', 'mối hàn', '500'),
(32, 'quality_records', 'rejected_welds', 'INT', 'Mối hàn bị reject', 'Rejected welds', 'mối hàn', '25'),
(33, 'quality_records', 'rejection_rate', 'DECIMAL(5,2)', 'Tỷ lệ reject', 'Rejection rate', '%', '5.00'),
(34, 'quality_records', 'rework_manhours', 'DECIMAL(10,2)', 'Giờ sửa chữa/làm lại', 'Rework manhours', 'giờ', '200'),
(35, 'safety_incidents', 'incident_type', 'VARCHAR(50)', 'Loại sự cố', 'Incident type', NULL, 'Near Miss, First Aid, Lost Time'),
(36, 'safety_incidents', 'severity', 'VARCHAR(20)', 'Mức độ nghiêm trọng', 'Severity level', NULL, 'Near Miss, Minor, Major, Critical'),
(37, 'safety_incidents', 'manhours_lost', 'DECIMAL(10,2)', 'Giờ công mất do sự cố', 'Lost manhours due to incident', 'giờ', '0, 24, 120'),
(38, 'workforce', 'skill_type', 'VARCHAR(50)', 'Loại kỹ năng', 'Skill type', NULL, 'Welder, Pipefitter, QC Inspector'),
(39, 'workforce', 'certification', 'VARCHAR(200)', 'Chứng chỉ nghề', 'Professional certifications', NULL, '6G SMAW, Duplex SS Welding');

-- _meta_kpi: 10 records
INSERT INTO `_meta_kpi` (`kpi_id`, `kpi_name`, `formula_sql`, `description_vi`, `description_en`, `related_tables`, `related_questions`) VALUES
('BURN_RATE', 'Budget Burn Rate', 'SELECT SUM(actual_amount) / NULLIF(SUM(budgeted_amount), 0) * 100 AS burn_rate FROM project_costs WHERE project_id = ?', 'Tỷ lệ tiêu thụ ngân sách = Actual / Budget × 100%', 'Budget consumption rate = Actual Cost / Budget × 100%', 'project_costs', 'Q3: Margin & cost overrun'),
('CPI', 'Cost Performance Index', 'SELECT SUM(earned_value_usd) / NULLIF(SUM(actual_amount), 0) AS cpi FROM project_progress pp JOIN (SELECT project_id, SUM(actual_amount) as actual_amount FROM project_costs WHERE report_month <= ? GROUP BY project_id) pc ON pp.project_id = pc.project_id WHERE pp.project_id = ? AND pp.report_month = ?', 'Chỉ số hiệu suất chi phí: >1 tiết kiệm, <1 vượt chi', 'Cost Performance Index: >1 under budget, <1 over budget', 'project_progress, project_costs', 'Q3: Margin & cost overrun'),
('EAC', 'Estimate at Completion', 'SELECT (SUM(budgeted_amount) / NULLIF(cpi, 1)) AS eac FROM (SELECT SUM(budgeted_amount) as budgeted_amount FROM project_costs WHERE project_id = ?) budget CROSS JOIN (SELECT SUM(earned_value_usd)/NULLIF(SUM(actual_amount),0) as cpi FROM ...) cpi_calc', 'Ước tính tổng chi phí khi hoàn thành = Budget / CPI', 'Estimate at Completion = Budget / CPI', 'project_costs, project_progress', 'Q3: Margin & cost overrun'),
('LTIR', 'Lost Time Incident Rate', 'SELECT (COUNT(CASE WHEN incident_type = "Lost Time" THEN 1 END) * 200000) / NULLIF(SUM(ml.actual_mh), 0) AS ltir FROM safety_incidents si JOIN (SELECT project_id, SUM(actual_mh) as actual_mh FROM manhour_logs GROUP BY project_id) ml ON si.project_id = ml.project_id WHERE si.project_id = ?', 'Tỷ lệ sự cố mất ngày công trên 200.000 giờ công', 'Lost Time Incident Rate per 200,000 manhours', 'safety_incidents, manhour_logs', 'Q6: Portfolio health'),
('ONTIME_DELIVERY', 'On-Time Delivery Rate', 'SELECT COUNT(CASE WHEN DATEDIFF(actual_delivery_date, planned_delivery_date) <= 5 THEN 1 END) * 100.0 / COUNT(*) FROM material_deliveries WHERE project_id = ? AND actual_delivery_date IS NOT NULL', 'Tỷ lệ PO giao hàng đúng hạn (±5 ngày). Benchmark: >90%', 'On-time delivery rate for POs (within 5 days tolerance)', 'material_deliveries', 'Q2: Material delay analysis'),
('OT_RATE', 'Overtime Rate', 'SELECT SUM(overtime_mh) / NULLIF(SUM(actual_mh), 0) AS ot_rate FROM manhour_logs WHERE project_id = ? AND work_area_id = ?', 'Tỷ lệ giờ tăng ca / tổng giờ thực tế. Benchmark: 10-20%', 'Overtime hours / Total actual hours. Benchmark: 10-20%', 'manhour_logs', 'Q3: Cost overrun (overtime driver)'),
('PRODUCTIVITY', 'Productivity Ratio', 'SELECT SUM(earned_mh) / NULLIF(SUM(actual_mh), 0) AS productivity FROM manhour_logs WHERE project_id = ?', 'Tỷ lệ năng suất = Earned MH / Actual MH. >1 hiệu quả cao, <1 lãng phí manhour', 'Productivity Ratio = Earned MH / Actual MH', 'manhour_logs', 'Q4: So sánh năng suất'),
('REJECTION_RATE', 'Weld Rejection Rate', 'SELECT rejection_rate FROM quality_records WHERE project_id = ? AND discipline_id = ? AND report_month = ?', 'Tỷ lệ mối hàn bị reject (%). Benchmark ngành O&G: 2-5%', 'Weld rejection rate (%). Industry benchmark: 2-5%', 'quality_records', 'Q2: Root cause analysis'),
('SPI', 'Schedule Performance Index', 'SELECT actual_pct / NULLIF(planned_pct, 0) AS spi FROM project_progress WHERE project_id = ? AND report_month = ?', 'Chỉ số hiệu suất tiến độ: >1 nhanh hơn kế hoạch, <1 chậm hơn kế hoạch', 'Schedule Performance Index: >1 ahead, <1 behind schedule', 'project_progress', 'Q1: Tổng quan tiến độ, Q5: Dự báo deadline'),
('TRIR', 'Total Recordable Incident Rate', 'SELECT (COUNT(CASE WHEN incident_type IN ("First Aid","Medical Treatment","Lost Time") THEN 1 END) * 200000) / NULLIF(SUM(ml.actual_mh), 0) AS trir FROM safety_incidents si JOIN (SELECT project_id, SUM(actual_mh) as actual_mh FROM manhour_logs GROUP BY project_id) ml ON si.project_id = ml.project_id WHERE si.project_id = ?', 'Tỷ lệ sự cố ghi nhận trên 200.000 giờ công. Benchmark: 0.3-0.8', 'Total Recordable Incident Rate per 200,000 manhours', 'safety_incidents, manhour_logs', 'Q6: Portfolio health');

-- _meta_glossary: 20 records
INSERT INTO `_meta_glossary` (`term_id`, `term_vi`, `term_en`, `abbreviation`, `definition`) VALUES
(1, 'Chỉ số hiệu suất tiến độ', 'Schedule Performance Index', 'SPI', 'SPI = Earned Value / Planned Value (hoặc actual_pct / planned_pct). >1.0 nghĩa là nhanh hơn kế hoạch, <1.0 là chậm hơn'),
(2, 'Chỉ số hiệu suất chi phí', 'Cost Performance Index', 'CPI', 'CPI = Earned Value / Actual Cost. >1.0 nghĩa là tiết kiệm hơn dự toán, <1.0 là vượt chi'),
(3, 'Quản lý giá trị thu được', 'Earned Value Management', 'EVM', 'Phương pháp đo lường hiệu suất dự án tích hợp phạm vi, tiến độ, và chi phí'),
(4, 'Tỷ lệ sự cố ghi nhận', 'Total Recordable Incident Rate', 'TRIR', 'Số sự cố ghi nhận × 200.000 / Tổng manhour. Dùng để so sánh an toàn giữa các dự án'),
(5, 'Tỷ lệ sự cố mất ngày công', 'Lost Time Incident Rate', 'LTIR', 'Số sự cố mất ngày công × 200.000 / Tổng manhour'),
(6, 'Thép không gỉ duplex', 'Duplex Stainless Steel', 'Duplex SS', 'Loại thép hợp kim austenitic-ferritic, chống ăn mòn tốt hơn carbon steel. Yêu cầu welding procedure đặc biệt (GTAW root, controlled heat input). Đắt hơn ~3-5x carbon steel'),
(7, 'Tổng thầu thiết kế - mua sắm - chế tạo - lắp đặt - chạy thử', 'Engineering Procurement Construction Installation Commissioning', 'EPCIC', 'Mô hình hợp đồng trọn gói từ thiết kế đến chạy thử. PTSC M&C là tổng thầu EPCIC'),
(8, 'Cấu trúc phân chia công việc', 'Work Breakdown Structure', 'WBS', 'Cấu trúc phân cấp chia nhỏ phạm vi dự án thành các gói công việc quản lý được'),
(9, 'Báo cáo không phù hợp', 'Non-Conformance Report', 'NCR', 'Tài liệu ghi nhận sai lệch so với tiêu chuẩn/quy trình. Yêu cầu corrective action'),
(10, 'Kiểm tra không phá hủy', 'Non-Destructive Testing', 'NDT', 'Phương pháp kiểm tra chất lượng mối hàn mà không phá hủy mẫu: RT (chụp X-quang), UT (siêu âm), MT (từ tính), PT (thẩm thấu)'),
(11, 'Giàn xử lý trung tâm', 'Central Processing Platform', 'CPP', 'Công trình ngoài khơi chính nơi xử lý dầu/khí khai thác từ các giàn đầu giếng'),
(12, 'Giàn đầu giếng', 'Wellhead Platform', 'WHP', 'Giàn nhỏ đặt trực tiếp trên miệng giếng, kết nối đường ống về CPP'),
(13, 'Trạm biến áp ngoài khơi', 'Offshore Substation', 'OSS', 'Công trình ngoài khơi cho điện gió — thu gom, biến đổi và truyền tải điện từ turbine về bờ'),
(14, 'Sự cố suýt xảy ra', 'Near Miss', NULL, 'Sự kiện nguy hiểm nhưng không gây thương tích. Theo dõi near-miss là chỉ số dẫn (leading indicator) cho an toàn'),
(15, 'Giá trị thu được', 'Earned Value', 'EV', 'Giá trị công việc đã hoàn thành tính theo ngân sách. EV = Budget × actual_pct'),
(16, 'Giá trị kế hoạch', 'Planned Value', 'PV', 'Giá trị công việc dự kiến hoàn thành theo kế hoạch. PV = Budget × planned_pct'),
(17, 'Hợp đồng trọn gói', 'Lump Sum Contract', NULL, 'Hợp đồng giá cố định — nhà thầu chịu rủi ro cost overrun. Phổ biến nhất trong EPC offshore VN'),
(18, 'Năng suất lao động', 'Productivity Ratio', NULL, 'Earned Manhour / Actual Manhour. >1.0 = hiệu quả cao. Bị ảnh hưởng bởi overtime (diminishing returns), learning curve, điều kiện thời tiết'),
(19, 'Ước tính chi phí hoàn thành', 'Estimate at Completion', 'EAC', 'EAC = Budget / CPI. Dự báo tổng chi phí khi hoàn thành dự án dựa trên hiệu suất chi phí hiện tại'),
(20, 'An toàn - Sức khỏe - Môi trường', 'Health Safety Environment', 'HSE', 'Bộ phận quản lý an toàn lao động, sức khỏe nghề nghiệp và bảo vệ môi trường tại công trường');

