-- ============================================================================
-- GEMADEPT SEAPORT DEMO — Master Data
-- Database: seaport_demo
-- Description: Dimension tables data — ports, shipping lines, equipment, customers, etc.
-- ============================================================================

USE seaport_demo;

-- ============================================================================
-- 1. PORTS
-- ============================================================================
INSERT INTO ports (port_id, port_name, port_name_short, region, port_type, design_capacity_teu, design_capacity_tons, quay_length_m, water_depth_m, num_berths, status) VALUES
('NDV', 'Cảng Nam Đình Vũ',   'Nam Đình Vũ', 'Miền Bắc',   'river_port',    1350000, 3000000, 890,  8.5,  4, 'active'),
('GML', 'Cảng Gemalink',      'Gemalink',     'Miền Nam',    'deep_sea_port', 1500000, 0,       1150, 16.0, 3, 'active'),
('PHL', 'Cảng Phước Long',    'Phước Long',   'Miền Nam',    'icd',           500000,  0,       350,  6.0,  2, 'active'),
('DQT', 'Cảng Dung Quất',     'Dung Quất',    'Miền Trung',  'sea_port',      0,       2000000, 420,  12.0, 2, 'active');

-- ============================================================================
-- 2. SHIPPING LINES
-- ============================================================================
INSERT INTO shipping_lines (shipping_line_id, shipping_line_name, alliance, country, market_share_pct) VALUES
('CMA_CGM',   'CMA CGM',                          'Ocean Alliance',       'Pháp',       25.0),
('MAERSK',    'Maersk',                            'Gemini Cooperation',   'Đan Mạch',   15.0),
('MSC',       'Mediterranean Shipping Company',    NULL,                   'Thụy Sĩ',    12.0),
('EVERGREEN', 'Evergreen Marine',                  'Ocean Alliance',       'Đài Loan',    8.0),
('ONE',       'Ocean Network Express',             'THE Alliance',         'Nhật Bản',    7.0),
('HMM',       'HMM (Hyundai Merchant Marine)',     'THE Alliance',         'Hàn Quốc',    6.0),
('YANGMING',  'Yang Ming Marine Transport',        'Ocean Alliance',       'Đài Loan',    5.0),
('ZIM',       'ZIM Integrated Shipping',           NULL,                   'Israel',      4.0),
('WANHAI',    'Wan Hai Lines',                     NULL,                   'Đài Loan',    4.0),
('SITC',      'SITC International Holdings',       NULL,                   'Hồng Kông',   3.0),
('COSCO',     'COSCO Shipping',                    'Ocean Alliance',       'Trung Quốc',  3.0),
('PIL',       'Pacific International Lines',       NULL,                   'Singapore',   3.0),
('HAPAG',     'Hapag-Lloyd',                       'Gemini Cooperation',   'Đức',         3.0),
('TS_LINES',  'TS Lines',                          NULL,                   'Đài Loan',    1.0),
('OTHER',     'Hãng tàu khác',                     NULL,                   NULL,          1.0);

-- ============================================================================
-- 3. COST TYPES
-- ============================================================================
INSERT INTO cost_types (cost_type_id, cost_type_name_vi, cost_type_name_en, typical_pct_of_total) VALUES
('labor',        'Nhân công',                       'Labor',                        32.0),
('depreciation', 'Khấu hao',                        'Depreciation',                 23.0),
('maintenance',  'Bảo trì thiết bị',                'Equipment Maintenance',        10.0),
('energy',       'Năng lượng (điện, nhiên liệu)',   'Energy (electricity, fuel)',    13.0),
('land_lease',   'Thuê đất, bến',                   'Land & Berth Lease',            7.0),
('other',        'Chi phí khác',                     'Other Operating Costs',        15.0);

-- ============================================================================
-- 4. CARGO TYPES
-- ============================================================================
INSERT INTO cargo_types (cargo_type_id, cargo_type_name_vi, cargo_type_name_en, unit, avg_revenue_per_unit_vnd) VALUES
('container_20ft', 'Container 20ft (TEU)',             '20ft Container',    'TEU',  1400000),
('container_40ft', 'Container 40ft (FEU)',             '40ft Container',    'FEU',  2200000),
('reefer',         'Container lạnh',                   'Reefer Container',  'TEU',  2800000),
('bulk',           'Hàng rời',                         'Bulk Cargo',        'tấn',  45000),
('breakbulk',      'Hàng bách hóa',                   'Breakbulk',         'tấn',  65000),
('oog',            'Hàng quá khổ (Out of Gauge)',      'OOG Cargo',         'TEU',  4500000);

