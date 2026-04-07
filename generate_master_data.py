#!/usr/bin/env python3
"""Generate master data for AP Saigon Petro lubricants_demo database."""

import mysql.connector
import random

random.seed(42)

conn = mysql.connector.connect(host='localhost', port=3306, user='root', password='root', database='lubricants_demo', charset='utf8mb4')
cur = conn.cursor()

# ============================================================
# REGIONS (~70 records)
# ============================================================
regions_data = [
    # Đông Nam Bộ - Miền Nam (30% DT)
    ('RG-01', 'Đông Nam Bộ', 'Miền Nam', 'TP. Hồ Chí Minh', 1.00),
    ('RG-02', 'Đông Nam Bộ', 'Miền Nam', 'Bình Dương', 0.55),
    ('RG-03', 'Đông Nam Bộ', 'Miền Nam', 'Đồng Nai', 0.50),
    ('RG-04', 'Đông Nam Bộ', 'Miền Nam', 'Bà Rịa - Vũng Tàu', 0.30),
    ('RG-05', 'Đông Nam Bộ', 'Miền Nam', 'Bình Phước', 0.18),
    ('RG-06', 'Đông Nam Bộ', 'Miền Nam', 'Tây Ninh', 0.20),
    ('RG-07', 'Đông Nam Bộ', 'Miền Nam', 'Long An', 0.25),
    # Đồng bằng Sông Cửu Long - Miền Nam (15% DT)
    ('RG-08', 'Đồng bằng Sông Cửu Long', 'Miền Nam', 'Cần Thơ', 0.35),
    ('RG-09', 'Đồng bằng Sông Cửu Long', 'Miền Nam', 'An Giang', 0.30),
    ('RG-10', 'Đồng bằng Sông Cửu Long', 'Miền Nam', 'Kiên Giang', 0.28),
    ('RG-11', 'Đồng bằng Sông Cửu Long', 'Miền Nam', 'Đồng Tháp', 0.22),
    ('RG-12', 'Đồng bằng Sông Cửu Long', 'Miền Nam', 'Tiền Giang', 0.25),
    ('RG-13', 'Đồng bằng Sông Cửu Long', 'Miền Nam', 'Bến Tre', 0.18),
    ('RG-14', 'Đồng bằng Sông Cửu Long', 'Miền Nam', 'Vĩnh Long', 0.16),
    ('RG-15', 'Đồng bằng Sông Cửu Long', 'Miền Nam', 'Sóc Trăng', 0.18),
    ('RG-16', 'Đồng bằng Sông Cửu Long', 'Miền Nam', 'Cà Mau', 0.20),
    ('RG-17', 'Đồng bằng Sông Cửu Long', 'Miền Nam', 'Bạc Liêu', 0.14),
    ('RG-18', 'Đồng bằng Sông Cửu Long', 'Miền Nam', 'Hậu Giang', 0.12),
    ('RG-19', 'Đồng bằng Sông Cửu Long', 'Miền Nam', 'Trà Vinh', 0.14),
    # Đồng bằng Sông Hồng - Miền Bắc (20% DT)
    ('RG-20', 'Đồng bằng Sông Hồng', 'Miền Bắc', 'Hà Nội', 0.90),
    ('RG-21', 'Đồng bằng Sông Hồng', 'Miền Bắc', 'Hải Phòng', 0.45),
    ('RG-22', 'Đồng bằng Sông Hồng', 'Miền Bắc', 'Quảng Ninh', 0.30),
    ('RG-23', 'Đồng bằng Sông Hồng', 'Miền Bắc', 'Hải Dương', 0.28),
    ('RG-24', 'Đồng bằng Sông Hồng', 'Miền Bắc', 'Hưng Yên', 0.20),
    ('RG-25', 'Đồng bằng Sông Hồng', 'Miền Bắc', 'Nam Định', 0.25),
    ('RG-26', 'Đồng bằng Sông Hồng', 'Miền Bắc', 'Thái Bình', 0.22),
    ('RG-27', 'Đồng bằng Sông Hồng', 'Miền Bắc', 'Bắc Ninh', 0.30),
    ('RG-28', 'Đồng bằng Sông Hồng', 'Miền Bắc', 'Vĩnh Phúc', 0.22),
    ('RG-29', 'Đồng bằng Sông Hồng', 'Miền Bắc', 'Ninh Bình', 0.18),
    # Trung du & Miền núi phía Bắc - Miền Bắc (8% DT)
    ('RG-30', 'Trung du và Miền núi phía Bắc', 'Miền Bắc', 'Thái Nguyên', 0.22),
    ('RG-31', 'Trung du và Miền núi phía Bắc', 'Miền Bắc', 'Phú Thọ', 0.18),
    ('RG-32', 'Trung du và Miền núi phía Bắc', 'Miền Bắc', 'Lào Cai', 0.12),
    ('RG-33', 'Trung du và Miền núi phía Bắc', 'Miền Bắc', 'Sơn La', 0.14),
    ('RG-34', 'Trung du và Miền núi phía Bắc', 'Miền Bắc', 'Hòa Bình', 0.14),
    ('RG-35', 'Trung du và Miền núi phía Bắc', 'Miền Bắc', 'Yên Bái', 0.12),
    ('RG-36', 'Trung du và Miền núi phía Bắc', 'Miền Bắc', 'Tuyên Quang', 0.10),
    ('RG-37', 'Trung du và Miền núi phía Bắc', 'Miền Bắc', 'Lạng Sơn', 0.12),
    ('RG-38', 'Trung du và Miền núi phía Bắc', 'Miền Bắc', 'Bắc Giang', 0.25),
    ('RG-39', 'Trung du và Miền núi phía Bắc', 'Miền Bắc', 'Bắc Kạn', 0.08),
    ('RG-40', 'Trung du và Miền núi phía Bắc', 'Miền Bắc', 'Cao Bằng', 0.08),
    ('RG-41', 'Trung du và Miền núi phía Bắc', 'Miền Bắc', 'Hà Giang', 0.10),
    ('RG-42', 'Trung du và Miền núi phía Bắc', 'Miền Bắc', 'Lai Châu', 0.06),
    ('RG-43', 'Trung du và Miền núi phía Bắc', 'Miền Bắc', 'Điện Biên', 0.08),
    # Bắc Trung Bộ - Miền Trung (10% DT)
    ('RG-44', 'Bắc Trung Bộ', 'Miền Trung', 'Thanh Hóa', 0.40),
    ('RG-45', 'Bắc Trung Bộ', 'Miền Trung', 'Nghệ An', 0.38),
    ('RG-46', 'Bắc Trung Bộ', 'Miền Trung', 'Hà Tĩnh', 0.18),
    ('RG-47', 'Bắc Trung Bộ', 'Miền Trung', 'Quảng Bình', 0.14),
    ('RG-48', 'Bắc Trung Bộ', 'Miền Trung', 'Quảng Trị', 0.10),
    ('RG-49', 'Bắc Trung Bộ', 'Miền Trung', 'Thừa Thiên Huế', 0.20),
    # Nam Trung Bộ & Duyên hải - Miền Trung (10% DT)
    ('RG-50', 'Nam Trung Bộ', 'Miền Trung', 'Đà Nẵng', 0.35),
    ('RG-51', 'Nam Trung Bộ', 'Miền Trung', 'Quảng Nam', 0.22),
    ('RG-52', 'Nam Trung Bộ', 'Miền Trung', 'Quảng Ngãi', 0.18),
    ('RG-53', 'Nam Trung Bộ', 'Miền Trung', 'Bình Định', 0.22),
    ('RG-54', 'Nam Trung Bộ', 'Miền Trung', 'Phú Yên', 0.14),
    ('RG-55', 'Nam Trung Bộ', 'Miền Trung', 'Khánh Hòa', 0.28),
    ('RG-56', 'Nam Trung Bộ', 'Miền Trung', 'Ninh Thuận', 0.10),
    ('RG-57', 'Nam Trung Bộ', 'Miền Trung', 'Bình Thuận', 0.18),
    # Tây Nguyên - Miền Trung (7% DT)
    ('RG-58', 'Tây Nguyên', 'Miền Trung', 'Đắk Lắk', 0.28),
    ('RG-59', 'Tây Nguyên', 'Miền Trung', 'Gia Lai', 0.22),
    ('RG-60', 'Tây Nguyên', 'Miền Trung', 'Kon Tum', 0.10),
    ('RG-61', 'Tây Nguyên', 'Miền Trung', 'Đắk Nông', 0.10),
    ('RG-62', 'Tây Nguyên', 'Miền Trung', 'Lâm Đồng', 0.22),
]

cur.executemany(
    "INSERT INTO regions (region_id, region_name, macro_region, province, population_index) VALUES (%s,%s,%s,%s,%s)",
    regions_data
)
print(f"Regions: {len(regions_data)} records")

# ============================================================
# CHANNELS (6 records)
# ============================================================
channels_data = [
    ('CH-01', 'B2B Công nghiệp', 'B2B', 31.00),
    ('CH-02', 'Đại lý xe máy', 'B2C', 24.00),
    ('CH-03', 'Gara ô tô', 'B2C', 27.00),
    ('CH-04', 'Hàng hải / Tàu thuyền', 'B2B', 22.00),
    ('CH-05', 'Trạm xăng', 'B2C', 20.00),
    ('CH-06', 'Online / TMĐT', 'B2C', 25.00),
]
cur.executemany(
    "INSERT INTO channels (channel_id, channel_name, channel_type, typical_margin_pct) VALUES (%s,%s,%s,%s)",
    channels_data
)
print(f"Channels: {len(channels_data)} records")

