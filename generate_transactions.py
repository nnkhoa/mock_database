#!/usr/bin/env python3
"""
Generate transaction data for AP Saigon Petro lubricants_demo database.
3 layers: Base volume → Seasonality → Anomaly injection
Tables: sales_orders, payments, production_batches, raw_material_costs
"""

import mysql.connector
import random
import math
from datetime import date, timedelta, datetime
from collections import defaultdict

random.seed(42)

# ============================================================
# CONFIG
# ============================================================
START_DATE = date(2024, 10, 1)
END_DATE = date(2026, 3, 31)
CURRENT_DATE = date(2026, 3, 31)  # "now" for anomaly calculations

# Monthly seasonality (index 0=Jan, 11=Dec)
MONTHLY_SEASONALITY = [1.15, 0.75, 0.90, 0.95, 1.05, 1.10, 1.12, 1.08, 1.05, 1.00, 0.95, 1.10]

# Weekly pattern (index 0=Mon, 6=Sun)
WEEKLY_PATTERN = [1.05, 1.08, 1.10, 1.05, 1.00, 0.85, 0.55]

# Category-level seasonality (index 0=Jan, 11=Dec)
CATEGORY_SEASONALITY = {
    'Dầu xe máy':      [1.20, 0.70, 0.85, 0.90, 1.05, 1.15, 1.18, 1.12, 1.05, 0.98, 0.92, 1.15],
    'Dầu ô tô':        [1.25, 0.65, 0.85, 0.95, 1.00, 1.05, 1.08, 1.05, 1.00, 0.98, 0.95, 1.10],
    'Dầu xe tải':      [1.05, 0.80, 0.95, 1.00, 1.08, 1.12, 1.15, 1.10, 1.05, 1.00, 0.95, 1.05],
    'Dầu hàng hải':    [0.80, 0.70, 1.10, 1.20, 1.25, 1.20, 1.10, 1.00, 0.90, 0.85, 0.80, 0.85],
    'Dầu công nghiệp': [0.90, 0.80, 0.95, 1.00, 1.05, 1.05, 1.08, 1.10, 1.12, 1.08, 1.00, 0.95],
    'Dầu nông nghiệp': [0.70, 0.60, 0.80, 0.90, 1.20, 1.30, 1.25, 1.10, 0.95, 0.85, 0.75, 0.70],
    'Mỡ bôi trơn':     [0.95, 0.80, 0.95, 1.00, 1.05, 1.05, 1.08, 1.05, 1.02, 1.00, 0.98, 0.95],
}

# Region revenue weight (proportional to DT share)
REGION_WEIGHT = {
    'Đông Nam Bộ': 0.30,
    'Đồng bằng Sông Cửu Long': 0.15,
    'Đồng bằng Sông Hồng': 0.20,
    'Trung du và Miền núi phía Bắc': 0.08,
    'Bắc Trung Bộ': 0.10,
    'Nam Trung Bộ': 0.10,
    'Tây Nguyên': 0.07,
}

# Tier config: (orders_per_month_min, orders_per_month_max, base_volume_per_order_mean)
# Target: ~150K-200K total orders over 18 months across 100 NPPs
# = ~8K-11K orders/month = ~80-110 orders/NPP/month avg
TIER_CONFIG = {
    'Tổng đại lý':  (120, 180, 2500),   # 16 NPPs × 150 avg = 2400/month
    'Đại lý cấp 1': (60, 100, 1200),    # 44 NPPs × 80 avg = 3520/month
    'Đại lý cấp 2': (25, 50, 500),      # 40 NPPs × 37 avg = 1480/month
    # Total: ~7400/month × 18 = ~133K base, + region scaling ≈ 150K-200K
}

# DSO anomaly NPPs and their delay progression (months_ago: extra_delay_days)
DSO_ANOMALY_NPPS = {'NPP-008', 'NPP-015', 'NPP-022'}
DSO_DELAY_BY_MONTHS_AGO = {1: 28, 2: 22, 3: 15, 4: 8, 5: 2}

# Growth anomaly NPP
GROWTH_ANOMALY_NPP = 'NPP-003'

# ĐBSCL region name for margin anomaly
DBSCL_REGION = 'Đồng bằng Sông Cửu Long'

