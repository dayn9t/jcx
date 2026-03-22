from typing import Any


def print_array(arr: list[Any], title: str) -> None:
    """显示数组及程序员"""
    print(title)
    for i, v in enumerate(arr):
        print("  [%d]" % i, v)
