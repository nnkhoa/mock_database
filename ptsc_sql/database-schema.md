# DATA SCHEMA — PTSC | Dịch vụ Kỹ thuật Dầu khí (Oil & Gas Services / EPC) BI
## Database: `ptsc_demo` (MySQL 8.0, utf8mb4_unicode_ci)
## Phạm vi: 01/2024 → 09/2025 (21 tháng) | "Hiện tại" = cuối 09/2025
## Grain trung tâm: DỰ ÁN × THÁNG (project-based, ghi nhận doanh thu theo POC — không phải bán lẻ/transaction)

---

## SƠ ĐỒ QUAN HỆ

```
dim_calendar (month_date PK)
  ├── fact_project_financials_monthly.month_date
  ├── fact_eac_snapshot_monthly.snapshot_month
  ├── fact_progress_monthly.month_date
  ├── fact_project_cost_monthly.month_date
  └── fact_plan_annual.year

dim_project (project_id PK)
  ├── contract_id  ───────────► dim_contract.contract_id
  ├── segment_id   ───────────► dim_segment.segment_id
  ├── region_id    ───────────► dim_region.region_id
  ├── facility_id  ───────────► dim_facility.facility_id
  ├── client_id    ───────────► dim_client.client_id
  └── fact_project_financials_monthly.project_id
      fact_eac_snapshot_monthly.project_id
      fact_progress_monthly.project_id
      fact_project_cost_monthly.project_id

dim_contract (contract_id PK)     -- loại hợp đồng: lump-sum / unit-rate / day-rate
dim_segment  (segment_id PK)      -- 7 mảng, có sub-segment M&C dầu khí vs điện gió
dim_region   (region_id PK)       -- trong nước (3 miền) + nước ngoài (4 khu vực)
dim_facility (facility_id PK)     -- 6 căn cứ/đơn vị (Vũng Tàu, Dung Quất, Nghi Sơn...)
dim_client   (client_id PK)       -- chủ đầu tư/khách hàng

_meta_tables / _meta_columns / _meta_kpi / _meta_glossary  -- nguồn truth mô tả schema
```

**Quan hệ chính:** `dim_project` là bảng trung tâm nối tất cả dimension khác qua FK, và là khóa nối tới 4 fact table. Mỗi dự án thuộc đúng 1 hợp đồng chính, 1 mảng, 1 khu vực, 1 căn cứ chủ lực, 1 khách hàng.

---

## DIMENSION TABLES

### 1. dim_calendar (~639 rows ngày, hoặc 21 rows nếu grain tháng)
Lịch, dùng để lọc/nhóm theo tháng/quý/năm. Grain khuyến nghị: tháng (month_date = ngày đầu tháng).

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `month_date` | DATE PK | Ngày đầu tháng (YYYY-MM-01) | Khóa nối mọi fact theo tháng |
| `year` | INT | Năm (2024, 2025) | |
| `quarter` | VARCHAR(7) | Quý ('2025-Q3') | Dùng cho so sánh quý |
| `month_num` | INT | Tháng 1–12 | Dùng cho seasonality thời tiết |
| `month_label_vi` | VARCHAR | 'Tháng 9/2025' | Hiển thị |
| `is_high_season_offshore` | TINYINT | 1 nếu mùa khô thuận thi công biển (T12–T5) | Đặc thù ngành |

### 2. dim_segment (7 rows)
Mảng hoạt động / loại hình dịch vụ. Tách M&C dầu khí và M&C điện gió vì biên khác nhau.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `segment_id` | INT PK | | |
| `segment_name` | VARCHAR | Tên mảng tiếng Việt | Xem giá trị bên dưới |
| `segment_group` | VARCHAR | Nhóm ('Cơ khí chế tạo (M&C)', 'Dịch vụ') | Gộp khi hỏi 'M&C' chung |
| `typical_margin_band` | VARCHAR | Dải biên điển hình (tham chiếu) | |

