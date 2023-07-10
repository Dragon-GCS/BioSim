from unittest import TestCase

from biosim._coordinate import Coordinate
from biosim.utils import spiral_scan


class TestUtils(TestCase):
    def test_spiral_span(self):
        radiums = 4
        coordinates = list(spiral_scan(4))
        # fmt: off
        targets = [
            (1, Coordinate(0, -1)), (1, Coordinate(1, 0)),    # v >
            *[(1, Coordinate(0, 1)) for _ in range(2)],     # ^
            *[(1, Coordinate(-1, 0)) for _ in range(2)],   # <
            *[(1, Coordinate(0, -1)) for _ in range(2)],    # v
            (2, Coordinate(0, -1)), *[(2, Coordinate(1, 0))] * 3,    # v > > >
            *[(2, Coordinate(0, 1))] * 4,     # ^ ^ ^ ^
            *[(2, Coordinate(-1, 0))] * 4,   # < < < <
            *[(2, Coordinate(0, -1))] * 4,     # v v v v
            (3, Coordinate(0, -1)), *[(3, Coordinate(1, 0))] * 5,    # v > > > >
            *[(3, Coordinate(0, 1))] * 6,     # ^ ^ ^ ^ ^
            *[(3, Coordinate(-1, 0))] * 6,   # < < < < <
            *[(3, Coordinate(0, -1))] * 6,     # v v v v v
            (4, Coordinate(0, -1)), *[(4, Coordinate(1, 0))] * 7,    # v > ...
            *[(4, Coordinate(0, 1))] * 8,   # ^ ^ ...
            *[(4, Coordinate(-1, 0))] * 8,  # < < ...
            *[(4, Coordinate(0, -1))] * 8,  # v v ...
        ]
        # fmt: on
        # 4个边，每边长度为2 * radiums
        self.assertEqual(len(coordinates), 4 * 2 * sum(range(radiums + 1)))
        self.assertEqual(len(targets), len(coordinates))
        self.assertEqual(coordinates, targets)
