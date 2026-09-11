from core.settings import settings
from sqlalchemy import create_engine, make_url, MetaData
from sqlalchemy.orm import sessionmaker, MappedAsDataclass, DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from .types import ImageFile
from sqlalchemy.sql.sqltypes import JSON, String
from sqlalchemy.dialects import postgresql
from sqlalchemy_file import FileField, ImageField, File
from sqlalchemy_file.storage import StorageManager
from core.storage import container

url = make_url(settings.DB_DSN.encoded_string())

engine = create_async_engine(
    url,
    pool_size=settings.DB__ENGINE__POOLSIZE,
    max_overflow=settings.DB__ENGINE__POOLOVERFLOW,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_timeout=10,
    isolation_level=settings.DB__ISOLATION_LEVEL,
    echo=True
)

SessionFactory = async_sessionmaker(engine, autoflush=False, expire_on_commit=False)

naming_convention = {
    "pk": "%(table_name)s_pk",
    "fk": "%(table_name)s_%(referred_table_name)s_%(column_0_N_name)s_fk",
    "uq": "%(table_name)s_%(column_0_N_name)s_uq",
    "ix": "%(table_name)s_%(column_0_N_name)s_ix",  # This will be used in case the index doesn't have a name specified (Index=True). If the index has a name, that name will be used instead.
    # "ck": "%(constraint_name)s", # Check constraints always require a name, so we can just use the constraint name as the naming convention for check constraints.
}

metadata = MetaData(naming_convention=naming_convention)


class Base(AsyncAttrs, MappedAsDataclass, DeclarativeBase, kw_only=True):
    metadata = metadata
    type_annotation_map = {
        File: FileField(none_as_null=True),  # type: ignore
        ImageFile: ImageField(upload_type=ImageFile, none_as_null=True),  # type: ignore
        dict: JSON(none_as_null=True),
        list[str]: postgresql.ARRAY(String),
    }


StorageManager.add_storage("default", container)