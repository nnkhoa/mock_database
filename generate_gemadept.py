#!/usr/bin/env python3
"""
Gemadept Seaport Demo — Transaction Data Generator
Generates 18 months of data (2024-01 to 2025-06) for seaport_demo database.
3 layers: Base volume → Seasonality → Anomaly injection
"""

import random
import math
import os
from datetime import date, datetime, timedelta
from collections import defaultdict

import mysql.connector

random.seed(42)

# =============================================================================
# CONFIG
# =============================================================================
DB_CONFIG = dict(host='localhost', port=3306, user='root', password='root', database='seaport_demo')
MONTHS = [date(y, m, 1) for y in (2024, 2025) for m in range(1, 13) if date(y, m, 1) <= date(2025, 6, 1)]
SQL_OUT = os.path.join(os.path.dirname(__file__), 'gemadept_sql', '04_transaction_data.sql')

PORTS = ['NDV', 'GML', 'PHL', 'DQT']
CARGO_TYPES = ['container_20ft', 'container_40ft', 'reefer', 'bulk', 'breakbulk', 'oog']
COST_TYPES = ['labor', 'depreciation', 'maintenance', 'energy', 'land_lease', 'other']

# =============================================================================
# LAYER 1 — BASE VOLUMES
# =============================================================================
base_monthly_revenue = {'NDV': 200e9, 'GML': 130e9, 'PHL': 22e9, 'DQT': 15e9}
base_monthly_teu = {'NDV': 115_000, 'GML': 130_000, 'PHL': 40_000, 'DQT': 0}
base_monthly_bulk_tons = {'NDV': 15_000, 'GML': 0, 'PHL': 0, 'DQT': 160_000}

revenue_mix = {
    'NDV': {'container_20ft': 0.35, 'container_40ft': 0.30, 'reefer': 0.08, 'bulk': 0.15, 'breakbulk': 0.07, 'oog': 0.05},
    'GML': {'container_20ft': 0.25, 'container_40ft': 0.40, 'reefer': 0.12, 'bulk': 0.02, 'breakbulk': 0.01, 'oog': 0.20},
    'PHL': {'container_20ft': 0.45, 'container_40ft': 0.35, 'reefer': 0.05, 'bulk': 0.05, 'breakbulk': 0.05, 'oog': 0.05},
    'DQT': {'container_20ft': 0.02, 'container_40ft': 0.01, 'reefer': 0.00, 'bulk': 0.80, 'breakbulk': 0.15, 'oog': 0.02},
}

avg_rev_per_unit = {
    'container_20ft': 1_400_000, 'container_40ft': 2_200_000, 'reefer': 2_800_000,
    'bulk': 45_000, 'breakbulk': 65_000, 'oog': 4_500_000,
}

# Revenue per TEU multiplier (port-specific pricing)
port_rev_per_teu = {'NDV': 1_650_000, 'GML': 2_100_000, 'PHL': 1_200_000, 'DQT': 0}

cost_structure = {
    'NDV': {'labor': 0.32, 'depreciation': 0.22, 'maintenance': 0.10, 'energy': 0.13, 'land_lease': 0.08, 'other': 0.15},
    'GML': {'labor': 0.28, 'depreciation': 0.27, 'maintenance': 0.11, 'energy': 0.14, 'land_lease': 0.06, 'other': 0.14},
    'PHL': {'labor': 0.35, 'depreciation': 0.18, 'maintenance': 0.09, 'energy': 0.12, 'land_lease': 0.10, 'other': 0.16},
    'DQT': {'labor': 0.30, 'depreciation': 0.20, 'maintenance': 0.12, 'energy': 0.15, 'land_lease': 0.07, 'other': 0.16},
}

target_gross_margin = {'NDV': 0.49, 'GML': 0.50, 'PHL': 0.38, 'DQT': 0.35}

