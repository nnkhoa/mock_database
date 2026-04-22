#!/usr/bin/env python3
"""
EVNCPC Demo Database Generator
Tổng Công ty Điện lực miền Trung — Mock Data Generation

Generates realistic data for 8 power companies across 13 provinces,
with embedded anomalies for 5 demo scenarios.

Time range: Oct 2023 (Year 1) → Sep 2025 (Year 2)
Most recent month: Sep 2025
"""

import mysql.connector
import random
import math
from datetime import date, timedelta, time as dtime
from decimal import Decimal

random.seed(42)

# ─── CONNECTION ───────────────────────────────────────────────────────────
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'root',
    'database': 'evncpc_demo',
    'charset': 'utf8mb4',
}

# ─── TIME CONSTANTS ──────────────────────────────────────────────────────
# Year 1 = Oct 2023 → Sep 2024,  Year 2 = Oct 2024 → Sep 2025
YEAR1 = 2024  # label for "năm trước"
YEAR2 = 2025  # label for "năm hiện tại"
MONTHS_24 = []
for y in [2023, 2024]:
    start_m = 10 if y == 2023 else 1
    end_m = 12 if y == 2023 else 9
    for m in range(start_m, end_m + 1):
        MONTHS_24.append(date(y + (1 if y == 2023 else 1), m, 1) if False else date(y, m, 1))

# Rebuild properly: Oct 2023..Sep 2025
MONTHS_24 = []
for y, m in [(2023,10),(2023,11),(2023,12),
             (2024,1),(2024,2),(2024,3),(2024,4),(2024,5),(2024,6),
             (2024,7),(2024,8),(2024,9),(2024,10),(2024,11),(2024,12),
             (2025,1),(2025,2),(2025,3),(2025,4),(2025,5),(2025,6),
             (2025,7),(2025,8),(2025,9)]:
    MONTHS_24.append(date(y, m, 1))

assert len(MONTHS_24) == 24, f"Expected 24 months, got {len(MONTHS_24)}"

# ─── SEASONALITY COEFFICIENTS ────────────────────────────────────────────
POWER_SEASON = {1:0.85, 2:0.82, 3:0.92, 4:0.98, 5:1.12, 6:1.22,
                7:1.20, 8:1.15, 9:1.02, 10:0.95, 11:0.90, 12:0.88}

SAIDI_SEASON = {1:0.80, 2:0.75, 3:0.85, 4:0.90, 5:1.00, 6:1.05,
                7:1.10, 8:1.05, 9:1.40, 10:1.65, 11:1.30, 12:0.95}

LOSS_SEASON  = {1:0.96, 2:0.94, 3:0.97, 4:0.99, 5:1.04, 6:1.08,
                7:1.07, 8:1.05, 9:1.01, 10:0.98, 11:0.96, 12:0.95}

INCIDENTS_SEASON = {1:0.60, 2:0.50, 3:0.65, 4:0.70, 5:0.85, 6:0.90,
                    7:0.95, 8:0.90, 9:1.50, 10:2.20, 11:1.60, 12:0.80}

COST_DISASTER_SEASON = {1:0.40, 2:0.30, 3:0.40, 4:0.50, 5:0.60, 6:0.70,
                        7:0.80, 8:0.80, 9:2.50, 10:3.50, 11:2.00, 12:0.80}

# ─── YoY GROWTH ──────────────────────────────────────────────────────────
YOY_POWER = 1.08
YOY_REVENUE = 1.10
YOY_LOSS_IMPROVE = 0.97  # loss decreases 3%/year (improvement)

# ─── MASTER DATA DEFINITIONS ─────────────────────────────────────────────

POWER_COMPANIES = [
    ('PC01', 'Công ty Điện lực Quảng Trị', 'PC Quảng Trị', 'Quảng Bình, Quảng Trị',
     'Đông Hà', 1800, 620000, 8500.0, 18, 3800, False, '2025-07-01',
     'Sáp nhập PC Quảng Bình và PC Quảng Trị. Vùng rủi ro bão cao nhất'),
    ('PC02', 'Công ty Điện lực Huế', 'PC Huế', 'Thừa Thiên Huế',
     'Huế', 1200, 480000, 5200.0, 14, 2900, False, '2025-07-01',
     'Giữ nguyên. Di sản văn hóa, du lịch'),
    ('PC03', 'Công ty Điện lực Đà Nẵng', 'PC Đà Nẵng', 'Đà Nẵng, Quảng Nam',
     'Đà Nẵng', 2400, 1050000, 12500.0, 32, 6200, False, '2025-07-01',
     'Sáp nhập, lớn nhất. Đô thị hóa cao, DMS tốt, restoration nhanh'),
    ('PC04', 'Công ty Điện lực Quảng Ngãi', 'PC Quảng Ngãi', 'Quảng Ngãi, Kon Tum',
     'Quảng Ngãi', 1400, 520000, 7800.0, 16, 3500, False, '2025-07-01',
     'Sáp nhập. Kon Tum vùng núi, lưới dài, khó vận hành'),
    ('PC05', 'Công ty Điện lực Gia Lai', 'PC Gia Lai', 'Gia Lai, Bình Định',
     'Pleiku', 1800, 680000, 9200.0, 22, 4500, False, '2025-07-01',
     'Sáp nhập. TRỌNG TÂM ANOMALY: tổn thất cao do MBA cũ vùng Bình Định'),
    ('PC06', 'Công ty Điện lực Đắk Lắk', 'PC Đắk Lắk', 'Đắk Lắk, Phú Yên',
     'Buôn Ma Thuột', 1500, 580000, 8100.0, 18, 3800, False, '2025-07-01',
     'Sáp nhập. Tây Nguyên, SAIDI anomaly tăng 18% YoY'),
    ('PC07', 'Công ty Điện lực Khánh Hòa', 'PC Khánh Hòa', 'Khánh Hòa, Ninh Thuận',
     'Nha Trang', 1200, 520000, 6800.0, 16, 3200, False, '2025-07-01',
     'Tiếp nhận Ninh Thuận từ EVNSPC. Du lịch biển + điện mặt trời'),
    ('PC08', 'Công ty Cổ phần Điện lực Khánh Hòa', 'CP ĐL Khánh Hòa', 'Khánh Hòa (Nha Trang TP)',
     'Nha Trang', 600, 350000, 2800.0, 8, 1800, True, '2025-07-01',
     'Công ty cổ phần, giữ nguyên. Chỉ quản lý đô thị Nha Trang'),
]

PROVINCES = [
    # (province_id, name, pc_id, region, area_km2, population, num_districts, terrain, storm_risk)
    ('P01', 'Quảng Bình', 'PC01', 'Duyên hải', 8065.3, 910000, 8, 'Hỗn hợp', 'Cao'),
    ('P02', 'Quảng Trị', 'PC01', 'Duyên hải', 4739.8, 640000, 10, 'Hỗn hợp', 'Cao'),
    ('P03', 'Thừa Thiên Huế', 'PC02', 'Duyên hải', 5033.2, 1130000, 9, 'Hỗn hợp', 'Cao'),
    ('P04', 'Đà Nẵng', 'PC03', 'Duyên hải', 1285.4, 1220000, 8, 'Ven biển', 'Cao'),
    ('P05', 'Quảng Nam', 'PC03', 'Duyên hải', 10574.7, 1500000, 18, 'Hỗn hợp', 'Cao'),
    ('P06', 'Quảng Ngãi', 'PC04', 'Duyên hải', 5153.6, 1230000, 14, 'Hỗn hợp', 'Cao'),
    ('P07', 'Kon Tum', 'PC04', 'Tây Nguyên', 9689.6, 580000, 10, 'Đồi núi', 'Thấp'),
    ('P08', 'Gia Lai', 'PC05', 'Tây Nguyên', 15536.9, 1530000, 17, 'Đồi núi', 'Thấp'),
    ('P09', 'Bình Định', 'PC05', 'Duyên hải', 6025.6, 1490000, 11, 'Hỗn hợp', 'Trung bình'),
    ('P10', 'Đắk Lắk', 'PC06', 'Tây Nguyên', 13125.4, 1920000, 15, 'Đồi núi', 'Thấp'),
    ('P11', 'Phú Yên', 'PC06', 'Duyên hải', 5060.6, 870000, 9, 'Hỗn hợp', 'Trung bình'),
    ('P12', 'Khánh Hòa', 'PC07', 'Duyên hải', 5137.8, 1250000, 9, 'Ven biển', 'Trung bình'),
    ('P13', 'Ninh Thuận', 'PC07', 'Duyên hải', 3358.3, 590000, 7, 'Ven biển', 'Trung bình'),
]

