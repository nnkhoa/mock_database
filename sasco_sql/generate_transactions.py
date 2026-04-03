#!/usr/bin/env python3
"""
SASCO Demo - Transaction Data Generator
Generates: passenger_traffic, lounge_visits, sales_transactions
Period: 2024-01-01 to 2025-06-30 (18 months)
"""

import mysql.connector
import random
import math
from datetime import date, timedelta, time
from collections import defaultdict

random.seed(2024)

# ============================================================================
# DATABASE CONNECTION
# ============================================================================
db = mysql.connector.connect(
    host="127.0.0.1", port=3306, user="root", password="root",
    database="sasco_demo", charset="utf8mb4"
)
cursor = db.cursor(dictionary=True)

# ============================================================================
# LOAD MASTER DATA
# ============================================================================
cursor.execute("SELECT * FROM terminals")
terminals = {r['terminal_id']: r for r in cursor.fetchall()}

cursor.execute("SELECT * FROM locations")
locations = {r['location_id']: r for r in cursor.fetchall()}

cursor.execute("SELECT * FROM lounges")
lounges = {r['lounge_id']: r for r in cursor.fetchall()}

cursor.execute("SELECT * FROM nationality_groups")
nationalities = {r['nationality_group_id']: r for r in cursor.fetchall()}

cursor.execute("""
    SELECT p.*, pc.business_line_id
    FROM products p
    JOIN product_categories pc ON p.category_id = pc.category_id
""")
all_products = cursor.fetchall()

# Organize products by business_line and category
products_by_bl = defaultdict(list)
products_by_cat = defaultdict(list)
for p in all_products:
    products_by_bl[p['business_line_id']].append(p)
    products_by_cat[p['category_id']].append(p)

# ============================================================================
# CONSTANTS & COEFFICIENTS
# ============================================================================
START_DATE = date(2024, 1, 1)
END_DATE = date(2025, 6, 30)

# Monthly seasonality (index 1-12)
MONTHLY_INTL = {1: 1.05, 2: 0.90, 3: 0.95, 4: 0.95, 5: 0.95, 6: 1.05,
                7: 1.15, 8: 1.10, 9: 0.90, 10: 1.00, 11: 1.10, 12: 1.15}
MONTHLY_DOMESTIC = {1: 1.25, 2: 1.35, 3: 0.85, 4: 0.80, 5: 0.85, 6: 1.10,
                    7: 1.20, 8: 1.15, 9: 0.80, 10: 0.85, 11: 0.90, 12: 1.05}

# Weekly pattern (0=Monday, 6=Sunday)
WEEKLY = {0: 1.10, 1: 0.90, 2: 0.85, 3: 1.00, 4: 1.20, 5: 1.10, 6: 1.05}

# Hourly pattern for lounges (hour -> coefficient)
HOURLY_INTL = {
    0: 0.60, 1: 0.60, 2: 0.60, 3: 0.60, 4: 0.60, 5: 0.60,
    6: 1.40, 7: 1.40, 8: 1.40,
    9: 1.20, 10: 1.20, 11: 1.20,
    12: 0.80, 13: 0.80, 14: 0.80,
    15: 1.00, 16: 1.00, 17: 1.00,
    18: 1.30, 19: 1.30, 20: 1.30,
    21: 1.10, 22: 1.10, 23: 1.10
}
HOURLY_DOMESTIC = {
    0: 0.30, 1: 0.30, 2: 0.30, 3: 0.30, 4: 0.30, 5: 0.30,
    6: 1.60, 7: 1.60, 8: 1.60,
    9: 1.00, 10: 1.00, 11: 1.00,
    12: 0.70, 13: 0.70, 14: 0.70,
    15: 0.90, 16: 0.90, 17: 0.90,
    18: 1.20, 19: 1.20, 20: 1.20,
    21: 0.80, 22: 0.80, 23: 0.80
}

# Anomaly 2: Domestic T1 lounge extreme skew
HOURLY_DOMESTIC_T1 = {
    0: 0.15, 1: 0.15, 2: 0.15, 3: 0.15, 4: 0.20, 5: 0.25,
    6: 1.80, 7: 1.90, 8: 1.80,  # peak 85-95%
    9: 1.10, 10: 1.00, 11: 0.90,
    12: 0.45, 13: 0.40, 14: 0.35,  # trough 25-35%
    15: 0.50, 16: 0.50, 17: 0.55,  # low 30-40%
    18: 0.90, 19: 0.85, 20: 0.80,
    21: 0.35, 22: 0.30, 23: 0.20
}

