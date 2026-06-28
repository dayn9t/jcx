"""JSON5 serialization and deserialization utilities using Pydantic.

This module provides functions for loading and saving JSON5 files with
proper error handling using the Result type. JSON5 is an extension of JSON
that supports comments, trailing commas, and other features.
"""

from typing import Protocol, TypeVar, runtime_checkable

import json5
import pydantic
from pydantic import BaseModel
from rustshed import Err, Ok, Result, result_shortcut

from jcx.sys.fs import StrPath, or_ext
from jcx.text.io import save_txt
from jcx.text.txt_json import load_txt

BMT = TypeVar("BMT", bound=BaseModel)
"""BaseModel派生类型"""


@runtime_checkable
class _ModelDump(Protocol):
    """具备 model_dump 方法的对象（pydantic BaseModel 协议）"""

    def model_dump(self) -> dict[str, object]:
        """Return a dictionary representation of the model."""
        ...


def to_json5(ob: object, pretty: bool = True) -> str:
    """Serialize an object to a JSON5 string.

    Args:
        ob: Object to serialize (Pydantic model or standard Python type).
        pretty: If True, format with 4-space indentation.

    Returns:
        JSON5 string representation of the object.

    """
    if isinstance(ob, _ModelDump):
        # 如果是Pydantic模型，先转为字典
        ob_dict = ob.model_dump()
        return str(json5.dumps(ob_dict, indent=4 if pretty else None))
    # 尝试直接序列化
    return str(json5.dumps(ob, indent=4 if pretty else None))


def from_json5[AnyStr: (bytes, str), BMT: BaseModel](json5_str: AnyStr, ob_type: type[BMT]) -> Result[BMT, Exception]:
    """Parse JSON5 text into a Pydantic model instance.

    Args:
        json5_str: JSON5 string or bytes to parse.
        ob_type: Pydantic model class to parse into.

    Returns:
        Ok with parsed model instance on success, Err with exception on failure.

    """
    assert isinstance(json5_str, str | bytes), "Invalid input type @ try_from_json5"  # noqa: S101 - 内部类型 narrowing
    try:
        # 先用json5解析成字典
        text: str = json5_str.decode("utf-8") if isinstance(json5_str, bytes) else json5_str
        obj_dict = json5.loads(text)
        # 然后用Pydantic模型验证
        ob = ob_type.model_validate(obj_dict)
    except ValueError as e:
        # json5 抛出 ValueError 而不是 JSONDecodeError
        return Err(ValueError(f"JSON5解析失败: {e}"))
    except pydantic.ValidationError as e:
        return Err(e)
    except UnicodeDecodeError as e:
        return Err(ValueError(f"UTF-8解码失败: {e}"))
    return Ok(ob)


def save_json5(
    obj: object, file: StrPath, pretty: bool = True
) -> Result[bool, Exception]:
    """Save an object to a JSON5 file.

    Args:
        obj: Object to serialize and save.
        file: Path to the output file (.json5 extension added if missing).
        pretty: If True, format with 4-space indentation.

    Returns:
        Ok(True) on success, Err with exception on failure.

    """
    file = or_ext(file, ".json5")
    s = to_json5(obj, pretty)
    return save_txt(s, file)


@result_shortcut
def load_json5[BMT: BaseModel](file: StrPath, obj_type: type[BMT]) -> Result[BMT, Exception]:
    """Load and parse a JSON5 file into a Pydantic model instance.

    Args:
        file: Path to the JSON5 file (.json5 extension added if missing).
        obj_type: Pydantic model class to parse into.

    Returns:
        Ok with parsed model instance on success, Err with exception on failure.

    """
    file = or_ext(file, ".json5")
    s = load_txt(file).Q
    return from_json5(s, obj_type)


@result_shortcut
def load_json5_or[BMT: BaseModel](
    file: StrPath | None,
    obj_type: type[BMT],
    default_value: BMT,
) -> Result[BMT, Exception]:
    """Load a JSON5 file or return a default value if no file is provided.

    Args:
        file: Path to the JSON5 file, or None to use default.
        obj_type: Pydantic model class to parse into.
        default_value: Value to return if file is None.

    Returns:
        Ok with parsed model or default value, Err with exception on parse failure.

    """
    return load_json5(file, obj_type) if file else Ok(default_value)
