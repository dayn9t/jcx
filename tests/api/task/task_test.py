from pydantic import BaseModel

from jcx.api.task.task import TaskStatus
from jcx.text.txt_json import to_json


class TaskStatusModel(BaseModel):
    status: TaskStatus = TaskStatus.NOT_STARTED


def test_task_status_serialization():
    model = TaskStatusModel()
    json_str = to_json(model)
    print(f"默认序列化结果: {json_str}")

    # 直接序列化枚举值
    status = TaskStatus.IN_PROGRESS
    json_enum = to_json(status)
    print(f"直接序列化枚举值: {json_enum}")

    # 在字典中序列化
    status_dict = {"status": TaskStatus.COMPLETED}
    json_dict = to_json(status_dict)
    print(f"在字典中序列化: {json_dict}")


if __name__ == "__main__":
    test_task_status_serialization()