# ============================================================
# DB CONNECTION & DATA LOAD
# ============================================================
conn = mysql.connector.connect(
    host='localhost', port=3306, user='root', password='root',
    database='lubricants_demo', charset='utf8mb4'
)
cur = conn.cursor(dictionary=True)

# Load master data
cur.execute("SELECT * FROM distributors")
distributors = {r['distributor_id']: r for r in cur.fetchall()}

cur.execute("SELECT * FROM regions")
regions = {r['region_id']: r for r in cur.fetchall()}

cur.execute("SELECT * FROM products WHERE status='active'")
all_products = cur.fetchall()

cur.execute("SELECT * FROM channels")
channels = {r['channel_id']: r for r in cur.fetchall()}

cur.execute("SELECT * FROM production_lines")
prod_lines = {r['line_id']: r for r in cur.fetchall()}

cur.execute("SELECT * FROM suppliers")
suppliers = {r['supplier_id']: r for r in cur.fetchall()}

# Enrich distributors with region info
for d in distributors.values():
    reg = regions[d['region_id']]
    d['region_name'] = reg['region_name']
    d['macro_region'] = reg['macro_region']
    d['population_index'] = float(reg['population_index']) if reg['population_index'] else 0.1

# Build product groups
products_by_group = defaultdict(list)
for p in all_products:
    products_by_group[p['product_group']].append(p)

# Build product weights for selection — use power-law (cube) to enforce Pareto 80/20
product_weights = [float(p['popularity_weight']) ** 3 for p in all_products]
total_weight = sum(product_weights)
product_probs = [w / total_weight for w in product_weights]

# Separate mineral vs non-mineral products
mineral_products = [p for p in all_products if p['product_type'] == 'mineral']
mineral_weights = [float(p['popularity_weight']) ** 3 for p in mineral_products]
mineral_total = sum(mineral_weights)
mineral_probs = [w / mineral_total for w in mineral_weights]

non_mineral_products = [p for p in all_products if p['product_type'] != 'mineral']
non_mineral_weights = [float(p['popularity_weight']) ** 3 for p in non_mineral_products]
non_mineral_total = sum(non_mineral_weights)
non_mineral_probs = [w / non_mineral_total for w in non_mineral_weights]

# ============================================================
# HELPER FUNCTIONS
# ============================================================
def months_between(d1, d2):
    """Number of months from d1 to d2 (d2 > d1 → positive)."""
    return (d2.year - d1.year) * 12 + (d2.month - d1.month)

def months_from_start(d):
    return months_between(START_DATE, d)

def months_ago(d):
    """How many months ago is d from CURRENT_DATE (1 = current month, 2 = last month, etc)."""
    d_m = date(d.year, d.month, 1)
    c_m = date(CURRENT_DATE.year, CURRENT_DATE.month, 1)
    return months_between(d_m, c_m) + 1

def get_category_for_product(product):
    """Map product_group to category seasonality key."""
    group = product['product_group']
    if group in CATEGORY_SEASONALITY:
        return group
    # Fallback mappings
    if 'xe máy' in group.lower():
        return 'Dầu xe máy'
    return 'Dầu xe máy'  # default

def select_product_for_order(distributor, is_dbscl):
    """Select a product weighted by popularity, with ĐBSCL mineral bias."""
    if is_dbscl:
        # 72% chance mineral, 28% non-mineral
        if random.random() < 0.72:
            idx = random.choices(range(len(mineral_products)), weights=mineral_weights, k=1)[0]
            return mineral_products[idx]
        else:
            idx = random.choices(range(len(non_mineral_products)), weights=non_mineral_weights, k=1)[0]
            return non_mineral_products[idx]
    else:
        # Normal: ~55% mineral by weighted selection (natural from product catalog)
        idx = random.choices(range(len(all_products)), weights=product_weights, k=1)[0]
        return all_products[idx]

def generate_order_volume():
    """Log-normal distribution for order size in liters."""
    # mean ~500, std ~300, min 50, max 5000
    vol = random.lognormvariate(math.log(400), 0.6)
    return max(50, min(5000, vol))

def get_region_weight(distributor):
    rname = distributor['region_name']
    base = REGION_WEIGHT.get(rname, 0.05)
    pop = distributor['population_index']
    return base * pop

# ============================================================
# GENERATE SALES ORDERS
# ============================================================
print("Generating sales orders...")

