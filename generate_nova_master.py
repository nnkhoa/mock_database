#!/usr/bin/env python3
"""
Generate master data for Nova Consumer (NCG) demo database.
Populates all dimension tables directly into MySQL.
"""

import mysql.connector
import random

random.seed(42)

conn = mysql.connector.connect(
    host='localhost', port=3306, user='root', password='root',
    database='nova_consumer_demo', charset='utf8mb4'
)
cur = conn.cursor()

# ============================================
# 1. BUSINESS SEGMENTS (3 records)
# ============================================
segments = [
    (1, 'ANIMAL_HEALTH', 'Thuốc thú y & Vaccine', 'Animal Health & Vaccines', 30.00,
     'Dẫn đầu >30% thị phần thuốc thú y VN. Sản phẩm: kháng sinh, vaccine, vitamin, kháng viêm. 2 nhà máy WHO-GMP.'),
    (2, 'ANIMAL_FEED', 'Thức ăn chăn nuôi', 'Animal Feed', 55.00,
     'Top tư nhân nội địa TACN. 3 nhà máy, tổng công suất ~730K tấn/năm. Thương hiệu: Anova Feed, BG Feed, Nova Feed.'),
    (3, 'FARM', 'Trang trại chăn nuôi', 'Farm Operations', 15.00,
     'Chăn nuôi khép kín heo, gà, bò theo mô hình 3F. GLOBALG.A.P. Phía Nam + Tây Nguyên.'),
]
cur.executemany(
    "INSERT INTO business_segments (segment_id, segment_code, segment_name, segment_name_en, revenue_share_pct, description) VALUES (%s,%s,%s,%s,%s,%s)",
    segments
)

# ============================================
# 2. SUBSIDIARIES (8 records)
# ============================================
subsidiaries = [
    ('SGV', 'Công ty CP Thú y Sài Gòn (Sài Gòn Vet)', 1, 'Công ty con', 100.00, 2005),
    ('ANP', 'Công ty CP Anova Pharma', 1, 'Công ty con', 100.00, 2010),
    ('TNV', 'Công ty TNHH Thành Nhơn Vet', 1, 'Công ty con', 100.00, 1995),
    ('AVT', 'Công ty CP Anovastech', 1, 'Công ty con', 95.00, 2015),
    ('BPC', 'Công ty CP Bio-Pharmachemie', 1, 'Công ty liên kết', 35.00, 2000),
    ('ANF', 'Công ty CP Anova Feed', 2, 'Công ty con', 100.00, 2003),
    ('AFM', 'Công ty CP Anova Farm', 3, 'Công ty con', 100.00, 2008),
    ('AAG', 'Công ty CP Anova Agri Bình Dương', 3, 'Công ty con', 100.00, 2012),
]
cur.executemany(
    "INSERT INTO subsidiaries (subsidiary_code, subsidiary_name, segment_id, ownership_type, ownership_pct, established_year) VALUES (%s,%s,%s,%s,%s,%s)",
    subsidiaries
)

# ============================================
# 3. REGIONS (7 vùng + 18 tỉnh trọng điểm)
# ============================================
regions_vung = [
    ('DBSH', 'Đồng bằng sông Hồng', 'Vùng', None, 23.00, 'Cao'),
    ('TDMNPB', 'Trung du & miền núi phía Bắc', 'Vùng', None, 12.50, 'Trung bình'),
    ('BTBDHMT', 'Bắc Trung Bộ & Duyên hải miền Trung', 'Vùng', None, 20.00, 'Trung bình'),
    ('TN', 'Tây Nguyên', 'Vùng', None, 6.00, 'Trung bình'),
    ('DNB', 'Đông Nam Bộ', 'Vùng', None, 18.00, 'Cao'),
    ('DBSCL', 'Đồng bằng sông Cửu Long', 'Vùng', None, 17.50, 'Cao'),
    ('XK', 'Xuất khẩu', 'Vùng', None, None, None),
]
for r in regions_vung:
    cur.execute(
        "INSERT INTO regions (region_code, region_name, region_level, parent_region_id, population_million, livestock_density) VALUES (%s,%s,%s,%s,%s,%s)",
        r
    )

# Get region IDs
cur.execute("SELECT region_id, region_code FROM regions")
region_map = {code: rid for rid, code in cur.fetchall()}

tinh_data = [
    # (code, name, parent_code, population, livestock_density)
    ('HN', 'Hà Nội', 'DBSH', 8.50, 'Cao'),
    ('HY', 'Hưng Yên', 'DBSH', 1.20, 'Cao'),
    ('HD', 'Hải Dương', 'DBSH', 1.90, 'Cao'),
    ('TB', 'Thái Bình', 'DBSH', 1.80, 'Cao'),
    ('SL', 'Sơn La', 'TDMNPB', 1.25, 'Trung bình'),
    ('TH', 'Thanh Hóa', 'BTBDHMT', 3.70, 'Cao'),
    ('NA', 'Nghệ An', 'BTBDHMT', 3.40, 'Trung bình'),
    ('DL', 'Đắk Lắk', 'TN', 2.00, 'Trung bình'),
    ('DN_TN', 'Đắk Nông', 'TN', 0.65, 'Trung bình'),
    ('GL', 'Gia Lai', 'TN', 1.55, 'Trung bình'),
    ('HCM', 'TP. Hồ Chí Minh', 'DNB', 9.50, 'Thấp'),
    ('DNA', 'Đồng Nai', 'DNB', 3.20, 'Cao'),
    ('BD', 'Bình Dương', 'DNB', 2.60, 'Trung bình'),
    ('LA', 'Long An', 'DNB', 1.70, 'Trung bình'),
    ('BTH', 'Bình Thuận', 'DNB', 1.25, 'Trung bình'),
    ('TG', 'Tiền Giang', 'DBSCL', 1.80, 'Cao'),
    ('DT', 'Đồng Tháp', 'DBSCL', 1.70, 'Trung bình'),
    ('CT', 'Cần Thơ', 'DBSCL', 1.25, 'Trung bình'),
]
for code, name, parent_code, pop, density in tinh_data:
    cur.execute(
        "INSERT INTO regions (region_code, region_name, region_level, parent_region_id, population_million, livestock_density) VALUES (%s,%s,%s,%s,%s,%s)",
        (code, name, 'Tỉnh/Thành', region_map[parent_code], pop, density)
    )

# Refresh region map
cur.execute("SELECT region_id, region_code FROM regions")
region_map = {code: rid for rid, code in cur.fetchall()}

