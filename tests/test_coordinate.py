from biosim import Coordinate
from unittest import TestCase


class TestCoordinate(TestCase):
    def test_operator(self):
        origin = Coordinate(0, 0)
        left = Coordinate(-1, 0)
        right = Coordinate(1, 0)
        self.assertEqual(origin + left, left)
        self.assertEqual(origin - right, left)
