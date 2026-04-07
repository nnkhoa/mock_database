#!/usr/bin/env python3
"""
Generate transaction data for Nova Consumer (NCG) demo database.
18 months: Jul 2024 - Dec 2025.
Includes 5 demo scenario anomalies.
"""

import mysql.connector
import random
import math
from datetime import date, timedelta
from decimal import Decimal

random.seed(42)

conn = mysql.connector.connect(
    host='localhost', port=3306, user='root', password='root',
    database='nova_consumer_demo', charset='utf8mb4'
)
cur = conn.cursor()

# ============================================
# HELPER: Generate months
# ============================================
months_18 = []
for y in [2024, 2025]:
    for m in range(1, 13):
        d = date(y, m, 1)
        if date(2024, 7, 1) <= d <= date(2025, 12, 1):
            months_18.append(d)
# months_18 = [2024-07-01, 2024-08-01, ..., 2025-12-01] = 18 months

# ============================================
# LOAD MASTER DATA REFERENCES
# ============================================
cur.execute("SELECT segment_id, segment_code FROM business_segments")
seg_map = {code: sid for sid, code in cur.fetchall()}

cur.execute("SELECT factory_id, factory_code, max_capacity_tons_month, fixed_cost_monthly FROM factories")
factories_data = {}
for fid, fcode, cap, fixed in cur.fetchall():
    factories_data[fcode] = {'id': fid, 'capacity': float(cap) if cap else None, 'fixed_cost': float(fixed)}

cur.execute("SELECT farm_id, farm_code FROM farms")
farm_map = {code: fid for fid, code in cur.fetchall()}

cur.execute("SELECT material_id, material_code, cogs_share_pct FROM raw_materials")
materials_data = {}
for mid, mcode, share in cur.fetchall():
    materials_data[mcode] = {'id': mid, 'share': float(share) if share else None}

cur.execute("SELECT supplier_id, supplier_code FROM suppliers")
sup_map = {code: sid for sid, code in cur.fetchall()}

cur.execute("SELECT product_id, product_code, segment_id, category_id, unit_price, unit_cost, popularity_weight, target_animal, unit FROM products")
products_data = []
for row in cur.fetchall():
    products_data.append({
        'id': row[0], 'code': row[1], 'segment_id': row[2], 'category_id': row[3],
        'price': float(row[4]) if row[4] else 0, 'cost': float(row[5]) if row[5] else 0,
        'weight': float(row[6]) if row[6] else 1.0, 'animal': row[7], 'unit': row[8]
    })

cur.execute("SELECT customer_id, customer_code, segment_id, channel_id, region_id, revenue_tier, customer_type FROM customers")
customers_data = []
for row in cur.fetchall():
    customers_data.append({
        'id': row[0], 'code': row[1], 'segment_id': row[2], 'channel_id': row[3],
        'region_id': row[4], 'tier': row[5], 'type': row[6]
    })

cur.execute("SELECT channel_id, channel_code FROM distribution_channels")
ch_map = {code: cid for cid, code in cur.fetchall()}

cur.execute("SELECT subsidiary_id, subsidiary_code, segment_id FROM subsidiaries")
sub_data = {}
for sid, scode, seg in cur.fetchall():
    sub_data[scode] = {'id': sid, 'segment_id': seg}

cur.execute("SELECT region_id, region_code FROM regions")
region_map = {code: rid for rid, code in cur.fetchall()}

# ============================================
# SEASONALITY COEFFICIENTS
# ============================================
seasonality_tacn = {1: 1.08, 2: 0.82, 3: 0.90, 4: 0.95, 5: 0.98, 6: 0.93,
                    7: 0.95, 8: 1.00, 9: 1.08, 10: 1.12, 11: 1.10, 12: 1.09}

seasonality_vet = {1: 1.05, 2: 0.88, 3: 0.95, 4: 1.00, 5: 1.02, 6: 1.08,
                   7: 1.10, 8: 1.05, 9: 1.02, 10: 0.98, 11: 0.95, 12: 0.92}

seasonality_farm = {1: 1.15, 2: 0.85, 3: 0.88, 4: 0.92, 5: 0.95, 6: 0.90,
                    7: 0.95, 8: 1.00, 9: 1.05, 10: 1.10, 11: 1.12, 12: 1.13}

# NVL price seasonality (corn)
ngo_price_factor = {1: 1.00, 2: 0.98, 3: 0.97, 4: 0.96, 5: 0.95, 6: 0.97,
                    7: 1.00, 8: 1.02, 9: 1.05, 10: 1.03, 11: 1.01, 12: 1.00}

# ============================================
# 1. SEGMENT FINANCIALS (54 records)
# ============================================
print("Generating segment_financials...")

base_revenue = {
    seg_map['ANIMAL_HEALTH']: 106000,  # triệu VND/tháng
    seg_map['ANIMAL_FEED']: 195000,
    seg_map['FARM']: 53000,
}
base_margin = {
    seg_map['ANIMAL_HEALTH']: 0.42,
    seg_map['ANIMAL_FEED']: 0.15,
    seg_map['FARM']: 0.09,
}
growth_rates = {
    seg_map['ANIMAL_HEALTH']: 0.08,
    seg_map['ANIMAL_FEED']: 0.06,
    seg_map['FARM']: 0.10,
}
seasonalities = {
    seg_map['ANIMAL_HEALTH']: seasonality_vet,
    seg_map['ANIMAL_FEED']: seasonality_tacn,
    seg_map['FARM']: seasonality_farm,
}
headcounts = {
    seg_map['ANIMAL_HEALTH']: 1200,
    seg_map['ANIMAL_FEED']: 1800,
    seg_map['FARM']: 800,
}
opex_ratio = {
    seg_map['ANIMAL_HEALTH']: 0.22,
    seg_map['ANIMAL_FEED']: 0.08,
    seg_map['FARM']: 0.05,
}