# ============================================
# 4. FACTORIES (5 records)
# ============================================
factories = [
    ('NM_TACN_LA', 'Nhà máy TACN Anova Feed Long An', 2, 6, region_map['LA'],
     'KCN Long Hậu, Long An', 'Thức ăn chăn nuôi', 10833.00, 130000.00, 3500.00, 'ISO 9001, ISO 22000', 2008),
    ('NM_TACN_DN', 'Nhà máy TACN Anova Feed Đồng Nai', 2, 6, region_map['DNA'],
     'KCN Nhơn Trạch, Đồng Nai', 'Thức ăn chăn nuôi', 25000.00, 300000.00, 7500.00, 'ISO 9001, ISO 22000', 2005),
    ('NM_TACN_HY', 'Nhà máy TACN Anova Feed Hưng Yên', 2, 6, region_map['HY'],
     'KCN Phố Nối A, Hưng Yên', 'Thức ăn chăn nuôi', 25000.00, 300000.00, 7200.00, 'ISO 9001, ISO 22000', 2012),
    ('NM_THUOC_BD', 'Nhà máy Thuốc thú y Bình Dương', 1, 2, region_map['BD'],
     'KCN Mỹ Phước, Bình Dương', 'Thuốc thú y', None, None, 2800.00, 'WHO-GMP', 2010),
    ('NM_VACCINE_DN', 'Nhà máy Vaccine Đồng Nai', 1, 4, region_map['DNA'],
     'Trảng Bom, Đồng Nai', 'Vaccine', None, None, 2200.00, 'WHO-GMP', 2015),
]
cur.executemany(
    """INSERT INTO factories (factory_code, factory_name, segment_id, subsidiary_id, region_id,
       address, factory_type, max_capacity_tons_month, max_capacity_tons_year, fixed_cost_monthly,
       certification, commissioned_year) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
    factories
)

# Get factory IDs
cur.execute("SELECT factory_id, factory_code FROM factories")
factory_map = {code: fid for fid, code in cur.fetchall()}

# ============================================
# 5. FARMS (3 records)
# ============================================
farms = [
    ('FARM_HT', 'Trang trại Anova Farm Hàm Tân', 7, region_map['BTH'],
     'Hàm Tân, Bình Thuận', 'Hỗn hợp', 120.00, 55000, 'GLOBALG.A.P'),
    ('FARM_DKN', 'Trang trại Anova Farm Đắk Nông', 7, region_map['DN_TN'],
     'Đắk R\'Lấp, Đắk Nông', 'Hỗn hợp', 200.00, 203000, 'GLOBALG.A.P'),
    ('FARM_BD', 'Trang trại Anova Agri Bình Dương', 8, region_map['BD'],
     'Bến Cát, Bình Dương', 'Bò', 80.00, 1500, 'VietGAP'),
]
cur.executemany(
    """INSERT INTO farms (farm_code, farm_name, subsidiary_id, region_id,
       address, farm_type, area_hectares, max_capacity_heads, certification)
       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
    farms
)

# ============================================
# 6. PRODUCT CATEGORIES (~25 records)
# ============================================
# Level 1 groups
cat_l1 = [
    ('AH_GROUP', 'Thuốc thú y & Vaccine', 'Animal Health & Vaccines', 1, None, 1),
    ('AF_GROUP', 'Thức ăn chăn nuôi', 'Animal Feed', 2, None, 1),
    ('FM_GROUP', 'Sản phẩm trang trại', 'Farm Products', 3, None, 1),
]
for c in cat_l1:
    cur.execute(
        "INSERT INTO product_categories (category_code, category_name, category_name_en, segment_id, parent_category_id, category_level) VALUES (%s,%s,%s,%s,%s,%s)", c)

cur.execute("SELECT category_id, category_code FROM product_categories")
cat_map = {code: cid for cid, code in cur.fetchall()}

# Level 2 categories
cat_l2 = [
    # Animal Health
    ('AH_ANTIBIOTIC', 'Kháng sinh', 'Antibiotics', 1, cat_map['AH_GROUP'], 2),
    ('AH_VACCINE', 'Vaccine', 'Vaccines', 1, cat_map['AH_GROUP'], 2),
    ('AH_VITAMIN', 'Vitamin & Khoáng chất', 'Vitamins & Minerals', 1, cat_map['AH_GROUP'], 2),
    ('AH_ANTIINFLAM', 'Kháng viêm giảm đau', 'Anti-inflammatory', 1, cat_map['AH_GROUP'], 2),
    ('AH_PARASITE', 'Ký sinh trùng', 'Anti-parasitic', 1, cat_map['AH_GROUP'], 2),
    ('AH_DIGESTIVE', 'Hỗ trợ tiêu hóa', 'Digestive Support', 1, cat_map['AH_GROUP'], 2),
    # Animal Feed
    ('AF_PIG', 'TACN Heo', 'Pig Feed', 2, cat_map['AF_GROUP'], 2),
    ('AF_POULTRY', 'TACN Gia cầm', 'Poultry Feed', 2, cat_map['AF_GROUP'], 2),
    ('AF_CATTLE', 'TACN Bò', 'Cattle Feed', 2, cat_map['AF_GROUP'], 2),
    ('AF_AQUA', 'TACN Thủy sản', 'Aquaculture Feed', 2, cat_map['AF_GROUP'], 2),
    # Farm
    ('FM_PIG', 'Heo xuất chuồng', 'Pig Output', 3, cat_map['FM_GROUP'], 2),
    ('FM_POULTRY', 'Gia cầm xuất chuồng', 'Poultry Output', 3, cat_map['FM_GROUP'], 2),
    ('FM_CATTLE', 'Bò xuất chuồng/sữa', 'Cattle Output', 3, cat_map['FM_GROUP'], 2),
]
for c in cat_l2:
    cur.execute(
        "INSERT INTO product_categories (category_code, category_name, category_name_en, segment_id, parent_category_id, category_level) VALUES (%s,%s,%s,%s,%s,%s)", c)

cur.execute("SELECT category_id, category_code FROM product_categories")
cat_map = {code: cid for cid, code in cur.fetchall()}

# Level 3 sub-categories
cat_l3 = [
    ('AF_PIG_MEAT', 'TACN Heo thịt', 'Pig Fattening Feed', 2, cat_map['AF_PIG'], 3),
    ('AF_PIG_SOW', 'TACN Heo nái', 'Sow Feed', 2, cat_map['AF_PIG'], 3),
    ('AF_CHICK_WHITE', 'TACN Gà lông trắng', 'White Broiler Feed', 2, cat_map['AF_POULTRY'], 3),
    ('AF_CHICK_COLOR', 'TACN Gà lông màu', 'Color Broiler Feed', 2, cat_map['AF_POULTRY'], 3),
    ('AF_LAYER', 'TACN Gà đẻ', 'Layer Feed', 2, cat_map['AF_POULTRY'], 3),
    ('AF_DUCK', 'TACN Vịt', 'Duck Feed', 2, cat_map['AF_POULTRY'], 3),
    ('AF_DAIRY', 'TACN Bò sữa', 'Dairy Cattle Feed', 2, cat_map['AF_CATTLE'], 3),
    ('AF_BEEF', 'TACN Bò thịt', 'Beef Cattle Feed', 2, cat_map['AF_CATTLE'], 3),
    ('AH_VAC_IMPORT', 'Vaccine nhập khẩu cao cấp', 'Premium Imported Vaccines', 1, cat_map['AH_VACCINE'], 3),
    ('AH_VAC_LOCAL', 'Vaccine nội địa', 'Domestic Vaccines', 1, cat_map['AH_VACCINE'], 3),
]
for c in cat_l3:
    cur.execute(
        "INSERT INTO product_categories (category_code, category_name, category_name_en, segment_id, parent_category_id, category_level) VALUES (%s,%s,%s,%s,%s,%s)", c)

