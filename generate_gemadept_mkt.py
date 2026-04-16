#!/usr/bin/env python3
"""
Gemadept BI Demo Database Generator — MKT Manager persona
Generates 24 months of data (2024-04 to 2026-03) for gemadept_bi_demo database.
Focus: multi-source cross-reference (internal + cảng vụ + news) for BD/MKT insights.

Output: SQL files in gemadept_mkt_sql/  + populates MySQL directly.
"""

import random
import math
import os
import json
from datetime import date, datetime, timedelta
from collections import defaultdict

random.seed(42)

# =============================================================================
# CONFIG
# =============================================================================
DB_NAME = 'gemadept_bi_demo'
SQL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gemadept_mkt_sql')
BATCH = 500

START_DATE = date(2024, 4, 1)
END_DATE   = date(2026, 3, 31)

MONTHS = []
d = START_DATE
while d <= END_DATE:
    MONTHS.append(d)
    y, m = d.year, d.month
    m += 1
    if m > 12:
        m = 1; y += 1
    d = date(y, m, 1)

YOY_2024_2025 = 0.12
YOY_2025_2026 = 0.15

# Seasonality (VN cảng biển) — 1=Jan ... 12=Dec
MONTHLY_SEASON = {
    1: 0.78, 2: 0.75, 3: 0.88, 4: 0.95, 5: 1.00, 6: 1.08,
    7: 1.10, 8: 1.12, 9: 1.18, 10: 1.22, 11: 1.15, 12: 1.02,
}

WEEKLY_PATTERN = [1.05, 1.08, 1.10, 1.12, 1.10, 0.90, 0.75]  # Mon..Sun

ALLIANCE_BREAK_DATE = date(2025, 2, 1)

# =============================================================================
# HELPERS
# =============================================================================
def esc(v):
    if v is None:
        return 'NULL'
    if isinstance(v, bool):
        return '1' if v else '0'
    if isinstance(v, (int,)):
        return str(v)
    if isinstance(v, float):
        if v == int(v) and abs(v) < 1e15:
            return str(int(v))
        return f'{v:.2f}'
    if isinstance(v, date) and not isinstance(v, datetime):
        return f"'{v.isoformat()}'"
    if isinstance(v, datetime):
        return f"'{v.strftime('%Y-%m-%d %H:%M:%S')}'"
    s = str(v).replace("\\", "\\\\").replace("'", "\\'")
    return f"'{s}'"


def write_inserts(f, table, columns, rows, batch=BATCH):
    if not rows:
        return
    col_str = ', '.join(f'`{c}`' for c in columns)
    for i in range(0, len(rows), batch):
        chunk = rows[i:i + batch]
        vals = ['(' + ', '.join(esc(v) for v in row) + ')' for row in chunk]
        f.write(f"INSERT INTO `{table}` ({col_str}) VALUES\n")
        f.write(',\n'.join(vals))
        f.write(';\n\n')


def growth_factor(month_date):
    """Compound growth from START_DATE, different rate per year."""
    months_since = (month_date.year - START_DATE.year) * 12 + (month_date.month - START_DATE.month)
    # Apr 2024 = base 1.0
    # Year 1 uses 12% annual -> monthly ~0.95%
    # Year 2 uses 15% annual -> monthly ~1.17%
    if months_since < 12:
        return (1 + YOY_2024_2025) ** (months_since / 12)
    else:
        year1 = (1 + YOY_2024_2025)
        return year1 * (1 + YOY_2025_2026) ** ((months_since - 12) / 12)


def days_in_month(d):
    y, m = d.year, d.month
    m2 = m + 1; y2 = y
    if m2 > 12: m2 = 1; y2 += 1
    return (date(y2, m2, 1) - d).days


# =============================================================================
# MASTER DATA — PORTS
# =============================================================================
# (port_id, port_name, port_code, is_gemadept, region, cluster, port_type, capacity_teu_year, max_dwt, operator_company, lat, lng)
PORTS = [
    # Gemadept ports
    ('P001', 'Nam Đình Vũ',              'NDV',   1, 'Bắc',   'Hải Phòng',   'river',   2_000_000, 55_000,  'Gemadept',        20.82,  106.78),
    ('P002', 'Nam Hải ICD',              'NHICD', 1, 'Bắc',   'Hải Phòng',   'ICD',       400_000, 30_000,  'Gemadept',        20.85,  106.73),
    ('P003', 'Cảng Dung Quất',           'DQ',    1, 'Trung', 'Miền Trung',  'bulk',       150_000, 70_000,  'Gemadept',        15.40,  108.78),
    ('P004', 'Phước Long ICD',           'PLICD', 1, 'Nam',   'HCM',         'ICD',       300_000, 20_000,  'Gemadept',        10.84,  106.75),
    ('P005', 'Cảng Bình Dương',          'BDP',   1, 'Nam',   'HCM',         'river',     250_000, 30_000,  'Gemadept',        10.93,  106.71),
    ('P006', 'Gemalink',                 'GML',   1, 'Nam',   'CM-TV',       'deepsea', 1_500_000, 250_000, 'Gemadept-CMA',    10.55,  107.05),
    ('P007', 'Nam Đình Vũ GĐ3',          'NDV3',  1, 'Bắc',   'Hải Phòng',   'river',     800_000, 55_000,  'Gemadept',        20.82,  106.79),
    # CM-TV competitors
    ('P010', 'TCIT',                     'TCIT',  0, 'Nam',   'CM-TV',       'deepsea', 1_500_000, 200_000, 'Tân Cảng SG',     10.53,  107.03),
    ('P011', 'TCCT',                     'TCCT',  0, 'Nam',   'CM-TV',       'deepsea',   800_000, 160_000, 'Tân Cảng SG',     10.54,  107.04),
    ('P012', 'TCTT',                     'TCTT',  0, 'Nam',   'CM-TV',       'deepsea',   700_000, 160_000, 'Tân Cảng SG',     10.56,  107.04),
    ('P013', 'CMIT',                     'CMIT',  0, 'Nam',   'CM-TV',       'deepsea', 1_200_000, 200_000, 'CMIT JV',         10.52,  107.03),
    ('P014', 'SSIT',                     'SSIT',  0, 'Nam',   'CM-TV',       'deepsea', 1_200_000, 200_000, 'SSA Marine',      10.50,  107.02),
    ('P015', 'SP-PSA',                   'SPPSA', 0, 'Nam',   'CM-TV',       'deepsea', 1_100_000, 160_000, 'PSA-Saigon',      10.49,  107.01),
    # Hải Phòng competitors
    ('P020', 'Lạch Huyện HIT',           'HIT',   0, 'Bắc',   'Hải Phòng',   'deepsea', 1_100_000, 140_000, 'Hateco',          20.80,  106.88),
    ('P021', 'Lạch Huyện HICT',          'HICT',  0, 'Bắc',   'Hải Phòng',   'deepsea', 1_100_000, 160_000, 'Hateco-Itochu',   20.80,  106.89),
    ('P022', 'Lạch Huyện TC-HICT',       'TCHICT',0, 'Bắc',   'Hải Phòng',   'deepsea', 1_100_000, 160_000, 'Tân Cảng SG',     20.81,  106.90),
    ('P023', 'VIP Green Port',           'VIPGP', 0, 'Bắc',   'Hải Phòng',   'river',     500_000, 45_000,  'VIP Group',       20.84,  106.78),
    ('P024', 'Nam Hải Đình Vũ',          'NHDV',  0, 'Bắc',   'Hải Phòng',   'river',     400_000, 40_000,  'VIMC',            20.83,  106.76),
    ('P025', 'Tân Cảng 128',             'TC128', 0, 'Bắc',   'Hải Phòng',   'river',     350_000, 40_000,  'Tân Cảng SG',     20.85,  106.74),
    # HCM
    ('P030', 'Cát Lái',                  'CLI',   0, 'Nam',   'HCM',         'river',   4_500_000, 45_000,  'Tân Cảng SG',     10.78,  106.78),
    ('P031', 'ICD Transimex',            'ICDTR', 0, 'Nam',   'HCM',         'ICD',       300_000, 20_000,  'Transimex',       10.83,  106.77),
    ('P032', 'ICD Sotrans',              'ICDST', 0, 'Nam',   'HCM',         'ICD',       280_000, 20_000,  'Sotrans',         10.83,  106.76),
]

# =============================================================================
# MASTER DATA — SHIPPING LINES
# =============================================================================
# (line_id, line_name, line_code, country, fleet_size_vessels, fleet_capacity_teu, global_rank, vietnam_presence_since)
SHIPPING_LINES = [
    ('L01', 'MSC',          'MSCU', 'Thụy Sĩ/Italy', 830, 6_400_000, 1,  1995),
    ('L02', 'Maersk',       'MAEU', 'Đan Mạch',      700, 4_300_000, 2,  1991),
    ('L03', 'CMA CGM',      'CMDU', 'Pháp',          620, 3_800_000, 3,  1996),
    ('L04', 'COSCO',        'COSU', 'Trung Quốc',    490, 3_100_000, 4,  1998),
    ('L05', 'Hapag-Lloyd',  'HLCU', 'Đức',           300, 2_200_000, 5,  2000),
    ('L06', 'ONE',          'ONEY', 'Nhật/Singapore',220, 1_900_000, 6,  2018),
    ('L07', 'Evergreen',    'EGLV', 'Đài Loan',      215, 1_800_000, 7,  1997),
    ('L08', 'HMM',          'HDMU', 'Hàn Quốc',      80,  810_000,   8,  1999),
    ('L09', 'Yang Ming',    'YMLU', 'Đài Loan',      90,  720_000,   9,  2002),
    ('L10', 'ZIM',          'ZIMU', 'Israel',        145, 800_000,   10, 2005),
    ('L11', 'Wan Hai',      'WHLC', 'Đài Loan',      150, 540_000,   11, 1998),
    ('L12', 'SITC',         'SITC', 'Trung Quốc',    115, 200_000,   12, 2003),
    ('L13', 'KMTC',         'KMTU', 'Hàn Quốc',      68,  150_000,   13, 2001),
    ('L14', 'TS Lines',     'TSLL', 'Đài Loan',      50,  130_000,   14, 2006),
    ('L15', 'PIL',          'PABV', 'Singapore',     95,  400_000,   15, 1997),
    ('L16', 'OOCL',         'OOLU', 'Hong Kong',     110, 800_000,   16, 1996),  # part of COSCO but operates independent
    ('L17', 'RCL',          'RCLU', 'Thái Lan',      38,  65_000,    17, 2004),
    ('L18', 'SM Line',      'SMLM', 'Hàn Quốc',      48,  90_000,    18, 2017),
    ('L19', 'Interasia',    'IALS', 'Đài Loan',      30,  55_000,    19, 2010),
    ('L20', 'CNC',          'CNCA', 'Pháp',          22,  45_000,    20, 2008),
    ('L21', 'Dongjin',      'DJSM', 'Hàn Quốc',      16,  20_000,    21, 2013),
    ('L22', 'Nam Sung',     'NSRU', 'Hàn Quốc',      15,  25_000,    22, 2011),
    ('L23', 'MCC',          'MCCQ', 'Đan Mạch',      40,  100_000,   23, 2005),
    ('L24', 'APL',          'APLU', 'Singapore',     60,  590_000,   24, 1997),  # part of CMA CGM
    ('L25', 'Sinokor',      'SKLU', 'Hàn Quốc',      55,  90_000,    25, 2002),
]

# =============================================================================
# ALLIANCES — with pre/post Feb 2025 structure
# =============================================================================
# (alliance_id, alliance_name, formed_date, dissolved_date, combined_teu, market_share_pct, trade_focus, status)
ALLIANCES = [
    ('A01', '2M Alliance',              date(2015, 1, 1),  date(2025, 1, 31), 8_700_000, 34.0, 'Asia-Europe, TransPacific', 'dissolved'),
    ('A02', 'THE Alliance',             date(2017, 4, 1),  date(2025, 1, 31), 4_900_000, 19.0, 'Asia-Europe, TransPacific', 'dissolved'),
    ('A03', 'Ocean Alliance (pre-2025)', date(2017, 4, 1), date(2025, 1, 31), 7_400_000, 29.0, 'Asia-Europe, TransPacific', 'restructured'),
    ('A04', 'Gemini Cooperation',       date(2025, 2, 1),  None,              3_400_000, 20.0, 'Asia-Europe, TransPacific — hub-and-spoke', 'active'),
    ('A05', 'Premier Alliance',         date(2025, 2, 1),  None,              1_900_000, 12.0, 'Asia-Europe, TransPacific',                 'active'),
    ('A06', 'Ocean Alliance',           date(2025, 2, 1),  None,              7_900_000, 30.0, 'Asia-Europe, TransPacific (gia hạn 2032)',  'active'),
    ('A07', 'MSC Standalone',           date(2025, 2, 1),  None,              6_400_000, 20.0, 'Global independent',                         'active'),
]

# =============================================================================
# ALLIANCE MEMBERSHIP HISTORY
# =============================================================================
# Pre-Feb-2025 ↔ Post-Feb-2025
# Pre: 2M = Maersk+MSC; THE Alliance = Hapag+ONE+YM+HMM; Ocean Alliance = CMA+COSCO+EV+OOCL
# Post: Gemini = Maersk+Hapag; Premier = ONE+YM+HMM; Ocean Alliance (unchanged); MSC standalone

ALLIANCE_MEMBERSHIPS = []
_MEMBER_ID = 1
def _add_mem(line_id, alliance_id, fr, to):
    global _MEMBER_ID
    ALLIANCE_MEMBERSHIPS.append((f'M{_MEMBER_ID:03d}', line_id, alliance_id, fr, to))
    _MEMBER_ID += 1

# Pre-Feb-2025
_add_mem('L02', 'A01', date(2015,1,1), date(2025,1,31))  # Maersk in 2M
_add_mem('L01', 'A01', date(2015,1,1), date(2025,1,31))  # MSC in 2M
_add_mem('L05', 'A02', date(2017,4,1), date(2025,1,31))  # Hapag in THE Alliance
_add_mem('L06', 'A02', date(2018,4,1), date(2025,1,31))  # ONE
_add_mem('L09', 'A02', date(2017,4,1), date(2025,1,31))  # Yang Ming
_add_mem('L08', 'A02', date(2017,4,1), date(2025,1,31))  # HMM
_add_mem('L03', 'A03', date(2017,4,1), date(2025,1,31))  # CMA CGM in Ocean Alliance (pre)
_add_mem('L04', 'A03', date(2017,4,1), date(2025,1,31))  # COSCO
_add_mem('L07', 'A03', date(2017,4,1), date(2025,1,31))  # Evergreen
_add_mem('L16', 'A03', date(2017,4,1), date(2025,1,31))  # OOCL

# Post-Feb-2025
_add_mem('L02', 'A04', date(2025,2,1), None)  # Maersk in Gemini
_add_mem('L05', 'A04', date(2025,2,1), None)  # Hapag in Gemini
_add_mem('L06', 'A05', date(2025,2,1), None)  # ONE in Premier
_add_mem('L09', 'A05', date(2025,2,1), None)  # Yang Ming
_add_mem('L08', 'A05', date(2025,2,1), None)  # HMM
_add_mem('L03', 'A06', date(2025,2,1), None)  # CMA CGM in Ocean Alliance (post)
_add_mem('L04', 'A06', date(2025,2,1), None)  # COSCO
_add_mem('L07', 'A06', date(2025,2,1), None)  # Evergreen
_add_mem('L16', 'A06', date(2025,2,1), None)  # OOCL
_add_mem('L01', 'A07', date(2025,2,1), None)  # MSC standalone

# =============================================================================
# VESSELS — ~120 realistic vessels
# =============================================================================
# (vessel_id, vessel_name, imo_number, flag, owner_line_id, dwt, teu_capacity, length_meters, year_built, vessel_type)

