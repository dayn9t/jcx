# tests/bin/cli_validation_test.py
"""Tests for CLI input validation."""

import ast

import pytest
from pydantic import ValidationError


class TestTaskCreateInputValidation:
    """Tests for TaskCreateInput validation model in cx_task.py."""

    def test_valid_input(self):
        """Test that valid input passes validation."""
        from jcx.bin.cx_task import TaskCreateInput

        validated = TaskCreateInput(name="Test Task", task_type=1, data="{}", desc="Test")
        assert validated.name == "Test Task"
        assert validated.task_type == 1

    def test_invalid_empty_name(self):
        """Test that empty name fails validation."""
        from jcx.bin.cx_task import TaskCreateInput

        with pytest.raises(ValidationError) as exc_info:
            TaskCreateInput(name="", task_type=1, data="{}")
        assert "name" in str(exc_info.value).lower()

    def test_invalid_negative_task_type(self):
        """Test that negative task_type fails validation."""
        from jcx.bin.cx_task import TaskCreateInput

        with pytest.raises(ValidationError) as exc_info:
            TaskCreateInput(name="Test", task_type=-1, data="{}")
        assert "task_type" in str(exc_info.value).lower()


class TestProgressUpdateInputValidation:
    """Tests for ProgressUpdateInput validation model in cx_task.py."""

    def test_valid_progress(self):
        """Test that valid progress passes validation."""
        from jcx.bin.cx_task import ProgressUpdateInput

        validated = ProgressUpdateInput(progress=50)
        assert validated.progress == 50

    def test_invalid_progress_above_100(self):
        """Test that progress > 100 fails validation."""
        from jcx.bin.cx_task import ProgressUpdateInput

        with pytest.raises(ValidationError) as exc_info:
            ProgressUpdateInput(progress=101)
        assert "progress" in str(exc_info.value).lower()

    def test_invalid_progress_below_0(self):
        """Test that progress < 0 fails validation."""
        from jcx.bin.cx_task import ProgressUpdateInput

        with pytest.raises(ValidationError) as exc_info:
            ProgressUpdateInput(progress=-1)
        assert "progress" in str(exc_info.value).lower()


class TestMainExceptionHandling:
    """Tests for main() exception handling in CLI tools."""

    def test_cx_task_main_catches_validation_error(self):
        """Test that main() in cx_task.py catches ValidationError specifically."""
        with open("src/jcx/bin/cx_task.py") as f:
            source = f.read()

        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "main":
                # Find the try block and check for ValidationError except handler
                for child in ast.walk(node):
                    if isinstance(child, ast.ExceptHandler):
                        if child.type and isinstance(child.type, ast.Name):
                            if child.type.id == "ValidationError":
                                return  # Found it
        pytest.fail("main() does not catch ValidationError specifically")

    def test_cx_dao_main_catches_validation_error(self):
        """Test that main() in cx_dao.py catches ValidationError specifically."""
        with open("src/jcx/bin/cx_dao.py") as f:
            source = f.read()

        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "main":
                for child in ast.walk(node):
                    if isinstance(child, ast.ExceptHandler):
                        if child.type and isinstance(child.type, ast.Name):
                            if child.type.id == "ValidationError":
                                return
        pytest.fail("main() does not catch ValidationError specifically")


class TestDaoTaskCreateInputValidation:
    """Tests for TaskCreateInput validation model in cx_dao.py."""

    def test_valid_input(self):
        """Test that valid input passes validation in cx_dao."""
        from jcx.bin.cx_dao import TaskCreateInput

        validated = TaskCreateInput(name="Test Task", task_type=1, data="{}", desc="Test")
        assert validated.name == "Test Task"
        assert validated.task_type == 1

    def test_invalid_empty_name(self):
        """Test that empty name fails validation in cx_dao."""
        from jcx.bin.cx_dao import TaskCreateInput

        with pytest.raises(ValidationError) as exc_info:
            TaskCreateInput(name="", task_type=1, data="{}")
        assert "name" in str(exc_info.value).lower()

    def test_invalid_negative_task_type(self):
        """Test that negative task_type fails validation in cx_dao."""
        from jcx.bin.cx_dao import TaskCreateInput

        with pytest.raises(ValidationError) as exc_info:
            TaskCreateInput(name="Test", task_type=-1, data="{}")
        assert "task_type" in str(exc_info.value).lower()
