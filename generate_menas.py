#!/usr/bin/env python3
"""
Menas Group — Multi-Business Demo Database Generator
Generates 18 months of data (2024-10 to 2026-03) for menas_demo database.
Businesses: Mall (TTTM), Supermarket, F&B, Duty Free, Beauty

Output: SQL files in menas_sql/
"""

import random
import math
import os
from datetime import date, timedelta
from collections import defaultdict

random.seed(42)

# =============================================================================
# CONFIG
# =============================================================================
DB_NAME = 'menas_demo'
SQL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'menas_sql')
BATCH = 500

START_DATE = date(2024, 10, 1)
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

YOY_GROWTH = 0.15  # 15% annual

# Monthly seasonality index (1-based month) — per spec
MONTHLY_SEASON = {
    1: 1.25, 2: 1.15, 3: 0.85, 4: 0.90, 5: 0.95, 6: 1.05,
    7: 1.10, 8: 1.00, 9: 0.90, 10: 0.95, 11: 1.05, 12: 1.15,
}

# Nha Trang location seasonality (tourist peaks) — per spec
NT_SEASON = {
    1: 1.10, 2: 1.05, 3: 0.85, 4: 0.90, 5: 1.00, 6: 1.30,
    7: 1.40, 8: 1.20, 9: 0.75, 10: 0.80, 11: 0.90, 12: 1.05,
}

# Weekly pattern for daily data (Mon=0 ... Sun=6) — per spec
WEEKLY_PATTERN = [0.80, 0.85, 0.90, 0.95, 1.10, 1.25, 1.15]

# =============================================================================
# HELPERS
# =============================================================================
def esc(v):
    if v is None:
        return 'NULL'
    if isinstance(v, bool):
        return '1' if v else '0'
    if isinstance(v, (int, float)):
        if isinstance(v, float) and v == int(v) and abs(v) < 1e15:
            return str(int(v))
        return f'{v:.2f}'
    if isinstance(v, date):
        return f"'{v.isoformat()}'"
    s = str(v).replace("\\", "\\\\").replace("'", "\\'")
    return f"'{s}'"


def write_inserts(f, table, columns, rows, batch=BATCH):
    if not rows:
        return
    col_str = ', '.join(columns)
    for i in range(0, len(rows), batch):
        chunk = rows[i:i + batch]
        vals = ['(' + ', '.join(esc(v) for v in row) + ')' for row in chunk]
        f.write(f"INSERT INTO `{table}` ({col_str}) VALUES\n")
        f.write(',\n'.join(vals))
        f.write(';\n\n')


def growth_factor(month_date):
    """Compound growth factor from START_DATE."""
    months_since = (month_date.year - START_DATE.year) * 12 + (month_date.month - START_DATE.month)
    return (1 + YOY_GROWTH) ** (months_since / 12)


def is_nha_trang(loc_id):
    return loc_id in ('LOC02', 'LOC15')


def location_season(loc_id, month_num):
    if is_nha_trang(loc_id):
        return NT_SEASON[month_num]
    return 1.0


def ramp_up(loc_id, month_date):
    """Ramp-up multiplier for new locations — exact spec values."""
    if loc_id == 'LOC04':
        key = f"{month_date.year}-{month_date.month:02d}"
        ramp_table = {
            '2024-11': 0.60, '2024-12': 0.75,
            '2025-01': 0.80, '2025-02': 0.82, '2025-03': 0.85,
            '2025-04': 0.88, '2025-05': 0.90, '2025-06': 0.92,
            '2025-07': 0.94, '2025-08': 0.95, '2025-09': 0.96,
            '2025-10': 0.97, '2025-11': 0.98, '2025-12': 1.00,
            '2026-01': 1.02, '2026-02': 1.00, '2026-03': 1.00,
        }
        return ramp_table.get(key, 0.0 if month_date < date(2024, 11, 1) else 1.0)
    if loc_id == 'LOC14':
        key = f"{month_date.year}-{month_date.month:02d}"
        ramp_table = {
            '2025-12': 0.50,
            '2026-01': 0.65, '2026-02': 0.55, '2026-03': 0.70,
        }
        return ramp_table.get(key, 0.0 if month_date < date(2025, 12, 1) else 1.0)
    return 1.0


def days_in_month(d):
    y, m = d.year, d.month
    m2 = m + 1
    y2 = y
    if m2 > 12:
        m2 = 1; y2 += 1
    return (date(y2, m2, 1) - d).days


# =============================================================================
# BUSINESS UNITS
# =============================================================================
BUSINESS_UNITS = [
    ('MALL',        'Trung tâm thương mại',   'Quản lý & vận hành TTTM',          'Cho thuê mặt bằng + chia sẻ doanh thu'),
    ('SUPERMARKET', 'Siêu thị Mena Gourmet',   'Siêu thị cao cấp nhập khẩu',       'Bán lẻ trực tiếp'),
    ('FB',          'F&B Restaurants',          'Chuỗi nhà hàng & ẩm thực',         'Doanh thu dịch vụ ăn uống'),
    ('DUTYFREE',    'Duty Free 3Sixty',         'Cửa hàng miễn thuế sân bay',       'Bán lẻ miễn thuế'),
    ('BEAUTY',      'Mena Cosmetics & Perfumes','Mỹ phẩm & nước hoa cao cấp',       'Bán lẻ chuyên ngành'),
]

# =============================================================================
# LOCATIONS
# =============================================================================
LOCATIONS = [
    ('LOC01','Menas Mall Saigon Airport','MALL','TTTM','60A Trường Sơn, Tân Bình','HCM','Tân Bình',15000,'2020-12-01','active'),
    ('LOC02','Menas Mall Central Square Nha Trang','MALL','TTTM','Trần Phú, Nha Trang','Nha Trang','Lộc Thọ',8000,'2021-06-01','active'),
    ('LOC03','Mena Gourmet - Saigon Airport','SUPERMARKET','Siêu thị','Tầng B1 Menas Mall SA','HCM','Tân Bình',3000,'2024-10-01','active'),
    ('LOC04','Mena Gourmet - Celesta Rise','SUPERMARKET','Siêu thị','Celesta Rise, Nhà Bè','HCM','Nhà Bè',1500,'2024-11-01','active'),
    ('LOC05','Steakhouse The Fan','FB','F&B','Kim Long Villas, Nhà Bè','HCM','Nhà Bè',250,'2021-03-01','active'),
    ('LOC06','Yum Food Village - Mall SA','FB','F&B','Tầng 5 Menas Mall SA','HCM','Tân Bình',1000,'2020-12-01','active'),
    ('LOC07',"L'Amuse Gourmet Bistro",'FB','F&B','Tầng B1 Menas Mall SA','HCM','Tân Bình',180,'2021-01-01','active'),
    ('LOC08',"Don Cipriani's",'FB','F&B','Menas Mall SA','HCM','Tân Bình',150,'2021-06-01','active'),
    ('LOC09','V-Senses Dining','FB','F&B','Menas Mall SA','HCM','Tân Bình',200,'2021-06-01','active'),
    ('LOC10','Thai Siam Kitchen','FB','F&B','547 Huỳnh Tấn Phát, Q7','HCM','Quận 7',200,'2022-01-01','active'),
    ('LOC11','Boulangeries de Saigon','FB','F&B','Trong Mena Gourmet Market','HCM','Tân Bình',80,'2024-10-01','active'),
    ('LOC12','Yum Food Outlet - Kim Long','FB','F&B','Kim Long Villas, Nhà Bè','HCM','Nhà Bè',200,'2022-06-01','active'),
    ('LOC13','3Sixty Duty-free','DUTYFREE','Duty Free','Menas Mall Saigon Airport','HCM','Tân Bình',1000,'2020-12-01','active'),
    ('LOC14','Mena Cosmetics & Perfumes','BEAUTY','Beauty','Tầng 1 Menas Mall SA','HCM','Tân Bình',200,'2025-12-01','active'),
    ('LOC15','Yum Food Village - Nha Trang','FB','F&B','Menas Mall Nha Trang','Nha Trang','Lộc Thọ',600,'2021-06-01','active'),
]

# =============================================================================
# PRODUCT CATEGORIES (Supermarket)
# =============================================================================
PRODUCT_CATEGORIES = [
    (1, 'Thực phẩm tươi sống',      'Rau củ, thịt cá, trái cây tươi',           25.00),
    (2, 'Thực phẩm nhập khẩu',      'Thực phẩm châu Âu, Nhật, Hàn',            15.00),
    (3, 'Rượu bia',                  'Rượu vang, bia nhập, sake, whisky',        20.00),
    (4, 'Mỹ phẩm & Nước hoa',       'Skincare, nước hoa cao cấp',               35.00),
    (5, 'Bánh kẹo & Quà tặng',      'Chocolate, quà Tết, gift set',             22.00),
    (6, 'Đồ dùng gia đình',         'Dụng cụ nhà bếp, nến thơm, trang trí',    28.00),
]

# Category seasonality: exact spec values per (category_id, month)
_CAT_SEASON_RAW = {
    1: {1:1.40, 2:1.10, 3:0.85, 4:0.90, 5:0.95, 6:1.00, 7:1.00, 8:0.95, 9:0.90, 10:0.95, 11:1.00, 12:1.20},  # Thực phẩm tươi sống
    2: {1:1.30, 2:1.10, 3:0.90, 4:0.90, 5:0.95, 6:1.00, 7:1.05, 8:0.95, 9:0.90, 10:0.95, 11:1.00, 12:1.20},  # Thực phẩm nhập khẩu
    3: {1:1.50, 2:1.20, 3:0.80, 4:0.85, 5:0.90, 6:1.10, 7:1.15, 8:0.95, 9:0.85, 10:0.90, 11:1.05, 12:1.30},  # Rượu bia
    4: {1:1.10, 2:1.30, 3:1.15, 4:0.90, 5:0.95, 6:0.95, 7:1.00, 8:0.90, 9:0.85, 10:1.10, 11:1.15, 12:1.20},  # Mỹ phẩm & Nước hoa
    5: {1:1.60, 2:1.00, 3:0.70, 4:0.80, 5:0.85, 6:0.90, 7:0.90, 8:0.95, 9:0.85, 10:0.95, 11:1.05, 12:1.30},  # Bánh kẹo & Quà tặng
    6: {1:1.05, 2:0.95, 3:0.90, 4:0.95, 5:1.00, 6:1.00, 7:1.00, 8:1.05, 9:0.95, 10:0.95, 11:1.05, 12:1.10},  # Đồ dùng gia đình
}
CAT_SEASON = {}
for cid in range(1, 7):
    for m in range(1, 13):
        CAT_SEASON[(cid, m)] = _CAT_SEASON_RAW[cid][m]