VESSEL_NAMES = {
    'L01': [  # MSC
        ('MSC OSCAR', 9703291, 192_672, 19_224, 395, 2015),
        ('MSC GULSUN', 9839272, 225_720, 23_756, 400, 2019),
        ('MSC ISABELLA', 9854494, 225_000, 23_656, 400, 2020),
        ('MSC MIA', 9839260, 225_000, 23_756, 400, 2019),
        ('MSC SAMAR', 9857769, 225_000, 23_656, 400, 2020),
        ('MSC DANIELA', 9398290, 165_500, 14_000, 366, 2009),
        ('MSC NICOLA MASTRO', 9839284, 218_960, 23_362, 400, 2019),
        ('MSC DITTE', 9839298, 218_960, 23_362, 400, 2019),
        ('MSC SIXIN', 9857745, 225_000, 23_656, 400, 2020),
        ('MSC LEANNE', 9857757, 225_000, 23_656, 400, 2020),
        ('MSC REEF', 9615157, 140_000, 13_092, 366, 2013),
        ('MSC CLARA', 9461104, 110_000, 10_081, 300, 2011),
    ],
    'L02': [  # Maersk
        ('MADRID MAERSK', 9778791, 194_153, 20_568, 400, 2017),
        ('MUNICH MAERSK', 9778806, 194_153, 20_568, 400, 2017),
        ('MOSCOW MAERSK', 9778818, 194_153, 20_568, 400, 2017),
        ('MANCHESTER MAERSK', 9778820, 194_153, 20_568, 400, 2017),
        ('MAASTRICHT MAERSK', 9778832, 194_153, 20_568, 400, 2017),
        ('MATZ MAERSK', 9778844, 194_153, 20_568, 400, 2017),
        ('MARSEILLE MAERSK', 9778856, 194_153, 20_568, 400, 2017),
        ('MARIBO MAERSK', 9778868, 194_153, 20_568, 400, 2017),
        ('EDITH MAERSK', 9321500, 157_000, 15_500, 397, 2007),
        ('ELEONORA MAERSK', 9321512, 157_000, 15_500, 397, 2007),
        ('MAERSK HORSBURGH', 9784740, 85_000, 8_500, 300, 2017),
    ],
    'L03': [  # CMA CGM
        ('CMA CGM JACQUES SAADE', 9839002, 236_583, 23_112, 400, 2020),
        ('CMA CGM CHAMPS ELYSEES', 9839014, 236_583, 23_112, 400, 2020),
        ('CMA CGM PALAIS ROYAL', 9839026, 236_583, 23_112, 400, 2020),
        ('CMA CGM MONTMARTRE', 9839038, 236_583, 23_112, 400, 2021),
        ('CMA CGM LOUVRE', 9839040, 236_583, 23_112, 400, 2020),
        ('CMA CGM MARCO POLO', 9454436, 187_000, 16_020, 396, 2012),
        ('CMA CGM BENJAMIN FRANKLIN', 9780456, 180_000, 18_000, 398, 2015),
        ('CMA CGM GEORG FORSTER', 9454412, 176_000, 16_020, 396, 2013),
        ('CMA CGM TAGE', 9465096, 150_000, 14_000, 366, 2012),
        ('CMA CGM COTE D IVOIRE', 9839052, 150_000, 14_812, 366, 2020),
        ('CMA CGM RIGEL', 9780466, 110_000, 10_500, 337, 2016),
    ],
    'L04': [  # COSCO
        ('COSCO SHIPPING UNIVERSE', 9795580, 197_500, 21_237, 400, 2018),
        ('COSCO SHIPPING GALAXY', 9795592, 197_500, 21_237, 400, 2018),
        ('COSCO SHIPPING SOLAR', 9795607, 197_500, 21_237, 400, 2018),
        ('COSCO SHIPPING NEBULA', 9795619, 197_500, 21_237, 400, 2019),
        ('COSCO SHIPPING STAR', 9795621, 197_500, 21_237, 400, 2018),
        ('COSCO SHIPPING ARIES', 9783033, 183_000, 20_119, 400, 2018),
        ('COSCO SHIPPING VIRGO', 9783045, 183_000, 20_119, 400, 2018),
        ('COSCO SHIPPING DENALI', 9448411, 141_000, 13_386, 366, 2011),
        ('COSCO BEIJING', 9448423, 140_000, 13_092, 366, 2011),
    ],
    'L05': [  # Hapag-Lloyd
        ('HAMBURG EXPRESS', 9501499, 151_600, 13_169, 366, 2012),
        ('HONG KONG EXPRESS', 9501475, 151_600, 13_169, 366, 2012),
        ('SHANGHAI EXPRESS', 9501487, 151_600, 13_169, 366, 2012),
        ('BERLIN EXPRESS', 9811892, 240_000, 23_660, 400, 2023),
        ('TOKYO EXPRESS', 9812006, 240_000, 23_660, 400, 2024),
        ('SOFIA EXPRESS', 9811907, 240_000, 23_660, 400, 2024),
        ('OSAKA EXPRESS', 9501504, 151_600, 13_169, 366, 2012),
        ('LEVERKUSEN EXPRESS', 9501516, 151_600, 13_169, 366, 2013),
    ],
    'L06': [  # ONE
        ('ONE INNOVATION', 9806756, 192_672, 20_150, 400, 2019),
        ('ONE INSPIRATION', 9806768, 192_672, 20_150, 400, 2019),
        ('ONE INTEGRITY', 9806770, 192_672, 20_150, 400, 2019),
        ('ONE INTELLIGENCE', 9806782, 192_672, 20_150, 400, 2019),
        ('ONE STORK', 9741858, 150_000, 14_000, 366, 2018),
        ('ONE SWAN', 9741860, 150_000, 14_000, 366, 2018),
        ('ONE HAWK', 9312377, 98_000, 8_500, 323, 2006),
    ],
    'L07': [  # Evergreen
        ('EVER ACE', 9893890, 235_579, 23_992, 400, 2021),
        ('EVER APEX', 9893905, 235_579, 23_992, 400, 2022),
        ('EVER ACME', 9893917, 235_579, 23_992, 400, 2022),
        ('EVER GIVEN', 9811000, 199_629, 20_124, 400, 2018),
        ('EVER GOLDEN', 9811012, 199_629, 20_124, 400, 2018),
        ('EVER GENIUS', 9811024, 199_629, 20_124, 400, 2019),
        ('EVER LAUREL', 9605607, 150_000, 13_808, 368, 2013),
        ('EVER LEADING', 9605619, 150_000, 13_808, 368, 2013),
    ],
    'L08': [  # HMM
        ('HMM ALGECIRAS', 9863297, 232_311, 23_964, 400, 2020),
        ('HMM OSLO', 9863302, 232_311, 23_964, 400, 2020),
        ('HMM COPENHAGEN', 9863314, 232_311, 23_964, 400, 2020),
        ('HMM HAMBURG', 9863326, 232_311, 23_964, 400, 2020),
        ('HMM HONG KONG', 9863338, 150_000, 11_000, 300, 2020),
    ],
    'L09': [  # Yang Ming
        ('YM WITNESS', 9708928, 150_000, 14_220, 368, 2015),
        ('YM WARMTH', 9708930, 150_000, 14_220, 368, 2015),
        ('YM WARRANTY', 9708942, 150_000, 14_220, 368, 2015),
        ('YM WONDROUS', 9708954, 150_000, 14_220, 368, 2016),
        ('YM MANDATE', 9318915, 90_000, 8_204, 335, 2007),
    ],
    'L10': [  # ZIM
        ('ZIM USA', 9924821, 140_000, 15_000, 366, 2023),
        ('ZIM MONACO', 9924833, 140_000, 15_000, 366, 2023),
        ('ZIM SAMMY OFER', 9924845, 140_000, 15_000, 366, 2023),
        ('ZIM AMBER', 9346457, 50_000, 4_250, 260, 2007),
        ('ZIM CROWN', 9346469, 50_000, 4_250, 260, 2008),
    ],
    'L11': [  # Wan Hai
        ('WAN HAI 805', 9849138, 130_000, 13_100, 335, 2023),
        ('WAN HAI 806', 9849140, 130_000, 13_100, 335, 2023),
        ('WAN HAI 511', 9345257, 40_000, 4_250, 262, 2007),
        ('WAN HAI 512', 9345269, 40_000, 4_250, 262, 2007),
        ('WAN HAI 313', 9345271, 30_000, 2_646, 215, 2006),
    ],
    'L12': [  # SITC
        ('SITC YOKKAICHI', 9823273, 24_000, 1_800, 172, 2018),
        ('SITC HAKATA', 9823285, 24_000, 1_800, 172, 2018),
        ('SITC INCHON', 9823297, 24_000, 1_800, 172, 2018),
        ('SITC SHANGHAI', 9823302, 24_000, 1_800, 172, 2019),
    ],
    'L13': [  # KMTC
        ('KMTC SHANGHAI', 9631498, 22_000, 1_800, 170, 2013),
        ('KMTC JAKARTA', 9631503, 22_000, 1_800, 170, 2013),
        ('KMTC DELHI', 9631515, 25_000, 2_300, 200, 2014),
    ],
    'L14': [  # TS Lines
        ('TS TAIPEI', 9443241, 32_000, 2_800, 213, 2011),
        ('TS KAOHSIUNG', 9443253, 32_000, 2_800, 213, 2011),
        ('TS KEELUNG', 9443265, 25_000, 2_300, 200, 2010),
    ],
    'L15': [  # PIL
        ('KOTA PAHLAWAN', 9786891, 60_000, 11_900, 334, 2017),
        ('KOTA PEKARANG', 9786906, 60_000, 11_900, 334, 2018),
        ('KOTA LAGU', 9610262, 40_000, 4_300, 260, 2012),
        ('KOTA LAMBAI', 9610274, 40_000, 4_300, 260, 2012),
    ],
    'L16': [  # OOCL
        ('OOCL HONG KONG', 9776171, 210_890, 21_413, 400, 2017),
        ('OOCL GERMANY', 9776183, 210_890, 21_413, 400, 2017),
        ('OOCL INDONESIA', 9776195, 210_890, 21_413, 400, 2018),
        ('OOCL JAPAN', 9776200, 210_890, 21_413, 400, 2018),
        ('OOCL SCANDINAVIA', 9776212, 210_890, 21_413, 400, 2018),
    ],
    'L17': [  # RCL
        ('RCL HO CHI MINH', 9450181, 25_000, 2_500, 200, 2010),
        ('RCL BANGKOK', 9450193, 25_000, 2_500, 200, 2011),
    ],
    'L18': [  # SM Line
        ('SM LONG BEACH', 9315602, 65_000, 5_100, 280, 2006),
        ('SM SHANGHAI', 9315614, 65_000, 5_100, 280, 2007),
    ],
    'L19': [  # Interasia
        ('INTERASIA INSPIRATION', 9435890, 18_000, 1_700, 170, 2010),
        ('INTERASIA INTREPID', 9435905, 18_000, 1_700, 170, 2010),
    ],
    'L20': [  # CNC
        ('CNC MERCURY', 9460069, 18_000, 1_700, 170, 2011),
        ('CNC NEPTUNE', 9460071, 18_000, 1_700, 170, 2011),
    ],
    'L21': [  # Dongjin
        ('DONGJIN VOYAGER', 9283435, 12_000, 1_000, 140, 2005),
        ('DONGJIN VENUS', 9283447, 12_000, 1_000, 140, 2005),
    ],
    'L22': [  # Nam Sung
        ('NAMSUNG ADMIRAL', 9293074, 15_000, 1_100, 147, 2005),
        ('NAMSUNG BRAVE', 9293086, 15_000, 1_100, 147, 2005),
    ],
    'L23': [  # MCC
        ('MCC YOKOHAMA', 9784685, 28_000, 2_500, 200, 2017),
        ('MCC TOKYO', 9784697, 28_000, 2_500, 200, 2017),
    ],
    'L24': [  # APL
        ('APL SOUTHAMPTON', 9632129, 150_000, 14_000, 368, 2014),
        ('APL TEMASEK', 9632131, 150_000, 14_000, 368, 2014),
        ('APL VANDA', 9461506, 80_000, 8_000, 320, 2011),
    ],
    'L25': [  # Sinokor
        ('SINOKOR HONG KONG', 9404211, 18_000, 1_700, 170, 2009),
        ('SINOKOR SHANGHAI', 9404223, 18_000, 1_700, 170, 2009),
    ],
}

VESSELS = []
_VID = 1
for line_id, vessels in VESSEL_NAMES.items():
    for name, imo, dwt, teu, length, year in vessels:
        # Vessel type — by DWT per spec (mega>=200k, large 100-200k, medium 50-100k, feeder<50k)
        if dwt >= 200_000:
            vtype = 'mega'
        elif dwt >= 100_000:
            vtype = 'large'
        elif dwt >= 50_000:
            vtype = 'medium'
        else:
            vtype = 'feeder'
        flag_map = {
            'L01':'Liberia','L02':'Đan Mạch','L03':'Pháp','L04':'Hong Kong','L05':'Đức',
            'L06':'Singapore','L07':'Panama','L08':'Hàn Quốc','L09':'Đài Loan','L10':'Israel',
            'L11':'Đài Loan','L12':'Panama','L13':'Hàn Quốc','L14':'Đài Loan','L15':'Singapore',
            'L16':'Hong Kong','L17':'Thái Lan','L18':'Hàn Quốc','L19':'Đài Loan','L20':'Pháp',
            'L21':'Hàn Quốc','L22':'Hàn Quốc','L23':'Đan Mạch','L24':'Singapore','L25':'Hàn Quốc',
        }
        VESSELS.append((f'V{_VID:03d}', name, imo, flag_map.get(line_id,'Panama'), line_id, dwt, teu, length, year, vtype))
        _VID += 1

# =============================================================================
# SERVICES — ~30 named routes
# =============================================================================
# (service_id, service_name, operator_alliance_id, trade_lane, frequency_weekly, port_rotation, active_from, active_to)
# Use post-Feb-2025 alliances primarily for active services
SERVICES = [
    # Asia-Europe
    ('S01', 'FE1 - Far East Europe 1',            'A06', 'Asia-Europe', 1, 'Ningbo-Shanghai-Yantian-Singapore-Gemalink-Port Klang-Suez-Rotterdam-Hamburg-Antwerp', date(2023,1,1), None),
    ('S02', 'FE2 - Far East Europe 2',            'A06', 'Asia-Europe', 1, 'Qingdao-Ningbo-Shanghai-Yantian-Gemalink-Singapore-Jeddah-Piraeus-Genoa', date(2023,4,1), None),
    ('S03', 'FE4 - Far East Europe 4',            'A06', 'Asia-Europe', 1, 'Shanghai-Ningbo-Nansha-Yantian-Gemalink-Singapore-Suez-Algeciras-Rotterdam', date(2024,1,1), None),
    ('S04', 'Gemini AE1 - Asia Europe Shuttle',   'A04', 'Asia-Europe', 1, 'Shanghai-Ningbo-Xiamen-Yantian-Singapore-Tangier-Rotterdam-Bremerhaven', date(2025,2,1), None),
    ('S05', 'Gemini AE2 - Asia Europe Direct',    'A04', 'Asia-Europe', 1, 'Qingdao-Ningbo-Shanghai-Yantian-Tanjung Pelepas-Algeciras-Rotterdam', date(2025,2,1), None),
    ('S06', 'Premier AE3',                        'A05', 'Asia-Europe', 1, 'Kaohsiung-Xiamen-Ningbo-Shanghai-Singapore-Port Klang-Colombo-Rotterdam', date(2025,2,1), None),
    # TransPacific
    ('S07', 'EC1 - East Coast 1',                 'A06', 'TransPacific', 1, 'Ningbo-Shanghai-Busan-Gemalink-Singapore-Colombo-Suez-New York-Savannah', date(2023,1,1), None),
    ('S08', 'EC2 - East Coast 2',                 'A06', 'TransPacific', 1, 'Yantian-Ningbo-Shanghai-Gemalink-Suez-Norfolk-New York-Charleston', date(2024,1,1), None),
    ('S09', 'EC5 - TransPacific via Panama',      'A06', 'TransPacific', 1, 'Gemalink-Shekou-Yantian-Busan-Panama-Savannah-Charleston', date(2024,6,1), None),
    ('S10', 'PN1 - Pacific North 1 (US West)',    'A07', 'TransPacific', 1, 'Ningbo-Shanghai-Busan-Los Angeles-Oakland', date(2025,2,1), None),
    ('S11', 'Gemini TP8',                         'A04', 'TransPacific', 1, 'Yantian-Ningbo-Shanghai-Los Angeles-Oakland', date(2025,2,1), None),
    ('S12', 'Premier PS1',                        'A05', 'TransPacific', 1, 'Kaohsiung-Xiamen-Hong Kong-Los Angeles-Long Beach', date(2025,2,1), None),
    # Intra-Asia (regional)
    ('S13', 'Tropic 1 - Southeast Asia Loop',     None,  'Intra-Asia', 2, 'Nam Đình Vũ-Hong Kong-Shekou-Singapore-Port Klang', date(2022,1,1), None),
    ('S14', 'Tropic 2',                           None,  'Intra-Asia', 1, 'Nam Đình Vũ-Cát Lái-Gemalink-Singapore-Port Klang', date(2023,1,1), None),
    ('S15', 'Korea Vietnam Express (KVX)',        None,  'Intra-Asia', 1, 'Busan-Incheon-Nam Đình Vũ-Cát Lái', date(2021,1,1), None),
    ('S16', 'Japan Vietnam Service (JVS)',        None,  'Intra-Asia', 1, 'Tokyo-Kobe-Nam Đình Vũ-Cát Lái', date(2021,1,1), None),
    ('S17', 'China Vietnam Shuttle 1',            None,  'Intra-Asia', 2, 'Shekou-Xiamen-Nam Đình Vũ', date(2021,1,1), None),
    ('S18', 'China Vietnam Shuttle 2',            None,  'Intra-Asia', 2, 'Shanghai-Ningbo-Nam Đình Vũ-Cát Lái', date(2020,1,1), None),
    ('S19', 'Taiwan Vietnam Express',             None,  'Intra-Asia', 1, 'Kaohsiung-Keelung-Nam Đình Vũ-Cát Lái', date(2020,1,1), None),
    ('S20', 'SITC China-Vietnam Direct',          None,  'Intra-Asia', 2, 'Qingdao-Shanghai-Ningbo-Gemalink-Nam Đình Vũ', date(2021,1,1), None),
    ('S21', 'Wan Hai AX1',                        None,  'Intra-Asia', 1, 'Kaohsiung-Hong Kong-Shekou-Cát Lái-Gemalink', date(2022,1,1), None),
    ('S22', 'Intra-Asia Feeder NDV-GML',          None,  'Intra-Asia', 2, 'Nam Đình Vũ-Cát Lái-Gemalink', date(2020,1,1), None),
    # Asia-Middle East / India
    ('S23', 'IMX - India Middle East Express',    'A06', 'Asia-Middle East', 1, 'Ningbo-Shanghai-Singapore-Gemalink-Colombo-Mundra-Jebel Ali', date(2023,1,1), None),
    ('S24', 'Asia Gulf Express',                  'A07', 'Asia-Middle East', 1, 'Shanghai-Yantian-Gemalink-Singapore-Jebel Ali-Dammam', date(2025,2,1), None),
    # Asia-Americas (West Coast)
    ('S25', 'WC1 - West Coast 1',                 'A04', 'Asia-Americas', 1, 'Shanghai-Ningbo-Gemalink-Busan-Los Angeles', date(2025,2,1), None),
    ('S26', 'WC2 - Pacific Shuttle',              'A06', 'Asia-Americas', 1, 'Yantian-Ningbo-Gemalink-Los Angeles-Oakland', date(2024,1,1), None),
    # Pre-2025 services (closed)
    ('S27', 'AE10 - 2M Asia Europe (legacy)',     'A01', 'Asia-Europe', 1, 'Yantian-Ningbo-Singapore-Rotterdam-Hamburg', date(2020,1,1), date(2025,1,31)),
    ('S28', 'TP2 - THE Alliance TransPacific (legacy)','A02', 'TransPacific', 1, 'Yantian-Ningbo-Gemalink-Los Angeles', date(2019,1,1), date(2025,1,31)),
    # ZIM-MSC new
    ('S29', 'ZIM-MSC ZX2 TransPacific',           'A07', 'TransPacific', 1, 'Ningbo-Shanghai-Xiamen-Hong Kong-Yantian-Los Angeles', date(2025,2,15), None),
    # CMA CGM standalone intra-asia
    ('S30', 'NEMO Asia-Pacific',                  'A06', 'Intra-Asia', 1, 'Shanghai-Xiamen-Hong Kong-Gemalink-Port Klang', date(2024,3,1), None),
]

