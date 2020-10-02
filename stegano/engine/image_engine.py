import os
from typing import List, Union

import numpy as np
from imageio import imread, imwrite

from stegano.engine import BaseEngine
from stegano.gui.config_param import RadioParam, ConfigParam, FloatParam
from stegano.util import RandomUtil, FileUtil

CONCEAL_LSB = 'conc_lsb'
CONCEAL_BPCS = 'conc_bpcs'
CONCEAL_RANDOM = 'conc_random'
CONCEAL_SEQ = 'conc_seq'
ENCRYPT_ON = 'enc_on'
ENCRYPT_OFF = 'enc_off'


class ImageEngine(BaseEngine):
    @staticmethod
    def get_conceal_option() -> List[ConfigParam]:
        return [
            RadioParam('Method', {CONCEAL_BPCS: 'BPCS', CONCEAL_LSB: 'LSB'}),
            RadioParam('Order', {CONCEAL_RANDOM: 'Random', CONCEAL_SEQ: 'Sequential'}),
            FloatParam('Threshold for BPCS', 0.1, 0.3)
        ]

    @staticmethod
    def get_supported_extensions() -> List[str]:
        return ['png', 'bmp']

    @staticmethod
    def check_file_supported(filepath: str) -> bool:
        return True

    @staticmethod
    def get_max_message(file_path: str, option: List[Union[str, float]]) -> int:
        return 1

    @staticmethod
    def conceal(
            file_in_path: str,
            secret_file_path: str,
            file_out_path: str,
            encryption_key: str,
            config: List[str],
    ) -> None:
        is_random = False
        is_lsb = True

        file_in_extension = os.path.splitext(file_in_path)[-1].lower()

        image = imread(file_in_path)
        image_shape = image.shape

        secret_file_extension = os.path.splitext(secret_file_path)[-1][1:].lower()
        secret_file_len = os.path.getsize(secret_file_path) * 8  # in bit

        max_file_size = int(np.prod(image_shape))
        metadata = FileUtil.gen_metadata(secret_file_len, max_file_size, secret_file_extension)

        metadata_len = FileUtil.get_metadata_len(max_file_size) + 1

        secret_file_handle = open(secret_file_path, 'rb')

        if is_lsb:
            min_pos = np.unravel_index(metadata_len, image_shape)

            metadata.append(1 if is_random else 0)
            image_flatten_view = image.ravel()

            # Insert metadata
            for i in range(metadata_len):
                image_flatten_view[i] = (image_flatten_view[i] & 254) | metadata[i]

            if is_random:
                seed = RandomUtil.get_seed_from_string(encryption_key)
                sequence = RandomUtil.get_random_sequence(min_pos, image_shape, secret_file_len,
                                                          seed)
                sequence.sort(key=lambda x: x[1])

                for position, idx in sequence:
                    bit_position = idx % 8
                    if bit_position == 0:
                        current_byte = secret_file_handle.read(1)

                    # noinspection PyUnboundLocalVariable
                    secret_bit = ord(current_byte) >> (7 - bit_position) & 1
                    image[position] = (image[position] & 254) | secret_bit
            else:
                for idx in range(secret_file_len):
                    bit_position = idx % 8
                    if bit_position == 0:
                        current_byte = secret_file_handle.read(1)

                    # noinspection PyUnboundLocalVariable
                    secret_bit = ord(current_byte) >> (7 - bit_position) & 1
                    img_idx = idx + metadata_len
                    image_flatten_view[img_idx] = (image_flatten_view[img_idx] & 254) | secret_bit


        else:
            raise RuntimeError('Not supported yet :(')

        imwrite(file_out_path, image, file_in_extension)
        secret_file_handle.close()

    @staticmethod
    def extract(file_in_path: str, extract_file_path: str, encryption_key: str) -> None:
        is_lsb = True

        image = imread(file_in_path)
        image_shape = image.shape

        image_flatten_view = image.ravel()

        output_handle = open(extract_file_path, 'wb')
        seed = RandomUtil.get_seed_from_string(encryption_key)

        if is_lsb:
            max_file_size = int(np.prod(image_shape))
            metadata_len = FileUtil.get_metadata_len(max_file_size) + 1

            # Baca metadata
            metadata_frame = list(image_flatten_view[:metadata_len] & 1)
            is_random = metadata_frame.pop() == 1
            secret_file_len, secret_file_ext = FileUtil.extract_metadata(metadata_frame)

            if is_random:
                min_pos = np.unravel_index(metadata_len, image_shape)
                sequence = RandomUtil.get_random_sequence(min_pos, image_shape, secret_file_len,
                                                          seed)
                sequence.sort(key=lambda x: x[1])

                temp_byte = []
                for position, idx in sequence:
                    temp_byte.append(image[position] & 1)

                    if idx % 8 == 7:
                        byte = bytes([FileUtil.binary_to_dec(temp_byte)])
                        output_handle.write(byte)
                        temp_byte.clear()
            else:
                temp_byte = []
                for idx in range(secret_file_len):
                    temp_byte.append(image_flatten_view[idx + metadata_len] & 1)

                    if idx % 8 == 7:
                        byte = bytes([FileUtil.binary_to_dec(temp_byte)])
                        output_handle.write(byte)
                        temp_byte.clear()

            output_handle.close()

        else:
            raise RuntimeError('Not supported yet :(')


if __name__ == '__main__':
    ImageEngine.conceal('sample.png', 'simple.txt', 'out.png', '', [])
    ImageEngine.extract('out.png', 'out_simple.txt', '')

    # ImageEngine.conceal('tiger.bmp', 'simple.txt', 'out', 'a', [])
    # ImageEngine.extract('out', 'extracted.txt', 'a')