sf_records = []
for i, ym in enumerate(months_18):
    for seg_id in [1, 2, 3]:
        month_idx = i  # 0-17
        m = ym.month

        # Growth multiplier (linear over 18 months)
        growth = 1 + (growth_rates[seg_id] * (month_idx / 17))

        # Seasonality
        season = seasonalities[seg_id][m]

        # Noise ±5%
        noise = random.uniform(0.95, 1.05)

        revenue = base_revenue[seg_id] * season * growth * noise
        margin = base_margin[seg_id]

        # ANOMALY S1: TACN margin erosion — last 4 months (Sep-Dec 2025)
        if seg_id == seg_map['ANIMAL_FEED'] and ym >= date(2025, 9, 1):
            anomaly_offset = (ym.year - 2025) * 12 + ym.month - 8  # 1,2,3,4
            # COGS inflated: margin drops from ~15% to ~12.8%
            cogs_multiplier = 1 + 0.012 * anomaly_offset
            cogs = revenue * (1 - margin) * cogs_multiplier
        else:
            cogs = revenue * (1 - margin) * random.uniform(0.98, 1.02)

        opex = revenue * opex_ratio[seg_id] * random.uniform(0.95, 1.05)
        hc = headcounts[seg_id] + random.randint(-20, 20)

        sf_records.append((seg_id, ym, round(revenue, 2), round(cogs, 2),
                           round(opex, 2), hc))

cur.executemany(
    "INSERT INTO segment_financials (segment_id, `year_month`, total_revenue, total_cogs, operating_expense, headcount) VALUES (%s,%s,%s,%s,%s,%s)",
    sf_records
)
print(f"  segment_financials: {len(sf_records)} records")

# ============================================
# 2. PRODUCTION MONTHLY (90 records = 5 factories × 18 months)
# ============================================
print("Generating production_monthly...")

# TACN factories cost structure
# Calibrated so cost/ton matches spec:
#   DN@72% → ~4.35, DN@55% → ~4.85, LA@68% → ~4.52, HY@70-78% → ~4.41-4.20
# Total monthly fixed cost per factory (depreciation + fixed labor + fixed overhead)
total_fixed_monthly = {
    'NM_TACN_LA': 12000,   # triệu VND — smaller factory
    'NM_TACN_DN': 29100,   # triệu VND — large, calibrated for 4.35@72%→4.85@55%
    'NM_TACN_HY': 27500,   # triệu VND — large, slightly lower
}
variable_cost_per_ton = 2.73  # triệu VND/tấn (NVL + biến đổi)
base_cost_per_ton = 4.20  # reference for BOM calculations

# Fixed cost split: depreciation 40%, labor 35%, overhead 25%
fixed_split = {'depreciation': 0.40, 'labor': 0.35, 'overhead': 0.25}
# Variable cost split: NVL 85%, labor 8%, overhead 7%
var_split = {'raw_material': 0.85, 'labor': 0.08, 'overhead': 0.07}

# Base utilization rates
base_util = {
    'NM_TACN_LA': 0.68,
    'NM_TACN_DN': 0.72,
    'NM_TACN_HY': 0.70,
}

# Waste %
base_waste = {
    'NM_TACN_LA': 1.8,
    'NM_TACN_DN': 2.2,
    'NM_TACN_HY': 1.7,
}

pm_records = []
for i, ym in enumerate(months_18):
    m = ym.month
    season = seasonality_tacn[m]

    for fcode in ['NM_TACN_LA', 'NM_TACN_DN', 'NM_TACN_HY']:
        fdata = factories_data[fcode]
        fid = fdata['id']
        capacity = fdata['capacity']

        util = base_util[fcode]

        # ANOMALY S2: Đồng Nai utilization drop (Sep-Dec 2025)
        if fcode == 'NM_TACN_DN' and ym >= date(2025, 9, 1):
            anomaly_month = (ym.year - 2025) * 12 + ym.month - 8  # 1,2,3,4
            util_schedule = {1: 0.72, 2: 0.65, 3: 0.60, 4: 0.55}
            util = util_schedule[anomaly_month]
        # ANOMALY S2 counter: Hưng Yên utilization increase (Sep-Dec 2025)
        elif fcode == 'NM_TACN_HY' and ym >= date(2025, 9, 1):
            anomaly_month = (ym.year - 2025) * 12 + ym.month - 8
            util_schedule = {1: 0.70, 2: 0.73, 3: 0.76, 4: 0.78}
            util = util_schedule[anomaly_month]
        else:
            # Normal slight variation
            util = util * season * random.uniform(0.96, 1.04)
            util = min(util, 0.92)  # cap at 92%

        actual_output = capacity * util
        actual_output = round(actual_output, 2)

        # Cost breakdown: fixed (doesn't change) + variable (scales with output)
        fixed_total = total_fixed_monthly[fcode]
        var_total = variable_cost_per_ton * actual_output

        depreciation = round(fixed_total * fixed_split['depreciation'], 2)
        labor_cost = round(fixed_total * fixed_split['labor'] + var_total * var_split['labor'], 2)
        raw_material_cost = round(var_total * var_split['raw_material'] * random.uniform(0.97, 1.03), 2)
        overhead = round(fixed_total * fixed_split['overhead'] + var_total * var_split['overhead'], 2)

        waste = base_waste[fcode] + random.uniform(-0.3, 0.3)

        pm_records.append((fid, ym, actual_output, capacity,
                           raw_material_cost, labor_cost, depreciation, overhead,
                           round(waste, 2)))

    # Thuốc thú y & Vaccine factories (simplified — no tons, use revenue-based proxy)
    for fcode in ['NM_THUOC_BD', 'NM_VACCINE_DN']:
        fdata = factories_data[fcode]
        fid = fdata['id']
        fixed_cost = fdata['fixed_cost']

        season_v = seasonality_vet[m]
        growth = 1 + (0.08 * (i / 17))

        # Use output in "units equivalent" — represent as tons equivalent for consistency
        base_output = 500 if fcode == 'NM_THUOC_BD' else 300  # tons equivalent
        actual_output = round(base_output * season_v * growth * random.uniform(0.95, 1.05), 2)
        max_cap = 800 if fcode == 'NM_THUOC_BD' else 500

        raw_material_cost = round(actual_output * 8.0 * random.uniform(0.97, 1.03), 2)  # higher cost/ton for pharma
        labor_cost = round(fixed_cost * 0.40 + actual_output * 1.5, 2)
        depreciation = round(fixed_cost * 0.35, 2)
        overhead = round(fixed_cost * 0.25 + actual_output * 0.8, 2)
        waste = round(random.uniform(0.5, 1.5), 2)

        pm_records.append((fid, ym, actual_output, max_cap,
                           raw_material_cost, labor_cost, depreciation, overhead, waste))