# ============================================================
# SUPPLIERS (15 records)
# ============================================================
suppliers_data = [
    ('SUP-01', 'GS Caltex Korea', 'Hàn Quốc', 'base_oil_group_II', 30),
    ('SUP-02', 'SK Lubricants', 'Hàn Quốc', 'base_oil_group_III', 28),
    ('SUP-03', 'Indian Oil Corporation', 'Ấn Độ', 'base_oil_group_I', 35),
    ('SUP-04', 'ADNOC Abu Dhabi', 'UAE', 'base_oil_group_II', 25),
    ('SUP-05', 'AP Oil International', 'Singapore', 'base_oil_group_IV', 14),
    ('SUP-06', 'Singapore Refining Co', 'Singapore', 'base_oil_group_II', 14),
    ('SUP-07', 'Hindustan Petroleum', 'Ấn Độ', 'base_oil_group_I', 35),
    ('SUP-08', 'Afton Chemical', 'Singapore', 'additive', 14),
    ('SUP-09', 'Lubrizol', 'Singapore', 'additive', 14),
    ('SUP-10', 'Infineum', 'Singapore', 'additive', 14),
    ('SUP-11', 'PVN / BSR Dung Quất', 'Việt Nam', 'base_oil_group_I', 7),
    ('SUP-12', 'Nghi Sơn Refinery', 'Việt Nam', 'base_oil_group_I', 7),
    ('SUP-13', 'Chevron Oronite', 'Singapore', 'additive', 14),
    ('SUP-14', 'Kukdong Oil & Chemicals', 'Hàn Quốc', 'base_oil_group_III', 28),
    ('SUP-15', 'Nynas AB (via Singapore)', 'Singapore', 'naphthenic_base_oil', 21),
]
cur.executemany(
    "INSERT INTO suppliers (supplier_id, supplier_name, country, material_type, lead_time_days) VALUES (%s,%s,%s,%s,%s)",
    suppliers_data
)
print(f"Suppliers: {len(suppliers_data)} records")

# ============================================================
# PRODUCTION LINES (5 records)
# ============================================================
production_lines_data = [
    ('LINE-01', 'Pha chế chính', 'blending', 1200000, 0.980),
    ('LINE-02', 'Chiết rót chai nhỏ (0.8L, 1L, 4L)', 'filling_small', 600000, 0.975),
    ('LINE-03', 'Chiết rót can lớn (18L, 25L)', 'filling_large', 500000, 0.978),
    ('LINE-04', 'Chiết rót phuy (200L)', 'filling_drum', 400000, 0.985),
    ('LINE-05', 'Dây chuyền mỡ bôi trơn', 'grease', 150000, 0.970),
]
cur.executemany(
    "INSERT INTO production_lines (line_id, line_name, line_type, max_capacity_liters_per_month, target_yield_rate) VALUES (%s,%s,%s,%s,%s)",
    production_lines_data
)
print(f"Production Lines: {len(production_lines_data)} records")

