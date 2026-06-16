from typing import Any, Dict, List

from pydantic_settings import BaseSettings
from src.configs import ConfigReaderInstance


class GlobalConfig(BaseSettings):
    """Global configurations."""
    SERVICE_CONFIG_YML: Dict[str, Any] = ConfigReaderInstance.yaml.read_config_from_file("settings/service_config.yaml")
    LLM_CONFIG_YML: Dict[str, Any] = ConfigReaderInstance.yaml.read_config_from_file("settings/llm_config.yaml")
    
    ROOT_PATH: str = SERVICE_CONFIG_YML["app"]["root_path"]

    API_KEYS: List[str] = SERVICE_CONFIG_YML["api_keys"]
    MODEL_CONF: Dict[str, Any] = LLM_CONFIG_YML["model"]


settings = GlobalConfig()
