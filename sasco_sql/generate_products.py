#!/usr/bin/env python3
"""Generate ~400 products with realistic names, Pareto weights, nationality preferences."""
import random
import math

random.seed(42)

def pareto_weights(n):
    """Generate Pareto-distributed weights: top 20% gets ~80% weight."""
    raw = sorted([random.paretovariate(1.2) for _ in range(n)], reverse=True)
    total = sum(raw)
    return [r / total for r in raw]

def sql_str(s):
    return s.replace("'", "''")

products = []
pid = 1000

# ============================================================================
# Category 11: Nuoc hoa cao cap (~30 SKU)
# ============================================================================
perfumes = [
    ("Nước hoa Chanel No.5 100ml", 3200000, "[1,3,4]"),
    ("Nước hoa Chanel Coco Mademoiselle 50ml", 2800000, "[1,3,4]"),
    ("Nước hoa Dior J'adore 50ml", 2500000, "[1,3,4,11]"),
    ("Nước hoa Dior Sauvage EDT 100ml", 2700000, "[1,4,5,11]"),
    ("Nước hoa Gucci Bloom 50ml", 2300000, "[1,3]"),
    ("Nước hoa Gucci Guilty 75ml", 2400000, "[1,5]"),
    ("Nước hoa Lancôme La Vie Est Belle 75ml", 2600000, "[1,3,11]"),
    ("Nước hoa YSL Black Opium 50ml", 2200000, "[1,3,4]"),
    ("Nước hoa Versace Eros 100ml", 1800000, "[5,11]"),
    ("Nước hoa Burberry Her 50ml", 1900000, "[1,11]"),
    ("Nước hoa Jo Malone English Pear 30ml", 1600000, "[4,8]"),
    ("Nước hoa Tom Ford Black Orchid 50ml", 3800000, "[1,5,8]"),
    ("Nước hoa Hermès Terre d'Hermès 75ml", 2900000, "[5,11]"),
    ("Nước hoa Prada Luna Rossa 100ml", 2100000, "[11]"),
    ("Nước hoa Dolce&Gabbana Light Blue 100ml", 1700000, "[5,11]"),
    ("Nước hoa Calvin Klein CK One 200ml", 1200000, "[5,7,10]"),
    ("Nước hoa Bulgari Omnia 65ml", 1500000, "[3,4]"),
    ("Nước hoa Marc Jacobs Daisy 75ml", 1400000, "[1,3]"),
    ("Nước hoa Givenchy L'Interdit 50ml", 2000000, "[1,11]"),
    ("Nước hoa Armani Sì 50ml", 2100000, "[1,3,11]"),
    ("Nước hoa Valentino Donna Born In Roma 50ml", 2300000, "[1,11]"),
    ("Nước hoa Montblanc Explorer 100ml", 1300000, "[5,11]"),
    ("Nước hoa Hugo Boss Bottled 100ml", 1100000, "[5,7,11]"),
    ("Nước hoa Chloé Eau de Parfum 50ml", 1800000, "[1,3,4]"),
    ("Nước hoa Thierry Mugler Angel 50ml", 1900000, "[11]"),
    ("Nước hoa Carolina Herrera Good Girl 50ml", 2000000, "[1,5]"),
    ("Nước hoa Narciso Rodriguez For Her 50ml", 1700000, "[4,1]"),
    ("Nước hoa Issey Miyake L'Eau d'Issey 50ml", 1500000, "[4]"),
    ("Nước hoa Kenzo Flower 50ml", 1300000, "[4,3]"),
    ("Nước hoa Ferragamo Signorina 50ml", 1200000, "[3]"),
]
cat_id = 11
weights = pareto_weights(len(perfumes))
for i, (name, price, nat) in enumerate(perfumes):
    cost = int(price * 0.33)
    products.append((pid, name, f"PF{pid-999:04d}", cat_id, price, cost, nat, weights[i]))
    pid += 1

