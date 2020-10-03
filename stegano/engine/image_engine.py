import os
from typing import List, Union

import numpy as np
from PIL import Image
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
            RadioParam('Method', {
                CONCEAL_LSB: 'LSB',
                CONCEAL_BPCS: 'BPCS'
            }),
            RadioParam('Order', {
                CONCEAL_RANDOM: 'Random',
                CONCEAL_SEQ: 'Sequential'
            }),
            FloatParam('Threshold for BPCS', 0.1, 0.3)
        ]

    @staticmethod
    def get_extract_option() -> List[ConfigParam]:
        return [
            RadioParam('Method', {
                CONCEAL_LSB: 'LSB',
                CONCEAL_BPCS: 'BPCS'
            }),
        ]

    @staticmethod
    def get_supported_extensions() -> List[str]:
        return ['png', 'bmp']

    @staticmethod
    def check_file_supported(filepath: str) -> bool:
        return True

    @staticmethod
    def get_max_message(file_path: str, option: List[Union[str, float]]) -> int:
        is_lsb = option[1] == CONCEAL_LSB
        if is_lsb:
            image = imread(file_path)
            max_file_size = int(np.prod(image.shape))
            metadata_len = FileUtil.get_metadata_len(max_file_size) + 1

            return max_file_size - metadata_len

    @staticmethod
    def conceal(
            file_in_path: str,
            secret_file_path: str,
            file_out_path: str,
            encryption_key: str,
            config: List[str],
    ) -> (str, float):
        is_lsb = config[1] == CONCEAL_LSB
        is_random = config[2] == CONCEAL_RANDOM

        file_in_extension = os.path.splitext(file_in_path)[-1].lower()

        image = imread(file_in_path)
        original_image = image.copy()
        image_shape = image.shape

        image_flatten_view = image.ravel()

        secret_file_extension = os.path.splitext(secret_file_path)[-1][1:].lower()
        secret_file_len = os.path.getsize(secret_file_path) * 8  # in bit

        max_file_size = int(np.prod(image_shape))
        metadata = FileUtil.gen_metadata(secret_file_len, max_file_size, secret_file_extension)

        metadata_len = FileUtil.get_metadata_len(max_file_size) + 1

        secret_file_handle = open(secret_file_path, 'rb')

        if is_lsb:
            # Insert metadata
            metadata.append(1 if is_random else 0)
            for i in range(metadata_len):
                image_flatten_view[i] = (image_flatten_view[i] & 254) | metadata[i]

            # Generate sequence
            if is_random:
                min_pos = np.unravel_index(metadata_len, image_shape)
                seed = RandomUtil.get_seed_from_string(encryption_key)
                sequence = RandomUtil.get_random_sequence(min_pos, image_shape, secret_file_len,
                                                          seed)
                sequence.sort(key=lambda x: x[1])
            else:
                sequence = [(idx + metadata_len, idx) for idx in range(secret_file_len)]

            # Insert to image
            for position, idx in sequence:
                bit_position = idx % 8
                if bit_position == 0:
                    current_byte = secret_file_handle.read(1)

                # noinspection PyUnboundLocalVariable
                secret_bit = ord(current_byte) >> (7 - bit_position) & 1
                if is_random:
                    image[position] = (image[position] & 254) | secret_bit
                else:
                    image_flatten_view[position] = (image_flatten_view[position] & 254) | secret_bit

        else:
            raise RuntimeError('Not supported yet :(')

        imwrite(file_out_path + file_in_extension, image, file_in_extension)
        secret_file_handle.close()

        mse = np.mean((original_image - image) ** 2)
        psnr = 20 * np.log10(255 / np.sqrt(mse))

        return file_out_path + file_in_extension, psnr

    @staticmethod
    def extract(
            file_in_path: str,
            extract_file_path: str,
            encryption_key: str,
            config: List[Union[str, float, bool]],
    ) -> str:
        print(config)
        is_lsb = config[1] == CONCEAL_LSB

        image = imread(file_in_path)
        image_shape = image.shape

        image_flatten_view = image.ravel()

        seed = RandomUtil.get_seed_from_string(encryption_key)

        if is_lsb:
            max_file_size = int(np.prod(image_shape))
            metadata_len = FileUtil.get_metadata_len(max_file_size) + 1

            # Baca metadata
            metadata_frame = list(image_flatten_view[:metadata_len] & 1)
            is_random = metadata_frame.pop() == 1
            secret_file_len, secret_file_ext = FileUtil.extract_metadata(metadata_frame)

            output_handle = open(extract_file_path + '.' + secret_file_ext, 'wb')

            # Buat sequence
            if is_random:
                min_pos = np.unravel_index(metadata_len, image_shape)
                sequence = RandomUtil.get_random_sequence(min_pos, image_shape, secret_file_len,
                                                          seed)
                sequence.sort(key=lambda x: x[1])

            else:
                sequence = [(idx + metadata_len, idx) for idx in range(secret_file_len)]

            # Output
            temp_byte = []
            for position, idx in sequence:
                if is_random:
                    temp_byte.append(image[position] & 1)
                else:
                    temp_byte.append(image_flatten_view[position] & 1)

                if idx % 8 == 7:
                    byte = bytes([FileUtil.binary_to_dec(temp_byte)])
                    output_handle.write(byte)
                    temp_byte.clear()

            output_handle.close()

            return extract_file_path + '.' + secret_file_ext
        else:
            raise RuntimeError('Not supported yet :(')


if __name__ == '__main__':
    # ImageEngine.conceal('exif.png', 'simple.txt', 'out.png', '', [True, CONCEAL_LSB, CONCEAL_SEQ])
    # ImageEngine.extract('out.png', 'out_simple.txt', '')

    ImageEngine.conceal('tiger.bmp', 'simple.txt', 'out', 'a', [True, CONCEAL_LSB, CONCEAL_SEQ])
    ImageEngine.extract('email-ta.png', 'extracted.txt', 'wbqpbm', [True, CONCEAL_LSB])
