#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_EXPORT_DIR = "copilot-session"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="导出 GitHub Copilot Chat 会话为本地 Markdown 或 JSON 文件。")
    parser.add_argument("--list-sessions", action="store_true", help="列出当前可发现的全部 session。")
    parser.add_argument("--list-json", action="store_true", help="配合 --list-sessions 使用，以 JSON 输出 session 列表。")
    parser.add_argument("--transcript", type=Path, help="直接指定 transcript 的 .jsonl 文件路径。")
    parser.add_argument("--session-log-path", type=Path, help="指定当前会话的 debug log 路径或 transcript 路径，脚本会自动推导 session ID。")
    parser.add_argument("--session-id", help="指定要导出的单个 session ID。")
    parser.add_argument("--session-ids", nargs="+", help="批量导出的 session ID 列表。")
    parser.add_argument(
        "--workspace-storage-root",
        type=Path,
        help="指定 VS Code workspaceStorage 根目录，例如 ~/Library/Application Support/Code/User/workspaceStorage。",
    )
    parser.add_argument("--transcripts-dir", type=Path, help="直接指定 transcripts 目录。")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="导出格式。默认 markdown。")
    parser.add_argument("--output", type=Path, help="输出文件路径。未指定时会写入当前目录下的 copilot-session/。")
    parser.add_argument("--output-dir", type=Path, help="导出目录。未指定时使用当前目录下的 copilot-session/。")
    parser.add_argument(
        "--roles",
        nargs="+",
        choices=["user", "assistant"],
        default=["user", "assistant"],
        help="按角色过滤消息。默认同时导出 user 和 assistant。",
    )
    parser.add_argument("--include-tools", action="store_true", help="保留工具调用摘要。")
    parser.add_argument("--include-reasoning", action="store_true", help="保留 assistant.message 中的 reasoningText。")
    parser.add_argument("--title-length", type=int, default=48, help="session 标题的最大显示长度。")
    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> None:
    if args.list_json and not args.list_sessions:
        raise ValueError("--list-json 只能和 --list-sessions 一起使用。")
    if args.list_sessions and any([args.transcript, args.session_log_path, args.session_id, args.session_ids]):
        raise ValueError("--list-sessions 不能和具体会话参数同时使用。")
    if args.session_id and args.session_ids:
        raise ValueError("--session-id 和 --session-ids 不能同时使用。")
    if args.output and args.session_ids:
        raise ValueError("批量导出时不能使用 --output，请改用 --output-dir。")
    if args.output and args.list_sessions:
        raise ValueError("--list-sessions 模式下不能使用 --output。")


def unique_paths(paths: list[Path]) -> list[Path]:
    seen: set[str] = set()
    result: list[Path] = []
    for path in paths:
        expanded = path.expanduser()
        key = str(expanded)
        if key in seen:
            continue
        seen.add(key)
        result.append(expanded)
    return result


def candidate_workspace_storage_roots() -> list[Path]:
    home = Path.home()
    candidates = [
        home / "Library" / "Application Support" / "Code" / "User" / "workspaceStorage",
        home / "Library" / "Application Support" / "Code - Insiders" / "User" / "workspaceStorage",
        home / ".config" / "Code" / "User" / "workspaceStorage",
        home / ".config" / "Code - Insiders" / "User" / "workspaceStorage",
    ]
    appdata = os.environ.get("APPDATA")
    if appdata:
        candidates.extend(
            [
                Path(appdata) / "Code" / "User" / "workspaceStorage",
                Path(appdata) / "Code - Insiders" / "User" / "workspaceStorage",
            ]
        )
    return [path for path in unique_paths(candidates) if path.exists()]


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def truncate_text(value: str, max_length: int) -> str:
    if max_length <= 0:
        return ""
    if len(value) <= max_length:
        return value
    if max_length <= 3:
        return value[:max_length]
    return value[: max_length - 3].rstrip() + "..."


def safe_filename_title(value: str, max_length: int = 48) -> str:
    normalized = normalize_text(value)
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]', " ", normalized)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" .")
    cleaned = truncate_text(cleaned, max_length).strip(" .")
    return cleaned