sales_orders = []
order_counter = 0

# Iterate month by month
current = START_DATE
while current <= END_DATE:
    year = current.year
    month = current.month
    m_from_start = months_from_start(current)
    m_ago = months_ago(current)

    # Growth multiplier: 8% YoY = ~0.667%/month
    growth_mult = 1 + (0.08 / 12) * m_from_start

    # Monthly seasonality
    monthly_s = MONTHLY_SEASONALITY[month - 1]

    # Days in this month
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    days_in_month = (next_month - current).days

    for dist_id, dist in distributors.items():
        tier = dist['tier']
        tier_cfg = TIER_CONFIG[tier]
        region_w = get_region_weight(dist)
        is_dbscl = dist['region_name'] == DBSCL_REGION
        channel = channels[dist['channel_id']]

        # Number of orders this month for this distributor
        base_orders = random.randint(tier_cfg[0], tier_cfg[1])
        # Apply monthly seasonality only (region weight already baked into tier assignment)
        num_orders = max(1, int(base_orders * monthly_s))

        # Growth anomaly for NPP-003 (Bách Khoa)
        bach_khoa_mult = 1.0
        if dist_id == GROWTH_ANOMALY_NPP:
            # 45% YoY growth, applied progressively
            bach_khoa_mult = 1 + 0.45 * (m_from_start / 18)

        for _ in range(num_orders):
            # Pick a random day in the month
            day_offset = random.randint(0, days_in_month - 1)
            order_date = current + timedelta(days=day_offset)
            weekday = order_date.weekday()

            # Weekly pattern
            weekly_s = WEEKLY_PATTERN[weekday]

            # Skip some Sunday orders
            if weekday == 6 and random.random() > 0.4:
                continue

            # Select product
            product = select_product_for_order(dist, is_dbscl)
            cat_key = get_category_for_product(product)
            cat_s = CATEGORY_SEASONALITY.get(cat_key, [1.0]*12)[month - 1]

            # Base volume
            base_vol = generate_order_volume()

            # Apply tier scaling
            tier_scale = tier_cfg[2] / 1200  # normalize to Đại lý cấp 1
            volume = base_vol * tier_scale * weekly_s * cat_s * growth_mult * bach_khoa_mult

            # Random noise ±15%
            volume *= random.uniform(0.85, 1.15)
            # Scale down total volume to target ~1,200 tỷ total (18 months)
            volume *= 0.42
            volume = max(20, round(volume, 2))

            # Pricing
            base_price = int(product['unit_price_vnd'])
            cost_base = int(product['cost_per_liter_vnd'])

            # Price discount by tier
            if tier == 'Tổng đại lý':
                price_mult = random.uniform(0.92, 0.97)
            elif tier == 'Đại lý cấp 1':
                price_mult = random.uniform(0.95, 0.99)
            else:
                price_mult = random.uniform(0.98, 1.02)

            unit_price = int(base_price * price_mult)
            total_revenue = int(volume * unit_price)

            # COGS calculation — target base margin ~28-29%
            # cost_base is product-level base cost/liter
            # Apply 1.04x uplift to bring margin from ~32% to ~28.5%
            effective_cost = cost_base * 1.04
            # Material: ~65% of COGS
            cogs_material = int(volume * effective_cost * 0.65)
            # Production: ~20%
            cogs_production = int(volume * effective_cost * 0.20)
            # Transport: ~15%
            cogs_transport = int(volume * effective_cost * 0.15)

            # === ANOMALY 2: ĐBSCL higher costs (transport +50%, material +10%) ===
            # Applied BEFORE anomaly 1 so cumulative effect creates ~19% margin
            if is_dbscl:
                cogs_transport = int(cogs_transport * 1.50)
                cogs_material = int(cogs_material * 1.10)

            # === ANOMALY 1: COGS increase in last 6 months ===
            if m_ago >= 1 and m_ago <= 6:
                month_offset = 7 - m_ago  # 1→6 (1=oldest in window, 6=newest)
                cogs_material = int(cogs_material * (1 + 0.015 * month_offset))
                cogs_transport = int(cogs_transport * (1 + 0.01 * month_offset))

            total_cogs = cogs_material + cogs_production + cogs_transport
            gross_profit = total_revenue - total_cogs
            gross_margin = round(gross_profit / total_revenue * 100, 2) if total_revenue > 0 else 0

            # Ensure margin is reasonable (skip if negative — shouldn't happen with our pricing)
            if gross_margin < 0:
                # Adjust price up slightly to maintain positive margin
                unit_price = int(total_cogs / volume * 1.08)
                total_revenue = int(volume * unit_price)
                gross_profit = total_revenue - total_cogs
                gross_margin = round(gross_profit / total_revenue * 100, 2)

            # Invoice and due dates
            invoice_date = order_date + timedelta(days=random.randint(0, 2))
            payment_term = dist['payment_term_days']
            due_date = invoice_date + timedelta(days=payment_term)

            order_counter += 1
            order_id = f"SO-{order_date.year}-{order_counter:06d}"

            sales_orders.append((
                order_id, order_date, dist_id, product['product_id'],
                volume, unit_price, total_revenue,
                cogs_material, cogs_production, cogs_transport,
                total_cogs, gross_profit, gross_margin,
                invoice_date, due_date, 'pending'  # payment_status set later
            ))

    # Move to next month
    if month == 12:
        current = date(year + 1, 1, 1)
    else:
        current = date(year, month + 1, 1)

