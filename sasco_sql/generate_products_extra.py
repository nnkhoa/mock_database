#!/usr/bin/env python3
"""Generate additional products to reach ~400 total. Append to master data SQL."""

def sql_str(s):
    return s.replace("'", "''")

products = []
pid = 2000

# More perfumes
extras = [
    (11, "Nước hoa Byredo Gypsy Water 50ml", 3200000, "[5,8,11]"),
    (11, "Nước hoa Maison Francis Kurkdjian Baccarat Rouge 540 35ml", 4800000, "[1,5]"),
    (11, "Nước hoa Penhaligon's Halfeti 75ml", 3500000, "[8,11]"),
    (11, "Nước hoa Le Labo Santal 33 50ml", 4200000, "[5,8]"),
    (11, "Nước hoa Diptyque Eau Rose 75ml", 2800000, "[4,11]"),
    # More skincare
    (12, "Kem dưỡng La Mer Moisturizing Cream 30ml", 5800000, "[1,5,8]"),
    (12, "Serum SK-II GenOptics Aura Essence 50ml", 4500000, "[1,3,4]"),
    (12, "Set mini Dior Addict Lip (5 thỏi)", 1800000, "[1,3]"),
    (12, "Kem mắt La Prairie Skin Caviar 20ml", 6200000, "[1,5]"),
    (12, "Sữa dưỡng thể Jo Malone 250ml", 1200000, "[8,11]"),
    (12, "Phấn phủ Laura Mercier Translucent", 950000, "[5,8,1]"),
    (12, "Son Guerlain KissKiss", 850000, "[1,11]"),
    (12, "Kem dưỡng Tatcha Dewy Skin Cream 50ml", 1500000, "[4,5]"),
    (12, "Set chăm sóc tóc Olaplex No.3-4-5", 1100000, "[5,8]"),
    (12, "Kem chống nắng Anessa Perfect UV 60ml", 550000, "[4,1,3]"),
    # More wines
    (21, "Rượu vang đỏ Antinori Tignanello 2020 750ml", 2500000, "[11,5]"),
    (21, "Rượu vang trắng Chablis Premier Cru 750ml", 850000, "[11]"),
    (21, "Champagne Krug Grande Cuvée 750ml", 5500000, "[5,11]"),
    (21, "Rượu vang đỏ Barossa Valley Shiraz 750ml", 680000, "[8]"),
    (21, "Rượu vang rosé Whispering Angel 750ml", 550000, "[5,11]"),
    # More spirits
    (22, "Rượu Nikka From The Barrel 500ml", 1200000, "[4]"),
    (22, "Rượu Hibiki Harmony 700ml", 2200000, "[4,1]"),
    (22, "Rượu Cointreau 700ml", 550000, "[11]"),
    (22, "Rượu Aperol Spritz 750ml", 450000, "[11]"),
    (22, "Rượu Crown Royal 750ml", 750000, "[5]"),
    # More bags/accessories
    (33, "Ví Louis Vuitton Zippy Wallet", 14500000, "[1,2,3]"),
    (33, "Túi xách Furla Metropolis Mini", 5500000, "[1,3,11]"),
    (31, "Kính mắt Maui Jim Peahi", 4200000, "[5,8]"),
    (31, "Kính mắt Celine CL40187I", 7800000, "[1,11]"),
    (32, "Đồng hồ Hamilton Khaki Field 42mm", 9500000, "[5,4]"),
    # More specialties
    (41, "Bánh tráng trộn Tây Ninh gói 200g", 55000, "[6,9,2]"),
    (41, "Chả lụa Vissan 500g", 85000, "[9,2]"),
    (41, "Muối tôm Tây Ninh 200g", 45000, "[6,9]"),
    (41, "Khô cá lóc 250g", 165000, "[9,2]"),
    (42, "Cà phê muối Huế gói 10 sticks", 85000, "[4,6]"),
    (42, "Trà lài Bảo Lộc 200g", 120000, "[2,4]"),
    (43, "Gia vị bún bò Huế (set 5 gói)", 75000, "[6]"),
    (43, "Nước cốt dừa Vietcoco 400ml", 35000, "[6,9]"),
    # More sweets
    (50, "Socola Venchi Assorted 200g", 380000, "[11]"),
    (50, "Kẹo dừa Bến Tre vị sầu riêng 300g", 75000, "[2,9]"),
    (50, "Mochi Nhật Bản hộp 12 viên", 150000, "[4,1]"),
    (50, "Bánh trung thu SASCO hộp 4", 350000, "[2,9]"),
    # More electronics
    (60, "Bộ chuyển đổi ổ cắm du lịch đa năng", 250000, "[6,7]"),
    (60, "Tai nghe Bose QuietComfort Earbuds II", 6800000, "[5,8]"),
    (60, "Chuột không dây Logitech MX Anywhere 3", 1500000, "[5,4]"),
    # More F&B
    (70, "Bánh canh cua", 128000, None),
    (70, "Cơm gà xối mỡ", 118000, None),
    (71, "Lẩu Thái mini (1 người)", 178000, None),
    (71, "Cơm chiên cá mặn", 108000, None),
    (72, "Beef Wellington mini", 288000, None),
    (72, "Crème brûlée", 78000, None),
    (73, "Trà sữa trân châu", 65000, None),
    (73, "Sinh tố dâu", 68000, None),
    (73, "Nước chanh dây", 55000, None),
    (74, "Chả giò rế (4 cuốn)", 65000, None),
    (74, "Bánh flan caramel", 45000, None),
    # More spa/services
    (90, "Nail art cơ bản", 180000, None),
    (90, "Gội đầu dưỡng sinh 30 phút", 150000, None),
    (93, "Dịch vụ giữ hành lý 24h", 150000, None),
    (93, "Dịch vụ bọc hành lý", 100000, None),
    # More lounge combos
    (82, "Upgrade phòng chờ tiêu chuẩn → VIP", 450000, None),
    (80, "Phòng chờ Lotus transit 3 giờ", 350000, None),
    (81, "Phòng chờ SENS ngày lễ (premium)", 950000, None),
    # Limo
    (92, "Xe đưa đón sân bay - Vũng Tàu", 1800000, None),
    (92, "Xe đưa đón sân bay - Bình Dương", 650000, None),
    # FX
    (91, "Phí thu đổi ngoại tệ - Yên Nhật", 80000, None),
    (91, "Phí thu đổi ngoại tệ - Won Hàn", 70000, None),
    # More crafts
    (44, "Túi thổ cẩm Tây Nguyên", 250000, "[4,5,8]"),
    (44, "Tranh đông hồ in canvas 30x40cm", 180000, "[4,8]"),
    (44, "Set đũa gỗ khảm trai (6 đôi)", 280000, "[4,2]"),
    # More tobacco
    (23, "Thuốc lá Parliament (1 tút)", 400000, "[11]"),
    (23, "Xì gà Romeo y Julieta (hộp 5)", 2200000, "[5,11]"),
    # More watches
    (32, "Đồng hồ Garmin Venu 3", 8500000, "[5,6]"),
    (32, "Đồng hồ Orient Bambino 40.5mm", 4500000, "[4]"),
    # More bags
    (33, "Balo Herschel Little America", 2200000, "[5,7]"),
    (33, "Túi crossbody Lacoste Classic", 2800000, "[7,10]"),
    # More eyewear
    (31, "Kính mắt Persol PO0714", 4800000, "[11,5]"),
]