cur.execute("SELECT category_id, category_code FROM product_categories")
cat_map = {code: cid for cid, code in cur.fetchall()}

# ============================================
# 7. PRODUCTS (~150 SKU)
# ============================================
products = []

# --- Segment 1: Thuốc thú y & Vaccine (60 SKU) ---

# Kháng sinh (15 SKU)
antibiotics = [
    ('AH001', 'Amoxicillin 50% WSP', cat_map['AH_ANTIBIOTIC'], 1, 'Anova Pharma', 'gói', 85000, 42500, 50.0, 'Đa loại', 3.5),
    ('AH002', 'Enrofloxacin 10% Injectable', cat_map['AH_ANTIBIOTIC'], 1, 'Sài Gòn Vet', 'chai', 120000, 54000, 55.0, 'Đa loại', 2.8),
    ('AH003', 'Florfenicol 30% Injectable', cat_map['AH_ANTIBIOTIC'], 1, 'Anova Pharma', 'chai', 150000, 67500, 55.0, 'Heo', 2.5),
    ('AH004', 'Doxycycline 50% WSP', cat_map['AH_ANTIBIOTIC'], 1, 'Sài Gòn Vet', 'gói', 75000, 37500, 50.0, 'Đa loại', 2.2),
    ('AH005', 'Tylosin Tartrate 100% Premix', cat_map['AH_ANTIBIOTIC'], 1, 'Anova Pharma', 'kg', 180000, 81000, 55.0, 'Heo', 1.8),
    ('AH006', 'Gentamicin 10% Injectable', cat_map['AH_ANTIBIOTIC'], 1, 'Sài Gòn Vet', 'chai', 95000, 47500, 50.0, 'Đa loại', 1.5),
    ('AH007', 'Oxytetracycline LA Injectable', cat_map['AH_ANTIBIOTIC'], 1, 'Thành Nhơn Vet', 'chai', 110000, 49500, 55.0, 'Bò', 1.3),
    ('AH008', 'Colistin Sulfate 10% WSP', cat_map['AH_ANTIBIOTIC'], 1, 'Anova Pharma', 'gói', 65000, 32500, 50.0, 'Gia cầm', 1.2),
    ('AH009', 'Tiamulin 45% Premix', cat_map['AH_ANTIBIOTIC'], 1, 'Sài Gòn Vet', 'kg', 200000, 90000, 55.0, 'Heo', 1.0),
    ('AH010', 'Lincomycin-Spectinomycin WSP', cat_map['AH_ANTIBIOTIC'], 1, 'Anova Pharma', 'gói', 90000, 45000, 50.0, 'Gia cầm', 0.9),
    ('AH011', 'Sulfadimethoxine Oral Solution', cat_map['AH_ANTIBIOTIC'], 1, 'Thành Nhơn Vet', 'chai', 55000, 27500, 50.0, 'Đa loại', 0.8),
    ('AH012', 'Ceftiofur 5% Injectable', cat_map['AH_ANTIBIOTIC'], 1, 'Anova Pharma', 'chai', 250000, 100000, 60.0, 'Heo', 0.7),
    ('AH013', 'Tilmicosin 25% Oral', cat_map['AH_ANTIBIOTIC'], 1, 'Sài Gòn Vet', 'chai', 130000, 58500, 55.0, 'Heo', 0.6),
    ('AH014', 'Trimethoprim-Sulfa WSP', cat_map['AH_ANTIBIOTIC'], 1, 'Thành Nhơn Vet', 'gói', 60000, 30000, 50.0, 'Gia cầm', 0.5),
    ('AH015', 'Neomycin Sulfate 50% WSP', cat_map['AH_ANTIBIOTIC'], 1, 'Sài Gòn Vet', 'gói', 70000, 35000, 50.0, 'Đa loại', 0.5),
]
for p in antibiotics:
    products.append(p)

# Vaccine nội địa (8 SKU)
vaccines_local = [
    ('AH016', 'Vaccine Dịch tả heo cổ điển (CSF)', cat_map['AH_VAC_LOCAL'], 1, 'Anovastech', 'liều', 8000, 3200, 60.0, 'Heo', 3.0),
    ('AH017', 'Vaccine PRRS (Hội chứng rối loạn sinh sản)', cat_map['AH_VAC_LOCAL'], 1, 'Anovastech', 'liều', 12000, 4800, 60.0, 'Heo', 2.5),
    ('AH018', 'Vaccine Newcastle (ND) gà', cat_map['AH_VAC_LOCAL'], 1, 'Anovastech', 'liều', 3500, 1400, 60.0, 'Gia cầm', 2.8),
    ('AH019', 'Vaccine Gumboro (IBD) gà', cat_map['AH_VAC_LOCAL'], 1, 'Anovastech', 'liều', 3000, 1200, 60.0, 'Gia cầm', 2.0),
    ('AH020', 'Vaccine E.coli heo con', cat_map['AH_VAC_LOCAL'], 1, 'Anovastech', 'liều', 9000, 3600, 60.0, 'Heo', 1.5),
    ('AH021', 'Vaccine Mycoplasma heo', cat_map['AH_VAC_LOCAL'], 1, 'Anovastech', 'liều', 10000, 4000, 60.0, 'Heo', 1.5),
    ('AH022', 'Vaccine IB (Viêm phế quản truyền nhiễm) gà', cat_map['AH_VAC_LOCAL'], 1, 'Anovastech', 'liều', 2500, 1000, 60.0, 'Gia cầm', 1.2),
    ('AH023', 'Vaccine Pasteurella đa giá', cat_map['AH_VAC_LOCAL'], 1, 'Anovastech', 'liều', 7000, 2800, 60.0, 'Đa loại', 1.0),
]
for p in vaccines_local:
    products.append(p)

# Vaccine nhập khẩu cao cấp (4 SKU, margin 55%+)
vaccines_import = [
    ('AH024', 'Vaccine FMD (Lở mồm long móng) nhập khẩu', cat_map['AH_VAC_IMPORT'], 1, 'Bio-Pharmachemie', 'liều', 35000, 14000, 60.0, 'Đa loại', 4.0),
    ('AH025', 'Vaccine PCV2 (Circovirus heo) nhập khẩu', cat_map['AH_VAC_IMPORT'], 1, 'Bio-Pharmachemie', 'liều', 45000, 18000, 60.0, 'Heo', 3.0),
    ('AH026', 'Vaccine PRRS nhập khẩu thế hệ mới', cat_map['AH_VAC_IMPORT'], 1, 'Bio-Pharmachemie', 'liều', 55000, 22000, 60.0, 'Heo', 2.0),
    ('AH027', 'Vaccine Marek + ND combo nhập khẩu', cat_map['AH_VAC_IMPORT'], 1, 'Bio-Pharmachemie', 'liều', 25000, 10000, 60.0, 'Gia cầm', 1.5),
]
for p in vaccines_import:
    products.append(p)