# =============================================================================
# PRODUCT GENERATION (~500 SKU)
# =============================================================================
def generate_products():
    """Generate ~500 products with Pareto-distributed popularity weights."""
    products = []
    pid = 0

    # Category config: (cat_id, n_sku, domestic_pct, price_range_base, price_range_top, cost_margin)
    cat_config = [
        (1, 80,  0.90, 25000,   350000,  0.75),   # Thực phẩm tươi sống
        (2, 100, 0.00, 45000,   800000,  0.85),   # Nhập khẩu (all imported)
        (3, 80,  0.30, 35000,   3500000, 0.80),   # Rượu bia
        (4, 100, 0.20, 150000,  5000000, 0.65),   # Mỹ phẩm
        (5, 80,  0.40, 30000,   1200000, 0.78),   # Bánh kẹo
        (6, 60,  0.50, 80000,   2500000, 0.72),   # Đồ dùng gia đình
    ]

    # Name seeds per category
    name_seeds = {
        1: [
            "Bơ Đắk Lắk loại 1","Cá hồi Na Uy fillet 300g","Rau organic Đà Lạt combo",
            "Gà H'Mông Tây Giang nguyên con","Tôm sú Cà Mau 500g","Thịt bò Wagyu Úc 200g",
            "Cá ngừ đại dương 500g","Nấm đùi gà Đà Lạt 300g","Xà lách Mỹ hữu cơ",
            "Cà chua cherry Đà Lạt 500g","Thịt heo Mộc Châu 500g","Cá diêu hồng phi lê",
            "Rau muống organic 300g","Bí đỏ Nhật 1kg","Khoai lang mật Đà Lạt",
            "Trứng gà ta Bến Tre 10 quả","Đậu bắp baby 300g","Ớt chuông 3 màu",
            "Bắp cải tím 500g","Dưa leo baby 300g","Măng tây Ninh Thuận 200g",
            "Chanh dây Đắk Nông 1kg","Sầu riêng Ri6 1kg","Xoài cát Hòa Lộc",
            "Thanh long ruột đỏ Bình Thuận","Bưởi da xanh Bến Tre","Táo Fuji Nhật",
            "Nho xanh Mỹ seedless 500g","Dâu tây Đà Lạt hộp 300g","Cam sành Vĩnh Long",
            "Thịt bò Úc MB3 300g","Sườn cừu New Zealand","Ba chỉ bò Mỹ 400g",
            "Cá chẽm phi lê 300g","Tôm hùm Alaska 500g","Mực ống tươi Phú Quốc",
            "Nghêu lụa Cần Giờ 500g","Hàu sữa Vân Đồn 1kg","Ếch đồng 500g",
            "Chả giò rế Cầu Tre","Nem chua Thanh Hóa","Giò lụa Ước Lễ",
        ],
        2: [
            "Phô mai Comté Pháp 200g","Dầu olive Colavita Ý 500ml","Mứt việt quất Bonne Maman",
            "Pasta Barilla Spaghetti 500g","Sốt cà chua San Marzano","Bơ Président Pháp 200g",
            "Phô mai Parmesan Ý 150g","Sữa tươi Meiji Nhật 1L","Xúc xích Đức Bratwurst",
            "Pate gan ngỗng Pháp 150g","Dầu truffle Urbani 100ml","Giấm Balsamic Modena 250ml",
            "Mù tạt Dijon Maille 200g","Nước mắm cá cơm Ý Colatura","Tương miso Marukome 500g",
            "Nori Yamamotoyama 50 tờ","Wasabi tươi S&B 43g","Dầu mè Kadoya Nhật 150ml",
            "Bơ đậu phộng Skippy 462g","Mật ong Manuka MGO400","Granola ngũ cốc Úc 500g",
            "Sữa chua Hy Lạp Fage","Kem Häagen-Dazs 473ml","Phô mai Brie Pháp 200g",
            "Thịt bò khô Úc 200g","Cá hộp Jose Gourmet","Soup miso instant Marukome",
            "Ketchup Heinz 570g","Mayo Kewpie Nhật 500g","Sốt teriyaki Kikkoman",
            "Trà Earl Grey Twinings","Cà phê Lavazza ORO 250g","Nước dừa Chaokoh 500ml",
            "Ngũ cốc Kelloggs 300g","Snack rong biển Tao Kae Noi","Đậu hũ organic Silken",
            "Kimchi Jongga Hàn Quốc 380g","Gạo Japonica Nhật 2kg","Miến Hàn Quốc 500g",
            "Bánh gạo Topokki Hàn 500g","Dầu hào Lee Kum Kee","Tương ớt Sriracha 482g",
        ],
        3: [
            "Bia Paulaner Đức 500ml","Rượu vang Château Bordeaux 750ml","Sake Dassai 45 720ml",
            "Bia Tiger Crystal 330ml","Whisky Macallan 12 năm 700ml","Rượu vang Ý Chianti 750ml",
            "Champagne Moët & Chandon","Gin Tanqueray 750ml","Vodka Grey Goose 700ml",
            "Rum Havana Club 700ml","Bia Heineken 330ml lon","Bia Sapporo Premium 330ml",
            "Rượu vang Chile Casillero","Prosecco Mionetto 750ml","Tequila Patrón Silver",
            "Cognac Hennessy VS 700ml","Bia Asahi Super Dry 330ml","Rượu mận Nhật Choya",
            "Bia craft Pasteur Street IPA","Bia Chimay Blue Bỉ 330ml","Whisky Johnnie Walker Black",
            "Rượu vang Úc Penfolds","Sake Kubota Manju 720ml","Bia Hoegaarden Bỉ 330ml",
            "Gin Hendrick's 700ml","Rượu vang New Zealand","Bia Leffe Blonde Bỉ",
            "Brandy Rémy Martin VSOP","Cider Somersby Apple 330ml","Bia Corona Extra 355ml",
            "Whisky Glenfiddich 12yr","Rượu vang Pháp Côtes du Rhône","Bia Budweiser 330ml",
            "Sake Hakutsuru 300ml","Port Wine Graham's","Amaretto Disaronno 700ml",
        ],
        4: [
            "Lancôme Advanced Génifique 30ml","Nước hoa Gucci Bloom 50ml",
            "The History of Whoo set","Kem chống nắng Anessa 60ml","SK-II Essence 230ml",
            "Estée Lauder Night Repair 50ml","Chanel No.5 EDP 50ml","Dior Sauvage EDT 100ml",
            "La Mer Moisturizing Cream 30ml","Shiseido Ultimune 50ml","Sulwhasoo First Care 90ml",
            "Clinique Dramatically Different 125ml","MAC Ruby Woo Lipstick","Tom Ford Black Orchid 50ml",
            "Nước hoa YSL Libre 50ml","Kiehl's Ultra Facial Cream 50ml","Laneige Water Bank 50ml",
            "Charlotte Tilbury Pillow Talk","NARS Orgasm Blush","Guerlain Abeille Royale 50ml",
            "Innisfree Green Tea Seed 80ml","Bioderma Sensibio H2O 500ml","Vichy Minéral 89 50ml",
            "Nước hoa Hermès Terre 100ml","Jo Malone Peony & Blush","Givenchy L'Interdit 50ml",
            "Clarins Double Serum 50ml","Origins Mega-Mushroom 50ml","Fresh Soy Face Cleanser 150ml",
            "Bobbi Brown Skin Foundation","Drunk Elephant C-Firma 30ml","Paula's Choice BHA 118ml",
            "AHC Eye Cream 40ml","Missha Time Revolution 150ml","Hera Black Cushion SPF34",
            "Son Dior Rouge 999","Phấn Chanel Les Beiges","Mascara Maybelline Lash Sensational",
        ],
        5: [
            "Chocolate Godiva hộp 16 viên","Bánh quy Bonne Maman 175g","Gift set Tết cao cấp Mena",
            "Kẹo Haribo Goldbären 200g","Chocolate Lindt Swiss 300g","Bánh Yoku Moku 20 cái",
            "Macaron Ladurée hộp 8","Kẹo Ferrero Rocher T30","Gift set rượu vang cao cấp",
            "Bánh LU Pháp assorted 400g","Chocolate Valrhona 250g","Kẹo dừa Bến Tre hộp",
            "Mứt Tết truyền thống","Gift hamper Mena Premium","Bánh trung thu Mena",
            "Trà Dilmah hộp quà","Chocolate Toblerone 360g","Kẹo Mentos hộp thiếc",
            "Gift set café Mena Selection","Bánh pía Sóc Trăng","Hạt điều Bình Phước rang muối",
            "Hạt mắc ca Đắk Lắk 500g","Mứt gừng Huế 300g","Ô mai Hàng Đường Hà Nội",
            "Gift box chocolate & wine","Bánh tráng cuốn Tây Ninh","Hạt mix healthy 500g",
            "Trà oolong Đà Lạt hộp thiếc","Cookie Danish Butter 908g","Chocolate Ghirardelli assorted",
        ],
        6: [
            "Nến thơm Yankee Candle","Bộ dao Zwilling Twin Chef","Bình giữ nhiệt S'well 500ml",
            "Chảo Tefal Unlimited 28cm","Bộ gia vị WMF 6 món","Khuôn silicone Lékué set",
            "Máy xay Vitamix E310","Ấm siêu tốc Smeg 1.7L","Bộ ly thuỷ tinh Riedel 4 cái",
            "Thớt gỗ teak cao cấp","Bình hoa pha lê Bohemia","Khăn tắm Sheridan Úc",
            "Bộ chén dĩa Noritake 12","Bộ nồi Fissler 3 cái","Dao bếp Victorinox Swiss",
            "Máy pha cà phê DeLonghi","Đèn thơm tinh dầu Muji","Bình pha trà Hario V60",
            "Tạp dề da cao cấp","Bộ đũa gỗ mun 10 đôi","Hộp đựng thực phẩm Lock&Lock set",
            "Khay gỗ tràm serving","Bàn ủi hơi nước Philips","Bộ dao thớt Scanpan",
            "Máy ép chậm Kuvings","Bình nước thuỷ tinh Luminarc 1.3L","Bộ ly champagne Schott Zwiesel",
        ],
    }

    for cat_id, n_sku, dom_pct, price_lo, price_hi, cost_margin in cat_config:
        seeds = name_seeds.get(cat_id, [])
        for i in range(n_sku):
            pid += 1
            if i < len(seeds):
                name = seeds[i]
            else:
                # Generate additional names
                base = seeds[i % len(seeds)] if seeds else f"SP-{cat_id}-{i}"
                suffix = ['Premium', 'Đặc biệt', 'Hộp quà', 'Size L', 'New', 'Classic',
                           'Mini', 'Family', 'Organic', 'Limited Edition', 'Set 2', 'Combo']
                name = f"{base} {suffix[i % len(suffix)]}"

            sku = f"SKU{pid:04d}"
            origin = 'domestic' if random.random() < dom_pct else 'imported'
            base_price = round(random.uniform(price_lo, price_hi), -3)  # round to nearest 1000
            cost_price = round(base_price * cost_margin, -3)

            # Pareto popularity weight
            # rank within category: top items get much higher weight
            rank = i + 1
            alpha = 1.2  # Pareto shape
            weight = round(1.0 / (rank ** alpha), 4)

            products.append((pid, sku, name, cat_id, origin, base_price, cost_price, weight))

    # Normalize weights so top 20% ~ 80% of total weight
    total_w = sum(p[7] for p in products)
    products = [(p[0], p[1], p[2], p[3], p[4], p[5], p[6], round(p[7] / total_w * len(products), 4))
                for p in products]

    return products


# =============================================================================
# FB OUTLETS
# =============================================================================
FB_OUTLETS = [
    ('FBO01','LOC05','Steakhouse The Fan','Western Premium',800000,80,250,'2021-03-01'),
    ('FBO02','LOC06','Yum Food Village - Mall SA','Multi-cuisine food court',150000,300,1000,'2020-12-01'),
    ('FBO03','LOC07',"L'Amuse Gourmet Bistro",'French Casual',400000,60,180,'2021-01-01'),
    ('FBO04','LOC08',"Don Cipriani's",'Italian',500000,50,150,'2021-06-01'),
    ('FBO05','LOC09','V-Senses Dining','Vietnamese Modern',350000,70,200,'2021-06-01'),
    ('FBO06','LOC10','Thai Siam Kitchen','Thai',250000,100,200,'2022-01-01'),
    ('FBO07','LOC11','Boulangeries de Saigon','Bakery/Café',120000,30,80,'2024-10-01'),
    ('FBO08','LOC12','Yum Food Outlet - Kim Long','Multi-cuisine compact',130000,80,200,'2022-06-01'),
    ('FBO09','LOC15','Yum Food Village - Nha Trang','Multi-cuisine food court',140000,200,600,'2021-06-01'),
]

# Map outlet_id -> location_id
OUTLET_LOC = {o[0]: o[1] for o in FB_OUTLETS}

