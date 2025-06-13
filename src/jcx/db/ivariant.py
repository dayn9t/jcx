from typing import Protocol, TypeVar

from rustshed import Option

T = TypeVar("T")


class IVariant(Protocol[T]):
    """数据库变量接口"""

    def name(self) -> str:
        """获取变量名"""

    def value_type(self) -> type[T]:
        """获取变量类型"""

    def exists(self) -> bool:
        """判断是否存在"""

    def get(self) -> Option[T]:
        """获取变量"""

    def set(self, value: T) -> None:
        """设置变量"""

    def remove(self) -> None:
        """删除变量"""
