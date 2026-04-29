# 人物关系可视化场景

## 场景说明

将文学作品、影视、历史等中的人物关系网络可视化。支持两种子类型，**根据关系性质选择**：

| 子类型 | 适用场景 | 特点 |
|--------|----------|------|
| **力导图**（Force Graph） | 人物之间存在多对多、网状关系 | 节点自由布局，边有标签，可拖拽 |
| **折叠树图**（Collapsible Tree） | 人物之间是明确的层级/传承关系 | 树状展开/折叠，清晰展示血脉或组织层级 |

**如果两种关系都存在**（如《百年孤独》既有家族树又有复杂关系），可考虑同页双图或提供切换。

---

## 技术栈

- **D3.js v7**（CDN: `https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js`）
- 纯 HTML + Vanilla JS，无需构建工具
- 数据通过 `fetch('./data.json')` 加载

---

## 数据格式规范

### 力导图数据格式（`data.json`）

参考模板：`templates/force-graph-data.json`

```json
{
  "title": "作品名称",
  "description": "图谱说明",
  "nodes": [
    {
      "id": "buendia_jose",
      "name": "何塞·阿尔卡蒂奥·布恩迪亚",
      "shortName": "老布恩迪亚",
      "group": "布恩迪亚家族",
      "gender": "male",
      "generation": 1,
      "description": "布恩迪亚家族创始人，马孔多镇的建立者",
      "importance": 5
    }
  ],
  "links": [
    {
      "source": "buendia_jose",
      "target": "ursula",
      "relation": "夫妻",
      "type": "marriage",
      "bidirectional": true
    }
  ]
}
```

**节点字段说明：**
- `id`：唯一标识符（英文，用于 D3 引用）
- `name`：完整名称
- `shortName`：图中显示的简短名称（可选）
- `group`：所属阵营/家族（用于节点分组着色）
- `gender`：`male` / `female` / `unknown`
- `generation`：代际层级（数字，用于布局参考）
- `importance`：重要程度 1-5（影响节点大小）
- `description`：人物简介（tooltip 显示）

**边字段说明：**
- `source` / `target`：节点 id
- `relation`：关系描述（显示在边上）
- `type`：关系类型，枚举值：`marriage` / `parent-child` / `sibling` / `friend` / `enemy` / `romance` / `political` / `other`
- `bidirectional`：是否双向关系（影响箭头样式）

---

### 折叠树图数据格式（`data.json`）

参考模板：`templates/collapsible-tree-data.json`

```json
{
  "title": "作品名称",
  "description": "家族传承图",
  "root": {
    "id": "buendia_jose",
    "name": "何塞·阿尔卡蒂奥·布恩迪亚",
    "shortName": "创始人",
    "gender": "male",
    "spouse": "乌尔苏拉",
    "born": "约1820年",
    "died": "约1880年",
    "description": "布恩迪亚家族创始人",
    "children": [
      {
        "id": "jose_arcadio_1",
        "name": "何塞·阿尔卡蒂奥（长子）",
        "gender": "male",
        "born": "约1840年",
        "description": "大儿子，继承父亲体型",
        "children": []
      }
    ]
  }
}
```

**节点字段说明：**
- `id`：唯一标识符
- `name`：完整名称
- `shortName`：图中显示的简短名称（可选）
- `gender`：`male` / `female` / `unknown`
- `spouse`：配偶姓名（字符串，显示用）
- `born` / `died`：生卒年份（字符串，可选）
- `description`：人物简介
- `children`：子节点数组（递归结构）

---

## 实现要点

### 力导图

**布局核心：**
```javascript
const simulation = d3.forceSimulation(nodes)
  .force("link", d3.forceLink(links).id(d => d.id).distance(120))
  .force("charge", d3.forceManyBody().strength(-400))
  .force("center", d3.forceCenter(width / 2, height / 2))
  .force("collision", d3.forceCollide().radius(d => nodeRadius(d) + 10));
```

**视图重置的正确实现（重要）：**

❌ **错误做法**（会导致图谱偏移到画布角落）：
```javascript
// 这只是把原点移到中心，而节点已经分布在 (width/2, height/2) 附近
// 叠加后会偏移到右下角
svg.transition().call(zoom.transform, d3.zoomIdentity
  .translate(width / 2, height / 2)
  .scale(0.65));
```

