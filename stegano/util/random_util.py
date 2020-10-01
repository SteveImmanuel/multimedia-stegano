import random
from typing import Tuple

import numpy as np
from nptyping import ndarray


class RandomUtil:
    @staticmethod
    def get_random_sequence(min_pos: ndarray, shape: ndarray, n: int, seed: int) -> list:
        random.seed(seed)
        min_index = np.ravel_multi_index(min_pos, shape)
        max_index = np.prod(shape)
        sequence = random.sample(range(min_index, max_index), n)
        sequence = list(
            map(lambda val: (np.unravel_index(val[1], shape), val[0]), enumerate(sequence)))
        sequence.sort()
        return sequence

    @staticmethod
    def get_seed_from_string(text: str) -> int:
        list_char = list(map(lambda x: ord(x), text))
        return sum(list_char)
