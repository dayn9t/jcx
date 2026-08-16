import tempfile

from jcx.db.jdb.table import *
from tests.data_types import *


def test_tab1() -> None:
    dir1 = Path(tempfile.mkdtemp())
    tab = Table(Student)
    tab.load(dir1)
    tab.clear()
    assert len(tab) == 0

    r0 = Student(id=0, name="one", age=10)
    r1 = Student(id=1, name="one", age=10)
    r2 = Student(id=2, name="one", age=10)
    r9 = Student(id=9, name="one", age=10)

    r = tab.post(r0).unwrap()
    assert r.id == 1
    assert len(tab) == 1
    assert tab.get(1).unwrap() == r1

    r = tab.post(r0).unwrap()
    assert r.id == 2
    assert len(tab) == 2
    assert tab.get(1).unwrap() == r1
    assert tab.get(2).unwrap() == r2

    # 已经存在的记录
    r = tab.post(r1)
    assert r.is_null()
    assert len(tab) == 2
    assert tab.get(1).unwrap() == r1
    assert tab.get(2).unwrap() == r2

    # 指定合法ID的记录
    r = tab.post(r9).unwrap()
    assert r.id == 9
    assert len(tab) == 3
    assert tab.get(1).unwrap() == r1
    assert tab.get(2).unwrap() == r2
    assert tab.get(9).unwrap() == r9

    # 更新
    r9.name = "nine"
    assert tab.get(9).unwrap() != r9
    tab.put(r9)
    assert len(tab) == 3
    assert tab.get(1).unwrap() == r1
    assert tab.get(2).unwrap() == r2
    assert tab.get(9).unwrap() == r9

    # 删除
    tab.remove(1)
    assert len(tab) == 2
    assert tab.get(1).is_null()
    assert tab.get(2).unwrap() == r2
    assert tab.get(9).unwrap() == r9

    # 查询
    rs = tab.query(lambda a: a.id == 9)
    assert rs == [r9]

    ids = tab.query_ids(lambda a: a.id == 9)
    assert ids == [9]

    # print('\n', rs)


def test_table_sid() -> None:
    dir1 = Path(tempfile.mkdtemp())
    tab = TableSid(StudentSid)
    tab.load(dir1)
    tab.clear()
    assert len(tab) == 0

    id1 = "685cf0cabe3b15682b5ea464"
    id2 = "f0e1d2c3b4a5968778695a4b"
    r1 = StudentSid(id=id1, name="one", age=10)
    r2 = StudentSid(id=id2, name="two", age=20)

    # post 指定 str id（无自增——主键由调用方分配）
    r = tab.post(r1).unwrap()
    assert r.id == id1
    assert len(tab) == 1
    assert tab.get(id1).unwrap() == r1
    assert tab.get(id2).is_null()

    # 已存在 id 重复 post → Null
    assert tab.post(r1).is_null()
    # 空 id post → Null（str 主键必须显式分配）
    assert tab.post(StudentSid(id="", name="x", age=1)).is_null()
    # 空 id put → Null
    assert tab.put(StudentSid(id="", name="x", age=1)).is_null()

    assert tab.post(r2).unwrap() == r2
    assert len(tab) == 2
    assert sorted(tab.ids()) == sorted([id1, id2])

    # put 更新
    r1b = r1.clone()
    r1b.name = "uno"
    tab.put(r1b)
    assert len(tab) == 2
    assert tab.get(id1).unwrap().name == "uno"

    # query / query_ids
    assert [r.id for r in tab.query(lambda r: r.age >= 20)] == [id2]
    assert tab.query_ids(lambda r: r.name == "uno") == [id1]

    # 落盘往返：新实例 load 同目录恢复全部记录（含更新）
    tab2 = TableSid(StudentSid)
    tab2.load(dir1)
    assert len(tab2) == 2
    assert tab2.get(id1).unwrap().name == "uno"
    assert tab2.get(id2).unwrap() == r2

    # remove
    tab.remove(id1)
    assert len(tab) == 1
    assert tab.get(id1).is_null()
    tab3 = TableSid(StudentSid)
    tab3.load(dir1)
    assert len(tab3) == 1