# ============================================================================
# Category 12: My pham & Skincare (~30 SKU)
# ============================================================================
skincare = [
    ("Kem dưỡng SK-II Facial Treatment Essence 75ml", 3500000, "[1,3,4]"),
    ("Kem dưỡng Estée Lauder Advanced Night Repair 50ml", 2800000, "[1,3,4]"),
    ("Son MAC Ruby Woo", 650000, "[1,3,2]"),
    ("Son YSL Rouge Pur Couture", 850000, "[1,3]"),
    ("Son Dior Addict Lip Glow", 950000, "[1,3,4]"),
    ("Kem chống nắng La Roche-Posay Anthelios 50ml", 550000, "[1,4,8]"),
    ("Sữa rửa mặt Shiseido Senka 120g", 280000, "[1,4,3]"),
    ("Mặt nạ Innisfree Jeju Volcanic (bộ 10)", 350000, "[1,2]"),
    ("Set dưỡng da Laneige Water Sleeping Mask", 680000, "[1,3]"),
    ("Kem mắt Clinique All About Eyes 15ml", 780000, "[1,5,8]"),
    ("Phấn Chanel Les Beiges Healthy Glow", 1500000, "[1,3]"),
    ("Mascara Lancôme Hypnôse", 780000, "[1,3,11]"),
    ("Serum Vichy Minéral 89 50ml", 650000, "[1,11]"),
    ("Kem nền Giorgio Armani Luminous Silk", 1400000, "[1,3]"),
    ("Set trang điểm Charlotte Tilbury Pillow Talk", 1200000, "[1,5,8]"),
    ("Dầu tẩy trang DHC Deep Cleansing Oil 200ml", 450000, "[4,1]"),
    ("Kem dưỡng Sulwhasoo Concentrated Ginseng 60ml", 4200000, "[1,2]"),
    ("Toner Hada Labo Gokujyun 170ml", 320000, "[4,1]"),
    ("BB Cream Missha M Perfect Cover", 380000, "[1,2]"),
    ("Serum The Ordinary Niacinamide 10% 30ml", 280000, "[5,8,11]"),
    ("Son Charlotte Tilbury Matte Revolution", 850000, "[5,8,1]"),
    ("Cushion Laneige Neo Cushion Matte", 720000, "[1,3]"),
    ("Kem dưỡng Kiehl's Ultra Facial Cream 50ml", 780000, "[5,8]"),
    ("Set chăm sóc da Aesop Departure Kit", 1200000, "[8,5]"),
    ("Sữa tắm Molton Brown 300ml", 850000, "[8,11]"),
    ("Kem body Byredo Gypsy Water 200ml", 1500000, "[5,8,11]"),
    ("Nước tẩy trang Bioderma Sensibio 500ml", 380000, "[11]"),
    ("Set mini nước hoa Chanel (4x7.5ml)", 2200000, "[1,3,4]"),
    ("Son Hermès Rouge à Lèvres Satin", 1600000, "[1,5]"),
    ("Phấn highlight Dior Backstage Glow Face", 1100000, "[1,3]"),
]
cat_id = 12
weights = pareto_weights(len(skincare))
for i, (name, price, nat) in enumerate(skincare):
    cost = int(price * 0.33)
    products.append((pid, name, f"SK{pid-999:04d}", cat_id, price, cost, nat, weights[i]))
    pid += 1

# ============================================================================
# Category 21: Ruou vang & Champagne (~15 SKU)
# ============================================================================
wines = [
    ("Champagne Moët & Chandon Impérial 750ml", 1200000, "[1,5,11]"),
    ("Champagne Dom Pérignon Vintage 750ml", 6500000, "[1,5,11]"),
    ("Champagne Veuve Clicquot Yellow Label 750ml", 1350000, "[5,11]"),
    ("Rượu vang đỏ Penfolds Bin 389 750ml", 1100000, "[8,5]"),
    ("Rượu vang đỏ Château Margaux 2015 750ml", 8500000, "[5,11]"),
    ("Rượu vang đỏ Opus One 2018 750ml", 12000000, "[5,1]"),
    ("Rượu vang trắng Cloudy Bay Sauvignon 750ml", 650000, "[8,5]"),
    ("Rượu vang đỏ Tignanello 2019 750ml", 2800000, "[11]"),
    ("Champagne Laurent-Perrier Rosé 750ml", 1800000, "[1,11]"),
    ("Rượu vang đỏ Casillero del Diablo 750ml", 350000, "[5,7,10]"),
    ("Rượu vang Prosecco DOC 750ml", 420000, "[11,5]"),
    ("Rượu vang đỏ Yellow Tail Shiraz 750ml", 280000, "[8]"),
    ("Champagne Perrier-Jouët Belle Époque 750ml", 4500000, "[1,5,11]"),
    ("Rượu vang đỏ Robert Mondavi Napa 750ml", 950000, "[5]"),
    ("Rượu vang Ice Wine Inniskillin 375ml", 1200000, "[1,2]"),
]
cat_id = 21
weights = pareto_weights(len(wines))
for i, (name, price, nat) in enumerate(wines):
    cost = int(price * 0.33)
    products.append((pid, name, f"WN{pid-999:04d}", cat_id, price, cost, nat, weights[i]))
    pid += 1