# Shipping line distribution per port
sl_dist = {
    'NDV': {'MAERSK': 0.22, 'CMA_CGM': 0.18, 'MSC': 0.12, 'HMM': 0.08, 'ONE': 0.07,
            'WANHAI': 0.07, 'SITC': 0.06, 'EVERGREEN': 0.05, 'YANGMING': 0.04,
            'TS_LINES': 0.03, 'ZIM': 0.03, 'PIL': 0.02, 'COSCO': 0.02, 'HAPAG': 0.01},
    'GML': {'CMA_CGM': 0.35, 'MSC': 0.15, 'MAERSK': 0.12, 'EVERGREEN': 0.10, 'ONE': 0.06,
            'COSCO': 0.06, 'HAPAG': 0.05, 'YANGMING': 0.04, 'HMM': 0.03, 'ZIM': 0.02,
            'PIL': 0.01, 'WANHAI': 0.01},
    'PHL': {'CMA_CGM': 0.25, 'WANHAI': 0.20, 'SITC': 0.18, 'TS_LINES': 0.12, 'MAERSK': 0.08,
            'MSC': 0.05, 'PIL': 0.05, 'ONE': 0.03, 'EVERGREEN': 0.02, 'HMM': 0.01, 'YANGMING': 0.01},
    'DQT': {'OTHER': 1.0},
}

# Vessel call parameters per port
vessel_params = {
    'NDV': {'calls_per_month': 120, 'min_teu': 1000, 'max_teu': 5000, 'turnaround_mean': 18, 'turnaround_std': 4},
    'GML': {'calls_per_month': 60, 'min_teu': 8000, 'max_teu': 24000, 'turnaround_mean': 22, 'turnaround_std': 5},
    'PHL': {'calls_per_month': 80, 'min_teu': 500, 'max_teu': 2000, 'turnaround_mean': 12, 'turnaround_std': 3},
    'DQT': {'calls_per_month': 25, 'min_teu': 0, 'max_teu': 0, 'turnaround_mean': 36, 'turnaround_std': 8},
}

# Equipment crane productivity (moves/hour)
crane_productivity = {
    'STS': {'NDV': 28, 'GML': 32, 'PHL': 0, 'DQT': 0},
    'RTG': {'NDV': 18, 'GML': 20, 'PHL': 0, 'DQT': 0},
    'FCC': {'NDV': 0, 'GML': 0, 'PHL': 22, 'DQT': 0},
    'MHC': {'NDV': 15, 'GML': 0, 'PHL': 0, 'DQT': 12},
    'GSU': {'NDV': 0, 'GML': 0, 'PHL': 0, 'DQT': 0},
    'Conveyor': {'NDV': 0, 'GML': 0, 'PHL': 0, 'DQT': 0},
    'Reachstacker': {'NDV': 0, 'GML': 0, 'PHL': 12, 'DQT': 0},
}

# =============================================================================
# LAYER 2 — SEASONALITY
# =============================================================================
monthly_seasonality = {
    1: 0.78, 2: 0.82, 3: 0.95, 4: 1.00, 5: 1.02, 6: 1.05,
    7: 1.12, 8: 1.18, 9: 1.15, 10: 1.08, 11: 1.02, 12: 0.93,
}

category_seasonality = {
    'reefer': {1: 0.85, 2: 0.80, 3: 0.90, 4: 0.95, 5: 1.05, 6: 1.15, 7: 1.20, 8: 1.25, 9: 1.15, 10: 1.05, 11: 0.90, 12: 0.85},
    'bulk':   {1: 0.70, 2: 0.75, 3: 1.00, 4: 1.05, 5: 1.10, 6: 1.05, 7: 1.00, 8: 1.05, 9: 1.10, 10: 1.15, 11: 1.05, 12: 0.90},
}

YOY_GROWTH = 0.22

def growth_factor(month_idx):
    """month_idx 0..17 → linear growth from 1.0 to ~1.22"""
    return 1.0 + (YOY_GROWTH / 17) * month_idx

def seasonal_factor(m, cargo_type=None):
    base = monthly_seasonality[m.month]
    if cargo_type in category_seasonality:
        base *= category_seasonality[cargo_type][m.month]
    return base

def noise(lo=0.95, hi=1.05):
    return random.uniform(lo, hi)

def round_vnd(v):
    """Round to nearest million"""
    return int(round(v / 1_000_000)) * 1_000_000

# =============================================================================
# LAYER 3 — ANOMALY FLAGS
# =============================================================================
def is_anomaly_2a(port, cost_type, m):
    """Maintenance spike NDV May-Jun 2025"""
    if port == 'NDV' and cost_type == 'maintenance':
        if m == date(2025, 5, 1): return 2.5
        if m == date(2025, 6, 1): return 2.8
    return 1.0

