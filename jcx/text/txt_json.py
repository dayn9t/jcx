import json
from typing import TypeVar, Type, Any

from cattr import unstructure, structure
from jcx.sys.fs import or_ext, StrPath
from jcx.text.io import save_txt
from rustshed import Option, Some, Null

"""
序列化可选替代技术:
- https://pypi.org/project/dataclass-wizard/

"""

T = TypeVar("T")


def load_txt(file: StrPath, ext: str = '.txt') -> Option[str]:
    """从文件加载文本"""
    file = or_ext(file, ext)
    if not file.is_file():
        return Null
    with open(file, 'r', encoding='utf-8') as f:
        txt = f.read()
    return Some(txt)


def to_json(obj: Any, pretty: bool = True) -> str:
    """对象序列化为JSON"""
    m = unstructure(obj)
    indent = 4 if pretty else None
    return json.dumps(m, ensure_ascii=False, indent=indent)


def try_from_json(s: str | bytes, obj_type: Type[T]) -> Option[T]:
    """从JSON文本构建对象"""
    assert isinstance(s, str | bytes), 'Invalid input type @ try_from_json'
    m = json.loads(s)
    return Some(structure(m, obj_type))


def from_json(s: str | bytes, obj_type: Type[T]) -> T:
    """从JSON文本构建对象"""
    return try_from_json(s, obj_type).unwrap()


def save_json(obj: Any, file: StrPath, pretty: bool = True) -> None:
    """对象序保存为JSON文件"""
    file = or_ext(file, '.json')
    s = to_json(obj, pretty)
    save_txt(s, file)


def try_load_json(file: StrPath, obj_type: Type[T]) -> Option[T]:
    """从Json文件加载对象"""
    file = or_ext(file, '.json')
    s = load_txt(file)
    if s.is_null():
        return Null
    # print('load_json:', file)
    return try_from_json(s.unwrap(), obj_type)


def load_json(file: StrPath, obj_type: Type[T]) -> T:
    """从Json文件加载对象"""
    return try_load_json(file, obj_type).unwrap()