# Vitamin & Khoáng (10 SKU)
vitamins = [
    ('AH028', 'Vitamin AD3E Injectable', cat_map['AH_VITAMIN'], 1, 'Sài Gòn Vet', 'chai', 45000, 22500, 50.0, 'Đa loại', 1.8),
    ('AH029', 'Vitamin C 10% WSP', cat_map['AH_VITAMIN'], 1, 'Anova Pharma', 'gói', 35000, 17500, 50.0, 'Đa loại', 1.5),
    ('AH030', 'Vitamin B-Complex Injectable', cat_map['AH_VITAMIN'], 1, 'Sài Gòn Vet', 'chai', 55000, 27500, 50.0, 'Đa loại', 1.3),
    ('AH031', 'Premix Khoáng vi lượng', cat_map['AH_VITAMIN'], 1, 'Anova Pharma', 'kg', 80000, 40000, 50.0, 'Đa loại', 1.0),
    ('AH032', 'Calcium Borogluconate Injectable', cat_map['AH_VITAMIN'], 1, 'Thành Nhơn Vet', 'chai', 40000, 20000, 50.0, 'Bò', 0.8),
    ('AH033', 'Iron Dextran Injectable (heo con)', cat_map['AH_VITAMIN'], 1, 'Sài Gòn Vet', 'chai', 30000, 15000, 50.0, 'Heo', 1.2),
    ('AH034', 'Electrolyte & Vitamin WSP', cat_map['AH_VITAMIN'], 1, 'Anova Pharma', 'gói', 28000, 14000, 50.0, 'Đa loại', 1.0),
    ('AH035', 'Vitamin K3 WSP', cat_map['AH_VITAMIN'], 1, 'Sài Gòn Vet', 'gói', 32000, 16000, 50.0, 'Gia cầm', 0.7),
    ('AH036', 'Selenium + Vitamin E Injectable', cat_map['AH_VITAMIN'], 1, 'Thành Nhơn Vet', 'chai', 60000, 30000, 50.0, 'Đa loại', 0.6),
    ('AH037', 'Biotin Premix', cat_map['AH_VITAMIN'], 1, 'Anova Pharma', 'kg', 95000, 47500, 50.0, 'Heo', 0.5),
]
for p in vitamins:
    products.append(p)

# Kháng viêm giảm đau (8 SKU)
anti_inflam = [
    ('AH038', 'Meloxicam 5mg/ml Injectable', cat_map['AH_ANTIINFLAM'], 1, 'Anova Pharma', 'chai', 140000, 63000, 55.0, 'Đa loại', 1.5),
    ('AH039', 'Flunixin Meglumine Injectable', cat_map['AH_ANTIINFLAM'], 1, 'Sài Gòn Vet', 'chai', 160000, 72000, 55.0, 'Bò', 1.2),
    ('AH040', 'Dexamethasone Injectable', cat_map['AH_ANTIINFLAM'], 1, 'Thành Nhơn Vet', 'chai', 50000, 22500, 55.0, 'Đa loại', 1.0),
    ('AH041', 'Ketoprofen 10% Injectable', cat_map['AH_ANTIINFLAM'], 1, 'Anova Pharma', 'chai', 130000, 58500, 55.0, 'Heo', 0.8),
    ('AH042', 'Phenylbutazone Oral Paste', cat_map['AH_ANTIINFLAM'], 1, 'Sài Gòn Vet', 'tuýp', 75000, 33750, 55.0, 'Bò', 0.6),
    ('AH043', 'Prednisolone 5mg Tablet', cat_map['AH_ANTIINFLAM'], 1, 'Thành Nhơn Vet', 'hộp', 45000, 20250, 55.0, 'Đa loại', 0.5),
    ('AH044', 'Tolfenamic Acid Injectable', cat_map['AH_ANTIINFLAM'], 1, 'Anova Pharma', 'chai', 170000, 76500, 55.0, 'Bò', 0.4),
    ('AH045', 'Aspirin Soluble Powder', cat_map['AH_ANTIINFLAM'], 1, 'Sài Gòn Vet', 'gói', 25000, 12500, 50.0, 'Gia cầm', 0.4),
]
for p in anti_inflam:
    products.append(p)

# Ký sinh trùng (8 SKU)
parasites = [
    ('AH046', 'Ivermectin 1% Injectable', cat_map['AH_PARASITE'], 1, 'Sài Gòn Vet', 'chai', 90000, 40500, 55.0, 'Đa loại', 1.5),
    ('AH047', 'Levamisole 10% Injectable', cat_map['AH_PARASITE'], 1, 'Thành Nhơn Vet', 'chai', 65000, 29250, 55.0, 'Đa loại', 1.0),
    ('AH048', 'Albendazole 10% Oral Suspension', cat_map['AH_PARASITE'], 1, 'Anova Pharma', 'chai', 45000, 20250, 55.0, 'Bò', 0.8),
    ('AH049', 'Fenbendazole 10% Oral', cat_map['AH_PARASITE'], 1, 'Sài Gòn Vet', 'chai', 50000, 22500, 55.0, 'Đa loại', 0.7),
    ('AH050', 'Praziquantel Tablet', cat_map['AH_PARASITE'], 1, 'Thành Nhơn Vet', 'hộp', 55000, 24750, 55.0, 'Đa loại', 0.5),
    ('AH051', 'Triclabendazole 5% Oral', cat_map['AH_PARASITE'], 1, 'Anova Pharma', 'chai', 70000, 31500, 55.0, 'Bò', 0.4),
    ('AH052', 'Doramectin 1% Injectable', cat_map['AH_PARASITE'], 1, 'Sài Gòn Vet', 'chai', 120000, 54000, 55.0, 'Bò', 0.4),
    ('AH053', 'Piperazine Citrate WSP', cat_map['AH_PARASITE'], 1, 'Thành Nhơn Vet', 'gói', 35000, 17500, 50.0, 'Gia cầm', 0.3),
]
for p in parasites:
    products.append(p)

# Hỗ trợ tiêu hóa (7 SKU)
digestive = [
    ('AH054', 'Probiotic Multi-strain Powder', cat_map['AH_DIGESTIVE'], 1, 'Anova Pharma', 'gói', 60000, 30000, 50.0, 'Đa loại', 1.2),
    ('AH055', 'Enzyme tiêu hóa Premix', cat_map['AH_DIGESTIVE'], 1, 'Sài Gòn Vet', 'kg', 110000, 55000, 50.0, 'Đa loại', 1.0),
    ('AH056', 'Toxin Binder (chất hấp phụ độc tố)', cat_map['AH_DIGESTIVE'], 1, 'Anova Pharma', 'kg', 85000, 42500, 50.0, 'Đa loại', 0.8),
    ('AH057', 'Acidifier (axit hữu cơ) Liquid', cat_map['AH_DIGESTIVE'], 1, 'Sài Gòn Vet', 'lít', 75000, 37500, 50.0, 'Heo', 0.7),
    ('AH058', 'Kaolin-Pectin Oral Suspension', cat_map['AH_DIGESTIVE'], 1, 'Thành Nhơn Vet', 'chai', 40000, 20000, 50.0, 'Đa loại', 0.5),
    ('AH059', 'Liver Tonic (bổ gan)', cat_map['AH_DIGESTIVE'], 1, 'Anova Pharma', 'chai', 55000, 27500, 50.0, 'Gia cầm', 0.4),
    ('AH060', 'Yeast Culture Powder', cat_map['AH_DIGESTIVE'], 1, 'Sài Gòn Vet', 'kg', 95000, 47500, 50.0, 'Đa loại', 0.4),
]
for p in digestive:
    products.append(p)