def is_anomaly_2b(port, cargo, m):
    """Bulk volume increase NDV May-Jun 2025"""
    if port == 'NDV' and cargo == 'bulk':
        if m == date(2025, 5, 1): return 1.60
        if m == date(2025, 6, 1): return 1.85
    return 1.0

def is_anomaly_2c(cost_type, m):
    """Energy cost +12% from Apr 2025 for all ports"""
    if cost_type == 'energy' and m >= date(2025, 4, 1):
        return 1.12
    return 1.0

def is_anomaly_4a(port, sl, m):
    """Maersk volume decline at NDV Apr-Jun 2025"""
    if port == 'NDV' and sl == 'MAERSK':
        if m == date(2025, 4, 1): return 0.90
        if m == date(2025, 5, 1): return 0.85
        if m == date(2025, 6, 1): return 0.82
    return 1.0

# =============================================================================
# GENERATION FUNCTIONS
# =============================================================================

def gen_port_revenue():
    """Generate port_revenue records: port × month × cargo_type"""
    rows = []
    for mi, m in enumerate(MONTHS):
        for port in PORTS:
            base_rev = base_monthly_revenue[port]
            gf = growth_factor(mi)
            sf = seasonal_factor(m)
            port_total_rev = base_rev * gf * sf * noise(0.96, 1.04)

            for cargo in CARGO_TYPES:
                share = revenue_mix[port].get(cargo, 0)
                if share == 0:
                    continue
                cat_sf = seasonal_factor(m, cargo) / sf  # additional category factor
                rev = port_total_rev * share * cat_sf * noise(0.93, 1.07)

                # Anomaly 2B: bulk volume increase at NDV → also increases bulk revenue
                anom_2b = is_anomaly_2b(port, cargo, m)
                rev *= anom_2b

                rev = round_vnd(rev)
                unit_price = avg_rev_per_unit[cargo]

                if cargo in ('bulk', 'breakbulk'):
                    vol_tons = max(1, int(rev / unit_price))
                    vol_teu = 0
                else:
                    vol_teu = max(1, int(rev / unit_price))
                    vol_tons = 0
                    if cargo == 'container_40ft':
                        vol_teu = max(1, vol_teu)  # FEU count, each = 2 TEU equiv

                rows.append((port, m, cargo, vol_teu, vol_tons, unit_price, rev))
    return rows

def gen_container_throughput(port_revenue_rows):
    """Derive container_throughput from port_revenue (same volumes)"""
    rows = []
    for (port, m, cargo, vol_teu, vol_tons, _, _) in port_revenue_rows:
        rows.append((port, m, cargo, vol_teu, vol_tons))
    return rows

def gen_operating_costs(port_revenue_rows):
    """Generate operating_costs: port × month × cost_type"""
    # First aggregate revenue by port×month
    port_month_rev = defaultdict(int)
    for (port, m, cargo, _, _, _, rev) in port_revenue_rows:
        port_month_rev[(port, m)] += rev

    rows = []
    for mi, m in enumerate(MONTHS):
        for port in PORTS:
            total_rev = port_month_rev.get((port, m), 0)
            if total_rev == 0:
                continue
            total_cost = total_rev * (1 - target_gross_margin[port])

            for ct in COST_TYPES:
                share = cost_structure[port][ct]
                cost = total_cost * share * noise(0.96, 1.04)

                # Anomaly 2A: maintenance spike
                cost *= is_anomaly_2a(port, ct, m)
                # Anomaly 2C: energy step change
                cost *= is_anomaly_2c(ct, m)

                rows.append((port, m, ct, round_vnd(cost)))
    return rows

