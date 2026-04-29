# D3.js v7 API 参考文档 - 化学可视化场景

本文档收集了 D3.js v7 中化学可视化场景常用的 API，涵盖缩放、力导图、树状布局、选择器和 SVG 操作等模块。

---

## 1. d3.zoom() - 缩放行为

### 创建缩放行为

```javascript
const zoom = d3.zoom();
```

创建一个新的缩放行为。返回的 `zoom` 既是对象也是函数，通常通过 `selection.call()` 应用到选择集上。

### 应用缩放行为

```javascript
selection.call(d3.zoom().on("zoom", zoomed));
```

将缩放行为应用到指定的选择集，绑定必要的事件监听器以允许平移和缩放，并将每个选中元素的缩放变换初始化为单位变换（如果尚未定义）。

### 主要方法

#### zoom.transform(selection, transform, point)

设置选择集的当前缩放变换。

```javascript
// 瞬间重置为身份变换
selection.call(zoom.transform, d3.zoomIdentity);

// 平滑过渡 750 毫秒重置
selection.transition().duration(750).call(zoom.transform, d3.zoomIdentity);
```

**参数：**
- `selection` - 选择集或过渡
- `transform` - 缩放变换对象或返回变换的函数
- `point` - 可选，视口中心点 `[x, y]`

#### zoom.translateBy(selection, x, y)

平移当前缩放变换。

```javascript
selection.call(zoom.translateBy, 10, 10);
```

新的平移量：`tx1 = tx0 + kx`, `ty1 = ty0 + ky`

#### zoom.translateTo(selection, x, y, p)

将指定位置 `<x,y>` 平移到给定点 `p`。

```javascript
selection.call(zoom.translateTo, 100, 100);
```

新的平移量：`tx = px - kx`, `ty = py - ky`

#### zoom.scaleBy(selection, k, p)

按比例缩放当前变换。

```javascript
selection.call(zoom.scaleBy, 2); // 放大 2 倍
```

新的比例：`k1 = k0 * k`

#### zoom.scaleTo(selection, k, p)

将缩放比例设置为指定值。

```javascript
selection.call(zoom.scaleTo, 2); // 设置为 2 倍
```

新的比例：`k1 = k`

### 配置方法

#### zoom.scaleExtent([extent])

设置缩放范围限制。

```javascript
zoom.scaleExtent([0.5, 10]); // 最小 0.5 倍，最大 10 倍
```

默认为 `[0, ∞]`。

#### zoom.translateExtent([extent])

设置平移范围限制。

```javascript
zoom.translateExtent([[0, 0], [width, height]]);
```

默认为 `[[-∞, -∞], [+∞, +∞]]`。

#### zoom.extent([extent])

设置视口范围。

```javascript
zoom.extent([[0, 0], [width, height]]);
```

默认为 `[[0, 0], [width, height]]`，其中 width 和 height 是元素的客户宽度和高度。

#### zoom.filter(filter)

设置事件过滤器。

```javascript
zoom.filter(event => !event.ctrlKey && !event.button);
```

默认过滤器忽略次要按钮的 mousedown 事件。

#### zoom.duration(duration)

设置双击和双击缩放过渡的持续时间（毫秒）。

```javascript
zoom.duration(250); // 默认 250 毫秒
```

#### zoom.on(typenames, listener)

注册事件监听器。

```javascript
zoom.on("zoom", (event) => {
  g.attr("transform", event.transform);
});
```

**事件类型：**
- `start` - 缩放开始时
- `zoom` - 缩放变换改变时
- `end` - 缩放结束时

**事件对象：**
- `event.transform` - 当前缩放变换
- `event.sourceEvent` - 底层输入事件

### 缩放变换对象

#### d3.zoomIdentity

身份变换，其中 `k = 1`, `tx = ty = 0`。

```javascript
const t = d3.zoomIdentity;
```

#### d3.zoomTransform(node)

获取节点的当前变换。

