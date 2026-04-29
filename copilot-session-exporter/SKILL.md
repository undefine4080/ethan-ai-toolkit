---
name: copilot-session-exporter
description: 将 GitHub Copilot Chat 会话交互式导出为本地文件。用户提到导出 Copilot 对话、保存 chat、批量备份多个会话、归档聊天记录、列出全部 sessions、按标题选择会话、转存当前 conversation、把 Copilot 聊天写入本地文件、导出 session 或 transcript 时都应使用；即使用户没有明确说“transcript”或“日志”，只要目标是把一个或多个 Copilot 对话保存成可复用文件，也要优先触发这个 skill。
---

# Copilot 会话导出器

这个 skill 用来把 GitHub Copilot Chat 的一个或多个会话交互式导出为本地文件，默认输出为适合阅读和归档的 Markdown。

## 核心原则

1. 默认导出用户可见的会话内容，不默认暴露内部推理。
2. `transcripts/*.jsonl` 是首选数据源；`debug-logs/` 只用于定位会话，不作为主要导出来源。
3. 触发 skill 后，默认先检索并列出全部可发现的 session，再让用户交互式多选，而不是直接猜测用户想导出哪一条。
4. 用户没有特别要求时，固定导出到当前目录下的 `copilot-session/` 目录；目录不存在就创建。
5. 用户没有指定格式时，默认导出 Markdown；只有在需要二次处理、审计或机器消费时再导出 JSON。
6. 用户没有要求保留工具细节时，不导出工具参数和执行状态，避免把噪声和敏感上下文一起写出去。

## 适用任务

- 导出当前 Copilot 对话
- 保存最近一次会话到本地文件
- 备份某个 session 的聊天记录
- 批量备份多个 Copilot 会话
- 列出全部 Copilot sessions 并按标题选择
- 将 Copilot 对话转成 Markdown 或 JSON
- 归档带工具调用信息的 Copilot 调试会话

## 默认工作流

### 第 1 步：检索全部 session 并提取标题

先运行脚本列出全部可发现的 session，不要先问用户 session ID。

优先使用：

```bash
python3 .claude/skills/copilot-session-exporter/scripts/export_copilot_session.py \
  --list-sessions \
  --list-json
```

脚本会返回按时间倒序排列的 session 列表。每一项至少包含：

- `session_id`
- `title`
- `display_time`
- `message_count`
- `source_transcript`

标题默认从该会话第一条非空用户消息提取；如果没有用户消息，则退化为第一条非空助手消息。

### 第 2 步：用交互式多选让用户勾选 session

拿到 session 列表后，使用 `vscode_askQuestions` 发起多选，不要让用户手动复制 session ID。

要求如下：

- `multiSelect` 设为 `true`
- `allowFreeformInput` 设为 `false`
- 选项按最新会话在前排序
- `label` 要能看见标题，建议格式：`<序号>. <标题>`
- `description` 要包含开始时间、session ID、消息数

用户没有明确说“全部导出”时，不要跳过选择步骤。

### 第 3 步：固定导出到当前目录的 copilot-session/

用户选中 session 后，统一导出到当前目录下的 `copilot-session/`，不要再追问输出目录。

推荐命令：

```bash
python3 .claude/skills/copilot-session-exporter/scripts/export_copilot_session.py \
  --session-ids <session-id-1> <session-id-2> ... \
  --output-dir ./copilot-session
```

如果用户明确要求 JSON、工具调用或用户消息过滤，再额外带上 `--format json`、`--include-tools`、`--roles user` 等参数。

### 第 4 步：定位 transcript 的优先级

优先级如下：

1. 用户显式给出 transcript 文件路径
2. 用户显式给出当前 session log 路径
3. 用户显式给出 session ID
4. 当前上下文里能推导出 session 路径或 session ID
5. 自动发现最新的 transcript 文件

默认不要从 `debug-logs` 直接导出，因为真正完整的会话内容通常在 `transcripts/<session-id>.jsonl`。

如果需要字段说明，读取 [references/log-format.md](references/log-format.md)。