# =============================================================================
# TENANTS
# =============================================================================
TENANTS_DATA = [
    # Mall SA tenants (T01-T30)
    ('T01','CGV','Giải trí','L3',800,250000,'2020-12-01','2028-12-01','fixed',5.00,15.00,'LOC01'),
    ('T02','California Fitness','Gym & Spa','L2',600,280000,'2021-01-01','2028-01-01','fixed',3.00,12.00,'LOC01'),
    ('T03','Highlands Coffee','F&B','L5',80,450000,'2021-03-01','2026-03-01','variable',8.00,18.00,'LOC01'),
    ('T04','Phúc Long','F&B','L1',60,500000,'2021-06-01','2026-06-01','variable',8.00,20.00,'LOC01'),
    ('T05','Manwah Hotpot','F&B','L4',250,380000,'2022-01-01','2027-01-01','variable',6.00,14.00,'LOC01'),
    ('T06','Skechers','Thời trang','L1',120,420000,'2025-11-01','2028-11-01','variable',5.00,22.00,'LOC01'),
    ('T07','TWG Tea','F&B Luxury','L1',45,550000,'2025-12-01','2028-12-01','variable',7.00,25.00,'LOC01'),
    ('T08','Pierre Cardin Shoes','Thời trang','L1',80,380000,'2021-06-01','2026-06-01','variable',4.00,15.00,'LOC01'),
    ('T09','Shiseido','Mỹ phẩm','L1',40,520000,'2022-03-01','2027-03-01','variable',6.00,30.00,'LOC01'),
    ('T10','7-Eleven','Tiện lợi','B1',50,400000,'2021-09-01','2026-09-01','variable',5.00,12.00,'LOC01'),
    ('T11','Fashion Line','Thời trang local','L2',150,350000,'2021-06-01','2026-06-01','variable',4.00,2.00,'LOC01'),  # ANOMALY low margin
    ('T12','Bygu','Thời trang local','L2',100,320000,'2022-01-01','2027-01-01','variable',4.00,5.00,'LOC01'),
    ('T13','Gosumo','Thời trang','L1',90,350000,'2022-06-01','2027-06-01','variable',4.00,7.00,'LOC01'),
    ('T14','SkyShop','Thời trang tổng hợp','L2',200,300000,'2023-01-01','2028-01-01','variable',5.00,11.00,'LOC01'),
    ('T15','An Mien Spa','Spa','L3',150,300000,'2022-06-01','2027-06-01','variable',3.00,13.00,'LOC01'),
    ('T17','Guardian','Dược phẩm','B1',70,420000,'2021-03-01','2026-03-01','variable',5.00,16.00,'LOC01'),
    ('T18','Fahasa','Nhà sách','L2',120,280000,'2021-06-01','2026-06-01','variable',3.00,10.00,'LOC01'),
    ('T19','The Coffee House','F&B','L5',65,450000,'2022-06-01','2027-06-01','variable',8.00,17.00,'LOC01'),
    ('T20','Jollibee','F&B','L4',100,400000,'2022-01-01','2027-01-01','variable',6.00,16.00,'LOC01'),
    ('T21','Adidas','Thời trang','L1',130,450000,'2021-09-01','2026-09-01','variable',5.00,20.00,'LOC01'),
    ('T22','Samsung Experience','Điện tử','L1',100,500000,'2022-03-01','2027-03-01','variable',4.00,18.00,'LOC01'),
    ('T23','Kiosk A - Trà sữa KOI','F&B Kiosk','L1',30,600000,'2023-01-01','2026-01-01','variable',10.00,8.00,'LOC01'),
    ('T24','Kiosk B - Bánh tráng','F&B Kiosk','L5',35,550000,'2023-06-01','2026-06-01','variable',10.00,9.00,'LOC01'),
    ('T25','Kiosk C - Nước ép','F&B Kiosk','L5',25,580000,'2024-01-01','2027-01-01','variable',10.00,15.00,'LOC01'),
    ('T26','Pandora','Trang sức','L1',35,600000,'2022-06-01','2027-06-01','variable',5.00,28.00,'LOC01'),
    ('T27','Samsonite','Hành lý','L1',80,400000,'2021-06-01','2026-06-01','variable',4.00,18.00,'LOC01'),
    ('T28',"Levi's",'Thời trang','L2',110,380000,'2022-01-01','2027-01-01','variable',5.00,17.00,'LOC01'),
    ('T29','Starbucks','F&B','L1',75,480000,'2021-03-01','2026-03-01','variable',8.00,22.00,'LOC01'),
    ('T30','Baskin Robbins','F&B','L5',40,500000,'2023-01-01','2028-01-01','variable',7.00,19.00,'LOC01'),
    # Mall Nha Trang tenants (T31-T45)
    ('T31','Lotte Cinema','Giải trí','L3',500,200000,'2021-06-01','2028-06-01','fixed',5.00,13.00,'LOC02'),
    ('T32','Highlands Coffee NT','F&B','L1',60,350000,'2021-06-01','2026-06-01','variable',8.00,18.00,'LOC02'),
    ('T33','Phúc Long NT','F&B','L1',50,380000,'2021-09-01','2026-09-01','variable',8.00,20.00,'LOC02'),
    ('T34','Jollibee NT','F&B','L2',90,320000,'2021-06-01','2026-06-01','variable',6.00,16.00,'LOC02'),
    ('T35','Adidas NT','Thời trang','L1',100,350000,'2022-01-01','2027-01-01','variable',5.00,19.00,'LOC02'),
    ('T36','Guardian NT','Dược phẩm','B1',60,320000,'2021-09-01','2026-09-01','variable',5.00,16.00,'LOC02'),
    ('T37','The Coffee House NT','F&B','L1',55,350000,'2022-06-01','2027-06-01','variable',8.00,17.00,'LOC02'),
    ('T38','Canifa NT','Thời trang','L2',80,300000,'2022-01-01','2027-01-01','variable',4.00,14.00,'LOC02'),
    ('T39','Kiosk D - Kem Fanny','F&B Kiosk','L1',20,450000,'2022-06-01','2027-06-01','variable',10.00,20.00,'LOC02'),
    ('T40','Samsung NT','Điện tử','L1',80,380000,'2022-01-01','2027-01-01','variable',4.00,17.00,'LOC02'),
    ('T41','Miniso NT','Lifestyle','L2',90,280000,'2022-06-01','2027-06-01','variable',5.00,15.00,'LOC02'),
    ('T42','Pizza Hut NT','F&B','L2',100,300000,'2021-09-01','2026-09-01','variable',6.00,15.00,'LOC02'),
    ('T43','Bitis NT','Giày dép','L1',70,320000,'2022-01-01','2027-01-01','variable',4.00,16.00,'LOC02'),
    ('T44','An Mien Spa NT','Spa','L3',120,250000,'2022-06-01','2027-06-01','variable',3.00,12.00,'LOC02'),
    ('T45','Kiosk E - Trà sữa Gong Cha','F&B Kiosk','L1',25,420000,'2023-01-01','2028-01-01','variable',10.00,18.00,'LOC02'),
]

# Base monthly revenue for tenants (VND millions)
TENANT_BASE_REVENUE = {
    'T01': 1800, 'T02': 960, 'T03': 200, 'T04': 180, 'T05': 625,
    'T06': 300, 'T07': 135, 'T08': 160, 'T09': 140, 'T10': 150,
    'T11': 300, 'T12': 130, 'T13': 120, 'T14': 360, 'T15': 300,
    'T17': 210, 'T18': 180, 'T19': 195, 'T20': 350, 'T21': 520,
    'T22': 400, 'T23': 105, 'T24': 87.5, 'T25': 62.5, 'T26': 224,
    'T27': 200, 'T28': 275, 'T29': 330, 'T30': 100,
    # Nha Trang - generally lower traffic
    'T31': 600, 'T32': 120, 'T33': 100, 'T34': 200, 'T35': 250,
    'T36': 120, 'T37': 110, 'T38': 120, 'T39': 60, 'T40': 200,
    'T41': 135, 'T42': 180, 'T43': 112, 'T44': 150, 'T45': 50,
}


# =============================================================================
# PLANNED LOCATIONS
# =============================================================================
PLANNED_LOCATIONS = [
    ('PL01','Nguyễn Thị Thập, Quận 7','Quận 7','HCM',1200,350000000,'Cao','Cao',2,'Siêu thị thường, không premium'),
    ('PL02','Trần Não, Quận 2','Quận 2','HCM',1000,400000000,'Trung bình-Cao','Rất cao',1,'Annam Gourmet'),
    ('PL03','Võ Văn Ngân, Thủ Đức','Thủ Đức','HCM',1500,250000000,'Cao','Trung bình',3,'Siêu thị thường'),
    ('PL04','Phan Đăng Lưu, Phú Nhuận','Phú Nhuận','HCM',800,380000000,'Rất cao','Cao',2,'2 siêu thị thường'),
    ('PL05','Huỳnh Tấn Phát, Nhà Bè','Nhà Bè','HCM',1300,280000000,'Trung bình','Trung bình-Cao',1,'1 siêu thị nhỏ'),
]


# =============================================================================
# EMPLOYEE HEADCOUNT
# =============================================================================
HEADCOUNT = {
    'LOC01': 45, 'LOC02': 25, 'LOC03': 80, 'LOC04': 50,
    'LOC05': 25, 'LOC06': 60, 'LOC07': 20, 'LOC08': 15,
    'LOC09': 22, 'LOC10': 35, 'LOC11': 10, 'LOC12': 25,
    'LOC13': 30, 'LOC14': 15, 'LOC15': 40,
}

# Average salary by location type (VND/month)
AVG_SALARY = {
    'MALL': 12000000, 'SUPERMARKET': 9000000, 'FB': 8500000,
    'DUTYFREE': 11000000, 'BEAUTY': 10000000,
}

LOC_BU = {loc[0]: loc[2] for loc in LOCATIONS}


# =============================================================================
# BASE MONTHLY REVENUE (VND)
# =============================================================================
BASE_REVENUE = {
    ('MALL','LOC01'):       10_000_000_000,
    ('MALL','LOC02'):        4_000_000_000,
    ('SUPERMARKET','LOC03'):12_000_000_000,
    ('SUPERMARKET','LOC04'): 6_000_000_000,
    ('FB','LOC05'):          1_200_000_000,
    ('FB','LOC06'):          2_500_000_000,
    ('FB','LOC07'):            800_000_000,
    ('FB','LOC08'):            600_000_000,
    ('FB','LOC09'):            700_000_000,
    ('FB','LOC10'):            500_000_000,
    ('FB','LOC11'):            400_000_000,
    ('FB','LOC12'):            450_000_000,
    ('FB','LOC15'):          1_000_000_000,
    ('DUTYFREE','LOC13'):    5_000_000_000,
    ('BEAUTY','LOC14'):      2_000_000_000,
}

# FB cost structure by outlet
FB_COST_RATIOS = {
    'FBO01': {'food_cost': 0.28, 'labor': 0.20, 'rent': 0.04, 'utilities': 0.02, 'marketing': 0.04},  # Steakhouse — target ~42% margin
    'FBO02': {'food_cost': 0.33, 'labor': 0.26, 'rent': 0.12, 'utilities': 0.05, 'marketing': 0.06},  # Yum SA
    'FBO03': {'food_cost': 0.30, 'labor': 0.25, 'rent': 0.14, 'utilities': 0.04, 'marketing': 0.06},  # L'Amuse
    'FBO04': {'food_cost': 0.32, 'labor': 0.26, 'rent': 0.15, 'utilities': 0.04, 'marketing': 0.06},  # Don Cipriani
    'FBO05': {'food_cost': 0.28, 'labor': 0.25, 'rent': 0.13, 'utilities': 0.04, 'marketing': 0.05},  # V-Senses
    'FBO06': {'food_cost': 0.32, 'labor': 0.38, 'rent': 0.15, 'utilities': 0.05, 'marketing': 0.07},  # Thai Siam ANOMALY over-labor
    'FBO07': {'food_cost': 0.35, 'labor': 0.24, 'rent': 0.16, 'utilities': 0.04, 'marketing': 0.05},  # Boulangeries
    'FBO08': {'food_cost': 0.33, 'labor': 0.27, 'rent': 0.14, 'utilities': 0.05, 'marketing': 0.06},  # Yum Kim Long
    'FBO09': {'food_cost': 0.33, 'labor': 0.26, 'rent': 0.10, 'utilities': 0.05, 'marketing': 0.06},  # Yum NT
}


# =============================================================================
# METADATA
# =============================================================================
META_TABLES = [
    ('business_units','Các mảng kinh doanh','Menas Group có 5 mảng: TTTM, Siêu thị, F&B, Duty Free, Beauty',5),
    ('locations','Tất cả địa điểm kinh doanh','15 địa điểm trải khắp HCM và Nha Trang',15),
    ('product_categories','Nhóm hàng siêu thị','6 nhóm hàng chính trong siêu thị Mena Gourmet',6),
    ('products','Danh mục sản phẩm','~500 SKU siêu thị với phân bố Pareto',500),
    ('fb_outlets','Chi tiết outlet F&B','9 outlet F&B thuộc Menas Group',9),
    ('tenants','Tenant thuê mặt bằng','~45 tenant tại 2 TTTM',45),
    ('planned_locations','Địa điểm dự kiến','5 vị trí mở rộng tiềm năng',5),
    ('employees_summary','Nhân sự theo tháng','Headcount và chi phí nhân sự',270),
    ('monthly_revenue','Doanh thu tổng hợp','Doanh thu, chi phí, lợi nhuận theo mảng/tháng',270),
    ('supermarket_daily_sales','Bán hàng siêu thị','~160K dòng bán hàng chi tiết theo ngày',160000),
    ('supermarket_shrinkage','Hao hụt hàng hóa','Hao hụt theo nhóm hàng/tháng',216),
    ('fb_monthly_revenue','Doanh thu F&B','Doanh thu, covers, avg check theo outlet/tháng',162),
    ('fb_monthly_costs','Chi phí F&B','Chi phí theo loại: food/labor/rent/utilities/marketing',810),
    ('tenant_monthly_revenue','Doanh thu tenant','Doanh thu gộp tenant theo tháng',810),
    ('promotions','Chương trình khuyến mãi','Khuyến mãi siêu thị và F&B',20),
    ('mall_events','Sự kiện TTTM','Sự kiện tại các TTTM bao gồm bảo trì',16),
    ('mall_daily_footfall','Lượt khách TTTM','Lượt khách hàng ngày theo phân khúc airport/local',2200),
    ('airport_daily_passengers','Khách sân bay TSN','Lượng khách sân bay Tân Sơn Nhất hàng ngày',549),
]

