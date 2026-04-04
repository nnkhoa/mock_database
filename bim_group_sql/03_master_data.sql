-- ============================================================================
-- BIM Group Real Estate & Construction Demo - Master Data
-- Mo ta: Insert dimension tables (clusters, projects, properties, contractors...)
-- Database: bim_realestate_demo
-- ============================================================================

USE bim_realestate_demo;

-- ============================================================================
-- CLUSTERS (4 records)
-- ============================================================================

INSERT INTO clusters (cluster_id, cluster_name, region, city, country) VALUES
('CL-HL', 'Hạ Long', 'Miền Bắc', 'Hạ Long', 'Việt Nam'),
('CL-PQ', 'Phú Quốc', 'Miền Nam', 'Phú Quốc', 'Việt Nam'),
('CL-HN', 'Hà Nội', 'Miền Bắc', 'Hà Nội', 'Việt Nam'),
('CL-LA', 'Viêng Chăn', 'Đông Nam Á', 'Vientiane', 'Lào');

-- ============================================================================
-- PROJECTS (8 records)
-- ============================================================================

INSERT INTO projects (project_id, project_name, cluster_id, project_type, total_budget, total_gfa, planned_start, planned_end, actual_progress_pct, planned_progress_pct, status, brand_partner) VALUES
('PJ-HL01', 'InterContinental Halong Bay Resort & Residences', 'CL-HL', 'Resort+Residences', 3200000000000, 45000, '2022-06-01', '2025-06-30', 58.00, 68.00, 'Đang xây dựng', 'IHG'),
('PJ-HL02', 'Sailing Club Residences Halong Bay', 'CL-HL', 'Residences', 1500000000000, 22000, '2023-01-01', '2025-09-30', 45.00, 47.00, 'Đang xây dựng', 'Sailing Club'),
('PJ-HL03', 'Lagoon Residences (Grand Bay Phase 3)', 'CL-HL', 'Biệt thự', 850000000000, 9600, '2023-06-01', '2025-03-31', 82.00, 84.00, 'Hoàn thiện', NULL),
('PJ-HL04', 'Tổ hợp TM-DV-Căn hộ HHO-B1.3', 'CL-HL', 'Tổ hợp', 2978000000000, 35000, '2026-01-01', '2029-12-31', 0.00, 0.00, 'Chuẩn bị', NULL),
('PJ-PQ01', 'Park Hyatt Phu Quoc Residences', 'CL-PQ', 'Resort+Residences', 2500000000000, 32000, '2022-09-01', '2025-12-31', 52.00, 54.00, 'Đang xây dựng', 'Hyatt'),
('PJ-PQ02', 'Phu Quoc Marina Water Park', 'CL-PQ', 'Giải trí', 800000000000, 15000, '2024-06-01', '2026-06-30', 15.00, 16.00, 'Đang xây dựng', 'LEOS/GLE'),
('PJ-HN01', 'Khu đô thị Thanh Xuân', 'CL-HN', 'Khu đô thị', 1200000000000, 28000, '2024-01-01', '2026-12-31', 22.00, 23.00, 'Đang xây dựng', NULL),
('PJ-LA01', 'Royal Square Phase 2', 'CL-LA', 'Tổ hợp', 450000000000, 12000, '2023-09-01', '2025-12-31', 35.00, 37.00, 'Đang xây dựng', NULL);

-- ============================================================================
-- PROPERTIES (6 records)
-- ============================================================================

INSERT INTO properties (property_id, property_name, cluster_id, rooms, brand_partner, opening_year, property_type) VALUES
('PR-PQ01', 'Regent Phu Quoc', 'CL-PQ', 120, 'IHG/Regent', 2022, 'Resort 6*'),
('PR-PQ02', 'InterContinental Phu Quoc Long Beach', 'CL-PQ', 459, 'IHG', 2018, 'Resort 5*'),
('PR-PQ03', 'Sailing Club Signature Resort Phu Quoc', 'CL-PQ', 200, 'Sailing Club', 2021, 'Resort 5*'),
('PR-HL01', 'Citadines Marina Halong', 'CL-HL', 260, 'Ascott', 2020, 'Căn hộ DV'),
('PR-HN01', 'Fraser Suites Hanoi', 'CL-HN', 80, 'Frasers', 2010, 'Căn hộ DV'),
('PR-LA01', 'Crowne Plaza Vientiane', 'CL-LA', 198, 'IHG', 2019, 'Khách sạn 5*');

