from jcx.text.txt_json import from_json
from jcx.time.calendar_type import *
from jcx.time.clock_time import to_clock_time


def test_period() -> None:
    c1 = ClockTime.parse('01:00:00').unwrap()
    c2 = ClockTime.parse('02:00:00').unwrap()

    p = ClockPeriod(begin=c1, end=c2)
    print('1:', c1, p)
    assert c1 in p
    assert c2 not in p

    calendar = CalendarTrigger(periods=[p])
    assert calendar.check(c1)
    assert not calendar.check(c2)


def test_calendar() -> None:
    c1 = to_clock_time('07:00:00').unwrap()
    c2 = to_clock_time('23:00:00').unwrap()

    p = ClockPeriod(begin=c1, end=c2)
    calendar1 = CalendarTrigger(periods=[p])
    # print('calendar1:', calendar1)

    txt = """
    {
        "periods": [
            {
                "begin": {
                    "hour": 7
                },
                "end": {
                    "hour": 23
                }
            }
        ]
    }
    """
    calendar2 = from_json(txt, CalendarTrigger).unwrap()
    assert calendar1 == calendar2
