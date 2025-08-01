from typing import Generic, TypeVar, Optional
from enum import IntEnum
from pydantic import BaseModel

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


T = TypeVar("T", bound=Record)


class TaskDb(Generic[T]):
    def __init__(
        self,
        db_url: str,
        task_record_class: type[T],
        task_table_name: str = "task",
        status_table_name: str = "status",
    ):
        """初始化任务数据库管理器

        Args:
            db_url: 数据库URL，通常是文件路径或数据库连接字符串
            task_record_class: 任务记录类型
            task_table_name: 任务表名称，默认为"task"
            status_table_name: 状态表名称，默认为"status"

        """
        self._db_url = db_url
        self._task_record_class = task_record_class
        self._task_table_name = task_table_name
        self._status_table_name = status_table_name

    def add_task(self, task: T) -> Option[T]:
        """添加新任务记录

        Args:
            task: 任务记录实例

        Returns:
            Option[T]: 添加后的任务记录，如果ID已存在则返回None
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

    def get_task(self, task_id: int) -> Option[T]:
        """获取指定ID的任务

        Args:
            task_id: 任务ID

        Returns:
            Option[T]: 任务记录，如果任务不存在则返回None
        """
        pass

    def get_all_tasks(self) -> list[T]:
        """获取所有任务

        Returns:
            list[T]: 所有任务记录列表
        """
        return []

    def update_task_status(self, task_id: int, status_info: StatusInfo) -> bool:
        """更新任务状态

        Args:
            task_id: 任务ID
            status_info: 新的状态信息

        Returns:
            bool: 更新是否成功
        """
        return True

    def delete_task(self, task_id: int) -> bool:
        """删除任务及其状态信息

        Args:
            task_id: 任务ID

        Returns:
            bool: 删除是否成功
        """
        return True

    def show(self) -> None:
        """显示所有任务信息"""
        for task in self.get_all_tasks():
            print(to_json(task))