# =============================================================================
# CUSTOMERS / SHIPPERS
# =============================================================================
CUSTOMERS = [
    ('C01', 'Samsung Electronics Vietnam',  'Electronics',  'Bắc'),
    ('C02', 'LG Electronics Vietnam',       'Electronics',  'Bắc'),
    ('C03', 'Foxconn Vietnam',              'Electronics',  'Bắc'),
    ('C04', 'Pegatron Vietnam',             'Electronics',  'Bắc'),
    ('C05', 'Canon Vietnam',                'Electronics',  'Bắc'),
    ('C06', 'Intel Vietnam',                'Semiconductor','Nam'),
    ('C07', 'Nike Vietnam',                 'Apparel',      'Nam'),
    ('C08', 'Adidas Vietnam',               'Apparel',      'Nam'),
    ('C09', 'Puma Vietnam',                 'Apparel',      'Nam'),
    ('C10', 'Uniqlo Vietnam',               'Apparel',      'Nam'),
    ('C11', 'H&M Vietnam',                  'Apparel',      'Nam'),
    ('C12', 'Vinamilk',                     'Dairy',        'Nam'),
    ('C13', 'Masan Group',                  'Consumer',     'Nam'),
    ('C14', 'Trung Nguyên Legend',          'Coffee',       'Nam'),
    ('C15', 'TCM Dệt May Thành Công',       'Textile',      'Nam'),
    ('C16', 'Garmex Sài Gòn',               'Textile',      'Nam'),
    ('C17', 'Vinatex',                      'Textile',      'Nam'),
    ('C18', 'Saigon Paper',                 'Paper',        'Nam'),
    ('C19', 'Hòa Phát Steel',               'Steel',        'Bắc'),
    ('C20', 'Pomina Steel',                 'Steel',        'Nam'),
    ('C21', 'Trường Thành Wood',            'Furniture',    'Nam'),
    ('C22', 'AA Corporation',               'Furniture',    'Nam'),
    ('C23', 'Minh Phú Seafood',             'Seafood',      'Nam'),
    ('C24', 'Vĩnh Hoàn Seafood',            'Seafood',      'Nam'),
    ('C25', 'Hùng Vương Seafood',           'Seafood',      'Nam'),
    ('C26', 'Lộc Trời Rice',                'Rice',         'Nam'),
    ('C27', 'Vinacafe Biên Hòa',            'Coffee',       'Nam'),
    ('C28', 'Phúc Sinh Coffee',             'Coffee',       'Nam'),
    ('C29', 'Intimex Group',                'Agricultural', 'Nam'),
    ('C30', 'Olam Vietnam',                 'Agricultural', 'Nam'),
    ('C31', 'Cargill Vietnam',              'Feed',         'Nam'),
    ('C32', 'CP Vietnam',                   'Feed',         'Nam'),
    ('C33', 'Mitsubishi Motors Vietnam',    'Automotive',   'Bắc'),
    ('C34', 'Toyota Vietnam',               'Automotive',   'Bắc'),
    ('C35', 'VinFast',                      'Automotive',   'Bắc'),
    ('C36', 'Nestlé Vietnam',               'Consumer',     'Nam'),
    ('C37', 'Unilever Vietnam',             'Consumer',     'Nam'),
    ('C38', 'PepsiCo Vietnam',              'Consumer',     'Nam'),
    ('C39', 'Coca-Cola Vietnam',            'Consumer',     'Nam'),
    ('C40', 'Panasonic Vietnam',            'Electronics',  'Bắc'),
    ('C41', 'Schaeffler Vietnam',           'Machinery',    'Nam'),
    ('C42', 'Bosch Vietnam',                'Machinery',    'Nam'),
    ('C43', 'Hoya Lens Vietnam',            'Optics',       'Bắc'),
    ('C44', 'Nitori Vietnam',               'Furniture',    'Nam'),
    ('C45', 'Casey International',          'Forwarder',    'Nam'),
]

