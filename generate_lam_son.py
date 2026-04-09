#!/usr/bin/env python3
"""
Lam Sơn Invest — Construction & Real Estate Demo Database Generator
Generates 18 months of data (10/2023 – 03/2025) for construction_re_demo database.
3 layers: Base volume → Seasonality → Anomaly injection

Output:
  1. Direct MySQL population
  2. SQL files in lam_son_sql/
"""

import random
import math
import os
from datetime import date, timedelta
from collections import defaultdict
from decimal import Decimal

import mysql.connector

random.seed(42)

# =============================================================================
# CONFIG
# =============================================================================
DB_CONFIG = dict(host='localhost', port=3306, user='root', password='root', database='construction_re_demo')
SQL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lam_son_sql')

MONTHS = []
for y in (2023, 2024, 2025):
    for m in range(1, 13):
        d = date(y, m, 1)
        if date(2023, 10, 1) <= d <= date(2025, 3, 1):
            MONTHS.append(d)
# 18 months: 2023-10 to 2025-03

CURRENT_DATE = date(2025, 3, 31)

# =============================================================================
# MASTER DATA DEFINITIONS
# =============================================================================

REGIONS = [
    (1, 'TP Thái Bình', 'thanh_pho', 'Trung tâm tỉnh, thị trường BĐS chính'),
    (2, 'Huyện Đông Hưng', 'huyen', 'Nơi có cụm CN Lam Sơn, nhiều dự án'),
    (3, 'Huyện Quỳnh Phụ', 'huyen', 'Dự án dân dụng, gần QL10'),
    (4, 'Huyện Thái Thụy', 'huyen', 'Ven biển, có KCN'),
    (5, 'Huyện Tiền Hải', 'huyen', 'Ven biển, KCN Tiền Hải'),
    (6, 'Huyện Vũ Thư', 'huyen', 'Nội đồng, nhiều cầu đường'),
    (7, 'Huyện Kiến Xương', 'huyen', 'Nông nghiệp'),
    (8, 'Huyện Hưng Hà', 'huyen', 'Nội đồng'),
]

COST_CATEGORIES = [
    (1, 'Nguyên vật liệu', 'Materials', 45.00, 55.00),
    (2, 'Nhân công', 'Labor', 20.00, 25.00),
    (3, 'Thầu phụ', 'Subcontractors', 15.00, 20.00),
    (4, 'Máy móc thiết bị', 'Equipment', 5.00, 10.00),
    (5, 'Quản lý & chi phí chung', 'Management & Overhead', 3.00, 5.00),
]

MATERIALS = [
    (1, 'Thép cuộn CB300', 'kg', 14500, 'thep'),
    (2, 'Thép hình H200', 'kg', 16800, 'thep'),
    (3, 'Xi măng PCB40 Vissai', 'tấn', 1650000, 'xi_mang'),
    (4, 'Cát san lấp', 'm³', 180000, 'cat'),
    (5, 'Cát xây dựng', 'm³', 350000, 'cat'),
    (6, 'Đá 1×2', 'm³', 320000, 'da'),
    (7, 'Gạch xây Đồng Nai', 'viên', 1200, 'gach'),
    (8, 'Bê tông thương phẩm M250', 'm³', 1250000, 'be_tong'),
]

SUBCONTRACTORS = [
    (1, 'Công ty TNHH XD Hải Minh Hưng', 'Thi công đường, cầu', 4.2, '0227.3851.234', 'Số 15 Lý Thường Kiệt, TP Thái Bình'),
    (2, 'Công ty CP Phú Thăng Long', 'Xây dựng dân dụng', 4.0, '0227.3862.456', 'Số 88 Trần Hưng Đạo, TP Thái Bình'),
    (3, 'Công ty TNHH Cơ khí Thái Bình', 'Kết cấu thép', 3.8, '0227.3845.789', 'KCN Nguyễn Đức Cảnh, Thái Bình'),
    (4, 'HTX Xây dựng Đông La', 'Nhân công & phụ trợ', 3.5, '0227.3871.012', 'Xã Đông La, Huyện Đông Hưng'),
    (5, 'Công ty CP Điện nước Thái Bình', 'M&E (cơ điện)', 4.1, '0227.3853.345', 'Số 22 Hai Bà Trưng, TP Thái Bình'),
    (6, 'Công ty TNHH Gia cường Nền móng Bắc Bộ', 'Xử lý nền đất yếu', 4.3, '024.3765.6789', 'Số 120 Nguyễn Trãi, Hà Đông, Hà Nội'),
]

COUNTERPARTIES = [
    (1, 'BQL DA XDCSHT tỉnh Thái Bình', 'chu_dau_tu', '1000123456', 'Số 10 Lê Lợi, TP Thái Bình', 'Ông Trần Văn Hùng', '0227.3831.100'),
    (2, 'Sở GD&ĐT Thái Bình', 'chu_dau_tu', '1000234567', 'Số 5 Lý Bôn, TP Thái Bình', 'Bà Nguyễn Thị Lan', '0227.3831.200'),
    (3, 'BQL DA huyện Đông Hưng', 'chu_dau_tu', '1000345678', 'TT Đông Hưng, Đông Hưng', 'Ông Phạm Đức Minh', '0227.3871.300'),
    (4, 'BQL DA NNPTNT tỉnh Thái Bình', 'chu_dau_tu', '1000456789', 'Số 8 Trần Phú, TP Thái Bình', 'Ông Lê Quốc Tuấn', '0227.3831.400'),
    (5, 'BQL KCN tỉnh Thái Bình', 'chu_dau_tu', '1000567890', 'Số 12 Quang Trung, TP Thái Bình', 'Ông Đỗ Văn Thắng', '0227.3831.500'),
    (6, 'Công ty TNHH XD Hải Minh Hưng', 'nha_thau_phu', '1001061001', 'Số 15 Lý Thường Kiệt, TP Thái Bình', 'Ông Bùi Văn Hải', '0227.3851.234'),
    (7, 'Công ty CP VLXD Đông Á', 'nha_cung_cap', '1001062002', 'KCN Tiền Hải, Tiền Hải', 'Ông Nguyễn Đức Anh', '0227.3892.567'),
    (8, 'Công ty CP Thép Việt Đức', 'nha_cung_cap', '0100567890', 'KCN Phố Nối, Hưng Yên', 'Bà Trần Thị Hương', '0221.3864.890'),
    (9, 'Ngân hàng TMCP Ngoại thương (Vietcombank) - CN Thái Bình', 'ngan_hang', '0100112233', 'Số 1 Trần Hưng Đạo, TP Thái Bình', 'Ông Hoàng Minh Tuấn', '0227.3831.600'),
    (10, 'Ngân hàng TMCP Đầu tư và PT (BIDV) - CN Thái Bình', 'ngan_hang', '0100445566', 'Số 3 Lý Bôn, TP Thái Bình', 'Bà Vũ Thị Ngọc', '0227.3831.700'),
]

RE_UNIT_TYPES = [
    (1, 'shophouse', 'Shophouse', 'Nhà phố thương mại, kết hợp kinh doanh tầng 1 và ở tầng trên'),
    (2, 'dat_nen', 'Đất nền', 'Lô đất đã có hạ tầng, khách tự xây'),
    (3, 'nha_lien_ke', 'Nhà liền kề', 'Nhà liền kề trong khu đô thị, thiết kế đồng bộ'),
    (4, 'biet_thu', 'Biệt thự', 'Biệt thự đơn lập hoặc song lập trong khu đô thị'),
    (5, 'dat_cong_nghiep', 'Đất công nghiệp', 'Lô đất trong khu/cụm công nghiệp, cho thuê hoặc bán'),
]

# Project definitions
# (project_id, name, type, subtype, region_id, client, contract_value, planned_budget,
#  planned_start, planned_end, actual_start, status, total_units, sales_start_date, notes)
PROJECTS_TC = [
    ('TC-001', 'Cầu Trà Lý – Đoạn Vũ Thư', 'thi_cong', 'giao_thong', 6,
     'BQL DA XDCSHT tỉnh Thái Bình', 45000, 42500,
     '2024-01-15', '2025-12-31', '2024-01-20', 'dang_thi_cong',
     None, None, 'Dự án cầu bắc qua sông Trà Lý, liên danh'),
    ('TC-002', 'Trường THPT Quỳnh Côi', 'thi_cong', 'dan_dung', 3,
     'Sở GD&ĐT Thái Bình', 28000, 26200,
     '2024-03-01', '2025-09-30', '2024-03-10', 'dang_thi_cong',
     None, None, 'Xây mới trường THPT Quỳnh Côi, 3 tầng, 24 phòng học'),
    ('TC-003', 'Đường giao thông Đông Hưng – Thái Thụy', 'thi_cong', 'giao_thong', 2,
     'BQL DA huyện Đông Hưng', 68000, 63500,
     '2023-06-01', '2025-06-30', '2023-06-15', 'dang_thi_cong',
     None, None, 'Đường cấp III đồng bằng, dài 12.5km, mặt đường 9m'),
    ('TC-004', 'Kè bờ sông Trà Lý đoạn Tiền Hải', 'thi_cong', 'thuy_loi', 5,
     'BQL DA NNPTNT tỉnh Thái Bình', 35000, 33000,
     '2023-09-01', '2025-03-31', '2023-09-10', 'dang_thi_cong',
     None, None, 'Kè bảo vệ bờ sông Trà Lý, dài 2.8km, chống sạt lở'),
    ('TC-005', 'Hạ tầng KCN Tiền Hải mở rộng', 'thi_cong', 'ha_tang', 5,
     'BQL KCN tỉnh Thái Bình', 52000, 48800,
     '2024-04-01', '2025-10-31', '2024-04-15', 'dang_thi_cong',
     None, None, 'Hạ tầng kỹ thuật KCN Tiền Hải giai đoạn 2, 45ha'),
]

PROJECTS_BDS = [
    ('BDS-001', 'KĐT Đông Hòa', 'bat_dong_san', 'khu_do_thi', 1,
     'Lam Sơn Invest (Chủ đầu tư)', 185000, 148000,
     '2023-04-01', '2026-12-31', '2023-04-15', 'dang_thi_cong',
     120, '2024-06-01', 'Khu đô thị 120 nhà liền kề, hạ tầng đồng bộ'),
    ('BDS-002', 'Shophouse Lý Bôn', 'bat_dong_san', 'shophouse', 1,
     'Lam Sơn Invest (Chủ đầu tư)', 22000, 17600,
     '2022-03-01', '2024-06-30', '2022-03-15', 'bao_hanh',
     35, '2023-01-01', 'Shophouse phong cách tân cổ điển Pháp, 35 căn'),
    ('BDS-003', 'KĐT Tây QL10', 'bat_dong_san', 'dat_nen', 2,
     'Lam Sơn Invest (Chủ đầu tư)', 48000, 36000,
     '2024-01-15', '2025-12-31', '2024-02-01', 'dang_thi_cong',
     80, '2024-09-01', 'Đất nền 80 lô, hạ tầng hoàn thiện, gần QL10'),
    ('BDS-004', 'KDC Nguyễn Đức Cảnh', 'bat_dong_san', 'khu_dan_cu', 4,
     'Lam Sơn Invest (Chủ đầu tư)', 32000, 25600,
     '2023-10-01', '2025-09-30', '2023-10-15', 'dang_thi_cong',
     60, '2024-03-01', 'Khu dân cư 60 lô đất nền, gần KCN'),
    ('BDS-005', 'Đất CN Xuân Quang', 'bat_dong_san', 'khu_cong_nghiep', 2,
     'Lam Sơn Invest (Chủ đầu tư)', 75000, 56000,
     '2023-07-01', '2025-12-31', '2023-07-20', 'dang_thi_cong',
     25, '2024-01-01', 'Đất công nghiệp 25 lô, diện tích 2.000-5.000 m²'),
]

# =============================================================================
# PROGRESS & FINANCIAL PARAMETERS
# =============================================================================

# planned_progress_pct and actual_progress_pct as of 03/2025
PROJECT_PROGRESS = {
    'TC-001': (62.0, 60.0),   # slight delay, normal
    'TC-002': (68.0, 66.0),   # normal
    'TC-003': (68.0, 45.0),   # ANOMALY: severe delay
    'TC-004': (95.0, 92.0),   # near completion
    'TC-005': (65.0, 63.0),   # normal
    'BDS-001': (55.0, 52.0),  # construction progress (sales anomaly separate)
    'BDS-002': (100.0, 100.0),# completed, in warranty
    'BDS-003': (58.0, 56.0),  # normal
    'BDS-004': (72.0, 70.0),  # normal
    'BDS-005': (65.0, 62.0),  # normal
}

# BDS sales: (sold_units, total_units)
BDS_SALES = {
    'BDS-001': (42, 120),   # ANOMALY: only 35% after 10 months
    'BDS-002': (27, 35),    # ANOMALY: 8 stuck, mostly sold early
    'BDS-003': (58, 80),    # normal
    'BDS-004': (48, 60),    # normal, almost done
    'BDS-005': (15, 25),    # normal for industrial
}

# Cost category distribution (% of planned_budget)
COST_DIST = {
    'nguyen_vat_lieu': 0.50,
    'nhan_cong': 0.22,
    'thau_phu': 0.17,
    'may_moc': 0.07,
    'quan_ly': 0.04,
}
CAT_ID_MAP = {1: 'nguyen_vat_lieu', 2: 'nhan_cong', 3: 'thau_phu', 4: 'may_moc', 5: 'quan_ly'}

