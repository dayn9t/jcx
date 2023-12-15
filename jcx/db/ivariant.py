from typing import Type, Protocol

from rustshed import Option

from jcx.text.txt_json import BMT


class IVariant(Protocol):
    """数据库变量接口"""

    def name(self) -> str:
        """"获取变量名"""
        pass

    def value_type(self) -> Type[BMT]:
        """"获取变量类型"""
        pass

    def exists(self) -> bool:
        """"判断是否存在"""
        pass

    def get(self) -> Option[BMT]:
        """获取变量"""
        pass

    def set(self, value: BMT) -> None:
        """设置变量"""
        pass

    def remove(self) -> None:
        """删除变量"""
        pass