# =============================================================================
# NEWS EVENTS
# =============================================================================
# (event_id, event_date, title_vi, title_en, summary_vi, source, category, sentiment, affected_lines, affected_ports, affected_regions)
NEWS_EVENTS_RAW = [
    # === Pre-break alliance news (2024) ===
    ('2024-05-20', 'Maersk và Hapag-Lloyd công bố liên minh Gemini — kỷ nguyên 2M kết thúc',
     'Maersk and Hapag-Lloyd announce Gemini Cooperation — 2M era ends',
     'Maersk và Hapag-Lloyd công bố liên minh Gemini Cooperation có hiệu lực 2/2025. Dự kiến vận hành 290 tàu, 3.4M TEU theo mô hình hub-and-spoke, giảm port call lẻ tại cảng phụ.',
     'Phaata', 'alliance', 'neutral', ['L02','L05'], ['P006'], ['global']),
    ('2024-06-10', 'THE Alliance tái cấu trúc thành Premier Alliance',
     'THE Alliance restructures into Premier Alliance',
     'ONE, HMM, Yang Ming công bố lập Premier Alliance từ 2/2025 sau khi Hapag rời đi. Quy mô 240 tàu 1.9M TEU.',
     'Alphaliner', 'alliance', 'neutral', ['L06','L08','L09'], [], ['global']),
    ('2024-08-15', 'Ocean Alliance gia hạn hợp tác đến 2032',
     'Ocean Alliance extends cooperation to 2032',
     'CMA CGM, COSCO, Evergreen và OOCL gia hạn Ocean Alliance thêm 5 năm đến 2032 — lớn nhất toàn cầu ~6M TEU, 30% thị phần Asia-Europe.',
     'Linerlytica', 'alliance', 'positive', ['L03','L04','L07','L16'], ['P006'], ['global']),
    ('2024-09-05', 'MSC độc lập — kế hoạch mở rộng 5 triệu TEU',
     'MSC goes independent — expands to 5M TEU',
     'MSC xác nhận sẽ độc lập từ 2/2025, khai thác đội tàu 5M TEU (19.8% thị phần toàn cầu) không qua liên minh. Hãng đang tìm đối tác cảng Việt Nam.',
     'Alphaliner', 'alliance', 'neutral', ['L01'], [], ['global']),
    ('2024-11-12', 'Giá sàn bốc xếp sẽ tăng 10% cho cảng nước sâu từ 2/2026',
     'Stevedoring price floor to rise 10% for deepsea ports from Feb 2026',
     'Bộ Xây dựng đề xuất sửa đổi QĐ 810/QĐ-BGTVT, tăng 10% khung giá sàn cho cảng nước sâu áp dụng từ 1/2/2026 — hỗ trợ đầu tư cảng.',
     'Cổng thông tin Bộ XD', 'regulation', 'positive', [], ['P006','P014','P015','P021','P022'], ['VN']),
    ('2024-12-15', 'TCIT ký MOU với Gemini Cooperation làm hub miền Nam',
     'TCIT signs MOU with Gemini as southern hub',
     'Tân Cảng - Cái Mép Thị Vải (TCIT) ký Biên bản ghi nhớ với Gemini Cooperation, dự kiến là hub chính tại Việt Nam cho Maersk và Hapag-Lloyd từ 2/2025.',
     'Phaata', 'route', 'negative', ['L02','L05'], ['P010','P006'], ['CM-TV']),
    # === Break point (Feb 2025) ===
    ('2025-01-31', '2M Alliance chính thức giải thể',
     '2M Alliance officially dissolves',
     'Sau 10 năm, liên minh 2M giữa Maersk và MSC chính thức giải thể. Hai hãng chọn chiến lược riêng.',
     'Lloyd List', 'alliance', 'neutral', ['L01','L02'], [], ['global']),
    ('2025-02-01', 'Gemini Cooperation chính thức vận hành',
     'Gemini Cooperation officially launches',
     'Maersk và Hapag-Lloyd bắt đầu vận hành liên minh Gemini Cooperation theo mô hình hub-and-spoke. Các tuyến chính giảm số port call, tăng reliability.',
     'Lloyd List', 'alliance', 'neutral', ['L02','L05'], ['P006','P010'], ['global']),
    ('2025-02-01', 'Premier Alliance khai trương',
     'Premier Alliance starts operations',
     'ONE, HMM, Yang Ming vận hành Premier Alliance từ hôm nay. 240 tàu phục vụ Asia-Europe và TransPacific.',
     'Lloyd List', 'alliance', 'neutral', ['L06','L08','L09'], [], ['global']),
    ('2025-02-01', 'Ocean Alliance bước vào chu kỳ mới',
     'Ocean Alliance enters new cycle',
     'CMA CGM, COSCO, Evergreen, OOCL chính thức khởi động Ocean Alliance gia hạn — cam kết đầu tư tuyến mới.',
     'Alphaliner', 'alliance', 'positive', ['L03','L04','L07','L16'], ['P006'], ['global']),
    ('2025-02-10', 'ZIM ký thoả thuận slot với MSC trên tuyến xuyên Thái Bình Dương',
     'ZIM partners with MSC on TransPacific slots',
     'ZIM và MSC công bố thoả thuận chia sẻ slot trên tuyến Asia-Americas. ZIM tăng hiện diện CM-TV để kết nối hub US West Coast.',
     'Alphaliner', 'alliance', 'positive', ['L01','L10'], ['P010','P013','P006'], ['CM-TV']),
    ('2025-02-18', 'Maersk xác nhận chuyển hub miền Nam Việt Nam sang TCIT',
     'Maersk confirms shift of southern VN hub to TCIT',
     'Trong briefing đầu tiên của Gemini tại VN, Maersk xác nhận Gemalink sẽ giảm call, TCIT thành hub chính.',
     'Phaata', 'route', 'negative', ['L02'], ['P006','P010'], ['CM-TV']),
    # === Post-break operations (Feb-Dec 2025) ===
    ('2025-03-05', 'Gemalink công suất mới: giai đoạn 2A vận hành thử',
     'Gemalink Phase 2A begins trial operations',
     'Gemalink bắt đầu chạy thử bến Phase 2A, nâng công suất từ 1.5M lên 2.0M TEU/năm.',
     'Gemadept IR', 'competitor', 'positive', [], ['P006'], ['CM-TV']),
    ('2025-04-15', 'Nam Đình Vũ GĐ3 khánh thành',
     'Nam Dinh Vu Phase 3 inaugurated',
     'Cụm Nam Đình Vũ khánh thành GĐ3 — công suất cảng cộng dồn đạt 2M TEU/năm, lớn nhất miền Bắc về cảng sông.',
     'Gemadept IR', 'competitor', 'positive', [], ['P001','P007'], ['Hải Phòng']),
    ('2025-05-20', 'CMA CGM mở dịch vụ NEMO kết nối Việt Nam-Nam Á-Úc',
     'CMA CGM launches NEMO service Vietnam-South Asia-Australia',
     'CMA CGM công bố tuyến NEMO mới, ghé Gemalink 1 lần/tuần, phục vụ hàng xuất Úc và Nam Á.',
     'Phaata', 'route', 'positive', ['L03'], ['P006'], ['CM-TV']),
    ('2025-06-10', 'Wan Hai mở tuyến AX1 ghé Cái Mép',
     'Wan Hai launches AX1 calling Cai Mep',
     'Wan Hai Lines mở tuyến AX1 mới, tăng tần suất ghé CM-TV từ 3 lên 5 chuyến/tháng, dùng cả TCIT và Gemalink.',
     'Linerlytica', 'route', 'positive', ['L11'], ['P010','P006'], ['CM-TV']),
    ('2025-07-03', 'Mỹ công bố thuế mới với hàng xuất khẩu Việt Nam',
     'US announces new tariffs on Vietnamese imports',
     'Chính phủ Mỹ công bố điều chỉnh thuế quan đối với một số mặt hàng Việt Nam. Các doanh nghiệp dệt may, điện tử lo ngại ảnh hưởng.',
     'Vietstock', 'tariff', 'negative', [], [], ['US-VN']),
    ('2025-07-22', 'ZIM tăng cường hiện diện tại Cát Mép với 6 call/tháng',
     'ZIM ramps CM-TV presence to 6 calls/month',
     'Sau thoả thuận slot với MSC, ZIM đẩy mạnh ghé TCIT và CMIT, 6 chuyến/tháng. Chưa có kế hoạch ghé Gemalink.',
     'Phaata', 'competitor', 'neutral', ['L10'], ['P010','P013'], ['CM-TV']),
    ('2025-08-15', 'HMM tăng tuyến Asia-Europe qua CM-TV',
     'HMM increases Asia-Europe via CM-TV',
     'HMM công bố tăng 2 tuyến Asia-Europe mới qua TCIT, mục tiêu tăng sản lượng VN 30% năm 2025.',
     'Phaata', 'route', 'positive', ['L08'], ['P010','P006'], ['CM-TV']),
    ('2025-09-02', 'Bão số 3 đổ bộ miền Trung — Dung Quất đóng 36h',
     'Typhoon #3 hits Central VN — Dung Quat closed 36h',
     'Bão số 3 gây ảnh hưởng cảng Dung Quất và Quy Nhơn. Dung Quất tạm đóng cửa 36 giờ, hoạt động trở lại bình thường 5/9.',
     'CafeF', 'weather', 'negative', [], ['P003'], ['Miền Trung']),
    ('2025-10-01', 'Gemadept công bố Q3/2025 doanh thu tăng 28% YoY',
     'Gemadept Q3 2025 revenue +28% YoY',
     'Doanh thu Q3/2025 đạt 1,580 tỷ đồng, tăng 28% YoY nhờ Gemalink full công suất.',
     'Vietstock', 'competitor', 'positive', [], ['P006'], ['CM-TV']),
    ('2025-10-15', 'Nam Đình Vũ GĐ3 vận hành thương mại đầy đủ',
     'Nam Dinh Vu Phase 3 fully operational',
     'GĐ3 Nam Đình Vũ bàn giao cần trục STS và RTG, bắt đầu vận hành thương mại 10/2025 sau thử nghiệm 6 tháng.',
     'Gemadept IR', 'competitor', 'positive', [], ['P001','P007'], ['Hải Phòng']),
    ('2025-11-20', 'Maersk giảm call tại Gemalink — chuyển hub về TCIT theo mô hình Gemini',
     'Maersk reduces Gemalink calls — shifts hub to TCIT under Gemini model',
     'Dữ liệu cảng vụ cho thấy Maersk đã giảm port call tại Gemalink 25% so với Q1/2025, đồng thời tăng tương ứng tại TCIT. Đây là bước đi phù hợp mô hình Gemini hub-and-spoke.',
     'Phaata', 'competitor', 'negative', ['L02'], ['P006','P010'], ['CM-TV']),
    ('2025-12-05', 'OOCL mở thêm tuyến Asia-Europe qua Gemalink',
     'OOCL adds Asia-Europe service via Gemalink',
     'OOCL (Ocean Alliance) mở tuyến FE4 mới, ghé Gemalink hàng tuần, mức tăng 1 call/tuần cho Gemalink.',
     'Phaata', 'route', 'positive', ['L16'], ['P006'], ['CM-TV']),
    ('2025-12-20', 'TCIT hoàn thành mở rộng bến C4, đón tàu 200k DWT',
     'TCIT completes berth C4 expansion — 200k DWT ready',
     'TCIT hoàn thành bến C4 dài 400m, chính thức đón tàu mega 200k DWT. Cạnh tranh trực tiếp với Gemalink.',
     'Phaata', 'competitor', 'negative', [], ['P010','P006'], ['CM-TV']),
    # === Escalation (Jan-Mar 2026) ===
    ('2026-01-08', 'Gemini vận hành ổn định — Maersk tiếp tục giảm Gemalink',
     'Gemini stabilizes — Maersk further reduces Gemalink',
     'Sau 1 năm vận hành Gemini Cooperation, Maersk chính thức rút 3 tuyến ra khỏi Gemalink, chuyển toàn bộ về TCIT. Sản lượng Maersk tại Gemalink giảm mạnh từ Q1/2026.',
     'Lloyd List', 'competitor', 'negative', ['L02'], ['P006','P010'], ['CM-TV']),
    ('2026-01-20', 'ZIM-MSC mở tuyến ZX2 TransPacific qua CMIT',
     'ZIM-MSC launches ZX2 TransPacific via CMIT',
     'Liên minh slot ZIM-MSC chính thức vận hành tuyến ZX2 qua CMIT, 1 chuyến/tuần sang Los Angeles. Gemalink không có trong rotation.',
     'Linerlytica', 'route', 'positive', ['L01','L10'], ['P013'], ['CM-TV']),
    ('2026-02-01', 'Khung giá sàn bốc xếp cảng nước sâu tăng 10%',
     'Deepsea stevedoring price floor raised 10%',
     'Quyết định 810/QĐ-BGTVT sửa đổi có hiệu lực 1/2/2026 — tăng 10% giá sàn cho cảng nước sâu (Gemalink, CMIT, SSIT, HICT, TC-HICT). Cảng sông không thay đổi.',
     'Cổng thông tin Bộ XD', 'regulation', 'positive', [], ['P006','P013','P014','P015','P021','P022'], ['VN']),
    ('2026-02-15', 'Hapag-Lloyd tăng call Gemalink theo Gemini',
     'Hapag-Lloyd increases Gemalink calls under Gemini',
     'Dù Maersk giảm, Hapag-Lloyd lại tăng call Gemalink lên 6/tháng — cân bằng phần nào mất mát từ Maersk. Gemadept đang tích cực tiếp cận Hapag.',
     'Phaata', 'competitor', 'positive', ['L05'], ['P006'], ['CM-TV']),
    ('2026-03-02', 'Mỹ đe doạ thuế 25% hàng Việt Nam từ Q2/2026',
     'US threatens 25% tariff on VN goods from Q2 2026',
     'Chính quyền Mỹ công bố sẽ áp thuế bổ sung 25% lên một số mặt hàng Việt Nam từ Q2/2026 nếu không đạt được thoả thuận thương mại. Hàng điện tử, dệt may, gỗ đứng trước rủi ro.',
     'Vietstock', 'tariff', 'negative', [], [], ['US-VN']),
    # === Historical references (for scenario 8) ===
    ('2018-07-06', 'Trump áp thuế 25% lên 34 tỷ USD hàng Trung Quốc — bắt đầu thương chiến',
     'Trump imposes 25% tariff on $34B Chinese goods — trade war starts',
     'Chính quyền Trump áp thuế 25% lên 34 tỷ USD hàng Trung Quốc, mở đầu thương chiến Mỹ-Trung. Dòng hàng dịch chuyển sang VN bắt đầu từ đây.',
     'Reuters', 'tariff', 'neutral', [], [], ['US-China']),
    ('2019-05-10', 'Trump tăng thuế lên 25% với 200 tỷ USD hàng Trung Quốc',
     'Trump raises tariff to 25% on $200B Chinese goods',
     'Leo thang thương chiến, thuế tăng lên 25% với 200 tỷ USD hàng TQ — VN hưởng lợi dòng hàng dịch chuyển.',
     'Reuters', 'tariff', 'positive', [], [], ['US-China']),
    # === Weather Hai Phong ===
    ('2024-12-08', 'Sương mù dày đặc Hải Phòng — nhiều tàu chờ luồng',
     'Dense fog in Hai Phong — vessels wait channel',
     'Sương mù giảm tầm nhìn tại luồng Lạch Huyện, nhiều tàu chờ cập bến. Nam Đình Vũ ảnh hưởng nhẹ.',
     'CafeF', 'weather', 'negative', [], ['P001','P020','P021'], ['Hải Phòng']),
    ('2025-01-28', 'Sương mù Hải Phòng — chậm trễ 1-2 ngày',
     'Hai Phong fog — 1-2 day delays',
     'Đợt sương mù thứ 2 mùa đông gây chậm cập tàu tại Hải Phòng 1-2 ngày. Không ảnh hưởng đáng kể sản lượng.',
     'CafeF', 'weather', 'negative', [], ['P001','P007','P020','P021','P025'], ['Hải Phòng']),
    ('2026-02-10', 'Sương mù mùa đông Hải Phòng nặng — ảnh hưởng lịch tàu',
     'Dense winter fog in Hai Phong affects vessel schedules',
     'Sương mù dày đặc miền Bắc giai đoạn trước Tết gây chậm cập tàu đồng loạt các cảng Hải Phòng 2-3 ngày.',
     'CafeF', 'weather', 'negative', [], ['P001','P007','P020','P021'], ['Hải Phòng']),
    # === Additional alliance/route speculation ===
    ('2025-05-02', 'Alphaliner: Gemini có thể tái cấu trúc năm 2', 'Alphaliner: Gemini may restructure year 2',
     'Alphaliner dự báo Gemini Cooperation có thể cần tái cấu trúc năm thứ 2 nếu các tuyến Asia-Europe không đạt target reliability 90%.',
     'Alphaliner', 'alliance', 'neutral', ['L02','L05'], [], ['global']),
    ('2025-08-28', 'COSCO mở rộng tuyến Ấn Độ qua Gemalink', 'COSCO expands India routes via Gemalink',
     'COSCO mở rộng tuyến IMX Asia-Ấn Độ, tăng tần suất ghé Gemalink lên 2 chuyến/tuần.',
     'Phaata', 'route', 'positive', ['L04'], ['P006'], ['CM-TV']),
    ('2025-09-20', 'Evergreen đầu tư terminal mới tại CM-TV', 'Evergreen invests new CM-TV terminal',
     'Evergreen công bố ký kết đầu tư vào dự án cảng mới khu vực Cái Mép, công suất 2M TEU/năm, dự kiến 2028.',
     'Vietstock', 'competitor', 'neutral', ['L07'], [], ['CM-TV']),
    ('2024-04-25', 'SITC mở rộng đội tàu 24 chiếc mới', 'SITC expands fleet with 24 new vessels',
     'SITC công bố đầu tư 24 tàu feeder 1,800 TEU mới, ưu tiên tuyến Việt Nam - Hàn - Nhật - TQ.',
     'Linerlytica', 'competitor', 'positive', ['L12'], [], ['Intra-Asia']),
    ('2024-07-08', 'Phí cảng biển TP.HCM đề xuất tăng', 'HCMC port fees proposed to rise',
     'UBND TP.HCM đề xuất tăng phí hạ tầng cảng biển 30% từ 2025, áp dụng cho Cát Lái và các ICD.',
     'CafeF', 'regulation', 'negative', [], ['P030','P031','P032','P004'], ['HCM']),
    ('2024-10-18', 'CMA CGM và Gemadept gia hạn thoả thuận liên doanh Gemalink', 'CMA CGM and Gemadept extend Gemalink JV',
     'CMA Terminals (CMA CGM) và Gemadept chính thức gia hạn hợp tác liên doanh Gemalink thêm 25 năm, cam kết tăng vốn cho GĐ2.',
     'Gemadept IR', 'route', 'positive', ['L03'], ['P006'], ['CM-TV']),
    ('2025-06-25', 'Hapag-Lloyd cân nhắc làm thêm call Gemalink', 'Hapag-Lloyd considers additional Gemalink call',
     'Briefing Q2: Hapag-Lloyd cân nhắc bổ sung 1 call/tuần tại Gemalink trong khuôn khổ Gemini để bù đắp giảm call do hub chính chuyển sang TCIT.',
     'Phaata', 'route', 'positive', ['L05'], ['P006'], ['CM-TV']),
    ('2025-11-04', 'TCIT vượt Gemalink về số call hãng lớn Q3/2025', 'TCIT surpasses Gemalink in major line calls Q3 2025',
     'Theo dữ liệu cảng vụ Vũng Tàu, TCIT đón nhiều port call của top-10 hãng tàu hơn Gemalink lần đầu tiên Q3/2025.',
     'Phaata', 'competitor', 'negative', [], ['P006','P010'], ['CM-TV']),
    ('2024-08-22', 'Cát Lái đạt kỷ lục 5.8M TEU năm 2024 (ước tính)', 'Cat Lai estimated 5.8M TEU record 2024',
     'Cát Lái (Tân Cảng SG) ước thông qua 5.8M TEU năm 2024, tiếp tục là cảng container lớn nhất VN.',
     'Vietstock', 'competitor', 'neutral', [], ['P030'], ['HCM']),
    ('2024-09-28', 'MSC tìm đối tác cảng VN sau tan rã 2M', 'MSC seeks VN port partner post-2M',
     'MSC phát tín hiệu tìm đối tác cảng chiến lược tại VN để chuẩn bị standalone 2/2025. Gemalink, CMIT, SSIT đều trong radar.',
     'Alphaliner', 'alliance', 'neutral', ['L01'], ['P006','P013','P014'], ['CM-TV']),
    ('2025-03-20', 'MSC tăng 3 call/tháng tại Gemalink', 'MSC adds 3 calls/month at Gemalink',
     'MSC chính thức tăng tần suất call Gemalink từ 3 lên 6/tháng bắt đầu 3/2025, trong chiến lược standalone.',
     'Phaata', 'route', 'positive', ['L01'], ['P006'], ['CM-TV']),
    ('2024-05-30', 'Hãng tàu cân nhắc hub lại tại CM-TV', 'Lines re-considering CM-TV hub strategy',
     'Linerlytica: Nhiều hãng tàu đang đánh giá lại chiến lược hub tại CM-TV trước thềm tái cấu trúc liên minh 2/2025.',
     'Linerlytica', 'alliance', 'neutral', [], ['P006','P010','P013','P014'], ['CM-TV']),
    ('2025-04-05', 'Gemadept đặt target 2026 thị phần 18%', 'Gemadept targets 18% market share 2026',
     'Trong AGM, Chủ tịch Gemadept đặt target thị phần container 18% năm 2026, chủ yếu nhờ Gemalink GĐ2A và NDV GĐ3.',
     'Gemadept IR', 'competitor', 'positive', [], [], ['VN']),
    ('2026-03-15', 'Gemini Cooperation có thể rút thêm tuyến CM-TV', 'Gemini may pull more CM-TV routes',
     'Briefing Lloyd List: Gemini Cooperation đánh giá hiệu quả năm 1, có thể rút thêm 1-2 tuyến CM-TV trong Q2/2026 để tối ưu hub-spoke.',
     'Lloyd List', 'alliance', 'negative', ['L02','L05'], ['P006','P010'], ['CM-TV']),
    ('2024-06-30', 'ZIM công bố liên minh xuyên Thái Bình Dương mới', 'ZIM announces new TransPacific alliance',
     'ZIM có kế hoạch mở rộng tuyến TransPacific thông qua liên minh slot mới với MSC, bắt đầu 2/2025. VN là điểm trọng tâm.',
     'Alphaliner', 'alliance', 'neutral', ['L01','L10'], [], ['global']),
    ('2025-07-18', 'Chiến tranh Trung Đông — tuyến Biển Đỏ tiếp tục tránh Suez',
     'Middle East conflict — Red Sea diversions continue',
     'Các hãng tiếp tục vòng qua Mũi Hảo Vọng, thời gian Asia-Europe kéo dài 14 ngày. Tăng nhu cầu công suất.',
     'Lloyd List', 'route', 'neutral', [], [], ['global']),
    ('2024-11-28', 'HICT Lạch Huyện tăng thị phần Hải Phòng',
     'HICT Lach Huyen gains Hai Phong market share',
     'HICT (Lạch Huyện Hateco-Itochu) tăng thị phần cont Hải Phòng từ 25% lên 32% trong 9T/2024 nhờ đón tàu mẹ Asia-US West Coast.',
     'Phaata', 'competitor', 'negative', [], ['P021','P001'], ['Hải Phòng']),
    ('2025-04-22', 'Cảng VN qua mốc 16 triệu TEU 6T/2025 — tăng 13% YoY', 'VN ports cross 16M TEU H1 2025 — +13% YoY',
     'Tổng sản lượng container qua các cảng VN đạt 16.3M TEU trong 6T/2025, tăng 13% YoY, dẫn dắt bởi cụm CM-TV và Hải Phòng.',
     'Vietstock', 'competitor', 'positive', [], [], ['VN']),
    ('2025-12-12', 'CMIT mở rộng thêm 2 tuyến TransPacific cho ZIM-MSC', 'CMIT adds 2 more TransPacific routes for ZIM-MSC',
     'CMIT công bố ký bổ sung 2 tuyến TransPacific tuần cho liên minh ZIM-MSC từ 1/2026 — củng cố vị thế hub xuyên TBD.',
     'Phaata', 'competitor', 'negative', ['L01','L10'], ['P013'], ['CM-TV']),
    ('2024-04-15', 'Khối lượng XK Mỹ năm 2024 dự báo +8%', 'US export volume forecast +8% for 2024',
     'Linerlytica dự báo khối lượng XK VN-Mỹ tăng 8% năm 2024 — TransPacific tiếp tục là tuyến tăng trưởng nhanh nhất.',
     'Linerlytica', 'route', 'positive', [], [], ['US-VN']),
    ('2025-10-25', 'Premier Alliance đánh giá hub VN tại CM-TV', 'Premier Alliance evaluates VN hub at CM-TV',
     'Briefing nội bộ ONE: Premier Alliance đánh giá lập hub VN, ưu tiên TCIT và CMIT, có thể giảm Gemalink trừ khi giá ưu đãi.',
     'Linerlytica', 'alliance', 'negative', ['L06','L08','L09'], ['P006','P010','P013'], ['CM-TV']),
    ('2026-03-25', 'Hapag-Lloyd ký thoả thuận khung dài hạn với Gemalink', 'Hapag-Lloyd signs long-term framework with Gemalink',
     'Trong khuôn khổ Gemini, Hapag-Lloyd ký framework deal 3 năm với Gemalink, cam kết tối thiểu 5 call/tháng, ưu đãi giá xếp dỡ.',
     'Phaata', 'route', 'positive', ['L05'], ['P006'], ['CM-TV']),
    ('2025-08-05', 'Bộ XD: Khung giá sàn cảng nước sâu được duyệt', 'MOC: Deepsea price floor approved',
     'Bộ Xây dựng chính thức ban hành Quyết định sửa đổi 810/QĐ-BGTVT — tăng 10% giá sàn cảng nước sâu hiệu lực 1/2/2026.',
     'Cổng thông tin Bộ XD', 'regulation', 'positive', [], ['P006','P013','P014','P015','P021','P022'], ['VN']),
    ('2024-04-10', 'Maersk báo Q1/2024 lợi nhuận giảm', 'Maersk Q1 2024 profit down',
     'Maersk báo Q1/2024 lợi nhuận giảm sâu do giá cước phục hồi chậm, dự báo phải tái cấu trúc network tiếp theo.',
     'Lloyd List', 'competitor', 'negative', ['L02'], [], ['global']),
]

NEWS_EVENTS = []
for i, ev in enumerate(NEWS_EVENTS_RAW):
    NEWS_EVENTS.append((f'N{i+1:03d}',) + ev)