-- ============================================================================
-- WORK_PACKAGES (8 records)
-- ============================================================================

INSERT INTO work_packages (work_package_id, work_package_name, category_vi, budget_weight_pct) VALUES
('WP-01', 'Foundation & Structure', 'Móng & Kết cấu', 25.00),
('WP-02', 'M&E (Mechanical & Electrical)', 'Cơ Điện', 18.00),
('WP-03', 'Interior Finishing', 'Hoàn thiện Nội thất', 15.00),
('WP-04', 'Exterior & Facade', 'Mặt ngoài & Façade', 12.00),
('WP-05', 'Landscape & Hardscape', 'Cảnh quan & Hạ tầng ngoài', 8.00),
('WP-06', 'MEP Systems', 'Hệ thống Cấp thoát nước', 10.00),
('WP-07', 'Fire Protection', 'Phòng cháy chữa cháy', 5.00),
('WP-08', 'Infrastructure & Roads', 'Hạ tầng giao thông', 7.00);

-- ============================================================================
-- CONTRACTORS (18 records)
-- ============================================================================

INSERT INTO contractors (contractor_id, contractor_name, specialty, region) VALUES
('CT-01', 'Xây dựng Hùng Vương', 'Tổng thầu', 'Quảng Ninh'),
('CT-02', 'Cơ Điện Hải Phòng', 'M&E', 'Hải Phòng'),
('CT-03', 'Nội thất Hoàng Gia', 'Hoàn thiện nội thất', 'Hà Nội'),
('CT-04', 'Kết cấu thép Đông Á', 'Kết cấu thép', 'Hải Dương'),
('CT-05', 'Cảnh quan Xanh Việt', 'Cảnh quan', 'Hà Nội'),
('CT-06', 'PCCC Phú Thành', 'Phòng cháy', 'Hà Nội'),
('CT-07', 'Xây dựng Phú Quốc Invest', 'Tổng thầu', 'Kiên Giang'),
('CT-08', 'Cơ Điện Sài Gòn', 'M&E', 'HCM'),
('CT-09', 'Nội thất Miền Nam', 'Hoàn thiện nội thất', 'HCM'),
('CT-10', 'Façade Global VN', 'Mặt ngoài', 'HCM'),
('CT-11', 'Hạ tầng Bắc Việt', 'Hạ tầng giao thông', 'Quảng Ninh'),
('CT-12', 'MEP Solutions', 'Cấp thoát nước', 'Hà Nội'),
('CT-13', 'Xây dựng Thăng Long', 'Tổng thầu', 'Hà Nội'),
('CT-14', 'Nội thất quốc tế FIVE', 'Nội thất cao cấp', 'HCM'),
('CT-15', 'Cơ Điện Lào-Việt', 'M&E', 'Lào'),
('CT-16', 'Xây dựng Mekong', 'Tổng thầu', 'Lào'),
('CT-17', 'Landscape Design VN', 'Cảnh quan', 'Phú Quốc'),
('CT-18', 'Hạ tầng Kiên Giang', 'Hạ tầng', 'Kiên Giang');

-- ============================================================================
-- MATERIALS (6 records)
-- ============================================================================

INSERT INTO materials (material_id, material_name, unit) VALUES
('MAT-01', 'Thép xây dựng', 'VND/kg'),
('MAT-02', 'Xi măng', 'VND/tấn'),
('MAT-03', 'Cát xây dựng', 'VND/m3'),
('MAT-04', 'Gạch ốp lát', 'VND/m2'),
('MAT-05', 'Gỗ nội thất', 'VND/m3'),
('MAT-06', 'Kính cường lực', 'VND/m2');

-- ============================================================================
-- PROJECT_FINANCIALS (8 records)
-- ============================================================================

