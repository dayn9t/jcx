from typing import Callable, Self

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
