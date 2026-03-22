from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def complete(a: T, b: T) -> T:
    """用a的值补全b缺失的值"""
    for k in b.__dict__.keys():
        b.__dict__[k] = b.__dict__[k] or a.__dict__[k]
    return b
