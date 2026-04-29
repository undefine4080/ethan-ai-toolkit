# Vue 3 评审指南

依赖：无

## 版本覆盖范围

- 主要覆盖：Vue 3.3+（Composition API、`<script setup>`、`defineProps` / `defineEmits` / `defineModel`）
- 兼容提及：Vue 3.0+ 的通用 Composition API 范式
- 不覆盖：Vue 2、class-style component、以 Options API 为主的老项目迁移细节

---

## 核心反模式

### 反模式 1：滥用 `watch`，把派生状态写成副作用链

**现象**：本来可以直接从已有状态推导出来的值，被写成 `watch` 监听后再去改另一个 `ref`。

**为什么是问题**：

- `watch` 是副作用工具，不是通用的状态同步器
- 派生状态写成 `watch` 会制造额外状态、副作用链和时序依赖
- 多个 `watch` 串起来后，组件行为会变得很难推理

**代码信号**：

- `watch(() => props.xxx, value => derived.value = transform(value))`
- 一个组件里出现多个 `watch`，互相修改别的 `ref`
- `watch` 里只做纯计算，没有任何外部副作用

**更好的方式**：能用 `computed` 的地方优先用 `computed`。`watch` 只留给真正的副作用，如请求、持久化、桥接第三方库。

### 反模式 2：错误解构响应式对象，导致响应性丢失

**现象**：直接解构 `props` 或 `reactive()` 返回的对象，然后把解构出来的值当作响应式数据使用。

**为什么是问题**：Vue 的响应式依赖 getter/setter 追踪。直接解构会把值取出来，后续更新不再联动。

**代码信号**：

- `const { foo } = props`
- `const { form } = reactiveState`
- 解构后直接在 template 或 `watch` / `computed` 里使用，但没有 `toRefs` / `toRef`

**更好的方式**：

- 保持 `props.xxx` 访问
- 或显式使用 `toRefs(props)` / `toRef(state, 'foo')`

### 反模式 3：`ref` / `reactive` 选型混乱

**现象**：所有状态都一股脑塞进 `reactive`，或反过来把复杂对象拆成大量离散 `ref`，没有明确标准。

**为什么是问题**：

- `reactive` 适合相关性强的对象状态，但过大对象会让职责模糊
- 大量离散 `ref` 会让一个表单或流程状态变成碎片，难以整体理解
- 选型混乱通常反映状态建模本身没有想清楚

**代码信号**：

- 一个组件里有十几个互相关联的 `ref`
- 一个超大 `reactive({ ... })` 承载了 UI、请求、业务流程等多个层面的状态
- 代码里频繁 `.value` / 非 `.value` 混用，读起来没有一致性

**判断原则**：

- 单值或独立状态：优先 `ref`
- 强相关的一组字段：考虑 `reactive`
- 不论选哪种，关键是让状态模型能被一句话讲清楚

### 反模式 4：直接修改 props 或用 props 当本地可变状态

**现象**：子组件直接改 props，或把 props 的对象当本地状态随手改。

**为什么是问题**：Vue 的数据流应保持单向。直接改 props 会让父子边界模糊，也会制造难以追踪的副作用。

**代码信号**：

- `props.user.name = 'x'`
- `props.visible = false`
- 没有显式 `emit`，而是依赖对象引用穿透来回写

**更好的方式**：

- 用 `emit` 把变更意图抛回父组件
- 需要本地可编辑副本时，显式创建本地状态并说明同步策略

### 反模式 5：Composable 隐藏依赖过多

**现象**：一个 composable 看起来像普通函数，实际内部偷偷依赖路由、Pinia、provide/inject 或全局单例。

**为什么是问题**：

- 输入输出不清晰，读函数签名看不出依赖
- 复用范围被锁死，只能在特定上下文里调用
- 测试困难，组合关系不透明

**代码信号**：

- `useXxx()` 里直接读取多个 store、router、window、localStorage
- composable 调用前必须先执行另一个 setup，否则运行时报错
- composable 返回值和副作用边界不清晰

**更好的方式**：

- 通过参数显式传入依赖
- 把副作用和纯计算拆开
- 让 composable 的职责能用一句话描述

### 反模式 6：`provide` / `inject` 被当作随手的全局状态通道

**现象**：本来只是父子两三层传值，却直接上 `provide/inject`；或者用它承载大型共享业务状态。

**为什么是问题**：

- 依赖关系变隐式，组件签名不再完整
- 调试时很难看出值从哪里来
- 大型共享状态通常更适合 Pinia 或明确的组合层

**代码信号**：

- 组件不收 props，却大量 `inject('xxx')`
- 同一个 key 在多个地方被 provide，作用域复杂
- `inject` 的对象被下游随意修改

