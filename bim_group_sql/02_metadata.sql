-- ============================================================================
-- BIM Group Real Estate & Construction Demo - Metadata
-- Mo ta: Populate _meta_tables, _meta_columns, _meta_kpi, _meta_glossary
-- Database: bim_realestate_demo
-- ============================================================================

USE bim_realestate_demo;

-- ============================================================================
-- _meta_tables
-- ============================================================================

INSERT INTO _meta_tables (table_name, description_vi, table_type, grain, row_count_estimate) VALUES
('clusters', 'Cụm dự án theo vùng địa lý. BIM Group có 4 cluster: Hạ Long, Phú Quốc, Hà Nội, Viêng Chăn (Lào).', 'dimension', NULL, 4),
('projects', 'Dự án BĐS đang triển khai. Mỗi dự án thuộc 1 cluster, có ngân sách, tiến độ, trạng thái riêng.', 'dimension', NULL, 8),
('properties', 'BĐS đang vận hành (resort, khách sạn, căn hộ dịch vụ). Mỗi property có đối tác quản lý thương hiệu quốc tế.', 'dimension', NULL, 6),
('work_packages', 'Hạng mục công việc xây dựng: móng kết cấu, cơ điện (M&E), nội thất, facade, cảnh quan, MEP, PCCC, hạ tầng.', 'dimension', NULL, 8),
('contractors', 'Nhà thầu xây dựng gồm tổng thầu và thầu phụ chuyên ngành, hoạt động tại các vùng khác nhau.', 'dimension', NULL, 18),
('materials', 'Vật liệu xây dựng chính được theo dõi giá hàng tháng: thép, xi măng, cát, gạch, gỗ, kính.', 'dimension', NULL, 6),
('budget_disbursements', 'Ngân sách giải ngân hàng tháng theo dự án. So sánh kế hoạch vs thực tế, có lũy kế.', 'fact', 'project x month', 144),
('construction_costs', 'Chi phí xây dựng chi tiết theo dự án, hạng mục, nhà thầu, tháng. Dùng để phân tích vượt dự toán.', 'fact', 'project x work_package x contractor x month', 2000),
('change_orders', 'Phát sinh thay đổi thiết kế/yêu cầu. Ghi nhận lý do, giá trị, nhà thầu liên quan.', 'fact', 'per event', 25),
('material_prices', 'Giá vật liệu xây dựng hàng tháng. Theo dõi biến động giá để phân tích tác động chi phí.', 'fact', 'material x month', 108),
('project_milestones', 'Mốc tiến độ dự án: ngày kế hoạch vs thực tế, trạng thái hoàn thành.', 'fact', 'project x milestone', 56),
('project_financials', 'Chỉ số tài chính tổng hợp mỗi dự án: chi phí/m2, margin dự kiến, IRR, payback.', 'fact', 'per project', 8),
('project_commitments', 'Cam kết bàn giao khách hàng: deadline, số đơn vị, điều khoản phạt.', 'fact', 'per project', 5),
('financing', 'Khoản vay từng dự án: ngân hàng, dư nợ, lãi suất. Dùng tính chi phí tài chính khi delay.', 'fact', 'per project', 8),
('hospitality_revenue', 'Doanh thu vận hành hospitality hàng tháng: phòng, F&B, khác. Kèm ADR và rooms sold.', 'fact', 'property x month', 108),
('hospitality_costs', 'Chi phí vận hành hospitality hàng tháng theo loại: nhân sự, điện nước, bảo trì, marketing, phí quản lý.', 'fact', 'property x month x cost_category', 650),
('occupancy_daily', 'Dữ liệu phòng hàng ngày: phòng khả dụng, phòng đã bán, giá trung bình. Phân tích seasonality.', 'fact', 'property x date', 3240);

-- ============================================================================
-- _meta_columns (cac cot quan trong nhat)
-- ============================================================================