cur.executemany(
    "INSERT INTO production_monthly (factory_id, `year_month`, actual_output_tons, max_capacity_tons, raw_material_cost, labor_cost, depreciation, overhead, waste_pct) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
    pm_records
)
print(f"  production_monthly: {len(pm_records)} records")

# ============================================
# 3. MATERIAL PURCHASES (~5,000 records)
# ============================================
print("Generating material_purchases...")

base_prices = {
    'NVL_NGO': 7200,
    'NVL_DTUONG': 11500,
    'NVL_CAMGAO': 5800,
    'NVL_DDGS': 6500,
    'NVL_PREMIX': 45000,
    'NVL_BOTCA': 22000,
    'NVL_DAUDAU': 18000,
    'NVL_LYSINE': 32000,
    'NVL_METHIONINE': 65000,
    'NVL_MUOI': 3500,
    'NVL_CAMMI': 5200,
}

# Supplier mapping per material per factory
# Each factory uses specific suppliers for each material
material_suppliers = {
    'NVL_NGO': {
        'NM_TACN_LA': ['SUP_CARGILL', 'SUP_BUNGE'],
        'NM_TACN_DN': ['SUP_ADM', 'SUP_COFCO'],
        'NM_TACN_HY': ['SUP_CORN_SL', 'SUP_LDC'],  # Sơn La supplier for Hưng Yên!
    },
    'NVL_DTUONG': {
        'NM_TACN_LA': ['SUP_BUNGE', 'SUP_LDC'],
        'NM_TACN_DN': ['SUP_CARGILL', 'SUP_ADM'],
        'NM_TACN_HY': ['SUP_COFCO', 'SUP_OLAM'],
    },
    'NVL_CAMGAO': {
        'NM_TACN_LA': ['SUP_CAMGAO_AG', 'SUP_CAMGAO_TG'],
        'NM_TACN_DN': ['SUP_CAMGAO_CT', 'SUP_CAMGAO_AG'],
        'NM_TACN_HY': ['SUP_CAMGAO_TB', 'SUP_CAMGAO_CT'],
    },
    'NVL_DDGS': {
        'NM_TACN_LA': ['SUP_WILMAR'],
        'NM_TACN_DN': ['SUP_OLAM'],
        'NM_TACN_HY': ['SUP_WILMAR'],
    },
    'NVL_PREMIX': {
        'NM_TACN_LA': ['SUP_DSM'],
        'NM_TACN_DN': ['SUP_DSM'],
        'NM_TACN_HY': ['SUP_DSM'],
    },
    'NVL_BOTCA': {
        'NM_TACN_LA': ['SUP_BOTCA_BTH'],
        'NM_TACN_DN': ['SUP_BOTCA_KH'],
        'NM_TACN_HY': ['SUP_BOTCA_KH'],
    },
    'NVL_DAUDAU': {
        'NM_TACN_LA': ['SUP_WILMAR'],
        'NM_TACN_DN': ['SUP_WILMAR'],
        'NM_TACN_HY': ['SUP_OLAM'],
    },
    'NVL_LYSINE': {
        'NM_TACN_LA': ['SUP_CJ_BIO'],
        'NM_TACN_DN': ['SUP_CJ_BIO'],
        'NM_TACN_HY': ['SUP_CJ_BIO'],
    },
    'NVL_METHIONINE': {
        'NM_TACN_LA': ['SUP_EVONIK'],
        'NM_TACN_DN': ['SUP_EVONIK'],
        'NM_TACN_HY': ['SUP_EVONIK'],
    },
    'NVL_MUOI': {
        'NM_TACN_LA': ['SUP_MUOI_NA'],
        'NM_TACN_DN': ['SUP_MUOI_NA'],
        'NM_TACN_HY': ['SUP_MUOI_NA'],
    },
    'NVL_CAMMI': {
        'NM_TACN_LA': ['SUP_CAMMI_BD'],
        'NM_TACN_DN': ['SUP_CAMMI_BD'],
        'NM_TACN_HY': ['SUP_CAMMI_HN'],
    },
}

