# jcx Library Refactoring

## What This Is

`jcx` 是一个 Python 工具库，提供 Rust 风格的类型安全编程模式（Option/Result）、数据存储、网络通信、时间处理等基础功能。本次重构目标是清零代码库中已识别的所有问题，提升代码质量和可维护性。

## Core Value

**质量优先** — 统一API风格、改进错误处理、确保代码正确性。所有 CONCERNS.md 中的问题必须解决。

## Requirements

### Validated

- ✓ Rust 风格类型系统 (Option/Result via rustshed) — existing
- ✓ JSON 文件数据库 (jdb) — existing
- ✓ Redis 客户端 (rdb) — existing
- ✓ REST API 客户端抽象 — existing
- ✓ MQTT 发布/订阅 — existing
- ✓ 时间/日历工具 — existing
- ✓ 文件系统工具 — existing
- ✓ CLI 工具集 (cx_rename, cx_task, cx_dao 等) — existing

### Active

- [ ] 解决所有 Tech Debt (6项)
- [ ] 修复所有 Known Bugs (2项)
- [ ] 解决所有 Security Risks (5项)
- [ ] 解决所有 Performance Bottlenecks (5项)
- [ ] 加固所有 Fragile Areas (5项)
- [ ] 实现所有 Missing Features (5项)
- [ ] 填补所有 Test Coverage Gaps (5项)
- [ ] 解决所有 Dependencies at Risk (4项)

### Out of Scope

- 新功能开发 — 本次仅重构，不添加新功能
- 大规模重写 — 保持最小范围，仅修复已识别问题
- 性能优化超出现有问题 — 不做额外优化
- 异步化 (async/await) — 超出最小范围，可后续考虑

## Context

**技术栈**: Python 3.12, Pydantic, rustshed, Flask-RESTX, Redis, MQTT, pytest

**代码库分析**: 2026-03-21 完成代码库映射，识别出 37 个具体问题分布在 7 个类别中。

**Pydantic 迁移**: 项目已完成 Pydantic 迁移，但导致大量测试失败，需要修复。

**依赖风险**: Flask-RESTX 项目不活跃，建议迁移到 FastAPI（但超出本次范围）。

## Constraints

- **API 兼容性**: 允许调整 API 签名，但必须保持语义一致
- **范围**: 最小范围 — 仅处理 CONCERNS.md 中已识别的问题
- **优先级**: 质量优先于功能和性能

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| 质量优先 | 统一API和改进错误处理是后续工作的基础 | — Pending |
| 最小范围 | 避免范围蔓延，确保可完成 | — Pending |
| 允许API调整 | 某些问题需要API变更才能正确解决 | — Pending |

---
*Last updated: 2026-03-21 after initialization*