# Districts: ~65 records — real district names
DISTRICTS = [
    # PC01 — Quảng Bình (P01): 4 districts
    ('D0101', 'TP Đồng Hới', 'P01', 'PC01', 'Thành phố', 155.5, 125000, True),
    ('D0102', 'Huyện Bố Trạch', 'P01', 'PC01', 'Huyện', 2115.5, 85000, False),
    ('D0103', 'Huyện Quảng Ninh', 'P01', 'PC01', 'Huyện', 1191.5, 48000, False),
    ('D0104', 'Huyện Lệ Thủy', 'P01', 'PC01', 'Huyện', 1276.5, 62000, False),
    # PC01 — Quảng Trị (P02): 4 districts
    ('D0105', 'TP Đông Hà', 'P02', 'PC01', 'Thành phố', 72.5, 98000, True),
    ('D0106', 'TX Quảng Trị', 'P02', 'PC01', 'Thị xã', 45.2, 32000, True),
    ('D0107', 'Huyện Hải Lăng', 'P02', 'PC01', 'Huyện', 426.5, 55000, False),
    ('D0108', 'Huyện Triệu Phong', 'P02', 'PC01', 'Huyện', 353.5, 48000, False),
    # PC02 — Thừa Thiên Huế (P03): 5 districts
    ('D0201', 'TP Huế', 'P03', 'PC02', 'Thành phố', 265.8, 165000, True),
    ('D0202', 'TX Hương Thủy', 'P03', 'PC02', 'Thị xã', 456.2, 52000, True),
    ('D0203', 'TX Hương Trà', 'P03', 'PC02', 'Thị xã', 518.5, 48000, True),
    ('D0204', 'Huyện Phú Vang', 'P03', 'PC02', 'Huyện', 280.3, 72000, False),
    ('D0205', 'Huyện Phong Điền', 'P03', 'PC02', 'Huyện', 948.5, 55000, False),
    # PC03 — Đà Nẵng (P04): 5 districts
    ('D0301', 'Quận Hải Châu', 'P04', 'PC03', 'Thành phố', 23.5, 145000, True),
    ('D0302', 'Quận Thanh Khê', 'P04', 'PC03', 'Thành phố', 9.5, 125000, True),
    ('D0303', 'Quận Sơn Trà', 'P04', 'PC03', 'Thành phố', 59.3, 110000, True),
    ('D0304', 'Quận Ngũ Hành Sơn', 'P04', 'PC03', 'Thành phố', 39.1, 85000, True),
    ('D0305', 'Quận Liên Chiểu', 'P04', 'PC03', 'Thành phố', 79.1, 95000, True),
    # PC03 — Quảng Nam (P05): 6 districts
    ('D0306', 'TP Tam Kỳ', 'P05', 'PC03', 'Thành phố', 92.8, 78000, True),
    ('D0307', 'TP Hội An', 'P05', 'PC03', 'Thành phố', 61.5, 65000, True),
    ('D0308', 'TX Điện Bàn', 'P05', 'PC03', 'Thị xã', 214.5, 82000, True),
    ('D0309', 'Huyện Đại Lộc', 'P05', 'PC03', 'Huyện', 587.5, 55000, False),
    ('D0310', 'Huyện Duy Xuyên', 'P05', 'PC03', 'Huyện', 299.1, 48000, False),
    ('D0311', 'Huyện Núi Thành', 'P05', 'PC03', 'Huyện', 533.5, 62000, False),
    # PC04 — Quảng Ngãi (P06): 5 districts
    ('D0401', 'TP Quảng Ngãi', 'P06', 'PC04', 'Thành phố', 160.2, 115000, True),
    ('D0402', 'Huyện Bình Sơn', 'P06', 'PC04', 'Huyện', 468.5, 65000, False),
    ('D0403', 'Huyện Sơn Tịnh', 'P06', 'PC04', 'Huyện', 245.8, 52000, False),
    ('D0404', 'Huyện Tư Nghĩa', 'P06', 'PC04', 'Huyện', 227.5, 48000, False),
    ('D0405', 'Huyện Đức Phổ', 'P06', 'PC04', 'Huyện', 372.3, 42000, False),
    # PC04 — Kon Tum (P07): 4 districts
    ('D0406', 'TP Kon Tum', 'P07', 'PC04', 'Thành phố', 432.5, 85000, True),
    ('D0407', 'Huyện Đắk Hà', 'P07', 'PC04', 'Huyện', 845.2, 35000, False),
    ('D0408', 'Huyện Ngọc Hồi', 'P07', 'PC04', 'Huyện', 844.8, 28000, False),
    ('D0409', 'Huyện Sa Thầy', 'P07', 'PC04', 'Huyện', 1492.5, 22000, False),
    # PC05 — Gia Lai (P08): 5 districts
    ('D0501', 'TX An Nhơn', 'P09', 'PC05', 'Thị xã', 242.5, 95000, True),   # Bình Định — anomaly
    ('D0502', 'Huyện Tuy Phước', 'P09', 'PC05', 'Huyện', 217.5, 78000, False),  # Bình Định — anomaly
    ('D0503', 'Huyện Phù Cát', 'P09', 'PC05', 'Huyện', 680.5, 72000, False),    # Bình Định — anomaly
    ('D0504', 'TP Quy Nhơn', 'P09', 'PC05', 'Thành phố', 286.2, 115000, True),  # Bình Định — anomaly
    ('D0505', 'TP Pleiku', 'P08', 'PC05', 'Thành phố', 260.8, 105000, True),
    ('D0506', 'TX An Khê', 'P08', 'PC05', 'Thị xã', 198.5, 42000, True),
    ('D0507', 'TX Ayun Pa', 'P08', 'PC05', 'Thị xã', 152.5, 35000, True),
    ('D0508', 'Huyện Chư Sê', 'P08', 'PC05', 'Huyện', 642.5, 48000, False),
    ('D0509', 'Huyện Ia Grai', 'P08', 'PC05', 'Huyện', 1152.5, 32000, False),
    ('D0510', 'Huyện Tây Sơn', 'P09', 'PC05', 'Huyện', 554.5, 58000, False),  # Bình Định
    # PC06 — Đắk Lắk (P10): 5 districts
    ('D0601', 'TP Buôn Ma Thuột', 'P10', 'PC06', 'Thành phố', 377.2, 125000, True),
    ('D0602', 'TX Buôn Hồ', 'P10', 'PC06', 'Thị xã', 282.5, 45000, True),
    ('D0603', 'Huyện Krông Pắc', 'P10', 'PC06', 'Huyện', 625.5, 58000, False),
    ('D0604', 'Huyện Cư M\'gar', 'P10', 'PC06', 'Huyện', 824.5, 52000, False),
    ('D0605', 'Huyện Ea H\'leo', 'P10', 'PC06', 'Huyện', 1352.5, 38000, False),
    # PC06 — Phú Yên (P11): 4 districts
    ('D0606', 'TP Tuy Hòa', 'P11', 'PC06', 'Thành phố', 106.5, 85000, True),
    ('D0607', 'TX Sông Cầu', 'P11', 'PC06', 'Thị xã', 488.5, 42000, True),
    ('D0608', 'Huyện Tuy An', 'P11', 'PC06', 'Huyện', 398.5, 48000, False),
    ('D0609', 'Huyện Đông Hòa', 'P11', 'PC06', 'Huyện', 268.5, 52000, False),
    # PC07 — Khánh Hòa (P12): 4 districts
    ('D0701', 'TP Cam Ranh', 'P12', 'PC07', 'Thành phố', 345.2, 78000, True),
    ('D0702', 'TX Ninh Hòa', 'P12', 'PC07', 'Thị xã', 1195.5, 65000, True),
    ('D0703', 'Huyện Vạn Ninh', 'P12', 'PC07', 'Huyện', 545.5, 42000, False),
    ('D0704', 'Huyện Diên Khánh', 'P12', 'PC07', 'Huyện', 335.5, 55000, False),
    # PC07 — Ninh Thuận (P13): 4 districts
    ('D0705', 'TP Phan Rang-Tháp Chàm', 'P13', 'PC07', 'Thành phố', 79.3, 85000, True),
    ('D0706', 'Huyện Ninh Phước', 'P13', 'PC07', 'Huyện', 342.5, 42000, False),
    ('D0707', 'Huyện Thuận Bắc', 'P13', 'PC07', 'Huyện', 318.5, 28000, False),
    ('D0708', 'Huyện Ninh Hải', 'P13', 'PC07', 'Huyện', 256.5, 35000, False),
    # PC08 — Khánh Hòa Nha Trang urban (P12): 4 districts
    ('D0801', 'Phường Lộc Thọ (Nha Trang)', 'P12', 'PC08', 'Thành phố', 12.5, 95000, True),
    ('D0802', 'Phường Vĩnh Hải (Nha Trang)', 'P12', 'PC08', 'Thành phố', 18.5, 85000, True),
    ('D0803', 'Phường Phước Hải (Nha Trang)', 'P12', 'PC08', 'Thành phố', 8.5, 92000, True),
    ('D0804', 'Phường Vĩnh Nguyên (Nha Trang)', 'P12', 'PC08', 'Thành phố', 15.5, 78000, True),
]

