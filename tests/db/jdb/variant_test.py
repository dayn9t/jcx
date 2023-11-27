from jcx.db.jdb.variant import *
from tests.data_types import *


def test_all() -> None:
    var = JdbVariant(DemoRecord, '/tmp', 'g1')

    var.set(R1)
    assert var.get() == R1
    assert var.name() == 'g1'
    assert var.exists()