# --- Segment 2: TACN (70 SKU) ---

def make_tacn_products():
    prods = []
    pid = 1

    # Heo thịt (20 SKU) - 3 brands × stages
    stages_pig = [
        ('Heo con tập ăn', 13000, 11050, 15.0, 'Heo'),
        ('Heo con cai sữa', 12500, 10625, 15.0, 'Heo'),
        ('Heo choai', 11500, 9775, 15.0, 'Heo'),
        ('Heo vỗ béo GĐ1', 10800, 9180, 15.0, 'Heo'),
        ('Heo vỗ béo GĐ2', 10500, 8925, 15.0, 'Heo'),
        ('Heo vỗ béo xuất chuồng', 10200, 8670, 15.0, 'Heo'),
    ]
    brands_pig = [
        ('Anova Feed', 1.0, [5.0, 4.5, 4.0, 3.5, 3.0, 2.5]),  # premium, high weight
        ('BG Feed', 0.95, [2.0, 1.8, 1.6, 1.4, 1.2, 1.0]),
        ('Nova Feed', 0.90, [1.0, 0.9, 0.8, 0.7, 0.6, 0.5]),
    ]
    for brand, price_mult, weights in brands_pig:
        for i, (stage, price, cost, margin, animal) in enumerate(stages_pig):
            code = f'AF{pid:03d}'
            name = f'{brand} {stage}'
            adj_price = round(price * price_mult)
            adj_cost = round(cost * price_mult)
            prods.append((code, name, cat_map['AF_PIG_MEAT'], 2, brand, 'kg',
                          adj_price, adj_cost, margin, animal, weights[i]))
            pid += 1

    # Heo nái (8 SKU) - 2 brands × stages
    stages_sow = [
        ('Heo nái mang thai', 10000, 8500, 15.0),
        ('Heo nái nuôi con', 10500, 8925, 15.0),
        ('Heo nái hậu bị', 10800, 9180, 15.0),
        ('Heo đực giống', 11000, 9350, 15.0),
    ]
    for brand, pmult in [('Anova Feed', 1.0), ('BG Feed', 0.95)]:
        for stage, price, cost, margin in stages_sow:
            code = f'AF{pid:03d}'
            prods.append((code, f'{brand} {stage}', cat_map['AF_PIG_SOW'], 2, brand, 'kg',
                          round(price*pmult), round(cost*pmult), margin, 'Heo', random.uniform(0.5, 1.5)))
            pid += 1

    # Gà lông trắng (10 SKU)
    stages_broiler = [('Starter', 11500, 9775), ('Grower', 10500, 8925), ('Finisher', 9800, 8330)]
    for brand, pmult in [('Anova Feed', 1.0), ('BG Feed', 0.95), ('Nova Feed', 0.90)]:
        for stage, price, cost in stages_broiler:
            code = f'AF{pid:03d}'
            w = 3.0 if brand == 'Anova Feed' and stage == 'Starter' else random.uniform(0.5, 2.0)
            prods.append((code, f'{brand} Gà lông trắng {stage}', cat_map['AF_CHICK_WHITE'], 2, brand, 'kg',
                          round(price*pmult), round(cost*pmult), 15.0, 'Gia cầm', round(w, 1)))
            pid += 1
    # 1 extra
    prods.append((f'AF{pid:03d}', 'Anova Feed Gà lông trắng Pre-starter', cat_map['AF_CHICK_WHITE'], 2, 'Anova Feed', 'kg',
                  13000, 11050, 15.0, 'Gia cầm', 1.5))
    pid += 1

    # Gà lông màu (8 SKU)
    for brand in ['Anova Feed', 'BG Feed']:
        for stage in ['Starter', 'Grower', 'Finisher GĐ1', 'Finisher GĐ2']:
            code = f'AF{pid:03d}'
            base_p = 10500 if 'Starter' in stage else 9800
            prods.append((code, f'{brand} Gà lông màu {stage}', cat_map['AF_CHICK_COLOR'], 2, brand, 'kg',
                          base_p, round(base_p*0.85), 15.0, 'Gia cầm', random.uniform(0.5, 1.5)))
            pid += 1

    # Gà đẻ (6 SKU)
    for brand in ['Anova Feed', 'BG Feed']:
        for stage in ['Hậu bị', 'Đẻ GĐ1', 'Đẻ GĐ2']:
            code = f'AF{pid:03d}'
            prods.append((code, f'{brand} Gà đẻ {stage}', cat_map['AF_LAYER'], 2, brand, 'kg',
                          10200, 8670, 15.0, 'Gia cầm', random.uniform(0.5, 1.5)))
            pid += 1

    # Vịt (5 SKU)
    for stage in ['Vịt thịt Starter', 'Vịt thịt Grower', 'Vịt thịt Finisher', 'Vịt đẻ GĐ1', 'Vịt đẻ GĐ2']:
        code = f'AF{pid:03d}'
        prods.append((code, f'Anova Feed {stage}', cat_map['AF_DUCK'], 2, 'Anova Feed', 'kg',
                      9500, 8075, 15.0, 'Gia cầm', random.uniform(0.4, 1.0)))
        pid += 1

    # Bò (6 SKU)
    for stage in ['Bò sữa cao sản', 'Bò sữa trung bình', 'Bò sữa cạn']:
        code = f'AF{pid:03d}'
        prods.append((code, f'Anova Feed {stage}', cat_map['AF_DAIRY'], 2, 'Anova Feed', 'kg',
                      11000, 9350, 15.0, 'Bò', random.uniform(0.5, 1.2)))
        pid += 1
    for stage in ['Bò thịt vỗ béo', 'Bò thịt tăng trưởng', 'Bê con']:
        code = f'AF{pid:03d}'
        prods.append((code, f'Anova Feed {stage}', cat_map['AF_BEEF'], 2, 'Anova Feed', 'kg',
                      10500, 8925, 15.0, 'Bò', random.uniform(0.4, 0.8)))
        pid += 1

    # Thủy sản (7 SKU)
    aqua_items = [
        ('Cá tra Starter', 12000, 10200, 'Thủy sản'),
        ('Cá tra Grower', 11000, 9350, 'Thủy sản'),
        ('Cá tra Finisher', 10500, 8925, 'Thủy sản'),
        ('Tôm thẻ Starter', 15000, 12750, 'Thủy sản'),
        ('Tôm thẻ Grower', 14000, 11900, 'Thủy sản'),
        ('Tôm thẻ Finisher', 13000, 11050, 'Thủy sản'),
        ('Cá rô phi Grower', 9500, 8075, 'Thủy sản'),
    ]
    for name, price, cost, animal in aqua_items:
        code = f'AF{pid:03d}'
        prods.append((code, f'Anova Feed {name}', cat_map['AF_AQUA'], 2, 'Anova Feed', 'kg',
                      price, cost, 15.0, animal, random.uniform(0.3, 0.8)))
        pid += 1

    return prods

