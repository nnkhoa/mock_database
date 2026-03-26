# Mock Database

MySQL 8.0 container chứa 2 databases mock data cho AI BI demo.

## Databases

| Database | Mô tả | Thời gian | Records |
|----------|-------|-----------|---------|
| `lc_aibi` | Dữ liệu vaccine Long Châu | 2024–2026 | ~29K sales orders |
| `textile_tcm_demo` | Dữ liệu dệt may TCM | 2024–2025 | ~5K production orders |

---

## 1. Khởi động Database

### Yêu cầu
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)

### Cài đặt

```bash
git clone <repo>
cd mock_database

# Lần đầu — tự tạo database và load data (~1-2 phút)
docker compose up -d

# Kiểm tra đã sẵn sàng chưa
docker ps
```

### Reset dữ liệu

```bash
docker compose down -v   # xóa volume cũ
docker compose up -d     # tạo lại từ đầu
```

### Thông tin kết nối

| Thông số | Giá trị |
|----------|---------|
| Host | `127.0.0.1` |
| Port | `3306` |
| User | `root` |
| Password | `root` |
| Databases | `lc_aibi`, `textile_tcm_demo` |

---

## 2. Chạy MCP Server

MCP server cho phép Claude.ai Web kết nối trực tiếp vào database để trả lời câu hỏi bằng ngôn ngữ tự nhiên.

### Yêu cầu
- Node.js (có `npx`)
- [ngrok](https://ngrok.com) đã cài
- File `.env.mcp` (xem bên dưới)

### Cấu hình `.env.mcp`

Tạo file `.env.mcp` trong thư mục repo (không commit file này):

```bash
# Long Châu — ngrok account 1
LONGCHAU_NGROK_DOMAIN="<your-domain>.ngrok-free.dev"
LONGCHAU_NGROK_AUTHTOKEN="<authtoken-account-1>"

# TCM — ngrok account 2
TCM_NGROK_DOMAIN="<your-domain>.ngrok-free.dev"
TCM_NGROK_AUTHTOKEN="<authtoken-account-2>"
```

> Lấy authtoken tại [dashboard.ngrok.com/authtokens](https://dashboard.ngrok.com/authtokens)
> Lấy static domain tại [dashboard.ngrok.com/domains](https://dashboard.ngrok.com/domains)

### Chạy MCP cho Long Châu (`lc_aibi`)

```bash
bash start_longchau_mcp.sh
```

Sau khi chạy, thêm integration vào Claude.ai:
> Claude.ai → Settings → Integrations → Add Integration
> URL: `https://<LONGCHAU_NGROK_DOMAIN>/mcp`

### Chạy MCP cho TCM (`textile_tcm_demo`)

```bash
bash start_tcm_mcp.sh
```

Sau khi chạy, thêm integration vào Claude.ai:
> Claude.ai → Settings → Integrations → Add Integration
> URL: `https://<TCM_NGROK_DOMAIN>/mcp`

### Chạy cả 2 cùng lúc

```bash
# Terminal 1
bash start_longchau_mcp.sh

# Terminal 2
bash start_tcm_mcp.sh
```

> **Lưu ý:** 2 MCP server dùng 2 port khác nhau (8000 và 8001) và 2 ngrok account khác nhau nên có thể chạy song song.

### Ports

| Service | Port | Database |
|---------|------|----------|
| Long Châu MCP | 8000 | `lc_aibi` |
| TCM MCP | 8001 | `textile_tcm_demo` |

---

## 3. Kiểm tra Database

```bash
# Kết nối MySQL
docker exec -it mock_database mysql -u root -proot

# Xem tất cả databases
SHOW DATABASES;

# Kiểm tra Long Châu
USE lc_aibi;
SELECT table_name, table_rows
FROM information_schema.tables
WHERE table_schema = 'lc_aibi';

# Kiểm tra TCM
USE textile_tcm_demo;
SELECT table_name, table_rows
FROM information_schema.tables
WHERE table_schema = 'textile_tcm_demo';
```