-- ============================================================================
-- 5. EQUIPMENT
-- ============================================================================

-- NDV — 12 units
INSERT INTO equipment (equipment_id, port_id, equipment_name, equipment_type, capacity_tons, year_acquired, status) VALUES
('STS-NDV-01', 'NDV', 'Cẩu bờ STS #1', 'STS', 65.0,  2018, 'active'),
('STS-NDV-02', 'NDV', 'Cẩu bờ STS #2', 'STS', 65.0,  2018, 'active'),
('STS-NDV-03', 'NDV', 'Cẩu bờ STS #3', 'STS', 65.0,  2019, 'active'),
('STS-NDV-04', 'NDV', 'Cẩu bờ STS #4', 'STS', 65.0,  2020, 'active'),
('RTG-NDV-01', 'NDV', 'Cẩu bãi RTG #1', 'RTG', 40.0, 2018, 'active'),
('RTG-NDV-02', 'NDV', 'Cẩu bãi RTG #2', 'RTG', 40.0, 2018, 'active'),
('RTG-NDV-03', 'NDV', 'Cẩu bãi RTG #3', 'RTG', 40.0, 2019, 'active'),
('RTG-NDV-04', 'NDV', 'Cẩu bãi RTG #4', 'RTG', 40.0, 2019, 'active'),
('RTG-NDV-05', 'NDV', 'Cẩu bãi RTG #5', 'RTG', 40.0, 2020, 'active'),
('RTG-NDV-06', 'NDV', 'Cẩu bãi RTG #6', 'RTG', 40.0, 2021, 'active'),
('MHC-NDV-01', 'NDV', 'Cẩu di động MHC #1', 'MHC', 100.0, 2019, 'active'),
('MHC-NDV-02', 'NDV', 'Cẩu di động MHC #2', 'MHC', 100.0, 2019, 'active');

-- GML — 12 units
INSERT INTO equipment (equipment_id, port_id, equipment_name, equipment_type, capacity_tons, year_acquired, status) VALUES
('STS-GML-01', 'GML', 'Cẩu bờ STS #1', 'STS', 85.0, 2021, 'active'),
('STS-GML-02', 'GML', 'Cẩu bờ STS #2', 'STS', 85.0, 2021, 'active'),
('STS-GML-03', 'GML', 'Cẩu bờ STS #3', 'STS', 85.0, 2021, 'active'),
('STS-GML-04', 'GML', 'Cẩu bờ STS #4', 'STS', 85.0, 2022, 'active'),
('STS-GML-05', 'GML', 'Cẩu bờ STS #5', 'STS', 85.0, 2022, 'active'),
('STS-GML-06', 'GML', 'Cẩu bờ STS #6', 'STS', 85.0, 2022, 'active'),
('RTG-GML-01', 'GML', 'Cẩu bãi RTG #1', 'RTG', 50.0, 2021, 'active'),
('RTG-GML-02', 'GML', 'Cẩu bãi RTG #2', 'RTG', 50.0, 2021, 'active'),
('RTG-GML-03', 'GML', 'Cẩu bãi RTG #3', 'RTG', 50.0, 2021, 'active'),
('RTG-GML-04', 'GML', 'Cẩu bãi RTG #4', 'RTG', 50.0, 2022, 'active'),
('RTG-GML-05', 'GML', 'Cẩu bãi RTG #5', 'RTG', 50.0, 2022, 'active'),
('RTG-GML-06', 'GML', 'Cẩu bãi RTG #6', 'RTG', 50.0, 2022, 'active');

-- PHL — 6 units
INSERT INTO equipment (equipment_id, port_id, equipment_name, equipment_type, capacity_tons, year_acquired, status) VALUES
('FCC-PHL-01', 'PHL', 'Cẩu cố định FCC #1',      'FCC',          45.0, 2015, 'active'),
('FCC-PHL-02', 'PHL', 'Cẩu cố định FCC #2',      'FCC',          45.0, 2015, 'active'),
('RS-PHL-01',  'PHL', 'Xe nâng Reachstacker #1',  'Reachstacker', 45.0, 2016, 'active'),
('RS-PHL-02',  'PHL', 'Xe nâng Reachstacker #2',  'Reachstacker', 45.0, 2016, 'active'),
('RS-PHL-03',  'PHL', 'Xe nâng Reachstacker #3',  'Reachstacker', 45.0, 2017, 'active'),
('RS-PHL-04',  'PHL', 'Xe nâng Reachstacker #4',  'Reachstacker', 45.0, 2018, 'active');

