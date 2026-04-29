---
name: code-review-architect
description: 专家级代码评审 skill。以资深工程师视角对软件项目做架构、简洁性、可读性、工程范式四个维度的品味级审查，而非 linter 级的低级规则检查。触发条件：用户要求"code review""代码评审""审查项目""帮我看看这个项目""review 这段代码""项目架构评审""技术债盘点"等；用户分享本地项目路径并希望评估代码质量、架构健康度、可维护性时也应触发。适用于 React / Vue 3 / Next.js 项目，其他技术栈会礼貌告知边界并让用户选择是否继续。
---

# Code Review Architect

一个以**品味**为核心的代码评审 skill。关注架构优雅、简洁、可读性、工程范式，**不做**规则级的 lint 类工作（命名、格式、明显 bug 那些交给 ESLint/Prettier）。

---

## 本 Skill 自身的扩展纪律（给未来的维护者）

这个 skill 自己也要遵守"大道至简"。任何扩展必须遵循：

1. **新增语言/框架** → 只新增 `frameworks/<name>.md`，不改其他任何文件
2. **调整评审维度** → 只改 `principles/` 下对应文件
3. **调整流程** → 只改 SKILL.md 或 `workflows/`
4. **禁止**：把语言/框架特化逻辑写进 `principles/` 或 SKILL.md
5. **禁止**：在 SKILL.md 里维护"框架→文件"中央映射表。依赖关系由每份 `frameworks/*.md` 自己在首段声明

违反以上任何一条，说明架构在腐化，必须重构。

---

## 核心定位

这个 skill 做什么 / 不做什么，一开始就要讲清楚：

**做**：
- 架构是否优美？是否过度设计、冗余抽象？
- 代码逻辑是否绕弯路、复杂度是否失控？
- 是否易读、易扩展？人类能不能持续维护？
- 是否采用了好的工程范式（组合优于继承、composable、完整类型声明）？
- 是否有**该做而没做**的事（缺少 error boundary、缺少 loading/empty 态、缺少类型守卫等）

**不做**：
- 不做命名、格式、缩进等 linter 级检查
- 不提供具体修改代码（只提出问题和方向）
- 不对自己不支持的语言瞎评（见礼貌终止流程）

---

## 启动流程（自顶向下的决策树）

### Step 1：确认技术栈（不要自己推理）

**原则**：code review 的触发者是人类开发者，他知道自己项目的技术栈。让 AI 自动探测 `package.json` 是对时间和 token 的双重浪费。

- 如果用户在调用时已经说明了栈（例："帮我 review 这个 Next 14 App Router 项目"），直接采纳
- 如果用户没说明，**主动询问一次**，例如：

  > 开始评审前需要确认技术栈，请告知：
  > - 主框架和版本（如 React 18 / Next 14 App Router / Vue 3 等）
  > - 是否使用 TypeScript
  > - 评审范围（默认整个目录，也可以指定子目录）

- **严禁**在用户未声明的情况下自己读 `package.json` 推理。拿不到就问，不要猜

### Step 2：框架支持检查

根据用户声明的框架，去 `frameworks/` 目录找对应文件：

- **命中** → 进入 Step 3
- **未命中**（例如用户说 Go、Python、Rust） → **不要硬撑**，加载 `workflows/graceful-exit.md` 按里面的协议处理

### Step 3：加载评审资源

**加载纪律（非常重要，决定评审质量）**：

| 时机 | 加载内容 | 原因 |
|---|---|---|
| 进入评审前 | `principles/` 下**全部 4 份** | 它们是评审的"尺子"，高价值短文档，必须全量加载 |
| 进入评审前 | 用户声明框架对应的 `frameworks/<name>.md` | 框架特化知识 |
| 递归加载 | 上一步文件**首段声明的依赖**（如 `next.md` 依赖 `react.md`） | 叠加加载模型，避免重复写 |
| 生成报告前 | `report-template.md` | 统一输出格式 |

**叠加加载示例**：
- 用户说 Next → 读 `frameworks/next.md` → 看到首段声明"依赖 react.md" → 同时加载 `frameworks/react.md`
- 用户说 React → 只加载 `frameworks/react.md`

**每份 frameworks 文档自己声明依赖**，SKILL.md 不维护中央配置表。这样新增 Go 只需写 `frameworks/go.md`，SKILL.md 一行不动。

### Step 4：执行审查

加载 `workflows/review-flow.md`，按它的"自顶向下，由粗到细"方法执行。

### Step 5：生成报告

按 `report-template.md` 的骨架输出，写入工作目录下：

```
<cwd>/.ai/code-review/review-YYYY-MM-DD-HHmm.md
```

如果用户指定了子目录范围，文件名附加 slug：
```
review-YYYY-MM-DD-HHmm-src-features-auth.md
```

目录不存在时自动创建 `.ai/code-review/`。

### Step 6：对话中只给摘要

详细内容进 markdown 文件，对话里只输出：
- 一段话总体评价
- Critical 问题数量（至多 3 条，见报告纪律）
- 报告文件路径

避免把完整报告塞进对话，浪费 token、也让用户难以归档。

---

## 输出纪律（防止 AI 味评审）

这几条要反复强调，模型容易犯：

1. **不给修改代码**。允许"建议把 X 和 Y 的职责拆分"；禁止贴完整重写后的代码块。
2. **Critical 级问题全报告至多 3 条**。超过必须降级或合并。这是防严重度通胀的硬约束。
3. **每条问题必须写"为什么"**。空泛评语（"这里可以更好"）不算一条问题。
4. **个人偏好必须标注为 💭 Nit**。不要把品味伪装成客观问题。
5. **报告可以有"亮点"章节**。全是负面，可能是不专业、不全面的评审。
6. **报告必须有"Blind Spots"章节**，强制思考"该做而没做"的事。

---

## 当用户的请求超出范围时

- 用户要求"帮我修复这些问题" → 温和地说明本 skill 只做 review，修复建议属于另一个工作，可以基于报告单独开一个任务
- 用户要求"只评审某一个维度"（如只看性能） → 可以做，但提醒"本 skill 强项是架构/简洁/可读/范式四个维度，性能/安全属于边缘覆盖"
- 用户要求审查语言不在支持列表 → 走 `workflows/graceful-exit.md`

---

## 目录地图（快速索引）

```
code-review-skill/
├── SKILL.md                    ← 你在这里
├── principles/                 ← 评审的尺子（永不变，全量加载）
│   ├── architecture.md         # 架构优雅 / 过度设计识别
│   ├── simplicity.md           # 大道至简 / 反绕弯路
│   ├── readability.md          # 可读 / 可扩展 / 可维护
│   └── paradigms.md            # 组合优于继承 / composable / 类型完整性
├── frameworks/                 ← 可插拔的底（按需加载 + 可叠加）
│   ├── _template.md            # 新增语言/框架时复制这份
│   ├── react.md
│   ├── vue.md
│   └── next.md                 # 依赖 react.md
├── workflows/                  ← 流程细节
│   ├── review-flow.md          # 主审查流程（自顶向下）
│   └── graceful-exit.md        # 不支持语言时的礼貌终止协议
└── report-template.md          ← 最终报告骨架
```
