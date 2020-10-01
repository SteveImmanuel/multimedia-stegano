import os
import wave
import math

from typing import List, Dict

from stegano.engine.base_engine import BaseEngine
from stegano.util.file_util import FileUtil
from stegano.util.random_util import RandomUtil


class AudioEngine(BaseEngine):
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
        max_file_size = cover_obj.getnframes()
        print('total frames', max_file_size)
        print('secret msg len', secret_msg_len)

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
            sequence_index = list(enumerate(range(secret_msg_len)))

        total_secret_size = secret_msg_len + len(metadata)
        if total_secret_size > max_file_size:
            raise ValueError(f'File too big, max size={max_file_size}, got {total_secret_size}')

        temp = metadata.copy()
        print(temp)
        print(len(temp))
        is_random = True if temp.pop() == 1 else False
        is_encrypt = True if temp.pop() == 1 else False

        secret_msg_len, ext = FileUtil.extract_metadata(temp)

        print('israndom', is_random)
        print('isencrypt', is_encrypt)
        print('ext', ext)
        print('len', secret_msg_len)

        frame_bytes = bytearray(list(cover_obj.readframes(max_file_size)))
        chunk_size = min(500000, max_file_size)
        with wave.open(file_out_path, 'wb') as stego:
            stego.setparams(cover_obj.getparams())

            with open(secret_file_path, 'rb') as secret:
                # offset = 0
                #readframes returns 2 bytes
                # frame_bytes = bytearray(list(cover_obj.readframes(chunk_size)))
                for i in range(len(metadata)):
                    bit = metadata[i]
                    frame_bytes[i] = (frame_bytes[i] & 254) | bit

                print(sequence_index)
                for idx_stego, idx_secret in sequence_index:
                    idx_byte = idx_secret // 8
                    secret.seek(idx_byte)
                    raw = secret.read(1)
                    bit = int(bin(ord(raw)).lstrip('0b').rjust(8, '0')[idx_secret % 8])
                    frame_bytes[idx_stego] = (frame_bytes[idx_stego] & 254) | bit
                    # if offset + idx_stego < chunk_size:
                    #     secret.seek(idx_secret)
                    #     bit = secret.read(1)
                    #     frame_bytes[offset +
                    #                 idx_stego] = (frame_bytes[offset + idx_stego] & 254) | bit

                print(bin(frame_bytes[0]))
                stego.writeframes(frame_bytes)
        cover_obj.close()

    def _extract(self, file_in_path: str, extract_file_path: str):
        self.is_encrypt = True
        self.is_random = True
        key = 'test123'

        filename, ext = os.path.basename(file_in_path).split('.')
        if ext.lower() != 'wav':
            raise OSError(f'Extension must be .wav, got .{ext}')

        stego_obj = wave.open(file_in_path, 'rb')
        max_file_size = stego_obj.getnframes()
        metadata_len = FileUtil.get_metadata_len(max_file_size) + 2
        print('total frames', max_file_size)

        frame_bytes = bytearray(list(stego_obj.readframes(max_file_size)))
        print(bin(frame_bytes[0]))

        metadata = []
        for i in range(metadata_len):
            metadata.append(frame_bytes[i] & 1)
        metadata_len = len(metadata)
        print(metadata)
        print(len(metadata))
        is_random = True if metadata.pop() == 1 else False
        is_encrypt = True if metadata.pop() == 1 else False

        secret_msg_len, ext = FileUtil.extract_metadata(metadata)

        print('israndom', is_random)
        print('isencrypt', is_encrypt)
        print('ext', ext)
        print('len', secret_msg_len)

        seed = RandomUtil.get_seed_from_string(key)
        sequence_index = RandomUtil.get_random_sequence((metadata_len, ), (max_file_size, ),
                                                        secret_msg_len, seed)
        sequence_index = list(map(lambda x: (x[1], x[0][0]), sequence_index))
        sequence_index.sort()
        print(sequence_index)
        # if self.is_random:
        #     seed = RandomUtil.get_seed_from_string(key)
        #     sequence_index = RandomUtil.get_random_sequence(0, max_file_size, secret_msg_len, seed)
        #     sequence_index = list(map(lambda x: (x[1], x[0]), enumerate(sequence_index)))
        #     sequence_index.sort()
        # else:
        #     sequence_index = list(enumerate(range(secret_msg_len)))

        print('frame bytes len', len(frame_bytes))
        with open(extract_file_path, 'wb') as secret:
            i = 0
            temp_byte = []
            for idx_secret, idx_stego in sequence_index:
                temp_byte.append(frame_bytes[idx_stego] & 1)
                i += 1
                if i == 8:
                    i = 0
                    print(temp_byte)
                    byte = bytes([FileUtil.binary_to_dec(temp_byte)])
                    secret.write(byte)
                    temp_byte = []

    @staticmethod
    def get_frame_idx(bit: int):
        return math.ceil(math.ceil(bit // 8) // 2)

    @staticmethod
    def get_conceal_option(self) -> List[Dict[str, str]]:
        # Return list of dict, each dict value will be used ad the option label
        pass
        return self._get_conceal_option()

    @staticmethod
    def get_supported_extensions(self) -> List[str]:
        pass

    def check_file_supported(self, filepath: str) -> bool:
        pass

    def get_max_message(self, filepath: str) -> int:
        pass


if __name__ == "__main__":
    audio_engine = AudioEngine()
    base_path = '/home/steve/Git/multimedia-stegano/stegano/engine'
    audio_engine.conceal(f'{base_path}/dual3.wav', f'{base_path}/sec.txt',
                         f'{base_path}/test123.wav')

    audio_engine.extract(f'{base_path}/test123.wav', 'dec.txt')