# ============================================================================
# Category 22: Ruou manh (~15 SKU)
# ============================================================================
spirits = [
    ("Rượu Hennessy VSOP 700ml", 1350000, "[2,1]"),
    ("Rượu Hennessy XO 700ml", 3800000, "[2,1]"),
    ("Rượu Johnnie Walker Blue Label 750ml", 4500000, "[1,2,5]"),
    ("Rượu Johnnie Walker Black Label 750ml", 850000, "[1,2,7,10]"),
    ("Rượu Chivas Regal 18 700ml", 1200000, "[1,2]"),
    ("Rượu Macallan 12 Years 700ml", 1500000, "[1,5,8]"),
    ("Rượu Jack Daniel's Old No.7 700ml", 650000, "[5,7]"),
    ("Rượu Mao Đài Quý Châu 500ml", 3200000, "[2]"),
    ("Rượu Sake Dassai 45 720ml", 850000, "[4]"),
    ("Rượu Vodka Grey Goose 750ml", 750000, "[5,11]"),
    ("Rượu Bombay Sapphire Gin 750ml", 550000, "[5,8,11]"),
    ("Rượu Rémy Martin XO 700ml", 4200000, "[2,1]"),
    ("Rượu Glenfiddich 15 Years 700ml", 1300000, "[5,8]"),
    ("Rượu Baileys Irish Cream 700ml", 450000, "[5,11,7]"),
    ("Rượu Patron Silver Tequila 750ml", 1100000, "[5]"),
]
cat_id = 22
weights = pareto_weights(len(spirits))
for i, (name, price, nat) in enumerate(spirits):
    cost = int(price * 0.33)
    products.append((pid, name, f"SP{pid-999:04d}", cat_id, price, cost, nat, weights[i]))
    pid += 1

# ============================================================================
# Category 23: Thuoc la (~10 SKU)
# ============================================================================
tobacco = [
    ("Thuốc lá Marlboro Gold (1 tút)", 380000, None),
    ("Thuốc lá Dunhill Fine Cut (1 tút)", 420000, "[11]"),
    ("Thuốc lá 555 Gold (1 tút)", 350000, "[7,10]"),
    ("Thuốc lá Mild Seven/Mevius (1 tút)", 380000, "[4]"),
    ("Thuốc lá Camel (1 tút)", 350000, "[5]"),
    ("Thuốc lá Winston (1 tút)", 320000, None),
    ("Thuốc lá Lucky Strike (1 tút)", 330000, None),
    ("Thuốc lá Kent (1 tút)", 360000, "[11]"),
    ("Xì gà Cohiba Robusto (hộp 5)", 2500000, "[5,11]"),
    ("Xì gà Montecristo No.4 (hộp 5)", 1800000, "[5,11]"),
]
cat_id = 23
weights = pareto_weights(len(tobacco))
for i, (name, price, nat) in enumerate(tobacco):
    cost = int(price * 0.33)
    products.append((pid, name, f"TB{pid-999:04d}", cat_id, price, cost, "NULL" if nat is None else nat, weights[i]))
    pid += 1

# ============================================================================
# Category 31: Kinh mat (~10 SKU)
# ============================================================================
eyewear = [
    ("Kính mắt Ray-Ban Aviator Classic", 3500000, "[1,5,11]"),
    ("Kính mắt Ray-Ban Wayfarer", 3200000, "[5,11]"),
    ("Kính mắt Gucci GG0036S", 7500000, "[1,3]"),
    ("Kính mắt Prada Linea Rossa", 5800000, "[1,11]"),
    ("Kính mắt Oakley Holbrook", 2800000, "[5,8]"),
    ("Kính mắt Tom Ford FT0237", 6500000, "[1,5]"),
    ("Kính mắt Dior DiorSoReal", 8500000, "[1,3]"),
    ("Kính mắt Versace VE4361", 4500000, "[1,2]"),
    ("Kính mắt Cartier Santos de Cartier", 12000000, "[1,2,5]"),
    ("Kính mắt Gentle Monster Dreamer", 5500000, "[1,2,3]"),
]
cat_id = 31
weights = pareto_weights(len(eyewear))
for i, (name, price, nat) in enumerate(eyewear):
    cost = int(price * 0.33)
    products.append((pid, name, f"EW{pid-999:04d}", cat_id, price, cost, nat, weights[i]))
    pid += 1

# ============================================================================
# Category 32: Dong ho (~10 SKU)
# ============================================================================
watches = [
    ("Đồng hồ Tissot PRX Powermatic 80", 12500000, "[1,5,11]"),
    ("Đồng hồ Seiko Presage Cocktail", 8500000, "[4,1]"),
    ("Đồng hồ Casio G-Shock GA-2100", 2800000, "[2,7,10]"),
    ("Đồng hồ Daniel Wellington Classic 40mm", 3500000, "[1,3]"),
    ("Đồng hồ Fossil Gen 6 Smartwatch", 6500000, "[5,6]"),
    ("Đồng hồ Citizen Eco-Drive", 5500000, "[4,5]"),
    ("Đồng hồ Calvin Klein Minimal 40mm", 4200000, "[1,11]"),
    ("Đồng hồ Swatch Sistem51", 3200000, "[11]"),
    ("Đồng hồ Michael Kors Runway", 5800000, "[5,1]"),
    ("Đồng hồ Longines La Grande Classique", 14500000, "[1,2]"),
]
cat_id = 32
weights = pareto_weights(len(watches))
for i, (name, price, nat) in enumerate(watches):
    cost = int(price * 0.33)
    products.append((pid, name, f"WT{pid-999:04d}", cat_id, price, cost, nat, weights[i]))
    pid += 1