Giá trị `segment_name`: 'Cơ khí dầu khí (M&C)', 'Cơ khí điện gió ngoài khơi (M&C)', 'FSO/FPSO', 'Tàu kỹ thuật & lắp đặt biển', 'Căn cứ cảng & logistics', 'Khảo sát ROV/địa chấn', 'Vận hành bảo dưỡng (O&M)'.

### 3. dim_contract (loại hợp đồng — ~3 loại, N hợp đồng)
Hợp đồng và loại hợp đồng — quyết định profile biên & rủi ro.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `contract_id` | INT PK | | |
| `contract_code` | VARCHAR | Mã HĐ | |
| `contract_type` | VARCHAR | Loại HĐ | 'Trọn gói (Lump-sum EPC/EPCI)', 'Đơn giá (Unit-rate)', 'Theo ngày (Day-rate)' |
| `contract_value_vnd` | DECIMAL(18,0) | Giá trị hợp đồng | VND — KHÔNG phải doanh thu kỳ |
| `sign_date` | DATE | Ngày ký | |
| `planned_completion` | DATE | Ngày hoàn thành dự kiến | Dùng cho projection |
| `risk_level` | VARCHAR | 'Cao'/'Trung bình'/'Thấp' | Lump-sum thường 'Cao' |

### 4. dim_region (7 rows)
Khu vực địa lý dự án.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `region_id` | INT PK | | |
| `region_name` | VARCHAR | Tên khu vực | Xem dưới |
| `is_overseas` | TINYINT | 1 = nước ngoài | DT nước ngoài >50% |

Giá trị: 'Trong nước - Miền Nam', 'Trong nước - Miền Trung', 'Trong nước - Miền Bắc', 'Nước ngoài - Đài Loan', 'Nước ngoài - Trung Đông', 'Nước ngoài - Châu Âu', 'Nước ngoài - Đông Nam Á'.

### 5. dim_facility (6 rows)
Đơn vị/căn cứ thực hiện (quan trọng để tìm nút thắt năng lực).

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `facility_id` | INT PK | | |
| `facility_name` | VARCHAR | Tên căn cứ | |
| `facility_type` | VARCHAR | 'Bãi chế tạo'/'Cảng'/'Depot' | |
| `location_vi` | VARCHAR | Địa điểm | |

Giá trị: 'PTSC Vũng Tàu (Bãi chế tạo M&C)', 'PTSC Sao Mai - Bến Đình', 'PTSC Quảng Ngãi (Dung Quất)', 'PTSC Thanh Hóa (Nghi Sơn)', 'PTSC Đình Vũ (Hải Phòng)', 'PTSC Phú Mỹ'.

### 6. dim_client (~10 rows)
Chủ đầu tư/khách hàng.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `client_id` | INT PK | | |
| `client_name` | VARCHAR | Tên khách hàng | |
| `client_country` | VARCHAR | Quốc gia | |

Giá trị mẫu: 'Petrovietnam (PVN)', 'Phú Quốc POC', 'Biển Đông POC (BIENDONG POC)', 'Ørsted', 'CIP', 'SembCorp', 'Aramco', 'QatarEnergy'.

### 7. dim_project (~50 rows) ⭐ BẢNG TRUNG TÂM
Dự án — grain trung tâm của toàn bộ mô hình.