# ============================================================
# DISTRIBUTORS (~100 records)
# ============================================================
# region_id references the province-level region records above
distributors_data = [
    # === TIER 1 — Tổng đại lý (15 NPP) ===
    ('NPP-001', 'Công ty TNHH TM DV Hoài Phương', 'RG-02', 'CH-02', 'Tổng đại lý', 'Bình Dương', 5000000000, 30, 'active', '2010-03-15'),
    ('NPP-002', 'Công ty CP Đầu tư An Hương', 'RG-08', 'CH-02', 'Tổng đại lý', 'Cần Thơ', 4000000000, 30, 'active', '2011-06-20'),
    ('NPP-003', 'Công ty TNHH MTV Dầu nhớt Bách Khoa', 'RG-01', 'CH-01', 'Tổng đại lý', 'TP. Hồ Chí Minh', 3000000000, 30, 'active', '2012-01-10'),
    ('NPP-004', 'Công ty TNHH Phát Đạt Oil', 'RG-20', 'CH-02', 'Tổng đại lý', 'Hà Nội', 4500000000, 30, 'active', '2010-08-01'),
    ('NPP-005', 'Công ty TNHH TM Đại Phát', 'RG-50', 'CH-01', 'Tổng đại lý', 'Đà Nẵng', 3500000000, 30, 'active', '2011-02-15'),
    ('NPP-006', 'Công ty TNHH Minh Trí Lube', 'RG-03', 'CH-03', 'Tổng đại lý', 'Đồng Nai', 4000000000, 30, 'active', '2010-11-20'),
    ('NPP-007', 'Công ty CP Dầu nhớt Thiên Long', 'RG-21', 'CH-02', 'Tổng đại lý', 'Hải Phòng', 4000000000, 30, 'active', '2011-04-10'),
    ('NPP-008', 'Công ty TNHH TM Hoài Phương Nam', 'RG-01', 'CH-02', 'Tổng đại lý', 'TP. Hồ Chí Minh', 5000000000, 30, 'active', '2009-07-15'),
    ('NPP-009', 'Công ty CP Phân phối Tân Phát', 'RG-44', 'CH-02', 'Tổng đại lý', 'Thanh Hóa', 3000000000, 30, 'active', '2012-05-01'),
    ('NPP-010', 'Công ty TNHH DV TM Hưng Thịnh', 'RG-58', 'CH-02', 'Tổng đại lý', 'Đắk Lắk', 2500000000, 30, 'active', '2013-02-20'),
    ('NPP-011', 'Công ty CP Năng lượng Đông Á', 'RG-27', 'CH-01', 'Tổng đại lý', 'Bắc Ninh', 3500000000, 30, 'active', '2012-09-15'),
    ('NPP-012', 'Công ty TNHH Vạn Lợi Oil', 'RG-10', 'CH-02', 'Tổng đại lý', 'Kiên Giang', 3000000000, 30, 'active', '2013-06-01'),
    ('NPP-013', 'Công ty CP TM DV Phước Lộc', 'RG-04', 'CH-04', 'Tổng đại lý', 'Bà Rịa - Vũng Tàu', 3500000000, 30, 'active', '2011-11-10'),
    ('NPP-014', 'Công ty TNHH TM Hải Đăng', 'RG-55', 'CH-04', 'Tổng đại lý', 'Khánh Hòa', 3000000000, 30, 'active', '2012-03-25'),
    ('NPP-015', 'Công ty CP An Hương Mekong', 'RG-09', 'CH-02', 'Tổng đại lý', 'An Giang', 4000000000, 30, 'active', '2010-12-01'),

    # === TIER 2 — Đại lý cấp 1 (45 NPP) ===
    # Đông Nam Bộ (12)
    ('NPP-016', 'Công ty TNHH Thành Công Lube', 'RG-01', 'CH-02', 'Đại lý cấp 1', 'TP. Hồ Chí Minh', 2500000000, 30, 'active', '2014-03-10'),
    ('NPP-017', 'Công ty TNHH TM Phú Quý', 'RG-02', 'CH-03', 'Đại lý cấp 1', 'Bình Dương', 2000000000, 30, 'active', '2014-07-20'),
    ('NPP-018', 'Công ty TNHH DV Nhật Tân', 'RG-03', 'CH-01', 'Đại lý cấp 1', 'Đồng Nai', 2500000000, 30, 'active', '2015-01-15'),
    ('NPP-019', 'Công ty CP Dầu nhớt Sài Gòn Xanh', 'RG-01', 'CH-05', 'Đại lý cấp 1', 'TP. Hồ Chí Minh', 1500000000, 30, 'active', '2015-05-10'),
    ('NPP-020', 'Công ty TNHH MTV An Phước', 'RG-05', 'CH-02', 'Đại lý cấp 1', 'Bình Phước', 1500000000, 30, 'active', '2015-08-20'),
    ('NPP-021', 'Công ty TNHH TM Tây Ninh Oil', 'RG-06', 'CH-02', 'Đại lý cấp 1', 'Tây Ninh', 1200000000, 30, 'active', '2016-02-15'),
    ('NPP-022', 'Công ty TNHH TM Đại Phát Trung', 'RG-53', 'CH-01', 'Tổng đại lý', 'Bình Định', 3500000000, 30, 'active', '2011-09-01'),
    ('NPP-023', 'Công ty TNHH Long An Petro', 'RG-07', 'CH-02', 'Đại lý cấp 1', 'Long An', 1800000000, 30, 'active', '2014-11-05'),
    ('NPP-024', 'Công ty CP Vũng Tàu Oil', 'RG-04', 'CH-03', 'Đại lý cấp 1', 'Bà Rịa - Vũng Tàu', 2000000000, 30, 'active', '2015-03-20'),
    ('NPP-025', 'Công ty TNHH TM DV Bình Dương Xanh', 'RG-02', 'CH-01', 'Đại lý cấp 1', 'Bình Dương', 2200000000, 30, 'active', '2014-06-15'),
    ('NPP-026', 'Công ty TNHH Đồng Nai Lube', 'RG-03', 'CH-02', 'Đại lý cấp 1', 'Đồng Nai', 1800000000, 30, 'active', '2015-09-10'),
    ('NPP-027', 'Công ty CP DV TM Sao Việt', 'RG-01', 'CH-06', 'Đại lý cấp 1', 'TP. Hồ Chí Minh', 1500000000, 30, 'active', '2018-01-15'),
    # ĐBSCL (8)
    ('NPP-028', 'Công ty TNHH TM Mekong Oil', 'RG-11', 'CH-02', 'Đại lý cấp 1', 'Đồng Tháp', 1500000000, 30, 'active', '2014-04-10'),
    ('NPP-029', 'Công ty TNHH Tiền Giang Petro', 'RG-12', 'CH-02', 'Đại lý cấp 1', 'Tiền Giang', 1800000000, 30, 'active', '2014-08-20'),
    ('NPP-030', 'Công ty CP TM Bến Tre Oil', 'RG-13', 'CH-02', 'Đại lý cấp 1', 'Bến Tre', 1200000000, 30, 'active', '2015-02-15'),
    ('NPP-031', 'Công ty TNHH Vĩnh Long Lube', 'RG-14', 'CH-02', 'Đại lý cấp 1', 'Vĩnh Long', 1000000000, 30, 'active', '2015-06-01'),
    ('NPP-032', 'Công ty TNHH Sóc Trăng Oil', 'RG-15', 'CH-05', 'Đại lý cấp 1', 'Sóc Trăng', 1200000000, 30, 'active', '2015-10-10'),
    ('NPP-033', 'Công ty CP Cà Mau Petro', 'RG-16', 'CH-04', 'Đại lý cấp 1', 'Cà Mau', 1500000000, 30, 'active', '2014-12-20'),
    ('NPP-034', 'Công ty TNHH TM Bạc Liêu Oil', 'RG-17', 'CH-02', 'Đại lý cấp 1', 'Bạc Liêu', 1000000000, 30, 'active', '2016-03-15'),
    ('NPP-035', 'Công ty TNHH Hậu Giang Lube', 'RG-18', 'CH-02', 'Đại lý cấp 1', 'Hậu Giang', 800000000, 30, 'active', '2016-07-01'),
    # ĐBSH (9)
    ('NPP-036', 'Công ty CP Dầu nhớt Thăng Long', 'RG-20', 'CH-03', 'Đại lý cấp 1', 'Hà Nội', 2500000000, 30, 'active', '2013-04-15'),
    ('NPP-037', 'Công ty TNHH TM Quảng Ninh Oil', 'RG-22', 'CH-01', 'Đại lý cấp 1', 'Quảng Ninh', 2000000000, 30, 'active', '2014-01-10'),
    ('NPP-038', 'Công ty TNHH Hải Dương Lube', 'RG-23', 'CH-02', 'Đại lý cấp 1', 'Hải Dương', 1500000000, 30, 'active', '2014-05-20'),
    ('NPP-039', 'Công ty CP Nam Định Petro', 'RG-25', 'CH-02', 'Đại lý cấp 1', 'Nam Định', 1200000000, 30, 'active', '2015-03-10'),
    ('NPP-040', 'Công ty TNHH TM Thái Bình Oil', 'RG-26', 'CH-05', 'Đại lý cấp 1', 'Thái Bình', 1000000000, 30, 'active', '2015-07-01'),
    ('NPP-041', 'Công ty CP Bắc Ninh Industrial', 'RG-27', 'CH-01', 'Đại lý cấp 1', 'Bắc Ninh', 2500000000, 30, 'active', '2013-09-15'),
    ('NPP-042', 'Công ty TNHH DV Hưng Yên Oil', 'RG-24', 'CH-02', 'Đại lý cấp 1', 'Hưng Yên', 1200000000, 30, 'active', '2015-11-20'),
    ('NPP-043', 'Công ty TNHH Vĩnh Phúc Lube', 'RG-28', 'CH-02', 'Đại lý cấp 1', 'Vĩnh Phúc', 1500000000, 30, 'active', '2014-09-10'),
    ('NPP-044', 'Công ty CP Ninh Bình Oil', 'RG-29', 'CH-02', 'Đại lý cấp 1', 'Ninh Bình', 1000000000, 30, 'active', '2016-01-15'),
    # Bắc Trung Bộ (5)
    ('NPP-045', 'Công ty TNHH TM Nghệ An Oil', 'RG-45', 'CH-02', 'Đại lý cấp 1', 'Nghệ An', 2000000000, 30, 'active', '2013-11-10'),
    ('NPP-046', 'Công ty CP Huế Petro', 'RG-49', 'CH-03', 'Đại lý cấp 1', 'Thừa Thiên Huế', 1500000000, 30, 'active', '2014-06-20'),
    ('NPP-047', 'Công ty TNHH Hà Tĩnh Oil', 'RG-46', 'CH-02', 'Đại lý cấp 1', 'Hà Tĩnh', 1200000000, 30, 'active', '2015-02-01'),
    ('NPP-048', 'Công ty TNHH Quảng Bình Lube', 'RG-47', 'CH-02', 'Đại lý cấp 1', 'Quảng Bình', 1000000000, 30, 'active', '2015-08-15'),
    ('NPP-049', 'Công ty CP Quảng Trị Oil', 'RG-48', 'CH-05', 'Đại lý cấp 1', 'Quảng Trị', 800000000, 30, 'active', '2016-04-10'),
    # Nam Trung Bộ (5)
    ('NPP-050', 'Công ty TNHH TM Quảng Nam Oil', 'RG-51', 'CH-02', 'Đại lý cấp 1', 'Quảng Nam', 1500000000, 30, 'active', '2014-07-15'),
    ('NPP-051', 'Công ty CP Bình Định Petro', 'RG-53', 'CH-02', 'Đại lý cấp 1', 'Bình Định', 1200000000, 30, 'active', '2014-11-20'),
    ('NPP-052', 'Công ty TNHH Khánh Hòa Marine', 'RG-55', 'CH-04', 'Đại lý cấp 1', 'Khánh Hòa', 2000000000, 30, 'active', '2013-10-01'),
    ('NPP-053', 'Công ty TNHH TM Bình Thuận Oil', 'RG-57', 'CH-02', 'Đại lý cấp 1', 'Bình Thuận', 1200000000, 30, 'active', '2015-04-10'),
    ('NPP-054', 'Công ty CP Quảng Ngãi Lube', 'RG-52', 'CH-01', 'Đại lý cấp 1', 'Quảng Ngãi', 1000000000, 30, 'active', '2015-09-20'),
    # Tây Nguyên (3)
    ('NPP-055', 'Công ty TNHH Gia Lai Oil', 'RG-59', 'CH-02', 'Đại lý cấp 1', 'Gia Lai', 1500000000, 30, 'active', '2014-05-15'),
    ('NPP-056', 'Công ty CP Lâm Đồng Petro', 'RG-62', 'CH-03', 'Đại lý cấp 1', 'Lâm Đồng', 1200000000, 30, 'active', '2015-01-10'),
    ('NPP-057', 'Công ty TNHH Đắk Nông Oil', 'RG-61', 'CH-02', 'Đại lý cấp 1', 'Đắk Nông', 800000000, 30, 'active', '2016-06-20'),
    # Trung du phía Bắc (3)
    ('NPP-058', 'Công ty CP Thái Nguyên Oil', 'RG-30', 'CH-02', 'Đại lý cấp 1', 'Thái Nguyên', 1500000000, 30, 'active', '2014-08-10'),
    ('NPP-059', 'Công ty TNHH Phú Thọ Lube', 'RG-31', 'CH-02', 'Đại lý cấp 1', 'Phú Thọ', 1200000000, 30, 'active', '2015-03-25'),
    ('NPP-060', 'Công ty TNHH Bắc Giang Oil', 'RG-38', 'CH-01', 'Đại lý cấp 1', 'Bắc Giang', 1500000000, 30, 'active', '2014-12-01'),

    # === TIER 3 — Đại lý cấp 2 (40 NPP) ===
    # Đông Nam Bộ (6)
    ('NPP-061', 'DNTN Dầu nhớt Tân Bình', 'RG-01', 'CH-02', 'Đại lý cấp 2', 'TP. Hồ Chí Minh', 800000000, 45, 'active', '2017-03-10'),
    ('NPP-062', 'DNTN Phương Nam Oil', 'RG-02', 'CH-05', 'Đại lý cấp 2', 'Bình Dương', 600000000, 45, 'active', '2017-07-20'),
    ('NPP-063', 'Cửa hàng Dầu nhớt Hùng Cường', 'RG-03', 'CH-02', 'Đại lý cấp 2', 'Đồng Nai', 500000000, 45, 'active', '2018-01-15'),
    ('NPP-064', 'DNTN TM Tây Ninh Xanh', 'RG-06', 'CH-02', 'Đại lý cấp 2', 'Tây Ninh', 500000000, 45, 'active', '2018-05-10'),
    ('NPP-065', 'Cửa hàng Dầu nhớt Bình Phước', 'RG-05', 'CH-02', 'Đại lý cấp 2', 'Bình Phước', 500000000, 45, 'active', '2018-09-01'),
    ('NPP-066', 'DNTN Vũng Tàu Marine', 'RG-04', 'CH-04', 'Đại lý cấp 2', 'Bà Rịa - Vũng Tàu', 700000000, 45, 'active', '2017-11-15'),
    # ĐBSCL (10)
    ('NPP-067', 'DNTN Trà Vinh Oil', 'RG-19', 'CH-02', 'Đại lý cấp 2', 'Trà Vinh', 500000000, 45, 'active', '2017-04-10'),
    ('NPP-068', 'Cửa hàng Dầu nhớt An Giang', 'RG-09', 'CH-02', 'Đại lý cấp 2', 'An Giang', 600000000, 45, 'active', '2017-08-20'),
    ('NPP-069', 'DNTN Kiên Giang Lube', 'RG-10', 'CH-02', 'Đại lý cấp 2', 'Kiên Giang', 600000000, 45, 'active', '2018-02-15'),
    ('NPP-070', 'DNTN Đồng Tháp Oil', 'RG-11', 'CH-05', 'Đại lý cấp 2', 'Đồng Tháp', 500000000, 45, 'active', '2018-06-01'),
    ('NPP-071', 'Cửa hàng Tiền Giang Xanh', 'RG-12', 'CH-02', 'Đại lý cấp 2', 'Tiền Giang', 500000000, 45, 'active', '2018-10-10'),
    ('NPP-072', 'DNTN Cà Mau Oil', 'RG-16', 'CH-02', 'Đại lý cấp 2', 'Cà Mau', 500000000, 45, 'active', '2017-12-20'),
    ('NPP-073', 'DNTN Sóc Trăng Lube', 'RG-15', 'CH-02', 'Đại lý cấp 2', 'Sóc Trăng', 500000000, 45, 'active', '2018-04-15'),
    ('NPP-074', 'Cửa hàng Bạc Liêu Oil', 'RG-17', 'CH-02', 'Đại lý cấp 2', 'Bạc Liêu', 500000000, 45, 'active', '2018-08-01'),
    ('NPP-075', 'DNTN Cần Thơ Petro', 'RG-08', 'CH-05', 'Đại lý cấp 2', 'Cần Thơ', 700000000, 45, 'active', '2017-06-15'),
    ('NPP-076', 'Cửa hàng Hậu Giang Oil', 'RG-18', 'CH-02', 'Đại lý cấp 2', 'Hậu Giang', 500000000, 45, 'active', '2019-01-10'),
    # ĐBSH (8)
    ('NPP-077', 'DNTN Hà Nội Oil Center', 'RG-20', 'CH-02', 'Đại lý cấp 2', 'Hà Nội', 800000000, 45, 'active', '2017-05-01'),
    ('NPP-078', 'Cửa hàng Hải Phòng Lube', 'RG-21', 'CH-02', 'Đại lý cấp 2', 'Hải Phòng', 700000000, 45, 'active', '2017-09-15'),
    ('NPP-079', 'DNTN Hải Dương Oil', 'RG-23', 'CH-05', 'Đại lý cấp 2', 'Hải Dương', 500000000, 45, 'active', '2018-03-10'),
    ('NPP-080', 'Cửa hàng Nam Định Lube', 'RG-25', 'CH-02', 'Đại lý cấp 2', 'Nam Định', 500000000, 45, 'active', '2018-07-20'),
    ('NPP-081', 'DNTN Thái Bình Oil', 'RG-26', 'CH-02', 'Đại lý cấp 2', 'Thái Bình', 500000000, 45, 'active', '2018-11-15'),
    ('NPP-082', 'Cửa hàng Quảng Ninh Lube', 'RG-22', 'CH-02', 'Đại lý cấp 2', 'Quảng Ninh', 600000000, 45, 'active', '2017-10-01'),
    ('NPP-083', 'DNTN Hưng Yên Oil', 'RG-24', 'CH-02', 'Đại lý cấp 2', 'Hưng Yên', 500000000, 45, 'active', '2019-02-10'),
    ('NPP-084', 'Cửa hàng Bắc Ninh Lube', 'RG-27', 'CH-02', 'Đại lý cấp 2', 'Bắc Ninh', 600000000, 45, 'active', '2018-05-20'),
    # Trung du phía Bắc (4)
    ('NPP-085', 'DNTN Lào Cai Oil', 'RG-32', 'CH-02', 'Đại lý cấp 2', 'Lào Cai', 500000000, 45, 'active', '2017-11-01'),
    ('NPP-086', 'Cửa hàng Sơn La Lube', 'RG-33', 'CH-02', 'Đại lý cấp 2', 'Sơn La', 500000000, 45, 'active', '2018-04-15'),
    ('NPP-087', 'DNTN Hòa Bình Oil', 'RG-34', 'CH-02', 'Đại lý cấp 2', 'Hòa Bình', 500000000, 45, 'active', '2018-09-10'),
    ('NPP-088', 'Cửa hàng Yên Bái Lube', 'RG-35', 'CH-02', 'Đại lý cấp 2', 'Yên Bái', 500000000, 45, 'active', '2019-01-20'),
    # Bắc Trung Bộ (5)
    ('NPP-089', 'DNTN Thanh Hóa Oil', 'RG-44', 'CH-02', 'Đại lý cấp 2', 'Thanh Hóa', 700000000, 45, 'active', '2017-06-10'),
    ('NPP-090', 'Cửa hàng Nghệ An Lube', 'RG-45', 'CH-05', 'Đại lý cấp 2', 'Nghệ An', 600000000, 45, 'active', '2017-10-20'),
    ('NPP-091', 'DNTN Hà Tĩnh Oil', 'RG-46', 'CH-02', 'Đại lý cấp 2', 'Hà Tĩnh', 500000000, 45, 'active', '2018-03-01'),
    ('NPP-092', 'Cửa hàng Quảng Bình Lube', 'RG-47', 'CH-02', 'Đại lý cấp 2', 'Quảng Bình', 500000000, 45, 'active', '2018-08-15'),
    ('NPP-093', 'DNTN Huế Oil Center', 'RG-49', 'CH-02', 'Đại lý cấp 2', 'Thừa Thiên Huế', 600000000, 45, 'active', '2017-12-10'),
    # Nam Trung Bộ (3)
    ('NPP-094', 'DNTN Đà Nẵng Oil', 'RG-50', 'CH-02', 'Đại lý cấp 2', 'Đà Nẵng', 700000000, 45, 'active', '2017-07-15'),
    ('NPP-095', 'Cửa hàng Phú Yên Lube', 'RG-54', 'CH-02', 'Đại lý cấp 2', 'Phú Yên', 500000000, 45, 'active', '2018-01-20'),
    ('NPP-096', 'DNTN Ninh Thuận Oil', 'RG-56', 'CH-02', 'Đại lý cấp 2', 'Ninh Thuận', 500000000, 45, 'active', '2018-06-10'),
    # Tây Nguyên (4)
    ('NPP-097', 'DNTN Đắk Lắk Lube', 'RG-58', 'CH-02', 'Đại lý cấp 2', 'Đắk Lắk', 600000000, 45, 'active', '2017-08-01'),
    ('NPP-098', 'Cửa hàng Gia Lai Oil', 'RG-59', 'CH-02', 'Đại lý cấp 2', 'Gia Lai', 500000000, 45, 'active', '2018-02-15'),
    ('NPP-099', 'DNTN Kon Tum Oil', 'RG-60', 'CH-02', 'Đại lý cấp 2', 'Kon Tum', 500000000, 45, 'active', '2018-07-20'),
    ('NPP-100', 'Cửa hàng Lâm Đồng Lube', 'RG-62', 'CH-02', 'Đại lý cấp 2', 'Lâm Đồng', 500000000, 45, 'active', '2018-11-10'),
]