# Customer segment templates
SEGMENT_TEMPLATES = [
    # (name, default_proportion, avg_price)
    ('Công nghiệp - Xây dựng', 60.0, 1750.0),
    ('Quản lý - Tiêu dùng', 30.0, 2200.0),
    ('Thương nghiệp - Dịch vụ', 3.0, 2600.0),
    ('Nông lâm ngư nghiệp', 2.0, 1200.0),
    ('Khác', 5.0, 1900.0),  # adjusted to sum to 100
]

# PC-specific segment overrides
SEGMENT_OVERRIDES = {
    'PC03': {'Thương nghiệp - Dịch vụ': 4.5, 'Công nghiệp - Xây dựng': 58.5},  # du lịch
    'PC05': {'Nông lâm ngư nghiệp': 3.5, 'Công nghiệp - Xây dựng': 58.5},  # Tây Nguyên
    'PC06': {'Nông lâm ngư nghiệp': 3.0, 'Công nghiệp - Xây dựng': 59.0},  # Tây Nguyên
}

LOSS_TARGETS_DATA = [
    # (pc_id, year1_loss, year2_loss, year1_saidi, year2_saidi, saifi)
    ('PC01', 3.80, 3.70, 280.0, 260.0, 2.8),
    ('PC02', 3.40, 3.30, 240.0, 220.0, 2.4),
    ('PC03', 2.90, 2.80, 160.0, 145.0, 1.8),
    ('PC04', 3.60, 3.50, 300.0, 280.0, 3.0),
    ('PC05', 4.50, 4.40, 320.0, 300.0, 3.2),
    ('PC06', 3.85, 3.75, 340.0, 320.0, 3.4),
    ('PC07', 3.50, 3.40, 260.0, 240.0, 2.6),
    ('PC08', 3.20, 3.10, 140.0, 130.0, 1.6),
]

# Weather events — 30 events over 24 months
WEATHER_EVENTS = [
    # Year 1 storm season (2023 Oct-Nov already, then 2024)
    # Late 2023
    (1, 'Áp thấp nhiệt đới số 8', 'Áp thấp nhiệt đới', '2023-10-12', '2023-10-14', 'Trung bình', 'P01,P02,P03', 75, 180, 'Ảnh hưởng duyên hải Bắc Trung Bộ'),
    (2, 'Bão số 7 - Jelawat', 'Bão', '2023-10-28', '2023-10-31', 'Nặng', 'P01,P02,P03,P04,P05', 110, 280, 'Đổ bộ Quảng Trị-Huế, gió mạnh'),
    (3, 'Mưa lớn miền Trung', 'Mưa lớn', '2023-11-05', '2023-11-08', 'Trung bình', 'P03,P04,P05,P06', 0, 350, 'Mưa lũ kéo dài, ngập nhiều nơi'),
    (4, 'Áp thấp nhiệt đới số 9', 'Áp thấp nhiệt đới', '2023-11-18', '2023-11-20', 'Nhẹ', 'P05,P06', 60, 120, 'Ảnh hưởng nhẹ ven biển'),
    (5, 'Mưa lớn Tây Nguyên', 'Mưa lớn', '2023-12-02', '2023-12-04', 'Nhẹ', 'P08,P10', 0, 180, 'Mưa cuối mùa'),
    # 2024 storm season
    (6, 'Mưa lớn đầu mùa', 'Mưa lớn', '2024-05-15', '2024-05-17', 'Nhẹ', 'P04,P05', 0, 120, 'Mưa đầu mùa bất thường'),
    (7, 'Áp thấp nhiệt đới số 1', 'Áp thấp nhiệt đới', '2024-07-10', '2024-07-12', 'Nhẹ', 'P06,P11,P12', 65, 100, 'Ảnh hưởng nhẹ Nam Trung Bộ'),
    (8, 'Bão số 2 - Prapiroon', 'Bão', '2024-07-22', '2024-07-24', 'Trung bình', 'P01,P02', 95, 200, 'Suy yếu trước khi đổ bộ'),
    (9, 'Mưa lớn miền Trung', 'Mưa lớn', '2024-08-10', '2024-08-13', 'Trung bình', 'P04,P05,P06', 0, 250, 'Mưa lớn diện rộng'),
    (10, 'Áp thấp nhiệt đới số 3', 'Áp thấp nhiệt đới', '2024-08-28', '2024-08-30', 'Nhẹ', 'P11,P12,P13', 70, 130, 'Ảnh hưởng Nam Trung Bộ'),
    (11, 'Bão số 3 - Soulik', 'Bão', '2024-09-18', '2024-09-21', 'Nặng', 'P01,P02,P03', 115, 300, 'Đổ bộ QB-QT, thiệt hại nặng'),
    (12, 'Bão số 4 - Trami', 'Bão', '2024-10-05', '2024-10-08', 'Nặng', 'P03,P04,P05,P06', 105, 350, 'Đổ bộ Đà Nẵng-Quảng Nam'),
    (13, 'Mưa lũ miền Trung', 'Lũ lụt', '2024-10-15', '2024-10-19', 'Nặng', 'P03,P04,P05,P06,P08', 0, 450, 'Lũ lịch sử nhiều tỉnh'),
    (14, 'Áp thấp nhiệt đới số 5', 'Áp thấp nhiệt đới', '2024-11-02', '2024-11-04', 'Trung bình', 'P06,P09,P11', 80, 200, 'Gây mưa Bình Định-Phú Yên'),
    (15, 'Mưa lớn Tây Nguyên', 'Mưa lớn', '2024-11-20', '2024-11-22', 'Nhẹ', 'P08,P10', 0, 160, 'Mưa cuối mùa Tây Nguyên'),
    (16, 'Sạt lở Kon Tum', 'Sạt lở', '2024-12-01', '2024-12-02', 'Trung bình', 'P07', 0, 80, 'Sạt lở đất vùng núi'),
    # 2025 storm season (Year 2)
    (17, 'Mưa lớn đầu mùa', 'Mưa lớn', '2025-05-20', '2025-05-22', 'Nhẹ', 'P04,P05,P06', 0, 130, 'Mưa trái mùa'),
    (18, 'Áp thấp nhiệt đới số 1/2025', 'Áp thấp nhiệt đới', '2025-06-25', '2025-06-27', 'Nhẹ', 'P11,P12', 60, 90, 'Ảnh hưởng nhẹ'),
    (19, 'Bão số 2/2025 - Gaemi', 'Bão', '2025-07-15', '2025-07-18', 'Trung bình', 'P01,P02,P03', 90, 220, 'Đi qua Bắc Trung Bộ'),
    (20, 'Mưa lớn Quảng Nam', 'Mưa lớn', '2025-08-05', '2025-08-07', 'Nhẹ', 'P05,P06', 0, 150, 'Mưa cục bộ'),
    (21, 'Áp thấp nhiệt đới số 3/2025', 'Áp thấp nhiệt đới', '2025-08-20', '2025-08-22', 'Trung bình', 'P06,P09,P11', 75, 170, 'Gây mưa duyên hải'),
    # KEY ANOMALY: 2 bão liên tiếp T9/2025 for Scenario 3
    (22, 'Bão số 5/2025 - Yagi', 'Bão', '2025-09-14', '2025-09-17', 'Nặng', 'P01,P02,P03', 120, 320, 'Đổ bộ QB-QT, gió cấp 12'),
    (23, 'Bão số 6/2025 - Bebinca', 'Bão', '2025-09-24', '2025-09-27', 'Rất nặng', 'P01,P02,P03,P04,P05', 150, 420, 'Siêu bão, đổ bộ QT-Huế-ĐN, thiệt hại rất lớn'),
    # Other minor events 2025
    (24, 'Lũ quét Gia Lai', 'Lũ lụt', '2025-08-12', '2025-08-13', 'Trung bình', 'P08', 0, 200, 'Lũ quét suối nhỏ'),
    (25, 'Mưa lớn Đắk Lắk', 'Mưa lớn', '2025-07-25', '2025-07-27', 'Nhẹ', 'P10', 0, 140, 'Mưa mùa hè Tây Nguyên'),
    (26, 'Sét đánh Quảng Ngãi', 'Mưa lớn', '2025-06-10', '2025-06-10', 'Nhẹ', 'P06', 0, 50, 'Giông sét cục bộ'),
    (27, 'Mưa lớn Ninh Thuận', 'Mưa lớn', '2025-09-08', '2025-09-09', 'Nhẹ', 'P13', 0, 100, 'Mưa hiếm tại Ninh Thuận'),
    (28, 'Áp thấp nhiệt đới số 4/2025', 'Áp thấp nhiệt đới', '2025-09-05', '2025-09-07', 'Trung bình', 'P09,P11,P12', 70, 180, 'Ảnh hưởng Nam Trung Bộ'),
]