INSERT INTO project_financials (project_id, total_investment, construction_cost_per_sqm, expected_revenue, expected_margin_pct, estimated_irr_pct, payback_years, cost_variance_pct) VALUES
('PJ-HL01', 4200000000000, 28500000, 5400000000000, 22.00, 13.80, 7.5, 8.20),
('PJ-HL02', 1950000000000, 27800000, 2500000000000, 23.50, 14.20, 7.0, 2.10),
('PJ-HL03', 1100000000000, 29200000, 1450000000000, 24.00, 15.00, 6.5, 1.80),
('PJ-HL04', 3900000000000, 28000000, 5200000000000, 25.00, 14.50, 7.2, 0.00),
('PJ-PQ01', 3300000000000, 35200000, 4500000000000, 28.00, 15.20, 6.8, 4.10),
('PJ-PQ02', 1050000000000, 34500000, 1400000000000, 26.50, 16.00, 5.5, 3.80),
('PJ-HN01', 1800000000000, 42800000, 2600000000000, 32.00, 18.50, 5.0, 2.30),
('PJ-LA01', 580000000000, 25500000, 720000000000, 19.50, 11.20, 8.5, 2.50);

-- ============================================================================
-- PROJECT_COMMITMENTS (5 records - chi du an co cam ket)
-- ============================================================================

INSERT INTO project_commitments (project_id, commitment_type, units_committed, commitment_date, has_penalty, penalty_rate_pct, notes) VALUES
('PJ-HL01', 'Bàn giao căn hộ Residences', 180, '2025-06-30', TRUE, 0.50, 'Hợp đồng mua bán đã ký với khách hàng. Phạt 0.5%/tháng trên giá trị HĐ nếu trễ.'),
('PJ-HL02', 'Bàn giao căn hộ Residences', 120, '2025-09-30', TRUE, 0.30, 'Cam kết bàn giao đợt 1. Phạt 0.3%/tháng.'),
('PJ-HL03', 'Bàn giao biệt thự', 48, '2025-03-31', TRUE, 0.50, 'Toàn bộ 48 biệt thự đã bán. Đang hoàn thiện giai đoạn cuối.'),
('PJ-PQ01', 'Bàn giao Residences + khai trương Resort', 95, '2025-12-31', TRUE, 0.40, 'Cam kết với Hyatt về timeline khai trương. Phạt theo hợp đồng quản lý.'),
('PJ-HN01', 'Bàn giao căn hộ đợt 1', 200, '2026-12-31', FALSE, NULL, 'Chưa mở bán chính thức. Deadline nội bộ, chưa có penalty clause.');

-- ============================================================================
-- FINANCING (8 records)
-- ============================================================================

INSERT INTO financing (project_id, lender, loan_amount, loan_outstanding, annual_interest_rate_pct, start_date, maturity_date) VALUES
('PJ-HL01', 'BIDV - Chi nhánh Quảng Ninh', 2200000000000, 1800000000000, 10.40, '2022-06-15', '2027-06-15'),
('PJ-HL02', 'Vietcombank', 1000000000000, 780000000000, 10.20, '2023-01-15', '2027-01-15'),
('PJ-HL03', 'Techcombank', 550000000000, 320000000000, 9.80, '2023-06-15', '2026-06-15'),
('PJ-HL04', 'BIDV - Chi nhánh Quảng Ninh', 2000000000000, 0, 10.50, '2026-01-01', '2031-12-31'),
('PJ-PQ01', 'VPBank', 1700000000000, 1350000000000, 10.60, '2022-09-15', '2027-09-15'),
('PJ-PQ02', 'MB Bank', 500000000000, 420000000000, 10.80, '2024-06-15', '2028-06-15'),
('PJ-HN01', 'Vietinbank', 800000000000, 650000000000, 9.50, '2024-01-15', '2028-01-15'),
('PJ-LA01', 'BIDV - Chi nhánh Lào', 300000000000, 220000000000, 11.00, '2023-09-15', '2027-09-15');

-- ============================================================================
-- PROJECT_MILESTONES (~7 milestones per project, 56 total)
-- ============================================================================

-- PJ-HL01: InterContinental Halong Bay (58% progress, behind schedule)
INSERT INTO project_milestones (project_id, milestone_name, planned_date, actual_date, status, progress_pct) VALUES
('PJ-HL01', 'Khởi công & Ép cọc', '2022-06-15', '2022-06-20', 'Hoàn thành', 5.00),
('PJ-HL01', 'Hoàn thành móng', '2022-12-31', '2023-01-15', 'Hoàn thành', 15.00),
('PJ-HL01', 'Cất nóc (kết cấu thô)', '2023-09-30', '2023-10-20', 'Hoàn thành', 35.00),
('PJ-HL01', 'Hoàn thành M&E thô', '2024-03-31', '2024-05-15', 'Hoàn thành', 50.00),
('PJ-HL01', 'Hoàn thiện nội thất 50%', '2024-06-30', NULL, 'Đang thực hiện', 58.00),
('PJ-HL01', 'Hoàn thiện nội thất 100% + M&E tinh', '2025-01-31', NULL, 'Chưa bắt đầu', 80.00),
('PJ-HL01', 'Nghiệm thu & Bàn giao', '2025-06-30', NULL, 'Chưa bắt đầu', 100.00);

