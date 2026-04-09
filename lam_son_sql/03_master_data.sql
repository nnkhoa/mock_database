-- Lam Sơn Invest — Master Data
USE construction_re_demo;

-- regions
INSERT INTO regions (region_id, region_name, region_type, notes) VALUES
(1, 'TP Thái Bình', 'thanh_pho', 'Trung tâm tỉnh, thị trường BĐS chính'),
(2, 'Huyện Đông Hưng', 'huyen', 'Nơi có cụm CN Lam Sơn, nhiều dự án'),
(3, 'Huyện Quỳnh Phụ', 'huyen', 'Dự án dân dụng, gần QL10'),
(4, 'Huyện Thái Thụy', 'huyen', 'Ven biển, có KCN'),
(5, 'Huyện Tiền Hải', 'huyen', 'Ven biển, KCN Tiền Hải'),
(6, 'Huyện Vũ Thư', 'huyen', 'Nội đồng, nhiều cầu đường'),
(7, 'Huyện Kiến Xương', 'huyen', 'Nông nghiệp'),
(8, 'Huyện Hưng Hà', 'huyen', 'Nội đồng');

-- cost_categories
INSERT INTO cost_categories (category_id, category_name_vi, category_name_en, typical_pct_min, typical_pct_max) VALUES
(1, 'Nguyên vật liệu', 'Materials', 45.0, 55.0),
(2, 'Nhân công', 'Labor', 20.0, 25.0),
(3, 'Thầu phụ', 'Subcontractors', 15.0, 20.0),
(4, 'Máy móc thiết bị', 'Equipment', 5.0, 10.0),
(5, 'Quản lý & chi phí chung', 'Management & Overhead', 3.0, 5.0);

-- materials
INSERT INTO materials (material_id, material_name, unit, base_price, material_group) VALUES
(1, 'Thép cuộn CB300', 'kg', 14500, 'thep'),
(2, 'Thép hình H200', 'kg', 16800, 'thep'),
(3, 'Xi măng PCB40 Vissai', 'tấn', 1650000, 'xi_mang'),
(4, 'Cát san lấp', 'm³', 180000, 'cat'),
(5, 'Cát xây dựng', 'm³', 350000, 'cat'),
(6, 'Đá 1×2', 'm³', 320000, 'da'),
(7, 'Gạch xây Đồng Nai', 'viên', 1200, 'gach'),
(8, 'Bê tông thương phẩm M250', 'm³', 1250000, 'be_tong');

-- subcontractors
INSERT INTO subcontractors (subcontractor_id, subcontractor_name, specialization, rating, phone, address) VALUES
(1, 'Công ty TNHH XD Hải Minh Hưng', 'Thi công đường, cầu', 4.2, '0227.3851.234', 'Số 15 Lý Thường Kiệt, TP Thái Bình'),
(2, 'Công ty CP Phú Thăng Long', 'Xây dựng dân dụng', 4.0, '0227.3862.456', 'Số 88 Trần Hưng Đạo, TP Thái Bình'),
(3, 'Công ty TNHH Cơ khí Thái Bình', 'Kết cấu thép', 3.8, '0227.3845.789', 'KCN Nguyễn Đức Cảnh, Thái Bình'),
(4, 'HTX Xây dựng Đông La', 'Nhân công & phụ trợ', 3.5, '0227.3871.012', 'Xã Đông La, Huyện Đông Hưng'),
(5, 'Công ty CP Điện nước Thái Bình', 'M&E (cơ điện)', 4.1, '0227.3853.345', 'Số 22 Hai Bà Trưng, TP Thái Bình'),
(6, 'Công ty TNHH Gia cường Nền móng Bắc Bộ', 'Xử lý nền đất yếu', 4.3, '024.3765.6789', 'Số 120 Nguyễn Trãi, Hà Đông, Hà Nội');

