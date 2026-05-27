# SNP v2 — Cảng Tân Cảng Cát Lái Demo Database

Mock database mô phỏng vận hành cảng container Cát Lái cho Tổng Công ty Tân Cảng Sài Gòn (SNP). Dùng để demo AI engine + MCP cho Giám đốc CNTT / Chuyển đổi số.

- **Database:** `catlai_demo`
- **Time range:** 01/12/2024 → 31/05/2026 (18 tháng + 15 ngày forward cho vessel schedule tới 15/06/2026)
- **Mốc "hiện tại" của demo:** 31/05/2026
- **Anomaly hội tụ:** Thứ Năm 04/06/2026 ("bão kép")
- **Tổng số bảng:** 19 (8 dim + 7 fact + 4 meta)
- **Tổng số rows:** ~628.000

## Cấu trúc file

| File | Nội dung | Kích thước |
|---|---|---|
| `01_ddl_schema.sql` | CREATE DATABASE + CREATE TABLE + indexes + FK | ~20KB |
| `02_metadata.sql` | INSERT cho 4 _meta tables (~104 rows) | ~21KB |
| `03_master_data.sql` | INSERT cho 8 dim tables (~970 rows) | ~70KB |
| `04_transaction_data.sql` | INSERT cho 7 fact tables (~628k rows) | ~43MB |
| `05_validation_queries.sql` | SELECT mẫu để verify + demo scenario | ~7KB |

Mỗi file chạy độc lập theo thứ tự 01 → 02 → 03 → 04 (file 05 chỉ là SELECT).

## Hướng dẫn reproduce trên máy mới

### 1. Khởi tạo MySQL container

```bash
docker run --name mock_database \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=catlai_demo \
  -p 3306:3306 \
  -d mysql:8.0 \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_unicode_ci
```

### 2. Chờ MySQL sẵn sàng

```bash
docker exec mock_database mysqladmin ping -uroot -proot --wait=30
```

### 3. Populate data theo thứ tự

```bash
docker exec -i mock_database mysql -uroot -proot < 01_ddl_schema.sql
docker exec -i mock_database mysql -uroot -proot < 02_metadata.sql
docker exec -i mock_database mysql -uroot -proot < 03_master_data.sql
docker exec -i mock_database mysql -uroot -proot < 04_transaction_data.sql
```

File 04 lớn ~43MB, mất 1-3 phút tùy máy.

### 4. Verify

```bash
docker exec -i mock_database mysql -uroot -proot < 05_validation_queries.sql
```

### 5. Reset (nếu cần làm lại)