```javascript
const transform = d3.zoomTransform(selection.node());
```

#### 变换属性

- `transform.x` - x 轴平移量
- `transform.y` - y 轴平移量
- `transform.k` - 缩放因子

#### 变换方法

```javascript
// 创建变换
const t = d3.zoomIdentity.translate(x, y).scale(k);

// 缩放变换
const t1 = transform.scale(2);

// 平移变换
const t1 = transform.translate(10, 20);

// 应用变换到点
const [px, py] = transform.apply([x, y]);

// 应用变换到 x 坐标
const px = transform.applyX(x);

// 应用变换到 y 坐标
const py = transform.applyY(y);

// 逆变换点
const [px, py] = transform.invert([x, y]);

// 逆变换 x 坐标
const px = transform.invertX(x);

// 逆变换 y 坐标
const py = transform.invertY(y);

// 重缩放 x 比例尺
const x2 = transform.rescaleX(x);

// 重缩放 y 比例尺
const y2 = transform.rescaleY(y);

// 转换为 SVG transform 字符串
const str = transform.toString(); // "translate(tx,ty) scale(k)"
```

### 应用变换示例

#### Canvas 2D

```javascript
context.translate(transform.x, transform.y);
context.scale(transform.k, transform.k);
```

#### HTML (CSS)

```javascript
div.style("transform", "translate(" + transform.x + "px," + transform.y + "px) scale(" + transform.k + ")");
div.style("transform-origin", "0 0");
```

#### SVG

```javascript
// 方法 1: 拼接字符串
g.attr("transform", "translate(" + transform.x + "," + transform.y + ") scale(" + transform.k + ")");

// 方法 2: 使用 toString()
g.attr("transform", transform);
```

**注意：** 变换顺序很重要！必须先平移后缩放。

---

## 2. d3.forceSimulation() - 力导图布局

力导图模拟实现了速度 Verlet 数值积分器，用于模拟粒子（节点）上的物理力。模拟假设每个时间步长 `Δt = 1`，所有粒子的质量 `m = 1`。

### 创建模拟

```javascript
const simulation = d3.forceSimulation(nodes);
```

创建一个带有指定节点数组的模拟。节点数组会被修改，添加以下属性：
- `index` - 节点的索引
- `x` - 当前 x 坐标
- `y` - 当前 y 坐标
- `vx` - 当前 x 速度
- `vy` - 当前 y 速度

### 添加力

```javascript
const simulation = d3.forceSimulation(nodes)
  .force("charge", d3.forceManyBody())
  .force("link", d3.forceLink(links))
  .force("center", d3.forceCenter(width / 2, height / 2))
  .force("collide", d3.forceCollide(radius));
```

### 模拟控制

#### simulation.restart()

重启模拟的内部计时器。

```javascript
simulation.restart();
```

#### simulation.stop()

停止模拟的内部计时器。

```javascript
simulation.stop();
```

#### simulation.tick(iterations)

手动推进模拟指定迭代次数。

```javascript
simulation.tick(300); // 默认迭代次数
```

#### simulation.nodes(nodes)

设置或获取节点数组。

```javascript
simulation.nodes(nodes);
```

### Alpha 参数

#### simulation.alpha(alpha)

获取或设置当前的 alpha 值（类似于模拟退火中的温度）。

```javascript
simulation.alpha(1); // 默认 1
```

#### simulation.alphaMin(min)

获取或设置最小 alpha 值。

```javascript
simulation.alphaMin(0.001); // 默认 0.001
```

#### simulation.alphaDecay(decay)

获取或设置 alpha 衰减率。

```javascript
simulation.alphaDecay(0.0228); // 默认 0.0228
```

默认衰减率对应 300 次迭代。

#### simulation.alphaTarget(target)

获取或设置目标 alpha 值。

```javascript
simulation.alphaTarget(0.3); // 默认 0
```

#### simulation.velocityDecay(decay)

获取或设置速度衰减因子。

