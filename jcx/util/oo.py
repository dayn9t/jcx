from pydantic import BaseModel


def complete(a: BaseModel, b: BaseModel) -> BaseModel:
    """用a的值补全b缺失的值"""
    for k in b.__dict__.keys():
        b.__dict__[k] = b.__dict__[k] or a.__dict__[k]
    return b