# Origin countries for imported materials
origin_countries = {
    'NVL_NGO': 'Argentina',
    'NVL_DTUONG': 'Brazil',
    'NVL_DDGS': 'Mỹ',
    'NVL_PREMIX': 'Hà Lan',
    'NVL_DAUDAU': 'Argentina',
    'NVL_LYSINE': 'Hàn Quốc',
    'NVL_METHIONINE': 'Đức',
}

# COGS share → approximate quantity needed per month per factory
# Based on total output and material share of cost
mp_records = []
for i, ym in enumerate(months_18):
    m = ym.month
    for fcode in ['NM_TACN_LA', 'NM_TACN_DN', 'NM_TACN_HY']:
        fdata = factories_data[fcode]
        capacity = fdata['capacity']
        util = base_util[fcode]

        # Apply anomaly utilization
        if fcode == 'NM_TACN_DN' and ym >= date(2025, 9, 1):
            ao = (ym.year - 2025) * 12 + ym.month - 8
            util = {1: 0.72, 2: 0.65, 3: 0.60, 4: 0.55}[ao]
        elif fcode == 'NM_TACN_HY' and ym >= date(2025, 9, 1):
            ao = (ym.year - 2025) * 12 + ym.month - 8
            util = {1: 0.70, 2: 0.73, 3: 0.76, 4: 0.78}[ao]
        else:
            util = util * seasonality_tacn[m] * random.uniform(0.96, 1.04)
            util = min(util, 0.92)

        monthly_output = capacity * util  # tons

        for mat_code, bp in base_prices.items():
            mat_data = materials_data[mat_code]
            share = mat_data['share']
            if share is None:
                continue

            # Quantity needed (tons) based on share of total cost
            # share% of (cost_per_ton × output) / price_per_kg / 1000
            quantity_tons = (share / 100) * base_cost_per_ton * monthly_output / (bp / 1000)
            # Simplified: just use share-proportional quantity
            quantity_tons = monthly_output * (share / 100) * 1.1  # ~share% of output weight, adjusted

            # Price calculation with anomalies
            price = bp

            # General seasonal factor
            if mat_code == 'NVL_NGO':
                price *= ngo_price_factor[m]

            # ANOMALY S3: Corn price increase — last 6 months (Jul-Dec 2025)
            if mat_code == 'NVL_NGO' and ym >= date(2025, 7, 1):
                anomaly_offset = (ym.year - 2025) * 12 + ym.month - 6  # 1,2,3,4,5,6
                price = 7200 * (1 + 0.02 * anomaly_offset)
                # T-5: 7200→7344, T-4:7488, T-3:7632, T-2:7776, T-1:7920, T0:8064
                # Approximate: 7200 → 8060 (+12%)

            # ANOMALY S3: Soybean meal price decrease (-8% over 6 months)
            if mat_code == 'NVL_DTUONG' and ym >= date(2025, 7, 1):
                anomaly_offset = (ym.year - 2025) * 12 + ym.month - 6
                price = 11500 * (1 - 0.013 * anomaly_offset)

            # ANOMALY S3: Hưng Yên corn 5% cheaper (Sơn La supplier)
            if mat_code == 'NVL_NGO' and fcode == 'NM_TACN_HY':
                price *= 0.95

            # Random noise ±3%
            price *= random.uniform(0.97, 1.03)

            # Growth trend for prices (slight increase over time)
            price *= 1 + (0.02 * (i / 17))

            # Split into 5-12 purchases per month (~5000 total target
            n_purchases = random.randint(5, 12)
            for p in range(n_purchases):
                pct = random.uniform(0.15, 0.45)
                if p == n_purchases - 1:
                    pct = 1.0  # remaining
                qty = quantity_tons * pct / n_purchases * random.uniform(0.8, 1.2)
                if qty < 0.1:
                    qty = 0.1

                # Random day within month
                day = random.randint(1, 28)
                pdate = date(ym.year, ym.month, day)

                suppliers_for = material_suppliers.get(mat_code, {}).get(fcode, ['SUP_CARGILL'])
                supplier_code = random.choice(suppliers_for)

                origin = origin_countries.get(mat_code, 'Việt Nam')
                if supplier_code.startswith('SUP_CAM') or supplier_code.startswith('SUP_MUOI') or supplier_code.startswith('SUP_BOT') or supplier_code == 'SUP_CORN_SL':
                    origin = 'Việt Nam'

                payment = random.choice(['T/T 30 ngày', 'T/T 45 ngày', 'T/T 60 ngày', 'L/C 90 ngày', 'Trả ngay'])

                mp_records.append((
                    fdata['id'], mat_data['id'], sup_map[supplier_code],
                    pdate, round(qty, 3), round(price, 2),
                    origin, payment
                ))
                quantity_tons -= qty

# Add pharma NVL purchases (simplified)
pharma_mats = ['NVL_API', 'NVL_TADUOC', 'NVL_BAOBI', 'NVL_ADJUVANT']
pharma_suppliers = {
    'NVL_API': ['SUP_API_CN', 'SUP_API_IN', 'SUP_API_EU'],
    'NVL_TADUOC': ['SUP_TADUOC_VN', 'SUP_API_IN'],
    'NVL_BAOBI': ['SUP_BAOBI_BD', 'SUP_BAOBI_LA'],
    'NVL_ADJUVANT': ['SUP_ADJ_FR'],
}
pharma_base_prices = {'NVL_API': 350000, 'NVL_TADUOC': 45000, 'NVL_BAOBI': 15000, 'NVL_ADJUVANT': 280000}
pharma_origins = {'NVL_API': 'Trung Quốc', 'NVL_TADUOC': 'Việt Nam', 'NVL_BAOBI': 'Việt Nam', 'NVL_ADJUVANT': 'Pháp'}

