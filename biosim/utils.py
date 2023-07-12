from __future__ import annotations

import signal
import sys
import typing
from multiprocessing import JoinableQueue, Process
from typing import Iterator

import cv2
import matplotlib.pyplot as plt
import numpy as np

from ._config import config
from ._coordinate import Coordinate

if typing.TYPE_CHECKING:
    from ._creature import Creature

UI_SIZE = (config.ui.width, config.ui.height)

match sys.platform:
    case "win32":
        plt.rcParams["font.sans-serif"] = ["SimHei"]
    case "darwin":
        plt.rcParams["font.sans-serif"] = ["PingFang HK"]
    case _:
        pass


def spiral_scan(max_radius: int) -> Iterator[tuple[int, Coordinate]]:
    """获取从原点开始，以螺旋扫描的方式遍历坐标系的坐标作为位移， 每一圈的遍历顺序为：v > ^ <。
    每圈都可以看作是从左下角开始移动的正方形，每个方向移动的步长等于2 * radius。但每个正方形的第一步都是向下移动的
    Args:
        max_radius: 最大半径
    Yield:
        radiums (int): 当前圈的半径
        direction (Coordinate): 当前移动方向
    """
    # 定义螺旋扫描的方向，按右、下、左、上的顺序移动
    # directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]  # -> ^ <- v
    directions = [Coordinate(1, 0), Coordinate(0, 1), Coordinate(-1, 0), Coordinate(0, -1)]

    for radius in range(1, max_radius + 1):
        yield radius, directions[-1]
        for _ in range(1, 2 * radius):
            yield radius, directions[0]
        for i in range(1, 4):
            for _ in range(1, 2 * radius + 1):
                yield radius, directions[i]


class Worker:
    """进程基类，封装了进程的创建和关闭"""

    def __init__(self) -> None:
        self.process = Process(target=self.work, daemon=True)
        self.queue = JoinableQueue()
        self.process.start()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        return True

    def work(self):
        # ignore SIGINT in the subprocess
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        while True:
            item = self.queue.get()
            try:
                self.handle(item)
            except Exception as e:
                print(e)
                break
            self.queue.task_done()

    def handle(self, item):
        raise NotImplementedError()

    def close(self):
        self.queue.close()
        self.process.terminate()


class Drawer(Worker):
    """绘制地图的进程，从队列中获取地图和延迟，然后绘制地图"""

    queue: JoinableQueue[tuple[np.ndarray, int]]

    def __init__(self, window_name: str) -> None:
        self.window_name = window_name
        super().__init__()

    def handle(self, item: tuple[np.ndarray, int]):
        _map, delay = item
        resized_map = cv2.resize(_map, UI_SIZE, interpolation=cv2.INTER_NEAREST)
        color_map = (
            np.stack([np.zeros_like(resized_map), (resized_map == 1), resized_map == 2])
            .transpose(1, 2, 0)
            .astype(np.float32)
        )
        cv2.imshow(self.window_name, color_map)
        cv2.waitKey(delay)

    def close(self):
        cv2.destroyAllWindows()
        super().close()


class Recorder(Worker):
    queue: JoinableQueue[Creature | None]

    def __init__(self) -> None:
        self.clear()
        self.fig = plt.figure(figsize=(12, 6), dpi=100)
        self.trait_ax = self.fig.add_subplot(1, 2, 1)
        self.age_ax = self.fig.add_subplot(1, 2, 2)
        super().__init__()

    def handle(self, creature: Creature | None):
        if creature is None:
            self.draw()
            return
        for trait, value in creature.traits.items():
            self.statistics["traits"][trait] += value
        sex = "雄性" if creature.sex else "雌性"
        self.statistics["traits"][sex] += 1
        self.statistics["ages"].append(creature.life)

    def draw(self):
        self.trait_ax.clear()
        self.trait_ax.bar(
            list(self.statistics["traits"].keys()), self.statistics["traits"].values()
        )
        self.age_ax.clear()
        self.age_ax.hist(self.statistics["ages"], bins=10, rwidth=0.8)
        self.age_ax.set_xlim(0, config.creature.life)
        self.fig.canvas.draw()
        plt.pause(0.1)
        self.clear()

    def done(self):
        self.queue.put(None)

    def record(self, creature: Creature):
        self.queue.put(creature)

    def clear(self):
        self.statistics = {
            "traits": {"智力": 0, "体力": 0, "幸运": 0, "外貌": 0, "雄性": 0, "雌性": 0},
            "ages": [],
        }
