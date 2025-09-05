import time
from jcx.time.stop_watch import StopWatch


def test_run_time_stats():
    stats = StopWatch()
    for _ in range(5):
        stats.start()
        # 你的代码
        time.sleep(0.1)
        stats.stop()

    print("单次:", stats.last())
    print("平均:", stats.avg())
    print("最大:", stats.max())
    print("最小:", stats.min())

    # 或者用上下文管理器
    with StopWatch() as stats:
        time.sleep(0.2)
    print("单次:", stats.last())
