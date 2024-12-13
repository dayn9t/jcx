from datetime import time

from jcx.time.dt import *


def atest_time() -> None:
    s = arrow.now()
    print(s)
    t = s.time()
    print(t)

    t = time(1, 1)
    print(t)


def atest_arrow() -> None:
    now = arrow.now()
    print(now, type(now))

    s = now.strftime("%Y-%m-%d/%H-%M-%S.%f")[:-3]
    print(s)
    a = arrow.Arrow(970, 1, 1)
    b = arrow.Arrow(1970, 1, 2)
    print(a, b)
    d = b - a
    print(d, type(d))

    s = "2021-08-14T23:21:28.409629+08:00"
    t = arrow.get(s)
    print(s)
    print(t)

    t1 = arrow.now().time()
    print("time:", t1, type(t1))
    a = arrow.get(s)
    print("a:", a)


def atest_funs() -> None:
    print(now_iso_str())
    _s = str(arrow.now())
    print("now_local_str:", now_local_str())
    print("now_local_str:", now_local_str(ms=True))
    print("now_id", now_id())
    print("now_id", now_id(ms=True))
    print("now_id", now_file(".jpg"))

    s = "2020-11-27T08:46:18.676+08:00"
    dt = arrow.get(s)
    print("dt:", dt, datetime_local_str(dt))
    print("tt:", dt.time(), arrow.now().time())
    print("tt:", type(arrow.now().time()))
    print(datetime_local_str(dt))

    print(now_local_str())
