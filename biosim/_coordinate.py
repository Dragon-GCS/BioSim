from functools import cache
from ._config import config


class Coordinate:
    """保存各生物的坐标信息， 左上角为坐标原点，x轴向右，y轴向下，index为坐标在一维数组中的索引"""

    __slots__ = ("x", "y")

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    @property
    @cache
    def index(self):
        return self.x + self.y * config.world.width

    def distance(self, other: "Coordinate") -> int:
        return abs(self.x - other.x) + abs(self.y - other.y)

    def radius(self, other: "Coordinate") -> int:
        return max(abs(self.x - other.x), abs(self.y - other.y))

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __add__(self, other: "Coordinate") -> "Coordinate":
        return Coordinate(self.x + other.x, self.y + other.y)

    def __iadd__(self, other: "Coordinate"):
        return self + other

    def __sub__(self, other: "Coordinate") -> "Coordinate":
        return Coordinate(self.x - other.x, self.y - other.y)

    def __isub__(self, other: "Coordinate"):
        return self - other

    def __eq__(self, other: "Coordinate") -> bool:
        return (self.x, self.y) == (other.x, other.y)

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"
