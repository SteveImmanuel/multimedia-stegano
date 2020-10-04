import time
import os
import shutil

from stegano.engine import AudioEngine
from stegano.engine import VideoEngine
from stegano.engine import ImageEngine
from stegano.engine import EngineFactory
from stegano.engine.constants import *
from stegano.util.file_util import FileUtil

MESSAGE_DIR = 'test_data/message'
message_type = ['txt', 'docx', 'pdf', 'xlsx']
message_size = ['small', 'big']
message_paths = [f'{mtype}_{msize}.{mtype}' for mtype in message_type for msize in message_size]

COVER_DIR = 'test_data/cover'
cover_type = ['audio']  #TODO: add image and video cover name, same as in the test_data/cover
cover_ext = {'audio': 'wav', 'video': 'avi', 'image_png': 'png', 'image_bmp': 'bmp'}
cover_paths = [f'{ctype}.{cover_ext[ctype]}' for ctype in cover_type]

if os.path.exists('test_result'):
    shutil.rmtree('test_result')
os.makedirs('test_result/concealed')
os.makedirs('test_result/extracted')

engine_conceal_param = [True, CONCEAL_LSB, CONCEAL_RANDOM]
engine_extract_param = [True, CONCEAL_LSB]

for cpath in cover_paths:
    for mpath in message_paths:
        print(f'==============Benchmark Result for {mpath}==============')
        print('Cover path:', cpath)
        print('Message path:', mpath)
        print('Message size:', os.path.getsize(f'{MESSAGE_DIR}/{mpath}'), 'bytes')

        engine_type = EngineFactory.get_engine_to_handle_file(cpath)
        engine = EngineFactory.get_engine_class(engine_type)

        temp_path = FileUtil.get_temp_out_name()
        elapsed = -time.time()
        out_path, psnr = engine.conceal(f'{COVER_DIR}/{cpath}', f'{MESSAGE_DIR}/{mpath}', temp_path,
                                        'test123', engine_conceal_param)
        elapsed += time.time()
        message_name = mpath.split('.')[0]
        real_out_path = f'test_result/concealed/{message_name}_{cpath}'
        FileUtil.move_file(out_path, real_out_path)
        print('PSNR:', '{:.2f}'.format(psnr), 'dB')
        print('Conceal:', '{:.2f}'.format(elapsed), 's')

        temp_path = FileUtil.get_temp_out_name()
        elapsed = -time.time()
        res_path = engine.extract(real_out_path, temp_path, 'test123', engine_extract_param)
        elapsed += time.time()
        cover_name = cpath.split('.')[0]
        out_path = f'test_result/extracted/{cover_name}_{mpath}'
        FileUtil.move_file(res_path, out_path)
        print('Extract:', '{:.2f}'.format(elapsed), 's')
        print()
