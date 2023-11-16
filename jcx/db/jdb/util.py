from pathlib import Path
from typing import TypeVar, Type

from jcx.db.precord import PRecord, RecordFilter
from jcx.sys.fs import StrPath
from jcx.text.txt_json import load_json
from rustshed import Option, Null

R = TypeVar("R", bound=PRecord)


def load_list(record_type: Type[R], folder: StrPath, filter_: Option[RecordFilter] = Null) -> list[R]:
    """加载记录到列表"""
    records: list[R] = []

    folder = Path(folder)
    if not folder.is_dir():
        return records

    for f in folder.glob('*.json'):
        r = load_json(f, record_type)
        if filter_.is_some() and not filter_.unwrap()(r):
            continue
        records.append(r)
    return records


def load_dict(record_type: Type[R], folder: StrPath, filter_: Option[RecordFilter] = Null) -> dict[int, R]:
    """加载记录到字典"""
    rs = load_list(record_type, folder, filter_)
    return {r.id: r for r in rs}
