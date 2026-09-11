from core.settings import settings, Environment
from libcloud.storage.drivers.local import LocalStorageDriver
from libcloud.storage.base import StorageDriver, Container
from libcloud.storage.drivers.google_storage import GoogleStorageDriver
from libcloud.storage.providers import get_driver, Provider

match settings.STORAGE_PROVIDER:
    case Provider.LOCAL:
        driver_cls: type[LocalStorageDriver] = get_driver(settings.STORAGE_PROVIDER)
        driver: LocalStorageDriver = driver_cls(key=settings.MEDIA_ROOT.as_posix())
        container: Container = driver.get_container("")
    case Provider.GOOGLE_STORAGE:
        driver_cls: type[GoogleStorageDriver] = get_driver(settings.STORAGE_PROVIDER)
        driver: GoogleStorageDriver = driver_cls(key=settings.STORAGE_KEY.get_secret_value(), secret=settings.STORAGE_SECRET.get_secret_value()) # ty: ignore[unresolved-attribute]
        container: Container = driver.get_container(settings.STORAGE_BUCKET) # ty: ignore[unresolved-attribute]
    case _:
        NotImplementedError(f"Storage provider {settings.STORAGE_PROVIDER} is not implemented.")