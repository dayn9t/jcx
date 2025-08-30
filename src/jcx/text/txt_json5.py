from typing import Any, AnyStr, TypeVar

import json5
from pydantic import BaseModel
from rustshed import Err, Ok, Result, result_shortcut

from jcx.sys.fs import StrPath, or_ext
from jcx.text.io import save_txt

BMT = TypeVar("BMT", bound=BaseModel)
"""BaseModel派生类型"""


def load_txt(file: StrPath, ext: str = ".txt") -> Result[str, Exception]:
    """从文件加载文本."""
    file = or_ext(file, ext)
    try:
        with open(file, encoding="utf-8") as f:
            txt = f.read()
    except Exception as e:
        return Err(e)
    return Ok(txt)


def to_json5(ob: Any, pretty: bool = True) -> str:
    """对象序列化为JSON5."""
    if hasattr(ob, "model_dump"):
        # 如果是Pydantic模型，先转为字典
        ob_dict = ob.model_dump()
        return json5.dumps(ob_dict, indent=4 if pretty else None)
    # 尝试直接序列化
    return json5.dumps(ob, indent=4 if pretty else None)


def from_json5(json5_str: AnyStr, ob_type: type[BMT]) -> Result[BMT, Exception]:
    """从JSON5文本构建对象."""
    assert isinstance(json5_str, str | bytes), "Invalid input type @ try_from_json5"
    try:
        # 先用json5解析成字典
        if isinstance(json5_str, bytes):
            json5_str = json5_str.decode("utf-8")
        obj_dict = json5.loads(json5_str)
        # 然后用Pydantic模型验证
        ob = ob_type.model_validate(obj_dict)
    except Exception as e:
        return Err(e)
    return Ok(ob)


def save_json5(obj: Any, file: StrPath, pretty: bool = True) -> Result[bool, Exception]:
    """对象序保存为JSON5文件."""
    file = or_ext(file, ".json5")
    s = to_json5(obj, pretty)
    return save_txt(s, file)


@result_shortcut
def load_json5(file: StrPath, obj_type: type[BMT]) -> Result[BMT, Exception]:
    """从Json5文件加载对象."""
    file = or_ext(file, ".json5")
    s = load_txt(file).Q
    return from_json5(s, obj_type)


@result_shortcut
def load_json5_or(
    file: StrPath | None,
    obj_type: type[BMT],
    default_value: BMT,
) -> Result[BMT, Exception]:
    """从Json5文件加载对象, 文件路径未提供则返回默认值."""
    return load_json5(file, obj_type) if file else Ok(default_value)
