from crypto.util.file_util import FileUtil
from enum import Enum
from typing import Union, BinaryIO

import os
import shutil


class DataType(Enum):
    FILE = 'file'
    TEXT = 'text'


class Data:
    def __init__(self, data_type: DataType, data: str, extended: bool = False):
        self.data_type = data_type
        if self.data_type == DataType.TEXT and not extended:
            self._data = data.lower()
        else:
            self._data = data

    @property
    def text(self) -> str:
        assert self.data_type == DataType.TEXT
        return self._data

    @property
    def file_handle(self) -> BinaryIO:
        assert self.data_type == DataType.FILE
        return open(self._data, 'rb')

    def move_file(self, new_path: str):
        assert self.data_type == DataType.FILE

        if not os.path.isfile(self._data):
            raise Exception('Source file not found')

        shutil.move(self._data, new_path)
        self._data = new_path

    @property
    def path(self) -> str:
        assert self.data_type == DataType.FILE
        return self._data
