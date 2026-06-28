"""通用 JSON 持久化变量。

与 `jdb.variant.JdbVariant`（BaseModel 专用，依赖 `model_validate_json`）不同，
`JsonVariant` 使用 pydantic `TypeAdapter`，支持 int/str/float/BaseModel 等所有
可验证类型，用于计数器等原始值场景。`get` 返回 `Option[T]`，缺失或解析失败时
为 `Null`，严格符合 `IVariant` 协议。
"""

from pathlib import Path
from typing import Self, TypeVar

import pydantic_core
from pydantic import TypeAdapter
from rustshed import Null, Option, Some

from jcx.db.ivariant import IVariant
from jcx.sys.fs import StrPath
from jcx.text.io import load_txt, save_txt

T = TypeVar("T")


class JsonVariant[T](IVariant[T]):
    """通用 JSON 变量——支持任意 pydantic 可验证类型"""

    @classmethod
    def open(cls, value_type: type[T], folder: StrPath, name: str) -> Self:
        """打开数据变量"""
        return cls(value_type, folder, name)

    def __init__(self, value_type: type[T], folder: StrPath, name: str) -> None:
        self._type = value_type
        self._adapter: TypeAdapter[T] = TypeAdapter(value_type)
        self._path = Path(folder, name + ".json")

    def name(self) -> str:
        """获取变量名"""
        return self._path.stem

    def value_type(self) -> type[T]:
        """获取变量类型"""
        return self._type

    def exists(self) -> bool:
        """获取变量类型"""
        return self._path.exists()

    def get(self) -> Option[T]:
        """获取变量；文件缺失或解析失败时返回 Null"""
        if not self._path.exists():
            return Null
        result = load_txt(self._path)
        if result.is_err():
            return Null
        try:
            value = self._adapter.validate_json(result.unwrap())
        except pydantic_core.ValidationError:
            return Null
        return Some(value)

    def set(self, value: T) -> None:
        """设置变量"""
        text = self._adapter.dump_json(value, indent=4).decode("utf-8")
        save_txt(text, self._path).expect(f"Failed to save variant to {self._path}")

    def remove(self) -> None:
        """删除变量"""
        self._path.unlink()