# ============================================================================
# Category 33: Tui xach & Vi (~10 SKU)
# ============================================================================
bags = [
    ("Túi xách Coach Tabby 26", 8500000, "[1,3,2]"),
    ("Túi xách Longchamp Le Pliage L", 3200000, "[1,3,4]"),
    ("Ví da Montblanc Meisterstück 6cc", 5500000, "[1,5,2]"),
    ("Túi xách Michael Kors Jet Set", 4800000, "[5,1]"),
    ("Ví Coach Signature Zip Around", 2800000, "[1,3]"),
    ("Túi đeo chéo Tory Burch Kira", 6500000, "[1,5]"),
    ("Ví Gucci GG Marmont Card Case", 7500000, "[1,2,3]"),
    ("Túi xách Kate Spade Cedar Street", 3800000, "[5,1]"),
    ("Ba lô Samsonite Red Aleron", 3500000, "[1,2,4]"),
    ("Túi du lịch Rimowa Original Cabin", 14500000, "[1,5,2]"),
]
cat_id = 33
weights = pareto_weights(len(bags))
for i, (name, price, nat) in enumerate(bags):
    cost = int(price * 0.33)
    products.append((pid, name, f"BG{pid-999:04d}", cat_id, price, cost, nat, weights[i]))
    pid += 1

# ============================================================================
# Category 41: Dac san vung mien (~12 SKU)
# ============================================================================
specialties = [
    ("Khô bò Bà Tư miếng 250g", 185000, "[2,9,6]"),
    ("Mắm tép Bà Giáo Khỏe 200ml", 95000, "[6,9]"),
    ("Bánh tráng cuốn Tây Ninh (bộ 20)", 65000, "[6,9,2]"),
    ("Nước mắm Phú Quốc Hưng Thịnh 500ml", 120000, "[6,9,4]"),
    ("Hạt điều rang muối Bình Phước 500g", 180000, "[2,6,9]"),
    ("Mứt dừa Bến Tre hộp quà 400g", 135000, "[2,9]"),
    ("Kẹo dừa Bến Tre hộp 400g", 85000, "[2,9,6]"),
    ("Phồng tôm Sa Giang hộp quà", 75000, "[6,9]"),
    ("Cơm cháy chà bông Ninh Bình 300g", 125000, "[2,6]"),
    ("Bột gia vị phở Việt Nam (set 5 gói)", 95000, "[6,4]"),
    ("Mật ong rừng U Minh 500ml", 250000, "[4,8]"),
    ("Tương ớt Sriracha 480ml", 55000, "[6,9,7]"),
]
cat_id = 41
weights = pareto_weights(len(specialties))
for i, (name, price, nat) in enumerate(specialties):
    cost = int(price * 0.40)
    products.append((pid, name, f"DS{pid-999:04d}", cat_id, price, cost, nat, weights[i]))
    pid += 1

# ============================================================================
# Category 42: Tra & Ca phe (~10 SKU)
# ============================================================================
tea_coffee = [
    ("Cà phê Trung Nguyên Legend hộp quà 500g", 350000, "[6,4,2]"),
    ("Cà phê Trung Nguyên G7 3in1 (hộp 50 gói)", 180000, "[6,9,2]"),
    ("Cà phê weasel (chồn) Đà Lạt 250g", 850000, "[4,8,5]"),
    ("Trà sen Tây Hồ hộp quà 200g", 280000, "[4,2,6]"),
    ("Trà ô long Bảo Lộc hộp quà 250g", 220000, "[2,3]"),
    ("Trà atiso Đà Lạt (hộp 20 túi lọc)", 85000, "[6,9]"),
    ("Cà phê phin nhôm + cà phê rang xay set", 250000, "[4,5,8]"),
    ("Trà Thái Nguyên đặc biệt 200g", 180000, "[2,4]"),
    ("Cà phê Highlands Coffee hộp quà", 150000, "[6,9]"),
    ("Socola cà phê Marou Bến Tre 80g", 120000, "[4,5,8,11]"),
]
cat_id = 42
weights = pareto_weights(len(tea_coffee))
for i, (name, price, nat) in enumerate(tea_coffee):
    cost = int(price * 0.40)
    products.append((pid, name, f"TC{pid-999:04d}", cat_id, price, cost, nat, weights[i]))
    pid += 1

# ============================================================================
# Category 43: Gia vi (~8 SKU)
# ============================================================================
spices = [
    ("Bột cà ri Ấn Độ Everest 200g", 85000, "[6]"),
    ("Nước mắm nhĩ Phan Thiết 250ml", 75000, "[6,9]"),
    ("Hạt tiêu Phú Quốc đen 200g", 120000, "[6,4,8]"),
    ("Sả tươi sấy khô gói 100g", 55000, "[6,9]"),
    ("Bột nghệ Đắk Lắk nguyên chất 200g", 95000, "[6]"),
    ("Muối ớt Tây Ninh 200g", 45000, "[6,9,2]"),
    ("Gia vị lẩu Thái hộp set (4 gói)", 65000, "[6,10]"),
    ("Set gia vị nấu phở gia truyền (5 gói)", 85000, "[6,4]"),
]
cat_id = 43
weights = pareto_weights(len(spices))
for i, (name, price, nat) in enumerate(spices):
    cost = int(price * 0.45)
    products.append((pid, name, f"GV{pid-999:04d}", cat_id, price, cost, nat, weights[i]))
    pid += 1

