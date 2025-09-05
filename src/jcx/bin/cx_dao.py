"""任务管理命令行工具

使用 DaoListClient 与任务管理服务进行交互，支持任务和任务状态的 CRUD 操作。
基于 typer 构建的完整命令行应用，演示 REST API 交互。
"""

import json
import sys
import uuid

import typer
from rich import print as rprint
from rich.console import Console

from jcx.api.dao_client import DaoListClient
from jcx.api.task.task_types import (
    StatusInfo,
    TaskInfo,
    TaskStatus,
    status_list_table,
    status_table,
    task_table,
    tasks_table,
)

# 创建 typer 应用和控制台对象
app = typer.Typer(help="任务管理命令行工具")
tasks_app = typer.Typer(help="任务相关操作")
statuses_app = typer.Typer(help="任务状态相关操作")
app.add_typer(tasks_app, name="tasks")
app.add_typer(statuses_app, name="statuses")
console = Console()


@tasks_app.callback()
def tasks_callback():
    """任务管理相关命令"""


@statuses_app.callback()
def statuses_callback():
    """任务状态相关命令"""


@tasks_app.command("list")
def list_tasks(
    base_url: str = typer.Option(..., "--url", "-u", help="API服务器基础URL"),
    filter_json: str | None = typer.Option(
        None, "--filter", "-f", help="过滤条件 (JSON格式)"
    ),
):
    """获取所有任务

    GET /tasks
    """
    client = DaoListClient(base_url)

    # 解析过滤参数
    params = None
    if filter_json:
        try:
            params = json.loads(filter_json)
        except json.JSONDecodeError:
            rprint("[red]过滤参数格式错误，请提供有效的JSON字符串[/red]")
            sys.exit(1)

    # 获取所有任务
    result = client.get_all(TaskInfo, "tasks", params)

    if result.is_ok():
        tasks = result.unwrap()
        console.print(tasks_table(tasks))
    else:
        rprint(f"[red]获取任务列表失败: {result.unwrap_err()}[/red]")
        sys.exit(1)


@tasks_app.command("get")
def get_task(
    task_id: str = typer.Argument(..., help="任务ID"),
    base_url: str = typer.Option(..., "--url", "-u", help="API服务器基础URL"),
):
    """获取指定任务

    GET /tasks/{id}
    """
    client = DaoListClient(base_url)

    # 获取指定任务
    result = client.get(TaskInfo, "tasks", task_id)

    if result.is_ok():
        task = result.unwrap()
        console.print(task_table(task))
    else:
        rprint(f"[red]获取任务失败: {result.unwrap_err()}[/red]")
        sys.exit(1)


@tasks_app.command("create")
def create_task(
    base_url: str = typer.Option(..., "--url", "-u", help="API服务器基础URL"),
    name: str = typer.Option(..., "--name", "-n", help="任务名称"),
    task_type: int = typer.Option(..., "--type", "-t", help="任务类型"),
    desc: str | None = typer.Option(None, "--desc", "-d", help="任务描述"),
    data: str = typer.Option(..., "--data", help="任务数据 (JSON格式)"),
):
    """创建新任务

    POST /tasks
    """
    client = DaoListClient(base_url)

    # 创建任务对象
    task = TaskInfo(
        id=str(uuid.uuid4()),  # ID将由服务器分配
        name=name,
        type=task_type,
        desc=desc,
        data=data,
    )

    # 提交创建请求
    result = client.post("tasks", task)

    if result.is_ok():
        created_task = result.unwrap()
        rprint("[green]任务创建成功[/green]")
        task_table(created_task)
    else:
        rprint(f"[red]创建任务失败: {result.unwrap_err()}[/red]")
        sys.exit(1)


@tasks_app.command("delete")
def delete_task(
    task_id: str = typer.Argument(..., help="任务ID"),
    base_url: str = typer.Option(..., "--url", "-u", help="API服务器基础URL"),
    force: bool = typer.Option(False, "--force", "-f", help="强制删除，不提示确认"),
):
    """删除指定任务

    DELETE /tasks/{id}
    """
    # 确认删除
    if not force:
        confirm = typer.confirm(f"确定要删除ID为 {task_id} 的任务吗?")
        if not confirm:
            rprint("操作已取消")
            return

    client = DaoListClient(base_url)

    # 发送删除请求
    result = client.delete("tasks", task_id)

    if result.is_ok():
        rprint(f"[green]已成功删除ID为 {task_id} 的任务[/green]")
    else:
        rprint(f"[red]删除任务失败: {result.unwrap_err()}[/red]")
        sys.exit(1)


@statuses_app.command("list")
def list_statuses(
    base_url: str = typer.Option(..., "--url", "-u", help="API服务器基础URL"),
    filter_json: str | None = typer.Option(
        None, "--filter", "-f", help="过滤条件 (JSON格式)"
    ),
):
    """获取所有任务状态

    GET /statuses
    """
    client = DaoListClient(base_url)

    # 解析过滤参数
    params = None
    if filter_json:
        try:
            params = json.loads(filter_json)
        except json.JSONDecodeError:
            rprint("[red]过滤参数格式错误，请提供有效的JSON字符串[/red]")
            sys.exit(1)

    # 获取所有任务状态
    result = client.get_all(StatusInfo, "statuses", params)

    if result.is_ok():
        statuses = result.unwrap()
        console.print(status_list_table(statuses))
    else:
        rprint(f"[red]获取任务状态列表失败: {result.unwrap_err()}[/red]")
        sys.exit(1)