# Category-specific seasonality multipliers (month -> multiplier on top of base)
CAT_SEASON = {
    # Cosmetics/Perfume: +15% Nov-Dec, +10% Feb (Valentine)
    10: {2: 1.10, 11: 1.15, 12: 1.15},
    11: {2: 1.10, 11: 1.15, 12: 1.15},
    12: {2: 1.10, 11: 1.15, 12: 1.15},
    # Alcohol: +20% Dec, +25% Jan-Feb (Tet)
    20: {1: 1.25, 2: 1.25, 12: 1.20},
    21: {1: 1.25, 2: 1.25, 12: 1.20},
    22: {1: 1.25, 2: 1.25, 12: 1.20},
    # Specialties/Gifts: +30% Jan-Feb (Tet), +15% Jun-Aug
    40: {1: 1.30, 2: 1.30, 6: 1.15, 7: 1.15, 8: 1.15},
    41: {1: 1.30, 2: 1.30, 6: 1.15, 7: 1.15, 8: 1.15},
    42: {1: 1.30, 2: 1.30, 6: 1.15, 7: 1.15, 8: 1.15},
    43: {1: 1.30, 2: 1.30, 6: 1.15, 7: 1.15, 8: 1.15},
    44: {1: 1.30, 2: 1.30, 6: 1.15, 7: 1.15, 8: 1.15},
    50: {1: 1.20, 2: 1.20, 11: 1.15, 12: 1.15},
}

# YoY growth rates per business line (annual)
BL_GROWTH = {1: 0.25, 2: 0.04, 3: 0.20, 4: 0.08}

# Nationality spending profiles for duty-free
# category_group -> probability weight per nationality
# Category groups: 10(cosmetics), 20(alcohol), 30(fashion), 40(specialty), 50(sweets), 60(electronics)
NAT_CAT_PREFS = {
    1:  {10: 0.45, 20: 0.20, 30: 0.15, 40: 0.10, 50: 0.05, 60: 0.05},  # Korea
    2:  {10: 0.35, 20: 0.15, 30: 0.10, 40: 0.25, 50: 0.10, 60: 0.05},  # China
    3:  {10: 0.40, 20: 0.10, 30: 0.15, 40: 0.15, 50: 0.10, 60: 0.10},  # Taiwan
    4:  {10: 0.30, 20: 0.10, 30: 0.05, 40: 0.30, 50: 0.10, 60: 0.15},  # Japan (crafts, tea)
    5:  {10: 0.25, 20: 0.25, 30: 0.15, 40: 0.10, 50: 0.10, 60: 0.15},  # USA
    6:  {10: 0.05, 20: 0.05, 30: 0.05, 40: 0.55, 50: 0.15, 60: 0.15},  # India - very low cosmetics!
    7:  {10: 0.20, 20: 0.15, 30: 0.10, 40: 0.20, 50: 0.20, 60: 0.15},  # Malaysia
    8:  {10: 0.25, 20: 0.25, 30: 0.10, 40: 0.15, 50: 0.10, 60: 0.15},  # Australia
    9:  {10: 0.05, 20: 0.05, 30: 0.05, 40: 0.45, 50: 0.30, 60: 0.10},  # Cambodia
    10: {10: 0.15, 20: 0.15, 30: 0.10, 40: 0.25, 50: 0.20, 60: 0.15},  # Thailand
    11: {10: 0.30, 20: 0.30, 30: 0.15, 40: 0.10, 50: 0.05, 60: 0.10},  # Other Europe
    12: {10: 0.20, 20: 0.20, 30: 0.15, 40: 0.20, 50: 0.15, 60: 0.10},  # Others
}

# Map top-level category_id to category group for NAT_CAT_PREFS
def get_cat_group(category_id):
    if category_id in (10, 11, 12): return 10
    if category_id in (20, 21, 22, 23): return 20
    if category_id in (30, 31, 32, 33): return 30
    if category_id in (40, 41, 42, 43, 44): return 40
    if category_id == 50: return 50
    if category_id == 60: return 60
    return 40  # fallback