-- PJ-HL02: Sailing Club Residences (45% progress)
INSERT INTO project_milestones (project_id, milestone_name, planned_date, actual_date, status, progress_pct) VALUES
('PJ-HL02', 'Khởi công & Ép cọc', '2023-01-15', '2023-01-20', 'Hoàn thành', 5.00),
('PJ-HL02', 'Hoàn thành móng', '2023-07-31', '2023-08-10', 'Hoàn thành', 15.00),
('PJ-HL02', 'Kết cấu tầng 1-15', '2024-01-31', '2024-02-15', 'Hoàn thành', 30.00),
('PJ-HL02', 'Kết cấu tầng 16-30 + cất nóc', '2024-06-30', '2024-07-05', 'Hoàn thành', 45.00),
('PJ-HL02', 'M&E + Hoàn thiện thô', '2024-12-31', NULL, 'Đang thực hiện', 65.00),
('PJ-HL02', 'Hoàn thiện nội thất + Cảnh quan', '2025-06-30', NULL, 'Chưa bắt đầu', 85.00),
('PJ-HL02', 'Nghiệm thu & Bàn giao', '2025-09-30', NULL, 'Chưa bắt đầu', 100.00);

-- PJ-HL03: Lagoon Residences (82% progress)
INSERT INTO project_milestones (project_id, milestone_name, planned_date, actual_date, status, progress_pct) VALUES
('PJ-HL03', 'Khởi công & San nền', '2023-06-15', '2023-06-20', 'Hoàn thành', 5.00),
('PJ-HL03', 'Hoàn thành móng 48 biệt thự', '2023-10-31', '2023-11-05', 'Hoàn thành', 20.00),
('PJ-HL03', 'Kết cấu thô 100%', '2024-02-28', '2024-03-05', 'Hoàn thành', 45.00),
('PJ-HL03', 'Hoàn thiện ngoại thất', '2024-06-30', '2024-06-28', 'Hoàn thành', 60.00),
('PJ-HL03', 'Hoàn thiện nội thất 80%', '2024-09-30', NULL, 'Hoàn thành', 75.00),
('PJ-HL03', 'Cảnh quan + Hạ tầng ngoài', '2024-12-31', NULL, 'Đang thực hiện', 82.00),
('PJ-HL03', 'Nghiệm thu & Bàn giao', '2025-03-31', NULL, 'Chưa bắt đầu', 100.00);

-- PJ-HL04: To hop HHO-B1.3 (0% - Chuan bi)
INSERT INTO project_milestones (project_id, milestone_name, planned_date, actual_date, status, progress_pct) VALUES
('PJ-HL04', 'Phê duyệt thiết kế cơ sở', '2025-06-30', NULL, 'Chưa bắt đầu', 0.00),
('PJ-HL04', 'Hoàn thành thiết kế kỹ thuật', '2025-09-30', NULL, 'Chưa bắt đầu', 0.00),
('PJ-HL04', 'Đấu thầu tổng thầu', '2025-10-31', NULL, 'Chưa bắt đầu', 0.00),
('PJ-HL04', 'Khởi công', '2026-01-15', NULL, 'Chưa bắt đầu', 5.00),
('PJ-HL04', 'Hoàn thành móng 3 tòa', '2026-12-31', NULL, 'Chưa bắt đầu', 20.00),
('PJ-HL04', 'Cất nóc tòa 1', '2028-06-30', NULL, 'Chưa bắt đầu', 50.00),
('PJ-HL04', 'Hoàn thành & Bàn giao', '2029-12-31', NULL, 'Chưa bắt đầu', 100.00);

