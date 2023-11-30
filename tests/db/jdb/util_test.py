import tempfile

from jcx.db.jdb.util import *
from jcx.text.txt_json import save_json
from tests.data_types import *


def test_load() -> None:
    dir1 = Path(tempfile.mkdtemp())
    save_json(STUDENT1, dir1 / '1.json').unwrap()
    save_json(STUDENT2, dir1 / '2.json').unwrap()
    rs1 = load_list(Student, dir1)
    assert len(rs1) == 2
    print(rs1)

    rs2 = load_dict(Student, dir1)
    assert len(rs2) == 2
    assert isinstance(rs2, dict)
    print(rs2)
