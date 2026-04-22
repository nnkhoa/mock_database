-- =============================================================================
-- Phú Mỹ Hưng Development — Master Data (Dimension Tables)
-- 7 dimension tables: projects, project_phases, contractors, unit_types,
--   cost_categories, management_zones, commercial_tenants
-- =============================================================================

USE phu_my_hung_demo;

-- =============================================================================
-- 1. PROJECTS (6 dự án)
-- =============================================================================
INSERT INTO projects (project_id, name, name_vi, location, city, type, segment, status, total_units, total_area_sqm, launch_date, expected_completion, actual_completion, total_investment_vnd) VALUES
('PRJ-001', 'Phu My Hung The Aurora', 'Phú Mỹ Hưng The Aurora', 'Đường Nguyễn Lương Bằng, Khu đô thị PMH, Quận 7', 'HCMC', 'residential', 'premium', 'selling', 95, 9500.00, '2024-03-01', '2025-09-30', NULL, 950000000000),
('PRJ-002', 'Phu My Hung L''Arcade', 'Phú Mỹ Hưng L''Arcade', 'Đường Nguyễn Đức Cảnh, Khu đô thị PMH, Quận 7', 'HCMC', 'mixed', 'ultra_luxury', 'construction', 37, 8500.00, '2024-06-01', '2026-06-30', NULL, 1200000000000),
('PRJ-003', 'Cardinal Court', 'Cardinal Court', 'Đường Nguyễn Lương Bằng, Khu đô thị PMH, Quận 7', 'HCMC', 'residential', 'luxury', 'delivered', 200, 22000.00, '2021-06-01', '2023-12-31', '2023-10-15', 1800000000000),
('PRJ-004', 'The Horizon', 'The Horizon', 'Đường Nguyễn Văn Linh, Khu đô thị PMH, Quận 7', 'HCMC', 'residential', 'luxury', 'delivered', 476, 52000.00, '2020-03-01', '2022-12-31', '2022-09-30', 3750000000000),
('PRJ-005', 'Hong Hac City Phase 1', 'Hồng Hạc City Giai đoạn 1', 'Khu đô thị Hồng Hạc, TP Từ Sơn, Bắc Ninh', 'Bac Ninh', 'township', 'mid_high', 'infrastructure', 300, 45000.00, '2024-09-01', '2027-06-30', NULL, 6750000000000),
('PRJ-006', 'Scenic Valley 2 Shops', 'Scenic Valley 2 — Khu thương mại', 'Đường Nguyễn Văn Linh, Khu đô thị PMH, Quận 7', 'HCMC', 'commercial', 'premium', 'selling', 45, 4500.00, '2022-01-01', '2024-06-30', '2023-03-31', 450000000000);

-- =============================================================================
-- 2. PROJECT PHASES (15 giai đoạn)
-- =============================================================================
INSERT INTO project_phases (phase_id, project_id, name, status, planned_start, planned_end, actual_start, actual_end) VALUES
-- The Aurora
('PH-001', 'PRJ-001', 'Foundation & Structure', 'completed', '2023-06-01', '2024-03-31', '2023-06-15', '2024-03-20'),
('PH-002', 'PRJ-001', 'MEP & Finishing', 'in_progress', '2024-01-01', '2025-03-31', '2024-01-10', NULL),
('PH-003', 'PRJ-001', 'Handover Phase', 'planned', '2025-04-01', '2025-09-30', NULL, NULL),
-- L'Arcade
('PH-004', 'PRJ-002', 'Foundation', 'completed', '2024-01-01', '2024-06-30', '2024-01-15', '2024-07-10'),
('PH-005', 'PRJ-002', 'Structure & Facade', 'in_progress', '2024-06-01', '2025-06-30', '2024-06-20', NULL),
('PH-006', 'PRJ-002', 'Interior & MEP', 'planned', '2025-03-01', '2026-03-31', NULL, NULL),
-- Cardinal Court (delivered)
('PH-007', 'PRJ-003', 'Full Construction', 'completed', '2021-06-01', '2023-09-30', '2021-06-15', '2023-09-20'),
('PH-008', 'PRJ-003', 'Handover & Warranty', 'completed', '2023-10-01', '2024-03-31', '2023-10-15', '2024-02-28'),
-- The Horizon (delivered)
('PH-009', 'PRJ-004', 'Foundation', 'completed', '2020-03-01', '2020-12-31', '2020-03-15', '2021-02-15'),
('PH-010', 'PRJ-004', 'Structure & Finishing', 'completed', '2020-10-01', '2022-06-30', '2020-11-01', '2022-08-15'),
('PH-011', 'PRJ-004', 'Handover', 'completed', '2022-06-01', '2022-12-31', '2022-07-01', '2022-09-30'),
-- Hồng Hạc City Phase 1
('PH-012', 'PRJ-005', 'Site Preparation & Infrastructure', 'in_progress', '2024-03-01', '2025-06-30', '2024-04-01', NULL),
('PH-013', 'PRJ-005', 'Phase 1 Construction', 'planned', '2025-06-01', '2026-12-31', NULL, NULL),
('PH-014', 'PRJ-005', 'Phase 2 Foundation', 'planned', '2025-09-01', '2026-06-30', NULL, NULL),
-- Scenic Valley 2
('PH-015', 'PRJ-006', 'Construction & Sales', 'completed', '2022-01-01', '2023-03-31', '2022-01-15', '2023-03-31');

