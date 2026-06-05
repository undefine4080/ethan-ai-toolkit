# UI 设计规范：纸质论文阅读体验

本规范定义了论文全文翻译 HTML 文档的视觉设计标准。设计目标：**模拟阅读纸质学术论文的真实体验**——暖白纸张、衬线字体、墨水质感、书桌氛围。

HTML 构建 Agent（第 3 步）必须严格遵循本规范来实现最终页面样式。

---

## 设计理念

**纸质论文阅读**。用户打开页面的感受应该是：一张学术论文铺在温暖色调的书桌上，左侧放着目录书签，右侧放着便签笔记。正文字体是经典衬线体，强调色是学术期刊常用的暗红色，整体氛围安静沉稳。

---

## 字体体系

### 字体栈

| 用途 | 字体栈 | 说明 |
|------|--------|------|
| **正文（衬线）** | `"Crimson Pro", "Noto Serif SC", "Songti SC", "SimSun", Georgia, serif` | 英文用 Crimson Pro，中文回退到 Noto Serif SC |
| **UI 元素** | `"Atkinson Hyperlegible", "Noto Serif SC", system-ui, sans-serif` | 目录、注解标题、按钮等 UI 组件 |
| **代码** | `"SF Mono", "Fira Code", "Consolas", monospace` | 代码块和行内代码 |

### Google Fonts 加载

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Crimson+Pro:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400;1,500&family=Noto+Serif+SC:wght@400;500;600;700&family=Atkinson+Hyperlegible:wght@400;700&display=swap" rel="stylesheet">
```

### 字号体系

| 元素 | 字号 | 字重 |
|------|------|------|
| body | 17px | 400 |
| h1 | 30px | 700 |
| h2 | 22px | 700 |
| h3 | 18px | 600 |
| h4 | 16px | 600 |
| 目录链接 | 13px | 400 |
| 注解卡片标题 | 12.5px | 700 |
| 注解卡片正文 | 12.5px | 400 |
| 图片 caption | 13.5px | 400 (italic) |

---

## 配色系统

### 设计令牌（CSS 变量）

亮色主题为默认，暗色主题通过 `[data-theme="dark"]` 覆盖。

| 变量名 | 亮色值 | 暗色值 | 用途 |
|--------|--------|--------|------|
| `--desk-bg` | `#e8e0d4` | `#1a1714` | 页面整体背景（书桌颜色） |
| `--paper-bg` | `#faf6f0` | `#2a2520` | 正文区域背景（纸张颜色） |
| `--paper-bg-subtle` | `#f5f0e8` | `#322c26` | 代码块、表格头等稍深区域 |
| `--ink` | `#2c2c2c` | `#d4c9b8` | 主文字颜色（墨水） |
| `--ink-light` | `#5c5346` | `#b8a98e` | 次要文字 |
| `--ink-muted` | `#8a7e6f` | `#8a7e6f` | 辅助文字、标签 |
| `--accent` | `#8b2500` | `#c45a32` | 强调色（学术暗红） |
| `--accent-light` | `rgba(139,37,0,0.07)` | `rgba(196,90,50,0.12)` | 强调色浅底 |
| `--accent-hover` | `#a52e00` | `#d96b42` | 强调色悬停态 |
| `--rule-color` | `#d4c9b8` | `#443d35` | 分隔线、边框 |
| `--rule-color-strong` | `#b8a98e` | `#5c5346` | 粗分隔线 |
| `--toc-bg` | `rgba(245,240,232,0.85)` | `rgba(42,37,32,0.92)` | 目录栏背景（半透明+毛玻璃） |
| `--note-bg` | `rgba(245,240,232,0.7)` | `rgba(42,37,32,0.85)` | 注解栏背景 |
| `--note-card` | `#fffdf9` | `#352f28` | 注解卡片背景 |
| `--hover-bg` | `rgba(139,37,0,0.04)` | `rgba(196,90,50,0.08)` | 悬停高亮底色 |

### 阴影

| 变量名 | 亮色值 | 用途 |
|--------|--------|------|
| `--shadow-paper` | `0 1px 3px rgba(60,40,20,0.08), 0 6px 24px rgba(60,40,20,0.05)` | 正文纸张投影 |
| `--shadow-card` | `0 1px 3px rgba(60,40,20,0.06)` | 注解卡片投影 |

