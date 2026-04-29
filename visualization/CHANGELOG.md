# Changelog

## v0.5.0 — 2026-03-23

### 新增：化学场景技术文档库

为 chemistry 场景收集整理了 5 份核心技术参考文档，作为子 agent 的知识库：

| 文档 | 路径 | 核心内容 |
|------|------|---------|
| SmilesDrawer v2 | `docs/smilesdrawer-reference.md` | parse/draw API、v2.1.x 7 参数签名、themes 配置、已知坑点 |
| 3Dmol.js | `docs/3dmol-reference.md` | 支持的格式列表（明确 `'smi' 不支持）、样式配置、颜色方案 |
| NGL Viewer | `docs/ngl-reference.md` | Stage API、20 种表示方式、22 种颜色方案、选择器语法 |
| D3.js v7 | `docs/d3-reference.md` | zoom/forceSimulation/tree API、SVG marker |
| PubChem REST API | `docs/pubchem-api-reference.md` | SDF 获取 URL、`record_type=3d` 参数、速率限制 |

### SCENE.md 更新

- 新增「技术文档参考」章节：子 agent 编码前优先查阅相关文档，避免盲目猜测 API
- 明确了各库的官方文档来源和关键 API 签名

### 价值

- SmilesDrawer：明确了 v2.1.x 的 `draw(data, target, theme, weights, infoOnly)` 7 参数签名
- 3Dmol.js：明确列出了支持/不支持的格式，`'smi'` 不可用
- PubChem API：提供了规范的 SDF 获取 URL 和速率限制说明

---

## v0.4.0 — 2026-03-23

### 新增场景
- **化学分子可视化**（`scenes/chemistry/`）：新增第7个场景，涵盖5个子类型
  - 合成路线图（SmilesDrawer + D3.js）
  - 分子结构查看器（SmilesDrawer 2D + 3Dmol.js 3D）
  - 反应机理动画（SmilesDrawer + SVG 动画）
  - 晶体结构（3Dmol.js / Three.js）
  - 蛋白质可视化（NGL Viewer）
- 基于阿莫西林案例完成首次实测，修复了所有发现的库使用问题，将踩坑经验写入 SCENE.md

### SOP 增强
- **可视化实现 Agent 新增第5步「冒烟测试」**：完成代码后强制用 agent-browser 截图验证，检查控制台报错和核心元素渲染，发现问题在子 agent 内直接修复，不再依赖用户反馈才能发现基础错误
- **实现 Agent 第1步增加「优先阅读已知坑点」提示**：确保子 agent 在编码前看到 SCENE.md 中的⚠️警告

### 数据质量增强
- **数据完整性自检清单**：数据 Agent 在写入 data.json 前必须执行5项自检（JSON 合法性、必填字段、id 引用完整性、数据量合理性、推断数据标注）
- **化学合成路线专项检查**：要求遍历所有 reactions 的 from/to，确保每个引用的 id 在 compounds 中均有对应条目

### 知识管理机制
- **SCENE.md 维护原则**：新增强制更新规则，API 用法不符、CDN 失效、数据格式变更、发现更优方案时，必须立即更新对应 SCENE.md，将实战经验永久沉淀为规范

### 已知坑点（chemistry SCENE.md 实测记录）
- SmilesDrawer v2 `Drawer` 实为 `SvgDrawer`，渲染目标必须是 `<svg>` 而非 `<canvas>`
- SmilesDrawer v2.1.x `draw()` 第4参数是 `weights`，调用时必须显式传 `null`，否则 `false` 被误当成 `weights` 报 `TypeError`
- 3Dmol.js 不支持 `'smi'` 格式，需通过 PubChem REST API 获取 SDF 再加载
- 化学合成路线中的过渡中间体（硅基化保护态等）容易被数据 Agent 遗漏，需专项检查

---

## v0.3.0 — 2026-03-23

### 新增
- **server.js 智能端口重试**：端口被占用时自动尝试下一个端口（最多尝试 10 次），无需手动指定新端口
- **SCENE.md 补充实战经验**（基于百年孤独案例）：
  - 视图重置的正确实现方法（计算包围盒避免偏移）
  - 详细的页面布局参考（力导图 + 家族树双视图切换）
  - 增强的交互功能（右侧详情面板、关联人物跳转、双击取消高亮）
  - 底部状态栏设计（统计信息 + 操作提示）

### 修复
- server.js 端口占用时会直接报错退出 → 现在自动尝试下一个可用端口

---

## v0.2.0 — 2026-03-23

### 新增
- **子 Agent 架构**：明确规定主 agent 只负责协调，实质性任务由数据准备和可视化实现两个子 agent 并行承担，避免主 agent 上下文被占满
- **自动数据采集**：数据准备 agent 负责通过 WebSearch 或 agent-browser skill 自动搜索、采集、整理数据，用户无需自备数据

### 变更
- SKILL.md 新增"子 Agent 架构"章节，作为最高优先级规范
- SOP 第四步重构为"并行启动子 Agents"，明确两个子 agent 的职责边界和交付物
- 数据采集策略：优先 WebSearch，复杂页面改用 agent-browser，不足时用常识补充并标注

---

## v0.1.0 — 2026-03-23

### 新增
- 初始化 skill 框架，确立核心 SOP 四步流程
- 实现**人物关系可视化**场景（`scenes/character-relationship/`）
  - 支持力导图（D3 Force Graph）用于多对多关系展示
  - 支持折叠树图（D3 Collapsible Tree）用于层级传承展示
  - 提供标准 JSON 数据格式规范（`templates/` 中的参考文件）
- 创建通用 Node.js 开发服务器（`shared/server.js`），支持自动打开浏览器
- 建立场景路由表机制，支持自动识别场景

### 设计决策
- 数据与视图分离：所有可视化数据存放在独立 `data.json`，HTML 通过 `fetch` 加载
- 模板仅作参考：每次可视化从零设计，不直接复制模板，保持最大灵活性
- 每次可视化在当前目录下创建独立子目录
- 优先自动识别场景，不确定时才呈现选项
