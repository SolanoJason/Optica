from pydantic_settings import BaseSettings, SettingsConfigDict
from fastapi.templating import Jinja2Templates
from pathlib import Path
from functools import cached_property
from pydantic import (
    PostgresDsn,
    SecretStr,
    PositiveInt,
    Field,
    BeforeValidator,
    NonNegativeInt
)
from typing import Annotated, ClassVar, get_origin
from urllib.parse import urlencode
from sqlalchemy.engine.interfaces import IsolationLevel
from libcloud.storage.providers import Provider
from .utils import Environment, SSLMode


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
        case_sensitive=True,
        env_ignore_empty=True,
        validate_default=True,
    )

    ENVIRONMENT: Annotated[Environment, BeforeValidator(lambda v: v.lower())]

    BASE_DIR: ClassVar[Path] = Path(__file__).parent.parent.parent

    MEDIA_ROOT: ClassVar[Path] = BASE_DIR / "media"
    MEDIA_URL: ClassVar[str] = "/media/"

    # Database Configuration
    DB__DRIVER: ClassVar[str] = "postgresql+psycopg"
    DB__HOST: str = "localhost"
    DB__USERNAME: str = "postgres"
    DB__PORT: int = 5432
    DB__PASSWORD: SecretStr
    DB__NAME: str
    DB__ISOLATION_LEVEL: ClassVar[IsolationLevel] = "READ COMMITTED"

    # Database Query Configuration
    DB__QUERY__APPLICATION_NAME: ClassVar[str] = "FastAPI-CoreySchafer"
    DB__QUERY__SSLMODE: ClassVar[SSLMode]

    # Database Engine Configuration
    DB__ENGINE__POOLSIZE: NonNegativeInt = 5
    DB__ENGINE__POOLOVERFLOW: Annotated[int, Field(ge=-1)] = 10

    STORAGE_PROVIDER: ClassVar[Provider]

    SECRET_KEY: SecretStr = SecretStr("YOUR_SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: PositiveInt = 30

    @cached_property
    def DB_DSN(self) -> PostgresDsn:
        query = urlencode(
            {
                "application_name": self.DB__QUERY__APPLICATION_NAME,
                "sslmode": self.DB__QUERY__SSLMODE.value,
            }
        )

        return PostgresDsn.build(
            scheme=self.DB__DRIVER,
            username=self.DB__USERNAME,
            password=self.DB__PASSWORD.get_secret_value(),
            host=self.DB__HOST,
            port=self.DB__PORT,
            path=self.DB__NAME,
            query=query,
        )

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        for base in cls.__mro__:
            annotations = base.__dict__.get("__annotations__", {})

            for name, annotation in annotations.items():
                if get_origin(annotation) is not ClassVar:
                    continue

                if name in base.__dict__:
                    continue

                if not hasattr(cls, name):
                    raise TypeError(f"{cls.__name__} must define {name}")
