from enum import Enum
from typing import Dict


class ConfigType(Enum):
    RADIO = 'radio'
    FLOAT = 'float'


class ConfigParam:
    def __init__(self, config_type: ConfigType, title: str):
        self.config_type = config_type
        self.title = title


class RadioParam(ConfigParam):
    def __init__(self, title: str, options: Dict[str, str]):
        super(RadioParam, self).__init__(ConfigType.RADIO, title)
        self.options = options


class FloatParam(ConfigParam):
    def __init__(self, title: str, step: float = 0.1, default: float = 0.0):
        super(FloatParam, self).__init__(ConfigType.FLOAT, title)
        self.step = step
        self.default = default
