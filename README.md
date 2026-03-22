# JCX

A Python utility library providing Result/Option types, file operations, time utilities, JSON handling, and more.

## Installation

```bash
# Using uv (recommended)
uv add jcx

# Using pip
pip install jcx
```

## Quick Start

```python
from jcx.rs import Result, Ok, Err
from jcx.sys.fs import files_in, remake_dir
from jcx.text.txt_json import load_json, save_json
```

## Modules

### Result/Option Types (`jcx.rs`)

Rust-inspired error handling with Result and Option types (powered by rustshed):

```python
from jcx.rs import Result, Ok, Err, Option, Some, Null

def divide(a: int, b: int) -> Result[float, str]:
    if b == 0:
        return Err("Division by zero")
    return Ok(a / b)

result = divide(10, 2)
if result.is_ok():
    print(f"Result: {result.unwrap()}")  # Result: 5.0
```

### File System Operations (`jcx.sys.fs`)

```python
from pathlib import Path
from jcx.sys.fs import files_in, find_first, remake_dir

# Get all JSON files in a directory
json_files = files_in("/data", ".json")

# Find first matching file recursively
result = find_first("/project", "*.toml")
if result.is_ok():
    print(f"Found: {result.unwrap()}")

# Recreate a clean directory
work_dir = remake_dir("/tmp/workspace")
```

### Time Utilities (`jcx.time`)

```python
from jcx.time.clock_time import ClockTime, to_clock_time
from arrow import Arrow

# Parse time from string
time = ClockTime.parse("14:30:00")
if time.is_some():
    print(f"Parsed: {time.unwrap()}")

# Convert various time formats
ct = to_clock_time(Arrow.now())
```

### JSON Handling (`jcx.text.txt_json`)

```python
from jcx.text.txt_json import load_json, save_json, to_json
from pydantic import BaseModel

class Config(BaseModel):
    name: str
    value: int

# Load configuration with type safety
result = load_json("config.json", Config)
if result.is_ok():
    config = result.unwrap()

# Save with pretty formatting
save_json(config, "output.json", pretty=True)
```

## Environment Variables

See [.env.example](.env.example) for all configurable options:

| Variable | Description | Default |
|----------|-------------|---------|
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) | INFO |
| `LOG_FORMAT` | Output format (json or text) | text |
| `DATABASE_URL` | PostgreSQL connection URL | - |
| `REDIS_URL` | Redis connection URL | - |
| `MQTT_URL` | MQTT broker URL | - |

## Development

```bash
# Install dev dependencies
uv sync --dev

# Run tests
uv run pytest

# Run type checking
uv run pyright src/jcx

# Format code
uv run ruff format .
```

## License

MIT
