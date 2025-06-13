from copy import deepcopy
from typing import Protocol, Self, TypeVar

C = TypeVar("C", bound="Cloned")


class Cloned(Protocol):
    """类型协议 - 复制"""

    def clone(self) -> Self:
        """克隆记录"""
        return deepcopy(self)