cur.executemany(
    "INSERT INTO distributors (distributor_id, distributor_name, region_id, channel_id, tier, city, credit_limit_vnd, payment_term_days, status, onboarded_date) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
    distributors_data
)
print(f"Distributors: {len(distributors_data)} records")

# ============================================================
# PRODUCTS (~200 SKU)
# ============================================================
products = []
prd_id = 0

def add_product(name, brand, group, category, ptype, viscosity, volume_ml, unit_price, cost_per_liter, pop_weight, api_grade=None):
    global prd_id
    prd_id += 1
    products.append((
        f'PRD-{prd_id:03d}', name, brand, group, category, ptype,
        viscosity, volume_ml, unit_price, cost_per_liter, pop_weight, api_grade, 'active'
    ))

# === Saigon Petro — Dầu xe máy (40 SKU, 35% DT) ===
# Dầu 4T
add_product('SP Super 4T 20W-50 0.8L', 'Saigon Petro', 'Dầu xe máy', 'Dầu 4T', 'mineral', '20W-50', 800, 28000, 19000, 5.000, 'SL')
add_product('SP Super 4T 20W-50 1L', 'Saigon Petro', 'Dầu xe máy', 'Dầu 4T', 'mineral', '20W-50', 1000, 27000, 18500, 4.800, 'SL')
add_product('SP Super 4T 20W-40 0.8L', 'Saigon Petro', 'Dầu xe máy', 'Dầu 4T', 'mineral', '20W-40', 800, 26000, 18000, 3.500, 'SJ')
add_product('SP Super 4T 20W-40 1L', 'Saigon Petro', 'Dầu xe máy', 'Dầu 4T', 'mineral', '20W-40', 1000, 25000, 17500, 3.200, 'SJ')
add_product('SP Super 4T 15W-40 0.8L', 'Saigon Petro', 'Dầu xe máy', 'Dầu 4T', 'mineral', '15W-40', 800, 27000, 18500, 3.000, 'SL')
add_product('SP Super 4T 15W-40 1L', 'Saigon Petro', 'Dầu xe máy', 'Dầu 4T', 'mineral', '15W-40', 1000, 26000, 18000, 2.800, 'SL')
add_product('SP Super 4T Premium 10W-40 0.8L', 'Saigon Petro', 'Dầu xe máy', 'Dầu 4T', 'semi_synthetic', '10W-40', 800, 52000, 32000, 4.200, 'SN')
add_product('SP Super 4T Premium 10W-40 1L', 'Saigon Petro', 'Dầu xe máy', 'Dầu 4T', 'semi_synthetic', '10W-40', 1000, 50000, 31000, 4.000, 'SN')
add_product('SP Super 4T Premium 10W-30 0.8L', 'Saigon Petro', 'Dầu xe máy', 'Dầu 4T', 'semi_synthetic', '10W-30', 800, 55000, 34000, 2.500, 'SN')
add_product('SP Super 4T Premium 10W-30 1L', 'Saigon Petro', 'Dầu xe máy', 'Dầu 4T', 'semi_synthetic', '10W-30', 1000, 53000, 33000, 2.300, 'SN')
add_product('SP Economy 4T 20W-50 0.8L', 'Saigon Petro', 'Dầu xe máy', 'Dầu 4T', 'mineral', '20W-50', 800, 22000, 15500, 3.800, 'SF')
add_product('SP Economy 4T 20W-50 1L', 'Saigon Petro', 'Dầu xe máy', 'Dầu 4T', 'mineral', '20W-50', 1000, 21000, 15000, 3.500, 'SF')
# Dầu 2T
add_product('SP 2T Super 0.8L', 'Saigon Petro', 'Dầu xe máy', 'Dầu 2T', 'mineral', None, 800, 25000, 17000, 2.000, 'TC')
add_product('SP 2T Super 1L', 'Saigon Petro', 'Dầu xe máy', 'Dầu 2T', 'mineral', None, 1000, 24000, 16500, 1.800, 'TC')
add_product('SP 2T Premium 0.8L', 'Saigon Petro', 'Dầu xe máy', 'Dầu 2T', 'semi_synthetic', None, 800, 45000, 28000, 1.200, 'TC+')
add_product('SP 2T Premium 1L', 'Saigon Petro', 'Dầu xe máy', 'Dầu 2T', 'semi_synthetic', None, 1000, 43000, 27000, 1.000, 'TC+')
# Dầu tay ga
add_product('SP Tay Ga Scooter 10W-40 0.8L', 'Saigon Petro', 'Dầu xe máy', 'Dầu tay ga', 'semi_synthetic', '10W-40', 800, 55000, 34000, 3.800, 'SN')
add_product('SP Tay Ga Scooter 10W-40 1L', 'Saigon Petro', 'Dầu xe máy', 'Dầu tay ga', 'semi_synthetic', '10W-40', 1000, 53000, 33000, 3.500, 'SN')
add_product('SP Tay Ga Scooter 10W-30 0.8L', 'Saigon Petro', 'Dầu xe máy', 'Dầu tay ga', 'semi_synthetic', '10W-30', 800, 58000, 36000, 2.200, 'SN')
add_product('SP Tay Ga Plus 5W-30 0.8L', 'Saigon Petro', 'Dầu xe máy', 'Dầu tay ga', 'semi_synthetic', '5W-30', 800, 60000, 38000, 1.800, 'SN')
# Extra motorcycle SKUs to reach ~40
add_product('SP Super 4T 20W-50 4L', 'Saigon Petro', 'Dầu xe máy', 'Dầu 4T', 'mineral', '20W-50', 4000, 25000, 17500, 2.200, 'SL')
add_product('SP Super 4T Premium 10W-40 4L', 'Saigon Petro', 'Dầu xe máy', 'Dầu 4T', 'semi_synthetic', '10W-40', 4000, 48000, 30000, 1.500, 'SN')
add_product('SP Super 4T Gold 10W-40 0.8L', 'Saigon Petro', 'Dầu xe máy', 'Dầu 4T', 'semi_synthetic', '10W-40', 800, 56000, 35000, 2.000, 'SN Plus')
add_product('SP Super 4T Gold 10W-40 1L', 'Saigon Petro', 'Dầu xe máy', 'Dầu 4T', 'semi_synthetic', '10W-40', 1000, 54000, 34000, 1.800, 'SN Plus')
add_product('SP Tay Ga City 10W-30 0.8L', 'Saigon Petro', 'Dầu xe máy', 'Dầu tay ga', 'mineral', '10W-30', 800, 32000, 21000, 1.500, 'SJ')
add_product('SP Super 4T 15W-50 0.8L', 'Saigon Petro', 'Dầu xe máy', 'Dầu 4T', 'mineral', '15W-50', 800, 28000, 19000, 1.200, 'SL')
add_product('SP Super 4T 15W-50 1L', 'Saigon Petro', 'Dầu xe máy', 'Dầu 4T', 'mineral', '15W-50', 1000, 27000, 18500, 1.000, 'SL')
add_product('SP 2T Economy 0.5L', 'Saigon Petro', 'Dầu xe máy', 'Dầu 2T', 'mineral', None, 500, 20000, 14000, 0.800, 'TB')
add_product('SP Tay Ga Premium 5W-40 0.8L', 'Saigon Petro', 'Dầu xe máy', 'Dầu tay ga', 'semi_synthetic', '5W-40', 800, 62000, 39000, 1.500, 'SN Plus')
add_product('SP Super 4T Max 20W-50 0.8L', 'Saigon Petro', 'Dầu xe máy', 'Dầu 4T', 'mineral', '20W-50', 800, 30000, 20000, 2.800, 'SL')
add_product('SP Super 4T Max 20W-50 1L', 'Saigon Petro', 'Dầu xe máy', 'Dầu 4T', 'mineral', '20W-50', 1000, 29000, 19500, 2.500, 'SL')
add_product('SP 2T Racing 0.8L', 'Saigon Petro', 'Dầu xe máy', 'Dầu 2T', 'semi_synthetic', None, 800, 48000, 30000, 0.700, 'TD')
add_product('SP Tay Ga ECO 10W-40 0.8L', 'Saigon Petro', 'Dầu xe máy', 'Dầu tay ga', 'mineral', '10W-40', 800, 30000, 20000, 1.200, 'SJ')
add_product('SP Super 4T 20W-40 4L', 'Saigon Petro', 'Dầu xe máy', 'Dầu 4T', 'mineral', '20W-40', 4000, 23000, 16000, 0.800, 'SJ')
add_product('SP Super 4T Ultra 10W-30 1L', 'Saigon Petro', 'Dầu xe máy', 'Dầu 4T', 'semi_synthetic', '10W-30', 1000, 57000, 36000, 1.000, 'SN Plus')
add_product('SP 2T Marine 1L', 'Saigon Petro', 'Dầu xe máy', 'Dầu 2T', 'mineral', None, 1000, 23000, 16000, 0.500, 'TC')
add_product('SP Tay Ga Sport 10W-40 1L', 'Saigon Petro', 'Dầu xe máy', 'Dầu tay ga', 'semi_synthetic', '10W-40', 1000, 55000, 34500, 1.500, 'SN')
add_product('SP Economy 4T 20W-40 0.8L', 'Saigon Petro', 'Dầu xe máy', 'Dầu 4T', 'mineral', '20W-40', 800, 20000, 14000, 1.200, 'SF')
add_product('SP Super 4T Long Life 10W-40 1L', 'Saigon Petro', 'Dầu xe máy', 'Dầu 4T', 'semi_synthetic', '10W-40', 1000, 52000, 32500, 0.900, 'SN')

