from jcx.db.jdb.table import *
from tests.data_types import DemoRecord


def test_tab1() -> None:
    tab = Table(DemoRecord)
    tab.load('/tmp/groups')
    tab.clear()
    assert len(tab) == 0

    r0 = DemoRecord(0, 'one')
    r1 = DemoRecord(1, 'one')
    r2 = DemoRecord(2, 'one')
    r9 = DemoRecord(9, 'one')

    r = tab.add(r0).unwrap()
    assert r.id == 1
    assert len(tab) == 1
    assert tab.get(1).unwrap() == r1

    r = tab.add(r0).unwrap()
    assert r.id == 2
    assert len(tab) == 2
    assert tab.get(1).unwrap() == r1
    assert tab.get(2).unwrap() == r2

    # 已经存在的记录
    r = tab.add(r1)
    assert r.is_null()
    assert len(tab) == 2
    assert tab.get(1).unwrap() == r1
    assert tab.get(2).unwrap() == r2

    # 指定合法ID的记录
    r = tab.add(r9).unwrap()
    assert r.id == 9
    assert len(tab) == 3
    assert tab.get(1).unwrap() == r1
    assert tab.get(2).unwrap() == r2
    assert tab.get(9).unwrap() == r9

    # 更新
    r9.name = 'nine'
    assert tab.get(9).unwrap() != r9
    tab.update(r9)
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
