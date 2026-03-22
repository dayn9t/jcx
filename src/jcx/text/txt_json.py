"""JSON serialization and deserialization utilities using Pydantic.

This module provides functions for loading and saving JSON files with
proper error handling using the Result type.
"""

from typing import Any, AnyStr, TypeVar

import pydantic_core
from pydantic import BaseModel
from rustshed import Err, Ok, Result, result_shortcut

from jcx.sys.fs import StrPath, or_ext
from jcx.text.io import save_txt

BMT = TypeVar("BMT", bound=BaseModel)
"""BaseModel派生类型"""


def load_txt(file: StrPath, ext: str = ".txt") -> Result[str, Exception]:
    """Load text content from a file.

    Args:
        file: Path to the file to load.
        ext: Extension to add if file has no extension.

    Returns:
        Ok(str) with file content on success, Err with exception on failure.

    """
    file = or_ext(file, ext)
    try:
        with open(file, encoding="utf-8") as f:
            txt = f.read()
    except FileNotFoundError:
        return Err(FileNotFoundError(f"文件不存在: {file}"))
    except PermissionError:
        return Err(PermissionError(f"权限不足: {file}"))
    except OSError as e:
        return Err(OSError(f"读取文件失败 {file}: {e}"))
    return Ok(txt)


def to_json(ob: Any, pretty: bool = True) -> str:
    """Serialize an object to a JSON string.

    Uses pydantic_core for serialization, supporting Pydantic models
    and standard Python types.

    Args:
        ob: Object to serialize.
        pretty: If True, format with 4-space indentation.

    Returns:
        JSON string representation of the object.

    """
    indent = 4 if pretty else None
    byte_str = pydantic_core.to_json(ob, indent=indent)
    return byte_str.decode("utf-8")


def from_json(json: AnyStr, ob_type: type[BMT]) -> Result[BMT, Exception]:
    """Parse JSON text into a Pydantic model instance.

    Args:
        json: JSON string or bytes to parse.
        ob_type: Pydantic model class to parse into.

    Returns:
        Ok with parsed model instance on success, Err with exception on failure.

    """
    assert isinstance(json, str | bytes), "Invalid input type @ try_from_json"
    try:
        ob = ob_type.model_validate_json(json)
    except pydantic_core.ValidationError as e:
        return Err(e)
    except AttributeError as e:
        # 类型可能不是 BaseModel 子类（如 int, str 等基本类型）
        return Err(AttributeError(f"类型 {ob_type} 缺少 model_validate_json 方法: {e}"))
    except ValueError as e:
        return Err(ValueError(f"JSON验证失败: {e}"))
    return Ok(ob)


def save_json(obj: Any, file: StrPath, pretty: bool = True) -> Result[bool, Exception]:
    """Save an object to a JSON file.

    Args:
        obj: Object to serialize and save.
        file: Path to the output file (.json extension added if missing).
        pretty: If True, format with 4-space indentation.

    Returns:
        Ok(True) on success, Err with exception on failure.

    """
    file = or_ext(file, ".json")
    s = to_json(obj, pretty)
    return save_txt(s, file)


@result_shortcut
def load_json(file: StrPath, obj_type: type[BMT]) -> Result[BMT, Exception]:
    """Load and parse a JSON file into a Pydantic model instance.

    Args:
        file: Path to the JSON file (.json extension added if missing).
        obj_type: Pydantic model class to parse into.

    Returns:
        Ok with parsed model instance on success, Err with exception on failure.

    """
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
    """Load a JSON file or return a default value if no file is provided.

    Args:
        file: Path to the JSON file, or None to use default.
        obj_type: Pydantic model class to parse into.
        default_value: Value to return if file is None.

    Returns:
        Ok with parsed model or default value, Err with exception on parse failure.

    """
    return load_json(file, obj_type) if file else Ok(default_value)
