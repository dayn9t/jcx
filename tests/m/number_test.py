from jcx.m.number import *


def test_is_real() -> None:
    assert is_real(1)
    assert is_real(1.0)
    assert not is_real('1')
    assert not is_real([])


def test_real_2d() -> None:
    assert real_2d(1) == (1, 1)
    assert real_2d(1.0) == (1.0, 1.0)
    assert real_2d((1, 1.0)) == (1.0, 1.0)


def test_align_round() -> None:
    align_num = 8
    m = {
        0: 0,
        1: 0,
        3: 0,
        4: 8,
        7: 8,
        8: 8,
        9: 8,
        15: 16,
        16: 16,
    }

    for k, v in m.items():
        assert align_round(k, align_num) == v