tacn_products = make_tacn_products()
for p in tacn_products:
    products.append(p)

# --- Segment 3: Trang trại (20 SKU) ---
farm_products = [
    ('FM001', 'Heo thịt xuất chuồng (heo hơi)', cat_map['FM_PIG'], 3, 'Anova Farm', 'kg', 64000, 57600, 10.0, 'Heo', 5.0),
    ('FM002', 'Heo thịt xuất chuồng loại 1', cat_map['FM_PIG'], 3, 'Anova Farm', 'kg', 67000, 60300, 10.0, 'Heo', 3.0),
    ('FM003', 'Heo giống hậu bị cái', cat_map['FM_PIG'], 3, 'Anova Farm', 'con', 5500000, 4400000, 20.0, 'Heo', 1.5),
    ('FM004', 'Heo giống hậu bị đực', cat_map['FM_PIG'], 3, 'Anova Farm', 'con', 7000000, 5600000, 20.0, 'Heo', 0.8),
    ('FM005', 'Heo con giống (7kg)', cat_map['FM_PIG'], 3, 'Anova Farm', 'con', 1200000, 960000, 20.0, 'Heo', 2.5),
    ('FM006', 'Heo con giống (15kg)', cat_map['FM_PIG'], 3, 'Anova Farm', 'con', 1800000, 1440000, 20.0, 'Heo', 2.0),
    ('FM007', 'Gà thịt lông trắng xuất chuồng', cat_map['FM_POULTRY'], 3, 'Anova Farm', 'kg', 42000, 37800, 10.0, 'Gia cầm', 3.0),
    ('FM008', 'Gà thịt lông màu xuất chuồng', cat_map['FM_POULTRY'], 3, 'Anova Farm', 'kg', 50000, 45000, 10.0, 'Gia cầm', 2.0),
    ('FM009', 'Gà giống 1 ngày tuổi (lông trắng)', cat_map['FM_POULTRY'], 3, 'Anova Farm', 'con', 12000, 9600, 20.0, 'Gia cầm', 1.5),
    ('FM010', 'Gà giống 1 ngày tuổi (lông màu)', cat_map['FM_POULTRY'], 3, 'Anova Farm', 'con', 15000, 12000, 20.0, 'Gia cầm', 1.0),
    ('FM011', 'Trứng gà giống', cat_map['FM_POULTRY'], 3, 'Anova Farm', 'quả', 5000, 4000, 20.0, 'Gia cầm', 0.8),
    ('FM012', 'Bò thịt xuất chuồng (bò hơi)', cat_map['FM_CATTLE'], 3, 'Anova Agri', 'kg', 90000, 81000, 10.0, 'Bò', 2.0),
    ('FM013', 'Bò thịt loại 1', cat_map['FM_CATTLE'], 3, 'Anova Agri', 'kg', 95000, 85500, 10.0, 'Bò', 1.5),
    ('FM014', 'Sữa tươi nguyên liệu', cat_map['FM_CATTLE'], 3, 'Anova Agri', 'lít', 14000, 11200, 20.0, 'Bò', 3.0),
    ('FM015', 'Bê giống', cat_map['FM_CATTLE'], 3, 'Anova Agri', 'con', 15000000, 12000000, 20.0, 'Bò', 0.5),
    ('FM016', 'Phân bò hữu cơ', cat_map['FM_CATTLE'], 3, 'Anova Agri', 'tấn', 800000, 400000, 50.0, 'Bò', 0.3),
    ('FM017', 'Heo sữa nguyên con', cat_map['FM_PIG'], 3, 'Anova Farm', 'con', 800000, 640000, 20.0, 'Heo', 1.0),
    ('FM018', 'Gà ta thả vườn xuất chuồng', cat_map['FM_POULTRY'], 3, 'Anova Farm', 'kg', 55000, 46750, 15.0, 'Gia cầm', 0.8),
    ('FM019', 'Vịt thịt xuất chuồng', cat_map['FM_POULTRY'], 3, 'Anova Farm', 'kg', 45000, 38250, 15.0, 'Gia cầm', 0.5),
    ('FM020', 'Bò sữa loại thải', cat_map['FM_CATTLE'], 3, 'Anova Agri', 'kg', 75000, 67500, 10.0, 'Bò', 0.3),
]
for p in farm_products:
    products.append(p)

# Insert all products
for p in products:
    cur.execute(
        """INSERT INTO products (product_code, product_name, category_id, segment_id, brand, unit,
           unit_price, unit_cost, margin_pct, target_animal, popularity_weight)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", p
    )

# ============================================
# 8. RAW MATERIALS (~15+ records)
# ============================================
raw_materials = [
    ('NVL_NGO', 'Ngô hạt', 'Corn', 'Ngũ cốc', 'kg', 'Nhập khẩu', 35.00, 'Cao'),
    ('NVL_DTUONG', 'Khô đậu tương', 'Soybean Meal', 'Đạm thực vật', 'kg', 'Nhập khẩu', 25.00, 'Cao'),
    ('NVL_CAMGAO', 'Cám gạo', 'Rice Bran', 'Phụ phẩm', 'kg', 'Nội địa', 12.00, 'Thấp'),
    ('NVL_DDGS', 'DDGS (Bã ngô khô)', 'DDGS', 'Phụ phẩm', 'kg', 'Nhập khẩu', 8.00, 'Trung bình'),
    ('NVL_PREMIX', 'Premix vitamin & khoáng', 'Vitamin-Mineral Premix', 'Premix/Phụ gia', 'kg', 'Nhập khẩu', 5.00, 'Trung bình'),
    ('NVL_BOTCA', 'Bột cá', 'Fish Meal', 'Đạm thực vật', 'kg', 'Nội địa', 4.00, 'Trung bình'),
    ('NVL_DAUDAU', 'Dầu đậu nành', 'Soybean Oil', 'Ngũ cốc', 'kg', 'Nhập khẩu', 3.00, 'Trung bình'),
    ('NVL_LYSINE', 'Lysine HCl 98%', 'Lysine', 'Premix/Phụ gia', 'kg', 'Nhập khẩu', 2.00, 'Trung bình'),
    ('NVL_METHIONINE', 'DL-Methionine 99%', 'Methionine', 'Premix/Phụ gia', 'kg', 'Nhập khẩu', 2.00, 'Trung bình'),
    ('NVL_MUOI', 'Muối & chất tạo viên', 'Salt & Pellet Binder', 'Khác', 'kg', 'Nội địa', 1.00, 'Thấp'),
    ('NVL_CAMMI', 'Cám mì', 'Wheat Bran', 'Phụ phẩm', 'kg', 'Cả hai', 3.00, 'Thấp'),
    ('NVL_API', 'Active Pharmaceutical Ingredients (API)', 'API', 'Dược liệu', 'kg', 'Nhập khẩu', None, 'Cao'),
    ('NVL_TADUOC', 'Tá dược', 'Excipients', 'Tá dược', 'kg', 'Cả hai', None, 'Thấp'),
    ('NVL_BAOBI', 'Bao bì dược phẩm', 'Pharma Packaging', 'Khác', 'kg', 'Nội địa', None, 'Thấp'),
    ('NVL_ADJUVANT', 'Adjuvant (tá dược vaccine)', 'Vaccine Adjuvant', 'Dược liệu', 'kg', 'Nhập khẩu', None, 'Trung bình'),
]
cur.executemany(
    """INSERT INTO raw_materials (material_code, material_name, material_name_en, material_category,
       unit, origin, cogs_share_pct, price_volatility)
       VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
    raw_materials
)

