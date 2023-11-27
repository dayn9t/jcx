from typing import Final

from attr import dataclass

from jcx.db.precord import PRecord


@dataclass
class DemoRecord(PRecord):
    """用于演示/测试的记录"""
    id: int
    name: str


R1: Final[DemoRecord] = DemoRecord(1, 'group1')
R2: Final[DemoRecord] = DemoRecord(2, 'group2')

GROUP_DIR: Final[str] = '/opt/ias/project/shtm/node/n1/db/group'