| Cột | Kiểu | Mô tả | Ghi chú |
|---|---|---|---|
| `project_id` | INT PK | | |
| `project_name` | VARCHAR | Tên dự án tiếng Việt | Ví dụ 'EPCI#2 Lô B - Ô Môn (Giàn thu gom CPP)' |
| `contract_id` | INT FK | | → dim_contract |
| `segment_id` | INT FK | | → dim_segment |
| `region_id` | INT FK | | → dim_region |
| `facility_id` | INT FK | Căn cứ chủ lực | → dim_facility |
| `client_id` | INT FK | | → dim_client |
| `project_type` | VARCHAR | 'EPCI', 'Cho thuê FSO', 'O&M', 'Khảo sát'... | Loại dự án (góc nhìn #3) |
| `contract_value_vnd` | DECIMAL(18,0) | Giá trị hợp đồng | VND |
| `bid_margin_pct` | DECIMAL(5,2) | Biên LN ký ban đầu | % — mốc so sánh EAC |
| `start_date` | DATE | Khởi công | |
| `planned_completion` | DATE | Hoàn thành dự kiến | |
| `status` | VARCHAR | 'Đang thực hiện'/'Hoàn thành'/'Chuẩn bị' | |
| `remaining_backlog_vnd` | DECIMAL(18,0) | Backlog còn lại | Dùng projection |

---

## FACT TABLES

### 8. fact_project_financials_monthly ⭐ (FACT CHÍNH — ~50 dự án × 21 tháng → 1.000+ rows)
Doanh thu ghi nhận (POC), chi phí, lợi nhuận gộp thực tế và kế hoạch — theo dự án × tháng.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `id` | BIGINT PK | | |
| `project_id` | INT FK | | → dim_project |
| `month_date` | DATE FK | Tháng | → dim_calendar |
| `revenue_recognized_vnd` | DECIMAL(18,0) | Doanh thu ghi nhận theo POC kỳ này | VND |
| `plan_revenue_vnd` | DECIMAL(18,0) | Doanh thu kế hoạch kỳ | VND |
| `cogs_vnd` | DECIMAL(18,0) | Giá vốn (chi phí trực tiếp) | VND |
| `gross_profit_vnd` | DECIMAL(18,0) | LN gộp = revenue − cogs | VND |
| `plan_gross_profit_vnd` | DECIMAL(18,0) | LN gộp kế hoạch | VND |
| `gross_margin_pct` | DECIMAL(5,2) | Biên gộp thực hiện | % |

⚠️ **Doanh thu kỳ LUÔN dùng `revenue_recognized_vnd`, KHÔNG dùng contract_value.** ⚠️ SUM theo dự án = SUM theo mảng = tổng TCT (đã đảm bảo consistency).

### 9. fact_eac_snapshot_monthly ⭐ (FACT CẢNH BÁO — snapshot theo dự án × tháng)
Chụp lại dự báo tỷ suất LN cuối hợp đồng (EAC) mỗi tháng — trái tim của kịch bản cảnh báo margin erosion.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `id` | BIGINT PK | | |
| `project_id` | INT FK | | → dim_project |
| `snapshot_month` | DATE FK | Tháng chụp snapshot | → dim_calendar |
| `bid_margin_pct` | DECIMAL(5,2) | Biên ký ban đầu (cố định) | % |
| `eac_margin_pct` | DECIMAL(5,2) | Tỷ suất LN dự kiến cuối HĐ tại thời điểm snapshot | % |
| `eac_cost_total_vnd` | DECIMAL(18,0) | Tổng chi phí dự toán mới (EAC) | VND |
| `eac_profit_vnd` | DECIMAL(18,0) | LN dự kiến cuối HĐ | VND |
| `cost_overrun_reason` | VARCHAR(255) | Lý do vượt chi phí (nếu có) | text tiếng Việt |

⚠️ **SNAPSHOT — KHÔNG SUM nhiều tháng.** Xem trạng thái hiện tại: `WHERE snapshot_month='2025-09-01'`. Xem xu hướng erosion: lọc 1 project qua nhiều tháng. **Margin erosion = eac_margin_pct − bid_margin_pct.**

### 10. fact_progress_monthly ⭐ (SẢN LƯỢNG & TIẾN ĐỘ — dự án × tháng)
Sản lượng thi công vật lý và % hoàn thành (POC) — kế hoạch vs thực tế.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `id` | BIGINT PK | | |
| `project_id` | INT FK | | → dim_project |
| `month_date` | DATE FK | | → dim_calendar |
| `planned_volume_ton` | DECIMAL(12,1) | Sản lượng chế tạo kế hoạch | tấn |
| `actual_volume_ton` | DECIMAL(12,1) | Sản lượng thực hiện | tấn |
| `planned_manhours` | INT | Man-hours kế hoạch | giờ công |
| `actual_manhours` | INT | Man-hours thực hiện | giờ công |
| `planned_poc_pct` | DECIMAL(5,2) | % hoàn thành lũy kế kế hoạch | % |
| `actual_poc_pct` | DECIMAL(5,2) | % hoàn thành lũy kế thực tế | % |

⚠️ POC lũy kế ≤ 100%. Sản lượng chậm → doanh thu POC hụt (nối sang bảng 8).

### 11. fact_project_cost_monthly (CHI TIẾT CHI PHÍ — dự án × tháng × loại chi phí)
Bóc tách chi phí để tìm nguyên nhân bào mòn margin.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `id` | BIGINT PK | | |
| `project_id` | INT FK | | → dim_project |
| `month_date` | DATE FK | | → dim_calendar |
| `cost_category` | VARCHAR | Loại chi phí | 'Thép/Vật tư', 'Nhân công (man-hours)', 'Thiết bị', 'Thầu phụ', 'Tỷ giá (FX)' |
| `budget_cost_vnd` | DECIMAL(18,0) | Chi phí dự toán | VND |
| `actual_cost_vnd` | DECIMAL(18,0) | Chi phí thực tế | VND |
| `variance_pct` | DECIMAL(6,2) | Chênh lệch vs dự toán | % |

⚠️ Dùng để trả lời "margin tụt do tiến độ hay giá vật tư" — so actual vs budget theo category.

### 12. fact_plan_annual (KẾ HOẠCH NĂM — theo mảng & toàn TCT)
Kế hoạch năm để so về đích.

| Cột | Kiểu | Mô tả | Đơn vị |
|---|---|---|---|
| `id` | INT PK | | |
| `year` | INT | | |
| `segment_id` | INT FK | NULL = toàn TCT | → dim_segment |
| `plan_revenue_vnd` | DECIMAL(18,0) | DT kế hoạch năm | VND |
| `plan_npat_vnd` | DECIMAL(18,0) | LNST kế hoạch năm | VND |
| `internal_target_npat_vnd` | DECIMAL(18,0) | Mục tiêu nội bộ (stretch) | VND |

⚠️ `plan_revenue` 2025 = 22.500 tỷ (công bố); `internal_target_npat` 2025 = 1.200 tỷ.

---

## SQL TEMPLATES

### T1. Doanh thu & LN gộp toàn TCT theo mảng, 1 quý, vs kế hoạch (Scenario 1)
```sql
SELECT s.segment_name,
       SUM(f.revenue_recognized_vnd)   AS dt_thuc_hien,
       SUM(f.plan_revenue_vnd)         AS dt_ke_hoach,
       ROUND(SUM(f.revenue_recognized_vnd)/SUM(f.plan_revenue_vnd)*100,1) AS pct_ke_hoach,
       SUM(f.gross_profit_vnd)         AS ln_gop,
       ROUND(SUM(f.gross_profit_vnd)/SUM(f.revenue_recognized_vnd)*100,1) AS bien_gop_pct
FROM fact_project_financials_monthly f
JOIN dim_project p ON p.project_id = f.project_id
JOIN dim_segment s ON s.segment_id = p.segment_id
JOIN dim_calendar c ON c.month_date = f.month_date
WHERE c.quarter = '2025-Q3'
GROUP BY s.segment_name
ORDER BY dt_thuc_hien DESC;
```

### T2. Xếp hạng bào mòn biên LN cuối hợp đồng (Scenario 2 — WOW)
```sql
SELECT p.project_name,
       e.bid_margin_pct,
       e.eac_margin_pct,
       ROUND(e.eac_margin_pct - e.bid_margin_pct,1) AS margin_erosion_diem,
       p.contract_value_vnd,
       ROUND((e.bid_margin_pct - e.eac_margin_pct)/100 * p.contract_value_vnd,0) AS ln_co_the_hut_vnd,
       e.cost_overrun_reason
FROM fact_eac_snapshot_monthly e
JOIN dim_project p ON p.project_id = e.project_id
WHERE e.snapshot_month = '2025-09-01'
ORDER BY margin_erosion_diem ASC   -- âm nhất lên đầu
LIMIT 10;
```

### T3. Xu hướng EAC margin của 1 dự án qua các snapshot (Scenario 2 drill)
```sql
SELECT e.snapshot_month, e.bid_margin_pct, e.eac_margin_pct
FROM fact_eac_snapshot_monthly e
JOIN dim_project p ON p.project_id = e.project_id
WHERE p.project_name LIKE '%EPCI#2 Lô B%'
ORDER BY e.snapshot_month;
```

### T4. Cost breakdown 1 dự án vs dự toán (Scenario 2 — nguyên nhân)
```sql
SELECT cost_category,
       SUM(budget_cost_vnd) AS du_toan,
       SUM(actual_cost_vnd) AS thuc_te,
       ROUND((SUM(actual_cost_vnd)-SUM(budget_cost_vnd))/SUM(budget_cost_vnd)*100,1) AS vuot_pct
FROM fact_project_cost_monthly ct
JOIN dim_project p ON p.project_id = ct.project_id
WHERE p.project_name LIKE '%EPCI#2 Lô B%'
GROUP BY cost_category
ORDER BY vuot_pct DESC;
```

### T5. Sản lượng thực hiện/kế hoạch & ảnh hưởng doanh thu (Scenario 3)
```sql
SELECT p.project_name,
       pr.planned_volume_ton, pr.actual_volume_ton,
       ROUND(pr.actual_volume_ton/pr.planned_volume_ton*100,1) AS san_luong_pct_kh,
       pr.actual_poc_pct, pr.planned_poc_pct,
       f.revenue_recognized_vnd, f.plan_revenue_vnd,
       (f.plan_revenue_vnd - f.revenue_recognized_vnd) AS dt_hut_vnd
FROM fact_progress_monthly pr
JOIN dim_project p ON p.project_id = pr.project_id
JOIN fact_project_financials_monthly f
     ON f.project_id = pr.project_id AND f.month_date = pr.month_date
WHERE pr.month_date = '2025-09-01'
  AND pr.actual_volume_ton < pr.planned_volume_ton
ORDER BY san_luong_pct_kh ASC;
```

### T6. Dự báo về đích năm: DT & LN 2025 vs kế hoạch (Scenario 4)
```sql
SELECT c.year,
       SUM(f.revenue_recognized_vnd) AS dt_luy_ke,
       (SELECT plan_revenue_vnd FROM fact_plan_annual WHERE year=2025 AND segment_id IS NULL) AS dt_kh_nam,
       SUM(f.gross_profit_vnd)       AS ln_gop_luy_ke
FROM fact_project_financials_monthly f
JOIN dim_calendar c ON c.month_date = f.month_date
WHERE c.year = 2025
GROUP BY c.year;
-- Projection Q4: dùng remaining_backlog_vnd (dim_project) và eac_margin_pct để ước LN cả năm.
```

### T7. Cơ cấu DT vs cơ cấu LN — mảng điện gió (Scenario 5)
```sql
SELECT s.segment_name,
       SUM(f.revenue_recognized_vnd) AS dt,
       ROUND(SUM(f.revenue_recognized_vnd)/(SELECT SUM(revenue_recognized_vnd)
             FROM fact_project_financials_monthly f2 JOIN dim_calendar c2 ON c2.month_date=f2.month_date
             WHERE c2.year=2025)*100,1) AS pct_dt,
       SUM(f.gross_profit_vnd) AS ln_gop,
       ROUND(SUM(f.gross_profit_vnd)/SUM(f.revenue_recognized_vnd)*100,1) AS bien_gop
FROM fact_project_financials_monthly f
JOIN dim_project p ON p.project_id=f.project_id
JOIN dim_segment s ON s.segment_id=p.segment_id
JOIN dim_calendar c ON c.month_date=f.month_date
WHERE c.year=2025
GROUP BY s.segment_name
ORDER BY dt DESC;
```

### T8. Biên LN theo loại hợp đồng × khu vực (Scenario 6)
```sql
SELECT ct.contract_type, r.region_name,
       SUM(f.revenue_recognized_vnd) AS dt,
       ROUND(SUM(f.gross_profit_vnd)/SUM(f.revenue_recognized_vnd)*100,1) AS bien_gop,
       COUNT(DISTINCT p.project_id) AS so_du_an
FROM fact_project_financials_monthly f
JOIN dim_project p  ON p.project_id = f.project_id
JOIN dim_contract ct ON ct.contract_id = p.contract_id
JOIN dim_region r    ON r.region_id = p.region_id
JOIN dim_calendar c  ON c.month_date = f.month_date
WHERE c.year = 2025
GROUP BY ct.contract_type, r.region_name
ORDER BY bien_gop DESC;
```

---

## JOIN WARNINGS

1. **fact_project_financials_monthly ↔ fact_progress_monthly / fact_project_cost_monthly:** cùng grain (project × month) → JOIN trên (project_id, month_date). An toàn nếu đúng cặp khóa; nếu chỉ join project_id sẽ nhân chéo các tháng → nhớ thêm điều kiện month.
2. **fact_eac_snapshot_monthly = SNAPSHOT:** LUÔN `WHERE snapshot_month = '<tháng>'` khi xem trạng thái. TUYỆT ĐỐI KHÔNG SUM nhiều snapshot (sẽ nhân đôi/ba dự báo). Nhiều tháng chỉ để vẽ xu hướng erosion 1 dự án.
3. **fact_project_cost_monthly có nhiều dòng/dự án/tháng** (mỗi cost_category 1 dòng): khi JOIN với financials phải aggregate cost trước (GROUP BY project_id, month_date) rồi mới JOIN, nếu không sẽ nhân đôi doanh thu.
4. **dim_project × dim_contract:** 1 dự án = 1 hợp đồng chính. Nếu sau này 1 hợp đồng có nhiều gói → cẩn thận nhân dòng; hiện tại mapping 1-1.
5. **contract_value_vnd ≠ doanh thu:** Đừng SUM contract_value để ra doanh thu kỳ. Doanh thu kỳ = revenue_recognized_vnd.
6. **Điện gió vs dầu khí trong M&C:** khi hỏi "M&C" chung → gộp 2 segment; khi phân tích biên → tách. Dùng `dim_segment.segment_group` để gộp, `segment_name` để tách.
7. **fact_plan_annual segment_id NULL:** dòng segment_id IS NULL là kế hoạch TOÀN TCT → đừng gộp nhầm vào GROUP BY theo mảng.

---

## ĐƠN VỊ TIỀN TỆ

| Bảng | Cột | Đơn vị |
|---|---|---|
| fact_project_financials_monthly | revenue_recognized_vnd, plan_revenue_vnd, cogs_vnd, gross_profit_vnd, plan_gross_profit_vnd | VND |
| fact_eac_snapshot_monthly | eac_cost_total_vnd, eac_profit_vnd | VND |
| fact_project_cost_monthly | budget_cost_vnd, actual_cost_vnd | VND |
| fact_plan_annual | plan_revenue_vnd, plan_npat_vnd, internal_target_npat_vnd | VND |
| dim_project / dim_contract | contract_value_vnd, remaining_backlog_vnd | VND |
| fact_progress_monthly | planned_volume_ton, actual_volume_ton | tấn |
| fact_progress_monthly | planned_manhours, actual_manhours | giờ công (man-hours) |
| các cột *_pct | bid_margin_pct, eac_margin_pct, gross_margin_pct, *_poc_pct | % |

Format hiển thị cho board:
- > 1.000 tỷ: "X.XXX tỷ" (ví dụ 24.986 tỷ)
- 1–1.000 tỷ: "XXX tỷ"
- < 1 tỷ: "XXX triệu"
- Phần trăm: 1 chữ số thập phân; chênh lệch biên dùng "điểm %" (ví dụ tụt 5,3 điểm).
