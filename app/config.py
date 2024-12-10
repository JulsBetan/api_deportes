import os
import logging
from functools import lru_cache

from pydantic_settings import BaseSettings


log = logging.getLogger("uvicorn")


class Settings(BaseSettings):

    db_user: str
    db_pass: str
    db_host: str
    db_port: str
    db_name: str
    secret_key: str
    algorithm: str
    openai_key: str
    weather_key: str
    sports_key: str

    class Config:
        env_file = ".dev_env" if os.getenv("ENVIRONMENT") != "production" else None


@lru_cache()
def get_settings() -> Settings:
    log.info("Loading config settings from the environment...")
    return Settings()
