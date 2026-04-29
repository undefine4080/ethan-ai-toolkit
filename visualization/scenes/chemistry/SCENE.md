# 化学分子可视化场景

## 场景说明

化学领域的交互式可视化，涵盖从小分子到生物大分子的多种展示形式。根据用户需求自动路由到对应子类型。

**子类型路由表：**

| 子类型 | 关键词 | 核心库 |
|--------|--------|--------|
| **合成路线图** | 合成路线、逆合成、反应步骤、制备方法 | SmilesDrawer + D3.js |
| **分子结构查看器** | 分子结构、3D 结构、化学式、SMILES、化合物 | SmilesDrawer + 3Dmol.js |
| **反应机理动画** | 反应机理、电子转移、过渡态、反应过程 | SmilesDrawer + SVG 动画 |
| **晶体结构** | 晶体、晶格、单元胞、X射线衍射、CIF | 3Dmol.js / Three.js |
| **蛋白质可视化** | 蛋白质、PDB、氨基酸、二级结构、对接 | NGL Viewer |

**子类型选择逻辑：**
- 关键词明确时自动匹配，无需询问
- 关键词模糊时（如"帮我看一下阿莫西林"）默认选「分子结构查看器」
- 同时涉及多个子类型时（如"合成路线 + 3D 结构"）可在同一页面组合展示

---

## 子类型一：合成路线图

### 技术栈
- **SmilesDrawer v2**（`https://cdn.jsdelivr.net/npm/smiles-drawer@2.1.7/dist/smiles-drawer.min.js`）渲染分子结构到 Canvas
- **D3.js v7**（`https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js`）布局与 SVG 箭头

### 数据格式

```json
{
  "title": "阿莫西林合成路线",
  "subtitle": "β-内酰胺类抗生素 · 工业合成路线",
  "description": "以6-APA为核心骨架，通过侧链酰化反应合成阿莫西林",
  "source": "Synthetic Communications, 2003",
  "compounds": [
    {
      "id": "6-apa",
      "name": "6-氨基青霉烷酸",
      "shortName": "6-APA",
      "smiles": "CC1(C)[C@H]2CC(=O)N2[C@@H]1C(=O)O",
      "type": "starting_material",
      "cas": "551-16-6",
      "mw": 216.24,
      "description": "青霉素类药物合成的核心中间体"
    },
    {
      "id": "amoxicillin",
      "name": "阿莫西林",
      "shortName": "Amoxicillin",
      "smiles": "CC1([C@@H](N2[C@H](S1)[C@@H](C2=O)NC(=O)[C@@H](c1ccc(O)cc1)N)C(=O)O)C",
      "type": "product",
      "cas": "26787-78-0",
      "mw": 365.40,
      "description": "广谱β-内酰胺类抗生素"
    }
  ],
  "reactions": [
    {
      "id": "step1",
      "from": ["6-apa", "hpg-derivative"],
      "to": ["amoxicillin"],
      "step": 1,
      "name": "N-酰化反应",
      "type": "acylation",
      "conditions": {
        "reagents": ["三乙胺 (TEA)"],
        "solvent": "二氯甲烷 (DCM)",
        "temperature": "0~5°C",
        "time": "2h"
      },
      "yield": "82%",
      "description": "氨基与活化羧基发生亲核酰化，形成酰胺键"
    }
  ]
}
```

**`compounds[].type` 枚举：** `starting_material` / `reagent` / `intermediate` / `product`

**`reactions[].type` 枚举：** `acylation` / `reduction` / `oxidation` / `cyclization` / `substitution` / `elimination` / `protection` / `deprotection` / `coupling` / `other`

### 实现要点

**布局：** 按 `reactions[].step` 字段分层，同层化合物水平均分，反应箭头连接层间。

**Canvas 与 SVG 混合：**

> ⚠️ **重要**：`SmilesDrawer.Drawer` 在 v2 实际上是 `SvgDrawer` 的别名，只能渲染到 **`<svg>` 元素**，不支持 `<canvas>`。
> - 渲染目标必须用 `document.createElementNS('http://www.w3.org/2000/svg', 'svg')` 创建
> - `draw()` 第二个参数传 **svg DOM 元素对象**
> - 用 `css width/height` 控制显示尺寸，用 `svg attribute width/height` 控制渲染分辨率