print(f"Generated {len(sales_orders)} sales orders")

# Sort by date
sales_orders.sort(key=lambda x: x[1])

# ============================================================
# GENERATE PAYMENTS & UPDATE PAYMENT STATUS
# ============================================================
print("Generating payments...")

payments = []
payment_counter = 0
updated_orders = []

for order in sales_orders:
    (order_id, order_date, dist_id, product_id,
     volume, unit_price, total_revenue,
     cogs_material, cogs_production, cogs_transport,
     total_cogs, gross_profit, gross_margin,
     invoice_date, due_date, _) = order

    dist = distributors[dist_id]

    # Determine payment behavior
    # Normal: pay within ±5 days of due_date
    base_delay = random.randint(-5, 5)  # days from due_date

    # === ANOMALY 3: DSO increasing for 3 NPPs ===
    order_month_start = date(order_date.year, order_date.month, 1)
    m_ago_order = months_ago(order_month_start)

    if dist_id in DSO_ANOMALY_NPPS and m_ago_order >= 1 and m_ago_order <= 5:
        extra_delay = DSO_DELAY_BY_MONTHS_AGO.get(m_ago_order, 0)
        base_delay = extra_delay + random.randint(-2, 2)
    elif dist_id == GROWTH_ANOMALY_NPP:
        # Bách Khoa: fast payer, DSO ~12-18 days
        base_delay = random.randint(-18, -12)  # pay well before due

    payment_date = due_date + timedelta(days=base_delay)

    # Don't generate payment for future dates
    if payment_date > CURRENT_DATE:
        # Still pending
        payment_status = 'pending'
        if due_date < CURRENT_DATE:
            payment_status = 'overdue'
        updated_orders.append(order[:15] + (payment_status,))
        continue

    is_overdue = payment_date > due_date
    days_from_inv = (payment_date - invoice_date).days

    # Payment status
    if is_overdue:
        payment_status = 'overdue' if payment_date > CURRENT_DATE else 'paid'
        # Some overdue are still unpaid
        if due_date > CURRENT_DATE - timedelta(days=60) and is_overdue:
            payment_status = 'overdue'
    else:
        payment_status = 'paid'

    # For recently overdue ones, mark differently
    if dist_id in DSO_ANOMALY_NPPS and m_ago_order <= 2 and is_overdue:
        payment_status = 'overdue'

    payment_counter += 1
    pay_id = f"PAY-{payment_date.year}-{payment_counter:06d}"

    # Payment method
    if total_revenue > 500000000:  # > 500M
        method = 'Chuyển khoản'
    elif total_revenue > 50000000:  # > 50M
        method = random.choice(['Chuyển khoản', 'Chuyển khoản', 'Tiền mặt'])
    else:
        method = random.choice(['Chuyển khoản', 'Tiền mặt', 'Tiền mặt'])

    payments.append((
        pay_id, order_id, dist_id, payment_date,
        total_revenue, method, days_from_inv, is_overdue
    ))

    updated_orders.append(order[:15] + (payment_status,))

# Replace sales_orders with updated payment statuses
sales_orders = updated_orders

