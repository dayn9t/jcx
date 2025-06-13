from typing import Any, AnyStr, TypeVar

import pydantic_core
from pydantic import BaseModel
from rustshed import Err, Ok, Result, result_shortcut

from jcx.sys.fs import StrPath, or_ext
from jcx.text.io import save_txt

BMT = TypeVar("BMT", bound=BaseModel)
"""BaseModel派生类型"""


def load_txt(file: StrPath, ext: str = ".txt") -> Result[str, Exception]:
    """从文件加载文本"""
    file = or_ext(file, ext)
    try:
        with open(file, encoding="utf-8") as f:
            txt = f.read()
    except Exception as e:
        return Err(e)
    return Ok(txt)


def to_json(ob: Any, pretty: bool = True) -> str:
    """对象序列化为JSON"""
    indent = 4 if pretty else None
    byte_str = pydantic_core.to_json(ob, indent=indent)
    decoded_str = byte_str.decode("utf-8")
    return decoded_str


def from_json(json: AnyStr, ob_type: type[BMT]) -> Result[BMT, Exception]:
    """从JSON文本构建对象"""
    assert isinstance(json, str | bytes), "Invalid input type @ try_from_json"
    try:
        ob = ob_type.model_validate_json(json)
    except Exception as e:
        return Err(e)
    return Ok(ob)


def save_json(obj: Any, file: StrPath, pretty: bool = True) -> Result[bool, Exception]:
    """对象序保存为JSON文件"""
    file = or_ext(file, ".json")
    s = to_json(obj, pretty)
    return save_txt(s, file)


@result_shortcut
def load_json(file: StrPath, obj_type: type[BMT]) -> Result[BMT, Exception]:
    """从Json文件加载对象"""
    file = or_ext(file, ".json")
    s = load_txt(file).Q
    # print('load_json:', file)
    return from_json(s, obj_type)


@result_shortcut
def load_json_or(
    file: StrPath | None,
    obj_type: type[BMT],
    default_value: BMT,
) -> Result[BMT, Exception]:
    """从Json文件加载对象, 文件路径未提供则返回默认值"""
    return load_json(file, obj_type) if file else Ok(default_value)
