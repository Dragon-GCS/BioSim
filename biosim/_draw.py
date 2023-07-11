import cv2
import numpy as np
from ._config import config

UI_SIZE = (config.ui.width, config.ui.height)


class Drawer:
    def __init__(self, window_name: str) -> None:
        self.window_name = window_name

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type != KeyboardInterrupt:
            return
        input("Press any key to exit...")
        self.close()
        return True

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
        cv2.destroyAllWindows()
