from jcx.util.algo import *


def test_dict_first_key() -> None:
    d = {1: "a", 2: "b", 3: "c", 4: "c"}

    assert dict_first_key(d, 1) == Null
    assert dict_first_key(d, "b").unwrap() == 2
    assert dict_first_key(d, "c").unwrap() == 3


def test_list_index() -> None:
    arr = [1, "a", 2, "b"]

    assert list_index(arr, 1) == Some(0)
    assert list_index(arr, "b") == Some(3)
    assert list_index(arr, "c") == Null


def test_low_bound_pos() -> None:
    arr = [1, 2, 4, 8, 16]

    p = low_pos(arr, 1)
    assert p == 0
    p = low_pos(arr, 3)
    assert p == 2
    p = low_pos(arr, 8)
    assert p == 3
    p = low_pos(arr, 17)
    assert p == 5
