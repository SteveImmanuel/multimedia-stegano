from enum import Enum
from typing import Type

from stegano.engine import BaseEngine, DummyEngine


class EngineType(Enum):
    DUMMY = 'Dummy engine'

    @staticmethod
    def list():
        return list(map(lambda engine: engine, EngineType))


class EngineFactory:

    @staticmethod
    def get_engine_class(engine_type: EngineType) -> Type[BaseEngine]:
        if engine_type == EngineType.DUMMY:
            return DummyEngine
        else:
            raise RuntimeError('Invalid engine')

    @staticmethod
    def create_engine(engine_type: EngineType) -> BaseEngine:
        return EngineFactory.get_engine_class(engine_type)()