```javascript
// ✅ 正确：用 <svg> 元素 + SvgDrawer
const svgEl = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
svgEl.setAttribute('width', 200);
svgEl.setAttribute('height', 160);
container.appendChild(svgEl);  // 必须先加入 DOM，再调用 draw

const drawer = new SmilesDrawer.SvgDrawer({ width: 200, height: 160, bondThickness: 1.2 });
SmilesDrawer.parse(smiles, (tree) => {
  // ⚠️ v2.1.x 签名：draw(data, target, theme, weights, infoOnly)
  // weights 参数在第4位，必须显式传 null，否则 false 被误当成 weights，导致 weights.every 报错
  drawer.draw(tree, svgEl, 'dark', null, false);
}, (err) => console.warn('解析失败', err));

// ❌ 错误：draw(tree, svgEl, 'dark', false) —— false 会被当成 weights，报 TypeError
```

// svg 绝对定位叠加在外层 SVG 上，zoom 时同步更新 left/top 和 width/height

**箭头标注：** 箭头上方显示反应名+产率，下方显示溶剂+温度。

### 页面布局
```
┌──────────────────────────────────────┬──────────────────────┐
│  主图（Canvas + SVG 混合）            │  右侧详情面板         │
│  - 化合物节点（分子结构 Canvas）      │  图例（类型配色）     │
│  - 反应箭头（SVG）                   │  选中化合物详情       │
│  - 条件标注（箭头旁）                 │  CAS / MW / 描述     │
└──────────────────────────────────────┴──────────────────────┘
```

### ⚠️ 已知坑点（实测总结）

| # | 问题 | 根本原因 | 正确做法 |
|---|------|---------|---------|
| 1 | `draw()` 传 `<canvas>` DOM 报 `determineDimensions null` 错误 | SmilesDrawer v2 的 `Drawer` 实际上是 `SvgDrawer` 的别名，只能渲染到 `<svg>`，不支持 canvas | 渲染目标必须用 `document.createElementNS('http://www.w3.org/2000/svg', 'svg')` 创建，传 svg DOM 元素 |
| 2 | `draw(tree, svgEl, 'dark', false)` 报 `weights.every is not a function` | v2.1.x 的 `draw()` 签名为 `draw(data, target, theme, weights, infoOnly)`，`false` 被误当成 `weights` 参数 | 必须显式传 `null` 占位：`draw(tree, svgEl, 'dark', null, false)` |
| 3 | 数据 Agent 整理的 `compounds` 缺少某些中间体，导致对应节点无法渲染 | 合成路线中存在硅基化保护态等过渡中间体（如 `6-apa-silylated`、`amoxicillin-silyl-ester`），容易被遗漏未收录 | 在给数据 Agent 的 prompt 中特别强调：整理完 compounds 后必须遍历所有 reactions 的 from/to，确认每个引用的 id 都已在 compounds 中有对应条目 |

---

## 子类型二：分子结构查看器

### 技术栈
- **SmilesDrawer v2** — 2D 结构渲染
- **3Dmol.js**（`https://cdn.jsdelivr.net/npm/3dmol@2.1.0/build/3Dmol-min.js`）— 3D WebGL 渲染，支持 SMILES / SDF / PDB 输入

### 数据格式

```json
{
  "title": "分子结构对比",
  "molecules": [
    {
      "id": "amoxicillin",
      "name": "阿莫西林",
      "smiles": "CC1([C@@H](N2[C@H](S1)[C@@H](C2=O)NC(=O)[C@@H](c1ccc(O)cc1)N)C(=O)O)C",
      "format": "smiles",
      "description": "广谱β-内酰胺类抗生素",
      "cas": "26787-78-0",
      "mw": 365.40,
      "formula": "C₁₆H₁₉N₃O₅S"
    }
  ],
  "defaultView": "3d"
}
```

**`format` 枚举：** `smiles`（小分子首选）/ `sdf`（带坐标的 Molfile）/ `pdb`（蛋白质/大分子）

### 实现要点

**3Dmol.js 初始化：**

> ⚠️ **注意**：3Dmol.js **不支持** `'smi'` 格式（会报 `Unknown format: smi`）。
> 必须先用 PubChem API 获取含 3D 坐标的 SDF 数据，再加载。

