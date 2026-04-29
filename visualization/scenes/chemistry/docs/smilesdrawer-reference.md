# SmilesDrawer v2 技术参考

## 版本信息

- **当前 npm 版本**: v2.2.0
- **推荐稳定版本**: v2.1.7
- **CDN**: `https://cdn.jsdelivr.net/npm/smiles-drawer@2.1.7/dist/smiles-drawer.min.js`
- **NPM 安装**: `npm install smiles-drawer@2.1.7`
- **仓库地址**: https://github.com/reymond-group/smilesDrawer
- **许可证**: MIT

## 核心类

### SmilesDrawer.parse()

解析 SMILES 字符串为分子结构数据。

**签名**
```javascript
SmilesDrawer.parse(smiles, onSuccess, onError)
```

**参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `smiles` | String | 是 | SMILES 字符串（如 `"C1CCCCC1"` 表示环己烷） |
| `onSuccess` | Function | 是 | 解析成功回调，接收解析树 (tree) 作为参数 |
| `onError` | Function | 否 | 解析失败回调，接收错误信息作为参数 |

**示例**
```javascript
SmilesDrawer.parse('C1CCCCC1', function(tree) {
  // 解析成功，tree 是分子结构数据
  drawer.draw(tree, 'canvas-id', 'light');
}, function(err) {
  console.error('解析失败:', err);
});
```

### SmilesDrawer.SvgDrawer

用于将分子结构渲染为 SVG 矢量图。

**构造函数**
```javascript
new SmilesDrawer.SvgDrawer(options)
```

**参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `options` | Object | 否 | 配置选项对象，详见"配置选项"章节 |
| `clear` | Boolean | 否 | 是否清除之前的内容，默认为 `true` |

**draw() 方法**

```javascript
drawer.draw(data, target, themeName, weights, infoOnly, highlight_atoms, weightsNormalized)
```

**参数说明**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `data` | Object | - | **必填**。由 `SmilesDrawer.parse()` 返回的解析树 |
| `target` | String \| SVGElement | - | **必填**。SVG 元素的 ID 或 SVGElement 对象。如为 `null` 或 `'svg'`，将自动创建 SVG 元素 |
| `themeName` | String | `'light'` | 主题名称。内置主题：`'light'` 和 `'dark'` |
| `weights` | Number[] \| null | `null` | **v2.1+**。每个原子的权重数组，用于高亮显示。长度必须等于重原子数 |
| `infoOnly` | Boolean | `false` | 仅计算分子属性（环数、HAC 等）而不绘制结构 |
| `highlight_atoms` | Array | `[]` | **v2.1+**。高亮原子数组，格式为 `[[atomClass, color], ...]` |
| `weightsNormalized` | Boolean | `false` | 权重是否已归一化 |

**返回值**: SVGElement（SVG 元素）

**示例**
```javascript
// 基本用法
const drawer = new SmilesDrawer.SvgDrawer({ width: 300, height: 200 });
SmilesDrawer.parse('CCCO', function(tree) {
  drawer.draw(tree, 'svg-container', 'light');
});

// 使用权重高亮（v2.1+）
const weights = [0.1, 0.5, 0.8, 0.3]; // 每个原子的权重
SmilesDrawer.parse('CCCO', function(tree) {
  drawer.draw(tree, svgElement, 'light', weights);
});

// 高亮特定原子
const highlights = [[1, '#ff0000'], [3, '#00ff00']];
SmilesDrawer.parse('c1ccccc1', function(tree) {
  drawer.draw(tree, 'svg-output', 'dark', null, false, highlights);
});
```

### SmilesDrawer.Drawer（Canvas 版本）

用于将分子结构渲染为 Canvas 位图。

**构造函数**
```javascript
new SmilesDrawer.Drawer(options)
```

**draw() 方法**
```javascript
drawer.draw(data, target, themeName, infoOnly)
```

**参数说明**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `data` | Object | - | 由 `SmilesDrawer.parse()` 返回的解析树 |
| `target` | String \| HTMLCanvasElement | - | Canvas 元素的 ID 或 HTMLCanvasElement 对象 |
| `themeName` | String | `'light'` | 主题名称 |
| `infoOnly` | Boolean | `false` | 仅计算属性而不绘制 |

**SvgDrawer vs Drawer 对比**

