import math
import random


def random_seed() -> int:
    return math.floor(random.random() * 2 ** 31)


class Random:
    def __init__(self, seed: int):
        self.seed = seed

    def next(self) -> float:
        if self.seed:
            self.seed = (48271 & 0xFFFFFFFF) * (self.seed & 0xFFFFFFFF) & 0xFFFFFFFF
            return (2 ** 31 - 1) & self.seed / 2 ** 31
        else:
            return random.random()
