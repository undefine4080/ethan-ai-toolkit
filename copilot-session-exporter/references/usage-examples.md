# 使用示例

以下命令默认在工作区根目录执行。

## 1. 列出全部可发现的 sessions

```bash
python3 .claude/skills/copilot-session-exporter/scripts/export_copilot_session.py \
  --list-sessions
```

## 2. 列出全部 sessions，并输出 JSON 供交互式选择使用

```bash
python3 .claude/skills/copilot-session-exporter/scripts/export_copilot_session.py \
  --list-sessions \
  --list-json
```

## 3. 按 session ID 批量导出到当前目录 copilot-session/

```bash
python3 .claude/skills/copilot-session-exporter/scripts/export_copilot_session.py \
  --session-ids b3f87693-34eb-4d44-a9ac-b427d3bf91c0 77b5dfc0-c82f-4493-83fa-2d7af2b0184c \
  --output-dir ./copilot-session
```

## 4. 直接导出最近一次会话

```bash
python3 .claude/skills/copilot-session-exporter/scripts/export_copilot_session.py
```

默认行为：

- 自动搜索常见的 VS Code `workspaceStorage`
- 选择最新的 transcript
- 导出为 Markdown
- 写入 `copilot-session/<标题>-<时间>.md`

## 5. 指定单个 session ID 导出

```bash
python3 .claude/skills/copilot-session-exporter/scripts/export_copilot_session.py \
  --session-id b3f87693-34eb-4d44-a9ac-b427d3bf91c0
```

## 6. 直接使用当前 session log 路径导出

```bash
python3 .claude/skills/copilot-session-exporter/scripts/export_copilot_session.py \
  --session-log-path "/Users/me/Library/Application Support/Code/User/workspaceStorage/.../GitHub.copilot-chat/debug-logs/b3f87693-34eb-4d44-a9ac-b427d3bf91c0"
```

## 7. 指定 transcript 文件导出

```bash
python3 .claude/skills/copilot-session-exporter/scripts/export_copilot_session.py \
  --transcript "/Users/me/Library/Application Support/Code/User/workspaceStorage/.../GitHub.copilot-chat/transcripts/abc.jsonl"
```

## 8. 导出为 JSON，并保留工具调用摘要

```bash
python3 .claude/skills/copilot-session-exporter/scripts/export_copilot_session.py \
  --format json \
  --include-tools
```

## 9. 只导出用户消息

```bash
python3 .claude/skills/copilot-session-exporter/scripts/export_copilot_session.py \
  --roles user
```

## 10. 指定输出路径

```bash
python3 .claude/skills/copilot-session-exporter/scripts/export_copilot_session.py \
  --output exports/current-chat.md
```

## 11. 指定 workspaceStorage 根目录

```bash
python3 .claude/skills/copilot-session-exporter/scripts/export_copilot_session.py \
  --workspace-storage-root "/Users/me/Library/Application Support/Code/User/workspaceStorage"
```

## 参数建议

- 只想保存可读聊天记录：保持默认值
- 需要机器再处理：加 `--format json`
- 需要调试工具调用：加 `--include-tools`
- 需要内部推理：只有用户明确要求时才加 `--include-reasoning`
- 需要交互式多选：先用 `--list-sessions --list-json` 生成会话列表
- 需要批量导出：用 `--session-ids ... --output-dir ./copilot-session`

## 常见结果说明

脚本执行成功后会打印：

- 输出文件路径
- 导出目录或批量导出数量
- 源 transcript 路径
- session ID
- 导出的消息数
- warning 数量

如果 warning 大于 0，优先检查 transcript 中是否有损坏行，或某些消息字段为空。