for i, ym in enumerate(months_18):
    for fcode in ['NM_THUOC_BD', 'NM_VACCINE_DN']:
        for mat_code in pharma_mats:
            if mat_code == 'NVL_ADJUVANT' and fcode != 'NM_VACCINE_DN':
                continue  # adjuvant only for vaccine factory

            mat_data = materials_data[mat_code]
            n_purchases = random.randint(1, 2)
            for _ in range(n_purchases):
                qty = random.uniform(0.5, 5.0) if mat_code != 'NVL_BAOBI' else random.uniform(2, 10)
                price = pharma_base_prices[mat_code] * random.uniform(0.95, 1.05)
                day = random.randint(1, 28)
                pdate = date(ym.year, ym.month, day)
                sup_code = random.choice(pharma_suppliers[mat_code])

                mp_records.append((
                    factories_data[fcode]['id'], mat_data['id'], sup_map[sup_code],
                    pdate, round(qty, 3), round(price, 2),
                    pharma_origins[mat_code],
                    random.choice(['T/T 30 ngày', 'T/T 60 ngày', 'L/C 90 ngày'])
                ))

# Batch insert material_purchases
batch_size = 1000
for b in range(0, len(mp_records), batch_size):
    batch = mp_records[b:b+batch_size]
    cur.executemany(
        """INSERT INTO material_purchases (factory_id, material_id, supplier_id, purchase_date,
           quantity_tons, unit_price, origin_country, payment_terms)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
        batch
    )
print(f"  material_purchases: {len(mp_records)} records")

# ============================================
# 4. BILL OF MATERIALS (~500 records)
# ============================================
print("Generating bill_of_materials...")

# Get TACN products
tacn_products = [p for p in products_data if p['segment_id'] == 2]
tacn_materials = ['NVL_NGO', 'NVL_DTUONG', 'NVL_CAMGAO', 'NVL_DDGS', 'NVL_PREMIX',
                  'NVL_BOTCA', 'NVL_DAUDAU', 'NVL_LYSINE', 'NVL_METHIONINE', 'NVL_MUOI', 'NVL_CAMMI']

# Standard BOM (kg per ton of finished product)
standard_bom = {
    'NVL_NGO': 400,       # 400 kg corn per ton feed
    'NVL_DTUONG': 220,    # 220 kg soybean meal
    'NVL_CAMGAO': 120,    # 120 kg rice bran
    'NVL_DDGS': 80,       # 80 kg DDGS
    'NVL_PREMIX': 25,     # 25 kg premix
    'NVL_BOTCA': 50,      # 50 kg fish meal
    'NVL_DAUDAU': 30,     # 30 kg soybean oil
    'NVL_LYSINE': 5,      # 5 kg lysine
    'NVL_METHIONINE': 3,  # 3 kg methionine
    'NVL_MUOI': 10,       # 10 kg salt/binder
    'NVL_CAMMI': 57,      # 57 kg wheat bran (balance to ~1000)
}

bom_records = []
for prod in tacn_products:
    # Vary BOM slightly by animal type
    animal = prod.get('animal', 'Heo')
    for mat_code, base_qty in standard_bom.items():
        qty = base_qty * random.uniform(0.85, 1.15)

        # Adjust by animal type
        if animal == 'Gia cầm':
            if mat_code == 'NVL_NGO':
                qty *= 1.1  # more corn for poultry
            elif mat_code == 'NVL_DTUONG':
                qty *= 1.05
            elif mat_code == 'NVL_BOTCA':
                qty *= 0.7
        elif animal == 'Thủy sản':
            if mat_code == 'NVL_BOTCA':
                qty *= 2.0  # more fish meal
            elif mat_code == 'NVL_NGO':
                qty *= 0.7

        # Cost share calculation
        cost_share = (qty * base_prices[mat_code] / 1000) / (base_cost_per_ton * 1000000) * 100
        # Simplified share
        share_pct = materials_data[mat_code]['share'] if materials_data[mat_code]['share'] else 1.0
        share_pct *= random.uniform(0.9, 1.1)

        bom_records.append((prod['id'], materials_data[mat_code]['id'],
                            round(qty, 4), round(share_pct, 2)))

cur.executemany(
    "INSERT INTO bill_of_materials (product_id, material_id, quantity_per_ton, cost_share_pct) VALUES (%s,%s,%s,%s)",
    bom_records
)
print(f"  bill_of_materials: {len(bom_records)} records")

# ============================================
# 5. SALES TRANSACTIONS (~50,000 records)
# ============================================
print("Generating sales_transactions...")

# Split customers by segment
cust_by_seg = {1: [], 2: [], 3: []}
for c in customers_data:
    cust_by_seg[c['segment_id']].append(c)
# Farm products sold via TACN customers + internal customers (no dedicated farm customers)
if not cust_by_seg[3]:
    cust_by_seg[3] = [c for c in customers_data if c['type'] in ('Nội bộ', 'Trang trại lớn', 'Đại lý cấp 1')]

# Products by segment
prod_by_seg = {1: [], 2: [], 3: []}
for p in products_data:
    prod_by_seg[p['segment_id']].append(p)

# Subsidiary assignment
seg_subsidiaries = {
    1: [sub_data['SGV']['id'], sub_data['ANP']['id'], sub_data['TNV']['id'], sub_data['AVT']['id'], sub_data['BPC']['id']],
    2: [sub_data['ANF']['id']],
    3: [sub_data['AFM']['id'], sub_data['AAG']['id']],
}

# Factory assignment for TACN sales
tacn_factory_ids = [factories_data['NM_TACN_LA']['id'], factories_data['NM_TACN_DN']['id'], factories_data['NM_TACN_HY']['id']]

# Identify "lost" customers for Đồng Nai anomaly (customer_id 1 and 2)
lost_customer_ids = set()
cur.execute("SELECT customer_id FROM customers WHERE customer_code IN ('KH_TACN_001', 'KH_TACN_002')")
for (cid,) in cur.fetchall():
    lost_customer_ids.add(cid)

st_records = []

for i, ym in enumerate(months_18):
    m = ym.month

    for seg_id in [1, 2, 3]:
        season = seasonalities[seg_id][m]
        growth = 1 + (growth_rates[seg_id] * (i / 17))
        target_revenue = base_revenue[seg_id] * season * growth  # triệu VND

        # Target number of transactions per month (~50K total / 18mo / 3seg)
        if seg_id == 1:
            n_txns = random.randint(550, 700)
        elif seg_id == 2:
            n_txns = random.randint(1200, 1500)
        else:
            n_txns = random.randint(100, 150)

        customers_seg = cust_by_seg[seg_id]
        products_seg = prod_by_seg[seg_id]

        # Weighted product selection (Pareto)
        prod_weights = [p['weight'] for p in products_seg]
        total_weight = sum(prod_weights)
        prod_probs = [w / total_weight for w in prod_weights]

        for _ in range(n_txns):
            # Pick product (weighted)
            prod = random.choices(products_seg, weights=prod_probs, k=1)[0]

            # Pick customer (weighted by tier)
            tier_weights = {'A': 4.0, 'B': 2.0, 'C': 1.0}
            cust_weights_list = [tier_weights.get(c['tier'], 1.0) for c in customers_seg]
            cust = random.choices(customers_seg, weights=cust_weights_list, k=1)[0]

            # ANOMALY S2: Lost customers reduce orders from Sep 2025
            if cust['id'] in lost_customer_ids and ym >= date(2025, 9, 1):
                if random.random() < 0.8:  # 80% chance to skip → dramatically reduced orders
                    continue

            # Sale date (random day in month)
            day = random.randint(1, 28)
            sale_date = date(ym.year, ym.month, day)

            # Quantity
            if prod['unit'] in ('kg', 'tấn'):
                if seg_id == 2:
                    # TACN: tons per order
                    qty = random.uniform(5, 50) if cust['tier'] == 'A' else random.uniform(1, 20)
                    if prod['unit'] == 'kg':
                        qty *= 1000  # convert to kg
                else:
                    qty = random.uniform(100, 5000)  # kg for farm products
            elif prod['unit'] == 'liều':
                qty = random.randint(50, 2000)
            elif prod['unit'] in ('chai', 'gói', 'hộp', 'tuýp', 'lít'):
                qty = random.randint(10, 200)
            elif prod['unit'] == 'con':
                qty = random.randint(1, 50)
            elif prod['unit'] == 'quả':
                qty = random.randint(100, 5000)
            else:
                qty = random.uniform(1, 100)

            # Price with small variance
            unit_price = prod['price'] * random.uniform(0.95, 1.05)
            unit_cost = prod['cost'] * random.uniform(0.97, 1.03)

            # Discount for tier A customers
            discount = 0
            if cust['tier'] == 'A':
                discount = random.uniform(2, 8)
            elif cust['tier'] == 'B':
                discount = random.uniform(0, 3)

            total_rev = qty * unit_price * (1 - discount / 100)
            total_cogs = qty * unit_cost

            # Subsidiary
            subs = seg_subsidiaries[seg_id]
            sub_id = random.choice(subs)

            # Factory (for TACN)
            factory_id = None
            if seg_id == 2:
                # Assign factory based on customer region
                region = cust['region_id']
                # Simple mapping: South → Long An/Đồng Nai, North → Hưng Yên
                if region in [region_map.get(c) for c in ['HN', 'HY', 'HD', 'TB', 'SL', 'TH', 'NA']]:
                    factory_id = factories_data['NM_TACN_HY']['id']
                elif region in [region_map.get(c) for c in ['TG', 'DT', 'CT']]:
                    factory_id = factories_data['NM_TACN_LA']['id']
                else:
                    factory_id = factories_data['NM_TACN_DN']['id']

            st_records.append((
                sale_date, seg_id, sub_id, prod['id'], cust['id'],
                cust['channel_id'], factory_id, cust['region_id'],
                round(qty, 3), round(unit_price, 2), round(total_rev, 2),
                round(unit_cost, 2), round(total_cogs, 2), round(discount, 2)
            ))

# Batch insert
for b in range(0, len(st_records), batch_size):
    batch = st_records[b:b+batch_size]
    cur.executemany(
        """INSERT INTO sales_transactions (sale_date, segment_id, subsidiary_id, product_id,
           customer_id, channel_id, factory_id, region_id, quantity, unit_price, total_revenue,
           unit_cost, total_cogs, discount_pct)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        batch
    )