```javascript
const viewer = $3Dmol.createViewer('viewer-container', {
  backgroundColor: '#0d1117',
  antialias: true
});

// ✅ 正确做法：通过 PubChem REST API 获取 3D SDF，再加载
const sdfUrl = `https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/${encodeURIComponent(casOrName)}/SDF?record_type=3d`;
const sdfData = await fetch(sdfUrl).then(r => r.text());
viewer.addModel(sdfData, 'sdf');

// ❌ 错误做法（不支持，会报 Unknown format: smi）：
// viewer.addModel(smilesString, 'smi');

viewer.setStyle({}, { stick: { radius: 0.15 }, sphere: { scale: 0.3 } });
viewer.zoomTo();
viewer.render();
```

**2D/3D 切换：** 同页面展示 SmilesDrawer 的 2D canvas 和 3Dmol.js 的 3D viewer，通过 Tab 或左右分栏切换。

**交互：**
- 3D 视图支持鼠标旋转/缩放/平移（3Dmol 原生支持）
- 点击原子显示元素类型、坐标
- 可选展示模式：棒状（stick）/ 球棒（ball-and-stick）/ 空间填充（sphere）/ 线框（line）

### 页面布局
```
┌─────────────────────────────────────────────────────────────┐
│  分子名 + 化学式 + CAS                                        │
│  [2D 结构] [3D 结构] [球棒模型 | 空间填充 | 线框]             │
├───────────────────────────┬─────────────────────────────────┤
│  2D 结构（SmilesDrawer）  │  3D 结构（3Dmol.js WebGL）       │
│  Canvas 居中显示           │  可旋转/缩放/平移                 │
├───────────────────────────┴─────────────────────────────────┤
│  基本属性：分子式 | 分子量 | CAS | 氢键供体/受体数 | LogP     │
└─────────────────────────────────────────────────────────────┘
```

### ⚠️ 已知坑点（实测总结）

| # | 问题 | 根本原因 | 正确做法 |
|---|------|---------|---------|
| 1 | `viewer.addModel(smilesString, 'smi')` 报 `Unknown format: smi` | 3Dmol.js 不支持直接加载 SMILES 字符串，`'smi'` 不是合法格式 | 先通过 PubChem REST API 获取含 3D 坐标的 SDF 数据，再用 `viewer.addModel(sdfData, 'sdf')` 加载：`https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{name}/SDF?record_type=3d` |

---

## 子类型三：反应机理动画

### 技术栈
- **SmilesDrawer v2** — 渲染反应前后的分子结构
- **SVG 动画**（原生 SMIL 或 CSS animation）— 绘制弯曲箭头表示电子转移
- **anime.js**（可选，`https://cdn.jsdelivr.net/npm/animejs@3.2.1/lib/anime.min.js`）— 控制动画时序

### 数据格式

```json
{
  "title": "SN2 亲核取代反应机理",
  "description": "卤代烷与亲核试剂发生背面进攻的双分子亲核取代",
  "steps": [
    {
      "id": "step1",
      "name": "初始状态",
      "description": "亲核试剂 OH⁻ 从 C-Br 键背面接近",
      "reactants": [
        { "id": "bromoethane", "smiles": "CCBr", "label": "溴乙烷", "role": "substrate" },
        { "id": "oh", "smiles": "[OH-]", "label": "OH⁻", "role": "nucleophile" }
      ],
      "electronArrows": [
        {
          "from": { "atomId": "O", "moleculeId": "oh" },
          "to": { "bond": ["C", "Br"], "moleculeId": "bromoethane" },
          "type": "curved",
          "description": "OH⁻ 提供电子对进攻 C"
        }
      ],
      "duration": 2000
    },
    {
      "id": "step2",
      "name": "过渡态",
      "description": "五配位过渡态，C 同时与 O 和 Br 部分成键",
      "transitionState": {
        "smiles": "[OH2+]CC[Br-]",
        "label": "过渡态 [TS]‡"
      },
      "duration": 1500
    },
    {
      "id": "step3",
      "name": "产物生成",
      "description": "C-Br 键断裂，C-O 键形成，构型翻转（Walden 翻转）",
      "products": [
        { "id": "ethanol", "smiles": "CCO", "label": "乙醇", "role": "product" },
        { "id": "br", "smiles": "[Br-]", "label": "Br⁻", "role": "byproduct" }
      ],
      "duration": 2000
    }
  ]
}
```

### 实现要点

