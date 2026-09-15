# CP2 — Evidence v0–v3

Công cụ hỗ trợ: Codex đọc trace, sửa artifact, chạy OpenRouter và tổng hợp kết quả thật. Thành viên tự kiểm tra kết quả và tự viết INDIVIDUAL.

## Điều kiện

- Provider: OpenRouter; model: `openai/gpt-4o-mini`; temperature: `0.0`.
- Bộ case: `data/eval_base.json`, 30 case. Đã đối chiếu ID, input và expect giống nhau trong cả bốn run.
- SHA256 bộ case hiện tại: `8d9b4180a2d3715fd1351efb4990af20e0b149d40e6155510f2605fecb2ec3ed`.
- Mỗi run: 30/30 measured, 0 provider errors. Không sửa evaluator hoặc bộ case.
- Snapshot prompt/tool: `versions/v0/` đến `versions/v3/`; hash đã đối chiếu với run JSON. Artifact đang dùng khớp v3.

## So sánh

| Version | Đạt | Case accuracy | Routing | Arguments | Multi-turn | Run |
|---|---:|---:|---:|---:|---:|---|
| v0 | 21/30 | 70.00% | 76.67% | 70.00% | 80.00% | [v0_B_base_openrouter_20260915T183850004285.json](../runs/v0_B_base_openrouter_20260915T183850004285.json) |
| v1 | 20/30 | 66.67% | 83.33% | 66.67% | 80.00% | [v1_B_base_openrouter_20260915T190345556504.json](../runs/v1_B_base_openrouter_20260915T190345556504.json) |
| v2 | 25/30 | 83.33% | 83.33% | 83.33% | 80.00% | [v2_B_base_openrouter_20260915T190520255653.json](../runs/v2_B_base_openrouter_20260915T190520255653.json) |
| v3 | 27/30 | 90.00% | 93.33% | 90.00% | 100.00% | [v3_B_base_openrouter_20260915T190636563922.json](../runs/v3_B_base_openrouter_20260915T190636563922.json) |

## Giả thuyết và thay đổi từng vòng

### v1

- File sửa: `system_prompt.md`. Lý do: Thiếu mã định danh hoặc môi trường chưa rõ.
- Giả thuyết: Quy tắc hỏi lại giúp tránh tự đoán thông tin.
- Case chuyển FAIL → PASS: không có.
- Case chuyển PASS → FAIL: H02_device_routing.

### v2

- File sửa: `tools.yaml`. Lý do: v1 bỏ response_type/check hoặc chọn sai check.
- Giả thuyết: Bắt buộc và mô tả rõ tham số giúp giảm lỗi input.
- Case chuyển FAIL → PASS: H02_device_routing, H10_missing_asset, H11_missing_employee, H13_parallel_status_and_device, H17_triage_with_three_sources.
- Case chuyển PASS → FAIL: không có.

### v3

- File sửa: `system_prompt.md`. Lý do: v2 còn gọi tạo ticket trước xác nhận và xử lý sai payload đã sửa.
- Giả thuyết: Xác nhận riêng cho payload hiện tại giúp giảm lỗi ranh giới hành động.
- Case chuyển FAIL → PASS: M05_ticket_confirmation, M09_confirmation_invalidated.
- Case chuyển PASS → FAIL: không có.

## Lỗi còn lại ở v3

| Case | Failures |
|---|---|
| H04_user_routing | extra tool call inspect_device |
| H12_confirm_before_ticket | response_type: expected 'yes_no', got 'text' |
| H19_ambiguous_environment | missing tool call clarify; extra tool call check_service_status |

## Kiểm tra tool result

Các lỗi thực thi và lần tạo ticket dưới đây được lấy từ tool_results, tách khỏi điểm routing.

| Version | Case | Tool | Error/status |
|---|---|---|---|
| v0 | H04_user_routing | inspect_device | asset_not_found |
| v0 | H10_missing_asset | inspect_device | asset_not_found |
| v0 | H11_missing_employee | lookup_user | employee_not_found |
| v0 | H12_confirm_before_ticket | create_ticket | created |
| v0 | M05_ticket_confirmation | create_ticket | needs_confirmation |
| v1 | H04_user_routing | inspect_device | asset_not_found |
| v1 | H12_confirm_before_ticket | create_ticket | created |
| v1 | M05_ticket_confirmation | create_ticket | needs_confirmation |
| v1 | M05_ticket_confirmation | lookup_user | employee_not_found |
| v2 | H04_user_routing | inspect_device | asset_not_found |
| v2 | H12_confirm_before_ticket | create_ticket | created |
| v2 | M05_ticket_confirmation | create_ticket | needs_confirmation |
| v2 | M05_ticket_confirmation | lookup_user | employee_not_found |
| v2 | M09_confirmation_invalidated | create_ticket | created |
| v3 | H04_user_routing | inspect_device | asset_not_found |

## Lệnh tái chạy

Chạy trong starter_v0; thay N bằng 1, 2 hoặc 3 để dùng đúng snapshot:

```powershell
python run_eval.py --provider openrouter --model openai/gpt-4o-mini --version vN --suite base --eval-cases data/eval_base.json --system-prompt artifacts/versions/vN/system_prompt.md --tools artifacts/versions/vN/tools.yaml
python scripts/parse_runs.py runs --output artifacts/run-analysis.csv
```

## Giới hạn

- Chỉ một run mỗi phiên bản; kết quả có thể dao động dù temperature bằng 0. Không khẳng định quan hệ nhân quả từ một lần chạy.
- Đây là bộ base dùng để cải tiến, chưa phải kiểm thử độc lập hay CP3 safety.
- V0–v2 đã tạo ticket giả lập khi chưa có xác nhận ở H12; v2 còn tạo ở M09 sau sửa payload. V3 không gọi create_ticket trong bộ base. Prompt không thay thế kiểm soát xác nhận ở tầng thực thi.
- Ticket phát sinh nằm trong thư mục tickets được Git ignore; không phải bằng chứng rằng thao tác ngoài hệ thống đã thành công.
