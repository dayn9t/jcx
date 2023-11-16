from jcx.m.rand import *


def test_random_choices():
    arr = list(range(10))
    n = 5
    ob = 0

    for i in range(100):
        arr1 = random_choices(arr, n, ob)
        assert len(arr1) == n
        assert arr1.count(ob) == 0