### 反模式 7：模板层逻辑过重

**现象**：template 里塞了复杂三元、链式调用、多个条件拼接，必须来回看 script 才能理解。

**为什么是问题**：模板应该主要表达结构。业务判断太多会让渲染层失去可读性。

**代码信号**：

- `v-if` / `v-else-if` 链很长
- 模板里直接写 `items.filter(...).map(...).slice(...)`
- class / style 绑定里放了复杂逻辑

**更好的方式**：把复杂判断上移为 `computed` 或具名辅助函数，让 template 保持声明式。

### 反模式 8：`v-if` 和 `v-for` 写在同一节点，或列表 key 不稳定

**现象**：列表渲染和条件渲染叠在一起，或者用 index 当 key。

**为什么是问题**：

- `v-if` 和 `v-for` 同节点时优先级和语义都容易让人困惑
- 不稳定 key 会导致 DOM 复用错位，表单和局部状态容易串位

**代码信号**：

- `<li v-for="(item, index) in items" :key="index" v-if="item.visible">`
- 列表中存在插入、删除、排序，却依然用 index 作为 key

**更好的方式**：

- 先在 script/computed 里过滤，再在 template 里循环
- key 优先使用稳定业务 id

### 反模式 9：Pinia store 成为上帝状态容器

**现象**：把页面局部状态、表单草稿、弹窗开关、服务器缓存、领域状态全都塞进一个 store。

**为什么是问题**：

- store 边界变得模糊，任何功能都可能被它影响
- 组件和 store 耦合过重，迁移和测试都困难
- 本地瞬时状态被提升成全局状态后，复杂度会上升而不是下降

**代码信号**：

- 一个 store 文件很大，字段和 action 涵盖多个无关模块
- 页面离开后仍残留本地 UI 状态在 store 中
- 组件几乎只是在 store 上做薄包装

---

## 优秀范式

### 范式 1：`computed` 优先，`watch` 克制

凡是派生值，优先建模为 `computed`。只有当需要与 Vue 响应式系统之外的世界同步时，才使用 `watch` / `watchEffect`。

### 范式 2：以 composable 组织业务能力

好的 Vue 3 项目通常能看到清晰的 composable 分层：

- 原子 composable：`useUser`、`usePagination`
- 业务 composable：`useCheckoutFlow`
- 组件负责组合和渲染

关键不在于抽成多少个 composable，而在于每个 composable 的职责是否单一、依赖是否显式。

### 范式 3：`<script setup>` + 显式契约

当项目使用 `<script setup>` 时，好的代码通常会：

- 用 `defineProps` / `defineEmits` 明确组件边界
- 尽量给 props / emits 补全类型
- 把组件对外能力收敛成清晰接口，而不是靠隐式约定

### 范式 4：领域状态与局部状态分层

- 局部瞬时 UI 状态留在组件内部
- 跨页面、跨模块共享的领域状态进 Pinia
- 服务器状态不要硬塞进全局 store，优先保持边界清晰

### 范式 5：模板保持声明式

优秀的 Vue 组件往往能做到：

- template 负责结构表达
- `computed` 负责派生展示数据
- composable / script 负责业务编排

这会让单文件组件虽然同时包含 template/script/style，但依然具备清晰分层。

---

## 评审 Checklist

- [ ] 是否把派生状态写成了 `watch` + `set` 链？
- [ ] 是否错误解构了 `props` 或 `reactive()`，导致响应性丢失？
- [ ] `ref` / `reactive` 的状态建模是否一致、清晰？
- [ ] 是否存在直接修改 props 的情况？
- [ ] composable 的依赖是否显式，而不是偷偷读取全局上下文？
- [ ] `provide` / `inject` 是否只用于合适的层级通信？
- [ ] template 是否过重，复杂逻辑是否可以上移到 `computed`？
- [ ] 列表渲染的 key 是否稳定？是否避免 `v-if` + `v-for` 同节点？
- [ ] Pinia store 是否职责清晰，没有沦为上帝容器？

---

## 严重度参考

| 现象 | 建议严重度 |
| --- | --- |
| 直接修改 props，破坏单向数据流 | 🟡 Major |
| 大量 `watch` 串成副作用链，核心数据流难以推理 | 🟡 Major |
| 错误解构响应式对象，导致状态不更新或行为错误 | 🟡 Major |
| Pinia store 过大，承担多个无关领域 | 🟡 Major |
| `provide` / `inject` 滥用导致依赖隐式 | 🟢 Minor |
| template 逻辑过重 | 🟢 Minor |
| 列表使用不稳定 key | 🟡 Major |
| `ref` / `reactive` 选型略显混乱 | 💭 Nit |