| 特性 | SvgDrawer | Drawer |
|------|-----------|--------|
| **输出格式** | SVG 矢量图 | Canvas 位图 |
| **缩放性** | 无损缩放 | 有损缩放 |
| **文件大小** | 较小（简单结构） | 固定大小 |
| **CSS 样式** | 支持 | 不支持 |
| **打印/导出** | 高质量 | 依赖分辨率 |
| **性能** | 较慢（复杂结构） | 较快 |
| **适用场景** | 打印、出版、高质量展示 | 大量结构渲染、交互式应用 |

**API 方法**

| 方法 | 描述 | 返回值 |
|------|------|--------|
| `getMolecularFormula()` | 返回分子式字符串（如 `"C6H12"`） | String |

## 配置选项

### 完整配置项列表

```javascript
const options = {
  // 画布尺寸
  width: 500,                    // 绘图宽度（像素）
  height: 500,                   // 绘图高度（像素）

  // 键的样式
  bondThickness: 0.6,            // 键的粗细
  bondLength: 15,                // 标准键长
  shortBondLength: 0.85,         // 短键（如双键）占标准键长的比例
  bondSpacing: 0.18 * 15,        // 双键/三键中各线之间的间距

  // 原子显示
  atomVisualization: 'default',  // 'default' | 'balls' | 'allballs' | 'none'

  // 字体大小
  fontSizeLarge: 6,              // 元素符号字体大小（pt）
  fontSizeSmall: 4,              // 数字（如氢原子数）字体大小（pt）

  // 布局
  padding: 20.0,                 // 分子结构周围的填充空间

  // 实验性功能
  experimental: false,           // 启用实验性功能（解决复杂环系统问题）

  // 显示选项
  terminalCarbons: false,        // 显示末端碳原子（CH3）
  explicitHydrogens: false,      // 显示显式氢原子
  compactDrawing: true,          // 绘制紧凑的末端基团和伪元素

  // 立体化学
  isomeric: true,                // 绘制立体化学（如果有）

  // 重叠处理
  overlapSensitivity: 0.42,      // 重叠敏感度
  overlapResolutionIterations: 1, // 重叠解决迭代次数

  // 调试
  debug: false,                  // 绘制调试信息

  // 颜色主题
  themes: {
    dark: { /* ... */ },
    light: { /* ... */ }
  },

  // v2.1+ 权重配置
  weights: {
    additionalPadding: 0,        // 权重图的额外填充
    sigma: 10,                   // 高斯模糊的 sigma 参数
    interval: 10,                // 采样间隔
    colormap: 'heat',            // 颜色映射方案
    opacity: 0.5                 // 权重层的不透明度
  }
};
```

### 配置项详细说明

| 选项 | 标识符 | 类型 | 默认值 | 说明 |
|------|--------|------|--------|------|
| 绘图宽度 | `width` | number | 500 | 输出 SVG/Canvas 的宽度（像素） |
| 绘图高度 | `height` | number | 500 | 输出 SVG/Canvas 的高度（像素） |
| 键粗细 | `bondThickness` | number | 0.6 | 键的线条粗细 |
| 键长 | `bondLength` | number | 15 | 标准单键的长度 |
| 短键长比例 | `shortBondLength` | number | 0.85 | 短键（双键中的短线）占标准键长的比例 |
| 键间距 | `bondSpacing` | number | 2.7 | 双键/三键中各条线之间的间距（默认 0.18 * 15） |
| 原子可视化 | `atomVisualization` | string | 'default' | 原子显示方式：`'default'`（文本）、`'balls'`（球棍）、`'allballs'`（全部球棍）、`'none'`（不显示） |
| 大字体大小 | `fontSizeLarge` | number | 6 | 元素符号的字体大小（pt） |
| 小字体大小 | `fontSizeSmall` | number | 4 | 数字和下标的字体大小（pt） |
| 填充 | `padding` | number | 20.0 | 分子结构周围的留白空间 |
| 实验性功能 | `experimental` | boolean | false | 启用实验性算法（推荐用于复杂环系统） |
| 显示末端碳 | `terminalCarbons` | boolean | false | 是否显示末端碳原子（CH3 等） |
| 显式氢原子 | `explicitHydrogens` | boolean | false | 是否显示所有氢原子 |
| 重叠敏感度 | `overlapSensitivity` | number | 0.42 | 检测原子重叠的敏感度 |
| 重叠迭代次数 | `overlapResolutionIterations` | number | 1 | 解决重叠的迭代次数 |
| 紧凑绘制 | `compactDrawing` | boolean | true | 将末端基团和伪元素合并显示 |
| 立体异构 | `isomeric` | boolean | true | 绘制立体化学信息（如有） |
| 调试模式 | `debug` | boolean | false | 绘制调试信息（顶点 ID、边 ID 等） |

