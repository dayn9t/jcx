# TODO

## 待办

### 代码质量（持续迭代）
- 补充关键公开 API 的 docstring（D100/D103；自解释函数按 j-coding-style「仅记录非显而易见」可省）
- PEP 695 泛型/类型别名现代化（UP040/UP046：旧式 `TypeVar` → `class X[T]` / `type T = ...`）
- `ui/progress_meter` 等低覆盖模块补类型注解与 docstring

### 功能
- `api` 模块：flask-restx 文档动态生成（`@ns.doc` 装饰器，参考 attr fields）
- `RedisCounter` 集成测试（需 redis 服务，当前无测试覆盖）

## 参考

- 工具链：uv / ruff / pyright / pytest
- 现代化改造进度：`.planning/modernization-plan.md`
