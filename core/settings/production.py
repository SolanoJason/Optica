from libcloud.storage.providers import Provider
from pydantic import SecretStr
from .base import Settings
from .utils import SSLMode

class ProductionSettings(Settings):
    DB__QUERY__SSLMODE = SSLMode.PREFER
    STORAGE_PROVIDER = Provider.GOOGLE_STORAGE

    STORAGE_KEY: SecretStr
    STORAGE_SECRET: SecretStr
    STORAGE_BUCKET: str