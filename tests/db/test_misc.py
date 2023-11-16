from pathlib import Path

from jcx.db.jdb.counter import JdbCounter
from jcx.db.precord import R1


def test_counter():
    db = Path('/tmp/jdb_test')

    c1 = JdbCounter(db, 'test_c1')
    c1.reset()
    assert c1.get() == 0

    for i in range(1, 10):
        n = next(c1)
        assert i == n


def test_demo_record():
    r = R1.clone()
    assert r == R1
    r.name = ''
    assert r != R1
