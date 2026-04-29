# React 评审指南

依赖：无

## 版本覆盖范围

- 主要覆盖：React 18+（含 Concurrent 特性、`useId`、`useSyncExternalStore`、Server Components 基础概念）
- 兼容提及：React 16.8+ 的 hooks 范式
- 不覆盖：class component 时代的问题（project 里如果还有大量 class component，该话题单独处理）

---

## 核心反模式

### 反模式 1：`useEffect` 滥用

**现象**：`useEffect` 被用来做各种不该它做的事。

**为什么是问题**：useEffect 是"**与 React 树外部世界同步**"的逃生舱，不是通用副作用钩子。滥用会引发多次渲染、竞态、心智负担。

**代码信号**（都是典型滥用）：
- `useEffect` 只为了根据 props/state **派生状态**：应该用直接计算（或 `useMemo`）。派生状态**几乎永远不需要 `useEffect` + `setState`**。
- `useEffect` 里**响应用户事件**触发副作用：应该写在事件处理函数里
- `useEffect` 依赖 `[]` 里跑异步函数拿数据：考虑用 Suspense、react-query / SWR、或 RSC
- 多个 `useEffect` **互相触发**形成链：重新设计数据流
- `useEffect` 里设置了另一个会导致重渲染的 state

**判断依据**：React 官方文档《You Might Not Need an Effect》是评审的第一参考。

### 反模式 2：不必要的 `useMemo` / `useCallback`

**现象**：到处包 `useMemo` / `useCallback`，理由是"性能优化"。

**为什么是问题**：
- 绝大多数计算 React 重新跑一遍的成本远低于 `useMemo` 缓存比较的成本
- `useCallback` 只在"传给了 `React.memo` 的子组件"或"作为另一个 hook 的依赖"时才有价值，否则是无效包裹
- 过度 memo 让代码可读性下降，且容易写错依赖数组引入 bug

**代码信号**：
- 组件里几乎每个函数都包 `useCallback`，但子组件没有 `React.memo`
- `useMemo` 用于非常廉价的计算（简单加减、三元判断）
- `useMemo` 依赖数组里明显漏了东西（闭包陷阱）

### 反模式 3：Context 滥用

**现象**：把所有需要跨层级传的数据都塞进一个大 Context。

**为什么是问题**：
- Context 变化会触发**所有**使用它的组件重渲染，即使只是关心其中一个字段
- 大 Context 让组件失去"只依赖自己需要的数据"的清晰性

**代码信号**：
- 一个 `AppContext` 里塞了 user、theme、locale、modal state 等互不相关的东西
- 某个组件只用 Context 里的 1 个字段，但整个 Context 变就重渲
- 本来可以 props drilling 两层就解决的，用 Context 绕远路

**更好的方式**：多个小 Context（按关注点划分）、状态管理库（Zustand / Jotai）、或者干脆 props drilling。

### 反模式 4：条件 hook / 循环 hook

**现象**：违反 Rules of Hooks。

**为什么是问题**：这是 React 的**硬约束**，违反会直接破坏 hook 的识别机制。

**代码信号**：
- `if (cond) { useEffect(...) }`
- `items.forEach(item => useSomething(item))`
- 组件 early return **之后**还有 hook

此类问题应该被 ESLint `react-hooks/rules-of-hooks` 捕获，如果项目连这个 lint 都没开，单独提一条。

**严重度**：🔴 Critical

### 反模式 5：`key` 用数组索引

**现象**：列表渲染用 `key={index}`。

**为什么是问题**：当列表增删改时，React 的 diff 会错位，导致组件状态错乱、动画错乱、input 值串位。

**代码信号**：`.map((item, index) => <Foo key={index} ... />)`

**例外**：纯静态列表（永不变化、不重排）可以用 index，但强烈建议用稳定 id。

### 反模式 6：业务逻辑和 UI 深度耦合

**现象**：组件里直接写网络请求、状态管理、数据转换。

**为什么是问题**：组件重写时业务逻辑也要重写；业务逻辑无法单独测试；复用困难。

**代码信号**：
- 组件文件超过 300 行且不是组合容器
- 一个组件里同时有：`fetch`/`axios` 调用、数据格式化、业务规则判断、JSX

**更好的方式**：自定义 hooks 承载业务 + 数据，组件只负责渲染。

### 反模式 7：受控/非受控组件混乱

**现象**：input 既有 `value` 又没有 `onChange`；或 `defaultValue` 和 `value` 同时传入。

**代码信号**：
- `<input value={x} />` 没有 `onChange`（React 会 warning）
- 组件内部 `useState` + props 传入的 value 互相冲突

### 反模式 8：状态放得太高 / 太低

**现象**：
- 局部状态被提升到根组件（无必要的 props drilling）
- 共享状态散落在多个组件各自持有副本

**判断**：状态应该放在"**能访问到所有需要它的组件的最近公共祖先**"，不要更高也不要更低。

---

## 优秀范式

### 范式 1：自定义 hook 分层

业务逻辑封装为自定义 hook，组件只做组合和渲染。好的项目能看到清晰的 hook 层次：

- 原子 hook：`useUser`、`useProducts`
- 组合 hook：`useCheckoutFlow`（组合多个原子 hook）
- UI 组件消费组合 hook

### 范式 2：状态分类管理
React 里有四种状态，评审时留意项目是否有意识区分：

| 状态类型 | 管理方式 |
|---|---|
| 服务器状态 | react-query / SWR（不要手写 useState + useEffect） |
| URL 状态 | 路由库 / `useSearchParams` |
| 全局 UI 状态 | Zustand / Jotai / Context |
| 局部组件状态 | `useState` / `useReducer` |

把服务器状态当作局部状态管理（用 useState 存 API 数据）是非常常见的坏气味。

### 范式 3：Composition over Conditional Rendering

不要写大量 `{isA ? <FooA /> : isB ? <FooB /> : <FooC />}`。考虑把它变成一个组件接受 props，或用 `children` 组合。

---

## 评审 Checklist

- [ ] 是否有违反 Rules of Hooks 的代码？
- [ ] `useEffect` 是否被用于不该它的场景？
- [ ] `useMemo`/`useCallback` 是否过度？
- [ ] 列表渲染的 `key` 是否稳定？
- [ ] Context 是否按关注点拆分？
- [ ] 服务器状态是否用了合适的库（react-query 等）？
- [ ] 组件是否过重（业务混在 UI 里）？
- [ ] 错误边界（Error Boundary）是否存在？
- [ ] Loading / Empty / Error 三态是否处理？

---

## 严重度参考

| 现象 | 建议严重度 |
|---|---|
| 违反 Rules of Hooks | 🔴 Critical |
| 核心数据流用 useEffect 链触发的错误架构 | 🟡 Major |
| 服务器状态用 useState+useEffect 手动管理 | 🟡 Major |
| 大 Context 导致全局重渲染 | 🟡 Major |
| 缺失 Error Boundary 且项目规模不小 | 🟡 Major |
| `key={index}` 但列表会变化 | 🟡 Major |
| 过度 useMemo/useCallback | 🟢 Minor |
| 局部状态位置略有不当 | 💭 Nit |