# === Saigon Petro — Dầu ô tô (25 SKU, 10% DT) ===
add_product('SP Auto 10W-40 4L', 'Saigon Petro', 'Dầu ô tô', 'Dầu động cơ xăng', 'semi_synthetic', '10W-40', 4000, 55000, 35000, 3.000, 'SN')
add_product('SP Auto 10W-40 1L', 'Saigon Petro', 'Dầu ô tô', 'Dầu động cơ xăng', 'semi_synthetic', '10W-40', 1000, 58000, 36000, 2.000, 'SN')
add_product('SP Auto 20W-50 4L', 'Saigon Petro', 'Dầu ô tô', 'Dầu động cơ xăng', 'mineral', '20W-50', 4000, 30000, 20000, 2.500, 'SL')
add_product('SP Auto 20W-50 1L', 'Saigon Petro', 'Dầu ô tô', 'Dầu động cơ xăng', 'mineral', '20W-50', 1000, 32000, 21000, 1.800, 'SL')
add_product('SP Auto 15W-40 4L', 'Saigon Petro', 'Dầu ô tô', 'Dầu động cơ xăng', 'mineral', '15W-40', 4000, 28000, 19000, 1.500, 'SL')
add_product('SP Auto 15W-40 1L', 'Saigon Petro', 'Dầu ô tô', 'Dầu động cơ xăng', 'mineral', '15W-40', 1000, 30000, 20000, 1.200, 'SL')
add_product('SP Auto Premium 5W-40 4L', 'Saigon Petro', 'Dầu ô tô', 'Dầu động cơ xăng', 'semi_synthetic', '5W-40', 4000, 65000, 38000, 1.500, 'SN Plus')
add_product('SP Auto Premium 5W-30 4L', 'Saigon Petro', 'Dầu ô tô', 'Dầu động cơ xăng', 'semi_synthetic', '5W-30', 4000, 62000, 37000, 1.200, 'SN Plus')
add_product('SP Diesel Light 15W-40 5L', 'Saigon Petro', 'Dầu ô tô', 'Dầu diesel', 'mineral', '15W-40', 5000, 28000, 19000, 2.000, 'CI-4')
add_product('SP Diesel Light 15W-40 1L', 'Saigon Petro', 'Dầu ô tô', 'Dầu diesel', 'mineral', '15W-40', 1000, 30000, 20500, 1.000, 'CI-4')
add_product('SP ATF III 1L', 'Saigon Petro', 'Dầu ô tô', 'Dầu hộp số tự động', 'mineral', None, 1000, 35000, 23000, 0.800, None)
add_product('SP ATF III 4L', 'Saigon Petro', 'Dầu ô tô', 'Dầu hộp số tự động', 'mineral', None, 4000, 33000, 22000, 0.600, None)
add_product('SP Brake Fluid DOT3 0.5L', 'Saigon Petro', 'Dầu ô tô', 'Dầu phanh', 'mineral', None, 500, 40000, 25000, 0.500, None)
add_product('SP Brake Fluid DOT4 0.5L', 'Saigon Petro', 'Dầu ô tô', 'Dầu phanh', 'semi_synthetic', None, 500, 55000, 35000, 0.400, None)
add_product('SP Coolant Green 1L', 'Saigon Petro', 'Dầu ô tô', 'Nước làm mát', 'mineral', None, 1000, 25000, 15000, 0.500, None)
add_product('SP Coolant Green 4L', 'Saigon Petro', 'Dầu ô tô', 'Nước làm mát', 'mineral', None, 4000, 22000, 13000, 0.400, None)
add_product('SP Auto 10W-30 4L', 'Saigon Petro', 'Dầu ô tô', 'Dầu động cơ xăng', 'semi_synthetic', '10W-30', 4000, 58000, 36000, 0.800, 'SN')
add_product('SP Diesel Light 10W-40 5L', 'Saigon Petro', 'Dầu ô tô', 'Dầu diesel', 'semi_synthetic', '10W-40', 5000, 48000, 30000, 0.700, 'CI-4')
add_product('SP Gear Oil 80W-90 1L', 'Saigon Petro', 'Dầu ô tô', 'Dầu hộp số', 'mineral', '80W-90', 1000, 32000, 21000, 0.500, 'GL-5')
add_product('SP Gear Oil 80W-90 4L', 'Saigon Petro', 'Dầu ô tô', 'Dầu hộp số', 'mineral', '80W-90', 4000, 30000, 20000, 0.400, 'GL-5')
add_product('SP Auto ECO 0W-20 4L', 'Saigon Petro', 'Dầu ô tô', 'Dầu động cơ xăng', 'semi_synthetic', '0W-20', 4000, 68000, 42000, 0.600, 'SN Plus')
add_product('SP Power Steering Fluid 1L', 'Saigon Petro', 'Dầu ô tô', 'Dầu trợ lực lái', 'mineral', None, 1000, 35000, 22000, 0.300, None)
add_product('SP Auto 5W-40 1L', 'Saigon Petro', 'Dầu ô tô', 'Dầu động cơ xăng', 'semi_synthetic', '5W-40', 1000, 68000, 40000, 0.500, 'SN Plus')
add_product('SP Diesel Premium 10W-40 5L', 'Saigon Petro', 'Dầu ô tô', 'Dầu diesel', 'semi_synthetic', '10W-40', 5000, 52000, 33000, 0.400, 'CJ-4')
add_product('SP Multi 3R 120ml', 'Saigon Petro', 'Dầu ô tô', 'Dầu đa dụng', 'mineral', None, 120, 35000, 18000, 1.500, None)

