# External Integrations

**Analysis Date:** 2026-03-21

## APIs & External Services

**HTTP REST APIs:**
- Custom REST APIs - DAO client for CRUD operations
  - Client: `requests` library
  - Implementation: `src/jcx/api/dao_client.py`
  - Auth: Bearer token support via `set_auth_token()`
  - Base URL configurable (default: `http://localhost:8080/api` in `src/jcx/bin/cx_task.py`)

**External HTTP:**
- HTTP connectivity test via Baidu
  - Purpose: Network connectivity verification
  - Implementation: `src/jcx/net/mqtt/mqtt_s.py`

## Data Storage

**Databases:**
- Redis
  - Connection: URL format `redis://host:port/db_num`
  - Client: `redis` Python package
  - Implementation: `src/jcx/db/rdb/db.py` (RedisDb class)
  - Example: `redis://127.0.0.1/10` (localhost, database 10)
  - Features: JSON serialization, key-value operations

**File Storage:**
- JSON file storage (JDB - JSON Database)
  - Implementation: `src/jcx/db/jdb/variant.py` (JdbVariant class)
  - Format: `.json` files
  - Location: Configurable folder path

**Caching:**
- None detected beyond Redis usage

## Authentication & Identity

**Auth Provider:**
- Custom Bearer token authentication
  - Implementation: HTTP Authorization header
  - Method: `set_auth_token()` in `src/jcx/api/dao_client.py`
  - Format: `Bearer <token>`

## Monitoring & Observability

**Error Tracking:**
- None detected (loguru used for logging)

**Logs:**
- Framework: loguru
- Implementation: Used throughout codebase (e.g., `src/jcx/sys/fs.py`, `src/jcx/net/mqtt/subscriber.py`)
- No centralized log aggregation detected

## CI/CD & Deployment

**Hosting:**
- Not detected (appears to be library/utility code)

**CI Pipeline:**
- Not detected

**Build:**
- Nuitka compilation to standalone executables
  - Command: `nuitka --job=8 --onefile --standalone --follow-imports --output-dir=dist src/jcx/bin/cx_task.py`
  - Output: `dist/` directory

## Environment Configuration

**Required env vars:**
- None explicitly required
- Configuration via:
  - Command-line arguments (typer CLI)
  - URL strings (Redis, HTTP APIs)
  - Pydantic models

**Secrets location:**
- No dedicated secrets management detected
- Auth tokens passed programmatically

## Webhooks & Callbacks

**Incoming:**
- None detected

**Outgoing:**
- MQTT publish/subscribe
  - Publisher: `src/jcx/net/mqtt/publisher.py`
  - Subscriber: `src/jcx/net/mqtt/subscriber.py`
  - Config: `MqttCfg` in `src/jcx/net/mqtt/cfg.py`
  - Fields: `server_url`, `root_topic`

## CLI Tools

**Installed Commands:**
- `cx_rename` - Rename utility (`src/jcx/bin/cx_rename.py`)
- `cx_task` - Task management CLI (`src/jcx/bin/cx_task.py`)
- `cx_dao` - DAO operations CLI (`src/jcx/bin/cx_dao.py`)
- `mv_re` - Regex-based move/rename (`src/jcx/bin/mv_re.py`)
- `rename_re` - Regex-based rename (`src/jcx/bin/rename_re.py`)

---

*Integration audit: 2026-03-21*
