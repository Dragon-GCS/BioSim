from typing import Iterator

from ._coordinate import Coordinate


def spiral_scan(max_radius: int) -> Iterator[tuple[int, Coordinate]]:
    """获取从原点开始，以螺旋扫描的方式遍历坐标系的坐标作为位移， 每一圈的遍历顺序为：v > ^ <。
    每圈都可以看作是从左下角开始移动的正方形，每个方向移动的步长等于2 * radius。但每个正方形的第一步都是向下移动的
    Args:
        max_radius: 最大半径
    Yield:
        radiums (int): 当前圈的半径
        direction (Coordinate): 当前移动方向
    """
    # 定义螺旋扫描的方向，按右、下、左、上的顺序移动
    # directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]  # -> ^ <- v
    directions = [Coordinate(1, 0), Coordinate(0, 1), Coordinate(-1, 0), Coordinate(0, -1)]

    for radius in range(1, max_radius + 1):
        yield radius, directions[-1]
        for _ in range(1, 2 * radius):
            yield radius, directions[0]
        for i in range(1, 4):
            for _ in range(1, 2 * radius + 1):
                yield radius, directions[i]
