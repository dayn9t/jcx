import tempfile

from rustshed import Some

from jcx.db.jdb.variant import *
from tests.data_types import *


def test_all() -> None:
    dir1 = tempfile.mkdtemp()
    var = JdbVariant(Student, dir1, "g1")

    var.set(STUDENT1)
    assert var.get() == Some(STUDENT1)
    assert var.name() == "g1"
    assert var.exists()
