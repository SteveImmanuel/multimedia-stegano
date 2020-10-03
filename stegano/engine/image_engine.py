import os
from typing import List, Union

import numpy as np
import math
from PIL import Image
from bitstring import BitArray
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

            return (max_file_size - metadata_len) // 8

    @staticmethod
    def _binary_to_gray(x: int) -> int:
        shifted = x >> 1
        return shifted ^ x

    @staticmethod
    def _gray_to_binary(x: int) -> int:
        result = 0
        for i in range(8):
            result ^= x
            x >>= 1
        return result

    @staticmethod
    def _count_complexity(bitplane) -> float:
        counter = 0

        for i in range(7):
            counter += np.sum(bitplane[i] ^ bitplane[i + 1])
            counter += np.sum(bitplane[:, i] ^ bitplane[:, i + 1])

        return counter / 112

    @staticmethod
    def conceal(
            file_in_path: str,
            secret_file_path: str,
            file_out_path: str,
            encryption_key: str,
            config: List[Union[str, bool, float]],
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

        secret_file_handle = open(secret_file_path, 'rb')

        seed = RandomUtil.get_seed_from_string(encryption_key)

        if is_lsb:
            max_file_size = int(np.prod(image_shape))
            metadata = FileUtil.gen_metadata(secret_file_len, max_file_size, secret_file_extension)

            metadata_len = FileUtil.get_metadata_len(max_file_size) + 1

            # Insert metadata
            metadata.append(1 if is_random else 0)
            for i in range(metadata_len):
                image_flatten_view[i] = (image_flatten_view[i] & 254) | metadata[i]

            # Generate sequence
            if is_random:
                min_pos = np.unravel_index(metadata_len, image_shape)
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
            complexity_threshold = config[3]
            print(image_shape)
            cgc_image = ImageEngine._binary_to_gray(image)
            block_index_size = (image_shape[0] // 8, image_shape[1] // 8, image_shape[2], 8)

            complexity = np.zeros(block_index_size, dtype=np.float)

            bit_plane_size = (image_shape[0], image_shape[1], image_shape[2], 1)
            cgc_bit_plane = np.reshape(cgc_image, bit_plane_size)
            cgc_bit_plane = np.unpackbits(cgc_bit_plane, axis=3)

            for channel in range(block_index_size[2]):
                for row in range(block_index_size[0]):
                    for col in range(block_index_size[1]):
                        for plane in range(8):
                            # Get bitplane
                            top_idx = row * 8
                            left_idx = col * 8
                            bitplane = cgc_bit_plane[top_idx:top_idx + 8,
                                       left_idx:left_idx + 8, channel, plane]

                            complexity[row, col, channel, plane] = ImageEngine._count_complexity(
                                bitplane)

            # Get max message
            max_message_size = int(np.prod(image_shape)) * 8  # Dalam bit
            metadata_conjugate_list_len = math.ceil(max_message_size / 64)
            metadata_len = FileUtil.get_metadata_len(max_message_size)
            metadata_len += 2 + 32 + metadata_conjugate_list_len  # 2 binary option + 1 float

            max_file_size = max_message_size - metadata_len

            print(max_file_size)
            print(metadata_len)

            metadata = FileUtil.gen_metadata(secret_file_len, max_file_size, secret_file_extension)

            metadata.append(is_random)
            metadata.append(0)  # TODO is_encrypted

            complexity_threshold_bit = BitArray(float=complexity_threshold, length=32)
            for threshold_bit in complexity_threshold_bit:
                metadata.append(1 if threshold_bit else 0)

            noise_index = np.where(complexity > complexity_threshold)
            noise_index_arr = np.array(noise_index)
            noise_index_arr = np.transpose(noise_index_arr)

            metadata_block_len = math.ceil(metadata_len / 64)
            metadata_block_index_arr = noise_index_arr[:metadata_block_len]
            noise_index_arr = noise_index_arr[metadata_block_len:]

            if is_random:
                np.random.seed(seed)
                noise_index_arr = np.random.permutation(noise_index_arr)

            message_data = ImageEngine._load_secret_message(secret_file_path)

            for (row, col, channel, plane), data in zip(noise_index_arr, message_data):
                complexity = ImageEngine._count_complexity(data)
                if complexity <= complexity_threshold:
                    data = ImageEngine._conjugate(data)
                    metadata.append(1)
                else:
                    metadata.append(0)

                top_idx = row * 8
                left_idx = col * 8

                cgc_bit_plane[top_idx:top_idx + 8, left_idx:left_idx + 8, channel, plane] = data

            metadata = np.pad(metadata, (0, 64 - len(metadata) % 64)).reshape((-1, 8, 8))
            for (row, col, channel, plane), data in zip(metadata_block_index_arr, metadata):
                top_idx = row * 8
                left_idx = col * 8

                cgc_bit_plane[top_idx:top_idx + 8, left_idx:left_idx + 8, channel, plane] = data

            new_cgc_image = np.packbits(cgc_bit_plane, axis=3)
            new_cgc_image = np.reshape(new_cgc_image, image_shape)
            image = ImageEngine._gray_to_binary(new_cgc_image)

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

    @staticmethod
    def _conjugate(bitplane):
        checker_board = np.array([[1, 0] * 4, [0, 1] * 4] * 4)
        return np.logical_xor(bitplane, checker_board).astype(int)

    @staticmethod
    def _load_secret_message(secret_message_path):
        secret_segments = np.array([], dtype=int)
        with open(secret_message_path, 'rb') as f:
            bytes = f.read()
            for byte in bytes:
                bin_string = bin(byte).lstrip('0b').rjust(8, '0')
                segment = np.array(list(map(int, bin_string)))
                secret_segments = np.append(secret_segments, segment)
        secret_segments = np.pad(secret_segments, (0, 64 - len(secret_segments) % 64))
        return np.reshape(secret_segments, (-1, 8, 8))


if __name__ == '__main__':
    # ImageEngine.conceal('exif.png', 'simple.txt', 'out.png', '', [True, CONCEAL_LSB, CONCEAL_SEQ])
    # ImageEngine.extract('out.png', 'out_simple.txt', '')

    ImageEngine.conceal('kecil.png', 'simple.txt', 'out', 'a',
                        [True, CONCEAL_BPCS, CONCEAL_RANDOM, 0.3])
    # ImageEngine.extract('email-ta.png', 'extracted.txt', 'wbqpbm', [True, CONCEAL_LSB])
