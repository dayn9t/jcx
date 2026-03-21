# Testing Patterns

**Analysis Date:** 2026-03-21

## Test Framework

**Runner:**
- pytest 9.0.2
- Config: No explicit config file found (using pytest defaults)

**Assertion Library:**
- pytest's built-in `assert` statement
- No additional assertion library (no `pytest-assert` or similar)

**Run Commands:**
```bash
pytest                  # Run all tests (from project root)
pytest -xvs            # Run with verbose output, stop on first failure
pytest tests/m/        # Run specific directory
pytest <test_file>     # Run specific file
```

**Direct Execution:**
- Tests can be run directly: `python tests/m/number_test.py`
- Main guard pattern used:
  ```python
  if __name__ == "__main__":
      pytest.main(["-xvs", __file__])
  ```

## Test File Organization

**Location:**
- Separate `tests/` directory at project root
- Mirrors `src/jcx/` structure:
  - `tests/m/` → `src/jcx/m/`
  - `tests/util/` → `src/jcx/util/`
  - `tests/sys/` → `src/jcx/sys/`
  - `tests/db/` → `src/jcx/db/`
  - `tests/api/` → `src/jcx/api/`

**Naming:**
- Two patterns observed:
  1. `test_*.py` (e.g., `test_record.py`, `test_task_db.py`)
  2. `*_test.py` (e.g., `number_test.py`, `algo_test.py`, `fs_test.py`)
- No strict convention; both patterns accepted

**Structure:**
```
tests/
├── m/               # Math utilities tests
├── util/            # General utilities tests
├── sys/             # System utilities tests
├── db/              # Database tests
│   ├── jdb/         # JSON database tests
│   └── test_record.py
├── net/             # Network tests
├── text/            # Text processing tests
├── api/             # API client tests
├── time/            # Time utilities tests
└── data_types.py    # Shared test fixtures
```

## Test Structure

**Suite Organization:**
```python
# Simple function-based tests (most common)
def test_is_real() -> None:
    assert is_real(1)
    assert is_real(1.0)
    assert not is_real("1")

def test_real_2d() -> None:
    assert real_2d(1) == (1, 1)
    assert real_2d(1.0) == (1.0, 1.0)
```

**Class-based tests** (for complex fixtures):
```python
class TestDaoListClient:
    """DaoListClient 测试类"""

    def test_init(self):
        """测试客户端初始化"""
        client = DaoListClient("http://api.example.com/v1")
        assert client.base_url == "http://api.example.com/v1"
```

**Patterns:**
- No explicit setup/teardown in most tests
- Fixtures used for shared test data (in `test_dao_list_client.py`)
- Temp directories created inline: `with tempfile.TemporaryDirectory() as tmp_dir:`
- Clean assertion style: direct `assert` statements

**Test Data:**
- Inline test data in functions
- Shared fixtures in `tests/data_types.py`:
  ```python
  from tests.data_types import *

  def test_record_clone() -> None:
      team1 = TEAM1
      team2 = team1.clone()
  ```

## Mocking

**Framework:** `unittest.mock` (standard library)

**Patterns:**
```python
from unittest.mock import Mock, patch

@patch("requests.Session.get")
def test_get_all_success(self, mock_get, client, test_records):
    # 准备模拟响应
    mock_response = Mock()
    mock_response.json.return_value = [{"id": 1, "name": "记录1"}]
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    # 执行测试
    result = client.get_all(TestRecord, "tests")

    # 验证结果
    assert result.is_ok()
```

**What to Mock:**
- External API calls (`requests.Session` methods)
- File system operations (rarely - mostly use real temp directories)
- Database connections (use in-memory or temp databases)

**What NOT to Mock:**
- File system operations in unit tests (use real temp dirs)
- Business logic classes
- Data structures

**Fixture Pattern:**
```python
@pytest.fixture
def client():
    """创建一个 DaoListClient 实例用于测试"""
    return DaoListClient("http://api.example.com/v1")

@pytest.fixture
def test_record():
    """创建一个测试记录用于测试"""
    return TestRecord(id=1, name="测试记录", value=100)
```

## Fixtures and Factories

**Test Data:**
- Inline construction: `TestRecord(id=1, name="test")`
- Pydantic models used for test data
- Shared fixtures in `tests/data_types.py`

**Location:**
- `tests/data_types.py` for shared test data
- Inline fixtures in test files using `@pytest.fixture`
- Temp directories created inline with `tempfile.TemporaryDirectory()`

**Example from `tests/api/task/test_task_db.py`:**
```python
class TestTaskInfo(TaskInfo):
    """测试用任务信息类"""
    content: str = ""  # 测试内容字段

def test_task_operations():
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_dir = Path(tmp_dir)
        db = TaskDb(db_dir, TestTaskInfo)
        # ... test code
```

## Coverage

**Requirements:** None enforced

**View Coverage:**
```bash
pytest --cov=src/jcx tests/
```

**Note:** No coverage configuration found (`.coveragerc` or `pyproject.toml` coverage section)

## Test Types

**Unit Tests:**
- Primary focus of test suite
- Test individual functions and classes
- Located in module-specific directories
- Example: `tests/m/number_test.py` tests `jcx.m.number`

**Integration Tests:**
- API client tests with mocked HTTP (`tests/api/test_dao_list_client.py`)
- Database integration tests using temp directories (`tests/api/task/test_task_db.py`)
- File system operations using real temp dirs

**E2E Tests:**
- Not detected
- No browser automation or full-stack testing

## Common Patterns

**Async Testing:**
- Not detected (no async/await in test files)

**Error Testing:**
```python
def test_get_error(self, mock_get, client):
    """测试 get 方法错误场景"""
    mock_get.side_effect = Exception("记录不存在")

    result = client.get(TestRecord, "tests", 999)

    assert result.is_err()
    error = result.unwrap_err()
    assert "获取资源失败" in error
```

**Option/Result Testing:**
```python
def test_dict_first_key() -> None:
    d = {1: "a", 2: "b", 3: "c", 4: "c"}

    assert dict_first_key(d, 1) == Null
    assert dict_first_key(d, "b").unwrap() == 2
    assert dict_first_key(d, "c").unwrap() == 3
```

**Chinese Docstrings:**
- Test functions use Chinese docstrings
- Example: `"""测试任务错误处理"""`

## Test Execution Issues

**Current Status:**
- Test collection shows errors: `collected 0 items / 28 errors`
- Tests may have import issues or missing dependencies
- Direct test execution works (`python tests/m/number_test.py`)
- Test suite needs maintenance

**Recommendation:**
- Fix import paths in test files
- Ensure all dependencies are installed
- Run `pytest --collect-only` to identify issues

## Test Count

- Approximately 67 test functions/classes found
- Test files range from 25-333 lines
- Largest test file: `tests/api/test_dao_list_client.py` (333 lines)

---

*Testing analysis: 2026-03-21*
