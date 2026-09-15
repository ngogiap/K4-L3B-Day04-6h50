"""Rebuild CP2 evidence from live runs; verify snapshots and identical cases."""
from pathlib import Path
import csv
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"
CHANGES = [
    ("baseline", "Đo bản gốc trước khi sửa", "Baseline chưa tối ưu"),
    ("system_prompt.md", "Thiếu mã định danh hoặc môi trường chưa rõ", "Quy tắc hỏi lại giúp tránh tự đoán thông tin"),
    ("tools.yaml", "v1 bỏ response_type/check hoặc chọn sai check", "Bắt buộc và mô tả rõ tham số giúp giảm lỗi input"),
    ("system_prompt.md", "v2 còn gọi tạo ticket trước xác nhận và xử lý sai payload đã sửa", "Xác nhận riêng cho payload hiện tại giúp giảm lỗi ranh giới hành động"),
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    runs = []
    for version in ("v0", "v1", "v2", "v3"):
        paths = sorted((ROOT / "runs").glob(f"{version}_B_base_openrouter_*.json"))
        if len(paths) != 1:
            raise SystemExit(f"Expected exactly one run for {version}; found {len(paths)}. Select evidence explicitly before rebuilding.")
        path = paths[0]
        run = json.loads(path.read_text(encoding="utf-8"))
        summary = run["summary"]
        assert summary["provider_error_cases"] == 0
        assert summary["measured_cases"] == summary["total_cases"] == 30
        for filename, key in (("system_prompt.md", "prompt_hash"), ("tools.yaml", "tools_hash")):
            assert digest(ART / "versions" / version / filename) == run[key]
        runs.append((path.relative_to(ROOT).as_posix(), run))
    case_signature = lambda run: [(r["id"], r["input"], r["expect"]) for r in run["results"]]
    for _, run in runs:
        assert case_signature(run) == case_signature(runs[0][1])
        assert run["model"] == runs[0][1]["model"] == "openai/gpt-4o-mini"
        assert run["provider"] == "openrouter"
    for filename, key in (("system_prompt.md", "prompt_hash"), ("tools.yaml", "tools_hash")):
        assert digest(ART / filename) == runs[-1][1][key]

    fields = "version,author,changed_artifact,artifact_version,prompt_hash,tools_hash,reason,hypothesis,metric_name,metric_before,metric_after,run_file".split(",")
    with (ART / "version_log.csv").open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        for i, (path, run) in enumerate(runs):
            changed, reason, hypothesis = CHANGES[i]
            writer.writerow(dict(version=run["version"], author="Codex (AI hỗ trợ)", changed_artifact=changed,
                artifact_version=run["artifact_version"], prompt_hash=run["prompt_hash"], tools_hash=run["tools_hash"],
                reason=reason, hypothesis=hypothesis, metric_name="case_accuracy",
                metric_before=runs[i-1][1]["summary"]["case_accuracy"] if i else "",
                metric_after=run["summary"]["case_accuracy"], run_file=path))

    lines = ["# CP2 — Evidence v0–v3", "", "Công cụ hỗ trợ: Codex đọc trace, sửa artifact, chạy OpenRouter và tổng hợp kết quả thật. Thành viên tự kiểm tra kết quả và tự viết INDIVIDUAL.", "",
        "## Điều kiện", "", "- Provider: OpenRouter; model: `openai/gpt-4o-mini`; temperature: `0.0`.",
        "- Bộ case: `data/eval_base.json`, 30 case. Đã đối chiếu ID, input và expect giống nhau trong cả bốn run.",
        f"- SHA256 bộ case hiện tại: `{digest(ROOT / 'data/eval_base.json')}`.",
        "- Mỗi run: 30/30 measured, 0 provider errors. Không sửa evaluator hoặc bộ case.",
        "- Snapshot prompt/tool: `versions/v0/` đến `versions/v3/`; hash đã đối chiếu với run JSON. Artifact đang dùng khớp v3.", "",
        "## So sánh", "", "| Version | Đạt | Case accuracy | Routing | Arguments | Multi-turn | Run |", "|---|---:|---:|---:|---:|---:|---|"]
    for path, run in runs:
        s = run["summary"]
        lines.append(f"| {run['version']} | {s['passed_cases']}/30 | {s['case_accuracy']:.2%} | {s['tool_routing_accuracy']:.2%} | {s['argument_accuracy']:.2%} | {s['multiturn_accuracy']:.2%} | [{Path(path).name}](../{path}) |")
    lines += ["", "## Giả thuyết và thay đổi từng vòng", ""]
    for i in range(1, 4):
        _, run = runs[i]
        before = {r["id"]: r["result"]["passed"] for r in runs[i-1][1]["results"]}
        fixed = [r["id"] for r in run["results"] if r["result"]["passed"] and not before[r["id"]]]
        regressions = [r["id"] for r in run["results"] if not r["result"]["passed"] and before[r["id"]]]
        lines += [f"### v{i}", "", f"- File sửa: `{CHANGES[i][0]}`. Lý do: {CHANGES[i][1]}.", f"- Giả thuyết: {CHANGES[i][2]}.",
                  f"- Case chuyển FAIL → PASS: {', '.join(fixed) or 'không có'}.", f"- Case chuyển PASS → FAIL: {', '.join(regressions) or 'không có'}.", ""]
    lines += ["## Lỗi còn lại ở v3", "", "| Case | Failures |", "|---|---|"]
    for item in runs[-1][1]["results"]:
        if not item["result"]["passed"]:
            lines.append(f"| {item['id']} | {'; '.join(item['result']['failures'])} |")
    lines += ["", "## Kiểm tra tool result", "", "Các lỗi thực thi và lần tạo ticket dưới đây được lấy từ tool_results, tách khỏi điểm routing.", "", "| Version | Case | Tool | Error/status |", "|---|---|---|---|"]
    for _, run in runs:
        for item in run["results"]:
            for tool in item["tool_results"]:
                result = tool.get("result", {})
                issue = tool.get("error") or result.get("error") or (result.get("status") if tool["tool"] == "create_ticket" else None)
                if issue:
                    lines.append(f"| {run['version']} | {item['id']} | {tool['tool']} | {issue} |")
    lines += ["", "## Lệnh tái chạy", "", "Chạy trong starter_v0; thay N bằng 1, 2 hoặc 3 để dùng đúng snapshot:", "", "```powershell",
        "python run_eval.py --provider openrouter --model openai/gpt-4o-mini --version vN --suite base --eval-cases data/eval_base.json --system-prompt artifacts/versions/vN/system_prompt.md --tools artifacts/versions/vN/tools.yaml",
        "python scripts/parse_runs.py runs --output artifacts/run-analysis.csv", "```", "", "## Giới hạn", "",
        "- Chỉ một run mỗi phiên bản; kết quả có thể dao động dù temperature bằng 0. Không khẳng định quan hệ nhân quả từ một lần chạy.",
        "- Đây là bộ base dùng để cải tiến, chưa phải kiểm thử độc lập hay CP3 safety.",
        "- V0–v2 đã tạo ticket giả lập khi chưa có xác nhận ở H12; v2 còn tạo ở M09 sau sửa payload. V3 không gọi create_ticket trong bộ base. Prompt không thay thế kiểm soát xác nhận ở tầng thực thi.",
        "- Ticket phát sinh nằm trong thư mục tickets được Git ignore; không phải bằng chứng rằng thao tác ngoài hệ thống đã thành công.", ""]
    (ART / "CP2_REPORT.md").write_text("\n".join(lines), encoding="utf-8")
    print("Verified all run/snapshot hashes, identical cases, model, measured counts; wrote version_log.csv and CP2_REPORT.md.")


if __name__ == "__main__":
    main()