# ============================================================================
# Category 44: Hang thu cong my nghe (~10 SKU)
# ============================================================================
crafts = [
    ("Áo dài lụa thêu tay size M", 1200000, "[4,5,8,11]"),
    ("Tranh sơn mài Hạ Long 40x60cm", 850000, "[4,8,11]"),
    ("Nón lá Huế thêu tay", 180000, "[4,5,8]"),
    ("Tượng gỗ trầm hương 20cm", 650000, "[2,1]"),
    ("Đèn lồng Hội An (bộ 3)", 250000, "[4,5,8]"),
    ("Khăn lụa Vạn Phúc 180x45cm", 350000, "[4,11]"),
    ("Gốm sứ Bát Tràng - Bộ trà 6 chén", 420000, "[4,2]"),
    ("Quạt lụa vẽ tay Huế", 150000, "[4,8]"),
    ("Hộp sơn mài khảm trai", 580000, "[4,8,11]"),
    ("Vòng tay trầm hương tự nhiên", 380000, "[2,1,3]"),
]
cat_id = 44
weights = pareto_weights(len(crafts))
for i, (name, price, nat) in enumerate(crafts):
    cost = int(price * 0.35)
    products.append((pid, name, f"TC{pid-999:04d}", cat_id, price, cost, nat, weights[i]))
    pid += 1

# ============================================================================
# Category 50: Banh keo & Chocolate (~12 SKU)
# ============================================================================
sweets = [
    ("Socola Godiva Gold Collection 24pc", 1200000, "[1,2,5]"),
    ("Socola Lindt Lindor Assorted 500g", 650000, "[5,11]"),
    ("Socola Ferrero Rocher T30", 450000, "[2,9,6]"),
    ("Kẹo Haribo Goldbären hộp 1kg", 280000, "[5,11]"),
    ("Bánh LU Petite Écolier hộp 300g", 220000, "[11]"),
    ("Socola Toblerone Gold 360g", 320000, "[5,11]"),
    ("Bánh quy Royce Chocolate Chip 12pc", 380000, "[4,1]"),
    ("Kẹo hạnh nhân Maxim's Paris 200g", 350000, "[11]"),
    ("Bánh quy bơ Đan Mạch hộp thiếc 908g", 250000, "[2,9]"),
    ("Socola Marou Lâm Đồng 70% 80g", 120000, "[4,5,8]"),
    ("Bánh pía Sóc Trăng hộp quà (6 cái)", 135000, "[2,9,6]"),
    ("Mè xửng Huế hộp quà 500g", 95000, "[2,9]"),
]
cat_id = 50
weights = pareto_weights(len(sweets))
for i, (name, price, nat) in enumerate(sweets):
    cost = int(price * 0.35)
    products.append((pid, name, f"BK{pid-999:04d}", cat_id, price, cost, nat, weights[i]))
    pid += 1

# ============================================================================
# Category 60: Dien tu & Phu kien (~10 SKU)
# ============================================================================
electronics = [
    ("Tai nghe Apple AirPods Pro 2", 5500000, "[1,2,6]"),
    ("Tai nghe Sony WH-1000XM5", 7500000, "[4,5,8]"),
    ("Sạc dự phòng Anker 20000mAh", 850000, "[6,7]"),
    ("Adapter sạc nhanh Anker 65W", 550000, "[6,7]"),
    ("Loa Bluetooth JBL Flip 6", 2500000, "[5,6]"),
    ("Tai nghe Samsung Galaxy Buds2 Pro", 3800000, "[1,6]"),
    ("Cáp Lightning/USB-C Belkin 1m", 350000, "[6,7]"),
    ("Ốp lưng iPhone Spigen Ultra Hybrid", 450000, "[1,6]"),
    ("Đồng hồ thông minh Amazfit GTR 4", 3500000, "[6,2]"),
    ("Bút cảm ứng Adonit Note+", 850000, "[5,4]"),
]
cat_id = 60
weights = pareto_weights(len(electronics))
for i, (name, price, nat) in enumerate(electronics):
    cost = int(price * 0.50)
    products.append((pid, name, f"DT{pid-999:04d}", cat_id, price, cost, nat, weights[i]))
    pid += 1

