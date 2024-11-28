from jcx.text.txt_json import *


class Student(BaseModel):
    id: int
    name: str


def test_parse() -> None:
    t1 = '{"id": 1, "name": "jack"}'
    s1 = Student(id=1, name='jack')
    s2 = from_json(t1, Student).unwrap()
    assert s1 == s2

    t1 = '{"id": 1, "name": "ja\\"c\\"k"}'
    s1 = Student(id=1, name='ja"c"k')
    s2 = from_json(t1, Student).unwrap()
    assert s1 == s2


def test_save() -> None:
    s1 = Student(id=1, name='捷克')
    save_json(s1, '/tmp/student.json').unwrap()

