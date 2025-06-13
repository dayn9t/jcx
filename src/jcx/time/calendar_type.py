from pydantic import BaseModel
from rustshed import Err, Ok, Result

from jcx.time.clock_time import ClockTime


class ClockPeriod(BaseModel):
    """时钟时间段"""

    begin: ClockTime = ClockTime()
    """起始时间"""
    end: ClockTime = ClockTime()
    """截至时间"""

    class Config:
        frozen = True

    def __str__(self) -> str:
        return "[%s,%s)" % (self.begin, self.end)

    def __contains__(self, clock_time: ClockTime) -> bool:
        return self.begin <= clock_time < self.end


type ClockPeriods = list[ClockPeriod]
"""时钟时间段集合"""


class CalendarTrigger(BaseModel):
    """日程表触发器"""

    periods: ClockPeriods
    """触发时段集合"""

    class Config:
        frozen = True

    def start_time(self) -> ClockTime:
        """日程的开始时间"""
        return self.periods[0].begin if self.periods else ClockTime()

    def check(self, clock_time: ClockTime) -> bool:
        """判定时间是否满足日历触发条件"""
        # 时段检查
        ok = False
        if self.periods:
            for p in self.periods:
                if clock_time in p:
                    ok = True
                    break
        else:
            ok = True
        # 检查星期 TODO:
        return ok

    def valid(self) -> Result[bool, str]:
        """判断是否有效"""
        if len(self.periods) > 0:
            return Ok(True)
        return Err("日程表触发器时段不存在")


type CalendarTriggers = list[CalendarTrigger]  # 时钟时间段集合
