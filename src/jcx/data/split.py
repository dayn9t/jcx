import random

from jcx.util.algo import lookup


def random_split_n(n: int, radios: list[float]) -> list[list[int]]:
    """按比例随机分割整数集合 [0, n-1]"""
    total = sum(radios)
    # 累积比例对应的分割边界
    ends: list[int] = []
    cumulative = 0.0
    for r in radios:
        cumulative += r
        ends.append(int(cumulative / total * n))

    indices = list(range(n))
    random.shuffle(indices)

    start = 0
    slices: list[list[int]] = []
    for end in ends:
        slices.append(indices[start:end])
        start = end
    return slices


def random_split_array(arr: list[object], radio_arr: list[float]) -> list[list[object]]:
    """按比例随机分割数组"""
    slices = random_split_n(len(arr), radio_arr)
    return [lookup(s, arr) for s in slices]


def random_split(x: int | list[object], radio: list[float]) -> list[list[object]]:
    """按比例随机分割整数集合或数组"""
    if isinstance(x, int):
        # list[list[int]] 非协变于 list[list[object]]，显式提升元素类型
        return [list(s) for s in random_split_n(x, radio)]
    if isinstance(x, list):
        return random_split_array(x, radio)
    raise TypeError(f"Unsupported type to split: {type(x).__name__}")


def group(arr: list[object], group_member: int) -> list[list[object]]:
    """分组"""
    total = len(arr)
    return [arr[i : i + group_member] for i in range(0, total, group_member)]