# Seasonality for construction costs
CONSTRUCTION_SEASONALITY = {
    1: 0.75, 2: 0.65, 3: 1.05, 4: 1.10, 5: 1.05, 6: 0.90,
    7: 0.85, 8: 0.85, 9: 0.95, 10: 1.15, 11: 1.25, 12: 1.30,
}

# Seasonality for RE sales
RE_SALES_SEASONALITY = {
    1: 0.70, 2: 0.60, 3: 1.20, 4: 1.15, 5: 1.00, 6: 0.85,
    7: 0.75, 8: 0.90, 9: 1.05, 10: 1.15, 11: 1.20, 12: 1.10,
}

# Steel seasonal factor
STEEL_SEASONAL = {
    1: 1.05, 2: 1.02, 3: 1.08, 4: 1.03, 5: 0.98, 6: 0.93,
    7: 0.90, 8: 0.92, 9: 0.95, 10: 1.00, 11: 1.04, 12: 1.06,
}

# Material suppliers
SUPPLIERS = [
    'Công ty CP Thép Việt Đức', 'Đại lý Thép Hoàng Long', 'Công ty CP VLXD Đông Á',
    'Xi măng Vissai Thái Bình', 'Đại lý VLXD Minh Phát', 'Công ty CP Cát sỏi Bắc Bộ',
    'Trạm trộn BT Thái Bình', 'Công ty TNHH Gạch Đồng Nai - CN Bắc',
]

# =============================================================================
# MILESTONES TEMPLATES
# =============================================================================

MILESTONES_GIAO_THONG = [
    ('Giải phóng mặt bằng', 10),
    ('Thi công nền đường', 25),
    ('Thi công mặt đường', 30),
    ('Hệ thống thoát nước', 15),
    ('Hoàn thiện, biển báo, vạch kẻ', 10),
    ('Nghiệm thu & bàn giao', 10),
]

MILESTONES_DAN_DUNG = [
    ('Khảo sát, thiết kế BVTC', 5),
    ('Móng & kết cấu tầng 1', 25),
    ('Kết cấu tầng 2-3', 25),
    ('Xây tường, hoàn thiện thô', 20),
    ('M&E, hoàn thiện nội thất', 15),
    ('Nghiệm thu & bàn giao', 10),
]

MILESTONES_THUY_LOI = [
    ('Chuẩn bị mặt bằng', 10),
    ('Thi công kè đoạn 1 (Km0-Km1.4)', 30),
    ('Thi công kè đoạn 2 (Km1.4-Km2.8)', 30),
    ('Hệ thống mái taluy, rọ đá', 15),
    ('Hoàn thiện & nghiệm thu', 15),
]

MILESTONES_HA_TANG = [
    ('San nền, đường nội bộ', 25),
    ('Hệ thống cấp thoát nước', 20),
    ('Hệ thống điện, chiếu sáng', 20),
    ('Cây xanh, vỉa hè', 15),
    ('Trạm xử lý nước thải', 10),
    ('Nghiệm thu tổng thể', 10),
]

MILESTONES_BDS = {
    'BDS-001': [
        ('Giải phóng mặt bằng', 5),
        ('San nền, hạ tầng kỹ thuật', 20),
        ('Thi công nhà liền kề đợt 1 (60 căn)', 30),
        ('Thi công nhà liền kề đợt 2 (60 căn)', 25),
        ('Hoàn thiện hạ tầng, cây xanh', 10),
        ('Nghiệm thu & bàn giao', 10),
    ],
    'BDS-002': [
        ('Giải phóng mặt bằng', 5),
        ('Thi công hạ tầng', 15),
        ('Xây dựng shophouse (35 căn)', 45),
        ('Hoàn thiện nội ngoại thất', 25),
        ('Nghiệm thu & bàn giao', 10),
    ],
    'BDS-003': [
        ('Giải phóng mặt bằng', 5),
        ('San nền, phân lô', 25),
        ('Hạ tầng đường, thoát nước', 30),
        ('Hệ thống điện, cây xanh', 20),
        ('Nghiệm thu & mở bán', 20),
    ],
    'BDS-004': [
        ('Giải phóng mặt bằng', 5),
        ('San nền, phân lô', 25),
        ('Đường nội bộ, thoát nước', 30),
        ('Điện, cây xanh, hàng rào', 20),
        ('Nghiệm thu & bàn giao', 20),
    ],
    'BDS-005': [
        ('Giải phóng mặt bằng, san lấp', 10),
        ('Đường giao thông nội bộ', 25),
        ('Hệ thống cấp thoát nước', 20),
        ('Hệ thống điện, PCCC', 20),
        ('Trạm xử lý nước thải', 15),
        ('Nghiệm thu tổng thể', 10),
    ],
}

MILESTONES_TC_MAP = {
    'giao_thong': MILESTONES_GIAO_THONG,
    'dan_dung': MILESTONES_DAN_DUNG,
    'thuy_loi': MILESTONES_THUY_LOI,
    'ha_tang': MILESTONES_HA_TANG,
}


def months_between(start, end):
    """Return list of first-of-month dates between start and end (inclusive of both months)."""
    result = []
    d = date(start.year, start.month, 1)
    end_m = date(end.year, end.month, 1)
    while d <= end_m:
        result.append(d)
        if d.month == 12:
            d = date(d.year + 1, 1, 1)
        else:
            d = date(d.year, d.month + 1, 1)
    return result


def month_diff(d1, d2):
    """Number of months from d1 to d2."""
    return (d2.year - d1.year) * 12 + (d2.month - d1.month)


def clamp(val, lo, hi):
    return max(lo, min(hi, val))


# =============================================================================
# GENERATION FUNCTIONS
# =============================================================================

def generate_material_price_index():
    """Generate market prices for 8 materials × 18 months."""
    rows = []
    for mat_id, mat_name, unit, base_price, group in MATERIALS:
        for mo in MONTHS:
            month_offset = month_diff(MONTHS[0], mo)  # 0..17

            if group == 'thep':
                # Steel: +8% YoY trend + seasonal + noise
                trend = 1 + 0.08 * month_offset / 12
                seasonal = STEEL_SEASONAL.get(mo.month, 1.0)
                noise = random.uniform(0.96, 1.04)
                avg_price = int(base_price * trend * seasonal * noise)
                # Inject peaks for anomaly: March 2024 and May 2024
                if mat_id == 1:  # Thép cuộn CB300
                    if mo == date(2024, 3, 1):
                        avg_price = int(base_price * trend * 1.20 * noise)  # peak +20%
                    elif mo == date(2024, 5, 1):
                        avg_price = int(base_price * trend * 1.22 * noise)  # peak +22%
            elif group == 'xi_mang':
                trend = 1 + 0.05 * month_offset / 12
                noise = random.uniform(0.97, 1.03)
                avg_price = int(base_price * trend * noise)
            elif group == 'be_tong':
                trend = 1 + 0.06 * month_offset / 12
                noise = random.uniform(0.97, 1.03)
                avg_price = int(base_price * trend * noise)
            else:
                # cat, da, gach: moderate trend
                trend = 1 + 0.04 * month_offset / 12
                noise = random.uniform(0.95, 1.05)
                avg_price = int(base_price * trend * noise)

            min_price = int(avg_price * random.uniform(0.90, 0.95))
            max_price = int(avg_price * random.uniform(1.05, 1.12))
            rows.append((mat_id, mo, avg_price, min_price, max_price))
    return rows


def get_project_active_months(proj):
    """Return list of months this project was active within our data range."""
    p_id = proj[0]
    actual_start = date.fromisoformat(proj[10]) if isinstance(proj[10], str) else proj[10]
    planned_end = date.fromisoformat(proj[9]) if isinstance(proj[9], str) else proj[9]
    # Clip to data range
    start_m = max(date(actual_start.year, actual_start.month, 1), MONTHS[0])
    end_m = min(date(planned_end.year, planned_end.month, 1), MONTHS[-1])
    # For ongoing projects, extend to current
    if planned_end > CURRENT_DATE:
        end_m = MONTHS[-1]
    return months_between(start_m, end_m)


def generate_cost_items(price_index_map):
    """Generate cost_items for 5 TC projects."""
    rows = []
    anomaly_extra = []

    for proj in PROJECTS_TC:
        p_id = proj[0]
        planned_budget = proj[7]
        active_months = get_project_active_months(proj)
        n_months = len(active_months)
        if n_months == 0:
            continue

        monthly_budget = planned_budget / n_months

        for mo in active_months:
            month_idx = month_diff(active_months[0], mo)
            seasonal = CONSTRUCTION_SEASONALITY.get(mo.month, 1.0)

            for cat_id in range(1, 6):
                cat_key = CAT_ID_MAP[cat_id]
                cat_pct = COST_DIST[cat_key]
                planned = int(monthly_budget * cat_pct * seasonal)
                planned = max(planned, 1)

                # Base: actual ≈ planned ± 3%
                actual = int(planned * random.uniform(0.97, 1.03))

                # ANOMALY: TC-003 cost overrun — category-level multipliers for TOTAL
                # Target: NVL +28%, thầu phụ +15%, nhân công +2%, máy móc -1%, quản lý +3%
                if p_id == 'TC-003':
                    if cat_id == 1:  # NVL: +28% total
                        actual = int(planned * 1.28 * random.uniform(0.96, 1.04))
                    elif cat_id == 2:  # Nhân công: +2%
                        actual = int(planned * 1.02 * random.uniform(0.97, 1.03))
                    elif cat_id == 3:  # Thầu phụ: +15%
                        actual = int(planned * 1.15 * random.uniform(0.96, 1.04))
                    elif cat_id == 4:  # Máy móc: -1%
                        actual = int(planned * 0.99 * random.uniform(0.97, 1.03))
                    elif cat_id == 5:  # Quản lý: +3%
                        actual = int(planned * 1.03 * random.uniform(0.97, 1.03))

                rows.append((p_id, cat_id, mo, planned, actual, None))

    # Extra anomaly row: TC-003 phát sinh gia cố nền đất yếu
    anomaly_month = date(2024, 9, 1)
    anomaly_extra.append(('TC-003', 3, anomaly_month, 0, 420,
                          'Phát sinh: gia cố nền đất yếu đoạn Km2+300 - Km3+100'))

    return rows + anomaly_extra


def generate_material_purchases(price_index_map):
    """Generate 2-4 POs/month for each active TC project."""
    rows = []
    purchase_id = 0

    # Which materials each project type typically uses
    project_materials = {
        'TC-001': [1, 3, 6, 8],      # cầu: thép, xi măng, đá, bê tông
        'TC-002': [1, 3, 5, 7, 8],   # dân dụng: thép, xi măng, cát, gạch, bê tông
        'TC-003': [1, 2, 3, 4, 6, 8],# đường: cả 2 loại thép, xi măng, cát san lấp, đá, bê tông
        'TC-004': [1, 3, 4, 6, 8],   # thủy lợi: thép, xi măng, cát san lấp, đá, bê tông
        'TC-005': [1, 3, 4, 5, 6, 8],# hạ tầng
    }

    # Scale factor based on project budget
    budget_map = {p[0]: p[7] for p in PROJECTS_TC}
    max_budget = max(budget_map.values())

    for proj in PROJECTS_TC:
        p_id = proj[0]
        active_months = get_project_active_months(proj)
        mats = project_materials.get(p_id, [1, 3, 8])
        scale = budget_map[p_id] / max_budget

        for mo in active_months:
            seasonal = CONSTRUCTION_SEASONALITY.get(mo.month, 1.0)
            n_pos = random.choice([2, 2, 3, 3, 4]) if seasonal > 0.9 else random.choice([1, 2, 2])

            for _ in range(n_pos):
                mat_id = random.choice(mats)
                mat_info = MATERIALS[mat_id - 1]
                mat_name, unit, base_price, group = mat_info[1], mat_info[2], mat_info[3], mat_info[4]

                # Get market price for this month
                key = (mat_id, mo)
                if key in price_index_map:
                    mkt_avg = price_index_map[key]['avg']
                    mkt_max = price_index_map[key]['max']
                else:
                    mkt_avg = base_price
                    mkt_max = int(base_price * 1.10)

                # Normal: buy at ±5% of market avg
                unit_price = int(mkt_avg * random.uniform(0.95, 1.05))

                # ANOMALY: TC-003 buys steel at peak price in March and May 2024
                if p_id == 'TC-003' and mat_id in (1, 2):
                    if mo == date(2024, 3, 1) or mo == date(2024, 5, 1):
                        unit_price = mkt_max  # buy at max

                # Quantity based on scale and unit
                if unit == 'kg':
                    qty = int(random.uniform(8000, 25000) * scale * seasonal)
                elif unit == 'tấn':
                    qty = int(random.uniform(30, 120) * scale * seasonal)
                elif unit == 'm³':
                    qty = int(random.uniform(50, 300) * scale * seasonal)
                elif unit == 'viên':
                    qty = int(random.uniform(20000, 80000) * scale * seasonal)
                else:
                    qty = int(random.uniform(50, 200) * scale * seasonal)

                qty = max(qty, 1)

                # total_amount in triệu VND
                total = round(unit_price * qty / 1_000_000, 0)
                total = max(int(total), 1)

                # Purchase date: random day in month
                day = random.randint(1, 28)
                p_date = date(mo.year, mo.month, day)

                # Special: TC-003 steel peak purchases on specific dates
                if p_id == 'TC-003' and mat_id == 1:
                    if mo == date(2024, 3, 1):
                        p_date = date(2024, 3, 15)
                        qty = 20000
                        total = int(unit_price * qty / 1_000_000)
                    elif mo == date(2024, 5, 1):
                        p_date = date(2024, 5, 10)
                        qty = 18000
                        total = int(unit_price * qty / 1_000_000)

                supplier = random.choice(SUPPLIERS)
                if mat_id in (1, 2):
                    supplier = random.choice(['Công ty CP Thép Việt Đức', 'Đại lý Thép Hoàng Long'])
                elif mat_id == 3:
                    supplier = 'Xi măng Vissai Thái Bình'
                elif mat_id in (4, 5, 6):
                    supplier = random.choice(['Công ty CP Cát sỏi Bắc Bộ', 'Công ty CP VLXD Đông Á'])
                elif mat_id == 7:
                    supplier = 'Công ty TNHH Gạch Đồng Nai - CN Bắc'
                elif mat_id == 8:
                    supplier = 'Trạm trộn BT Thái Bình'

                rows.append((p_id, mat_id, supplier, p_date, unit_price, qty, total, None))

    return rows


