import time
from typing import List, Dict, Union

from stegano.engine import BaseEngine
from stegano.gui.config_param import ConfigParam, RadioParam, FloatParam


class DummyEngine(BaseEngine):
    def __init__(self):
        super(DummyEngine, self).__init__()

    @staticmethod
    def get_conceal_option() -> List[ConfigParam]:
        return [
            RadioParam('radio', {
                'a': 'Option A',
                'b': 'Option B'
            }),
            FloatParam('float', 0.1, 0.5)
        ]

    @staticmethod
    def get_extract_option() -> List[ConfigParam]:
        return [RadioParam('radio', {'a': 'Option A', 'b': 'Option B'})]

    @staticmethod
    def get_supported_extensions() -> List[str]:
        return ['txt']

    @staticmethod
    def check_file_supported(file_path: str) -> bool:
        # File must starts with text and ends with txt
        return file_path.endswith('txt') and file_path.startswith('text')

    @staticmethod
    def get_max_message(file_path: str, option: List[Union[str, float, bool]]) -> int:
        return int(100000 * option[2])

    @staticmethod
    def conceal(
        file_in_path: str,
        secret_file_path: str,
        file_out_path: str,
        encryption_key: str,
        config: List[Union[str, float, bool]],
    ) -> str:
        print('Doing concealment with param {}'.format(config))
        time.sleep(10)
        with open(file_out_path, 'w') as file:
            file.write('Hello, this is test')
        print('Done concealment')
        return secret_file_path + '.dummy'

    @staticmethod
    def extract(
        file_in_path: str,
        extract_file_path: str,
        encryption_key: str,
        config: List[Union[str, float, bool]],
    ) -> str:
        print('Doing extract with param {} {}'.format(encryption_key, config))
        time.sleep(5)
        with open(extract_file_path, 'w') as file:
            file.write('Hello, this is extracted test')
        print('Done extracting')
        return extract_file_path + '.result'
