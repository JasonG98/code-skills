#!/usr/bin/env python3
"""
解析今日 Claude Code 对话记录, 只适用于 Claude Code.
从 ~/.claude/projects/ 读取 JSONL, 输出结构化文本供日报生成使用
"""

import json
import sys
from datetime import date, datetime
from pathlib import Path


def decode_project_name(dir_name: str) -> str:
    """
    将编码后的目录名还原为可读路径。
    Claude Code 将路径中的 / 替换为 -，并去掉开头的 /
    例：-Users-name-Code-myproject -> /Users/name/Code/myproject
    """
    if dir_name.startswith("-"):
        return "/" + dir_name[1:].replace("-", "/")
    return dir_name.replace("-", "/")


def extract_text(content) -> str:
    """从 message content（str 或 block 列表）中提取纯文本。"""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
        return "\n".join(parts)
    return str(content)


def parse_jsonl(filepath: Path, today: date) -> list[dict]:
    """解析单个 JSONL 文件，返回今日的 user/assistant 消息列表。"""
    messages = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue

                # 只取 user / assistant 类型事件
                event_type = event.get("type", "")
                if event_type not in ("user", "assistant"):
                    continue

                ts_str = event.get("timestamp", "")
                if not ts_str:
                    continue

                try:
                    ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                    # 转换为本地日期比较
                    local_date = ts.astimezone().date()
                    if local_date != today:
                        continue
                except Exception:
                    continue

                message = event.get("message", {})
                role = message.get("role", event_type)
                content = message.get("content", "")
                text = extract_text(content).strip()

                if text:
                    messages.append(
                        {
                            "timestamp": ts_str,
                            "local_time": ts.astimezone().strftime("%H:%M"),
                            "role": role,
                            "text": text,
                        }
                    )
    except Exception as e:
        print(f"[警告] 无法读取 {filepath}: {e}", file=sys.stderr)

    return messages


def main():
    today = date.today()
    today_str = today.strftime("%Y-%m-%d")
    weekday_cn = ["一", "二", "三", "四", "五", "六", "日"][today.weekday()]

    projects_dir = Path.home() / ".claude" / "projects"
    if not projects_dir.exists():
        print(f"未找到 Claude Code 项目目录：{projects_dir}")
        sys.exit(1)

    # 收集各项目的今日消息
    all_projects: dict[str, list[dict]] = {}

    for project_dir in sorted(projects_dir.iterdir()):
        if not project_dir.is_dir():
            continue

        project_path = decode_project_name(project_dir.name)
        project_messages: list[dict] = []

        for jsonl_file in project_dir.glob("*.jsonl"):
            # 先用文件修改时间做快速过滤
            mtime_date = datetime.fromtimestamp(jsonl_file.stat().st_mtime).date()
            if mtime_date < today:
                continue
            project_messages.extend(parse_jsonl(jsonl_file, today))

        if project_messages:
            project_messages.sort(key=lambda x: x["timestamp"])
            all_projects[project_path] = project_messages

    if not all_projects:
        print(f"今日（{today_str}）未找到任何 Claude Code 对话记录。")
        sys.exit(0)

    # 输出结构化文本
    total_msgs = sum(len(v) for v in all_projects.values())
    print("=== Claude Code 今日对话摘要 ===")
    print(f"日期：{today_str}（周{weekday_cn}）")
    print(f"涉及项目数：{len(all_projects)}")
    print(f"消息总数：{total_msgs}")
    print()

    for project_path, messages in all_projects.items():
        display_name = Path(project_path).name or project_path
        print(f"{'=' * 60}")
        print(f"项目：{display_name}")
        print(f"路径：{project_path}")
        print(f"消息数：{len(messages)}")
        print()

        for msg in messages:
            role_label = "用户" if msg["role"] == "user" else "Claude"
            text = msg["text"]
            # 截断过长消息，保留关键内容
            if len(text) > 800:
                text = text[:800] + "\n...[内容过长，已截断]"
            print(f"  [{msg['local_time']}] {role_label}:")
            # 缩进显示
            for line in text.split("\n"):
                print(f"    {line}")
            print()


if __name__ == "__main__":
    main()