META_COLUMNS = [
    ('monthly_revenue','revenue_vnd','Doanh thu tháng (VND)','SUM, AVG','Tổng doanh thu theo mảng kinh doanh'),
    ('monthly_revenue','cost_vnd','Chi phí tháng (VND)','SUM, AVG','Tổng chi phí vận hành'),
    ('monthly_revenue','profit_vnd','Lợi nhuận tháng (VND)','SUM','Doanh thu - Chi phí'),
    ('supermarket_daily_sales','quantity','Số lượng bán','SUM, AVG','Số lượng sản phẩm bán theo ngày'),
    ('supermarket_daily_sales','selling_price_vnd','Giá bán (VND)','AVG','Giá bán thực tế (có thể khác base)'),
    ('supermarket_daily_sales','discount_amount_vnd','Giảm giá (VND)','SUM','Tổng giảm giá trong chương trình KM'),
    ('supermarket_shrinkage','shrinkage_rate_pct','Tỷ lệ hao hụt (%)','AVG','Tỷ lệ hao hụt trên doanh thu nhóm hàng'),
    ('fb_monthly_revenue','covers','Số lượt khách','SUM, AVG','Tổng lượt khách F&B trong tháng'),
    ('fb_monthly_revenue','avg_check_vnd','Giá trị trung bình/lượt','AVG','Doanh thu / số lượt khách'),
    ('fb_monthly_costs','amount_vnd','Chi phí (VND)','SUM','Chi phí theo loại: food/labor/rent/utilities/marketing'),
    ('tenant_monthly_revenue','gross_revenue_vnd','Doanh thu gộp tenant','SUM, AVG','Doanh thu tenant để tính revenue share'),
    ('mall_daily_footfall','total_count','Lượt khách','SUM, AVG','Lượt khách TTTM hàng ngày theo phân khúc airport/local'),
    ('mall_daily_footfall','segment','Phân khúc khách','GROUP BY','airport = khách sân bay, local = khách địa phương'),
    ('airport_daily_passengers','total_passengers','Tổng lượt khách sân bay','SUM, AVG','Lượng khách TSN hàng ngày'),
]

META_KPI = [
    ('gross_margin_pct','Biên lợi nhuận gộp (%)','(Revenue - Cost) / Revenue × 100','Siêu thị target ≥22%, F&B target ≥30%'),
    ('revenue_per_sqm','Doanh thu/m²','Revenue / Diện tích','So sánh hiệu quả sử dụng mặt bằng'),
    ('shrinkage_rate','Tỷ lệ hao hụt (%)','Shrinkage / Revenue × 100','Target <1.5%, cảnh báo >2%'),
    ('food_cost_ratio','Tỷ lệ food cost (%)','Food Cost / F&B Revenue × 100','Target <35%'),
    ('labor_cost_ratio','Tỷ lệ chi phí nhân sự (%)','Labor Cost / Revenue × 100','Target <28%, cảnh báo >32%'),
    ('avg_check','Giá trị trung bình/lượt (VND)','Revenue / Covers','Theo dõi xu hướng giá trị đơn hàng'),
    ('occupancy_rate','Tỷ lệ lấp đầy (%)','Diện tích cho thuê / Tổng diện tích thuê × 100','Target >90%'),
    ('tenant_rev_per_sqm','Doanh thu tenant/m²','Tenant Revenue / SQM thuê','Đánh giá hiệu quả tenant'),
    ('marketing_roi','ROI Marketing','Revenue Uplift / Marketing Spend','Đánh giá hiệu quả marketing'),
    ('yoy_growth','Tăng trưởng YoY (%)','(Revenue_current - Revenue_prior) / Revenue_prior × 100','Target 15% YoY'),
]

META_GLOSSARY = [
    ('TTTM','Trung tâm thương mại','Shopping mall / Commercial center'),
    ('BU','Business Unit','Mảng kinh doanh'),
    ('SKU','Stock Keeping Unit','Đơn vị quản lý kho'),
    ('Covers','Lượt khách F&B','Số lượt khách phục vụ tại nhà hàng'),
    ('Avg Check','Giá trị trung bình/lượt','Average check per customer'),
    ('Shrinkage','Hao hụt','Tổn thất hàng hóa do hư hỏng, mất cắp, hết hạn'),
    ('Revenue Share','Chia sẻ doanh thu','Tỷ lệ doanh thu tenant chia cho TTTM'),
    ('Footfall','Lượt khách','Số lượt khách đến TTTM/cửa hàng'),
    ('Gross Margin','Biên lợi nhuận gộp','(Doanh thu - Giá vốn) / Doanh thu'),
    ('Food Cost','Chi phí nguyên liệu','Chi phí nguyên liệu thực phẩm F&B'),
    ('Duty Free','Miễn thuế','Cửa hàng bán hàng miễn thuế tại sân bay'),
    ('Ramp-up','Giai đoạn khởi động','Thời gian location mới đạt công suất tối đa'),
]


# =============================================================================
# DDL
# =============================================================================
DDL_SQL = f"""\
USE {DB_NAME};

-- ============================================================
-- DIMENSION TABLES
-- ============================================================

CREATE TABLE business_units (
  id VARCHAR(20) PRIMARY KEY,
  name VARCHAR(100) NOT NULL COMMENT 'Tên mảng kinh doanh',
  description TEXT COMMENT 'Mô tả',
  revenue_model VARCHAR(100) COMMENT 'Mô hình doanh thu'
) COMMENT='Các mảng kinh doanh của Menas Group';

CREATE TABLE locations (
  id VARCHAR(10) PRIMARY KEY,
  name VARCHAR(200) NOT NULL,
  business_unit_id VARCHAR(20) NOT NULL,
  location_type VARCHAR(50) COMMENT 'TTTM/Siêu thị/F&B/Duty Free/Beauty',
  address TEXT,
  city VARCHAR(50),
  district VARCHAR(50),
  sqm DECIMAL(10,2) COMMENT 'Diện tích (m²)',
  opening_date DATE,
  status VARCHAR(20) DEFAULT 'active',
  FOREIGN KEY (business_unit_id) REFERENCES business_units(id)
) COMMENT='Tất cả địa điểm kinh doanh';

CREATE TABLE product_categories (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL COMMENT 'Tên nhóm hàng',
  description TEXT,
  base_margin_pct DECIMAL(5,2) COMMENT 'Biên lợi nhuận gộp cơ bản (%)'
) COMMENT='Nhóm hàng siêu thị';

CREATE TABLE products (
  id INT AUTO_INCREMENT PRIMARY KEY,
  sku VARCHAR(20) UNIQUE NOT NULL,
  name VARCHAR(200) NOT NULL COMMENT 'Tên sản phẩm',
  category_id INT NOT NULL,
  origin VARCHAR(20) COMMENT 'domestic/imported',
  base_price_vnd DECIMAL(15,2) COMMENT 'Giá bán cơ bản (VND)',
  cost_price_vnd DECIMAL(15,2) COMMENT 'Giá vốn (VND)',
  popularity_weight DECIMAL(5,3) COMMENT 'Trọng số phổ biến (Pareto)',
  FOREIGN KEY (category_id) REFERENCES product_categories(id)
) COMMENT='Danh mục sản phẩm siêu thị (~500 SKU)';

CREATE TABLE fb_outlets (
  id VARCHAR(10) PRIMARY KEY,
  location_id VARCHAR(10) NOT NULL,
  name VARCHAR(200) NOT NULL,
  cuisine_type VARCHAR(100),
  avg_check_per_person_vnd DECIMAL(15,2),
  seats INT,
  sqm DECIMAL(10,2),
  opening_date DATE,
  FOREIGN KEY (location_id) REFERENCES locations(id)
) COMMENT='Chi tiết các outlet F&B';

CREATE TABLE tenants (
  id VARCHAR(10) PRIMARY KEY,
  name VARCHAR(200) NOT NULL,
  category VARCHAR(100) COMMENT 'Ngành hàng tenant',
  floor VARCHAR(10),
  sqm_rented DECIMAL(10,2) COMMENT 'Diện tích thuê (m²)',
  rent_per_sqm_monthly DECIMAL(15,2) COMMENT 'Giá thuê/m²/tháng (VND)',
  lease_start DATE,
  lease_end DATE,
  lease_type VARCHAR(20) DEFAULT 'variable' COMMENT 'fixed/variable',
  revenue_share_pct DECIMAL(5,2) COMMENT 'Tỷ lệ chia doanh thu (%)',
  estimated_operating_margin_pct DECIMAL(5,2) COMMENT 'Ước tính biên LN hoạt động (%)',
  location_id VARCHAR(10) NOT NULL,
  FOREIGN KEY (location_id) REFERENCES locations(id)
) COMMENT='Tenant thuê mặt bằng tại TTTM';

CREATE TABLE planned_locations (
  id VARCHAR(10) PRIMARY KEY,
  address TEXT,
  district VARCHAR(50),
  city VARCHAR(50),
  sqm DECIMAL(10,2),
  estimated_monthly_rent_vnd DECIMAL(15,2),
  population_density VARCHAR(20) COMMENT 'Cao/Trung bình/Thấp',
  avg_income_level VARCHAR(20) COMMENT 'Rất cao/Cao/Trung bình',
  competitor_count INT,
  competitor_notes TEXT
) COMMENT='Địa điểm dự kiến mở rộng';

CREATE TABLE employees_summary (
  id INT AUTO_INCREMENT PRIMARY KEY,
  location_id VARCHAR(10) NOT NULL,
  month DATE NOT NULL COMMENT 'Tháng (YYYY-MM-01)',
  headcount INT NOT NULL,
  total_labor_cost_vnd DECIMAL(15,2) COMMENT 'Tổng chi phí nhân sự (VND)',
  FOREIGN KEY (location_id) REFERENCES locations(id),
  UNIQUE KEY (location_id, month)
) COMMENT='Headcount theo location theo tháng';

-- ============================================================
-- FACT TABLES
-- ============================================================

CREATE TABLE monthly_revenue (
  id INT AUTO_INCREMENT PRIMARY KEY,
  business_unit_id VARCHAR(20) NOT NULL,
  location_id VARCHAR(10) NOT NULL,
  month DATE NOT NULL COMMENT 'Tháng (YYYY-MM-01)',
  revenue_vnd DECIMAL(18,2) NOT NULL COMMENT 'Doanh thu (VND)',
  cost_vnd DECIMAL(18,2) COMMENT 'Chi phí (VND)',
  profit_vnd DECIMAL(18,2) COMMENT 'Lợi nhuận (VND)',
  FOREIGN KEY (business_unit_id) REFERENCES business_units(id),
  FOREIGN KEY (location_id) REFERENCES locations(id),
  UNIQUE KEY (business_unit_id, location_id, month),
  INDEX idx_month (month),
  INDEX idx_bu (business_unit_id)
) COMMENT='Doanh thu tổng hợp theo mảng, địa điểm, tháng';

CREATE TABLE supermarket_daily_sales (
  id INT AUTO_INCREMENT PRIMARY KEY,
  date DATE NOT NULL,
  location_id VARCHAR(10) NOT NULL,
  product_id INT NOT NULL,
  quantity INT NOT NULL COMMENT 'Số lượng',
  selling_price_vnd DECIMAL(15,2) NOT NULL COMMENT 'Giá bán (VND)',
  cost_price_vnd DECIMAL(15,2) NOT NULL COMMENT 'Giá vốn (VND)',
  discount_amount_vnd DECIMAL(15,2) DEFAULT 0 COMMENT 'Giảm giá (VND)',
  FOREIGN KEY (location_id) REFERENCES locations(id),
  FOREIGN KEY (product_id) REFERENCES products(id),
  INDEX idx_date (date),
  INDEX idx_location (location_id),
  INDEX idx_product (product_id)
) COMMENT='Bán hàng siêu thị chi tiết theo ngày, sản phẩm';

CREATE TABLE supermarket_shrinkage (
  id INT AUTO_INCREMENT PRIMARY KEY,
  location_id VARCHAR(10) NOT NULL,
  category_id INT NOT NULL,
  month DATE NOT NULL,
  shrinkage_amount_vnd DECIMAL(15,2) NOT NULL COMMENT 'Giá trị hao hụt (VND)',
  shrinkage_rate_pct DECIMAL(5,2) COMMENT 'Tỷ lệ hao hụt (%)',
  FOREIGN KEY (location_id) REFERENCES locations(id),
  FOREIGN KEY (category_id) REFERENCES product_categories(id),
  UNIQUE KEY (location_id, category_id, month)
) COMMENT='Hao hụt hàng hóa siêu thị theo tháng';

CREATE TABLE fb_monthly_revenue (
  id INT AUTO_INCREMENT PRIMARY KEY,
  outlet_id VARCHAR(10) NOT NULL,
  month DATE NOT NULL,
  revenue_vnd DECIMAL(18,2) NOT NULL,
  covers INT COMMENT 'Số lượt khách',
  avg_check_vnd DECIMAL(15,2) COMMENT 'Giá trị trung bình/lượt',
  FOREIGN KEY (outlet_id) REFERENCES fb_outlets(id),
  UNIQUE KEY (outlet_id, month)
) COMMENT='Doanh thu F&B theo outlet theo tháng';

CREATE TABLE fb_monthly_costs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  outlet_id VARCHAR(10) NOT NULL,
  month DATE NOT NULL,
  cost_type VARCHAR(30) NOT NULL COMMENT 'labor/food_cost/rent/utilities/marketing',
  channel VARCHAR(30) COMMENT 'digital/offline/event (only for marketing)',
  amount_vnd DECIMAL(18,2) NOT NULL,
  FOREIGN KEY (outlet_id) REFERENCES fb_outlets(id),
  INDEX idx_outlet_month (outlet_id, month),
  INDEX idx_cost_type (cost_type)
) COMMENT='Chi phí F&B theo outlet, tháng, loại chi phí';

CREATE TABLE tenant_monthly_revenue (
  id INT AUTO_INCREMENT PRIMARY KEY,
  tenant_id VARCHAR(10) NOT NULL,
  month DATE NOT NULL,
  gross_revenue_vnd DECIMAL(18,2) NOT NULL COMMENT 'Doanh thu gộp của tenant (VND)',
  FOREIGN KEY (tenant_id) REFERENCES tenants(id),
  UNIQUE KEY (tenant_id, month),
  INDEX idx_month (month)
) COMMENT='Doanh thu tenant theo tháng';

CREATE TABLE promotions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(200) NOT NULL,
  location_id VARCHAR(10),
  business_unit_id VARCHAR(20),
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  discount_pct DECIMAL(5,2) COMMENT 'Tỷ lệ giảm giá (%)',
  description TEXT,
  FOREIGN KEY (location_id) REFERENCES locations(id),
  FOREIGN KEY (business_unit_id) REFERENCES business_units(id)
) COMMENT='Chương trình khuyến mãi';

CREATE TABLE mall_events (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(200) NOT NULL,
  location_id VARCHAR(10),
  event_date DATE NOT NULL,
  event_type VARCHAR(50) COMMENT 'grand_opening/seasonal/marketing/community/maintenance',
  estimated_footfall_impact_pct DECIMAL(5,2) COMMENT 'Tác động lượt khách (%)',
  description TEXT,
  FOREIGN KEY (location_id) REFERENCES locations(id)
) COMMENT='Sự kiện tại TTTM';

CREATE TABLE mall_daily_footfall (
  id INT AUTO_INCREMENT PRIMARY KEY,
  location_id VARCHAR(10) NOT NULL,
  date DATE NOT NULL,
  segment VARCHAR(20) NOT NULL COMMENT 'airport/local',
  total_count INT NOT NULL COMMENT 'Lượt khách',
  FOREIGN KEY (location_id) REFERENCES locations(id),
  UNIQUE KEY (location_id, date, segment),
  INDEX idx_date (date)
) COMMENT='Lượt khách TTTM hàng ngày theo phân khúc';

CREATE TABLE airport_daily_passengers (
  id INT AUTO_INCREMENT PRIMARY KEY,
  date DATE NOT NULL UNIQUE,
  arrivals INT NOT NULL COMMENT 'Lượt đến',
  departures INT NOT NULL COMMENT 'Lượt đi',
  total_passengers INT NOT NULL COMMENT 'Tổng lượt khách',
  INDEX idx_date (date)
) COMMENT='Lượng khách sân bay Tân Sơn Nhất hàng ngày';
"""