print(f"  sales_transactions: {len(st_records)} records")

# ============================================
# 6. PRODUCTION ORDERS (~3,000 records)
# ============================================
print("Generating production_orders...")

tacn_prods = [p for p in products_data if p['segment_id'] == 2]
tacn_custs = [c for c in customers_data if c['segment_id'] == 2]

po_records = []
for i, ym in enumerate(months_18):
    m = ym.month
    for fcode in ['NM_TACN_LA', 'NM_TACN_DN', 'NM_TACN_HY']:
        fdata = factories_data[fcode]

        # Number of production orders per factory per month (~3000 total / 3 / 18)
        n_orders = random.randint(45, 65)

        for _ in range(n_orders):
            prod = random.choices(tacn_prods, weights=[p['weight'] for p in tacn_prods], k=1)[0]
            cust = random.choice(tacn_custs) if random.random() < 0.7 else None

            order_day = random.randint(1, 25)
            order_date = date(ym.year, ym.month, order_day)
            required_date = order_date + timedelta(days=random.randint(5, 15))
            completed_date = required_date + timedelta(days=random.randint(-2, 3))

            qty = random.uniform(20, 200)

            # Status
            if ym == months_18[-1] and random.random() < 0.15:
                status = 'Đang sản xuất'
                completed_date = None
            elif random.random() < 0.03:
                status = 'Đã hủy'
                completed_date = None
            else:
                status = 'Đã hoàn thành'

            po_records.append((
                fdata['id'], prod['id'],
                cust['id'] if cust else None,
                order_date, required_date, completed_date,
                round(qty, 3), status
            ))