```javascript
simulation.velocityDecay(0.4); // 默认 0.4
```

类似于大气摩擦；每次 tick 后，每个节点的速度乘以 `1 - decay`。

### 力的方法

#### simulation.force(name, force)

添加或获取力。

```javascript
simulation.force("charge", d3.forceManyBody());
simulation.force("charge", null); // 移除力
```

#### simulation.find(x, y, radius)

查找指定位置最近的节点。

```javascript
const node = simulation.find(100, 100, 50); // 在半径 50 内查找
```

### 事件监听

#### simulation.on(typenames, listener)

注册事件监听器。

```javascript
simulation.on("tick", () => {
  // 更新渲染
});

simulation.on("end", () => {
  // 模拟结束
});
```

**事件类型：**
- `tick` - 每次 tick 后
- `end` - 模拟停止时

### 力的类型

#### d3.forceLink(links) - 链接力

根据期望的链接距离推动链接的节点靠近或分开。

```javascript
const link = d3.forceLink(links)
  .id(d => d.id)
  .distance(30)
  .strength(1);
```

**方法：**
- `link.links(links)` - 设置链接数组
- `link.id(id)` - 设置节点 id 访问器
- `link.distance(distance)` - 设置链接距离（默认 30）
- `link.strength(strength)` - 设置链接强度（默认 `1 / Math.min(count(source), count(target))`）
- `link.iterations(iterations)` - 设置迭代次数（默认 1）

**链接对象：**
- `source` - 源节点
- `target` - 目标节点
- `index` - 链接索引

#### d3.forceManyBody() - 多体力

在所有节点之间应用相互作用力。正值表示吸引（类似重力），负值表示排斥（类似静电荷）。

```javascript
const manyBody = d3.forceManyBody()
  .strength(-30)
  .theta(0.9)
  .distanceMin(1)
  .distanceMax(Infinity);
```

**方法：**
- `manyBody.strength(strength)` - 设置力强度（默认 -30）
- `manyBody.theta(theta)` - 设置 Barnes-Hut 近似标准（默认 0.9）
- `manyBody.distanceMin(distance)` - 设置最小距离（默认 1）
- `manyBody.distanceMax(distance)` - 设置最大距离（默认 Infinity）

#### d3.forceCenter(x, y) - 中心力

将节点统一平移，使所有节点的平均位置位于给定位置 `<x,y>`。

```javascript
const center = d3.forceCenter(width / 2, height / 2)
  .strength(0.05);
```

**方法：**
- `center.x(x)` - 设置中心 x 坐标（默认 0）
- `center.y(y)` - 设置中心 y 坐标（默认 0）
- `center.strength(strength)` - 设置力强度（默认 1）

#### d3.forceCollide(radius) - 碰撞力

将节点视为具有给定半径的圆，防止节点重叠。

```javascript
const collide = d3.forceCollide(d => d.r)
  .strength(1)
  .iterations(1);
```

**方法：**
- `collide.radius(radius)` - 设置半径访问器（默认 1）
- `collide.strength(strength)` - 设置力强度（默认 1）
- `collide.iterations(iterations)` - 设置迭代次数（默认 1）

### 固定节点

要固定节点在给定位置，可以指定两个额外属性：

```javascript
node.fx = 100; // 固定 x 位置
node.fy = 100; // 固定 y 位置
```

要取消固定，将 `fx` 和 `fy` 设置为 `null` 或删除这些属性。

### 自定义力

力是一个修改节点位置或速度的函数：

```javascript
function force(alpha) {
  for (let i = 0, n = nodes.length, node, k = alpha * 0.1; i < n; ++i) {
    node = nodes[i];
    node.vx -= node.x * k;
    node.vy -= node.y * k;
  }
}
```

力必须实现：
- `force(alpha)` - 应用力
- `force.initialize(nodes)` - 初始化节点数组

---

## 3. d3.tree() / d3.cluster() - 树状布局

