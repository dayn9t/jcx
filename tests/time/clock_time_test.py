from jcx.time.clock_time import *


def test_convert() -> None:
    c1 = ClockTime(1, 1, 1)
    c2 = ClockTime.from_time(c1.to_time())
    assert c1 == c2


def test_all() -> None:
    tab = {
        "01:01:01": Some(ClockTime(1, 1, 1)),
        "00:00:00": Some(ClockTime(0, 0, 0)),
        "aa:00:00": Null,
    }

    for k, v in tab.items():
        c = ClockTime.parse(k)
        assert c == v
        if c.is_some():
            assert str(c.unwrap()) == k

    c1 = ClockTime(1, 0, 0)
    c2 = ClockTime(2, 0, 0)
    c3 = ClockTime(3, 0, 0)
    c4 = ClockTime(4, 0, 0)
    assert ClockTime(1, 1, 1) > ClockTime(0, 0, 0)
    assert ClockTime(1, 1, 1) > ClockTime(0, 9, 9)
    assert ClockTime(1, 1, 1) >= ClockTime(0, 0, 9)
    assert ClockTime(1, 1, 1) <= ClockTime(1, 1, 1)

    # 闭区间 [c1, c3] 包含性（原用 interval 库，改直接比较以减少依赖）
    assert c1 <= c1 <= c3
    assert c1 <= c2 <= c3
    assert c1 <= c3 <= c3
    assert not (c1 <= c4 <= c3)