# =============================================================================
# PROMOTIONS & EVENTS
# =============================================================================
PROMOTIONS = [
    (1,'Khai trương Mena Gourmet Airport','LOC03','SUPERMARKET','2024-10-01','2024-10-31',10.00,'Giảm 10% toàn bộ sản phẩm khai trương'),
    (2,'Khai trương Mena Gourmet Celesta','LOC04','SUPERMARKET','2024-11-01','2024-11-30',10.00,'Giảm 10% khai trương Celesta Rise'),
    (3,'Christmas Sale 2024','LOC03','SUPERMARKET','2024-12-15','2024-12-31',8.00,'Chương trình Giáng Sinh 2024'),
    (4,'Christmas Sale 2024 Celesta','LOC04','SUPERMARKET','2024-12-15','2024-12-31',8.00,'Giáng Sinh Celesta Rise'),
    (5,'Tết Ất Tỵ 2025','LOC03','SUPERMARKET','2025-01-15','2025-02-15',12.00,'Đại tiệc Tết - Giảm giá toàn bộ'),
    (6,'Tết Ất Tỵ 2025 Celesta','LOC04','SUPERMARKET','2025-01-15','2025-02-15',12.00,'Tết Celesta Rise'),
    (7,'Valentine Day 2025','LOC03','SUPERMARKET','2025-02-10','2025-02-16',5.00,'Khuyến mãi Valentine'),
    (8,'Summer Fresh 2025','LOC03','SUPERMARKET','2025-06-01','2025-06-30',7.00,'Mùa hè tươi mát - Thực phẩm tươi sống'),
    (9,'Mid-Autumn 2025','LOC03','SUPERMARKET','2025-09-01','2025-09-30',8.00,'Trung Thu - Bánh kẹo quà tặng'),
    (10,'Black Friday 2025','LOC03','SUPERMARKET','2025-11-25','2025-11-30',15.00,'Black Friday - Giảm sâu 15%'),
    (11,'Christmas 2025','LOC03','SUPERMARKET','2025-12-15','2025-12-31',8.00,'Giáng Sinh 2025'),
    (12,'Tết Bính Ngọ 2026','LOC03','SUPERMARKET','2026-01-15','2026-02-28',12.00,'Đại tiệc Tết 2026 - ANOMALY: deep discount'),
    (13,'Tết 2026 Celesta','LOC04','SUPERMARKET','2026-01-15','2026-02-28',12.00,'Tết Celesta 2026'),
    (14,'F&B Happy Hour','LOC06','FB','2025-06-01','2025-08-31',10.00,'Happy Hour 14h-17h tại Yum Food Village'),
    (15,'Steakhouse Anniversary','LOC05','FB','2025-03-01','2025-03-31',15.00,'Kỷ niệm 4 năm Steakhouse The Fan'),
    (16,'Duty Free Summer','LOC13','DUTYFREE','2025-06-01','2025-07-31',5.00,'Khuyến mãi mùa hè Duty Free'),
    (17,'Beauty Grand Opening','LOC14','BEAUTY','2025-12-01','2025-12-31',20.00,'Khai trương Mena Cosmetics'),
    (18,'Mall SA Anniversary','LOC01','MALL','2025-12-01','2025-12-15',None,'Kỷ niệm 5 năm Menas Mall Saigon Airport'),
    (19,'Nha Trang Summer Fest','LOC02','MALL','2025-07-01','2025-07-31',None,'Lễ hội mùa hè Nha Trang'),
    (20,'Spring Sale 2026','LOC03','SUPERMARKET','2026-03-01','2026-03-31',10.00,'Khuyến mãi mùa xuân 2026'),
]

MALL_EVENTS = [
    (1,'Grand Opening Mena Gourmet Airport','LOC03','2024-10-01','grand_opening',50.00,'Khai trương siêu thị Mena Gourmet tại Menas Mall SA'),
    (2,'Grand Opening Mena Gourmet Celesta','LOC04','2024-11-01','grand_opening',40.00,'Khai trương Mena Gourmet Celesta Rise'),
    (3,'Christmas Market 2024','LOC01','2024-12-20','seasonal',30.00,'Chợ Giáng Sinh tại sảnh chính'),
    (4,'Tết Fair 2025','LOC01','2025-01-20','seasonal',35.00,'Hội chợ Tết Ất Tỵ tại Mall SA'),
    (5,'Nha Trang Food Festival','LOC02','2025-07-15','marketing',25.00,'Lễ hội ẩm thực Nha Trang'),
    (6,'Mall SA 5th Anniversary','LOC01','2025-12-01','marketing',40.00,'Kỷ niệm 5 năm thành lập'),
    (7,'Grand Opening Mena Cosmetics','LOC14','2025-12-01','grand_opening',45.00,'Khai trương Mena Cosmetics & Perfumes'),
    (8,'Valentine Wine Tasting','LOC03','2025-02-14','marketing',15.00,'Thử rượu vang Valentine'),
    (9,'Summer BBQ Festival','LOC05','2025-06-15','seasonal',20.00,'Lễ hội BBQ mùa hè tại Steakhouse'),
    (10,'Mid-Autumn Lantern Night','LOC01','2025-09-15','seasonal',25.00,'Đêm hội trung thu thắp đèn lồng'),
    (11,'Black Friday Midnight Sale','LOC01','2025-11-28','marketing',45.00,'Đêm hội mua sắm Black Friday'),
    (12,'Tết Fair 2026','LOC01','2026-01-25','seasonal',35.00,'Hội chợ Tết Bính Ngọ'),
    (13,'Nha Trang Beach Run','LOC02','2026-03-15','community',15.00,'Chạy bộ bãi biển Nha Trang'),
    (14,'Boulangerie Bread Festival','LOC11','2025-05-15','marketing',10.00,'Lễ hội bánh mì Pháp'),
    (15,'Don Cipriani Wine Dinner','LOC08','2025-11-20','marketing',8.00,'Bữa tối rượu vang Ý'),
    (16,'Sửa chữa lối vào B1','LOC01','2026-03-10','maintenance',-15.00,'Sửa chữa lối vào tầng B1, ảnh hưởng khách local'),
]


# =============================================================================
# GENERATION FUNCTIONS
# =============================================================================

def generate_monthly_revenue(fb_costs_by_outlet_month):
    """Generate monthly_revenue rows for all BU/location/month combinations."""
    rows = []
    for mo in MONTHS:
        month_num = mo.month
        for (bu, loc_id), base_rev in BASE_REVENUE.items():
            ru = ramp_up(loc_id, mo)
            if ru == 0:
                continue

            # Location opening check
            loc_open = None
            for l in LOCATIONS:
                if l[0] == loc_id:
                    loc_open = date.fromisoformat(l[8])
                    break
            if loc_open and mo < date(loc_open.year, loc_open.month, 1):
                continue

            season = MONTHLY_SEASON[month_num]
            loc_s = location_season(loc_id, month_num)
            gf = growth_factor(mo)
            noise = random.uniform(0.92, 1.08)

            revenue = base_rev * season * loc_s * gf * noise * ru

            # Anomaly 1: DUTYFREE LOC13 Mar 2026 × 0.95
            if bu == 'DUTYFREE' and loc_id == 'LOC13' and mo == date(2026, 3, 1):
                revenue *= 0.95

            # Anomaly 7: LOC12 declining Jan-Mar 2026
            if loc_id == 'LOC12':
                if mo == date(2026, 1, 1):
                    revenue *= 0.92
                elif mo == date(2026, 2, 1):
                    revenue *= 0.88
                elif mo == date(2026, 3, 1):
                    revenue *= 0.85

            revenue = round(revenue, 2)

            # Cost calculation
            if bu == 'MALL':
                cost = round(revenue * 0.35, 2)
            elif bu == 'SUPERMARKET':
                # Base cost ratio 0.78, shifts to 0.787 in Q1/2026
                if mo >= date(2026, 1, 1):
                    cost_ratio = 0.787
                else:
                    cost_ratio = 0.78
                cost = round(revenue * cost_ratio, 2)
            elif bu == 'FB':
                # Sum costs from fb_monthly_costs for this outlet
                outlet_id = None
                for o in FB_OUTLETS:
                    if o[1] == loc_id:
                        outlet_id = o[0]
                        break
                if outlet_id and (outlet_id, mo) in fb_costs_by_outlet_month:
                    cost = round(fb_costs_by_outlet_month[(outlet_id, mo)], 2)
                else:
                    cost = round(revenue * 0.80, 2)
            elif bu == 'DUTYFREE':
                cost = round(revenue * 0.55, 2)
            elif bu == 'BEAUTY':
                cost = round(revenue * 0.60, 2)
            else:
                cost = round(revenue * 0.75, 2)

            profit = round(revenue - cost, 2)
            rows.append((bu, loc_id, mo, revenue, cost, profit))

    return rows


def generate_fb_revenue():
    """Generate fb_monthly_revenue rows."""
    rows = []
    for mo in MONTHS:
        month_num = mo.month
        for outlet in FB_OUTLETS:
            oid = outlet[0]
            loc_id = outlet[1]
            avg_check = outlet[4]

            # Location opening check
            loc_open = date.fromisoformat(outlet[7])
            if mo < date(loc_open.year, loc_open.month, 1):
                continue

            bu_loc = ('FB', loc_id)
            if bu_loc not in BASE_REVENUE:
                continue

            base_rev = BASE_REVENUE[bu_loc]
            season = MONTHLY_SEASON[month_num]
            loc_s = location_season(loc_id, month_num)
            gf = growth_factor(mo)
            noise = random.uniform(0.93, 1.07)

            revenue = base_rev * season * loc_s * gf * noise

            # Anomaly 7: LOC12 declining
            if loc_id == 'LOC12':
                if mo == date(2026, 1, 1):
                    revenue *= 0.92
                elif mo == date(2026, 2, 1):
                    revenue *= 0.88
                elif mo == date(2026, 3, 1):
                    revenue *= 0.85

            revenue = round(revenue, 2)
            covers = int(revenue / avg_check)
            actual_avg_check = round(revenue / covers, 2) if covers > 0 else 0

            rows.append((oid, mo, revenue, covers, actual_avg_check))

    return rows