cur.executemany(
    """INSERT INTO production_orders (factory_id, product_id, customer_id, order_date,
       required_date, completed_date, quantity_tons, status)
       VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
    po_records
)
print(f"  production_orders: {len(po_records)} records")

# ============================================
# 7. FARM OPERATIONS (~54+ records)
# ============================================
print("Generating farm_operations...")

farm_animals = {
    'FARM_HT': [
        {'type': 'Heo nái', 'opening': 5000, 'births_rate': 0, 'sales_rate': 0.02, 'death_rate': 0.005},
        {'type': 'Heo thịt', 'opening': 45000, 'births_rate': 0, 'sales_rate': 0.15, 'death_rate': 0.02,
         'feed_per_head': 0.08, 'avg_weight': 110},
    ],
    'FARM_DKN': [
        {'type': 'Heo nái', 'opening': 3000, 'births_rate': 0, 'sales_rate': 0.02, 'death_rate': 0.005},
        {'type': 'Heo thịt', 'opening': 30000, 'births_rate': 0, 'sales_rate': 0.12, 'death_rate': 0.02,
         'feed_per_head': 0.08, 'avg_weight': 108},
        {'type': 'Gà', 'opening': 200000, 'births_rate': 0, 'sales_rate': 0.25, 'death_rate': 0.03,
         'feed_per_head': 0.003, 'avg_weight': 2.5},
    ],
    'FARM_BD': [
        {'type': 'Bò sữa', 'opening': 1000, 'births_rate': 0.03, 'sales_rate': 0.05, 'death_rate': 0.008,
         'feed_per_head': 0.5, 'avg_weight': 450},
        {'type': 'Bò thịt', 'opening': 500, 'births_rate': 0.02, 'sales_rate': 0.08, 'death_rate': 0.01,
         'feed_per_head': 0.3, 'avg_weight': 380},
    ],
}

# Price per kg for revenue calculation
animal_prices = {
    'Heo nái': 55000, 'Heo thịt': 64000, 'Gà': 45000,
    'Bò sữa': 14000, 'Bò thịt': 90000,  # bò sữa = giá sữa/lít
}

fo_records = []
for fcode, animals in farm_animals.items():
    farm_id = farm_map[fcode]
    for animal_info in animals:
        stock = animal_info['opening']
        for i, ym in enumerate(months_18):
            m = ym.month
            season = seasonality_farm[m]

            opening = stock

            # Births (from sows/breeding stock)
            if animal_info['type'] == 'Heo nái':
                births = int(opening * 2.2 / 12 * random.uniform(0.9, 1.1))  # ~2.2 litters/year, ~12 piglets
                births = int(births * 12)  # piglets born
            elif animal_info['type'] in ('Bò sữa', 'Bò thịt'):
                births = int(opening * animal_info['births_rate'] * random.uniform(0.8, 1.2))
            else:
                births = 0

            # For heo nái, births go to heo thịt, not self
            if animal_info['type'] == 'Heo nái':
                actual_births_for_stock = 0  # nái stock stays roughly stable
                births_display = births
            else:
                actual_births_for_stock = births
                births_display = births

            purchases = 0
            if animal_info['type'] == 'Gà':
                # Gà: buy new batches
                purchases = int(opening * 0.25 * random.uniform(0.9, 1.1))

            sales = int(opening * animal_info['sales_rate'] * season * random.uniform(0.9, 1.1))
            deaths = int(opening * animal_info['death_rate'] * random.uniform(0.7, 1.3))

            if animal_info['type'] == 'Heo nái':
                closing = opening - sales - deaths + random.randint(-20, 20)  # roughly stable
            else:
                closing = opening + actual_births_for_stock + purchases - sales - deaths
            closing = max(closing, int(opening * 0.7))

            # Feed & costs
            feed_per_head = animal_info.get('feed_per_head', 0.06)  # tons/head/month
            avg_stock = (opening + closing) / 2
            feed_tons = round(avg_stock * feed_per_head * random.uniform(0.95, 1.05), 2)
            feed_cost = round(feed_tons * 4.2 * random.uniform(0.95, 1.05), 2)  # triệu VND

            vet_cost = round(avg_stock * 0.005 * random.uniform(0.8, 1.2), 2)  # ~5K/head/month
            labor_cost = round(avg_stock * 0.003 * random.uniform(0.9, 1.1), 2)
            other_cost = round(avg_stock * 0.002 * random.uniform(0.8, 1.2), 2)
            total_cost = round(feed_cost + vet_cost + labor_cost + other_cost, 2)

            # Revenue from sales
            avg_weight = animal_info.get('avg_weight', 100)
            price_per_kg = animal_prices[animal_info['type']]

            if animal_info['type'] == 'Bò sữa':
                # Revenue from milk, not meat
                milk_per_cow = 18  # liters/day average
                revenue = round(avg_stock * milk_per_cow * 30 * price_per_kg / 1e6, 2)
            elif animal_info['type'] == 'Heo nái':
                # Revenue from selling piglets/culled sows
                revenue = round(sales * 55000 * 80 / 1e6 + births_display * 1200000 * 0.1 / 1e6, 2)
            else:
                revenue = round(sales * avg_weight * price_per_kg * season / 1e6, 2)

            fo_records.append((
                farm_id, ym, animal_info['type'],
                opening,
                births_display if animal_info['type'] != 'Heo nái' else 0,
                purchases, sales, deaths, closing,
                feed_tons, feed_cost, vet_cost, labor_cost, other_cost, total_cost,
                revenue, round(avg_weight * random.uniform(0.97, 1.03), 2)
            ))

            stock = closing

cur.executemany(
    """INSERT INTO farm_operations (farm_id, `year_month`, animal_type, opening_stock,
       births, purchases, sales, deaths, closing_stock, feed_consumed_tons,
       feed_cost, vet_cost, labor_cost, other_cost, total_cost, revenue, avg_weight_kg)
       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
    fo_records
)
print(f"  farm_operations: {len(fo_records)} records")

