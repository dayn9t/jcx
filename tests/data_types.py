from typing import Final

from jcx.db.record import Record


class Student(Record):
    """用于演示/测试的记录"""

    name: str
    age: int


class Team(Record):
    """小组"""

    name: str
    students: list[Student]


STUDENT1: Final[Student] = Student(id=1, name="Jack", age=11)
STUDENT2: Final[Student] = Student(id=2, name="Jones", age=12)
JSON1 = """{
    "id": 1,
    "name": "Jack",
    "age": 11
}"""
JSON2 = """{
    "id": 2,
    "name": "Jones",
    "age": 12
}"""

TEAM1: Final[Team] = Team(id=1, name="group1", students=[STUDENT1, STUDENT2])