# ─── BASE KPI VALUES PER PC ──────────────────────────────────────────────
# (pc_id, base_commercial_gwh, base_revenue_bvnd, base_loss_pct, base_saidi_min,
#  base_saifi, base_maifi, base_peak_mw, base_employees, base_collection_rate)
PC_BASE_KPI = {
    'PC01': (232, 465, 3.65, 22, 0.22, 0.35, 580, 1800, 99.85),
    'PC02': (184, 380, 3.25, 18, 0.18, 0.28, 475, 1200, 99.90),
    'PC03': (514, 1065, 2.75, 12, 0.12, 0.18, 1280, 2400, 99.95),
    'PC04': (196, 392, 3.45, 24, 0.24, 0.38, 490, 1400, 99.82),
    'PC05': (257, 502, 4.20, 26, 0.26, 0.42, 635, 1800, 99.80),
    'PC06': (220, 440, 3.70, 28, 0.28, 0.45, 550, 1500, 99.78),
    'PC07': (196, 404, 3.35, 20, 0.20, 0.32, 500, 1200, 99.88),
    'PC08': (135, 294, 3.05, 10, 0.10, 0.15, 340, 600, 99.92),
}

# Loss breakdown ratios (technical_mv : technical_lv : commercial)
LOSS_BREAKDOWN = {
    'PC01': (0.38, 0.42, 0.20),
    'PC02': (0.36, 0.44, 0.20),
    'PC03': (0.35, 0.40, 0.25),
    'PC04': (0.37, 0.43, 0.20),
    'PC05': (0.37, 0.48, 0.15),  # high LV loss — anomaly root cause
    'PC06': (0.38, 0.42, 0.20),
    'PC07': (0.36, 0.44, 0.20),
    'PC08': (0.34, 0.41, 0.25),
}

# Incident share by PC
PC_INCIDENT_SHARE = {
    'PC01': 0.18, 'PC02': 0.10, 'PC03': 0.15, 'PC04': 0.12,
    'PC05': 0.16, 'PC06': 0.13, 'PC07': 0.10, 'PC08': 0.06,
}

# Operating cost base per PC per month (million VND) — 8 categories
# (sửa chữa thường xuyên, sửa chữa lớn, nhân công, khấu hao, khắc phục thiên tai, vật tư, điện tự dùng, khác)
PC_COST_BASE = {
    'PC01': (12000, 7000, 18000, 8000, 3000, 2500, 800, 700),
    'PC02': (9000, 5500, 13000, 6000, 2000, 1800, 600, 500),
    'PC03': (15000, 10000, 25000, 12000, 4000, 3500, 1200, 1000),
    'PC04': (10000, 6000, 14500, 7000, 2500, 2000, 700, 600),
    'PC05': (12000, 7500, 18000, 8500, 3000, 2500, 900, 700),
    'PC06': (11000, 6500, 15500, 7500, 2500, 2200, 750, 650),
    'PC07': (9500, 5500, 13000, 6500, 2000, 1800, 650, 550),
    'PC08': (5000, 3000, 7000, 3500, 1000, 1000, 350, 300),
}
COST_CATEGORIES = [
    'Sửa chữa thường xuyên', 'Sửa chữa lớn', 'Nhân công', 'Khấu hao',
    'Khắc phục thiên tai', 'Vật tư', 'Điện tự dùng', 'Khác'
]

# Manufacturers for substations
MANUFACTURERS = ['ABB', 'Siemens', 'Schneider Electric', 'Thibidi', 'EEMC',
                 'Đông Anh', 'BTH', 'Hanaka', 'Mitsubishi', 'LS Electric']

SUBSTATION_TYPES = ['Trạm treo', 'Trạm giàn', 'Trạm hợp bộ']
CAPACITIES_KVA = [50, 75, 100, 160, 250, 320, 400, 500, 630, 750, 1000]

# ─── HELPER FUNCTIONS ────────────────────────────────────────────────────

def noise(low=0.95, high=1.05):
    return random.uniform(low, high)

def clamp(val, lo, hi):
    return max(lo, min(hi, val))

def is_year2(dt):
    """Is this date in Year 2 (Oct 2024 → Sep 2025)?"""
    return dt >= date(2024, 10, 1)

def yoy_factor(dt, base_growth):
    """Return YoY multiplier: Year1=1.0, Year2=base_growth"""
    return base_growth if is_year2(dt) else 1.0

def month_index(dt):
    """0-based index in MONTHS_24"""
    for i, m in enumerate(MONTHS_24):
        if m == dt:
            return i
    return -1

# ─── DATABASE OPERATIONS ─────────────────────────────────────────────────

def get_conn():
    return mysql.connector.connect(**DB_CONFIG)

def execute_many(conn, sql, data):
    cur = conn.cursor()
    cur.executemany(sql, data)
    conn.commit()
    cur.close()

def execute_one(conn, sql, data=None):
    cur = conn.cursor()
    cur.execute(sql, data)
    conn.commit()
    cur.close()

def truncate_facts(conn):
    """Truncate fact tables for re-generation"""
    cur = conn.cursor()
    cur.execute("SET FOREIGN_KEY_CHECKS=0")
    for t in ['monthly_kpi_summary', 'power_loss_detail', 'grid_incidents',
              'investment_history', 'operating_costs']:
        cur.execute(f"TRUNCATE TABLE {t}")
    cur.execute("SET FOREIGN_KEY_CHECKS=1")
    conn.commit()
    cur.close()

# ═══════════════════════════════════════════════════════════════════════════
# PHASE B — MASTER DATA
# ═══════════════════════════════════════════════════════════════════════════

def populate_master_data(conn):
    print("─── Phase B: Master Data ───")

    # 1. power_companies
    print("  [1/7] power_companies...")
    sql = """INSERT INTO power_companies
             (pc_id, pc_name, pc_short_name, provinces_covered, headquarters_city,
              num_employees, num_customers, total_line_length_km, num_substations_110kv,
              num_distribution_substations, is_joint_stock, established_date, notes)
             VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    execute_many(conn, sql, POWER_COMPANIES)

    # 2. provinces
    print("  [2/7] provinces...")
    sql = """INSERT INTO provinces
             (province_id, province_name, pc_id, region, area_km2, population,
              num_districts, terrain_type, storm_risk_level)
             VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    execute_many(conn, sql, PROVINCES)

    # 3. districts
    print("  [3/7] districts...")
    sql = """INSERT INTO districts
             (district_id, district_name, province_id, pc_id, district_type,
              area_km2, num_customers, is_urban)
             VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""
    execute_many(conn, sql, DISTRICTS)

    # 4. customer_segments
    print("  [4/7] customer_segments...")
    seg_data = []
    pc_customers = {pc[0]: pc[5+1] for pc in POWER_COMPANIES}  # num_customers
    for pc_id in [pc[0] for pc in POWER_COMPANIES]:
        total_cust = pc_customers[pc_id]
        overrides = SEGMENT_OVERRIDES.get(pc_id, {})
        for seg_name, default_prop, avg_price in SEGMENT_TEMPLATES:
            prop = overrides.get(seg_name, default_prop) + random.uniform(-1.0, 1.0)
            num_cust = int(total_cust * prop / 100)
            price = avg_price + random.uniform(-50, 50)
            seg_data.append((pc_id, seg_name, num_cust, round(prop, 2), round(price, 2)))
    sql = """INSERT INTO customer_segments (pc_id, segment_name, num_customers, proportion_pct, avg_price_vnd_per_kwh)
             VALUES (%s,%s,%s,%s,%s)"""
    execute_many(conn, sql, seg_data)

    # 5. loss_targets
    print("  [5/7] loss_targets...")
    lt_data = []
    for pc_id, y1_loss, y2_loss, y1_saidi, y2_saidi, saifi in LOSS_TARGETS_DATA:
        lt_data.append((pc_id, YEAR1, y1_loss, y1_saidi, saifi))
        lt_data.append((pc_id, YEAR2, y2_loss, y2_saidi, saifi - 0.2))
    sql = """INSERT INTO loss_targets (pc_id, year, target_loss_rate_pct, target_saidi_minutes, target_saifi_times)
             VALUES (%s,%s,%s,%s,%s)"""
    execute_many(conn, sql, lt_data)

    # 6. weather_events
    print("  [6/7] weather_events...")
    we_data = []
    for ev in WEATHER_EVENTS:
        we_data.append((ev[0], ev[1], ev[2], ev[3], ev[4], ev[5], ev[6], ev[7], ev[8], ev[9]))
    sql = """INSERT INTO weather_events
             (event_id, event_name, event_type, start_date, end_date, severity,
              affected_provinces, max_wind_speed_kmh, rainfall_mm, notes)
             VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    execute_many(conn, sql, we_data)

    # 7. substations + grid_assets
    print("  [7/7] substations + grid_assets...")
    generate_substations(conn)
    generate_grid_assets(conn)

    print("  Master data complete.")


