#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from chat import (
    assistant_tool_message,
    execute_tool_call,
    json_text,
    now_iso,
    run_model_tool_loop,
    safe_slug,
    tool_results_message,
    trim_history,
    write_transcript,
)
from env_loader import load_lab_env
from providers import make_provider
from providers.base import ToolCall
from tools import TOOL_FUNCTIONS, load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"
DATA_DIR = ROOT / "data"
INDEX_HTML_PATH = ROOT / "index.html"
load_lab_env(ROOT)

# Global active sessions storage: {session_id: {"history": [...], "transcript": {...}, "path": Path}}
SESSIONS: dict[str, dict[str, Any]] = {}


def get_or_create_session(session_id: str, provider_name: str, version_label: str, system_prompt_path: Path, tools_path: Path, model: str | None) -> dict[str, Any]:
    if session_id in SESSIONS:
        return SESSIONS[session_id]

    TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    artifact_version = build_artifact_version(version_label, system_prompt_path, tools_path)
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join([
        safe_slug(version_label),
        safe_slug(provider_name),
        "web",
        timestamp,
    ])
    transcript_path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"

    transcript: dict[str, Any] = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact_version),
        "provider": provider_name,
        "model": model,
        "system_prompt": str(system_prompt_path),
        "tools": str(tools_path),
        "history_window": 5,
        "max_tool_rounds": 4,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }

    session = {
        "session_id": session_id,
        "transcript_id": transcript_id,
        "transcript_path": transcript_path,
        "transcript": transcript,
        "history": [],
        "turn_index": 0,
    }
    SESSIONS[session_id] = session
    return session


def extract_reply_text(text: str | None) -> str | None:
    """system_prompt.md instructs the model to answer as JSON
    ({"intent","action","reply","evidence_ids"}) so run_eval.py's routing
    checks have a consistent shape to inspect. That's fine for eval, but the
    web chat is for humans, so show the human-readable `reply` field instead
    of the raw JSON blob when the model followed that instruction. Returns
    None (caller keeps the original text) when it isn't that JSON shape, so
    plain-text replies are untouched.
    """
    if not text:
        return None
    stripped = text.strip()
    if not (stripped.startswith("{") and stripped.endswith("}")):
        return None
    try:
        parsed = json.loads(stripped)
    except (ValueError, TypeError):
        return None
    reply = parsed.get("reply") if isinstance(parsed, dict) else None
    return reply if isinstance(reply, str) and reply.strip() else None


