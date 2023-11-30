from tests.data_types import *


def test_record_clone() -> None:
    team1 = TEAM1
    team2 = team1.clone()
    assert team1 == team2

    # 对象非同一
    assert id(team1) != id(team2)
    assert id(team1.students) != id(team2.students)
    assert id(team1.students[0]) != id(team2.students[0])

    # 不变类型同一
    assert id(team1.name) == id(team2.name)
    assert id(team1.students[0].name) == id(team2.students[0].name)
    assert id(team1.students[0].age) == id(team2.students[0].age)

    team2.students[0].age += 1
    assert team1.students[0].age != team2.students[0].age
