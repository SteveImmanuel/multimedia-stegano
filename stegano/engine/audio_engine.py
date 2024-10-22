import os
import wave
import math
import subprocess

from typing import List, Union

from stegano.engine import BaseEngine
from stegano.engine.constants import *
from stegano.util.file_util import FileUtil
from stegano.util.random_util import RandomUtil
from stegano.gui.config_param import RadioParam, ConfigParam

FRAME_SIZE = 500000


class AudioEngine(BaseEngine):
    def __init__(self):
        super(AudioEngine, self).__init__()

    @staticmethod
    def conceal(
        file_in_path: str,
        message_file_path: str,
        file_out_path: str,
        encryption_key: str,
        config: List[str],
    ) -> (str, float):
        is_encrypt, is_random = AudioEngine.parse_config(config)
        _, ext = os.path.basename(message_file_path).split('.')
        file_in_ext = os.path.splitext(file_in_path)[-1].lower()
        full_out_path = file_out_path + file_in_ext

        if is_encrypt:
            real_message_path = AudioEngine.encrypt(message_file_path, encryption_key)
        else:
            real_message_path = message_file_path

        cover_obj = wave.open(file_in_path, 'rb')
        secret_msg_len = os.path.getsize(real_message_path) * 8  # in bit
        max_file_size = cover_obj.getnframes() * 4  # in bit

        metadata = FileUtil.gen_metadata(secret_msg_len, max_file_size, ext)
        metadata.append(1) if is_encrypt else metadata.append(0)
        if is_random:
            metadata.append(1)
            seed = RandomUtil.get_seed_from_string(encryption_key)
            sequence_index = RandomUtil.get_random_sequence((len(metadata), ), (max_file_size, ),
                                                            secret_msg_len, seed)
            sequence_index = list(map(lambda x: (x[0][0], x[1]), sequence_index))
        else:
            metadata.append(0)
            sequence_index = [(i + len(metadata), i) for i in range(secret_msg_len)]

        total_secret_size = secret_msg_len + len(metadata)
        if total_secret_size > max_file_size:
            raise ValueError(f'File too big, max size={max_file_size}, got {total_secret_size}')

        frame_size = min(FRAME_SIZE, cover_obj.getnframes())  # 1 frame = 4 bytes
        frame_bytes = bytearray(list(cover_obj.readframes(frame_size)))

        with wave.open(full_out_path, 'wb') as stego:
            stego.setparams(cover_obj.getparams())

            with open(real_message_path, 'rb') as secret:
                # set header, format, etc
                for i in range(len(metadata)):
                    bit = metadata[i]
                    frame_bytes[i] = (frame_bytes[i] & 254) | bit

                # read chunk by chunk and flush the result
                offset = 1
                i = 0
                while (i < len(sequence_index)):
                    idx_stego, idx_secret = sequence_index[i]

                    if idx_stego < frame_size * 4 * offset:
                        idx_byte = idx_secret // 8
                        secret.seek(idx_byte)
                        raw = secret.read(1)

                        bit = int(bin(ord(raw)).lstrip('0b').rjust(8, '0')[idx_secret % 8])
                        idx_offset = idx_stego % (frame_size * 4)
                        frame_bytes[idx_offset] = (frame_bytes[idx_offset] & 254) | bit
                        i += 1

                    else:
                        stego.writeframes(frame_bytes)
                        frame_bytes = bytearray(list(cover_obj.readframes(frame_size)))
                        offset += 1

                # in case reading has not reached eof
                while (cover_obj.tell() < cover_obj.getnframes()):
                    stego.writeframes(frame_bytes)
                    frame_bytes = bytearray(list(cover_obj.readframes(frame_size)))

                stego.writeframes(frame_bytes)
        cover_obj.close()

        psnr = AudioEngine.count_psnr(full_out_path, file_in_path)
        return (full_out_path, psnr)

    @staticmethod
    def extract(
        file_in_path: str,
        extract_file_path: str,
        encryption_key: str,
        config: List[Union[str, float, bool]],
    ) -> str:

        filename, _ = os.path.basename(file_in_path).split('.')

        stego_obj = wave.open(file_in_path, 'rb')
        max_file_size = stego_obj.getnframes() * 4
        metadata_len = FileUtil.get_metadata_len(max_file_size) + 2

        frame_bytes = bytearray(list(stego_obj.readframes(metadata_len)))
        metadata = []
        for i in range(metadata_len):
            metadata.append(frame_bytes[i] & 1)
        metadata_len = len(metadata)

        is_random = True if metadata.pop() == 1 else False
        is_encrypt = True if metadata.pop() == 1 else False
        secret_msg_len, ext = FileUtil.extract_metadata(metadata)

        if is_random:
            seed = RandomUtil.get_seed_from_string(encryption_key)
            sequence_index = RandomUtil.get_random_sequence((metadata_len, ), (max_file_size, ),
                                                            secret_msg_len, seed)
            sequence_index = list(map(lambda x: (x[1], x[0][0]), sequence_index))
            sequence_index.sort()
            sequence_index = list(map(lambda x: x[1], sequence_index))

        else:
            sequence_index = [i + metadata_len for i in range(secret_msg_len)]

        temp_file = FileUtil.get_temp_out_name()
        with open(temp_file, 'wb') as secret:
            i = 0
            temp_byte = []
            for idx_stego in sequence_index:
                byte = AudioEngine.get_ith_byte(stego_obj, idx_stego)
                temp_byte.append(byte & 1)
                i += 1

                if i == 8:
                    i = 0
                    byte = bytes([FileUtil.binary_to_dec(temp_byte)])
                    secret.write(byte)
                    temp_byte.clear()
        stego_obj.close()

        if is_encrypt:
            out_path = AudioEngine.decrypt(temp_file, encryption_key)
        else:
            out_path = temp_file
        full_extract_path = f'{extract_file_path}.{ext}'
        FileUtil.move_file(out_path, full_extract_path)

        return full_extract_path

    @staticmethod
    def count_psnr(stego_filepath: str, original_filepath: str) -> float:
        stego = wave.open(stego_filepath, 'rb')
        original = wave.open(original_filepath, 'rb')

        cur_max = 0
        total_len = 0
        mse = 0.0
        frame_size = min(FRAME_SIZE, original.getnframes())
        while (original.tell() < original.getnframes()):
            stego_frames = list(stego.readframes(frame_size))
            original_frames = list(original.readframes(frame_size))

            total_len += len(original_frames)
            cur_max = max(cur_max, max(stego_frames))
            for i in range(len(original_frames)):
                mse += (stego_frames[i] - original_frames[i])**2
        mse /= total_len

        return 20 * math.log(cur_max, 10) - 10 * math.log(mse, 10)

    @staticmethod
    def get_ith_byte(stego_obj, i: int) -> int:
        stego_obj.setpos(i // 4)
        frame_bytes = stego_obj.readframes(1)
        byte = frame_bytes[i % 4]
        return byte

    @staticmethod
    def get_conceal_option() -> List[ConfigParam]:
        return [RadioParam('Order', {CONCEAL_RANDOM: 'Sequential', CONCEAL_SEQ: 'Random'})]

    @staticmethod
    def parse_config(config: List[str]) -> List[bool]:
        res = [None] * 2
        res[0] = config[0]
        res[1] = True if config[1] == CONCEAL_RANDOM else False
        return res

    @staticmethod
    def get_supported_extensions() -> List[str]:
        return ['wav']

    @staticmethod
    def check_file_supported(filepath: str) -> bool:
        filename, ext = os.path.basename(filepath).split('.')
        return ext.lower() == 'wav'

    @staticmethod
    def get_max_message(file_path: str, option: List[Union[str, float]]) -> int:
        cover_obj = wave.open(file_path, 'rb')
        return cover_obj.getnframes() * 4 // 8

    @staticmethod
    def convert_to_wav(file_in_path: str, file_out_path: str) -> None:
        subprocess.call(['ffmpeg', '-loglevel', 'quiet', '-i', file_in_path, file_out_path])


if __name__ == "__main__":
    base_path = '/home/steve/Git/multimedia-stegano/'
    res = AudioEngine.conceal(f'{base_path}/new.wav', f'{base_path}/a.txt',
                              f'{base_path}/testbuffer.wav', 'test123', [True, CONCEAL_RANDOM])
    print(res)
    res = AudioEngine.extract(f'{base_path}/testbuffer.wav', 'dec.txt', 'test123')
    print(res)