### Themes 配置

颜色主题用于定义分子中各元素的颜色和背景色。

**默认主题配置**
```javascript
themes: {
  dark: {
    C: '#fff',          // 碳 - 白色
    O: '#e74c3c',       // 氧 - 红色
    N: '#3498db',       // 氮 - 蓝色
    F: '#27ae60',       // 氟 - 绿色
    CL: '#16a085',      // 氯 - 青绿色
    BR: '#d35400',      // 溴 - 橙色
    I: '#8e44ad',       // 碘 - 紫色
    P: '#d35400',       // 磷 - 橙色
    S: '#f1c40f',       // 硫 - 黄色
    B: '#e67e22',       // 硼 - 橙色
    SI: '#e67e22',      // 硅 - 橙色
    H: '#fff',          // 氢 - 白色
    BACKGROUND: '#141414' // 背景 - 深灰
  },
  light: {
    C: '#222',          // 碳 - 深灰
    O: '#e74c3c',       // 氧 - 红色
    N: '#3498db',       // 氮 - 蓝色
    F: '#27ae60',       // 氟 - 绿色
    CL: '#16a085',      // 氯 - 青绿色
    BR: '#d35400',      // 溴 - 橙色
    I: '#8e44ad',       // 碘 - 紫色
    P: '#d35400',       // 磷 - 橙色
    S: '#f1c40f',       // 硫 - 黄色
    B: '#e67e22',       // 硼 - 橙色
    SI: '#e67e22',      // 硅 - 橙色
    H: '#222',          // 氢 - 深灰
    BACKGROUND: '#fff'  // 背景 - 白色
  }
}
```

**自定义主题示例**
```javascript
const customTheme = {
  custom: {
    C: '#333333',
    O: '#FF6B6B',
    N: '#4ECDC4',
    F: '#95E1D3',
    CL: '#F38181',
    BR: '#AA96DA',
    I: '#FCBAD3',
    P: '#A8D8EA',
    S: '#FFB6B9',
    B: '#61C0BF',
    SI: '#BBDED6',
    H: '#666666',
    BACKGROUND: '#F9F9F9'
  }
};

const drawer = new SmilesDrawer.SvgDrawer({
  themes: customTheme
});

// 使用自定义主题
drawer.draw(tree, 'svg-output', 'custom');
```

### Weights 配置（v2.1+）

`weights` 参数用于在分子结构上叠加权重热图，常用于可视化分子属性（如电荷、反应活性等）。

**配置选项**
```javascript
weights: {
  additionalPadding: 0,    // 权重图的额外边距
  sigma: 10,               // 高斯分布的 sigma 参数（控制模糊程度）
  interval: 10,            // 颜色采样间隔
  colormap: 'heat',        // 颜色映射方案
  opacity: 0.5             // 权重层的透明度（0-1）
}
```

**使用示例**
```javascript
const drawer = new SmilesDrawer.SvgDrawer({
  width: 400,
  height: 300,
  weights: {
    sigma: 15,
    opacity: 0.6,
    colormap: 'viridis'
  }
});

// 每个重原子的权重（电荷、反应活性等）
const atomWeights = [0.1, -0.2, 0.5, 0.8, 0.3, -0.1];

SmilesDrawer.parse('CCCOCC', function(tree) {
  drawer.draw(tree, 'svg-output', 'light', atomWeights);
});
```

**注意事项**
- `weights` 数组长度必须等于分子中的重原子数（不包括氢）
- 当提供 `weights` 时，会自动禁用 `compactDrawing` 并增加 `padding`
- 如果所有权重都为 0，将不会绘制权重层

## 版本差异

### v2.0 相对于 v1.x 的变化

**当前状态**: 声明完全向后兼容（"As of now, there is full backwards compatibility"）

**主要改进**
1. **SVG 支持**: 新增 `SvgDrawer` 类，支持矢量图渲染
2. **模块化架构**: 代码重构为更清晰的模块结构
3. **性能优化**: 提升了渲染性能和解析速度
4. **TypeScript 支持**: v2.2.0+ 添加 TypeScript 定义

**迁移指南**
- v1.x 代码可直接升级到 v2.x，无需修改
- 推荐使用 `SvgDrawer` 替代 `Drawer` 以获得更好的输出质量

### v2.1.x 相对于 v2.0.x 的 API 变更

**新增功能**

1. **weights 参数**
   - 在 `SvgDrawer.draw()` 方法中添加 `weights` 参数
   - 支持在分子结构上叠加权重热图
   - 需要配置 `weights` 选项（sigma、opacity、colormap 等）