# ============================================================================
# Category 70: Pho & Mon Viet (~15 SKU)
# ============================================================================
viet_food = [
    ("Phở bò tái nạm", 128000, None),
    ("Phở bò tái chín gầu", 138000, None),
    ("Phở gà", 118000, None),
    ("Bún bò Huế", 138000, None),
    ("Cơm tấm sườn bì chả", 128000, None),
    ("Bánh mì thịt nướng", 78000, None),
    ("Gỏi cuốn tôm thịt (4 cuốn)", 88000, None),
    ("Hủ tiếu Nam Vang", 118000, None),
    ("Mì Quảng", 108000, None),
    ("Bún thịt nướng", 118000, None),
    ("Bánh xèo Sài Gòn", 108000, None),
    ("Cháo lòng", 88000, None),
    ("Bún riêu cua", 118000, None),
    ("Cơm chiên Dương Châu", 108000, None),
    ("Nem rán/Chả giò (4 cuốn)", 78000, None),
]
cat_id = 70
weights = pareto_weights(len(viet_food))
for i, (name, price, nat) in enumerate(viet_food):
    cost = int(price * 0.25)
    products.append((pid, name, f"VF{pid-999:04d}", cat_id, price, cost, "NULL", weights[i]))
    pid += 1

# ============================================================================
# Category 71: Mon A (~12 SKU)
# ============================================================================
asian_food = [
    ("Cơm cuộn Hàn Quốc (Kimbap)", 108000, None),
    ("Mì ramen Nhật Bản", 148000, None),
    ("Pad Thái", 128000, None),
    ("Cơm rang kimchi", 118000, None),
    ("Dim sum set (6 viên)", 128000, None),
    ("Gà teriyaki cơm Nhật", 158000, None),
    ("Curry gà Ấn Độ & cơm", 138000, None),
    ("Nasi goreng", 118000, None),
    ("Tom yum kung", 148000, None),
    ("Sushi set (8 miếng)", 188000, None),
    ("Bibimbap Hàn Quốc", 138000, None),
    ("Mì xào Singapore", 118000, None),
]
cat_id = 71
weights = pareto_weights(len(asian_food))
for i, (name, price, nat) in enumerate(asian_food):
    cost = int(price * 0.25)
    products.append((pid, name, f"AF{pid-999:04d}", cat_id, price, cost, "NULL", weights[i]))
    pid += 1

# ============================================================================
# Category 72: Mon Au (~10 SKU)
# ============================================================================
western_food = [
    ("Steak bò Úc 200g kèm khoai tây", 298000, None),
    ("Burger bò phô mai", 158000, None),
    ("Pasta Carbonara", 168000, None),
    ("Pizza Margherita 9 inch", 178000, None),
    ("Salad Caesar gà nướng", 138000, None),
    ("Fish & Chips", 168000, None),
    ("Club Sandwich", 128000, None),
    ("Soup kem nấm", 78000, None),
    ("Risotto hải sản", 198000, None),
    ("Spaghetti Bolognese", 148000, None),
]
cat_id = 72
weights = pareto_weights(len(western_food))
for i, (name, price, nat) in enumerate(western_food):
    cost = int(price * 0.25)
    products.append((pid, name, f"WF{pid-999:04d}", cat_id, price, cost, "NULL", weights[i]))
    pid += 1

# ============================================================================
# Category 73: Cafe & Do uong (~15 SKU)
# ============================================================================
drinks = [
    ("Cà phê sữa đá", 55000, None),
    ("Cà phê đen đá", 45000, None),
    ("Bạc xỉu", 55000, None),
    ("Cappuccino", 65000, None),
    ("Latte", 65000, None),
    ("Espresso", 50000, None),
    ("Trà sen nóng", 55000, None),
    ("Trà đào cam sả", 65000, None),
    ("Sinh tố bơ", 75000, None),
    ("Nước ép cam tươi", 65000, None),
    ("Bia Tiger lon 330ml", 45000, None),
    ("Bia Heineken lon 330ml", 50000, None),
    ("Nước suối Aquafina 500ml", 20000, None),
    ("Coca-Cola lon 330ml", 25000, None),
    ("Smoothie xoài nhiệt đới", 75000, None),
]
cat_id = 73
weights = pareto_weights(len(drinks))
for i, (name, price, nat) in enumerate(drinks):
    cost = int(price * 0.25)
    products.append((pid, name, f"DK{pid-999:04d}", cat_id, price, cost, "NULL", weights[i]))
    pid += 1

# ============================================================================
# Category 74: An nhanh & Snack (~8 SKU)
# ============================================================================
snacks = [
    ("Bánh mì que pate", 45000, None),
    ("Xôi gà", 55000, None),
    ("Sandwich tam giác", 48000, None),
    ("Croissant bơ", 42000, None),
    ("Salad trái cây", 58000, None),
    ("Khoai tây chiên", 55000, None),
    ("Onion rings", 48000, None),
    ("Gà viên chiên (6 viên)", 58000, None),
]
cat_id = 74
weights = pareto_weights(len(snacks))
for i, (name, price, nat) in enumerate(snacks):
    cost = int(price * 0.25)
    products.append((pid, name, f"SN{pid-999:04d}", cat_id, price, cost, "NULL", weights[i]))
    pid += 1

