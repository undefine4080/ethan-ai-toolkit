# 研究报告模板

> 使用此模板生成统一格式的代码研究报告

## 报告结构

### 必需章节

1. **概述** - 功能定义、核心特性、应用场景
2. **核心架构** - 系统架构图、模块依赖、代码组织
3. **关键组件** - 组件清单、组件详解
4. **数据结构** - 类型定义、数据流
5. **核心流程** - 执行流程、时序图、状态图
6. **总结** - 核心优势、架构评价

### 可选章节

- 状态管理
- 集成关系
- 设计模式
- 代码示例
- 最佳实践

## Mermaid 图表使用

### 架构图

```mermaid
flowchart TB
    subgraph Layer1["层1"]
        A[组件]
    end
    subgraph Layer2["层2"]
        B[组件]
    end
    Layer1 --> Layer2
```

### 流程图

```mermaid
flowchart TD
    A[开始] --> B{判断}
    B -->|是| C[操作1]
    B -->|否| D[操作2]
```

### 时序图

```mermaid
sequenceDiagram
    participant A as 角色1
    participant B as 角色2
    A->>B: 请求
    B-->>A: 响应
```

### 状态图

```mermaid
stateDiagram-v2
    [*] --> State1
    State1 --> State2: 事件
    State2 --> [*]
```

### 思维导图

```mermaid
mindmap
  root((主题))
    分支1
    分支2
```

详细参考：[Mermaid 图表指南](mermaid-guide.md)

## 代码引用格式

```typescript
// 文件位置: path/to/file.ts:行号

class ClassName {
  // 关键方法
  method() {
    // 实现
  }
}
```

## 表格使用

| 组件 | 文件 | 职责 |
|------|------|------|
| 组件A | path/a.ts | 说明 |
| 组件B | path/b.ts | 说明 |

## 质量检查清单

- [ ] 研究主题准确
- [ ] 覆盖主要功能
- [ ] 图表清晰完整
- [ ] 代码引用正确
- [ ] Mermaid 语法正确
- [ ] 有深度见解
