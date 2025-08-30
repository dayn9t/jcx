import datetime
from zoneinfo import ZoneInfo

from jcx.text.txt_json import to_json
from jcx.time.dt_util import now_sh_dt


def test_now_utc_dt_returns_datetime():
    """测试now_utc_dt函数返回datetime类型"""
    result = now_sh_dt()
    assert isinstance(result, datetime.datetime)


def test_now_utc_dt_timezone_is_utc():
    """测试now_utc_dt返回的datetime对象时区是UTC"""
    result = now_sh_dt()
    assert result.tzinfo == ZoneInfo("UTC")


def test_now_utc_dt_correct_time():
    """测试now_utc_dt返回的时间正确"""
    result = now_sh_dt()

    s = to_json(result)
    assert s.endswith('+08:00"')
