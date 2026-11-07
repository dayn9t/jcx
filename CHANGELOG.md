# Changelog

本项目变更记录。参考 [Keep a Changelog](https://keepachangelog.com/)，版本遵循 SemVer。

## [Unreleased]

依据参考项目 `j-cc`（现代化 Claude Code 配置标准）进行的现代化改造。

### Fixed
- `PRecord` 导入错误（`db/record.py` 缺定义，导致 `api` 模块无法导入）
- `data/split.py` 的 `raise "Unknown type"`（Python3 非法，改 `raise TypeError`）
- `JdbCounter` 类型 bug（`int` 非 BaseModel，`test_counter` panic；新增 `JsonVariant[T]` + PEP 695 `RedisVariant` + TypeAdapter `RedisDb`）
- `db/record.py` 中 `RecordFilter` 重复定义
- `api/dao_client.py` 的 `ResultE` 类型与实际 `Err` 载荷不符（`Result[T, Exception]` → `Result[T, str]`）
- `text/txt_json5.py` 的 `load_txt` 与 `txt_json.py` 完全重复
- 无意义 `assert self`（progress_meter、_dao_list）
- `ItemDao`/`ItemListDao` 的 B024（ABC 无 abstract method）
- 拼写错误 `cx_hisotry_clean.py` → `cx_history_clean.py`

### Changed
- 声明缺失运行时依赖：`cattrs`、`flask-restx`、`rich`
- 移除未使用依赖：`pydantic-extra-types`、`interval`、`numpy`、`sh`
- `data/split.py` 改用标准库 `random`（移除 numpy 重依赖）
- `sys/fs.py` 的 `du` 改用 `subprocess`（移除 `sh` 库）
- `db/rdb` 用 TypeAdapter 重构，支持 int/str/BaseModel 等任意类型
- `ruff.toml` 忽略中文全角标点误报（RUF001/002/003）
- `pyproject.toml` 的 `description` 占位符修正

### Removed
- 实验脚本：`util/mutithread`、`util/array`、`util/trace`、`net/mqtt/mqtt_c`、`net/mqtt/mqtt_s`、`db/rdb/mutithread`
- 死代码 `common.py`（`JCX_ASSERTS` 无引用且指向不存在的 `assets/` 目录）
- 生产模块的 `if __name__` demo 块与残留 `print`

### Added
- `svc/` 微服务基建模块（2026-11-07 上提纪律首例：自下游 avs-common 上提并剥离重写，零下游命名/路径假设）：`paths`（可执行位→树根反解，深度/标记双策略参数化 + 树内 `*_path` 相对解析、绝对值拒收）、`config`（分层加载：层序可配、首层胜出、缺失回退、损坏即报禁静默，json5+yaml 双格式）、`app`（FastAPI 壳：healthz/readyz + cfg 注入 + lifespan 透传）；fastapi/pyyaml 走 `svc` extra，不让全库用户背负
- `CLAUDE.md`（项目入口，< 100 行）
- `.claude/settings.json`（权限白名单）
- `LICENSE`（MIT）
- `CHANGELOG.md`
- `.planning/modernization-plan.md`（改造进度跟踪）

## [0.5.6] - 2026-03-23

Phase 1-4 重构：基础修复、安全健壮、质量基础设施、类型安全与文档。详见 `.planning/`。