def mock_deterministic_fallback(user_text: str, provider_error: str) -> dict[str, Any]:
    """Used only when the real provider call raises (rate limit, offline, etc).

    This must never assert a fact about tool state that the real tool result
    doesn't back up. Earlier versions hardcoded narratives (e.g. always saying
    a service was "normal") regardless of what the tool actually returned,
    which produced transcripts contradicting the real tool_results (see
    v0_openrouter_web_20260915T194527764448: assistant said VPN was normal
    while the real check_service_status result said degraded with an open
    incident). Every branch below is tagged `fallback: True` with the real
    provider_error, and any assistant text is either a direct echo of the
    real tool result or a plain "no model response" notice — never a scripted
    conclusion about what the tool result means.
    """
    text_lower = user_text.lower()
    disclaimer = f"[FALLBACK - loi provider, khong phai phan hoi that tu model: {provider_error}]\n"

    def _tool_turn(name: str, args: dict[str, Any], status: str = "answered") -> dict[str, Any]:
        call = {"name": name, "args": args}
        ev = execute_tool_call(ToolCall(name=name, args=args))
        result_summary = json.dumps(ev["result"], ensure_ascii=False, indent=2)
        return {
            "status": status,
            "fallback": True,
            "provider_error": provider_error,
            "assistant_text": disclaimer + f"Ket qua thuc te tu tool `{name}` (chua qua model dien giai):\n{result_summary}",
            "rounds": [{"round": 1, "tool_calls": [call], "tool_results": [ev]}],
            "tool_events": [ev],
        }

    if "vpn" in text_lower and ("production" in text_lower or "sự cố" in text_lower or "trạng thái" in text_lower):
        return _tool_turn("check_service_status", {"service": "vpn", "environment": "production"})

    if "lt-204" in text_lower or "lt-240" in text_lower or "lt-501" in text_lower or "lt-105" in text_lower:
        matched_id = "LT-204"
        for candidate in ["LT-204", "LT-240", "LT-501", "LT-105"]:
            if candidate.lower() in text_lower:
                matched_id = candidate
                break
        check_val = "vpn" if "vpn" in text_lower else ("hardware" if "phần cứng" in text_lower or "màn hình" in text_lower else ("software" if "phần mềm" in text_lower else "all"))
        return _tool_turn("inspect_device", {"asset_id": matched_id, "check": check_val})

    if "tạo ticket" in text_lower or "lập ticket" in text_lower:
        result = _tool_turn(
            "clarify",
            {"question": "Bạn có chắc chắn muốn xác nhận tạo ticket sự cố này không?", "response_type": "yes_no"},
            status="waiting_for_user",
        )
        result["assistant_text"] = disclaimer + "Truoc khi tao ticket, can xac nhan tu ban (cau hoi mau, chua qua model)."
        return result

    if "chớp giật" in text_lower or ("máy của mình" in text_lower and not any(k in text_lower for k in ["lt-", "pr-"])):
        result = _tool_turn(
            "clarify",
            {"question": "Vui lòng cung cấp mã tài sản (Asset ID) dán ở đáy laptop của bạn để kiểm tra.", "response_type": "text"},
            status="waiting_for_user",
        )
        result["assistant_text"] = disclaimer + "Can Asset ID de kiem tra phan cung (cau hoi mau, chua qua model)."
        return result

    if "quy định" in text_lower or "chính sách" in text_lower or "ai bên ngoài" in text_lower:
        return _tool_turn("policy", {"policy_area": "external_tools", "query": "Quy định công cụ AI bên ngoài"})

    if "dell" in text_lower or "latitude" in text_lower or "thông số" in text_lower:
        return _tool_turn("search_device_info", {"manufacturer": "Dell", "model": "Latitude 5440", "query_type": "specs"})

    # No matching tool keyword: report the real provider error, do not fabricate an answer.
    return {
        "status": "provider_error",
        "fallback": True,
        "provider_error": provider_error,
        "assistant_text": disclaimer + "Khong co ket qua tool de doi chieu cho yeu cau nay. Vui long thu lai sau khi provider phuc hoi.",
        "rounds": [],
        "tool_events": [],
    }