-- PJ-PQ01: Park Hyatt Phu Quoc (52% progress)
INSERT INTO project_milestones (project_id, milestone_name, planned_date, actual_date, status, progress_pct) VALUES
('PJ-PQ01', 'Khởi công & San nền', '2022-09-15', '2022-09-20', 'Hoàn thành', 5.00),
('PJ-PQ01', 'Hoàn thành móng', '2023-03-31', '2023-04-10', 'Hoàn thành', 15.00),
('PJ-PQ01', 'Kết cấu thô Resort', '2023-09-30', '2023-10-15', 'Hoàn thành', 30.00),
('PJ-PQ01', 'Kết cấu thô Residences', '2024-03-31', '2024-04-05', 'Hoàn thành', 45.00),
('PJ-PQ01', 'M&E + Nội thất Resort 50%', '2024-09-30', NULL, 'Đang thực hiện', 52.00),
('PJ-PQ01', 'Hoàn thiện + Cảnh quan', '2025-06-30', NULL, 'Chưa bắt đầu', 80.00),
('PJ-PQ01', 'Khai trương Resort + Bàn giao Residences', '2025-12-31', NULL, 'Chưa bắt đầu', 100.00);

-- PJ-PQ02: Water Park (15% progress)
INSERT INTO project_milestones (project_id, milestone_name, planned_date, actual_date, status, progress_pct) VALUES
('PJ-PQ02', 'Khởi công & San nền', '2024-06-15', '2024-06-18', 'Hoàn thành', 5.00),
('PJ-PQ02', 'Hoàn thành móng + Bể kỹ thuật', '2024-10-31', NULL, 'Đang thực hiện', 15.00),
('PJ-PQ02', 'Kết cấu các công trình chính', '2025-03-31', NULL, 'Chưa bắt đầu', 35.00),
('PJ-PQ02', 'Lắp đặt thiết bị giải trí', '2025-09-30', NULL, 'Chưa bắt đầu', 60.00),
('PJ-PQ02', 'Hoàn thiện + Cảnh quan', '2026-03-31', NULL, 'Chưa bắt đầu', 85.00),
('PJ-PQ02', 'Khai trương', '2026-06-30', NULL, 'Chưa bắt đầu', 100.00);

-- PJ-HN01: Khu do thi Thanh Xuan (22% progress)
INSERT INTO project_milestones (project_id, milestone_name, planned_date, actual_date, status, progress_pct) VALUES
('PJ-HN01', 'Khởi công & Ép cọc', '2024-01-15', '2024-01-18', 'Hoàn thành', 5.00),
('PJ-HN01', 'Hoàn thành móng', '2024-06-30', '2024-07-10', 'Hoàn thành', 15.00),
('PJ-HN01', 'Kết cấu tầng hầm + podium', '2024-10-31', NULL, 'Đang thực hiện', 22.00),
('PJ-HN01', 'Kết cấu thô tòa nhà', '2025-06-30', NULL, 'Chưa bắt đầu', 45.00),
('PJ-HN01', 'M&E + Hoàn thiện', '2026-03-31', NULL, 'Chưa bắt đầu', 75.00),
('PJ-HN01', 'Cảnh quan + Hạ tầng khu đô thị', '2026-09-30', NULL, 'Chưa bắt đầu', 90.00),
('PJ-HN01', 'Nghiệm thu & Bàn giao', '2026-12-31', NULL, 'Chưa bắt đầu', 100.00);

-- PJ-LA01: Royal Square Phase 2 (35% progress)
INSERT INTO project_milestones (project_id, milestone_name, planned_date, actual_date, status, progress_pct) VALUES
('PJ-LA01', 'Khởi công', '2023-09-15', '2023-09-18', 'Hoàn thành', 5.00),
('PJ-LA01', 'Hoàn thành móng', '2024-01-31', '2024-02-10', 'Hoàn thành', 15.00),
('PJ-LA01', 'Kết cấu thô 50%', '2024-06-30', '2024-07-05', 'Hoàn thành', 30.00),
('PJ-LA01', 'Kết cấu thô 100% + Cất nóc', '2024-10-31', NULL, 'Đang thực hiện', 35.00),
('PJ-LA01', 'M&E + Hoàn thiện thô', '2025-04-30', NULL, 'Chưa bắt đầu', 60.00),
('PJ-LA01', 'Hoàn thiện nội thất + Ngoại thất', '2025-09-30', NULL, 'Chưa bắt đầu', 85.00),
('PJ-LA01', 'Nghiệm thu & Bàn giao', '2025-12-31', NULL, 'Chưa bắt đầu', 100.00);