# =============================================================================
# DDL
# =============================================================================
DDL_SQL = f"""-- =============================================================================
-- 01_ddl_schema.sql  |  Database: {DB_NAME}
-- Gemadept BI Demo — MKT Manager persona
-- Schema: 12 data tables + 4 metadata tables
-- =============================================================================

DROP DATABASE IF EXISTS `{DB_NAME}`;
CREATE DATABASE `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `{DB_NAME}`;

-- ----- Dimensions -----
CREATE TABLE `ports` (
  `port_id` VARCHAR(10) PRIMARY KEY,
  `port_name` VARCHAR(100) NOT NULL,
  `port_code` VARCHAR(10) NOT NULL,
  `is_gemadept` TINYINT(1) NOT NULL DEFAULT 0,
  `region` VARCHAR(20) NOT NULL,
  `cluster` VARCHAR(30) NOT NULL,
  `port_type` VARCHAR(20) NOT NULL,
  `capacity_teu_year` INT,
  `max_dwt` INT,
  `operator_company` VARCHAR(100),
  `latitude` DECIMAL(9,4),
  `longitude` DECIMAL(9,4)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `shipping_lines` (
  `line_id` VARCHAR(10) PRIMARY KEY,
  `line_name` VARCHAR(100) NOT NULL,
  `line_code` VARCHAR(10) NOT NULL,
  `country` VARCHAR(50),
  `fleet_size_vessels` INT,
  `fleet_capacity_teu` INT,
  `global_rank` INT,
  `vietnam_presence_since` INT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `alliances` (
  `alliance_id` VARCHAR(10) PRIMARY KEY,
  `alliance_name` VARCHAR(100) NOT NULL,
  `formed_date` DATE,
  `dissolved_date` DATE,
  `combined_teu` INT,
  `market_share_pct` DECIMAL(5,2),
  `trade_focus` VARCHAR(200),
  `status` VARCHAR(20)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `alliance_membership_history` (
  `membership_id` VARCHAR(10) PRIMARY KEY,
  `line_id` VARCHAR(10) NOT NULL,
  `alliance_id` VARCHAR(10) NOT NULL,
  `from_date` DATE NOT NULL,
  `to_date` DATE,
  FOREIGN KEY (`line_id`) REFERENCES `shipping_lines`(`line_id`),
  FOREIGN KEY (`alliance_id`) REFERENCES `alliances`(`alliance_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `vessels` (
  `vessel_id` VARCHAR(10) PRIMARY KEY,
  `vessel_name` VARCHAR(100) NOT NULL,
  `imo_number` INT,
  `flag` VARCHAR(30),
  `owner_line_id` VARCHAR(10),
  `dwt` INT,
  `teu_capacity` INT,
  `length_meters` INT,
  `year_built` INT,
  `vessel_type` VARCHAR(20),
  FOREIGN KEY (`owner_line_id`) REFERENCES `shipping_lines`(`line_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `services` (
  `service_id` VARCHAR(10) PRIMARY KEY,
  `service_name` VARCHAR(150) NOT NULL,
  `operator_alliance_id` VARCHAR(10),
  `trade_lane` VARCHAR(50),
  `frequency_weekly` INT,
  `port_rotation` TEXT,
  `active_from` DATE,
  `active_to` DATE,
  FOREIGN KEY (`operator_alliance_id`) REFERENCES `alliances`(`alliance_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `news_events` (
  `event_id` VARCHAR(10) PRIMARY KEY,
  `event_date` DATE NOT NULL,
  `title_vi` VARCHAR(500),
  `title_en` VARCHAR(500),
  `summary_vi` TEXT,
  `source` VARCHAR(100),
  `category` VARCHAR(30),
  `sentiment` VARCHAR(20),
  `affected_lines` JSON,
  `affected_ports` JSON,
  `affected_regions` JSON,
  INDEX `idx_date` (`event_date`),
  INDEX `idx_category` (`category`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `customers_shippers` (
  `customer_id` VARCHAR(10) PRIMARY KEY,
  `customer_name` VARCHAR(150) NOT NULL,
  `industry` VARCHAR(50),
  `primary_region` VARCHAR(20)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----- Facts -----
CREATE TABLE `port_calls` (
  `call_id` VARCHAR(15) PRIMARY KEY,
  `port_id` VARCHAR(10) NOT NULL,
  `vessel_id` VARCHAR(10) NOT NULL,
  `voyage_no` VARCHAR(20),
  `service_id` VARCHAR(10),
  `shipping_line_id` VARCHAR(10) NOT NULL,
  `eta` DATETIME NOT NULL,
  `etb` DATETIME,
  `etd` DATETIME,
  `ata` DATETIME,
  `atb` DATETIME,
  `atd` DATETIME,
  `berth_id` VARCHAR(10),
  `teu_discharged` INT,
  `teu_loaded` INT,
  `teu_transshipment` INT,
  `total_teu_handled` INT,
  `dwell_time_hours` DECIMAL(7,2),
  `revenue_vnd` BIGINT,
  `cost_vnd` BIGINT,
  `reefer_teu` INT,
  `vas_revenue_vnd` BIGINT,
  FOREIGN KEY (`port_id`) REFERENCES `ports`(`port_id`),
  FOREIGN KEY (`vessel_id`) REFERENCES `vessels`(`vessel_id`),
  FOREIGN KEY (`shipping_line_id`) REFERENCES `shipping_lines`(`line_id`),
  FOREIGN KEY (`service_id`) REFERENCES `services`(`service_id`),
  INDEX `idx_port_eta` (`port_id`, `eta`),
  INDEX `idx_line_eta` (`shipping_line_id`, `eta`),
  INDEX `idx_service_eta` (`service_id`, `eta`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `daily_port_stats` (
  `stat_id` VARCHAR(15) PRIMARY KEY,
  `port_id` VARCHAR(10) NOT NULL,
  `stat_date` DATE NOT NULL,
  `total_teu` INT,
  `total_calls` INT,
  `total_revenue_vnd` BIGINT,
  `unique_lines_count` INT,
  FOREIGN KEY (`port_id`) REFERENCES `ports`(`port_id`),
  UNIQUE KEY `uniq_port_date` (`port_id`, `stat_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `port_vessel_schedule_external` (
  `schedule_id` VARCHAR(15) PRIMARY KEY,
  `port_id` VARCHAR(10) NOT NULL,
  `vessel_id` VARCHAR(10),
  `shipping_line_id` VARCHAR(10) NOT NULL,
  `eta` DATETIME NOT NULL,
  `etd` DATETIME,
  `service_id` VARCHAR(10),
  `teu_capacity_est` INT,
  `source` VARCHAR(30),
  FOREIGN KEY (`port_id`) REFERENCES `ports`(`port_id`),
  FOREIGN KEY (`shipping_line_id`) REFERENCES `shipping_lines`(`line_id`),
  INDEX `idx_ext_port_eta` (`port_id`, `eta`),
  INDEX `idx_ext_line_eta` (`shipping_line_id`, `eta`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `pricing_tariff` (
  `tariff_id` VARCHAR(15) PRIMARY KEY,
  `port_id` VARCHAR(10) NOT NULL,
  `line_id` VARCHAR(10),
  `rate_per_teu_vnd` INT NOT NULL,
  `effective_from` DATE NOT NULL,
  `effective_to` DATE,
  FOREIGN KEY (`port_id`) REFERENCES `ports`(`port_id`),
  FOREIGN KEY (`line_id`) REFERENCES `shipping_lines`(`line_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----- Metadata -----
CREATE TABLE `_meta_tables` (
  `table_name` VARCHAR(50) PRIMARY KEY,
  `description_vi` TEXT,
  `description_en` TEXT,
  `business_context` TEXT,
  `data_source` VARCHAR(50)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `_meta_columns` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `table_name` VARCHAR(50) NOT NULL,
  `column_name` VARCHAR(50) NOT NULL,
  `data_type` VARCHAR(30),
  `description_vi` TEXT,
  `description_en` TEXT,
  `unit` VARCHAR(30),
  `example_values` TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `_meta_kpi` (
  `kpi_name` VARCHAR(100) PRIMARY KEY,
  `formula_sql` TEXT,
  `description_vi` TEXT,
  `related_questions` TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `_meta_glossary` (
  `term_vi` VARCHAR(100) PRIMARY KEY,
  `term_en` VARCHAR(100),
  `definition` TEXT,
  `related_tables` VARCHAR(200)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""


def write_ddl():
    path = os.path.join(SQL_DIR, '01_ddl_schema.sql')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(DDL_SQL)
    print(f"Wrote {path}")


# =============================================================================
# MASTER DATA WRITER
# =============================================================================
def write_master_data():
    path = os.path.join(SQL_DIR, '03_master_data.sql')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(f"-- 03_master_data.sql | Database: {DB_NAME}\n")
        f.write(f"-- Master/dimension tables: ports, shipping_lines, alliances, alliance_membership_history, vessels, services, news_events, customers_shippers\n\n")
        f.write(f"USE `{DB_NAME}`;\n\n")

        write_inserts(f, 'ports',
                      ['port_id','port_name','port_code','is_gemadept','region','cluster',
                       'port_type','capacity_teu_year','max_dwt','operator_company','latitude','longitude'],
                      PORTS)

        write_inserts(f, 'shipping_lines',
                      ['line_id','line_name','line_code','country','fleet_size_vessels',
                       'fleet_capacity_teu','global_rank','vietnam_presence_since'],
                      SHIPPING_LINES)

        write_inserts(f, 'alliances',
                      ['alliance_id','alliance_name','formed_date','dissolved_date',
                       'combined_teu','market_share_pct','trade_focus','status'],
                      ALLIANCES)

        write_inserts(f, 'alliance_membership_history',
                      ['membership_id','line_id','alliance_id','from_date','to_date'],
                      ALLIANCE_MEMBERSHIPS)

        write_inserts(f, 'vessels',
                      ['vessel_id','vessel_name','imo_number','flag','owner_line_id',
                       'dwt','teu_capacity','length_meters','year_built','vessel_type'],
                      VESSELS)

        write_inserts(f, 'services',
                      ['service_id','service_name','operator_alliance_id','trade_lane',
                       'frequency_weekly','port_rotation','active_from','active_to'],
                      SERVICES)

        # news_events: JSON cols need json.dumps
        news_rows = []
        for ev in NEWS_EVENTS:
            (eid, dt, t_vi, t_en, summ, src, cat, sent, lines, ports, regions) = ev
            news_rows.append((eid, dt, t_vi, t_en, summ, src, cat, sent,
                              json.dumps(lines, ensure_ascii=False),
                              json.dumps(ports, ensure_ascii=False),
                              json.dumps(regions, ensure_ascii=False)))
        write_inserts(f, 'news_events',
                      ['event_id','event_date','title_vi','title_en','summary_vi','source',
                       'category','sentiment','affected_lines','affected_ports','affected_regions'],
                      news_rows)

        write_inserts(f, 'customers_shippers',
                      ['customer_id','customer_name','industry','primary_region'],
                      CUSTOMERS)

    print(f"Wrote {path}")


# =============================================================================
# PHASE C — TRANSACTION DATA
# =============================================================================
# Vessel pool by line (vessel_id list)
VESSELS_BY_LINE = defaultdict(list)
for v in VESSELS:
    VESSELS_BY_LINE[v[4]].append(v)  # owner_line_id → vessel tuple

# Port DWT capacity for filtering vessels
PORT_INFO = {p[0]: p for p in PORTS}  # port_id → tuple

# Service lookup: line_id → preferred services
LINE_TO_SERVICES = defaultdict(list)
for s in SERVICES:
    if s[7] is None or s[7] >= START_DATE:  # active
        # Determine line membership of operating alliance at base date
        if s[2] is not None:
            for m in ALLIANCE_MEMBERSHIPS:
                if m[2] == s[2] and m[4] is None:  # current memberships
                    LINE_TO_SERVICES[m[1]].append(s[0])

# =============================================================================
# Base monthly call patterns
# =============================================================================
# Format: { port_id: { line_id: base_calls_per_month } }
GEMADEPT_BASE = {
    'P006': {  # Gemalink — deepsea, ULCV friendly
        'L03': 4.0, 'L04': 2.5, 'L07': 2.0, 'L16': 1.0,
        'L02': 2.5, 'L05': 1.0, 'L06': 1.5, 'L08': 1.0, 'L09': 0.5,
        'L01': 1.0, 'L11': 0.5, 'L24': 0.5, 'L12': 0.3,
    },
    'P001': {  # Nam Đình Vũ — river HP, intra-asia feeders
        'L12': 5.0, 'L13': 3.5, 'L19': 3.5, 'L11': 2.5,
        'L14': 1.5, 'L20': 2.0, 'L23': 2.5, 'L25': 1.8,
        'L18': 1.0, 'L21': 1.2, 'L22': 1.2, 'L17': 1.5,
        'L15': 1.0, 'L02': 1.5, 'L01': 0.8, 'L03': 1.5,
        'L04': 2.0, 'L07': 1.2,
    },
    'P007': {  # Nam Đình Vũ GĐ3 (vận hành từ Oct 2025)
        'L12': 3.0, 'L13': 2.0, 'L19': 2.0, 'L11': 2.0,
        'L02': 1.5, 'L01': 1.0, 'L03': 1.5, 'L04': 1.0,
        'L23': 1.0,
    },
    'P002': {  # Nam Hải ICD — barge feeder
        'L12': 3.5, 'L19': 2.5, 'L20': 1.8, 'L13': 1.8,
        'L21': 1.2, 'L22': 1.2, 'L17': 1.0,
    },
    'P003': {  # Dung Quất — bulk, few container
        'L01': 0.4, 'L02': 0.4, 'L03': 0.8, 'L11': 0.8, 'L12': 1.2,
    },
    'P004': {  # Phước Long ICD — mid-stream HCM
        'L11': 3.5, 'L12': 4.5, 'L13': 2.5, 'L17': 2.5, 'L19': 2.5,
        'L20': 1.5, 'L23': 1.8, 'L25': 1.2, 'L18': 1.2,
    },
    'P005': {  # Bình Dương — river, vệ tinh GML
        'L11': 2.5, 'L12': 2.5, 'L13': 2.0, 'L17': 1.5, 'L19': 1.8,
        'L20': 1.2, 'L23': 1.2, 'L18': 1.2, 'L25': 1.0,
    },
}

COMPETITOR_BASE = {
    # CM-TV competitors (deepsea like Gemalink)
    'P010': {  # TCIT — biggest competitor (Tan Cang Cai Mep)
        'L02': 3.0, 'L01': 2.5, 'L03': 2.5, 'L04': 2.0, 'L05': 2.0,
        'L06': 3.5, 'L07': 2.0, 'L08': 2.0, 'L09': 1.8,
        'L10': 1.0, 'L11': 1.5, 'L16': 1.0, 'L24': 1.0,
    },
    'P011': {  # TCCT
        'L02': 1.0, 'L06': 2.0, 'L08': 1.5, 'L09': 1.0,
        'L24': 1.0, 'L11': 1.0, 'L25': 0.5,
    },
    'P012': {  # TCTT
        'L06': 1.5, 'L08': 1.0, 'L09': 1.0, 'L25': 0.5, 'L11': 1.0,
    },
    'P013': {  # CMIT — major
        'L02': 2.0, 'L05': 1.5, 'L01': 2.0, 'L03': 2.0,
        'L10': 1.0, 'L11': 1.0, 'L04': 1.5,
    },
    'P014': {  # SSIT
        'L02': 1.5, 'L01': 1.5, 'L05': 1.0, 'L08': 1.0, 'L03': 1.0,
    },
    'P015': {  # SP-PSA
        'L01': 1.5, 'L02': 1.0, 'L03': 1.0, 'L04': 1.0, 'L07': 0.8,
    },
    # HP competitors
    'P020': {  # Lạch Huyện HIT
        'L02': 1.0, 'L06': 1.0, 'L01': 0.5, 'L05': 0.5,
    },
    'P021': {  # Lạch Huyện HICT (Hateco-Itochu) — major
        'L02': 2.5, 'L06': 2.5, 'L01': 1.5, 'L09': 1.5, 'L03': 1.0, 'L05': 1.0,
    },
    'P022': {  # TC-HICT (Tan Cang)
        'L06': 2.0, 'L08': 1.5, 'L01': 1.0, 'L03': 1.0, 'L09': 1.0,
    },
    'P023': {  # VIP Green — river HP
        'L12': 3.0, 'L19': 2.0, 'L13': 2.0, 'L11': 1.5, 'L21': 1.0, 'L20': 1.0,
    },
    'P024': {  # Nam Hải Đình Vũ — river HP
        'L12': 2.5, 'L19': 2.0, 'L13': 1.5, 'L11': 1.0, 'L23': 1.0,
    },
    'P025': {  # Tân Cảng 128 — river HP
        'L12': 2.0, 'L19': 1.5, 'L13': 1.5, 'L17': 1.0, 'L23': 0.8,
    },
    # HCM
    'P030': {  # Cát Lái — biggest VN
        'L01': 3.5, 'L02': 4.0, 'L03': 3.5, 'L04': 2.5, 'L06': 4.5,
        'L07': 2.5, 'L08': 2.0, 'L09': 1.8, 'L11': 3.5, 'L12': 5.0,
        'L13': 3.5, 'L17': 2.0, 'L18': 1.5, 'L19': 2.5, 'L20': 1.5,
        'L23': 2.5, 'L24': 2.5, 'L25': 1.8, 'L05': 1.8, 'L16': 1.5,
        'L15': 1.0,
    },
    'P031': {  # ICD Transimex
        'L12': 2.0, 'L19': 1.5, 'L17': 1.0, 'L11': 1.0, 'L13': 1.0,
    },
    'P032': {  # ICD Sotrans
        'L12': 1.5, 'L13': 1.0, 'L19': 1.0, 'L17': 1.0, 'L25': 0.8,
    },
}

# =============================================================================
# Anomaly application
# =============================================================================
def maersk_gemalink_decay(month_date):
    """ANOMALY 1: Maersk at Gemalink decreases from Jan 2026 (Wow scenario 2)."""
    if month_date >= date(2026, 1, 1):
        months_in = (month_date.year - 2026) * 12 + (month_date.month - 1)
        # Decay multiplier: Jan=0.78, Feb=0.65, Mar=0.55
        decay = max(0.55, 1.0 - 0.12 * (months_in + 1.5))
        return decay
    return 1.0


def maersk_tcit_boost(month_date):
    """ANOMALY 1 mirror: Maersk at TCIT increases from Jan 2026."""
    if month_date >= date(2026, 1, 1):
        months_in = (month_date.year - 2026) * 12 + (month_date.month - 1)
        boost = 1.0 + 0.4 * (months_in + 1)  # 1.4, 1.8, 2.2
        return min(boost, 2.5)
    return 1.0


def hapag_post_gemini(line_id, port_id, month_date):
    """ANOMALY 3: Hapag-Lloyd at Gemalink increases post-Feb 2025 (Gemini)."""
    if line_id == 'L05' and port_id == 'P006' and month_date >= ALLIANCE_BREAK_DATE:
        return 2.5  # 1.0 -> 2.5/month
    return 1.0


def msc_post_split(line_id, port_id, month_date):
    """ANOMALY 3: MSC at Gemalink ramps up after Mar 2025."""
    if line_id == 'L01' and port_id == 'P006' and month_date >= date(2025, 3, 1):
        months_in = (month_date.year - 2025) * 12 + (month_date.month - 3)
        return min(3.0, 1.0 + 0.2 * months_in)
    return 1.0


def zim_cmtv_ramp(line_id, port_id, month_date):
    """ANOMALY 2: ZIM ramps up at TCIT/CMIT from Oct 2025 (BD opportunity)."""
    if line_id == 'L10' and port_id in ('P010', 'P013') and month_date >= date(2025, 10, 1):
        months_in = (month_date.year - 2025) * 12 + (month_date.month - 10)
        return 2.0 + 0.4 * months_in  # 2x, 2.4x, 2.8x...
    return 1.0


def hmm_tcit_ramp(line_id, port_id, month_date):
    """ANOMALY 2: HMM at TCIT 4→8 over 6 months."""
    if line_id == 'L08' and port_id == 'P010' and month_date >= date(2025, 10, 1):
        months_in = (month_date.year - 2025) * 12 + (month_date.month - 10)
        return min(2.0, 1.0 + 0.2 * months_in)
    return 1.0


def wan_hai_cmtv_ramp(line_id, port_id, month_date):
    """ANOMALY 2: Wan Hai at CM-TV ports ramps up."""
    if line_id == 'L11' and port_id in ('P010', 'P013', 'P011') and month_date >= date(2025, 10, 1):
        months_in = (month_date.year - 2025) * 12 + (month_date.month - 10)
        return min(2.3, 1.0 + 0.25 * months_in)
    return 1.0


def hp_fog_factor(port_id, month_date):
    """Sương mù HP T1-T2 reduces calls."""
    cluster = PORT_INFO[port_id][5]
    if cluster == 'Hải Phòng' and month_date.month in (1, 2):
        return 0.85
    return 1.0


def dung_quat_typhoon(port_id, month_date):
    """Bão Sept 2025 closes Dung Quất 36h → ~10% loss for that month."""
    if port_id == 'P003' and month_date == date(2025, 9, 1):
        return 0.85
    return 1.0


def ndv3_ramp(port_id, month_date):
    """NDV3 starts Oct 2025, ramps up."""
    if port_id == 'P007':
        if month_date < date(2025, 10, 1):
            return 0.0  # not operational
        else:
            months_in = (month_date.year - 2025) * 12 + (month_date.month - 10)
            return min(1.0, 0.3 + 0.15 * months_in)
    return 1.0


def gemalink_phase2a(port_id, month_date):
    """Gemalink P2A trial Mar 2025+ → +10% capacity available."""
    if port_id == 'P006' and month_date >= date(2025, 3, 1):
        return 1.05
    return 1.0


def apply_modifiers(base, line_id, port_id, month_date):
    """Apply all relevant anomaly modifiers."""
    val = base
    val *= MONTHLY_SEASON[month_date.month]
    val *= growth_factor(month_date)
    val *= hp_fog_factor(port_id, month_date)
    val *= dung_quat_typhoon(port_id, month_date)
    val *= ndv3_ramp(port_id, month_date)
    val *= gemalink_phase2a(port_id, month_date)
    val *= hapag_post_gemini(line_id, port_id, month_date)
    val *= msc_post_split(line_id, port_id, month_date)
    val *= zim_cmtv_ramp(line_id, port_id, month_date)
    val *= hmm_tcit_ramp(line_id, port_id, month_date)
    val *= wan_hai_cmtv_ramp(line_id, port_id, month_date)
    if line_id == 'L02' and port_id == 'P006':
        val *= maersk_gemalink_decay(month_date)
    if line_id == 'L02' and port_id == 'P010':
        val *= maersk_tcit_boost(month_date)
    return val


def pick_vessel(line_id, port_id):
    """Pick a vessel from line that fits port DWT capacity."""
    vessels = VESSELS_BY_LINE.get(line_id, [])
    if not vessels:
        return None
    port = PORT_INFO[port_id]
    max_dwt = port[8]
    port_type = port[6]
    candidates = [v for v in vessels if v[5] <= max_dwt]
    if not candidates:
        candidates = vessels  # fallback
    # Prefer larger vessels for deepsea, smaller for river/ICD
    if port_type == 'deepsea':
        candidates = sorted(candidates, key=lambda v: -v[5])[:max(3, len(candidates)//2)]
    elif port_type in ('river','ICD','bulk'):
        candidates = sorted(candidates, key=lambda v: v[5])[:max(3, len(candidates)//2)]
    return random.choice(candidates)


def pick_service(line_id, vessel_size_teu):
    """Pick a service the line operates that matches vessel size context."""
    sids = LINE_TO_SERVICES.get(line_id, [])
    if not sids:
        return None
    # Filter by vessel size: large vessels → long-haul (Asia-Europe/TransPacific/Asia-Americas/Asia-Middle East)
    candidates = []
    for sid in sids:
        s = next((x for x in SERVICES if x[0] == sid), None)
        if s and s[3] in ('Asia-Europe','TransPacific','Asia-Americas','Asia-Middle East'):
            if vessel_size_teu >= 8000:
                candidates.append(sid)
        elif s and s[3] == 'Intra-Asia':
            if vessel_size_teu < 8000:
                candidates.append(sid)
    if not candidates:
        candidates = sids
    return random.choice(candidates)


# Pricing baseline
PORT_BASE_RATE = {
    'deepsea': 1_500_000,
    'river':   850_000,
    'ICD':     550_000,
    'bulk':    700_000,
}
TOP5_LINES = {'L01','L02','L03','L04','L05'}  # MSC, Maersk, CMA, COSCO, Hapag
MEDIUM_LINES = {'L06','L08','L09','L16','L07'}  # ONE, HMM, YM, OOCL, EV


def line_rate_multiplier(line_id):
    if line_id in TOP5_LINES:
        return 0.95
    elif line_id in MEDIUM_LINES:
        return 1.00
    else:
        return 1.05


def gen_pricing_tariff():
    """Generate pricing_tariff: per port × line × period. Deepsea +10% from 2026-02-01."""
    rows = []
    tid = 1
    for port in PORTS:
        port_id = port[0]
        ptype = port[6]
        is_gd = port[3]
        if not is_gd:
            continue  # only Gemadept ports for tariff
        base_rate = PORT_BASE_RATE.get(ptype, 800_000)
        for line in SHIPPING_LINES:
            line_id = line[0]
            mult = line_rate_multiplier(line_id)
            rate1 = int(base_rate * mult)
            # period 1: from 2024-04 to 2026-01-31
            rows.append((f'T{tid:04d}', port_id, line_id, rate1, date(2024,4,1), date(2026,1,31)))
            tid += 1
            # period 2: from 2026-02-01 — deepsea +10%
            rate2 = int(rate1 * (1.10 if ptype == 'deepsea' else 1.0))
            rows.append((f'T{tid:04d}', port_id, line_id, rate2, date(2026,2,1), None))
            tid += 1
    return rows


# =============================================================================
# Generate calls
# =============================================================================
def random_dt_in_month(month_date):
    """Pick a random datetime within the given month."""
    dim = days_in_month(month_date)
    day = random.randint(1, dim)
    hour = random.randint(0, 23)
    minute = random.choice([0, 15, 30, 45])
    return datetime(month_date.year, month_date.month, day, hour, minute)


def teu_per_call(port_type, vessel_teu):
    """How many TEU handled in this call (load+discharge+transship)."""
    # Utilization ~25-45% of vessel capacity per call
    if port_type == 'deepsea':
        util = random.uniform(0.30, 0.50)
    elif port_type == 'river':
        util = random.uniform(0.55, 0.80)
    elif port_type == 'ICD':
        util = random.uniform(0.60, 0.85)
    else:
        util = random.uniform(0.40, 0.65)
    return int(vessel_teu * util * random.uniform(0.85, 1.15))


def gen_port_calls():
    """Internal Gemadept port_calls."""
    rows = []
    cid = 1
    for port_id, line_map in GEMADEPT_BASE.items():
        port = PORT_INFO[port_id]
        ptype = port[6]
        for line_id, base in line_map.items():
            for month in MONTHS:
                expected = apply_modifiers(base, line_id, port_id, month)
                expected *= random.uniform(0.85, 1.15)  # noise
                # convert to integer count (Poisson-ish)
                n_calls = max(0, int(round(expected)))
                if n_calls == 0 and expected > 0.3:
                    n_calls = 1 if random.random() < expected else 0
                for _ in range(n_calls):
                    vessel = pick_vessel(line_id, port_id)
                    if not vessel:
                        continue
                    eta = random_dt_in_month(month)
                    # ETB ~2-8h after ETA, ETD ~24-72h after ETB depending on port type
                    etb = eta + timedelta(hours=random.uniform(2, 8))
                    if ptype == 'deepsea':
                        etd_offset_h = random.uniform(36, 96)
                    elif ptype == 'river':
                        etd_offset_h = random.uniform(20, 60)
                    elif ptype == 'ICD':
                        etd_offset_h = random.uniform(12, 36)
                    else:
                        etd_offset_h = random.uniform(48, 120)
                    etd = etb + timedelta(hours=etd_offset_h)
                    # Actuals: usually within ±6h of estimates (occasional weather delays)
                    delay_h = random.uniform(-2, 6)
                    if PORT_INFO[port_id][5] == 'Hải Phòng' and month.month in (1,2):
                        delay_h += random.uniform(0, 12)  # fog
                    if port_id == 'P003' and month == date(2025,9,1):
                        delay_h += random.uniform(0, 24)
                    ata = eta + timedelta(hours=delay_h)
                    atb = etb + timedelta(hours=delay_h)
                    atd = etd + timedelta(hours=delay_h * 0.6)
                    teu_total = teu_per_call(ptype, vessel[6])
                    teu_disc = int(teu_total * random.uniform(0.40, 0.55))
                    teu_load = int(teu_total * random.uniform(0.40, 0.55))
                    teu_trans = max(0, teu_total - teu_disc - teu_load)
                    voyage_no = f'{vessel[1][:3].replace(" ","")}{random.randint(100,999)}{random.choice("NSEW")}'
                    service_id = pick_service(line_id, vessel[6])
                    berth_id = f'B{random.randint(1, 8):02d}'
                    dwell = (atd - atb).total_seconds() / 3600.0
                    # Revenue: rate × teu_total + reefer + VAS
                    base_rate = PORT_BASE_RATE.get(ptype, 800_000) * line_rate_multiplier(line_id)
                    if month >= date(2026,2,1) and ptype == 'deepsea':
                        base_rate *= 1.10
                    revenue_thc = int(base_rate * teu_total)
                    reefer_teu = int(teu_total * random.uniform(0.05, 0.12))
                    vas_revenue = int(revenue_thc * random.uniform(0.08, 0.18))
                    revenue_total = revenue_thc + vas_revenue
                    cost = int(revenue_total * random.uniform(0.55, 0.70))
                    rows.append((
                        f'PC{cid:06d}', port_id, vessel[0], voyage_no, service_id, line_id,
                        eta, etb, etd, ata, atb, atd, berth_id,
                        teu_disc, teu_load, teu_trans, teu_total, round(dwell,2),
                        revenue_total, cost, reefer_teu, vas_revenue
                    ))
                    cid += 1
    return rows


def gen_external_schedule(port_calls):
    """External schedule: mirror port_calls for Gemadept ports + generate competitor schedule."""
    rows = []
    sid = 1
    # 1. Mirror Gemadept calls (5% missed)
    for pc in port_calls:
        if random.random() < 0.05:
            continue
        # capacity_est ≈ vessel_teu_capacity (lookup)
        vessel = next((v for v in VESSELS if v[0] == pc[2]), None)
        teu_cap = vessel[6] if vessel else None
        # source by region
        port = PORT_INFO[pc[1]]
        cluster = port[5]
        if cluster == 'Hải Phòng':
            src = 'cangvuhaiphong'
        elif cluster == 'CM-TV':
            src = 'cangvuvungtau'
        elif cluster in ('HCM', 'Miền Trung'):
            src = 'cangvuhcm' if cluster == 'HCM' else 'cangvuquynhon'
        else:
            src = 'cangvuhcm'
        rows.append((
            f'SE{sid:06d}', pc[1], pc[2], pc[5], pc[6], pc[8], pc[4],  # port_id, vessel, line, eta, etd, service
            teu_cap, src
        ))
        sid += 1
    # 2. Generate competitor schedule
    for port_id, line_map in COMPETITOR_BASE.items():
        port = PORT_INFO[port_id]
        ptype = port[6]
        cluster = port[5]
        if cluster == 'Hải Phòng':
            src = 'cangvuhaiphong'
        elif cluster == 'CM-TV':
            src = 'cangvuvungtau'
        else:
            src = 'cangvuhcm'
        for line_id, base in line_map.items():
            for month in MONTHS:
                expected = apply_modifiers(base, line_id, port_id, month)
                expected *= random.uniform(0.85, 1.15)
                n_calls = max(0, int(round(expected)))
                if n_calls == 0 and expected > 0.3:
                    n_calls = 1 if random.random() < expected else 0
                for _ in range(n_calls):
                    vessel = pick_vessel(line_id, port_id)
                    if not vessel:
                        continue
                    eta = random_dt_in_month(month)
                    if ptype == 'deepsea':
                        etd = eta + timedelta(hours=random.uniform(40, 100))
                    elif ptype == 'river':
                        etd = eta + timedelta(hours=random.uniform(24, 60))
                    else:
                        etd = eta + timedelta(hours=random.uniform(16, 40))
                    service_id = pick_service(line_id, vessel[6])
                    rows.append((
                        f'SE{sid:06d}', port_id, vessel[0], line_id, eta, etd, service_id,
                        vessel[6], src
                    ))
                    sid += 1
    return rows


def gen_daily_stats(port_calls):
    """Aggregate daily port stats from port_calls."""
    by_pd = defaultdict(lambda: {'teu':0,'calls':0,'rev':0,'lines':set()})
    for pc in port_calls:
        d = pc[6].date() if isinstance(pc[6], datetime) else pc[6]
        key = (pc[1], d)
        by_pd[key]['teu'] += pc[16]
        by_pd[key]['calls'] += 1
        by_pd[key]['rev'] += pc[18]
        by_pd[key]['lines'].add(pc[5])
    rows = []
    sid = 1
    for (pid, d), v in sorted(by_pd.items()):
        rows.append((f'DS{sid:06d}', pid, d, v['teu'], v['calls'], v['rev'], len(v['lines'])))
        sid += 1
    return rows


# =============================================================================
# WRITE TRANSACTION SQL
# =============================================================================
def write_transactions(port_calls, external, daily, tariff):
    path = os.path.join(SQL_DIR, '04_transaction_data.sql')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(f"-- 04_transaction_data.sql | Database: {DB_NAME}\n")
        f.write(f"-- port_calls: {len(port_calls)}, external_schedule: {len(external)}, daily_stats: {len(daily)}, tariff: {len(tariff)}\n\n")
        f.write(f"USE `{DB_NAME}`;\n\n")
        f.write("SET autocommit=0;\n")
        f.write("SET unique_checks=0;\n")
        f.write("SET foreign_key_checks=0;\n\n")

        write_inserts(f, 'port_calls',
                      ['call_id','port_id','vessel_id','voyage_no','service_id','shipping_line_id',
                       'eta','etb','etd','ata','atb','atd','berth_id',
                       'teu_discharged','teu_loaded','teu_transshipment','total_teu_handled',
                       'dwell_time_hours','revenue_vnd','cost_vnd','reefer_teu','vas_revenue_vnd'],
                      port_calls)

        write_inserts(f, 'port_vessel_schedule_external',
                      ['schedule_id','port_id','vessel_id','shipping_line_id','eta','etd',
                       'service_id','teu_capacity_est','source'],
                      external)

        write_inserts(f, 'daily_port_stats',
                      ['stat_id','port_id','stat_date','total_teu','total_calls',
                       'total_revenue_vnd','unique_lines_count'],
                      daily)

        write_inserts(f, 'pricing_tariff',
                      ['tariff_id','port_id','line_id','rate_per_teu_vnd','effective_from','effective_to'],
                      tariff)

        f.write("SET foreign_key_checks=1;\n")
        f.write("SET unique_checks=1;\n")
        f.write("COMMIT;\n")
    print(f"Wrote {path} ({os.path.getsize(path):,} bytes)")


# =============================================================================
# PHASE D — METADATA
# =============================================================================
META_TABLES = [
    ('ports', 'Danh sách cảng biển/ICD liên quan: Gemadept và đối thủ',
     'Catalog of ports/ICDs: Gemadept ports + competitors',
     'Phân biệt qua is_gemadept. Cluster gồm: Hải Phòng, CM-TV (Cái Mép-Thị Vải), HCM, Miền Trung.', 'Internal'),
    ('shipping_lines', '25 hãng tàu container hoạt động tại VN — top 10 global + regional',
     '25 container shipping lines active in VN — top 10 global + regional',
     'Bao gồm fleet size, ranking toàn cầu. Dùng để cross-reference với alliance_membership_history.', 'Internal/Linerlytica'),
    ('alliances', '7 liên minh: 3 cũ (giải thể 1/2025) + 4 mới (từ 2/2025)',
     '7 alliances: 3 legacy (dissolved Jan 2025) + 4 current (since Feb 2025)',
     'Tái cấu trúc 2/2025: 2M tan rã, THE Alliance → Premier, Ocean Alliance gia hạn, Gemini ra đời, MSC standalone.', 'Industry'),
    ('alliance_membership_history', 'Lịch sử thành viên liên minh — line × alliance × period',
     'Membership history — line × alliance × period',
     'Critical cho phân tích trước/sau Feb 2025. Một line có thể thuộc nhiều alliance trong các thời kỳ khác nhau.', 'Industry'),
    ('vessels', '~120 tàu container thực tế đang hoạt động tuyến VN',
     '~120 real container vessels operating VN routes',
     'Mega ≥200k DWT (chỉ Gemalink đón được), large 100-200k, medium 50-100k, feeder <50k.', 'Internal/IMO'),
    ('services', '30 tuyến dịch vụ container có ghé VN',
     '30 container services calling VN ports',
     'Bao gồm tên dịch vụ thật (FE1, EC5, AE1, Tropic, ZX2), trade lane, port rotation, alliance vận hành.', 'Industry'),
    ('news_events', '~60 sự kiện ngành 2024-2026 ảnh hưởng đến hoạt động cảng',
     '~60 industry events 2024-2026 affecting port operations',
     'Categories: alliance, route, regulation, tariff, weather, competitor. Chứa thông tin Feb 2025 reshuffle, Feb 2026 price hike, Trump tariff.', 'Phaata/Vietstock/Lloyd List'),
    ('customers_shippers', '45 shipper/khách hàng XNK lớn dùng dịch vụ cảng',
     '45 large shippers/customers using port services',
     'Industry: Electronics, Apparel, Textile, Steel, Furniture, Seafood... primary_region cho biết miền chính.', 'Internal CRM'),
    ('port_calls', 'Transaction-level: mỗi lần tàu cập cảng Gemadept (2024-04 → 2026-03)',
     'Transaction-level: every vessel call at Gemadept ports (2024-04 to 2026-03)',
     'Grain: 1 row = 1 port call. Bao gồm ETA/ETB/ETD + ATA/ATB/ATD, TEU handled, revenue, cost.', 'Internal SmartPort/CATOS'),
    ('daily_port_stats', 'Aggregated daily — fast query cho dashboard',
     'Daily aggregated stats for dashboard fast queries',
     'Chỉ Gemadept ports. Có total_teu, total_calls, total_revenue_vnd, unique_lines_count.', 'Internal (derived from port_calls)'),
    ('port_vessel_schedule_external', 'Lịch tàu CÔNG KHAI từ cảng vụ — TẤT CẢ cảng (Gemadept + đối thủ)',
     'Public vessel schedule from Cảng Vụ — ALL ports (Gemadept + competitors)',
     'CRITICAL cho cross-reference. Chứa data đối thủ. Source: cangvuhaiphong, cangvuvungtau, cangvuhcm.', 'Public — Cảng Vụ'),
    ('pricing_tariff', 'Giá sàn xếp dỡ theo cảng × hãng × thời kỳ',
     'Stevedoring tariff by port × line × period',
     'Top 5 line: 0.95×base, Medium: 1.00×, Small: 1.05×. Deepsea +10% từ 2026-02-01 (QĐ 810 sửa đổi).', 'Internal'),
]

META_COLUMNS = [
    # ports
    ('ports','port_id','VARCHAR','Mã cảng','Port ID','-','P006'),
    ('ports','port_name','VARCHAR','Tên cảng','Port name','-','Gemalink'),
    ('ports','is_gemadept','TINYINT','1 nếu là cảng Gemadept','1 if Gemadept-operated','-','0/1'),
    ('ports','cluster','VARCHAR','Cụm cảng','Port cluster','-','Hải Phòng / CM-TV / HCM / Miền Trung'),
    ('ports','port_type','VARCHAR','Loại cảng','Port type','-','deepsea / river / ICD / bulk'),
    ('ports','capacity_teu_year','INT','Công suất TEU/năm','Annual capacity','TEU','1500000'),
    ('ports','max_dwt','INT','DWT tối đa tàu cập được','Max DWT vessel','DWT','250000'),
    # shipping_lines
    ('shipping_lines','line_id','VARCHAR','Mã hãng','Line ID','-','L02'),
    ('shipping_lines','line_name','VARCHAR','Tên hãng','Line name','-','Maersk'),
    ('shipping_lines','line_code','VARCHAR','Code SCAC','SCAC code','-','MAEU'),
    ('shipping_lines','fleet_capacity_teu','INT','Tổng TEU đội tàu hãng','Fleet TEU capacity','TEU','4300000'),
    ('shipping_lines','global_rank','INT','Xếp hạng toàn cầu','Global ranking','-','2'),
    # alliances
    ('alliances','alliance_id','VARCHAR','Mã liên minh','Alliance ID','-','A04'),
    ('alliances','alliance_name','VARCHAR','Tên liên minh','Alliance name','-','Gemini Cooperation'),
    ('alliances','formed_date','DATE','Ngày thành lập','Formation date','-','2025-02-01'),
    ('alliances','dissolved_date','DATE','Ngày giải thể (NULL nếu còn hoạt động)','Dissolution date (NULL if active)','-','2025-01-31'),
    ('alliances','status','VARCHAR','Trạng thái','Status','-','active / dissolved / restructured'),
    # alliance_membership_history
    ('alliance_membership_history','line_id','VARCHAR','Mã hãng','Line ID','-','L02'),
    ('alliance_membership_history','alliance_id','VARCHAR','Mã liên minh','Alliance ID','-','A04'),
    ('alliance_membership_history','from_date','DATE','Ngày bắt đầu','Start date','-','2025-02-01'),
    ('alliance_membership_history','to_date','DATE','Ngày kết thúc (NULL = current)','End date','-','NULL'),
    # vessels
    ('vessels','vessel_id','VARCHAR','Mã tàu','Vessel ID','-','V001'),
    ('vessels','vessel_name','VARCHAR','Tên tàu','Vessel name','-','MSC GULSUN'),
    ('vessels','imo_number','INT','Số IMO','IMO number','-','9839272'),
    ('vessels','dwt','INT','Trọng tải tàu','Deadweight tonnage','DWT','225720'),
    ('vessels','teu_capacity','INT','Sức chứa TEU','TEU capacity','TEU','23756'),
    ('vessels','vessel_type','VARCHAR','Phân loại','Vessel class','-','mega / large / medium / feeder'),
    # services
    ('services','service_name','VARCHAR','Tên tuyến','Service name','-','FE1 - Far East Europe 1'),
    ('services','trade_lane','VARCHAR','Tuyến chính','Trade lane','-','Asia-Europe / TransPacific / Intra-Asia / Asia-Middle East / Asia-Americas'),
    ('services','frequency_weekly','INT','Tần suất chuyến/tuần','Weekly frequency','calls/week','1'),
    ('services','port_rotation','TEXT','Chuỗi cảng ghé','Port rotation sequence','-','Ningbo-Shanghai-Yantian-Singapore-Gemalink-...'),
    # news_events
    ('news_events','event_date','DATE','Ngày sự kiện','Event date','-','2025-02-01'),
    ('news_events','category','VARCHAR','Phân loại','Category','-','alliance / route / regulation / tariff / weather / competitor'),
    ('news_events','sentiment','VARCHAR','Tác động tới cảng VN','Sentiment for VN ports','-','positive / negative / neutral'),
    ('news_events','affected_lines','JSON','JSON array các line_id bị ảnh hưởng','JSON line_id array','-','["L02","L05"]'),
    ('news_events','affected_ports','JSON','JSON array port_id bị ảnh hưởng','JSON port_id array','-','["P006","P010"]'),
    # port_calls
    ('port_calls','call_id','VARCHAR','Mã port call','Port call ID','-','PC000123'),
    ('port_calls','eta','DATETIME','Giờ dự kiến tàu đến','Estimated time of arrival','-','2026-01-15 06:30:00'),
    ('port_calls','etb','DATETIME','Giờ dự kiến cập bến','Estimated time of berthing','-','2026-01-15 09:00:00'),
    ('port_calls','etd','DATETIME','Giờ dự kiến tàu rời','Estimated time of departure','-','2026-01-17 14:00:00'),
    ('port_calls','ata','DATETIME','Giờ thực tế tàu đến','Actual time of arrival','-','2026-01-15 07:15:00'),
    ('port_calls','total_teu_handled','INT','Tổng TEU bốc dỡ + transship','Total TEU handled','TEU','8500'),
    ('port_calls','teu_discharged','INT','TEU dỡ xuống','TEU discharged','TEU','3800'),
    ('port_calls','teu_loaded','INT','TEU bốc lên','TEU loaded','TEU','3700'),
    ('port_calls','teu_transshipment','INT','TEU trung chuyển','Transshipment TEU','TEU','1000'),
    ('port_calls','dwell_time_hours','DECIMAL','Thời gian tàu nằm bến (giờ)','Dwell time hours','hours','45.5'),
    ('port_calls','revenue_vnd','BIGINT','Doanh thu (VND) — THC + VAS','Revenue VND','VND','12750000000'),
    ('port_calls','reefer_teu','INT','TEU lạnh','Reefer TEU','TEU','680'),
    ('port_calls','vas_revenue_vnd','BIGINT','Doanh thu Value-Added Service','VAS revenue','VND','1500000000'),
    # external schedule
    ('port_vessel_schedule_external','source','VARCHAR','Nguồn data cảng vụ','Source','-','cangvuhaiphong / cangvuvungtau / cangvuhcm'),
    ('port_vessel_schedule_external','teu_capacity_est','INT','Sức chứa TEU ước tính','Estimated TEU capacity','TEU','15000'),
    # pricing
    ('pricing_tariff','rate_per_teu_vnd','INT','Giá xếp dỡ/TEU','Rate per TEU','VND','1500000'),
    ('pricing_tariff','effective_from','DATE','Hiệu lực từ','Effective from','-','2026-02-01'),
    ('pricing_tariff','effective_to','DATE','Hiệu lực đến (NULL = hiện hành)','Effective to (NULL = current)','-','NULL'),
    # daily stats
    ('daily_port_stats','total_teu','INT','Tổng TEU trong ngày','Daily total TEU','TEU','12500'),
    ('daily_port_stats','total_calls','INT','Số call trong ngày','Daily call count','-','3'),
    ('daily_port_stats','unique_lines_count','INT','Số hãng khác nhau trong ngày','Distinct lines count','-','3'),
]

META_KPI = [
    ('TEU Throughput',
     "SELECT SUM(total_teu_handled) FROM port_calls WHERE eta BETWEEN ? AND ?",
     'Tổng TEU thông qua cảng (load + discharge + transshipment)',
     'Câu 1, 2, 5'),
    ('TEU Throughput by Alliance',
     "SELECT a.alliance_name, SUM(pc.total_teu_handled) FROM port_calls pc JOIN alliance_membership_history m ON m.line_id=pc.shipping_line_id AND m.from_date<=DATE(pc.eta) AND (m.to_date IS NULL OR m.to_date>=DATE(pc.eta)) JOIN alliances a ON m.alliance_id=a.alliance_id GROUP BY a.alliance_name",
     'TEU theo liên minh hãng tàu (theo thời điểm) — quan trọng cho phân tích trước/sau Feb 2025',
     'Câu 1, 5'),
    ('TEU Throughput by Line',
     "SELECT shipping_line_id, SUM(total_teu_handled) FROM port_calls GROUP BY shipping_line_id",
     'TEU theo hãng tàu',
     'Câu 1, 2, 6'),
    ('Port Call Frequency',
     "SELECT port_id, shipping_line_id, COUNT(*) FROM port_calls GROUP BY port_id, shipping_line_id",
     'Số lần tàu cập cảng theo hãng',
     'Câu 2, 3, 4'),
    ('Market Share within Cluster',
     "WITH cluster_total AS (SELECT p.cluster, SUM(pvs.teu_capacity_est) total FROM port_vessel_schedule_external pvs JOIN ports p ON pvs.port_id=p.port_id GROUP BY p.cluster) SELECT pvs.port_id, p.port_name, SUM(pvs.teu_capacity_est)/ct.total*100 share FROM port_vessel_schedule_external pvs JOIN ports p ON pvs.port_id=p.port_id JOIN cluster_total ct ON p.cluster=ct.cluster GROUP BY pvs.port_id",
     'Thị phần TEU ước tính trong cụm cảng (Gemalink trong CM-TV...)',
     'Câu 3'),
    ('Wallet Share per Line',
     "SELECT pc.shipping_line_id, SUM(pc.total_teu_handled) gemadept_teu, (SELECT SUM(pvs.teu_capacity_est) FROM port_vessel_schedule_external pvs WHERE pvs.shipping_line_id=pc.shipping_line_id) total_vn_capacity FROM port_calls pc GROUP BY pc.shipping_line_id",
     '% sản lượng VN của hãng đi qua Gemadept',
     'Câu 4, 6'),
    ('BD Opportunity Gap',
     "WITH cm_tv AS (SELECT pvs.shipping_line_id, COUNT(*) c FROM port_vessel_schedule_external pvs JOIN ports p ON pvs.port_id=p.port_id WHERE p.cluster='CM-TV' AND p.port_name<>'Gemalink' AND eta>=DATE_SUB(CURDATE(),INTERVAL 6 MONTH) GROUP BY pvs.shipping_line_id), gml AS (SELECT shipping_line_id, COUNT(*) c FROM port_calls WHERE port_id='P006' AND eta>=DATE_SUB(CURDATE(),INTERVAL 6 MONTH) GROUP BY shipping_line_id) SELECT cm_tv.shipping_line_id, cm_tv.c-COALESCE(gml.c,0) gap FROM cm_tv LEFT JOIN gml USING(shipping_line_id) ORDER BY gap DESC",
     'Gap port_call: hãng đang ghé CM-TV nhưng ít/không ghé Gemalink',
     'Câu 4'),
    ('Revenue THC',
     "SELECT SUM(revenue_vnd-vas_revenue_vnd) FROM port_calls",
     'Doanh thu xếp dỡ (THC) — không tính VAS',
     'Câu 7, 8'),
    ('Total Revenue',
     "SELECT SUM(revenue_vnd) FROM port_calls",
     'Tổng doanh thu (THC + VAS)',
     'Câu 1, 6, 7'),
    ('Gross Margin',
     "SELECT (SUM(revenue_vnd)-SUM(cost_vnd))/SUM(revenue_vnd)*100 FROM port_calls",
     'Biên lợi nhuận gộp — Gemalink target ~44%',
     'Câu 6, 7'),
    ('Reefer Mix',
     "SELECT SUM(reefer_teu)/SUM(total_teu_handled)*100 FROM port_calls",
     '% TEU lạnh trong tổng TEU',
     'Operational'),
    ('Avg Dwell Time',
     "SELECT AVG(dwell_time_hours) FROM port_calls",
     'Thời gian tàu nằm bến trung bình (giờ)',
     'Operational efficiency'),
]

META_GLOSSARY = [
    ('TEU','Twenty-foot Equivalent Unit','Đơn vị quy đổi 1 container 20 feet. Tàu mega có sức chứa 23k TEU.','vessels, port_calls'),
    ('DWT','Deadweight Tonnage','Trọng tải toàn phần tàu (tonne). Gemalink đón tàu tới 250k DWT.','vessels, ports'),
    ('Port Call','Vessel Port Call','Một lần tàu cập cảng để xếp dỡ.','port_calls, port_vessel_schedule_external'),
    ('THC','Terminal Handling Charge','Phí xếp dỡ tại cảng — chiếm 60-70% doanh thu cảng.','pricing_tariff, port_calls.revenue_vnd'),
    ('VAS','Value-Added Service','Dịch vụ giá trị gia tăng (CFS, đóng rút cont, reefer monitoring).','port_calls.vas_revenue_vnd'),
    ('Liên minh hãng tàu','Shipping Alliance','Nhóm các hãng chia sẻ slot/space, phối hợp lịch trình. Tái cấu trúc 2/2025.','alliances, alliance_membership_history'),
    ('Gemini Cooperation','Gemini Cooperation','Liên minh mới Maersk + Hapag-Lloyd, từ 2/2025, mô hình hub-and-spoke. TCIT là hub VN.','alliances'),
    ('Premier Alliance','Premier Alliance','Liên minh ONE+HMM+YM từ 2/2025 (tái cấu trúc từ THE Alliance).','alliances'),
    ('Ocean Alliance','Ocean Alliance','CMA CGM+COSCO+EV+OOCL — gia hạn đến 2032. Lớn nhất toàn cầu.','alliances'),
    ('CM-TV','Cái Mép - Thị Vải','Cụm cảng nước sâu BRVT — gồm Gemalink, TCIT, CMIT, SSIT, SP-PSA, TCCT, TCTT.','ports.cluster'),
    ('ICD','Inland Container Depot','Cảng cạn — depot container nội địa.','ports.port_type'),
    ('Hub-and-spoke','Hub-and-spoke model','Mô hình tàu mẹ chỉ ghé 1-2 hub chính, feeder phân phối tới các port phụ.','services'),
    ('Cảng vụ','Maritime Administration','Cơ quan quản lý nhà nước về hàng hải, công bố lịch tàu công khai.','port_vessel_schedule_external.source'),
    ('Trade lane','Trade Lane','Tuyến thương mại chính: Asia-Europe, TransPacific, Intra-Asia, Asia-Middle East, Asia-Americas.','services.trade_lane'),
    ('Pareto 80/20','80/20 Rule','Top 5 hãng tàu chiếm ~72% sản lượng Gemadept.','port_calls'),
    ('SAIDI','-','Không áp dụng cho ngành cảng.','-'),
    ('Reefer','Reefer Container','Container lạnh dùng cho hàng đông lạnh.','port_calls.reefer_teu'),
    ('Megaship','Mega Vessel','Tàu container ≥ 18,000 TEU. Chỉ Gemalink ở VN đón được megaship 250k DWT.','vessels.vessel_type'),
]


def write_metadata():
    path = os.path.join(SQL_DIR, '02_metadata.sql')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(f"-- 02_metadata.sql | Database: {DB_NAME}\n")
        f.write("-- Metadata for AI engine via MCP: tables, columns, KPI, glossary\n\n")
        f.write(f"USE `{DB_NAME}`;\n\n")
        write_inserts(f, '_meta_tables',
                      ['table_name','description_vi','description_en','business_context','data_source'],
                      META_TABLES)
        write_inserts(f, '_meta_columns',
                      ['table_name','column_name','data_type','description_vi','description_en','unit','example_values'],
                      META_COLUMNS)
        write_inserts(f, '_meta_kpi',
                      ['kpi_name','formula_sql','description_vi','related_questions'],
                      META_KPI)
        write_inserts(f, '_meta_glossary',
                      ['term_vi','term_en','definition','related_tables'],
                      META_GLOSSARY)
    print(f"Wrote {path}")


# =============================================================================
# 05_validation_queries.sql
# =============================================================================
VALIDATION_SQL = f"""-- 05_validation_queries.sql | Database: {DB_NAME}
-- 8 demo scenario dry-runs + magnitude/integrity checks
USE `{DB_NAME}`;