-- counterparties
INSERT INTO counterparties (counterparty_id, counterparty_name, counterparty_type, tax_code, address, contact_person, phone) VALUES
(1, 'BQL DA XDCSHT tỉnh Thái Bình', 'chu_dau_tu', '1000123456', 'Số 10 Lê Lợi, TP Thái Bình', 'Ông Trần Văn Hùng', '0227.3831.100'),
(2, 'Sở GD&ĐT Thái Bình', 'chu_dau_tu', '1000234567', 'Số 5 Lý Bôn, TP Thái Bình', 'Bà Nguyễn Thị Lan', '0227.3831.200'),
(3, 'BQL DA huyện Đông Hưng', 'chu_dau_tu', '1000345678', 'TT Đông Hưng, Đông Hưng', 'Ông Phạm Đức Minh', '0227.3871.300'),
(4, 'BQL DA NNPTNT tỉnh Thái Bình', 'chu_dau_tu', '1000456789', 'Số 8 Trần Phú, TP Thái Bình', 'Ông Lê Quốc Tuấn', '0227.3831.400'),
(5, 'BQL KCN tỉnh Thái Bình', 'chu_dau_tu', '1000567890', 'Số 12 Quang Trung, TP Thái Bình', 'Ông Đỗ Văn Thắng', '0227.3831.500'),
(6, 'Công ty TNHH XD Hải Minh Hưng', 'nha_thau_phu', '1001061001', 'Số 15 Lý Thường Kiệt, TP Thái Bình', 'Ông Bùi Văn Hải', '0227.3851.234'),
(7, 'Công ty CP VLXD Đông Á', 'nha_cung_cap', '1001062002', 'KCN Tiền Hải, Tiền Hải', 'Ông Nguyễn Đức Anh', '0227.3892.567'),
(8, 'Công ty CP Thép Việt Đức', 'nha_cung_cap', '0100567890', 'KCN Phố Nối, Hưng Yên', 'Bà Trần Thị Hương', '0221.3864.890'),
(9, 'Ngân hàng TMCP Ngoại thương (Vietcombank) - CN Thái Bình', 'ngan_hang', '0100112233', 'Số 1 Trần Hưng Đạo, TP Thái Bình', 'Ông Hoàng Minh Tuấn', '0227.3831.600'),
(10, 'Ngân hàng TMCP Đầu tư và PT (BIDV) - CN Thái Bình', 'ngan_hang', '0100445566', 'Số 3 Lý Bôn, TP Thái Bình', 'Bà Vũ Thị Ngọc', '0227.3831.700');

-- re_unit_types
INSERT INTO re_unit_types (unit_type_id, unit_type_code, unit_type_name, description) VALUES
(1, 'shophouse', 'Shophouse', 'Nhà phố thương mại, kết hợp kinh doanh tầng 1 và ở tầng trên'),
(2, 'dat_nen', 'Đất nền', 'Lô đất đã có hạ tầng, khách tự xây'),
(3, 'nha_lien_ke', 'Nhà liền kề', 'Nhà liền kề trong khu đô thị, thiết kế đồng bộ'),
(4, 'biet_thu', 'Biệt thự', 'Biệt thự đơn lập hoặc song lập trong khu đô thị'),
(5, 'dat_cong_nghiep', 'Đất công nghiệp', 'Lô đất trong khu/cụm công nghiệp, cho thuê hoặc bán');

