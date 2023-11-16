from jcx.m.fun import *
from jcx.m.number import md5_int


def test_linear():
    f = Linear.from_xyxy(-1, 0, 1, 1)

    assert f(-1) == 0
    assert f(1) == 1


def test_md5_int():
    a = md5_int('abc', 100)
    print(len(a))
    for c in a:
        print(c)
