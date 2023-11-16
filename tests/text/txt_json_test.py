from jcx.db.precord import *
from jcx.text.txt_json import *


def test_io() -> None:
    s = to_json(R1)
    # print(s)
    g1 = from_json(s, DemoRecord)
    # print(g2)
    assert g1 == R1

    p = '/tmp/g1'
    save_json(g1, p)
    g3 = load_json(p, DemoRecord)

    assert g1 == g3