# ============================================================================
# Category 80: Dich vu phong cho tieu chuan (~5 SKU)
# ============================================================================
lounge_std = [
    ("Phòng chờ Lotus tiêu chuẩn - Nội địa", 380000, None),
    ("Phòng chờ Lotus tiêu chuẩn - Quốc tế", 650000, None),
    ("Phòng chờ Lotus tiêu chuẩn - Hỗn hợp", 550000, None),
    ("Phòng chờ Lotus tiêu chuẩn - Cam Ranh", 550000, None),
    ("Phòng chờ SENS Leisure - Phú Quốc", 600000, None),
]
cat_id = 80
weights = pareto_weights(len(lounge_std))
for i, (name, price, nat) in enumerate(lounge_std):
    cost = int(price * 0.20)
    products.append((pid, name, f"LS{pid-999:04d}", cat_id, price, cost, "NULL", weights[i]))
    pid += 1

# ============================================================================
# Category 81: Dich vu phong cho VIP (~5 SKU)
# ============================================================================
lounge_vip = [
    ("Phòng chờ SENS Business - Quốc tế T2", 850000, None),
    ("Phòng chờ SENS Business - T3", 750000, None),
    ("Phòng chờ Lotus First Class", 1200000, None),
    ("Phòng chờ VIP riêng (2 giờ)", 2500000, None),
    ("Gói phòng chờ gia đình (4 người)", 2000000, None),
]
cat_id = 81
weights = pareto_weights(len(lounge_vip))
for i, (name, price, nat) in enumerate(lounge_vip):
    cost = int(price * 0.20)
    products.append((pid, name, f"LV{pid-999:04d}", cat_id, price, cost, "NULL", weights[i]))
    pid += 1

# ============================================================================
# Category 82: Goi dich vu dac biet (~5 SKU)
# ============================================================================
lounge_special = [
    ("Combo phòng chờ + Spa 60 phút", 1100000, None),
    ("Combo phòng chờ + Spa 90 phút", 1400000, None),
    ("Gói nghỉ ngơi qua đêm (phòng chờ + giường)", 1800000, None),
    ("Combo phòng chờ + Limousine đưa đón", 2200000, None),
    ("Gói trải nghiệm SASCO Premium (trọn gói)", 3500000, None),
]
cat_id = 82
weights = pareto_weights(len(lounge_special))
for i, (name, price, nat) in enumerate(lounge_special):
    cost = int(price * 0.20)
    products.append((pid, name, f"LX{pid-999:04d}", cat_id, price, cost, "NULL", weights[i]))
    pid += 1

# ============================================================================
# Category 90: Spa & Massage (~8 SKU)
# ============================================================================
spa = [
    ("Massage chân 30 phút", 250000, None),
    ("Massage toàn thân 60 phút", 500000, None),
    ("Massage toàn thân 90 phút", 700000, None),
    ("Massage đầu & vai 30 phút", 200000, None),
    ("Facial chăm sóc da mặt 45 phút", 450000, None),
    ("Combo massage + facial 90 phút", 800000, None),
    ("Massage ghế tự động 15 phút", 80000, None),
    ("Liệu trình detox toàn thân 120 phút", 1200000, None),
]
cat_id = 90
weights = pareto_weights(len(spa))
for i, (name, price, nat) in enumerate(spa):
    cost = int(price * 0.25)
    products.append((pid, name, f"SP{pid-999:04d}", cat_id, price, cost, "NULL", weights[i]))
    pid += 1

# ============================================================================
# Category 91: Thu doi ngoai te (~3 SKU)
# ============================================================================
forex = [
    ("Phí thu đổi ngoại tệ (dưới 500 USD)", 50000, None),
    ("Phí thu đổi ngoại tệ (500-2000 USD)", 100000, None),
    ("Phí thu đổi ngoại tệ (trên 2000 USD)", 200000, None),
]
cat_id = 91
weights = pareto_weights(len(forex))
for i, (name, price, nat) in enumerate(forex):
    cost = int(price * 0.30)
    products.append((pid, name, f"FX{pid-999:04d}", cat_id, price, cost, "NULL", weights[i]))
    pid += 1

# ============================================================================
# Category 92: Van chuyen Limousine (~5 SKU)
# ============================================================================
limo = [
    ("Limousine đưa đón sân bay - nội thành", 550000, None),
    ("Limousine đưa đón sân bay - ngoại thành", 850000, None),
    ("Limousine VIP Mercedes S-Class", 1500000, None),
    ("Xe đưa đón sân bay - sedan", 350000, None),
    ("Xe đưa đón sân bay - SUV 7 chỗ", 650000, None),
]
cat_id = 92
weights = pareto_weights(len(limo))
for i, (name, price, nat) in enumerate(limo):
    cost = int(price * 0.40)
    products.append((pid, name, f"LM{pid-999:04d}", cat_id, price, cost, "NULL", weights[i]))
    pid += 1

