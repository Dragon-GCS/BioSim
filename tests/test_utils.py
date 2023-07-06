from unittest import TestCase

from biosim._coordinate import Coordinate
from biosim.utils import spiral_scan


class TestUtils(TestCase):
    def test_spiral_span(self):
        radiums = 4
        coordinates = list(spiral_scan(4))
        # fmt: off
        targets = [
            Coordinate(0, -1), Coordinate(1, 0),    # v >
            *[Coordinate(0, 1) for _ in range(2)],     # ^
            *[Coordinate(-1, 0) for _ in range(2)],   # <
            *[Coordinate(0, -1) for _ in range(2)],    # v
            Coordinate(0, -1), *[Coordinate(1, 0)] * 3,    # v > > >
            *[Coordinate(0, 1)] * 4,     # ^ ^ ^ ^
            *[Coordinate(-1, 0)] * 4,   # < < < <
            *[Coordinate(0, -1)] * 4,     # v v v v
            Coordinate(0, -1), *[Coordinate(1, 0)] * 5,    # v > > > >
            *[Coordinate(0, 1)] * 6,     # ^ ^ ^ ^ ^
            *[Coordinate(-1, 0)] * 6,   # < < < < <
            *[Coordinate(0, -1)] * 6,     # v v v v v
            Coordinate(0, -1), *[Coordinate(1, 0)] * 7,    # v > ...
            *[Coordinate(0, 1)] * 8,   # ^ ^ ...
            *[Coordinate(-1, 0)] * 8,  # < < ...
            *[Coordinate(0, -1)] * 8,  # v v ...
        ]
        # fmt: on
        # 4个边，每边长度为2 * radiums
        self.assertEqual(len(coordinates), 4 * 2 * sum(range(radiums + 1)))
        self.assertEqual(len(targets), len(coordinates))
        self.assertEqual(coordinates, targets)