def generate_substations(conn):
    """Generate ~800 substations with anomaly seeding for PC05 Bình Định districts."""
    district_ids = [d[0] for d in DISTRICTS]
    district_pc = {d[0]: d[3] for d in DISTRICTS}
    district_cust = {d[0]: d[6] for d in DISTRICTS}

    # Anomaly districts (Bình Định in PC05)
    anomaly_districts = {'D0501', 'D0502', 'D0503', 'D0504'}

    # Allocate substations proportional to customers
    total_cust = sum(district_cust.values())
    subs_data = []
    sub_counter = 0

    # 20 substations 110kV — spread across PCs
    pcs_110kv = {'PC01': 3, 'PC02': 2, 'PC03': 5, 'PC04': 2, 'PC05': 3, 'PC06': 2, 'PC07': 2, 'PC08': 1}
    pc_districts = {}
    for d in DISTRICTS:
        pc_districts.setdefault(d[3], []).append(d[0])

    for pc_id, count in pcs_110kv.items():
        dists = pc_districts[pc_id]
        for i in range(count):
            sub_counter += 1
            did = dists[i % len(dists)]
            sid = f"S110_{sub_counter:03d}"
            year = random.randint(2005, 2020)
            cap = random.choice([25000, 40000, 63000])
            load = round(random.uniform(55, 78), 2)
            cond = 'Tốt' if year >= 2015 else ('Trung bình' if year >= 2008 else 'Kém')
            mfr = random.choice(MANUFACTURERS[:5])
            maint = date(2025, random.randint(1, 9), random.randint(1, 28))
            subs_data.append((sid, f'Trạm 110kV {did}', pc_id, did, '110kV', 'Trạm 110kV',
                              cap, year, mfr, load, cond, maint))

    # ~780 distribution substations
    target_dist_subs = 780
    for did in district_ids:
        pc_id = district_pc[did]
        cust = district_cust[did]
        n_subs = max(5, int(target_dist_subs * cust / total_cust))
        is_anomaly = did in anomaly_districts

        for i in range(n_subs):
            sub_counter += 1
            sid = f"S{did[1:]}_{i+1:03d}"

            if is_anomaly and random.random() < 0.47:
                # Anomaly: old, overloaded MBA
                year = random.randint(1995, 2009)
                load = round(random.uniform(85, 105), 2)
                cond = random.choice(['Kém', 'Cần thay thế'])
            else:
                year = random.randint(2000, 2024)
                if year >= 2018:
                    load = round(random.uniform(35, 65), 2)
                    cond = 'Tốt'
                elif year >= 2010:
                    load = round(random.uniform(50, 80), 2)
                    cond = random.choice(['Tốt', 'Trung bình'])
                else:
                    load = round(random.uniform(60, 88), 2)
                    cond = random.choice(['Trung bình', 'Kém'])

            cap = random.choice(CAPACITIES_KVA)
            stype = random.choice(SUBSTATION_TYPES)
            mfr = random.choice(MANUFACTURERS)
            maint_m = random.randint(1, 9)
            maint = date(2025, maint_m, random.randint(1, 28))
            if maint_m == 2 and maint.day > 28:
                maint = date(2025, 2, 28)

            subs_data.append((sid, f'TBA {stype} {did}-{i+1}', pc_id, did,
                              '0.4kV', stype, cap, year, mfr, load, cond, maint))

    sql = """INSERT INTO substations
             (substation_id, substation_name, pc_id, district_id, voltage_level,
              substation_type, capacity_kva, installed_year, manufacturer,
              load_rate_pct, condition_rating, last_maintenance_date)
             VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    execute_many(conn, sql, subs_data)
    print(f"    → {len(subs_data)} substations inserted")


def generate_grid_assets(conn):
    """Generate ~600 grid assets."""
    district_ids = [d[0] for d in DISTRICTS]
    district_pc = {d[0]: d[3] for d in DISTRICTS}
    pc_districts = {}
    for d in DISTRICTS:
        pc_districts.setdefault(d[3], []).append(d[0])

    assets = []
    aid = 0

    # MBA phân phối: ~300
    for pc_id, dists in pc_districts.items():
        n = 38 if pc_id == 'PC03' else (18 if pc_id == 'PC08' else 30)
        for i in range(n):
            aid += 1
            did = random.choice(dists)
            year = random.randint(1998, 2024)
            cap = random.choice(CAPACITIES_KVA)
            if year >= 2015:
                cond = 'Tốt'
            elif year >= 2005:
                cond = random.choice(['Tốt', 'Trung bình'])
            else:
                cond = random.choice(['Trung bình', 'Kém'])
            cost = round(cap * random.uniform(0.8, 1.5), 1)
            assets.append((f'A{aid:04d}', 'MBA phân phối', pc_id, did, year, cap, 'kVA', cond, cost))

    # Recloser: ~80 (PC03 most)
    for pc_id, dists in pc_districts.items():
        n = 18 if pc_id == 'PC03' else (5 if pc_id == 'PC08' else 8)
        for i in range(n):
            aid += 1
            did = random.choice(dists)
            year = random.randint(2010, 2024)
            cond = 'Tốt' if year >= 2018 else 'Trung bình'
            cost = round(random.uniform(150, 350), 1)
            assets.append((f'A{aid:04d}', 'Recloser', pc_id, did, year, 1, 'bộ', cond, cost))

    # Đường dây trung thế: ~120 segments
    for pc_id, dists in pc_districts.items():
        n = 20 if pc_id == 'PC03' else (8 if pc_id == 'PC08' else 13)
        for i in range(n):
            aid += 1
            did = random.choice(dists)
            year = random.randint(2000, 2023)
            length = round(random.uniform(3, 25), 2)
            cond = 'Tốt' if year >= 2015 else ('Trung bình' if year >= 2005 else 'Kém')
            cost = round(length * random.uniform(200, 500), 1)
            assets.append((f'A{aid:04d}', 'Đường dây trung thế', pc_id, did, year, length, 'km', cond, cost))

    # Đường dây hạ thế: ~100 segments
    for pc_id, dists in pc_districts.items():
        n = 16 if pc_id == 'PC03' else (6 if pc_id == 'PC08' else 11)
        for i in range(n):
            aid += 1
            did = random.choice(dists)
            year = random.randint(2002, 2024)
            length = round(random.uniform(1, 12), 2)
            cond = 'Tốt' if year >= 2016 else ('Trung bình' if year >= 2008 else 'Kém')
            cost = round(length * random.uniform(100, 250), 1)
            assets.append((f'A{aid:04d}', 'Đường dây hạ thế', pc_id, did, year, length, 'km', cond, cost))

    # Tụ bù: ~40
    for pc_id, dists in pc_districts.items():
        n = 8 if pc_id == 'PC03' else (3 if pc_id == 'PC08' else 5)
        for i in range(n):
            aid += 1
            did = random.choice(dists)
            year = random.randint(2008, 2024)
            cap = random.choice([100, 200, 300, 450, 600])
            cond = 'Tốt' if year >= 2018 else 'Trung bình'
            cost = round(cap * random.uniform(0.3, 0.6), 1)
            assets.append((f'A{aid:04d}', 'Tụ bù', pc_id, did, year, cap, 'kVAr', cond, cost))

    sql = """INSERT INTO grid_assets
             (asset_id, asset_type, pc_id, district_id, installed_year,
              capacity_or_length, unit, condition_rating, replacement_cost_million_vnd)
             VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    execute_many(conn, sql, assets)
    print(f"    → {len(assets)} grid_assets inserted")


# ═══════════════════════════════════════════════════════════════════════════
# PHASE C — TRANSACTION DATA
# ═══════════════════════════════════════════════════════════════════════════

def populate_transaction_data(conn):
    print("─── Phase C: Transaction Data ───")
    truncate_facts(conn)

    generate_monthly_kpi(conn)
    generate_power_loss_detail(conn)
    generate_grid_incidents(conn)
    generate_investment_history(conn)
    generate_operating_costs(conn)

    print("  Transaction data complete.")