### 第 3 步：运行导出脚本

使用本 skill 自带的脚本 [scripts/export_copilot_session.py](scripts/export_copilot_session.py)。

常见命令：

```bash
python3 .claude/skills/copilot-session-exporter/scripts/export_copilot_session.py \
  --session-id <session-id> \
  --format markdown \
  --output copilot-session/<标题>-<时间>.md
```

如果当前上下文里已经拿到了 session log 路径，也可以直接传给脚本：

```bash
python3 .claude/skills/copilot-session-exporter/scripts/export_copilot_session.py \
  --session-log-path <session-log-path>
```

如果用户只说“导出当前会话”，不要直接假设“最新 transcript 就是目标”。先列出全部 sessions 再让用户勾选；只有用户明确说“最近一次”或“当前这一次”时，才可以跳过列表直接定位单条会话。

脚本会自动在常见的 VS Code `workspaceStorage` 目录里寻找 transcript。更多参数和示例见 [references/usage-examples.md](references/usage-examples.md)。

### 第 5 步：校验导出结果

导出后至少做三件事：

1. 确认 `copilot-session/` 目录已经存在
2. 确认用户勾选的每个 session 都生成了对应文件
3. 预览至少一个输出文件的前几行，确认标题、会话 ID 和消息数量正常

如果用户要求“只导出用户消息”或“保留工具调用”，重新运行脚本时使用相应参数，而不是手工改文件。

## 默认输出策略

### 交互式多选

这是默认交互，不是可选增强。

标准流程是：

1. 检索全部 session
2. 展示标题列表
3. 让用户多选
4. 批量导出到 `./copilot-session/`

### Markdown

适用于大多数“保存对话”“归档聊天记录”“发给别人看”的场景。

应包含：

- 会话元数据：session ID、标题、源 transcript、导出时间、消息数
- 按时间顺序排列的用户和助手消息
- 可选的工具调用摘要

默认不包含：

- `reasoningText`
- 完整工具参数
- 无内容的 turn 边界事件

### JSON

适用于后续分析、再处理或批量脚本消费。

应包含：

- 会话元数据
- 线性消息序列
- 可选的工具调用信息
- 解析过程中的 warnings

## 参数选择建议

- 用户没有特别说明时：不要加 `--include-reasoning`
- 用户想审计工具动作时：加 `--include-tools`
- 用户只要用户自己的输入时：加 `--roles user`
- 用户只要可读版本时：用 Markdown，不要 JSON
- 用户需要一次导多条时：优先用 `--session-ids`，不要循环手工一条条导出

## 失败处理

如果导出失败，优先判断是哪一类问题：

1. transcript 没找到
2. session ID 不存在
3. 输出目录不可写
4. transcript 中有损坏的 JSONL 行
5. 用户还没有完成多选

处理原则：

- 优先给出明确失败原因和下一步动作
- 对单行 JSON 解析失败，尽量跳过坏行并保留 warning，而不是整次导出直接失败
- 不要静默降级成导出 `debug-logs`，除非用户明确同意
- 如果选择列表为空，不要擅自导出全部 session

## 响应模板

完成批量导出后，默认告诉用户：

```markdown
已导出 Copilot 会话。

- 导出目录：./copilot-session
- 导出数量：<count>
- 导出格式：Markdown 或 JSON
- 会话列表：
  - <标题 1> -> <path>
  - <标题 2> -> <path>
```

如果用户没有要求额外处理，不要展开解释 transcript 内部结构。

## 示例触发

**示例 1：**
输入：把我的 Copilot sessions 都列出来，我要选几条批量导出。
输出：先列出全部 session 标题和时间，用多选让用户勾选，再导出到当前目录下的 `copilot-session/`。

**示例 2：**
输入：帮我把最近几次 Copilot 对话备份下来，先让我选。
输出：先展示所有可发现的会话标题，让用户多选，不追问输出路径。

**示例 3：**
输入：导出 Copilot 会话到本地，目录固定放当前目录，保留工具调用。
输出：按交互式多选流程执行，并在批量导出时加上 `--include-tools`。