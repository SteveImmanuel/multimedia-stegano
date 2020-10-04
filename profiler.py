import time
import os
import shutil

from stegano.engine import AudioEngine
from stegano.engine import VideoEngine
from stegano.engine import ImageEngine
from stegano.engine.constants import *
from stegano.util.file_util import FileUtil

MESSAGE_DIR = 'test_data/message'
message_type = ['txt', 'docx', 'pdf', 'xlsx']
message_size = ['small', 'big']
message_paths = [f'{mtype}_{msize}.{mtype}' for mtype in message_type for msize in message_size]

COVER_DIR = 'test_data/cover'
cover_type = ['audio']  #TODO: add image and video cover name, same as in the test_data/cover
cover_ext = {'audio': 'wav', 'video': 'avi', 'image': 'png'}
cover_paths = [f'{ctype}.{cover_ext[ctype]}' for ctype in cover_type]

if os.path.exists('test_result'):
    shutil.rmtree('test_result')
os.makedirs('test_result/concealed')
os.makedirs('test_result/extracted')

for cpath in cover_paths:
    for mpath in message_paths:
        print('==============Benchmark Result==============')
        print('Cover path:', cpath)
        print('Message path:', mpath)
        print('Message size:', os.path.getsize(f'{MESSAGE_DIR}/{mpath}'), 'bytes')

        temp_path = FileUtil.get_temp_out_name()
        elapsed = -time.time()
        out_path, psnr = AudioEngine.conceal(f'{COVER_DIR}/{cpath}', f'{MESSAGE_DIR}/{mpath}',
                                             temp_path, 'test123', [False, CONCEAL_SEQ])
        elapsed += time.time()
        message_name = mpath.split('.')[0]
        real_out_path = f'test_result/concealed/{message_name}_{cpath}'
        FileUtil.move_file(out_path, real_out_path)
        print('====Conceal Result====')
        print('Time elapsed:', elapsed, 's')
        print('Output path:', real_out_path)
        print('PSNR:', psnr)

        temp_path = FileUtil.get_temp_out_name()
        elapsed = -time.time()
        res_path = AudioEngine.extract(real_out_path, temp_path, 'test123', [False, CONCEAL_SEQ])
        elapsed += time.time()
        cover_name = cpath.split('.')[0]
        out_path = f'test_result/extracted/{cover_name}_{mpath}'
        FileUtil.move_file(res_path, out_path)
        print('====Extract Result====')
        print('Time elapsed:', elapsed, 's')
        print('Output path:', out_path)
        print('============================================')
        print()
