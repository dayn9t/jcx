import tempfile
from datetime import datetime
from pathlib import Path

from jcx.text.txt_json import *
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