# === Saigon Petro — Dầu xe tải (20 SKU, 15% DT) ===
add_product('SP Diesel HD 15W-40 5L', 'Saigon Petro', 'Dầu xe tải', 'Dầu diesel HD', 'mineral', '15W-40', 5000, 27000, 18500, 4.500, 'CI-4')
add_product('SP Diesel HD 15W-40 18L', 'Saigon Petro', 'Dầu xe tải', 'Dầu diesel HD', 'mineral', '15W-40', 18000, 25000, 17500, 4.000, 'CI-4')
add_product('SP Diesel HD 15W-40 25L', 'Saigon Petro', 'Dầu xe tải', 'Dầu diesel HD', 'mineral', '15W-40', 25000, 24000, 17000, 3.500, 'CI-4')
add_product('SP Diesel HD 15W-40 200L', 'Saigon Petro', 'Dầu xe tải', 'Dầu diesel HD', 'mineral', '15W-40', 200000, 23000, 16500, 3.000, 'CI-4')
add_product('SP Diesel HD Plus 10W-40 5L', 'Saigon Petro', 'Dầu xe tải', 'Dầu diesel HD', 'semi_synthetic', '10W-40', 5000, 48000, 30000, 2.500, 'CI-4')
add_product('SP Diesel HD Plus 10W-40 18L', 'Saigon Petro', 'Dầu xe tải', 'Dầu diesel HD', 'semi_synthetic', '10W-40', 18000, 45000, 28000, 2.000, 'CI-4')
add_product('SP Diesel HD Plus 10W-40 25L', 'Saigon Petro', 'Dầu xe tải', 'Dầu diesel HD', 'semi_synthetic', '10W-40', 25000, 43000, 27000, 1.500, 'CI-4')
add_product('SP Diesel HD 20W-50 5L', 'Saigon Petro', 'Dầu xe tải', 'Dầu diesel HD', 'mineral', '20W-50', 5000, 26000, 18000, 3.200, 'CH-4')
add_product('SP Diesel HD 20W-50 18L', 'Saigon Petro', 'Dầu xe tải', 'Dầu diesel HD', 'mineral', '20W-50', 18000, 24000, 17000, 2.800, 'CH-4')
add_product('SP Diesel HD 20W-50 200L', 'Saigon Petro', 'Dầu xe tải', 'Dầu diesel HD', 'mineral', '20W-50', 200000, 22000, 16000, 2.000, 'CH-4')
add_product('SP Gear Oil HD 85W-140 5L', 'Saigon Petro', 'Dầu xe tải', 'Dầu hộp số', 'mineral', '85W-140', 5000, 30000, 20000, 1.500, 'GL-5')
add_product('SP Gear Oil HD 85W-140 18L', 'Saigon Petro', 'Dầu xe tải', 'Dầu hộp số', 'mineral', '85W-140', 18000, 28000, 19000, 1.200, 'GL-5')
add_product('SP Gear Oil HD 80W-90 5L', 'Saigon Petro', 'Dầu xe tải', 'Dầu hộp số', 'mineral', '80W-90', 5000, 29000, 19500, 1.000, 'GL-5')
add_product('SP Gear Oil HD 80W-90 18L', 'Saigon Petro', 'Dầu xe tải', 'Dầu hộp số', 'mineral', '80W-90', 18000, 27000, 18500, 0.800, 'GL-5')
add_product('SP Diesel Turbo 15W-40 5L', 'Saigon Petro', 'Dầu xe tải', 'Dầu diesel HD', 'mineral', '15W-40', 5000, 29000, 19500, 1.800, 'CJ-4')
add_product('SP Diesel Turbo 15W-40 18L', 'Saigon Petro', 'Dầu xe tải', 'Dầu diesel HD', 'mineral', '15W-40', 18000, 27000, 18500, 1.200, 'CJ-4')
add_product('SP Diesel HD Economy 15W-40 200L', 'Saigon Petro', 'Dầu xe tải', 'Dầu diesel HD', 'mineral', '15W-40', 200000, 21000, 15000, 1.500, 'CF-4')
add_product('SP Diesel HD 40 5L', 'Saigon Petro', 'Dầu xe tải', 'Dầu diesel HD', 'mineral', '40', 5000, 24000, 16500, 1.000, 'CF')
add_product('SP Diesel HD 40 18L', 'Saigon Petro', 'Dầu xe tải', 'Dầu diesel HD', 'mineral', '40', 18000, 22000, 15500, 0.800, 'CF')
add_product('SP Diesel HD 40 200L', 'Saigon Petro', 'Dầu xe tải', 'Dầu diesel HD', 'mineral', '40', 200000, 20000, 14500, 0.600, 'CF')

# === AP OIL — Dầu xe máy Premium (20 SKU, 8% DT) ===
add_product('AP Super 4T Premium 10W-40 0.8L', 'AP OIL', 'Dầu xe máy', 'Dầu 4T cao cấp', 'semi_synthetic', '10W-40', 800, 62000, 36000, 3.500, 'SN Plus')
add_product('AP Super 4T Premium 10W-40 1L', 'AP OIL', 'Dầu xe máy', 'Dầu 4T cao cấp', 'semi_synthetic', '10W-40', 1000, 60000, 35000, 3.200, 'SN Plus')
add_product('AP Super 4T Fully Synthetic 5W-40 0.8L', 'AP OIL', 'Dầu xe máy', 'Dầu 4T cao cấp', 'full_synthetic', '5W-40', 800, 95000, 55000, 2.500, 'SN Plus')
add_product('AP Super 4T Fully Synthetic 5W-40 1L', 'AP OIL', 'Dầu xe máy', 'Dầu 4T cao cấp', 'full_synthetic', '5W-40', 1000, 90000, 52000, 2.200, 'SN Plus')
add_product('AP Super 4T Racing 10W-50 0.8L', 'AP OIL', 'Dầu xe máy', 'Dầu 4T cao cấp', 'full_synthetic', '10W-50', 800, 100000, 58000, 1.800, 'SN Plus')
add_product('AP Super 4T Racing 10W-50 1L', 'AP OIL', 'Dầu xe máy', 'Dầu 4T cao cấp', 'full_synthetic', '10W-50', 1000, 95000, 55000, 1.500, 'SN Plus')
add_product('AP Tay Ga Premium 10W-40 0.8L', 'AP OIL', 'Dầu xe máy', 'Dầu tay ga cao cấp', 'semi_synthetic', '10W-40', 800, 65000, 38000, 2.800, 'SN Plus')
add_product('AP Tay Ga Premium 10W-40 1L', 'AP OIL', 'Dầu xe máy', 'Dầu tay ga cao cấp', 'semi_synthetic', '10W-40', 1000, 63000, 37000, 2.500, 'SN Plus')
add_product('AP Tay Ga Fully Synthetic 5W-30 0.8L', 'AP OIL', 'Dầu xe máy', 'Dầu tay ga cao cấp', 'full_synthetic', '5W-30', 800, 105000, 60000, 1.500, 'SN Plus')
add_product('AP Tay Ga Fully Synthetic 5W-30 1L', 'AP OIL', 'Dầu xe máy', 'Dầu tay ga cao cấp', 'full_synthetic', '5W-30', 1000, 100000, 58000, 1.200, 'SN Plus')
add_product('AP Super 4T Premium 10W-30 0.8L', 'AP OIL', 'Dầu xe máy', 'Dầu 4T cao cấp', 'semi_synthetic', '10W-30', 800, 64000, 37000, 1.500, 'SN Plus')
add_product('AP Super 4T Premium 10W-30 1L', 'AP OIL', 'Dầu xe máy', 'Dầu 4T cao cấp', 'semi_synthetic', '10W-30', 1000, 62000, 36000, 1.200, 'SN Plus')
add_product('AP Super 4T Gold 15W-50 0.8L', 'AP OIL', 'Dầu xe máy', 'Dầu 4T cao cấp', 'semi_synthetic', '15W-50', 800, 58000, 34000, 1.000, 'SN')
add_product('AP Super 4T Gold 15W-50 1L', 'AP OIL', 'Dầu xe máy', 'Dầu 4T cao cấp', 'semi_synthetic', '15W-50', 1000, 56000, 33000, 0.800, 'SN')
add_product('AP Super 4T Fully Synthetic 0W-40 1L', 'AP OIL', 'Dầu xe máy', 'Dầu 4T cao cấp', 'full_synthetic', '0W-40', 1000, 110000, 62000, 0.800, 'SP')
add_product('AP Tay Ga City 10W-30 0.8L', 'AP OIL', 'Dầu xe máy', 'Dầu tay ga cao cấp', 'semi_synthetic', '10W-30', 800, 60000, 36000, 0.700, 'SN')
add_product('AP Super 4T Premium 10W-40 4L', 'AP OIL', 'Dầu xe máy', 'Dầu 4T cao cấp', 'semi_synthetic', '10W-40', 4000, 56000, 33000, 0.600, 'SN Plus')
add_product('AP 2T Premium Racing 0.8L', 'AP OIL', 'Dầu xe máy', 'Dầu 2T cao cấp', 'semi_synthetic', None, 800, 55000, 33000, 0.500, 'TD')
add_product('AP Tay Ga Premium 5W-40 0.8L', 'AP OIL', 'Dầu xe máy', 'Dầu tay ga cao cấp', 'full_synthetic', '5W-40', 800, 108000, 62000, 0.500, 'SP')
add_product('AP Super 4T Premium 15W-40 1L', 'AP OIL', 'Dầu xe máy', 'Dầu 4T cao cấp', 'semi_synthetic', '15W-40', 1000, 58000, 34000, 0.400, 'SN')

# === AP OIL — Dầu ô tô Premium (15 SKU, 5% DT) ===
add_product('AP Fully Synthetic 5W-40 4L', 'AP OIL', 'Dầu ô tô', 'Dầu ô tô cao cấp', 'full_synthetic', '5W-40', 4000, 95000, 55000, 2.500, 'SN Plus')
add_product('AP Fully Synthetic 5W-40 1L', 'AP OIL', 'Dầu ô tô', 'Dầu ô tô cao cấp', 'full_synthetic', '5W-40', 1000, 100000, 58000, 1.800, 'SN Plus')
add_product('AP Fully Synthetic 5W-30 4L', 'AP OIL', 'Dầu ô tô', 'Dầu ô tô cao cấp', 'full_synthetic', '5W-30', 4000, 90000, 52000, 2.000, 'SP')
add_product('AP Fully Synthetic 5W-30 1L', 'AP OIL', 'Dầu ô tô', 'Dầu ô tô cao cấp', 'full_synthetic', '5W-30', 1000, 95000, 55000, 1.500, 'SP')
add_product('AP Fully Synthetic 0W-20 4L', 'AP OIL', 'Dầu ô tô', 'Dầu ô tô cao cấp', 'full_synthetic', '0W-20', 4000, 105000, 60000, 1.200, 'SP')
add_product('AP Fully Synthetic 0W-20 1L', 'AP OIL', 'Dầu ô tô', 'Dầu ô tô cao cấp', 'full_synthetic', '0W-20', 1000, 110000, 62000, 0.800, 'SP')
add_product('AP Fully Synthetic 0W-40 4L', 'AP OIL', 'Dầu ô tô', 'Dầu ô tô cao cấp', 'full_synthetic', '0W-40', 4000, 100000, 58000, 0.800, 'SP')
add_product('AP Semi Synthetic 10W-40 4L', 'AP OIL', 'Dầu ô tô', 'Dầu ô tô cao cấp', 'semi_synthetic', '10W-40', 4000, 65000, 38000, 1.000, 'SN Plus')
add_product('AP Semi Synthetic 10W-40 1L', 'AP OIL', 'Dầu ô tô', 'Dầu ô tô cao cấp', 'semi_synthetic', '10W-40', 1000, 68000, 40000, 0.700, 'SN Plus')
add_product('AP Diesel Premium CK-4 5W-30 5L', 'AP OIL', 'Dầu ô tô', 'Dầu diesel cao cấp', 'full_synthetic', '5W-30', 5000, 88000, 52000, 0.600, 'CK-4')
add_product('AP Diesel Premium CJ-4 10W-40 5L', 'AP OIL', 'Dầu ô tô', 'Dầu diesel cao cấp', 'semi_synthetic', '10W-40', 5000, 55000, 34000, 0.500, 'CJ-4')
add_product('AP ATF Multi 1L', 'AP OIL', 'Dầu ô tô', 'Dầu hộp số tự động', 'semi_synthetic', None, 1000, 60000, 36000, 0.400, None)
add_product('AP ATF Multi 4L', 'AP OIL', 'Dầu ô tô', 'Dầu hộp số tự động', 'semi_synthetic', None, 4000, 55000, 34000, 0.300, None)
add_product('AP CVT Fluid 1L', 'AP OIL', 'Dầu ô tô', 'Dầu hộp số CVT', 'full_synthetic', None, 1000, 75000, 45000, 0.300, None)
add_product('AP Fully Synthetic 10W-60 4L', 'AP OIL', 'Dầu ô tô', 'Dầu ô tô cao cấp', 'full_synthetic', '10W-60', 4000, 115000, 65000, 0.200, 'SP')