2. **highlight_atoms 参数**
   - 支持高亮特定原子
   - 格式：`[[atomClass, color], ...]`

3. **weightsNormalized 参数**
   - 指示权重是否已归一化

**API 签名变更**

v2.0.x:
```javascript
drawer.draw(data, target, themeName, infoOnly)
```

v2.1.x:
```javascript
drawer.draw(data, target, themeName, weights, infoOnly, highlight_atoms, weightsNormalized)
```

**向后兼容性**
- 所有新参数都是可选的，默认值确保与 v2.0.x 行为一致
- 如果省略 `weights` 参数（传 `null`），行为与 v2.0.x 相同

**版本推荐**
- **生产环境**: 推荐使用 v2.1.7（稳定且包含权重功能）
- **最新功能**: 可使用 v2.2.0（TypeScript 支持）
- **保守选择**: v2.0.x（如不需要权重功能）

## 已知问题与注意事项

### 1. 复杂环系统绘制问题

**现象**: 复杂环系统（特别是桥环）绘制时出现过长键或布局异常

**解决方案**:
```javascript
const drawer = new SmilesDrawer.SvgDrawer({
  experimental: true,  // 启用实验性功能
  overlapResolutionIterations: 2  // 增加重叠解决迭代次数
});
```

**相关 Issues**: GitHub Issues 中多个关于环系统绘制的反馈

### 2. 桥环分子的芳香性表示

**现象**: 含有桥环的分子中，显式定义的芳香环不会用圆圈表示，而是用虚线表示双键位置

**说明**: 这是预期行为，参见 README 中的 "Bridged Rings" 章节

### 3. 芳香氮原子的氢原子数

**现象**: 芳香环中的氮原子可能显示错误的氢原子数

**原因**: 这是 KEkulization 过程的已知限制

**临时方案**: 使用显式氢原子表示或手动调整

### 4. SSR（服务端渲染）兼容性

**现象**: 在 React/Gatsby 等框架中使用时出现 "Document not defined" 错误

**解决方案**:
```javascript
// 仅在客户端加载
if (typeof window !== 'undefined') {
  const SmilesDrawer = require('smiles-drawer');
  // 或使用动态导入
  import('smiles-drawer').then(module => {
    const drawer = new module.SvgDrawer(options);
  });
}
```