for item in extras:
    if len(item) == 4:
        cat_id, name, price, nat = item
    else:
        cat_id, name, price = item[:3]
        nat = None

    # Cost ratios by category
    if cat_id in (11, 12, 21, 22, 31, 32, 33):
        cost = int(price * 0.33)
    elif cat_id in (41, 42, 43):
        cost = int(price * 0.40)
    elif cat_id in (44, 50):
        cost = int(price * 0.35)
    elif cat_id == 60:
        cost = int(price * 0.50)
    elif cat_id in (70, 71, 72, 73, 74):
        cost = int(price * 0.25)
    elif cat_id in (80, 81, 82):
        cost = int(price * 0.20)
    elif cat_id == 23:
        cost = int(price * 0.33)
    elif cat_id in (90, 93):
        cost = int(price * 0.25)
    elif cat_id == 91:
        cost = int(price * 0.30)
    elif cat_id == 92:
        cost = int(price * 0.40)
    else:
        cost = int(price * 0.35)

    nat_sql = "NULL" if nat is None else nat
    products.append((pid, name, f"EX{pid-999:04d}", cat_id, price, cost, nat_sql, 0.005))
    pid += 1

print(f"-- Additional products: {len(products)}")
print()

def sql_esc(s):
    return s.replace("'", "''")

batch_size = 50
for batch_start in range(0, len(products), batch_size):
    batch = products[batch_start:batch_start + batch_size]
    print("INSERT INTO products (product_id, product_name, product_code, category_id, unit_price_vnd, cost_price_vnd, is_active, popularity_weight, nationality_preference) VALUES")
    lines = []
    for p in batch:
        pid_v, name, code, cat, price, cost, nat, weight = p
        name_esc = sql_esc(name)
        if nat == "NULL":
            nat_val = "NULL"
        else:
            nat_val = f"'{nat}'"
        lines.append(f"({pid_v}, '{name_esc}', '{code}', {cat}, {price}, {cost}, TRUE, {weight:.4f}, {nat_val})")
    print(",\n".join(lines) + ";")
    print()
