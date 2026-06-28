import datetime
from zoneinfo import ZoneInfo

type Datetime = datetime.datetime
"""时间类型别名"""


def now_sh_dt() -> Datetime:
    """获取当前时间的datetime对象，带有上海时区信息"""
    return datetime.datetime.now(ZoneInfo("Asia/Shanghai"))
