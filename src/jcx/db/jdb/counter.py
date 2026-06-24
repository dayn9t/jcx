from pathlib import Path

from jcx.db.counter import Counter
from jcx.db.jdb.json_variant import JsonVariant


class JdbCounter(Counter):
    """Jdb 计数器——基于 JSON 文件持久化的自增整数"""

    def __init__(self, db: Path, name: str) -> None:
        super().__init__(JsonVariant(int, db, name))
