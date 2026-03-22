---
phase: 02-security-robustness
plan: 05
status: completed
completed: 2026-03-22
---

# 02-05: Text Utilities Exception Handling

## Summary

Replaced broad `except Exception` handlers in text utility modules with specific exception types (FileNotFoundError, PermissionError, OSError, ValueError, ValidationError).

## Changes

### Task 1: txt_json5.py
- `load_txt`: Catch FileNotFoundError, PermissionError, OSError with file path in error messages
- `from_json5`: Catch ValueError (json5 raises this, not JSONDecodeError), pydantic.ValidationError, UnicodeDecodeError

### Task 2: txt_json.py
- `load_txt`: Catch FileNotFoundError, PermissionError, OSError with file path in error messages
- `from_json`: Catch pydantic_core.ValidationError, ValueError for validation failures

### Task 3: io.py
- `save_txt`: Catch PermissionError, OSError with file path in error messages

### Task 4: err.py Review
- `catch_show_err` intentionally catches Exception for logging - no change needed

## Key Files

| File | Purpose |
|------|---------|
| `src/jcx/text/txt_json5.py` | JSON5 I/O with specific exception handling |
| `src/jcx/text/txt_json.py` | JSON I/O with specific exception handling |
| `src/jcx/text/io.py` | Text I/O with specific exception handling |
| `tests/text/txt_json_test.py` | Tests for exception handling |

## Verification

```bash
pytest tests/text/txt_json_test.py -v  # All tests pass
grep -c "except Exception" src/jcx/text/*.py  # Returns 0
```

## Notes

- The `json5` library raises `ValueError` for parse errors, not `JSONDecodeError`
- Pydantic's `ValidationError` is preserved as-is for detailed validation feedback

## Self-Check

- [x] All tasks executed
- [x] Each task committed
- [x] SUMMARY.md created
- [x] Tests pass