def generate_monthly_kpi(conn):
    """Generate 192 monthly KPI records (8 PC × 24 months) with anomalies."""
    print("  [1/5] monthly_kpi_summary...")

    rows = []
    for pc_id, (base_power, base_rev, base_loss, base_saidi,
                base_saifi, base_maifi, base_peak, base_emp, base_coll) in PC_BASE_KPI.items():
        mv_r, lv_r, comm_r = LOSS_BREAKDOWN[pc_id]

        for i, dt in enumerate(MONTHS_24):
            m = dt.month
            yr2 = is_year2(dt)

            # Base × seasonality × YoY × noise
            power_gwh = base_power * POWER_SEASON[m] * (YOY_POWER if yr2 else 1.0) * noise(0.96, 1.04)
            revenue = base_rev * POWER_SEASON[m] * (YOY_REVENUE if yr2 else 1.0) * noise(0.96, 1.04)

            # Loss rate with improvement trend
            loss_pct = base_loss * LOSS_SEASON[m] * (YOY_LOSS_IMPROVE if yr2 else 1.0) * noise(0.97, 1.03)

            # ANOMALY: PC05 Gia Lai — upward loss trend last 6 months
            if pc_id == 'PC05' and i >= 18:  # months 18..23 = Apr 2025..Sep 2025
                anomaly_targets = {18: 4.20, 19: 4.35, 20: 4.48, 21: 4.55, 22: 4.70, 23: 4.82}
                loss_pct = anomaly_targets[i] * LOSS_SEASON[m] / LOSS_SEASON[m]  # keep the absolute value
                loss_pct = anomaly_targets[i] * noise(0.995, 1.005)

            # ANOMALY: PC06 Đắk Lắk — slight upward 3 months
            if pc_id == 'PC06' and i >= 21:  # Jul-Sep 2025
                anomaly_losses = {21: 3.70, 22: 3.74, 23: 3.78}
                loss_pct = anomaly_losses[i] * noise(0.998, 1.002)

            # Loss breakdown
            tech_mv = loss_pct * mv_r * noise(0.95, 1.05)
            tech_lv = loss_pct * lv_r * noise(0.95, 1.05)
            comm_l = loss_pct - tech_mv - tech_lv
            if comm_l < 0:
                comm_l = loss_pct * comm_r
                tech_mv = loss_pct * mv_r
                tech_lv = loss_pct - tech_mv - comm_l

            # Power received from loss rate
            power_recv = power_gwh / (1 - loss_pct / 100)

            # Avg selling price
            avg_price = revenue * 1000 / power_gwh  # billion VND → million VND → VND/kWh (*1000/GWh)
            avg_price = (revenue * 1e9) / (power_gwh * 1e6)  # VND/kWh

            # SAIDI with seasonality
            saidi = base_saidi * SAIDI_SEASON[m] * noise(0.90, 1.10)
            # ANOMALY: PC06 SAIDI +18% YoY in Sep 2025
            if pc_id == 'PC06' and dt == date(2025, 9, 1):
                # Find Sep 2024 SAIDI baseline
                sep24_saidi = base_saidi * SAIDI_SEASON[9] * 1.0  # year1 base
                saidi = sep24_saidi * 1.18

            saifi = base_saifi * SAIDI_SEASON[m] * noise(0.90, 1.10)
            maifi = base_maifi * SAIDI_SEASON[m] * noise(0.85, 1.15)

            # Incidents
            base_inc_pc = 80 * PC_INCIDENT_SHARE[pc_id]
            inc_total = int(base_inc_pc * INCIDENTS_SEASON[m] * noise(0.85, 1.15))
            inc_110 = max(0, int(inc_total * 0.05))
            inc_mv = int(inc_total * 0.65)

            # Peak load
            peak = base_peak * POWER_SEASON[m] * noise(0.95, 1.05) * (1.04 if yr2 else 1.0)

            # Overloaded substations
            n_overloaded = int(base_peak / 50 * POWER_SEASON[m] * noise(0.8, 1.2))

            # Collection rate
            coll = base_coll * noise(0.9995, 1.0005)
            coll = min(100.0, coll)

            # Employees (stable with slight growth)
            emp = base_emp + (50 if yr2 else 0) + random.randint(-10, 10)

            # Productivity
            prod = power_gwh * 1000000 / emp  # kWh/employee

            rows.append((
                pc_id, dt,
                round(power_recv, 3), round(power_gwh, 3), round(revenue, 2), round(avg_price, 2),
                round(loss_pct, 2), round(tech_mv, 2), round(tech_lv, 2), round(comm_l, 2),
                round(saidi, 2), round(saifi, 2), round(maifi, 2),
                inc_110, inc_mv, inc_total,
                round(peak, 1), n_overloaded, round(coll, 2),
                emp, round(prod, 1)
            ))

    sql = """INSERT INTO monthly_kpi_summary
             (pc_id, report_month, power_received_gwh, commercial_power_gwh,
              revenue_billion_vnd, avg_selling_price_vnd, loss_rate_pct,
              technical_loss_mv_pct, technical_loss_lv_pct, commercial_loss_pct,
              saidi_minutes, saifi_times, maifi_times,
              num_incidents_110kv, num_incidents_medium_voltage, num_incidents_total,
              peak_load_mw, num_overloaded_substations, collection_rate_pct,
              num_employees, productivity_kwh_per_employee)
             VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    execute_many(conn, sql, rows)
    print(f"    → {len(rows)} monthly_kpi records inserted")


def generate_power_loss_detail(conn):
    """Generate power loss detail per district × month."""
    print("  [2/5] power_loss_detail...")

    # Get PC base values & district list
    pc_districts_map = {}
    for d in DISTRICTS:
        pc_districts_map.setdefault(d[3], []).append(d)

    anomaly_districts = {'D0501', 'D0502', 'D0503', 'D0504'}
    anomaly_lv_targets = {
        'D0501': 3.5, 'D0502': 3.8, 'D0503': 3.1, 'D0504': 3.3
    }

    rows = []
    for pc_id, districts_list in pc_districts_map.items():
        base_loss = PC_BASE_KPI[pc_id][2]
        mv_r, lv_r, comm_r = LOSS_BREAKDOWN[pc_id]
        base_power_gwh = PC_BASE_KPI[pc_id][0]

        # Distribute power among districts proportional to customers
        total_cust = sum(d[6] for d in districts_list)

        for d in districts_list:
            did = d[0]
            cust_share = d[6] / total_cust
            is_anomaly = did in anomaly_districts

            for i, dt in enumerate(MONTHS_24):
                m = dt.month
                yr2 = is_year2(dt)

                # District power (MWh)
                district_power_gwh = base_power_gwh * cust_share * POWER_SEASON[m] * (YOY_POWER if yr2 else 1.0) * noise(0.93, 1.07)
                power_recv_mwh = district_power_gwh * 1000  # GWh → MWh

                # Loss rates at district level
                district_base_loss = base_loss + random.uniform(-0.3, 0.3)

                if is_anomaly and i >= 18:
                    # Anomaly: high LV loss in last 6 months, gradually increasing
                    target_lv = anomaly_lv_targets[did]
                    # Gradual: from 2.5% at month 18 to target at month 23
                    progress = (i - 18) / 5.0
                    tech_lv = 2.5 + (target_lv - 2.5) * progress * noise(0.95, 1.05)
                    tech_mv = base_loss * mv_r * LOSS_SEASON[m] * noise(0.95, 1.05)
                    comm = base_loss * comm_r * noise(0.90, 1.10)
                    total_loss = tech_mv + tech_lv + comm
                elif is_anomaly:
                    # Normal period for anomaly districts — slightly elevated
                    tech_lv = base_loss * lv_r * LOSS_SEASON[m] * noise(0.95, 1.05) * 1.1
                    tech_mv = base_loss * mv_r * LOSS_SEASON[m] * noise(0.95, 1.05)
                    comm = base_loss * comm_r * noise(0.90, 1.10)
                    total_loss = tech_mv + tech_lv + comm
                else:
                    tech_mv = district_base_loss * mv_r * LOSS_SEASON[m] * noise(0.95, 1.05)
                    tech_lv = district_base_loss * lv_r * LOSS_SEASON[m] * noise(0.95, 1.05)
                    comm = district_base_loss * comm_r * noise(0.90, 1.10)
                    total_loss = tech_mv + tech_lv + comm

                # YoY improvement for non-anomaly
                if not is_anomaly and yr2:
                    total_loss *= YOY_LOSS_IMPROVE
                    tech_mv *= YOY_LOSS_IMPROVE
                    tech_lv *= YOY_LOSS_IMPROVE
                    comm *= YOY_LOSS_IMPROVE

                commercial_mwh = power_recv_mwh * (1 - total_loss / 100)
                n_overloaded = random.randint(0, 3) if not is_anomaly else random.randint(2, 8)

                rows.append((
                    did, pc_id, dt,
                    round(power_recv_mwh, 2), round(commercial_mwh, 2),
                    round(total_loss, 2), round(tech_mv, 2), round(tech_lv, 2), round(comm, 2),
                    n_overloaded
                ))

    sql = """INSERT INTO power_loss_detail
             (district_id, pc_id, report_month, power_received_mwh, commercial_power_mwh,
              total_loss_rate_pct, technical_loss_mv_pct, technical_loss_lv_pct,
              commercial_loss_pct, num_substations_overloaded)
             VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    execute_many(conn, sql, rows)
    print(f"    → {len(rows)} power_loss_detail records inserted")