def parse_iso_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def display_timestamp(value: str | None) -> str:
    dt = parse_iso_datetime(value)
    if not dt:
        return "unknown"
    return dt.astimezone().strftime("%Y-%m-%d %H:%M:%S")


def filename_timestamp(value: str | None) -> str:
    dt = parse_iso_datetime(value)
    if not dt:
        return "unknown-time"
    return dt.astimezone().strftime("%Y-%m-%d_%H-%M-%S")


def discover_transcript_files(args: argparse.Namespace) -> list[Path]:
    directories: list[Path] = []
    if args.transcripts_dir:
        directories.append(args.transcripts_dir.expanduser())
    else:
        roots = [args.workspace_storage_root.expanduser()] if args.workspace_storage_root else candidate_workspace_storage_roots()
        for root in roots:
            directories.extend(path for path in root.glob("*/GitHub.copilot-chat/transcripts") if path.is_dir())

    transcripts: list[Path] = []
    for directory in unique_paths(directories):
        transcripts.extend(path for path in directory.glob("*.jsonl") if path.is_file())
    return sorted(transcripts, key=lambda path: path.stat().st_mtime, reverse=True)


def discover_required_transcript_files(args: argparse.Namespace) -> list[Path]:
    transcripts = discover_transcript_files(args)
    if transcripts:
        return transcripts
    raise FileNotFoundError("没有找到任何 transcript 文件。请显式传入 --transcript、--session-log-path、--session-id 或 --workspace-storage-root。")


def resolve_transcript(args: argparse.Namespace) -> Path:
    if args.transcript:
        transcript_path = args.transcript.expanduser()
        if not transcript_path.is_file():
            raise FileNotFoundError(f"transcript 不存在: {transcript_path}")
        return transcript_path

    if args.session_log_path:
        return resolve_from_session_log_path(args.session_log_path, args)

    transcripts = discover_required_transcript_files(args)
    if args.session_id:
        for transcript_path in transcripts:
            if transcript_path.stem == args.session_id:
                return transcript_path
        raise FileNotFoundError(f"没有找到 session ID 为 {args.session_id} 的 transcript。")

    return transcripts[0]


def derive_session_id_from_path(path: Path) -> str | None:
    if path.suffix == ".jsonl" and path.parent.name == "transcripts":
        return path.stem
    if path.is_dir() and path.parent.name == "debug-logs":
        return path.name
    if path.parent.parent.name == "debug-logs":
        return path.parent.name
    if path.suffix == ".jsonl":
        return path.stem
    if path.name:
        return path.name
    return None


def resolve_from_session_log_path(session_log_path: Path, args: argparse.Namespace) -> Path:
    source_path = session_log_path.expanduser()
    if source_path.is_file() and source_path.parent.name == "transcripts":
        return source_path

    session_id = derive_session_id_from_path(source_path)
    if not session_id:
        raise FileNotFoundError(f"无法从路径推导 session ID: {source_path}")

    for candidate in [source_path, *source_path.parents]:
        if candidate.name != "GitHub.copilot-chat":
            continue
        transcript_path = candidate / "transcripts" / f"{session_id}.jsonl"
        if transcript_path.is_file():
            return transcript_path

    transcripts = discover_required_transcript_files(args)
    for transcript_path in transcripts:
        if transcript_path.stem == session_id:
            return transcript_path

    raise FileNotFoundError(f"没有找到与 session log 对应的 transcript: {source_path}")