-- =============================================================================
-- 3. CONTRACTORS (12 nhà thầu)
-- =============================================================================
INSERT INTO contractors (contractor_id, name, specialization, rating, active_since, company_size) VALUES
-- 4 large firms
('CTR-001', 'Tập đoàn Xây dựng Hòa Bình', 'structure', 4.2, '2015-01-01', 'large'),
('CTR-002', 'CTCP Xây dựng Coteccons', 'structure', 4.5, '2016-06-01', 'large'),
('CTR-003', 'Công ty CP Newtecons', 'structure', 4.6, '2018-01-01', 'large'),
('CTR-004', 'Công ty CP Ricons', 'finishing', 4.3, '2017-03-01', 'large'),
-- 4 mid-size firms
('CTR-005', 'Công ty TNHH Delta Construction', 'foundation', 3.2, '2019-01-01', 'medium'),
('CTR-006', 'Công ty CP Phú Hưng Gia', 'structure', 3.8, '2020-06-01', 'medium'),
('CTR-007', 'Công ty TNHH An Phát M&E', 'mep', 4.0, '2018-09-01', 'medium'),
('CTR-008', 'Công ty CP Đại Việt Foundation', 'foundation', 3.9, '2017-06-01', 'medium'),
-- 4 specialized firms
('CTR-009', 'Công ty TNHH Thành Công Landscaping', 'landscaping', 4.1, '2019-06-01', 'specialized'),
('CTR-010', 'Công ty CP Saigon Waterproofing', 'finishing', 4.0, '2016-03-01', 'specialized'),
('CTR-011', 'Công ty CP Alpha Elevator', 'mep', 4.4, '2015-09-01', 'specialized'),
('CTR-012', 'Công ty TNHH Pacific Interior', 'finishing', 4.2, '2020-01-01', 'specialized');

-- =============================================================================
-- 4. UNIT TYPES (8 loại sản phẩm)
-- =============================================================================
INSERT INTO unit_types (unit_type_id, name, category, typical_area_min_sqm, typical_area_max_sqm, typical_price_min_per_sqm, typical_price_max_per_sqm) VALUES
('UT-001', 'Apartment 1BR', 'apartment_1br', 55.00, 65.00, 85000000, 120000000),
('UT-002', 'Apartment 2BR', 'apartment_2br', 75.00, 95.00, 90000000, 130000000),
('UT-003', 'Apartment 3BR', 'apartment_3br', 100.00, 140.00, 95000000, 150000000),
('UT-004', 'Penthouse', 'penthouse', 180.00, 300.00, 150000000, 250000000),
('UT-005', 'Villa', 'villa', 250.00, 500.00, 120000000, 200000000),
('UT-006', 'Townhouse', 'townhouse', 150.00, 250.00, 100000000, 160000000),
('UT-007', 'Shop', 'shop', 50.00, 150.00, 200000000, 400000000),
('UT-008', 'Office', 'office', 100.00, 500.00, 80000000, 120000000);

-- =============================================================================
-- 5. COST CATEGORIES (8 hạng mục)
-- =============================================================================
INSERT INTO cost_categories (category_id, name, name_vi, parent_category, is_material) VALUES
('CAT-001', 'foundation', 'Nền móng', NULL, FALSE),
('CAT-002', 'structure', 'Kết cấu', NULL, TRUE),
('CAT-003', 'mep', 'Cơ điện (M&E)', NULL, TRUE),
('CAT-004', 'finishing', 'Hoàn thiện', NULL, TRUE),
('CAT-005', 'facade', 'Mặt dựng', NULL, TRUE),
('CAT-006', 'landscaping', 'Cảnh quan', NULL, FALSE),
('CAT-007', 'infrastructure', 'Hạ tầng', NULL, FALSE),
('CAT-008', 'contingency', 'Dự phòng', NULL, FALSE);

-- =============================================================================
-- 6. MANAGEMENT ZONES (8 khu vực)
-- =============================================================================
INSERT INTO management_zones (zone_id, name, name_vi, area_description, total_units, avg_unit_area_sqm, zone_type, year_established) VALUES
('ZON-001', 'Crescent / CBD', 'Hồ Bán Nguyệt / TTTCQT', 'Khu trung tâm thương mại — Crescent Mall, văn phòng cao cấp, nhà hàng', 1200, 95.00, 'mixed', 2008),
('ZON-002', 'Canh Doi', 'Cảnh Đồi', 'Khu dân cư đầu tiên — biệt thự, nhà phố, hạ tầng đang lão hóa', 2800, 180.00, 'residential', 1997),
('ZON-003', 'Nam Vien', 'Nam Viên', 'Khu biệt thự ven sông — yên tĩnh, nhiều cây xanh', 1500, 220.00, 'residential', 2005),
('ZON-004', 'Midtown', 'Midtown', 'Khu căn hộ mới — The Signature, The Peak, The Grande', 2200, 85.00, 'mixed', 2017),
('ZON-005', 'Riverside', 'Ven Sông', 'Khu căn hộ ven sông Cả Cấm — Riverside Residence, River Park', 1800, 110.00, 'residential', 2003),
('ZON-006', 'Garden / Panorama', 'Kênh Đào', 'Khu căn hộ cạnh kênh đào — Green Valley, Panorama, Garden Plaza', 2500, 100.00, 'residential', 2010),
('ZON-007', 'Star Hill / Chateau', 'Ngôi Sao / Lâu Đài', 'Khu biệt thự cao cấp — Star Hill, Chateau, My Kim', 600, 280.00, 'residential', 2012),
('ZON-008', 'Medical & Education', 'Y tế & Giáo dục', 'Khu tiện ích — bệnh viện FV, trường quốc tế, phòng khám', 400, 300.00, 'commercial', 2015);

