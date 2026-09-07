# pvfcco_phase1_demo — Mock Database

**Khách hàng:** Tổng công ty Phân bón và Hóa chất Dầu khí (PVFCCo — DPM — Đạm Phú Mỹ)
**Phạm vi:** AI4BI **Giai đoạn 1** — 13 chỉ số · 05 chiều dữ liệu · 30 câu hỏi UAT
**Nguồn phạm vi:** `20260904_AI4BI_PVFCCo_Chisochieudulieu_V9.xlsx`
**Thời gian:** kế hoạch 2024-01 → 2026-12 · thực hiện 2024-01 → 2026-08 · "Hiện tại" = **tháng 8/2026**
**Charset:** utf8mb4_unicode_ci

> ⚠️ **Dữ liệu mô phỏng.** Số liệu được sinh theo nhịp mùa vụ và cơ cấu sản phẩm của ngành phân bón Việt Nam, **không phải** số thực tế của PVFCCo. Cấu trúc bảng và quy tắc tính thì ngược lại — được thiết kế để dùng lại khi triển khai thật.

> 📌 **Khác với `pvfcco_sql`.** Thư mục `pvfcco_sql` là bộ demo giai đoạn **pitching** (2024–2025, grain ngày, có nhà phân phối, giá khí, 3 anomaly cài sẵn). Bộ này là giai đoạn **chốt phạm vi hợp đồng**: bám đúng 13 chỉ số / 05 chiều đã thống nhất, grain tháng, **không cài anomaly**. Hai bộ phục vụ hai mục đích khác nhau, không thay thế nhau.

---

## 1. Nạp dữ liệu

```bash
# Cách 1 — dùng script chung của repo
./populate.sh pvfcco_phase1

# Cách 2 — thủ công
docker exec -i mock_database mysql -uroot -proot < pvfcco_phase1_sql/01_ddl_schema.sql
docker exec -i mock_database mysql -uroot -proot < pvfcco_phase1_sql/02_metadata.sql
docker exec -i mock_database mysql -uroot -proot < pvfcco_phase1_sql/03_master_data.sql
docker exec -i mock_database mysql -uroot -proot < pvfcco_phase1_sql/04_transaction_data.sql

# Kiểm tra
docker exec -i mock_database mysql -uroot -proot < pvfcco_phase1_sql/05_validation_queries.sql
```

## 2. Nội dung thư mục

| File | Mô tả |
|---|---|
| `01_ddl_schema.sql` | DROP+CREATE `pvfcco_phase1_demo`, 15 bảng, 6 view ngữ nghĩa |
| `02_metadata.sql` | INSERT `_meta_tables` (15) · `_meta_columns` (91) · `_meta_kpi` (13) · `_meta_glossary` (28) |
| `03_master_data.sql` | INSERT 6 bảng dimension |
| `04_transaction_data.sql` | INSERT 5 bảng fact (7.696 dòng) |
| `05_validation_queries.sql` | Kiểm tra kỹ thuật + mốc số liệu + dry-run 30 câu UAT kèm đáp án kỳ vọng |
| `database-schema.md` | Đặc tả schema đầy đủ — nguồn duy nhất khi cần đối chiếu cấu trúc |

## 3. Bảng và số dòng thực tế

```
DIM  (6):   dim_calendar(36) · dim_org_unit(7) · dim_product(8)
            dim_sales_region(6) · dim_cost_item(14) · dim_scenario(2)
FACT (5):   fact_sales(3.808) · fact_production(272) · fact_inventory(1.216)
            fact_gross_profit(160) · fact_opex(2.240)
META (4):   _meta_tables(15) · _meta_columns(91) · _meta_kpi(13) · _meta_glossary(28)
VIEW (6):   vw_sales · vw_production · vw_inventory · vw_gross_profit
            vw_opex · vw_executive_summary
```

Tổng dữ liệu giao dịch: **7.696 dòng** — nhỏ hơn hẳn các bộ demo khác trong repo, vì phạm vi Giai đoạn 1 dừng ở grain tháng và 13 chỉ số.

## 4. Năm đặc thù phải giữ đúng khi đọc dữ liệu

**4.1 — Hạt tháng, không có cấp ngày.** Toàn bộ database nối qua `dim_calendar.fiscal_period` dạng `'YYYY-MM'`. Không có bảng nào ở grain ngày. Câu hỏi về ngày nằm ngoài phạm vi.

