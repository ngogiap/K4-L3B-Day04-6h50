# TEAM — Day04, K4-L3B

**Làm nhóm.** Mỗi người tự viết và commit phần INDIVIDUAL của mình.

## Thông tin bài nộp

- Tên nhóm: 6h50    
- Người đại diện / MSSV: Ngô Văn Giáp / 2A202602644
- Tên repo: `K4-L3B-DAY04-6h50`
- URL repo: https://github.com/ngogiap/K4-L3B-Day04-6h50
- Nhánh nộp: demo
- Commit chốt: demo
- Deadline áp dụng và link thông báo đổi hạn nếu có: không có

## Thành viên

| Họ và tên | MSSV | GitHub | Vai trò và công việc | File/commit/PR |
|---|---|---|---|---|
| Nguyễn Khánh Đô | 2A202602697 | Diohus | Thành viên và làm checkpoint 3 | CP3 |
| Bùi Lê Gia Huy | 2A202602607 | blgihuy | Thành viên và làm checkpoint 4 | CP4 |
| Mai Văn Trung | 2A202602513 | trungmv2004 | Thành viên và làm checkpoint 1 | CP1 |
| Ngô Văn Giáp | 2A202602644 | ngogiap | Nhóm trưởng và làm checkpoint 2 | CP2 |

## Nhận xét chung

- Kết quả và bằng chứng: Agent hỗ trợ IT Helpdesk. Bốn run tái kiểm tra ngày 16/09/2026 trong `starter_v0/runs/recheck/` khớp snapshot `starter_v0/artifacts/versions/v0–v3/`, cùng ID/input/expect, đạt lần lượt 21/30, 20/30, 25/30, 27/30; tất cả đo đủ 30 câu và có 0 lỗi provider. Có UI, bộ case nhóm và transcript trong `starter_v0/`.
- Thay đổi hiệu quả nhất: Theo chuỗi snapshot được mô tả trong [CP2_REPORT.md](starter_v0/artifacts/CP2_REPORT.md), vòng v2 làm rõ/ràng buộc tham số tool tăng từ 20/30 lên 25/30; v3 bổ sung quy tắc xác nhận đạt 27/30. Đây là kết quả quan sát, chưa chứng minh quan hệ nhân quả từ một lần chạy.
- Giới hạn còn lại: Run cũ đạt điểm cao hơn ở v1–v3 có hash khác snapshot hiện tại; cần đồng bộ báo cáo và version log theo cùng chuỗi cấu hình. Run an toàn tốt nhất đạt 11/12, còn lỗi A10 về xác nhận cũ; hai run này đã ở `starter_v0/runs/` (commit `9a6092f`), không còn kẹt ở backup. Snapshot thử nghiệm `v3_cp3` (16/09) đã chạy xong nhưng điểm thấp hơn v3 gốc (18/30, 7/12) và phát sinh regression mới ở A12 (mã nội bộ lọt vào đối số `search_device_info`); xem [CP3_REVIEW.md](starter_v0/artifacts/CP3_REVIEW.md) — chưa chốt dùng snapshot này để nộp. Cần hoàn tất merge (nhiều file mới/xóa chưa commit trong working tree), rà dữ liệu nhạy cảm trong transcript và cập nhật liên kết run đã xóa. Tên repo hiện tại cần đối chiếu quy tắc trong SUBMISSION.md trước khi nộp.
- Cách phân công và tích hợp: Trung phụ trách CP1/baseline; Giáp phụ trách CP2/cải tiến v1–v3 và điều phối; Đô phụ trách CP3/an toàn; Huy phụ trách CP4/UI và bộ case nhóm. Tích hợp qua Git, đối chiếu hash, case và trace trước khi cập nhật báo cáo chung; chốt commit sau khi giải quyết xung đột và kiểm tra bằng chứng.

## INDIVIDUAL

Các mục dưới đây là bản nháp tổng hợp từ phân công và bằng chứng repo. Mỗi thành viên tự rà soát, sửa phần trải nghiệm cá nhân và tự commit. Chưa xác nhận việc nộp VLearn.

### Nguyễn Khánh Đô — 2A202602697