-- =============================================================================
-- 7. COMMERCIAL TENANTS (18 khách thuê)
-- =============================================================================
INSERT INTO commercial_tenants (tenant_id, name, zone_id, unit_description, tenant_type, lease_start, lease_end, monthly_rent_vnd, leased_area_sqm) VALUES
-- Crescent Mall & CBD — ZON-001
('TNT-001', 'Starbucks Coffee', 'ZON-001', 'Tầng trệt Crescent Mall, góc chính', 'fnb', '2022-01-01', '2026-12-31', 280000000, 120.00),
('TNT-002', 'Uniqlo Vietnam', 'ZON-001', 'Tầng 1-2 Crescent Mall', 'retail', '2023-06-01', '2028-05-31', 450000000, 350.00),
('TNT-003', 'CGV Cinemas', 'ZON-001', 'Tầng 5 Crescent Mall', 'retail', '2018-01-01', '2028-12-31', 520000000, 800.00),
('TNT-004', 'Vietcombank — PMH Branch', 'ZON-001', 'Tòa nhà văn phòng CBD', 'bank', '2020-03-01', '2027-02-28', 185000000, 200.00),
('TNT-005', 'HSBC — PMH Office', 'ZON-001', 'Tòa nhà văn phòng CBD, tầng 8-10', 'bank', '2019-06-01', '2026-05-31', 320000000, 450.00),
('TNT-006', 'The Coffee House', 'ZON-001', 'Tầng trệt khu CBD', 'fnb', '2023-01-01', '2026-12-31', 150000000, 80.00),
('TNT-007', 'Phúc Long Coffee & Tea', 'ZON-001', 'Tầng trệt Crescent Mall, cạnh lối vào', 'fnb', '2022-06-01', '2025-12-31', 165000000, 65.00),
('TNT-008', 'Nike Store', 'ZON-001', 'Tầng 1 Crescent Mall', 'retail', '2023-03-01', '2027-02-28', 380000000, 200.00),
-- Midtown — ZON-004
('TNT-009', 'Decathlon Vietnam', 'ZON-004', 'Podium Midtown, tầng trệt', 'retail', '2023-09-01', '2028-08-31', 290000000, 400.00),
('TNT-010', 'Pizza 4P''s', 'ZON-004', 'Midtown food court', 'fnb', '2023-06-01', '2027-05-31', 180000000, 150.00),
('TNT-011', 'Anytime Fitness', 'ZON-004', 'Tầng 2 Midtown Podium', 'service', '2023-01-01', '2027-12-31', 220000000, 350.00),
-- Garden / Panorama — ZON-006
('TNT-012', 'Bệnh viện FV — Phòng khám PMH', 'ZON-006', 'Tầng trệt Garden Plaza', 'healthcare', '2021-01-01', '2028-12-31', 250000000, 300.00),
('TNT-013', 'Trường Quốc tế SSIS — Văn phòng', 'ZON-006', 'Tòa nhà Green Valley', 'education', '2020-06-01', '2027-05-31', 195000000, 250.00),
-- Medical & Education zone — ZON-008
('TNT-014', 'Bệnh viện FV — Cơ sở chính', 'ZON-008', 'Khuôn viên riêng, 6 tầng', 'healthcare', '2015-01-01', '2030-12-31', 850000000, 2500.00),
('TNT-015', 'Trường Quốc tế Saigon South (SSIS)', 'ZON-008', 'Khuôn viên riêng', 'education', '2010-01-01', '2030-12-31', 680000000, 3000.00),
('TNT-016', 'Trường Quốc tế Đức (IGS)', 'ZON-008', 'Khuôn viên riêng', 'education', '2012-01-01', '2027-12-31', 420000000, 1800.00),
-- Star Hill — ZON-007
('TNT-017', 'Citibank — PMH Office', 'ZON-007', 'Shophouse Star Hill', 'bank', '2022-01-01', '2027-12-31', 145000000, 120.00),
-- Riverside — ZON-005
('TNT-018', 'Co.opmart — PMH Branch', 'ZON-005', 'Tầng trệt Riverside Residence', 'retail', '2019-01-01', '2027-12-31', 350000000, 500.00);
