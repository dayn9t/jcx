from pydantic import TypeAdapter

from jcx.text.txt_json import to_json
from jcx.util.lict import *


def test_lict_map() -> None:
    m = Lict[int, str]([])
    assert m.get(1) is None
    assert 1 not in m
    m[1] = "a"
    assert 1 in m
    assert m.get(1) == "a"
    assert m[1] == "a"
    assert m.pop(1) == "a"
    assert m.pop(1) is None

    items = [LictItem(key=0, value="a"), LictItem(key=1, value="b"), LictItem(key=2, value="c")]
    m = Lict[int, str](items)

    for i, k in enumerate(m.keys()):
        assert i == k

    for i, p in enumerate(m.items()):
        assert items[i] == LictItem(key=p[0], value=p[1])

    d = {0: "a", 1: "b", 2: "c"}
    assert m.to_dict() == d


def test_lict_io() -> None:
    m = Lict[str, int]([])
    m["a"] = 1
    m["b"] = 2
    s = to_json(m.inner())
    # print(s)
    l1 = TypeAdapter(list[LictItem[str, int]]).validate_json(s)
    assert l1 == [LictItem(key="a", value=1), LictItem(key="b", value=2)]