def generate_project_financials():
    """Generate monthly P&L for all 10 projects."""
    rows = []

    # TC projects: revenue recognized by progress, margin varies
    for proj in PROJECTS_TC:
        p_id = proj[0]
        subtype = proj[3]
        contract_value = proj[6]
        planned_budget = proj[7]
        active_months = get_project_active_months(proj)
        n_months = len(active_months)
        if n_months == 0:
            continue

        # Monthly revenue = contract_value / n_total_months * seasonal
        total_duration_months = month_diff(
            date.fromisoformat(proj[10]) if isinstance(proj[10], str) else proj[10],
            date.fromisoformat(proj[9]) if isinstance(proj[9], str) else proj[9]
        )
        total_duration_months = max(total_duration_months, 1)
        monthly_rev_base = contract_value / total_duration_months

        for i, mo in enumerate(active_months):
            seasonal = CONSTRUCTION_SEASONALITY.get(mo.month, 1.0)
            revenue = int(monthly_rev_base * seasonal * random.uniform(0.92, 1.08))

            # Margin by subtype
            if subtype == 'giao_thong':
                # ANOMALY: margin erosion from 12.3% → 6.8% over 12 months
                # Use the last 12 months index
                total_am = len(active_months)
                if total_am >= 12:
                    recent_idx = max(0, i - (total_am - 12))
                    if i >= total_am - 12:
                        margin_pct = 12.3 - 0.46 * recent_idx + random.uniform(-0.5, 0.5)
                    else:
                        margin_pct = random.uniform(11.5, 13.0)
                else:
                    month_idx = i
                    margin_pct = 12.3 - 0.46 * month_idx + random.uniform(-0.5, 0.5)
                margin_pct = clamp(margin_pct, 4.0, 15.0)
            elif subtype == 'dan_dung':
                margin_pct = random.uniform(14.0, 16.0)
            elif subtype == 'thuy_loi':
                margin_pct = random.uniform(10.0, 12.0)
            elif subtype == 'ha_tang':
                margin_pct = random.uniform(10.5, 12.5)
            else:
                margin_pct = random.uniform(10.0, 14.0)

            cogs = int(revenue * (1 - margin_pct / 100))
            gross_profit = revenue - cogs
            rows.append((p_id, mo, revenue, cogs, gross_profit, round(margin_pct, 2)))

    # BDS projects: revenue from unit sales
    for proj in PROJECTS_BDS:
        p_id = proj[0]
        subtype = proj[3]
        sales_start_str = proj[13]
        total_units = proj[12]
        sold_target = BDS_SALES[p_id][0]

        if sales_start_str is None:
            continue
        sales_start = date.fromisoformat(sales_start_str) if isinstance(sales_start_str, str) else sales_start_str
        actual_start = date.fromisoformat(proj[10]) if isinstance(proj[10], str) else proj[10]

        # Active months = from actual_start to current, clipped to data range
        active_months = get_project_active_months(proj)

        # Average price per unit (triệu VND)
        if subtype == 'khu_do_thi':
            avg_price = 1500  # nhà liền kề
        elif subtype == 'shophouse':
            avg_price = 1500  # shophouse ~1.5 tỷ avg
        elif subtype == 'dat_nen':
            avg_price = 700
        elif subtype == 'khu_dan_cu':
            avg_price = 700
        elif subtype == 'khu_cong_nghiep':
            avg_price = 4500  # đất CN lớn
        else:
            avg_price = 1000

        # Cost per unit ~65-80% of price depending on type
        if subtype in ('khu_do_thi', 'shophouse'):
            cost_ratio = 0.75  # margin ~25%
        elif subtype in ('dat_nen', 'khu_dan_cu'):
            cost_ratio = 0.70  # margin ~30% (đất nền margin cao)
        else:
            cost_ratio = 0.78  # margin ~22%

        for mo in active_months:
            # Before sales start: only construction costs, no revenue
            if mo < date(sales_start.year, sales_start.month, 1):
                # Construction cost recognized
                construction_months = months_between(
                    date(actual_start.year, actual_start.month, 1),
                    date(sales_start.year, sales_start.month, 1)
                )
                if mo in construction_months:
                    # Recognize construction cost but no sales revenue
                    pass
                continue

            seasonal = RE_SALES_SEASONALITY.get(mo.month, 1.0)

            # BDS-002 anomaly: fast early sales then stall
            if p_id == 'BDS-002':
                if mo < date(2023, 7, 1):
                    units_this_month = random.choice([3, 4, 5])
                elif mo < date(2024, 1, 1):
                    units_this_month = random.choice([0, 0, 1])
                else:
                    units_this_month = random.choice([0, 0, 0, 1])
            else:
                # Normal distribution of sales
                months_selling = months_between(
                    date(sales_start.year, sales_start.month, 1), MONTHS[-1]
                )
                n_sell_months = len(months_selling)
                if n_sell_months > 0:
                    base_units = sold_target / n_sell_months
                    units_this_month = max(0, int(base_units * seasonal * random.uniform(0.6, 1.4)))
                else:
                    units_this_month = 0

            revenue = int(units_this_month * avg_price * random.uniform(0.95, 1.05))
            cogs = int(revenue * cost_ratio * random.uniform(0.97, 1.03))
            gross_profit = revenue - cogs
            margin_pct = round((gross_profit / revenue * 100) if revenue > 0 else 0, 2)

            rows.append((p_id, mo, revenue, cogs, gross_profit, margin_pct))

    return rows


def generate_bid_history():
    """Generate ~15 bid records."""
    rows = []
    bid_id = 0

    # Existing projects that were won
    won_bids = [
        ('TC-001', 'Xây dựng cầu Trà Lý – Đoạn qua huyện Vũ Thư', 'BQL DA XDCSHT tỉnh Thái Bình',
         'giao_thong', 47000, 45000, 0.9574, 4, 'trung_thau', '2023-10-15', '2023-11-20'),
        ('TC-002', 'Xây mới Trường THPT Quỳnh Côi', 'Sở GD&ĐT Thái Bình',
         'dan_dung', 30000, 28000, 0.9333, 3, 'trung_thau', '2023-12-10', '2024-01-15'),
        ('TC-003', 'Đường giao thông liên huyện Đông Hưng – Thái Thụy', 'BQL DA huyện Đông Hưng',
         'giao_thong', 72000, 68000, 0.9444, 5, 'trung_thau', '2023-03-20', '2023-04-25'),
        ('TC-004', 'Kè chống sạt lở bờ sông Trà Lý đoạn Tiền Hải', 'BQL DA NNPTNT tỉnh',
         'thuy_loi', 37000, 35000, 0.9459, 3, 'trung_thau', '2023-06-15', '2023-07-20'),
        ('TC-005', 'Hạ tầng kỹ thuật KCN Tiền Hải mở rộng GĐ2', 'BQL KCN tỉnh',
         'ha_tang', 55000, 52000, 0.9455, 4, 'trung_thau', '2024-01-20', '2024-02-25'),
    ]

    for wb in won_bids:
        rows.append(wb)

    # ANOMALY: 3 recent giao_thong bids with very low bid_ratio
    low_bids = [
        (None, 'Nâng cấp ĐT.396B đoạn Đông Hưng – Quỳnh Phụ', 'BQL DA XDCSHT tỉnh Thái Bình',
         'giao_thong', 42000, 35700, 0.8500, 7, 'trung_thau', '2024-09-10', '2024-10-15'),
        (None, 'Đường vào KCN Gia Lễ, Đông Hưng', 'BQL DA huyện Đông Hưng',
         'giao_thong', 28000, 24360, 0.8700, 6, 'trung_thau', '2024-11-05', '2024-12-10'),
        (None, 'Cải tạo ĐT.454 đoạn qua Thái Thụy', 'BQL DA huyện Thái Thụy',
         'giao_thong', 38000, 32680, 0.8600, 8, 'trung_thau', '2025-01-15', '2025-02-20'),
    ]
    for lb in low_bids:
        rows.append(lb)

    # Normal bids (some won, some lost)
    other_bids = [
        (None, 'Trường Tiểu học Vũ Thư', 'Sở GD&ĐT Thái Bình',
         'dan_dung', 18000, 17100, 0.9500, 3, 'trung_thau', '2024-04-20', '2024-05-25'),
        (None, 'Sửa chữa trụ sở UBND huyện Kiến Xương', 'UBND huyện Kiến Xương',
         'dan_dung', 8500, 7990, 0.9400, 2, 'trung_thau', '2024-06-10', '2024-07-15'),
        (None, 'Kè bờ sông Hồng đoạn Hưng Hà', 'BQL DA NNPTNT tỉnh',
         'thuy_loi', 45000, 42750, 0.9500, 4, 'that_bai', '2024-07-15', '2024-08-20'),
        (None, 'Đường vào cảng Diêm Điền', 'BQL DA XDCSHT tỉnh',
         'giao_thong', 55000, 50050, 0.9100, 6, 'that_bai', '2024-05-20', '2024-06-25'),
        (None, 'Hạ tầng CCN Đông La, Đông Hưng', 'BQL KCN tỉnh',
         'ha_tang', 32000, 30400, 0.9500, 3, 'trung_thau', '2024-08-10', '2024-09-15'),
    ]
    for ob in other_bids:
        rows.append(ob)

    return rows


def generate_milestones():
    """Generate milestones for all 10 projects."""
    rows = []

    for proj in PROJECTS_TC:
        p_id = proj[0]
        subtype = proj[3]
        actual_start = date.fromisoformat(proj[10]) if isinstance(proj[10], str) else proj[10]
        planned_end = date.fromisoformat(proj[9]) if isinstance(proj[9], str) else proj[9]
        planned_progress, actual_progress = PROJECT_PROGRESS[p_id]

        template = MILESTONES_TC_MAP.get(subtype, MILESTONES_GIAO_THONG)
        total_days = (planned_end - actual_start).days
        cumulative_pct = 0
        cumulative_days = 0

        for order, (name, weight) in enumerate(template, 1):
            ms_days = int(total_days * weight / 100)
            p_start = actual_start + timedelta(days=cumulative_days)
            p_end = actual_start + timedelta(days=cumulative_days + ms_days)
            cumulative_days += ms_days
            cumulative_pct += weight

            # Determine actual dates based on progress
            if actual_progress >= cumulative_pct:
                # Milestone completed
                delay_factor = 1.0
                if p_id == 'TC-003':
                    delay_factor = 1.3  # 30% slower
                a_start = p_start + timedelta(days=random.randint(-3, 5))
                a_end = p_end + timedelta(days=int(ms_days * (delay_factor - 1)) + random.randint(-2, 5))
                status = 'hoan_thanh'
            elif actual_progress >= cumulative_pct - weight:
                # In progress
                a_start = p_start + timedelta(days=random.randint(-3, 10))
                a_end = None
                status = 'dang_thuc_hien'
                if p_id == 'TC-003':
                    status = 'cham_tien_do'
            else:
                a_start = None
                a_end = None
                status = 'chua_bat_dau'

            rows.append((p_id, name, order, p_start, p_end, a_start, a_end, weight, status, None))

    # BDS milestones
    for proj in PROJECTS_BDS:
        p_id = proj[0]
        actual_start = date.fromisoformat(proj[10]) if isinstance(proj[10], str) else proj[10]
        planned_end = date.fromisoformat(proj[9]) if isinstance(proj[9], str) else proj[9]
        planned_progress, actual_progress = PROJECT_PROGRESS[p_id]

        template = MILESTONES_BDS.get(p_id, [('Thi công', 80), ('Nghiệm thu', 20)])
        total_days = (planned_end - actual_start).days
        cumulative_pct = 0
        cumulative_days = 0

        for order, (name, weight) in enumerate(template, 1):
            ms_days = int(total_days * weight / 100)
            p_start = actual_start + timedelta(days=cumulative_days)
            p_end = actual_start + timedelta(days=cumulative_days + ms_days)
            cumulative_days += ms_days
            cumulative_pct += weight

            if actual_progress >= cumulative_pct:
                a_start = p_start + timedelta(days=random.randint(-2, 5))
                a_end = p_end + timedelta(days=random.randint(-5, 10))
                status = 'hoan_thanh'
            elif actual_progress >= cumulative_pct - weight:
                a_start = p_start + timedelta(days=random.randint(-2, 5))
                a_end = None
                status = 'dang_thuc_hien'
            else:
                a_start = None
                a_end = None
                status = 'chua_bat_dau'

            rows.append((p_id, name, order, p_start, p_end, a_start, a_end, weight, status, None))

    return rows


