import random


class RandomUtil:
    @staticmethod
    def get_random_sequence(min: int, max: int, n: int, seed: int) -> list:
        random.seed(seed)
        choices = list(range(min, max + 1))
        return random.sample(choices, n)