class HelpdeskUIHandler(BaseHTTPRequestHandler):
    provider_name: str = "openrouter"
    version_label: str = "v0"
    model: str | None = None
    system_prompt_path: Path = ARTIFACTS_DIR / "system_prompt.md"
    tools_path: Path = ARTIFACTS_DIR / "tools.yaml"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        if path in {"/", "/index.html"}:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            if INDEX_HTML_PATH.exists():
                html = INDEX_HTML_PATH.read_text(encoding="utf-8")
            else:
                html = "<h1>index.html not found</h1>"
            self.wfile.write(html.encode("utf-8"))
            return

        if path == "/api/info":
            artifact_version = build_artifact_version(self.version_label, self.system_prompt_path, self.tools_path)
            data = {
                "version": self.version_label,
                "provider": self.provider_name,
                "model": self.model or "default",
                **artifact_version_dict(artifact_version),
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode("utf-8"))
            return

        if path == "/api/transcript":
            query = parse_qs(parsed.query)
            t_id = query.get("id", [""])[0]
            target_path = TRANSCRIPTS_DIR / f"{safe_slug(t_id)}.transcript.json"
            if target_path.exists():
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(target_path.read_bytes())
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'{"error": "not_found"}')
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self) -> None:
        if self.path == "/api/chat":
            content_length = int(self.headers.get("Content-Length", 0))
            raw_data = self.rfile.read(content_length)
            try:
                payload = json.loads(raw_data.decode("utf-8"))
            except Exception as e:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
                return

            user_text = payload.get("message", "").strip()
            session_id = payload.get("session_id", "default_session")

            session = get_or_create_session(
                session_id,
                self.provider_name,
                self.version_label,
                self.system_prompt_path,
                self.tools_path,
                self.model,
            )

            system_prompt = self.system_prompt_path.read_text(encoding="utf-8")
            tool_declarations = load_tool_declarations(self.tools_path)
            openai_tools = to_openai_tools(tool_declarations)

            session["turn_index"] += 1
            turn_index = session["turn_index"]

            messages = [
                {"role": "system", "content": system_prompt},
                *trim_history(session["history"], 5),
                {"role": "user", "content": user_text},
            ]

            turn_record: dict[str, Any] = {
                "turn_index": turn_index,
                "started_at": now_iso(),
                "user": user_text,
                "status": "started",
                "assistant_text": None,
                "rounds": [],
                "tool_events": [],
                "fallback": False,
                "provider_error": None,
            }

            try:
                provider = make_provider(self.provider_name)
                result = run_model_tool_loop(
                    provider=provider,
                    messages=messages,
                    tools=openai_tools,
                    model=self.model,
                    max_tool_rounds=4,
                )
                turn_record.update(result)
                assistant_text = extract_reply_text(result["assistant_text"]) or result["assistant_text"]
                turn_record["assistant_text"] = assistant_text
                session["history"].append({"role": "user", "content": user_text})
                session["history"].append({"role": "assistant", "content": assistant_text})
            except Exception as exc:
                # Provider call failed (rate limit, offline, ...). Fall back to a
                # clearly-tagged local response instead of a real model reply.
                fallback_res = mock_deterministic_fallback(user_text, str(exc))
                turn_record.update(fallback_res)
                assistant_text = fallback_res["assistant_text"]
                session["history"].append({"role": "user", "content": user_text})
                session["history"].append({"role": "assistant", "content": assistant_text})

            turn_record["ended_at"] = now_iso()
            session["transcript"]["turns"].append(turn_record)
            write_transcript(session["transcript_path"], session["transcript"])

            response_data = {
                "session_id": session_id,
                "transcript_id": session["transcript_id"],
                "assistant_text": assistant_text,
                "rounds": turn_record.get("rounds", []),
                "tool_events": turn_record.get("tool_events", []),
                "status": turn_record.get("status"),
                "fallback": turn_record.get("fallback", False),
                "provider_error": turn_record.get("provider_error"),
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()


def main() -> None:
    parser = argparse.ArgumentParser(description="Web UI for IT Helpdesk Agent with real-time tool inspection.")
    parser.add_argument("--port", type=int, default=8000, help="HTTP port (default 8000)")
    parser.add_argument("--provider", choices=["openrouter", "openai", "anthropic", "gemini"], default="openrouter")
    parser.add_argument("--version", default="v0", help="Artifact version label")
    parser.add_argument("--model", default=None)
    parser.add_argument("--system-prompt", type=Path, default=ARTIFACTS_DIR / "system_prompt.md")
    parser.add_argument("--tools", type=Path, default=ARTIFACTS_DIR / "tools.yaml")
    args = parser.parse_args()

    HelpdeskUIHandler.provider_name = args.provider
    HelpdeskUIHandler.version_label = args.version
    HelpdeskUIHandler.model = args.model
    HelpdeskUIHandler.system_prompt_path = args.system_prompt
    HelpdeskUIHandler.tools_path = args.tools

    # Threaded so a slow/hung provider call on one request (a real risk with
    # the free model, see complete()'s timeout) doesn't block every other
    # request (page load, transcript fetch, another chat turn).
    server = ThreadingHTTPServer(("0.0.0.0", args.port), HelpdeskUIHandler)
    print(f"==================================================")
    print(f"  Northstar IT Helpdesk Web UI running!")
    print(f"  URL: http://localhost:{args.port}")
    print(f"  Provider: {args.provider} | Version: {args.version}")
    print(f"  Transcripts will be saved to: {TRANSCRIPTS_DIR}")
    print(f"==================================================")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        server.server_close()


if __name__ == "__main__":
    main()
