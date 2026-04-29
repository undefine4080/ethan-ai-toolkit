# Next.js 评审指南

依赖：react.md

<!--
加载本文档时，SKILL.md 会同时加载 react.md。
本文档只覆盖 Next 特有的评审维度，不重复 React 通用部分。
-->

## 版本覆盖范围

- 主要覆盖：**Next 13.4+ App Router**（RSC、Server Actions、新缓存模型）
- 兼容提及：Next 12-13 Pages Router 的部分要点
- 不覆盖：Next 11 及更早版本

评审前应明确用户项目是 App Router 还是 Pages Router，两者差异巨大。

---

## 核心反模式

### 反模式 1：Server/Client Components 边界混乱

**现象**：不清楚 Server 和 Client 组件的使用边界，导致大量不必要的 `"use client"` 或反之。

**为什么是问题**：
- 滥用 `"use client"` 让整棵子树失去 RSC 收益（bundle 变大、可以 server 侧渲染的东西被推到 client）
- 反过来，该用 client 的（有交互、用了浏览器 API、用了 hook）却声明成 server，运行时报错

**代码信号**：
- **根布局 / 根页面直接 `"use client"`**：几乎一定是架构错误，让整个 app 丧失 RSC 收益
- Client 组件里 `import` 了大量 server-only 代码（数据库客户端、server SDK）
- Server 组件里用了 `useState` / `useEffect` / 事件处理
- 文件顶部 `"use client"` 但整个文件没有任何客户端交互特征

**好的模式**：
- 默认用 Server Component
- 把 client 边界推到**树的叶子**（按钮、表单、交互元素），而不是放在顶层
- Server 组件可以作为 Client 组件的 children 传入，避免把整棵子树 client 化

### 反模式 2：Data Fetching 位置不当

**现象**：数据获取在错误的层级发生。

**代码信号**：
- **Client 组件里 `useEffect` + `fetch` 获取初始数据**：App Router 下应该用 RSC 直接在 server 取数
- **Server 组件里用 client-side 数据库 SDK**：应该用 server SDK 或直接查询
- **重复获取同样的数据**：Next 的 `fetch` 自带请求去重，但只在同一次渲染内。跨组件的数据共享应该用 RSC 的自然传递

### 反模式 3：缓存模型使用不当

Next 14/15 的缓存是**出了名的复杂**。评审时重点关注：

**代码信号**：
- 到处写 `export const dynamic = 'force-dynamic'` 取消缓存：多半是不理解缓存模型在"全体拉爆"
- 反过来，数据明显应该动态却被静态缓存了（用户相关数据、带 cookie 的页面）
- `fetch(url, { next: { revalidate: N } })` 的 N 是拍脑袋的数字，没有业务理由
- 用了 `revalidatePath` / `revalidateTag` 但不清楚它影响哪些页面

**判断**：项目如果对缓存感到困惑，要单独提一条"缓存策略缺乏系统性思考"，建议先梳理哪些数据是静态、哪些是动态。

### 反模式 4：`"use client"` 边界泄漏

**现象**：一个底层 UI 组件被声明成 client，导致所有用它的组件都被强制 client 化。

**代码信号**：
- 一个 `<Button>` 组件里用了 `onClick` 所以声明 `"use client"` → 所有用到 Button 的页面都变 client
- 实际上 `<Button>` 如果只是把 `onClick` 传给原生 `<button>`，未必需要 `"use client"`（取决于具体写法）

**评审要点**：client 边界应该"向叶子推"，而不是"向根推"。

### 反模式 5：Metadata / SEO 处理缺失

**现象**：页面没有 `generateMetadata` 或 `metadata` 导出。

**代码信号**：
- 业务页面只有 `export default function Page()`，没有任何元信息
- 标题、描述依赖客户端 JS 设置 → 爬虫拿不到

### 反模式 6：Route Handler 滥用

**现象**：用 API Route Handler (`route.ts`) 做其实可以直接在 Server Component / Server Action 里做的事。

**为什么是问题**：
- Server Component 已经在 server 跑，再通过 fetch 调自己的 API 是绕远路
- Server Action 比手写 POST handler 更简洁且类型安全

**例外**：需要给第三方暴露 API、webhook、需要流式响应等，确实需要 Route Handler。

### 反模式 7：Loading / Error 约定未利用

**现象**：没有使用 Next App Router 提供的 `loading.tsx` / `error.tsx` / `not-found.tsx` 约定。

**代码信号**：
- 手写 loading state 散落在每个组件
- 没有 error boundary，出错直接白屏

### 反模式 8：Client / Server 之间传递不可序列化数据

**现象**：从 Server Component 给 Client Component 传递函数、class 实例、Date 之类。

**代码信号**：
- `<ClientComp callback={() => ...} />` 从 server 组件传下去 → 报错
- 把 server 侧的 class 实例整个传给 client

---

## 优秀范式

### 范式 1：Server-first，Client 按需

默认所有组件都是 Server Component。只有当需要以下能力时才加 `"use client"`：
- 浏览器 API（localStorage、window）
- 事件监听器
- React hooks（`useState`、`useEffect` 等）
- 只存在于 client 的库

### 范式 2：数据获取在它该在的地方

- 页面级数据：Server Component 直接取
- 交互后才需要的数据：Server Action 或 API Route
- 实时/频繁更新：client-side + react-query 或类似

### 范式 3：利用 Parallel Routes / Intercepting Routes

对于复杂布局和模态框场景，用 Next 提供的路由能力，而不是手写状态管理。

---

## 评审 Checklist

- [ ] 根 layout 是 Server Component 吗？
- [ ] `"use client"` 只在必要处出现吗？
- [ ] 数据获取是否优先在 Server Component 发生？
- [ ] 缓存策略是否有系统性理解（不是到处 `force-dynamic` 或拍脑袋 revalidate）？
- [ ] 有没有利用 `loading.tsx` / `error.tsx` / `not-found.tsx`？
- [ ] 页面是否有 `metadata` / `generateMetadata`？
- [ ] 从 server 传 client 的 props 是否都可序列化？
- [ ] Server Action / Route Handler 选用是否合理？

---

## 严重度参考

| 现象 | 建议严重度 |
|---|---|
| 根布局被 `"use client"` 污染整棵树 | 🟡 Major |
| Server Component 和 Client Component 边界混乱导致构建错误 | 🔴 Critical |
| 关键页面缺 metadata（SEO 敏感业务） | 🟡 Major |
| 缓存策略混乱、到处 `force-dynamic` | 🟡 Major |
| 数据在 client 用 useEffect+fetch 拿（App Router 项目） | 🟡 Major |
| 没用 `loading.tsx` / `error.tsx` 约定但手写了 | 🟢 Minor |
| client 边界可以进一步推向叶子 | 💭 Nit |
