import warnings
from pathlib import Path
from typing import TypeVar

from jcx.db.record import Record, RecordFilter, RecordSid, RecordSidFilter
from jcx.sys.fs import StrPath
from jcx.text.txt_json import load_json

R = TypeVar("R", bound=Record)


def load_list[R: Record](
    record_type: type[R],
    folder: StrPath,
    filter_: RecordFilter | None = None,
) -> list[R]:
    """加载记录到列表"""
    records: list[R] = []

    folder = Path(folder)
    if not folder.is_dir():
        return records

    for f in folder.glob("*.json"):
        result = load_json(f, record_type)
        if result.is_err():
            warnings.warn(f"Failed to load {f}: {result.unwrap_err()}", stacklevel=2)
            continue
        r = result.unwrap()
        if filter_ and not filter_(r):
            continue
        records.append(r)
    return records


def load_dict[R: Record](
    record_type: type[R],
    folder: StrPath,
    filter_: RecordFilter | None = None,
) -> dict[int, R]:
    """加载记录到字典"""
    rs = load_list(record_type, folder, filter_)
    return {r.id: r for r in rs}


def load_sid_list[R: RecordSid](
    record_type: type[R],
    folder: StrPath,
    filter_: RecordSidFilter | None = None,
) -> list[R]:
    """加载字符串主键记录到列表（与 [`load_list`] 并列，供 `TableSid` 消费）"""
    records: list[R] = []

    folder = Path(folder)
    if not folder.is_dir():
        return records

    for f in folder.glob("*.json"):
        result = load_json(f, record_type)
        if result.is_err():
            warnings.warn(f"Failed to load {f}: {result.unwrap_err()}", stacklevel=2)
            continue
        r = result.unwrap()
        if filter_ and not filter_(r):
            continue
        records.append(r)
    return records


def load_sid_dict[R: RecordSid](
    record_type: type[R],
    folder: StrPath,
    filter_: RecordSidFilter | None = None,
) -> dict[str, R]:
    """加载字符串主键记录到字典"""
    rs = load_sid_list(record_type, folder, filter_)
    return {r.id: r for r in rs}
