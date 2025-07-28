from typing import TypeVar, Optional, List, Dict, Any
import requests

from jcx.db.record import Record
from rustshed import *

R = TypeVar("R", bound=Record)


class DaoListClient:
    """DAO列表客户端类

    用于与后端服务进行HTTP通信，支持对资源集合进行基本的CRUD操作。
    遵循REST风格API设计，自动处理序列化和反序列化。
    """

    def __init__(self, base_url: str):
        """初始化项目列表客户端

        Args:
            base_url: API服务器基础URL，例如 'http://api.example.com/v1'
        """
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.headers = {"Content-Type": "application/json"}

    def get_all(
        self,
        record_type: type[R],
        table_name: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Result[List[R]]:
        """获取所有资源项目

        发送GET请求获取指定表中的所有记录

        Args:
            record_type: 返回记录的类型
            table_name: 表名/资源集合名称
            params: 查询参数字典，用于过滤结果集

        Returns:
            包含记录对象列表的Result

        Example:
            >>> result = client.get_all(UserRecord, "users", {"status": "active"})
            >>> if result.is_ok():
            >>>     users = result.unwrap()
        """
        try:
            url = f"{self.base_url}/{table_name}"
            response = self.session.get(url, params=params, headers=self.headers)
            response.raise_for_status()

            data_list = response.json()
            records = [record_type(**item) for item in data_list]
            return Ok(records)
        except Exception as e:
            return Err(f"获取所有资源失败: {str(e)}")

    def get(self, record_type: type[R], table_name: str, record_id: int) -> Result[R]:
        """获取单个资源项目

        发送GET请求获取指定表中的单条记录

        Args:
            record_type: 返回记录的类型
            table_name: 表名/资源集合名称
            record_id: 记录ID

        Returns:
            包含记录对象的Result

        Example:
            >>> result = client.get(UserRecord, "users", 123)
            >>> if result.is_ok():
            >>>     user = result.unwrap()
        """
        try:
            url = f"{self.base_url}/{table_name}/{record_id}"

            response = self.session.get(url, headers=self.headers)
            response.raise_for_status()

            data = response.json()
            record = record_type(**data)
            return Ok(record)
        except Exception as e:
            return Err(f"获取资源失败: {str(e)}")

    def post(self, table_name: str, record: R) -> Result[R]:
        """创建新资源项目

        发送POST请求创建新记录

        Args:
            table_name: 表名/资源集合名称
            record: 要创建的记录对象

        Returns:
            包含创建后的记录对象的Result

        Example:
            >>> user = UserRecord(name="张三", age=30)
            >>> result = client.post("users", user)
        """
        try:
            url = f"{self.base_url}/{table_name}"
            data = record.model_dump()
            response = self.session.post(url, json=data, headers=self.headers)
            response.raise_for_status()

            response_data = response.json()
            return Ok(record.__class__(**response_data))
        except Exception as e:
            return Err(f"创建资源失败: {str(e)}")

    def put(self, table_name: str, record: R) -> Result[R]:
        """更新资源项目

        发送PUT请求更新已有记录

        Args:
            table_name: 表名/资源集合名称
            record: 包含更新内容的记录对象，必须包含id字段

        Returns:
            包含更新后的记录对象的Result

        Example:
            >>> user.name = "李四"
            >>> result = client.put("users", user)
        """
        try:
            if not hasattr(record, "id") or record.id is None:
                return Err("更新资源失败: 记录缺少id字段")

            url = f"{self.base_url}/{table_name}/{record.id}"
            data = record.model_dump()
            response = self.session.put(url, json=data, headers=self.headers)
            response.raise_for_status()

            response_data = response.json()
            return Ok(record.__class__(**response_data))
        except Exception as e:
            return Err(f"更新资源失败: {str(e)}")

    def delete(self, table_name: str, record_id: int) -> Result[bool]:
        """删除资源项目

        发送DELETE请求删除指定记录

        Args:
            table_name: 表名/资源集合名称
            record_id: 要删除的记录ID

        Returns:
            包含操作成功状态的Result

        Example:
            >>> result = client.delete("users", 123)
        """
        try:
            url = f"{self.base_url}/{table_name}/{record_id}"
            response = self.session.delete(url, headers=self.headers)
            response.raise_for_status()

            return Ok(True)
        except Exception as e:
            return Err(f"删除资源失败: {str(e)}")

    def set_auth_token(self, token: str) -> None:
        """设置认证令牌

        Args:
            token: JWT或其他认证令牌
        """
        self.headers["Authorization"] = f"Bearer {token}"

    def close(self) -> None:
        """关闭HTTP会话，释放资源"""
        self.session.close()
