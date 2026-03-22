class Array(list[int]):
    """可以继承自 List"""

    def __init__(self, arr: list[int]) -> None:
        super().__init__()
        self.extend(arr)

    def hi(self) -> None:
        print("hi array")


def test_array() -> None:
    arr = [1, 2, 4, 8, 16]

    a = Array(arr)
    a.extend(arr)
    print(a)
    a.hi()
