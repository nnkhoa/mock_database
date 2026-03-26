# Mock Database

MySQL 8.0 container chứa 2 databases mock data cho AI BI demo.

## Databases

| Database | Mô tả | Tables |
|----------|-------|--------|
| `lc_aibi` | Dữ liệu vaccine Long Châu (2024–2026) | 6 tables, ~29K sales orders |
| `textile_tcm_demo` | Dữ liệu dệt may TCM (2024–2025) | 26 tables, ~5K sales orders |

## Yêu cầu

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)

## Cài đặt

```bash
git clone <repo>
cd mock_database

# Lần đầu (fresh)
docker compose up -d
```

MySQL sẽ tự động tạo cả 2 databases và load toàn bộ dữ liệu. Khoảng **1–2 phút**.

## Kiểm tra

```bash
# Kết nối
docker exec -it mock_database mysql -u root -proot

# Xem databases
SHOW DATABASES;

# Kiểm tra lc_aibi
USE lc_aibi;
SELECT table_name, table_rows FROM information_schema.tables WHERE table_schema = 'lc_aibi';

# Kiểm tra TCM
USE textile_tcm_demo;
SELECT table_name, table_rows FROM information_schema.tables WHERE table_schema = 'textile_tcm_demo';
```

## Thông tin kết nối

| Thông số | Giá trị |
|----------|---------|
| Host | `127.0.0.1` |
| Port | `3306` |
| User | `root` |
| Password | `root` |

## Reset dữ liệu

```bash
docker compose down -v
docker compose up -d
```
