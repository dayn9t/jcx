import tempfile
from datetime import datetime
from pathlib import Path

from jcx.text.txt_json import *
from jcx.text.txt_json5 import load_txt as load_txt5, from_json5, load_json5
from tests.data_types import *


def test_to_json() -> None:
    assert to_json(1) == "1"
    assert to_json(1.1) == "1.1"
    assert to_json("OK") == '"OK"'
    assert to_json(True) == "true"
    assert to_json(None) == "null"
    assert to_json([1, 2, 3], pretty=False) == "[1,2,3]"
    assert to_json({"a": 1, "b": 2}, pretty=False) == '{"a":1,"b":2}'

    dt = datetime(2023, 1, 1, 0, 0, 0)
    assert to_json(dt) == '"2023-01-01T00:00:00"'

    # FIXME: 放弃对arrow的支持

    # time = arrow.get('2023-01-01T00:00:00.000Z')
    # assert to_json(time) == '"2023-01-01T00:00:00+00:00"'


def test_json_from_to() -> None:
    json1 = to_json(STUDENT1)
    assert json1 == JSON1

    s1 = from_json(json1, Student).unwrap()
    assert s1 == STUDENT1

    json_bad = """{
        "id": 1,
        "name": "Jack",
        "age": 11
    """
    r = from_json(json_bad, Student)
    assert r.is_err()


def test_from_io() -> None:
    dir1 = tempfile.mkdtemp()
    f1 = Path(dir1, "1.json")
    f2 = Path(dir1, "2.json")
    # print(f1)
    r = save_json(STUDENT1, f1)
    assert r.is_ok()

    s1 = load_json(f1, Student).unwrap()
    assert s1 == STUDENT1

    s2 = load_json(f2, Student)


def test_load_txt_file_not_found() -> None:
    """Test FileNotFoundError returns Err with file path."""
    result = load_txt("/nonexistent/path/file.txt")
    assert result.is_err()
    err = result.unwrap_err()
    assert isinstance(err, FileNotFoundError)
    assert "nonexistent" in str(err)


def test_load_txt5_file_not_found() -> None:
    """Test FileNotFoundError in txt_json5.load_txt returns Err with file path."""
    result = load_txt5("/nonexistent/path/file.json5")
    assert result.is_err()
    err = result.unwrap_err()
    assert isinstance(err, FileNotFoundError)
    assert "nonexistent" in str(err)


def test_from_json_invalid_json() -> None:
    """Test JSON decode error returns Err with parse message."""
    bad_json = "{invalid json"
    result = from_json(bad_json, Student)
    assert result.is_err()


def test_from_json5_invalid_json5() -> None:
    """Test JSON5 decode error returns Err with parse message."""
    bad_json5 = "{invalid json5"
    result = from_json5(bad_json5, Student)
    assert result.is_err()
    err = result.unwrap_err()
    assert isinstance(err, ValueError)
    assert "JSON5" in str(err) or "Invalid" in str(err)


def test_from_json5_validation_error() -> None:
    """Test Pydantic validation error returns Err."""
    # Valid JSON5 but wrong types for Student model
    bad_data = '{"id": "not_a_number", "name": "Test", "age": "also_not_number"}'
    result = from_json5(bad_data, Student)
    assert result.is_err()


def test_from_json5_bytes_input() -> None:
    """Test bytes input works correctly."""
    json5_bytes = b'{"id": 1, "name": "Jack", "age": 11}'
    result = from_json5(json5_bytes, Student)
    assert result.is_ok()
    student = result.unwrap()
    assert student.name == "Jack"