def generate_real_estate_units():
    """Generate individual RE units for all 5 BDS projects."""
    rows = []

    unit_configs = {
        'BDS-001': {
            'total': 120, 'type_id': 3, 'prefix': 'LK',
            'area_range': (72, 95), 'price_range': (1300, 1700),
            'listing_date': date(2024, 6, 1),
            'sold': 42,
            'blocks': ['A', 'B', 'C', 'D'],
        },
        'BDS-002': {
            'total': 35, 'type_id': 1, 'prefix': 'SH',
            'area_range': (85, 130), 'price_range': (1200, 1800),
            'listing_date': date(2023, 1, 1),
            'sold': 27,
            'blocks': ['A', 'B'],
        },
        'BDS-003': {
            'total': 80, 'type_id': 2, 'prefix': 'DN',
            'area_range': (80, 120), 'price_range': (560, 840),
            'listing_date': date(2024, 9, 1),
            'sold': 58,
            'blocks': ['A', 'B', 'C'],
        },
        'BDS-004': {
            'total': 60, 'type_id': 2, 'prefix': 'NC',
            'area_range': (75, 110), 'price_range': (525, 770),
            'listing_date': date(2024, 3, 1),
            'sold': 48,
            'blocks': ['A', 'B'],
        },
        'BDS-005': {
            'total': 25, 'type_id': 5, 'prefix': 'CN',
            'area_range': (2000, 5000), 'price_range': (3000, 8000),
            'listing_date': date(2024, 1, 1),
            'sold': 15,
            'blocks': ['I', 'II'],
        },
    }

    for p_id, cfg in unit_configs.items():
        total = cfg['total']
        sold = cfg['sold']
        listing_date = cfg['listing_date']
        positions = ['Mặt đường chính', 'Lô góc', 'Trong khu', 'Gần công viên', 'Mặt đường phụ']

        # Generate sale dates
        # For BDS-002: anomaly — mostly sold early, then stalled
        if p_id == 'BDS-002':
            # 27 sold: 22 in first 6 months, 5 in next 12 months
            sale_dates = []
            for i in range(22):
                m = random.randint(0, 5)
                mo = date(2023, 1 + m, random.randint(5, 25))
                sale_dates.append(mo)
            for i in range(5):
                m = random.randint(6, 17)
                yr = 2023 + (m // 12)
                mn = (m % 12) + 1
                if mn > 12:
                    mn -= 12
                    yr += 1
                mo = date(min(yr, 2025), min(mn, 3) if yr == 2025 else mn, random.randint(5, 25))
                sale_dates.append(mo)
            sale_dates.sort()
        else:
            # Normal: distribute sales over selling period
            sale_dates = []
            sell_start_m = listing_date
            sell_months = months_between(sell_start_m, MONTHS[-1])
            sell_months_filtered = [m for m in sell_months if m >= date(sell_start_m.year, sell_start_m.month, 1)]

            for i in range(sold):
                if sell_months_filtered:
                    mo = random.choice(sell_months_filtered)
                    day = random.randint(3, 27)
                    sale_dates.append(date(mo.year, mo.month, day))
            sale_dates.sort()

        # Create units
        sold_idx = 0
        for i in range(1, total + 1):
            code = f"{cfg['prefix']}-{cfg['blocks'][(i-1) % len(cfg['blocks'])]}{((i-1) // len(cfg['blocks'])) + 1:02d}"
            area = round(random.uniform(*cfg['area_range']), 1)
            base_price = random.randint(*cfg['price_range'])

            # Position premium
            pos = random.choice(positions)
            if pos in ('Lô góc', 'Mặt đường chính'):
                listed_price = int(base_price * random.uniform(1.03, 1.08))
            else:
                listed_price = base_price

            if sold_idx < sold:
                # This unit is sold
                sale_dt = sale_dates[sold_idx] if sold_idx < len(sale_dates) else listing_date + timedelta(days=random.randint(30, 300))
                reservation_dt = sale_dt - timedelta(days=random.randint(7, 30))
                actual_price = int(listed_price * random.uniform(0.97, 1.02))

                # Some already handed over
                months_since_sale = month_diff(sale_dt, CURRENT_DATE)
                if months_since_sale > 3:
                    status = 'da_ban_giao'
                    handover_dt = sale_dt + timedelta(days=random.randint(60, 180))
                elif months_since_sale > 0:
                    status = 'da_ban'
                    handover_dt = None
                else:
                    status = 'dat_coc'
                    handover_dt = None

                buyer_type = random.choice(['ca_nhan', 'ca_nhan', 'ca_nhan', 'dau_tu', 'dau_tu', 'doanh_nghiep'])
                if cfg['type_id'] == 5:
                    buyer_type = random.choice(['doanh_nghiep', 'doanh_nghiep', 'dau_tu'])

                rows.append((
                    p_id, cfg['type_id'], code, area, listed_price, actual_price,
                    status, listing_date, reservation_dt, sale_dt, handover_dt,
                    buyer_type, None, cfg['blocks'][(i-1) % len(cfg['blocks'])], pos
                ))
                sold_idx += 1
            else:
                # Unsold
                rows.append((
                    p_id, cfg['type_id'], code, area, listed_price, None,
                    'chua_ban', listing_date, None, None, None,
                    None, None, cfg['blocks'][(i-1) % len(cfg['blocks'])], pos
                ))

    return rows


def generate_re_sales_monthly():
    """Generate aggregated monthly sales for BDS projects."""
    rows = []

    for proj in PROJECTS_BDS:
        p_id = proj[0]
        sales_start_str = proj[13]
        if sales_start_str is None:
            continue
        sales_start = date.fromisoformat(sales_start_str)
        total_units = proj[12]
        sold_target = BDS_SALES[p_id][0]

        sell_months = [m for m in MONTHS if m >= date(sales_start.year, sales_start.month, 1)]
        n_sell = len(sell_months)
        if n_sell == 0:
            continue

        # Calculate pre-range sales: units sold before data range starts
        pre_range_sold = 0
        if p_id == 'BDS-002':
            pre_range_sold = 22  # 22 sold in Jan-Jun 2023, before data range starts Oct 2023
        elif sales_start < MONTHS[0]:
            # Project started selling before data range — estimate pre-range sales
            pre_range_months = month_diff(date(sales_start.year, sales_start.month, 1), MONTHS[0])
            in_range_months = n_sell
            total_sell_months = pre_range_months + in_range_months
            if total_sell_months > 0:
                pre_range_sold = int(sold_target * pre_range_months / total_sell_months)

        remaining = total_units - pre_range_sold
        total_sold_so_far = pre_range_sold
        in_range_target = sold_target - pre_range_sold  # units to sell within data range

        for i, mo in enumerate(sell_months):
            seasonal = RE_SALES_SEASONALITY.get(mo.month, 1.0)

            if p_id == 'BDS-002':
                # Anomaly: slow trickle — only ~5 sales over 18 months
                units = random.choice([0, 0, 0, 1])
                if mo == date(2024, 3, 1) or mo == date(2024, 11, 1) or mo == date(2025, 1, 1):
                    units = 1  # guarantee a few sales
            else:
                if in_range_target > 0 and n_sell > 0:
                    base = in_range_target / n_sell
                else:
                    base = 0
                units = max(0, int(base * seasonal * random.uniform(0.5, 1.5)))

            # Don't exceed total sold target
            if total_sold_so_far + units > sold_target:
                units = max(0, sold_target - total_sold_so_far)

            total_sold_so_far += units
            remaining = total_units - total_sold_so_far
            remaining = max(0, remaining)

            # Revenue (triệu VND)
            if p_id == 'BDS-001':
                avg_p = 1500
            elif p_id == 'BDS-002':
                avg_p = 1500
            elif p_id == 'BDS-003':
                avg_p = 700
            elif p_id == 'BDS-004':
                avg_p = 700
            elif p_id == 'BDS-005':
                avg_p = 4500
            else:
                avg_p = 1000

            revenue = int(units * avg_p * random.uniform(0.95, 1.05))
            rows.append((p_id, mo, units, revenue, remaining))

    return rows


def generate_receivables():
    """Generate receivable records tied to milestones."""
    rows = []

    # TC projects: receivables tied to milestone completions
    tc_counterparty_map = {
        'TC-001': 1, 'TC-002': 2, 'TC-003': 3, 'TC-004': 4, 'TC-005': 5,
    }

    for proj in PROJECTS_TC:
        p_id = proj[0]
        contract_value = proj[6]
        cp_id = tc_counterparty_map[p_id]
        planned_progress, actual_progress = PROJECT_PROGRESS[p_id]

        # Milestones payments: typically 5-6 payments tied to progress
        payment_schedule = [
            ('Tạm ứng hợp đồng', 15, date(2023, 10, 15)),
            ('Nghiệm thu giai đoạn 1', 25, None),
            ('Nghiệm thu giai đoạn 2', 25, None),
            ('Nghiệm thu giai đoạn 3', 20, None),
            ('Nghiệm thu hoàn thành', 10, None),
            ('Bảo lãnh bảo hành (giữ lại)', 5, None),
        ]

        actual_start = date.fromisoformat(proj[10]) if isinstance(proj[10], str) else proj[10]
        planned_end = date.fromisoformat(proj[9]) if isinstance(proj[9], str) else proj[9]
        total_days = (planned_end - actual_start).days

        cumulative_pct = 0
        for milestone_name, pct, forced_date in payment_schedule:
            amount = int(contract_value * pct / 100)
            cumulative_pct += pct

            if forced_date:
                due = forced_date
            else:
                days_offset = int(total_days * cumulative_pct / 100)
                due = actual_start + timedelta(days=days_offset)

            # Status based on progress
            if cumulative_pct <= actual_progress * 0.95:
                status = 'da_thanh_toan'
                actual_paid = due + timedelta(days=random.randint(5, 30))
                expected = due
            elif cumulative_pct <= actual_progress * 1.2:
                # Due soon or slightly overdue
                if due < CURRENT_DATE:
                    status = 'qua_han'
                    actual_paid = None
                    expected = due + timedelta(days=random.randint(15, 45))
                else:
                    status = 'chua_thanh_toan'
                    actual_paid = None
                    expected = due
            else:
                status = 'du_kien'
                actual_paid = None
                expected = due if p_id != 'TC-003' else None  # TC-003: uncertain

            rows.append((p_id, cp_id, milestone_name, amount, due, expected, actual_paid, status, None))

    # ANOMALY: TC-003 critical receivable for T+2
    # Override/add the key receivable
    rows.append(('TC-003', 3, 'Nghiệm thu giai đoạn 2 — khoản trọng yếu', 8500,
                  date(2025, 5, 15), None, None, 'du_kien',
                  'Phụ thuộc tiến độ thi công — hiện chậm 23%'))

    # BDS projects: receivables from unit sales (aggregated by quarter)
    for proj in PROJECTS_BDS:
        p_id = proj[0]
        sold = BDS_SALES[p_id][0]
        if p_id == 'BDS-001':
            avg_p = 1500
        elif p_id == 'BDS-002':
            avg_p = 1500
        elif p_id in ('BDS-003', 'BDS-004'):
            avg_p = 700
        else:
            avg_p = 4500

        # A few receivable entries for BDS
        total_revenue = sold * avg_p
        n_payments = min(4, max(2, sold // 10))
        per_payment = total_revenue // n_payments

        sales_start = date.fromisoformat(proj[13]) if isinstance(proj[13], str) else proj[13]
        for i in range(n_payments):
            due = sales_start + timedelta(days=90 * (i + 1))
            if due < CURRENT_DATE - timedelta(days=30):
                status = 'da_thanh_toan'
                actual_paid = due + timedelta(days=random.randint(3, 20))
                expected = due
            elif due < CURRENT_DATE:
                status = 'chua_thanh_toan'
                actual_paid = None
                expected = due + timedelta(days=random.randint(0, 15))
            else:
                status = 'du_kien'
                actual_paid = None
                expected = due

            rows.append((p_id, None, f'Đợt thu tiền bán hàng lần {i+1}', per_payment,
                          due, expected, actual_paid, status, None))

    return rows


def generate_payables():
    """Generate payable records."""
    rows = []

    subcontractor_counterparty = 6  # Hải Minh Hưng
    supplier_counterparty_1 = 7     # VLXD Đông Á
    supplier_counterparty_2 = 8     # Thép Việt Đức

    for proj in PROJECTS_TC:
        p_id = proj[0]
        planned_budget = proj[7]
        active_months = get_project_active_months(proj)

        # Monthly payables: NTP, NVL, nhân công
        for mo in active_months:
            if random.random() < 0.5:  # Not every month
                continue

            seasonal = CONSTRUCTION_SEASONALITY.get(mo.month, 1.0)
            monthly_budget = planned_budget / len(active_months)

            # NTP payment
            ntp_amount = int(monthly_budget * 0.17 * seasonal * random.uniform(0.8, 1.2))
            due = date(mo.year, mo.month, 25)
            if due < CURRENT_DATE - timedelta(days=30):
                status = 'da_thanh_toan'
                actual_paid = due + timedelta(days=random.randint(0, 15))
            elif due < CURRENT_DATE:
                status = 'chua_thanh_toan'
                actual_paid = None
            else:
                status = 'chua_thanh_toan'
                actual_paid = None
            rows.append((p_id, subcontractor_counterparty, 'nha_thau_phu',
                          f'Thanh toán NTP tháng {mo.month}/{mo.year}',
                          ntp_amount, due, actual_paid, status))

            # Material payment
            nvl_amount = int(monthly_budget * 0.50 * seasonal * random.uniform(0.8, 1.2))
            cp_id = random.choice([supplier_counterparty_1, supplier_counterparty_2])
            due_nvl = date(mo.year, mo.month, 15)
            if due_nvl < CURRENT_DATE - timedelta(days=30):
                status_nvl = 'da_thanh_toan'
                actual_paid_nvl = due_nvl + timedelta(days=random.randint(0, 10))
            elif due_nvl < CURRENT_DATE:
                status_nvl = 'chua_thanh_toan'
                actual_paid_nvl = None
            else:
                status_nvl = 'chua_thanh_toan'
                actual_paid_nvl = None
            rows.append((p_id, cp_id, 'vat_lieu',
                          f'Thanh toán NVL tháng {mo.month}/{mo.year}',
                          nvl_amount, due_nvl, actual_paid_nvl, status_nvl))

    # ANOMALY: TC-003 critical payable for T+2
    rows.append(('TC-003', subcontractor_counterparty, 'nha_thau_phu',
                  'Thanh toán NTP đợt Q2/2025 — hợp đồng ràng buộc',
                  6200, date(2025, 5, 10), None, 'chua_thanh_toan'))

    # Loan interest payables for BDS
    for proj in PROJECTS_BDS:
        p_id = proj[0]
        if p_id in ('BDS-001', 'BDS-002', 'BDS-005'):
            for mo in MONTHS[-6:]:  # last 6 months
                interest = random.randint(80, 250) if p_id != 'BDS-005' else random.randint(200, 450)
                due = date(mo.year, mo.month, 20)
                if due < CURRENT_DATE:
                    status = 'da_thanh_toan'
                    actual_paid = due + timedelta(days=random.randint(0, 5))
                else:
                    status = 'chua_thanh_toan'
                    actual_paid = None
                rows.append((p_id, 9, 'lai_vay', f'Lãi vay tháng {mo.month}/{mo.year}',
                              interest, due, actual_paid, status))

    return rows


def generate_cash_flow_actual():
    """Generate 18 months of company-wide cash flow."""
    rows = []
    opening = 5200  # triệu VND (~5.2 tỷ)

    for mo in MONTHS:
        seasonal = CONSTRUCTION_SEASONALITY.get(mo.month, 1.0)
        re_seasonal = RE_SALES_SEASONALITY.get(mo.month, 1.0)

        # Base inflow: ~25-35 tỷ/month from all projects
        base_inflow = random.randint(22000, 35000)
        inflow = int(base_inflow * (seasonal * 0.6 + re_seasonal * 0.4) * random.uniform(0.85, 1.15))

        # Base outflow: slightly less than inflow (company is profitable)
        base_outflow = int(inflow * random.uniform(0.88, 0.97))
        outflow = base_outflow

        # Growth trend: +12% YoY
        month_offset = month_diff(MONTHS[0], mo)
        growth = 1 + 0.12 * month_offset / 12
        inflow = int(inflow * growth)
        outflow = int(outflow * growth)

        net = inflow - outflow
        closing = opening + net

        # Keep closing balance in reasonable range (2-8 tỷ)
        if closing < 2000:
            inflow += random.randint(1000, 3000)
            net = inflow - outflow
            closing = opening + net
        elif closing > 9000:
            outflow += random.randint(1000, 2000)
            net = inflow - outflow
            closing = opening + net

        rows.append((mo, opening, inflow, outflow, net, closing))
        opening = closing

    # Ensure recent months have closing ~4000-5000 (tight, for anomaly 4)
    # Adjust last 3 months
    for i in range(len(rows) - 3, len(rows)):
        mo, op, inf, out, net, cl = rows[i]
        target_closing = random.randint(3800, 5200)
        if i == len(rows) - 3:
            # Set opening from previous
            op = rows[i-1][5] if i > 0 else op
        else:
            op = rows[i-1][5]
        # Adjust outflow to hit target
        net = target_closing - op
        if net > 0:
            inf = random.randint(24000, 32000)
            out = inf - net
        else:
            inf = random.randint(22000, 28000)
            out = inf - net
        rows[i] = (mo, op, inf, out, net, target_closing)

    return rows


def generate_project_financing():
    """Generate loan/financing records for BDS projects."""
    rows = []
    financing = [
        ('BDS-001', 'Ngân hàng TMCP Ngoại thương (Vietcombank) - CN Thái Bình',
         85000, 72000, 9.5, date(2023, 6, 1), date(2026, 6, 1), 570, 'dang_vay'),
        ('BDS-002', 'Ngân hàng TMCP Đầu tư và PT (BIDV) - CN Thái Bình',
         12000, 12000, 10.0, date(2022, 6, 1), date(2025, 6, 1), 100, 'dang_vay'),
        ('BDS-003', 'Ngân hàng TMCP Ngoại thương (Vietcombank) - CN Thái Bình',
         25000, 20000, 9.8, date(2024, 3, 1), date(2026, 3, 1), 163, 'dang_vay'),
        ('BDS-004', 'Ngân hàng TMCP Đầu tư và PT (BIDV) - CN Thái Bình',
         15000, 14000, 10.2, date(2023, 12, 1), date(2025, 12, 1), 119, 'dang_vay'),
        ('BDS-005', 'Ngân hàng TMCP Ngoại thương (Vietcombank) - CN Thái Bình',
         40000, 35000, 9.5, date(2023, 9, 1), date(2026, 9, 1), 277, 'dang_vay'),
    ]
    return financing


# =============================================================================
# METADATA GENERATION
# =============================================================================

def generate_meta_tables():
    rows = [
        ('regions', 'dimension', 'Danh mục khu vực hành chính tỉnh Thái Bình', 'Administrative regions in Thai Binh province', 8, '1 dòng = 1 huyện/thành phố'),
        ('cost_categories', 'dimension', 'Phân loại 5 hạng mục chi phí trong thi công xây dựng', '5 construction cost categories', 5, '1 dòng = 1 hạng mục chi phí'),
        ('materials', 'dimension', 'Danh mục nguyên vật liệu xây dựng chính', 'Main construction materials catalog', 8, '1 dòng = 1 loại vật liệu'),
        ('subcontractors', 'dimension', 'Danh mục nhà thầu phụ hợp tác', 'Subcontractors list', 6, '1 dòng = 1 nhà thầu phụ'),
        ('counterparties', 'dimension', 'Danh mục đối tác kinh doanh', 'Business partners catalog', 10, '1 dòng = 1 đối tác'),
        ('re_unit_types', 'dimension', 'Phân loại sản phẩm bất động sản', 'Real estate product types', 5, '1 dòng = 1 loại sản phẩm'),
        ('projects', 'dimension', 'Danh mục dự án thi công + BĐS', 'All projects (construction + RE)', 10, '1 dòng = 1 dự án'),
        ('project_milestones', 'fact', 'Mốc tiến độ dự án — so sánh kế hoạch vs thực tế', 'Project milestones planned vs actual', 60, '1 dòng = 1 mốc tiến độ'),
        ('cost_items', 'fact', 'Chi phí phát sinh theo dự án × hạng mục × tháng', 'Monthly cost items by project and category', 400, '1 dòng = 1 dự án × 1 hạng mục × 1 tháng'),
        ('material_purchases', 'fact', 'Chi tiết từng lần mua nguyên vật liệu', 'Material purchase orders', 300, '1 dòng = 1 PO line'),
        ('material_price_index', 'fact', 'Chỉ số giá vật liệu xây dựng theo tháng', 'Monthly material price index', 144, '1 dòng = 1 vật liệu × 1 tháng'),
        ('project_financials', 'fact', 'P&L theo dự án × tháng', 'Monthly P&L by project', 140, '1 dòng = 1 dự án × 1 tháng'),
        ('bid_history', 'fact', 'Lịch sử đấu thầu', 'Bidding history', 15, '1 dòng = 1 gói thầu'),
        ('receivables', 'fact', 'Công nợ phải thu từ chủ đầu tư / khách hàng', 'Accounts receivable', 50, '1 dòng = 1 khoản thu'),
        ('payables', 'fact', 'Công nợ phải trả — NTP, NCC, lãi vay', 'Accounts payable', 80, '1 dòng = 1 khoản trả'),
        ('cash_flow_actual', 'fact', 'Dòng tiền thực tế theo tháng — tổng hợp công ty', 'Monthly actual cash flow', 18, '1 dòng = 1 tháng'),
        ('real_estate_units', 'fact', 'Chi tiết từng sản phẩm BĐS (căn/lô)', 'Individual RE units', 320, '1 dòng = 1 căn/lô'),
        ('re_sales_monthly', 'fact', 'Thống kê bán hàng BĐS theo dự án × tháng', 'Monthly RE sales aggregation', 60, '1 dòng = 1 dự án × 1 tháng'),
        ('project_financing', 'fact', 'Khoản vay ngân hàng theo dự án', 'Project loans', 5, '1 dòng = 1 khoản vay'),
    ]
    return rows


def generate_meta_kpi():
    rows = [
        ('gross_margin_pct', 'Biên lợi nhuận gộp',
         '(revenue_recognized - cogs) / revenue_recognized * 100',
         'Biên lợi nhuận gộp (%) — tỷ lệ lợi nhuận gộp trên doanh thu. Theo dõi theo dự án, theo mảng (thi công/BĐS), theo loại công trình.',
         'project_financials, projects', 'Q3'),
        ('cost_variance', 'Chênh lệch chi phí',
         'actual_cost_to_date - planned_budget',
         'Chênh lệch chi phí so dự toán (triệu VND). Dương = vượt chi phí. Phân tích theo hạng mục qua bảng cost_items.',
         'projects, cost_items', 'Q2'),
        ('cost_variance_pct', 'Tỷ lệ vượt chi phí',
         '(actual_cost_to_date - planned_budget) / planned_budget * 100',
         'Tỷ lệ vượt chi phí so dự toán (%). Ngưỡng cảnh báo: > 10%.',
         'projects', 'Q2'),
        ('schedule_variance_days', 'Chênh lệch tiến độ',
         'actual_progress_pct - planned_progress_pct',
         'Chênh lệch tiến độ (% điểm). Âm = chậm tiến độ. Kết hợp planned_end - actual_end cho từng milestone.',
         'projects, project_milestones', 'Q1'),
        ('absorption_rate', 'Tỷ lệ hấp thụ BĐS',
         'sold_units / total_units * 100',
         'Tỷ lệ sản phẩm BĐS đã bán so tổng sản phẩm (%). Đánh giá hiệu quả bán hàng dự án.',
         'projects, real_estate_units', 'Q5'),
        ('sell_through_rate', 'Tốc độ bán BĐS',
         'units_sold / units_available',
         'Số sản phẩm bán được trong tháng / tổng sản phẩm còn lại. Đánh giá tốc độ hấp thụ.',
         're_sales_monthly', 'Q5'),
        ('inventory_holding_cost', 'Chi phí vốn tồn kho BĐS',
         'unsold_value * interest_rate / 100 * holding_months / 12',
         'Chi phí lãi vay phát sinh do tồn kho BĐS chưa bán (triệu VND). Tính theo giá trị tồn × lãi suất × thời gian.',
         'real_estate_units, project_financing', 'Q5'),
        ('net_cash_flow', 'Dòng tiền thuần',
         'total_inflow - total_outflow',
         'Dòng tiền thuần hàng tháng (triệu VND). Âm = thiếu hụt. Cần theo dõi liên tục.',
         'cash_flow_actual', 'Q4'),
        ('revenue_by_segment', 'Doanh thu theo mảng',
         'SUM(revenue_recognized) GROUP BY project_type',
         'Tổng doanh thu phân theo mảng thi công và BĐS. So sánh đóng góp.',
         'project_financials, projects', 'Q1,Q3'),
        ('bid_ratio', 'Tỷ lệ giá thầu',
         'bid_price / estimated_value',
         'Tỷ lệ giá dự thầu so giá gói thầu. < 0.90 = rất cạnh tranh, rủi ro margin thấp.',
         'bid_history', 'Q3'),
        ('bid_win_rate', 'Tỷ lệ trúng thầu',
         'COUNT(result=trung_thau) / COUNT(*) * 100',
         'Tỷ lệ trúng thầu (%). Theo dõi theo loại công trình.',
         'bid_history', 'Q3'),
        ('receivable_aging', 'Tuổi nợ phải thu',
         'DATEDIFF(CURRENT_DATE, due_date)',
         'Số ngày quá hạn thanh toán. > 30 ngày cần theo dõi sát.',
         'receivables', 'Q4'),
        ('project_rag_status', 'Trạng thái RAG dự án',
         "CASE WHEN progress_gap < -15 OR cost_variance_pct > 10 THEN 'RED' WHEN progress_gap < -5 OR cost_variance_pct > 5 THEN 'YELLOW' ELSE 'GREEN' END",
         'Đánh giá tổng quan dự án: RED (có vấn đề nghiêm trọng), YELLOW (cần theo dõi), GREEN (bình thường).',
         'projects', 'Q1'),
        ('avg_inventory_months', 'Thời gian tồn kho trung bình',
         "AVG(DATEDIFF(CURRENT_DATE, listing_date) / 30) WHERE status='chua_ban'",
         'Thời gian tồn kho trung bình của sản phẩm BĐS chưa bán (tháng). > 12 tháng cần ưu tiên giải phóng.',
         'real_estate_units', 'Q5'),
    ]
    return rows


def generate_meta_glossary():
    rows = [
        # Xây dựng
        ('Chủ đầu tư', 'Project Owner / Client', 'Tổ chức, cá nhân sở hữu vốn đầu tư, thuê nhà thầu thi công', 'xay_dung'),
        ('Nhà thầu chính', 'Main Contractor', 'Đơn vị ký hợp đồng trực tiếp với chủ đầu tư để thi công toàn bộ/phần lớn công trình', 'xay_dung'),
        ('Nhà thầu phụ (NTP)', 'Subcontractor', 'Đơn vị được nhà thầu chính thuê thi công một phần công việc chuyên môn', 'xay_dung'),
        ('Dự toán', 'Cost Estimate', 'Tổng chi phí dự kiến cho dự án, được lập trước khi thi công', 'xay_dung'),
        ('Nghiệm thu', 'Acceptance / Inspection', 'Kiểm tra và xác nhận khối lượng, chất lượng công việc hoàn thành', 'xay_dung'),
        ('Giải ngân', 'Disbursement', 'Việc chuyển tiền từ nguồn vốn (ngân sách/vay) cho dự án theo tiến độ', 'xay_dung'),
        ('Đấu thầu', 'Bidding / Tendering', 'Quy trình cạnh tranh để chọn nhà thầu thi công dựa trên hồ sơ dự thầu', 'xay_dung'),
        ('Gói thầu', 'Bid Package', 'Phần công việc được tách ra để đấu thầu, có giá dự toán riêng', 'xay_dung'),
        ('Giá trúng thầu', 'Winning Bid Price', 'Giá mà nhà thầu đề xuất và được chấp thuận', 'xay_dung'),
        ('Bid ratio', 'Bid Ratio', 'Tỷ lệ giá dự thầu / giá gói thầu. Thấp hơn = cạnh tranh hơn nhưng rủi ro margin', 'xay_dung'),
        ('BOT', 'Build-Operate-Transfer', 'Hình thức đầu tư: xây dựng, vận hành thu phí, sau đó chuyển giao cho nhà nước', 'xay_dung'),
        ('BVTC', 'Bản vẽ thi công', 'Bản vẽ chi tiết kỹ thuật dùng để thi công tại công trường', 'xay_dung'),
        ('M&E', 'Mechanical & Electrical', 'Hệ thống cơ điện trong công trình: điện, nước, HVAC, PCCC', 'xay_dung'),
        ('Đất yếu', 'Soft Ground', 'Nền đất có sức chịu tải kém, cần gia cố (cọc, vải địa kỹ thuật) trước khi xây', 'xay_dung'),
        ('Rọ đá', 'Gabion', 'Lưới thép chứa đá, dùng trong kè chống sạt lở bờ sông', 'xay_dung'),
        ('Kè', 'Revetment / Embankment', 'Công trình bảo vệ bờ sông, bờ biển khỏi xói lở', 'xay_dung'),
        # Bất động sản
        ('Shophouse', 'Shophouse', 'Nhà phố thương mại, tầng trệt kinh doanh, tầng trên để ở', 'bat_dong_san'),
        ('Nhà liền kề', 'Townhouse', 'Nhà thiết kế đồng bộ trong khu đô thị, chung tường với nhà bên cạnh', 'bat_dong_san'),
        ('Đất nền', 'Land Plot', 'Lô đất đã có hạ tầng (đường, điện, nước), khách tự xây', 'bat_dong_san'),
        ('Khu đô thị (KĐT)', 'Urban Area', 'Khu vực quy hoạch đồng bộ: nhà ở, đường, công viên, trường học', 'bat_dong_san'),
        ('KDC', 'Khu dân cư', 'Khu dân cư — vùng quy hoạch cho mục đích ở, thường quy mô nhỏ hơn KĐT', 'bat_dong_san'),
        ('KCN', 'Khu công nghiệp', 'Khu vực chuyên dụng cho sản xuất công nghiệp, có hạ tầng riêng', 'bat_dong_san'),
        ('Tỷ lệ hấp thụ', 'Absorption Rate', 'Tỷ lệ sản phẩm BĐS đã bán trên tổng sản phẩm mở bán (%)', 'bat_dong_san'),
        ('Tốc độ bán', 'Sell-through Rate', 'Số sản phẩm bán được mỗi tháng — đo thanh khoản dự án', 'bat_dong_san'),
        ('Tồn kho BĐS', 'RE Inventory', 'Sản phẩm BĐS chưa bán được — gánh chi phí vốn (lãi vay)', 'bat_dong_san'),
        ('Mở bán', 'Sales Launch', 'Thời điểm chính thức giới thiệu và bán sản phẩm BĐS ra thị trường', 'bat_dong_san'),
        ('Đặt cọc', 'Deposit / Reservation', 'Khách đặt tiền giữ chỗ trước khi ký hợp đồng mua bán chính thức', 'bat_dong_san'),
        ('Bàn giao', 'Handover', 'Chuyển giao sản phẩm BĐS hoàn thiện cho khách mua', 'bat_dong_san'),
        ('Lô góc', 'Corner Lot', 'Lô đất ở vị trí góc — thường có diện tích lớn hơn và giá cao hơn', 'bat_dong_san'),
        # Tài chính
        ('Biên lợi nhuận gộp', 'Gross Margin', 'Tỷ lệ (Doanh thu - Giá vốn) / Doanh thu × 100. Đo hiệu quả quản lý chi phí trực tiếp.', 'tai_chinh'),
        ('Dòng tiền thuần', 'Net Cash Flow', 'Chênh lệch giữa tổng dòng tiền vào và dòng tiền ra trong kỳ', 'tai_chinh'),
        ('Công nợ phải thu', 'Accounts Receivable', 'Số tiền khách hàng/chủ đầu tư nợ công ty, chưa thanh toán', 'tai_chinh'),
        ('Công nợ phải trả', 'Accounts Payable', 'Số tiền công ty nợ NTP, NCC, ngân hàng, chưa thanh toán', 'tai_chinh'),
        ('Chi phí vốn', 'Cost of Capital', 'Chi phí phát sinh khi sử dụng vốn (lãi vay) để đầu tư dự án', 'tai_chinh'),
        ('Giải ngân ĐTC', 'Public Investment Disbursement', 'Giải ngân vốn đầu tư công — thường cao điểm cuối năm (Q4)', 'tai_chinh'),
        # Chung
        ('RAG Status', 'Red-Amber-Green Status', 'Hệ thống đánh giá trạng thái: Đỏ (có vấn đề), Vàng (cần theo dõi), Xanh (bình thường)', 'chung'),
        ('Variance', 'Variance / Chênh lệch', 'Chênh lệch giữa giá trị thực tế và giá trị kế hoạch — dùng cho chi phí, tiến độ', 'chung'),
        ('YoY', 'Year-over-Year', 'So sánh cùng kỳ năm trước — đánh giá xu hướng tăng trưởng', 'chung'),
        ('MoM', 'Month-over-Month', 'So sánh tháng liền trước — đánh giá biến động ngắn hạn', 'chung'),
        ('Triệu VND', 'Million VND', 'Đơn vị tiền tệ trong database. 1 tỷ = 1.000 triệu VND.', 'chung'),
    ]
    return rows


def generate_meta_columns():
    """Generate metadata for important columns."""
    cols = []
    # projects
    for c in [
        ('projects', 'project_id', 'VARCHAR(10)', 'Mã dự án: TC-xxx (thi công), BDS-xxx (bất động sản)', None, 1, None),
        ('projects', 'project_name', 'VARCHAR(200)', 'Tên dự án đầy đủ', None, 0, None),
        ('projects', 'project_type', 'ENUM', 'Loại dự án: thi_cong hoặc bat_dong_san', None, 0, None),
        ('projects', 'project_subtype', 'VARCHAR(50)', 'Phân loại chi tiết: giao_thong, dan_dung, thuy_loi, ha_tang, khu_do_thi, shophouse, dat_nen, khu_dan_cu, khu_cong_nghiep', None, 0, None),
        ('projects', 'region_id', 'INT', 'Khu vực triển khai dự án', None, 1, 'regions.region_id'),
        ('projects', 'client', 'VARCHAR(200)', 'Chủ đầu tư / khách hàng', None, 0, None),
        ('projects', 'contract_value', 'BIGINT', 'Giá trị hợp đồng / tổng mức đầu tư', 'triệu VND', 0, None),
        ('projects', 'planned_budget', 'BIGINT', 'Tổng dự toán chi phí', 'triệu VND', 0, None),
        ('projects', 'actual_cost_to_date', 'BIGINT', 'Chi phí thực tế lũy kế', 'triệu VND', 0, None),
        ('projects', 'planned_progress_pct', 'DECIMAL(5,2)', 'Tiến độ kế hoạch hiện tại', '%', 0, None),
        ('projects', 'actual_progress_pct', 'DECIMAL(5,2)', 'Tiến độ thực tế hiện tại', '%', 0, None),
        ('projects', 'status', 'ENUM', 'Trạng thái: chuan_bi, dang_thi_cong, tam_dung, hoan_thanh, bao_hanh', None, 0, None),
        ('projects', 'total_units', 'INT', 'Tổng sản phẩm BĐS (NULL nếu thi công)', 'căn/lô', 0, None),
        ('projects', 'sold_units', 'INT', 'Số sản phẩm đã bán (NULL nếu thi công)', 'căn/lô', 0, None),
        ('projects', 'sales_start_date', 'DATE', 'Ngày mở bán BĐS', None, 0, None),
    ]:
        cols.append(c)

    # cost_items
    for c in [
        ('cost_items', 'project_id', 'VARCHAR(10)', 'Mã dự án', None, 1, 'projects.project_id'),
        ('cost_items', 'category_id', 'INT', 'Hạng mục chi phí', None, 1, 'cost_categories.category_id'),
        ('cost_items', 'cost_month', 'DATE', 'Tháng phát sinh (ngày đầu tháng)', None, 0, None),
        ('cost_items', 'planned_amount', 'BIGINT', 'Chi phí kế hoạch', 'triệu VND', 0, None),
        ('cost_items', 'actual_amount', 'BIGINT', 'Chi phí thực tế', 'triệu VND', 0, None),
    ]:
        cols.append(c)

    # material_purchases
    for c in [
        ('material_purchases', 'project_id', 'VARCHAR(10)', 'Mã dự án', None, 1, 'projects.project_id'),
        ('material_purchases', 'material_id', 'INT', 'Loại vật liệu', None, 1, 'materials.material_id'),
        ('material_purchases', 'purchase_date', 'DATE', 'Ngày mua', None, 0, None),
        ('material_purchases', 'unit_price', 'BIGINT', 'Đơn giá mua', 'VND/đơn vị', 0, None),
        ('material_purchases', 'quantity', 'DECIMAL(12,2)', 'Số lượng mua', 'theo đơn vị vật liệu', 0, None),
        ('material_purchases', 'total_amount', 'BIGINT', 'Thành tiền', 'triệu VND', 0, None),
    ]:
        cols.append(c)

    # material_price_index
    for c in [
        ('material_price_index', 'material_id', 'INT', 'Loại vật liệu', None, 1, 'materials.material_id'),
        ('material_price_index', 'price_month', 'DATE', 'Tháng (ngày đầu tháng)', None, 0, None),
        ('material_price_index', 'market_avg_price', 'BIGINT', 'Giá trung bình thị trường', 'VND/đơn vị', 0, None),
        ('material_price_index', 'market_min_price', 'BIGINT', 'Giá thấp nhất thị trường', 'VND/đơn vị', 0, None),
        ('material_price_index', 'market_max_price', 'BIGINT', 'Giá cao nhất thị trường', 'VND/đơn vị', 0, None),
    ]:
        cols.append(c)

    # project_financials
    for c in [
        ('project_financials', 'project_id', 'VARCHAR(10)', 'Mã dự án', None, 1, 'projects.project_id'),
        ('project_financials', 'fin_month', 'DATE', 'Tháng tài chính', None, 0, None),
        ('project_financials', 'revenue_recognized', 'BIGINT', 'Doanh thu ghi nhận trong tháng', 'triệu VND', 0, None),
        ('project_financials', 'cogs', 'BIGINT', 'Giá vốn / chi phí trực tiếp', 'triệu VND', 0, None),
        ('project_financials', 'gross_profit', 'BIGINT', 'Lợi nhuận gộp', 'triệu VND', 0, None),
        ('project_financials', 'gross_margin_pct', 'DECIMAL(5,2)', 'Biên lợi nhuận gộp', '%', 0, None),
    ]:
        cols.append(c)

    # bid_history
    for c in [
        ('bid_history', 'project_id', 'VARCHAR(10)', 'Mã dự án (NULL nếu chưa gắn/thất bại)', None, 1, 'projects.project_id'),
        ('bid_history', 'tender_name', 'VARCHAR(300)', 'Tên gói thầu', None, 0, None),
        ('bid_history', 'estimated_value', 'BIGINT', 'Giá gói thầu (dự toán)', 'triệu VND', 0, None),
        ('bid_history', 'bid_price', 'BIGINT', 'Giá dự thầu của Lam Sơn', 'triệu VND', 0, None),
        ('bid_history', 'bid_ratio', 'DECIMAL(5,4)', 'Tỷ lệ giá thầu = bid_price / estimated_value', None, 0, None),
        ('bid_history', 'competitors_count', 'INT', 'Số nhà thầu cạnh tranh', None, 0, None),
        ('bid_history', 'result', 'ENUM', 'Kết quả: trung_thau hoặc that_bai', None, 0, None),
    ]:
        cols.append(c)

    # receivables
    for c in [
        ('receivables', 'project_id', 'VARCHAR(10)', 'Mã dự án', None, 1, 'projects.project_id'),
        ('receivables', 'amount', 'BIGINT', 'Số tiền phải thu', 'triệu VND', 0, None),
        ('receivables', 'due_date', 'DATE', 'Ngày đáo hạn', None, 0, None),
        ('receivables', 'expected_collection_date', 'DATE', 'Ngày dự kiến thu (NULL nếu không chắc)', None, 0, None),
        ('receivables', 'status', 'ENUM', 'Trạng thái: chua_thanh_toan, da_thanh_toan, qua_han, du_kien', None, 0, None),
    ]:
        cols.append(c)

    # payables
    for c in [
        ('payables', 'project_id', 'VARCHAR(10)', 'Mã dự án', None, 1, 'projects.project_id'),
        ('payables', 'category', 'ENUM', 'Loại: nha_thau_phu, vat_lieu, nhan_cong, thue, lai_vay, khac', None, 0, None),
        ('payables', 'amount', 'BIGINT', 'Số tiền phải trả', 'triệu VND', 0, None),
        ('payables', 'due_date', 'DATE', 'Ngày đáo hạn', None, 0, None),
        ('payables', 'status', 'ENUM', 'Trạng thái: chua_thanh_toan, da_thanh_toan, qua_han', None, 0, None),
    ]:
        cols.append(c)

    # cash_flow_actual
    for c in [
        ('cash_flow_actual', 'flow_month', 'DATE', 'Tháng (ngày đầu tháng)', None, 0, None),
        ('cash_flow_actual', 'opening_balance', 'BIGINT', 'Số dư đầu kỳ', 'triệu VND', 0, None),
        ('cash_flow_actual', 'total_inflow', 'BIGINT', 'Tổng dòng tiền vào', 'triệu VND', 0, None),
        ('cash_flow_actual', 'total_outflow', 'BIGINT', 'Tổng dòng tiền ra', 'triệu VND', 0, None),
        ('cash_flow_actual', 'net_cash_flow', 'BIGINT', 'Dòng tiền thuần', 'triệu VND', 0, None),
        ('cash_flow_actual', 'closing_balance', 'BIGINT', 'Số dư cuối kỳ', 'triệu VND', 0, None),
    ]:
        cols.append(c)

    # real_estate_units
    for c in [
        ('real_estate_units', 'project_id', 'VARCHAR(10)', 'Mã dự án BĐS', None, 1, 'projects.project_id'),
        ('real_estate_units', 'unit_type_id', 'INT', 'Loại sản phẩm', None, 1, 're_unit_types.unit_type_id'),
        ('real_estate_units', 'unit_code', 'VARCHAR(30)', 'Mã căn/lô', None, 0, None),
        ('real_estate_units', 'area_m2', 'DECIMAL(10,2)', 'Diện tích', 'm²', 0, None),
        ('real_estate_units', 'listed_price', 'BIGINT', 'Giá niêm yết', 'triệu VND', 0, None),
        ('real_estate_units', 'actual_price', 'BIGINT', 'Giá bán thực tế (NULL nếu chưa bán)', 'triệu VND', 0, None),
        ('real_estate_units', 'status', 'ENUM', 'Trạng thái: chua_ban, dat_coc, da_ban, da_ban_giao', None, 0, None),
        ('real_estate_units', 'listing_date', 'DATE', 'Ngày đưa vào bán', None, 0, None),
        ('real_estate_units', 'sale_date', 'DATE', 'Ngày ký HĐMB', None, 0, None),
        ('real_estate_units', 'buyer_type', 'ENUM', 'Loại khách: ca_nhan, dau_tu, doanh_nghiep', None, 0, None),
    ]:
        cols.append(c)

    # re_sales_monthly
    for c in [
        ('re_sales_monthly', 'project_id', 'VARCHAR(10)', 'Mã dự án BĐS', None, 1, 'projects.project_id'),
        ('re_sales_monthly', 'sales_month', 'DATE', 'Tháng', None, 0, None),
        ('re_sales_monthly', 'units_sold', 'INT', 'Số sản phẩm bán trong tháng', 'căn/lô', 0, None),
        ('re_sales_monthly', 'revenue', 'BIGINT', 'Doanh thu bán hàng', 'triệu VND', 0, None),
        ('re_sales_monthly', 'units_available', 'INT', 'Số sản phẩm còn lại', 'căn/lô', 0, None),
    ]:
        cols.append(c)

    # project_financing
    for c in [
        ('project_financing', 'project_id', 'VARCHAR(10)', 'Mã dự án', None, 1, 'projects.project_id'),
        ('project_financing', 'loan_amount', 'BIGINT', 'Hạn mức vay', 'triệu VND', 0, None),
        ('project_financing', 'interest_rate', 'DECIMAL(5,2)', 'Lãi suất năm', '%', 0, None),
        ('project_financing', 'monthly_interest', 'BIGINT', 'Lãi vay hàng tháng ước tính', 'triệu VND', 0, None),
    ]:
        cols.append(c)

    return cols


# =============================================================================
# SQL EXPORT HELPERS
# =============================================================================

def sql_val(v):
    """Format a Python value for SQL."""
    if v is None:
        return 'NULL'
    if isinstance(v, str):
        return "'" + v.replace("'", "''").replace("\\", "\\\\") + "'"
    if isinstance(v, date):
        return f"'{v.isoformat()}'"
    if isinstance(v, (int, float, Decimal)):
        return str(v)
    return str(v)


def batch_inserts(table, columns, rows, batch_size=1000):
    """Generate INSERT statements with batching."""
    stmts = []
    col_str = ', '.join(columns)
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i+batch_size]
        values = []
        for row in batch:
            vals = ', '.join(sql_val(v) for v in row)
            values.append(f'({vals})')
        stmt = f"INSERT INTO {table} ({col_str}) VALUES\n" + ',\n'.join(values) + ';'
        stmts.append(stmt)
    return '\n\n'.join(stmts)


# =============================================================================
# MAIN GENERATION & EXPORT
# =============================================================================

def main():
    print("=" * 60)
    print("Lam Sơn Invest — Construction & RE Demo Generator")
    print("=" * 60)

    os.makedirs(SQL_DIR, exist_ok=True)

    # =========================================================================
    # GENERATE ALL DATA
    # =========================================================================
    print("\n[1/8] Generating material price index...")
    price_index_rows = generate_material_price_index()
    # Build lookup map
    price_index_map = {}
    for mat_id, mo, avg, mn, mx in price_index_rows:
        price_index_map[(mat_id, mo)] = {'avg': avg, 'min': mn, 'max': mx}

    print("[2/8] Generating cost items...")
    cost_item_rows = generate_cost_items(price_index_map)

    print("[3/8] Generating material purchases...")
    purchase_rows = generate_material_purchases(price_index_map)

    print("[4/8] Generating project financials...")
    financial_rows = generate_project_financials()

    print("[5/8] Generating bid history, milestones, receivables, payables, cash flow...")
    bid_rows = generate_bid_history()
    milestone_rows = generate_milestones()
    receivable_rows = generate_receivables()
    payable_rows = generate_payables()
    cashflow_rows = generate_cash_flow_actual()
    financing_rows = generate_project_financing()

    print("[6/8] Generating real estate units & monthly sales...")
    re_unit_rows = generate_real_estate_units()
    re_sales_rows = generate_re_sales_monthly()

    print("[7/8] Generating metadata...")
    meta_table_rows = generate_meta_tables()
    meta_kpi_rows = generate_meta_kpi()
    meta_glossary_rows = generate_meta_glossary()
    meta_column_rows = generate_meta_columns()

    # =========================================================================
    # COMPUTE DERIVED VALUES FOR PROJECTS
    # =========================================================================
    print("[8/8] Computing derived project values...")

    # actual_cost_to_date for TC projects = sum of cost_items actual_amount
    project_costs = defaultdict(int)
    for row in cost_item_rows:
        project_costs[row[0]] += row[4]  # actual_amount

    # =========================================================================
    # WRITE SQL FILES
    # =========================================================================
    print("\nWriting SQL files...")

    # --- 02_metadata.sql ---
    meta_sql = "-- Lam Sơn Invest — Metadata\nUSE construction_re_demo;\n\n"

    meta_sql += "-- _meta_tables\n"
    meta_sql += batch_inserts('_meta_tables',
        ['table_name', 'table_type', 'description_vi', 'description_en', 'row_count_approx', 'grain'],
        meta_table_rows)
    meta_sql += "\n\n"

    meta_sql += "-- _meta_columns\n"
    meta_sql += batch_inserts('_meta_columns',
        ['table_name', 'column_name', 'data_type', 'description_vi', 'unit', 'is_key', 'fk_references'],
        meta_column_rows)
    meta_sql += "\n\n"

    meta_sql += "-- _meta_kpi\n"
    meta_sql += batch_inserts('_meta_kpi',
        ['kpi_name', 'kpi_name_vi', 'formula_sql', 'description_vi', 'related_tables', 'related_questions'],
        meta_kpi_rows)
    meta_sql += "\n\n"

    meta_sql += "-- _meta_glossary\n"
    meta_sql += batch_inserts('_meta_glossary',
        ['term_vi', 'term_en', 'definition_vi', 'domain'],
        meta_glossary_rows)

    with open(os.path.join(SQL_DIR, '02_metadata.sql'), 'w', encoding='utf-8') as f:
        f.write(meta_sql)
    print(f"  02_metadata.sql written")

    # --- 03_master_data.sql ---
    master_sql = "-- Lam Sơn Invest — Master Data\nUSE construction_re_demo;\n\n"

    master_sql += "-- regions\n"
    master_sql += batch_inserts('regions',
        ['region_id', 'region_name', 'region_type', 'notes'], REGIONS)
    master_sql += "\n\n"

    master_sql += "-- cost_categories\n"
    master_sql += batch_inserts('cost_categories',
        ['category_id', 'category_name_vi', 'category_name_en', 'typical_pct_min', 'typical_pct_max'],
        COST_CATEGORIES)
    master_sql += "\n\n"

    master_sql += "-- materials\n"
    master_sql += batch_inserts('materials',
        ['material_id', 'material_name', 'unit', 'base_price', 'material_group'], MATERIALS)
    master_sql += "\n\n"

    master_sql += "-- subcontractors\n"
    master_sql += batch_inserts('subcontractors',
        ['subcontractor_id', 'subcontractor_name', 'specialization', 'rating', 'phone', 'address'],
        SUBCONTRACTORS)
    master_sql += "\n\n"

    master_sql += "-- counterparties\n"
    master_sql += batch_inserts('counterparties',
        ['counterparty_id', 'counterparty_name', 'counterparty_type', 'tax_code', 'address', 'contact_person', 'phone'],
        COUNTERPARTIES)
    master_sql += "\n\n"

    master_sql += "-- re_unit_types\n"
    master_sql += batch_inserts('re_unit_types',
        ['unit_type_id', 'unit_type_code', 'unit_type_name', 'description'], RE_UNIT_TYPES)
    master_sql += "\n\n"

    # Projects — need to build full rows
    master_sql += "-- projects\n"
    project_rows = []
    for proj in PROJECTS_TC:
        p_id = proj[0]
        pp, ap = PROJECT_PROGRESS[p_id]
        actual_cost = project_costs.get(p_id, 0)
        project_rows.append((
            p_id, proj[1], proj[2], proj[3], proj[4], proj[5],  # id, name, type, subtype, region, client
            proj[6], proj[7], actual_cost,  # contract_value, planned_budget, actual_cost
            proj[8], proj[9],  # planned_start, planned_end (strings)
            proj[10], None,   # actual_start, actual_end
            pp, ap, proj[11],  # planned_progress, actual_progress, status
            None, None, None, proj[14]  # total_units, sold_units, sales_start, notes
        ))

    for proj in PROJECTS_BDS:
        p_id = proj[0]
        pp, ap = PROJECT_PROGRESS[p_id]
        sold = BDS_SALES[p_id][0]
        bds_actual_cost = int(proj[7] * ap / 100 * random.uniform(0.97, 1.03))  # cost proportional to progress
        project_rows.append((
            p_id, proj[1], proj[2], proj[3], proj[4], proj[5],
            proj[6], proj[7], bds_actual_cost,  # actual_cost_to_date based on progress
            proj[8], proj[9],
            proj[10], None,
            pp, ap, proj[11],
            proj[12], sold, proj[13], proj[14]
        ))

    master_sql += batch_inserts('projects',
        ['project_id', 'project_name', 'project_type', 'project_subtype', 'region_id', 'client',
         'contract_value', 'planned_budget', 'actual_cost_to_date',
         'planned_start', 'planned_end', 'actual_start', 'actual_end',
         'planned_progress_pct', 'actual_progress_pct', 'status',
         'total_units', 'sold_units', 'sales_start_date', 'notes'],
        project_rows)

    with open(os.path.join(SQL_DIR, '03_master_data.sql'), 'w', encoding='utf-8') as f:
        f.write(master_sql)
    print(f"  03_master_data.sql written")

    # --- 04_transaction_data.sql ---
    tx_sql = "-- Lam Sơn Invest — Transaction Data\nUSE construction_re_demo;\n\n"

    # Milestones
    tx_sql += "-- project_milestones\n"
    milestone_insert_rows = []
    for r in milestone_rows:
        milestone_insert_rows.append((r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9]))
    tx_sql += batch_inserts('project_milestones',
        ['project_id', 'milestone_name', 'milestone_order', 'planned_start', 'planned_end',
         'actual_start', 'actual_end', 'weight_pct', 'status', 'notes'],
        milestone_insert_rows)
    tx_sql += "\n\n"

    # Cost items
    tx_sql += "-- cost_items\n"
    ci_insert = [(r[0], r[1], r[2], r[3], r[4], r[5]) for r in cost_item_rows]
    tx_sql += batch_inserts('cost_items',
        ['project_id', 'category_id', 'cost_month', 'planned_amount', 'actual_amount', 'item_description'],
        ci_insert)
    tx_sql += "\n\n"

    # Material price index
    tx_sql += "-- material_price_index\n"
    tx_sql += batch_inserts('material_price_index',
        ['material_id', 'price_month', 'market_avg_price', 'market_min_price', 'market_max_price'],
        price_index_rows)
    tx_sql += "\n\n"

    # Material purchases
    tx_sql += "-- material_purchases\n"
    tx_sql += batch_inserts('material_purchases',
        ['project_id', 'material_id', 'supplier_name', 'purchase_date', 'unit_price', 'quantity', 'total_amount', 'notes'],
        purchase_rows)
    tx_sql += "\n\n"

    # Project financials
    tx_sql += "-- project_financials\n"
    tx_sql += batch_inserts('project_financials',
        ['project_id', 'fin_month', 'revenue_recognized', 'cogs', 'gross_profit', 'gross_margin_pct'],
        financial_rows)
    tx_sql += "\n\n"

    # Bid history
    tx_sql += "-- bid_history\n"
    bid_insert = []
    for r in bid_rows:
        bid_insert.append((r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], None))
    tx_sql += batch_inserts('bid_history',
        ['project_id', 'tender_name', 'tender_owner', 'project_subtype', 'estimated_value',
         'bid_price', 'bid_ratio', 'competitors_count', 'result', 'bid_date', 'award_date', 'notes'],
        bid_insert)
    tx_sql += "\n\n"

    # Receivables
    tx_sql += "-- receivables\n"
    tx_sql += batch_inserts('receivables',
        ['project_id', 'counterparty_id', 'milestone_name', 'amount', 'due_date',
         'expected_collection_date', 'actual_paid_date', 'status', 'notes'],
        receivable_rows)
    tx_sql += "\n\n"

    # Payables
    tx_sql += "-- payables\n"
    tx_sql += batch_inserts('payables',
        ['project_id', 'counterparty_id', 'category', 'description', 'amount',
         'due_date', 'actual_paid_date', 'status'],
        payable_rows)
    tx_sql += "\n\n"

    # Cash flow
    tx_sql += "-- cash_flow_actual\n"
    tx_sql += batch_inserts('cash_flow_actual',
        ['flow_month', 'opening_balance', 'total_inflow', 'total_outflow', 'net_cash_flow', 'closing_balance'],
        cashflow_rows)
    tx_sql += "\n\n"

    # Real estate units
    tx_sql += "-- real_estate_units\n"
    tx_sql += batch_inserts('real_estate_units',
        ['project_id', 'unit_type_id', 'unit_code', 'area_m2', 'listed_price', 'actual_price',
         'status', 'listing_date', 'reservation_date', 'sale_date', 'handover_date',
         'buyer_type', 'floor_number', 'block', 'position'],
        re_unit_rows)
    tx_sql += "\n\n"

    # RE sales monthly
    tx_sql += "-- re_sales_monthly\n"
    tx_sql += batch_inserts('re_sales_monthly',
        ['project_id', 'sales_month', 'units_sold', 'revenue', 'units_available'],
        re_sales_rows)
    tx_sql += "\n\n"

    # Project financing
    tx_sql += "-- project_financing\n"
    tx_sql += batch_inserts('project_financing',
        ['project_id', 'bank_name', 'loan_amount', 'disbursed_amount', 'interest_rate',
         'disbursement_date', 'maturity_date', 'monthly_interest', 'status'],
        financing_rows)

    with open(os.path.join(SQL_DIR, '04_transaction_data.sql'), 'w', encoding='utf-8') as f:
        f.write(tx_sql)
    print(f"  04_transaction_data.sql written")

    # =========================================================================
    # POPULATE MySQL
    # =========================================================================
    print("\nPopulating MySQL database...")
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()

        # Truncate all tables in reverse dependency order
        cur.execute("SET FOREIGN_KEY_CHECKS = 0")
        for tbl in ['project_financing', 're_sales_monthly', 'real_estate_units',
                     'cash_flow_actual', 'payables', 'receivables', 'bid_history',
                     'project_financials', 'material_purchases', 'material_price_index',
                     'cost_items', 'project_milestones', 'projects',
                     're_unit_types', 'counterparties', 'subcontractors', 'materials',
                     'cost_categories', 'regions',
                     '_meta_glossary', '_meta_kpi', '_meta_columns', '_meta_tables']:
            cur.execute(f"TRUNCATE TABLE {tbl}")
        cur.execute("SET FOREIGN_KEY_CHECKS = 1")
        conn.commit()

        # Insert master data
        print("  Inserting master data...")
        for r in REGIONS:
            cur.execute("INSERT INTO regions VALUES (%s,%s,%s,%s)", r)
        for r in COST_CATEGORIES:
            cur.execute("INSERT INTO cost_categories VALUES (%s,%s,%s,%s,%s)", r)
        for r in MATERIALS:
            cur.execute("INSERT INTO materials VALUES (%s,%s,%s,%s,%s)", r)
        for r in SUBCONTRACTORS:
            cur.execute("INSERT INTO subcontractors VALUES (%s,%s,%s,%s,%s,%s)", r)
        for r in COUNTERPARTIES:
            cur.execute("INSERT INTO counterparties VALUES (%s,%s,%s,%s,%s,%s,%s)", r)
        for r in RE_UNIT_TYPES:
            cur.execute("INSERT INTO re_unit_types VALUES (%s,%s,%s,%s)", r)

        # Projects
        for row in project_rows:
            cur.execute("""INSERT INTO projects
                (project_id, project_name, project_type, project_subtype, region_id, client,
                 contract_value, planned_budget, actual_cost_to_date,
                 planned_start, planned_end, actual_start, actual_end,
                 planned_progress_pct, actual_progress_pct, status,
                 total_units, sold_units, sales_start_date, notes)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", row)
        conn.commit()

        # Insert metadata
        print("  Inserting metadata...")
        for r in meta_table_rows:
            cur.execute("INSERT INTO _meta_tables VALUES (%s,%s,%s,%s,%s,%s)", r)
        for r in meta_column_rows:
            cur.execute("INSERT INTO _meta_columns (table_name,column_name,data_type,description_vi,unit,is_key,fk_references) VALUES (%s,%s,%s,%s,%s,%s,%s)", r)
        for r in meta_kpi_rows:
            cur.execute("INSERT INTO _meta_kpi (kpi_name,kpi_name_vi,formula_sql,description_vi,related_tables,related_questions) VALUES (%s,%s,%s,%s,%s,%s)", r)
        for r in meta_glossary_rows:
            cur.execute("INSERT INTO _meta_glossary (term_vi,term_en,definition_vi,domain) VALUES (%s,%s,%s,%s)", r)
        conn.commit()

        # Insert transaction data
        print("  Inserting milestones...")
        for r in milestone_rows:
            cur.execute("""INSERT INTO project_milestones
                (project_id, milestone_name, milestone_order, planned_start, planned_end,
                 actual_start, actual_end, weight_pct, status, notes)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", r)
        conn.commit()

        print("  Inserting cost items...")
        for r in cost_item_rows:
            cur.execute("""INSERT INTO cost_items
                (project_id, category_id, cost_month, planned_amount, actual_amount, item_description)
                VALUES (%s,%s,%s,%s,%s,%s)""", r)
        conn.commit()

        print("  Inserting material price index...")
        for r in price_index_rows:
            cur.execute("INSERT INTO material_price_index (material_id, price_month, market_avg_price, market_min_price, market_max_price) VALUES (%s,%s,%s,%s,%s)", r)
        conn.commit()

        print("  Inserting material purchases...")
        for r in purchase_rows:
            cur.execute("""INSERT INTO material_purchases
                (project_id, material_id, supplier_name, purchase_date, unit_price, quantity, total_amount, notes)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""", r)
        conn.commit()

        print("  Inserting project financials...")
        for r in financial_rows:
            cur.execute("""INSERT INTO project_financials
                (project_id, fin_month, revenue_recognized, cogs, gross_profit, gross_margin_pct)
                VALUES (%s,%s,%s,%s,%s,%s)""", r)
        conn.commit()

        print("  Inserting bid history...")
        for r in bid_rows:
            cur.execute("""INSERT INTO bid_history
                (project_id, tender_name, tender_owner, project_subtype, estimated_value,
                 bid_price, bid_ratio, competitors_count, result, bid_date, award_date)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", r)
        conn.commit()

        print("  Inserting receivables...")
        for r in receivable_rows:
            cur.execute("""INSERT INTO receivables
                (project_id, counterparty_id, milestone_name, amount, due_date,
                 expected_collection_date, actual_paid_date, status, notes)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""", r)
        conn.commit()

        print("  Inserting payables...")
        for r in payable_rows:
            cur.execute("""INSERT INTO payables
                (project_id, counterparty_id, category, description, amount,
                 due_date, actual_paid_date, status)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""", r)
        conn.commit()

        print("  Inserting cash flow...")
        for r in cashflow_rows:
            cur.execute("""INSERT INTO cash_flow_actual
                (flow_month, opening_balance, total_inflow, total_outflow, net_cash_flow, closing_balance)
                VALUES (%s,%s,%s,%s,%s,%s)""", r)
        conn.commit()

        print("  Inserting real estate units...")
        for r in re_unit_rows:
            cur.execute("""INSERT INTO real_estate_units
                (project_id, unit_type_id, unit_code, area_m2, listed_price, actual_price,
                 status, listing_date, reservation_date, sale_date, handover_date,
                 buyer_type, floor_number, block, position)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", r)
        conn.commit()

        print("  Inserting RE sales monthly...")
        for r in re_sales_rows:
            cur.execute("""INSERT INTO re_sales_monthly
                (project_id, sales_month, units_sold, revenue, units_available)
                VALUES (%s,%s,%s,%s,%s)""", r)
        conn.commit()

        print("  Inserting project financing...")
        for r in financing_rows:
            cur.execute("""INSERT INTO project_financing
                (project_id, bank_name, loan_amount, disbursed_amount, interest_rate,
                 disbursement_date, maturity_date, monthly_interest, status)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""", r)
        conn.commit()

        # Update actual_cost_to_date for TC projects from cost_items
        print("  Updating actual_cost_to_date...")
        cur.execute("""
            UPDATE projects p
            SET actual_cost_to_date = (
                SELECT COALESCE(SUM(ci.actual_amount), 0)
                FROM cost_items ci WHERE ci.project_id = p.project_id
            )
            WHERE p.project_type = 'thi_cong'
        """)
        conn.commit()

        # Print row counts
        print("\n  Row counts:")
        for tbl in ['regions', 'cost_categories', 'materials', 'subcontractors', 'counterparties',
                     're_unit_types', 'projects', 'project_milestones', 'cost_items',
                     'material_purchases', 'material_price_index', 'project_financials',
                     'bid_history', 'receivables', 'payables', 'cash_flow_actual',
                     'real_estate_units', 're_sales_monthly', 'project_financing',
                     '_meta_tables', '_meta_columns', '_meta_kpi', '_meta_glossary']:
            cur.execute(f"SELECT COUNT(*) FROM {tbl}")
            cnt = cur.fetchone()[0]
            print(f"    {tbl}: {cnt}")

        cur.close()
        conn.close()
        print("\n  MySQL populated successfully!")

    except Exception as e:
        print(f"\n  ERROR populating MySQL: {e}")
        import traceback
        traceback.print_exc()

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "=" * 60)
    print("GENERATION COMPLETE")
    print("=" * 60)
    print(f"Database: construction_re_demo")
    print(f"SQL files: {SQL_DIR}/")
    print(f"  - 01_ddl_schema.sql")
    print(f"  - 02_metadata.sql")
    print(f"  - 03_master_data.sql")
    print(f"  - 04_transaction_data.sql")
    print(f"  - (05_validation_queries.sql — write separately)")
    print(f"\nData range: 10/2023 – 03/2025 (18 months)")
    print(f"Projects: 5 thi công + 5 BĐS = 10")
    print(f"RE units: {len(re_unit_rows)}")
    print(f"Cost items: {len(cost_item_rows)}")
    print(f"Material purchases: {len(purchase_rows)}")
    print(f"Price index: {len(price_index_rows)}")
    print(f"Financials: {len(financial_rows)}")
    print(f"Bids: {len(bid_rows)}")
    print(f"Receivables: {len(receivable_rows)}")
    print(f"Payables: {len(payable_rows)}")


if __name__ == '__main__':
    main()
