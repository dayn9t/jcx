from jcx.time.count_timer import *


def test_timer():
    timer = CountTimer(10)

    for i in range(30):
        if timer.inc_check():
            # print(i + 1)
            timer.reset()