**弯曲箭头（电子转移）：** 用 SVG `<path>` 绘制贝塞尔曲线箭头，箭头头部用 `marker-end`，手绘风格可增加说明感。

**动画控制：** 每步之间用 fade 过渡，电子箭头用 `stroke-dashoffset` 动画模拟"划出"效果。

**步骤导航：** 提供上一步/下一步/自动播放按钮，当前步骤高亮显示。

### 页面布局
```
┌─────────────────────────────────────────────────────────────┐
│  步骤指示器：● ○ ○  [◀ 上一步] [▶ 下一步] [⏵ 自动播放]      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   反应物结构          弯曲箭头（电子转移）       产物结构     │
│   （SmilesDrawer）   （SVG 动画）              （SmilesDrawer）│
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  当前步骤说明：xxx（文字描述 + 关键词高亮）                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 子类型四：晶体结构

### 技术栈
- **3Dmol.js** — 支持加载 CIF/PDB 格式，渲染晶体单元胞
- **Three.js**（备选，`https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js`）— 自定义晶格线框绘制

### 数据格式

```json
{
  "title": "NaCl 晶体结构",
  "description": "面心立方（FCC）结构，配位数 6",
  "crystal": {
    "system": "cubic",
    "spaceGroup": "Fm3m",
    "a": 5.64,
    "b": 5.64,
    "c": 5.64,
    "alpha": 90,
    "beta": 90,
    "gamma": 90,
    "atoms": [
      { "element": "Na", "x": 0.0, "y": 0.0, "z": 0.0, "color": "#74B9FF", "radius": 1.02 },
      { "element": "Cl", "x": 0.5, "y": 0.0, "z": 0.0, "color": "#55EFC4", "radius": 1.81 }
    ],
    "bonds": [
      { "from": 0, "to": 1, "type": "ionic" }
    ]
  },
  "pdbUrl": "",
  "cifContent": ""
}
```

**`crystal.system` 枚举：** `cubic` / `tetragonal` / `orthorhombic` / `hexagonal` / `trigonal` / `monoclinic` / `triclinic`

### 实现要点

**3Dmol.js 加载 CIF：**
```javascript
// 若有 CIF 数据直接加载
viewer.addModel(cifContent, 'cif');
viewer.setStyle({}, { sphere: { scale: 0.3 }, stick: { radius: 0.1 } });

// 显示单元胞边框
viewer.addUnitCell();
viewer.render();
```

**自定义晶格线框（Three.js）：** 用 `THREE.EdgesGeometry` 绘制单元胞轮廓线，`THREE.InstancedMesh` 批量渲染重复原子。

**交互：** 支持选择显示范围（1×1×1 到 3×3×3 超晶胞），切换球棒/空间填充模式，标注晶格参数。

### 页面布局
```
┌───────────────────────────────┬─────────────────────────────┐
│  3D 晶格查看器                │  右侧信息面板               │
│  （可旋转，显示单元胞边框）    │  空间群：Fm3m               │
│                               │  晶系：立方                 │
│                               │  a=b=c=5.64 Å              │
│                               │  α=β=γ=90°                  │
│                               │  ─────────────────          │
│                               │  [1×1×1] [2×2×2] [3×3×3]   │
│                               │  [球棒] [空间填充] [线框]    │
└───────────────────────────────┴─────────────────────────────┘
```

---

## 子类型五：蛋白质可视化

### 技术栈
- **NGL Viewer**（`https://cdn.jsdelivr.net/npm/ngl@2.0.0-dev.37/dist/ngl.js`）— 专为生物大分子设计，支持 PDB/mmCIF/SDF，WebGL 渲染
- 备选：**3Dmol.js**（同样支持 PDB，API 更简单）

### 数据格式

```json
{
  "title": "溶菌酶结构",
  "description": "一种具有抗菌活性的酶，PDB ID: 1LYZ",
  "proteins": [
    {
      "id": "lysozyme",
      "name": "溶菌酶",
      "pdbId": "1LYZ",
      "source": "rcsb",
      "description": "鸡蛋清溶菌酶，含 129 个氨基酸残基",
      "defaultRepresentation": "cartoon",
      "highlights": [
        { "selection": "35 or 52", "label": "活性位点 (Glu35, Asp52)", "color": "#FF6B6B" }
      ]
    }
  ]
}
```

