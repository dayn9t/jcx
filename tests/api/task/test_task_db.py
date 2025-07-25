import os
import tempfile
from pathlib import Path
import pytest

from jcx.api.task.task import TaskDb, TaskInfoBase, StatusInfo, TaskStatus


class TestTaskInfo(TaskInfoBase):
    """测试用任务信息类"""

    content: str = ""  # 测试内容字段


def test_task_db_init():
    """测试TaskDb初始化"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_dir = Path(tmp_dir)
        # 初始化一个TaskDb实例
        db = TaskDb(db_dir, TestTaskInfo)

        # 验证任务表和状态表已正确初始化
        assert db.task_tab is not None
        assert db.status_tab is not None

        # 验证表文件已创建
        assert (db_dir / "task").exists()
        assert (db_dir / "status").exists()


def test_task_operations():
    """测试任务的添加、查找和状态更新操作"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_dir = Path(tmp_dir)
        db = TaskDb(db_dir, TestTaskInfo)

        # 创建测试任务
        task = TestTaskInfo(id=1, name="test_task", type=1, content="test content")
        db.task_tab.update(task)

        # 创建对应的状态记录
        status = StatusInfo(id=1)
        db.status_tab.update(status)

        # 测试查找任务
        task_result = db.find_task()
        assert task_result.is_some()

        found_task, found_status = task_result.unwrap()
        assert found_task.id == 1
        assert found_task.name == "test_task"
        assert found_task.content == "test content"
        assert found_status.status == TaskStatus.NOT_STARTED
        assert found_status.progress == 0

        # 测试更新任务进度
        db.update_progress(1, 50)
        updated_status = db.status_tab.get(1).unwrap()
        assert updated_status.progress == 50
        assert updated_status.status == TaskStatus.IN_PROGRESS
        assert updated_status.start_time is not None

        # 测试完成任务
        db.task_done(1)
        completed_status = db.status_tab.get(1).unwrap()
        assert completed_status.status == TaskStatus.COMPLETED
        assert completed_status.progress == 100

        # 测试查找任务 - 此时应返回None，因为任务已完成
        assert db.find_task().is_null()


def test_task_error_handling():
    """测试任务错误处理"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_dir = Path(tmp_dir)
        db = TaskDb(db_dir, TestTaskInfo)

        # 创建测试任务
        task = TestTaskInfo(id=2, name="error_task", type=1)
        db.task_tab.update(task)

        # 创建对应的状态记录
        status = StatusInfo(id=2)
        db.status_tab.update(status)

        # 测试标记任务为错误状态
        db.task_error(2)
        error_status = db.status_tab.get(2).unwrap()
        assert error_status.status == TaskStatus.ERROR

        # 测试查找任务 - 此时应返回None，因为任务出错
        assert db.find_task().is_null()


def test_multiple_tasks():
    """测试多个任务的处理顺序"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_dir = Path(tmp_dir)
        db = TaskDb(db_dir, TestTaskInfo)

        # 创建多个测试任务
        for i in range(1, 4):
            task = TestTaskInfo(id=i, name=f"task_{i}", type=1)
            db.task_tab.update(task)

            status = StatusInfo(id=i)
            if i == 2:
                status.status = TaskStatus.IN_PROGRESS  # 任务2处于进行中
            elif i == 3:
                status.enabled = False  # 任务3被禁用
            db.status_tab.update(status)

        # 验证首先找到的任务1
        task_result = db.find_task()
        assert task_result.is_some()
        found_task, _ = task_result.unwrap()
        assert found_task.id == 1

        # 完成任务1
        db.task_done(1)

        # 现在应该找到任务2
        task_result = db.find_task()
        assert task_result.is_some()
        found_task, _ = task_result.unwrap()
        assert found_task.id == 2

        # 将任务3启用
        status = db.status_tab.get(3).unwrap()
        status.enabled = True
        db.status_tab.update(status)

        # 完成任务1
        db.task_done(2)

        # 现在应该找到任务3
        task_result = db.find_task()
        assert task_result.is_some()
        found_task, _ = task_result.unwrap()
        assert found_task.id == 3


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
