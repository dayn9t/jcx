from jcx.text.txt_json import to_json, from_json
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

    items = [LictItem(0, "a"), LictItem(1, "b"), LictItem(2, "c")]
    m = Lict[int, str](items)

    for i, k in enumerate(m.keys()):
        assert i == k

    for i, p in enumerate(m.items()):
        assert items[i] == LictItem(p[0], p[1])

    d = {0: "a", 1: "b", 2: "c"}
    assert m.to_dict() == d


def test_lict_io() -> None:
    m = Lict[str, int]([])
    m["a"] = 1
    m["b"] = 2
    s = to_json(m.inner())
    # print(s)
    l1 = from_json(s, LictItems[str, int])
    assert l1 == [LictItem(key="a", value=1), LictItem(key="b", value=2)]
