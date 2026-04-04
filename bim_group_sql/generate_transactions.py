#!/usr/bin/env python3
"""
BIM Group - Transaction Data Generator
Generates 04_transaction_data.sql with 3 layers:
  Layer 1: Base volume
  Layer 2: Seasonality injection
  Layer 3: Anomaly injection
Period: T1/2023 - T6/2024 (18 months)
"""

import random
import math
from datetime import date, timedelta
from collections import defaultdict

random.seed(42)  # Reproducible

# ============================================================================
# CONSTANTS & CONFIGURATION
# ============================================================================

PERIODS = [f"{y}-{m:02d}" for y in [2023, 2024] for m in range(1, 13)
           if not (y == 2024 and m > 6)]  # 2023-01 to 2024-06

START_DATE = date(2023, 1, 1)
END_DATE = date(2024, 6, 30)

# Projects config: id, budget (VND), start_period_index (relative to PERIODS), active_months, cluster
PROJECTS = {
    'PJ-HL01': {'budget': 3_200_000_000_000, 'start_idx': 0, 'months': 18, 'cluster': 'CL-HL'},
    'PJ-HL02': {'budget': 1_500_000_000_000, 'start_idx': 0, 'months': 18, 'cluster': 'CL-HL'},
    'PJ-HL03': {'budget':   850_000_000_000, 'start_idx': 5, 'months': 13, 'cluster': 'CL-HL'},
    # PJ-HL04: Chuan bi - no disbursements
    'PJ-PQ01': {'budget': 2_500_000_000_000, 'start_idx': 0, 'months': 18, 'cluster': 'CL-PQ'},
    'PJ-PQ02': {'budget':   800_000_000_000, 'start_idx': 17, 'months': 1, 'cluster': 'CL-PQ'},  # only Jun 2024
    'PJ-HN01': {'budget': 1_200_000_000_000, 'start_idx': 12, 'months': 6, 'cluster': 'CL-HN'},  # Jan-Jun 2024
    'PJ-LA01': {'budget':   450_000_000_000, 'start_idx': 8, 'months': 10, 'cluster': 'CL-LA'},
}

# S-curve coefficients (normalized)
def s_curve(n):
    """Generate S-curve distribution for n months, sum=1.0"""
    raw = []
    for i in range(n):
        t = (i + 0.5) / n
        # Logistic S-curve derivative (bell-shaped allocation)
        val = math.exp(-10 * (t - 0.45)) / (1 + math.exp(-10 * (t - 0.45)))**2
        raw.append(val)
    total = sum(raw)
    return [v / total for v in raw]

# Work package weights
WP_WEIGHTS = {
    'WP-01': 0.25, 'WP-02': 0.18, 'WP-03': 0.15, 'WP-04': 0.12,
    'WP-05': 0.08, 'WP-06': 0.10, 'WP-07': 0.05, 'WP-08': 0.07,
}

# WP phase activity (month_index -> which WPs are active, 0-indexed within project)
def wp_is_active(wp_id, month_in_project, total_months):
    """Determine if a work package is active in a given project month."""
    pct = month_in_project / max(total_months - 1, 1)
    if wp_id == 'WP-01': return pct <= 0.50  # Foundation: first half
    if wp_id == 'WP-08': return pct <= 0.45  # Infrastructure: first 45%
    if wp_id == 'WP-02': return 0.15 <= pct <= 0.85  # M&E: mid-range
    if wp_id == 'WP-06': return 0.15 <= pct <= 0.80  # MEP: similar to M&E
    if wp_id == 'WP-07': return 0.20 <= pct <= 0.85  # Fire: after structure
    if wp_id == 'WP-03': return pct >= 0.35  # Interior: later phase
    if wp_id == 'WP-04': return 0.30 <= pct <= 0.90  # Exterior
    if wp_id == 'WP-05': return pct >= 0.55  # Landscape: late
    return True

# Project -> Contractor assignments
PROJECT_CONTRACTORS = {
    'PJ-HL01': {
        'WP-01': 'CT-01', 'WP-02': 'CT-02', 'WP-03': 'CT-03', 'WP-04': 'CT-10',
        'WP-05': 'CT-05', 'WP-06': 'CT-12', 'WP-07': 'CT-06', 'WP-08': 'CT-11',
    },
    'PJ-HL02': {
        'WP-01': 'CT-01', 'WP-02': 'CT-02', 'WP-03': 'CT-03', 'WP-04': 'CT-10',
        'WP-05': 'CT-05', 'WP-06': 'CT-12', 'WP-07': 'CT-06', 'WP-08': 'CT-11',
    },
    'PJ-HL03': {
        'WP-01': 'CT-04', 'WP-02': 'CT-02', 'WP-03': 'CT-14', 'WP-04': 'CT-10',
        'WP-05': 'CT-05', 'WP-06': 'CT-12', 'WP-07': 'CT-06', 'WP-08': 'CT-11',
    },
    'PJ-PQ01': {
        'WP-01': 'CT-07', 'WP-02': 'CT-08', 'WP-03': 'CT-09', 'WP-04': 'CT-10',
        'WP-05': 'CT-17', 'WP-06': 'CT-08', 'WP-07': 'CT-06', 'WP-08': 'CT-18',
    },
    'PJ-PQ02': {
        'WP-01': 'CT-07', 'WP-02': 'CT-08', 'WP-03': 'CT-09', 'WP-04': 'CT-10',
        'WP-05': 'CT-17', 'WP-06': 'CT-08', 'WP-07': 'CT-06', 'WP-08': 'CT-18',
    },
    'PJ-HN01': {
        'WP-01': 'CT-13', 'WP-02': 'CT-12', 'WP-03': 'CT-14', 'WP-04': 'CT-10',
        'WP-05': 'CT-05', 'WP-06': 'CT-12', 'WP-07': 'CT-06', 'WP-08': 'CT-13',
    },
    'PJ-LA01': {
        'WP-01': 'CT-16', 'WP-02': 'CT-15', 'WP-03': 'CT-09', 'WP-04': 'CT-10',
        'WP-05': 'CT-17', 'WP-06': 'CT-15', 'WP-07': 'CT-06', 'WP-08': 'CT-16',
    },
}

