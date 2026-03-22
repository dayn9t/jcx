from typing import Literal

from arrow import Arrow
from pydantic import BaseModel, ConfigDict
from rustshed import Err, Ok, Result

from jcx.time.clock_time import ClockTime

type Weekday = Literal[0, 1, 2, 3, 4, 5, 6]
"""星期几 (0=周一, 6=周日)"""


class ClockPeriod(BaseModel):
    """时钟时间段"""

    model_config = ConfigDict(frozen=True)

    begin: ClockTime = ClockTime()
    """起始时间"""
    end: ClockTime = ClockTime()
    """截至时间"""

    def __str__(self) -> str:
        return "[%s,%s)" % (self.begin, self.end)

    def __contains__(self, clock_time: ClockTime) -> bool:
        return self.begin <= clock_time < self.end


type ClockPeriods = list[ClockPeriod]
"""时钟时间段集合"""


class CalendarTrigger(BaseModel):
    """日程表触发器"""

    model_config = ConfigDict(frozen=True)

    periods: ClockPeriods
    """触发时段集合"""
    weekdays: list[Weekday] | None = None
    """允许触发的星期几 (0=周一, 6=周日), None表示不限制"""

    def start_time(self) -> ClockTime:
        """日程的开始时间"""
        return self.periods[0].begin if self.periods else ClockTime()

    def check(self, clock_time: ClockTime, dt: Arrow | None = None) -> bool:
        """判定时间是否满足日历触发条件

        Args:
            clock_time: 时钟时间
            dt: 完整日期时间，用于星期检查。如果为None且设置了weekdays，则使用当前日期

        Returns:
            是否满足触发条件

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
        """判断是否有效"""
        if len(self.periods) > 0:
            return Ok(True)
        return Err("日程表触发器时段不存在")


type CalendarTriggers = list[CalendarTrigger]  # 时钟时间段集合