# ============================================
# 8. LOGISTICS COSTS (~21 routes = 3 factories × 7 vùng)
# ============================================
print("Generating logistics_costs...")

# Distance/cost matrix (approximate)
logistics = []
vung_codes = ['DBSH', 'TDMNPB', 'BTBDHMT', 'TN', 'DNB', 'DBSCL', 'XK']

# Distances from each factory to each region (km)
distances = {
    'NM_TACN_LA': {'DBSH': 1700, 'TDMNPB': 1900, 'BTBDHMT': 1100, 'TN': 350, 'DNB': 50, 'DBSCL': 80, 'XK': 100},
    'NM_TACN_DN': {'DBSH': 1650, 'TDMNPB': 1850, 'BTBDHMT': 1050, 'TN': 300, 'DNB': 30, 'DBSCL': 150, 'XK': 80},
    'NM_TACN_HY': {'DBSH': 50, 'TDMNPB': 200, 'BTBDHMT': 350, 'TN': 1400, 'DNB': 1600, 'DBSCL': 1750, 'XK': 150},
}

for fcode, dists in distances.items():
    fid = factories_data[fcode]['id']
    for vcode, dist in dists.items():
        rid = region_map[vcode]
        # Cost per ton: base 50K + 300 VND/km/ton
        cost = 50000 + 300 * dist
        transit = max(1, dist // 300)

        logistics.append((fid, rid, cost, transit, dist))

cur.executemany(
    "INSERT INTO logistics_costs (from_factory_id, to_region_id, cost_per_ton, transit_days, distance_km) VALUES (%s,%s,%s,%s,%s)",
    logistics
)
print(f"  logistics_costs: {len(logistics)} records")

# ============================================
# COMMIT
# ============================================
conn.commit()

# ============================================
# SUMMARY
# ============================================
print("\n=== TRANSACTION DATA SUMMARY ===")
fact_tables = ['segment_financials', 'production_monthly', 'material_purchases',
               'bill_of_materials', 'sales_transactions', 'production_orders',
               'farm_operations', 'logistics_costs']
for t in fact_tables:
    cur.execute(f"SELECT COUNT(*) FROM {t}")
    print(f"  {t}: {cur.fetchone()[0]} records")

# Verify anomalies
print("\n=== ANOMALY VERIFICATION ===")

# S1: TACN margin trend
cur.execute("""
    SELECT `year_month`, total_revenue, total_cogs, gross_margin_pct
    FROM segment_financials WHERE segment_id = 2
    ORDER BY `year_month` DESC LIMIT 6
""")
print("\nS1 — TACN margin (last 6 months):")
for row in cur.fetchall():
    print(f"  {row[0]}: revenue={row[1]:.0f}, cogs={row[2]:.0f}, margin={row[3]}%")

# S2: Đồng Nai utilization
cur.execute("""
    SELECT `year_month`, actual_output_tons, utilization_pct, cost_per_ton
    FROM production_monthly WHERE factory_id = %s
    ORDER BY `year_month` DESC LIMIT 6
""", (factories_data['NM_TACN_DN']['id'],))
print("\nS2 — Đồng Nai utilization (last 6 months):")
for row in cur.fetchall():
    print(f"  {row[0]}: output={row[1]:.0f}t, util={row[2]}%, cost/t={row[3]}")

# S3: Corn prices
cur.execute("""
    SELECT DATE_FORMAT(purchase_date, '%Y-%m') as ym, AVG(unit_price) as avg_price
    FROM material_purchases WHERE material_id = %s
    GROUP BY ym ORDER BY ym DESC LIMIT 8
""", (materials_data['NVL_NGO']['id'],))
print("\nS3 — Corn avg price (last 8 months):")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]:.0f} đ/kg")

cur.close()
conn.close()
print("\nDone!")
