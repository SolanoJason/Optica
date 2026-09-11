from pydantic import BaseModel, EmailStr, Field, ConfigDict, model_validator
from typing import Annotated


class UserBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr
    username: Annotated[str, Field(min_length=3, max_length=60)]


class UserCreate(UserBase):
    password: Annotated[str, Field(min_length=8, max_length=128)]
    repeat_password: Annotated[str, Field(min_length=8, max_length=128)]

    @model_validator(mode="after")
    def passwords_must_match(self) -> "UserCreate":
        if self.password != self.repeat_password:
            raise ValueError("Passwords do not match")
        return self


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    username: Annotated[str | None, Field(min_length=3, max_length=60)] = None


class UserResponse(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