### 圆角

统一使用 `--radius: 3px`。极小圆角模拟纸张边缘的微妙弧度，禁止大圆角。

---

## 纹理质感

使用真实的纸张纹理照片叠加，模拟纸张纤维和微妙的表面凹凸。

### 纹理文件

`assets/smooth-white-plaster-wall.jpg` — 白色石膏墙面纹理，平铺使用。

构建 HTML 时将此图片复制到输出目录（与 HTML 同级），然后在 CSS 中引用：

```css
body::before {
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 9999;
  opacity: 0.5;
  mix-blend-mode: multiply;
  background-image: url("smooth-white-plaster-wall.jpg");
  background-size: 800px 800px;
  background-repeat: repeat;
}
```

关键参数：
- `opacity: 0.5`：让纹理清晰可见但不干扰文字阅读
- `mix-blend-mode: multiply`：纹理与底色自然融合，比纯 opacity 更逼真
- `background-size: 800px`：平铺单元大小，可根据实际纹理密度调整
- `z-index: 9999` + `pointer-events: none`：覆盖全页但不影响交互
- `position: fixed`：纹理不随滚动移动

**构建 Agent 必须在生成 HTML 时，将 `assets/smooth-white-plaster-wall.jpg` 复制到 HTML 输出目录。**

---

## 布局结构

### 三栏布局

```
┌─────────────────────────────────────────────┐
│  顶部标题栏 (sticky, 纸张色背景)              │
├────────┬──────────────────────┬──────────────┤
│ 目录栏  │  正文（纸张区域）     │ 注解栏       │
│ 240px  │  max 800px          │ 300px        │
│ 毛玻璃  │  纸张投影            │ 毛玻璃        │
│ sticky  │  纸张纹理边线        │ sticky       │
│        │                     │              │
└────────┴──────────────────────┴──────────────┘
     ↓ 暖棕书桌背景 (#e8e0d4)              ↓
```

### 关键布局参数

| 属性 | 值 |
|------|-----|
| 目录栏宽度 | 240px |
| 正文最大宽度 | 800px |
| 注解栏宽度 | 300px |
| 布局最大宽度 | 1342px（三栏之和），`margin: 0 auto` 居中 |
| 正文内边距 | 48px 56px 100px |

### 正文纸张效果

正文 `.content` 区域模拟物理纸张：
- `background: var(--paper-bg)` — 暖白纸张色
- `box-shadow: var(--shadow-paper)` — 纸张投影
- `::before` / `::after` 伪元素 — 纸张左右边缘渐变线条

### 侧栏毛玻璃效果

目录栏和注解栏使用半透明背景 + 毛玻璃：
- `background: var(--toc-bg)` — 半透明
- `backdrop-filter: blur(8px)` — 毛玻璃
- `-webkit-backdrop-filter: blur(8px)` — Safari 兼容

---

## 亮/暗主题切换

### 实现方式

通过 `<html>` 元素的 `data-theme` 属性切换：

```html
<html lang="zh-CN">                    <!-- 亮色（默认） -->
<html lang="zh-CN" data-theme="dark">  <!-- 暗色 -->
```

### 切换按钮

标题栏右侧放置主题切换按钮：
```html
<button class="theme-toggle" onclick="toggleTheme()" title="切换亮/暗主题">☀ / ☾</button>
```

### 持久化

用户偏好保存到 `localStorage`：
```javascript
function toggleTheme() {
  var html = document.documentElement;
  var isDark = html.getAttribute('data-theme') === 'dark';
  if (isDark) {
    html.removeAttribute('data-theme');
    localStorage.setItem('paper-theme', 'light');
  } else {
    html.setAttribute('data-theme', 'dark');
    localStorage.setItem('paper-theme', 'dark');
  }
}
```

页面加载时恢复偏好：
```javascript
(function() {
  var saved = localStorage.getItem('paper-theme');
  if (saved === 'dark') document.documentElement.setAttribute('data-theme', 'dark');
})();
```

### 暗色主题设计原则