# === AP OIL — Dầu công nghiệp (30 SKU, 12% DT) ===
add_product('AP Hydraulic Oil 32 18L', 'AP OIL', 'Dầu công nghiệp', 'Dầu thủy lực', 'mineral', '32', 18000, 28000, 19000, 3.000, None)
add_product('AP Hydraulic Oil 46 18L', 'AP OIL', 'Dầu công nghiệp', 'Dầu thủy lực', 'mineral', '46', 18000, 28000, 19000, 3.500, None)
add_product('AP Hydraulic Oil 68 18L', 'AP OIL', 'Dầu công nghiệp', 'Dầu thủy lực', 'mineral', '68', 18000, 29000, 19500, 2.500, None)
add_product('AP Hydraulic Oil 46 200L', 'AP OIL', 'Dầu công nghiệp', 'Dầu thủy lực', 'mineral', '46', 200000, 26000, 18000, 2.800, None)
add_product('AP Hydraulic Oil 32 200L', 'AP OIL', 'Dầu công nghiệp', 'Dầu thủy lực', 'mineral', '32', 200000, 26000, 18000, 2.200, None)
add_product('AP Hydraulic AW 46 18L', 'AP OIL', 'Dầu công nghiệp', 'Dầu thủy lực', 'semi_synthetic', '46', 18000, 45000, 28000, 1.500, None)
add_product('AP Gear Oil 100 25L', 'AP OIL', 'Dầu công nghiệp', 'Dầu bánh răng', 'mineral', '100', 25000, 30000, 20000, 2.000, None)
add_product('AP Gear Oil 220 25L', 'AP OIL', 'Dầu công nghiệp', 'Dầu bánh răng', 'mineral', '220', 25000, 32000, 21000, 2.500, None)
add_product('AP Gear Oil 320 25L', 'AP OIL', 'Dầu công nghiệp', 'Dầu bánh răng', 'mineral', '320', 25000, 33000, 22000, 1.500, None)
add_product('AP Gear Oil 460 25L', 'AP OIL', 'Dầu công nghiệp', 'Dầu bánh răng', 'mineral', '460', 25000, 34000, 23000, 1.000, None)
add_product('AP Gear Oil 220 200L', 'AP OIL', 'Dầu công nghiệp', 'Dầu bánh răng', 'mineral', '220', 200000, 30000, 20000, 1.800, None)
add_product('AP Cutting Oil 18L', 'AP OIL', 'Dầu công nghiệp', 'Dầu cắt gọt', 'mineral', None, 18000, 35000, 22000, 1.500, None)
add_product('AP Cutting Oil 200L', 'AP OIL', 'Dầu công nghiệp', 'Dầu cắt gọt', 'mineral', None, 200000, 32000, 20000, 1.200, None)
add_product('AP Cutting Oil Semi-Syn 18L', 'AP OIL', 'Dầu công nghiệp', 'Dầu cắt gọt', 'semi_synthetic', None, 18000, 52000, 32000, 0.800, None)
add_product('AP Heat Transfer Oil 200L', 'AP OIL', 'Dầu công nghiệp', 'Dầu truyền nhiệt', 'mineral', None, 200000, 30000, 20000, 1.500, None)
add_product('AP Heat Transfer Oil 25L', 'AP OIL', 'Dầu công nghiệp', 'Dầu truyền nhiệt', 'mineral', None, 25000, 32000, 21000, 1.000, None)
add_product('AP Compressor Oil 46 18L', 'AP OIL', 'Dầu công nghiệp', 'Dầu máy nén khí', 'mineral', '46', 18000, 33000, 22000, 1.200, None)
add_product('AP Compressor Oil 68 18L', 'AP OIL', 'Dầu công nghiệp', 'Dầu máy nén khí', 'mineral', '68', 18000, 34000, 23000, 1.000, None)
add_product('AP Compressor Oil 100 18L', 'AP OIL', 'Dầu công nghiệp', 'Dầu máy nén khí', 'mineral', '100', 18000, 35000, 23500, 0.800, None)
add_product('AP Turbine Oil 32 200L', 'AP OIL', 'Dầu công nghiệp', 'Dầu tuabin', 'mineral', '32', 200000, 35000, 24000, 0.600, None)
add_product('AP Transformer Oil 200L', 'AP OIL', 'Dầu công nghiệp', 'Dầu biến thế', 'mineral', None, 200000, 28000, 19000, 0.800, None)
add_product('AP Hydraulic Oil 100 18L', 'AP OIL', 'Dầu công nghiệp', 'Dầu thủy lực', 'mineral', '100', 18000, 30000, 20000, 0.700, None)
add_product('AP Slideway Oil 68 18L', 'AP OIL', 'Dầu công nghiệp', 'Dầu trượt', 'mineral', '68', 18000, 33000, 22000, 0.500, None)
add_product('AP Spindle Oil 10 18L', 'AP OIL', 'Dầu công nghiệp', 'Dầu trục chính', 'mineral', '10', 18000, 35000, 23000, 0.400, None)
add_product('AP Chain Oil 18L', 'AP OIL', 'Dầu công nghiệp', 'Dầu xích', 'mineral', None, 18000, 30000, 20000, 0.300, None)
add_product('AP Rust Preventive Oil 18L', 'AP OIL', 'Dầu công nghiệp', 'Dầu chống rỉ', 'mineral', None, 18000, 32000, 21000, 0.300, None)
add_product('AP Hydraulic Oil 46 25L', 'AP OIL', 'Dầu công nghiệp', 'Dầu thủy lực', 'mineral', '46', 25000, 27000, 18500, 1.200, None)
add_product('AP Gear Oil Synthetic 220 25L', 'AP OIL', 'Dầu công nghiệp', 'Dầu bánh răng', 'full_synthetic', '220', 25000, 65000, 42000, 0.400, None)
add_product('AP Hydraulic HVLP 46 18L', 'AP OIL', 'Dầu công nghiệp', 'Dầu thủy lực', 'semi_synthetic', '46', 18000, 48000, 30000, 0.500, None)
add_product('AP Food Grade Oil H1 18L', 'AP OIL', 'Dầu công nghiệp', 'Dầu thực phẩm', 'mineral', None, 18000, 55000, 35000, 0.200, None)

# === Saigon Petro — Dầu hàng hải (15 SKU, 7% DT) ===
add_product('SP Marine Diesel 15W-40 200L', 'Saigon Petro', 'Dầu hàng hải', 'Dầu tàu viễn dương', 'mineral', '15W-40', 200000, 25000, 17000, 3.500, 'CF')
add_product('SP Marine Diesel 15W-40 25L', 'Saigon Petro', 'Dầu hàng hải', 'Dầu tàu viễn dương', 'mineral', '15W-40', 25000, 27000, 18000, 2.500, 'CF')
add_product('SP Marine Diesel 30 200L', 'Saigon Petro', 'Dầu hàng hải', 'Dầu tàu viễn dương', 'mineral', '30', 200000, 23000, 16000, 2.000, 'CF')
add_product('SP Marine Diesel 40 200L', 'Saigon Petro', 'Dầu hàng hải', 'Dầu tàu viễn dương', 'mineral', '40', 200000, 22000, 15500, 1.800, 'CF')
add_product('SP Ghe Cá 2T 1L', 'Saigon Petro', 'Dầu hàng hải', 'Dầu ghe cá', 'mineral', None, 1000, 24000, 16000, 3.000, 'TC')
add_product('SP Ghe Cá 2T 4L', 'Saigon Petro', 'Dầu hàng hải', 'Dầu ghe cá', 'mineral', None, 4000, 22000, 15000, 2.200, 'TC')
add_product('SP Marine Gear Oil 90 25L', 'Saigon Petro', 'Dầu hàng hải', 'Dầu hộp số tàu', 'mineral', '90', 25000, 28000, 19000, 1.200, 'GL-4')
add_product('SP Marine Gear Oil 140 25L', 'Saigon Petro', 'Dầu hàng hải', 'Dầu hộp số tàu', 'mineral', '140', 25000, 29000, 19500, 1.000, 'GL-5')
add_product('SP Marine System Oil 200L', 'Saigon Petro', 'Dầu hàng hải', 'Dầu hệ thống tàu', 'mineral', None, 200000, 24000, 16500, 1.500, None)
add_product('SP Marine Cylinder Oil 200L', 'Saigon Petro', 'Dầu hàng hải', 'Dầu xi lanh tàu', 'mineral', None, 200000, 26000, 17500, 0.800, None)
add_product('SP Ghe Cá 4T 15W-40 1L', 'Saigon Petro', 'Dầu hàng hải', 'Dầu ghe cá', 'mineral', '15W-40', 1000, 26000, 17500, 1.500, 'CF')
add_product('SP Ghe Cá 4T 15W-40 4L', 'Saigon Petro', 'Dầu hàng hải', 'Dầu ghe cá', 'mineral', '15W-40', 4000, 24000, 16500, 1.200, 'CF')
add_product('SP Marine Diesel TBN30 200L', 'Saigon Petro', 'Dầu hàng hải', 'Dầu tàu viễn dương', 'mineral', None, 200000, 28000, 19000, 0.500, None)
add_product('SP Marine Hydraulic 46 25L', 'Saigon Petro', 'Dầu hàng hải', 'Dầu thủy lực tàu', 'mineral', '46', 25000, 29000, 19500, 0.500, None)
add_product('SP Marine Stern Tube Oil 25L', 'Saigon Petro', 'Dầu hàng hải', 'Dầu ống bao lái', 'mineral', None, 25000, 32000, 21000, 0.300, None)

