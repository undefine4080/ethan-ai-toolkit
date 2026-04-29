# NGL Viewer 核心技术文档

## 1. Stage 初始化

### 构造函数
```javascript
const stage = new NGL.Stage(container, options);
```

### Stage 完整配置参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `impostor` | boolean | `true` | 使用 impostor 渲染 |
| `quality` | string | `'medium'` | 渲染质量 (`'low'`, `'medium'`, `'high'`) |
| `workerDefault` | boolean | `true` | 默认启用 worker |
| `sampleLevel` | number | `0` | 采样级别 |
| `backgroundColor` | string | `'black'` | 背景颜色 |
| `rotateSpeed` | number | `2.0` | 旋转速度 |
| `zoomSpeed` | number | `1.2` | 缩放速度 |
| `panSpeed` | number | `1.0` | 平移速度 |
| `clipNear` | number | `0` | 近裁剪面 |
| `clipFar` | number | `100` | 远裁剪面 |
| `clipDist` | number | `10` | 裁剪距离 |
| `fogNear` | number | `50` | 雾效起始距离 |
| `fogFar` | number | `100` | 雾效结束距离 |
| `cameraFov` | number | `40` | 相机视野角度 |
| `cameraType` | string | `'perspective'` | 相机类型 (`'perspective'`, `'orthographic'`) |
| `lightColor` | number | `0xdddddd` | 主光源颜色 |
| `lightIntensity` | number | `1.0` | 主光源强度 |
| `ambientColor` | number | `0xdddddd` | 环境光颜色 |
| `ambientIntensity` | number | `0.2` | 环境光强度 |
| `hoverTimeout` | number | `0` | 悬停超时时间 |
| `tooltip` | boolean | `true` | 启用工具提示 |
| `mousePreset` | string | `'default'` | 鼠标预设 |

### 示例
```javascript
const stage = new NGL.Stage('container', {
  backgroundColor: 'white',
  cameraType: 'orthographic',
  quality: 'high',
  cameraFov: 50
});
```

---

## 2. 加载分子文件

### loadFile 方法
```javascript
stage.loadFile(url, options).then(component => {
  // 加载成功后的操作
});
```

### 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `url` | string | 文件路径或 URL |
| `options` | object | 加载选项 |
| `options.name` | string | 组件名称 |
| `options.defaultRepresentation` | boolean | 是否自动添加默认表示 |

### 支持的文件格式

| 格式 | 扩展名 | 说明 |
|------|--------|------|
| PDB | `.pdb` | 蛋白质数据库格式 |
| mmCIF | `.cif`, `.mmcif` | 大分子晶体信息文件 |
| PDBx | `.pdbx` | PDBx/mmCIF 格式 |
| SDF | `.sdf` | 结构数据文件 |
| MOL | `.mol` | MDL MOL 格式 |
| MOL2 | `.mol2` | Tripos MOL2 格式 |
| GRO | `.gro` | GROMACS 格式 |
| XYZ | `.xyz` | XYZ 坐标格式 |
| PQR | `.pqr` | PQR 格式 (带电荷和半径) |
| MMTF | `.mmtf` | Macromolecular Transmission Format |
| PSE | `.pse` | PyMOL 会话文件 |
| DCD | `.dcd` | CHARMM/NAMD 轨迹文件 |
| XTC | `.xtc` | GROMACS 压缩轨迹 |
| TRR | `.trr` | GROMACS 轨迹 |
| NETCDF | `.nc` | AMBER NetCDF 轨迹 |
| DTR | `.dtr` | DESMOND 轨迹 |
| CUBE | `.cube` | Gaussian Cube 体积数据 |
| DX | `.dx` | DX 体积数据 |
| DXBIN | `.dxbin` | 二进制 DX 体积数据 |

### 从 RCSB PDB 在线加载

使用 `rcsb://` 前缀直接从 RCSB 数据库加载结构：

```javascript
// 加载 PDB ID 为 1LYZ 的结构
stage.loadFile('rcsb://1LYZ').then(component => {
  component.addRepresentation('cartoon');
  component.autoView();
});

// 带选项加载
stage.loadFile('rcsb://1LYZ', {
  name: '溶菌酶',
  defaultRepresentation: false
});
```

### 加载本地文件

```javascript
// 使用文件选择器
document.getElementById('fileInput').addEventListener('change', function() {
  const file = this.files[0];
  stage.loadFile(file).then(component => {
    component.addRepresentation('cartoon');
    component.autoView();
  });
});

// 从相对路径加载
stage.loadFile('./data/protein.pdb');
```

