import random
import string


class StringUtil:
    @staticmethod
    def generate_random_string(length: int) -> str:
        return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))