**`source` 枚举：** `rcsb`（从 RCSB PDB 在线加载）/ `local`（本地 PDB 文件）

**`defaultRepresentation` 枚举：** `cartoon`（二级结构卡通）/ `surface`（分子表面）/ `ball+stick`（球棒）/ `ribbon`（色带）

### 实现要点

**NGL Viewer 加载 PDB：**
```javascript
const stage = new NGL.Stage('viewer-container', { backgroundColor: '#0d1117' });

// 从 RCSB 在线加载（自动拼接 URL）
stage.loadFile(`rcsb://${pdbId}`, { defaultRepresentation: false })
  .then(component => {
    // 卡通表示（按二级结构着色）
    component.addRepresentation('cartoon', { colorScheme: 'sstruc' });
    // 高亮活性位点
    component.addRepresentation('ball+stick', {
      sele: '35 or 52',
      color: '#FF6B6B'
    });
    stage.autoView();
  });
```

**表示方式切换：** 提供按钮切换 cartoon / surface / ball+stick / ribbon。

**活性位点标注：** 用 `addRepresentation('label')` 在 3D 空间中添加残基标签。

**配体展示：** 若 PDB 包含小分子配体，单独渲染为 ball+stick 并高亮。

### 页面布局
```
┌───────────────────────────────┬─────────────────────────────┐
│  NGL 3D 查看器                │  右侧控制面板               │
│  （可旋转/缩放/平移）          │  PDB ID + 蛋白质名          │
│                               │  来源 + 分辨率              │
│                               │  ─────────────────          │
│                               │  表示方式：                 │
│                               │  [卡通] [表面] [球棒] [色带] │
│                               │  ─────────────────          │
│                               │  着色方案：                 │
│                               │  [二级结构] [链] [元素]      │
│                               │  ─────────────────          │
│                               │  高亮区域列表               │
│                               │  ● 活性位点 Glu35, Asp52    │
└───────────────────────────────┴─────────────────────────────┘
```

---

## 通用配色方案

**化合物类型（合成路线图）：**
- 起始原料：`#4A90D9`（蓝）
- 试剂：`#7B68EE`（紫）
- 中间体：`#F5A623`（橙）
- 目标产物：`#52C41A`（绿）

**元素配色（CPK 标准）：**
- C：`#ffffff`（深色背景）/ `#333333`（浅色背景）
- O：`#FF6B6B`，N：`#74B9FF`，S：`#FFD700`，P：`#FFA07A`
- F：`#55EFC4`，Cl：`#81ECEC`，Br：`#A29BFE`，I：`#636E72`

**背景：**
- 深色主题：`#0d1117`（推荐，减少视觉疲劳）
- 浅色主题：`#f5f6fa`

---

## 数据采集说明（供数据 Agent 参考）

| 子类型 | 数据来源 | 关键搜索策略 |
|--------|---------|------------|
| 合成路线图 | 有机化学教材、SciFinder、Reaxys | 搜索"[药物名] synthesis" + "total synthesis" |
| 分子结构 | PubChem（SMILES）、ChemSpider | 搜索 CAS 号或化合物名获取 SMILES |
| 反应机理 | 有机化学教材、ChemTube3D | 搜索反应名称 + "mechanism" |
| 晶体结构 | CCDC（剑桥晶体数据库）、ICSD | 搜索化合物名 + "crystal structure" + CIF |
| 蛋白质可视化 | RCSB PDB | 直接用 PDB ID，NGL Viewer 可在线加载 |

---

## 技术文档参考

> **重要**：遇到库 API 问题时，优先查阅以下参考文档，而不是盲目猜测或搜索。

| 库 | 文档路径 | 用途 |
|----|---------|------|
| SmilesDrawer v2 | `docs/smilesdrawer-reference.md` | parse/draw API、配置选项、已知问题 |
| 3Dmol.js | `docs/3dmol-reference.md` | 支持的格式、样式配置、加载方式 |
| NGL Viewer | `docs/ngl-reference.md` | Stage API、表示方式、选择器语法 |
| D3.js v7 | `docs/d3-reference.md` | zoom、forceSimulation、tree 布局 |
| PubChem REST API | `docs/pubchem-api-reference.md` | SDF 获取、CID 查询、速率限制 |

**使用方式**：子 agent 编码前先读取相关文档，确保 API 调用方式正确。