---

## 3. 表示方式 (Representations)

### addRepresentation 方法

```javascript
component.addRepresentation(type, parameters);
```

### 表示类型一览

| 类型 | 说明 | 适用场景 |
|------|------|----------|
| `cartoon` | 卡通表示 | 蛋白质二级结构 |
| `ribbon` | 带状表示 | 蛋白质骨架 |
| `backbone` | 骨架表示 | 主链原子连线 |
| `ball+stick` | 球棍模型 | 原子细节 |
| `licorice` | 甘草棒模型 | 类似球棍但无球 |
| `spacefill` | 空间填充 | 范德华球 |
| `surface` | 分子表面 | 溶剂可及表面 |
| `wireframe` | 线框模型 | 键的线框 |
| `point` | 点模型 | 原子点 |
| `line` | 线模型 | 键线 |
| `label` | 标签 | 文本标注 |
| `distance` | 距离测量 | 原子间距离 |
| `angle` | 角度测量 | 三原子角度 |
| `dihedral` | 二面角测量 | 四原子二面角 |
| `helixorient` | 螺旋方向 | α螺旋分析 |
| `simplified` | 简化表示 | 简单几何体 |
| `trace` | 轨迹表示 | Cα轨迹 |

### 通用参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `sele` | string | 选择器表达式 |
| `colorScheme` | string | 颜色方案 |
| `color` | string/number | 自定义颜色 |
| `opacity` | number | 不透明度 (0-1) |
| `visible` | boolean | 可见性 |

### Cartoon 表示参数

```javascript
component.addRepresentation('cartoon', {
  sele: ':A',                    // 选择器
  colorScheme: 'sstruc',         // 按二级结构着色
  opacity: 1.0,                  // 不透明度
  radiusScale: 1.0,              // 半径缩放
  aspectRatio: 5,                // 宽高比
  subdiv: 12,                    // 细分级别
  quality: 'medium',             // 质量
  tension: 0.5,                  // 曲线张力
  smoothSheet: 0.5,              // 平滑β折叠
  smoothTube: 0.5,               // 平滑管道
  wireframe: false,              // 线框模式
  side: 'front',                 // 渲染面 ('front', 'back', 'double')
  roughness: 0.4,                // 粗糙度
  metalness: 0.0                 // 金属度
});
```

### Ball+Stick 表示参数

```javascript
component.addRepresentation('ball+stick', {
  sele: 'ligand',
  colorScheme: 'element',
  radiusScale: 0.3,              // 球半径缩放
  sphereRadius: 0.3,             // 球半径
  cylinderScale: 0.3,            // 圆柱半径缩放
  radiusType: 'vdw',             // 半径类型 ('vdw', 'covalent', 'bfactor')
  bondScale: 1.0,                // 键缩放
  bondSpacing: 0.0,              // 双键间距
  aspectRatio: 1.0,              // 宽高比
  quality: 'high',               // 质量
  wireframe: false,
  roughness: 0.3,
  metalness: 0.0,
  multipleBond: 'symmetric'      // 多键模式 ('off', 'symmetric', 'offset')
});
```

### Surface 表示参数

```javascript
component.addRepresentation('surface', {
  sele: 'protein',
  colorScheme: 'chainid',
  opacity: 0.8,
  radiusScale: 1.0,
  scale: 1.0,                    // 表面缩放
  probeRadius: 1.4,              // 探针半径 (溶剂)
  smooth: 2,                     // 平滑度
  background: false,             // 背景表面
  wireframe: false,
  roughness: 0.6,
  metalness: 0.0,
  opacitySaturation: true,       // 不透明度饱和
  transparentBackfaces: 'off'    // 透明背面 ('off', 'on', 'one')
});
```

### Label 表示参数

