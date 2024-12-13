from pathlib import Path

from pydantic import BaseModel

from jcx.db.counter import Counter
from jcx.db.jdb.variant import JdbVariant

class Item(BaseModel):
    """数据库记录"""
    id: int


class JdbCounter(Counter):
    """Jdb计数器"""

    def __init__(self, db: Path, name: str):
        super().__init__(JdbVariant(int, db, name))