**4.2 — Cấp Tổng công ty là tổng cộng lên, không phải một dòng.** `org_unit_id = 1` không có dòng fact nào. Lọc `org_unit_id = 1` để đại diện Tổng công ty sẽ ra rỗng; phải bỏ điều kiện lọc đơn vị và cộng toàn bộ.

**4.3 — `fact_inventory` là snapshot bán cộng.** Cộng được theo đơn vị và sản phẩm, **không** cộng theo thời gian. Tồn kho một quý = giá trị tại tháng cuối quý.

**4.4 — Ba chỉ số bị chặn chiều theo ma trận phạm vi.**

| Chỉ số | KHÔNG phân rã theo |
|---|---|
| Sản lượng sản xuất (và hai tỷ lệ của nó) | Đơn vị, Khu vực |
| Giá vốn hàng bán, Lợi nhuận gộp | Sản phẩm, Khu vực |
| Tồn kho thành phẩm | Khu vực (và không có số kế hoạch) |

Đây là giới hạn có chủ đích, không phải thiếu dữ liệu. Câu hỏi rơi vào ô bị chặn phải bị từ chối kèm giải thích, không được tự nối bảng khác rồi phân bổ.

**4.5 — Tỷ lệ tính sau khi tổng hợp.** `%HTKH = SUM(thực hiện) / SUM(kế hoạch)`, không bao giờ là `AVG` của tỷ lệ theo dòng. So cùng kỳ ở mức lũy kế phải khớp số tháng (8 tháng 2026 so với 8 **tháng** 2025).

## 5. Mốc sanity check (đã verify trên dữ liệu thật)

Lũy kế 8 tháng 2026, cấp Tổng công ty:

| Chỉ tiêu | Thực hiện | Kế hoạch | %HTKH |
|---|---|---|---|
| Sản lượng kinh doanh | 942.500 tấn | 966.666 tấn | 97,5% |
| Doanh thu bán hàng | 9.952,4 tỷ | 10.385,2 tỷ | **95,8%** ← thấp nhất |
| Sản lượng sản xuất | 730.136 tấn | 745.037 tấn | 98,0% |

So cùng kỳ: sản lượng kinh doanh **+1,7%**, sản lượng sản xuất **−2,7%** (giảm mạnh nhất).
Lợi nhuận gộp lũy kế 1.260,9 tỷ (+3,4% so cùng kỳ) · Chi phí bán hàng 689,8 tỷ · Chi phí quản lý 208,1 tỷ.
Tồn kho thành phẩm cuối tháng 8/2026: 68.064 tấn.
Đối soát: `SUM(doanh thu TH) − SUM(giá vốn) − SUM(lợi nhuận gộp) = 0,0000` tỷ.

## 6. Phân tán có chủ đích — thay cho anomaly

Bộ này **không cài anomaly**. Nhưng nếu mọi thành viên của một chiều đều ngang nhau thì câu hỏi xếp hạng sẽ có đáp án do nhiễu quyết định và buổi UAT sẽ tranh cãi. Vì vậy mỗi câu xếp hạng được thiết kế có **một đáp án duy nhất, cách biệt đủ rõ**:

| Câu | Đáp án | Khoảng cách với hạng kế tiếp |
|---|---|---|
| C13 — đơn vị %HTKH doanh thu thấp nhất | PVFCCo Tây Nam Bộ 89,7% | 3,1 điểm % |
| C14 — sản phẩm giảm SLKD mạnh nhất | SA Phú Mỹ −15,0% (−7.367 tấn) | dẫn đầu cả theo % lẫn tuyệt đối |
| C19 — sản phẩm %HTKH SLSX thấp nhất | UAN 88,5% | 7,9 điểm % |
| C26 — đơn vị lợi nhuận gộp thấp nhất | PVFCCo Miền Trung 182,0 tỷ | 23% |
| C30 — khoản mục tăng mạnh nhất T8 vs T7 | Chi phí vận chuyển, bốc xếp +18,9% (+6,10 tỷ) | 13,8 điểm % |

Phần D.4 của `05_validation_queries.sql` kiểm tra chính các khoảng cách này. Nếu đổi tham số sinh dữ liệu, chạy lại D.4 trước tiên.