- 背景是深棕色 `#1a1714`（模拟暗光下的书桌），不是纯黑
- 纸张区域是深棕 `#2a2520`（模拟暖光灯下的纸张），不是冷灰
- 文字是暖白 `#d4c9b8`（模拟墨水在暖光下的反射），不是纯白
- 强调色亮度提高至 `#c45a32`（保证暗色下的可读性）

---

## 组件样式规范

### 顶部标题栏

- 背景：纸张色 `var(--paper-bg)`
- 底部边框：`1px solid var(--rule-color)`
- 阴影：`0 2px 8px rgba(60,40,20,0.06)`
- 字体：UI 字体栈
- 内边距：`12px 28px`
- sticky 定位

### 徽章（Badge）

- 字号 11px，字重 700，大写字母
- 圆角 2px（几乎无圆角）
- 论文翻译徽章：强调色浅底 + 强调色文字 + 强调色边框
- 注解徽章：绿色系（亮色 `#3d7a4a`，暗色 `#6abf7b`）

### 目录栏

- 标题字号 11px，大写，字间距 1.5px
- 链接字号 13px，悬停时浅底高亮
- 激活项：强调色浅底 + 强调色文字 + 字重 700
- 子标题（toc-h3）：左缩进 22px，字号 12.5px

### 图片容器

- 背景：`var(--paper-bg-subtle)`
- 边框：`1px solid var(--rule-color)`
- 圆角：`var(--radius)`
- 投影：`var(--shadow-card)`
- 内边距：20px
- Caption：13.5px，斜体，左对齐

### 引用块（Blockquote）

- 左边框：`3px solid var(--accent)`（暗红强调线）
- 背景：`var(--accent-light)`
- 正文：斜体
- 圆角：右侧 `var(--radius)`

### 表格

- 使用 UI 字体栈
- 表头背景 `var(--paper-bg-subtle)`
- 行悬停 `var(--hover-bg)`

### 注解卡片

- 卡片背景：`var(--note-card)`
- 卡片边框：`1px solid var(--rule-color)`
- 悬停：阴影加深 + 边框加深
- 标题区字号 12.5px，字重 700
- 正文区字号 12.5px，使用衬线字体栈
- 展开时顶部有 `1px solid var(--rule-color)` 分隔线

### 注解引用标记（note-ref）

- 圆形，17×17px
- 背景：强调色，文字：纸张色
- 字号 10px，字重 700
- 悬停放大 1.15 倍

---

## 响应式断点

| 断点 | 行为 |
|------|------|
| `> 1100px` | 完整三栏布局 |
| `768px ~ 1100px` | 目录栏缩至 200px，注解栏隐藏（点击按钮弹出浮层），正文内边距缩小 |
| `< 768px` | 目录栏隐藏（点击按钮弹出浮层），注解栏隐藏，正文自适应全宽，标题字号缩小 |

---

## 打印样式

打印时隐藏：侧栏、标题栏、切换按钮。正文去除阴影和背景色，使用纯白背景和纯黑文字。

---

## 外部依赖

| 库 | CDN | 用途 |
|----|-----|------|
| KaTeX | `cdn.jsdelivr.net/npm/katex@0.16.9` | 数学公式渲染 |
| Crimson Pro | Google Fonts | 英文衬线正文字体 |
| Noto Serif SC | Google Fonts | 中文衬线正文字体 |
| Atkinson Hyperlegible | Google Fonts | UI 元素字体 |

---

## HTML 构建 Agent 执行检查清单

构建 HTML 时，Agent 必须确认：

- [ ] `<head>` 中包含 Google Fonts 的三个 `<link>` 标签
- [ ] CSS 变量同时定义了 `:root`（亮色）和 `[data-theme="dark"]`（暗色）
- [ ] `body::before` 包含纸张纹理叠加
- [ ] `.content` 有纸张投影和边缘伪元素
- [ ] 侧栏有 `backdrop-filter: blur(8px)` 毛玻璃效果
- [ ] 标题栏包含主题切换按钮 `<button class="theme-toggle">`
- [ ] `<script>` 中包含主题切换函数和 localStorage 持久化逻辑
- [ ] 所有颜色使用 CSS 变量，没有硬编码色值（作者信息行等 inline style 除外）
- [ ] 响应式断点覆盖 1100px 和 768px
- [ ] 打印样式正确隐藏非必要元素
