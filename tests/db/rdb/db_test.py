# tests/db/rdb/db_test.py
"""Tests for Redis database URL parsing and client initialization."""

import pytest

from jcx.db.rdb.db import RedisDb, parse_redis_url


class TestParseRedisUrl:
    """Tests for parse_redis_url function."""

    def test_valid_url_full(self):
        """Test parsing valid URL with all components."""
        result = parse_redis_url("redis://127.0.0.1:6379/10")
        assert result.is_ok()
        host, port, db_num = result.unwrap()
        assert host == "127.0.0.1"
        assert port == 6379
        assert db_num == 10

    def test_valid_url_default_port(self):
        """Test parsing valid URL without port (uses default)."""
        result = parse_redis_url("redis://localhost/5")
        assert result.is_ok()
        host, port, db_num = result.unwrap()
        assert host == "localhost"
        assert port == 6379  # default
        assert db_num == 5

    def test_valid_url_localhost_explicit(self):
        """Test parsing localhost with explicit port."""
        result = parse_redis_url("redis://localhost:6380/0")
        assert result.is_ok()
        host, port, db_num = result.unwrap()
        assert host == "localhost"
        assert port == 6380
        assert db_num == 0

    def test_invalid_scheme(self):
        """Test parsing URL with wrong scheme."""
        result = parse_redis_url("http://localhost/5")
        assert result.is_err()
        error = result.unwrap_err()
        assert "scheme" in error.lower()

    def test_invalid_no_path(self):
        """Test parsing URL without database path."""
        result = parse_redis_url("redis://localhost")
        assert result.is_err()
        error = result.unwrap_err()
        assert "path" in error.lower()

    def test_invalid_path_non_numeric(self):
        """Test parsing URL with non-numeric database path."""
        result = parse_redis_url("redis://localhost/abc")
        assert result.is_err()
        error = result.unwrap_err()
        assert "path" in error.lower()


class TestRedisDbInit:
    """Tests for RedisDb initialization."""

    def test_init_invalid_url_raises_value_error(self):
        """Test that invalid URL raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            RedisDb("http://localhost/5")
        assert "scheme" in str(exc_info.value).lower()

    def test_init_invalid_path_raises_value_error(self):
        """Test that invalid path raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            RedisDb("redis://localhost")
        assert "path" in str(exc_info.value).lower()

    # Note: Testing actual Redis connection requires running Redis server
    # Mark as integration test or use mock
    @pytest.mark.integration
    def test_open_with_valid_url(self):
        """Test RedisDb.open() with valid URL (requires running Redis)."""
        # This test is marked as integration and will be skipped by default
        db = RedisDb.open("redis://127.0.0.1:6379/10")
        assert db.name() == "10"
