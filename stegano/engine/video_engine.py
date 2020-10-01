import math
import os
import random
from typing import Dict, List

import cv2
import numpy as np
import skvideo.io
from stegano.engine.base_engine import BaseEngine
from stegano.util.file_util import FileUtil
from stegano.util.random_util import RandomUtil

import datetime


class VideoEngine(BaseEngine):
    def check_key(self, key: str):
        s = len(key)
        assert s >= 1 and s <= 25

    @staticmethod
    def get_conceal_option(self) -> List[Dict[str, str]]:
        return [{
            'enc': 'dengan enkripsi',
            'nenc': 'tanpa enkripsi'
        }, {
            'f_seq': 'frame sekuensial',
            'f_rand': 'frame acak'
        }, {
            'p_seq': 'pixel-pixel sekuensial',
            'p_rand': 'pixel-pixel acak'
        }]

    @staticmethod
    def get_supported_extensions(self) -> List[str]:
        return ['avi']

    def check_file_supported(self, filepath: str) -> bool:
        vid_cap = cv2.VideoCapture(filepath)
        is_opened = vid_cap.isOpened()
        vid_cap.release()
        return filepath.endswith('.avi') and is_opened

    def get_max_message(self, filepath: str) -> int:
        vid_cap = cv2.VideoCapture(filepath)

        if not vid_cap.isOpened():
            return 0

        ret, frame = vid_cap.read()
        if not ret:
            return 0
        frame_dim = frame.shape
        frame_count = vid_cap.get(7)
        max_stego_size = np.prod(frame_dim) * frame_count
        meta_data_len = FileUtil.get_metadata_len(max_stego_size)
        meta_data_len += 3  # 3 bit for 3 option

        max_message_size = max_stego_size - math.ceil(meta_data_len / 8)

        vid_cap.release()
        return max_message_size

    def _conceal(self, file_in_path: str, secret_file_path: str, file_out_path: str,
                 encryption_key: str, config: List[str]):
        start = datetime.datetime.now()
        self.check_key(encryption_key)

        input_handle = open(secret_file_path, 'rb')
        input_handle.seek(0, os.SEEK_END)
        file_size = input_handle.tell()

        writer = skvideo.io.FFmpegWriter(
            file_out_path,
            outputdict={
                '-vcodec': 'libx264',  #use the h.264 codec
                '-crf': '0',
                '-preset': 'veryslow',
                '-r': '30'
            })
        print(file_size)

        vid_cap = cv2.VideoCapture(file_in_path)
        assert vid_cap.isOpened()

        fourcc = cv2.VideoWriter_fourcc(*'FFV1')
        # out_writer = cv2.VideoWriter(file_out_path, fourcc, vid_cap.get(5),
        #                              (int(vid_cap.get(3)), int(vid_cap.get(4))), True)

        ret, frame = vid_cap.read()
        assert ret

        frame_dim = frame.shape
        frame_count = vid_cap.get(7)
        max_stego_size = np.prod(frame_dim) * frame_count
        meta_data_len = FileUtil.get_metadata_len(max_stego_size)
        meta_data_len += 3  # 3 bit for 3 option
        ext = file_in_path.split('.')[-1]

        shape = [int(frame_count)] + [i for i in frame_dim]
        min_pos = np.unravel_index(meta_data_len, shape)

        meta_data = FileUtil.gen_metadata(file_size, max_stego_size, ext)
        seed = RandomUtil.get_seed_from_string(encryption_key)
        sequence = RandomUtil.get_random_sequence(min_pos, shape, file_size * 8, seed)
        # sequence = [(np.unravel_index(i, shape), i) for i in range(file_size * 8)]

        vid_cap.set(1, 0)  # set next frame to 0
        current_frame = 0
        squence_idx = 0
        pos, idx = sequence[squence_idx]
        count = 0
        while vid_cap.isOpened():
            ret, frame = vid_cap.read()
            if not ret:  # end file
                break

            # TODO handle meta data

            frame_pos = pos[0]
            while frame_pos == current_frame:

                byte_pos, bit_pos = divmod(idx, 8)
                input_handle.seek(byte_pos)
                the_byte = input_handle.read(1)
                the_bit = ord(the_byte) >> (7 - bit_pos) & 1

                frame[pos[1:]] &= 254
                frame[pos[1:]] |= the_bit

                squence_idx += 1
                count += 1
                if squence_idx >= len(sequence):
                    break

                pos, idx = sequence[squence_idx]
                frame_pos = pos[0]

            # out_writer.write(frame)
            writer.writeFrame(frame[:, :, ::-1])
            current_frame += 1

        writer.close()  #close the writer
        vid_cap.release()
        # out_writer.release()
        print(datetime.datetime.now() - start)

    def _extract(
        self,
        file_in_path: str,
        extract_file_path: str,
        encryption_key: str,
    ):
        start = datetime.datetime.now()
        self.check_key(encryption_key)

        output_handler = open(extract_file_path, 'wb')
        output_handler.seek(0, os.SEEK_END)
        file_size = 11

        vid_cap = cv2.VideoCapture(file_in_path)
        assert vid_cap.isOpened()

        ret, frame = vid_cap.read()
        assert ret

        frame_dim = frame.shape
        frame_count = vid_cap.get(7)
        max_stego_size = np.prod(frame_dim) * frame_count
        meta_data_len = FileUtil.get_metadata_len(max_stego_size)
        meta_data_len += 3  # 3 bit for 3 option
        ext = file_in_path.split('.')[-1]

        shape = [int(frame_count)] + [i for i in frame_dim]
        min_pos = np.unravel_index(meta_data_len, shape)

        meta_data = FileUtil.gen_metadata(file_size, max_stego_size, ext)
        seed = RandomUtil.get_seed_from_string(encryption_key)
        sequence = RandomUtil.get_random_sequence(min_pos, shape, file_size * 8, seed)
        # sequence = [(np.unravel_index(i, shape), i) for i in range(file_size * 8)]

        # print(sequence)
        sequence.sort(key=lambda val: val[1])

        the_byte = 0
        assign_count = 0
        count = 0
        # print(sequence)
        for pos, idx in sequence:
            # print(pos, idx)
            frame_pos = pos[0]
            vid_cap.set(1, frame_pos)  # set next frame
            ret, frame = vid_cap.read()

            if not ret:
                # error accure not reach end of sequence
                print('an error occure while extract')
                break

            the_bit = frame[pos[1:]] & 1
            # print(the_bit, idx)
            the_byte <<= 1
            the_byte |= the_bit
            assign_count += 1

            if assign_count == 8:
                count += 1
                print(bytes([the_byte]))
                output_handler.write(bytes([the_byte]))
                # print('write')
                the_byte = 0
                assign_count = 0

        print(count)

        vid_cap.release()
        print(datetime.datetime.now() - start)