```javascript
component.addRepresentation('label', {
  sele: ':A and .CA',            // Cα原子
  labelType: 'residue',          // 标签类型
  labelText: { residue: '{resname} {resno}' },  // 标签文本格式
  labelSize: 1.0,                // 标签大小
  labelColor: 'skyblue',         // 标签颜色
  labelRelativeOffset: [0, 0],   // 相对偏移
  labelXOffset: 0,               // X偏移
  labelYOffset: 0,               // Y偏移
  labelZOffset: 2.0,             // Z偏移 (距离原子)
  labelAttachment: 'bottom-left', // 附件位置
  backgroundColor: 'black',      // 背景颜色
  backgroundOpacity: 0.5,        // 背景不透明度
  borderColor: 'white',          // 边框颜色
  borderWidth: 0.5,              // 边框宽度
  borderRadius: 0.3,             // 边框圆角
  showBackground: true,          // 显示背景
  showBorder: true,              // 显示边框
  fontWeight: 'normal',          // 字重
  fontStyle: 'normal',           // 字体样式
  fontFamily: 'sans-serif',      // 字体
  textAlign: 'left',             // 文本对齐
  xOffset: 0,                    // X偏移 (deprecated)
  yOffset: 0,                    // Y偏移 (deprecated)
  zOffset: 2.0                   // Z偏移 (deprecated)
});

// 标签类型 (labelType)
// 'atom' - 原子标签
// 'residue' - 残基标签
// 'residuecount' - 残基计数
// 'text' - 自定义文本
```

### Distance 表示参数

```javascript
component.addRepresentation('distance', {
  atomPair: [
    ['10:A.CA', '50:A.CA'],
    ['.CA', '.CB']
  ],
  labelColor: 'black',
  labelSize: 0.7,
  color: 'red',
  opacity: 0.8,
  lineColor: 'green',
  linewidth: 2.0,
  labelUnit: 'angstrom'          // 距离单位
});
```

### Ribbon 表示参数

```javascript
component.addRepresentation('ribbon', {
  sele: 'protein',
  colorScheme: 'residueindex',
  radiusScale: 1.0,
  subdiv: 20,
  tension: 0.7,
  arrowAxis: 'custom',           // 箭头轴
  colorMode: 'hcl'               // 颜色模式
});
```

### Spacefill 表示参数

```javascript
component.addRepresentation('spacefill', {
  sele: 'ligand',
  colorScheme: 'element',
  radiusScale: 1.0,
  radiusType: 'vdw',
  quality: 'high',
  roughness: 0.0,
  metalness: 0.5
});
```

---

## 4. 颜色方案 (Color Schemes)

### 可用的颜色方案

| 方案名称 | 说明 |
|----------|------|
| `atomindex` | 原子索引 |
| `bfactor` | B因子 (温度因子) |
| `chainid` | 链ID |
| `chainindex` | 链索引 |
| `chainname` | 链名称 |
| `densityfit` | 密度拟合 |
| `electrostatic` | 静电势 |
| `element` | 元素 (默认) |
| `entityindex` | 实体索引 |
| `entitytype` | 实体类型 |
| `geoquality` | 几何质量 |
| `hydrophobicity` | 疏水性 |
| `modelindex` | 模型索引 |
| `moleculetype` | 分子类型 |
| `occupancy` | 占据率 |
| `random` | 随机颜色 |
| `residueindex` | 残基索引 |
| `resname` | 残基名称 |
| `sstruc` | 二级结构 (α螺旋/β折叠等) |
| `uniform` | 统一颜色 |
| `value` | 数值 |
| `volume` | 体积 |

### 使用示例

```javascript
// 按元素着色
component.addRepresentation('ball+stick', {
  colorScheme: 'element'
});

// 按链着色
component.addRepresentation('cartoon', {
  colorScheme: 'chainid'
});

// 按二级结构着色
component.addRepresentation('cartoon', {
  colorScheme: 'sstruc',
  colorScale: 'RdYlBu'  // 颜色映射表
});

// 自定义颜色
component.addRepresentation('surface', {
  color: 0xff0000,              // 十六进制数字
  // 或
  color: 'red',                 // 颜色名称
  // 或
  color: 'rgb(255, 0, 0)'       // CSS颜色
});

// 使用颜色映射
component.addRepresentation('cartoon', {
  colorScheme: 'bfactor',
  colorScale: 'rainbow',
  colorReverse: false,
  colorDomain: [0, 100]
});
```

### 预定义颜色映射表 (Color Scales)

```
Accent, Dark2, Paired, Pastel1, Pastel2, Set1, Set2, Set3,
Category10, Category20, Category20b, Category20c,
Viridis, Inferno, Magma, Plasma, Warm, Cool, Rainbow, Sinebow,
Cubehelix, YlGnBu, YlGn, OrRd, PuBuGn, PuBu, BuPu, RdPu, PuRd,
Oranges, Reds, Greens, Blues, Purples, RdBu, RdYlBu, RdYlGn,
Spectral
```

---

## 5. 选择器语法 (Selection Language)

### 基本语法

选择器用于指定要对哪些原子/残基进行操作。

### 选择类型

