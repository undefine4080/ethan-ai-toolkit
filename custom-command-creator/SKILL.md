---
name: custom-command-creator
description: 创建 Claude Code 自定义斜杠命令（.claude/commands/）。支持全局命令和项目命令的创建，包含参数传递、frontmatter 配置等完整功能。使用场景：（1）用户要求创建新的自定义命令（2）用户询问如何创建 /command 形式的命令（3）用户需要为特定工作流编写快捷命令
---

# 自定义命令创建器

## 概述

本技能帮助创建 Claude Code 的自定义斜杠命令。命令以 `/` 开头，可在任何会话中快速调用预设的工作流。

## 创建流程

### 步骤 1：确定命令类型

根据使用范围选择命令位置：

| 类型 | 位置 | 适用范围 | 优先级 |
|------|------|----------|--------|
| 全局命令 | `~/.claude/commands/` | 所有项目 | 低 |
| 项目命令 | `project/.claude/commands/` | 当前项目 | 高 |

询问用户：**此命令是全局使用还是仅用于当前项目？**

### 步骤 2：收集命令信息

需要以下信息：

1. **命令名称**（使用小写字母和连字符，如 `fix-issue`）
2. **描述**（命令功能的简要说明）
3. **参数提示**（可选，如 `<filename> [path]`）
4. **命令内容**（命令执行时要做什么）

使用以下问题收集信息：
- "命令叫什么名字？（建议使用小写字母和连字符，如 `fix-issue`）"
- "这个命令的功能是什么？"
- "需要接收参数吗？如果需要，参数格式是什么？"
- "命令执行时应该做什么？"

### 步骤 3：创建命令文件

使用 Write 工具创建文件：

- 全局命令：`~/.claude/commands/<command-name>.md`
- 项目命令：`<project-path>/.claude/commands/<command-name>.md`

文件格式：

```yaml
---
description: 命令的简要描述
argument-hint: <参数提示>
---

命令的实际执行内容...
```

### 步骤 4：编写命令内容

使用参数变量：
- `$ARGUMENTS`：所有传入的参数
- `$0`, `$1`, `$2`：第 1、2、3 个参数

示例：

```yaml
---
description: 修复 GitHub issue
argument-hint: <issue-number>
---

修复 GitHub issue $0：
1. 阅读 issue $0 的描述
2. 理解需求和上下文
3. 实现修复方案
4. 编写相关测试
5. 创建提交，引用 issue #$0
```

### 步骤 5：验证命令

使用 Read 工具读取创建的文件，确认格式正确。

然后告知用户：
1. 命令已创建成功
2. 使用方法：`/<command-name> [参数]`
3. 如果命令未显示在 `/` 菜单中，可能需要重启会话

## 高级功能

### 默认值语法

使用 `${N:-default}` 设置默认值：

```yaml
---
description: 部署应用
argument-hint: [env=production]
---

部署应用到 ${0:-production} 环境：
1. 检查 ${0:-production} 环境配置
2. 运行构建命令
3. 执行部署脚本
4. 验证部署成功
```

### 调用其他命令

```yaml
---
description: 完整的发布流程
---

执行完整的发布流程：
1. /run-tests
2. /build-production
3. /deploy production
4. /verify-deployment
```

## 参考资源

详细教程、更多示例和最佳实践请查看：[references/tutorial.md](references/tutorial.md)

## 常见问题

### 命令未出现在 `/` 菜单

检查：
- 文件扩展名是否是 `.md`
- Frontmatter 格式是否正确
- `description` 字段是否存在
- 文件是否在正确的目录

### 参数传递失败

确保：
- 使用 `$ARGUMENTS` 或 `$N` 变量
- 参数之间用空格分隔
- 带空格的参数用引号包裹

## 与 Skills 的选择

| 场景 | 推荐使用 |
|------|----------|
| 简单单步骤任务 | `.claude/commands/` |
| 快速创建临时命令 | `.claude/commands/` |
| 需要工具权限控制 | `.claude/skills/` |
| 需要子代理执行 | `.claude/skills/` |
| 需要多文件支持 | `.claude/skills/` |
