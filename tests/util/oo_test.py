from dataclasses import dataclass

from jcx.util.oo import *


@dataclass
class Student:
    id: int = 0
    name: str = ''
    height: float = 0


def test_complete():
    s1 = Student(1, 'Jack', 1.1)
    s2 = Student(2)
    s3 = Student(2, 'Jack', 1.1)

    complete(s1, s2)
    assert s2 == s3
