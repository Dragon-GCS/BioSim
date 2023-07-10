from __future__ import annotations

from random import choice
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # to avoid circular import
    from ._world import World

from ._config import config
from ._coordinate import Coordinate
from ._genome import Genome
from .utils import spiral_scan


class Creature:
    """

    Attributes:
        perception (int): 感知范围(1~5)， 每点智力增加1
        movement (int): 移动力(1~5)，每点体力增加1
        life (int): 寿命，每回合消耗1点，为0时死亡，食物不足时每回合额外消耗1点
        food (int): 食物量(0~3[5])，每点体力增加1点上限
    """

    __slots__ = ("_genome", "_loc", "food", "life", "map")

    def __init__(self, location: Coordinate, map: World, genome: Genome | None = None) -> None:
        self._loc = location
        self._genome = genome or Genome()
        self.food = 0
        self.life = config.creature.life
        self.map = map

    def __eq__(self, other: "Creature") -> int:
        return self._genome == other._genome

    def __hash__(self) -> int:
        return hash(self._genome)

    @property
    def perception(self):
        """感知范围"""
        return min(1 + self._genome.traits["智力"], 5)

    @property
    def movement(self):
        return min(1 + self._genome.traits["体力"], 5)

    def is_live(self) -> bool:
        return self.life > 0

    def interact(self, other: "Creature"):
        pass

    def move(self, location: Coordinate):
        self._loc = location

    def step(self):
        """从自身位置开始，顺时针扫描周围的食物和生物。
        如果周围存在食物则移动到最远的食物处，否则随机移动到一个最远的位置
        寿命减1，食物不足时额外减1
        """
        location = self._loc  # 扫描起始位置
        self.map[self._loc] = 0  # 清空当前位置
        foods, creatures, outer = [], [], []
        max_radiums = min(self.perception, self.movement)
        # 扫描周围
        for radiums, direction in spiral_scan(self.perception):
            location += direction
            match self.map[location]:
                case 0 if radiums == max_radiums:
                    outer.append((radiums, location))
                case 1:
                    foods.append((radiums, location))
                case 2:
                    creatures.append((radiums, location))
                case _:
                    pass

        # TODO: interact with other creatures
        if foods and self.food <= config.creature.max_food:
            _, location = max(foods, key=lambda x: x[0])
            # _, location = max(foods, key=lambda x: x[0])
            self.move(location)
        else:
            _, location = choice(outer)
            self.move(location)
            self.food = max(0, self.food - 1)
        self.life -= 1 + (self.food == 0)
        self._genome.mutate()
