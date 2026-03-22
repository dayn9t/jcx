import re
from typing import Any
from urllib.parse import urlparse

import redis
from pydantic import BaseModel
from rustshed import Err, Ok, Result

from jcx.text.txt_json import BMT, from_json, to_json


class DbCfg(BaseModel):
    hot_db: str
    pretty: bool = True


def parse_redis_url(url: str) -> Result[tuple[str, int, int], str]:
    """Parse Redis URL and return (host, port, db_num) or error message.

    Expected format: redis://host:port/db_num
    Example: redis://127.0.0.1:6379/10

    Args:
        url: Redis connection URL string

    Returns:
        Ok((host, port, db_num)) on success
        Err(error_message) on invalid URL

    """
    try:
        uri = urlparse(url)
        if uri.scheme != "redis":
            return Err(f"Invalid Redis URL scheme: expected 'redis://', got '{uri.scheme}://'")

        host = uri.hostname or "localhost"
        port = uri.port or 6379

        p = re.compile(r"/(\d+)")
        m = p.match(uri.path)
        if not m:
            return Err(f"Invalid Redis URL path: expected '/<db_num>', got '{uri.path}'")

        db_num = int(m.groups()[0])
        return Ok((host, port, db_num))
    except Exception as e:
        return Err(f"Failed to parse Redis URL: {e}")


class RedisDb:
    """数据库变量"""

    @staticmethod
    def open(server_url: str) -> "RedisDb":
        """打开数据变量"""
        return RedisDb(server_url)

    def __init__(self, url: str):
        """Initialize Redis client from URL.

        Args:
            url: Redis connection URL (format: redis://host:port/db_num)

        Raises:
            ValueError: If URL is invalid

        """
        result = parse_redis_url(url)
        if result.is_err():
            raise ValueError(result.unwrap_err())

        host, port, db_num = result.unwrap()
        self._name = str(db_num)
        self._db = redis.Redis(
            host=host,
            port=port,
            db=db_num,
            decode_responses=True,
        )

    def name(self) -> str:
        """ "获取数据库名"""
        return self._name

    def set(self, name: str, value: Any) -> None:
        """保存变量"""
        self._db.set(name, to_json(value))

    def get(self, name: str, var_type: type[BMT], default_value: BMT) -> BMT:
        """获取变量"""
        s = self._db.get(name)
        if not s:
            return default_value
        result = from_json(s, var_type)
        if result.is_err():
            return default_value
        return result.unwrap()

    def exists(self, name: str) -> bool:
        """ "判断是否存在"""
        return self._db.exists(name) > 0

    def remove(self, name: str) -> None:
        """ "删除"""
        self._db.delete(name)


def a_test() -> None:
    cfg = DbCfg(hot_db="redis://127.0.0.1/10")

    db = RedisDb(cfg.hot_db)

    db.set("name", "jack")
    v = db.get("name", str, "")
    print(v, type(v))

    db.set("age", 18)
    v = db.get("age", int, 0)
    print(v, type(v))

    db.set("cfg", cfg)
    v = db.get("cfg", DbCfg, DbCfg())
    print(v, type(v))

    print(db.exists("cfg"))
    db.remove("cfg")
    print(db.exists("cfg"))


if __name__ == "__main__":
    a_test()