-- ===========================================================================
-- TECHNICAL CHECKS
-- ===========================================================================
-- TC-1: Row counts
SELECT 'ports' tbl, COUNT(*) n FROM ports
UNION ALL SELECT 'shipping_lines', COUNT(*) FROM shipping_lines
UNION ALL SELECT 'alliances', COUNT(*) FROM alliances
UNION ALL SELECT 'alliance_membership_history', COUNT(*) FROM alliance_membership_history
UNION ALL SELECT 'vessels', COUNT(*) FROM vessels
UNION ALL SELECT 'services', COUNT(*) FROM services
UNION ALL SELECT 'news_events', COUNT(*) FROM news_events
UNION ALL SELECT 'customers_shippers', COUNT(*) FROM customers_shippers
UNION ALL SELECT 'port_calls', COUNT(*) FROM port_calls
UNION ALL SELECT 'port_vessel_schedule_external', COUNT(*) FROM port_vessel_schedule_external
UNION ALL SELECT 'daily_port_stats', COUNT(*) FROM daily_port_stats
UNION ALL SELECT 'pricing_tariff', COUNT(*) FROM pricing_tariff;

-- TC-2: Referential integrity
SELECT 'orphan_port_calls_port' anomaly, COUNT(*) cnt FROM port_calls pc LEFT JOIN ports p ON pc.port_id=p.port_id WHERE p.port_id IS NULL
UNION ALL SELECT 'orphan_port_calls_vessel', COUNT(*) FROM port_calls pc LEFT JOIN vessels v ON pc.vessel_id=v.vessel_id WHERE v.vessel_id IS NULL
UNION ALL SELECT 'orphan_port_calls_line', COUNT(*) FROM port_calls pc LEFT JOIN shipping_lines sl ON pc.shipping_line_id=sl.line_id WHERE sl.line_id IS NULL;

