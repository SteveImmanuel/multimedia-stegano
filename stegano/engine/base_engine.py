from abc import ABC, abstractmethod

from typing import List, Dict


class BaseEngine(ABC):
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
    def extract(
        file_in_path: str,
        extract_file_path: str,
        encryption_key: str,
    ) -> None:
        pass

    @staticmethod
    @abstractmethod
    def get_conceal_option() -> List[Dict[str, str]]:
        # Return list of dict, each dict value will be used ad the option label
        pass

    @staticmethod
    @abstractmethod
    def get_supported_extensions() -> List[str]:
        pass

    @staticmethod
    @abstractmethod
    def check_file_supported(filepath: str) -> bool:
        pass

    @staticmethod
    @abstractmethod
    def get_max_message(filepath: str) -> int:
        pass
