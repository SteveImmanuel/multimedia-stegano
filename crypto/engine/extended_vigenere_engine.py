from crypto.engine.base_engine import BaseEngine, EngineCapabilities
from crypto.engine.data import *
from crypto.engine.key import *
from crypto.engine.vigenere_engine import VigenereEngine
from crypto.util.file_util import FileUtil
from crypto.util.string_util import StringUtil
from nptyping import NDArray

import numpy as np
import random
import string
import os


class ExtendedVigenereEngine(VigenereEngine):
    def __init__(self):
        super().__init__(
            EngineCapabilities(
                support_file=True, support_text=True, key_type=KeyType.STRING, key_length=1
            )
        )

    def _do_encrypt(self, data: Data, key: Key) -> Data:
        if data.data_type == DataType.TEXT:
            string_array = self._transform_text(data)
            full_key_array = self._transform_key(key, len(string_array), np.int32)

            encrypted_array = string_array + full_key_array
            encrypted_array = np.mod(encrypted_array, 256)

            return Data(
                data_type=DataType.TEXT, data=''.join(map(chr, encrypted_array)), extended=True
            )
        elif data.data_type == DataType.FILE:
            input_handle = data.file_handle
            output_handle = FileUtil.generate_temp_file()
            output_path = output_handle.name

            input_handle.seek(0, os.SEEK_END)
            file_size = input_handle.tell()

            key_length = len(key.data[0])
            chunk_size = min(20000000, file_size)
            chunk_size += chunk_size % key_length

            input_handle.seek(0)

            for i in range(0, file_size + 1, chunk_size):
                output_handle.seek(i)
                input_handle.seek(i)

                bytes_left = file_size - i
                seek_count = min(chunk_size, bytes_left)

                input_array = np.fromfile(input_handle, count=seek_count, dtype=np.uint8)
                full_key_array = self._transform_key(key, len(input_array), np.uint8)

                encrypted_array = input_array + full_key_array

                encrypted_array.tofile(output_handle)

            output_handle.seek(0, os.SEEK_END)
            input_handle.seek(0, os.SEEK_END)
            input_handle.close()
            output_handle.close()

            return Data(data_type=DataType.FILE, data=output_path)

    def _do_decrypt(self, data: Data, key: Key) -> Data:
        if data.data_type == DataType.TEXT:
            string_array = self._transform_text(data)
            full_key_array = self._transform_key(key, len(string_array), np.int32)

            decrypted_array = string_array - full_key_array
            decrypted_array = np.mod(decrypted_array, 256)

            return Data(data_type=DataType.TEXT, data=''.join(map(chr, decrypted_array)))
        elif data.data_type == DataType.FILE:
            input_handle = data.file_handle
            output_handle = FileUtil.generate_temp_file()
            output_path = output_handle.name

            input_handle.seek(0, os.SEEK_END)
            file_size = input_handle.tell()

            key_length = len(key.data[0])
            chunk_size = min(20000000, file_size)
            chunk_size += chunk_size % key_length

            input_handle.seek(0)

            for i in range(0, file_size + 1, chunk_size):
                output_handle.seek(i)
                input_handle.seek(i)

                bytes_left = file_size - i
                seek_count = min(chunk_size, bytes_left)

                input_array = np.fromfile(input_handle, count=seek_count, dtype=np.uint8)
                full_key_array = self._transform_key(key, len(input_array), np.uint8)

                decrypted_array = input_array - full_key_array

                decrypted_array.tofile(output_handle)

            output_handle.seek(0, os.SEEK_END)
            input_handle.seek(0, os.SEEK_END)
            input_handle.close()
            output_handle.close()

            return Data(data_type=DataType.FILE, data=output_path)

    def _transform_key(self, key: Key, length: int, output_type) -> NDArray:
        key_array = np.frombuffer(key.data[0].encode(), np.int8)
        return np.resize(key_array, length).astype(output_type)

    def _transform_text(self, data: Data) -> NDArray[np.int32]:
        raw_text = StringUtil.strip_non_ascii(data.text)
        return np.array([ord(ch) for ch in raw_text], dtype=np.int32)