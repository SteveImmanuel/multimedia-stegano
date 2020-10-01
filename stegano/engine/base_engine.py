from abc import ABC, abstractmethod

from typing import List, Dict


class BaseEngine(ABC):
    def conceal(self, file_in_path: str, secret_file_path: str, file_out_path: str,
                encryption_key: str, config: List[str]):
        # TODO: validation
        self._conceal(file_in_path, secret_file_path, file_out_path, encryption_key, config)

    def extract(
        self,
        file_in_path: str,
        extract_file_path: str,
        encryption_key: str,
    ):
        # TODO: validation
        self._extract(file_in_path, extract_file_path, encryption_key)

    @staticmethod
    @abstractmethod
    def get_conceal_option() -> List[Dict[str, str]]:
        # Return list of dict, each dict value will be used ad the option label
        pass

    @staticmethod
    @abstractmethod
    def get_supported_extensions() -> List[str]:
        pass

    @abstractmethod
    def check_file_supported(self, filepath: str) -> bool:
        pass

    @abstractmethod
    def get_max_message(self, filepath: str) -> int:
        pass

    @abstractmethod
    def _conceal(self, file_in_path: str, message_file_path: str, file_out_path: str,
                 encryption_key: str, config: List[str]):
        # Encryption key will be filled with empty string if encryption is disabled
        pass

    @abstractmethod
    def _extract(
        self,
        file_in_path: str,
        extract_file_path: str,
        encryption_key: str,
    ):
        pass
