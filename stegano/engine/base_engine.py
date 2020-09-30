from abc import ABC, abstractmethod


class BaseEngine(ABC):
    def conceal(self, file_in_path: str, secret_file_path: str, file_out_path: str):
        #TODO: validation
        self._conceal(file_in_path, secret_file_path, file_out_path)

    def extract(self, file_in_path: str, extract_file_path: str):
        #TODO: validation
        self._extract(file_in_path, extract_file_path)

    @abstractmethod
    def _conceal(self, file_in_path: str, secret_file_path: str, file_out_path: str):
        pass

    @abstractmethod
    def _extract(self, file_in_path: str, extract_file_path: str):
        pass