print(f"Generated {len(payments)} payments")

# ============================================================
# GENERATE PRODUCTION BATCHES
# ============================================================
print("Generating production batches...")

production_batches = []
batch_counter = 0

# Map product groups to production lines
def get_line_for_product(product):
    vol_ml = product['volume_ml'] or 1000
    ptype = product['product_type']
    if ptype == 'grease':
        return 'LINE-05'
    elif vol_ml <= 4000:
        return 'LINE-02'  # Small bottles
    elif vol_ml <= 25000:
        return 'LINE-03'  # Large cans
    else:
        return 'LINE-04'  # Drums

# Generate batches month by month
current = START_DATE
while current <= END_DATE:
    year = current.year
    month = current.month
    m_ago_batch = months_ago(current)

    # For each production line, generate batches
    for line_id, line in prod_lines.items():
        max_cap = int(line['max_capacity_liters_per_month'])
        target_yield = float(line['target_yield_rate'])

        # Capacity utilization: 60-85% normally, trending up
        m_from_s = months_from_start(current)
        base_util = 0.65 + 0.01 * m_from_s  # slowly increasing
        base_util = min(0.88, base_util)
        monthly_s = MONTHLY_SEASONALITY[month - 1]
        utilization = base_util * monthly_s
        utilization = max(0.40, min(0.95, utilization))

        target_output = max_cap * utilization

        # Number of batches per month per line (target: 5K-8K total / 18 months / 5 lines ≈ 55-90/line/month)
        if line_id == 'LINE-01':  # Blending - large batches
            batches_per_month = random.randint(50, 80)
        elif line_id == 'LINE-05':  # Grease - fewer batches
            batches_per_month = random.randint(25, 40)
        else:
            batches_per_month = random.randint(60, 100)

        batch_size = target_output / batches_per_month

        # Select products for this line
        line_products = [p for p in all_products if get_line_for_product(p) == line_id]
        if not line_products:
            line_products = all_products[:5]  # fallback
        line_weights = [float(p['popularity_weight']) for p in line_products]

        for b in range(batches_per_month):
            # Random day in month
            if month == 12:
                nm = date(year + 1, 1, 1)
            else:
                nm = date(year, month + 1, 1)
            days_in_m = (nm - current).days
            batch_date = current + timedelta(days=random.randint(0, days_in_m - 1))

            # Skip weekends for production
            if batch_date.weekday() >= 6:
                batch_date -= timedelta(days=1)

            # Select product
            pidx = random.choices(range(len(line_products)), weights=line_weights, k=1)[0]
            product = line_products[pidx]

            # Batch size with noise
            input_qty = batch_size * random.uniform(0.7, 1.3)
            input_qty = max(500, round(input_qty, 2))

            # === ANOMALY 5: LINE-02 yield declining ===
            if line_id == 'LINE-02' and m_ago_batch >= 1 and m_ago_batch <= 4:
                yield_targets = {4: 0.975, 3: 0.968, 2: 0.959, 1: 0.948}
                yr = yield_targets[m_ago_batch] + random.uniform(-0.003, 0.003)
            else:
                yr = target_yield + random.uniform(-0.005, 0.005)
                yr = max(0.94, min(0.995, yr))

            output_qty = round(input_qty * yr, 2)
            yield_rate = round(output_qty / input_qty, 3)

            # Costs
            avg_material_cost = int(product['cost_per_liter_vnd']) if product['cost_per_liter_vnd'] else 18000
            material_cost = int(input_qty * avg_material_cost * 0.65)
            labor_cost = int(input_qty * 1800)  # ~1800 VND/liter labor
            overhead_cost = int(input_qty * 1500)  # ~1500 VND/liter overhead
            total_prod_cost = material_cost + labor_cost + overhead_cost
            cost_per_liter = int(total_prod_cost / output_qty) if output_qty > 0 else 0

            batch_counter += 1
            batch_id = f"BATCH-{batch_date.year}-{batch_counter:05d}"

            production_batches.append((
                batch_id, batch_date, line_id, product['product_id'],
                input_qty, output_qty, yield_rate,
                material_cost, labor_cost, overhead_cost,
                total_prod_cost, cost_per_liter
            ))

    if month == 12:
        current = date(year + 1, 1, 1)
    else:
        current = date(year, month + 1, 1)

