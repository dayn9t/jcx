"""Clock time representation and parsing utilities.

This module provides the ClockTime class for representing time of day
(hours, minutes, seconds) without date information.
"""

from typing import Self

from arrow import Arrow
# parse library (v1.20.2) has no type stubs available
from parse import parse  # type: ignore[import]
from pydantic.dataclasses import dataclass
from rustshed import Null, Option, Some


# @total_ordering
@dataclass(frozen=True, order=True)
class ClockTime:
    """Clock time representation (hours, minutes, seconds).

    A frozen dataclass representing a time of day without date information.
    Supports ordering comparisons and conversion to/from various formats.

    Attributes:
        hour: Hour component (0-23).
        minute: Minute component (0-59).
        second: Second component (0-59).
    """

    hour: int = 0
    """小时"""
    minute: int = 0
    """分钟"""
    second: int = 0
    """秒"""

    @classmethod
    def new(cls, hour: int, minute: int, second: int) -> Self:
        """Create a new ClockTime instance.

        Args:
            hour: Hour component (0-23).
            minute: Minute component (0-59).
            second: Second component (0-59).

        Returns:
            A new ClockTime instance.
        """
        return ClockTime(hour=hour, minute=minute, second=second)

    @classmethod
    def from_secs(cls, secs: int) -> Self:
        """Create a ClockTime from total seconds.

        Args:
            secs: Total seconds from midnight.

        Returns:
            ClockTime instance calculated from total seconds.
        """
        minute, second = divmod(secs, 60)
        hour, minute = divmod(minute, 60)
        return ClockTime(hour=hour, minute=minute, second=second)

    @staticmethod
    def from_time(t: Arrow) -> "ClockTime":
        """Extract ClockTime from an Arrow datetime.

        Args:
            t: Arrow datetime object.

        Returns:
            ClockTime with the hour, minute, second from the datetime.
        """
        return ClockTime(hour=t.hour, minute=t.minute, second=t.second)

    @staticmethod
    def parse(s: str) -> Option["ClockTime"]:
        """Parse a time string in "HH:MM:SS" format.

        Args:
            s: Time string to parse (e.g., "14:30:00").

        Returns:
            Some(ClockTime) if parsing succeeds, Null otherwise.
        """
        arr = parse("{:d}:{:d}:{:d}", s)
        if arr:
            return Some(ClockTime(hour=arr[0], minute=arr[1], second=arr[2]))
        return Null

    def __str__(self) -> str:
        """Return formatted time string "HH:MM:SS"."""
        return "%02d:%02d:%02d" % (self.hour, self.minute, self.second)

    def to_time(self) -> Arrow:
        """Convert to Arrow datetime using today's date.

        Returns:
            Arrow datetime with today's date and this time.
        """
        t = Arrow.now()
        # now.date()
        return t.replace(
            hour=self.hour,
            minute=self.minute,
            second=self.second,
            microsecond=0,
        )


type ClockTimes = list[ClockTime]  # 时钟时间列表


def to_clock_time(time: ClockTime | str | Arrow) -> Option[ClockTime]:
    """Convert various time representations to ClockTime.

    Args:
        time: Time value to convert. Can be:
            - ClockTime: returned as-is
            - str: parsed as "HH:MM:SS" format
            - Arrow: hour/minute/second extracted

    Returns:
        Some(ClockTime) if conversion succeeds, Null otherwise.
    """
    if isinstance(time, ClockTime):
        return Some(time)
    if isinstance(time, str):
        return ClockTime.parse(time)
    if isinstance(time, Arrow):
        return Some(ClockTime.from_time(time))

    return Null
