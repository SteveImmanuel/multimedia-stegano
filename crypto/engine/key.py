from enum import Enum
from typing import List, Union


class KeyType(Enum):
    NUMBER = 'number'
    STRING = 'string'


class Key:
    def __init__(self, key_type: KeyType, data: List[Union[str, int]]):
        self.key_type = key_type

        if key_type == KeyType.NUMBER:
            self.data = list(map(int, data))
        elif key_type == KeyType.STRING:
            self.data = list(map(lambda x: x.lower(), map(str, data)))
