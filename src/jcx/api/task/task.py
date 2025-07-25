from typing import Generic
from enum import IntEnum

from jcx.db.jdb.table import *
from jcx.db.record import Record
from jcx.text.txt_json import to_json
from jcx.time.dt_util import now_sh_dt, Datetime


class TaskStatus(IntEnum):
    """任务状态枚举类型"""

    NOT_STARTED = 0  # 未启动
    IN_PROGRESS = 1  # 进行中
    COMPLETED = 2  # 完成
    ERROR = 3  # 出错


class TaskInfoBase(Record):
    """任务信息基础类

    包含任务基本信息，用于描述需要处理的视频分析任务
    """

    name: str
    """任务名称"""
    type: int
    """任务类型，例如视频跟踪、标记等不同处理类型"""
    created_at: Datetime = now_sh_dt()
    """任务创建时间，ISO格式字符串"""


TaskRecord = TypeVar("TaskRecord", bound=TaskInfoBase)
"""任务记录类型"""


class StatusInfo(Record):
    """任务状态记录类

    记录任务的状态信息，用于跟踪任务的执行进度和状态
    """

    status: TaskStatus = TaskStatus.NOT_STARTED
    """任务状态码，0-未启动，1-进行，2-完成，3-出错"""
    progress: int = 0
    """任务进度值，范围从起始进度到结束进度"""
    start_time: Datetime | None = None
    """任务开始执行时间"""
    update_time: Datetime | None = None
    """任务数据更新时间"""
    enabled: bool = True
    """任务是否启用"""
    worker: str | None = None
    """执行任务的工作者标识，例如线程名或进程名"""


class TaskDb(Generic[TaskRecord]):
    def __init__(
        self,
        db_dir: Path,
        task_record_cls: type[TaskRecord],
        task_table_name: str = "task",
        status_table_name: str = "status",
    ):
        """初始化任务数据库管理器

        Args:
            db_dir: 数据库目录路径
            task_record_cls: 任务记录类，必须是 TaskInfoBase 的子类

        """
        self.task_tab = Table(task_record_cls)
        self.status_tab = Table(StatusInfo)
        self.task_tab.load(db_dir / task_table_name)
        self.status_tab.load(db_dir / status_table_name)

    def show(self) -> None:
        for task in self.task_tab.records():
            print(to_json(task))
        for status in self.status_tab.records():
            print(to_json(status))

    def find_task(self) -> Option[tuple[TaskRecord, StatusInfo]]:
        """找到可执行任务"""
        for status in self.status_tab.records():
            if not status.enabled or status.status > TaskStatus.IN_PROGRESS:
                continue

            task = self.task_tab.get(status.id).unwrap()
            return Some((task, status))
        return Null

    def task_done(self, task_id: int) -> None:
        """终结指定任务"""
        self.update_progress(task_id, 100)

    def task_error(self, task_id: int) -> None:
        """标记指定任务为出错"""
        status: StatusInfo = self.status_tab.get(task_id).unwrap()
        status.status = TaskStatus.ERROR
        status.update_time = now_sh_dt()
        self.status_tab.update(status)

    def update_progress(self, task_id: int, progress: int) -> None:
        """更新指定任务进度"""
        status: StatusInfo = self.status_tab.get(task_id).unwrap()
        assert status.status < TaskStatus.COMPLETED, "任务已完成，无法更新进度"
        assert 0 <= progress <= 100, "进度值必须在0到100之间"
        if status.status == TaskStatus.NOT_STARTED:
            status.status = TaskStatus.IN_PROGRESS
        if status.status == TaskStatus.IN_PROGRESS and progress == 100:
            status.status = TaskStatus.COMPLETED
        status.progress = progress
        status.update_time = now_sh_dt()
        if status.start_time is None:
            status.start_time = status.update_time
        self.status_tab.update(status)
