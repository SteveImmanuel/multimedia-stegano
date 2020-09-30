from abc import ABC, abstractmethod

from typing import List, Dict


class BaseEngine(ABC):
    def conceal(self, file_in_path: str, secret_file_path: str, file_out_path: str):
        # TODO: validation
        self._conceal(file_in_path, secret_file_path, file_out_path)

    def extract(self, file_in_path: str, extract_file_path: str):
        # TODO: validation
        self._extract(file_in_path, extract_file_path)

    @staticmethod
    @abstractmethod
    def get_conceal_option(self) -> List[Dict[str, str]]:
        # Return list of dict, each dict value will be used ad the option label
        pass
        return self._get_conceal_option()

    @staticmethod
    @abstractmethod
    def get_supported_extensions(self) -> List[str]:
        pass

    @abstractmethod
    def check_file_supported(self, filepath: str) -> bool:
        pass

    @abstractmethod
    def get_max_message(self, filepath: str) -> int:
        pass

    @abstractmethod
    def _conceal(self, file_in_path: str, secret_file_path: str, file_out_path: str):
        pass

    @abstractmethod
    def _extract(self, file_in_path: str, extract_file_path: str):
        pass
