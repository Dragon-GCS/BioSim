import time

import numpy as np
from numpy.random import choice, random
from tqdm import trange

from ._config import config
from ._coordinate import Coordinate
from ._creature import Creature
from ._log import log
from .utils import Drawer, Recorder


class World:
    def __init__(self) -> None:
        self._map: np.ndarray = np.zeros((config.world.height, config.world.width), dtype=np.int8)
        self.creatures: dict[Coordinate, Creature] = {}
        self.drawer = Drawer("生物模拟器")
        self.recorder = Recorder()
        self.refresh_food()
        blanks = np.where(self._map == 0)
        for i in choice(np.arange(len(blanks[0])), config.world.init_count, replace=False):
            x, y = int(blanks[1][i]), int(blanks[0][i])
            creature = Creature(Coordinate(x, y), self)
            self.add_creature(creature)

    def add_creature(self, creature: Creature):
        self[creature._loc] = 2
        self.creatures[creature._loc] = creature

    def remove_creature(self, creature: Creature) -> Creature | None:
        self[creature._loc] = 0
        return self.creatures.pop(creature._loc, None)

    def refresh_food(self):
        # 空地上随机生成食物并在地图上标记为1
        food_mask = (random(self._map.shape) < config.world.food_rate) & (self._map == 0)
        self._map = np.where(food_mask, 1, self._map)

    def step(self, i: int) -> float:
        start = time.time()
        for creature in list(self.creatures.values()):
            self.remove_creature(creature)
            if creature.is_alive():
                creature.step()
                self.add_creature(creature)
                self.recorder.record(creature)
        self.recorder.done()
        if i % config.world.food_refresh_year == 0:
            self.refresh_food()
        return time.time() - start

    def start(self, max_round: int = 100):
        print(config.model_dump_json(indent=2))
        for i in trange(1, max_round + 1):
            try:
                cost = self.step(i)
                delay = max(1, int((config.world.second_per_year - cost) * 1000))
                self.drawer.queue.put((self._map, delay))
            except KeyboardInterrupt:
                if input("Input q to exit...\n") == "q":
                    break
            if i % 5 == 0:
                log.debug(f"第{i}年，共有{len(self.creatures)}个生物")
        input("Wait...")
        self.drawer.close()
        self.recorder.close()

    def __getitem__(self, loc: Coordinate):
        if not all((0 <= loc.x < self._map.shape[1], 0 <= loc.y < self._map.shape[0])):
            return None
        return self._map[loc.y][loc.x]

    def __setitem__(self, loc: Coordinate, value: int):
        if not all((0 <= loc.x < self._map.shape[1], 0 <= loc.y < self._map.shape[0])):
            return None
        self._map[loc.y][loc.x] = value
