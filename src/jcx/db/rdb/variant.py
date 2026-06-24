from typing import Self

from rustshed import Null, Option, Some

from jcx.db.rdb.db import RedisDb


class RedisVariant[T]:
    """数据库变量"""

    def __init__(
        self, value_type: type[T], db: RedisDb, name: str, default: T | None = None
    ) -> None:
        self._type = value_type
        self._db = db
        self._name = str(name)
        self._default = default

    @classmethod
    def open(
        cls, value_type: type[T], db: RedisDb, name: str, default: T | None = None
    ) -> Self:
        """打开数据变量"""
        return cls(value_type, db, name, default)

    def name(self) -> str:
        """获取变量名"""
        return self._name

    def value_type(self) -> type[T]:
        """获取变量类型"""
        return self._type

    def exists(self) -> bool:
        """判断是否存在"""
        return self._db.exists(self._name)

    def get(self) -> Option[T]:
        """获取变量；缺失时返回 Null"""
        value = self._db.get(self._name, self._type, self._default)
        return Null if value is None else Some(value)

    def set(self, value: T) -> None:
        """设置变量"""
        self._db.set(self._name, value)

    def remove(self) -> None:
        """删除变量"""
        self._db.remove(self._name)
