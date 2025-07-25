import datetime
from typing import TypeAlias
from zoneinfo import ZoneInfo

Datetime: TypeAlias = datetime.datetime
"""时间类型别名"""


def now_sh_dt() -> Datetime:
    """获取当前时间的datetime对象，带有上海时区信息"""
    now = Datetime.now(ZoneInfo("Asia/Shanghai"))
    return now
