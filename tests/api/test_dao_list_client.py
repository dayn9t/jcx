#!/usr/bin/env python3

"""DaoListClient 单元测试

测试 DaoListClient 类的各种方法，包括 CRUD 操作和认证令牌设置。
使用 unittest.mock 来模拟 HTTP 请求，避免对实际服务器的依赖。
"""

from unittest.mock import Mock, patch

import pytest
from requests.exceptions import ConnectionError

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

    # ========== Task 1 Tests: Timeout and Pool Configuration ==========

    def test_init_default_timeout(self):
        """Test 1: DaoListClient initializes with default timeout (30.0)"""
        client = DaoListClient("http://api.example.com/v1")
        assert client.timeout == 30.0

    def test_init_custom_timeout(self):
        """Test 2: DaoListClient initializes with custom timeout parameter"""
        client = DaoListClient("http://api.example.com/v1", timeout=60.0)
        assert client.timeout == 60.0

    def test_init_http_adapter_pool_config(self):
        """Test 3: DaoListClient mounts HTTPAdapter with pool_connections"""
        client = DaoListClient(
            "http://api.example.com/v1",
            pool_connections=5,
            pool_maxsize=20,
        )
        # Verify adapters are mounted for both http and https
        assert "http://" in client.session.adapters
        assert "https://" in client.session.adapters

    @patch("requests.Session.get")
    def test_get_all_passes_timeout(self, mock_get):
        """Test 4: get_all passes timeout to session.get()"""
        client = DaoListClient("http://api.example.com/v1", timeout=45.0)
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = client.get_all(TestRecord, "tests")
        assert result.is_ok()

        # Verify timeout was passed
        call_kwargs = mock_get.call_args[1]
        assert "timeout" in call_kwargs
        assert call_kwargs["timeout"] == 45.0

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
            timeout=30.0,
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
            timeout=30.0,
        )

    @patch("requests.Session.get")
    def test_get_all_error(self, mock_get, client):
        """测试 get_all 方法错误场景"""
        # 准备模拟响应 - 使用 ConnectionError 而不是通用 Exception
        mock_get.side_effect = ConnectionError("API连接失败")

        # 执行测试
        result = client.get_all(TestRecord, "tests")

        # 验证结果
        assert result.is_err()
        error = result.unwrap_err()
        assert "获取所有资源失败" in error
        assert "连接失败" in error

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
            timeout=30.0,
        )

    @patch("requests.Session.get")
    def test_get_error(self, mock_get, client):
        """测试 get 方法错误场景"""
        # 准备模拟响应 - 使用 ConnectionError
        mock_get.side_effect = ConnectionError("记录不存在")

        # 执行测试
        result = client.get(TestRecord, "tests", 999)

        # 验证结果
        assert result.is_err()
        error = result.unwrap_err()
        assert "获取资源失败" in error
        assert "连接失败" in error

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
        assert "data" in call_args[1]
        # data contains JSON string of the record

    @patch("requests.Session.post")
    def test_post_error(self, mock_post, client, test_record):
        """测试 post 方法错误场景"""
        # 准备模拟响应 - 使用 ConnectionError
        mock_post.side_effect = ConnectionError("数据验证失败")

        # 执行测试
        result = client.post("tests", test_record)

        # 验证结果
        assert result.is_err()
        error = result.unwrap_err()
        assert "创建资源失败" in error
        assert "连接失败" in error

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
        assert "data" in call_args[1]
        # data contains JSON string of the record

    @patch("requests.Session.put")
    def test_put_error(self, mock_put, client, test_record):
        """测试 put 方法错误场景"""
        # 准备模拟响应 - 使用 ConnectionError
        mock_put.side_effect = ConnectionError("更新操作失败")

        # 执行测试
        result = client.put("tests", test_record)

        # 验证结果
        assert result.is_err()
        error = result.unwrap_err()
        assert "更新资源失败" in error
        assert "连接失败" in error

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
            timeout=30.0,
        )

    @patch("requests.Session.delete")
    def test_delete_error(self, mock_delete, client):
        """测试 delete 方法错误场景"""
        # 准备模拟响应 - 使用 ConnectionError
        mock_delete.side_effect = ConnectionError("删除操作失败")

        # 执行测试
        result = client.delete("tests", 1)

        # 验证结果
        assert result.is_err()
        error = result.unwrap_err()
        assert "删除资源失败" in error
        assert "连接失败" in error

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
