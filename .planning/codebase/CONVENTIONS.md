# Coding Conventions

**Analysis Date:** 2026-03-21

## Naming Patterns

**Files:**
- `snake_case` for all Python modules and scripts
- Test files: `test_*.py` pattern (e.g., `test_record.py`, `txt_json_test.py`)
- Source modules: lowercase names (e.g., `number.py`, `algo.py`, `fs.py`)

**Functions:**
- `snake_case` for all functions
- Descriptive names: `align_down()`, `file_names_in()`, `dict_first_key()`
- Utility functions often short: `low_pos()`, `up_pos()`, `lookup()`

**Variables:**
- `snake_case` for local variables
- Short names for loop variables: `i`, `k`, `v`, `f`
- Descriptive for domain objects: `record`, `folder`, `file_name`

**Types/Classes:**
- `PascalCase` for classes: `Record`, `Table`, `Subscriber`, `StopWatch`
- Type aliases: `PascalCase` with `type` keyword (Python 3.12+)
  - `type Real = int | float`
  - `type Real2D = tuple[Real, Real]`
  - `type RecordFilter = Callable[[Record], bool]`

**Constants:**
- Not widely used; when present: `SCREAMING_SNAKE_CASE` implied but rare in codebase

## Code Style

**Formatting:**
- Ruff (configured in `ruff.toml`)
- Rule set: `select = ["ALL"]` with specific ignores: `F403`, `F405`, `D203`, `D213`, `COM812`
- 4-space indentation (Python standard)
- Line length: Not explicitly configured (Ruff default likely applies)

**Linting:**
- Ruff handles both linting and formatting
- Ignores `F403`/`F405` (wildcard imports)
- Ignores `D203`/`D213` (docstring formatting conflicts)
- Ignores `COM812` (trailing comma)

**File Organization:**
- Small to medium files: 30-370 lines (largest is `src/jcx/sys/fs.py` at 369 lines)
- Modular design: each module has clear purpose
- Bin scripts in `src/jcx/bin/` with `main()` entry points

## Import Organization

**Order:**
1. Standard library imports (e.g., `import hashlib`, `from pathlib import Path`)
2. Third-party imports (e.g., `import arrow`, `from loguru import logger`, `from pydantic import BaseModel`)
3. Local imports (e.g., `from jcx.text.txt_json import to_json`, `from jcx.sys.fs import StrPath`)

**Path Aliases:**
- No explicit path aliases configured
- Uses relative imports from `jcx` root package
- Example: `from jcx.db.record import Record`

**Wildcard Imports:**
- Used in tests: `from jcx.util.algo import *`
- Ruff configured to ignore `F403`/`F405` for these cases

## Error Handling

**Patterns:**
- Extensive use of `rustshed` library for Rust-style error handling
- `Result[T, E]` types: `Ok(value)` or `Err(error)`
- `Option[T]` types: `Some(value)` or `Null`
- Decorator `@to_option` and `@result_shortcut` for automatic wrapping

**Example from `src/jcx/util/algo.py`:**
```python
from rustshed import Null, Option, Some, to_option

@to_option
def list_index(arr: list, value) -> int:
    """List中查找值的索引, 失败则Null"""
    return arr.index(value)
```

**Example from `src/jcx/sys/fs.py`:**
```python
from rustshed import Err, Ok, Result

def find_first(folder: StrPath, pattern: str, recursive: bool = True) -> Result[Path, str]:
    """在文件夹内查找满足条件的第一个文件."""
    folder = Path(folder)
    if not folder.is_dir():
        return Err("指定路径不是目录: " + str(folder))
    # ...
    return Ok(f)
```

**Error Display:**
- `src/jcx/util/err.py` provides `show_err()` and `catch_show_err()` helpers
- Uses `loguru.logger` for error logging
- Distinguishes between `Err`, `AssertionError`, and generic exceptions

## Logging

**Framework:** `loguru`

**Patterns:**
- Import: `from loguru import logger`
- Usage: `logger.info()`, `logger.error()`
- Example from `src/jcx/net/mqtt/subscriber.py`:
  ```python
  logger.info("Subscribe mqtt topic: %s/%s ..." % (self.url, topic))
  ```
- Error logging in `src/jcx/util/err.py`:
  ```python
  logger.error(msg)
  ```

**Console Output:**
- `print()` used in bin scripts and test code
- Debug prints removed in production code (evidence of cleanup)

## Comments

**When to Comment:**
- Docstrings for all public functions and classes (Chinese comments used)
- Inline comments for complex logic or workarounds
- TODO/FIXME markers for known issues

**JSDoc/TSDoc equivalent:**
- Python docstrings with triple quotes `"""..."""`
- Function signature style:
  ```python
  def find_first(folder: StrPath, pattern: str, recursive: bool = True) -> Result[Path, str]:
      """在文件夹内查找满足条件的第一个文件."""
  ```

**Type Annotations:**
- Heavy use of Python 3.12+ type aliases
- Type hints on all function parameters and returns
- Generic types: `TypeVar`, `bound=BaseModel`
- Union types: `str | Path` (modern syntax)

## Function Design

**Size:** Generally small and focused
- Most functions under 20 lines
- Some longer functions up to 50 lines (e.g., `dispatch_msg` in subscriber.py)
- Complex operations broken into helper functions

**Parameters:**
- Type hints required
- Default values common: `reverse: bool = False`
- Optional parameters: `folder: StrPath | None`
- Use of `StrPath` type alias for `str | Path`

**Return Values:**
- Explicit return types
- `Result[T, E]` for fallible operations
- `Option[T]` for nullable returns
- Direct returns for simple functions

## Module Design

**Exports:**
- `__init__.py` files present in subdirectories
- Public API through explicit imports
- Barrel files: `src/jcx/util/__init__.py`, `src/jcx/m/__init__.py`

**Barrel Files:**
- Used to aggregate module exports
- Example pattern: `from jcx.util.algo import *` in tests

**Module Structure:**
```
src/jcx/
├── bin/          # CLI entry points (main() functions)
├── db/           # Database abstractions
├── m/            # Math utilities
├── net/          # Networking (MQTT)
├── sys/          # System utilities (filesystem)
├── text/         # Text processing (JSON)
├── time/         # Time utilities
├── ui/           # UI components
└── util/         # General utilities
```

## Special Conventions

**Immutability:**
- `clone()` method on `Record` classes using `model_copy(deep=True)`
- Defensive copying in `Table` class: `record = record.clone()`
- Rust-inspired patterns through `rustshed` library

**Rust Style Adaptation:**
- Extensive use of `rustshed` for Option/Result types
- Pattern matching with `match` statements
- Null-safety through Option types

**Chinese Comments:**
- Docstrings and comments use Chinese language
- Example: `"""在文件夹内查找满足条件的第一个文件."""`

**Type Aliases:**
- Python 3.12+ type syntax used throughout
- `type` keyword for creating readable type aliases
- Examples: `type Real = int | float`, `type StrPath = str | Path`

---

*Convention analysis: 2026-03-21*
