# `.claude/commands/` 详细教程

## 目录结构

```
project-root/
└── .claude/
    └── commands/
        ├── command1.md
        ├── command2.md
        └── command3.md
```

全局命令位于 `~/.claude/commands/`，项目命令位于 `project/.claude/commands/`。

## 基本格式

每个命令文件包含两部分：**Frontmatter**（配置区）和**内容区**（执行指令）

```yaml
---
description: 命令的简要描述
argument-hint: <参数提示>
---

命令的实际执行内容...
```

---

## Frontmatter 字段详解

### 必需字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `description` | string | 描述命令功能，Claude 根据此判断何时使用 |

### 可选字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `argument-hint` | string | 自动完成时显示的参数提示 |
| `name` | string | 命令名（默认使用文件名不含 .md） |

---

## 参数传递机制

### 基本参数变量

| 变量 | 说明 | 示例 |
|------|------|------|
| `$ARGUMENTS` | 所有传入的参数（原始字符串） | `hello world` |
| `$ARGUMENTS[N]` 或 `$N` | 第 N 个参数（从 0 开始） | `$0` = 第一个参数 |

### 示例：参数处理

#### 命令文件 `fix-issue.md`

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

调用：`/fix-issue 123`

#### 命令文件 `create-component.md`

```yaml
---
description: 创建新的 React 组件
argument-hint: <component-name> [path]
---

创建 React 组件 $0：

如果提供了路径 $1，则在 $1 目录下创建，否则在 src/components/ 下。

组件名称：$0
路径：${1:-src/components/}

请执行：
1. 使用 Glob 查找现有的组件结构
2. 参考现有组件的风格
3. 创建 $0 组件，包含必要的 props 和类型定义
4. 添加基础样式
```

调用：`/create-component Button` 或 `/create-component Button src/ui/`

---

## 实战示例

### 示例 1：数据库迁移命令

```yaml
---
description: 创建数据库迁移文件
argument-hint: <migration-name>
---

创建数据库迁移文件 $0：

1. 检查项目中的迁移文件结构
2. 在 migrations/ 目录下创建迁移文件
3. 迁移文件名格式：YYYYMMDDHHMMSS_$0.sql
4. 添加 up 和 down 语句模板
5. 提醒用户填写具体的 SQL 逻辑
```

### 示例 2：API 测试命令

```yaml
---
description: 测试 API 端点
argument-hint: <endpoint> [method=GET]
---

测试 API 端点：

端点：$0
方法：${1:-GET}

请执行：
1. 使用 Grep 查找该端点的实现代码
2. 阅读端点的参数和返回值定义
3. 使用 Bash 调用该端点进行测试
4. 验证返回结果是否符合预期
```

调用：`/api-test /users` 或 `/api-test /users POST`

### 示例 3：代码格式化命令

```yaml
---
description: 格式化指定文件或目录
argument-hint: <file-or-directory> [formatter]
---

格式化代码：

目标：$0
格式化工具：${1:-prettier}

请执行：
1. 检查 $0 是否存在
2. 确定项目使用的格式化工具
3. 运行格式化命令
4. 显示格式化的变更
```

### 示例 4：环境变量检查命令

```yaml
---
description: 检查环境变量配置
argument-hint: [env=development]
---

检查 $0 环境变量配置：

1. 检查 .env.${0:-development} 文件是否存在
2. 验证必需的环境变量是否已设置
3. 检查是否有变量缺失或无效
4. 提供修复建议
```

调用：`/env-check` 或 `/env-check production`

---

## 高级技巧

### 技巧 1：使用特殊字符实现多行提示

```yaml
---
description: 生成测试用例
argument-hint: <module-name>
---

为模块 $0 生成测试用例：

要求：
- 至少包含 3 个测试用例
- 包含正常情况测试
- 包含边界情况测试
- 包含异常情况测试

使用项目现有的测试框架和风格。
```

### 技巧 2：默认值语法

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

`${0:-default}` 表示如果 $0 未提供则使用 default

### 技巧 3：条件执行提示

```yaml
---
description: 代码重构
argument-hint: <file-path>
---

重构文件 $0：

先分析当前代码：
- 找出代码异味
- 识别重复代码
- 检查命名规范

然后执行重构：
- 提取重复逻辑为函数
- 改善命名
- 简化复杂逻辑

注意：不要改变外部接口
```

---

## 目录位置

| 位置 | 路径 | 适用范围 |
|------|------|----------|
| 全局命令 | `~/.claude/commands/` | 所有项目 |
| 项目命令 | `project/.claude/commands/` | 当前项目 |

**优先级**：项目命令 > 全局命令（同名时项目命令优先）

---

## 命令命名规范

1. **使用小写字母**：`deploy-app.md`
2. **使用连字符分隔单词**：`fix-issue.md`
3. **简洁描述性**：`db-migrate.md` 比 `database-migration.md` 更好
4. **避免特殊字符**：不要使用空格、下划线等

---

## 调试技巧

### 1. 检查命令是否被识别

在 Claude Code 中输入 `/` 看看你的命令是否出现在列表中

### 2. 测试命令执行

```bash
# 查看命令文件
cat .claude/commands/your-command.md

# 测试命令
/your-command test-argument
```

### 3. 查看执行日志

如果命令没有按预期工作，查看 Claude 的输出，了解它如何理解你的命令

---

## 最佳实践

### 1. 描述要清晰

```yaml
---
description: 生成 README 文档，包含项目概述、安装和使用说明
---
```

### 2. 参数提示要具体

```yaml
---
argument-hint: <filename> [output-format=markdown]
---
```

### 3. 内容要分步骤

```yaml
---

步骤 1：分析需求
- 理解用户意图
- 确定技术方案

步骤 2：实现代码
- 按照规范编码
- 添加必要的注释

步骤 3：测试验证
- 编写测试用例
- 验证功能正确性
```

### 4. 保持命令专注

每个命令应该做一件事，做好一件事

### 5. 使用项目特定信息

```yaml
---
description: 部署到公司内部服务器
---

部署到内部服务器：
- 使用公司内部的部署脚本
- 遵循安全规范
- 获取必要的授权
```

---

## 常见问题

### Q1: 命令没有被识别？

**A**: 检查以下几点：
- 文件是否在正确的目录（`.claude/commands/`）
- 文件扩展名是否是 `.md`
- Frontmatter 是否格式正确
- `description` 字段是否存在

### Q2: 参数没有传递成功？

**A**:
- 确保使用 `$ARGUMENTS` 或 `$0`、`$1` 等变量
- 检查参数之间是否有空格分隔
- 使用引号包裹带空格的参数：`/command "hello world"`

### Q3: 如何实现更复杂的功能？

**A**: 如果需要复杂功能，考虑：
1. 将命令拆分成多个简单命令
2. 迁移到 Skills 格式，支持更多高级特性

### Q4: 可以在命令中调用其他命令吗？

**A**: 可以。在内容区写清楚调用其他命令的指令即可：

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

---

## 与 Skills 的选择

| 场景 | 推荐使用 |
|------|----------|
| 简单的单步骤任务 | `.claude/commands/` |
| 需要多文件支持（示例、模板） | `.claude/skills/` |
| 需要控制工具权限 | `.claude/skills/` |
| 需要在子代理中执行 | `.claude/skills/` |
| 快速创建临时命令 | `.claude/commands/` |
| 长期维护的复杂功能 | `.claude/skills/` |
