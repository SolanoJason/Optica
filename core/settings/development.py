from .base import Settings
from libcloud.storage.providers import Provider
from .utils import SSLMode

class DevelopmentSettings(Settings):
    DB__QUERY__SSLMODE = SSLMode.ALLOW
    STORAGE_PROVIDER = Provider.LOCAL