# Construction seasonality by cluster
CONSTRUCTION_SEASONALITY = {
    'CL-PQ': {1:1.00,2:1.00,3:1.00,4:1.02,5:1.08,6:1.12,7:1.15,8:1.15,9:1.10,10:1.05,11:1.00,12:1.00},
    'CL-HL': {1:1.05,2:1.03,3:1.00,4:1.00,5:1.00,6:1.00,7:1.08,8:1.10,9:1.08,10:1.00,11:1.02,12:1.05},
    'CL-HN': {m:1.00 for m in range(1,13)},
    'CL-LA': {m:1.00 for m in range(1,13)},
}

# Tet: reduce construction in Jan 2023, Feb 2024
TET_MONTHS = {('2023','01'): 0.70, ('2024','02'): 0.70}

# Properties config
PROPERTIES = {
    'PR-PQ01': {'rooms': 120, 'cluster': 'CL-PQ', 'base_adr': 8_500_000, 'base_occ': 0.72,
                'adr_range': (7_500_000, 9_500_000)},
    'PR-PQ02': {'rooms': 459, 'cluster': 'CL-PQ', 'base_adr': 5_200_000, 'base_occ': 0.68,
                'adr_range': (4_500_000, 6_000_000)},
    'PR-PQ03': {'rooms': 200, 'cluster': 'CL-PQ', 'base_adr': 3_800_000, 'base_occ': 0.65,
                'adr_range': (3_200_000, 4_500_000)},
    'PR-HL01': {'rooms': 260, 'cluster': 'CL-HL', 'base_adr': 1_800_000, 'base_occ': 0.55,
                'adr_range': (1_500_000, 2_200_000)},
    'PR-HN01': {'rooms': 80, 'cluster': 'CL-HN', 'base_adr': 3_200_000, 'base_occ': 0.78,
                'adr_range': (2_800_000, 3_600_000)},
    'PR-LA01': {'rooms': 198, 'cluster': 'CL-LA', 'base_adr': 2_100_000, 'base_occ': 0.48,
                'adr_range': (1_800_000, 2_500_000)},
}

# Monthly occupancy seasonality
OCCUPANCY_SEASONALITY = {
    'CL-PQ': {1:1.20,2:1.25,3:1.15,4:1.05,5:0.75,6:0.70,7:0.72,8:0.78,9:0.80,10:0.85,11:1.10,12:1.30},
    'CL-HL': {1:0.70,2:0.75,3:0.80,4:0.90,5:1.10,6:1.25,7:1.30,8:1.25,9:1.10,10:0.90,11:0.75,12:0.70},
    'CL-HN': {1:0.90,2:0.85,3:1.05,4:1.10,5:1.05,6:0.95,7:0.90,8:0.95,9:1.05,10:1.10,11:1.05,12:0.95},
    'CL-LA': {1:1.15,2:1.10,3:0.95,4:0.80,5:0.75,6:0.70,7:0.72,8:0.78,9:0.82,10:0.90,11:1.10,12:1.20},
}

WEEKLY_SEASONALITY = {0:0.85, 1:0.88, 2:0.90, 3:0.95, 4:1.10, 5:1.20, 6:1.12}

# Tet dates (14-day boost)
TET_2023 = date(2023, 1, 22)
TET_2024 = date(2024, 2, 10)

# Cost categories for hospitality
COST_CATEGORIES = ['Nhân sự', 'Điện nước', 'Bảo trì', 'Marketing', 'Phí quản lý', 'Khác']

