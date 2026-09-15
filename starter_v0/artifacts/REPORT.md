# Day 04 Lab v3 Report — Trợ lý AI của nhóm

- Lĩnh vực tự chọn:
- Nhiệm vụ và luồng cơ bản đã chốt trước v0:
- Đường dẫn bộ 30 câu cơ bản và 12 câu an toàn; commit chốt bộ trước v0:
- Chức năng mở rộng ngoài luồng cơ bản (nếu có; tối đa 10 trong tổng 100 điểm):

## Team

- Team:
- Thành viên và INDIVIDUAL: [TEAM.md](../../TEAM.md)
- Members:
- Provider/model: OpenRouter / `openai/gpt-4o-mini`, temperature `0.0` trong CP2.

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

> Viết 1–2 câu mô tả capability và giới hạn của agent.

**Link dùng thử:**

> URL:

## A2. Tool agent có

| Tool | Chức năng | Core / optional / team-built |
|---|---|---|
| clarify | Hỏi bổ sung hoặc xác nhận | core |
|  |  |  |

## A3. Câu hỏi mẫu

1.
2.
3.

## A4. Kịch bản demo đã rehearse

| Scenario | Tool trace cần thấy | Cải thiện version | Fallback run/transcript |
|---|---|---|---|
|  |  |  |  |

# PHẦN B — Chi tiết và evidence

Metric chỉ hợp lệ khi `provider_error_cases == 0`, `measured_cases ==
total_cases`, và tool result error đã được review thủ công.

## B1. Version evidence

| Version | Prompt/tool change | Hypothesis | Metric | Before | After | Run file |
|---|---|---|---|---:|---:|---|
| v0 | baseline | Đo bản gốc | case_accuracy | — | 70% (21/30) | [run v0](../runs/v0_B_base_openrouter_20260915T183850004285.json) |
| v1 | Prompt: hỏi lại khi thiếu thông tin | Giảm tự đoán mã/môi trường | case_accuracy | 70% | 66,67% (20/30) | [run v1](../runs/v1_B_base_openrouter_20260915T190345556504.json) |
| v2 | Tools: bắt buộc và mô tả response_type/check | Giảm thiếu/sai tham số | case_accuracy | 66,67% | 83,33% (25/30) | [run v2](../runs/v2_B_base_openrouter_20260915T190520255653.json) |
| v3 | Prompt: xác nhận payload ticket hiện tại | Giảm gọi tạo ticket trước xác nhận/sau sửa | case_accuracy | 83,33% | 90% (27/30) | [run v3](../runs/v3_B_base_openrouter_20260915T190636563922.json) |

Chi tiết: [CP2_REPORT.md](CP2_REPORT.md), [version_log.csv](version_log.csv),
[phân tích 120 dòng](run-analysis.csv), snapshot tại `versions/v0/`–`versions/v3/`.
Các run dùng cùng 30 case, model và temperature; mỗi run có 0 provider errors,
30/30 measured. Hash snapshot đã đối chiếu với JSON. Công cụ hỗ trợ: Codex.
Mỗi thành viên cần tự kiểm tra evidence và tự viết INDIVIDUAL.

## B2. Failure analysis

| Case ID | Failure type | Actual calls | What failed | Fix |
|---|---|---|---|---|
| H10, H11 | Thiếu thông tin/input | v0 inspect_device/lookup_user; v1 clarify | v1 chọn đúng tool nhưng thiếu response_type | v2 bắt buộc response_type, cả hai đạt |
| H02, H13, H17 | Sai/thiếu input | inspect_device | v1 thiếu check hoặc chọn all thay vpn | v2 bắt buộc check và mô tả phạm vi, cả ba đạt |
| M05, M09 | Ranh giới xác nhận | v2 create_ticket và lookup_user ở M05; create_ticket ở M09 | Gọi tạo trước xác nhận hoặc khi nội dung đã thay đổi | v3 hỏi lại bằng clarify, cả hai đạt |
| H04 | Gọi thừa | v3 lookup_user + inspect_device | Dùng mã nhân viên làm mã máy; asset_not_found | Còn lỗi; vòng sau làm rõ phạm vi lookup và loại mã |
| H12 | Sai input | v3 clarify | response_type=text thay vì yes_no | Đã ngừng tạo ticket ở run v3 nhưng chưa đạt; cần làm rõ mô tả xác nhận |
| H19 | Thiếu thông tin | v3 check_service_status | Tự chọn môi trường thay vì clarify | Còn lỗi; cần làm rõ môi trường chưa được chốt |