@statuses_app.command("get")
def get_status(
    status_id: str = typer.Argument(..., help="状态ID"),
    base_url: str = typer.Option(..., "--url", "-u", help="API服务器基础URL"),
):
    """获取指定任务状态

    GET /statuses/{id}
    """
    client = DaoListClient(base_url)

    # 获取指定任务状态
    result = client.get(StatusInfo, "statuses", status_id)

    if result.is_ok():
        status = result.unwrap()
        console.print(status_table(status))
    else:
        rprint(f"[red]获取任务状态失败: {result.unwrap_err()}[/red]")
        sys.exit(1)


@statuses_app.command("update")
def update_status(
    status_id: str = typer.Argument(..., help="状态ID"),
    base_url: str = typer.Option(..., "--url", "-u", help="API服务器基础URL"),
    status: int | None = typer.Option(None, "--status", "-s", help="任务状态码 (0-3)"),
    progress: int | None = typer.Option(
        None, "--progress", "-p", help="任务进度 (0-100)"
    ),
    enabled: bool | None = typer.Option(None, "--enabled/--disabled", help="是否启用"),
):
    """更新指定任务状态

    PUT /statuses/{id}
    """
    client = DaoListClient(base_url)

    # 首先获取当前任务状态
    get_result = client.get(StatusInfo, "statuses", status_id)
    if not get_result.is_ok():
        rprint(f"[red]获取任务状态失败: {get_result.unwrap_err()}[/red]")
        sys.exit(1)

    current_status = get_result.unwrap()

    # 更新提供的字段
    if status is not None:
        try:
            current_status.status = TaskStatus(status)
        except ValueError:
            rprint("[red]无效的状态码，必须是 0-3 之间的整数[/red]")
            sys.exit(1)

    if progress is not None:
        if not (0 <= progress <= 100):
            rprint("[red]无效的进度值，必须是 0-100 之间的整数[/red]")
            sys.exit(1)
        current_status.progress = progress

    if enabled is not None:
        current_status.enabled = enabled

    # 发送更新请求
    result = client.put("statuses", current_status)

    if result.is_ok():
        updated_status = result.unwrap()
        rprint("[green]任务状态更新成功[/green]")
        status_table(updated_status)
    else:
        rprint(f"[red]更新任务状态失败: {result.unwrap_err()}[/red]")
        sys.exit(1)


@app.command()
def demo():
    """运行演示程序

    展示如何使用此工具操作任务和任务状态
    """
    rprint("[bold blue]===== 任务管理命令行工具演示 =====[/bold blue]")
    rprint("以下是一些常用命令示例：\n")

    rprint("[bold cyan]1. 获取所有任务[/bold cyan]")
    rprint("  python -m jcx.bin.cx_task tasks list --url http://api.example.com/v1")
    rprint("  # 可选：添加过滤条件")
    rprint(
        "  python -m jcx.bin.cx_task tasks list --url http://api.example.com/v1 --filter '{\"type\": 1}'\n"
    )

    rprint("[bold cyan]2. 获取单个任务[/bold cyan]")
    rprint(
        "  python -m jcx.bin.cx_task tasks get 123 --url http://api.example.com/v1\n"
    )

    rprint("[bold cyan]3. 创建新任务[/bold cyan]")
    rprint(
        "  python -m jcx.bin.cx_task tasks create --url http://api.example.com/v1 \\"
    )
    rprint(
        '    --name "视频分析任务" --type 2 --desc "分析监控视频" --data "{\\"video_url\\": \\"http://example.com/video.mp4\\"}"'
    )

    rprint("[bold cyan]4. 删除任务[/bold cyan]")
    rprint(
        "  python -m jcx.bin.cx_task tasks delete 123 --url http://api.example.com/v1"
    )
    rprint("  # 强制删除（不提示确认）")
    rprint(
        "  python -m jcx.bin.cx_task tasks delete 123 --url http://api.example.com/v1 --force\n"
    )

    rprint("[bold cyan]5. 获取所有任务状态[/bold cyan]")
    rprint(
        "  python -m jcx.bin.cx_task statuses list --url http://api.example.com/v1\n"
    )

    rprint("[bold cyan]6. 获取单个任务状态[/bold cyan]")
    rprint(
        "  python -m jcx.bin.cx_task statuses get 123 --url http://api.example.com/v1\n"
    )

    rprint("[bold cyan]7. 更新任务状态[/bold cyan]")
    rprint("  # 更新状态为进行中")
    rprint(
        "  python -m jcx.bin.cx_task statuses update 123 --url http://api.example.com/v1 --status 1 --progress 50"
    )
    rprint("  # 更新状态为完成")
    rprint(
        "  python -m jcx.bin.cx_task statuses update 123 --url http://api.example.com/v1 --status 2 --progress 100"
    )
    rprint("  # 禁用任务")
    rprint(
        "  python -m jcx.bin.cx_task statuses update 123 --url http://api.example.com/v1 --disabled\n"
    )

    rprint("[bold blue]提示：所有命令都需要 --url 参数指定API服务器地址[/bold blue]")


def main():
    """程序入口点"""
    try:
        app()
    except Exception as e:
        rprint(f"[red]程序异常: {e!s}[/red]")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