print(f"Generated {len(production_batches)} production batches")

# ============================================================
# GENERATE RAW MATERIAL COSTS
# ============================================================
print("Generating raw material costs...")

raw_material_costs = []
BASE_PRICES = {
    'base_oil_group_I': 14000,
    'base_oil_group_II': 18000,
    'base_oil_group_III': 28000,
    'base_oil_group_IV': 45000,
    'additive': 35000,
    'naphthenic_base_oil': 22000,
}

current = START_DATE
while current <= END_DATE:
    m_from_s = months_from_start(current)
    m_ago_rmc = months_ago(current)

    for sup_id, sup in suppliers.items():
        mat_type = sup['material_type']
        base_price = BASE_PRICES.get(mat_type, 20000)

        # === ANOMALY 6: Price trend + spike ===
        # Trend: +0.5%/month
        price = base_price * (1 + 0.005 * m_from_s)
        # Spike last 3 months: +2%/month
        if m_ago_rmc >= 1 and m_ago_rmc <= 3:
            price *= (1 + 0.02 * (4 - m_ago_rmc))

        # Random noise ±3%
        price *= random.uniform(0.97, 1.03)
        price = int(price)

        # Volume purchased - proportional to supplier importance
        base_volume = random.uniform(50000, 200000)
        monthly_s = MONTHLY_SEASONALITY[current.month - 1]
        volume = round(base_volume * monthly_s, 2)

        total_cost = int(price * volume)

        raw_material_costs.append((
            current, sup_id, mat_type, price, volume, total_cost
        ))

    if current.month == 12:
        current = date(current.year + 1, 1, 1)
    else:
        current = date(current.year, current.month + 1, 1)

print(f"Generated {len(raw_material_costs)} raw material cost records")

# ============================================================
# INSERT INTO DATABASE
# ============================================================
print("\nInserting into database...")

# Clear existing data
cur2 = conn.cursor()
cur2.execute("SET FOREIGN_KEY_CHECKS = 0")
for table in ['payments', 'sales_orders', 'production_batches', 'raw_material_costs']:
    cur2.execute(f"TRUNCATE TABLE {table}")
cur2.execute("SET FOREIGN_KEY_CHECKS = 1")
conn.commit()

# Insert sales_orders in batches of 1000
print(f"  Inserting {len(sales_orders)} sales orders...")
INSERT_SO = """INSERT INTO sales_orders
    (order_id, order_date, distributor_id, product_id, quantity_liters, unit_price_vnd,
     total_revenue_vnd, cogs_material_vnd, cogs_production_vnd, cogs_transport_vnd,
     total_cogs_vnd, gross_profit_vnd, gross_margin_pct, invoice_date, due_date, payment_status)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""

for i in range(0, len(sales_orders), 1000):
    batch = sales_orders[i:i+1000]
    cur2.executemany(INSERT_SO, batch)
    if (i // 1000) % 20 == 0:
        print(f"    ... {i+len(batch)}/{len(sales_orders)}")
conn.commit()
print(f"  Sales orders done: {len(sales_orders)}")

# Insert payments
print(f"  Inserting {len(payments)} payments...")
INSERT_PAY = """INSERT INTO payments
    (payment_id, order_id, distributor_id, payment_date, amount_vnd,
     payment_method, days_from_invoice, is_overdue)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""

for i in range(0, len(payments), 1000):
    batch = payments[i:i+1000]
    cur2.executemany(INSERT_PAY, batch)
conn.commit()
print(f"  Payments done: {len(payments)}")

