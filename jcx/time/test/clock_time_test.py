from jcx.time.clock_time import ClockTime


def test_clock_time() -> None:
    c1 = ClockTime.from_secs(3600)
    c2 = ClockTime(1, 0, 0)
    assert c1 == c2
