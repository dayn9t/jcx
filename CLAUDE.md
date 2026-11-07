# jcx

J 的 Python 通用工具库：Result/Option 类型、文件/时间/JSON/数据库/网络辅助。
Python 3.12，uv 管理，ruff + pyright + pytest。

## 模块

| 模块 | 职责 |
|------|------|
| `rs/` | rustshed 的 `Result`/`Option` 再导出、Protocol、RichEnum |
| `sys/` | 文件系统（fs）、OS 包比较（os_pkg） |
| `text/` | JSON/JSON5 序列化、文本 I/O |
| `time/` | ClockTime、Timer、Calendar、时间迭代器 |
| `util/` | 算法、错误处理（loguru）、泛型容器（lict） |
| `db/` | JSON 文件数据库（jdb）+ Redis（rdb）；Counter/Variant/Record |
| `api/` | REST DAO 层：flask-restx 服务端 + requests 客户端 + 任务管理 |
| `net/` | MQTT pub/sub |
| `svc/` | 微服务基建：树根反解+树内相对路径（paths）、分层配置加载（config，缺省→覆盖/损坏即报，json5+yaml）、FastAPI 壳（app，healthz/readyz+cfg 注入）；需 `svc` extra（fastapi+pyyaml） |
| `bin/` | CLI 工具（cx_task / cx_dao / cx_rename 等，typer + argparse） |
| `data/` | 数据分割工具 |

## 关键约定

- **错误处理**：用 `rustshed` 的 `Result[T, E]` / `Option[T]`，不裸抛异常（系统边界除外）。
- **类型注解**：所有函数完整注解；pyright strict 风格；PEP 695 泛型/类型别名。
- **数据模型**：Pydantic v2 `BaseModel`；不可变用 `frozen=True`。
- **配置**：Pydantic `BaseSettings`；禁止裸 `os.environ.get`。
- **日志**：loguru；禁止输出密钥/PII；生产库不用 `print`（CLI 输出除外）。
- **依赖**：uv 管理，最小依赖；每个依赖都必须被代码使用。
- **禁止**：兼容性代码、静默降级、`Any`/`**kwargs`/裸 `except`（详见全局 rule `j-coding-style`、`j-python-coding-style`）。

## 常用命令

```bash
uv sync                       # 安装/同步依赖
uv run pytest                 # 单元测试（排除 integration，覆盖率阈值 80%）
uv run pytest -m integration  # 集成测试（需 redis 等外部服务）
uv run ruff check .           # lint
uv run ruff format .          # 格式化
uv run pyright src/           # 类型检查
```

## 测试

- `tests/` 镜像 `src/jcx/` 结构。
- `@pytest.mark.integration` 标记需外部服务的测试，CI 默认排除（`-m 'not integration'`）。
- 覆盖率阈值 80%（`pyproject.toml [tool.coverage].fail_under`）。

## 规划

- `.planning/`：历史重构记录（Phase 1-4）。
- `.planning/modernization-plan.md`：当前依据 `j-cc` 标准的现代化改造进度。
