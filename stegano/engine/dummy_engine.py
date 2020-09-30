from typing import List, Dict

from stegano.engine import BaseEngine


class DummyEngine(BaseEngine):
    def __init__(self):
        super(DummyEngine, self).__init__()

    def _get_conceal_option(self) -> List[Dict[str, str]]:
        return [{'a': 'urutan a', 'b': 'urutan b'}, {'1': 'metode 1', '2': 'metode 2'}]

    def _get_supported_extensions(self) -> List[str]:
        return ['txt']

    def check_file_supported(self, filepath: str) -> bool:
        # File must starts with text and ends with txt
        return filepath.endswith('txt') and filepath.startswith('text')

    def get_max_message(self, filepath) -> int:
        return 1

    def _conceal(self, file_in_path: str, secret_file_path: str, file_out_path: str):
        pass

    def _extract(self, file_in_path: str, extract_file_path: str):
        pass