-- projects
INSERT INTO projects (project_id, project_name, project_type, project_subtype, region_id, client, contract_value, planned_budget, actual_cost_to_date, planned_start, planned_end, actual_start, actual_end, planned_progress_pct, actual_progress_pct, status, total_units, sold_units, sales_start_date, notes) VALUES
('TC-001', 'Cầu Trà Lý – Đoạn Vũ Thư', 'thi_cong', 'giao_thong', 6, 'BQL DA XDCSHT tỉnh Thái Bình', 45000, 42500, 40480, '2024-01-15', '2025-12-31', '2024-01-20', NULL, 62.0, 60.0, 'dang_thi_cong', NULL, NULL, NULL, 'Dự án cầu bắc qua sông Trà Lý, liên danh'),
('TC-002', 'Trường THPT Quỳnh Côi', 'thi_cong', 'dan_dung', 3, 'Sở GD&ĐT Thái Bình', 28000, 26200, 25900, '2024-03-01', '2025-09-30', '2024-03-10', NULL, 68.0, 66.0, 'dang_thi_cong', NULL, NULL, NULL, 'Xây mới trường THPT Quỳnh Côi, 3 tầng, 24 phòng học'),
('TC-003', 'Đường giao thông Đông Hưng – Thái Thụy', 'thi_cong', 'giao_thong', 2, 'BQL DA huyện Đông Hưng', 68000, 63500, 74358, '2023-06-01', '2025-06-30', '2023-06-15', NULL, 68.0, 45.0, 'dang_thi_cong', NULL, NULL, NULL, 'Đường cấp III đồng bằng, dài 12.5km, mặt đường 9m'),
('TC-004', 'Kè bờ sông Trà Lý đoạn Tiền Hải', 'thi_cong', 'thuy_loi', 5, 'BQL DA NNPTNT tỉnh Thái Bình', 35000, 33000, 32990, '2023-09-01', '2025-03-31', '2023-09-10', NULL, 95.0, 92.0, 'dang_thi_cong', NULL, NULL, NULL, 'Kè bảo vệ bờ sông Trà Lý, dài 2.8km, chống sạt lở'),
('TC-005', 'Hạ tầng KCN Tiền Hải mở rộng', 'thi_cong', 'ha_tang', 5, 'BQL KCN tỉnh Thái Bình', 52000, 48800, 48059, '2024-04-01', '2025-10-31', '2024-04-15', NULL, 65.0, 63.0, 'dang_thi_cong', NULL, NULL, NULL, 'Hạ tầng kỹ thuật KCN Tiền Hải giai đoạn 2, 45ha'),
('BDS-001', 'KĐT Đông Hòa', 'bat_dong_san', 'khu_do_thi', 1, 'Lam Sơn Invest (Chủ đầu tư)', 185000, 148000, 75282, '2023-04-01', '2026-12-31', '2023-04-15', NULL, 55.0, 52.0, 'dang_thi_cong', 120, 42, '2024-06-01', 'Khu đô thị 120 nhà liền kề, hạ tầng đồng bộ'),
('BDS-002', 'Shophouse Lý Bôn', 'bat_dong_san', 'shophouse', 1, 'Lam Sơn Invest (Chủ đầu tư)', 22000, 17600, 17188, '2022-03-01', '2024-06-30', '2022-03-15', NULL, 100.0, 100.0, 'bao_hanh', 35, 27, '2023-01-01', 'Shophouse phong cách tân cổ điển Pháp, 35 căn'),
('BDS-003', 'KĐT Tây QL10', 'bat_dong_san', 'dat_nen', 2, 'Lam Sơn Invest (Chủ đầu tư)', 48000, 36000, 20105, '2024-01-15', '2025-12-31', '2024-02-01', NULL, 58.0, 56.0, 'dang_thi_cong', 80, 58, '2024-09-01', 'Đất nền 80 lô, hạ tầng hoàn thiện, gần QL10'),
('BDS-004', 'KDC Nguyễn Đức Cảnh', 'bat_dong_san', 'khu_dan_cu', 4, 'Lam Sơn Invest (Chủ đầu tư)', 32000, 25600, 17869, '2023-10-01', '2025-09-30', '2023-10-15', NULL, 72.0, 70.0, 'dang_thi_cong', 60, 48, '2024-03-01', 'Khu dân cư 60 lô đất nền, gần KCN'),
('BDS-005', 'Đất CN Xuân Quang', 'bat_dong_san', 'khu_cong_nghiep', 2, 'Lam Sơn Invest (Chủ đầu tư)', 75000, 56000, 35137, '2023-07-01', '2025-12-31', '2023-07-20', NULL, 65.0, 62.0, 'dang_thi_cong', 25, 15, '2024-01-01', 'Đất công nghiệp 25 lô, diện tích 2.000-5.000 m²');