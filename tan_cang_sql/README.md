# SNP Port Demo Database — `snp_port_demo`

Mock database mô phỏng hệ thống khai thác cảng của **Tổng công ty Tân Cảng Sài Gòn (SNP)** — phục vụ demo BI/AI cho board (Hội đồng thành viên).

## Phạm vi data

- **4 cụm cảng:** Cát Lái (TP.HCM), Cái Mép (BR-VT), Hải Phòng, Miền Trung (Quy Nhơn)
- **8 terminal, 22 cầu bến, 62 cẩu STS, 65 block bãi, 138 tàu, 14 hãng tàu**
- **24 tháng:** 2024-05-01 → 2026-04-30
- **~110k transaction rows:** 16.7k chuyến tàu + 45.3k log cẩu + 47.5k yard snapshot

## 3 demo scenarios đã nhúng trong data

1. **Tổng quan tháng gần nhất + YoY** — `fact_vessel_calls` SUM theo cụm.
2. **Cảng kém hiệu quả** — anomaly nhúng tại **Cát Lái Terminal B**, 6 tuần cuối (2026-03-20 → 2026-04-30):
   - 2 cẩu cụ thể (`CL-B-02-C02`, `CL-B-03-C01`) downtime tăng → availability tụt 96% → 77%.
   - Bãi Terminal B occupancy ramp 84% → 88-92%, rehandle +18%.
   - Hệ quả: GMPH chuyến tàu cập Terminal B giảm ~6% (avg) / ~12% (đỉnh tuần cuối).
3. **What-if +10% sản lượng** — `dim_ports.design_capacity_teu` cho phép tính util.
   - Cát Lái 86% → +10% sẽ vượt trần.
   - Cái Mép 72%, Hải Phòng 60%, Miền Trung 47% — còn dư địa.

## Populate vào MySQL Docker container mới

### 1. Khởi tạo container

```bash
docker run --name mock_database \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=snp_port_demo \
  -p 3306:3306 \
  -d mysql:8.0 \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_unicode_ci
```

### 2. Chờ MySQL sẵn sàng

```bash
docker exec mock_database mysqladmin ping -uroot -proot --wait=30
```

### 3. Populate theo thứ tự

```bash
docker exec -i mock_database mysql -uroot -proot < tan_cang_sql/01_ddl_schema.sql
docker exec -i mock_database mysql -uroot -proot < tan_cang_sql/02_metadata.sql
docker exec -i mock_database mysql -uroot -proot < tan_cang_sql/03_master_data.sql
docker exec -i mock_database mysql -uroot -proot < tan_cang_sql/04_transaction_data.sql
```

### 4. Verify

```bash
docker exec -i mock_database mysql -uroot -proot < tan_cang_sql/05_validation_queries.sql
```

### 5. Reset (nếu cần làm lại)

```bash
docker exec -i mock_database mysql -uroot -proot -e \
  "DROP DATABASE IF EXISTS snp_port_demo;
   CREATE DATABASE snp_port_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
# Rồi chạy lại bước 3
```

## Cấu trúc file

| File | Mục đích | Size |
|---|---|---:|
| `01_ddl_schema.sql` | DROP + CREATE database + 15 tables + indexes + comments | ~12 KB |
| `02_metadata.sql` | INSERT metadata (`_meta_tables`, `_meta_columns`, `_meta_kpi`, `_meta_glossary`) | ~15 KB |
| `03_master_data.sql` | INSERT dimension tables (~1.1k rows) | ~58 KB |
| `04_transaction_data.sql` | INSERT fact tables (~110k rows, 529 batched INSERTs) | ~8 MB |
| `05_validation_queries.sql` | SELECT queries verify + dry-run 3 scenarios | ~7 KB |

## Tables

### Dimension (8)

| Table | Rows | Mô tả |
|---|---:|---|
| `dim_ports` | 4 | Cụm cảng (Cát Lái, Cái Mép, Hải Phòng, Miền Trung) + công suất thiết kế |
| `dim_terminals` | 8 | Terminal trong từng cảng |
| `dim_berths` | 22 | Cầu bến |
| `dim_cranes` | 62 | Cẩu bờ STS |
| `dim_yard_blocks` | 65 | Block bãi container |
| `dim_shipping_lines` | 14 | Hãng tàu (Maersk, MSC, ONE, ...) |
| `dim_vessels` | 138 | Tàu container (Feeder/Panamax/Post-Panamax) |
| `dim_calendar` | 730 | 24 tháng + flags Tết/peak season |

### Fact (3)

| Table | Rows | Grain |
|---|---:|---|
| `fact_vessel_calls` | 16,666 | 1 row / chuyến tàu cập cảng |
| `fact_crane_logs` | 45,260 | 1 row / cẩu / ngày |
| `fact_yard_snapshots` | 47,450 | 1 row / block / ngày |

### Metadata (4) — nguồn truth cho AI engine

| Table | Rows | Mô tả |
|---|---:|---|
| `_meta_tables` | 11 | Mô tả từng table (VI/EN + business context) |
| `_meta_columns` | 26 | Mô tả từng column (đơn vị + ví dụ) |
| `_meta_kpi` | 13 | Công thức SQL các KPI chính |
| `_meta_glossary` | 20 | Thuật ngữ ngành (TEU, GMPH, rehandle, dwell...) |

## Magnitude data (sanity check)

- **Tổng throughput last 12 months:** ~8,9 triệu TEU (4-cluster scope)
- **Cát Lái last 12mo:** ~5,6 triệu TEU (utilization 86%)
- **Tổng doanh thu khai thác cảng / năm:** ~23.500 tỷ VND (xấp xỉ mảng cảng của SNP, chưa gồm logistics + vận tải biển)
- **ASP:** ~1,8 – 2,2 triệu VND/TEU

> Lưu ý: Tổng SNP công bố ~10,81 triệu TEU và ~32.000 tỷ doanh thu bao gồm 26 cảng + nhiều mảng kinh doanh; data này chỉ scope 4 cụm cảng container chính.

## Anomaly target — Cát Lái Terminal B (Scenario 2)

| Trường | Bình thường | Anomaly window (last 6w) |
|---|---|---|
| Cẩu `CL-B-02-C02` availability | ~96% | ~77% |
| Cẩu `CL-B-03-C01` availability | ~96% | ~79% |
| Cẩu `CL-B-02-C02` downtime | 0.9h/ngày | 5.2h/ngày |
| Yard Terminal B occupancy | ~84% | ~88% (đỉnh 92%) |
| Yard Terminal B rehandle | ~10% | ~11% (đỉnh 13%) |
| Vessel calls Terminal B GMPH | ~30 | ~28 (đỉnh giảm tới 26) |
| Vessel turnaround Terminal B | ~30h | ~33h |

Anomaly chỉ tồn tại ở Cát Lái Terminal B, các terminal khác giữ bình thường.

## Connection info

- Host: `localhost`
- Port: `3306`
- Database: `snp_port_demo`
- User / Password: `root / root`
- Charset: `utf8mb4`