INSERT INTO _meta_columns (table_name, column_name, description_vi, data_type, unit, is_key, example_value) VALUES
-- clusters
('clusters', 'cluster_id', 'Mã cụm dự án', 'VARCHAR(10)', NULL, TRUE, 'CL-HL'),
('clusters', 'cluster_name', 'Tên cụm dự án', 'VARCHAR(50)', NULL, FALSE, 'Hạ Long'),
('clusters', 'region', 'Vùng miền', 'VARCHAR(50)', NULL, FALSE, 'Miền Bắc'),
-- projects
('projects', 'project_id', 'Mã dự án', 'VARCHAR(10)', NULL, TRUE, 'PJ-HL01'),
('projects', 'project_name', 'Tên dự án đầy đủ', 'VARCHAR(200)', NULL, FALSE, 'InterContinental Halong Bay Resort & Residences'),
('projects', 'cluster_id', 'Khóa ngoại tới clusters', 'VARCHAR(10)', NULL, TRUE, 'CL-HL'),
('projects', 'total_budget', 'Tổng ngân sách dự án', 'BIGINT', 'VND', FALSE, '3200000000000'),
('projects', 'total_gfa', 'Tổng diện tích sàn xây dựng', 'INT', 'm2', FALSE, '45000'),
('projects', 'actual_progress_pct', 'Tiến độ thực tế hiện tại', 'DECIMAL(5,2)', '%', FALSE, '58.00'),
('projects', 'planned_progress_pct', 'Tiến độ theo kế hoạch', 'DECIMAL(5,2)', '%', FALSE, '68.00'),
('projects', 'status', 'Trạng thái dự án', 'VARCHAR(30)', NULL, FALSE, 'Đang xây dựng'),
-- properties
('properties', 'property_id', 'Mã BĐS vận hành', 'VARCHAR(10)', NULL, TRUE, 'PR-PQ01'),
('properties', 'rooms', 'Số phòng/căn hộ', 'INT', 'phòng', FALSE, '120'),
('properties', 'brand_partner', 'Đối tác quản lý thương hiệu', 'VARCHAR(50)', NULL, FALSE, 'IHG/Regent'),
-- budget_disbursements
('budget_disbursements', 'period', 'Kỳ báo cáo tháng', 'VARCHAR(7)', NULL, FALSE, '2024-01'),
('budget_disbursements', 'planned_amount', 'Ngân sách kế hoạch tháng', 'BIGINT', 'VND', FALSE, '180000000000'),
('budget_disbursements', 'actual_amount', 'Giải ngân thực tế tháng', 'BIGINT', 'VND', FALSE, '195000000000'),
('budget_disbursements', 'cumulative_planned', 'Lũy kế kế hoạch', 'BIGINT', 'VND', FALSE, '1500000000000'),
('budget_disbursements', 'cumulative_actual', 'Lũy kế thực tế', 'BIGINT', 'VND', FALSE, '1620000000000'),
-- construction_costs
('construction_costs', 'budgeted_cost', 'Chi phí dự toán tháng', 'BIGINT', 'VND', FALSE, '5000000000'),
('construction_costs', 'actual_cost', 'Chi phí thực tế tháng', 'BIGINT', 'VND', FALSE, '5500000000'),
-- change_orders
('change_orders', 'reason', 'Lý do phát sinh chi tiết', 'VARCHAR(500)', NULL, FALSE, 'Brand compliance - IHG: nâng cấp spec HVAC'),
('change_orders', 'reason_category', 'Phân loại lý do', 'VARCHAR(50)', NULL, FALSE, 'Brand compliance'),
('change_orders', 'amount', 'Giá trị phát sinh', 'BIGINT', 'VND', FALSE, '22000000000'),
-- hospitality_revenue
('hospitality_revenue', 'room_revenue', 'Doanh thu phòng', 'BIGINT', 'VND', FALSE, '12000000000'),
('hospitality_revenue', 'fnb_revenue', 'Doanh thu ẩm thực (Food & Beverage)', 'BIGINT', 'VND', FALSE, '3600000000'),
('hospitality_revenue', 'total_revenue', 'Tổng doanh thu = phòng + F&B + khác', 'BIGINT', 'VND', FALSE, '16800000000'),
('hospitality_revenue', 'avg_daily_rate', 'Giá phòng trung bình mỗi đêm (ADR)', 'BIGINT', 'VND', FALSE, '8500000'),
('hospitality_revenue', 'rooms_sold', 'Tổng phòng đã bán trong tháng', 'INT', 'phòng', FALSE, '2800'),
-- hospitality_costs
('hospitality_costs', 'cost_category', 'Loại chi phí vận hành', 'VARCHAR(50)', NULL, FALSE, 'Nhân sự'),
('hospitality_costs', 'cost_amount', 'Giá trị chi phí', 'BIGINT', 'VND', FALSE, '2500000000'),
-- occupancy_daily
('occupancy_daily', 'rooms_available', 'Phòng khả dụng trong ngày', 'INT', 'phòng', FALSE, '120'),
('occupancy_daily', 'rooms_sold', 'Phòng đã bán trong ngày', 'INT', 'phòng', FALSE, '96'),
('occupancy_daily', 'avg_rate', 'Giá phòng trung bình ngày đó', 'BIGINT', 'VND', FALSE, '8500000'),
-- project_financials
('project_financials', 'construction_cost_per_sqm', 'Chi phí xây dựng trên mỗi m2 sàn', 'BIGINT', 'VND/m2', FALSE, '28500000'),
('project_financials', 'expected_margin_pct', 'Biên lợi nhuận dự kiến', 'DECIMAL(5,2)', '%', FALSE, '22.00'),
('project_financials', 'estimated_irr_pct', 'Tỷ suất hoàn vốn nội bộ ước tính', 'DECIMAL(5,2)', '%', FALSE, '14.50'),
-- financing
('financing', 'loan_outstanding', 'Dư nợ hiện tại', 'BIGINT', 'VND', FALSE, '1800000000000'),
('financing', 'annual_interest_rate_pct', 'Lãi suất năm', 'DECIMAL(5,2)', '%', FALSE, '10.40');