✅ **正确做法**（计算包围盒，确保图谱居中）：
```javascript
function calcFitTransform() {
  const bounds = g.node().getBBox(); // 获取所有节点的包围盒
  const fullWidth = bounds.width;
  const fullHeight = bounds.height;
  const midX = bounds.x + fullWidth / 2;
  const midY = bounds.y + fullHeight / 2;

  // 计算合适的缩放比例（留 10% 边距）
  const scale = 0.9 / Math.max(fullWidth / width, fullHeight / height);

  // 计算平移量，使包围盒中心对齐画布中心
  const translate = [width / 2 - scale * midX, height / 2 - scale * midY];

  return d3.zoomIdentity.translate(translate[0], translate[1]).scale(scale);
}

// 使用
svg.transition().duration(750).call(zoom.transform, calcFitTransform());
```

**关键交互：**
- 节点可拖拽（`dragstarted` / `dragged` / `dragended`）
- hover 显示人物详情 tooltip
- 点击节点 → 高亮关联边和邻居节点 + 右侧面板显示详情（包含关联人物列表，可点击跳转）
- 支持缩放和平移（`d3.zoom()`）
- 双击空白区域取消高亮
- **视图重置按钮**：计算节点包围盒，自动缩放并居中显示完整图谱（避免偏移到画布角落）

**视觉编码：**
- 节点颜色 → group（家族/阵营）
- 节点大小 → importance
- 边颜色 → type（不同关系类型用不同色）
- 边粗细 → 关系重要程度（可选）

### 折叠树图

**布局核心：**
```javascript
const treeLayout = d3.tree().size([height, width - 200]);
// 点击节点展开/折叠
function toggle(d) {
  if (d.children) {
    d._children = d.children;
    d.children = null;
  } else {
    d.children = d._children;
    d._children = null;
  }
}
```

**关键交互：**
- 点击节点展开/折叠子树
- hover 显示详细信息
- 支持缩放和平移

**视觉编码：**
- 节点颜色 → gender（男/女不同色）
- 节点形状 → 有无子节点（圆形 vs 菱形，可选）
- 连线样式 → 平滑贝塞尔曲线

---

## 页面布局建议

### 力导图布局（参考百年孤独案例）

```
┌─────────────────────────────────────────────────────────┐
│  标题 + 副标题 + 统计信息（右上角）                        │
│  [视图切换按钮] [重置视图] [缩放控制]                      │
├──────────────────────────────────┬──────────────────────┤
│                                  │  右侧面板（固定宽度）  │
│   主图区域（D3 SVG，占 75%）      │  ─────────────────   │
│   - 深色背景                      │  图例：              │
│   - 节点可拖拽                    │  - 关系类型色块      │
│   - 边带标签                      │  - 家族/阵营色块     │
│   - 支持缩放平移                  │                      │
│                                  │  人物详情（点击显示）：│
│                                  │  - 姓名              │
│                                  │  - 简介              │
│                                  │  - 关联人物列表      │
│                                  │    （可点击跳转）     │
└──────────────────────────────────┴──────────────────────┘
│  底部状态栏：数据统计 + 操作提示 + 版权信息                │
└─────────────────────────────────────────────────────────┘
```

### 家族树布局（可选，与力导图切换）

```
┌─────────────────────────────────────────────────────────┐
│  [力导图 | 家族树] 切换按钮                                │
├──────────────────────────────────┬──────────────────────┤
│                                  │  右侧面板：           │
│   水平树状图（D3 Tree）           │  - 代际说明          │
│   - 根节点居左                    │  - 性别图例          │
│   - 后代向右展开                  │  - 节点操作说明      │
│   - 点击展开/折叠                 │                      │
│   - 节点下方显示配偶              │                      │
└──────────────────────────────────┴──────────────────────┘
```

**关键设计要点：**
- 右侧面板固定宽度（300-350px），主图区域自适应
- 顶部工具栏包含视图切换、重置、缩放控制
- 底部状态栏显示统计信息（如"34 人物 · 66 关系"）
- 深色主题更适合复杂关系网络，减少视觉疲劳

---

## 配色参考

**家族/阵营配色：** 使用 `d3.schemeTableau10` 或自定义色板
**性别配色：** 男性 `#4A90D9`，女性 `#E8739C`
**背景：** 深色 `#1a1a2e` 或浅色 `#f8f9fa`，根据主题选择
**边颜色：** marriage `#FFD700`，enemy `#FF4444`，friend `#44BB44`，其他 `#999`

---

## 模板参考文件

- `templates/force-graph-data.json`：力导图标准数据格式示例（《百年孤独》片段）
- `templates/collapsible-tree-data.json`：折叠树图标准数据格式示例（布恩迪亚家族树）

> 模板仅作数据格式参考，**不直接使用**，每次根据实际内容从零设计页面。