| 选择器 | 说明 | 示例 |
|--------|------|------|
| 数字 | 残基编号 | `35`, `52` |
| 数字范围 | 残基范围 | `10-20` |
| `:` | 链标识 | `:A`, `:B` |
| `.` | 原子名称 | `.CA`, `.CB`, `.N` |
| `%` | 元素 | `%C`, `%O`, `%N` |
| `@` | 残基名称 | `@ALA`, `@GLU` |
| `/` | 模型索引 | `/0`, `/1` |
| `#` | 替代位置 | `#A` |
| `^` | 插入码 | `^A` |
| 文本 | 关键字 | `protein`, `ligand`, `water` |

### 布尔运算符

| 运算符 | 说明 | 示例 |
|--------|------|------|
| `or` | 或 | `35 or 52` |
| `and` | 与 | `:A and 10-20` |
| `not` | 非 | `not water` |

### 预定义关键字

| 关键字 | 说明 |
|--------|------|
| `all` | 所有原子 |
| `none` | 无原子 |
| `protein` | 蛋白质 |
| `nucleic` | 核酸 |
| `rna` | RNA |
| `dna` | DNA |
| `hetero` | 杂原子 |
| `ligand` | 配体 |
| `water` | 水分子 |
| `ion` | 离子 |
| `saccharide` | 糖类 |
| `lipid` | 脂质 |
| `backbone` | 主链 |
| `sidechain` | 侧链 |
| `metal` | 金属 |
| `helix` | α螺旋 |
| `sheet` | β折叠 |
| `turn` | 转角 |
| `helixalpha` | α螺旋 |
| `helixpi` | π螺旋 |
| `helix310` | 3-10螺旋 |

### 示例

```javascript
// 选择残基 35 和 52
'35 or 52'

// 选择链 A 的所有原子
':A'

// 选择链 A 的 Cα 原子
':A and .CA'

// 选择残基 10 到 20
'10-20'

// 选择配体
'ligand'

// 选择蛋白质的侧链
'protein and sidechain'

// 选择水分子和离子
'water or ion'

// 选择 ALA 残基
'@ALA'

// 选择碳原子
'%C'

// 选择残基 50 的 Cα 原子在链 A
'50:A.CA'

// 选择氢原子
'%H'

// 排除氢原子
'not %H'

// 选择距离某个原子 5 埃内的原子
'5 within :A.25'

// 选择特定残基范围内的螺旋结构
'helix and 10-50'

// 复合选择
'10^A:F.CA%C/0'
// 解释：残基10 + 插入码A + 链F + Cα原子 + 碳元素 + 模型0
```

---

## 6. 其他常用 API

### 视图控制

#### autoView - 自动调整视图

```javascript
// 自动调整整个 Stage 的视图
stage.autoView();

// 自动调整组件的视图
component.autoView();

// 自动调整特定选择器的视图
component.autoView('ligand');

// 带动画持续时间 (毫秒)
component.autoView(1000);

// 选择器 + 动画
component.autoView('protein', 500);
```

#### 手动控制相机

```javascript
// 旋转
stage.spinAnimation = true;           // 开启自动旋转
stage.setSpin([x, y, z], speed);      // 设置旋转轴和速度

// 缩放
stage.setZoom(zoomLevel, duration);

// 平移
stage.translationView([x, y, z]);

// 设置相机位置
stage.viewerControls.translate([x, y, z]);
stage.viewerControls.rotate(quaternion);
stage.viewerControls.zoom(zoomFactor);

// 重置视图
stage.resetView(duration);
```

#### 聚焦和裁剪

```javascript
// 聚焦到选择
component.centerView('ligand', 1000);

// 聚焦并缩放
component.focus('protein');

// 设置裁剪平面
stage.setParameters({
  clipNear: 0,
  clipFar: 100,
  clipDist: 10
});
```

### 组件操作

#### 获取组件

```javascript
// 按名称获取组件
const comp = stage.getComponentsByName('myProtein');

// 获取所有组件
const allComps = stage.compList;

// 按索引获取
const firstComp = stage.compList[0];
```

#### 组件方法

```javascript
// 自动视图
component.autoView(duration);

// 隐藏/显示
component.setVisibility(false);

// 设置透明度
component.setOpacity(0.5);

// 销毁组件
component.dispose();

// 获取表示
const repr = component.getRepresentationsByName('cartoon');
```

### 表示操作

```javascript
// 获取表示
const repr = component.addRepresentation('cartoon', params);

// 设置可见性
repr.setVisibility(false);

// 设置参数
repr.setParameters({ opacity: 0.5 });

// 销毁表示
repr.dispose();

// 暂停/恢复渲染
repr.setVisibility(true);
```