树状布局使用 Reingold-Tilford "整洁" 算法生成整洁的节点-链接图。

### 创建布局

#### d3.tree()

```javascript
const tree = d3.tree();
```

创建一个带有默认设置的树布局。

#### d3.cluster()

```javascript
const cluster = d3.cluster();
```

创建一个带有默认设置的集群布局（树状图）。

### 应用布局

```javascript
const root = tree(hierarchy);
```

布局指定的根层次结构，在根及其后代上分配以下属性：
- `node.x` - 节点的 x 坐标
- `node.y` - 节点的 y 坐标

### 配置方法

#### tree.size([size])

设置布局大小。

```javascript
tree.size([width, height]);
```

如果 `size` 为 `null`，表示将使用节点大小。坐标 `x` 和 `y` 表示任意坐标系；例如，生成径向布局时，大小 `[360, radius]` 对应 360° 的宽度和半径的深度。

#### tree.nodeSize([size])

设置节点大小。

```javascript
tree.nodeSize([width, height]);
```

当指定节点大小时，根节点始终位于 `<0, 0>`。节点大小为 `null` 表示将使用布局大小。

**size() vs nodeSize()：**
- `size()` - 定义整个树布局的总面积
- `nodeSize()` - 定义每个节点的固定空间；更适合防止可变大小节点的重叠

#### tree.separation([separation])

设置相邻节点之间的分隔访问器。

```javascript
tree.separation((a, b) => a.parent == b.parent ? 1 : 2);
```

默认分隔函数：

```javascript
function separation(a, b) {
  return a.parent == b.parent ? 1 : 2;
}
```

适用于径向布局的变体，按半径成比例减小分隔间隙：

```javascript
function separation(a, b) {
  return (a.parent == b.parent ? 1 : 2) / a.depth;
}
```

分隔访问器用于分隔相邻节点。分隔函数传递两个节点 `a` 和 `b`，必须返回所需的分隔。节点通常是兄弟节点，但如果布局决定将这样的节点相邻放置，节点可能是更远的关系。

---

## 4. d3.select / d3.selectAll - 选择器

### 选择元素

#### d3.select(selector)

选择第一个匹配的元素。

```javascript
d3.select("body");
d3.select("#chart");
d3.select(".container");
```

#### d3.selectAll(selector)

选择所有匹配的元素。

```javascript
d3.selectAll("p");
d3.selectAll(".item");
d3.selectAll("circle");
```

### 修改元素

#### selection.attr(name, value)

设置属性。

```javascript
selection.attr("class", "graf");
selection.attr("width", 100);
selection.attr("transform", "translate(10, 20)");
```

如果 `value` 是函数，则为每个选中的元素求值：

```javascript
selection.attr("r", d => d.radius);
```

如果未指定 `value`，返回第一个元素的属性值：

```javascript
selection.attr("class"); // "graf"
```

#### selection.style(name, value, priority)

设置样式属性。

```javascript
selection.style("color", "red");
selection.style("fill", "steelblue");
selection.style("stroke-width", "2px", "important");
```

**注意：** 与许多 SVG 属性不同，CSS 样式通常有关联的单位。例如，`3px` 是有效的 stroke-width 属性值，而 `3` 不是。

#### selection.classed(names, value)

分配或取消分配 CSS 类。

```javascript
selection.classed("foo", true); // 添加类
selection.classed("foo bar", true); // 添加多个类
selection.classed("foo", false); // 移除类
```

如果 `value` 是函数：

```javascript
selection.classed("active", d => d.active);
```

#### selection.property(name, value)

设置元素属性（用于 HTML 元素的特殊属性，如表单字段的 `value` 或复选框的 `checked`）。

```javascript
selection.property("checked", true);
selection.property("value", "hello");
```

#### selection.text(value)

设置文本内容。

```javascript
selection.text("Hello, world!");
selection.text(d => d.label);
```

#### selection.html(value)

设置内部 HTML。

```javascript
selection.html("Hello, <i>world</i>!");
```

