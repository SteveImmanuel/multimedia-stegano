import textwrap
import re
import random
import string


class StringUtil:
    @staticmethod
    def strip_non_ascii(input: str) -> str:
        return re.sub('[^\x00-\xff]', '', input)

    @staticmethod
    def strip_non_alphabet(input: str) -> str:
        return re.sub('[^a-zA-Z]+', '', input)

    @staticmethod
    def remove_char(input: str, char: str) -> str:
        return input.replace(char, '')

    @staticmethod
    def remove_space(input: str) -> str:
        return StringUtil.remove_char(input, ' ')

    @staticmethod
    def split_to_group(input: str, width: int = 5) -> str:
        input_no_space = StringUtil.remove_space(input)
        return ' '.join(textwrap.wrap(input_no_space, width=width))

    @staticmethod
    def generate_random_string(length: int) -> str:
        return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))

    @staticmethod
    def get_unique_char(input: str) -> str:
        unique_char = set()
        add_char = unique_char.add
        return ''.join([char for char in input if not (char in unique_char or add_char(char))])

    @staticmethod
    def pad_alphabet(input: str) -> str:
        pattern = f'[{input}]+'
        return input + re.sub(pattern, '', string.ascii_lowercase)