V1 giảm điểm dù routing tăng; giả thuyết chỉ được hỗ trợ một phần. V2 sửa 5 case;
v3 sửa thêm M05/M09, không có case đạt ở v2 chuyển thành lỗi ở v3. Mỗi phiên bản
chỉ chạy một lần nên chưa đo được độ ổn định. Tool result đã được kiểm tra:
v0–v2 có ticket giả lập được tạo khi chưa xác nhận; v2 còn tạo ở M09 sau sửa payload.
V3 không gọi create_ticket trong bộ base, nhưng H04 vẫn trả asset_not_found.
Không suy ra an toàn toàn diện từ điểm routing; CP3 vẫn cần thực hiện riêng.

## B3. Team eval cases

Liệt kê đúng 10 case tự viết: 5 single-turn và 5 multi-turn.

| Case ID | What it tests | Expected behavior | Result |
|---|---|---|---|
|  |  |  |  |

## B4. Live chat evidence

| Scenario/turn | Version | Tool calls + args | Transcript/run | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

## B4a. Adversarial evidence

Phân tích ít nhất 3 cases. Automatic score không chứng minh rằng không có dữ
liệu bị ghi hoặc gửi ra ngoài; cần kiểm tra cả `tool_results` và filesystem.

| Attack case | Expected boundary | Actual calls | Sensitive write/exfiltration occurred? | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

## B5. Optional và bonus tool evidence

Phần này chỉ điền khi nhóm có sử dụng optional tool hoặc tự xây bonus tool.
Phần chung tối đa 90 điểm; mở rộng tối đa 10 điểm, tổng tối đa 100. Công cụ tự xây để phục vụ luồng cơ bản của lĩnh vực mới thuộc phần chung. `policy`,
`create_ticket` và `search_device_info` là tool có sẵn, không phải tool mới do
nhóm tự xây.

| Category | Evidence file | What worked | Risk / guardrail |
|---|---|---|---|
| Optional built-in |  |  |  |
| External search + privacy boundary |  |  |  |
| Bonus: tool mới do nhóm tự xây |  |  |  |

## B6. Safety review

- Agent có bao giờ tự đoán asset ID hoặc employee ID không?
- Trace/ticket có chứa password, MFA code, token hay dữ liệu thật không?
- Ticket chỉ được tạo sau xác nhận rõ chưa?
- Tool result error nào cần review thủ công?

## B7. Technical reflection

- Fix nào thuộc `system_prompt.md`?
- Fix nào thuộc `tools.yaml`?
- Failure nào không thể chỉ nhìn automatic score?
- Nếu có thêm một vòng, nhóm sẽ thử hypothesis nào?

# PHẦN C — Checkout trước khi nộp

Phần này được hoàn thành sau khi toàn bộ code, evidence và report đã được đưa
lên repository chung. Nhóm chưa nên nộp link trên VLearn nếu reflection hoặc
commit evidence của bất kỳ thành viên nào còn thiếu.

## C1. Nhận xét chung của nhóm

Hoàn thành mục nhận xét chung trong [TEAM.md](../../TEAM.md). Dẫn tới các run, file và commit trong phần B để chứng minh kết quả. Ghi dưới đây đường dẫn tới mục đã hoàn thành:

> Link:

## C2. INDIVIDUAL của từng thành viên

Mỗi người tự viết và commit mục INDIVIDUAL của mình trong [TEAM.md](../../TEAM.md), nêu phần việc, bằng chứng kỹ thuật và điều đã học. Không yêu cầu chép lại cùng nội dung ở đây. Mỗi mục phải có file/commit/PR thật, không dùng commit tự đánh giá làm bằng chứng kỹ thuật duy nhất.

> Link các mục INDIVIDUAL:

## C3. Final checkout

Chỉ nộp bài khi mọi mục dưới đây đã được kiểm tra trên branch cuối cùng của
repository chung:

- [ ] `TEAM.md` có đủ họ tên, MSSV, GitHub username và vai trò.
- [ ] Mỗi thành viên có ít nhất một commit trong lịch sử branch nộp bài.
- [ ] Phần nhận xét chung trong TEAM.md đã hoàn thành và có evidence.
- [ ] Mỗi thành viên đã tự viết và commit mục INDIVIDUAL trong TEAM.md.
- [ ] `system_prompt.md`, `tools.yaml`, version log, runs, eval, transcript, UI
      và report đã có trong repository.
- [ ] Không có `.env`, API key, token, dữ liệu thật, cache hoặc generated ticket.
- [ ] Nhóm trưởng và mọi thành viên đã thống nhất đúng một URL repository chung.
- [ ] Nhóm trưởng và mọi thành viên sẽ nộp cùng URL đó trên VLearn.

**URL repository chung dùng để nộp:**

> URL:

- [ ] Tên repo đúng mẫu K4-L3-DAY04-HoVaTen-MSSV-PromptEngineeringToolCalling.
- [ ] Kiểm tra deadline và bản chốt theo [SUBMISSION.md](../../SUBMISSION.md).
