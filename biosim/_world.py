import time
from random import random, sample
from tqdm import trange

from ._config import config
from ._coordinate import Coordinate
from ._creature import Creature


class World:
    def __init__(self) -> None:
        world_size = config.world.width * config.world.height
        self._map: list[int | Creature] = [0] * world_size
        self.creatures: set[Creature] = set()
        creature_num = config.world.init_count
        food_num = int(config.world.food_rate * (world_size - creature_num))
        for i in sample(range(world_size), food_num + creature_num):
            if len(self.creatures) < creature_num:
                # 根据索引计算坐标
                x, y = divmod(i, config.world.width)
                creature = Creature(Coordinate(x, y), self)
                self._map[i] = creature
                self.creatures.add(creature)
            else:
                self._map[i] = 1

    def refresh_food(self):
        for i, item in enumerate(self._map):
            if isinstance(item, Creature):
                continue
            self._map[i] = item + (random() < config.world.food_refresh_rate)

    def step(self):
        for creature in self.creatures:
            creature.step()
        self.refresh_food()

    def start(self, max_round: int = 100):
        second_per_year = round(1 / config.world.year_per_second, 2)
        for _ in trange(max_round):
            start = time.time()
            self.step()
            time.sleep(max(second_per_year + start - time.time(), 0))

    def __getitem__(self, loc: Coordinate):
        if loc.index >= len(self._map):
            return None
        return self._map[loc.index]

    def __setitem__(self, loc: Coordinate, value: int):
        if loc.index < len(self._map):
            self._map[loc.index] = value
