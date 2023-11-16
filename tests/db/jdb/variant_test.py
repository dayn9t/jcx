from jcx.db.jdb.variant import *
from jcx.db.precord import DemoRecord, R1


def test_all():
    var = JdbVariant(DemoRecord, '/tmp', 'g1')

    var.set(R1)
    assert var.get() == R1
    assert var.name() == 'g1'
    assert var.exists()
