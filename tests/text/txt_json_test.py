import tempfile
from pathlib import Path

from jcx.text.txt_json import *
from tests.data_types import *


def test_json_from_to() -> None:
    json1 = to_json(STUDENT1)
    assert json1 == JSON1

    s1 = from_json(json1, Student).unwrap()
    assert s1 == STUDENT1

    json_bad = '''{
        "id": 1,
        "name": "Jack",
        "age": 11
    '''
    r = from_json(json_bad, Student)
    assert r.is_err()


def test_from_io() -> None:
    dir1 = tempfile.mkdtemp()
    f1 = Path(dir1, '1.json')
    f2 = Path(dir1, '2.json')
    # print(f1)
    r = save_json(STUDENT1, f1)
    assert r.is_ok()

    s1 = load_json(f1, Student).unwrap()
    assert s1 == STUDENT1

    s2 = load_json(f2, Student)
