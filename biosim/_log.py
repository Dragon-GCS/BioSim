from tqdm import tqdm
from loguru import logger as log

log.remove()
log.add(lambda msg: tqdm.write(msg, end=""), format="{message}", colorize=True)
