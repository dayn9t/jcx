#!/usr/bin/env python3

"""DaoListClient 单元测试

测试 DaoListClient 类的各种方法，包括 CRUD 操作和认证令牌设置。
使用 unittest.mock 来模拟 HTTP 请求，避免对实际服务器的依赖。
"""

from unittest.mock import Mock, patch

import pytest

from jcx.api.dao_client import DaoListClient
from jcx.db.record import Record


class TestRecord(Record):
    """用于测试的记录类"""

    name: str
    value: int
    active: bool = True


@pytest.fixture
def client():
    """创建一个 DaoListClient 实例用于测试"""
    return DaoListClient("http://api.example.com/v1")


@pytest.fixture
def test_record():
    """创建一个测试记录用于测试"""
    return TestRecord(id=1, name="测试记录", value=100)


@pytest.fixture
def test_records():
    """创建一个测试记录列表用于测试"""
    return [
        TestRecord(id=1, name="记录1", value=100),
        TestRecord(id=2, name="记录2", value=200),
        TestRecord(id=3, name="记录3", value=300),
    ]


class TestDaoListClient:
    """DaoListClient 测试类"""

    def test_init(self):
        """测试客户端初始化"""
        # 测试正常URL
        client = DaoListClient("http://api.example.com/v1")
        assert client.base_url == "http://api.example.com/v1"
        assert "Content-Type" in client.headers
        assert client.headers["Content-Type"] == "application/json"

        # 测试带尾斜杠的URL
        client = DaoListClient("http://api.example.com/v1/")
        assert client.base_url == "http://api.example.com/v1"

    @patch("requests.Session.get")
    def test_get_all_success(self, mock_get, client, test_records):
        """测试 get_all 方法成功场景"""
        # 准备模拟响应
        mock_response = Mock()
        mock_response.json.return_value = [
            {"id": 1, "name": "记录1", "value": 100, "active": True},
            {"id": 2, "name": "记录2", "value": 200, "active": True},
            {"id": 3, "name": "记录3", "value": 300, "active": True},
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # 执行测试
        result = client.get_all(TestRecord, "tests")

        # 验证结果
        assert result.is_ok()
        records = result.unwrap()
        assert isinstance(records, list)
        assert len(records) == 3
        assert all(isinstance(r, TestRecord) for r in records)
        assert records[0].name == "记录1"
        assert records[0].value == 100
        assert records[1].name == "记录2"
        assert records[1].value == 200

        # 验证请求
        mock_get.assert_called_once_with(
            "http://api.example.com/v1/tests",
            params=None,
            headers={"Content-Type": "application/json"},
        )

    @patch("requests.Session.get")
    def test_get_all_with_params(self, mock_get, client):
        """测试 get_all 方法带参数"""
        # 准备模拟响应
        mock_response = Mock()
        mock_response.json.return_value = [
            {"id": 1, "name": "测试记录", "value": 100, "active": True},
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # 执行测试
        params = {"active": True, "value_gt": 50}
        result = client.get_all(TestRecord, "tests", params)

        # 验证请求
        mock_get.assert_called_once_with(
            "http://api.example.com/v1/tests",
            params=params,
            headers={"Content-Type": "application/json"},
        )

    @patch("requests.Session.get")
    def test_get_all_error(self, mock_get, client):
        """测试 get_all 方法错误场景"""
        # 准备模拟响应
        mock_get.side_effect = Exception("API连接失败")

        # 执行测试
        result = client.get_all(TestRecord, "tests")

        # 验证结果
        assert result.is_err()
        error = result.unwrap_err()
        assert "获取所有资源失败" in error
        assert "API连接失败" in error

    @patch("requests.Session.get")
    def test_get_success(self, mock_get, client, test_record):
        """测试 get 方法成功场景"""
        # 准备模拟响应
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": 1,
            "name": "测试记录",
            "value": 100,
            "active": True,
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # 执行测试
        result = client.get(TestRecord, "tests", 1)

        # 验证结果
        assert result.is_ok()
        record = result.unwrap()
        assert isinstance(record, TestRecord)
        assert record.id == 1
        assert record.name == "测试记录"
        assert record.value == 100

        # 验证请求
        mock_get.assert_called_once_with(
            "http://api.example.com/v1/tests/1",
            headers={"Content-Type": "application/json"},
        )

    @patch("requests.Session.get")
    def test_get_error(self, mock_get, client):
        """测试 get 方法错误场景"""
        # 准备模拟响应
        mock_get.side_effect = Exception("记录不存在")

        # 执行测试
        result = client.get(TestRecord, "tests", 999)

        # 验证结果
        assert result.is_err()
        error = result.unwrap_err()
        assert "获取资源失败" in error
        assert "记录不存在" in error

    @patch("requests.Session.post")
    def test_post_success(self, mock_post, client, test_record):
        """测试 post 方法成功场景"""
        # 准备模拟响应
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": 1,
            "name": "测试记录",
            "value": 100,
            "active": True,
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # 执行测试
        result = client.post("tests", test_record)

        # 验证结果
        assert result.is_ok()
        record = result.unwrap()
        assert isinstance(record, TestRecord)
        assert record.id == 1
        assert record.name == "测试记录"
        assert record.value == 100

        # 验证请求
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "http://api.example.com/v1/tests"
        assert "json" in call_args[1]
        assert call_args[1]["json"] == test_record.model_dump()

    @patch("requests.Session.post")
    def test_post_error(self, mock_post, client, test_record):
        """测试 post 方法错误场景"""
        # 准备模拟响应
        mock_post.side_effect = Exception("数据验证失败")

        # 执行测试
        result = client.post("tests", test_record)

        # 验证结果
        assert result.is_err()
        error = result.unwrap_err()
        assert "创建资源失败" in error
        assert "数据验证失败" in error

    @patch("requests.Session.put")
    def test_put_success(self, mock_put, client, test_record):
        """测试 put 方法成功场景"""
        # 准备模拟响应
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": 1,
            "name": "更新的记录",
            "value": 200,
            "active": True,
        }
        mock_response.raise_for_status.return_value = None
        mock_put.return_value = mock_response

        # 修改记录数据
        test_record.name = "更新的记录"
        test_record.value = 200

        # 执行测试
        result = client.put("tests", test_record)

        # 验证结果
        assert result.is_ok()
        record = result.unwrap()
        assert isinstance(record, TestRecord)
        assert record.id == 1
        assert record.name == "更新的记录"
        assert record.value == 200

        # 验证请求
        mock_put.assert_called_once()
        call_args = mock_put.call_args
        assert call_args[0][0] == "http://api.example.com/v1/tests/1"
        assert "json" in call_args[1]
        assert call_args[1]["json"] == test_record.model_dump()

    @patch("requests.Session.put")
    def test_put_error(self, mock_put, client, test_record):
        """测试 put 方法错误场景"""
        # 准备模拟响应
        mock_put.side_effect = Exception("更新操作失败")

        # 执行测试
        result = client.put("tests", test_record)

        # 验证结果
        assert result.is_err()
        error = result.unwrap_err()
        assert "更新资源失败" in error
        assert "更新操作失败" in error

    @patch("requests.Session.delete")
    def test_delete_success(self, mock_delete, client):
        """测试 delete 方法成功场景"""
        # 准备模拟响应
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_delete.return_value = mock_response

        # 执行测试
        result = client.delete("tests", 1)

        # 验证结果
        assert result.is_ok()
        assert result.unwrap() is True

        # 验证请求
        mock_delete.assert_called_once_with(
            "http://api.example.com/v1/tests/1",
            headers={"Content-Type": "application/json"},
        )

    @patch("requests.Session.delete")
    def test_delete_error(self, mock_delete, client):
        """测试 delete 方法错误场景"""
        # 准备模拟响应
        mock_delete.side_effect = Exception("删除操作失败")

        # 执行测试
        result = client.delete("tests", 1)

        # 验证结果
        assert result.is_err()
        error = result.unwrap_err()
        assert "删除资源失败" in error
        assert "删除操作失败" in error

    def test_set_auth_token(self, client):
        """测试设置认证令牌"""
        # 执行测试
        client.set_auth_token("test-token")

        # 验证结果
        assert "Authorization" in client.headers
        assert client.headers["Authorization"] == "Bearer test-token"

    @patch("requests.Session.close")
    def test_close(self, mock_close, client):
        """测试关闭会话"""
        # 执行测试
        client.close()

        # 验证调用
        mock_close.assert_called_once()


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
