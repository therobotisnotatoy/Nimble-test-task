import logging
import marshmallow.validate as mav
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from environs import Env


logger = logging.getLogger(__name__)


@dataclass_json
@dataclass
class DBConfig():
    """A configuration class for the database connection."""
    DB_HOST: str = None
    DB_PORT: int = None
    DB_NAME: str = None
    DB_USER: str = None
    DB_PASSWORD: str = None
    DB_CONTAINER_NAME: str = None
    DB_SERVICE_NAME: str = None

    @staticmethod
    def from_env(env: Env) -> "DBConfig":
        config = DBConfig()
        with env.prefixed('DB_'):
            config.DB_HOST = env.str("HOST", "localhost", validate=mav.Length(min=1))
            config.DB_PORT = env.int("PORT", 5432, validate=mav.Range(min=1, max=65535))
            config.DB_NAME = env.str("NAME", validate=mav.Length(min=3))
            config.DB_USER = env.str("USER", validate=mav.Length(min=3))
            config.DB_PASSWORD = env.str("PASSWORD", validate=mav.Length(min=8))
            config.DB_CONTAINER_NAME = env.str("CONTAINER_NAME", "tt_nimble_inc-db-1")
            config.DB_SERVICE_NAME = env.str("SERVICE_NAME", "db")
        # logger.info(config)
        return config

    def __repr__(self) -> str:
        return f"DBConfig: \n{self.to_json(indent=4, sort_keys=True)}"


@dataclass_json
@dataclass
class NimbleAPIConfig():
    """A configuration class for the Nimble API."""
    NIMBLE_API_KEY: str = None
    NIMBLE_API_URL: str = None

    @staticmethod
    def from_env(env: Env) -> "NimbleAPIConfig":
        config = NimbleAPIConfig()
        with env.prefixed('NIMBLE_API_'):
            config.NIMBLE_API_KEY = env.str("KEY", validate=mav.Length(equal=30))
            config.NIMBLE_API_URL = env.str("URL", validate=mav.URL())
        # logger.info(config)
        return config

    def __repr__(self) -> str:
        return f"NimbleAPIConfig: \n{self.to_json(indent=4, sort_keys=True)}"


@dataclass_json
@dataclass
class AppConfig():
    """A configuration class for the entire application."""
    db_config: DBConfig = None
    nimble_api_config: NimbleAPIConfig = None

    @staticmethod
    def from_env(env: Env) -> "AppConfig":
        config = AppConfig()
        config.db_config = DBConfig.from_env(env)
        config.nimble_api_config = NimbleAPIConfig.from_env(env)
        return config

    def __repr__(self) -> str:
        return f"AppConfig: \n{self.to_json(indent=4, sort_keys=True)}"