- Phần việc và file/commit/PR: CP3, kiểm thử an toàn và hội thoại; commit `9a6092f`; `starter_v0/transcripts/`, run adversarial hiện trong bản sao lưu.
- Quyết định, khó khăn và cách xử lý (bản nháp): Cần phân tích lỗi A10 về xác nhận cũ và đối chiếu 3 phân tích an toàn với đúng case/trace.
- Điều đã học (cá nhân tự xác nhận): Xác nhận phải gắn với nội dung thao tác hiện tại; dữ liệu nội bộ không được đưa vào truy vấn web.
- AI/công cụ đã dùng và cách kiểm tra: Có bằng chứng eval và transcript qua provider trong repo; cá nhân bổ sung công cụ thực sự đã dùng và cách kiểm tra. Codex hỗ trợ rà bằng chứng và soạn bản nháp TEAM này.
- Thời điểm đã tự nộp URL repo chung trên VLearn: Chưa xác nhận; cá nhân điền thời điểm thực tế sau khi nộp và mở lại kiểm tra URL.

### Bùi Lê Gia Huy — 2A202602607

- Phần việc và file/commit/PR: CP4; commit `12e978c`, `191d3d9`; `starter_v0/ui.py`, `starter_v0/index.html`, `starter_v0/data/eval_group.json`.
- Quyết định, khó khăn và cách xử lý (bản nháp): Một số transcript gặp lỗi provider 429; cần dùng transcript chạy thành công làm bằng chứng hành vi UI và agent.
- Điều đã học (cá nhân tự xác nhận): UI cần hiển thị tool call và kết quả thực tế; lỗi provider không đồng nghĩa với sai logic agent.
- AI/công cụ đã dùng và cách kiểm tra: Repo có UI Python/HTML và transcript; cá nhân bổ sung công cụ thực sự đã dùng, cách chạy thử và kiểm tra. Codex hỗ trợ soạn bản nháp TEAM này.
- Thời điểm đã tự nộp URL repo chung trên VLearn: Chưa xác nhận; cá nhân điền thời điểm thực tế sau khi nộp và mở lại kiểm tra URL.

### Mai Văn Trung — 2A202602513

- Phần việc và file/commit/PR: CP1; commit `522925d`, `9256957`; `starter_v0/runs/v0_B_base_openrouter_20260915T183850004285.json`.
- Quyết định, khó khăn và cách xử lý (bản nháp): Baseline đạt 21/30 với 0 lỗi provider. Khi so sánh các lần chạy cần kiểm tra hash prompt/tools và cùng bộ case để tránh trộn cấu hình.
- Điều đã học (cá nhân tự xác nhận): Phân biệt sai chọn tool, sai tham số, lỗi thực thi tool và lỗi provider; điểm cao nhất không đại diện cho độ ổn định.
- AI/công cụ đã dùng và cách kiểm tra: Git, Python và run eval là bằng chứng trong repo; cá nhân xác nhận công cụ mình đã dùng. Codex hỗ trợ rà run, đối chiếu hash và soạn bản nháp TEAM này.
- Thời điểm đã tự nộp URL repo chung trên VLearn: Chưa xác nhận; cá nhân điền thời điểm thực tế sau khi nộp và mở lại kiểm tra URL.

### Ngô Văn Giáp — 2A202602644

- Phần việc và file/commit/PR: CP2 và điều phối nhóm; commit `63931cf`, `2bab847`, `83237c9`; prompt, tools và `starter_v0/artifacts/version_log.csv`.
- Quyết định, khó khăn và cách xử lý (bản nháp): Repo có các cấu hình cùng nhãn version nhưng khác hash; cần chọn một chuỗi bằng chứng nhất quán, ghi giả thuyết từng vòng và cập nhật đúng đường dẫn run.
- Điều đã học (cá nhân tự xác nhận): Mỗi vòng cải tiến cần giả thuyết, hash và trace đối chiếu; kết quả giảm cũng cần ghi nhận trung thực.
- AI/công cụ đã dùng và cách kiểm tra: Repo có Git, eval OpenRouter và snapshot; cá nhân bổ sung công cụ thực sự đã dùng và phạm vi hỗ trợ. Codex hỗ trợ rà bằng chứng và soạn bản nháp TEAM này.
- Thời điểm đã tự nộp URL repo chung trên VLearn: Chưa xác nhận; cá nhân điền thời điểm thực tế sau khi nộp và mở lại kiểm tra URL.