-- TC-3: Business logic (eta < etb < etd)
SELECT 'eta_etb_violation' anomaly, COUNT(*) cnt FROM port_calls WHERE eta >= etb
UNION ALL SELECT 'etb_etd_violation', COUNT(*) FROM port_calls WHERE etb >= etd
UNION ALL SELECT 'teu_negative', COUNT(*) FROM port_calls WHERE total_teu_handled <= 0
UNION ALL SELECT 'revenue_negative', COUNT(*) FROM port_calls WHERE revenue_vnd <= 0;

-- ===========================================================================
-- STATISTICAL — magnitude + Pareto + seasonality
-- ===========================================================================
-- ST-1: Annual TEU magnitude
SELECT YEAR(eta) yr, FORMAT(SUM(total_teu_handled),0) total_teu,
       COUNT(*) calls, FORMAT(SUM(revenue_vnd)/1e9,1) revenue_bil_vnd
FROM port_calls GROUP BY yr;
-- Expect 2024 (9mo): ~3-4M TEU, 2025: ~5-6M, 2026 (3mo): ~1-1.5M

-- ST-2: Monthly trend (seasonality check — Tết trough Jan-Feb, peak Sep-Oct)
SELECT DATE_FORMAT(eta,'%Y-%m') mo, SUM(total_teu_handled) teu
FROM port_calls GROUP BY mo ORDER BY mo;

