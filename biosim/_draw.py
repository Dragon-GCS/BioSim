import signal
from multiprocessing import JoinableQueue, Process

import cv2
import numpy as np

from ._config import config

UI_SIZE = (config.ui.width, config.ui.height)


class Drawer:
    def __init__(self, window_name: str) -> None:
        self.window_name = window_name
        self.queue = JoinableQueue()
        self._process = Process(target=self._daemon, daemon=True)
        self._process.start()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        return True

    def _daemon(self):
        # ignore SIGINT in the subprocess
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        while True:
            _map, delay = self.queue.get()
            self.draw_map(_map, delay)
            self.queue.task_done()

    def draw_map(self, map: np.ndarray, delay: int):
        resized_map = cv2.resize(map, UI_SIZE, interpolation=cv2.INTER_NEAREST)
        color_map = (
            np.stack([np.zeros_like(resized_map), (resized_map == 1), resized_map == 2])
            .transpose(1, 2, 0)
            .astype(np.float32)
        )
        cv2.imshow(self.window_name, color_map)
        cv2.waitKey(delay)

    def close(self):
        self.queue.join()
        self._process.kill()
        cv2.destroyAllWindows()
