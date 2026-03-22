"""Calendar-based trigger types for scheduling.

This module provides types for defining time-based triggers that can
check if a given time falls within specified periods and weekdays.
"""

from typing import Literal

from arrow import Arrow
from pydantic import BaseModel, ConfigDict
from rustshed import Err, Ok, Result

from jcx.time.clock_time import ClockTime

type Weekday = Literal[0, 1, 2, 3, 4, 5, 6]
"""星期几 (0=周一, 6=周日)"""


class ClockPeriod(BaseModel):
    """Clock time period representing a half-open interval [begin, end).

    Attributes:
        begin: Start time of the period (inclusive).
        end: End time of the period (exclusive).

    """

    model_config: ConfigDict = ConfigDict(frozen=True)

    begin: ClockTime = ClockTime()
    """起始时间"""
    end: ClockTime = ClockTime()
    """截至时间"""

    def __str__(self) -> str:
        """Return string representation "[begin,end)"."""
        return "[%s,%s)" % (self.begin, self.end)

    def __contains__(self, clock_time: ClockTime) -> bool:
        """Check if a ClockTime falls within this period.

        Args:
            clock_time: Time to check.

        Returns:
            True if begin <= clock_time < end.

        """
        return self.begin <= clock_time < self.end


type ClockPeriods = list[ClockPeriod]
"""时钟时间段集合"""


class CalendarTrigger(BaseModel):
    """Calendar-based trigger for scheduling.

    Combines time periods with optional weekday restrictions to determine
    if a given time should trigger an action.

    Attributes:
        periods: List of time periods during which triggers are allowed.
        weekdays: Optional list of allowed weekdays (0=Monday, 6=Sunday).
                  None means no weekday restriction.

    """

    model_config: ConfigDict = ConfigDict(frozen=True)

    periods: ClockPeriods
    """触发时段集合"""
    weekdays: list[Weekday] | None = None
    """允许触发的星期几 (0=周一, 6=周日), None表示不限制"""

    def start_time(self) -> ClockTime:
        """Get the earliest start time from all periods.

        Returns:
            The begin time of the first period, or ClockTime() if no periods.

        """
        return self.periods[0].begin if self.periods else ClockTime()

    def check(self, clock_time: ClockTime, dt: Arrow | None = None) -> bool:
        """Check if the given time satisfies the calendar trigger conditions.

        Args:
            clock_time: Clock time to check.
            dt: Full datetime for weekday checking. If None and weekdays is set,
                uses the current date.

        Returns:
            True if the time is within a period and on an allowed weekday.

        """
        # 时段检查
        if self.periods:
            ok = any(clock_time in p for p in self.periods)
            if not ok:
                return False

        # 星期检查
        if self.weekdays is not None:
            check_dt = dt if dt is not None else Arrow.now()
            if check_dt.weekday() not in self.weekdays:
                return False

        return True

    def valid(self) -> Result[bool, str]:
        """Validate that the trigger has at least one period defined.

        Returns:
            Ok(True) if valid, Err with message if no periods defined.

        """
        if len(self.periods) > 0:
            return Ok(True)
        return Err("日程表触发器时段不存在")


type CalendarTriggers = list[CalendarTrigger]  # 时钟时间段集合
