from pydantic import BaseModel

from jcx.util.oo import *


class Student(BaseModel):
    id: int = 0
    name: str = ""
    height: float = 0


def test_complete() -> None:
    s1 = Student(id=1, name="Jack", height=1.1)
    s2 = Student(id=2)
    s3 = Student(id=2, name="Jack", height=1.1)

    complete(s1, s2)
    assert s2 == s3
