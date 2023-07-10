import time

import numpy as np
from numpy.random import choice, random
from tqdm import trange

from ._config import config
from ._coordinate import Coordinate
from ._creature import Creature


class World:
    def __init__(self) -> None:
        self._map: np.ndarray = np.zeros((config.world.height, config.world.width), dtype=np.int8)
        self.creatures: list[Creature] = []
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

    def step(self, i: int) -> float:
        start = time.time()
        for creature in self.creatures:
            creature.step()
        if i % config.world.food_refresh_year == 0:
            self.refresh_food()
        return time.time() - start

    def start(self, max_round: int = 100):
        second_per_year = round(1 / config.world.year_per_second, 3)
        for i in trange(1, max_round + 1):
            cost = self.step(i)
            time.sleep(max(0, second_per_year - cost))

    def __getitem__(self, loc: Coordinate):
        if not all((0 <= loc.x < self._map.shape[1], 0 <= loc.y < self._map.shape[0])):
            return None
        return self._map[loc.y][loc.x]

    def __setitem__(self, loc: Coordinate, value: int):
        if not all((0 <= loc.x < self._map.shape[1], 0 <= loc.y < self._map.shape[0])):
            return None
        self._map[loc.y][loc.x] = value
