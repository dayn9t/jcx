# Quick Task 2: 修正 8 个失败的测试用例 - Context

**Gathered:** 2026-03-23
**Status:** Ready for planning

<domain>
## Task Boundary

修正以下 8 个失败的测试用例：

1. `tests/net/publisher_test.py::test_publish` - MqttCfg 位置参数问题
2. `tests/util/lict_test.py::test_lict_map` - LictItem 位置参数问题
3. `tests/util/lict_test.py::test_lict_io` - LictItems NameError
4. `tests/time/dt_util_test.py::test_now_utc_dt_timezone_is_utc` - 时区断言错误
5. `tests/util/test_logging_config.py` (3个) - JSON 格式结构不匹配
6. `tests/db/test_misc.py::test_counter` - 已知 bug (STATE.md 记录)

</domain>

<decisions>
## Implementation Decisions

### Pydantic V2 兼容性
- 使用关键字参数调用，如 `MqttCfg(url=..., topic=...)`
- 修改测试代码而非实现代码

### dt_util 测试
- 修复测试：测试调用了 `now_sh_dt()` 但期望 UTC，应改为 `now_utc_dt()` 或修改断言

### LictItems NameError
- 检查是否需要导出或修正测试中的类型引用

### Logging JSON 格式
- loguru `serialize=True` 生成嵌套结构 `{record: {...}, text: "..."}`
- 测试期望扁平结构 `{message, level, timestamp, ...}`
- 方案：修改测试以匹配 loguru 的实际输出格式

### test_counter
- STATE.md 已记录为已知 bug，暂时跳过

### Claude's Discretion
- 具体修复细节

</decisions>

<specifics>
## Specific Ideas

所有修复应保持最小范围，仅修改测试代码以适应现有实现。

</specifics>