Bối cảnh nghiệp vụ của C30: tháng 8 là cao điểm giao hàng vụ Thu Đông — chi phí vận chuyển tăng là hợp lý, không phải bất thường.

## 7. Lưu ý cho người kết nối AI engine

- Cho AI engine đọc **6 view** (`vw_*`) thay vì bảng gốc. View đã nối sẵn dimension nên câu SQL sinh ra hầu hết không cần `JOIN`, và cột nào không có trong view thì không thể `GROUP BY` — hàng rào phạm vi được khoá ở mức cột chứ không chỉ dặn trong system prompt.
- View xoay kịch bản TH/KH thành **cột** (`volume_act_ton` / `volume_plan_ton`), nên `%HTKH` là một phép chia trên cùng dòng, không phải self-join.
- `_meta_kpi` là hàng rào phạm vi ở dạng dữ liệu: đúng 13 dòng, mỗi dòng có `allowed_dims`. Chỉ số không có trong bảng này thì ngoài phạm vi; chiều không có trong `allowed_dims` thì không được phân rã theo.
- "Kỳ hiện tại" lấy từ `dim_calendar.is_current_period = 1`, **không** dùng `NOW()`/`CURDATE()` — dữ liệu dừng ở 2026-08.
- Cấp quyền `SELECT` **chỉ trên view** cho tài khoản mà AI engine dùng, không cấp trên bảng gốc.

## 8. Ghi chú phạm vi cần chốt với PVFCCo

Khi đối chiếu mô hình với file phạm vi V9, phát hiện file **tự mâu thuẫn ở hai câu hỏi**: cột "chiều dữ liệu liên quan" của **C2** và **C3** có liệt kê chiều *Đơn vị / phạm vi báo cáo*, nhưng ma trận chỉ số–chiều **không** cho hai chỉ số sản xuất (số 12 và 13) phân rã theo đơn vị.

Bộ dữ liệu này dựng **theo ma trận** — vì ma trận chi tiết đến từng ô, còn cột kia là mô tả tóm tắt ở mức câu hỏi. C2 và C3 được trả lời ở cấp Tổng công ty.

Ba phương án xử lý nằm trong tài liệu `01_PVFCCo_AI4BI_Schema_DuLieu.md` mục 11 (thư mục `AI4BI_Demo/PVFCCo`). Cần chốt trước khi ký hợp đồng: nếu chọn phương án đưa chiều Đơn vị vào chỉ số sản xuất thì phạm vi và khối lượng công việc thay đổi.

## 9. Sinh lại dữ liệu

Toàn bộ file SQL được sinh từ `pvfcco_phase1_scripts/`:

```bash
cd pvfcco_phase1_scripts
python3 gen_pvfcco.py     # sinh CSV + chạy 12 phép kiểm K1–K12
python3 answer_key.py     # tính đáp án kỳ vọng cho 30 câu UAT
python3 conformance.py    # đối chiếu mô hình với file Excel phạm vi (K13)
python3 build_pkg.py && python3 build_pkg2.py && python3 build_pkg3.py && python3 build_pkg4.py
python3 test_load.py      # nạp bộ SQL vào SQLite và đối chiếu 47 phép kiểm
```

Seed ngẫu nhiên cố định `20260907` — chạy lại cho ra số y hệt.

`test_load.py` nạp thật bộ SQL (sau khi gỡ cú pháp riêng của MySQL) rồi đối chiếu số dòng, toàn vẹn tham chiếu, hàng rào phạm vi, toàn bộ mốc số liệu, năm câu xếp hạng kèm độ cách biệt, và tính nhất quán giữa `_meta_columns` / `_meta_kpi` với schema thực tế. Chạy nó trước khi bàn giao — nó bắt được cả lỗi dữ liệu lẫn lỗi mô tả metadata lệch schema.

`conformance.py` đọc thẳng file Excel phạm vi và đối chiếu 65 ô ma trận, đơn vị đo, danh mục nhóm B, 6 báo cáo BI hiện hữu và 30 câu UAT. **Mỗi lần khách gửi bản phạm vi mới (V10, V11…), chạy script này trước tiên** — nó phát hiện được việc phạm vi đã đổi mà mô hình chưa đổi theo.
