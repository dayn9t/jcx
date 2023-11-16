from jcx.db.jdb.util import *
from jcx.db.precord import *


def test_load():
    rs1 = load_list(DemoRecord, GROUP_DIR)
    assert len(rs1) > 1000

    rs2 = load_dict(DemoRecord, GROUP_DIR)
    assert len(rs2) > 1000
    assert isinstance(rs2, dict)
