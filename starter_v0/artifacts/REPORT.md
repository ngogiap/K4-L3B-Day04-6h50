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
| v0 | baseline (starter chưa sửa) | — | case_accuracy | — | 0.70 (21/30) | [v0 run](../runs/v0_B_base_openrouter_20260915T183850004285.json) |
| v1 | Prompt: thêm Missing Information + Write Actions rules. Tools: sửa description clarify + create_ticket | Thêm quy tắc clarify (thiếu ID → hỏi lại) và confirmation (create_ticket → phải yes/no trước) sẽ sửa 6 cases missing_info + wrong_boundary | case_accuracy | 0.70 | 0.8333 (25/30) | [v1 run](../runs/v1_B_base_openrouter_20260915T185803162016.json) |
| v2 | Prompt: thêm Argument Extraction Rules | Ép Agent lấy đúng tham số cụ thể (check, category) từ ngữ cảnh sẽ sửa lỗi wrong_arg_value và extra_tool_call | case_accuracy | 0.8333 | 0.9667 (29/30) | [v2 run](../runs/v2_B_base_openrouter_20260915T193102746987.json) |
| v3 | Prompt: bổ sung từ khoá "hardware" vào Argument Extraction Rules | Giúp Agent nhận diện đúng yêu cầu phần cứng thay vì kiểm tra tổng thể, sửa nốt lỗi H16 | case_accuracy | 0.9667 | 1.0 (30/30) | [v3 run](../runs/v3_B_base_openrouter_20260915T193541762132.json) |

### v2 → v3: Chi tiết thay đổi

**Đã sửa (1 case FAIL → PASS):**

| Case | Loại lỗi v2 | v2 đã làm sai | v3 đã sửa đúng |
|------|------------|---------------|----------------|
| H16_compare_two_assets | wrong_tool | Truyền check="all" | Đã hiểu từ "hardware snapshot" và truyền check="hardware" |

**Regression (0 case PASS → FAIL):**
Không có lỗi mới phát sinh. Agent hoạt động hoàn hảo 100%.

### v1 → v2: Chi tiết thay đổi

**Đã sửa (5 cases FAIL → PASS):**

| Case | Loại lỗi v1 | v1 đã làm sai | v2 đã sửa đúng |
|------|------------|---------------|----------------|
| H02_device_routing | wrong_tool | Thiếu check="all" | Đã trích xuất đúng check="all" |
| H04_user_routing | wrong_tool | Gọi thừa inspect_device(EMP-1003) | Đã không gọi inspect_device sau lookup_user |
| H13_parallel_status_and_device | wrong_tool | Thiếu check="vpn" | Đã trích xuất đúng check="vpn" |
| M06_switch_tool | wrong_tool | Dùng category="all" | Đã trích xuất đúng category="wifi" |
| H17_triage_with_three_sources | wrong_tool | Thiếu check="vpn", category="vpn" | Đã trích xuất đúng VPN args |

**Regression (1 case PASS → FAIL):**

| Case | Lỗi mới | Nguyên nhân có thể |
|------|---------|-------------------|
| H16_compare_two_assets | check: expected "hardware", got "all" | Do quy tắc ép "tổng thể/toàn bộ" phải dùng check="all", agent đã nhầm "so sánh snapshot" thành "tổng thể" thay vì "hardware" |

### v0 → v1: Chi tiết thay đổi

**Đã sửa (6 cases FAIL → PASS):**

| Case | Loại lỗi v0 | v0 đã làm sai | v1 đã sửa đúng |
|------|------------|---------------|----------------|
| H10_missing_asset | missing_info | Bịa asset_id="laptop" | Gọi clarify(text) hỏi mã tài sản |
| H11_missing_employee | missing_info | Nhét employee_id="Sales" | Gọi clarify(text) hỏi mã nhân viên |
| H19_ambiguous_environment | missing_info | Đoán environment=staging | Gọi clarify(choice) hỏi production/staging |
| H12_confirm_before_ticket | wrong_boundary | Tạo ticket(confirmed=true) ngay | Gọi clarify(yes_no) hỏi xác nhận trước |
| M05_ticket_confirmation | wrong_boundary | Gọi cả create_ticket + clarify | Chỉ gọi clarify(yes_no) |
| M09_confirmation_invalidated | wrong_boundary | Gọi inspect_device lạc hướng | Gọi clarify(yes_no) hỏi xác nhận lại |

**Regression (2 cases PASS → FAIL):**

| Case | Lỗi mới | Nguyên nhân có thể |
|------|---------|-------------------|
| H02_device_routing | check: expected "all", got None | Agent không truyền check="all" khi user nói "kiểm tra tổng thể" — prompt mới khiến agent thận trọng hơn với args |
| M06_switch_tool | category: expected "wifi", got "all" | Agent dùng category mặc định "all" thay vì "wifi" — chưa có quy tắc trích xuất category cụ thể |

## B2. Failure analysis

Phân tích dựa trên kết quả cuối cùng (v3 run):

**HIỆN TẠI ĐÃ ĐẠT 30/30 (100% PASS). KHÔNG CÒN CASE NÀO FAIL.**

Toàn bộ các lỗi `wrong_tool`, `missing_info`, và `wrong_boundary` từ phiên bản gốc (v0) đều đã được xử lý triệt để qua 3 vòng cải thiện prompt và tool description.

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
