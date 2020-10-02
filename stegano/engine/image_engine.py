from typing import List, Dict, Union

from stegano.engine import BaseEngine
from stegano.gui.config_param import RadioParam, ConfigParam, FloatParam

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
            RadioParam('Method', {CONCEAL_BPCS: 'BPCS', CONCEAL_LSB: 'LSB'}),
            RadioParam('Order', {CONCEAL_RANDOM: 'Random', CONCEAL_SEQ: 'Sequential'}),
            FloatParam('Threshold for BPCS', 0.1, 0.3)
        ]

    @staticmethod
    def get_supported_extensions() -> List[str]:
        return ['png']

    @staticmethod
    def check_file_supported(filepath: str) -> bool:
        return True

    @staticmethod
    def get_max_message(file_path: str, option: List[Union[str, float]]) -> int:
        return 1

    @staticmethod
    def conceal(
            file_in_path: str,
            secret_file_path: str,
            file_out_path: str,
            encryption_key: str,
            config: List[str],
    ) -> None:
        pass

    @staticmethod
    def extract(file_in_path: str, extract_file_path: str, encryption_key: str) -> None:
        super().extract(file_in_path, extract_file_path, encryption_key)
