import re
from typing import Self, TypeVar, cast
from urllib.parse import urlparse

import pydantic_core
import redis
from pydantic import BaseModel, TypeAdapter
from rustshed import Err, Ok, Result

T = TypeVar("T")


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
            return Err(
                f"Invalid Redis URL scheme: expected 'redis://', got '{uri.scheme}://'"
            )

        host = uri.hostname or "localhost"
        port = uri.port or 6379

        p = re.compile(r"/(\d+)")
        m = p.match(uri.path)
        if not m:
            return Err(
                f"Invalid Redis URL path: expected '/<db_num>', got '{uri.path}'"
            )

        db_num = int(m.groups()[0])
        return Ok((host, port, db_num))
    except Exception as e:
        return Err(f"Failed to parse Redis URL: {e}")


class RedisDb:
    """Redis 数据库"""

    @classmethod
    def open(cls, server_url: str) -> Self:
        """打开数据库"""
        return cls(server_url)

    def __init__(self, url: str) -> None:
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
        """获取数据库名"""
        return self._name

    def set(self, name: str, value: object) -> None:
        """保存变量"""
        self._db.set(name, pydantic_core.to_json(value).decode("utf-8"))

    def get(
        self, name: str, var_type: type[T], default_value: T | None = None
    ) -> T | None:
        """获取变量；缺失或解析失败时返回 default_value"""
        raw = cast("str | None", self._db.get(name))
        if not raw:
            return default_value
        try:
            return TypeAdapter(var_type).validate_json(raw)
        except pydantic_core.ValidationError:
            return default_value

    def exists(self, name: str) -> bool:
        """判断是否存在"""
        return cast("int", self._db.exists(name)) > 0

    def remove(self, name: str) -> None:
        """删除"""
        self._db.delete(name)