-- DQT — 5 units
INSERT INTO equipment (equipment_id, port_id, equipment_name, equipment_type, capacity_tons, year_acquired, status) VALUES
('MHC-DQT-01', 'DQT', 'Cẩu di động MHC #1',      'MHC',      100.0,  2017, 'active'),
('MHC-DQT-02', 'DQT', 'Cẩu di động MHC #2',      'MHC',      100.0,  2017, 'active'),
('GSU-DQT-01', 'DQT', 'Grab ship unloader #1',    'GSU',      1500.0, 2017, 'active'),
('GSU-DQT-02', 'DQT', 'Grab ship unloader #2',    'GSU',      1500.0, 2017, 'active'),
('CVY-DQT-01', 'DQT', 'Hệ thống băng tải',        'Conveyor', 2000.0, 2017, 'active');

-- ============================================================================
-- 6. CUSTOMERS (40 records)
-- ============================================================================
INSERT INTO customers (customer_id, customer_name, industry, primary_port_id, cargo_type_preference) VALUES
-- Seed 10
('SAMSUNG_VN',  'Samsung Electronics Vietnam',      'Điện tử',                'NDV', 'container_40ft'),
('LG_VN',       'LG Electronics Vietnam',           'Điện tử',                'NDV', 'container_40ft'),
('XIMANG_HP',   'Công ty Xi Măng Hải Phòng',        'Vật liệu xây dựng',     'NDV', 'bulk'),
('VINAMILK',    'Công ty CP Sữa Việt Nam',          'Thực phẩm',             'GML', 'reefer'),
('HOAPHAT',     'Tập đoàn Hòa Phát',                'Thép',                   'DQT', 'bulk'),
('NIKE_VN',     'Nike Vietnam',                      'Giày dép',              'GML', 'container_40ft'),
('FOXCONN_VN',  'Foxconn Vietnam',                   'Điện tử',                'NDV', 'container_40ft'),
('NESTLE_VN',   'Nestlé Vietnam',                    'Thực phẩm',             'GML', 'container_20ft'),
('FORMOSA',     'Formosa Ha Tinh Steel',             'Thép',                   'DQT', 'bulk'),
('VN_RUBBER',   'Tập đoàn Cao su Việt Nam',          'Cao su',                 'GML', 'container_20ft'),

-- Dệt may (5)
('VINATEX',     'Vinatex',                           'Dệt may',               'NDV', 'container_20ft'),
('THANH_CONG',  'Dệt May Thành Công',               'Dệt may',               'GML', 'container_20ft'),
('PHONG_PHU',   'Dệt Phong Phú',                    'Dệt may',               'GML', 'container_20ft'),
('SRITHAI',     'Srithai Vietnam',                   'Dệt may',               'GML', 'container_20ft'),
('HANSAE',      'Hansae Vietnam',                    'Dệt may',               'NDV', 'container_20ft'),

-- Gỗ (3)
('TRUONG_THANH','Gỗ Trường Thành',                   'Gỗ',                    'GML', 'container_40ft'),
('WOODSLAND',   'Woodsland',                         'Gỗ',                    'GML', 'container_40ft'),
('SCANSIA',     'Scansia Pacific',                    'Gỗ',                    'GML', 'container_40ft'),

-- Thủy sản (3)
('MINH_PHU',    'Minh Phú Seafood',                  'Thủy sản',              'GML', 'reefer'),
('VINH_HOAN',   'Vĩnh Hoàn',                         'Thủy sản',              'GML', 'reefer'),
('HUNG_VUONG',  'Hùng Vương Corp',                   'Thủy sản',              'GML', 'reefer'),

-- Nông sản (3)
('INTIMEX',     'Intimex Group',                     'Nông sản',              'GML', 'container_20ft'),
('TAN_LONG',    'Tân Long Group',                    'Nông sản',              'PHL', 'container_20ft'),
('TRUNG_NGUYEN','Trung Nguyên Legend',               'Nông sản',              'GML', 'container_20ft'),

