from jcx.db.jdb.util import *
from tests.data_types import *


def test_load() -> None:
    rs1 = load_list(DemoRecord, GROUP_DIR)
    assert len(rs1) > 1000

    rs2 = load_dict(DemoRecord, GROUP_DIR)
    assert len(rs2) > 1000
    assert isinstance(rs2, dict)
