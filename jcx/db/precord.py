from copy import deepcopy
from dataclasses import dataclass
from typing import Final, TypeVar, TypeAlias, Callable
from typing import Protocol

Self = TypeVar('Self', bound='PRecord')


class PRecord(Protocol):
    """数据库记录"""
    id: int
    """记录ID"""

    def clone(self: Self) -> Self:
        """克隆记录"""
        return deepcopy(self)


RecordFilter: TypeAlias = Callable[[PRecord], bool]
"""记录过滤器"""


@dataclass
class DemoRecord(PRecord):
    """用于演示/测试的记录"""
    id: int
    name: str


R1: Final[DemoRecord] = DemoRecord(1, 'group1')
R2: Final[DemoRecord] = DemoRecord(2, 'group2')

GROUP_DIR: Final[str] = '/opt/ias/project/shtm/node/n1/db/group'
