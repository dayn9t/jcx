# Quick Task 1: 定义 Pydantic V2 不可变枚举基类 - Context

**Gathered:** 2026-03-23
**Status:** Ready for planning

<domain>
## Task Boundary

定义 Pydantic V2 风格的不可变枚举基类，包括：
- `EnumItem`: 不可变枚举项数据结构（使用 FrozenModel）
- `PydanticEnum`: 通用枚举基类，提供 value_int, name_str, description 属性

</domain>

<decisions>
## Implementation Decisions

### 实现方式
- 直接继承 `FrozenModel` 实现不可变特性
- 配置 `model_config = {"extra": "forbid"}` 禁止额外字段

### 字段设计
- 基础三字段：`value: int`, `name: str`, `description: str = ""`
- 保持简洁，不添加 alias 或 deprecated 字段

### 序列化支持
- 使用 Pydantic 默认序列化（model_dump, model_validate）
- 不添加自定义序列化逻辑

### Claude's Discretion
- 文件位置：根据项目结构选择合适位置
- 测试策略：基本单元测试覆盖

</decisions>

<specifics>
## Specific Ideas

用户提供了完整代码示例：
- EnumItem 继承 FrozenModel
- PydanticEnum 使用 EnumItem 作为 value
- 属性：value_int, name_str, description

</specifics>