-- Nhựa / Hóa chất (3)
('BINH_MINH',   'Nhựa Bình Minh',                    'Nhựa / Hóa chất',       'GML', 'container_20ft'),
('DPM_CHEM',    'Đạm Phú Mỹ',                       'Nhựa / Hóa chất',       'GML', 'container_20ft'),
('VINACHEM',    'Vinachem',                           'Nhựa / Hóa chất',       'NDV', 'container_20ft'),

-- Ô tô / Phụ tùng (3)
('THACO',       'Thaco',                              'Ô tô / Phụ tùng',       'NDV', 'container_40ft'),
('TOYOTA_VN',   'Toyota Vietnam',                     'Ô tô / Phụ tùng',       'NDV', 'container_40ft'),
('DENSO_VN',    'Denso Vietnam',                      'Ô tô / Phụ tùng',       'GML', 'container_40ft'),

-- Logistics 3PL (3)
('GEMADEPT_LOG','Gemadept Logistics',                 'Logistics 3PL',         'PHL', 'container_20ft'),
('TRANSIMEX',   'Transimex',                          'Logistics 3PL',         'PHL', 'container_20ft'),
('SOTRANS_LOG', 'Sotrans',                            'Logistics 3PL',         'PHL', 'container_20ft'),

-- Others (7)
('HABECO',      'Habeco',                             'Đồ uống',              'NDV', 'container_20ft'),
('SABECO',      'Sabeco',                             'Đồ uống',              'GML', 'container_20ft'),
('VINGROUP',    'Vingroup',                           'Đa ngành',             'GML', 'container_40ft'),
('FPT_TRADING', 'FPT Trading',                       'Công nghệ',            'NDV', 'container_20ft'),
('PETROVN',     'PetroVietnam',                       'Dầu khí',              'DQT', 'bulk'),
('VNSTEEL',     'Tổng Công ty Thép VN',              'Thép',                   'DQT', 'bulk'),
('AEON_VN',     'Aeon Vietnam',                       'Bán lẻ',               'GML', 'container_40ft');

-- ============================================================================
-- 7. REGIONS
-- ============================================================================
INSERT INTO regions (region_id, region_name, provinces_included) VALUES
('NORTH',      'Miền Bắc',       'Hà Nội, Hải Phòng, Quảng Ninh, Bắc Ninh, Hải Dương, Thái Nguyên, Vĩnh Phúc, Bắc Giang'),
('CENTRAL',    'Miền Trung',     'Đà Nẵng, Quảng Ngãi, Quảng Nam, Thừa Thiên Huế, Nghệ An, Hà Tĩnh, Bình Định'),
('SOUTH',      'Miền Nam',       'TP.HCM, Bình Dương, Đồng Nai, Long An, Bà Rịa-Vũng Tàu, Cần Thơ, Tây Ninh'),
('ASIA',       'Châu Á (XNK)',   'Trung Quốc, Nhật Bản, Hàn Quốc, Đài Loan, ASEAN'),
('EUROPE',     'Châu Âu (XNK)',  'EU, UK'),
('AMERICAS',   'Châu Mỹ (XNK)', 'Mỹ, Canada'),
('OTHER_INTL', 'Khác (XNK)',     'Châu Phi, Trung Đông, Úc');

-- ============================================================================
-- 8. INVESTMENT PROJECTS
-- ============================================================================
INSERT INTO investment_projects (project_id, project_name, port_id, total_investment_usd, total_investment_vnd, additional_capacity_teu, depreciation_years, annual_depreciation_vnd, estimated_annual_opex_vnd, construction_start, expected_completion, status) VALUES
('GML_2A',  'Gemalink Deep-Water Port – Phase 2A',    'GML', 150000000, 3750000000000, 600000, 20, 187500000000,  630000000000, '2024-10-01', '2026-12-31', 'under_construction'),
('NDV_GD3', 'Nam Đình Vũ – Giai đoạn 3',              'NDV',  80000000, 2000000000000, 650000, 20, 100000000000,  450000000000, '2025-03-01', '2027-06-30', 'under_construction'),
('DQT_MR',  'Dung Quất – Mở rộng bến tổng hợp',       'DQT',  25000000,  625000000000,      0, 15,  41666666667,  120000000000, '2025-06-01', '2026-12-31', 'planning');

-- ============================================================================
-- END OF MASTER DATA
-- ============================================================================