**相关 Issues**: [#80](https://github.com/reymond-group/smilesDrawer/issues/80)

### 5. Canvas 尺寸不匹配

**现象**: 长链分子水平绘制时超出 Canvas 边界

**解决方案**:
```javascript
const drawer = new SmilesDrawer.SvgDrawer({
  width: 800,   // 增加宽度
  height: 200,  // 减小高度
  padding: 30   // 调整填充
});
```

**相关 Issues**: [#182](https://github.com/reymond-group/smilesDrawer/issues/182)

### 6. 立体化学表示不准确

**现象**: 某些顺反异构体或手性中心显示不正确

**建议**:
- 使用标准的 SMILES 立体化学表示法（`/` 和 `\` 表示方向）
- 验证输入 SMILES 的正确性

**相关 Issues**: [#92](https://github.com/reymond-group/smilesDrawer/issues/92), [#217](https://github.com/reymond-group/smilesDrawer/issues/217)

### 7. 点键（Dot Bonds）和离子化合物

**现象**: 包含多个由点分隔的片段的 SMILES（离子化合物、盐类）可能显示异常

**说明**: 这是当前解析器的限制

**相关 Issues**: [#184](https://github.com/reymond-group/smilesDrawer/issues/184), [#193](https://github.com/reymond-group/smilesDrawer/issues/193)

### 8. SVG Drawer 在某些环境下不工作

**排查步骤**:
1. 确保 DOM 元素已加载
2. 检查是否正确传入 SVG 元素或元素 ID
3. 确认 `SmilesDrawer.parse()` 回调中调用 `draw()`

**相关 Issues**: [#105](https://github.com/reymond-group/smilesDrawer/issues/105), [#158](https://github.com/reymond-group/smilesDrawer/issues/158)

### 9. 字体渲染问题

**解决方案**: 在 HTML 中引入 Droid Sans 字体
```html
<link href="https://fonts.googleapis.com/css?family=Droid+Sans:400,700" rel="stylesheet" />
```

### 10. 性能问题

**建议**:
- 对于大量分子渲染，使用 `Drawer`（Canvas）而非 `SvgDrawer`
- 避免过于频繁的重新渲染
- 使用 `infoOnly=true` 仅计算属性时，性能更好

## 最佳实践

### 1. 初始化 Drawer

```javascript
// 推荐：创建可复用的 drawer 实例
const drawer = new SmilesDrawer.SvgDrawer({
  width: 300,
  height: 200,
  padding: 20
});

// 多次使用
SmilesDrawer.parse('CCCO', tree => drawer.draw(tree, svg1, 'light'));
SmilesDrawer.parse('c1ccccc1', tree => drawer.draw(tree, svg2, 'dark'));
```

### 2. 错误处理

```javascript
SmilesDrawer.parse(smilesString, function(tree) {
  try {
    drawer.draw(tree, target, 'light');
  } catch (error) {
    console.error('绘制失败:', error);
  }
}, function(error) {
  console.error('SMILES 解析失败:', error);
  // 显示用户友好的错误信息
});
```

### 3. 响应式设计

```javascript
function drawResponsive(smiles, containerId) {
  const container = document.getElementById(containerId);
  const width = container.clientWidth;
  const height = container.clientHeight || 200;

  const drawer = new SmilesDrawer.SvgDrawer({
    width: width,
    height: height,
    padding: Math.min(20, width * 0.05)
  });

  SmilesDrawer.parse(smiles, tree => {
    drawer.draw(tree, containerId, 'light');
  });
}
```

### 4. React 集成示例

```jsx
import { useEffect, useRef } from 'react';
import SmilesDrawer from 'smiles-drawer';

function MoleculeViewer({ smiles }) {
  const svgRef = useRef(null);

  useEffect(() => {
    if (!svgRef.current || !smiles) return;

    const drawer = new SmilesDrawer.SvgDrawer({
      width: 300,
      height: 200
    });

    SmilesDrawer.parse(smiles, tree => {
      drawer.draw(tree, svgRef.current, 'light');
    }, err => {
      console.error('Parse error:', err);
    });
  }, [smiles]);

  return <svg ref={svgRef} />;
}
```

### 5. 导出高质量图像

```javascript
// SVG 导出
function exportSVG(drawer, tree) {
  const svgElement = drawer.draw(tree, null, 'light');
  const svgData = new XMLSerializer().serializeToString(svgElement);
  const blob = new Blob([svgData], { type: 'image/svg+xml' });
  return URL.createObjectURL(blob);
}

// Canvas 导出（PNG）
function exportPNG(canvasElement) {
  return canvasElement.toDataURL('image/png');
}
```

## 参考资源

- **官方仓库**: https://github.com/reymond-group/smilesDrawer
- **NPM 包**: https://www.npmjs.com/package/smiles-drawer
- **GitHub Issues**: https://github.com/reymond-group/smilesDrawer/issues
- **学术论文**: Probst et al., "SmilesDrawer: Parsing and Drawing SMILES-Encoded Molecular Structures Using Client-Side JavaScript", *J. Chem. Inf. Model.* 2018, 58, 1-7
  - DOI: [10.1021/acs.jcim.7b00425](https://pubs.acs.org/doi/10.1021/acs.jcim.7b00425)
- **在线文档**: http://smilesdrawer.rocks (可能不可用)
- **示例集合**: https://github.com/reymond-group/smilesDrawer/tree/master/example

## 引用

如果在学术研究中使用 SmilesDrawer，请引用：

```bibtex
@article{probst2018smilesdrawer,
  title={SmilesDrawer: Parsing and Drawing SMILES-Encoded Molecular Structures Using Client-Side JavaScript},
  author={Probst, Daniel and Reymond, Jean-Louis},
  journal={Journal of Chemical Information and Modeling},
  volume={58},
  number={1},
  pages={1--7},
  year={2018},
  publisher={ACS Publications},
  doi={10.1021/acs.jcim.7b00425}
}
```

---

**文档版本**: 1.0
**最后更新**: 2026-03-23
**适用 SmilesDrawer 版本**: v2.0.x - v2.2.0

**Sources:**
- [GitHub - reymond-group/smilesDrawer](https://github.com/reymond-group/smilesDrawer)
- [smiles-drawer - NPM](https://www.npmjs.com/package/smiles-drawer/v/2.1.7)
- [smilesDrawer/src/SvgDrawer.js - GitHub](https://github.com/reymond-group/smilesDrawer/blob/master/src/SvgDrawer.js)
- [ACS Publication - SmilesDrawer](https://pubs.acs.org/doi/10.1021/acs.jcim.7b00425)