# Build product pools per category group for duty-free
df_products_by_catgroup = defaultdict(list)
for p in products_by_bl[2]:  # duty-free products
    cg = get_cat_group(p['category_id'])
    df_products_by_catgroup[cg].append(p)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def days_range():
    """Iterator over all days in the period."""
    d = START_DATE
    while d <= END_DATE:
        yield d
        d += timedelta(days=1)

def months_from_start(d):
    """Months elapsed since start date."""
    return (d.year - START_DATE.year) * 12 + (d.month - START_DATE.month)

def yoy_growth_factor(d, bl_id):
    """Cumulative growth factor for a given date and business line."""
    m = months_from_start(d)
    annual_rate = BL_GROWTH.get(bl_id, 0.12)
    return 1 + annual_rate * m / 12

def get_nationality_shares(d):
    """Get nationality PAX shares for a given date, with anomaly mix shift."""
    # Baseline shares
    shares = {}
    for nid, ng in nationalities.items():
        if nid == 0:
            continue
        shares[nid] = float(ng['pax_share_pct']) / 100.0

    # Anomaly 1: nationality mix shift from Jan 2025 onwards
    if d >= date(2025, 1, 1):
        month_offset = min(6, (d.year - 2025) * 12 + d.month - 1)  # 0-6
        frac = month_offset / 6.0

        # Korea: 28% -> 24%
        shares[1] = (0.28 - 0.04 * frac)
        # India: 5% -> 9%
        shares[6] = (0.05 + 0.04 * frac)
        # Cambodia: 3% -> 5%
        shares[9] = (0.03 + 0.02 * frac)

        # Redistribute remaining to keep sum=1
        fixed_ids = {1, 6, 9}
        fixed_sum = sum(shares[k] for k in fixed_ids)
        other_ids = [k for k in shares if k not in fixed_ids]
        other_baseline_sum = sum(float(nationalities[k]['pax_share_pct']) / 100.0 for k in other_ids)
        remaining = 1.0 - fixed_sum
        for k in other_ids:
            baseline = float(nationalities[k]['pax_share_pct']) / 100.0
            shares[k] = baseline * (remaining / other_baseline_sum)

    return shares

def is_location_open(loc, d):
    """Check if a location is open on a given date."""
    return d >= loc['open_date']

def pick_product_weighted(product_list):
    """Pick a product from list using popularity_weight."""
    weights = [float(p['popularity_weight']) for p in product_list]
    return random.choices(product_list, weights=weights, k=1)[0]

def random_time_in_day():
    """Random time weighted towards business hours."""
    # Weight towards 6-21h
    hour_weights = [0.02]*6 + [0.08,0.10,0.10,0.08,0.07,0.06,0.05,0.05,0.06,0.07,0.08,0.08,0.06,0.03,0.01] + [0.0]*3
    # Pad to 24
    while len(hour_weights) < 24:
        hour_weights.append(0.0)
    total = sum(hour_weights)
    hour_weights = [w/total for w in hour_weights]
    h = random.choices(range(24), weights=hour_weights, k=1)[0]
    m = random.randint(0, 59)
    s = random.randint(0, 59)
    return time(h, m, s)

# ============================================================================
# PHASE 1: PASSENGER TRAFFIC
# ============================================================================
print("=== Generating passenger_traffic ===")

# Base daily PAX per terminal
# TSN T2 (international): ~15,000 departure PAX/day (half of 30K both ways)
# TSN T1 (domestic): ~25,000 departure PAX/day
# T3: mixed, starts Apr 2025
# Cam Ranh: ~2,500 intl PAX/day
# Phu Quoc: ~1,500 mixed PAX/day

TERMINAL_PAX_BASE = {
    1: {'domestic': 25000, 'intl': 0},        # T1 domestic only
    2: {'domestic': 0, 'intl': 15000},         # T2 international only
    3: {'domestic': 5000, 'intl': 5000},       # T3 mixed (at full capacity)
    4: {'domestic': 0, 'intl': 2500},          # Cam Ranh international
    5: {'domestic': 1000, 'intl': 500},        # Phu Quoc mixed
}

traffic_rows = []
traffic_by_date_terminal = {}  # cache for sales generation