def generate_grid_incidents(conn):
    """Generate ~2500 grid incidents with Scenario 3 anomaly."""
    print("  [3/5] grid_incidents...")

    pc_districts_map = {}
    for d in DISTRICTS:
        pc_districts_map.setdefault(d[3], []).append(d[0])

    cause_cats_normal = [
        ('Bão-Áp thấp', 0.25), ('Cây đổ', 0.22), ('Sét', 0.12),
        ('Ngập', 0.08), ('Thiết bị hỏng', 0.18), ('Quá tải', 0.08),
        ('Thi công bên thứ 3', 0.05), ('Khác', 0.02)
    ]
    cause_cats_storm = [
        ('Bão-Áp thấp', 0.42), ('Cây đổ', 0.18), ('Sét', 0.08),
        ('Ngập', 0.15), ('Thiết bị hỏng', 0.10), ('Quá tải', 0.03),
        ('Thi công bên thứ 3', 0.02), ('Khác', 0.02)
    ]

    cause_details = {
        'Bão-Áp thấp': ['Gió mạnh làm đứt dây dẫn', 'Cột điện bị gãy do bão', 'Mưa bão gây chập mạch'],
        'Cây đổ': ['Cây xanh đổ vào đường dây', 'Cành cây chạm dây trung thế', 'Cây rừng gãy đè lên trụ'],
        'Sét': ['Sét đánh trực tiếp vào đường dây', 'Sét lan truyền gây hư MBA', 'Quá điện áp do sét'],
        'Ngập': ['Ngập nước trạm biến áp', 'Nước tràn vào tủ điện hạ thế', 'Đường dây ngầm ngập nước'],
        'Thiết bị hỏng': ['MBA cháy do quá tải', 'Sứ cách điện bị vỡ', 'Dao cách ly hỏng', 'Cáp ngầm bị đứt'],
        'Quá tải': ['MBA quá tải gây cháy cuộn dây', 'Đường dây quá tải gây võng dây', 'Tải đỉnh vượt công suất MBA'],
        'Thi công bên thứ 3': ['Xe cẩu chạm đường dây', 'Đào đường gây đứt cáp ngầm', 'Xe tải va vào cột điện'],
        'Khác': ['Động vật gây chập mạch', 'Diều vướng đường dây', 'Nguyên nhân chưa xác định'],
    }

    equipment_damaged_options = {
        'Bão-Áp thấp': ['Cột điện BTLT, dây AC-70', 'Cột thép, sứ cách điện', 'MBA 100kVA, cột bê tông'],
        'Cây đổ': ['Dây dẫn AC-50, sứ đứng', 'Xà néo, dây nhôm'],
        'Sét': ['Chống sét van, MBA 160kVA', 'Sứ chuỗi, dây chống sét'],
        'Ngập': ['Tủ điện hạ thế, aptomat', 'MBA trạm giàn, cáp hạ thế'],
        'Thiết bị hỏng': ['MBA 250kVA', 'Dao cách ly 24kV', 'Recloser', 'Cáp ngầm 24kV'],
        'Quá tải': ['MBA 100kVA (cháy)', 'Dây dẫn AC-35 (võng)', 'Cầu chì tự rơi'],
        'Thi công bên thứ 3': ['Cột bê tông ly tâm', 'Cáp ngầm 22kV', 'Dây dẫn AC-70'],
        'Khác': ['Sứ cách điện', 'Dây dẫn bọc'],
    }

    voltage_levels = ['Trung thế', 'Hạ thế']
    voltage_weights = [0.65, 0.35]

    # Build weather event lookup: event_id → (start_date, end_date, affected_provinces, severity)
    we_lookup = {}
    for ev in WEATHER_EVENTS:
        we_lookup[ev[0]] = {
            'start': date.fromisoformat(ev[3]),
            'end': date.fromisoformat(ev[4]) if ev[4] else date.fromisoformat(ev[3]),
            'provinces': ev[6].split(','),
            'severity': ev[5],
        }

    rows = []
    base_incidents_per_month = 105

    for month_dt in MONTHS_24:
        m = month_dt.month
        y = month_dt.year
        yr2 = is_year2(month_dt)
        is_storm_season = m in [9, 10, 11]

        # Total incidents this month
        coeff = INCIDENTS_SEASON[m]
        total_this_month = int(base_incidents_per_month * coeff * noise(0.90, 1.10))

        # ANOMALY: Q3 2025 (Jul-Sep) = 287 total, Q3 2024 = 198 total
        # These are EXACT totals (not per-PC), so we set and skip per-PC distribution below
        q3_override = None
        if y == 2025 and m == 7:
            q3_override = 72
        elif y == 2025 and m == 8:
            q3_override = 78
        elif y == 2025 and m == 9:
            q3_override = 137  # 72+78+137 = 287
        elif y == 2024 and m == 7:
            q3_override = 55
        elif y == 2024 and m == 8:
            q3_override = 58
        elif y == 2024 and m == 9:
            q3_override = 85  # 55+58+85 = 198
        if q3_override is not None:
            total_this_month = q3_override

        # Distribute among PCs
        pc_ids_list = list(PC_INCIDENT_SHARE.keys())
        if q3_override is not None:
            # Precise distribution for Q3 anomaly months
            pc_counts = {}
            is_sep2025 = (y == 2025 and m == 9)
            if is_sep2025:
                # PC01 gets exactly 89; distribute remaining 48 among other PCs
                pc_counts['PC01'] = 89
                remaining = total_this_month - 89
                other_pcs = [p for p in pc_ids_list if p != 'PC01']
                other_total_share = sum(PC_INCIDENT_SHARE[p] for p in other_pcs)
                allocated = 0
                for j, pc in enumerate(other_pcs):
                    if j == len(other_pcs) - 1:
                        pc_counts[pc] = remaining - allocated
                    else:
                        n = max(1, int(remaining * PC_INCIDENT_SHARE[pc] / other_total_share))
                        pc_counts[pc] = n
                        allocated += n
            else:
                # Other Q3 months — proportional distribution with exact total
                allocated = 0
                for j, pc in enumerate(pc_ids_list):
                    if j == len(pc_ids_list) - 1:
                        pc_counts[pc] = total_this_month - allocated
                    else:
                        n = max(1, int(total_this_month * PC_INCIDENT_SHARE[pc]))
                        pc_counts[pc] = n
                        allocated += n
        else:
            pc_counts = {}
            for pc in pc_ids_list:
                pc_counts[pc] = max(1, int(total_this_month * PC_INCIDENT_SHARE[pc] * noise(0.85, 1.15)))

        for pc_id in pc_ids_list:
            n_incidents = pc_counts[pc_id]
            dists = pc_districts_map[pc_id]

            cause_list = cause_cats_storm if is_storm_season else cause_cats_normal

            for _ in range(n_incidents):
                # Pick cause
                r = random.random()
                cumul = 0
                cause = cause_list[-1][0]
                for c, w in cause_list:
                    cumul += w
                    if r <= cumul:
                        cause = c
                        break

                # Date within month
                days_in_month = 28 if m == 2 else (30 if m in [4, 6, 9, 11] else 31)

                # ANOMALY: PC01 Sep 2025 — cluster 65/89 in 14-day window
                if pc_id == 'PC01' and y == 2025 and m == 9:
                    if random.random() < 65/89:
                        day = random.randint(14, 27)  # Sep 14-27
                    else:
                        day = random.randint(1, 13)
                else:
                    day = random.randint(1, days_in_month)

                inc_date = date(y, m, min(day, days_in_month))
                inc_time = dtime(random.randint(0, 23), random.randint(0, 59))

                # Voltage level
                vl = random.choices(voltage_levels, voltage_weights)[0]
                if cause in ('Bão-Áp thấp', 'Cây đổ', 'Sét'):
                    vl = 'Trung thế'  # mostly medium voltage

                # District
                did = random.choice(dists)

                # Affected customers
                affected = int(random.lognormvariate(math.log(500), 0.8))
                affected = clamp(affected, 50, 25000)

                # Duration and restoration
                if cause in ('Bão-Áp thấp', 'Ngập'):
                    outage = round(random.lognormvariate(math.log(10), 0.5), 2)
                    restoration = round(outage * random.uniform(0.85, 1.05), 2)
                elif cause == 'Thiết bị hỏng':
                    outage = round(random.lognormvariate(math.log(7), 0.5), 2)
                    restoration = round(outage * random.uniform(0.85, 1.05), 2)
                else:
                    outage = round(random.lognormvariate(math.log(5.5), 0.5), 2)
                    restoration = round(outage * random.uniform(0.80, 1.0), 2)

                outage = clamp(outage, 0.5, 48)
                restoration = clamp(restoration, 0.5, 48)

                # ANOMALY: Restoration time improvement Year 2
                # Year 1 avg ~8.5h, Year 2 avg ~6.6h → factor 0.776
                if yr2:
                    restoration *= 0.78
                    outage *= 0.80

                # PC03 (Đà Nẵng) fastest restoration — target ~4.2h avg in Q3
                if pc_id == 'PC03':
                    restoration *= 0.65
                    outage *= 0.68

                # Repair cost (million VND) — log-normal
                if cause in ('Bão-Áp thấp', 'Ngập'):
                    repair_cost = round(random.lognormvariate(math.log(120), 0.8), 1)
                else:
                    repair_cost = round(random.lognormvariate(math.log(50), 0.7), 1)
                repair_cost = clamp(repair_cost, 5, 2000)

                # ANOMALY: PC01 Q3 2025 — higher repair costs (total ~47,000 million = 47 tỷ)
                # PC01 Sep 2025 has 89 incidents → need avg ~380M each
                if pc_id == 'PC01' and y == 2025 and m == 9:
                    repair_cost = round(random.lognormvariate(math.log(380), 0.5), 1)
                    repair_cost = clamp(repair_cost, 60, 2500)
                elif pc_id == 'PC01' and y == 2025 and m in [7, 8]:
                    repair_cost *= 1.8
                    repair_cost = clamp(repair_cost, 30, 2000)

                # Weather event linkage
                weather_eid = None
                if cause in ('Bão-Áp thấp', 'Ngập', 'Cây đổ') and is_storm_season:
                    # Find matching weather event
                    for eid, we in we_lookup.items():
                        if we['start'] <= inc_date <= we['end'] + timedelta(days=2):
                            weather_eid = eid
                            break

                detail = random.choice(cause_details[cause])
                equip = random.choice(equipment_damaged_options[cause])

                rows.append((
                    pc_id, did, inc_date, inc_time, vl, cause, detail,
                    affected, round(outage, 2), round(restoration, 2),
                    round(repair_cost, 1), weather_eid, equip
                ))

    sql = """INSERT INTO grid_incidents
             (pc_id, district_id, incident_date, incident_time, voltage_level,
              cause_category, cause_detail, affected_customers, outage_duration_hours,
              restoration_time_hours, repair_cost_million_vnd, weather_event_id,
              equipment_damaged)
             VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    execute_many(conn, sql, rows)
    print(f"    → {len(rows)} grid_incidents inserted")


def generate_investment_history(conn):
    """Generate ~70 investment projects."""
    print("  [4/5] investment_history...")

    pc_districts_map = {}
    for d in DISTRICTS:
        pc_districts_map.setdefault(d[3], []).append(d[0])

    project_types = [
        ('Cải tạo lưới trung thế', 15, 45, 0.10, 0.25, 8, 15),
        ('Cải tạo lưới hạ thế', 8, 25, 0.08, 0.20, 5, 12),
        ('Thay MBA', 3, 15, 0.05, 0.15, 3, 8),
        ('Lắp recloser', 2, 8, 0.02, 0.05, 10, 20),
        ('Xây TBA 110kV', 80, 200, 0.15, 0.40, 15, 25),
        ('Kéo dây mới', 5, 20, 0.05, 0.12, 5, 10),
    ]
    statuses = ['Hoàn thành', 'Hoàn thành', 'Hoàn thành', 'Đang triển khai', 'Chậm tiến độ']

    rows = []
    for pc_id, dists in pc_districts_map.items():
        n_projects = 10 if pc_id in ('PC03', 'PC05') else (5 if pc_id == 'PC08' else 8)
        for _ in range(n_projects):
            ptype, inv_lo, inv_hi, lr_lo, lr_hi, saidi_lo, saidi_hi = random.choice(project_types)
            did = random.choice(dists) if ptype != 'Xây TBA 110kV' else None
            start_y = random.randint(2022, 2025)
            status = random.choice(statuses)
            comp_y = start_y + random.randint(1, 2) if status == 'Hoàn thành' else None
            inv = round(random.uniform(inv_lo, inv_hi), 2)
            exp_loss = round(random.uniform(lr_lo, lr_hi), 2)
            act_loss = round(exp_loss * random.uniform(0.6, 1.1), 2) if status == 'Hoàn thành' else None
            exp_saidi = round(random.uniform(saidi_lo, saidi_hi), 2)

            district_name = ''
            if did:
                for dd in DISTRICTS:
                    if dd[0] == did:
                        district_name = dd[1]
                        break

            name = f"{ptype} {district_name}" if did else f"{ptype} toàn {pc_id}"

            rows.append((
                pc_id, did, name, ptype, start_y, comp_y, inv,
                exp_loss, act_loss, exp_saidi, status
            ))

    sql = """INSERT INTO investment_history
             (pc_id, district_id, project_name, project_type, start_year, completion_year,
              investment_billion_vnd, expected_loss_reduction_pct, actual_loss_reduction_pct,
              expected_saidi_reduction_pct, status)
             VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    execute_many(conn, sql, rows)
    print(f"    → {len(rows)} investment_history records inserted")