# ============================================
# 9. SUPPLIERS (~30 records)
# ============================================
suppliers = [
    # NVL nhập khẩu (10)
    ('SUP_CARGILL', 'Cargill Trading (Vietnam)', 'Mỹ', 'NVL TACN', None),
    ('SUP_BUNGE', 'Bunge Asia', 'Argentina', 'NVL TACN', None),
    ('SUP_ADM', 'ADM Vietnam', 'Mỹ', 'NVL TACN', None),
    ('SUP_COFCO', 'COFCO International', 'Trung Quốc', 'NVL TACN', None),
    ('SUP_LDC', 'Louis Dreyfus Company', 'Pháp', 'NVL TACN', None),
    ('SUP_CJ_BIO', 'CJ Bio (Amino Acid)', 'Hàn Quốc', 'NVL TACN', None),
    ('SUP_EVONIK', 'Evonik Vietnam (Methionine)', 'Đức', 'NVL TACN', None),
    ('SUP_DSM', 'DSM Animal Nutrition', 'Hà Lan', 'NVL TACN', None),
    ('SUP_WILMAR', 'Wilmar International', 'Singapore', 'NVL TACN', None),
    ('SUP_OLAM', 'Olam Agri Vietnam', 'Singapore', 'NVL TACN', None),
    # NVL nội địa (10)
    ('SUP_CAMGAO_AG', 'HTX Lúa gạo An Giang', 'Việt Nam', 'NVL TACN', region_map['DBSCL']),
    ('SUP_CAMGAO_CT', 'Công ty TNHH Cám Cần Thơ', 'Việt Nam', 'NVL TACN', region_map['CT']),
    ('SUP_BOTCA_KH', 'Công ty CP Bột cá Khánh Hòa', 'Việt Nam', 'NVL TACN', region_map['BTBDHMT']),
    ('SUP_BOTCA_BTH', 'Cơ sở Bột cá Bình Thuận', 'Việt Nam', 'NVL TACN', region_map['BTH']),
    ('SUP_CORN_SL', 'HTX Ngô Sơn La', 'Việt Nam', 'NVL TACN', region_map['SL']),  # Special: Hưng Yên rẻ hơn 5%
    ('SUP_MUOI_NA', 'Muối Nghệ An', 'Việt Nam', 'NVL TACN', region_map['NA']),
    ('SUP_CAMMI_HN', 'Nhà máy Bột mì Hà Nội', 'Việt Nam', 'NVL TACN', region_map['HN']),
    ('SUP_CAMMI_BD', 'Nhà máy Bột mì Bình Dương', 'Việt Nam', 'NVL TACN', region_map['BD']),
    ('SUP_CAMGAO_TB', 'HTX Lúa gạo Thái Bình', 'Việt Nam', 'NVL TACN', region_map['TB']),
    ('SUP_CAMGAO_TG', 'HTX Lúa gạo Tiền Giang', 'Việt Nam', 'NVL TACN', region_map['TG']),
    # NVL thuốc thú y (5)
    ('SUP_API_CN', 'Zhejiang Pharma (API Trung Quốc)', 'Trung Quốc', 'NVL Thuốc', None),
    ('SUP_API_IN', 'Aurobindo Pharma India', 'Ấn Độ', 'NVL Thuốc', None),
    ('SUP_API_EU', 'Huvepharma (EU API)', 'Bulgaria', 'NVL Thuốc', None),
    ('SUP_TADUOC_VN', 'Công ty CP Tá dược Việt Nam', 'Việt Nam', 'NVL Thuốc', region_map['BD']),
    ('SUP_ADJ_FR', 'SEPPIC (Adjuvant Pháp)', 'Pháp', 'NVL Thuốc', None),
    # Bao bì & khác (5)
    ('SUP_BAOBI_BD', 'Bao bì Đại Đồng Bình Dương', 'Việt Nam', 'Bao bì', region_map['BD']),
    ('SUP_BAOBI_LA', 'Bao bì Long An', 'Việt Nam', 'Bao bì', region_map['LA']),
    ('SUP_BAOBI_HY', 'Bao bì Hưng Yên', 'Việt Nam', 'Bao bì', region_map['HY']),
    ('SUP_PHUGGIA_KR', 'Daesang Group (phụ gia)', 'Hàn Quốc', 'Khác', None),
    ('SUP_PHUGGIA_JP', 'Ajinomoto Animal Nutrition', 'Nhật Bản', 'Khác', None),
]
cur.executemany(
    "INSERT INTO suppliers (supplier_code, supplier_name, country, supplier_type, region_id) VALUES (%s,%s,%s,%s,%s)",
    suppliers
)

# ============================================
# 10. DISTRIBUTION CHANNELS (10 records)
# ============================================
channels = [
    ('CH_DL1_TACN', 'Đại lý cấp 1 TACN', 'Đại lý', 2),
    ('CH_DL2_TACN', 'Đại lý cấp 2 TACN', 'Đại lý', 2),
    ('CH_TT_TACN', 'Trang trại lớn (TACN trực tiếp)', 'Trang trại lớn', 2),
    ('CH_XK_TACN', 'Xuất khẩu TACN', 'Xuất khẩu', 2),
    ('CH_DL_THUOC', 'Đại lý thuốc thú y', 'Đại lý', 1),
    ('CH_BV_THUOC', 'Bệnh viện thú y / Cơ sở tiêm phòng', 'Bệnh viện thú y', 1),
    ('CH_TT_THUOC', 'Trang trại lớn (thuốc trực tiếp)', 'Trang trại lớn', 1),
    ('CH_XK_THUOC', 'Xuất khẩu thuốc thú y', 'Xuất khẩu', 1),
    ('CH_NOIBO', 'Nội bộ — trang trại Nova', 'Nội bộ', 2),
    ('CH_ONLINE', 'Online (B2B platform)', 'Online', 1),
]
cur.executemany(
    "INSERT INTO distribution_channels (channel_code, channel_name, channel_type, segment_id) VALUES (%s,%s,%s,%s)",
    channels
)

# Get channel IDs
cur.execute("SELECT channel_id, channel_code FROM distribution_channels")
channel_map = {code: cid for cid, code in cur.fetchall()}

# ============================================
# 11. CUSTOMERS (~200 records)
# ============================================
# Get tinh region IDs for customer distribution
tinh_ids_nam = [region_map[c] for c in ['HCM', 'DNA', 'BD', 'LA', 'BTH', 'TG', 'DT', 'CT']]
tinh_ids_bac = [region_map[c] for c in ['HN', 'HY', 'HD', 'TB', 'SL']]
tinh_ids_trung = [region_map[c] for c in ['TH', 'NA', 'DL', 'DN_TN', 'GL']]