# Cost ratios per property (% of revenue)
# Normal total ~62-65% → GOP margin 35-38%
# Citadines HL anomaly: total ~88% → GOP margin ~12%
# Crowne Plaza anomaly: total ~92% → GOP margin ~8%
PROPERTY_COST_RATIOS = {
    # Normal properties (GOP 35-42%)
    'PR-PQ01': {'Nhân sự': 0.28, 'Điện nước': 0.07, 'Bảo trì': 0.05, 'Marketing': 0.04, 'Phí quản lý': 0.06, 'Khác': 0.04},  # Regent: luxury, efficient
    'PR-PQ02': {'Nhân sự': 0.30, 'Điện nước': 0.08, 'Bảo trì': 0.05, 'Marketing': 0.05, 'Phí quản lý': 0.05, 'Khác': 0.04},  # IC PQ
    'PR-PQ03': {'Nhân sự': 0.29, 'Điện nước': 0.07, 'Bảo trì': 0.06, 'Marketing': 0.05, 'Phí quản lý': 0.04, 'Khác': 0.04},  # Sailing Club
    'PR-HN01': {'Nhân sự': 0.28, 'Điện nước': 0.06, 'Bảo trì': 0.05, 'Marketing': 0.04, 'Phí quản lý': 0.05, 'Khác': 0.03},  # Fraser HN: stable
    # Anomaly: Citadines HL — over-staffed + old building → GOP ~12%
    'PR-HL01': {'Nhân sự': 0.42, 'Điện nước': 0.12, 'Bảo trì': 0.12, 'Marketing': 0.08, 'Phí quản lý': 0.06, 'Khác': 0.08},
    # Anomaly: Crowne Plaza Vientiane — low occupancy + high IHG fee → GOP ~8%
    'PR-LA01': {'Nhân sự': 0.38, 'Điện nước': 0.12, 'Bảo trì': 0.10, 'Marketing': 0.10, 'Phí quản lý': 0.15, 'Khác': 0.07},
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def noise(low=0.97, high=1.03):
    return random.uniform(low, high)

def days_in_month(year, month):
    if month == 12:
        return 31
    return (date(year, month + 1, 1) - date(year, month, 1)).days

def is_tet_period(d):
    """Check if date is within 14 days around Tet."""
    for tet in [TET_2023, TET_2024]:
        if abs((d - tet).days) <= 7:
            return True
    return False

def sql_val(v):
    """Format value for SQL."""
    if v is None:
        return 'NULL'
    if isinstance(v, str):
        return "'" + v.replace("'", "''") + "'"
    if isinstance(v, (int, float)):
        return str(int(round(v)))
    return str(v)

# ============================================================================
# GENERATE DATA
# ============================================================================

budget_disbursements = []
construction_costs = []
change_orders_data = []
material_prices_data = []
hospitality_revenue_data = []
hospitality_costs_data = []
occupancy_daily_data = []

# --------------------------------------------------------------------------
# 1. BUDGET DISBURSEMENTS
# --------------------------------------------------------------------------
print("Generating budget_disbursements...")

for proj_id, cfg in PROJECTS.items():
    budget = cfg['budget']
    start_idx = cfg['start_idx']
    n_months = cfg['months']
    cluster = cfg['cluster']

    curve = s_curve(n_months)
    cum_planned = 0
    cum_actual = 0

    # Calibrate budget_in_period so that cumulative disbursement_pct ≈ planned_progress_pct
    # For PJ-HL01: planned_progress=68%, anomaly will push actual to ~71% (gap 13 vs actual 58%)
    # For others: disbursement_pct ≈ actual_progress_pct (gap ≤ 3%)
    # For PJ-HL01: set planned base at 60%, anomaly will push actual to ~71%
    # (gap = 71% - 58% actual_progress = 13 points)
    # For all others: target disbursement ≈ actual_progress (gap ≤ 3%)
    TARGET_DISBURSEMENT = {
        'PJ-HL01': 0.68,   # Base planned ~68%, anomaly ×1.20 on 6 months pushes to ~71%
        'PJ-HL02': 0.46,   # progress=45%, gap ≤ 3%
        'PJ-HL03': 0.83,   # progress=82%, nearly done
        'PJ-PQ01': 0.51,   # progress=52%, gap ≤ 3%
        'PJ-PQ02': 0.06,   # progress=15%, just started
        'PJ-HN01': 0.22,   # progress=22%, early stage
        'PJ-LA01': 0.36,   # progress=35%, gap ≤ 3%
    }
    budget_in_period = budget * TARGET_DISBURSEMENT.get(proj_id, 0.50)

    for i in range(n_months):
        period_idx = start_idx + i
        if period_idx >= len(PERIODS):
            break
        period = PERIODS[period_idx]
        year_str, month_str = period.split('-')
        month_num = int(month_str)

        planned = budget_in_period * curve[i]

        # Layer 2: Construction seasonality
        seasonal = CONSTRUCTION_SEASONALITY[cluster].get(month_num, 1.0)

        # Tet reduction
        tet_key = (year_str, month_str)
        tet_factor = TET_MONTHS.get(tet_key, 1.0)

        planned *= tet_factor  # Tet affects planned too

        # Layer 3: Anomaly - PJ-HL01 from Jan 2024 onward
        # Need x1.20 on last 6 months to push total from ~59% to ~71% (gap 13 pts vs 58% progress)
        if proj_id == 'PJ-HL01' and period >= '2024-01':
            actual = planned * 1.20 * seasonal * noise(0.98, 1.02)
        else:
            actual = planned * seasonal * noise(0.97, 1.03)

        planned = round(planned)
        actual = round(actual)
        cum_planned += planned
        cum_actual += actual

        budget_disbursements.append({
            'project_id': proj_id,
            'period': period,
            'planned_amount': planned,
            'actual_amount': actual,
            'cumulative_planned': cum_planned,
            'cumulative_actual': cum_actual,
        })

# --------------------------------------------------------------------------
# 2. CONSTRUCTION COSTS
# --------------------------------------------------------------------------
print("Generating construction_costs...")

for proj_id, cfg in PROJECTS.items():
    budget = cfg['budget']
    start_idx = cfg['start_idx']
    n_months = cfg['months']
    cluster = cfg['cluster']
    contractors = PROJECT_CONTRACTORS[proj_id]

    construction_budget = budget * 0.70  # ~70% of total is construction
    curve = s_curve(n_months)

    for i in range(n_months):
        period_idx = start_idx + i
        if period_idx >= len(PERIODS):
            break
        period = PERIODS[period_idx]
        year_str, month_str = period.split('-')
        month_num = int(month_str)

        for wp_id, weight in WP_WEIGHTS.items():
            if not wp_is_active(wp_id, i, n_months):
                continue

            contractor_id = contractors[wp_id]

            # Base budgeted cost
            # Distribute WP budget across active months
            active_months_count = sum(1 for m in range(n_months)
                                      if wp_is_active(wp_id, m, n_months))
            wp_budget = construction_budget * weight
            # Use curve shape but normalize for active months
            base_cost = wp_budget * curve[i] / (sum(curve[m] for m in range(n_months)
                                                    if wp_is_active(wp_id, m, n_months)) or 1)

            budgeted = base_cost
            seasonal = CONSTRUCTION_SEASONALITY[cluster].get(month_num, 1.0)

            # Tet
            tet_key = (year_str, month_str)
            tet_factor = TET_MONTHS.get(tet_key, 1.0)

            # Growth factor (2% annual - mild inflation)
            year_offset = (int(year_str) - 2023) + (month_num - 1) / 12
            growth = 1.0 + 0.02 * year_offset

            actual = budgeted * seasonal * tet_factor * growth * noise(0.97, 1.03)

            # Layer 3: Anomaly injection for PJ-HL01
            # Start anomaly earlier and use stronger multipliers so WP variance is clearly visible
            if proj_id == 'PJ-HL01':
                if wp_id == 'WP-02' and contractor_id == 'CT-02' and period >= '2024-01':
                    # M&E: +25% from Jan 2024 (brand compliance HVAC + spec upgrades)
                    actual = budgeted * 1.25 * seasonal * growth * noise(0.98, 1.02)
                elif wp_id == 'WP-03' and period >= '2024-01':
                    # Interior: +22% from Jan 2024 (lobby material changes)
                    actual = budgeted * 1.22 * seasonal * growth * noise(0.98, 1.02)
                elif wp_id == 'WP-01' and period >= '2024-01':
                    # Structure: +12% from Jan 2024 (steel price increase)
                    actual = budgeted * 1.12 * seasonal * growth * noise(0.98, 1.02)

            # Phu Quoc logistics surcharge (~15% higher)
            if cluster == 'CL-PQ':
                budgeted *= 1.15
                actual *= 1.15

            budgeted = round(budgeted)
            actual = round(actual)

            if budgeted > 0:
                construction_costs.append({
                    'project_id': proj_id,
                    'work_package_id': wp_id,
                    'contractor_id': contractor_id,
                    'period': period,
                    'budgeted_cost': budgeted,
                    'actual_cost': actual,
                })

# --------------------------------------------------------------------------
# 3. CHANGE ORDERS
# --------------------------------------------------------------------------
print("Generating change_orders...")

change_orders_data = [
    # PJ-HL01: 4 major change orders (Scenario 2)
    {'id': 'CO-001', 'project': 'PJ-HL01', 'wp': 'WP-02', 'contractor': 'CT-02',
     'reason': 'Brand compliance - IHG: nâng cấp spec hệ thống HVAC theo tiêu chuẩn IHG mới',
     'category': 'Brand compliance', 'amount': 22_000_000_000, 'date': '2024-04-15', 'status': 'Đã duyệt'},
    {'id': 'CO-002', 'project': 'PJ-HL01', 'wp': 'WP-03', 'contractor': 'CT-03',
     'reason': 'Brand compliance - IHG: thay đổi vật liệu lobby và hành lang theo brand standard mới',
     'category': 'Brand compliance', 'amount': 18_000_000_000, 'date': '2024-05-20', 'status': 'Đã duyệt'},
    {'id': 'CO-003', 'project': 'PJ-HL01', 'wp': 'WP-07', 'contractor': 'CT-06',
     'reason': 'Brand compliance - IHG: nâng cấp hệ thống PCCC theo tiêu chuẩn an toàn IHG',
     'category': 'Brand compliance', 'amount': 15_000_000_000, 'date': '2024-07-10', 'status': 'Đã duyệt'},
    {'id': 'CO-004', 'project': 'PJ-HL01', 'wp': 'WP-01', 'contractor': 'CT-04',
     'reason': 'Biến động giá thép Q2/2024 (+12%) - điều chỉnh đơn giá kết cấu thép',
     'category': 'Biến động giá', 'amount': 12_000_000_000, 'date': '2024-06-05', 'status': 'Đã duyệt'},

    # PJ-HL02: 2 minor
    {'id': 'CO-005', 'project': 'PJ-HL02', 'wp': 'WP-03', 'contractor': 'CT-03',
     'reason': 'Thay đổi thiết kế phòng mẫu theo yêu cầu Sailing Club',
     'category': 'Thay đổi thiết kế', 'amount': 4_500_000_000, 'date': '2024-02-18', 'status': 'Đã duyệt'},
    {'id': 'CO-006', 'project': 'PJ-HL02', 'wp': 'WP-05', 'contractor': 'CT-05',
     'reason': 'Bổ sung hạng mục cảnh quan khu vực bể bơi',
     'category': 'Thay đổi thiết kế', 'amount': 3_200_000_000, 'date': '2024-04-10', 'status': 'Đã duyệt'},

    # PJ-HL03: 1 minor
    {'id': 'CO-007', 'project': 'PJ-HL03', 'wp': 'WP-04', 'contractor': 'CT-10',
     'reason': 'Thay đổi vật liệu facade biệt thự mẫu',
     'category': 'Thay đổi thiết kế', 'amount': 2_800_000_000, 'date': '2024-01-25', 'status': 'Đã duyệt'},

    # PJ-PQ01: 3 medium
    {'id': 'CO-008', 'project': 'PJ-PQ01', 'wp': 'WP-02', 'contractor': 'CT-08',
     'reason': 'Brand compliance - Hyatt: nâng cấp hệ thống điều hòa trung tâm',
     'category': 'Brand compliance', 'amount': 12_000_000_000, 'date': '2024-03-12', 'status': 'Đã duyệt'},
    {'id': 'CO-009', 'project': 'PJ-PQ01', 'wp': 'WP-03', 'contractor': 'CT-09',
     'reason': 'Brand compliance - Hyatt: thay đổi spec nội thất phòng suite',
     'category': 'Brand compliance', 'amount': 8_500_000_000, 'date': '2024-05-08', 'status': 'Đã duyệt'},
    {'id': 'CO-010', 'project': 'PJ-PQ01', 'wp': 'WP-05', 'contractor': 'CT-17',
     'reason': 'Bổ sung cảnh quan khu vực private beach',
     'category': 'Thay đổi thiết kế', 'amount': 5_000_000_000, 'date': '2024-01-20', 'status': 'Đã duyệt'},

    # PJ-PQ02: 1 small
    {'id': 'CO-011', 'project': 'PJ-PQ02', 'wp': 'WP-01', 'contractor': 'CT-07',
     'reason': 'Điều chỉnh thiết kế móng bể sóng do địa chất',
     'category': 'Khác', 'amount': 3_500_000_000, 'date': '2024-06-25', 'status': 'Đã duyệt'},

    # PJ-HN01: 2 small
    {'id': 'CO-012', 'project': 'PJ-HN01', 'wp': 'WP-08', 'contractor': 'CT-13',
     'reason': 'Bổ sung hạ tầng kết nối giao thông theo yêu cầu quy hoạch quận',
     'category': 'Khác', 'amount': 4_200_000_000, 'date': '2024-03-15', 'status': 'Đã duyệt'},
    {'id': 'CO-013', 'project': 'PJ-HN01', 'wp': 'WP-01', 'contractor': 'CT-13',
     'reason': 'Điều chỉnh thiết kế tầng hầm do mực nước ngầm cao',
     'category': 'Khác', 'amount': 3_800_000_000, 'date': '2024-04-20', 'status': 'Đã duyệt'},

    # PJ-LA01: 2 small
    {'id': 'CO-014', 'project': 'PJ-LA01', 'wp': 'WP-02', 'contractor': 'CT-15',
     'reason': 'Nâng cấp hệ thống M&E theo tiêu chuẩn mới của Lào',
     'category': 'Khác', 'amount': 2_500_000_000, 'date': '2024-02-28', 'status': 'Đã duyệt'},
    {'id': 'CO-015', 'project': 'PJ-LA01', 'wp': 'WP-04', 'contractor': 'CT-10',
     'reason': 'Thay đổi vật liệu mặt ngoài do nhập khẩu chậm',
     'category': 'Khác', 'amount': 1_800_000_000, 'date': '2024-05-15', 'status': 'Đã duyệt'},

    # Additional small change orders for realism
    {'id': 'CO-016', 'project': 'PJ-HL01', 'wp': 'WP-05', 'contractor': 'CT-05',
     'reason': 'Bổ sung hệ thống tưới tự động khu vực cảnh quan resort',
     'category': 'Thay đổi thiết kế', 'amount': 3_500_000_000, 'date': '2024-03-28', 'status': 'Đã duyệt'},
    {'id': 'CO-017', 'project': 'PJ-HL01', 'wp': 'WP-06', 'contractor': 'CT-12',
     'reason': 'Nâng cấp hệ thống xử lý nước thải theo quy chuẩn mới',
     'category': 'Khác', 'amount': 4_800_000_000, 'date': '2024-06-18', 'status': 'Đã duyệt'},
    {'id': 'CO-018', 'project': 'PJ-PQ01', 'wp': 'WP-01', 'contractor': 'CT-07',
     'reason': 'Gia cố móng khu Residences do thay đổi tải trọng thiết kế',
     'category': 'Thay đổi thiết kế', 'amount': 6_200_000_000, 'date': '2023-08-15', 'status': 'Đã duyệt'},
    {'id': 'CO-019', 'project': 'PJ-HL02', 'wp': 'WP-01', 'contractor': 'CT-01',
     'reason': 'Biến động giá thép Q2/2024 - điều chỉnh đơn giá',
     'category': 'Biến động giá', 'amount': 3_800_000_000, 'date': '2024-05-25', 'status': 'Đã duyệt'},
    {'id': 'CO-020', 'project': 'PJ-HL03', 'wp': 'WP-03', 'contractor': 'CT-14',
     'reason': 'Nâng cấp nội thất biệt thự mẫu theo phản hồi khách hàng',
     'category': 'Thay đổi thiết kế', 'amount': 2_200_000_000, 'date': '2024-03-10', 'status': 'Đã duyệt'},
    {'id': 'CO-021', 'project': 'PJ-PQ02', 'wp': 'WP-08', 'contractor': 'CT-18',
     'reason': 'Bổ sung đường nội bộ kết nối khu vực water park',
     'category': 'Thay đổi thiết kế', 'amount': 2_000_000_000, 'date': '2024-06-28', 'status': 'Cho duyệt'},
    {'id': 'CO-022', 'project': 'PJ-HN01', 'wp': 'WP-06', 'contractor': 'CT-12',
     'reason': 'Bổ sung hệ thống thoát nước mưa theo thiết kế điều chỉnh',
     'category': 'Thay đổi thiết kế', 'amount': 2_500_000_000, 'date': '2024-05-10', 'status': 'Đã duyệt'},
    {'id': 'CO-023', 'project': 'PJ-LA01', 'wp': 'WP-03', 'contractor': 'CT-09',
     'reason': 'Thay đổi spec nội thất sảnh chính theo yêu cầu chủ đầu tư',
     'category': 'Thay đổi thiết kế', 'amount': 1_500_000_000, 'date': '2024-04-08', 'status': 'Đã duyệt'},
]

# --------------------------------------------------------------------------
# 4. MATERIAL PRICES
# --------------------------------------------------------------------------
print("Generating material_prices...")

# Base prices (Jan 2023)
BASE_PRICES = {
    'MAT-01': 14_800,    # Thep (VND/kg)
    'MAT-02': 1_650_000, # Xi mang (VND/tan)
    'MAT-03': 280_000,   # Cat (VND/m3)
    'MAT-04': 185_000,   # Gach op lat (VND/m2)
    'MAT-05': 12_500_000,# Go noi that (VND/m3)
    'MAT-06': 850_000,   # Kinh cuong luc (VND/m2)
}

# Steel price trajectory (anomaly: +12% in Q2/2024)
STEEL_TRAJECTORY = {
    '2023-01': 14800, '2023-02': 14900, '2023-03': 15000,
    '2023-04': 15100, '2023-05': 15200, '2023-06': 15300,
    '2023-07': 15200, '2023-08': 15100, '2023-09': 15200,
    '2023-10': 15300, '2023-11': 15400, '2023-12': 15500,
    '2024-01': 15500, '2024-02': 15600, '2024-03': 16200,
    '2024-04': 17000, '2024-05': 17200, '2024-06': 17360,
}

for mat_id, base_price in BASE_PRICES.items():
    for period in PERIODS:
        if mat_id == 'MAT-01':
            price = STEEL_TRAJECTORY[period]
        else:
            # Normal fluctuation ±3% with slight upward trend
            month_idx = PERIODS.index(period)
            trend = 1.0 + 0.003 * month_idx  # ~0.3%/month = ~3.6%/year
            price = base_price * trend * noise(0.97, 1.03)

        material_prices_data.append({
            'material_id': mat_id,
            'period': period,
            'price': round(price),
        })

# --------------------------------------------------------------------------
# 5. HOSPITALITY REVENUE
# --------------------------------------------------------------------------
print("Generating hospitality_revenue...")

for prop_id, cfg in PROPERTIES.items():
    rooms = cfg['rooms']
    cluster = cfg['cluster']
    base_adr = cfg['base_adr']
    base_occ = cfg['base_occ']
    adr_low, adr_high = cfg['adr_range']
    seasonality = OCCUPANCY_SEASONALITY[cluster]

    for period in PERIODS:
        year = int(period[:4])
        month = int(period[5:])
        dim = days_in_month(year, month)

        rooms_available = rooms * dim

        # Occupancy with seasonality
        seasonal_factor = seasonality[month]
        # YoY growth
        year_factor = 1.0 if year == 2023 else 1.08
        occ_rate = base_occ * seasonal_factor * year_factor * noise(0.95, 1.05)
        occ_rate = min(max(occ_rate, 0.20), 0.98)

        rooms_sold = round(rooms_available * occ_rate)

        # ADR with seasonality (higher in peak)
        adr_seasonal = base_adr * (0.7 + 0.3 * seasonal_factor)
        adr_seasonal = max(adr_low, min(adr_high, adr_seasonal))
        adr = round(adr_seasonal * noise(0.95, 1.05))

        room_revenue = rooms_sold * adr
        fnb_revenue = round(room_revenue * 0.30 * noise(0.90, 1.10))
        other_revenue = round(room_revenue * 0.10 * noise(0.85, 1.15))
        total_revenue = room_revenue + fnb_revenue + other_revenue

        hospitality_revenue_data.append({
            'property_id': prop_id,
            'period': period,
            'room_revenue': room_revenue,
            'fnb_revenue': fnb_revenue,
            'other_revenue': other_revenue,
            'total_revenue': total_revenue,
            'rooms_available': rooms_available,
            'rooms_sold': rooms_sold,
            'avg_daily_rate': adr,
        })

# --------------------------------------------------------------------------
# 6. HOSPITALITY COSTS
# --------------------------------------------------------------------------
print("Generating hospitality_costs...")

for rev in hospitality_revenue_data:
    prop_id = rev['property_id']
    period = rev['period']
    total_rev = rev['total_revenue']

    prop_ratios = PROPERTY_COST_RATIOS[prop_id]

    for cat in COST_CATEGORIES:
        ratio = prop_ratios[cat] * noise(0.95, 1.05)
        cost = round(total_rev * ratio)

        hospitality_costs_data.append({
            'property_id': prop_id,
            'period': period,
            'cost_category': cat,
            'cost_amount': cost,
        })

# --------------------------------------------------------------------------
# 7. OCCUPANCY DAILY
# --------------------------------------------------------------------------
print("Generating occupancy_daily...")

for prop_id, cfg in PROPERTIES.items():
    rooms = cfg['rooms']
    cluster = cfg['cluster']
    base_occ = cfg['base_occ']
    base_adr = cfg['base_adr']
    adr_low, adr_high = cfg['adr_range']
    seasonality = OCCUPANCY_SEASONALITY[cluster]

    current = START_DATE
    while current <= END_DATE:
        month = current.month
        year = current.year
        weekday = current.weekday()

        # Occupancy: monthly × weekly × noise × Tet boost × YoY
        monthly_s = seasonality[month]
        weekly_s = WEEKLY_SEASONALITY[weekday]
        year_factor = 1.0 if year == 2023 else 1.08
        tet_boost = 1.30 if is_tet_period(current) else 1.0

        occ = base_occ * monthly_s * weekly_s * year_factor * tet_boost * noise(0.90, 1.10)
        occ = min(max(occ, 0.10), 0.99)

        rooms_sold = round(rooms * occ)
        rooms_sold = min(rooms_sold, rooms)

        # ADR
        adr_seasonal = base_adr * (0.7 + 0.3 * monthly_s) * (1.15 if is_tet_period(current) else 1.0)
        adr = round(max(adr_low, min(adr_high, adr_seasonal * noise(0.95, 1.05))))

        occupancy_daily_data.append({
            'property_id': prop_id,
            'date': current.isoformat(),
            'rooms_available': rooms,
            'rooms_sold': rooms_sold,
            'avg_rate': adr,
        })

        current += timedelta(days=1)

# ============================================================================
# WRITE SQL FILE
# ============================================================================
print(f"\nRecord counts:")
print(f"  budget_disbursements: {len(budget_disbursements)}")
print(f"  construction_costs: {len(construction_costs)}")
print(f"  change_orders: {len(change_orders_data)}")
print(f"  material_prices: {len(material_prices_data)}")
print(f"  hospitality_revenue: {len(hospitality_revenue_data)}")
print(f"  hospitality_costs: {len(hospitality_costs_data)}")
print(f"  occupancy_daily: {len(occupancy_daily_data)}")
print(f"  TOTAL: {len(budget_disbursements) + len(construction_costs) + len(change_orders_data) + len(material_prices_data) + len(hospitality_revenue_data) + len(hospitality_costs_data) + len(occupancy_daily_data)}")

print("\nWriting 04_transaction_data.sql...")

with open('04_transaction_data.sql', 'w', encoding='utf-8') as f:
    f.write("-- ============================================================================\n")
    f.write("-- BIM Group Real Estate & Construction Demo - Transaction Data\n")
    f.write("-- Mo ta: Insert fact tables (budget, construction, hospitality, occupancy...)\n")
    f.write("-- Database: bim_realestate_demo\n")
    f.write("-- Generated by generate_transactions.py\n")
    f.write("-- ============================================================================\n\n")
    f.write("USE bim_realestate_demo;\n\n")

    # --- budget_disbursements ---
    f.write("-- ============================================================================\n")
    f.write("-- BUDGET_DISBURSEMENTS\n")
    f.write("-- ============================================================================\n\n")

    batch = []
    for r in budget_disbursements:
        batch.append(f"({sql_val(r['project_id'])}, {sql_val(r['period'])}, "
                     f"{r['planned_amount']}, {r['actual_amount']}, "
                     f"{r['cumulative_planned']}, {r['cumulative_actual']})")
        if len(batch) >= 500:
            f.write("INSERT INTO budget_disbursements (project_id, period, planned_amount, actual_amount, cumulative_planned, cumulative_actual) VALUES\n")
            f.write(",\n".join(batch) + ";\n\n")
            batch = []
    if batch:
        f.write("INSERT INTO budget_disbursements (project_id, period, planned_amount, actual_amount, cumulative_planned, cumulative_actual) VALUES\n")
        f.write(",\n".join(batch) + ";\n\n")

    # --- construction_costs ---
    f.write("-- ============================================================================\n")
    f.write("-- CONSTRUCTION_COSTS\n")
    f.write("-- ============================================================================\n\n")

    batch = []
    for r in construction_costs:
        batch.append(f"({sql_val(r['project_id'])}, {sql_val(r['work_package_id'])}, "
                     f"{sql_val(r['contractor_id'])}, {sql_val(r['period'])}, "
                     f"{r['budgeted_cost']}, {r['actual_cost']})")
        if len(batch) >= 500:
            f.write("INSERT INTO construction_costs (project_id, work_package_id, contractor_id, period, budgeted_cost, actual_cost) VALUES\n")
            f.write(",\n".join(batch) + ";\n\n")
            batch = []
    if batch:
        f.write("INSERT INTO construction_costs (project_id, work_package_id, contractor_id, period, budgeted_cost, actual_cost) VALUES\n")
        f.write(",\n".join(batch) + ";\n\n")

    # --- change_orders ---
    f.write("-- ============================================================================\n")
    f.write("-- CHANGE_ORDERS\n")
    f.write("-- ============================================================================\n\n")

    f.write("INSERT INTO change_orders (change_order_id, project_id, work_package_id, contractor_id, reason, reason_category, amount, order_date, status) VALUES\n")
    co_vals = []
    for r in change_orders_data:
        co_vals.append(f"({sql_val(r['id'])}, {sql_val(r['project'])}, {sql_val(r['wp'])}, "
                       f"{sql_val(r['contractor'])}, {sql_val(r['reason'])}, {sql_val(r['category'])}, "
                       f"{r['amount']}, {sql_val(r['date'])}, {sql_val(r['status'])})")
    f.write(",\n".join(co_vals) + ";\n\n")

    # --- material_prices ---
    f.write("-- ============================================================================\n")
    f.write("-- MATERIAL_PRICES\n")
    f.write("-- ============================================================================\n\n")

    f.write("INSERT INTO material_prices (material_id, period, price) VALUES\n")
    mp_vals = []
    for r in material_prices_data:
        mp_vals.append(f"({sql_val(r['material_id'])}, {sql_val(r['period'])}, {r['price']})")
    f.write(",\n".join(mp_vals) + ";\n\n")

    # --- hospitality_revenue ---
    f.write("-- ============================================================================\n")
    f.write("-- HOSPITALITY_REVENUE\n")
    f.write("-- ============================================================================\n\n")

    f.write("INSERT INTO hospitality_revenue (property_id, period, room_revenue, fnb_revenue, other_revenue, total_revenue, rooms_available, rooms_sold, avg_daily_rate) VALUES\n")
    hr_vals = []
    for r in hospitality_revenue_data:
        hr_vals.append(f"({sql_val(r['property_id'])}, {sql_val(r['period'])}, "
                       f"{r['room_revenue']}, {r['fnb_revenue']}, {r['other_revenue']}, {r['total_revenue']}, "
                       f"{r['rooms_available']}, {r['rooms_sold']}, {r['avg_daily_rate']})")
    f.write(",\n".join(hr_vals) + ";\n\n")

    # --- hospitality_costs ---
    f.write("-- ============================================================================\n")
    f.write("-- HOSPITALITY_COSTS\n")
    f.write("-- ============================================================================\n\n")

    batch = []
    for r in hospitality_costs_data:
        batch.append(f"({sql_val(r['property_id'])}, {sql_val(r['period'])}, "
                     f"{sql_val(r['cost_category'])}, {r['cost_amount']})")
        if len(batch) >= 500:
            f.write("INSERT INTO hospitality_costs (property_id, period, cost_category, cost_amount) VALUES\n")
            f.write(",\n".join(batch) + ";\n\n")
            batch = []
    if batch:
        f.write("INSERT INTO hospitality_costs (property_id, period, cost_category, cost_amount) VALUES\n")
        f.write(",\n".join(batch) + ";\n\n")

    # --- occupancy_daily ---
    f.write("-- ============================================================================\n")
    f.write("-- OCCUPANCY_DAILY\n")
    f.write("-- ============================================================================\n\n")

    batch = []
    for r in occupancy_daily_data:
        batch.append(f"({sql_val(r['property_id'])}, {sql_val(r['date'])}, "
                     f"{r['rooms_available']}, {r['rooms_sold']}, {r['avg_rate']})")
        if len(batch) >= 1000:
            f.write("INSERT INTO occupancy_daily (property_id, date, rooms_available, rooms_sold, avg_rate) VALUES\n")
            f.write(",\n".join(batch) + ";\n\n")
            batch = []
    if batch:
        f.write("INSERT INTO occupancy_daily (property_id, date, rooms_available, rooms_sold, avg_rate) VALUES\n")
        f.write(",\n".join(batch) + ";\n\n")

print("Done! 04_transaction_data.sql generated.")