### 事件监听

```javascript
// 点击事件
stage.signals.clicked.add((pickingProxy) => {
  if (pickingProxy) {
    const atom = pickingProxy.atom;
    const bond = pickingProxy.bond;
    console.log('Clicked:', atom || bond);
  }
});

// 悬停事件
stage.signals.hovered.add((pickingProxy) => {
  console.log('Hovered:', pickingProxy);
});

// 组件加载完成
stage.signals.componentAdded.add((component) => {
  console.log('Component added:', component);
});

// 视图变化
stage.signals.viewChanged.add(() => {
  console.log('View changed');
});
```

### 测量和标注

#### 距离测量

```javascript
component.addRepresentation('distance', {
  atomPair: [
    ['10:A.CA', '50:A.CA']
  ],
  labelSize: 1.0,
  labelColor: 'black',
  color: 'red',
  linewidth: 2.0
});
```

#### 角度测量

```javascript
component.addRepresentation('angle', {
  atomTriple: [
    ['10:A.N', '10:A.CA', '10:A.C']
  ],
  color: 'blue',
  opacity: 0.8
});
```

#### 二面角测量

```javascript
component.addRepresentation('dihedral', {
  atomQuad: [
    ['10:A.N', '10:A.CA', '10:A.C', '11:A.N']
  ],
  color: 'green'
});
```

### 导出和截图

```javascript
// 截图
stage.makeImage({
  factor: 2,              // 分辨率倍数
  antialias: true,        // 抗锯齿
  trim: false,            // 裁剪空白
  transparent: true       // 透明背景
}).then((blob) => {
  // blob 是图片数据
  const url = URL.createObjectURL(blob);
  const img = new Image();
  img.src = url;
});
```

### 实用方法

```SSFWorkbook
// 设置背景色
stage.setParameters({ backgroundColor: 'white' });

// 设置质量
stage.setParameters({ quality: 'high' });

// 切换全屏
stage.toggleFullscreen();

// 执行脚本
component.structure.eachAtom((atom) => {
  console.log(atom.resname, atom.resno);
}, new NGL.Selection(':A'));
```

---

## 7. 完整示例

### 基础示例

```javascript
// 初始化
const stage = new NGL.Stage('viewport', {
  backgroundColor: 'white',
  quality: 'high'
});

// 加载 PDB
stage.loadFile('rcsb://1LYZ', {
  defaultRepresentation: false
}).then((component) => {
  // 添加卡通表示
  component.addRepresentation('cartoon', {
    sele: 'protein',
    colorScheme: 'sstruc',
    opacity: 1.0
  });

  // 添加配体的球棍模型
  component.addRepresentation('ball+stick', {
    sele: 'ligand',
    colorScheme: 'element'
  });

  // 添加标签
  component.addRepresentation('label', {
    sele: 'ligand',
    labelType: 'residue',
    labelSize: 1.5,
    labelColor: 'black',
    zOffset: 3.0
  });

  // 调整视图
  component.autoView(1000);
});
```

### 高级示例

```javascript
const stage = new NGL.Stage('viewport', {
  backgroundColor: '#1a1a1a',
  cameraFov: 45,
  clipNear: 0,
  clipFar: 100
});

stage.loadFile('rcsb://4HHB').then((component) => {
  // 蛋白质卡通
  component.addRepresentation('cartoon', {
    sele: 'protein',
    colorScheme: 'chainid',
    opacity: 0.9
  });

  // 血红素表面
  component.addRepresentation('surface', {
    sele: 'hem',
    colorScheme: 'element',
    opacity: 0.7,
    probeRadius: 1.4
  });

  // 铁原子的空间填充
  component.addRepresentation('spacefill', {
    sele: '%FE',
    color: 'orange',
    radiusScale: 1.2
  });

  // 水分子
  component.addRepresentation('ball+stick', {
    sele: 'water',
    colorScheme: 'element',
    radiusScale: 0.3,
    opacity: 0.5
  });

  // 测量距离
  component.addRepresentation('distance', {
    atomPair: [
      ['58:A.CD1', '63:A.CE1']
    ],
    color: 'yellow',
    labelColor: 'white'
  });

  // 自动视图
  component.autoView();
});
```

---

## 参考资源

- **官方文档**: http://nglviewer.org/ngl/api/
- **GitHub**: https://github.com/nglviewer/ngl
- **在线演示**: http://nglviewer.org/ngl/
- **RCSB PDB**: https://www.rcsb.org/