def gen_shipping_line_revenue(port_revenue_rows):
    """Generate shipping_line_revenue: port × month × shipping_line"""
    # Aggregate TEU and revenue by port×month
    port_month_rev = defaultdict(int)
    port_month_teu = defaultdict(int)
    for (port, m, cargo, vol_teu, vol_tons, _, rev) in port_revenue_rows:
        port_month_rev[(port, m)] += rev
        port_month_teu[(port, m)] += vol_teu

    rows = []
    for mi, m in enumerate(MONTHS):
        for port in PORTS:
            total_rev = port_month_rev.get((port, m), 0)
            total_teu = port_month_teu.get((port, m), 0)
            if total_rev == 0:
                continue

            dist = sl_dist.get(port, {})
            for sl, share in dist.items():
                if share <= 0:
                    continue
                sl_rev = total_rev * share * noise(0.95, 1.05)
                sl_teu = int(total_teu * share * noise(0.95, 1.05))

                # Anomaly 4A: Maersk decline at NDV
                anom = is_anomaly_4a(port, sl, m)
                sl_rev *= anom
                sl_teu = int(sl_teu * anom)

                # Estimate vessel calls
                vp = vessel_params[port]
                base_calls = max(1, int(vp['calls_per_month'] * share))
                # Anomaly 4A vessel calls
                if port == 'NDV' and sl == 'MAERSK':
                    if m == date(2025, 4, 1): base_calls = 7
                    elif m == date(2025, 5, 1): base_calls = 6
                    elif m == date(2025, 6, 1): base_calls = 6
                    elif m >= date(2024, 1, 1): base_calls = 8

                rows.append((port, m, sl, max(1, sl_teu), round_vnd(sl_rev), base_calls))
    return rows

# Vessel name pools
_vessel_prefixes = {
    'CMA_CGM': ['CMA CGM', 'APL'],
    'MAERSK': ['Maersk', 'Sealand'],
    'MSC': ['MSC'],
    'EVERGREEN': ['Ever'],
    'ONE': ['ONE'],
    'HMM': ['HMM'],
    'YANGMING': ['YM'],
    'ZIM': ['ZIM'],
    'WANHAI': ['Wan Hai'],
    'SITC': ['SITC'],
    'COSCO': ['COSCO'],
    'PIL': ['Kota'],
    'HAPAG': ['Hapag'],
    'TS_LINES': ['TS'],
    'OTHER': ['MV'],
}
_vessel_suffixes = [
    'Fortuna', 'Liberty', 'Harmony', 'Phoenix', 'Meridian', 'Voyager', 'Pioneer',
    'Explorer', 'Titan', 'Atlas', 'Eagle', 'Star', 'Dragon', 'Pearl', 'Jade',
    'Coral', 'Sapphire', 'Ruby', 'Diamond', 'Emerald', 'Horizon', 'Aurora',
    'Neptune', 'Poseidon', 'Zeus', 'Apollo', 'Venus', 'Mars', 'Saturn', 'Jupiter',
    'Orion', 'Sirius', 'Vega', 'Altair', 'Rigel', 'Polaris', 'Deneb', 'Antares',
    'Bangkok', 'Saigon', 'Haiphong', 'Singapore', 'Shanghai', 'Tokyo', 'Seoul',
    'Mumbai', 'Jakarta', 'Manila', 'Colombo', 'Busan', 'Kaohsiung', 'Laem Chabang',
]

def _vessel_name(sl):
    prefixes = _vessel_prefixes.get(sl, ['MV'])
    return f"{random.choice(prefixes)} {random.choice(_vessel_suffixes)}"

