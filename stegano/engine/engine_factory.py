from enum import Enum
from os import path
from typing import Type, Union

from stegano.engine import BaseEngine, DummyEngine


class EngineType(Enum):
    DUMMY = 'Dummy engine'

    @staticmethod
    def list():
        return list(map(lambda engine: engine, EngineType))


class EngineFactory:

    @staticmethod
    def get_engine_to_handle_file(file_path: str) -> Union[EngineType, None]:
        all_engine = EngineType.list()

        file_ext = path.splitext(file_path)[-1][1:]

        selected_engine = None

        for engine in all_engine:
            extension_supported = EngineFactory.get_engine_class(engine).get_supported_extensions()
            if file_ext in extension_supported:
                selected_engine = engine
                break

        return selected_engine

    @staticmethod
    def get_engine_class(engine_type: EngineType) -> Type[BaseEngine]:
        if engine_type == EngineType.DUMMY:
            return DummyEngine
        else:
            raise RuntimeError('Invalid engine')

    @staticmethod
    def create_engine(engine_type: EngineType) -> BaseEngine:
        return EngineFactory.get_engine_class(engine_type)()
