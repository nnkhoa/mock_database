#!/usr/bin/env python3
"""
Phú Mỹ Hưng Development — Real Estate Demo Database Generator
Generates 18 months of data (01/2024 – 06/2025) for phu_my_hung_demo database.
3 layers: Base volume → Seasonality → Anomaly injection

Output:
  1. Direct MySQL population
  2. SQL file: phu_my_hung_sql/04_transaction_data.sql
"""

import random
import math
import os
from datetime import date, timedelta, datetime
from collections import defaultdict

import mysql.connector

random.seed(42)

# =============================================================================
# CONFIG
# =============================================================================
DB_CONFIG = dict(host='127.0.0.1', port=3306, user='root', password='root')
DB_NAME = 'phu_my_hung_demo'
SQL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'phu_my_hung_sql')
BATCH_SIZE = 1000

# 18 months: 2024-01 to 2025-06
MONTHS = [date(2024 + (m - 1) // 12, (m - 1) % 12 + 1, 1) for m in range(1, 19)]
CURRENT_DATE = date(2025, 6, 30)

# =============================================================================
# SEASONALITY COEFFICIENTS
# =============================================================================
# Index 0=Jan ... 11=Dec
REVENUE_SEASONALITY = [0.60, 0.45, 0.90, 1.05, 1.10, 1.05, 0.95, 0.90, 1.15, 1.20, 1.15, 1.10]
CONSTRUCTION_SEASONALITY = [0.85, 0.65, 0.95, 1.05, 1.10, 1.15, 0.90, 0.85, 1.05, 1.10, 1.10, 1.00]
COLLECTION_SEASONALITY = [0.82, 0.72, 0.90, 0.95, 0.96, 0.94, 0.93, 0.92, 0.95, 0.97, 0.96, 0.88]

YOY_GROWTH = 0.15  # 15% annual
MONTHLY_GROWTH = (1 + YOY_GROWTH) ** (1 / 12)  # ~1.0117

# =============================================================================
# BASE VOLUMES
# =============================================================================
# Monthly revenue in billion VND
BASE_REVENUE = {
    'PRJ-001': 85,   # The Aurora — active selling/delivering
    'PRJ-002': 45,   # L'Arcade — construction, recognition based
    'PRJ-003': 15,   # Cardinal Court — delivered, residual
    'PRJ-004': 10,   # The Horizon — delivered, residual
    'PRJ-005': 0,    # Hồng Hạc — no sales yet
    'PRJ-006': 8,    # Scenic Valley Shops — slow sales
}

COST_RATIO = {
    'PRJ-001': 0.55,
    'PRJ-002': 0.58,
    'PRJ-003': 0.60,
    'PRJ-004': 0.62,
    'PRJ-005': None,
    'PRJ-006': 0.50,
}

SGA_RATIO = {
    'PRJ-001': 0.08,
    'PRJ-002': 0.06,
    'PRJ-003': 0.05,
    'PRJ-004': 0.04,
    'PRJ-005': 0.02,
    'PRJ-006': 0.07,
}

# Hồng Hạc monthly infrastructure cost (billion VND), ramping up
HONG_HAC_BASE_COST = 80

# Budget allocations by category (% of total budget)
BUDGET_ALLOCATION = {
    'foundation':     0.15,
    'structure':      0.30,
    'mep':            0.18,
    'finishing':      0.15,
    'facade':         0.08,
    'landscaping':    0.05,
    'infrastructure': 0.06,
    'contingency':    0.03,
}

# Project total budgets (billion VND)
PROJECT_BUDGETS = {
    'PRJ-001': 520,
    'PRJ-002': 700,
    'PRJ-003': 1080,
    'PRJ-004': 375,   # The Horizon — will overrun to ~420
    'PRJ-005': 4000,
    'PRJ-006': 225,
}

# Contractor assignments per project
# {project_id: [(contractor_id, role, scope, category, contract_value_bn)]}
CONTRACTOR_ASSIGNMENTS = {
    'PRJ-001': [
        ('CTR-002', 'main_contractor', 'Structure & facade', 'structure', 180),
        ('CTR-007', 'sub_contractor', 'MEP installation', 'mep', 85),
        ('CTR-005', 'sub_contractor', 'Foundation works', 'foundation', 55),
        ('CTR-012', 'sub_contractor', 'Interior finishing', 'finishing', 70),
        ('CTR-009', 'sub_contractor', 'Landscaping', 'landscaping', 25),
    ],
    'PRJ-002': [
        ('CTR-003', 'main_contractor', 'Full construction', 'structure', 280),
        ('CTR-007', 'sub_contractor', 'MEP systems', 'mep', 120),
        ('CTR-010', 'sub_contractor', 'Waterproofing & facade', 'facade', 65),
        ('CTR-012', 'sub_contractor', 'Ultra-luxury interiors', 'finishing', 150),
    ],
    'PRJ-003': [
        ('CTR-001', 'main_contractor', 'Full construction', 'structure', 350),
        ('CTR-007', 'sub_contractor', 'MEP', 'mep', 160),
        ('CTR-004', 'sub_contractor', 'Finishing & fit-out', 'finishing', 200),
    ],
    'PRJ-004': [
        ('CTR-001', 'main_contractor', 'Structure & superstructure', 'structure', 120),
        ('CTR-005', 'sub_contractor', 'Foundation piling', 'foundation', 45),
        ('CTR-007', 'sub_contractor', 'MEP installation', 'mep', 65),
        ('CTR-004', 'sub_contractor', 'Finishing works', 'finishing', 55),
        ('CTR-010', 'sub_contractor', 'Waterproofing', 'facade', 30),
    ],
    'PRJ-005': [
        ('CTR-008', 'main_contractor', 'Foundation & earthworks', 'foundation', 600),
        ('CTR-006', 'sub_contractor', 'Road & utilities infrastructure', 'infrastructure', 450),
        ('CTR-005', 'sub_contractor', 'Piling works Phase 1', 'foundation', 280),
        ('CTR-009', 'sub_contractor', 'Green space & landscaping', 'landscaping', 120),
    ],
    'PRJ-006': [
        ('CTR-004', 'main_contractor', 'Shop fit-out', 'finishing', 90),
        ('CTR-011', 'sub_contractor', 'Elevator installation', 'mep', 35),
    ],
}

# Unit type distribution per project (unit_type_id, count)
# Pareto: 2BR and 3BR apartments dominate
UNIT_DISTRIBUTION = {
    'PRJ-001': [('UT-001', 15), ('UT-002', 40), ('UT-003', 30), ('UT-004', 5), ('UT-006', 5)],
    'PRJ-002': [('UT-003', 10), ('UT-004', 8), ('UT-005', 12), ('UT-006', 7)],
    'PRJ-003': [('UT-001', 30), ('UT-002', 85), ('UT-003', 65), ('UT-004', 10), ('UT-006', 10)],
    'PRJ-004': [('UT-001', 80), ('UT-002', 200), ('UT-003', 150), ('UT-004', 16), ('UT-005', 10), ('UT-006', 20)],
    'PRJ-005': [],  # No sales yet
    'PRJ-006': [('UT-007', 45)],
}

# Unit type price ranges per sqm (min, max) — already defined in master data
UNIT_TYPE_PRICES = {
    'UT-001': (85_000_000, 120_000_000),
    'UT-002': (90_000_000, 130_000_000),
    'UT-003': (95_000_000, 150_000_000),
    'UT-004': (150_000_000, 250_000_000),
    'UT-005': (120_000_000, 200_000_000),
    'UT-006': (100_000_000, 160_000_000),
    'UT-007': (200_000_000, 400_000_000),
    'UT-008': (80_000_000, 120_000_000),
}

UNIT_TYPE_AREAS = {
    'UT-001': (55, 65),
    'UT-002': (75, 95),
    'UT-003': (100, 140),
    'UT-004': (180, 300),
    'UT-005': (250, 500),
    'UT-006': (150, 250),
    'UT-007': (50, 150),
    'UT-008': (100, 500),
}

# Segment price multiplier (relative to base)
SEGMENT_MULTIPLIER = {
    'PRJ-001': 1.10,  # premium
    'PRJ-002': 1.40,  # ultra luxury
    'PRJ-003': 1.15,  # luxury
    'PRJ-004': 1.05,  # luxury but older
    'PRJ-005': 0.75,  # mid-high, Bac Ninh
    'PRJ-006': 1.20,  # commercial premium
}

# Management zone base costs (million VND/month per unit)
ZONE_BASE_COST = {
    'ZON-001': {'staff': 1.8, 'security': 1.2, 'elevator_maintenance': 0.8, 'waterproofing_repairs': 0.3,
                'landscaping': 0.5, 'utilities': 1.0, 'cleaning': 0.8, 'other': 0.8},
    'ZON-002': {'staff': 0.9, 'security': 0.6, 'elevator_maintenance': 0.65, 'waterproofing_repairs': 0.43,
                'landscaping': 0.4, 'utilities': 0.35, 'cleaning': 0.3, 'other': 0.17},
    'ZON-003': {'staff': 1.0, 'security': 0.7, 'elevator_maintenance': 0.3, 'waterproofing_repairs': 0.25,
                'landscaping': 0.6, 'utilities': 0.4, 'cleaning': 0.35, 'other': 0.2},
    'ZON-004': {'staff': 1.2, 'security': 0.9, 'elevator_maintenance': 0.5, 'waterproofing_repairs': 0.2,
                'landscaping': 0.4, 'utilities': 0.6, 'cleaning': 0.5, 'other': 0.3},
    'ZON-005': {'staff': 1.0, 'security': 0.7, 'elevator_maintenance': 0.45, 'waterproofing_repairs': 0.3,
                'landscaping': 0.5, 'utilities': 0.45, 'cleaning': 0.35, 'other': 0.25},
    'ZON-006': {'staff': 1.1, 'security': 0.8, 'elevator_maintenance': 0.5, 'waterproofing_repairs': 0.25,
                'landscaping': 0.5, 'utilities': 0.5, 'cleaning': 0.4, 'other': 0.25},
    'ZON-007': {'staff': 1.5, 'security': 1.0, 'elevator_maintenance': 0.4, 'waterproofing_repairs': 0.2,
                'landscaping': 0.8, 'utilities': 0.6, 'cleaning': 0.5, 'other': 0.3},
    'ZON-008': {'staff': 1.0, 'security': 0.8, 'elevator_maintenance': 0.3, 'waterproofing_repairs': 0.15,
                'landscaping': 0.3, 'utilities': 0.8, 'cleaning': 0.4, 'other': 0.25},
}

ZONE_UNITS = {
    'ZON-001': 1200, 'ZON-002': 2800, 'ZON-003': 1500, 'ZON-004': 2200,
    'ZON-005': 1800, 'ZON-006': 2500, 'ZON-007': 600, 'ZON-008': 400,
}

# Management fee per unit per month (million VND)
ZONE_FEE_PER_UNIT = {
    'ZON-001': 6.5, 'ZON-002': 3.5, 'ZON-003': 4.0, 'ZON-004': 4.8,
    'ZON-005': 3.8, 'ZON-006': 4.2, 'ZON-007': 5.5, 'ZON-008': 5.0,
}


# =============================================================================
# HELPERS
# =============================================================================
def bn_to_vnd(bn):
    """Billion VND to VND."""
    return int(bn * 1_000_000_000)

def mn_to_vnd(mn):
    """Million VND to VND."""
    return int(mn * 1_000_000)

def noise(lo=0.88, hi=1.12):
    return random.uniform(lo, hi)

def month_index(d):
    """0-based month index from MONTHS[0]."""
    return (d.year - 2024) * 12 + d.month - 1

def growth_factor(mi):
    """Compound growth factor for month index mi."""
    return MONTHLY_GROWTH ** mi

def seasonal(mi, coeffs):
    """Get seasonality coefficient for month index."""
    return coeffs[mi % 12]

def lognormal_price(median, sigma=0.08):
    """Log-normal price around median."""
    return int(median * math.exp(random.gauss(0, sigma)))

def random_date_in_month(d):
    """Random date within the month."""
    if d.month == 12:
        last_day = 31
    else:
        last_day = (date(d.year, d.month + 1, 1) - timedelta(days=1)).day
    day = random.randint(1, last_day)
    return date(d.year, d.month, day)

def format_date(d):
    return d.strftime('%Y-%m-%d') if d else 'NULL'

def sql_str(s):
    if s is None:
        return 'NULL'
    return "'" + str(s).replace("'", "''") + "'"

def sql_val(v):
    if v is None:
        return 'NULL'
    return str(v)

def batch_inserts(table, columns, rows, batch_size=BATCH_SIZE):
    """Generate INSERT statements in batches."""
    stmts = []
    cols_str = ', '.join(columns)
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i + batch_size]
        values = []
        for row in batch:
            vals = ', '.join(sql_val(v) for v in row)
            values.append(f'({vals})')
        stmts.append(f"INSERT INTO {table} ({cols_str}) VALUES\n" + ',\n'.join(values) + ';')
    return '\n\n'.join(stmts)


# =============================================================================
# DATA GENERATION
# =============================================================================
class DataGenerator:
    def __init__(self):
        self.project_financials = []
        self.project_budgets = []
        self.unit_sales = []
        self.payment_schedules = []
        self.payment_collections = []
        self.revenue_recognition = []
        self.construction_costs = []
        self.contractor_invoices = []
        self.contract_milestones = []
        self.project_assignments = []
        self.change_orders = []
        self.material_prices = []
        self.debt_schedule = []
        self.debt_payments = []
        self.unsold_inventory = []
        self.project_permits = []
        self.construction_payment_schedule = []
        self.management_costs = []
        self.management_revenue = []
        self.maintenance_tickets = []
        self.lease_income = []
        self.management_fees_monthly = []

        self.sale_counter = 0
        self.invoice_counter = 0
        self.ticket_counter = 0

    def generate_all(self):
        print("Layer 1+2: Base volumes with seasonality...")
        self.gen_material_prices()
        self.gen_project_budgets()
        self.gen_project_assignments()
        self.gen_unit_sales()
        self.gen_payment_schedules_and_collections()
        self.gen_project_financials()
        self.gen_revenue_recognition()
        self.gen_construction_costs()
        self.gen_contractor_invoices()
        self.gen_contract_milestones()
        self.gen_construction_payment_schedule()
        self.gen_debt_schedule_and_payments()
        self.gen_project_permits()
        self.gen_management_costs()
        self.gen_management_revenue()
        self.gen_maintenance_tickets()
        self.gen_lease_income()
        self.gen_management_fees_monthly()
        self.gen_unsold_inventory()

        print("Layer 3: Anomaly injection...")
        self.inject_anomaly_1_larcade_recognition()
        self.inject_anomaly_2_horizon_overrun()
        self.inject_anomaly_3_delta_underperformance()
        self.inject_anomaly_4_cashflow_gap()
        self.inject_anomaly_5_bond_maturity()
        self.inject_anomaly_6_unsold_commercial()
        self.inject_anomaly_7_canh_doi_maintenance()

        self.gen_change_orders()  # After anomaly 2

        print("Data generation complete.")

    # -------------------------------------------------------------------------
    # Material Prices
    # -------------------------------------------------------------------------
    def gen_material_prices(self):
        materials = ['steel_rebar', 'cement', 'glass_aluminum', 'electrical_cable', 'plumbing_pipe', 'finishing_material']
        base_prices = {
            'steel_rebar': 14500000,  # VND/ton
            'cement': 1650000,
            'glass_aluminum': 850000,
            'electrical_cable': 320000,
            'plumbing_pipe': 280000,
            'finishing_material': 450000,
        }
        for mat in materials:
            for mi, md in enumerate(MONTHS):
                # Normal: slight inflation 0.3% per month + noise
                idx = 100 * (1.003 ** mi) * noise(0.97, 1.03)
                price = int(base_prices[mat] * idx / 100)
                self.material_prices.append((mat, format_date(md), round(idx, 2), price))
        # Anomaly 2 (steel spike) will be injected later

    # -------------------------------------------------------------------------
    # Project Budgets
    # -------------------------------------------------------------------------
    def gen_project_budgets(self):
        for proj_id, total_bn in PROJECT_BUDGETS.items():
            for cat, pct in BUDGET_ALLOCATION.items():
                budgeted = bn_to_vnd(total_bn * pct)
                self.project_budgets.append((sql_str(proj_id), sql_str(cat), budgeted))

    # -------------------------------------------------------------------------
    # Project Assignments
    # -------------------------------------------------------------------------
    def gen_project_assignments(self):
        aid = 0
        for proj_id, assignments in CONTRACTOR_ASSIGNMENTS.items():
            for ctr_id, role, scope, cat, val_bn in assignments:
                aid += 1
                # Determine dates based on project
                if proj_id == 'PRJ-005' and ctr_id == 'CTR-005':
                    # Delta on Hồng Hạc Phase 2 — future/planned
                    status = 'planned'
                    start_d = '2025-09-01'
                    end_d = '2026-06-30'
                elif proj_id in ('PRJ-003', 'PRJ-004'):
                    status = 'completed'
                    start_d = '2020-03-01' if proj_id == 'PRJ-004' else '2021-06-01'
                    end_d = '2022-09-30' if proj_id == 'PRJ-004' else '2023-10-15'
                else:
                    status = 'active'
                    start_d = '2024-01-01'
                    end_d = '2026-06-30' if proj_id == 'PRJ-005' else '2025-09-30'

                self.project_assignments.append((
                    sql_str(ctr_id), sql_str(proj_id),
                    'NULL',  # phase_id
                    sql_str(role), sql_str(scope),
                    bn_to_vnd(val_bn),
                    sql_str(start_d), sql_str(end_d), sql_str(status)
                ))

    # -------------------------------------------------------------------------
    # Unit Sales
    # -------------------------------------------------------------------------
    def gen_unit_sales(self):
        for proj_id, dist in UNIT_DISTRIBUTION.items():
            if not dist:
                continue
            multiplier = SEGMENT_MULTIPLIER[proj_id]
            for ut_id, count in dist:
                area_min, area_max = UNIT_TYPE_AREAS[ut_id]
                price_min, price_max = UNIT_TYPE_PRICES[ut_id]
                median_price = (price_min + price_max) / 2 * multiplier

                for i in range(count):
                    self.sale_counter += 1
                    sale_id = f"SAL-{self.sale_counter:04d}"

                    area = round(random.uniform(area_min, area_max), 2)
                    # Floor premium: +3% per 5 floors for apartments
                    floor = None
                    floor_premium = 1.0
                    if ut_id in ('UT-001', 'UT-002', 'UT-003', 'UT-004'):
                        floor = random.randint(2, 35)
                        floor_premium = 1 + (floor / 35) * 0.06  # up to +6% for top floor
                    # Corner premium
                    corner_premium = 1.05 if random.random() < 0.15 else 1.0

                    price_sqm = lognormal_price(median_price * floor_premium * corner_premium, sigma=0.06)
                    total_price = int(price_sqm * area)

                    # Sale date: spread over selling period
                    if proj_id == 'PRJ-001':
                        # Selling from Mar 2024 onwards
                        sale_month = random.choice(MONTHS[2:])  # Mar 2024+
                    elif proj_id == 'PRJ-002':
                        # Sold out by month 10 (Oct 2024)
                        sale_month = random.choice(MONTHS[:10])
                    elif proj_id == 'PRJ-003':
                        # Delivered — sold earlier, but some residual
                        sale_month = random.choice(MONTHS[:6])
                    elif proj_id == 'PRJ-004':
                        # Delivered — historical sales
                        sale_month = random.choice(MONTHS[:4])
                    elif proj_id == 'PRJ-006':
                        # Slow sales throughout period
                        sale_month = random.choice(MONTHS)
                    else:
                        sale_month = random.choice(MONTHS)

                    sale_date = random_date_in_month(sale_month)

                    # Status based on project
                    if proj_id in ('PRJ-003', 'PRJ-004'):
                        status = 'handed_over'
                    elif proj_id == 'PRJ-001':
                        status = random.choice(['contracted', 'paying', 'paying', 'paying'])
                    elif proj_id == 'PRJ-002':
                        status = 'contracted'  # sold but not yet delivered
                    else:
                        status = random.choice(['contracted', 'paying'])

                    # Unit code
                    if ut_id in ('UT-001', 'UT-002', 'UT-003', 'UT-004'):
                        block = random.choice(['A', 'B', 'C'])
                        unit_code = f"{block}-{floor:02d}{random.randint(1,8):02d}"
                    elif ut_id == 'UT-005':
                        unit_code = f"V-{i+1:03d}"
                    elif ut_id == 'UT-006':
                        unit_code = f"TH-{i+1:03d}"
                    elif ut_id == 'UT-007':
                        unit_code = f"SH-{i+1:03d}"
                    else:
                        unit_code = f"OF-{i+1:03d}"

                    buyer = random.choices(['individual', 'corporate', 'foreign'], weights=[0.7, 0.2, 0.1])[0]

                    self.unit_sales.append((
                        sql_str(sale_id), sql_str(proj_id), sql_str(ut_id),
                        sql_str(unit_code), sql_val(floor), area,
                        price_sqm, total_price,
                        sql_str(format_date(sale_date)),
                        sql_str(buyer), sql_str(status)
                    ))

    # -------------------------------------------------------------------------
    # Payment Schedules & Collections
    # -------------------------------------------------------------------------
    def gen_payment_schedules_and_collections(self):
        schedule_id = 0
        for sale in self.unit_sales:
            s_sale_id = sale[0]  # already sql_str
            sale_id_raw = s_sale_id.strip("'")
            total_price = sale[7]  # int
            sale_date_str = sale[8].strip("'")
            sale_date = datetime.strptime(sale_date_str, '%Y-%m-%d').date()
            status = sale[10].strip("'")

            # Standard installment schedule: 5 installments
            # 30% deposit, 20% milestone 1, 20% milestone 2, 20% milestone 3, 10% handover
            pcts = [0.30, 0.20, 0.20, 0.20, 0.10]
            descs = ['Đặt cọc & ký HĐ', 'Đợt 2 — Thi công tầng 10', 'Đợt 3 — Cất nóc',
                     'Đợt 4 — Hoàn thiện', 'Đợt 5 — Bàn giao']

            for inst_no, (pct, desc) in enumerate(zip(pcts, descs), 1):
                schedule_id += 1
                amount = int(total_price * pct)
                due = sale_date + timedelta(days=90 * (inst_no - 1))
                if due > CURRENT_DATE + timedelta(days=180):
                    due = CURRENT_DATE + timedelta(days=random.randint(30, 180))

                self.payment_schedules.append((
                    schedule_id,
                    s_sale_id, inst_no,
                    sql_str(format_date(due)),
                    amount, sql_str(desc)
                ))

                # Collection: generate if due date is past
                if due <= CURRENT_DATE:
                    mi = month_index(due)
                    if 0 <= mi < 18:
                        coll_rate = seasonal(mi, COLLECTION_SEASONALITY)
                    else:
                        coll_rate = 0.93

                    # Most people pay, some delay
                    if random.random() < coll_rate:
                        delay_days = random.randint(0, 15)
                        pay_date = due + timedelta(days=delay_days)
                        if pay_date > CURRENT_DATE:
                            pay_date = CURRENT_DATE
                        pay_amount = amount  # full payment
                        pay_method = random.choices(
                            ['bank_transfer', 'cash', 'mortgage'],
                            weights=[0.65, 0.10, 0.25]
                        )[0]

                        self.payment_collections.append((
                            s_sale_id, schedule_id,
                            sql_str(format_date(pay_date)),
                            pay_amount, sql_str(pay_method)
                        ))

    # -------------------------------------------------------------------------
    # Project Financials
    # -------------------------------------------------------------------------
    def gen_project_financials(self):
        for proj_id in BASE_REVENUE:
            base_rev = BASE_REVENUE[proj_id]
            cr = COST_RATIO[proj_id]
            sga_r = SGA_RATIO[proj_id]

            for mi, md in enumerate(MONTHS):
                gf = growth_factor(mi)
                seas = seasonal(mi, REVENUE_SEASONALITY)
                n = noise()

                if proj_id == 'PRJ-005':
                    # Hồng Hạc: no revenue, only cost
                    rev = 0
                    # Cost ramps up
                    ramp = min(1.0, (mi + 1) / 6)  # ramp over 6 months
                    cost = bn_to_vnd(HONG_HAC_BASE_COST * ramp * seasonal(mi, CONSTRUCTION_SEASONALITY) * noise(0.90, 1.10))
                    sga = bn_to_vnd(base_rev * sga_r if base_rev else 2 * gf * n)
                else:
                    rev = bn_to_vnd(base_rev * gf * seas * n)
                    cost = int(rev * cr * noise(0.95, 1.05)) if cr else 0
                    sga = int(rev * sga_r * noise(0.90, 1.10))

                self.project_financials.append((
                    sql_str(proj_id), sql_str(format_date(md)),
                    rev, cost, sga
                ))

    # -------------------------------------------------------------------------
    # Revenue Recognition
    # -------------------------------------------------------------------------
    def gen_revenue_recognition(self):
        # Pre-compute total contract values from unit_sales
        project_contract_values = defaultdict(int)
        project_units_sold = defaultdict(int)
        project_total_units = {'PRJ-001': 95, 'PRJ-002': 37, 'PRJ-003': 200,
                               'PRJ-004': 476, 'PRJ-005': 300, 'PRJ-006': 45}

        for sale in self.unit_sales:
            pid = sale[1].strip("'")
            project_contract_values[pid] += sale[7]

        for proj_id in BASE_REVENUE:
            total_cv = project_contract_values.get(proj_id, 0)
            total_units = project_total_units[proj_id]

            for mi, md in enumerate(MONTHS):
                # Count units sold up to this month
                units_sold = 0
                for sale in self.unit_sales:
                    pid = sale[1].strip("'")
                    sd = sale[8].strip("'")
                    if pid == proj_id and sd <= format_date(md):
                        units_sold += 1

                sell_through = min(100.0, units_sold / total_units * 100) if total_units > 0 else 0

                # Recognition based on construction progress
                if proj_id == 'PRJ-003':
                    # Delivered — 100%
                    recognized_pct = 100.0
                    construction_pct = 100.0
                elif proj_id == 'PRJ-004':
                    recognized_pct = 100.0
                    construction_pct = 100.0
                elif proj_id == 'PRJ-001':
                    # In progress — steady increase
                    construction_pct = min(95.0, 45 + mi * 3.2)
                    recognized_pct = min(sell_through, construction_pct * 0.95)
                elif proj_id == 'PRJ-002':
                    # L'Arcade — will be overridden by anomaly
                    construction_pct = min(80.0, 10 + mi * 4.0)
                    recognized_pct = construction_pct * 0.8
                elif proj_id == 'PRJ-005':
                    # No sales, no recognition
                    sell_through = 0
                    recognized_pct = 0
                    construction_pct = min(30.0, mi * 1.8)
                elif proj_id == 'PRJ-006':
                    construction_pct = 100.0
                    recognized_pct = sell_through * 0.95

                recognized_rev = int(total_cv * recognized_pct / 100) if total_cv else 0

                self.revenue_recognition.append((
                    sql_str(proj_id), sql_str(format_date(md)),
                    total_cv, recognized_rev,
                    round(recognized_pct, 2), round(sell_through, 2),
                    round(construction_pct, 2) if proj_id != 'PRJ-005' or mi > 0 else 0
                ))

    # -------------------------------------------------------------------------
    # Construction Costs
    # -------------------------------------------------------------------------
    def gen_construction_costs(self):
        for proj_id, assignments in CONTRACTOR_ASSIGNMENTS.items():
            total_budget = PROJECT_BUDGETS[proj_id]
            for ctr_id, role, scope, cat, val_bn in assignments:
                # Spread cost over relevant months with bell-curve distribution
                active_months = []
                for mi, md in enumerate(MONTHS):
                    if proj_id == 'PRJ-005':
                        active_months.append((mi, md))
                    elif proj_id in ('PRJ-003', 'PRJ-004'):
                        # Delivered — residual warranty/maintenance costs only
                        if mi < 12:
                            active_months.append((mi, md))
                    else:
                        active_months.append((mi, md))

                if not active_months:
                    continue

                n_months = len(active_months)
                total_cost_vnd = bn_to_vnd(val_bn)

                for idx, (mi, md) in enumerate(active_months):
                    # Bell curve: more cost in middle months
                    center = n_months / 2
                    sigma = n_months / 4
                    weight = math.exp(-((idx - center) ** 2) / (2 * sigma ** 2))
                    seas = seasonal(mi, CONSTRUCTION_SEASONALITY)

                    # Budget for this month
                    budgeted = int(total_cost_vnd / n_months * weight * seas * 1.5)
                    # Actual: close to budget with noise
                    actual = int(budgeted * noise(0.97, 1.08))

                    if budgeted > 0:
                        self.construction_costs.append((
                            sql_str(proj_id), sql_str(ctr_id), sql_str(cat),
                            sql_str(f'{scope} — {format_date(md)[:7]}'),
                            sql_str(format_date(md)),
                            budgeted, actual
                        ))

    # -------------------------------------------------------------------------
    # Contractor Invoices
    # -------------------------------------------------------------------------
    def gen_contractor_invoices(self):
        for cc in self.construction_costs:
            proj_id = cc[0]
            ctr_id = cc[1]
            cat = cc[2]
            md_str = cc[4].strip("'")
            actual = cc[6]

            if actual <= 0:
                continue

            self.invoice_counter += 1
            inv_id = f"INV-{self.invoice_counter:05d}"
            inv_date = random_date_in_month(datetime.strptime(md_str, '%Y-%m-%d').date())

            status = random.choices(['paid', 'approved', 'pending'], weights=[0.7, 0.2, 0.1])[0]

            self.contractor_invoices.append((
                sql_str(inv_id), ctr_id, proj_id,
                sql_str(format_date(inv_date)),
                actual, cat,
                sql_str(f'Invoice for {cat.strip(chr(39))} works'),
                sql_str(status)
            ))

    # -------------------------------------------------------------------------
    # Contract Milestones
    # -------------------------------------------------------------------------
    def gen_contract_milestones(self):
        milestone_names = [
            'Site preparation complete', 'Foundation complete', 'Structure 50%',
            'Structure complete', 'MEP rough-in', 'Facade 50%', 'Facade complete',
            'Interior finishing start', 'MEP testing', 'Finishing complete',
            'Inspection & handover prep', 'Final handover'
        ]

        for proj_id, assignments in CONTRACTOR_ASSIGNMENTS.items():
            for ctr_id, role, scope, cat, val_bn in assignments:
                # Each contractor gets 5-8 milestones (more data for reliable OTD calc)
                n_milestones = random.randint(5, 8)
                selected = random.sample(milestone_names, min(n_milestones, len(milestone_names)))

                base_date = date(2024, 1, 1)
                if proj_id == 'PRJ-005':
                    base_date = date(2024, 4, 1)

                for j, ms_name in enumerate(selected):
                    planned = base_date + timedelta(days=60 + j * 75 + random.randint(-10, 10))
                    if planned > CURRENT_DATE:
                        actual = None
                        status = 'pending'
                    else:
                        # Normal contractors: 92% on-time, 8% with 1-7 day delays
                        if random.random() < 0.92:
                            actual = planned - timedelta(days=random.randint(0, 5))
                        else:
                            actual = planned + timedelta(days=random.randint(1, 7))
                        status = 'completed'

                    self.contract_milestones.append((
                        sql_str(ctr_id), sql_str(proj_id),
                        sql_str(f'{ms_name} — {scope}'),
                        sql_str(format_date(planned)),
                        sql_str(format_date(actual)) if actual else 'NULL',
                        sql_str(status)
                    ))

    # -------------------------------------------------------------------------
    # Construction Payment Schedule
    # -------------------------------------------------------------------------
    def gen_construction_payment_schedule(self):
        for proj_id in PROJECT_BUDGETS:
            total_bn = PROJECT_BUDGETS[proj_id]
            for mi, md in enumerate(MONTHS):
                for cat, pct in BUDGET_ALLOCATION.items():
                    seas = seasonal(mi, CONSTRUCTION_SEASONALITY)
                    # Bell curve over 18 months
                    center = 9
                    sigma = 5
                    weight = math.exp(-((mi - center) ** 2) / (2 * sigma ** 2))

                    planned = bn_to_vnd(total_bn * pct / 18 * weight * seas * 1.8)
                    actual = int(planned * noise(0.92, 1.08)) if md <= date(2025, 6, 1) else None

                    if planned > 0:
                        self.construction_payment_schedule.append((
                            sql_str(proj_id), sql_str(format_date(md)),
                            planned, sql_val(actual), sql_str(cat)
                        ))

    # -------------------------------------------------------------------------
    # Debt Schedule & Payments
    # -------------------------------------------------------------------------
    def gen_debt_schedule_and_payments(self):
        debts = [
            ('DEBT-001', 'International Bond Tranche A', 'bond_usd', 'USD', 125_000_000,
             125_000_000 * 25000, 5.5, '2019-06-01', '2024-06-01', 'matured'),
            ('DEBT-002', 'International Bond Tranche B', 'bond_usd', 'USD', 100_000_000,
             100_000_000 * 25000, 5.8, '2020-09-01', '2025-04-01', 'active'),
            ('DEBT-003', 'International Bond Tranche C', 'bond_usd', 'USD', 80_000_000,
             80_000_000 * 25000, 6.2, '2021-03-01', '2025-08-01', 'active'),
            ('DEBT-004', 'Vietcombank Term Loan', 'bank_loan', 'VND', 2_000_000_000_000,
             2_000_000_000_000, 7.5, '2022-01-01', '2027-01-01', 'active'),
            ('DEBT-005', 'BIDV Project Finance — Hồng Hạc', 'bank_loan', 'VND', 1_800_000_000_000,
             1_800_000_000_000, 7.8, '2024-03-01', '2029-03-01', 'active'),
            ('DEBT-006', 'VPBank Credit Line', 'credit_line', 'VND', 1_200_000_000_000,
             1_200_000_000_000, 8.2, '2023-06-01', '2026-06-01', 'active'),
        ]

        for d in debts:
            self.debt_schedule.append((
                sql_str(d[0]), sql_str(d[1]), sql_str(d[2]), sql_str(d[3]),
                d[4], d[5], d[6],
                sql_str(d[7]), sql_str(d[8]), sql_str(d[9])
            ))

            # Generate monthly payments
            issue = datetime.strptime(d[7], '%Y-%m-%d').date()
            maturity = datetime.strptime(d[8], '%Y-%m-%d').date()

            for mi, md in enumerate(MONTHS):
                if md < issue or md > maturity:
                    continue
                if d[9] == 'matured' and md > maturity:
                    continue

                # Monthly interest
                monthly_rate = d[6] / 100 / 12
                interest = int(d[5] * monthly_rate)

                # Principal: balloon at maturity, small amortization for bank loans
                principal = 0
                if d[2] in ('bank_loan', 'credit_line'):
                    # Amortizing: principal / remaining months
                    months_remaining = max(1, (maturity.year - md.year) * 12 + maturity.month - md.month)
                    principal = int(d[5] * 0.003)  # ~0.3% monthly amortization
                elif d[2] == 'bond_usd':
                    # Balloon at maturity month
                    if md.year == maturity.year and md.month == maturity.month:
                        principal = d[5]

                pay_type = 'both' if principal > 0 else 'interest'
                pay_date = date(md.year, md.month, 15)

                self.debt_payments.append((
                    sql_str(d[0]),
                    sql_str(format_date(pay_date)),
                    sql_str(pay_type),
                    interest, principal
                ))

    # -------------------------------------------------------------------------
    # Project Permits
    # -------------------------------------------------------------------------
    def gen_project_permits(self):
        permits_data = [
            ('PRJ-001', 'construction', 'approved', '2023-03-01', '2023-05-01', '2023-04-28'),
            ('PRJ-001', 'pre_sale', 'approved', '2023-12-01', '2024-02-01', '2024-01-25'),
            ('PRJ-001', 'fire_safety', 'approved', '2024-06-01', '2024-09-01', '2024-08-20'),
            ('PRJ-002', 'construction', 'approved', '2023-09-01', '2023-12-01', '2023-11-28'),
            ('PRJ-002', 'pre_sale', 'approved', '2024-01-01', '2024-04-01', '2024-03-15'),
            ('PRJ-002', 'fire_safety', 'pending', '2025-01-01', '2025-06-01', None),
            ('PRJ-003', 'completion', 'approved', '2023-06-01', '2023-09-01', '2023-09-10'),
            ('PRJ-004', 'completion', 'approved', '2022-06-01', '2022-08-01', '2022-07-28'),
            ('PRJ-005', 'construction', 'approved', '2024-01-01', '2024-03-01', '2024-02-28'),
            ('PRJ-005', 'environmental', 'approved', '2023-09-01', '2024-01-01', '2023-12-15'),
            ('PRJ-005', 'pre_sale', 'pending', '2025-01-01', '2025-06-01', None),  # ANOMALY: pending
            ('PRJ-006', 'completion', 'approved', '2022-12-01', '2023-02-01', '2023-01-20'),
        ]
        for p in permits_data:
            self.project_permits.append((
                sql_str(p[0]), sql_str(p[1]), sql_str(p[2]),
                sql_str(p[3]) if p[3] else 'NULL',
                sql_str(p[4]) if p[4] else 'NULL',
                sql_str(p[5]) if p[5] else 'NULL',
                'NULL'
            ))

    # -------------------------------------------------------------------------
    # Management Costs
    # -------------------------------------------------------------------------
    def gen_management_costs(self):
        categories = ['staff', 'security', 'elevator_maintenance', 'waterproofing_repairs',
                       'landscaping', 'utilities', 'cleaning', 'other']
        for zone_id, costs in ZONE_BASE_COST.items():
            units = ZONE_UNITS[zone_id]
            for mi, md in enumerate(MONTHS):
                for cat in categories:
                    base = costs.get(cat, 0.2)
                    # Normal inflation: 0.3% per month
                    inflation = 1.003 ** mi
                    cost = mn_to_vnd(base * units * inflation * noise(0.95, 1.05))
                    self.management_costs.append((
                        sql_str(zone_id), sql_str(format_date(md)),
                        sql_str(cat), cost
                    ))

    # -------------------------------------------------------------------------
    # Management Revenue
    # -------------------------------------------------------------------------
    def gen_management_revenue(self):
        for zone_id in ZONE_UNITS:
            units = ZONE_UNITS[zone_id]
            fee = ZONE_FEE_PER_UNIT[zone_id]
            for mi, md in enumerate(MONTHS):
                inflation = 1.003 ** mi
                coll_rate = seasonal(mi, COLLECTION_SEASONALITY) * noise(0.97, 1.03)
                coll_rate = min(1.0, coll_rate)
                rev = mn_to_vnd(fee * units * inflation * coll_rate)
                billed = units
                self.management_revenue.append((
                    sql_str(zone_id), sql_str(format_date(md)),
                    rev, billed, round(coll_rate * 100, 2)
                ))

    # -------------------------------------------------------------------------
    # Maintenance Tickets
    # -------------------------------------------------------------------------
    def gen_maintenance_tickets(self):
        categories = ['elevator', 'waterproofing', 'electrical', 'plumbing', 'hvac', 'general', 'landscaping']
        cat_weights = [0.15, 0.10, 0.15, 0.15, 0.10, 0.25, 0.10]

        for zone_id in ZONE_UNITS:
            units = ZONE_UNITS[zone_id]
            # Base tickets per month proportional to units
            base_tickets = max(5, units // 100)

            for mi, md in enumerate(MONTHS):
                n_tickets = int(base_tickets * noise(0.7, 1.3))
                for _ in range(n_tickets):
                    self.ticket_counter += 1
                    tid = f"TKT-{self.ticket_counter:05d}"
                    cat = random.choices(categories, weights=cat_weights)[0]
                    tdate = random_date_in_month(md)
                    priority = random.choices(['low', 'medium', 'high', 'critical'],
                                              weights=[0.3, 0.4, 0.2, 0.1])[0]

                    # Resolution: most resolved within 1-14 days
                    if random.random() < 0.85:
                        res_days = random.randint(1, 14)
                        res_date = tdate + timedelta(days=res_days)
                        if res_date > CURRENT_DATE:
                            res_date = None
                            status = 'in_progress'
                        else:
                            status = random.choice(['resolved', 'closed'])
                    else:
                        res_date = None
                        status = random.choice(['open', 'in_progress'])

                    # Cost
                    base_cost = {'elevator': 22_000_000, 'waterproofing': 15_000_000,
                                 'electrical': 8_000_000, 'plumbing': 6_000_000,
                                 'hvac': 12_000_000, 'general': 3_000_000,
                                 'landscaping': 5_000_000}
                    cost = int(base_cost.get(cat, 5_000_000) * noise(0.5, 2.0))

                    self.maintenance_tickets.append((
                        sql_str(tid), sql_str(zone_id),
                        sql_str(format_date(tdate)), sql_str(cat),
                        sql_str(f'Sự cố {cat} tại {zone_id}'),
                        sql_str(priority), sql_str(status),
                        sql_str(format_date(res_date)) if res_date else 'NULL',
                        cost
                    ))

    # -------------------------------------------------------------------------
    # Lease Income
    # -------------------------------------------------------------------------
    def gen_lease_income(self):
        tenants = [
            ('TNT-001', 280_000_000), ('TNT-002', 450_000_000), ('TNT-003', 520_000_000),
            ('TNT-004', 185_000_000), ('TNT-005', 320_000_000), ('TNT-006', 150_000_000),
            ('TNT-007', 165_000_000), ('TNT-008', 380_000_000), ('TNT-009', 290_000_000),
            ('TNT-010', 180_000_000), ('TNT-011', 220_000_000), ('TNT-012', 250_000_000),
            ('TNT-013', 195_000_000), ('TNT-014', 850_000_000), ('TNT-015', 680_000_000),
            ('TNT-016', 420_000_000), ('TNT-017', 145_000_000), ('TNT-018', 350_000_000),
        ]
        for tid, rent in tenants:
            for mi, md in enumerate(MONTHS):
                # Slight annual escalation
                escalation = 1.0 + (mi // 12) * 0.05  # 5% per year
                monthly_rent = int(rent * escalation)
                # Collection: most pay full, some delay
                if random.random() < 0.95:
                    collected = monthly_rent
                    occ = 'occupied'
                else:
                    collected = int(monthly_rent * random.uniform(0.5, 0.9))
                    occ = 'occupied'

                self.lease_income.append((
                    sql_str(tid), sql_str(format_date(md)),
                    monthly_rent, collected, sql_str(occ)
                ))

    # -------------------------------------------------------------------------
    # Management Fees Monthly (aggregated)
    # -------------------------------------------------------------------------
    def gen_management_fees_monthly(self):
        # Will be computed after management_costs and management_revenue are final
        pass

    def compute_management_fees_monthly(self):
        """Compute after anomaly injection."""
        rev_by_month = defaultdict(int)
        cost_by_month = defaultdict(int)

        for r in self.management_revenue:
            md = r[1].strip("'")
            rev_by_month[md] += r[2]

        for c in self.management_costs:
            md = c[1].strip("'")
            cost_by_month[md] += c[3]

        for mi, md in enumerate(MONTHS):
            md_str = format_date(md)
            rev = rev_by_month.get(md_str, 0)
            cost = cost_by_month.get(md_str, 0)
            self.management_fees_monthly.append((
                sql_str(md_str), rev, cost
            ))

    # =========================================================================
    # ANOMALY INJECTIONS
    # =========================================================================

    # Anomaly 1: L'Arcade Revenue Recognition Gap
    def inject_anomaly_1_larcade_recognition(self):
        """L'Arcade: 100% sell-through by month 10, but only 62% recognized by month 18."""
        recognition_curve = {
            9: 20.0, 10: 25.0, 11: 30.0, 12: 35.0, 13: 40.0,
            14: 48.0, 15: 53.0, 16: 57.0, 17: 62.0
        }
        for i, rec in enumerate(self.revenue_recognition):
            pid = rec[0].strip("'")
            if pid != 'PRJ-002':
                continue
            md_str = rec[1].strip("'")
            md = datetime.strptime(md_str, '%Y-%m-%d').date()
            mi = month_index(md)

            total_cv = rec[2]

            # Sell-through: ramps to 100% by month 10
            if mi < 3:
                st = mi * 15
            elif mi < 6:
                st = 45 + (mi - 3) * 12
            elif mi < 10:
                st = 81 + (mi - 6) * 5
            else:
                st = 100.0
            st = min(100.0, st)

            # Recognition: tied to construction milestones, lagging
            if mi in recognition_curve:
                rp = recognition_curve[mi]
            elif mi < 9:
                rp = min(st * 0.5, 18.0 + mi * 2.0)
            else:
                rp = 62.0

            construction_pct = rp * 1.05  # construction slightly ahead of recognition

            recognized_rev = int(total_cv * rp / 100)

            self.revenue_recognition[i] = (
                rec[0], rec[1], total_cv, recognized_rev,
                round(rp, 2), round(st, 2), round(min(construction_pct, 65.0), 2)
            )

    # Anomaly 2: The Horizon 12% Cost Overrun
    def inject_anomaly_2_horizon_overrun(self):
        """Steel spike + Hòa Bình delays + change orders → 12% overrun on PRJ-004."""
        # Steel price spike in months 5-8 (Jun-Sep 2024)
        for i, mp in enumerate(self.material_prices):
            if mp[0] != 'steel_rebar':
                continue
            md = datetime.strptime(mp[1], '%Y-%m-%d').date()
            mi = month_index(md)
            if 5 <= mi <= 8:
                # Spike: 100 → 118
                spike = 100 + (mi - 4) * 5  # 105, 110, 115, 118
                if mi == 8:
                    spike = 118
                new_idx = spike * noise(0.98, 1.02)
                new_price = int(14500000 * new_idx / 100)
                self.material_prices[i] = (mp[0], mp[1], round(new_idx, 2), new_price)
            elif 9 <= mi <= 11:
                # Recovery to 112
                recover = 118 - (mi - 8) * 2  # 116, 114, 112
                new_idx = recover * noise(0.98, 1.02)
                new_price = int(14500000 * new_idx / 100)
                self.material_prices[i] = (mp[0], mp[1], round(new_idx, 2), new_price)

        # Inflate steel-related construction costs for PRJ-004 in months 5-9
        for i, cc in enumerate(self.construction_costs):
            pid = cc[0].strip("'")
            ctr = cc[1].strip("'")
            cat = cc[2].strip("'")
            md = datetime.strptime(cc[4].strip("'"), '%Y-%m-%d').date()
            mi = month_index(md)

            if pid == 'PRJ-004' and cat == 'structure' and 5 <= mi <= 9:
                # Steel impact: actual = budget × 1.18
                budgeted = cc[5]
                actual = int(budgeted * 1.18 * noise(0.97, 1.03))
                self.construction_costs[i] = (cc[0], cc[1], cc[2], cc[3], cc[4], budgeted, actual)

        # Add extra Hòa Bình delay charges for PRJ-004 in months 6-7
        for extra_month in [6, 7]:
            md = MONTHS[extra_month]
            self.construction_costs.append((
                sql_str('PRJ-004'), sql_str('CTR-001'), sql_str('structure'),
                sql_str(f'Idle crew charges — delay penalty {format_date(md)[:7]}'),
                sql_str(format_date(md)),
                0,  # no budget for this
                bn_to_vnd(6.3 * noise(0.95, 1.05))  # ~6.3B each month = ~12.6B total
            ))

    # Anomaly 3: Delta Construction Underperformance
    def inject_anomaly_3_delta_underperformance(self):
        """Delta (CTR-005): every milestone delayed 7-35 days, costs 10-25% over budget."""
        for i, cm in enumerate(self.contract_milestones):
            ctr = cm[0].strip("'")
            if ctr != 'CTR-005':
                continue

            planned_str = cm[3].strip("'")
            planned = datetime.strptime(planned_str, '%Y-%m-%d').date()

            if planned <= CURRENT_DATE:
                # Delta: target OTD ~65% → 35% delayed
                r = random.random()
                if r < 0.60:
                    # On-time: finish 0-3 days early
                    actual = planned - timedelta(days=random.randint(0, 3))
                    status_val = 'completed'
                else:
                    # Delayed: 7-35 days late
                    delay = random.randint(7, 35)
                    actual = planned + timedelta(days=delay)
                    status_val = 'delayed' if delay > 14 else 'completed'
                self.contract_milestones[i] = (
                    cm[0], cm[1], cm[2], cm[3],
                    sql_str(format_date(actual)),
                    sql_str(status_val)
                )

        # Inflate Delta's costs
        for i, cc in enumerate(self.construction_costs):
            ctr = cc[1].strip("'")
            if ctr != 'CTR-005':
                continue
            budgeted = cc[5]
            actual = int(budgeted * random.uniform(1.10, 1.25))
            self.construction_costs[i] = (cc[0], cc[1], cc[2], cc[3], cc[4], budgeted, actual)

    # Anomaly 4: Cash Flow Gap Q3 2025
    def inject_anomaly_4_cashflow_gap(self):
        """Hồng Hạc infrastructure payments front-loaded in months 12-15 (Q3-Q4 2025)."""
        heavy_payments = {12: 380, 13: 350, 14: 400, 15: 370}  # billion VND

        for i, cps in enumerate(self.construction_payment_schedule):
            pid = cps[0].strip("'")
            if pid != 'PRJ-005':
                continue
            md = datetime.strptime(cps[1].strip("'"), '%Y-%m-%d').date()
            mi = month_index(md)

            if mi in heavy_payments:
                heavy = bn_to_vnd(heavy_payments[mi])
                cat = cps[4]
                actual = int(heavy * noise(0.95, 1.05)) if md <= date(2025, 6, 1) else None
                self.construction_payment_schedule[i] = (
                    cps[0], cps[1], heavy, sql_val(actual), cat
                )

        # Also reduce collection rates for months 0-3 (Jan-Apr 2024) — Tết effect
        for i, pc in enumerate(self.payment_collections):
            pd_str = pc[2].strip("'")
            pd = datetime.strptime(pd_str, '%Y-%m-%d').date()
            mi = month_index(pd)
            if 0 <= mi <= 3:
                # Reduce amount by factor to simulate 0.78 collection rate
                original = pc[3]
                reduced = int(original * 0.78 / 0.93)  # adjust from normal ~0.93 to 0.78
                self.payment_collections[i] = (pc[0], pc[1], pc[2], reduced, pc[4])

    # Anomaly 5: Bond Maturity Concentration — already in debt_schedule data
    def inject_anomaly_5_bond_maturity(self):
        """Already implemented in gen_debt_schedule. Verify balloon payments exist."""
        pass  # Data already correct from generation

    # Anomaly 6: Unsold Commercial Inventory
    def inject_anomaly_6_unsold_commercial(self):
        """14 shop units in Scenic Valley 2 with extended listing periods."""
        pass  # Will be generated in gen_unsold_inventory

    def gen_unsold_inventory(self):
        """Generate 14 unsold shop units for PRJ-006."""
        listing_dates = (
            # 6 units listed 15-18 months ago (Jan-Apr 2024)
            [date(2024, 1, random.randint(5, 25)) for _ in range(3)] +
            [date(2024, 2, random.randint(5, 25)) for _ in range(1)] +
            [date(2024, 3, random.randint(5, 20)) for _ in range(1)] +
            [date(2024, 4, random.randint(5, 20)) for _ in range(1)] +
            # 5 units listed 12-14 months ago (May-Jul 2024)
            [date(2024, 5, random.randint(5, 25)) for _ in range(2)] +
            [date(2024, 6, random.randint(5, 25)) for _ in range(2)] +
            [date(2024, 7, random.randint(5, 20)) for _ in range(1)] +
            # 3 units listed 8-10 months ago (Sep-Nov 2024)
            [date(2024, 9, random.randint(5, 25)) for _ in range(1)] +
            [date(2024, 10, random.randint(5, 25)) for _ in range(1)] +
            [date(2024, 11, random.randint(5, 20)) for _ in range(1)]
        )

        for idx, ld in enumerate(listing_dates):
            uid = f"USI-{idx + 1:03d}"
            area = round(random.uniform(50, 150), 2)
            price_sqm = lognormal_price(300_000_000, sigma=0.08)
            listed_price = int(price_sqm * area)
            carrying = mn_to_vnd(random.uniform(35, 50))  # ~35-50M VND/month

            self.unsold_inventory.append((
                sql_str(uid), sql_str('PRJ-006'), sql_str('UT-007'),
                sql_str(f'SH-U{idx + 32:03d}'),  # units 32-45 (31 already sold)
                area, listed_price, sql_str(format_date(ld)),
                carrying, sql_str('available')
            ))

    # Anomaly 7: Cảnh Đồi Rising Maintenance
    def inject_anomaly_7_canh_doi_maintenance(self):
        """ZON-002 elevator_maintenance grows 3.5%/mo, waterproofing 2.8%/mo compound."""
        for i, mc in enumerate(self.management_costs):
            zid = mc[0].strip("'")
            if zid != 'ZON-002':
                continue

            cat = mc[2].strip("'")
            md = datetime.strptime(mc[1].strip("'"), '%Y-%m-%d').date()
            mi = month_index(md)
            units = ZONE_UNITS['ZON-002']

            if cat == 'elevator_maintenance':
                # Start at 180M/month total, grow 3.5% per month compound
                base_total = 180_000_000
                cost = int(base_total * (1.035 ** mi) * noise(0.95, 1.05))
                self.management_costs[i] = (mc[0], mc[1], mc[2], cost)
            elif cat == 'waterproofing_repairs':
                # Start at 120M/month total, grow 2.8% per month compound
                base_total = 120_000_000
                cost = int(base_total * (1.028 ** mi) * noise(0.95, 1.05))
                self.management_costs[i] = (mc[0], mc[1], mc[2], cost)

        # Also inject escalating maintenance tickets for ZON-002
        # Remove existing ZON-002 elevator/waterproofing tickets and regenerate
        self.maintenance_tickets = [t for t in self.maintenance_tickets
                                     if not (t[1].strip("'") == 'ZON-002'
                                             and t[3].strip("'") in ('elevator', 'waterproofing'))]

        for mi, md in enumerate(MONTHS):
            # Elevator tickets: 8/mo (months 0-5) → 12 (6-11) → 18 (12-17)
            if mi < 6:
                n_elev = random.randint(6, 10)
                elev_cost_base = 22_000_000
            elif mi < 12:
                n_elev = random.randint(10, 14)
                elev_cost_base = 28_000_000
            else:
                n_elev = random.randint(16, 20)
                elev_cost_base = 35_000_000

            for _ in range(n_elev):
                self.ticket_counter += 1
                tid = f"TKT-{self.ticket_counter:05d}"
                tdate = random_date_in_month(md)
                cost = int(elev_cost_base * noise(0.6, 1.5))
                priority = random.choices(['medium', 'high', 'critical'], weights=[0.4, 0.4, 0.2])[0]

                if random.random() < 0.80:
                    res_date = tdate + timedelta(days=random.randint(1, 10))
                    status = 'resolved'
                else:
                    res_date = None
                    status = 'open'

                self.maintenance_tickets.append((
                    sql_str(tid), sql_str('ZON-002'),
                    sql_str(format_date(tdate)), sql_str('elevator'),
                    sql_str('Sự cố thang máy — Cảnh Đồi'),
                    sql_str(priority), sql_str(status),
                    sql_str(format_date(res_date)) if res_date else 'NULL',
                    cost
                ))

            # Waterproofing tickets: similar trend, lower volume
            if mi < 6:
                n_wp = random.randint(3, 6)
                wp_cost_base = 15_000_000
            elif mi < 12:
                n_wp = random.randint(5, 9)
                wp_cost_base = 20_000_000
            else:
                n_wp = random.randint(8, 13)
                wp_cost_base = 28_000_000

            for _ in range(n_wp):
                self.ticket_counter += 1
                tid = f"TKT-{self.ticket_counter:05d}"
                tdate = random_date_in_month(md)
                cost = int(wp_cost_base * noise(0.5, 1.8))
                priority = random.choices(['low', 'medium', 'high'], weights=[0.3, 0.5, 0.2])[0]

                if random.random() < 0.75:
                    res_date = tdate + timedelta(days=random.randint(2, 21))
                    status = 'resolved'
                else:
                    res_date = None
                    status = 'in_progress'

                self.maintenance_tickets.append((
                    sql_str(tid), sql_str('ZON-002'),
                    sql_str(format_date(tdate)), sql_str('waterproofing'),
                    sql_str('Sự cố chống thấm — Cảnh Đồi'),
                    sql_str(priority), sql_str(status),
                    sql_str(format_date(res_date)) if res_date else 'NULL',
                    cost
                ))

    # -------------------------------------------------------------------------
    # Change Orders (after anomaly 2)
    # -------------------------------------------------------------------------
    def gen_change_orders(self):
        """3 change orders for The Horizon totaling ~7.65B VND."""
        orders = [
            ('CO-001', 'PRJ-004', '2024-05-15', 'Thay đổi thiết kế lobby tầng trệt — nâng cấp vật liệu đá granite',
             'finishing', bn_to_vnd(2.1), 'implemented', 'Mr. Trần Quốc Việt — PMH Board'),
            ('CO-002', 'PRJ-004', '2024-07-20', 'Bổ sung hệ thống PCCC tầng hầm B2-B3 theo yêu cầu mới',
             'mep', bn_to_vnd(3.25), 'implemented', 'Mr. Nguyễn Hoàng Minh — Technical Director'),
            ('CO-003', 'PRJ-004', '2024-08-10', 'Thay đổi façade kính tầng 20-35 — chuyển sang Low-E glass',
             'facade', bn_to_vnd(2.3), 'implemented', 'Ms. Lê Thị Hồng — Design Director'),
            # Some change orders for other projects (normal operations)
            ('CO-004', 'PRJ-001', '2024-09-05', 'Bổ sung smart home system cho căn Penthouse',
             'mep', bn_to_vnd(0.85), 'approved', 'Mr. Trần Quốc Việt'),
            ('CO-005', 'PRJ-002', '2024-11-15', 'Nâng cấp marble sảnh chính L''Arcade',
             'finishing', bn_to_vnd(1.5), 'approved', 'Ms. Lê Thị Hồng'),
            ('CO-006', 'PRJ-005', '2025-02-20', 'Điều chỉnh cao độ san nền khu A theo khảo sát mới',
             'infrastructure', bn_to_vnd(3.8), 'implemented', 'Mr. Nguyễn Hoàng Minh'),
        ]
        for co in orders:
            self.change_orders.append((
                sql_str(co[0]), sql_str(co[1]), sql_str(co[2]),
                sql_str(co[3]), sql_str(co[4]), co[5],
                sql_str(co[6]), sql_str(co[7])
            ))

    # =========================================================================
    # SQL EXPORT
    # =========================================================================
    def export_transaction_sql(self, filepath):
        """Export all transaction data to SQL file."""
        print(f"Exporting to {filepath}...")

        sections = []

        # Header
        sections.append("""-- =============================================================================
-- Phú Mỹ Hưng Development — Transaction Data
-- 22 fact tables, ~{total} records
-- Data range: 01/2024 – 06/2025 (18 months)
-- =============================================================================

USE phu_my_hung_demo;
""")

        # Material Prices
        sections.append("-- Material Prices")
        rows = [(sql_str(r[0]), sql_str(r[1]), r[2], r[3]) for r in self.material_prices]
        sections.append(batch_inserts('material_prices',
            ['material_type', 'month_date', 'price_index', 'unit_price_vnd'], rows))

        # Project Budgets
        sections.append("\n-- Project Budgets")
        rows = [(r[0], r[1], r[2]) for r in self.project_budgets]
        sections.append(batch_inserts('project_budgets',
            ['project_id', 'category', 'budgeted_cost_vnd'], rows))

        # Project Assignments
        sections.append("\n-- Project Assignments")
        rows = [(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8])
                for r in self.project_assignments]
        sections.append(batch_inserts('project_assignments',
            ['contractor_id', 'project_id', 'phase_id', 'role', 'scope_description',
             'contract_value_vnd', 'start_date', 'end_date', 'status'], rows))

        # Unit Sales
        sections.append("\n-- Unit Sales")
        sections.append(batch_inserts('unit_sales',
            ['sale_id', 'project_id', 'unit_type_id', 'unit_code', 'floor_level',
             'area_sqm', 'price_per_sqm', 'total_price_vnd', 'sale_date',
             'buyer_type', 'status'], self.unit_sales))

        # Payment Schedules
        sections.append("\n-- Payment Schedules")
        rows = [(r[0], r[1], r[2], r[3], r[4], r[5]) for r in self.payment_schedules]
        sections.append(batch_inserts('payment_schedules',
            ['sale_id', 'installment_no', 'due_date', 'amount_vnd', 'description'],
            [(r[1], r[2], r[3], r[4], r[5]) for r in self.payment_schedules]))

        # Payment Collections
        sections.append("\n-- Payment Collections")
        rows = [(r[0], r[1], r[2], r[3], r[4]) for r in self.payment_collections]
        sections.append(batch_inserts('payment_collections',
            ['sale_id', 'schedule_id', 'payment_date', 'amount_vnd', 'payment_method'], rows))

        # Project Financials
        sections.append("\n-- Project Financials")
        sections.append(batch_inserts('project_financials',
            ['project_id', 'month_date', 'revenue_vnd', 'cost_vnd', 'sga_vnd'],
            self.project_financials))

        # Revenue Recognition
        sections.append("\n-- Revenue Recognition")
        sections.append(batch_inserts('revenue_recognition',
            ['project_id', 'month_date', 'total_contract_value_vnd', 'recognized_revenue_vnd',
             'recognized_pct', 'sell_through_pct', 'construction_completion_pct'],
            self.revenue_recognition))

        # Construction Costs
        sections.append("\n-- Construction Costs")
        sections.append(batch_inserts('construction_costs',
            ['project_id', 'contractor_id', 'category', 'description', 'month_date',
             'budgeted_cost_vnd', 'actual_cost_vnd'],
            self.construction_costs))

        # Contractor Invoices
        sections.append("\n-- Contractor Invoices")
        sections.append(batch_inserts('contractor_invoices',
            ['invoice_id', 'contractor_id', 'project_id', 'invoice_date',
             'amount_vnd', 'category', 'description', 'status'],
            self.contractor_invoices))

        # Contract Milestones
        sections.append("\n-- Contract Milestones")
        sections.append(batch_inserts('contract_milestones',
            ['contractor_id', 'project_id', 'milestone_name', 'planned_date',
             'actual_date', 'status'],
            self.contract_milestones))

        # Change Orders
        sections.append("\n-- Change Orders")
        sections.append(batch_inserts('change_orders',
            ['change_order_id', 'project_id', 'order_date', 'description',
             'category', 'cost_impact_vnd', 'status', 'approved_by'],
            self.change_orders))

        # Debt Schedule
        sections.append("\n-- Debt Schedule")
        sections.append(batch_inserts('debt_schedule',
            ['instrument_id', 'instrument_name', 'instrument_type', 'currency',
             'principal_amount', 'principal_amount_vnd', 'interest_rate_pct',
             'issue_date', 'maturity_date', 'status'],
            self.debt_schedule))

        # Debt Payments
        sections.append("\n-- Debt Payments")
        sections.append(batch_inserts('debt_payments',
            ['instrument_id', 'payment_date', 'payment_type',
             'interest_amount_vnd', 'principal_amount_vnd'],
            self.debt_payments))

        # Unsold Inventory
        sections.append("\n-- Unsold Inventory")
        sections.append(batch_inserts('unsold_inventory',
            ['unit_id', 'project_id', 'unit_type_id', 'unit_code', 'area_sqm',
             'listed_price_vnd', 'listing_date', 'monthly_carrying_cost_vnd', 'status'],
            self.unsold_inventory))

        # Project Permits
        sections.append("\n-- Project Permits")
        sections.append(batch_inserts('project_permits',
            ['project_id', 'permit_type', 'status', 'application_date',
             'expected_date', 'actual_date', 'notes'],
            self.project_permits))

        # Construction Payment Schedule
        sections.append("\n-- Construction Payment Schedule")
        sections.append(batch_inserts('construction_payment_schedule',
            ['project_id', 'month_date', 'planned_amount_vnd', 'actual_amount_vnd', 'category'],
            self.construction_payment_schedule))

        # Management Costs
        sections.append("\n-- Management Costs")
        sections.append(batch_inserts('management_costs',
            ['zone_id', 'month_date', 'cost_category', 'cost_vnd'],
            self.management_costs))

        # Management Revenue
        sections.append("\n-- Management Revenue")
        sections.append(batch_inserts('management_revenue',
            ['zone_id', 'month_date', 'revenue_vnd', 'units_billed', 'collection_rate'],
            self.management_revenue))

        # Maintenance Tickets
        sections.append("\n-- Maintenance Tickets")
        sections.append(batch_inserts('maintenance_tickets',
            ['ticket_id', 'zone_id', 'ticket_date', 'category', 'description',
             'priority', 'status', 'resolution_date', 'cost_vnd'],
            self.maintenance_tickets))

        # Lease Income
        sections.append("\n-- Lease Income")
        sections.append(batch_inserts('lease_income',
            ['tenant_id', 'month_date', 'monthly_rent_vnd', 'collected_vnd', 'occupancy_status'],
            self.lease_income))

        # Management Fees Monthly
        sections.append("\n-- Management Fees Monthly")
        sections.append(batch_inserts('management_fees_monthly',
            ['month_date', 'total_fee_revenue_vnd', 'total_fee_cost_vnd'],
            self.management_fees_monthly))

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(sections))

        print(f"Exported to {filepath}")

    # =========================================================================
    # MySQL POPULATION
    # =========================================================================
    def populate_mysql(self):
        """Execute DDL + master data + transaction data directly into MySQL."""
        print("Connecting to MySQL...")
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Create database
        cursor.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")
        cursor.execute(f"CREATE DATABASE {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.execute(f"USE {DB_NAME}")
        conn.commit()

        # Execute DDL
        print("Creating schema...")
        ddl_path = os.path.join(SQL_DIR, '01_ddl_schema.sql')
        self._exec_sql_file(cursor, conn, ddl_path, skip_create_db=True)

        # Execute metadata
        print("Loading metadata...")
        meta_path = os.path.join(SQL_DIR, '02_metadata.sql')
        self._exec_sql_file(cursor, conn, meta_path)

        # Execute master data
        print("Loading master data...")
        master_path = os.path.join(SQL_DIR, '03_master_data.sql')
        self._exec_sql_file(cursor, conn, master_path)

        # Insert transaction data
        print("Inserting transaction data...")
        self._insert_transaction_data(cursor, conn)

        cursor.close()
        conn.close()
        print("MySQL population complete.")

    def _exec_sql_file(self, cursor, conn, filepath, skip_create_db=False):
        with open(filepath, 'r', encoding='utf-8') as f:
            sql = f.read()

        # Remove comments and split carefully on semicolons outside of strings
        # Simple approach: strip comment lines, then split on ;\n patterns
        lines = []
        for line in sql.split('\n'):
            stripped = line.strip()
            if stripped.startswith('--') or not stripped:
                continue
            if skip_create_db and ('CREATE DATABASE' in stripped.upper()):
                continue
            if 'USE ' in stripped.upper() and stripped.upper().startswith('USE'):
                continue
            lines.append(line)

        full_sql = '\n'.join(lines)
        # Split on semicolons that end a statement (semicolon + newline or end of string)
        import re
        statements = re.split(r';\s*\n', full_sql)

        for stmt in statements:
            stmt = stmt.strip().rstrip(';').strip()
            if not stmt:
                continue
            try:
                cursor.execute(stmt)
            except Exception as e:
                print(f"  Warning: {e}")
                print(f"  Statement: {stmt[:120]}...")
        conn.commit()

    def _insert_transaction_data(self, cursor, conn):
        def do_insert(table, columns, rows, transform=None):
            if not rows:
                return
            cols = ', '.join(columns)
            for i in range(0, len(rows), BATCH_SIZE):
                batch = rows[i:i + BATCH_SIZE]
                vals_list = []
                for row in batch:
                    if transform:
                        row = transform(row)
                    vals = []
                    for v in row:
                        if v == 'NULL' or v is None:
                            vals.append('NULL')
                        elif isinstance(v, str) and v.startswith("'"):
                            vals.append(v)
                        else:
                            vals.append(str(v))
                    vals_list.append(f"({', '.join(vals)})")
                sql = f"INSERT INTO {table} ({cols}) VALUES\n" + ',\n'.join(vals_list)
                try:
                    cursor.execute(sql)
                except Exception as e:
                    print(f"  Error inserting into {table}: {e}")
                    print(f"  First row: {vals_list[0][:200]}")
            conn.commit()
            print(f"  {table}: {len(rows)} rows")

        do_insert('material_prices', ['material_type', 'month_date', 'price_index', 'unit_price_vnd'],
                  [(sql_str(r[0]), sql_str(r[1]), r[2], r[3]) for r in self.material_prices])

        do_insert('project_budgets', ['project_id', 'category', 'budgeted_cost_vnd'],
                  self.project_budgets)

        do_insert('project_assignments',
                  ['contractor_id', 'project_id', 'phase_id', 'role', 'scope_description',
                   'contract_value_vnd', 'start_date', 'end_date', 'status'],
                  self.project_assignments)

        do_insert('unit_sales',
                  ['sale_id', 'project_id', 'unit_type_id', 'unit_code', 'floor_level',
                   'area_sqm', 'price_per_sqm', 'total_price_vnd', 'sale_date',
                   'buyer_type', 'status'],
                  self.unit_sales)

        do_insert('payment_schedules',
                  ['sale_id', 'installment_no', 'due_date', 'amount_vnd', 'description'],
                  [(r[1], r[2], r[3], r[4], r[5]) for r in self.payment_schedules])

        do_insert('payment_collections',
                  ['sale_id', 'schedule_id', 'payment_date', 'amount_vnd', 'payment_method'],
                  self.payment_collections)

        do_insert('project_financials',
                  ['project_id', 'month_date', 'revenue_vnd', 'cost_vnd', 'sga_vnd'],
                  self.project_financials)

        do_insert('revenue_recognition',
                  ['project_id', 'month_date', 'total_contract_value_vnd', 'recognized_revenue_vnd',
                   'recognized_pct', 'sell_through_pct', 'construction_completion_pct'],
                  self.revenue_recognition)

        do_insert('construction_costs',
                  ['project_id', 'contractor_id', 'category', 'description', 'month_date',
                   'budgeted_cost_vnd', 'actual_cost_vnd'],
                  self.construction_costs)

        do_insert('contractor_invoices',
                  ['invoice_id', 'contractor_id', 'project_id', 'invoice_date',
                   'amount_vnd', 'category', 'description', 'status'],
                  self.contractor_invoices)

        do_insert('contract_milestones',
                  ['contractor_id', 'project_id', 'milestone_name', 'planned_date',
                   'actual_date', 'status'],
                  self.contract_milestones)

        do_insert('change_orders',
                  ['change_order_id', 'project_id', 'order_date', 'description',
                   'category', 'cost_impact_vnd', 'status', 'approved_by'],
                  self.change_orders)

        do_insert('debt_schedule',
                  ['instrument_id', 'instrument_name', 'instrument_type', 'currency',
                   'principal_amount', 'principal_amount_vnd', 'interest_rate_pct',
                   'issue_date', 'maturity_date', 'status'],
                  self.debt_schedule)

        do_insert('debt_payments',
                  ['instrument_id', 'payment_date', 'payment_type',
                   'interest_amount_vnd', 'principal_amount_vnd'],
                  self.debt_payments)

        do_insert('unsold_inventory',
                  ['unit_id', 'project_id', 'unit_type_id', 'unit_code', 'area_sqm',
                   'listed_price_vnd', 'listing_date', 'monthly_carrying_cost_vnd', 'status'],
                  self.unsold_inventory)

        do_insert('project_permits',
                  ['project_id', 'permit_type', 'status', 'application_date',
                   'expected_date', 'actual_date', 'notes'],
                  self.project_permits)

        do_insert('construction_payment_schedule',
                  ['project_id', 'month_date', 'planned_amount_vnd', 'actual_amount_vnd', 'category'],
                  self.construction_payment_schedule)

        do_insert('management_costs',
                  ['zone_id', 'month_date', 'cost_category', 'cost_vnd'],
                  self.management_costs)

        do_insert('management_revenue',
                  ['zone_id', 'month_date', 'revenue_vnd', 'units_billed', 'collection_rate'],
                  self.management_revenue)

        do_insert('maintenance_tickets',
                  ['ticket_id', 'zone_id', 'ticket_date', 'category', 'description',
                   'priority', 'status', 'resolution_date', 'cost_vnd'],
                  self.maintenance_tickets)

        do_insert('lease_income',
                  ['tenant_id', 'month_date', 'monthly_rent_vnd', 'collected_vnd', 'occupancy_status'],
                  self.lease_income)

        do_insert('management_fees_monthly',
                  ['month_date', 'total_fee_revenue_vnd', 'total_fee_cost_vnd'],
                  self.management_fees_monthly)


# =============================================================================
# MAIN
# =============================================================================
def main():
    gen = DataGenerator()
    gen.generate_all()
    gen.compute_management_fees_monthly()

    # 1. Populate MySQL
    try:
        gen.populate_mysql()
    except Exception as e:
        print(f"MySQL population failed: {e}")
        print("Continuing with SQL export...")

    # 2. Export SQL
    os.makedirs(SQL_DIR, exist_ok=True)
    tx_path = os.path.join(SQL_DIR, '04_transaction_data.sql')
    gen.export_transaction_sql(tx_path)

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    tables = {
        'material_prices': len(gen.material_prices),
        'project_budgets': len(gen.project_budgets),
        'project_assignments': len(gen.project_assignments),
        'unit_sales': len(gen.unit_sales),
        'payment_schedules': len(gen.payment_schedules),
        'payment_collections': len(gen.payment_collections),
        'project_financials': len(gen.project_financials),
        'revenue_recognition': len(gen.revenue_recognition),
        'construction_costs': len(gen.construction_costs),
        'contractor_invoices': len(gen.contractor_invoices),
        'contract_milestones': len(gen.contract_milestones),
        'change_orders': len(gen.change_orders),
        'debt_schedule': len(gen.debt_schedule),
        'debt_payments': len(gen.debt_payments),
        'unsold_inventory': len(gen.unsold_inventory),
        'project_permits': len(gen.project_permits),
        'construction_payment_schedule': len(gen.construction_payment_schedule),
        'management_costs': len(gen.management_costs),
        'management_revenue': len(gen.management_revenue),
        'maintenance_tickets': len(gen.maintenance_tickets),
        'lease_income': len(gen.lease_income),
        'management_fees_monthly': len(gen.management_fees_monthly),
    }
    total = 0
    for t, c in sorted(tables.items()):
        print(f"  {t:40s} {c:>8,d} rows")
        total += c
    print(f"  {'TOTAL':40s} {total:>8,d} rows")
    print(f"\nSQL exported to: {SQL_DIR}/04_transaction_data.sql")


if __name__ == '__main__':
    main()
