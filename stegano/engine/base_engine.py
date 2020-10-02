from abc import ABC, abstractmethod

from typing import List, Dict, Union

from stegano.gui.config_param import ConfigParam
from crypto.engine.extended_vigenere_engine import ExtendedVigenereEngine
from crypto.engine.data import *
from crypto.engine.key import *


class BaseEngine(ABC):
    encrypt_engine = ExtendedVigenereEngine()

    @staticmethod
    def conceal(
            file_in_path: str,
            secret_file_path: str,
            file_out_path: str,
            encryption_key: str,
            config: List[Union[str, float, bool]],
    ) -> None:
        pass

    @staticmethod
    def extract(
            file_in_path: str,
            extract_file_path: str,
            encryption_key: str,
    ) -> str:
        pass

    @staticmethod
    @abstractmethod
    def get_conceal_option() -> List[ConfigParam]:
        pass

    @staticmethod
    @abstractmethod
    def get_supported_extensions() -> List[str]:
        pass

    @staticmethod
    @abstractmethod
    def check_file_supported(file_path: str) -> bool:
        pass

    @staticmethod
    @abstractmethod
    def get_max_message(file_path: str, option: List[Union[str, float, bool]]) -> int:
        pass

    @staticmethod
    def encrypt(filepath: str, enc_key: str) -> str:
        data = Data(DataType.FILE, data=filepath, extended=True)
        key = Key(KeyType.STRING, [enc_key])
        result = BaseEngine.encrypt_engine.encrypt(data, key)
        return result.path

    @staticmethod
    def decrypt(filepath: str, enc_key: str) -> str:
        data = Data(DataType.FILE, data=filepath, extended=True)
        key = Key(KeyType.STRING, [enc_key])
        result = BaseEngine.encrypt_engine.decrypt(data, key)
        return result.path
