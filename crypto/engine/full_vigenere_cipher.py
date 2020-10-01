from crypto.engine.base_engine import BaseEngine, EngineCapabilities
from crypto.engine.data import *
from crypto.engine.key import *
from crypto.engine.vigenere_engine import VigenereEngine
from crypto.util.string_util import StringUtil

import numpy as np
import random
import string


class FullVigenereEngine(VigenereEngine):
    def __init__(self):
        super().__init__(
            EngineCapabilities(
                support_file=False,
                support_text=True,
                key_type=KeyType.STRING,
                key_length=1 + (26 * 26)
            )
        )

    def generate_random_key(self) -> Key:
        alphabet_sequence = [c for c in string.ascii_lowercase]

        key_sequence = ["key"]

        for i in range(26):
            key_sequence += random.sample(alphabet_sequence, 26)

        return Key(KeyType.STRING, key_sequence)

    def _do_encrypt(self, data: Data, key: Key) -> Data:
        string_array = self._transform_text(data)
        full_key_array = self._transform_key(key, string_array)

        alphabet_array = np.array(key.data[1:])

        index_array = (full_key_array * 26) + string_array

        encrypted_array = np.take(alphabet_array, index_array)

        return Data(data_type=DataType.TEXT, data=''.join(encrypted_array))

    def _do_decrypt(self, data: Data, key: Key) -> Data:
        string_array = StringUtil.strip_non_alphabet(data.text)

        full_key_array = self._transform_key(key, string_array)

        alphabet_array = np.array(key.data[1:])

        alphabet_matrix = np.reshape(alphabet_array, (26, 26))

        output_str = []

        for i in range(len(string_array)):
            cipher_char = string_array[i]
            key_index = full_key_array[i]
            alphabet_index = np.where(alphabet_matrix[key_index] == cipher_char)[0][0]
            output_str.append(chr(alphabet_index + ord('a')))

        return Data(data_type=DataType.TEXT, data=''.join(output_str))