**注意：** `selection.html` 仅支持 HTML 元素。SVG 元素和其他非 HTML 元素不支持 innerHTML 属性。

### 添加和移除元素

#### selection.append(type)

追加新元素。

```javascript
d3.select("div").append("p");
d3.select("svg").append("g");
```

如果 `type` 是函数：

```javascript
d3.selectAll("div").append(() => document.createElement("p"));
```

#### selection.insert(type, before)

在指定元素前插入新元素。

```javascript
d3.select("div").insert("p", ":first-child");
```

#### selection.remove()

移除选中的元素。

```javascript
selection.remove();
```

#### selection.clone(deep)

克隆选中的元素。

```javascript
selection.clone(true); // 深度克隆
```

### 排序和重排

#### selection.sort(compare)

排序选择集。

```javascript
selection.sort((a, b) => d3.ascending(a.value, b.value));
```

#### selection.order()

重新插入元素，使文档顺序与选择顺序匹配。

```javascript
selection.order();
```

#### selection.raise()

将每个选中的元素重新插入为其父元素的最后一个子元素。

```javascript
selection.raise();
```

#### selection.lower()

将每个选中的元素重新插入为其父元素的第一个子元素。

```javascript
selection.lower();
```

### 调用函数

#### selection.call(function)

调用指定的函数，将选择集作为参数传递。

```javascript
selection.call(d3.zoom().on("zoom", zoomed));

// 等价于
const zoom = d3.zoom().on("zoom", zoomed);
zoom(selection);
```

这对可重用组件很有用：

```javascript
function customize(selection) {
  selection
    .attr("class", "custom")
    .style("color", "red");
}

selection.call(customize);
```

### 创建元素

#### d3.create(name)

创建一个包含指定名称的分离元素的单元素选择集。

```javascript
d3.create("svg"); // 等价于 svg:svg
d3.create("svg:svg"); // 更明确
d3.create("svg:g"); // SVG G 元素
```

---

## 5. SVG 操作

### d3.line() - 线生成器

线生成器生成样条线或折线，如折线图中所示。

#### 创建线生成器

```javascript
const line = d3.line()
  .x(d => x(d.Date))
  .y(d => y(d.Close));
```

或使用构造函数参数：

```javascript
const line = d3.line(d => x(d.Date), d => y(d.Close));
```

#### 生成路径

```javascript
svg.append("path")
  .attr("d", line(data))
  .attr("stroke", "currentColor");
```

如果线生成器有上下文，则线条作为路径方法调用序列渲染到此上下文，此函数返回 void。否则，返回路径数据字符串。

#### 配置方法

##### line.x(x)

设置 x 访问器。

```javascript
line.x(d => x(d.Date));
```

默认：

```javascript
function x(d) {
  return d[0];
}
```

##### line.y(y)

设置 y 访问器。

```javascript
line.y(d => y(d.Close));
```

默认：

```javascript
function y(d) {
  return d[1];
}
```

##### line.defined(defined)

设置定义访问器。

```javascript
line.defined(d => !isNaN(d.Close));
```

对于输入数据数组中的每个元素调用定义访问器。如果返回真值，则评估 x 和 y 访问器并将点添加到当前线段。否则，跳过该元素，结束当前线段，并为下一个定义的点生成新的线段。

默认：

```javascript
function defined() {
  return true;
}
```

##### line.curve(curve)

设置曲线工厂。

```javascript
line.curve(d3.curveStep);
line.curve(d3.curveCardinal);
line.curve(d3.curveLinear); // 默认
```

##### line.context(context)

设置上下文。

```javascript
const context = canvas.getContext("2d");
line.context(context);
```

如果上下文不为 null，则生成的线条作为路径方法调用序列渲染到此上下文。否则，返回表示生成的线条的路径数据字符串。

##### line.digits(digits)

设置小数点后的最大位数。

```javascript
line.digits(3); // 默认 3
```

此选项仅在关联的上下文为 null 时适用。