def generate_fb_costs(fb_revenue_rows):
    """Generate fb_monthly_costs rows. Returns rows and a lookup dict."""
    rows = []
    costs_lookup = {}  # (outlet_id, month) -> total cost

    fb_rev_lookup = {}
    for r in fb_revenue_rows:
        fb_rev_lookup[(r[0], r[1])] = r[2]  # (outlet_id, month) -> revenue

    for mo in MONTHS:
        for outlet in FB_OUTLETS:
            oid = outlet[0]
            loc_id = outlet[1]

            key = (oid, mo)
            if key not in fb_rev_lookup:
                continue

            revenue = fb_rev_lookup[key]
            ratios = FB_COST_RATIOS[oid]
            total_cost = 0

            for cost_type in ['food_cost', 'labor', 'rent', 'utilities']:
                base_ratio = ratios[cost_type]
                noise = random.uniform(0.97, 1.03)

                # Anomaly: LOC12 costs stay constant even as revenue declines
                if loc_id == 'LOC12' and mo >= date(2026, 1, 1):
                    # Use pre-decline revenue for cost calculation
                    base_rev_for_cost = BASE_REVENUE[('FB', loc_id)]
                    season = MONTHLY_SEASON[mo.month]
                    gf = growth_factor(mo)
                    stable_rev = base_rev_for_cost * season * gf * 1.0
                    amount = round(stable_rev * base_ratio * noise, 2)
                else:
                    amount = round(revenue * base_ratio * noise, 2)

                total_cost += amount
                rows.append((oid, mo, cost_type, None, amount))

            # Marketing: split into 3 channels
            mkt_ratio = ratios['marketing']
            mkt_total = revenue * mkt_ratio

            # Anomaly 11: Thai Siam marketing Feb/Mar 2026 spike
            if oid == 'FBO06':
                base_mkt = 35_000_000  # 35M baseline
                if mo == date(2026, 2, 1) or mo == date(2026, 3, 1):
                    mkt_total = 45_000_000
                else:
                    # Correlate with revenue (r=0.75)
                    rev_factor = revenue / BASE_REVENUE[('FB', loc_id)]
                    mkt_total = base_mkt * (0.25 + 0.75 * rev_factor) * random.uniform(0.90, 1.10)

            # Anomaly 12: Steakhouse marketing cut Jan-Mar 2026
            if oid == 'FBO01':
                base_mkt = 75_000_000  # 75M baseline
                if mo >= date(2026, 1, 1) and mo <= date(2026, 3, 1):
                    mkt_total = 60_000_000 * random.uniform(0.92, 1.08)
                else:
                    # Low correlation with revenue (r~0.15)
                    mkt_total = base_mkt * random.uniform(0.85, 1.15)

            # Split marketing into channels
            digital_pct = random.uniform(0.35, 0.45)
            offline_pct = random.uniform(0.35, 0.45)
            event_pct = 1.0 - digital_pct - offline_pct

            mkt_digital = round(mkt_total * digital_pct, 2)
            mkt_offline = round(mkt_total * offline_pct, 2)
            mkt_event = round(mkt_total * event_pct, 2)

            rows.append((oid, mo, 'marketing', 'digital', mkt_digital))
            rows.append((oid, mo, 'marketing', 'offline', mkt_offline))
            rows.append((oid, mo, 'marketing', 'event', mkt_event))

            total_cost += mkt_digital + mkt_offline + mkt_event
            costs_lookup[key] = total_cost

    return rows, costs_lookup


def generate_tenant_revenue():
    """Generate tenant_monthly_revenue rows."""
    rows = []
    for mo in MONTHS:
        month_num = mo.month
        for t in TENANTS_DATA:
            tid = t[0]
            loc_id = t[11]
            lease_start = date.fromisoformat(t[6])
            lease_end = date.fromisoformat(t[7])

            # Only generate if tenant active during this month
            if mo < date(lease_start.year, lease_start.month, 1):
                continue
            if mo > date(lease_end.year, lease_end.month, 1):
                continue

            base = TENANT_BASE_REVENUE.get(tid, 100) * 1_000_000  # Convert to VND
            season = MONTHLY_SEASON[month_num]
            loc_s = location_season(loc_id, month_num)
            gf = growth_factor(mo)
            noise = random.uniform(0.90, 1.10)

            revenue = base * season * loc_s * gf * noise

            # Anomaly 9: Fashion Line (T11) declining 40% YoY
            if tid == 'T11':
                months_since = (mo.year - START_DATE.year) * 12 + (mo.month - START_DATE.month)
                decline_factor = max(0.4, 1.0 - (0.40 * months_since / 17))  # 40% decline over 18 months
                revenue *= decline_factor

            # Anomaly: Skechers (T06) and TWG Tea (T07) × 1.20 (new tenant surge)
            if tid == 'T06':
                revenue *= 1.20
            if tid == 'T07':
                revenue *= 1.20

            revenue = round(revenue, 2)
            rows.append((tid, mo, revenue))

    return rows


def generate_employees():
    """Generate employees_summary rows."""
    rows = []
    eid = 0
    for mo in MONTHS:
        for loc in LOCATIONS:
            loc_id = loc[0]
            bu = loc[2]

            # Check if location is open
            loc_open = date.fromisoformat(loc[8])
            if mo < date(loc_open.year, loc_open.month, 1):
                continue

            hc = HEADCOUNT[loc_id]
            avg_sal = AVG_SALARY[bu]
            # Small monthly variation
            hc_actual = hc + random.randint(-2, 2)
            hc_actual = max(hc_actual, int(hc * 0.8))
            labor_cost = round(hc_actual * avg_sal * random.uniform(0.95, 1.05), 2)

            eid += 1
            rows.append((loc_id, mo, hc_actual, labor_cost))

    return rows


def generate_shrinkage(products):
    """Generate supermarket_shrinkage rows."""
    rows = []
    # Shrinkage rates by (location, category)
    shrinkage_rates = {}
    for cid in range(1, 7):
        shrinkage_rates[('LOC03', cid)] = random.uniform(1.2, 1.5)
    # LOC04 anomaly: high shrinkage for specific categories
    shrinkage_rates[('LOC04', 1)] = 3.5   # Thực phẩm tươi sống
    shrinkage_rates[('LOC04', 4)] = 2.1   # Mỹ phẩm
    shrinkage_rates[('LOC04', 3)] = 1.8   # Rượu bia
    for cid in [2, 5, 6]:
        shrinkage_rates[('LOC04', cid)] = 1.5

    for mo in MONTHS:
        for loc_id in ['LOC03', 'LOC04']:
            loc_open = date(2024, 10, 1) if loc_id == 'LOC03' else date(2024, 11, 1)
            if mo < loc_open:
                continue

            for cid in range(1, 7):
                rate = shrinkage_rates.get((loc_id, cid), 1.5)
                noise = random.uniform(0.85, 1.15)
                actual_rate = round(rate * noise, 2)
                # Estimate category revenue (rough: total supermarket rev / 6)
                base_rev = BASE_REVENUE[('SUPERMARKET', loc_id)]
                cat_rev = base_rev * MONTHLY_SEASON[mo.month] * growth_factor(mo) * ramp_up(loc_id, mo) / 6
                shrinkage_amount = round(cat_rev * actual_rate / 100, 2)
                rows.append((loc_id, cid, mo, shrinkage_amount, actual_rate))

    return rows


def generate_footfall_and_airport():
    """Generate mall_daily_footfall (with airport/local segments) + airport_daily_passengers."""
    footfall_rows = []   # (location_id, date, segment, count)
    airport_rows = []    # (date, arrivals, departures, total)

    # Base daily footfall for malls: LOC01=12K (75% airport, 25% local), LOC02=5K (all local/tourist)
    BASE_AIRPORT_PASSENGERS = 115000  # TSN ~115K/day base

    current = START_DATE
    while current <= END_DATE:
        mo_first = date(current.year, current.month, 1)
        season = MONTHLY_SEASON[current.month]
        weekly = WEEKLY_PATTERN[current.weekday()]
        gf = growth_factor(mo_first)

        # Airport passengers
        ap_noise = random.uniform(0.90, 1.10)
        total_pax = int(BASE_AIRPORT_PASSENGERS * season * weekly * gf * ap_noise)
        # Post-Tet dip in March 2026: airport traffic drops 8%
        if current.year == 2026 and current.month == 3:
            total_pax = int(total_pax * 0.92)
        arrivals = int(total_pax * random.uniform(0.48, 0.52))
        departures = total_pax - arrivals
        airport_rows.append((current, arrivals, departures, total_pax))

        # Mall SA (LOC01): 12K base, 75% airport-driven, 25% local
        base_mall_sa = 12000
        loc_s = 1.0
        noise_a = random.uniform(0.90, 1.10)
        noise_l = random.uniform(0.85, 1.15)

        airport_count = int(base_mall_sa * 0.75 * season * weekly * gf * noise_a)
        local_count = int(base_mall_sa * 0.25 * season * weekly * gf * noise_l)

        # Anomaly 8: local segment dip 10-16 Mar 2026 (B1 renovation)
        if date(2026, 3, 10) <= current <= date(2026, 3, 16):
            local_count = int(local_count * 0.85)

        footfall_rows.append(('LOC01', current, 'airport', airport_count))
        footfall_rows.append(('LOC01', current, 'local', local_count))

        # Mall Nha Trang (LOC02): 5K base, all tourist/local
        base_mall_nt = 5000
        loc_s_nt = NT_SEASON[current.month]
        noise_nt = random.uniform(0.85, 1.15)
        nt_count = int(base_mall_nt * season * loc_s_nt * weekly * gf * noise_nt)
        footfall_rows.append(('LOC02', current, 'local', nt_count))

        current += timedelta(days=1)

    return footfall_rows, airport_rows


def generate_supermarket_sales(products):
    """Generate supermarket_daily_sales rows (~160K+)."""
    rows = []

    # Build product lookup by category for weighted selection
    prod_by_cat = defaultdict(list)
    prod_weights_by_cat = defaultdict(list)
    prod_lookup = {}
    for p in products:
        pid, sku, name, cat_id, origin, base_price, cost_price, weight = p
        prod_by_cat[cat_id].append(p)
        prod_weights_by_cat[cat_id].append(weight)
        prod_lookup[pid] = p

    # All products flat list with weights for selection
    all_products = list(products)
    # Category volume multipliers: fresh food dominates (high volume, low price)
    # Imported/premium categories are low volume but high unit price
    # Target: ~30% imported revenue share baseline, rising to ~38% via anomaly
    CAT_VOL_MULT = {1: 7.0, 2: 0.35, 3: 0.35, 4: 0.22, 5: 0.6, 6: 0.22}
    base_weights = []
    for p in all_products:
        w = p[7] * CAT_VOL_MULT.get(p[3], 1.0)
        if p[4] == 'imported':
            w *= 0.35
        base_weights.append(w)

    # Check for active promotions on a given date
    def get_discount_rate(dt, loc_id):
        for promo in PROMOTIONS:
            p_loc = promo[2]
            p_start = date.fromisoformat(promo[4]) if isinstance(promo[4], str) else promo[4]
            p_end = date.fromisoformat(promo[5]) if isinstance(promo[5], str) else promo[5]
            p_disc = promo[6]
            if p_loc == loc_id and p_start <= dt <= p_end and p_disc is not None:
                return p_disc / 100.0
        return 0.0

    # Anomaly 3: imported mix shift from Oct 2025
    # Gradually boost imported selection from 30% → 38% revenue share
    def imported_boost_factor(dt):
        """Multiplier for imported product weights after Oct 2025."""
        if dt < date(2025, 10, 1):
            return 1.0
        months = (dt.year - 2025) * 12 + dt.month - 10
        # Increase imported weight by up to 50% over 6 months to shift 30%→38% revenue share
        return 1.0 + min(0.50, months * 0.083)

    current = START_DATE
    while current <= END_DATE:
        for loc_id in ['LOC03', 'LOC04']:
            loc_open = date(2024, 10, 1) if loc_id == 'LOC03' else date(2024, 11, 1)
            if current < loc_open:
                continue

            mo_first = date(current.year, current.month, 1)
            season = MONTHLY_SEASON[current.month]
            weekly = WEEKLY_PATTERN[current.weekday()]
            gf = growth_factor(mo_first)
            ru = ramp_up(loc_id, mo_first)
            noise = random.uniform(0.88, 1.12)

            # Base line items per day
            base_items = 350 if loc_id == 'LOC03' else 200
            n_items = int(base_items * season * weekly * gf * ru * noise)
            n_items = max(50, min(n_items, 600))

            # Pick distinct products for the day
            n_distinct = min(n_items, len(all_products))

            # Adjust weights for imported mix shift anomaly
            imp_boost = imported_boost_factor(current)

            adjusted_weights = []
            for i, p in enumerate(all_products):
                w = base_weights[i]
                if p[4] == 'imported':
                    w *= imp_boost
                adjusted_weights.append(w)

            # Normalize
            total_w = sum(adjusted_weights)
            probs = [w / total_w for w in adjusted_weights]

            # Select products (with replacement for speed, but aggregate per product)
            selected_indices = random.choices(range(len(all_products)), weights=probs, k=n_items)

            # Aggregate by product
            product_counts = defaultdict(int)
            for idx in selected_indices:
                product_counts[idx] += 1

            disc_rate = get_discount_rate(current, loc_id)

            # Anomaly 4: Tết promo deep discount Jan 15 - Feb 28, 2026
            if date(2026, 1, 15) <= current <= date(2026, 2, 28):
                disc_rate = max(disc_rate, 0.12)

            for idx, count in product_counts.items():
                p = all_products[idx]
                pid = p[0]
                base_price = p[5]
                cost_price = p[6]
                cat_id = p[3]
                cat_season = CAT_SEASON.get((cat_id, current.month), 1.0)

                # Quantity per line: mostly 1-3, sometimes more
                qty = count  # aggregate count from selections
                if qty > 10:
                    qty = random.randint(5, 10)

                sell_price = round(base_price * random.uniform(0.97, 1.03), 2)
                discount = round(sell_price * qty * disc_rate, 2) if disc_rate > 0 else 0

                rows.append((current, loc_id, pid, qty, sell_price, cost_price, discount))

        current += timedelta(days=1)

    return rows


