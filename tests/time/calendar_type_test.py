from datetime import datetime

from arrow import Arrow

from jcx.text.txt_json import from_json
from jcx.time.calendar_type import *
from jcx.time.clock_time import to_clock_time


def test_period() -> None:
    c1 = ClockTime.parse("01:00:00").unwrap()
    c2 = ClockTime.parse("02:00:00").unwrap()

    p = ClockPeriod(begin=c1, end=c2)
    print("1:", c1, p)
    assert c1 in p
    assert c2 not in p

    calendar = CalendarTrigger(periods=[p])
    assert calendar.check(c1)
    assert not calendar.check(c2)


def test_calendar() -> None:
    c1 = to_clock_time("07:00:00").unwrap()
    c2 = to_clock_time("23:00:00").unwrap()

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


class TestCalendarTriggerWeekdays:
    """Tests for CalendarTrigger weekday filtering."""

    def test_no_weekday_restriction(self):
        """Test that None weekdays allows all days."""
        trigger = CalendarTrigger(
            periods=[],
            weekdays=None
        )
        # Should accept any day - test with various weekdays
        for day_offset in range(7):  # Monday to Sunday
            dt = Arrow.fromdatetime(datetime(2026, 3, 23 + day_offset))  # Mon 23 through Sun 29
            ct = ClockTime.from_time(dt)
            assert trigger.check(ct) is True

    def test_weekdays_only(self):
        """Test filtering for weekdays (Mon-Fri)."""
        trigger = CalendarTrigger(
            periods=[],
            weekdays=[0, 1, 2, 3, 4]  # Mon-Fri
        )
        # Monday (0) should pass
        dt_monday = Arrow.fromdatetime(datetime(2026, 3, 23))  # Monday
        ct_monday = ClockTime.from_time(dt_monday)
        assert trigger.check(ct_monday, dt_monday) is True

        # Saturday (5) should fail
        dt_saturday = Arrow.fromdatetime(datetime(2026, 3, 28))  # Saturday
        ct_saturday = ClockTime.from_time(dt_saturday)
        assert trigger.check(ct_saturday, dt_saturday) is False

    def test_weekends_only(self):
        """Test filtering for weekends (Sat-Sun)."""
        trigger = CalendarTrigger(
            periods=[],
            weekdays=[5, 6]  # Sat-Sun
        )
        # Saturday (5) should pass
        dt_saturday = Arrow.fromdatetime(datetime(2026, 3, 28))
        ct_saturday = ClockTime.from_time(dt_saturday)
        assert trigger.check(ct_saturday, dt_saturday) is True

        # Monday (0) should fail
        dt_monday = Arrow.fromdatetime(datetime(2026, 3, 23))
        ct_monday = ClockTime.from_time(dt_monday)
        assert trigger.check(ct_monday, dt_monday) is False

    def test_combined_periods_and_weekdays(self):
        """Test that both periods and weekdays must match."""
        # Create period for 9am-5pm
        period = ClockPeriod(
            begin=ClockTime(hour=9, minute=0),
            end=ClockTime(hour=17, minute=0)
        )
        trigger = CalendarTrigger(
            periods=[period],
            weekdays=[0, 1, 2, 3, 4]  # Mon-Fri
        )
        # Monday 10am - should pass both checks
        ct_weekday_work_hour = ClockTime.from_time(
            Arrow.fromdatetime(datetime(2026, 3, 23, 10, 0))  # Monday 10am
        )
        dt_weekday = Arrow.fromdatetime(datetime(2026, 3, 23, 10, 0))
        assert trigger.check(ct_weekday_work_hour, dt_weekday) is True

        # Saturday 10am - passes time but fails weekday
        ct_weekend_work_hour = ClockTime.from_time(
            Arrow.fromdatetime(datetime(2026, 3, 28, 10, 0))  # Saturday 10am
        )
        dt_weekend = Arrow.fromdatetime(datetime(2026, 3, 28, 10, 0))
        assert trigger.check(ct_weekend_work_hour, dt_weekend) is False