def read_jsonl(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    events: list[dict[str, Any]] = []
    warnings: list[str] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                warnings.append(f"第 {line_number} 行 JSON 解析失败：{exc.msg}")
                continue
            if isinstance(payload, dict):
                events.append(payload)
            else:
                warnings.append(f"第 {line_number} 行不是 JSON 对象，已跳过。")
    return events, warnings


def derive_session_title(events: list[dict[str, Any]], title_length: int) -> tuple[str, str]:
    for event_type, source in [("user.message", "user"), ("assistant.message", "assistant")]:
        for event in events:
            if event.get("type") != event_type:
                continue
            data = event.get("data") or {}
            content = normalize_text(data.get("content") or "")
            if content:
                return truncate_text(content, title_length), source
    return "Untitled session", "fallback"


def count_messages(events: list[dict[str, Any]]) -> tuple[int, int]:
    user_count = 0
    assistant_count = 0
    for event in events:
        event_type = event.get("type")
        if event_type == "user.message":
            user_count += 1
        elif event_type == "assistant.message":
            assistant_count += 1
    return user_count, assistant_count


def build_session_summary(transcript_path: Path, title_length: int) -> dict[str, Any]:
    events, warnings = read_jsonl(transcript_path)
    session_start = next((event for event in events if event.get("type") == "session.start"), None)
    session_data = (session_start or {}).get("data") or {}
    title, title_source = derive_session_title(events, title_length)
    user_count, assistant_count = count_messages(events)
    start_time = session_data.get("startTime")
    if not start_time:
        start_time = datetime.fromtimestamp(transcript_path.stat().st_mtime, tz=timezone.utc).isoformat()

    return {
        "session_id": session_data.get("sessionId") or transcript_path.stem,
        "title": title,
        "title_source": title_source,
        "session_start_time": start_time,
        "display_time": display_timestamp(start_time),
        "message_count": user_count + assistant_count,
        "user_message_count": user_count,
        "assistant_message_count": assistant_count,
        "warning_count": len(warnings),
        "source_transcript": str(transcript_path),
    }


def collect_session_summaries(args: argparse.Namespace) -> list[dict[str, Any]]:
    transcripts = discover_required_transcript_files(args)
    return [build_session_summary(path, args.title_length) for path in transcripts]


def normalize_tool_arguments(arguments: Any) -> Any:
    if isinstance(arguments, str):
        stripped = arguments.strip()
        if stripped.startswith("{") or stripped.startswith("["):
            try:
                return json.loads(stripped)
            except json.JSONDecodeError:
                return arguments
    return arguments


def collect_tool_calls(events: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    tool_calls: dict[str, dict[str, Any]] = {}
    for event in events:
        event_type = event.get("type")
        data = event.get("data") or {}
        if event_type == "tool.execution_start":
            tool_call_id = data.get("toolCallId")
            if not tool_call_id:
                continue
            entry = tool_calls.setdefault(
                tool_call_id,
                {"tool_call_id": tool_call_id, "name": None, "arguments": None, "success": None},
            )
            entry["name"] = data.get("toolName") or entry["name"]
            if "arguments" in data:
                entry["arguments"] = normalize_tool_arguments(data.get("arguments"))
        elif event_type == "tool.execution_complete":
            tool_call_id = data.get("toolCallId")
            if not tool_call_id:
                continue
            entry = tool_calls.setdefault(
                tool_call_id,
                {"tool_call_id": tool_call_id, "name": None, "arguments": None, "success": None},
            )
            if "success" in data:
                entry["success"] = data.get("success")
    return tool_calls


def build_metadata(events: list[dict[str, Any]], transcript_path: Path, warnings: list[str], args: argparse.Namespace) -> dict[str, Any]:
    session_start = next((event for event in events if event.get("type") == "session.start"), None)
    session_data = (session_start or {}).get("data") or {}
    session_title, title_source = derive_session_title(events, args.title_length)
    return {
        "session_id": session_data.get("sessionId") or transcript_path.stem,
        "session_title": session_title,
        "title_source": title_source,
        "copilot_version": session_data.get("copilotVersion"),
        "vscode_version": session_data.get("vscodeVersion"),
        "session_start_time": session_data.get("startTime"),
        "source_transcript": str(transcript_path),
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "output_format": args.format,
        "roles": args.roles,
        "include_tools": args.include_tools,
        "include_reasoning": args.include_reasoning,
        "warning_count": len(warnings),
        "raw_event_count": len(events),
    }


def serialize_tool_request(request: dict[str, Any], tool_calls: dict[str, dict[str, Any]]) -> dict[str, Any]:
    tool_call_id = request.get("toolCallId")
    merged = tool_calls.get(tool_call_id or "", {})
    arguments = request.get("arguments")
    if arguments is None:
        arguments = merged.get("arguments")
    return {
        "tool_call_id": tool_call_id,
        "name": request.get("name") or merged.get("name"),
        "arguments": normalize_tool_arguments(arguments),
        "success": merged.get("success"),
    }


def build_messages(events: list[dict[str, Any]], tool_calls: dict[str, dict[str, Any]], args: argparse.Namespace) -> list[dict[str, Any]]:
    allowed_roles = set(args.roles)
    messages: list[dict[str, Any]] = []

    for event in events:
        event_type = event.get("type")
        data = event.get("data") or {}
        timestamp = event.get("timestamp")
        event_id = event.get("id")
        parent_id = event.get("parentId")

        if event_type == "user.message" and "user" in allowed_roles:
            content = data.get("content") or ""
            messages.append(
                {
                    "role": "user",
                    "content": content,
                    "timestamp": timestamp,
                    "event_id": event_id,
                    "parent_id": parent_id,
                    "attachments": data.get("attachments") or [],
                }
            )
            continue

        if event_type == "assistant.message" and "assistant" in allowed_roles:
            content = data.get("content") or ""
            tool_requests = []
            if args.include_tools:
                tool_requests = [serialize_tool_request(request, tool_calls) for request in data.get("toolRequests") or []]

            reasoning_text = data.get("reasoningText") if args.include_reasoning else None
            if not content and not tool_requests and not reasoning_text:
                continue

            message = {
                "role": "assistant",
                "content": content,
                "timestamp": timestamp,
                "event_id": event_id,
                "parent_id": parent_id,
                "message_id": data.get("messageId"),
            }
            if args.include_tools:
                message["tool_requests"] = tool_requests
            if reasoning_text:
                message["reasoning_text"] = reasoning_text
            messages.append(message)

    return messages


def choose_output_dir(args: argparse.Namespace) -> Path:
    if args.output_dir:
        return args.output_dir.expanduser()
    return Path.cwd() / DEFAULT_EXPORT_DIR


def build_default_filename(metadata: dict[str, Any]) -> str:
    extension = "md" if metadata["output_format"] == "markdown" else "json"
    timestamp = filename_timestamp(metadata.get("session_start_time"))
    title = safe_filename_title(metadata.get("session_title") or "")
    if not title:
        title = "session"
    return f"{title}-{timestamp}.{extension}"


def choose_output_path(args: argparse.Namespace, metadata: dict[str, Any]) -> Path:
    if args.output:
        return args.output.expanduser()
    return choose_output_dir(args) / build_default_filename(metadata)


def render_markdown(metadata: dict[str, Any], messages: list[dict[str, Any]], warnings: list[str]) -> str:
    lines: list[str] = [
        "# Copilot Chat 会话导出",
        "",
        f"- 会话 ID：{metadata['session_id']}",
        f"- 标题：{metadata['session_title']}",
        f"- 源 transcript：{metadata['source_transcript']}",
        f"- 导出时间：{metadata['exported_at']}",
        f"- 消息数：{len(messages)}",
        f"- 角色：{', '.join(metadata['roles'])}",
        f"- 包含工具调用：{'是' if metadata['include_tools'] else '否'}",
        f"- 包含内部推理：{'是' if metadata['include_reasoning'] else '否'}",
        "",
    ]

    for index, message in enumerate(messages, start=1):
        role_title = "用户" if message["role"] == "user" else "助手"
        lines.extend(
            [
                f"## {index}. {role_title}",
                "",
                f"- 时间：{message.get('timestamp') or '未知'}",
            ]
        )
        if message.get("message_id"):
            lines.append(f"- messageId：{message['message_id']}")
        lines.extend(["", "### 内容", ""])
        content = (message.get("content") or "").rstrip()
        lines.append(content if content else "[空内容]")
        lines.append("")

        attachments = message.get("attachments") or []
        if attachments:
            lines.extend(["### 附件", "", "```json", json.dumps(attachments, ensure_ascii=False, indent=2), "```", ""])

        tool_requests = message.get("tool_requests") or []
        if tool_requests:
            lines.extend(["### 工具调用", ""])
            for tool_request in tool_requests:
                tool_name = tool_request.get("name") or "unknown"
                success = tool_request.get("success")
                success_text = "unknown" if success is None else str(success).lower()
                lines.extend(
                    [
                        f"#### {tool_name}",
                        "",
                        f"- toolCallId：{tool_request.get('tool_call_id') or 'unknown'}",
                        f"- success：{success_text}",
                    ]
                )
                if tool_request.get("arguments") is not None:
                    lines.extend(
                        [
                            "- arguments：",
                            "```json",
                            json.dumps(tool_request["arguments"], ensure_ascii=False, indent=2),
                            "```",
                        ]
                    )
                lines.append("")

        reasoning_text = message.get("reasoning_text")
        if reasoning_text:
            lines.extend(["### 内部推理", "", reasoning_text.rstrip(), ""])

    if warnings:
        lines.extend(["## Warnings", ""])
        for item in warnings:
            lines.append(f"- {item}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_json_payload(metadata: dict[str, Any], messages: list[dict[str, Any]], warnings: list[str]) -> str:
    payload = {"metadata": metadata, "messages": messages, "warnings": warnings}
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def write_output(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_export_result(args: argparse.Namespace, transcript_path: Path, explicit_output_path: Path | None = None) -> dict[str, Any]:
    events, warnings = read_jsonl(transcript_path)
    tool_calls = collect_tool_calls(events)
    metadata = build_metadata(events, transcript_path, warnings, args)
    messages = build_messages(events, tool_calls, args)
    metadata["message_count"] = len(messages)
    output_path = explicit_output_path or choose_output_path(args, metadata)

    if args.format == "markdown":
        content = render_markdown(metadata, messages, warnings)
    else:
        content = render_json_payload(metadata, messages, warnings)

    write_output(output_path, content)
    return {
        "output_path": str(output_path),
        "source_transcript": str(transcript_path),
        "session_id": metadata["session_id"],
        "session_title": metadata["session_title"],
        "message_count": metadata["message_count"],
        "warning_count": len(warnings),
        "metadata": metadata,
    }


def build_session_index(args: argparse.Namespace) -> dict[str, Path]:
    return {path.stem: path for path in discover_required_transcript_files(args)}


def export_multiple_sessions(args: argparse.Namespace) -> list[dict[str, Any]]:
    session_index = build_session_index(args)
    results: list[dict[str, Any]] = []
    missing = [session_id for session_id in args.session_ids or [] if session_id not in session_index]
    if missing:
        raise FileNotFoundError(f"没有找到这些 session ID 对应的 transcript: {', '.join(missing)}")

    for session_id in args.session_ids or []:
        results.append(build_export_result(args, session_index[session_id]))
    return results


def render_session_list_text(summaries: list[dict[str, Any]]) -> str:
    lines = [f"sessions: {len(summaries)}", ""]
    for index, summary in enumerate(summaries, start=1):
        lines.extend(
            [
                f"{index}. {summary['title']}",
                f"   session_id: {summary['session_id']}",
                f"   started_at: {summary['display_time']}",
                f"   messages: {summary['message_count']} (user={summary['user_message_count']}, assistant={summary['assistant_message_count']})",
                f"   transcript: {summary['source_transcript']}",
            ]
        )
        if summary["warning_count"]:
            lines.append(f"   warnings: {summary['warning_count']}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = parse_args()
    try:
        validate_args(args)

        if args.list_sessions:
            summaries = collect_session_summaries(args)
            if args.list_json:
                print(json.dumps({"count": len(summaries), "sessions": summaries}, ensure_ascii=False, indent=2))
            else:
                print(render_session_list_text(summaries), end="")
            return 0

        if args.session_ids:
            results = export_multiple_sessions(args)
            print(f"输出目录: {choose_output_dir(args)}")
            print(f"导出会话数: {len(results)}")
            for result in results:
                print(f"- {result['session_title']} | {result['session_id']} | {result['output_path']}")
            return 0

        transcript_path = resolve_transcript(args)
        result = build_export_result(args, transcript_path)
    except (FileNotFoundError, ValueError) as exc:
        print(f"导出失败：{exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # pragma: no cover
        print(f"导出失败：{exc}", file=sys.stderr)
        return 1

    print(f"输出文件: {result['output_path']}")
    print(f"源 transcript: {result['source_transcript']}")
    print(f"会话 ID: {result['session_id']}")
    print(f"标题: {result['session_title']}")
    print(f"消息数: {result['message_count']}")
    print(f"warnings: {result['warning_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())