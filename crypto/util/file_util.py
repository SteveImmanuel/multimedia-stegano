from typing import BinaryIO

import os
import tempfile


class FileUtil:
    @staticmethod
    def generate_temp_file() -> BinaryIO:
        return tempfile.NamedTemporaryFile(delete=False)

    @staticmethod
    def read_file(path: str) -> str:
        with open(path, 'r') as file:
            data = file.read()

        return data

    @staticmethod
    def save_file(path: str, data: str):
        with open(path, 'w') as file:
            file.write(data)

    @staticmethod
    def with_move_file(exec_func, filepath):
        def wrapper(*args, **kwargs):
            result = exec_func(*args, **kwargs)
            result.move_file(filepath)
            return f'Execution complete. File saved in {filepath}.'

        return wrapper
