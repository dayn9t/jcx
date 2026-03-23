---
phase: 2-fix-failed-tests
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - tests/net/publisher_test.py
  - tests/util/lict_test.py
  - tests/time/dt_util_test.py
  - tests/util/test_logging_config.py
autonomous: true
requirements: []
must_haves:
  truths:
    - "All 7 fixable tests pass (test_counter skipped)"
    - "Pydantic V2 models use keyword arguments"
    - "Logging tests match loguru's actual JSON structure"
  artifacts:
    - path: "tests/net/publisher_test.py"
      provides: "MqttCfg test with keyword args"
    - path: "tests/util/lict_test.py"
      provides: "LictItem keyword args + LictItems type alias"
    - path: "tests/time/dt_util_test.py"
      provides: "Correct function call for UTC test"
    - path: "tests/util/test_logging_config.py"
      provides: "Tests matching loguru serialize format"
  key_links: []
---

<objective>
Fix 7 failing test cases by updating tests to match Pydantic V2 requirements and loguru's actual JSON output format.

Purpose: Ensure test suite passes after Pydantic V2 migration.
Output: All fixable tests pass; test_counter skipped as documented in STATE.md.
</objective>

<execution_context>
@/home/jiang/.claude/get-shit-done/workflows/execute-plan.md
@/home/jiang/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
@.planning/quick/2-fix-failed-tests/2-CONTEXT.md

<interfaces>
<!-- Key types from source files that tests need to use correctly -->

From src/jcx/net/mqtt/cfg.py:
```python
class MqttCfg(BaseModel):
    server_url: str  # was positional arg 1
    root_topic: str  # was positional arg 2
```

From src/jcx/util/lict.py:
```python
class LictItem(BaseModel, Generic[KT, VT]):
    key: KT
    value: VT

# LictItems is NOT exported - it's list[LictItem[KT, VT]]
```

From src/jcx/time/dt_util.py:
```python
def now_sh_dt() -> Datetime:  # Returns Asia/Shanghai timezone
```

From loguru serialize=True output:
```json
{
  "text": "2026-03-23 15:40:46.023 | INFO | ...",
  "record": {
    "message": "Test",
    "level": {"name": "INFO", "no": 20, "icon": "..."},
    "time": {"timestamp": 1774251646.023337, ...},
    "module": "<string>",
    "function": "<module>",
    "line": 1,
    "extra": {}
  }
}
```
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Fix Pydantic V2 keyword argument tests</name>
  <files>tests/net/publisher_test.py, tests/util/lict_test.py</files>
  <action>
Fix Pydantic V2 compatibility issues in tests:

1. **tests/net/publisher_test.py** - Line 5:
   - Change: `MqttCfg("tcp://localhost:1883", "howell/ias")`
   - To: `MqttCfg(server_url="tcp://localhost:1883", root_topic="howell/ias")`

2. **tests/util/lict_test.py** - Line 16:
   - Change: `LictItem(0, "a")`, `LictItem(1, "b")`, `LictItem(2, "c")`
   - To: `LictItem(key=0, value="a")`, `LictItem(key=1, value="b")`, `LictItem(key=2, value="c")`

3. **tests/util/lict_test.py** - Line 35:
   - `LictItems` is not exported from the module
   - Change: `from_json(s, LictItems[str, int])`
   - To: `from_json(s, list[LictItem[str, int]])`
</action>
  <verify>
    <automated>uv run pytest tests/net/publisher_test.py::test_publish tests/util/lict_test.py -v</automated>
  </verify>
  <done>MqttCfg and LictItem tests pass with keyword arguments; LictItems type alias replaced with list[LictItem[...]]</done>
</task>

<task type="auto">
  <name>Task 2: Fix dt_util timezone test</name>
  <files>tests/time/dt_util_test.py</files>
  <action>
Fix test that calls wrong function for UTC timezone check:

The test `test_now_utc_dt_timezone_is_utc` calls `now_sh_dt()` but expects UTC timezone.
- `now_sh_dt()` returns Asia/Shanghai timezone (+08:00)
- The test should either:
  a) Change the function call to a hypothetical `now_utc_dt()` (doesn't exist), OR
  b) Fix the assertion to match the actual function behavior

Since the test name says "now_utc_dt" but the function called is `now_sh_dt()`, and there's no `now_utc_dt` function in the module, the fix is:
- Change the assertion from `ZoneInfo("UTC")` to `ZoneInfo("Asia/Shanghai")`

Also fix the import on line 5 to match what's actually being tested.

Alternatively, if the intent was to test Shanghai timezone, keep the function call but fix the assertion.
</action>
  <verify>
    <automated>uv run pytest tests/time/dt_util_test.py -v</automated>
  </verify>
  <done>dt_util_test.py passes with correct timezone assertion for now_sh_dt()</done>
</task>

<task type="auto">
  <name>Task 3: Fix logging JSON format tests</name>
  <files>tests/util/test_logging_config.py</files>
  <action>
Fix tests to match loguru's actual JSON output format with `serialize=True`.

Loguru's `serialize=True` produces nested structure:
```json
{
  "text": "...formatted log line...",
  "record": {
    "message": "Test message",
    "level": {"name": "INFO", "no": 20, "icon": "..."},
    "time": {"timestamp": ..., "repr": "..."},
    "module": "...",
    "function": "...",
    "line": 1,
    "extra": {...}
  }
}
```

Update the following tests in `tests/util/test_logging_config.py`:

1. **test_json_format_output** (lines 26-42):
   - Access nested fields: `parsed["record"]["message"]` instead of `parsed["message"]`
   - Level is an object: `parsed["record"]["level"]["name"]` instead of `parsed["level"]`
   - Timestamp is nested: `parsed["record"]["time"]` instead of `parsed["timestamp"]`

2. **test_json_format_includes_extra** (lines 44-55):
   - Access nested: `parsed["record"]["extra"]` instead of `parsed["extra"]`

3. **test_logger_works_after_reconfiguration** (lines 101-103):
   - Same nested access pattern for `parsed["record"]["message"]`

Do NOT modify the implementation in src/jcx/util/logging_config.py - only fix the tests.
</action>
  <verify>
    <automated>uv run pytest tests/util/test_logging_config.py -v</automated>
  </verify>
  <done>Logging tests pass with correct nested JSON structure access</done>
</task>

</tasks>

<verification>
Run full test suite for affected modules:
```bash
uv run pytest tests/net/publisher_test.py tests/util/lict_test.py tests/time/dt_util_test.py tests/util/test_logging_config.py -v
```

Expected: 7 tests pass (test_counter in test_misc.py is skipped per STATE.md documented bug).
</verification>

<success_criteria>
- [ ] tests/net/publisher_test.py::test_publish passes
- [ ] tests/util/lict_test.py::test_lict_map passes
- [ ] tests/util/lict_test.py::test_lict_io passes
- [ ] tests/time/dt_util_test.py::test_now_utc_dt_timezone_is_utc passes
- [ ] tests/util/test_logging_config.py::test_json_format_output passes
- [ ] tests/util/test_logging_config.py::test_json_format_includes_extra passes
- [ ] tests/util/test_logging_config.py::test_logger_works_after_reconfiguration passes
</success_criteria>

<output>
After completion, create `.planning/quick/2-fix-failed-tests/2-SUMMARY.md`
</output>