# === Saigon Petro — Dầu nông nghiệp (10 SKU, 3% DT) ===
add_product('SP Nông nghiệp 15W-40 5L', 'Saigon Petro', 'Dầu nông nghiệp', 'Dầu máy nông nghiệp', 'mineral', '15W-40', 5000, 26000, 18000, 2.500, 'CF-4')
add_product('SP Nông nghiệp 15W-40 18L', 'Saigon Petro', 'Dầu nông nghiệp', 'Dầu máy nông nghiệp', 'mineral', '15W-40', 18000, 24000, 17000, 2.000, 'CF-4')
add_product('SP Nông nghiệp 20W-50 5L', 'Saigon Petro', 'Dầu nông nghiệp', 'Dầu máy nông nghiệp', 'mineral', '20W-50', 5000, 25000, 17500, 1.500, 'CF')
add_product('SP Nông nghiệp 20W-50 18L', 'Saigon Petro', 'Dầu nông nghiệp', 'Dầu máy nông nghiệp', 'mineral', '20W-50', 18000, 23000, 16500, 1.200, 'CF')
add_product('SP Nông nghiệp Đa dụng 15W-40 200L', 'Saigon Petro', 'Dầu nông nghiệp', 'Dầu máy nông nghiệp', 'mineral', '15W-40', 200000, 22000, 15500, 1.000, 'CF-4')
add_product('SP Máy cày 40 5L', 'Saigon Petro', 'Dầu nông nghiệp', 'Dầu máy nông nghiệp', 'mineral', '40', 5000, 22000, 15000, 0.800, 'CF')
add_product('SP Máy cày 40 18L', 'Saigon Petro', 'Dầu nông nghiệp', 'Dầu máy nông nghiệp', 'mineral', '40', 18000, 20000, 14000, 0.600, 'CF')
add_product('SP Máy gặt 15W-40 5L', 'Saigon Petro', 'Dầu nông nghiệp', 'Dầu máy nông nghiệp', 'mineral', '15W-40', 5000, 25000, 17000, 0.500, 'CI-4')
add_product('SP Máy bơm nước 5L', 'Saigon Petro', 'Dầu nông nghiệp', 'Dầu máy nông nghiệp', 'mineral', '15W-40', 5000, 24000, 16500, 0.400, 'CF')
add_product('SP Nông nghiệp Gear 80W-90 5L', 'Saigon Petro', 'Dầu nông nghiệp', 'Dầu máy nông nghiệp', 'mineral', '80W-90', 5000, 28000, 19000, 0.300, 'GL-4')

# === Sino — Dầu phổ thông (15 SKU, 3% DT) ===
add_product('Sino 4T 20W-50 0.8L', 'Sino', 'Dầu xe máy', 'Dầu xe máy phổ thông', 'mineral', '20W-50', 800, 20000, 14000, 2.500, 'SG')
add_product('Sino 4T 20W-50 1L', 'Sino', 'Dầu xe máy', 'Dầu xe máy phổ thông', 'mineral', '20W-50', 1000, 19000, 13500, 2.200, 'SG')
add_product('Sino 4T 20W-40 0.8L', 'Sino', 'Dầu xe máy', 'Dầu xe máy phổ thông', 'mineral', '20W-40', 800, 18000, 13000, 1.800, 'SF')
add_product('Sino 4T 20W-40 1L', 'Sino', 'Dầu xe máy', 'Dầu xe máy phổ thông', 'mineral', '20W-40', 1000, 17000, 12500, 1.500, 'SF')
add_product('Sino 2T 0.8L', 'Sino', 'Dầu xe máy', 'Dầu xe máy phổ thông', 'mineral', None, 800, 18000, 12500, 1.200, 'TB')
add_product('Sino 2T 1L', 'Sino', 'Dầu xe máy', 'Dầu xe máy phổ thông', 'mineral', None, 1000, 17000, 12000, 1.000, 'TB')
add_product('Sino Đa dụng 20W-50 1L', 'Sino', 'Dầu xe máy', 'Dầu đa dụng', 'mineral', '20W-50', 1000, 18000, 12500, 0.800, 'SF')
add_product('Sino Đa dụng 20W-50 4L', 'Sino', 'Dầu xe máy', 'Dầu đa dụng', 'mineral', '20W-50', 4000, 16000, 11500, 0.600, 'SF')
add_product('Sino Diesel 15W-40 5L', 'Sino', 'Dầu xe máy', 'Dầu diesel phổ thông', 'mineral', '15W-40', 5000, 22000, 15000, 1.000, 'CF')
add_product('Sino Diesel 15W-40 18L', 'Sino', 'Dầu xe máy', 'Dầu diesel phổ thông', 'mineral', '15W-40', 18000, 20000, 14000, 0.800, 'CF')
add_product('Sino 4T Economy 20W-50 0.8L', 'Sino', 'Dầu xe máy', 'Dầu xe máy phổ thông', 'mineral', '20W-50', 800, 16000, 11000, 1.500, 'SA')
add_product('Sino Tay Ga 10W-40 0.8L', 'Sino', 'Dầu xe máy', 'Dầu xe máy phổ thông', 'mineral', '10W-40', 800, 25000, 17000, 0.700, 'SJ')
add_product('Sino Gear 80W-90 1L', 'Sino', 'Dầu xe máy', 'Dầu đa dụng', 'mineral', '80W-90', 1000, 22000, 15000, 0.400, 'GL-4')
add_product('Sino Multi Spray 300ml', 'Sino', 'Dầu xe máy', 'Dầu đa dụng', 'mineral', None, 300, 30000, 15000, 0.500, None)
add_product('Sino 4T 15W-40 1L', 'Sino', 'Dầu xe máy', 'Dầu xe máy phổ thông', 'mineral', '15W-40', 1000, 20000, 14000, 0.600, 'SJ')

# === Polaris — Mỡ bôi trơn (10 SKU, 2% DT) ===
add_product('Polaris Mỡ Đa dụng EP2 0.5kg', 'Polaris', 'Mỡ bôi trơn', 'Mỡ công nghiệp', 'grease', None, 500, 45000, 28000, 2.000, None)
add_product('Polaris Mỡ Đa dụng EP2 1kg', 'Polaris', 'Mỡ bôi trơn', 'Mỡ công nghiệp', 'grease', None, 1000, 42000, 26000, 1.800, None)
add_product('Polaris Mỡ Đa dụng EP2 15kg', 'Polaris', 'Mỡ bôi trơn', 'Mỡ công nghiệp', 'grease', None, 15000, 40000, 25000, 1.500, None)
add_product('Polaris Mỡ Đa dụng EP3 15kg', 'Polaris', 'Mỡ bôi trơn', 'Mỡ công nghiệp', 'grease', None, 15000, 42000, 26000, 1.200, None)
add_product('Polaris Mỡ Chịu nhiệt EP2 1kg', 'Polaris', 'Mỡ bôi trơn', 'Mỡ công nghiệp', 'grease', None, 1000, 55000, 35000, 0.800, None)
add_product('Polaris Mỡ Chịu nhiệt EP2 15kg', 'Polaris', 'Mỡ bôi trơn', 'Mỡ công nghiệp', 'grease', None, 15000, 52000, 33000, 1.000, None)
add_product('Polaris Mỡ Bò 0.5kg', 'Polaris', 'Mỡ bôi trơn', 'Mỡ công nghiệp', 'grease', None, 500, 35000, 22000, 0.800, None)
add_product('Polaris Mỡ Bò 1kg', 'Polaris', 'Mỡ bôi trơn', 'Mỡ công nghiệp', 'grease', None, 1000, 33000, 21000, 0.600, None)
add_product('Polaris Mỡ Thực phẩm H1 1kg', 'Polaris', 'Mỡ bôi trơn', 'Mỡ thực phẩm', 'grease', None, 1000, 60000, 40000, 0.300, None)
add_product('Polaris Mỡ Xanh EP2 180kg', 'Polaris', 'Mỡ bôi trơn', 'Mỡ công nghiệp', 'grease', None, 180000, 38000, 24000, 0.500, None)

cur.executemany(
    "INSERT INTO products (product_id, product_name, brand, product_group, product_category, product_type, viscosity_grade, volume_ml, unit_price_vnd, cost_per_liter_vnd, popularity_weight, api_grade, status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
    products
)
print(f"Products: {len(products)} records")

conn.commit()

# Print summary
cur.execute("SELECT COUNT(*) FROM regions")
print(f"\nVerify - Regions: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM channels")
print(f"Verify - Channels: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM distributors")
print(f"Verify - Distributors: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM products")
print(f"Verify - Products: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM suppliers")
print(f"Verify - Suppliers: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM production_lines")
print(f"Verify - Production Lines: {cur.fetchone()[0]}")

# Product breakdown
cur.execute("SELECT brand, product_group, product_type, COUNT(*) FROM products GROUP BY brand, product_group, product_type ORDER BY brand, product_group")
print("\nProduct breakdown:")
for row in cur.fetchall():
    print(f"  {row[0]} | {row[1]} | {row[2]}: {row[3]} SKU")

# Distributor breakdown
cur.execute("SELECT tier, COUNT(*) FROM distributors GROUP BY tier")
print("\nDistributor breakdown:")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]} NPP")

# Region breakdown
cur.execute("SELECT region_name, COUNT(*) FROM regions GROUP BY region_name")
print("\nRegion breakdown:")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]} tỉnh")

cur.close()
conn.close()
print("\nDone!")