### d3.path() - 路径序列化

将 Canvas path 方法调用序列化为 SVG 路径数据。

```javascript
const path = d3.path();
path.moveTo(0, 0);
path.lineTo(100, 100);
path.closePath();
const d = path.toString(); // "M0,0L100,100Z"
```

**方法：**
- `path.moveTo(x, y)`
- `path.closePath()`
- `path.lineTo(x, y)`
- `path.quadraticCurveTo(cpx, cpy, x, y)`
- `path.bezierCurveTo(cpx1, cpy1, cpx2, cpy2, x, y)`
- `path.arc(x, y, radius, startAngle, endAngle)`
- `path.arcTo(x1, y1, x2, y2, radius)`
- `path.rect(x, y, w, h)`
- `path.toString()` - 返回路径数据字符串

### SVG Marker - 箭头标记

#### 定义标记

在 SVG 的 `<defs>` 元素中定义标记：

```javascript
svg.append("defs").append("marker")
  .attr("id", "arrow")
  .attr("viewBox", "0 -5 10 10")
  .attr("refX", 15)
  .attr("refY", -1.5)
  .attr("markerWidth", 6)
  .attr("markerHeight", 6)
  .attr("orient", "auto")
  .append("path")
  .attr("d", "M0,-5L10,0L0,5");
```

#### 使用标记

将标记应用到路径或线条上：

```javascript
// 在路径末端添加箭头
path.attr("marker-end", "url(#arrow)");

// 在路径起点添加箭头
path.attr("marker-start", "url(#arrow)");

// 在每个顶点添加箭头
path.attr("marker-mid", "url(#arrow)");
```

#### 标记属性

- `id` - 标记的唯一标识符
- `viewBox` - 标记的坐标系统
- `refX` - 标记的参考点 x 坐标
- `refY` - 标记的参考点 y 坐标
- `markerWidth` - 标记的宽度
- `markerHeight` - 标记的高度
- `orient` - 标记的方向（"auto" 自动旋转）

### 组合使用示例

#### 带箭头的力导图

```javascript
// 定义箭头标记
svg.append("defs").append("marker")
  .attr("id", "arrowhead")
  .attr("viewBox", "-10 -5 10 10")
  .attr("refX", 0)
  .attr("refY", 0)
  .attr("markerWidth", 6)
  .attr("markerHeight", 6)
  .attr("orient", "auto")
  .append("path")
  .attr("d", "M-10,-5L0,0L-10,5")
  .attr("fill", "#999");

// 创建链接
const link = svg.append("g")
  .selectAll("line")
  .data(links)
  .enter().append("line")
  .attr("stroke", "#999")
  .attr("marker-end", "url(#arrowhead)");

// 创建节点
const node = svg.append("g")
  .selectAll("circle")
  .data(nodes)
  .enter().append("circle")
  .attr("r", 5)
  .call(d3.drag()
    .on("start", dragstarted)
    .on("drag", dragged)
    .on("end", dragended));

// 力导图模拟
const simulation = d3.forceSimulation(nodes)
  .force("link", d3.forceLink(links))
  .force("charge", d3.forceManyBody())
  .force("center", d3.forceCenter(width / 2, height / 2))
  .on("tick", ticked);

function ticked() {
  link
    .attr("x1", d => d.source.x)
    .attr("y1", d => d.source.y)
    .attr("x2", d => d.target.x)
    .attr("y2", d => d.target.y);

  node
    .attr("cx", d => d.x)
    .attr("cy", d => d.y);
}
```

---

## 参考资料

- [D3.js 官方文档](https://d3js.org/)
- [D3 Zoom API](https://d3js.org/d3-zoom)
- [D3 Force API](https://d3js.org/d3-force)
- [D3 Hierarchy API](https://d3js.org/d3-hierarchy)
- [D3 Selection API](https://d3js.org/d3-selection)
- [D3 Shape API](https://d3js.org/d3-shape)
