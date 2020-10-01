import os
import wave

from typing import List, Dict

from stegano.engine.base_engine import BaseEngine
from stegano.util.file_util import FileUtil
from stegano.util.random_util import RandomUtil

FRAME_SIZE = 500000


class AudioEngine(BaseEngine):
    def __init__(self):
        super(AudioEngine, self).__init__()

    def _conceal(self, file_in_path: str, secret_file_path: str, file_out_path: str):
        self.is_encrypt = True
        self.is_random = True
        key = 'test123'

        #TODO: convert to wav if file format is wrong or raise exception, await further development
        filename, ext = os.path.basename(file_in_path).split('.')
        if ext.lower() != 'wav':
            raise OSError(f'Extension must be .wav, got .{ext}')

        cover_obj = wave.open(file_in_path, 'rb')
        secret_msg_len = os.path.getsize(secret_file_path) * 8  #in bit
        max_file_size = cover_obj.getnframes() * 4  #in bit

        metadata = FileUtil.gen_metadata(secret_msg_len, max_file_size, ext)
        metadata.append(1) if self.is_encrypt else metadata.append(0)
        if self.is_random:
            metadata.append(1)
            seed = RandomUtil.get_seed_from_string(key)
            sequence_index = RandomUtil.get_random_sequence((len(metadata), ), (max_file_size, ),
                                                            secret_msg_len, seed)
            sequence_index = list(map(lambda x: (x[0][0], x[1]), sequence_index))
        else:
            metadata.append(0)
            sequence_index = [(i + len(metadata), i) for i in range(secret_msg_len)]

        total_secret_size = secret_msg_len + len(metadata)
        if total_secret_size > max_file_size:
            raise ValueError(f'File too big, max size={max_file_size}, got {total_secret_size}')

        frame_size = min(FRAME_SIZE, cover_obj.getnframes())  #1 frame = 4 bytes
        frame_bytes = bytearray(list(cover_obj.readframes(frame_size)))

        with wave.open(file_out_path, 'wb') as stego:
            stego.setparams(cover_obj.getparams())

            with open(secret_file_path, 'rb') as secret:
                #set header, format, etc
                for i in range(len(metadata)):
                    bit = metadata[i]
                    frame_bytes[i] = (frame_bytes[i] & 254) | bit

                #read chunk by chunk and flush the result
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

                #in case reading has not reached eof
                while (cover_obj.tell() < cover_obj.getnframes()):
                    stego.writeframes(frame_bytes)
                    frame_bytes = bytearray(list(cover_obj.readframes(frame_size)))

                stego.writeframes(frame_bytes)
        cover_obj.close()

    def _extract(self, file_in_path: str, extract_file_path: str):
        key = 'test123'

        filename, ext = os.path.basename(file_in_path).split('.')
        if ext.lower() != 'wav':
            raise OSError(f'Extension must be .wav, got .{ext}')

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
            seed = RandomUtil.get_seed_from_string(key)
            sequence_index = RandomUtil.get_random_sequence((metadata_len, ), (max_file_size, ),
                                                            secret_msg_len, seed)
            sequence_index = list(map(lambda x: (x[1], x[0][0]), sequence_index))
            sequence_index.sort()
            sequence_index = list(map(lambda x: x[1], sequence_index))

        else:
            sequence_index = [i + metadata_len for i in range(secret_msg_len)]

        with open(extract_file_path, 'wb') as secret:
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

    @staticmethod
    def get_ith_byte(stego_obj, i: int) -> int:
        stego_obj.setpos(i // 4)
        frame_bytes = stego_obj.readframes(1)
        byte = frame_bytes[i % 4]
        return byte

    @staticmethod
    def get_conceal_option(self) -> List[Dict[str, str]]:
        return [{'a': 'urutan a', 'b': 'urutan b'}, {'1': 'metode 1', '2': 'metode 2'}]

    @staticmethod
    def get_supported_extensions(self) -> List[str]:
        return ['wav']

    def check_file_supported(self, filepath: str) -> bool:
        filename, ext = os.path.basename(filepath).split('.')
        return ext.lower() == 'wav'

    def get_max_message(self, filepath: str) -> int:
        cover_obj = wave.open(filepath, 'rb')
        return cover_obj.getnframes() * 4 // 8


if __name__ == "__main__":
    audio_engine = AudioEngine()
    base_path = '/home/steve/Git/multimedia-stegano/stegano/engine'
    audio_engine.conceal(f'{base_path}/dual3.wav', f'{base_path}/sec.txt',
                         f'{base_path}/testbuffer.wav')
    audio_engine.extract(f'{base_path}/testbuffer.wav', 'dec.txt')
