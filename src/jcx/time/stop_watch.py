#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from typing import List, Optional


class StopWatch:
    """统计程序运行时间的类，支持记录单次运行时间、平均时间、最大/最小时间"""

    def __init__(self, name: str = ""):
        """初始化运行时间统计类

        Args:
            name: 统计器名称，可选
        """
        self.name = name
        self.times: List[float] = []
        self._start: float = 0

    def start(self) -> None:
        """开始计时"""
        self._start = time.perf_counter()

    def stop(self) -> float:
        """停止计时并返回耗时

        Returns:
            本次运行耗时(秒)
        """
        elapsed = time.perf_counter() - self._start
        self.times.append(elapsed)
        return elapsed

    def last(self) -> Optional[float]:
        """获取最后一次运行时间

        Returns:
            最后一次运行的时间(秒)，如果没有记录则返回None
        """
        return self.times[-1] if self.times else None

    def avg(self) -> Optional[float]:
        """获取平均运行时间

        Returns:
            平均运行时间(秒)，如果没有记录则返回None
        """
        return sum(self.times) / len(self.times) if self.times else None

    def max(self) -> Optional[float]:
        """获取最大运行时间

        Returns:
            最大运行时间(秒)，如果没有记录则返回None
        """
        return max(self.times) if self.times else None

    def min(self) -> Optional[float]:
        """获取最小运行时间

        Returns:
            最小运行时间(秒)，如果没有记录则返回None
        """
        return min(self.times) if self.times else None

    def reset(self) -> None:
        """重置统计数据"""
        self.times.clear()

    def count(self) -> int:
        """获取统计次数

        Returns:
            已统计的运行次数
        """
        return len(self.times)

    def __enter__(self) -> "StopWatch":
        """上下文管理器支持 - 进入时开始计时"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """上下文管理器支持 - 退出时停止计时"""
        self.stop()

    def __str__(self) -> str:
        """字符串表示，包含统计信息"""
        name_str = f"[{self.name}] " if self.name else ""
        if not self.times:
            return f"{name_str}RunTimeStats: No records"

        return (
            f"{name_str}RunTimeStats: count={self.count()}, "
            f"last={self.last():.6f}s, avg={self.avg():.6f}s, "
            f"min={self.min():.6f}s, max={self.max():.6f}s"
        )