# =============================================================================
# WRITE SQL FILES
# =============================================================================

def main():
    os.makedirs(SQL_DIR, exist_ok=True)
    print(f"Generating Menas demo data in {SQL_DIR}/")
    print(f"Date range: {START_DATE} to {END_DATE} ({len(MONTHS)} months)")

    # Generate products
    print("  Generating products (~500 SKU)...")
    products = generate_products()
    print(f"    -> {len(products)} products")

    # Generate FB revenue first (needed for costs)
    print("  Generating F&B revenue...")
    fb_rev_rows = generate_fb_revenue()
    print(f"    -> {len(fb_rev_rows)} rows")

    # Generate FB costs
    print("  Generating F&B costs...")
    fb_cost_rows, fb_costs_lookup = generate_fb_costs(fb_rev_rows)
    print(f"    -> {len(fb_cost_rows)} rows")

    # Generate monthly revenue (needs fb_costs_lookup)
    print("  Generating monthly revenue...")
    monthly_rev_rows = generate_monthly_revenue(fb_costs_lookup)
    print(f"    -> {len(monthly_rev_rows)} rows")

    # Generate tenant revenue
    print("  Generating tenant revenue...")
    tenant_rev_rows = generate_tenant_revenue()
    print(f"    -> {len(tenant_rev_rows)} rows")

    # Generate employees
    print("  Generating employees summary...")
    emp_rows = generate_employees()
    print(f"    -> {len(emp_rows)} rows")

    # Generate shrinkage
    print("  Generating supermarket shrinkage...")
    shrinkage_rows = generate_shrinkage(products)
    print(f"    -> {len(shrinkage_rows)} rows")

    # Generate footfall + airport passengers
    print("  Generating footfall & airport passengers...")
    footfall_rows, airport_rows = generate_footfall_and_airport()
    print(f"    -> {len(footfall_rows)} footfall rows, {len(airport_rows)} airport rows")

    # Generate supermarket daily sales (LARGE)
    print("  Generating supermarket daily sales (this may take a moment)...")
    sales_rows = generate_supermarket_sales(products)
    print(f"    -> {len(sales_rows)} rows")

    # =========================================================================
    # WRITE SQL FILES
    # =========================================================================
    print("\nWriting SQL files...")

    # -- 01_ddl_schema.sql --
    with open(os.path.join(SQL_DIR, '01_ddl_schema.sql'), 'w', encoding='utf-8') as f:
        f.write("-- ============================================================\n")
        f.write("-- 01_ddl_schema.sql\n")
        f.write(f"-- Database: {DB_NAME}\n")
        f.write("-- Menas Group — Multi-Business Demo Schema\n")
        f.write("-- ============================================================\n\n")
        f.write(DDL_SQL)
        f.write("\n")
    print("  01_ddl_schema.sql")

    # -- 02_metadata.sql --
    with open(os.path.join(SQL_DIR, '02_metadata.sql'), 'w', encoding='utf-8') as f:
        f.write("-- ============================================================\n")
        f.write("-- 02_metadata.sql\n")
        f.write(f"-- Database: {DB_NAME}\n")
        f.write("-- Menas Group — Metadata\n")
        f.write("-- ============================================================\n\n")
        f.write(f"USE {DB_NAME};\n\n")

        # _meta_tables
        f.write("-- Metadata: Tables\n")
        f.write("CREATE TABLE IF NOT EXISTS _meta_tables (\n")
        f.write("  table_name VARCHAR(100) PRIMARY KEY,\n")
        f.write("  description VARCHAR(500),\n")
        f.write("  notes TEXT,\n")
        f.write("  approx_rows INT\n")
        f.write(") COMMENT='Mô tả các bảng dữ liệu';\n\n")
        write_inserts(f, '_meta_tables',
                      ['table_name', 'description', 'notes', 'approx_rows'],
                      META_TABLES)

        # _meta_columns
        f.write("-- Metadata: Key Columns\n")
        f.write("CREATE TABLE IF NOT EXISTS _meta_columns (\n")
        f.write("  id INT AUTO_INCREMENT PRIMARY KEY,\n")
        f.write("  table_name VARCHAR(100),\n")
        f.write("  column_name VARCHAR(100),\n")
        f.write("  description VARCHAR(500),\n")
        f.write("  aggregation_hint VARCHAR(100),\n")
        f.write("  notes TEXT\n")
        f.write(") COMMENT='Mô tả các cột quan trọng';\n\n")
        meta_col_rows = [(r[0], r[1], r[2], r[3], r[4]) for r in META_COLUMNS]
        write_inserts(f, '_meta_columns',
                      ['table_name', 'column_name', 'description', 'aggregation_hint', 'notes'],
                      meta_col_rows)

        # _meta_kpi
        f.write("-- Metadata: KPIs\n")
        f.write("CREATE TABLE IF NOT EXISTS _meta_kpi (\n")
        f.write("  kpi_code VARCHAR(50) PRIMARY KEY,\n")
        f.write("  kpi_name VARCHAR(200),\n")
        f.write("  formula TEXT,\n")
        f.write("  benchmark TEXT\n")
        f.write(") COMMENT='Các KPI chính';\n\n")
        write_inserts(f, '_meta_kpi',
                      ['kpi_code', 'kpi_name', 'formula', 'benchmark'],
                      META_KPI)

        # _meta_glossary
        f.write("-- Metadata: Glossary\n")
        f.write("CREATE TABLE IF NOT EXISTS _meta_glossary (\n")
        f.write("  term VARCHAR(100) PRIMARY KEY,\n")
        f.write("  definition_vi VARCHAR(500),\n")
        f.write("  definition_en VARCHAR(500)\n")
        f.write(") COMMENT='Bảng thuật ngữ';\n\n")
        write_inserts(f, '_meta_glossary',
                      ['term', 'definition_vi', 'definition_en'],
                      META_GLOSSARY)

    print("  02_metadata.sql")

    # -- 03_master_data.sql --
    with open(os.path.join(SQL_DIR, '03_master_data.sql'), 'w', encoding='utf-8') as f:
        f.write("-- ============================================================\n")
        f.write("-- 03_master_data.sql\n")
        f.write(f"-- Database: {DB_NAME}\n")
        f.write("-- Menas Group — Master/Dimension Data\n")
        f.write("-- ============================================================\n\n")
        f.write(f"USE {DB_NAME};\n")
        f.write("SET FOREIGN_KEY_CHECKS = 0;\n\n")

        # business_units
        f.write(f"-- business_units: {len(BUSINESS_UNITS)} records\n")
        write_inserts(f, 'business_units', ['id', 'name', 'description', 'revenue_model'],
                      BUSINESS_UNITS)

        # locations
        f.write(f"-- locations: {len(LOCATIONS)} records\n")
        loc_rows = [(l[0], l[1], l[2], l[3], l[4], l[5], l[6], l[7], l[8], l[9]) for l in LOCATIONS]
        write_inserts(f, 'locations',
                      ['id', 'name', 'business_unit_id', 'location_type', 'address', 'city', 'district', 'sqm', 'opening_date', 'status'],
                      loc_rows)

        # product_categories
        f.write(f"-- product_categories: {len(PRODUCT_CATEGORIES)} records\n")
        write_inserts(f, 'product_categories', ['id', 'name', 'description', 'base_margin_pct'],
                      PRODUCT_CATEGORIES)

        # products
        f.write(f"-- products: {len(products)} records\n")
        write_inserts(f, 'products',
                      ['id', 'sku', 'name', 'category_id', 'origin', 'base_price_vnd', 'cost_price_vnd', 'popularity_weight'],
                      products, batch=100)

        # fb_outlets
        f.write(f"-- fb_outlets: {len(FB_OUTLETS)} records\n")
        write_inserts(f, 'fb_outlets',
                      ['id', 'location_id', 'name', 'cuisine_type', 'avg_check_per_person_vnd', 'seats', 'sqm', 'opening_date'],
                      FB_OUTLETS)

        # tenants
        f.write(f"-- tenants: {len(TENANTS_DATA)} records\n")
        tenant_rows = [(t[0], t[1], t[2], t[3], t[4], t[5], t[6], t[7], t[8], t[9], t[10], t[11]) for t in TENANTS_DATA]
        write_inserts(f, 'tenants',
                      ['id', 'name', 'category', 'floor', 'sqm_rented', 'rent_per_sqm_monthly',
                       'lease_start', 'lease_end', 'lease_type', 'revenue_share_pct',
                       'estimated_operating_margin_pct', 'location_id'],
                      tenant_rows)

        # planned_locations
        f.write(f"-- planned_locations: {len(PLANNED_LOCATIONS)} records\n")
        write_inserts(f, 'planned_locations',
                      ['id', 'address', 'district', 'city', 'sqm', 'estimated_monthly_rent_vnd',
                       'population_density', 'avg_income_level', 'competitor_count', 'competitor_notes'],
                      PLANNED_LOCATIONS)

        # promotions
        f.write(f"-- promotions: {len(PROMOTIONS)} records\n")
        write_inserts(f, 'promotions',
                      ['id', 'name', 'location_id', 'business_unit_id', 'start_date', 'end_date', 'discount_pct', 'description'],
                      PROMOTIONS)

        # mall_events
        f.write(f"-- mall_events: {len(MALL_EVENTS)} records\n")
        write_inserts(f, 'mall_events',
                      ['id', 'name', 'location_id', 'event_date', 'event_type', 'estimated_footfall_impact_pct', 'description'],
                      MALL_EVENTS)

        f.write("\nSET FOREIGN_KEY_CHECKS = 1;\n")
    print("  03_master_data.sql")

    # -- 04_a_monthly_revenue.sql --
    with open(os.path.join(SQL_DIR, '04_a_monthly_revenue.sql'), 'w', encoding='utf-8') as f:
        f.write("-- 04_a_monthly_revenue.sql\n")
        f.write(f"-- Database: {DB_NAME}\n")
        f.write("-- Menas Group — Monthly Revenue Data\n\n")
        f.write(f"USE {DB_NAME};\n\n")
        f.write(f"-- monthly_revenue: {len(monthly_rev_rows)} records\n")
        write_inserts(f, 'monthly_revenue',
                      ['business_unit_id', 'location_id', 'month', 'revenue_vnd', 'cost_vnd', 'profit_vnd'],
                      monthly_rev_rows)
    print("  04_a_monthly_revenue.sql")

    # -- 04_b_supermarket_sales.sql -- (LARGE, batch 500)
    with open(os.path.join(SQL_DIR, '04_b_supermarket_sales.sql'), 'w', encoding='utf-8') as f:
        f.write("-- 04_b_supermarket_sales.sql\n")
        f.write(f"-- Database: {DB_NAME}\n")
        f.write("-- Menas Group — Supermarket Daily Sales\n\n")
        f.write(f"USE {DB_NAME};\n")
        f.write("SET FOREIGN_KEY_CHECKS = 0;\n")
        f.write("SET autocommit = 0;\n\n")
        f.write(f"-- supermarket_daily_sales: {len(sales_rows)} records\n\n")

        cols = ['date', 'location_id', 'product_id', 'quantity', 'selling_price_vnd', 'cost_price_vnd', 'discount_amount_vnd']
        col_str = ', '.join(cols)
        for i in range(0, len(sales_rows), BATCH):
            chunk = sales_rows[i:i + BATCH]
            vals = ['(' + ', '.join(esc(v) for v in row) + ')' for row in chunk]
            f.write(f"INSERT INTO `supermarket_daily_sales` ({col_str}) VALUES\n")
            f.write(',\n'.join(vals))
            f.write(';\n\n')
            # Commit every 5000 rows
            if (i // BATCH) % 10 == 9:
                f.write("COMMIT;\n\n")

        f.write("\nCOMMIT;\nSET autocommit = 1;\nSET FOREIGN_KEY_CHECKS = 1;\n")
    print("  04_b_supermarket_sales.sql")

    # -- 04_c_fb_data.sql --
    with open(os.path.join(SQL_DIR, '04_c_fb_data.sql'), 'w', encoding='utf-8') as f:
        f.write("-- 04_c_fb_data.sql\n")
        f.write(f"-- Database: {DB_NAME}\n")
        f.write("-- Menas Group — F&B Revenue & Costs\n\n")
        f.write(f"USE {DB_NAME};\n\n")

        f.write(f"-- fb_monthly_revenue: {len(fb_rev_rows)} records\n")
        write_inserts(f, 'fb_monthly_revenue',
                      ['outlet_id', 'month', 'revenue_vnd', 'covers', 'avg_check_vnd'],
                      fb_rev_rows)

        f.write(f"-- fb_monthly_costs: {len(fb_cost_rows)} records\n")
        write_inserts(f, 'fb_monthly_costs',
                      ['outlet_id', 'month', 'cost_type', 'channel', 'amount_vnd'],
                      fb_cost_rows)
    print("  04_c_fb_data.sql")

    # -- 04_d_tenant_data.sql --
    with open(os.path.join(SQL_DIR, '04_d_tenant_data.sql'), 'w', encoding='utf-8') as f:
        f.write("-- 04_d_tenant_data.sql\n")
        f.write(f"-- Database: {DB_NAME}\n")
        f.write("-- Menas Group — Tenant Monthly Revenue\n\n")
        f.write(f"USE {DB_NAME};\n\n")
        f.write(f"-- tenant_monthly_revenue: {len(tenant_rev_rows)} records\n")
        write_inserts(f, 'tenant_monthly_revenue',
                      ['tenant_id', 'month', 'gross_revenue_vnd'],
                      tenant_rev_rows)
    print("  04_d_tenant_data.sql")

    # -- 04_e_footfall_airport.sql --
    with open(os.path.join(SQL_DIR, '04_e_footfall_airport.sql'), 'w', encoding='utf-8') as f:
        f.write("-- 04_e_footfall_airport.sql\n")
        f.write(f"-- Database: {DB_NAME}\n")
        f.write("-- Menas Group — Mall Footfall & Airport Passengers\n\n")
        f.write(f"USE {DB_NAME};\n\n")
        f.write(f"-- mall_daily_footfall: {len(footfall_rows)} records\n")
        write_inserts(f, 'mall_daily_footfall',
                      ['location_id', 'date', 'segment', 'total_count'],
                      footfall_rows)
        f.write(f"\n-- airport_daily_passengers: {len(airport_rows)} records\n")
        write_inserts(f, 'airport_daily_passengers',
                      ['date', 'arrivals', 'departures', 'total_passengers'],
                      airport_rows)
    print("  04_e_footfall_airport.sql")

    # -- 04_f_shrinkage_promos_events.sql --
    with open(os.path.join(SQL_DIR, '04_f_shrinkage_promos_events.sql'), 'w', encoding='utf-8') as f:
        f.write("-- 04_f_shrinkage_promos_events.sql\n")
        f.write(f"-- Database: {DB_NAME}\n")
        f.write("-- Menas Group — Shrinkage Data\n\n")
        f.write(f"USE {DB_NAME};\n\n")
        f.write(f"-- supermarket_shrinkage: {len(shrinkage_rows)} records\n")
        write_inserts(f, 'supermarket_shrinkage',
                      ['location_id', 'category_id', 'month', 'shrinkage_amount_vnd', 'shrinkage_rate_pct'],
                      shrinkage_rows)
    print("  04_f_shrinkage_promos_events.sql")

    # -- 04_g_employees.sql --
    with open(os.path.join(SQL_DIR, '04_g_employees.sql'), 'w', encoding='utf-8') as f:
        f.write("-- 04_g_employees.sql\n")
        f.write(f"-- Database: {DB_NAME}\n")
        f.write("-- Menas Group — Employee Summary\n\n")
        f.write(f"USE {DB_NAME};\n\n")
        f.write(f"-- employees_summary: {len(emp_rows)} records\n")
        write_inserts(f, 'employees_summary',
                      ['location_id', 'month', 'headcount', 'total_labor_cost_vnd'],
                      emp_rows)
    print("  04_g_employees.sql")

    # -- 05_validation_queries.sql --
    with open(os.path.join(SQL_DIR, '05_validation_queries.sql'), 'w', encoding='utf-8') as f:
        f.write("-- ============================================================\n")
        f.write("-- 05_validation_queries.sql\n")
        f.write(f"-- Database: {DB_NAME}\n")
        f.write("-- Menas Group — Validation & Sanity Check Queries\n")
        f.write("-- ============================================================\n\n")
        f.write(f"USE {DB_NAME};\n\n")
        f.write("""\
-- 1. Row counts per table
SELECT 'business_units' AS tbl, COUNT(*) AS cnt FROM business_units
UNION ALL SELECT 'locations', COUNT(*) FROM locations
UNION ALL SELECT 'product_categories', COUNT(*) FROM product_categories
UNION ALL SELECT 'products', COUNT(*) FROM products
UNION ALL SELECT 'fb_outlets', COUNT(*) FROM fb_outlets
UNION ALL SELECT 'tenants', COUNT(*) FROM tenants
UNION ALL SELECT 'planned_locations', COUNT(*) FROM planned_locations
UNION ALL SELECT 'employees_summary', COUNT(*) FROM employees_summary
UNION ALL SELECT 'monthly_revenue', COUNT(*) FROM monthly_revenue
UNION ALL SELECT 'supermarket_daily_sales', COUNT(*) FROM supermarket_daily_sales
UNION ALL SELECT 'supermarket_shrinkage', COUNT(*) FROM supermarket_shrinkage
UNION ALL SELECT 'fb_monthly_revenue', COUNT(*) FROM fb_monthly_revenue
UNION ALL SELECT 'fb_monthly_costs', COUNT(*) FROM fb_monthly_costs
UNION ALL SELECT 'tenant_monthly_revenue', COUNT(*) FROM tenant_monthly_revenue
UNION ALL SELECT 'promotions', COUNT(*) FROM promotions
UNION ALL SELECT 'mall_events', COUNT(*) FROM mall_events
UNION ALL SELECT 'mall_daily_footfall', COUNT(*) FROM mall_daily_footfall
UNION ALL SELECT 'airport_daily_passengers', COUNT(*) FROM airport_daily_passengers;

-- 2. Total revenue by business unit (last 3 months)
SELECT business_unit_id,
       SUM(revenue_vnd) AS total_revenue,
       SUM(profit_vnd) AS total_profit,
       ROUND(SUM(profit_vnd)/SUM(revenue_vnd)*100, 2) AS margin_pct
FROM monthly_revenue
WHERE month >= '2026-01-01'
GROUP BY business_unit_id
ORDER BY total_revenue DESC;

-- 3. Supermarket gross margin trend
SELECT DATE_FORMAT(date, '%Y-%m') AS ym,
       location_id,
       SUM(selling_price_vnd * quantity - discount_amount_vnd) AS gross_sales,
       SUM(cost_price_vnd * quantity) AS total_cost,
       ROUND((SUM(selling_price_vnd * quantity - discount_amount_vnd) - SUM(cost_price_vnd * quantity))
             / SUM(selling_price_vnd * quantity - discount_amount_vnd) * 100, 2) AS margin_pct
FROM supermarket_daily_sales
GROUP BY ym, location_id
ORDER BY ym, location_id;

-- 4. F&B cost structure by outlet (latest month)
SELECT o.name, c.cost_type,
       SUM(c.amount_vnd) AS total_cost,
       ROUND(SUM(c.amount_vnd) / r.revenue_vnd * 100, 2) AS pct_of_revenue
FROM fb_monthly_costs c
JOIN fb_outlets o ON o.id = c.outlet_id
JOIN fb_monthly_revenue r ON r.outlet_id = c.outlet_id AND r.month = c.month
WHERE c.month = '2026-03-01'
GROUP BY o.name, c.cost_type, r.revenue_vnd
ORDER BY o.name, c.cost_type;

-- 5. Tenant revenue per sqm ranking
SELECT t.name, t.sqm_rented,
       ROUND(tmr.gross_revenue_vnd / t.sqm_rented, 0) AS rev_per_sqm,
       t.estimated_operating_margin_pct
FROM tenants t
JOIN tenant_monthly_revenue tmr ON tmr.tenant_id = t.id
WHERE tmr.month = '2026-03-01'
  AND t.location_id = 'LOC01'
ORDER BY rev_per_sqm DESC;

-- 6. Shrinkage rates by location and category (latest quarter)
SELECT s.location_id, pc.name AS category,
       ROUND(AVG(s.shrinkage_rate_pct), 2) AS avg_shrinkage_pct
FROM supermarket_shrinkage s
JOIN product_categories pc ON pc.id = s.category_id
WHERE s.month >= '2026-01-01'
GROUP BY s.location_id, pc.name
ORDER BY avg_shrinkage_pct DESC;

-- 7. Imported product mix trend (Anomaly 3 check)
SELECT DATE_FORMAT(date, '%Y-%m') AS ym,
       ROUND(SUM(CASE WHEN p.origin = 'imported' THEN sds.selling_price_vnd * sds.quantity ELSE 0 END)
             / SUM(sds.selling_price_vnd * sds.quantity) * 100, 2) AS imported_mix_pct
FROM supermarket_daily_sales sds
JOIN products p ON p.id = sds.product_id
GROUP BY ym
ORDER BY ym;

-- 8. F&B outlet performance comparison
SELECT o.name,
       ROUND(AVG(r.revenue_vnd), 0) AS avg_monthly_revenue,
       ROUND(AVG(r.avg_check_vnd), 0) AS avg_check,
       ROUND(AVG(r.covers), 0) AS avg_covers,
       ROUND((AVG(r.revenue_vnd) - (
         SELECT SUM(c.amount_vnd) FROM fb_monthly_costs c
         WHERE c.outlet_id = o.id AND c.month = r.month
       )) / AVG(r.revenue_vnd) * 100, 2) AS est_margin_pct
FROM fb_monthly_revenue r
JOIN fb_outlets o ON o.id = r.outlet_id
WHERE r.month >= '2025-10-01'
GROUP BY o.id, o.name
ORDER BY avg_monthly_revenue DESC;
""")
    print("  05_validation_queries.sql")

    # -- README.md --
    with open(os.path.join(SQL_DIR, 'README.md'), 'w', encoding='utf-8') as f:
        f.write(f"""# Menas Group Demo Database (`{DB_NAME}`)

## Overview
Multi-business retail & hospitality demo database for Menas Group (Sovico ecosystem).

- **5 Business Units**: Mall (TTTM), Supermarket, F&B, Duty Free, Beauty
- **15 Locations** across HCM and Nha Trang
- **~500 SKU** supermarket products
- **45 Tenants** across 2 malls
- **18 months** of data: 2024-10 to 2026-03

## SQL Files

| File | Description |
|------|-------------|
| `01_ddl_schema.sql` | Schema definition (all tables) |
| `02_metadata.sql` | Metadata tables for AI context |
| `03_master_data.sql` | Dimension/master data |
| `04_a_monthly_revenue.sql` | Monthly revenue by BU/location |
| `04_b_supermarket_sales.sql` | Daily supermarket sales (~{len(sales_rows):,} rows) |
| `04_c_fb_data.sql` | F&B revenue and cost data |
| `04_d_tenant_data.sql` | Tenant monthly revenue |
| `04_e_footfall_airport.sql` | Daily footfall data |
| `04_f_shrinkage_promos_events.sql` | Shrinkage data |
| `04_g_employees.sql` | Employee headcount summary |
| `05_validation_queries.sql` | Validation and sanity check queries |

## Embedded Anomalies

1. **Duty Free revenue dip** (Mar 2026): LOC13 revenue x0.95
2. **Supermarket margin compression** (Q1/2026): Cost ratio shifts from 0.78 to 0.787
3. **Imported product mix shift** (Oct 2025 - Mar 2026): Imported share rises from ~30% to ~38%
4. **Tet promo margin erosion** (Jan-Feb 2026): 12% discount on all supermarket items
5. **LOC04 high shrinkage**: Fresh food 3.5%, cosmetics 2.1% vs LOC03 ~1.3%
6. **Thai Siam over-staffing**: Labor cost at 38% of revenue (vs industry 24-28%)
7. **Yum Kim Long declining** (Jan-Mar 2026): Revenue drops 8-15% while costs stay flat
8. **Fashion Line low margin**: Operating margin only 2%, declining revenue 40% YoY
9. **Skechers & TWG Tea surge**: New tenants outperforming at 1.2x base
10. **Thai Siam marketing inefficiency**: Marketing spend up 29% in Feb-Mar 2026 with low ROI
11. **Steakhouse marketing independence**: Marketing cut 20% but revenue unaffected
12. **Kiosk low margins**: KOI (8%), Banh Trang (9%) despite high rent/sqm
13. **Footfall dip** (10-16 Mar 2026): Local segment LOC01 -15% due to B1 renovation
14. **Airport passenger dip** (Mar 2026): TSN traffic -8% post-Tết, drives Duty Free decline

## Usage
```bash
./populate.sh menas
```
""")
    print("  README.md")

    print(f"\nDone! Generated {len(os.listdir(SQL_DIR))} files in {SQL_DIR}/")


if __name__ == '__main__':
    main()