for d in days_range():
    month = d.month
    dow = d.weekday()  # 0=Monday
    monthly_intl = MONTHLY_INTL[month]
    monthly_dom = MONTHLY_DOMESTIC[month]
    weekly = WEEKLY[dow]

    # YoY PAX growth: ~12% intl, ~5% domestic
    m_offset = months_from_start(d)
    intl_growth = 1 + 0.12 * m_offset / 12
    dom_growth = 1 + 0.05 * m_offset / 12

    nat_shares = get_nationality_shares(d)

    for tid, base in TERMINAL_PAX_BASE.items():
        term = terminals[tid]
        if not d >= term['open_date']:
            continue

        # T3 ramp-up (Anomaly 3)
        t3_mult = 1.0
        if tid == 3:
            if d < date(2025, 4, 1):
                continue  # T3 not open yet
            week_num = max(1, (d - date(2025, 4, 1)).days // 7 + 1)
            t3_mult = min(0.60, 0.15 + 0.08 * week_num * random.uniform(0.80, 1.20))

        # Phu Quoc ramp-up
        pq_mult = 1.0
        if tid == 5:
            if d < date(2024, 11, 1):
                continue
            week_num = max(1, (d - date(2024, 11, 1)).days // 7 + 1)
            pq_mult = min(0.45, 0.10 + 0.05 * week_num * random.uniform(0.80, 1.20))

        # Phu Quoc seasonality: low Mar-May, high Jul-Aug, Nov-Dec
        pq_season = 1.0
        if tid == 5:
            pq_seasons = {1: 1.0, 2: 0.8, 3: 0.6, 4: 0.5, 5: 0.6, 6: 0.9,
                         7: 1.3, 8: 1.3, 9: 0.7, 10: 0.8, 11: 1.2, 12: 1.3}
            pq_season = pq_seasons.get(month, 1.0)

        ramp = t3_mult if tid == 3 else (pq_mult * pq_season if tid == 5 else 1.0)

        # International PAX
        if base['intl'] > 0:
            total_intl_day = base['intl'] * monthly_intl * weekly * intl_growth * ramp
            total_intl_day *= random.uniform(0.90, 1.10)
            total_intl_day = max(0, int(total_intl_day))

            # Split by nationality
            for nid, share in nat_shares.items():
                pax = max(1, int(total_intl_day * share * random.uniform(0.92, 1.08)))
                traffic_rows.append((d, tid, nid, 'Quoc te', pax))

            # Cache total intl for this terminal-date
            key = (d, tid)
            traffic_by_date_terminal.setdefault(key, {'intl': 0, 'domestic': 0})
            traffic_by_date_terminal[key]['intl'] = total_intl_day

        # Domestic PAX
        if base['domestic'] > 0:
            total_dom_day = base['domestic'] * monthly_dom * weekly * dom_growth * ramp
            total_dom_day *= random.uniform(0.90, 1.10)
            total_dom_day = max(0, int(total_dom_day))

            traffic_rows.append((d, tid, 0, 'Noi dia', total_dom_day))

            key = (d, tid)
            traffic_by_date_terminal.setdefault(key, {'intl': 0, 'domestic': 0})
            traffic_by_date_terminal[key]['domestic'] = total_dom_day

print(f"  passenger_traffic rows: {len(traffic_rows)}")

# Insert passenger_traffic
print("  Inserting passenger_traffic...")
batch = []
for row in traffic_rows:
    batch.append(row)
    if len(batch) >= 1000:
        cursor.executemany(
            "INSERT INTO passenger_traffic (traffic_date, terminal_id, nationality_group_id, passenger_type, pax_count) VALUES (%s, %s, %s, %s, %s)",
            batch
        )
        batch = []
if batch:
    cursor.executemany(
        "INSERT INTO passenger_traffic (traffic_date, terminal_id, nationality_group_id, passenger_type, pax_count) VALUES (%s, %s, %s, %s, %s)",
        batch
    )
db.commit()
print("  passenger_traffic DONE")

# ============================================================================
# PHASE 2: LOUNGE VISITS
# ============================================================================
print("\n=== Generating lounge_visits ===")

visit_rows = []

for d in days_range():
    month = d.month
    dow = d.weekday()
    weekly = WEEKLY[dow]

    for lid, lounge in lounges.items():
        loc = locations[lid]
        if not is_location_open(loc, d):
            continue

        tid = loc['terminal_id']
        capacity = loc['capacity']
        max_cap_hour = lounge['max_capacity_per_hour']
        ltype = lounge['lounge_type']

        # Base utilization
        if ltype == 'Quoc te':
            monthly_coeff = MONTHLY_INTL[month]
            hourly_map = HOURLY_INTL
        elif ltype == 'Noi dia':
            monthly_coeff = MONTHLY_DOMESTIC[month]
            # Anomaly 2: extreme skew for domestic T1
            if tid == 1:
                hourly_map = HOURLY_DOMESTIC_T1
            else:
                hourly_map = HOURLY_DOMESTIC
        else:  # Hỗn hợp
            monthly_coeff = (MONTHLY_INTL[month] + MONTHLY_DOMESTIC[month]) / 2
            hourly_map = {h: (HOURLY_INTL[h] + HOURLY_DOMESTIC[h]) / 2 for h in range(24)}

        # Growth factor
        m_offset = months_from_start(d)
        growth = 1 + 0.20 * m_offset / 12  # lounges grow ~20%/yr

        # T3 ramp-up
        ramp = 1.0
        if tid == 3:
            week_num = max(1, (d - date(2025, 4, 1)).days // 7 + 1)
            ramp = min(0.60, 0.15 + 0.08 * week_num * random.uniform(0.80, 1.20))
        elif tid == 5:  # Phu Quoc
            week_num = max(1, (d - date(2024, 11, 1)).days // 7 + 1)
            ramp = min(0.45, 0.10 + 0.05 * week_num * random.uniform(0.80, 1.20))
            # PQ seasonality
            pq_s = {1: 1.0, 2: 0.8, 3: 0.6, 4: 0.5, 5: 0.6, 6: 0.9,
                    7: 1.3, 8: 1.3, 9: 0.7, 10: 0.8, 11: 1.2, 12: 1.3}
            ramp *= pq_s.get(month, 1.0)

        # Base average utilization target
        # International T2: ~75%, Domestic T1: ~50% avg (but skewed), T3/PQ: ramping
        if tid == 2:
            base_util = 0.72
        elif tid == 1:
            base_util = 0.48
        elif tid == 4:  # Cam Ranh
            base_util = 0.55
        else:
            base_util = 0.65

        for hour in range(24):
            hourly_coeff = hourly_map[hour]

            # Calculate guest count
            util = base_util * monthly_coeff * weekly * hourly_coeff * growth * ramp
            util *= random.uniform(0.85, 1.15)  # noise
            util = min(util, 1.20)  # cap at 120% (overcrowding possible)
            util = max(util, 0.02)  # minimum

            guest_count = max(0, int(capacity * util))
            if guest_count == 0 and hour >= 6 and hour <= 22:
                guest_count = random.randint(1, 3)

            util_rate = round(guest_count / capacity * 100, 2) if capacity > 0 else 0

            visit_rows.append((d, hour, lid, tid, guest_count, capacity, util_rate))

print(f"  lounge_visits rows: {len(visit_rows)}")

# Insert lounge_visits
print("  Inserting lounge_visits...")
batch = []
for row in visit_rows:
    batch.append(row)
    if len(batch) >= 2000:
        cursor.executemany(
            "INSERT INTO lounge_visits (visit_date, hour_slot, lounge_id, terminal_id, guest_count, capacity, utilization_rate) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            batch
        )
        batch = []
if batch:
    cursor.executemany(
        "INSERT INTO lounge_visits (visit_date, hour_slot, lounge_id, terminal_id, guest_count, capacity, utilization_rate) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        batch
    )
db.commit()
print("  lounge_visits DONE")

# ============================================================================
# PHASE 3: SALES TRANSACTIONS
# ============================================================================
print("\n=== Generating sales_transactions ===")

# Revenue targets (VND/day):
# Total: ~8.3 billion/day baseline (3000 billion/year)
# BL1 Lounge: 30% = ~2.49B/day -> but derived from lounge visits * price
# BL2 Duty-free: 35% = ~2.9B/day
# BL3 F&B: 25% = ~2.1B/day
# BL4 Other: 10% = ~0.83B/day

# We'll generate transactions per location per day

sales_rows = []
tx_count = 0

# Pre-compute duty-free product pools per category group
df_cat_groups = list(df_products_by_catgroup.keys())

def generate_df_transaction(d, loc, nat_id):
    """Generate a duty-free sales transaction for a given nationality."""
    tid = loc['terminal_id']
    bl_id = 2

    # Pick category group based on nationality preference
    prefs = NAT_CAT_PREFS.get(nat_id, NAT_CAT_PREFS[12])
    cat_groups = list(prefs.keys())
    cat_weights = list(prefs.values())
    chosen_cg = random.choices(cat_groups, weights=cat_weights, k=1)[0]

    # Pick product from that category group
    pool = df_products_by_catgroup.get(chosen_cg, [])
    if not pool:
        pool = products_by_bl[2]  # fallback
    product = pick_product_weighted(pool)

    # Quantity (mostly 1, sometimes 2-3)
    qty = random.choices([1, 2, 3], weights=[0.75, 0.20, 0.05], k=1)[0]

    # Price with small variation (±3%)
    base_price = int(product['unit_price_vnd'])
    unit_price = int(base_price * random.uniform(0.97, 1.03))
    total_rev = unit_price * qty
    cost = int(float(product['cost_price_vnd']) * qty)

    t = random_time_in_day()

    return (d, t, loc['location_id'], bl_id, tid, product['product_id'],
            nat_id, qty, unit_price, total_rev, cost)

def generate_fnb_transaction(d, loc):
    """Generate an F&B/retail transaction (represents a customer receipt)."""
    tid = loc['terminal_id']
    bl_id = 3

    pool = products_by_bl[3]
    product = pick_product_weighted(pool)

    # Airport F&B: customers order multiple items (food + drink + snack)
    # Model as single line item with higher qty to represent a "receipt"
    qty = random.choices([2, 3, 4, 5, 6, 8], weights=[0.20, 0.30, 0.25, 0.15, 0.07, 0.03], k=1)[0]
    base_price = int(product['unit_price_vnd'])
    unit_price = int(base_price * random.uniform(0.97, 1.03))
    total_rev = unit_price * qty
    cost = int(float(product['cost_price_vnd']) * qty)

    # F&B nationality is mostly NULL (domestic or unknown)
    nat_id = None

    t = random_time_in_day()

    return (d, t, loc['location_id'], bl_id, tid, product['product_id'],
            nat_id, qty, unit_price, total_rev, cost)

def generate_lounge_transaction(d, loc, guest_count_day):
    """Generate lounge service transactions."""
    tid = loc['terminal_id']
    bl_id = 1

    pool = products_by_bl[1]
    product = pick_product_weighted(pool)

    qty = 1
    base_price = int(product['unit_price_vnd'])
    unit_price = int(base_price * random.uniform(0.97, 1.03))
    total_rev = unit_price * qty
    cost = int(float(product['cost_price_vnd']) * qty)

    nat_id = None
    t = random_time_in_day()

    return (d, t, loc['location_id'], bl_id, tid, product['product_id'],
            nat_id, qty, unit_price, total_rev, cost)

def generate_other_transaction(d, loc):
    """Generate other service transaction."""
    tid = loc['terminal_id']
    bl_id = 4

    pool = products_by_bl[4]
    product = pick_product_weighted(pool)

    qty = random.choices([1, 2, 3], weights=[0.70, 0.20, 0.10], k=1)[0]
    base_price = int(product['unit_price_vnd'])
    unit_price = int(base_price * random.uniform(0.97, 1.03))
    total_rev = unit_price * qty
    cost = int(float(product['cost_price_vnd']) * qty)

    nat_id = None
    t = random_time_in_day()

    return (d, t, loc['location_id'], bl_id, tid, product['product_id'],
            nat_id, qty, unit_price, total_rev, cost)

print("  Generating transactions day by day...")

for day_idx, d in enumerate(days_range()):
    month = d.month
    dow = d.weekday()
    monthly_intl = MONTHLY_INTL[month]
    monthly_dom = MONTHLY_DOMESTIC[month]
    weekly = WEEKLY[dow]

    nat_shares = get_nationality_shares(d)

    for lid, loc in locations.items():
        if not is_location_open(loc, d):
            continue

        tid = loc['terminal_id']
        bl_id = loc['business_line_id']

        # T3 ramp-up multiplier
        ramp = 1.0
        if tid == 3:
            week_num = max(1, (d - date(2025, 4, 1)).days // 7 + 1)
            ramp = min(0.60, 0.15 + 0.08 * week_num * random.uniform(0.80, 1.20))
        elif tid == 5:
            if d < date(2024, 11, 1):
                continue
            week_num = max(1, (d - date(2024, 11, 1)).days // 7 + 1)
            ramp = min(0.45, 0.10 + 0.05 * week_num * random.uniform(0.80, 1.20))
            pq_s = {1: 1.0, 2: 0.8, 3: 0.6, 4: 0.5, 5: 0.6, 6: 0.9,
                    7: 1.3, 8: 1.3, 9: 0.7, 10: 0.8, 11: 1.2, 12: 1.3}
            ramp *= pq_s.get(month, 1.0)

        growth = yoy_growth_factor(d, bl_id)
        noise = random.uniform(0.88, 1.12)

        if bl_id == 1:  # Lounge
            # Target: ~900 tỷ/year total lounge revenue across 15 lounges
            # ~900B / 365 / 15 = ~164M/day/lounge average
            # Avg lounge price ~500K -> ~328 guests/day for large lounges (capacity 120)
            # Scale by capacity: capacity 120 -> 200 guests, capacity 50 -> 80 guests
            capacity = loc['capacity'] or 50
            lounge = lounges.get(lid)
            if not lounge:
                continue

            ltype = lounge['lounge_type']
            # Base daily guests proportional to capacity
            # Target ~900B/yr / 15 lounges / 365 = ~164M/day/lounge
            # Avg price ~500K -> ~328 guests/day for large lounges
            base_daily_guests = capacity * 2.15  # calibrated for ~900B/yr

            if ltype == 'Noi dia':
                monthly_coeff = monthly_dom
            elif ltype == 'Quoc te':
                monthly_coeff = monthly_intl
            else:
                monthly_coeff = (monthly_intl + monthly_dom) / 2

            daily_tx = base_daily_guests * monthly_coeff * weekly * growth * ramp * noise

            n_tx = max(1, int(daily_tx))
            n_tx = min(n_tx, 400)

            for _ in range(n_tx):
                sales_rows.append(generate_lounge_transaction(d, loc, n_tx))

        elif bl_id == 2:  # Duty-free
            # Daily transactions based on PAX and conversion rate (~12%)
            key = (d, tid)
            pax_data = traffic_by_date_terminal.get(key, {'intl': 0})
            intl_pax = pax_data.get('intl', 0)

            if intl_pax == 0:
                continue

            # Conversion rate ~6% (line-item level, each customer ~2 items avg)
            conversion = 0.048
            # Scale by location size (3 DF in T2, 1 in T3, 1 in CR)
            if tid == 2:
                loc_share = {201: 0.40, 202: 0.35, 203: 0.25}.get(lid, 0.33)
            elif tid == 3:
                loc_share = 1.0
            elif tid == 4:
                loc_share = 1.0
            else:
                loc_share = 0.5

            daily_tx = intl_pax * conversion * loc_share * growth * noise
            # Category seasonality
            cat_boost = 1.0
            for cat_parent, season_map in CAT_SEASON.items():
                if month in season_map:
                    cat_boost = max(cat_boost, season_map[month])

            daily_tx *= (cat_boost * 0.3 + 0.7)  # partial category effect

            n_tx = max(1, int(daily_tx))
            n_tx = min(n_tx, 20000)

            # Generate transactions with nationality distribution
            for _ in range(n_tx):
                # Pick nationality weighted by current shares
                nat_ids = list(nat_shares.keys())
                nat_weights = [nat_shares[k] for k in nat_ids]
                nat_id = random.choices(nat_ids, weights=nat_weights, k=1)[0]
                sales_rows.append(generate_df_transaction(d, loc, nat_id))

        elif bl_id == 3:  # F&B & Retail
            # Target: ~750 tỷ/year total F&B revenue across 12 locations
            # ~750B / 365 / 12 = ~171M/day/location average
            # Avg F&B item ~100K, need ~1710 items/day -> multiple items per customer
            # Actually: restaurants ~300 customers * 2 items * 100K = 60M
            # But with higher-value items and more volume, target ~170M/day avg
            # Base daily transactions (line items, not customers)
            loc_type = loc['location_type']
            if loc_type == 'Nhà hàng':
                base_tx = 820  # calibrated for ~750B/yr F&B total
            elif loc_type == 'Café':
                base_tx = 680
            elif loc_type == 'Shop bán lẻ':
                base_tx = 410
            else:
                base_tx = 550

            # Terminal scaling
            if tid == 2:
                term_scale = 1.0
            elif tid == 1:
                term_scale = 0.85
            elif tid == 4:
                term_scale = 0.40
            else:
                term_scale = 0.60

            monthly_mix = (monthly_intl + monthly_dom) / 2
            daily_tx = base_tx * term_scale * monthly_mix * weekly * growth * ramp * noise

            n_tx = max(1, int(daily_tx))
            n_tx = min(n_tx, 3000)

            for _ in range(n_tx):
                sales_rows.append(generate_fnb_transaction(d, loc))

        elif bl_id == 4:  # Other services
            # Target ~300 tỷ/year across 5 locations = ~164M/day/loc
            # Avg service price ~400K -> ~410 tx/day for main loc
            base_tx = 270  # calibrated for ~300B/yr Other total
            if tid == 2:
                term_scale = 1.0
            elif tid == 3:
                term_scale = 0.5
            else:
                term_scale = 0.3

            monthly_mix = (monthly_intl + monthly_dom) / 2
            daily_tx = base_tx * term_scale * monthly_mix * weekly * growth * ramp * noise

            n_tx = max(1, int(daily_tx))
            n_tx = min(n_tx, 2000)

            for _ in range(n_tx):
                sales_rows.append(generate_other_transaction(d, loc))

    # Progress
    if (day_idx + 1) % 30 == 0:
        print(f"    Day {day_idx+1}/{(END_DATE - START_DATE).days + 1}, "
              f"accumulated rows: {len(sales_rows)}")

print(f"  Total sales_transactions rows: {len(sales_rows)}")

# Insert sales_transactions in batches
print("  Inserting sales_transactions...")
batch = []
inserted = 0
for row in sales_rows:
    batch.append(row)
    if len(batch) >= 2000:
        cursor.executemany(
            """INSERT INTO sales_transactions
            (transaction_date, transaction_time, location_id, business_line_id,
             terminal_id, product_id, nationality_group_id, quantity,
             unit_price_vnd, total_revenue_vnd, cost_vnd)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            batch
        )
        inserted += len(batch)
        batch = []
        if inserted % 100000 == 0:
            db.commit()
            print(f"    Inserted {inserted:,} / {len(sales_rows):,}")

if batch:
    cursor.executemany(
        """INSERT INTO sales_transactions
        (transaction_date, transaction_time, location_id, business_line_id,
         terminal_id, product_id, nationality_group_id, quantity,
         unit_price_vnd, total_revenue_vnd, cost_vnd)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        batch
    )
    inserted += len(batch)

db.commit()
print(f"  sales_transactions DONE: {inserted:,} rows inserted")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n=== SUMMARY ===")
for table in ['passenger_traffic', 'lounge_visits', 'sales_transactions']:
    cursor.execute(f"SELECT COUNT(*) AS cnt FROM {table}")
    cnt = cursor.fetchone()['cnt']
    print(f"  {table}: {cnt:,} rows")

cursor.execute("SELECT SUM(total_revenue_vnd)/1e12 AS total_rev_nghin_ty FROM sales_transactions WHERE transaction_date BETWEEN '2024-01-01' AND '2024-12-31'")
rev = cursor.fetchone()['total_rev_nghin_ty']
print(f"  2024 total revenue: {rev:.3f} nghìn tỷ VND (target: ~2.8-3.1)")

cursor.execute("SELECT SUM(total_revenue_vnd)/1e12 AS total_rev FROM sales_transactions")
total = cursor.fetchone()['total_rev']
print(f"  18-month total revenue: {total:.3f} nghìn tỷ VND (target: ~4.3-4.5)")

cursor.close()
db.close()
print("\n=== ALL DONE ===")
