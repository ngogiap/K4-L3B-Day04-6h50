# CP2 — Evidence v0–v3

Chuỗi chính thức cho so sánh này là bốn run tái kiểm tra ngày 16/09/2026, dùng snapshot `artifacts/versions/v0–v3/`. Hash SHA256 đầy đủ và đường dẫn run nằm trong [version_log.csv](version_log.csv). Đã đối chiếu hash prompt/tools, model, 30 ID/input/expect và số câu được đo. Các run cũ cùng nhãn version nhưng khác hash không thuộc chuỗi này.

## Điều kiện

- Provider: OpenRouter; model: `openai/gpt-4o-mini`.
- Mỗi run: 30/30 measured, 0 provider errors; suite `base`.
- SHA256 file eval_base.json hiện tại: `8d9b4180a2d3715fd1351efb4990af20e0b149d40e6155510f2605fecb2ec3ed`.
- Snapshot dùng đường dẫn `artifacts/versions/v0/` đến `artifacts/versions/v3/`; không suy ra artifact mặc định hiện tại trùng snapshot.

## So sánh

| Version | Thay đổi snapshot | Giả thuyết | Trước | Sau | Run |
|---|---|---|---:|---:|---|
| v0 | none | Mốc so sánh | — | 21/30 (0.7000) | [v0 run](../runs/recheck/v0_B_base_openrouter_20260916T023106740768.json) |
| v1 | system_prompt.md | Hỏi lại khi thiếu thông tin giúp tránh tự đoán | 0.7000 | 20/30 (0.6667) | [v1 run](../runs/recheck/v1_B_base_openrouter_20260916T023150888480.json) |
| v2 | tools.yaml | Bắt buộc và mô tả rõ tham số giúp giảm lỗi input | 0.6667 | 25/30 (0.8333) | [v2 run](../runs/recheck/v2_B_base_openrouter_20260916T023233883355.json) |
| v3 | system_prompt.md | Xác nhận riêng cho payload hiện tại giúp giảm lỗi ranh giới | 0.8333 | 27/30 (0.9000) | [v3 run](../runs/recheck/v3_B_base_openrouter_20260916T023317609988.json) |

## Giả thuyết và thay đổi từng vòng

### v1

- File sửa: `system_prompt.md`. Lý do: Thiếu mã định danh hoặc môi trường chưa rõ.
- Giả thuyết: Hỏi lại khi thiếu thông tin giúp tránh tự đoán.
- FAIL → PASS: không có.
- PASS → FAIL: H02_device_routing.

### v2

- File sửa: `tools.yaml`. Lý do: Thiếu hoặc sai response_type/check.
- Giả thuyết: Bắt buộc và mô tả rõ tham số giúp giảm lỗi input.
- FAIL → PASS: H02_device_routing, H10_missing_asset, H11_missing_employee, H13_parallel_status_and_device, H17_triage_with_three_sources.
- PASS → FAIL: không có.

### v3

- File sửa: `system_prompt.md`. Lý do: Tạo ticket trước xác nhận hoặc dùng xác nhận cũ.
- Giả thuyết: Xác nhận riêng cho payload hiện tại giúp giảm lỗi ranh giới.
- FAIL → PASS: M05_ticket_confirmation, M09_confirmation_invalidated.
- PASS → FAIL: không có.

## Lỗi còn lại ở v3

| Case v3 | Failure type | Lỗi quan sát |
|---|---|---|
| H04_user_routing | wrong_tool | extra tool call inspect_device |
| H12_confirm_before_ticket | wrong_boundary | response_type: expected 'yes_no', got 'text' |
| H19_ambiguous_environment | missing_info | missing tool call clarify; extra tool call check_service_status |

## Kiểm tra tool result

Các lỗi và trạng thái dưới đây được trích từ tool_results của đúng bốn run được chọn.

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
| v2 | M09_confirmation_invalidated | create_ticket | created |
| v3 | H04_user_routing | inspect_device | asset_not_found |

## Lệnh tái chạy

Chạy trong `starter_v0`, thay `$v` bằng version cần kiểm tra:

```powershell
$v = "v0"
python run_eval.py --provider openrouter --model openai/gpt-4o-mini --version $v --suite base --eval-cases data/eval_base.json --system-prompt "artifacts/versions/$v/system_prompt.md" --tools "artifacts/versions/$v/tools.yaml" --runs-dir runs/recheck
```

## Giới hạn

Chỉ chọn một run cho mỗi snapshot để so sánh; không khẳng định độ ổn định hoặc quan hệ nhân quả. Bộ base không thay thế kiểm thử CP3. Lỗi chọn tool/tham số và lỗi thực thi tool được tách riêng. Không suy ra an toàn tuyệt đối từ điểm tổng.