-- ============================================================================
-- _meta_kpi
-- ============================================================================

INSERT INTO _meta_kpi (kpi_name, formula_sql, description_vi, related_tables, category) VALUES
('occupancy_rate', 'rooms_sold / rooms_available * 100', 'Tỷ lệ lấp đầy phòng (%)', 'occupancy_daily, hospitality_revenue', 'Hospitality'),
('adr', 'room_revenue / rooms_sold', 'Giá phòng trung bình mỗi đêm (Average Daily Rate) - VND', 'hospitality_revenue', 'Hospitality'),
('revpar', 'room_revenue / rooms_available', 'Doanh thu trên phòng khả dụng (Revenue Per Available Room) - VND', 'hospitality_revenue', 'Hospitality'),
('gop', 'total_revenue - SUM(cost_amount)', 'Lợi nhuận gộp vận hành (Gross Operating Profit) - VND', 'hospitality_revenue, hospitality_costs', 'Hospitality'),
('gop_margin', '(total_revenue - SUM(cost_amount)) / total_revenue * 100', 'Biên lợi nhuận gộp vận hành (%)', 'hospitality_revenue, hospitality_costs', 'Hospitality'),
('goppar', '(total_revenue - SUM(cost_amount)) / rooms_available', 'GOP trên phòng khả dụng (GOP Per Available Room) - VND', 'hospitality_revenue, hospitality_costs', 'Hospitality'),
('budget_variance', 'actual_amount - planned_amount', 'Chênh lệch ngân sách tháng (VND). Dương = vượt, Âm = tiết kiệm', 'budget_disbursements', 'Ngân sách'),
('budget_variance_pct', '(actual_amount - planned_amount) / planned_amount * 100', 'Tỷ lệ vượt/thấp hơn ngân sách (%)', 'budget_disbursements', 'Ngân sách'),
('disbursement_pct', 'cumulative_actual / total_budget * 100', 'Tỷ lệ giải ngân lũy kế so tổng ngân sách (%)', 'budget_disbursements, projects', 'Ngân sách'),
('cost_per_sqm', 'SUM(actual_cost) / total_gfa', 'Chi phí xây dựng thực tế trên mỗi m2 sàn (VND/m2)', 'construction_costs, projects', 'Ngân sách'),
('change_order_ratio', 'SUM(change_order_amount) / total_budget * 100', 'Tỷ lệ phát sinh thay đổi so tổng ngân sách (%)', 'change_orders, projects', 'Ngân sách'),
('cost_of_delay', 'loan_outstanding * annual_interest_rate_pct / 100 / 12 * months_delayed', 'Chi phí tài chính phát sinh do delay (VND). VD: 1800 tỷ x 10.4%/12 x 3 tháng = 46.8 tỷ', 'financing', 'Tài chính'),
('progress_gap', 'disbursement_pct - actual_progress_pct', 'Chênh lệch giữa tỷ lệ giải ngân và tiến độ thực tế (điểm %). Gap > 10 = cảnh báo đỏ', 'budget_disbursements, projects', 'Tiến độ'),
('staff_cost_ratio', 'staff_cost / total_revenue * 100', 'Tỷ lệ chi phí nhân sự trên doanh thu (%). Benchmark resort VN: 28-32%', 'hospitality_costs, hospitality_revenue', 'Hospitality');

-- ============================================================================
-- _meta_glossary
-- ============================================================================