def gen_vessel_calls(shipping_line_rev_rows):
    """Generate individual vessel call events"""
    rows = []
    # Group by port×month×sl to get call counts
    call_map = {}
    for (port, m, sl, teu, rev, calls) in shipping_line_rev_rows:
        call_map[(port, m, sl)] = (calls, teu)

    for (port, m, sl), (num_calls, total_teu) in call_map.items():
        vp = vessel_params[port]
        for _ in range(num_calls):
            # Random day within month
            days_in_month = 28 if m.month == 2 else (30 if m.month in (4, 6, 9, 11) else 31)
            day = random.randint(1, days_in_month)
            hour = random.randint(0, 23)
            minute = random.randint(0, 59)
            try:
                arrival = datetime(m.year, m.month, day, hour, minute)
            except ValueError:
                arrival = datetime(m.year, m.month, min(day, 28), hour, minute)

            turnaround = max(4, random.gauss(vp['turnaround_mean'], vp['turnaround_std']))
            departure = arrival + timedelta(hours=turnaround)

            if port == 'DQT':
                # Bulk vessel — DWT based
                capacity = random.randint(10000, 50000)
                actual_vol = int(capacity * random.uniform(0.6, 0.9))
                cargo_handled = random.choice(['bulk', 'bulk,breakbulk', 'breakbulk'])
            else:
                capacity = random.randint(vp['min_teu'], vp['max_teu'])
                # Distribute total TEU across calls
                avg_per_call = max(100, total_teu // max(1, num_calls))
                actual_vol = int(avg_per_call * noise(0.7, 1.3))
                actual_vol = min(actual_vol, capacity)
                cargo_handled = random.choice([
                    'container_20ft,container_40ft',
                    'container_20ft,container_40ft,reefer',
                    'container_20ft,container_40ft,oog',
                ])

            vname = _vessel_name(sl)
            rows.append((port, sl, vname, capacity, actual_vol,
                         arrival, departure, round(turnaround, 1), cargo_handled))
    return rows

def gen_equipment_utilization():
    """Generate equipment_utilization: equipment × month"""
    # Get equipment list from DB
    conn = mysql.connector.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT equipment_id, equipment_type, port_id FROM equipment")
    equip_list = cur.fetchall()
    cur.close()
    conn.close()

    rows = []
    for mi, m in enumerate(MONTHS):
        sf = monthly_seasonality[m.month]
        for (eid, etype, port) in equip_list:
            total_hours = 720

            # Base operating hours
            if etype in ('STS', 'RTG', 'FCC'):
                base_op = random.uniform(580, 650)
            elif etype == 'MHC':
                base_op = random.uniform(520, 600)
            else:
                base_op = random.uniform(450, 550)

            op_hours = int(base_op * sf * noise(0.95, 1.05))

            # Maintenance hours
            maint_hours = random.randint(15, 40)

            # Anomaly: STS-NDV-03/04 major overhaul May/Jun 2025
            if eid == 'STS-NDV-03' and m == date(2025, 5, 1):
                maint_hours = 360  # ~15 days
                op_hours = min(op_hours, total_hours - maint_hours - 20)
            elif eid == 'STS-NDV-04' and m == date(2025, 6, 1):
                maint_hours = 432  # ~18 days
                op_hours = min(op_hours, total_hours - maint_hours - 20)

            op_hours = max(50, min(op_hours, total_hours - maint_hours - 10))
            idle_hours = total_hours - op_hours - maint_hours
            idle_hours = max(0, idle_hours)

            # Moves count (cranes only)
            prod = crane_productivity.get(etype, {}).get(port, 0)
            if prod > 0:
                moves = int(op_hours * prod * noise(0.92, 1.08))
                prod_actual = round(moves / max(1, op_hours), 1)
            else:
                moves = 0
                prod_actual = 0

            avail = round((total_hours - maint_hours) / total_hours * 100, 2)

            rows.append((eid, port, m, total_hours, op_hours, idle_hours,
                         maint_hours, moves if moves > 0 else None,
                         avail, prod_actual if prod_actual > 0 else None))
    return rows

def gen_equipment_maintenance():
    """Generate routine + anomaly maintenance events"""
    conn = mysql.connector.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT equipment_id, equipment_type, port_id FROM equipment")
    equip_list = cur.fetchall()
    cur.close()
    conn.close()

    rows = []
    for (eid, etype, port) in equip_list:
        # Routine inspections: ~1-2 per quarter
        for q_start_month in range(0, 18, 3):
            m = MONTHS[min(q_start_month, 17)]
            num_inspections = random.randint(1, 2)
            for _ in range(num_inspections):
                offset_days = random.randint(0, 80)
                sd = date(2024, 1, 1) + timedelta(days=q_start_month * 30 + offset_days)
                if sd > date(2025, 6, 30):
                    continue
                ed = sd + timedelta(days=random.randint(1, 3))
                cost = random.randint(50, 200) * 1_000_000
                rows.append((eid, port, 'inspection', sd, ed, cost,
                             f'Kiểm tra định kỳ {eid}'))

        # Routine maintenance: ~1 per 4-6 months
        for offset in range(0, 18, random.randint(4, 6)):
            if offset >= len(MONTHS):
                break
            m = MONTHS[offset]
            sd = date(m.year, m.month, random.randint(5, 20))
            ed = sd + timedelta(days=random.randint(3, 7))
            cost = random.randint(200, 800) * 1_000_000
            rows.append((eid, port, 'routine', sd, ed, cost,
                         f'Bảo trì định kỳ {eid} — kiểm tra và thay thế phụ tùng'))

    # Anomaly maintenance records
    rows.append(('STS-NDV-03', 'NDV', 'major_overhaul',
                 date(2025, 5, 10), date(2025, 5, 25), 8_500_000_000,
                 'Đại tu cẩu STS #3 — thay thế cáp nâng và hệ thống thủy lực'))
    rows.append(('STS-NDV-04', 'NDV', 'major_overhaul',
                 date(2025, 6, 1), date(2025, 6, 18), 9_200_000_000,
                 'Đại tu cẩu STS #4 — thay thế motor hoisting và trolley'))

    return rows

def gen_customer_revenue(port_revenue_rows):
    """Generate customer_revenue: port × month × customer (Pareto distribution)"""
    # Get customers
    conn = mysql.connector.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT customer_id, primary_port_id, cargo_type_preference FROM customers")
    customers = cur.fetchall()
    cur.close()
    conn.close()

    # Group customers by port affinity
    port_customers = defaultdict(list)
    multi_port_customers = {
        'SAMSUNG_VN': ['NDV', 'GML'],
        'VINAMILK': ['GML', 'PHL'],
        'HOAPHAT': ['DQT', 'NDV'],
        'NESTLE_VN': ['GML', 'PHL'],
        'FORMOSA': ['DQT'],
        'FOXCONN_VN': ['NDV'],
        'LG_VN': ['NDV'],
        'NIKE_VN': ['GML'],
        'VN_RUBBER': ['GML'],
        'XIMANG_HP': ['NDV'],
    }

    for (cid, primary_port, cargo_pref) in customers:
        ports_for_cust = multi_port_customers.get(cid, [primary_port])
        for p in ports_for_cust:
            port_customers[p].append((cid, cargo_pref))

    # Aggregate revenue by port×month
    port_month_rev = defaultdict(int)
    for (port, m, cargo, _, _, _, rev) in port_revenue_rows:
        port_month_rev[(port, m)] += rev

    # Assign Pareto weights to customers per port
    port_cust_weights = {}
    for port, custs in port_customers.items():
        n = len(custs)
        # Pareto: top 20% get 80% revenue
        weights = []
        for i in range(n):
            w = 1.0 / ((i + 1) ** 1.2)  # Power law
            weights.append(w)
        total_w = sum(weights)
        weights = [w / total_w for w in weights]
        random.shuffle(custs)  # Randomize which customers are "big"
        # But keep known big customers at top
        big_custs = ['SAMSUNG_VN', 'NIKE_VN', 'FOXCONN_VN', 'LG_VN', 'VINAMILK',
                     'HOAPHAT', 'FORMOSA', 'XIMANG_HP', 'NESTLE_VN', 'VN_RUBBER']
        sorted_custs = []
        remaining = list(custs)
        for bc in big_custs:
            for c in remaining:
                if c[0] == bc:
                    sorted_custs.append(c)
                    remaining.remove(c)
                    break
        sorted_custs.extend(remaining)
        port_cust_weights[port] = list(zip(sorted_custs, weights))

    rows = []
    for mi, m in enumerate(MONTHS):
        for port in PORTS:
            total_rev = port_month_rev.get((port, m), 0)
            if total_rev == 0 or port not in port_cust_weights:
                continue

            cw_list = port_cust_weights[port]
            for (cid, cargo_pref), weight in cw_list:
                cust_rev = total_rev * weight * noise(0.85, 1.15)

                # Anomaly 2B: XIMANG_HP bulk increase
                if cid == 'XIMANG_HP' and port == 'NDV':
                    if m == date(2025, 5, 1): cust_rev *= 1.60
                    elif m == date(2025, 6, 1): cust_rev *= 1.85

                cust_rev = round_vnd(cust_rev)
                if cust_rev <= 0:
                    continue

                # Some small customers skip months
                if weight < 0.01 and random.random() < 0.3:
                    continue

                unit_price = avg_rev_per_unit.get(cargo_pref, 1_400_000)
                if cargo_pref in ('bulk', 'breakbulk'):
                    vol_teu = 0
                    vol_tons = max(1, int(cust_rev / unit_price))
                else:
                    vol_teu = max(1, int(cust_rev / unit_price))
                    vol_tons = 0

                rows.append((port, m, cid, cargo_pref, vol_teu, vol_tons, cust_rev))
    return rows

# =============================================================================
# DATABASE INSERT
# =============================================================================

def insert_data(conn, table, columns, rows, batch=500):
    cur = conn.cursor()
    placeholders = ', '.join(['%s'] * len(columns))
    col_str = ', '.join(columns)
    sql = f"INSERT INTO {table} ({col_str}) VALUES ({placeholders})"

    for i in range(0, len(rows), batch):
        cur.executemany(sql, rows[i:i+batch])
    conn.commit()
    cur.close()
    print(f"  ✓ {table}: {len(rows)} rows inserted")

# =============================================================================
# SQL EXPORT
# =============================================================================

def export_sql(tables_data):
    """Export all transaction data to SQL file"""
    os.makedirs(os.path.dirname(SQL_OUT), exist_ok=True)

    with open(SQL_OUT, 'w', encoding='utf-8') as f:
        f.write("-- ============================================================================\n")
        f.write("-- GEMADEPT SEAPORT DEMO — Transaction Data\n")
        f.write("-- Database: seaport_demo\n")
        f.write("-- Generated by generate_gemadept.py\n")
        f.write(f"-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("-- ============================================================================\n\n")
        f.write("USE seaport_demo;\n\n")

        for table, columns, rows in tables_data:
            f.write(f"-- {table}: {len(rows)} rows\n")
            f.write(f"DELETE FROM {table};\n\n")

            # Batch inserts
            col_str = ', '.join(columns)
            for i in range(0, len(rows), 500):
                batch = rows[i:i+500]
                f.write(f"INSERT INTO {table} ({col_str}) VALUES\n")
                vals = []
                for row in batch:
                    formatted = []
                    for v in row:
                        if v is None:
                            formatted.append('NULL')
                        elif isinstance(v, (date, datetime)):
                            formatted.append(f"'{v}'")
                        elif isinstance(v, str):
                            escaped = v.replace("'", "''")
                            formatted.append(f"'{escaped}'")
                        elif isinstance(v, float):
                            formatted.append(str(round(v, 2)))
                        else:
                            formatted.append(str(v))
                    vals.append(f"({', '.join(formatted)})")
                f.write(',\n'.join(vals))
                f.write(';\n\n')

    print(f"\n✓ SQL exported to {SQL_OUT}")

# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 60)
    print("GEMADEPT SEAPORT DEMO — Transaction Data Generator")
    print("=" * 60)
    print(f"Time range: {MONTHS[0]} to {MONTHS[-1]} ({len(MONTHS)} months)")
    print()

    # Connect
    conn = mysql.connector.connect(**DB_CONFIG)

    # Clear existing transaction data
    cur = conn.cursor()
    for t in ['customer_revenue', 'equipment_maintenance', 'equipment_utilization',
              'vessel_calls', 'shipping_line_revenue', 'operating_costs',
              'container_throughput', 'port_revenue']:
        cur.execute(f"DELETE FROM {t}")
    conn.commit()
    cur.close()
    print("Cleared existing transaction data.\n")

    # Generate Layer 1+2+3
    print("Generating data...")

    # 1. Port Revenue
    pr_rows = gen_port_revenue()
    pr_cols = ['port_id', 'month', 'cargo_type_id', 'volume_teu', 'volume_tons',
               'revenue_per_unit_vnd', 'total_revenue_vnd']
    insert_data(conn, 'port_revenue', pr_cols, pr_rows)

    # 2. Container Throughput
    ct_rows = gen_container_throughput(pr_rows)
    ct_cols = ['port_id', 'month', 'cargo_type_id', 'volume_teu', 'volume_tons']
    insert_data(conn, 'container_throughput', ct_cols, ct_rows)

    # 3. Operating Costs
    oc_rows = gen_operating_costs(pr_rows)
    oc_cols = ['port_id', 'month', 'cost_type_id', 'cost_amount_vnd']
    insert_data(conn, 'operating_costs', oc_cols, oc_rows)

    # 4. Shipping Line Revenue
    slr_rows = gen_shipping_line_revenue(pr_rows)
    slr_cols = ['port_id', 'month', 'shipping_line_id', 'volume_teu', 'revenue_vnd', 'num_vessel_calls']
    insert_data(conn, 'shipping_line_revenue', slr_cols, slr_rows)

    # 5. Vessel Calls
    vc_rows = gen_vessel_calls(slr_rows)
    vc_cols = ['port_id', 'shipping_line_id', 'vessel_name', 'vessel_capacity_teu',
               'actual_volume_teu', 'arrival_time', 'departure_time',
               'turnaround_hours', 'cargo_types_handled']
    insert_data(conn, 'vessel_calls', vc_cols, vc_rows)

    # 6. Equipment Utilization
    eu_rows = gen_equipment_utilization()
    eu_cols = ['equipment_id', 'port_id', 'month', 'total_hours', 'operating_hours',
               'idle_hours', 'maintenance_hours', 'moves_count', 'availability_pct',
               'productivity_moves_per_hour']
    insert_data(conn, 'equipment_utilization', eu_cols, eu_rows)

    # 7. Equipment Maintenance
    em_rows = gen_equipment_maintenance()
    em_cols = ['equipment_id', 'port_id', 'maintenance_type', 'start_date', 'end_date',
               'cost_vnd', 'description']
    insert_data(conn, 'equipment_maintenance', em_cols, em_rows)

    # 8. Customer Revenue
    cr_rows = gen_customer_revenue(pr_rows)
    cr_cols = ['port_id', 'month', 'customer_id', 'cargo_type_id', 'volume_teu',
               'volume_tons', 'revenue_vnd']
    insert_data(conn, 'customer_revenue', cr_cols, cr_rows)

    conn.close()

    # Export SQL
    tables_data = [
        ('port_revenue', pr_cols, pr_rows),
        ('container_throughput', ct_cols, ct_rows),
        ('operating_costs', oc_cols, oc_rows),
        ('shipping_line_revenue', slr_cols, slr_rows),
        ('vessel_calls', vc_cols, vc_rows),
        ('equipment_utilization', eu_cols, eu_rows),
        ('equipment_maintenance', em_cols, em_rows),
        ('customer_revenue', cr_cols, cr_rows),
    ]
    export_sql(tables_data)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    total_rows = sum(len(r) for _, _, r in tables_data)
    print(f"Total rows: {total_rows:,}")
    for tname, _, trows in tables_data:
        print(f"  {tname}: {len(trows):,}")

    # Quick validation
    conn = mysql.connector.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("SELECT SUM(total_revenue_vnd)/1e9 FROM port_revenue WHERE YEAR(month)=2024")
    rev_2024 = cur.fetchone()[0]
    print(f"\nTotal revenue 2024: {rev_2024:,.0f} tỷ VND (target: ~4,200-4,500)")

    cur.execute("SELECT SUM(total_revenue_vnd)/1e9 FROM port_revenue WHERE month BETWEEN '2025-01-01' AND '2025-06-30'")
    rev_h1_2025 = cur.fetchone()[0]
    print(f"H1/2025 revenue: {rev_h1_2025:,.0f} tỷ VND (target: ~2,200-2,500)")

    cur.execute("""
        SELECT pr.month,
               SUM(pr.total_revenue_vnd)/1e9 as rev,
               SUM(oc.cost)/1e9 as cost,
               ROUND((SUM(pr.total_revenue_vnd) - SUM(oc.cost))*100.0/SUM(pr.total_revenue_vnd), 1) as margin
        FROM port_revenue pr
        JOIN (SELECT port_id, month, SUM(cost_amount_vnd) as cost FROM operating_costs GROUP BY port_id, month) oc
          ON pr.port_id = oc.port_id AND pr.month = oc.month
        WHERE pr.port_id = 'NDV' AND pr.month >= '2025-01-01'
        GROUP BY pr.month ORDER BY pr.month
    """)
    print("\nNDV margin trend 2025:")
    for row in cur.fetchall():
        print(f"  {row[0]}: rev={row[1]:,.1f}B, cost={row[2]:,.1f}B, margin={row[3]}%")

    cur.close()
    conn.close()
    print("\nDone!")

if __name__ == '__main__':
    main()