def generate_operating_costs(conn):
    """Generate operating costs: 8 PC × 24 months × 8 categories."""
    print("  [5/5] operating_costs...")

    rows = []
    for pc_id, cost_bases in PC_COST_BASE.items():
        for dt in MONTHS_24:
            m = dt.month
            yr2 = is_year2(dt)

            for j, cat in enumerate(COST_CATEGORIES):
                base = cost_bases[j]

                # Seasonality
                if cat == 'Khắc phục thiên tai':
                    amount = base * COST_DISASTER_SEASON[m] * noise(0.80, 1.20)
                    # ANOMALY: PC01 Sep 2025 — disaster cost spike
                    if pc_id == 'PC01' and dt.year == 2025 and m == 9:
                        amount = base * 12.0  # huge spike
                elif cat == 'Sửa chữa thường xuyên':
                    amount = base * POWER_SEASON[m] * noise(0.90, 1.10) * (1.05 if yr2 else 1.0)
                elif cat == 'Nhân công':
                    amount = base * noise(0.98, 1.02) * (1.08 if yr2 else 1.0)  # salary increase
                else:
                    amount = base * noise(0.92, 1.08) * (1.05 if yr2 else 1.0)

                note = None
                if cat == 'Khắc phục thiên tai' and m in [9, 10, 11] and amount > base * 2:
                    note = 'Chi phí tăng do mùa bão'

                rows.append((pc_id, dt, cat, round(amount, 1), note))

    sql = """INSERT INTO operating_costs (pc_id, report_month, cost_category, amount_million_vnd, notes)
             VALUES (%s,%s,%s,%s,%s)"""
    execute_many(conn, sql, rows)
    print(f"    → {len(rows)} operating_costs records inserted")


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

def print_master_summary(conn):
    """Print summary of master data for checkpoint 2."""
    cur = conn.cursor()
    tables = ['power_companies', 'provinces', 'districts', 'substations', 'grid_assets',
              'customer_segments', 'loss_targets', 'weather_events']
    print("\n═══ MASTER DATA SUMMARY ═══")
    for t in tables:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        count = cur.fetchone()[0]
        print(f"  {t}: {count} records")

    # Substations anomaly check
    cur.execute("""
        SELECT district_id, COUNT(*) AS total,
               SUM(CASE WHEN installed_year <= 2009 AND load_rate_pct > 85 THEN 1 ELSE 0 END) AS old_overloaded
        FROM substations
        WHERE district_id IN ('D0501','D0502','D0503','D0504')
        GROUP BY district_id
    """)
    print("\n  Anomaly check — Bình Định substations (installed≤2009, load>85%):")
    for row in cur.fetchall():
        pct = row[2] / row[1] * 100 if row[1] > 0 else 0
        print(f"    {row[0]}: {row[2]}/{row[1]} = {pct:.0f}%")

    cur.close()


def print_transaction_summary(conn):
    """Print summary of transaction data."""
    cur = conn.cursor()
    print("\n═══ TRANSACTION DATA SUMMARY ═══")
    for t in ['monthly_kpi_summary', 'power_loss_detail', 'grid_incidents',
              'investment_history', 'operating_costs']:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        count = cur.fetchone()[0]
        print(f"  {t}: {count} records")
    cur.close()


if __name__ == '__main__':
    import sys
    phase = sys.argv[1] if len(sys.argv) > 1 else 'all'
    conn = get_conn()
    try:
        if phase in ('master', 'all'):
            populate_master_data(conn)
            print_master_summary(conn)
        if phase in ('transaction', 'all'):
            populate_transaction_data(conn)
            print_transaction_summary(conn)
    finally:
        conn.close()
    print("\nDone.")
