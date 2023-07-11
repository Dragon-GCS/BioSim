import time

import numpy as np
from numpy.random import choice, random
from tqdm import trange

from ._config import config
from ._coordinate import Coordinate
from ._creature import Creature
from ._draw import Drawer
from ._log import log


class World:
    def __init__(self) -> None:
        self._map: np.ndarray = np.zeros((config.world.height, config.world.width), dtype=np.int8)
        self.creatures: list[Creature] = []
        self.statistics = {}

        self.refresh_food()
        blanks = np.where(self._map == 0)
        for i in choice(np.arange(len(blanks[0])), config.world.init_count, replace=False):
            x, y = int(blanks[1][i]), int(blanks[0][i])
            creature = Creature(Coordinate(x, y), self)
            self._map[y][x] = 2
            self.creatures.append(creature)

    def refresh_food(self):
        # 空地上随机生成食物并在地图上标记为1
        food_mask = random(self._map.shape) < config.world.food_rate
        self._map = np.where(food_mask, 1, self._map)

    def update_statistics(self, traits: dict[str, int]):
        """更新统计信息"""
        for trait, value in traits.items():
            self.statistics[trait] = self.statistics.get(trait, 0) + value

    def step(self, i: int) -> float:
        start = time.time()
        lives = []
        self.statistics.clear()
        for creature in self.creatures:
            if creature.is_alive():
                lives.append(creature)
                creature.step()
                self.update_statistics(creature.traits)
            else:
                self[creature._loc] = 0
        if i % config.world.food_refresh_year == 0:
            self.refresh_food()
        self.creatures = lives
        return time.time() - start

    def start(self, max_round: int = 100):
        with Drawer("生物进化模拟器") as drawer:
            for i in trange(1, max_round + 1):
                cost = self.step(i)
                delay = max(1, int((config.world.second_per_year - cost) * 1000))
                drawer.draw_map(self._map, delay)
                if i % 5 == 0:
                    log.debug(f"第{i}年，共有{len(self.creatures)}个生物，{self.statistics}")

    def __getitem__(self, loc: Coordinate):
        if not all((0 <= loc.x < self._map.shape[1], 0 <= loc.y < self._map.shape[0])):
            return None
        return self._map[loc.y][loc.x]

    def __setitem__(self, loc: Coordinate, value: int):
        if not all((0 <= loc.x < self._map.shape[1], 0 <= loc.y < self._map.shape[0])):
            return None
        self._map[loc.y][loc.x] = value
