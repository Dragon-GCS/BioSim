from __future__ import annotations

from functools import cache
from random import choice, random
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
        self.life = 0
        self.map = map

    def __eq__(self, other: "Creature") -> int:
        return self._genome == other._genome

    def __hash__(self) -> int:
        return hash(self._genome)

    @property
    @cache
    def sex(self):
        return self._genome._gene.bit_count() % 2

    @property
    @cache
    def perception(self):
        """感知范围"""
        return min(1 + self._genome.traits["智力"], 10)

    @property
    @cache
    def movement(self):
        return min(1 + self._genome.traits["体力"], 10)

    @property
    @cache
    def charm(self):
        """魅力值，影响生育。越高生育率越高"""
        return (
            self.traits["外貌"] * 2 + 0.5 * self.traits["体力"] + 0.5 * self.traits["智力"]
        ) / config.gene.init_gene_count

    @property
    @cache
    def food_cost(self):
        return (
            self.traits["体力"] + self.traits["智力"] - 0.5 * self.traits["外貌"]
        ) / config.gene.init_gene_count

    @property
    def traits(self):
        return self._genome.traits

    def is_alive(self) -> bool:
        return self.life < config.creature.life

    def roll(self):
        """生成随机点数，点数越小，某件事成功率越高"""
        return random() - self.traits["幸运"] * 0.01

    def search_blank(self) -> Coordinate | None:
        """扫描自身周围的空地"""
        location = self._loc
        for _, direction in spiral_scan(self.perception):
            location += direction
            if self.map[location] == 0:
                return location

    def mate(self, other: "Creature"):
        if self.roll() > self.charm:
            return
        child_loc = other.search_blank() or self.search_blank()
        if child_loc is None:
            return
        child = Creature(child_loc, self.map, self._genome & other._genome)
        self.map.add_creature(child)

    def fight(self, other: "Creature"):
        if self.roll() < 0.5:
            other.life += 5
            other.food = 0
            self.food += other.food
        else:
            self.life += 5
            other.food += self.food
            self.food = 0

    def interact(self, other: "Creature"):
        dst = other.search_blank()
        if dst is None:
            return
        self.move(dst)
        if self.sex == other.sex:
            self.fight(other)
        else:
            self.mate(other)

    def move(self, location: Coordinate):
        self._loc = location
        self.map[location] = 2

    def step(self):
        """从自身位置开始，顺时针扫描周围的食物和生物。
        如果周围存在食物则移动到最远的食物处，否则随机移动到一个最远的位置
        寿命减1，食物不足时额外减1
        """
        location = self._loc  # 扫描起始位置
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

        if foods and self.food <= config.creature.max_food // 2:
            _, location = max(foods, key=lambda x: x[0])
            self.food += 1
            self.move(location)
        elif creatures and self.life >= config.creature.adult_age and self.food:
            _, location = choice(creatures)
            creatures = self.map.creatures[location]
            self.interact(creatures)
        elif outer:
            _, location = choice(outer)
            self.move(location)
        self.food = max(0, self.food - self.food_cost)
        self.life += 1 + (self.food == 0) * 10
        self._genome.mutate()