# Insert production_batches
print(f"  Inserting {len(production_batches)} production batches...")
INSERT_PB = """INSERT INTO production_batches
    (batch_id, batch_date, line_id, product_id, input_quantity_liters, output_quantity_liters,
     yield_rate, material_cost_vnd, labor_cost_vnd, overhead_cost_vnd,
     total_production_cost_vnd, cost_per_liter_vnd)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""

for i in range(0, len(production_batches), 1000):
    batch = production_batches[i:i+1000]
    cur2.executemany(INSERT_PB, batch)
conn.commit()
print(f"  Production batches done: {len(production_batches)}")

# Insert raw_material_costs
print(f"  Inserting {len(raw_material_costs)} raw material costs...")
INSERT_RMC = """INSERT INTO raw_material_costs
    (month_date, supplier_id, material_type, price_per_liter_vnd,
     volume_purchased_liters, total_cost_vnd)
    VALUES (%s,%s,%s,%s,%s,%s)"""

cur2.executemany(INSERT_RMC, raw_material_costs)
conn.commit()
print(f"  Raw material costs done: {len(raw_material_costs)}")

# ============================================================
# QUICK VALIDATION
# ============================================================
print("\n=== QUICK VALIDATION ===")

valcur = conn.cursor(dictionary=True)

valcur.execute("SELECT COUNT(*) as cnt FROM sales_orders")
print(f"Sales orders: {valcur.fetchone()['cnt']}")

valcur.execute("SELECT COUNT(*) as cnt FROM payments")
print(f"Payments: {valcur.fetchone()['cnt']}")

valcur.execute("SELECT COUNT(*) as cnt FROM production_batches")
print(f"Production batches: {valcur.fetchone()['cnt']}")

valcur.execute("SELECT COUNT(*) as cnt FROM raw_material_costs")
print(f"Raw material costs: {valcur.fetchone()['cnt']}")

# Revenue check
valcur.execute("""
    SELECT SUM(total_revenue_vnd)/1e9 as total_bn,
           AVG(gross_margin_pct) as avg_margin
    FROM sales_orders
""")
r = valcur.fetchone()
print(f"\nTotal revenue (18mo): {r['total_bn']:.1f} tỷ VND")
print(f"Average margin: {r['avg_margin']:.1f}%")

# Monthly trend
valcur.execute("""
    SELECT DATE_FORMAT(order_date, '%Y-%m') as month,
           SUM(total_revenue_vnd)/1e9 as revenue_bn,
           AVG(gross_margin_pct) as margin
    FROM sales_orders
    GROUP BY month ORDER BY month
""")
print("\nMonthly revenue trend:")
for row in valcur.fetchall():
    print(f"  {row['month']}: {row['revenue_bn']:.1f} tỷ, margin {row['margin']:.1f}%")

# ĐBSCL margin check
valcur.execute("""
    SELECT r.region_name,
           SUM(s.total_revenue_vnd)/1e9 as revenue_bn,
           SUM(s.gross_profit_vnd)/SUM(s.total_revenue_vnd)*100 as margin_pct
    FROM sales_orders s
    JOIN distributors d ON s.distributor_id = d.distributor_id
    JOIN regions r ON d.region_id = r.region_id
    GROUP BY r.region_name
    ORDER BY margin_pct
""")
print("\nMargin by region:")
for row in valcur.fetchall():
    print(f"  {row['region_name']}: {row['revenue_bn']:.1f} tỷ, margin {row['margin_pct']:.1f}%")

# DSO check for anomaly NPPs
valcur.execute("""
    SELECT d.distributor_name, DATE_FORMAT(p.payment_date, '%Y-%m') as month,
           AVG(p.days_from_invoice) as avg_dso, COUNT(*) as cnt
    FROM payments p
    JOIN distributors d ON p.distributor_id = d.distributor_id
    WHERE p.distributor_id IN ('NPP-008', 'NPP-015', 'NPP-022')
    AND p.payment_date >= '2025-11-01'
    GROUP BY d.distributor_name, month
    ORDER BY d.distributor_name, month
""")
print("\nDSO trend (anomaly NPPs, last 5 months):")
for row in valcur.fetchall():
    print(f"  {row['distributor_name']} | {row['month']}: DSO={row['avg_dso']:.0f} days ({row['cnt']} payments)")

# Yield check
valcur.execute("""
    SELECT pl.line_name, DATE_FORMAT(pb.batch_date, '%Y-%m') as month,
           AVG(pb.yield_rate) as avg_yield
    FROM production_batches pb
    JOIN production_lines pl ON pb.line_id = pl.line_id
    WHERE pb.batch_date >= '2025-12-01'
    GROUP BY pl.line_name, month
    ORDER BY pl.line_name, month
""")
print("\nYield by line (last 4 months):")
for row in valcur.fetchall():
    print(f"  {row['line_name']} | {row['month']}: yield={row['avg_yield']:.3f}")

valcur.close()

cur2.close()
cur.close()
conn.close()
print("\nDone!")
