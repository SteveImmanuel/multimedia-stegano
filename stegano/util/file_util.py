import math
import tempfile
import os
import uuid
import shutil

from typing import List, Dict, Tuple


class FileUtil:
    @staticmethod
    def gen_metadata(secret_len: int, max_len: int, ext: str) -> list:
        metadata = ''
        secret_len_bitsize = math.ceil(math.log(max_len, 2))
        metadata += bin(secret_len).lstrip('0b').rjust(secret_len_bitsize, '0')

        for _ in range(4 - len(ext)):
            metadata += '00000000'

        for char in ext:
            char_bin = bin(ord(char)).lstrip('0b').rjust(8, '0')
            metadata += char_bin

        return list(map(int, metadata))

    @staticmethod
    def get_metadata_len(filesize: int) -> int:
        secret_len_bitsize = math.ceil(math.log(filesize, 2))
        return secret_len_bitsize + 32

    @staticmethod
    def binary_to_dec(bin_array: List[int]) -> int:
        string_array = map(str, bin_array)
        dec = ''.join(string_array)
        dec = '0b' + dec
        return int(dec, 2)

    @staticmethod
    def extract_metadata(bin_array: List[int]) -> Tuple[int, str]:
        metadata = bin_array.copy()

        ext = []
        for i in range(4):
            char = []
            for j in range(8):
                char.insert(0, str(metadata.pop()))
            char = FileUtil.binary_to_dec(char)
            char = chr(char)
            if char != '\x00':
                ext.insert(0, char)
        ext = ''.join(ext)

        secret_msg_len = FileUtil.binary_to_dec(metadata)

        return (secret_msg_len, ext)

    @staticmethod
    def get_temp_out_name() -> str:
        return os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))

    @staticmethod
    def move_file(source: str, dest: str):
        shutil.move(source, dest)


if __name__ == "__main__":
    print(FileUtil.gen_metadata(8, 17, 'doc'))
