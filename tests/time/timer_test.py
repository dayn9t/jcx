from jcx.time.timer import *


def test_timer() -> None:
    day1 = Arrow(2000, 1, 1)
    day2 = Arrow(2000, 1, 2)
    day3 = Arrow(2000, 1, 3)
    day4 = Arrow(2000, 1, 4)
    d2 = timedelta(days=2)

    timer = Timer(day1)
    print('t:', timer)

    assert timer.next(d2) == day3
    assert not timer.check(day2, d2)
    assert timer.check(day3, d2)
    assert timer.check(day4, d2)

    timer.update(day2)
    assert not timer.check(day3, d2)
    assert timer.check(day4, d2)
