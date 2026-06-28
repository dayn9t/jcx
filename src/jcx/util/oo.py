from pydantic import BaseModel


def complete[T: BaseModel](a: T, b: T) -> T:
    """用a的值补全b缺失的值"""
    # pydantic BaseModel.__dict__ 为异构字段字典；以 object 承载字段值类型
    b_dict: dict[str, object] = b.__dict__
    a_dict: dict[str, object] = a.__dict__
    for k in b_dict:
        b_dict[k] = b_dict[k] or a_dict[k]
    return b