customers = []
cust_id = 0

# 80 khách TACN
tacn_channels = [channel_map['CH_DL1_TACN'], channel_map['CH_DL2_TACN'], channel_map['CH_TT_TACN']]
for i in range(80):
    cust_id += 1
    code = f'KH_TACN_{cust_id:03d}'

    if i < 48:  # 60% miền Nam
        region = random.choice(tinh_ids_nam)
    elif i < 72:  # 30% miền Bắc
        region = random.choice(tinh_ids_bac)
    else:  # 10% miền Trung
        region = random.choice(tinh_ids_trung)

    if i < 25:
        ctype = 'Đại lý cấp 1'
        channel = channel_map['CH_DL1_TACN']
    elif i < 55:
        ctype = 'Đại lý cấp 2'
        channel = channel_map['CH_DL2_TACN']
    else:
        ctype = 'Trang trại lớn'
        channel = channel_map['CH_TT_TACN']

    # Revenue tier
    if i < 16:
        tier = 'A'
    elif i < 40:
        tier = 'B'
    else:
        tier = 'C'

    # Generate Vietnamese-style names
    prefixes = ['Đại lý', 'Cửa hàng', 'Trang trại', 'HTX', 'Cơ sở', 'Công ty TNHH']
    lastnames = ['Nguyễn', 'Trần', 'Lê', 'Phạm', 'Hoàng', 'Huỳnh', 'Phan', 'Vũ', 'Võ', 'Đặng',
                 'Bùi', 'Đỗ', 'Hồ', 'Ngô', 'Dương', 'Lý']
    firstnames = ['Văn Minh', 'Thị Hoa', 'Hữu Tài', 'Thanh Tùng', 'Minh Đức', 'Thị Lan',
                  'Quốc Hưng', 'Thị Mai', 'Anh Tuấn', 'Văn Hùng', 'Thị Thu', 'Đức Thắng',
                  'Quang Hải', 'Thị Ngọc', 'Văn Long', 'Thị Phương']

    if ctype == 'Trang trại lớn':
        name = f'Trang trại {random.choice(lastnames)} {random.choice(firstnames)}'
    else:
        name = f'{random.choice(prefixes)} TACN {random.choice(lastnames)} {random.choice(firstnames)}'

    customers.append((code, name, ctype, region, channel, 2, tier))

# 80 khách thuốc thú y
thuoc_channels = [channel_map['CH_DL_THUOC'], channel_map['CH_BV_THUOC'], channel_map['CH_TT_THUOC']]
for i in range(80):
    cust_id += 1
    code = f'KH_THUOC_{cust_id:03d}'

    if i < 48:
        region = random.choice(tinh_ids_nam)
    elif i < 72:
        region = random.choice(tinh_ids_bac)
    else:
        region = random.choice(tinh_ids_trung)

    if i < 30:
        ctype = 'Đại lý cấp 1'
        channel = channel_map['CH_DL_THUOC']
    elif i < 55:
        ctype = 'Bệnh viện thú y'
        channel = channel_map['CH_BV_THUOC']
    else:
        ctype = 'Trang trại lớn'
        channel = channel_map['CH_TT_THUOC']

    if i < 16:
        tier = 'A'
    elif i < 40:
        tier = 'B'
    else:
        tier = 'C'

    if ctype == 'Bệnh viện thú y':
        name = f'Phòng khám thú y {random.choice(lastnames)} {random.choice(firstnames)}'
    elif ctype == 'Trang trại lớn':
        name = f'Trang trại {random.choice(lastnames)} {random.choice(firstnames)}'
    else:
        name = f'Đại lý thuốc thú y {random.choice(lastnames)} {random.choice(firstnames)}'

    customers.append((code, name, ctype, region, channel, 1, tier))

# 20 khách xuất khẩu
xk_countries = ['Campuchia', 'Lào', 'Myanmar', 'Philippines', 'Indonesia', 'Bangladesh']
for i in range(20):
    cust_id += 1
    code = f'KH_XK_{cust_id:03d}'
    country = random.choice(xk_countries)

    if i < 12:
        channel = channel_map['CH_XK_TACN']
        seg = 2
        name = f'Export Partner {country} #{i+1}'
    else:
        channel = channel_map['CH_XK_THUOC']
        seg = 1
        name = f'Pharma Export {country} #{i-11}'

    tier = 'A' if i < 4 else ('B' if i < 10 else 'C')
    customers.append((code, name, 'Xuất khẩu', region_map['XK'], channel, seg, tier))

# 20 khách nội bộ (trang trại Nova)
for i in range(20):
    cust_id += 1
    code = f'KH_NB_{cust_id:03d}'
    farm_regions = [region_map['BTH'], region_map['DN_TN'], region_map['BD']]
    region = random.choice(farm_regions)

    if i < 10:
        seg = 2  # mua TACN
        name = f'Nội bộ - Anova Farm #{i+1} (TACN)'
    else:
        seg = 1  # mua thuốc
        name = f'Nội bộ - Anova Farm #{i-9} (Thuốc)'

    tier = 'B'
    customers.append((code, name, 'Nội bộ', region, channel_map['CH_NOIBO'], seg, tier))

# Mark 2 tier-A customers in Đông Nam Bộ as "lost" customers for anomaly S2
# These will be customer IDs for KH_TACN_001 and KH_TACN_002 (first 2 tier A, miền Nam)
# We'll track this by naming convention
customers[0] = (customers[0][0], 'Đại lý TACN Phát Đạt (Đồng Nai)', 'Đại lý cấp 1',
                region_map['DNA'], channel_map['CH_DL1_TACN'], 2, 'A')
customers[1] = (customers[1][0], 'Trang trại Hoàng Gia (Bình Dương)', 'Trang trại lớn',
                region_map['BD'], channel_map['CH_TT_TACN'], 2, 'A')

cur.executemany(
    """INSERT INTO customers (customer_code, customer_name, customer_type, region_id, channel_id, segment_id, revenue_tier)
       VALUES (%s,%s,%s,%s,%s,%s,%s)""",
    customers
)

conn.commit()

# Print summary
tables_counts = [
    'business_segments', 'subsidiaries', 'regions', 'factories', 'farms',
    'product_categories', 'products', 'raw_materials', 'suppliers',
    'distribution_channels', 'customers'
]
print("=== MASTER DATA SUMMARY ===")
for t in tables_counts:
    cur.execute(f"SELECT COUNT(*) FROM {t}")
    count = cur.fetchone()[0]
    print(f"  {t}: {count} records")

# Sample data
print("\n=== SAMPLE: Products by segment ===")
cur.execute("SELECT segment_id, COUNT(*) FROM products GROUP BY segment_id")
for seg_id, cnt in cur.fetchall():
    print(f"  Segment {seg_id}: {cnt} SKU")

print("\n=== SAMPLE: Customers by type ===")
cur.execute("SELECT customer_type, COUNT(*) FROM customers GROUP BY customer_type")
for ctype, cnt in cur.fetchall():
    print(f"  {ctype}: {cnt}")

cur.close()
conn.close()
print("\nDone!")
