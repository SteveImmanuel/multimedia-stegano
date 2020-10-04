import math
import os
import random
from typing import List, Union, Tuple

import cv2
import numpy as np
import skvideo.io

from stegano.engine.base_engine import BaseEngine
from stegano.engine.constants import *
from stegano.gui.config_param import ConfigParam, RadioParam
from stegano.util.file_util import FileUtil
from stegano.util.random_util import RandomUtil


class VideoEngine(BaseEngine):
    @staticmethod
    def check_key(key: str):
        assert 1 <= len(key) <= 25, 'Key length must be between 1 and 25'

    @staticmethod
    def rgb_to_bgr(location: Tuple) -> Tuple:
        location = np.array(location)
        location[-1] = 2 - location[-1]
        return tuple(location)

    @staticmethod
    def parse_config(config: List[str]) -> List[bool]:
        res = [False] * 3
        res[0] = True if config[0] else False
        res[1] = True if config[1] == FRAME_SEQ else False
        res[2] = True if config[2] == PIXEL_SEQ else False
        return res

    @staticmethod
    def generate_sequence(config: List[Union[str, float]], min_pos: Tuple, video_shape: Tuple,
                          message_len: int, seed: int) -> List[Tuple[Tuple, int]]:
        _, is_frame_seq, is_pixel_seq = VideoEngine.parse_config(config)
        random.seed(seed)

        if not is_frame_seq and not is_pixel_seq:
            return RandomUtil.get_random_sequence(min_pos, video_shape, message_len,
                                                  random.random())

        if is_frame_seq and is_pixel_seq:
            min_idx = int(np.ravel_multi_index(min_pos, video_shape))
            return [(np.unravel_index(i, video_shape), i - min_idx)
                    for i in range(min_idx, min_idx + message_len)]

        frame_shape = video_shape[1:]
        max_bit_in_frame = int(np.prod(frame_shape))
        frame_needed = math.ceil(
            (message_len + np.ravel_multi_index(min_pos, video_shape) + 1) / max_bit_in_frame)

        if is_frame_seq and not is_pixel_seq:
            temp_sequence = []
            for frame_pos in range(frame_needed):
                if frame_pos == 0:
                    # first_frame
                    min_pixel_pos = min_pos[1:]  # for metadata
                    bit_len = max_bit_in_frame - np.ravel_multi_index(min_pixel_pos, frame_shape)
                    bit_len = min(bit_len, message_len)
                else:
                    min_pixel_pos = np.unravel_index(0, frame_shape)
                    bit_len = max_bit_in_frame
                    remainder_message_len = message_len - (frame_pos * max_bit_in_frame)
                    bit_len = min(bit_len, remainder_message_len)

                pixel_random_sequence_in_frame = RandomUtil.get_random_sequence(
                    min_pixel_pos, frame_shape, bit_len, random.random())
                for location, idx in pixel_random_sequence_in_frame:
                    location = tuple([frame_pos] + [i for i in location])
                    temp_sequence.append((location, idx + (frame_pos * max_bit_in_frame)))

            return temp_sequence

        if not is_frame_seq and is_pixel_seq:
            pixel_random_sequence_in_frame = RandomUtil.get_random_sequence((0, ), video_shape[0],
                                                                            frame_needed,
                                                                            random.random())
            temp_sequence = []
            for idx, ((frame_pos, ), padding) in enumerate(pixel_random_sequence_in_frame):
                if frame_pos == 0:
                    # first_frame
                    min_pixel_idx = np.ravel_multi_index(min_pos, video_shape)  # for metadata
                else:
                    min_pixel_idx = 0

                remainder_message_len = message_len - (idx * max_bit_in_frame)
                bit_len_in_frame = min(max_bit_in_frame, remainder_message_len)
                for pixel_idx in range(min_pixel_idx, bit_len_in_frame):
                    location = tuple([frame_pos] +
                                     [i for i in np.unravel_index(pixel_idx, frame_shape)])
                    temp_sequence.append((location, padding + pixel_idx))
            return temp_sequence

    @staticmethod
    def get_conceal_option() -> List[ConfigParam]:
        return [
            RadioParam('Frame Arrangement', {
                FRAME_SEQ: 'Sequential',
                FRAME_RANDOM: 'Random'
            }),
            RadioParam('Pixel Arrangement', {
                PIXEL_SEQ: 'Sequential',
                PIXEL_RANDOM: 'Random'
            })
        ]

    @staticmethod
    def get_supported_extensions() -> List[str]:
        return ['avi']

    def check_file_supported(self, filepath: str) -> bool:
        vid_cap = cv2.VideoCapture(filepath)
        is_opened = vid_cap.isOpened()
        vid_cap.release()
        return filepath.endswith('.avi') and is_opened

    @staticmethod
    def get_max_message(file_path: str, option: List[Union[str, float]]) -> int:
        video_reader = skvideo.io.FFmpegReader(file_path)
        shape = video_reader.getShape()
        max_cover_size = int(np.prod(shape))
        len_metadata = FileUtil.get_metadata_len(max_cover_size) + len(
            VideoEngine.get_conceal_option()) + 1  # 2 bit for 2 option + 1 for encryption
        return (max_cover_size - math.ceil(len_metadata / 8)) // 8

    @staticmethod
    def conceal(file_in_path: str, message_file_path: str, file_out_path: str, encryption_key: str,
                config: List[Union[str, float]]) -> None:
        def psnr(original, edited):
            mse = np.mean((original - edited)**2)
            if mse == 0:
                return 100
            return 20 * np.log10(255 / np.sqrt(mse))

        is_encrypt, is_frame_seq, is_pixel_seq = VideoEngine.parse_config(config)
        VideoEngine.check_key(encryption_key)
        _, ext = os.path.basename(message_file_path).split('.')

        video_reader = skvideo.io.FFmpegReader(file_in_path)
        video_writer = skvideo.io.FFmpegWriter(
            file_out_path + video_reader.extension,
            outputdict={
                '-vcodec': 'libx264rgb',  # use the h.264 codec
                '-crf': '0',
                '-preset': 'veryslow',
            })

        video_shape = video_reader.getShape()
        max_cover_size = int(np.prod(video_shape))

        max_message_size = VideoEngine.get_max_message(file_in_path, config) * 8  # in bit
        message_len = os.path.getsize(message_file_path) * 8  # in bit

        if message_len > max_message_size:
            raise ValueError(f'File too big, max size={max_message_size}, got {message_len}')

        metadata = FileUtil.gen_metadata(message_len, max_cover_size, ext)

        metadata_len = FileUtil.get_metadata_len(max_cover_size) + len(
            VideoEngine.get_conceal_option()) + 1  # 2 bit for 2 option + 1 for encryption

        min_pos = np.unravel_index(metadata_len, video_shape)
        seed = RandomUtil.get_seed_from_string(encryption_key)
        pixel_sequence = VideoEngine.generate_sequence(config, min_pos, video_shape, message_len,
                                                       seed)

        metadata.append(0)
        used_message_file_path = message_file_path
        if is_encrypt:
            metadata[-1] = 1
            used_message_file_path = VideoEngine.encrypt(message_file_path, encryption_key)

        metadata.append(1) if is_frame_seq else metadata.append(0)
        metadata.append(1) if is_pixel_seq else metadata.append(0)

        current_video_frame = 0
        random_pixel_sequence_idx = 0
        pixel_location_in_video, bit_idx_in_message = pixel_sequence[random_pixel_sequence_idx]
        list_of_psnr = []
        with open(used_message_file_path, 'rb') as message_handle:
            for read_frame in video_reader.nextFrame():
                frame = read_frame.copy()
                original_frame = frame.copy()

                if current_video_frame == 0:
                    #  first frame, insert meta data
                    for i in range(len(metadata)):
                        metadata_bit = metadata[i]
                        # TODO generalize this
                        it, idx = divmod(i, 3)
                        location = 3 * it + (2 - idx)
                        frame_byte = frame[np.unravel_index(location, video_shape)[1:]]
                        frame[np.unravel_index(
                            location, video_shape)[1:]] = (frame_byte & 0xFE) | metadata_bit

                pixel_frame_location = pixel_location_in_video[0]
                while pixel_frame_location == current_video_frame:
                    byte_location_in_message, bit_location_in_byte = divmod(bit_idx_in_message, 8)
                    message_handle.seek(byte_location_in_message)
                    message_byte = message_handle.read(1)  # read 1 byte
                    message_bit = ord(message_byte) >> (
                            7 - bit_location_in_byte) & 1  # 0 location is from left

                    pixel_location_in_frame = VideoEngine.rgb_to_bgr(pixel_location_in_video[1:])
                    frame[pixel_location_in_frame] &= 254
                    frame[pixel_location_in_frame] |= message_bit

                    random_pixel_sequence_idx += 1
                    if random_pixel_sequence_idx >= len(pixel_sequence):
                        # all bit in message have been embedded
                        break

                    pixel_location_in_video, bit_idx_in_message = pixel_sequence[
                        random_pixel_sequence_idx]
                    pixel_frame_location = pixel_location_in_video[0]

                video_writer.writeFrame(frame)
                current_video_frame += 1
                list_of_psnr.append(psnr(original_frame, frame))

        video_reader.close() # close reader
        video_writer.close()  # close the writer
        return file_out_path + video_reader.extension, np.mean(list_of_psnr)

    @staticmethod
    def extract(
            file_in_path: str,
            extract_file_path: str,
            encryption_key: str,
            config: List[Union[str, float, bool]],
    ) -> str:
        VideoEngine.check_key(encryption_key)

        filename, ext = os.path.basename(file_in_path).split('.')
        if ext.lower() not in VideoEngine.get_supported_extensions():
            raise OSError(f'Extension .{ext} not supported')

        video_capture = cv2.VideoCapture(file_in_path)  # getting first frame for metadata
        video_reader = skvideo.io.FFmpegReader(file_in_path)
        assert video_capture.isOpened(), "Cannot open cover video"
        ret_status, frame = video_capture.read()  # get first frame
        assert ret_status, "Cannot open cover video"

        video_shape = video_reader.getShape()
        max_cover_size = int(np.prod(video_shape))

        metadata_len = FileUtil.get_metadata_len(max_cover_size) + len(
            VideoEngine.get_conceal_option()) + 1
        frame_header = bytearray(list(frame.ravel()[:metadata_len]))

        metadata = []
        for i in range(metadata_len):
            metadata.append(frame_header[i] & 1)

        is_pixel_seq = True if metadata.pop() == 1 else False
        is_frame_seq = True if metadata.pop() == 1 else False
        is_encrypt = True if metadata.pop() == 1 else False

        message_len, ext = FileUtil.extract_metadata(metadata)  # message_len in bit

        min_pos = np.unravel_index(metadata_len, video_shape)

        config = [''] * 3
        config[1] = FRAME_SEQ if is_frame_seq else FRAME_RANDOM
        config[2] = PIXEL_SEQ if is_pixel_seq else PIXEL_RANDOM

        seed = RandomUtil.get_seed_from_string(encryption_key)
        pixel_sequence = VideoEngine.generate_sequence(config, min_pos, video_shape, message_len,
                                                       seed)

        temp_file = FileUtil.get_temp_out_name()

        current_video_frame = 0
        random_pixel_sequence_idx = 0
        pixel_location_in_video, bit_idx_in_message = pixel_sequence[random_pixel_sequence_idx]
        with open(temp_file, 'wb+') as message_output_handler:
            message_output_handler.write(bytes([0] * (message_len // 8)))
            for read_frame in video_reader.nextFrame():
                frame = read_frame.copy()

                pixel_frame_location = pixel_location_in_video[0]
                while pixel_frame_location == current_video_frame:
                    byte_location_in_message, bit_location_in_byte = divmod(bit_idx_in_message, 8)

                    pixel_location_in_frame = VideoEngine.rgb_to_bgr(pixel_location_in_video[1:])
                    message_bit = frame[pixel_location_in_frame] & 1

                    message_output_handler.seek(byte_location_in_message)
                    message_byte = message_output_handler.read(1)  # read 1 byte
                    temp_byte = bytes([message_bit << (7 - bit_location_in_byte)])
                    message_output_handler.seek(byte_location_in_message)
                    message_output_handler.write(bytes([message_byte[0] | temp_byte[0]]))

                    random_pixel_sequence_idx += 1
                    if random_pixel_sequence_idx >= len(pixel_sequence):
                        # all bit in message have been embedded
                        break

                    pixel_location_in_video, bit_idx_in_message = pixel_sequence[
                        random_pixel_sequence_idx]
                    pixel_frame_location = pixel_location_in_video[0]

                current_video_frame += 1

                if random_pixel_sequence_idx >= len(pixel_sequence):
                    # all bit in message have been embedded
                    break

        video_reader.close()
        video_capture.release()

        temp_file_path = temp_file
        if is_encrypt:
            temp_file_path = VideoEngine.decrypt(temp_file, encryption_key)
        FileUtil.move_file(temp_file_path, extract_file_path + '.' + ext)

        return extract_file_path + '.' + ext
