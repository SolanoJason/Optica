from typing import Annotated
from sqlalchemy.orm import mapped_column
from sqlalchemy import Identity
from sqlalchemy_file import File
from pydantic_core import core_schema, CoreSchema
from pydantic.json_schema import JsonSchemaValue
from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler

intpk = Annotated[int, mapped_column(Identity(True), primary_key=True)]


class ImageFile(File):

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type,
        handler: GetCoreSchemaHandler,
    ):
        return core_schema.is_instance_schema(
            cls,
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda value: value.url if value else None,
                info_arg=False,
                return_schema=core_schema.str_schema(),
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        core_schema: CoreSchema,
        handler: GetJsonSchemaHandler,
    ) -> JsonSchemaValue:
        return {"type": "string"}
