# Mermaid 图表绘制指南

## 快速参考

| 图表类型 | 适用场景 | 语法 |
|---------|---------|------|
| 流程图 | 展示流程、步骤 | `flowchart TD` / `flowchart LR` |
| 时序图 | 展示交互顺序 | `sequenceDiagram` |
| 状态图 | 展示状态转换 | `stateDiagram-v2` |
| 类图 | 展示类结构 | `classDiagram` |
| 思维导图 | 展示层次 | `mindmap` |

## 流程图

### 基础

```mermaid
flowchart TD
    A[开始] --> B{判断}
    B -->|是| C[操作1]
    B -->|否| D[操作2]
    C --> E[结束]
    D --> E
```

### 子图

```mermaid
flowchart TB
    subgraph Layer1["层1"]
        A[组件1]
        B[组件2]
    end
    subgraph Layer2["层2"]
        C[组件3]
    end
    Layer1 --> Layer2
```

### 样式

```mermaid
flowchart LR
    A[节点1] --> B[节点2]
    A:::style1
    B:::style2

    classDef style1 fill:#e3f2fd,stroke:#2196f3
    classDef style2 fill:#e8f5e9,stroke:#4caf50
```

## 时序图

### 基础

```mermaid
sequenceDiagram
    participant A as 用户
    participant B as 系统

    A->>B: 请求
    activate B
    B-->>A: 响应
    deactivate B
```

### 高级

```mermaid
sequenceDiagram
    participant A as 用户
    participant B as 系统
    participant C as 数据库

    A->>B: 请求
    activate B

    alt 缓存命中
        B->>B: 返回缓存
    else 缓存未命中
        B->>C: 查询
        C-->>B: 数据
    end

    B-->>A: 响应
    deactivate B
```

## 状态图

```mermaid
stateDiagram-v2
    [*] --> State1
    State1 --> State2: 事件1
    State2 --> State3: 事件2
    State3 --> [*]
```

## 类图

```mermaid
classDiagram
    class Animal {
        +String name
        +eat()
    }
    class Dog {
        +bark()
    }
    Animal <|-- Dog
```

## 思维导图

```mermaid
mindmap
  root((主题))
    分支1
      子分支1.1
      子分支1.2
    分支2
      子分支2.1
```

## 颜色参考

- 蓝色: `#e3f2fd` (背景), `#2196f3` (边框)
- 绿色: `#e8f5e9` (背景), `#4caf50` (边框)
- 橙色: `#fff4e1` (背景), `#ffa726` (边框)
- 红色: `#ffebee` (背景), `#f44336` (边框)
- 紫色: `#f3e5f5` (背景), `#9c27b0` (边框)

## 最佳实践

1. **简洁明了** - 一个图表表达一个核心概念
2. **样式统一** - 使用一致的颜色和样式
3. **标注完整** - 添加必要的注释和说明
4. **节点清晰** - 使用明确的节点名称
5. **层次清晰** - 合理使用子图和分组

参考：[Mermaid 官方文档](https://mermaid.js.org/)