# ============================================================================
# Category 93: Ho tro hanh khach VIP (~4 SKU)
# ============================================================================
vip_svc = [
    ("Dịch vụ đón/tiễn VIP cửa máy bay", 800000, None),
    ("Dịch vụ fast-track xuất nhập cảnh", 500000, None),
    ("Dịch vụ hỗ trợ hành lý ưu tiên", 300000, None),
    ("Gói VIP trọn gói (đón + fast-track + phòng chờ)", 2000000, None),
]
cat_id = 93
weights = pareto_weights(len(vip_svc))
for i, (name, price, nat) in enumerate(vip_svc):
    cost = int(price * 0.30)
    products.append((pid, name, f"VP{pid-999:04d}", cat_id, price, cost, "NULL", weights[i]))
    pid += 1

# ============================================================================
# Additional filler products to reach ~400 total
# ============================================================================
# More duty-free cosmetics & misc
filler_df = [
    (12, "Set dưỡng da The History of Whoo", 5500000, "[1,2]"),
    (12, "Kem dưỡng Laneige Water Bank 50ml", 680000, "[1,3]"),
    (12, "Son Chanel Rouge Allure", 1050000, "[1,3]"),
    (12, "Phấn mắt Urban Decay Naked 3", 1200000, "[5,8]"),
    (12, "Serum Estée Lauder Re-Nutriv 30ml", 3200000, "[1,5]"),
    (11, "Nước hoa Acqua di Gio Profumo 75ml", 2200000, "[5,11]"),
    (11, "Nước hoa Miss Dior Blooming Bouquet 50ml", 2100000, "[1,3]"),
    (11, "Nước hoa Creed Aventus 50ml", 5500000, "[5,8]"),
    (50, "Socola Belgian Seashells 250g", 280000, "[11]"),
    (50, "Bánh quy Gavottes Crêpes Dentelles 125g", 180000, "[11]"),
    (41, "Mực rim me 200g", 145000, "[2,9]"),
    (41, "Tôm khô Cà Mau loại 1 250g", 280000, "[2,9]"),
    (42, "Trà hoa cúc Đà Lạt hộp 50g", 95000, "[4,6]"),
    (42, "Cà phê Arabica Cầu Đất 250g", 165000, "[4,5,8]"),
    (60, "Cáp sạc nhanh USB-C 2m Ugreen", 180000, "[6,7]"),
    (60, "Pin dự phòng Xiaomi 10000mAh", 450000, "[6,2]"),
    (22, "Rượu Hennessy Paradis 700ml", 8500000, "[2,1]"),
    (22, "Rượu Yamazaki 12 Years 700ml", 3500000, "[4]"),
    (21, "Rượu vang đỏ Sassicaia 2019 750ml", 3800000, "[11,5]"),
    (33, "Túi xách MCM Stark Backpack Mini", 9500000, "[1,2,3]"),
]
for cat_id, name, price, nat in filler_df:
    if cat_id in (11, 12):
        cost = int(price * 0.33)
    elif cat_id in (21, 22):
        cost = int(price * 0.33)
    elif cat_id == 33:
        cost = int(price * 0.33)
    elif cat_id in (41, 42):
        cost = int(price * 0.40)
    elif cat_id == 50:
        cost = int(price * 0.35)
    elif cat_id == 60:
        cost = int(price * 0.50)
    else:
        cost = int(price * 0.35)
    products.append((pid, name, f"FL{pid-999:04d}", cat_id, price, cost, nat, 0.005))
    pid += 1

# More F&B items
filler_fnb = [
    (70, "Phở chay rau nấm", 98000),
    (70, "Bún chả Hà Nội", 128000),
    (71, "Cơm gà Hải Nam", 128000),
    (71, "Mì udon tempura", 148000),
    (72, "Chicken Cordon Bleu", 188000),
    (72, "Grilled salmon fillet", 258000),
    (73, "Matcha Latte", 68000),
    (73, "Hot Chocolate", 58000),
    (73, "Fresh coconut juice", 55000),
    (74, "Bánh cuốn nóng", 65000),
]
for cat_id, name, price in filler_fnb:
    cost = int(price * 0.25)
    products.append((pid, name, f"FF{pid-999:04d}", cat_id, price, cost, "NULL", 0.005))
    pid += 1

print(f"-- Total products: {len(products)}")
print()

# Generate SQL
print("-- ============================================================================")
print("-- Products (~{} SKU)".format(len(products)))
print("-- ============================================================================")
print()

# Batch insert 50 at a time
batch_size = 50
for batch_start in range(0, len(products), batch_size):
    batch = products[batch_start:batch_start + batch_size]
    print("INSERT INTO products (product_id, product_name, product_code, category_id, unit_price_vnd, cost_price_vnd, is_active, popularity_weight, nationality_preference) VALUES")
    lines = []
    for p in batch:
        pid_v, name, code, cat, price, cost, nat, weight = p
        name_esc = sql_str(name)
        if nat == "NULL":
            nat_sql = "NULL"
        else:
            nat_sql = f"'{nat}'"
        lines.append(f"({pid_v}, '{name_esc}', '{code}', {cat}, {price}, {cost}, TRUE, {weight:.4f}, {nat_sql})")
    print(",\n".join(lines) + ";")
    print()
