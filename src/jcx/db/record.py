from collections.abc import Callable
from typing import Self

from pydantic import BaseModel


class Record(BaseModel):
    """数据库记录"""

    id: int
    """记录ID"""

    def clone(self: Self) -> Self:
        """克隆记录"""
        return self.model_copy(deep=True)


type RecordFilter = Callable[[Record], bool]
"""记录过滤器"""


class RecordSid(BaseModel):
    """数据库记录"""

    id: str
    """记录ID"""

    def clone(self: Self) -> Self:
        """克隆记录"""
        return self.model_copy(deep=True)


type RecordFilter = Callable[[Record], bool]
"""记录过滤器"""

type RecordSidFilter = Callable[[RecordSid], bool]
"""记录过滤器"""
