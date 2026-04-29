# 3Dmol.js 技术参考文档

## 目录

1. [概述](#概述)
2. [CDN 和版本](#cdn-和版本)
3. [支持的文件格式](#支持的文件格式)
4. [加载分子数据的方式](#加载分子数据的方式)
5. [样式配置](#样式配置)
6. [交互 API](#交互-api)
7. [参考资源](#参考资源)

---

## 概述

3Dmol.js 是一个基于 WebGL 的面向对象 JavaScript 库，用于在线分子可视化，无需 Java 插件！

**主要特性：**
- 支持多种分子文件格式
- 并行化分子表面计算
- 多种可视化样式（sphere、stick、line、cross、cartoon、surface）
- 基于原子属性的选择和样式设置
- 可点击的交互功能
- 几何形状（包括球体和箭头）

**官方引用：**
> Nicholas Rego and David Koes
> 3Dmol.js: molecular visualization with WebGL
> Bioinformatics (2015) 31 (8): 1322-1324 doi:10.1093/bioinformatics/btu829

---

## CDN 和版本

### 最新稳定版本

**推荐 CDN（2.5.4）：**

```html
<!-- jsDelivr CDN - 指定版本 -->
<script src="https://cdn.jsdelivr.net/npm/3dmol@2.5.4/build/3Dmol-min.js"></script>

<!-- jsDelivr CDN - 始终使用最新版本 -->
<script src="https://cdn.jsdelivr.net/npm/3dmol@latest/build/3Dmol-min.js"></script>

<!-- cdnjs CDN（注意：必须指定版本） -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/3Dmol/2.0.1/3Dmol-min.js"></script>
```

### 官方托管

```html
<!-- 官方最新版本（经常更新） -->
<script src="https://3Dmol.org/build/3Dmol-min.js"></script>

<!-- 未压缩版本（用于调试） -->
<script src="https://3Dmol.org/build/3Dmol.js"></script>
```

### NPM 安装

```bash
npm install 3dmol
# 或
yarn add 3dmol
```

**ES6 导入方式：**

```javascript
import("3dmol/build/3Dmol.js").then(($3Dmol) => {
  console.log($3Dmol);
  // 在这里使用 $3Dmol
});

// 或使用 flat imports（如果配置了 expose-loader）
import * as $3Dmol from '3dmol/build/3Dmol.js';
```

---

## 支持的文件格式

### ✅ 支持的格式

以下格式可通过 `addModel(data, format)` 加载：

| 格式代码 | 格式名称 | 说明 | 数据结构要求 |
|---------|---------|------|-------------|
| `pdb` | Protein Data Bank | 蛋白质数据库格式 | 标准 PDB 文本格式 |
| `sdf` | Structure Data File | 结构数据文件 | 标准 SDF/MOL 格式 |
| `mol2` | Tripos Mol2 | Tripos 分子格式 | 标准 Mol2 文本格式 |
| `xyz` | Cartesian Coordinates | 笛卡尔坐标格式 | 原子坐标列表 |
| `cube` | Gaussian Cube | 高斯体积数据 | 包含体积数据的 Cube 文件 |
| `pqr` | PQR Format | PDB 衍生格式（含电荷和半径） | 空格分隔的 PDB 变体 |
| `cif` | mmCIF | 大分子晶体信息文件 | mmCIF 标准格式 |
| `gro` | GROMACS | GROMACS 坐标文件 | GROMACS 格式 |
| `prmtop` | AMBER Topology | AMBER 拓扑文件 | AMBER 参数文件 |
| `vasp` | VASP | VASP 格式 | VASP 结构文件 |
| `mmtf` | MMTF | 大分子传输格式（二进制） | 二进制 UInt8Array 或 base64 字符串 |
| `bcif` | Binary CIF | 二进制 CIF 格式 | 二进制 UInt8Array 或 base64 字符串 |
| `cdjson` | ChemDoodle JSON | ChemDoodle JSON 格式 | JSON 格式（注意：非通用化学 JSON） |

### ❌ 不支持的格式

以下格式**不能**直接通过 `addModel()` 加载：

| 格式代码 | 格式名称 | 说明 | 替代方案 |
|---------|---------|------|----------|
| `smi` / `smiles` | SMILES | SMILES 字符串格式 | **转换为 SDF 或 Mol2** |
| `inchi` | InChI | InChI 字符串 | 转换为支持格式 |
| `mol` | MDL Mol | MDL Mol 文件 | 使用 SDF 格式（包含 Mol） |

**SMILES 转换建议：**
- 使用 PubChem API 或 Cactus 服务从 SMILES 获取 3D 坐标
- 使用 RDKit（Python）将 SMILES 转换为 SDF/Mol2
- 使用 Open Babel 命令行工具转换

**示例（从 SMILES 获取 SDF）：**

```javascript
// 通过 PubChem API
const cid = '2519'; // 咖啡因的 CID
const url = `https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/${cid}/SDF`;
$3Dmol.get(url, function(sdfData) {
  viewer.addModel(sdfData, 'sdf');
  viewer.zoomTo();
  viewer.render();
});
```

### 解析器选项（ParserOptionsSpec）

不同的文件格式支持不同的解析选项：

**PDB 格式选项：**

```javascript
viewer.addModel(pdbData, 'pdb', {
  keepH: false,              // 是否保留氢原子（默认：false）
  noSecondaryStructure: false, // 是否跳过二级结构计算
  assignbonds: true,         // 是否计算隐式键（默认：true）
  altLoc: '*'                // 选择哪个交替位置（'*' 表示全部）
});
```

---

## 加载分子数据的方式

### 1. `addModel()` - 基础方法

创建并添加单个模型到查看器。

**语法：**

```javascript
let model = viewer.addModel(data, format, options);
```

**参数：**
- `data` (string): 分子数据字符串
- `format` (string): 数据格式（'pdb', 'sdf', 'mol2', 'xyz', 'pqr', 'cube' 等）
- `options` (ParserOptionsSpec, 可选): 格式相关选项

**返回值：**
- `GLModel` 对象

**示例：**

```javascript
// 从字符串加载 SDF
let sdfString = `
     RDKit          3D

  5  4  0  0  0  0  0  0  0  0999 V2000
    0.0000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    1.0000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    1.5000    0.8660    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    0.5000    0.8660    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    0.0000    0.0000    1.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  1  0
  2  3  1  0
  3  4  1  0
  4  1  1  0
M  END
`;

let model = viewer.addModel(sdfString, 'sdf');
viewer.setStyle({stick: {}});
viewer.zoomTo();
viewer.render();
```

### 2. `addModels()` - 多模型文件

从包含多个分子的文件中创建多个独立模型。

**语法：**

```javascript
let models = viewer.addModels(data, format);
```

**返回值：**
- `Array<GLModel>` - 模型数组

**示例：**

```javascript
// 加载包含多个分子的 SDF 文件
$3Dmol.get('multiple_compounds.sdf', function(data) {
  let models = viewer.addModels(data, 'sdf');
  models.forEach((model, index) => {
    model.setStyle({stick: {colorscheme: 'greenCarbon'}});
  });
  viewer.zoomTo();
  viewer.render();
});
```

### 3. `addAsOneMolecule()` - 合并为单模型

从多模型文件中将所有原子添加到一个模型中。

**语法：**

```javascript
let model = viewer.addAsOneMolecule(data, format);
```

**示例：**

```javascript
$3Dmol.get('multiple.sdf', function(data) {
  viewer.addAsOneMolecule(data, 'sdf');
  viewer.setStyle({stick: {}});
  viewer.zoomTo();
  viewer.render();
});
```

### 4. `addModelsAsFrames()` - 作为动画帧

从多模型文件创建动画帧。

**语法：**

```javascript
let model = viewer.addModelsAsFrames(data, format);
```

**示例：**

```javascript
$3Dmol.get('trajectory.xyz', function(data) {
  viewer.addModelsAsFrames(data, 'xyz');
  viewer.setStyle({stick: {colorscheme: 'magentaCarbon'}});

  // 播放动画
  viewer.animate({
    loop: 'forward',
    reps: 1,
    interval: 100
  });

  viewer.zoomTo();
  viewer.render();
});
```

### 5. `$3Dmol.download()` - 从 PDB/PubChem 加载

从在线数据库直接下载分子结构。

**语法：**

```javascript
let model = $3Dmol.download(query, viewer, options, callback);
```

**参数：**
- `query` (string): 查询字符串，必须以 "pdb:" 或 "cid:" 开头
  - `"pdb:1UBQ"` - 从 PDB 加载
  - `"cid:2519"` - 从 PubChem 加载
  - `"mmtf:2ll5"` - 以 MMTF 格式加载
- `viewer` (GLViewer): 目标查看器
- `options` (Object, 可选):
  - `format`: 文件格式（默认 'pdb'）
  - `pdbUri`: PDB 文件 URI（默认 'http://www.rcsb.org/pdb/files/'）
  - `onemol`: 是否合并为单分子
  - `multimodel`: 是否作为多模型处理
- `callback` (function, 可选): 加载完成后的回调函数

**返回值：**
- 如果提供了 callback：返回 `GLModel`
- 如果未提供 callback：返回 `Promise`

**示例：**

```javascript
// 从 PDB 加载
let viewer = $3Dmol.createViewer('gldiv', {
  backgroundColor: 'white'
});

$3Dmol.download('pdb:4UAA', viewer, {}, function(model) {
  viewer.setStyle({cartoon: {color: 'spectrum'}});
  viewer.zoomTo();
  viewer.render();
});

// 从 PubChem 加载
$3Dmol.download('cid:2519', viewer, {}, function(model) {
  viewer.setStyle({stick: {}});
  viewer.zoomTo();
  viewer.render();
});

// 使用 Promise（无 callback）
$3Dmol.download('pdb:1UBQ', viewer)
  .then(model => {
    model.setStyle({cartoon: {}});
    viewer.zoomTo();
    viewer.render();
  });
```

### 6. `$3Dmol.get()` - 从 URL 加载

从任意 URL 获取分子数据。

**语法：**

```javascript
$3Dmol.get(url, callback);
```

**示例：**

```javascript
$3Dmol.get('https://example.com/molecule.sdf', function(data) {
  viewer.addModel(data, 'sdf');
  viewer.setStyle({stick: {}});
  viewer.zoomTo();
  viewer.render();
});
```

---

## 样式配置

### AtomStyleSpec 接口

`setStyle()` 方法接受 `AtomStyleSpec` 对象，定义如何渲染原子和键。

**基本结构：**

```javascript
viewer.setStyle(selection, styleSpec);
```

### 支持的样式类型

| 样式 | 类型 | 说明 |
|------|------|------|
| `line` | LineStyleSpec | 将键绘制为线条 |
| `stick` | StickStyleSpec | 将键绘制为圆柱体 |
| `sphere` | SphereStyleSpec | 将原子绘制为球体 |
| `cross` | CrossStyleSpec | 将原子绘制为交叉线（星形） |
| `cartoon` | CartoonStyleSpec | 绘制二级结构卡通图 |
| `surface` | SurfaceStyleSpec | 绘制分子表面 |

### 1. Line Style（线条）

**LineStyleSpec 参数：**

```javascript
viewer.setStyle({line: {
  hidden: false,              // boolean - 是否隐藏
  color: 'red',               // ColorSpec - 固定颜色
  colorscheme: 'greenCarbon', // ColorschemeSpec - 颜色方案
  colorfunc: null,            // function - 自定义颜色函数
  linewidth: 1.0,             // number - 线宽
  opacity: 1.0                // number - 不透明度（0-1）
}});
```

**示例：**

```javascript
viewer.setStyle({line: {color: 'blue', linewidth: 2.0}});
```

### 2. Cross Style（交叉线）

**CrossStyleSpec 参数：**

```javascript
viewer.setStyle({cross: {
  hidden: false,              // boolean - 是否隐藏
  color: 'black',             // ColorSpec - 固定颜色
  colorscheme: 'default',     // ColorschemeSpec - 颜色方案
  colorfunc: null,            // function - 自定义颜色函数
  linewidth: 1.0,             // number - 线宽
  radius: 0.5,                // number - 交叉线半径
  scale: 1.0,                 // number - 缩放因子
  opacity: 1.0                // number - 不透明度（0-1）
}});
```

**示例：**

```javascript
viewer.setStyle({cross: {radius: 1.0, linewidth: 2.0, color: 'red'}});
```

### 3. Stick Style（棍棒）

**StickStyleSpec 参数：**

```javascript
viewer.setStyle({stick: {
  hidden: false,              // boolean - 是否隐藏
  color: 'gray',              // ColorSpec - 固定颜色
  colorscheme: 'element',     // ColorschemeSpec - 颜色方案
  colorfunc: null,            // function(atom) - 自定义颜色函数
  radius: 0.25,               // number - 棍棒半径
  opacity: 1.0,               // number - 不透明度（0-1）
  singleBonds: false,         // boolean - 是否将所有键显示为单键
  showNonBonded: false,       // boolean - 是否将非键合原子显示为球体
  doubleBondScaling: 0.4,     // number - 双键缩放因子
  tripleBondScaling: 0.25,    // number - 三键缩放因子
  dashedBonds: false,         // boolean - 是否将键显示为虚线
  dashedBondConfig: {         // DashedBondSpec - 虚线配置
    dashLength: 0.3,
    gapLength: 0.1
  }
}});
```

**示例：**

```javascript
// 基础棍棒样式
viewer.setStyle({stick: {}});

// 自定义棍棒样式
viewer.setStyle({stick: {
  radius: 0.5,
  colorscheme: 'magentaCarbon',
  singleBonds: true
}});

// 虚线键
viewer.setStyle({stick: {
  dashedBonds: true,
  dashedBondConfig: {
    dashLength: 0.3,
    gapLength: 0.1
  }
}});
```

### 4. Sphere Style（球体）

**SphereStyleSpec 参数：**

```javascript
viewer.setStyle({sphere: {
  hidden: false,              // boolean - 是否隐藏
  color: 'blue',              // ColorSpec - 固定颜色
  colorscheme: 'Jmol',        // ColorschemeSpec - 颜色方案
  colorfunc: null,            // function(atom) - 自定义颜色函数
  radius: 1.5,                // number - 固定半径
  scale: 1.0,                 // number - 缩放范德华半径
  opacity: 1.0                // number - 不透明度（0-1）
}});
```

**示例：**

```javascript
// 使用固定半径
viewer.setStyle({sphere: {radius: 1.0}});

// 使用范德华半径缩放
viewer.setStyle({sphere: {scale: 0.5, colorscheme: 'Jmol'}});
```

### 5. Cartoon Style（卡通图）

用于蛋白质和核酸的二级结构可视化。

**CartoonStyleSpec 参数：**

```javascript
viewer.setStyle({cartoon: {
  hidden: false,              // boolean - 是否隐藏
  color: 'spectrum',          // ColorSpec - 固定颜色
  colorscheme: 'chain',       // ColorschemeSpec - 颜色方案
  colorfunc: null,            // function(atom) - 自定义颜色函数
  style: 'trace',             // 'trace' | 'oval' | 'rectangle' | 'parabola' | 'edged'
  thickness: 0.4,             // number - 厚度
  width: 1.0,                 // number - 宽度
  opacity: 1.0,               // number - 不透明度（0-1）
  ribbon: false,              // boolean - 是否显示为带状
  tubes: false,               // boolean - 是否显示为管状
  arrows: false,              // boolean - β折叠是否显示箭头
  opacity: 1.0                // number - 不透明度
}});
```

**示例：**

```javascript
// 基础卡通图
viewer.setStyle({cartoon: {}});

// 按链着色
viewer.setStyle({cartoon: {colorscheme: 'chain'}});

// 按温度因子着色（渐变）
viewer.setStyle({cartoon: {
  colorscheme: {
    prop: 'b',
    gradient: 'roygb',
    min: 0,
    max: 50
  }
}});

// 自定义样式
viewer.setStyle({cartoon: {
  style: 'parabola',
  thickness: 0.8,
  color: 'purple',
  arrows: true
}});
```

### 6. 组合样式

可以在一个选择中组合多个样式。

**示例：**

```javascript
// 球棍模型
viewer.setStyle({stick: {}, sphere: {scale: 0.3}});

// 卡通图 + 棍棒（针对配体）
viewer.setStyle({cartoon: {}});
viewer.setStyle({hetflag: true}, {stick: {}, sphere: {scale: 0.5}});
```

---

## 颜色方案（ColorschemeSpec）

### 内置颜色方案

3Dmol.js 提供了多种内置颜色方案：

| 方案名称 | 说明 | 适用场景 |
|---------|------|---------|
| `default` | 默认元素着色 | 通用 |
| `Jmol` | Jmol 元素默认颜色 | 与 Jmol 一致 |
| `rasmol` | RasMol 默认元素颜色 | 与 RasMol 一致 |
| `greenCarbon` | 绿色碳 | 强调碳原子 |
| `cyanCarbon` | 青色碳 | 强调碳原子 |
| `magentaCarbon` | 洋红色碳 | 强调碳原子 |
| `purpleCarbon` | 紫色碳 | 强调碳原子 |
| `whiteCarbon` | 白色碳 | 强调碳原子 |
| `orangeCarbon` | 橙色碳 | 强调碳原子 |
| `yellowCarbon` | 黄色碳 | 强调碳原子 |
| `blueCarbon` | 蓝色碳 | 强调碳原子 |
| `chain` | 按链着色 | 多链蛋白 |
| `chainHetatm` | 按链着色（包括杂原子） | 多链蛋白 |
| `ssPyMol` | PyMol 二级结构着色 | 二级结构 |
| `ssJmol` | Jmol 二级结构着色 | 二级结构 |
| `amino` | 氨基酸着色 | 蛋白质 |
| `shapely` | Shapely 氨基酸着色 | 蛋白质 |
| `nucleic` | 核酸着色 | DNA/RNA |

**使用示例：**

```javascript
// 使用内置颜色方案
viewer.setStyle({stick: {colorscheme: 'Jmol'}});
viewer.setStyle({cartoon: {colorscheme: 'chain'}});
viewer.setStyle({sphere: {colorscheme: 'greenCarbon'}});
```

### 渐变颜色方案

基于原子属性的渐变着色。

**内置渐变类型：**

| 渐变 | 说明 |
|------|------|
| `rwb` | 红-白-蓝渐变（支持中点） |
| `roygb` | 彩虹渐变 |
| `sinebow` | 饱和度更好的彩虹渐变 |
| `linear` | 在指定颜色之间线性映射 |

**渐变语法：**

```javascript
viewer.setStyle({cartoon: {
  colorscheme: {
    prop: 'b',         // 原子属性（如温度因子 'b'）
    gradient: 'roygb', // 渐变类型
    min: 0,            // 最小值
    max: 50            // 最大值
  }
}});

// 红白蓝渐变（带中点）
viewer.setStyle({sphere: {
  colorscheme: {
    prop: 'b',
    gradient: 'rwb',
    min: -10,
    mid: 0,            // 中点值（白色）
    max: 10
  }
}});
```

### 自定义颜色函数

通过 `colorfunc` 完全自定义颜色逻辑。

**示例：**

```javascript
// 根据残基索引交替着色
var colorAsSnake = function(atom) {
  return atom.resi % 2 ? 'white' : 'green';
};

viewer.setStyle({chain: 'A'}, {
  cartoon: {colorfunc: colorAsSnake}
});
```

### 自定义元素颜色映射

通过 `colorscheme.map` 自定义属性到颜色的映射。

**示例：**

```javascript
viewer.setStyle({}, {
  stick: {
    colorscheme: {
      prop: 'elem',
      map: {
        'C': 'green',
        'N': 'blue',
        'O': 'red',
        'H': 'white'
      }
    }
  }
});
```

---

## 原子选择（AtomSelectionSpec）

`setStyle()`、`addStyle()` 等方法的第一个参数是 `AtomSelectionSpec`，用于选择要应用样式的原子。

### 基本属性

```javascript
viewer.setStyle(selection, style);
```

**常用选择属性：**

| 属性 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `elem` | string | 元素符号 | `{elem: 'C'}` |
| `atom` | string | 原子名称 | `{atom: 'CA'}` |
| `resn` | string | 残基名称 | `{resn: 'ALA'}` |
| `resi` | number/string/Array | 残基序号 | `{resi: [1, 5, "10-15"]}` |
| `chain` | string | 链标识符 | `{chain: 'A'}` |
| `model` | GLModel/number | 模型对象或索引 | `{model: 0}` |
| `bonds` | number | 键的数量 | `{bonds: 0}` （非键合原子） |
| `hetflag` | boolean | 是否为杂原子 | `{hetflag: true}` |
| `ss` | string | 二级结构 | `{ss: 'h'}` （螺旋） |
| `index` | number/Array | 原子索引 | `{index: [0, 1, 2]}` |

### 逻辑操作

**invert（反向选择）：**

```javascript
// 选择除了链 A 以外的所有原子
viewer.setStyle({chain: 'A', invert: true}, {sphere: {}});
```

**byres（按残基扩展）：**

```javascript
// 选择包含指定原子的整个残基
viewer.setStyle({resn: 'PMP', byres: true}, {stick: {}});
```

**expand（按距离扩展）：**

```javascript
// 选择 5 Å 范围内的所有原子
viewer.setStyle({resn: 'STI', expand: 5}, {stick: {}});
```

**within（在另一选择的距离内）：**

```javascript
// 选择在配体 5 Å 范围内的蛋白质原子
viewer.setStyle({
  within: {
    distance: 5,
    sel: {resn: 'STI'}
  }
}, {cartoon: {}});
```

**and / or（逻辑组合）：**

```javascript
// AND：链 A 且残基 10-20
viewer.setStyle({
  and: [
    {chain: 'A'},
    {resi: '10-20'}
  ]
}, {cartoon: {}});

// OR：链 A 或链 B
viewer.setStyle({
  or: [
    {chain: 'A'},
    {chain: 'B'}
  ]
}, {stick: {}});
```

**not（否定）：**

```javascript
// 选择所有非碳原子
viewer.setStyle({not: {elem: 'C'}}, {sphere: {}});
```

### predicate（自定义谓词函数）

使用函数进行复杂选择。

**示例：**

```javascript
// 选择所有温度因子 > 50 的原子
viewer.setStyle({
  predicate: function(atom) {
    return atom.b > 50;
  }
}, {sphere: {color: 'red'}});
```

### 组合示例

```javascript
// 选择水分子
viewer.setStyle({bonds: 0}, {sphere: {radius: 0.5}});

// 选择特定残基范围
viewer.setStyle({resi: ['91-95', '42-50']}, {cartoon: {color: 'green'}});

// 选择配体及其周围 5 Å 的残基
viewer.setStyle({resn: 'STI', byres: true, expand: 5}, {stick: {colorscheme: 'greenCarbon'}});
```

---

## 交互 API

### 基础方法

#### `zoomTo(sel, animationDuration, fixedPath)`

调整相机视图以适应选定的原子（居中并缩放）。

**参数：**
- `sel` (AtomSelectionSpec, 可选): 要缩放到的原子选择，默认为所有原子
- `animationDuration` (number, 可选): 动画持续时间（毫秒）
- `fixedPath` (boolean, 可选): 是否固定动画路径

**示例：**

```javascript
// 缩放到所有原子
viewer.zoomTo();

// 缩放到特定选择，动画 1 秒
viewer.zoomTo({chain: 'A'}, 1000);

// 缩放到配体
viewer.zoomTo({resn: 'STI'});
```

#### `center(sel, animationDuration, fixedPath)`

重新居中查看器（不缩放）。

**示例：**

```javascript
// 居中到特定残基
viewer.center({resn: 'ALA'});
```

#### `render(callback)`

重新渲染场景。

**参数：**
- `callback` (function, 可选): 渲染完成后的回调

**示例：**

```javascript
viewer.setStyle({cartoon: {}});
viewer.zoomTo();
viewer.render();
```

#### `resize()`

处理视口调整大小。

**示例：**

```javascript
// 在窗口调整大小时调用
window.addEventListener('resize', function() {
  viewer.resize();
  viewer.render();
});
```

#### `setBackgroundColor(color, opacity)`

设置背景颜色。

**参数：**
- `color` (ColorSpec): 颜色（十六进制数或颜色名称）
- `opacity` (number, 可选): 不透明度（0-1）

**示例：**

```javascript
viewer.setBackgroundColor('white');
viewer.setBackgroundColor(0x000000);  // 黑色
viewer.setBackgroundColor('lightgray', 1.0);
```

#### `setViewStyle(style)`

设置查看器整体样式。

**示例：**

```javascript
// 添加轮廓效果
viewer.setViewStyle({style: 'outline'});
```

### 交互功能

#### `setClickable(sel, clickable, callback)`

设置原子是否可点击。

**参数：**
- `sel` (AtomSelectionSpec): 原子选择
- `clickable` (boolean): 是否可点击
- `callback` (function): 点击回调函数 `function(atom, viewer, event)`

**示例：**

```javascript
// 使所有原子可点击
viewer.setClickable({}, true, function(atom, viewer, event) {
  console.log('Clicked atom:', atom.elem, 'at', atom.x, atom.y, atom.z);
  console.log('Residue:', atom.resn, atom.resi);
  console.log('Chain:', atom.chain);

  // 改变点击原子的颜色
  atom.color = 0xFF0000;  // 红色
  viewer.render();
});

// 仅使配体可点击
viewer.setClickable({resn: 'STI'}, true, function(atom, viewer, event) {
  alert('Ligand atom: ' + atom.elem);
});
```

#### `setHoverable(sel, hoverable, hover_callback, unhover_callback)`

设置原子是否可悬停。

**参数：**
- `sel` (AtomSelectionSpec): 原子选择
- `hoverable` (boolean): 是否可悬停
- `hover_callback` (function): 悬停回调
- `unhover_callback` (function): 取消悬停回调

**示例：**

```javascript
viewer.setHoverable({}, true,
  function(atom, viewer, event, container) {
    // 悬停时改变颜色
    atom.color = 0x00FF00;
    viewer.render();

    // 显示标签
    console.log('Hovering:', atom.elem);
  },
  function(atom, viewer) {
    // 取消悬停时恢复颜色
    atom.color = atom.defaultColor;
    viewer.render();
  }
);
```

#### `enableContextMenu(sel, contextMenuEnabled)`

启用/禁用右键菜单。

**示例：**

```javascript
viewer.enableContextMenu({}, true);
```

### 标签

#### `addLabel(text, options, sel, noshow)`

添加文本标签。

**参数：**
- `text` (string): 标签文本
- `options` (LabelSpec): 标签样式
  - `font`: 字体（如 'sans-serif'）
  - `fontSize`: 字体大小
  - `fontColor`: 字体颜色
  - `fontOpacity`: 字体不透明度
  - `borderThickness`: 边框厚度
  - `borderColor`: 边框颜色
  - `borderOpacity`: 边框不透明度
  - `backgroundColor`: 背景颜色
  - `backgroundOpacity`: 背景不透明度
  - `position`: 位置 `{x, y, z}`
  - `inFront`: 是否在最前面
  - `showBackground`: 是否显示背景
- `sel` (AtomSelectionSpec, 可选): 将标签定位到选择的中心
- `noshow` (boolean, 可选): 是否立即显示

**示例：**

```javascript
// 在指定位置添加标签
viewer.addLabel('Active Site', {
  position: {x: 10.5, y: 5.0, z: 3.2},
  backgroundColor: 'black',
  backgroundOpacity: 0.8,
  fontColor: 'white',
  fontSize: 14
});

// 添加到原子选择中心
viewer.addLabel('Ligand', {
  font: 'Arial',
  fontSize: 18,
  fontColor: 'white',
  backgroundColor: 'blue',
  backgroundOpacity: 0.7
}, {resn: 'STI'});

viewer.render();
```

#### `removeLabel(label)`

移除标签。

**示例：**

```javascript
let label = viewer.addLabel('Test', {position: {x:0, y:0, z:0}});
// 稍后移除
viewer.removeLabel(label);
```

### 其他有用方法

#### `getModel(id)`

获取模型对象。

```javascript
let model = viewer.getModel();  // 获取最后添加的模型
let model = viewer.getModel(0); // 获取第一个模型
```

#### `getCanvas()`

获取底层 canvas 元素。

```javascript
let canvas = viewer.getCanvas();
```

#### `exportJSON(includeStyles, modelID)`

导出为 ChemDoodle 兼容 JSON。

```javascript
let json = viewer.exportJSON(true);  // 包含样式
```

#### `clear()`

清除场景中的所有对象。

```javascript
viewer.clear();
```

#### `rotate(angle, axis, animationDuration, fixedPath)`

旋转视图。

```javascript
viewer.rotate(90, 'x');  // 绕 X 轴旋转 90 度
viewer.rotate(45, {x:1, y:1, z:1}, 1000);  // 绕自定义轴旋转，动画 1 秒
```

#### `spin(axis, speed)`

连续旋转。

```javascript
viewer.spin('y', 1);  // 绕 Y 轴旋转
viewer.spin(false);   // 停止旋转
```

---

## 参考资源

### 官方文档

- **官方主页**: https://3dmol.csb.pitt.edu/
- **API 文档**: https://3dmol.csb.pitt.edu/doc/index.html
- **GLViewer 类**: https://3dmol.csb.pitt.edu/doc/GLViewer.html
- **GLModel 类**: https://3dmol.csb.pitt.edu/doc/GLModel.html
- **教程**: https://3dmol.csb.pitt.edu/doc/tutorial-code.html

### GitHub

- **仓库**: https://github.com/3dmol/3Dmol.js
- **问题追踪**: https://github.com/3dmol/3Dmol.js/issues

### CDN

- **jsDelivr**: https://cdn.jsdelivr.net/npm/3dmol@latest/
- **cdnjs**: https://cdnjs.com/libraries/3Dmol

### 相关项目

- **py3Dmol**: Python 包装器，用于在 Jupyter notebooks 中使用 3Dmol.js
- **3Dmol.js Server**: 在线分子查看服务

---

## 完整示例

### 示例 1：基础蛋白质可视化

```html
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdn.jsdelivr.net/npm/3dmol@latest/build/3Dmol-min.js"></script>
  <style>
    #viewer {
      width: 600px;
      height: 400px;
      position: relative;
    }
  </style>
</head>
<body>
  <div id="viewer"></div>
  <script>
    let viewer = $3Dmol.createViewer('viewer', {
      backgroundColor: 'white'
    });

    $3Dmol.download('pdb:1UBQ', viewer, {}, function(model) {
      viewer.setStyle({cartoon: {color: 'spectrum'}});
      viewer.zoomTo();
      viewer.render();
    });
  </script>
</body>
</html>
```

### 示例 2：球棍模型 + 交互

```html
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdn.jsdelivr.net/npm/3dmol@latest/build/3Dmol-min.js"></script>
</head>
<body>
  <div id="viewer" style="width: 600px; height: 400px;"></div>
  <script>
    let viewer = $3Dmol.createViewer('viewer', {backgroundColor: 'white'});

    // 从 PubChem 加载咖啡因
    $3Dmol.download('cid:2519', viewer, {}, function(model) {
      // 设置球棍模型
      viewer.setStyle({stick: {radius: 0.2}, sphere: {scale: 0.3}});

      // 添加交互
      viewer.setClickable({}, true, function(atom) {
        alert(`元素: ${atom.elem}\n残基: ${atom.resn}\n坐标: (${atom.x.toFixed(2)}, ${atom.y.toFixed(2)}, ${atom.z.toFixed(2)})`);
      });

      viewer.zoomTo();
      viewer.render();
    });
  </script>
</body>
</html>
```

### 示例 3：蛋白质 + 配体（不同样式）

```javascript
let viewer = $3Dmol.createViewer('viewer', {backgroundColor: 'white'});

$3Dmol.download('pdb:4UAA', viewer, {}, function(model) {
  // 蛋白质：卡通图，按链着色
  viewer.setStyle({cartoon: {colorscheme: 'chain'}});

  // 配体：棍棒 + 球体，绿色碳
  viewer.setStyle({hetflag: true}, {
    stick: {colorscheme: 'greenCarbon', radius: 0.3},
    sphere: {colorscheme: 'greenCarbon', scale: 0.5}
  });

  // 缩放到配体
  viewer.zoomTo({hetflag: true});
  viewer.render();
});
```

### 示例 4：渐变着色（温度因子）

```javascript
let viewer = $3Dmol.createViewer('viewer', {backgroundColor: 'white'});

$3Dmol.download('pdb:1UBQ', viewer, {}, function(model) {
  // 按温度因子着色
  viewer.setStyle({cartoon: {
    colorscheme: {
      prop: 'b',
      gradient: 'rwb',
      min: 0,
      mid: 30,
      max: 60
    }
  }});

  viewer.zoomTo();
  viewer.render();
});
```

---

**文档版本**: 基于官方文档整理（访问日期：2026-03-23）
**3Dmol.js 版本**: 2.5.4
**整理者**: Claude Code Agent