```bash
docker exec -i mock_database mysql -uroot -proot -e \
  "DROP DATABASE IF EXISTS catlai_demo; CREATE DATABASE catlai_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

Rồi chạy lại bước 3-4.

## Schema tổng quan

### 8 dimension tables (~970 rows)
| Bảng | Rows | Vai trò |
|---|---|---|
| `dim_calendar` | 562 | Trục thời gian, cờ lễ VN, hệ số mùa vụ |
| `dim_shift` | 3 | 3 ca (6-14, 14-22, 22-6) |
| `dim_block` | 20 | 13 thường (B01-B13) + 3 reefer (R01-R03) + 3 rỗng (E01-E03) + 1 OOG (S01) |
| `dim_gate` | 10 | 4 nhập + 4 xuất + 2 hỗn hợp, 350 GD/giờ/cổng |
| `dim_shipping_line` | 40 | Maersk/MSC/CMA CGM/ONE/.../Gemadept/Tân Cảng |
| `dim_vessel` | 150 | 105 feeder + 30 sà lan + 15 tàu mẹ |
| `dim_container_type` | 8 | 20DC/40DC/40HC/45HC/20RF/40RF/OOG/ISO |
| `dim_equipment` | 177 | 22 QC + 60 RTG + 15 RS + 80 xe đầu kéo |

### 7 fact tables (~628k rows)
| Bảng | Rows | Grain |
|---|---|---|
| `fact_yard_occupancy` ⭐ | ~266k | snapshot giờ × block |
| `fact_container_inventory` ⭐ | ~53k | container hiện đang ở bãi (snapshot 31/05/2026) |
| `fact_gate_transaction` ⭐ | ~133k | giờ × cổng |
| `fact_truck_turnaround` | ~114k | trip (chỉ 90 ngày 01/03-31/05/2026) |
| `fact_vessel_schedule` ⭐ | ~500 | chuyến tàu (gồm forward tới 15/06/2026) |
| `fact_throughput` ⭐ | ~13k | ngày × ca × loại container |
| `fact_equipment_usage` | ~47k | ngày × ca × thiết bị (chỉ 90 ngày gần nhất) |

### 4 metadata tables (~104 rows)
| Bảng | Mô tả |
|---|---|
| `_meta_tables` | Mô tả 19 bảng + business_context |
| `_meta_columns` | Mô tả các cột chính (đơn vị, example values) |
| `_meta_kpi` | KPI tree với công thức SQL + benchmark từ ground truth SNP |
| `_meta_glossary` | Từ điển thuật ngữ ngành cảng (TEU/box/rehandle/dwell/QC/RTG...) |

## 4 anomalies hội tụ vào Thứ Năm 04/06/2026

| Anomaly | Bảng affected | Pattern |
|---|---|---|
| **A — Nghẽn bãi** | `fact_yard_occupancy` | B12 ramp 79→95%, B07 ramp 76→91%, R03 ramp 83→97% từ 28/05 đến 04/06. B12 rehandle tăng đột biến (tín hiệu sớm) |
| **B — Ùn cổng** | `fact_gate_transaction` | 04/06 khung 09-11h spike ×1.25 (~2400 GD/h tổng), 14-16h spike ×1.18 |
| **C — Peak sản lượng** | `fact_vessel_schedule` + `fact_throughput` | 04/06: 5 tàu cập (2 mother + 3 feeder), throughput ~21.700 TEU/ngày, Ca 2 = 10.000 TEU |
| **D — Tồn quá hạn** | `fact_container_inventory` | 1.150 cont >30 ngày (308 cont >60 ngày), tập trung 60% ở B12/B07 |

## 6 demo scenarios (xem 05_validation_queries.sql để có SQL mẫu)

1. **S1 — Snapshot khai thác hôm nay** (Q1)
2. **S2 — Dự báo nghẽn bãi B12/B07/R03** (Q2, ⭐)
3. **S3 — Dự báo ùn cổng 04/06** (Q3, ⭐)
4. **S4 — Dự báo sản lượng tuần tới** (Q4)
5. **S5 — Tổng hợp rủi ro tuần tới** (Q5, ⭐⭐ — chốt demo)
6. **S6 — Hàng tồn quá hạn** (Q6, ⭐)

## Lưu ý cho AI engine

- **Mốc hiện tại 31/05/2026** — query "hôm nay/yesterday/last week" phải mốc theo ngày này.
- **31/05/2026 là Chủ Nhật** (hệ số 0.75) — traffic hôm nay tự nhiên thấp hơn các Thứ trong tuần. AI engine nên giải thích bối cảnh này khi trả lời S1.
- **`fact_yard_occupancy` là SNAPSHOT** — KHÔNG SUM nhiều snapshot khi tính tồn. Lọc theo (snapshot_date, snapshot_hour) cụ thể.
- **`fact_truck_turnaround` và `fact_equipment_usage` chỉ có 90 ngày gần nhất** (01/03/2026 - 31/05/2026). Trước thời gian này không có chi tiết - dùng `fact_gate_transaction` và `fact_throughput` cho trend dài hạn.
- **Vessel schedule kéo dài tới 15/06/2026** với status='Sắp cập'/'Kế hoạch' cho forward-looking.
- **Box ↔ TEU**: 1 box = 1,6 TEU bình quân (cơ cấu 40% 20' + 60% 40'/45').
- **Doanh thu/lợi nhuận** trong `_meta_kpi` chỉ là TOÀN HỆ THỐNG SNP (cả logistics + vận tải + depot), KHÔNG mock dữ liệu tài chính chi tiết cho Cát Lái.

## Calibration đã dùng

- **Daily base:** 8.400 box/ngày = ~13.400 TEU/ngày (trước khi áp seasonality + growth)
- **Growth:** +8% YoY linear
- **Monthly seasonality:** T2=0.72 (Tết), T11=1.20 (peak xuất khẩu), T7-T8 mùa mưa giảm nhẹ
- **Weekly:** Thứ 3 đỉnh (1.10), Chủ Nhật đáy (0.75)
- **Hourly:** 09-11h và 14-16h cao điểm (1.45 / 1.35), 00-05h thấp (0.45)
- **Noise:** ±12%
- **Pareto:** Top 8/40 hãng tàu chiếm ~70% inventory

## Validation summary (đã chạy)

✅ 18/18 ground truth band checks PASS  
✅ Demo scenario dry-run cho cả 6 scenarios — anomaly visible đúng kỳ vọng  
✅ Referential integrity, business logic, completeness — 0 violations  
✅ Annual 2025: 5.48M TEU (target 5.3-5.8M)  
✅ Seasonality: T2=9.6k/day, T11=17.6k/day (đỉnh-đáy rõ)
