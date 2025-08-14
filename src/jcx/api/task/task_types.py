from enum import IntEnum

from rich.table import Table

from jcx.db.record import RecordSid
from jcx.time.dt_util import now_sh_dt, Datetime


class TaskStatus(IntEnum):
    """任务状态枚举类型"""

    PENDING = 0  # 未启动
    IN_PROGRESS = 1  # 进行中
    COMPLETED = 2  # 完成
    ERROR = 3  # 出错


class TaskInfo(RecordSid):
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


class StatusInfo(RecordSid):
    """任务状态记录类

    记录任务的状态信息，用于跟踪任务的执行进度和状态
    """

    status: TaskStatus = TaskStatus.PENDING
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


def task_table(task: TaskInfo) -> Table:
    """格式化显示单个任务信息

    Args:
        task: 要显示的任务信息对象
    """
    table = Table(title=f"任务 #{task.id}: {task.name}")

    table.add_column("字段", style="cyan")
    table.add_column("值", style="green")

    table.add_row("ID", str(task.id))
    table.add_row("名称", task.name)
    table.add_row("类型", str(task.type))
    table.add_row("创建时间", str(task.created_at))
    table.add_row("描述", task.desc or "无")
    table.add_row("数据", task.data)

    return table


def tasks_table(tasks: list[TaskInfo]) -> Table:
    """格式化显示任务列表

    Args:
        tasks: 任务列表
    """
    table = Table(title="任务列表")

    table.add_column("ID", style="cyan")
    table.add_column("名称", style="green")
    table.add_column("类型", style="blue")
    table.add_column("创建时间", style="magenta")
    table.add_column("数据", style="white")
    table.add_column("描述", style="yellow")

    for task in tasks:
        table.add_row(
            str(task.id),
            task.name,
            str(task.type),
            str(task.created_at),
            task.data,
            task.desc or "无",
        )

    return table


def status_table(status: StatusInfo) -> Table:
    """格式化显示单个任务状态信息

    Args:
        status: 要显示的任务状态对象
    """
    table = Table(title=f"任务状态 #{status.id}")

    table.add_column("字段", style="cyan")
    table.add_column("值", style="green")

    table.add_row("ID", str(status.id))
    table.add_row("状态", f"{status.status.name} ({status.status.value})")
    table.add_row("进度", f"{status.progress}%")
    table.add_row("开始时间", str(status.start_time or "未开始"))
    table.add_row("更新时间", str(status.update_time or "未更新"))
    table.add_row("启用状态", "启用" if status.enabled else "禁用")

    return table


def status_list_table(statuses: list[StatusInfo]) -> Table:
    """格式化显示任务状态列表

    Args:
        statuses: 任务状态列表
    """
    table = Table(title="任务状态列表")

    table.add_column("ID", style="cyan")
    table.add_column("状态", style="green")
    table.add_column("进度", style="blue")
    table.add_column("开始时间", style="magenta")
    table.add_column("更新时间", style="yellow")
    table.add_column("启用", style="cyan")

    for status in statuses:
        status_name = f"{status.status.name} ({status.status.value})"
        start_time = str(status.start_time or "未开始")
        update_time = str(status.update_time or "未更新")

        table.add_row(
            str(status.id),
            status_name,
            f"{status.progress}%",
            start_time,
            update_time,
            "√" if status.enabled else "×",
        )

    return table
