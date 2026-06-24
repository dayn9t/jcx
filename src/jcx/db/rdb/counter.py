from jcx.db.counter import Counter
from jcx.db.rdb.db import RedisDb
from jcx.db.rdb.variant import RedisVariant


class RedisCounter(Counter):
    """Redis计数器"""

    def __init__(self, db: RedisDb, name: str) -> None:
        super().__init__(RedisVariant(int, db, name))
