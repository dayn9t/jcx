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


class TaskInfo(Record):
    """任务信息

    包含任务基本信息，用于描述需要处理的视频分析任务
    """

    name: str
    """任务名称"""
    type: int
    """任务类型，例如视频跟踪、标记等不同处理类型"""
    created_at: Datetime = now_sh_dt()
    """任务创建时间，ISO格式字符串"""
    desc: str | None = None
    """任务描述信息，可选字段"""
    data: str
    """任务数据，存储任务相关的JSON数据或其他信息"""


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
    worker_id: str | None = None
    """执行任务的工作者标识，例如线程名或进程名"""


class TaskDb:
    def __init__(
        self,
        db_url: str,
        task_table_name: str = "task",
        status_table_name: str = "status",
    ):
        """初始化任务数据库管理器

        Args:
            db_url: 数据库URL，通常是文件路径或数据库连接字符串
            task_table_name: 任务表名称，默认为"task"
            status_table_name: 状态表名称，默认为"status"

        """
        self._db_url = db_url
        self._task_table_name = task_table_name
        self._status_table_name = status_table_name

    def add_task(self, task: TaskInfo) -> Option[TaskInfo]:
        """添加新任务记录

        Args:
            task: 任务记录实例

        Returns:
            Option[TaskRecord]: 添加后的任务记录，如果ID已存在则返回None
        """

        return Some(task)

    def get_task_status(self, task_id: int) -> Option[StatusInfo]:
        """获取指定任务的状态信息

        Args:
            task_id: 任务ID

        Returns:
            Option[StatusInfo]: 任务状态信息，如果任务不存在则返回None
        """
        pass

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

    def task_start(self, task_id: int, worker: str | None) -> None:
        """开始执行指定任务"""
        status: StatusInfo = self.status_tab.get(task_id).unwrap()
        if status.status == TaskStatus.NOT_STARTED:
            status.status = TaskStatus.IN_PROGRESS
            status.start_time = now_sh_dt()
            status.update_time = status.start_time
            status.worker_id = worker
            self.status_tab.put(status)
        else:
            raise ValueError("任务已开始或已完成，无法重新开始")

    def task_done(self, task_id: int) -> None:
        """终结指定任务"""
        self.update_progress(task_id, 100)

    def task_error(self, task_id: int) -> None:
        """标记指定任务为出错"""
        status: StatusInfo = self.status_tab.get(task_id).unwrap()
        status.status = TaskStatus.ERROR
        status.update_time = now_sh_dt()
        self.status_tab.put(status)

    def update_progress(self, task_id: int, progress: int) -> None:
        """更新指定任务进度"""
        status: StatusInfo = self.status_tab.get(task_id).unwrap()
        if status.status >= TaskStatus.COMPLETED:
            raise ValueError("任务已完成，无法更新进度")
        if not (0 <= progress <= 100):
            raise ValueError("进度值必须在0到100之间")
        if status.status == TaskStatus.NOT_STARTED:
            status.status = TaskStatus.IN_PROGRESS
        if status.status == TaskStatus.IN_PROGRESS and progress == 100:
            status.status = TaskStatus.COMPLETED
        status.progress = progress
        status.update_time = now_sh_dt()
        if status.start_time is None:
            status.start_time = status.update_time
        self.status_tab.put(status)
