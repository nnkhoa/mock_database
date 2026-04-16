# Gemadept BI Demo Database — `gemadept_bi_demo`

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
docker run --name mock_database \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=gemadept_bi_demo \
  -p 3306:3306 \
  -d mysql:8.0 \
  --character-set-server=utf8mb4 \
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
docker exec -i mock_database mysql -uroot -proot -e \
  "DROP DATABASE IF EXISTS gemadept_bi_demo; CREATE DATABASE gemadept_bi_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
# Rồi chạy lại bước 3-4
```

## Kết nối AI engine
Database chứa 4 metadata tables (`_meta_tables`, `_meta_columns`, `_meta_kpi`, `_meta_glossary`) sẵn sàng cho MCP/Claude integration. Mọi câu hỏi MKT Manager dạng tự nhiên đều có thể trả lời bằng SQL trên schema này.

**Cross-reference key:** scenarios 2 và 4 đặc biệt yêu cầu JOIN giữa `port_calls` (internal) + `port_vessel_schedule_external` (cảng vụ public, gồm cả đối thủ) + `news_events` (tin ngành) — đây là wow factor chính của demo.

Timezone: ICT (UTC+7).
