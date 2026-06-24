from collections.abc import Callable
from typing import Self

from pydantic import BaseModel


class Record(BaseModel):
    """带 int 主键的数据库记录"""

    id: int
    """记录ID"""

    def clone(self: Self) -> Self:
        """克隆记录"""
        return self.model_copy(deep=True)


type PRecord = Record
"""DAO 层泛型约束——带 int 主键的记录"""


type RecordFilter = Callable[[Record], bool]
"""记录过滤器"""


class RecordSid(BaseModel):
    """带 str 主键的数据库记录"""

    id: str
    """记录ID"""

    def clone(self: Self) -> Self:
        """克隆记录"""
        return self.model_copy(deep=True)


type RecordSidFilter = Callable[[RecordSid], bool]
"""字符串主键记录过滤器"""
