from pydantic.dataclasses import dataclass

from .config_loader.read_json import JsonConfigReader
from .config_loader.read_yaml import YamlConfigReader

@dataclass
class ConfigReaderInstance:
    json = JsonConfigReader()
    yaml = YamlConfigReader()