INSERT INTO _meta_glossary (term, definition_vi, related_kpi, context) VALUES
('ADR', 'Average Daily Rate - Giá phòng trung bình mỗi đêm. Tính bằng tổng doanh thu phòng chia số phòng đã bán.', 'adr', 'Hospitality'),
('RevPAR', 'Revenue Per Available Room - Doanh thu trên phòng khả dụng. Đo hiệu quả kinh doanh phòng tổng thể.', 'revpar', 'Hospitality'),
('GOP', 'Gross Operating Profit - Lợi nhuận gộp vận hành. Doanh thu trừ toàn bộ chi phí vận hành (chưa trừ lãi vay, khấu hao).', 'gop, gop_margin', 'Hospitality'),
('GOPPAR', 'GOP Per Available Room - GOP chia cho tổng số phòng khả dụng. Đo hiệu quả sinh lời trên mỗi phòng.', 'goppar', 'Hospitality'),
('Occupancy Rate', 'Tỷ lệ lấp đầy phòng - phòng đã bán chia phòng khả dụng. Benchmark resort VN 5*: 60-75%.', 'occupancy_rate', 'Hospitality'),
('GFA', 'Gross Floor Area - Tổng diện tích sàn xây dựng (m2). Dùng tính chi phí/m2.', 'cost_per_sqm', 'Xây dựng'),
('M&E', 'Mechanical & Electrical - Hệ thống cơ điện trong tòa nhà: HVAC, thang máy, hệ thống điện.', NULL, 'Xây dựng'),
('MEP', 'Mechanical, Electrical & Plumbing - Hệ thống cấp thoát nước, điện, cơ khí.', NULL, 'Xây dựng'),
('PCCC', 'Phòng cháy chữa cháy - hệ thống báo cháy, sprinkler, bơm chữa cháy.', NULL, 'Xây dựng'),
('Change Order', 'Lệnh thay đổi - yêu cầu thay đổi thiết kế/spec sau khi đã ký hợp đồng. Thường gây tăng chi phí.', 'change_order_ratio', 'Xây dựng'),
('Brand Compliance', 'Tuân thủ tiêu chuẩn thương hiệu quốc tế (IHG, Hyatt). Yêu cầu vật liệu, thiết kế, trang thiết bị theo brand standard.', 'change_order_ratio', 'BĐS nghỉ dưỡng'),
('S-Curve', 'Đường cong chữ S - mô hình giải ngân xây dựng: chậm đầu, tăng tốc giữa, chậm lại cuối dự án.', 'disbursement_pct', 'Quản lý dự án'),
('IRR', 'Internal Rate of Return - Tỷ suất hoàn vốn nội bộ. Lãi suất chiết khấu làm NPV = 0.', 'estimated_irr_pct', 'Tài chính'),
('Condotel', 'Căn hộ khách sạn - BĐS nghỉ dưỡng kết hợp đầu tư và lưu trú. Pháp lý VN đang hoàn thiện.', NULL, 'BĐS nghỉ dưỡng'),
('Management Fee', 'Phí quản lý - phí trả cho đối tác thương hiệu quốc tế để vận hành resort. Thường 2-3% revenue + 8-10% GOP.', 'gop_margin', 'Hospitality'),
('Cluster', 'Cụm dự án - nhóm các dự án BĐS tại cùng vùng địa lý, chia sẻ hạ tầng và thương hiệu.', NULL, 'BĐS'),
('Biên lợi nhuận gộp', 'GOP Margin - tỷ lệ lợi nhuận gộp vận hành trên tổng doanh thu. Benchmark resort 5* VN: 25-35%.', 'gop_margin', 'Hospitality'),
('Tỷ lệ giải ngân', 'Disbursement Rate - tỷ lệ ngân sách đã chi so với tổng ngân sách. Kết hợp với tiến độ để phát hiện vượt chi.', 'disbursement_pct', 'Quản lý dự án'),
('Phát sinh', 'Change Order / Cost Overrun - chi phí ngoài dự toán ban đầu. Nguyên nhân phổ biến: thay đổi thiết kế, biến động giá vật liệu, brand compliance.', 'budget_variance, change_order_ratio', 'Xây dựng'),
('Đòn bẩy tài chính', 'Tỷ lệ nợ trên vốn chủ sở hữu. BIM Land: nợ/vốn CSH = 2.86 lần. Delay dự án → lãi vay phát sinh lớn.', 'cost_of_delay', 'Tài chính');
