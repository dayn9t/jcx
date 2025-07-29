from jcx.api.dao_list_client import ResultE, DaoListClient
from jcx.api.task.task_db import TaskInfo, StatusInfo, TaskStatus
from jcx.time.dt_util import now_sh_dt
from typing import Optional, List, Dict, Any, Tuple
from rustshed import Ok, Err


class TaskClient:
        def __init__(
                self,
                base_url: str,
                task_table_name: str = "task",
                status_table_name: str = "status",
        ):
            """初始化任务数据库管理器

            Args:
                base_url: 数据库URL，通常是文件路径或数据库连接字符串
                task_table_name: 任务表名称，默认为"tasks"
                status_table_name: 状态表名称，默认为"statuses"

            """
            self._client = DaoListClient(base_url)
            self._task_table_name = task_table_name
            self._status_table_name = status_table_name

        def add_task(self, task: TaskInfo) -> ResultE[TaskInfo]:
            """添加新任务记录

            Args:
                task: 任务记录实例

            Returns:
                ResultE[TaskInfo]: 添加后的任务记录，如果ID已存在则返回None
            """
            return self._client.post(self._task_table_name, task)

        def get_task_status(self, task_id: int) -> ResultE[StatusInfo]:
            """获取指定任务的状态信息

            Args:
                task_id: 任务ID

            Returns:
                ResultE[StatusInfo]: 任务状态信息，如果任务不存在则返回错误
            """
            return self._client.get(StatusInfo, self._status_table_name, task_id)

        def find_task(self) -> ResultE[Tuple[TaskInfo, StatusInfo]]:
            """找到可执行任务

            查找状态为未启动且已启用的任务

            Returns:
                ResultE[Tuple[TaskInfo, StatusInfo]]: 任务信息和状态的元组，如果没有可执行任务则返回错误
            """
            # 获取所有任务状态
            status_result = self._client.get_all(
                StatusInfo,
                self._status_table_name,
                {"status": TaskStatus.NOT_STARTED.value, "enabled": True}
            )

            if status_result.is_err():
                return Err(status_result.unwrap_err())

            statuses = status_result.unwrap()
            if not statuses:
                return Err("没有找到可执行的任务")

            # 获取第一个未启动任务的信息
            first_status = statuses[0]
            task_result = self._client.get(TaskInfo, self._task_table_name, first_status.id)

            if task_result.is_err():
                return Err(f"获取任务信息失败: {task_result.unwrap_err()}")

            return Ok((task_result.unwrap(), first_status))

        def task_start(self, task_id: int, worker: Optional[str] = None) -> ResultE[StatusInfo]:
            """开始执行指定任务

            将任务状态设置为进行中，记录开始时间，设置进度为0

            Args:
                task_id: 任务ID
                worker: 可选的工作者标识

            Returns:
                ResultE[StatusInfo]: 更新后的任务状态
            """
            # 获取当前状态
            status_result = self.get_task_status(task_id)
            if status_result.is_err():
                return status_result

            status = status_result.unwrap()
            # 更新状态为进行中
            status.status = TaskStatus.IN_PROGRESS
            status.progress = 0
            status.start_time = now_sh_dt()
            status.update_time = now_sh_dt()

            # 提交更新
            return self._client.put(self._status_table_name, status)

        def task_done(self, task_id: int) -> ResultE[StatusInfo]:
            """终结指定任务

            将任务状态设置为已完成，进度设为100%

            Args:
                task_id: 任务ID

            Returns:
                ResultE[StatusInfo]: 更新后的任务状态
            """
            return self.update_progress(task_id, 100, TaskStatus.COMPLETED)

        def task_error(self, task_id: int) -> ResultE[StatusInfo]:
            """标记指定任务为出错

            Args:
                task_id: 任务ID

            Returns:
                ResultE[StatusInfo]: 更新后的任务状态
            """
            # 获取当前状态
            status_result = self.get_task_status(task_id)
            if status_result.is_err():
                return status_result

            status = status_result.unwrap()
            # 更新状态为出错
            status.status = TaskStatus.ERROR
            status.update_time = now_sh_dt()

            # 提交更新
            return self._client.put(self._status_table_name, status)

        def update_progress(self, task_id: int, progress: int, status: TaskStatus = None) -> ResultE[StatusInfo]:
            """更新指定任务进度

            Args:
                task_id: 任务ID
                progress: 进度值(0-100)
                status: 可选的状态更新

            Returns:
                ResultE[StatusInfo]: 更新后的任务状态
            """
            if not 0 <= progress <= 100:
                return Err(f"无效的进度值: {progress}，必须在 0-100 之间")

            # 获取当前状态
            status_result = self.get_task_status(task_id)
            if status_result.is_err():
                return status_result

            status_info = status_result.unwrap()
            # 更新进度
            status_info.progress = progress
            status_info.update_time = now_sh_dt()

            # 如果提供了新状态，则更新
            if status is not None:
                status_info.status = status
            # 如果进度为100%，自动设置状态为已完成
            elif progress == 100 and status_info.status != TaskStatus.ERROR:
                status_info.status = TaskStatus.COMPLETED

            # 提交更新
            return self._client.put(self._status_table_name, status_info)
