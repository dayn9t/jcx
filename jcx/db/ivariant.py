from typing import Type, Protocol, TypeVar, Generic

from rustshed import Option

T = TypeVar('T')

class IVariant(Protocol[T]):
    """数据库变量接口"""

    def name(self) -> str:
        """获取变量名"""
        pass

    def value_type(self) -> Type[T]:
        """获取变量类型"""
        pass

    def exists(self) -> bool:
        """判断是否存在"""
        pass

    def get(self) -> Option[T]:
        """获取变量"""
        pass

    def set(self, value: T) -> None:
        """设置变量"""
        pass

    def remove(self) -> None:
        """删除变量"""
        pass