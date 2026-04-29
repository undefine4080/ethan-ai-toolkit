# Copilot transcript 格式说明

本 skill 默认从 `transcripts/<session-id>.jsonl` 读取会话，而不是从 `debug-logs/` 直接读取。

## 为什么优先使用 transcripts

- `transcripts` 里通常有完整的用户消息和助手消息
- 文件是 JSONL，适合顺序扫描和增量处理
- 同一个会话的工具调用、turn 边界和消息事件通常都集中在这里

## 常见事件类型

### 1. `session.start`

通常用于提取会话级元数据：

- `data.sessionId`
- `data.copilotVersion`
- `data.vscodeVersion`
- `data.startTime`

### 2. `user.message`

最重要的字段：

- `data.content`
- `data.attachments`
- 顶层 `timestamp`

这是导出用户发言的主要来源。

### 3. `assistant.message`

最重要的字段：

- `data.content`
- `data.toolRequests`
- `data.reasoningText`
- 顶层 `timestamp`

默认导出时应保留 `content`，是否保留 `toolRequests` 和 `reasoningText` 取决于用户意图。

### 4. `tool.execution_start`

常见字段：

- `data.toolCallId`
- `data.toolName`
- `data.arguments`

这类事件通常用来补全工具调用的执行信息，而不是作为用户可见聊天正文。

### 5. `tool.execution_complete`

常见字段：

- `data.toolCallId`
- `data.success`

可以和 `assistant.message.data.toolRequests` 或 `tool.execution_start` 关联，生成工具调用摘要。

### 6. `assistant.turn_start` / `assistant.turn_end`

这类事件更适合调试，不适合直接导出为最终聊天正文。默认可以忽略。

## 导出时的默认取舍

- 默认导出：`user.message.data.content`
- 默认导出：`assistant.message.data.content`
- 可选导出：`assistant.message.data.toolRequests`
- 默认不导出：`assistant.message.data.reasoningText`
- 默认不导出：turn 边界事件

## 推荐的数据映射

## session 标题提取建议

交互式多选场景需要给每个 session 一个可读标题。推荐顺序：

1. 第一条非空 `user.message.data.content`
2. 第一条非空 `assistant.message.data.content`
3. 如果都没有，退化为 `Untitled session`

标题只用于展示和选择，不应替代 `session_id` 作为唯一标识。

### Markdown

- 会话元数据写在文件头部
- 按时间顺序写出用户和助手消息
- 工具调用作为助手消息下的附加小节

### JSON

- `metadata`：会话级信息和导出配置
- `messages`：线性消息数组
- `warnings`：解析坏行、找不到字段等问题

## 不推荐的做法

- 直接从 `debug-logs/main.jsonl` 导出完整对话
- 默认暴露 `reasoningText`
- 把每个 tool event 都独立导成一条“聊天消息”