-- ST-3: Pareto top 5 lines at Gemalink (target ~72%)
WITH line_teu AS (
  SELECT sl.line_name, SUM(pc.total_teu_handled) teu
  FROM port_calls pc JOIN shipping_lines sl ON pc.shipping_line_id=sl.line_id
  WHERE pc.port_id='P006'
  GROUP BY sl.line_name
)
SELECT line_name, FORMAT(teu,0) teu,
       ROUND(100*teu/SUM(teu) OVER (),1) pct,
       ROUND(100*SUM(teu) OVER (ORDER BY teu DESC) / SUM(teu) OVER (),1) cum_pct
FROM line_teu ORDER BY teu DESC LIMIT 8;

-- ===========================================================================
-- DEMO SCENARIO DRY-RUNS
-- ===========================================================================

-- ===== Scenario 1: Mar 2026 by line+alliance, vs Mar 2025 =====
SELECT YEAR(pc.eta) yr, sl.line_name,
       a.alliance_name AS alliance_then,
       SUM(pc.total_teu_handled) teu, COUNT(*) calls
FROM port_calls pc
JOIN shipping_lines sl ON pc.shipping_line_id=sl.line_id
LEFT JOIN alliance_membership_history m
  ON m.line_id=pc.shipping_line_id
  AND m.from_date<=DATE(pc.eta)
  AND (m.to_date IS NULL OR m.to_date>=DATE(pc.eta))
LEFT JOIN alliances a ON m.alliance_id=a.alliance_id
WHERE MONTH(pc.eta)=3 AND YEAR(pc.eta) IN (2025, 2026)
GROUP BY yr, sl.line_name, a.alliance_name
ORDER BY sl.line_name, yr;

-- ===== Scenario 2 (WOW): Maersk @ Gemalink decline + TCIT increase =====
SELECT 'INTERNAL Gemalink' src, DATE_FORMAT(eta,'%Y-%m') mo,
       COUNT(*) calls, SUM(total_teu_handled) teu
FROM port_calls pc JOIN shipping_lines sl ON pc.shipping_line_id=sl.line_id
WHERE sl.line_name='Maersk' AND pc.port_id='P006' AND eta>='2025-07-01'
GROUP BY mo
UNION ALL
SELECT 'EXTERNAL TCIT' src, DATE_FORMAT(eta,'%Y-%m') mo,
       COUNT(*) calls, SUM(teu_capacity_est) teu
FROM port_vessel_schedule_external pvs
JOIN shipping_lines sl ON pvs.shipping_line_id=sl.line_id
WHERE sl.line_name='Maersk' AND pvs.port_id='P010' AND eta>='2025-07-01'
GROUP BY mo
ORDER BY src, mo;
-- Expect: Gemalink Maersk drops from 4→2 calls Q1 2026, TCIT rises from 4→8

-- News context for scenario 2
SELECT event_date, title_vi, source FROM news_events
WHERE event_date BETWEEN '2024-06-01' AND '2026-03-31'
  AND (JSON_CONTAINS(affected_lines, '"L02"') OR JSON_CONTAINS(affected_lines, '"L05"'))
  AND category IN ('alliance','route','competitor')
ORDER BY event_date;

-- ===== Scenario 3: CM-TV competitive (Gemalink vs others, vessels >50k DWT) =====
SELECT p.port_name, COUNT(*) port_calls,
       SUM(v.teu_capacity) total_teu_capacity,
       AVG(v.dwt) avg_dwt
FROM port_vessel_schedule_external pvs
JOIN ports p ON pvs.port_id=p.port_id
JOIN vessels v ON pvs.vessel_id=v.vessel_id
WHERE p.cluster='CM-TV' AND v.dwt>=50000
  AND eta>='2025-10-01'
GROUP BY p.port_name ORDER BY 2 DESC;

-- ===== Scenario 4: BD opportunity — lines at CM-TV not at Gemalink =====
WITH cm_tv_calls AS (
  SELECT pvs.shipping_line_id, sl.line_name, COUNT(*) calls_cm_tv
  FROM port_vessel_schedule_external pvs
  JOIN shipping_lines sl ON pvs.shipping_line_id=sl.line_id
  JOIN ports p ON pvs.port_id=p.port_id
  WHERE p.cluster='CM-TV' AND p.port_name<>'Gemalink'
    AND eta>='2025-10-01'
  GROUP BY pvs.shipping_line_id, sl.line_name
),
gml AS (
  SELECT shipping_line_id, COUNT(*) calls_gml FROM port_calls
  WHERE port_id='P006' AND eta>='2025-10-01'
  GROUP BY shipping_line_id
)
SELECT c.line_name, c.calls_cm_tv, COALESCE(g.calls_gml,0) calls_gml,
       c.calls_cm_tv-COALESCE(g.calls_gml,0) gap
FROM cm_tv_calls c LEFT JOIN gml g USING(shipping_line_id)
WHERE c.calls_cm_tv>=8
ORDER BY gap DESC LIMIT 8;

-- News context for ZIM/Wan Hai
SELECT event_date, title_vi FROM news_events
WHERE (JSON_CONTAINS(affected_lines,'"L10"') OR JSON_CONTAINS(affected_lines,'"L11"') OR JSON_CONTAINS(affected_lines,'"L08"'))
  AND event_date>='2024-10-01'
ORDER BY event_date;

-- ===== Scenario 5: Alliance reshuffle Feb 2025 — Gemalink alliance share =====
WITH calls_with_alliance AS (
  SELECT
    CASE WHEN pc.eta<'2025-02-01' THEN 'PRE Feb 2025' ELSE 'POST Feb 2025' END AS period,
    a.alliance_name AS alliance,
    pc.total_teu_handled
  FROM port_calls pc
  JOIN alliance_membership_history m
    ON m.line_id=pc.shipping_line_id AND m.from_date<=DATE(pc.eta)
    AND (m.to_date IS NULL OR m.to_date>=DATE(pc.eta))
  JOIN alliances a ON m.alliance_id=a.alliance_id
  WHERE pc.port_id='P006'
),
agg AS (
  SELECT period, alliance, SUM(total_teu_handled) teu
  FROM calls_with_alliance GROUP BY period, alliance
)
SELECT period, alliance,
       ROUND(100*teu/SUM(teu) OVER (PARTITION BY period),1) pct
FROM agg ORDER BY period DESC, pct DESC;

-- ===== Scenario 6: Strategic top 3 candidates (data underlying) =====
-- Multi-turn, uses scenarios 4 + wallet share
SELECT sl.line_name, sl.fleet_capacity_teu, sl.global_rank,
       COALESCE(gemadept_teu, 0) gemadept_teu,
       COALESCE(vn_capacity_est, 0) vn_capacity_est,
       ROUND(100*COALESCE(gemadept_teu,0)/NULLIF(vn_capacity_est,0),1) wallet_pct
FROM shipping_lines sl
LEFT JOIN (SELECT shipping_line_id, SUM(total_teu_handled) gemadept_teu FROM port_calls WHERE eta>='2025-10-01' GROUP BY shipping_line_id) g ON g.shipping_line_id=sl.line_id
LEFT JOIN (SELECT shipping_line_id, SUM(teu_capacity_est) vn_capacity_est FROM port_vessel_schedule_external WHERE eta>='2025-10-01' GROUP BY shipping_line_id) v ON v.shipping_line_id=sl.line_id
WHERE sl.global_rank<=15
ORDER BY (vn_capacity_est-gemadept_teu) DESC LIMIT 5;

-- ===== Scenario 7: Pricing optimization — line tier mix at Gemalink =====
SELECT
  CASE
    WHEN sl.line_id IN ('L01','L02','L03','L04','L05') THEN 'TOP5'
    WHEN sl.line_id IN ('L06','L07','L08','L09','L16') THEN 'MEDIUM'
    ELSE 'SMALL'
  END tier,
  COUNT(*) calls, SUM(pc.total_teu_handled) teu,
  ROUND(100*SUM(pc.total_teu_handled)/SUM(SUM(pc.total_teu_handled)) OVER (),1) pct,
  AVG(pt.rate_per_teu_vnd) avg_rate
FROM port_calls pc
JOIN shipping_lines sl ON pc.shipping_line_id=sl.line_id
LEFT JOIN pricing_tariff pt ON pt.port_id=pc.port_id AND pt.line_id=pc.shipping_line_id
  AND DATE(pc.eta) BETWEEN pt.effective_from AND COALESCE(pt.effective_to,'9999-12-31')
WHERE pc.port_id='P006' AND pc.eta>='2025-04-01'
GROUP BY tier ORDER BY teu DESC;

-- Pricing change verification (deepsea +10% from Feb 2026)
SELECT p.port_name, sl.line_name, pt.rate_per_teu_vnd, pt.effective_from
FROM pricing_tariff pt JOIN ports p ON pt.port_id=p.port_id JOIN shipping_lines sl ON pt.line_id=sl.line_id
WHERE p.port_name IN ('Gemalink','Nam Đình Vũ') AND sl.line_name='Maersk'
ORDER BY p.port_name, pt.effective_from;

-- ===== Scenario 8: What-if — historical tariff context + US share =====
SELECT event_date, title_vi, sentiment FROM news_events
WHERE category='tariff' ORDER BY event_date;

-- ===== FALLBACK: Out-of-scenario queries =====
-- "CMA CGM at Nam Đình Vũ last 3 months"
SELECT DATE_FORMAT(eta,'%Y-%m') mo, COUNT(*) calls, SUM(total_teu_handled) teu
FROM port_calls pc JOIN shipping_lines sl ON pc.shipping_line_id=sl.line_id
JOIN ports p ON pc.port_id=p.port_id
WHERE sl.line_name='CMA CGM' AND p.port_name LIKE 'Nam %' AND eta>='2026-01-01'
GROUP BY mo;

-- "Cảng Dung Quất tháng 9/2025"
SELECT COUNT(*) calls, FORMAT(SUM(total_teu_handled),0) teu FROM port_calls pc
JOIN ports p ON pc.port_id=p.port_id
WHERE p.port_name='Cảng Dung Quất' AND DATE_FORMAT(eta,'%Y-%m')='2025-09';
"""


def write_validation():
    path = os.path.join(SQL_DIR, '05_validation_queries.sql')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(VALIDATION_SQL)
    print(f"Wrote {path}")


# =============================================================================
# README.md
# =============================================================================
README_MD = f"""# Gemadept BI Demo Database — `{DB_NAME}`

Database mock cho demo BI/AI tại Gemadept Corporation, focus persona: **MKT Manager**.

## Mục tiêu
Khai thác dữ liệu đa nguồn (lịch tàu cảng vụ, tin tức ngành, dữ liệu nội bộ) để phát hiện xu hướng thị trường và xác định cơ hội Business Development cho mạng lưới cảng Gemadept (đặc biệt Gemalink).

## Phạm vi data
- **Thời gian:** 2024-04-01 → 2026-03-31 (24 tháng)
- **16 bảng:** 12 data + 4 metadata
- **22 cảng** (7 Gemadept + 15 đối thủ)
- **25 hãng tàu** (top 10 global + 15 regional)
- **7 liên minh** (3 cũ giải thể 1/2025 + 4 mới từ 2/2025: Gemini, Premier, Ocean post, MSC standalone)
- **124 tàu** (mega/large/medium/feeder)
- **30 tuyến dịch vụ** (FE1, EC5, AE1 Gemini, ZX2 ZIM-MSC, Tropic, KVX, JVS...)
- **~60 sự kiện ngành** (Feb 2025 alliance reshuffle, Feb 2026 +10% deepsea, Trump tariff refs)
- **~3,000 port_calls** (transaction Gemadept), **~7,500 lịch tàu cảng vụ** (all ports)
- **350 pricing_tariff** records (port × line × period)

## 8 demo scenarios đã embed anomaly
| # | Scenario | Tầng | Anomaly |
|---|---|---|---|
| 1 | Sản lượng Mar 2026 by alliance | Descriptive | YoY shift do reshuffle Feb 2025 |
| 2 | ⭐ Maersk diagnostic Gemalink | Diagnostic | Maersk Gemalink ↓50% Q1/2026, TCIT ↑100% (Gemini hub-spoke) |
| 3 | Cạnh tranh CM-TV cluster | Diagnostic | TCIT vượt Gemalink về số call hãng lớn Q4/2025 |
| 4 | BD opportunity | Predictive | ZIM 0 calls Gemalink nhưng 6+/tháng CM-TV; HMM/Wan Hai tương tự |
| 5 | Alliance reshuffle impact | Predictive | Pre Feb 2025: 2M+THE+Ocean; Post: Gemini+Premier+Ocean+MSC standalone |
| 6 | Top 3 BD targets | Strategic | Tổng hợp multi-turn |
| 7 | Pricing optimization | Optimization | Top 5 lines = ~72% TEU; deepsea +10% Feb 2026 |
| 8 | What-if Mỹ thuế 25% Q2/2026 | Scenario | News events Trump 2018-2019 + Jul 2025 + Mar 2026 threat |

## Reproduce trên máy mới

```bash
# 1. Khởi tạo MySQL container
docker run --name mock_database \\
  -e MYSQL_ROOT_PASSWORD=root \\
  -e MYSQL_DATABASE={DB_NAME} \\
  -p 3306:3306 \\
  -d mysql:8.0 \\
  --character-set-server=utf8mb4 \\
  --collation-server=utf8mb4_unicode_ci

# 2. Chờ MySQL sẵn sàng
docker exec mock_database mysqladmin ping -uroot -proot --wait=30

# 3. Populate data theo thứ tự
docker exec -i mock_database mysql -uroot -proot < gemadept_mkt_sql/01_ddl_schema.sql
docker exec -i mock_database mysql -uroot -proot < gemadept_mkt_sql/02_metadata.sql
docker exec -i mock_database mysql -uroot -proot < gemadept_mkt_sql/03_master_data.sql
docker exec -i mock_database mysql -uroot -proot < gemadept_mkt_sql/04_transaction_data.sql

# 4. Verify
docker exec -i mock_database mysql -uroot -proot < gemadept_mkt_sql/05_validation_queries.sql

# 5. Reset (nếu cần làm lại)
docker exec -i mock_database mysql -uroot -proot -e \\
  "DROP DATABASE IF EXISTS {DB_NAME}; CREATE DATABASE {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
# Rồi chạy lại bước 3-4
```

## Kết nối AI engine
Database chứa 4 metadata tables (`_meta_tables`, `_meta_columns`, `_meta_kpi`, `_meta_glossary`) sẵn sàng cho MCP/Claude integration. Mọi câu hỏi MKT Manager dạng tự nhiên đều có thể trả lời bằng SQL trên schema này.

**Cross-reference key:** scenarios 2 và 4 đặc biệt yêu cầu JOIN giữa `port_calls` (internal) + `port_vessel_schedule_external` (cảng vụ public, gồm cả đối thủ) + `news_events` (tin ngành) — đây là wow factor chính của demo.

Timezone: ICT (UTC+7).
"""


def write_readme():
    path = os.path.join(SQL_DIR, 'README.md')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(README_MD)
    print(f"Wrote {path}")


if __name__ == '__main__':
    os.makedirs(SQL_DIR, exist_ok=True)
    write_ddl()
    write_master_data()
    write_metadata()

    print("\nGenerating transactions...")
    port_calls = gen_port_calls()
    print(f"  port_calls: {len(port_calls):,}")
    external = gen_external_schedule(port_calls)
    print(f"  external_schedule: {len(external):,}")
    daily = gen_daily_stats(port_calls)
    print(f"  daily_stats: {len(daily):,}")
    tariff = gen_pricing_tariff()
    print(f"  pricing_tariff: {len(tariff):,}")
    write_transactions(port_calls, external, daily, tariff)
    write_validation()
    write_readme()
    print("\nAll files written.")
