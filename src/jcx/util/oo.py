from typing import Any, TypeVar, cast

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def complete(a: T, b: T) -> T:
    """用a的值补全b缺失的值"""
    # BaseModel.__dict__ is mutable dict[str, Any]; pyright may infer MappingProxyType
    b_dict: dict[str, Any] = cast(dict[str, Any], b.__dict__)
    a_dict: dict[str, Any] = cast(dict[str, Any], a.__dict__)
    for k in b_dict.keys():
        b_dict[k] = b_dict[k] or a_dict[k]
    return b
