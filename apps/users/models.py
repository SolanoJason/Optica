from __future__ import annotations
from core.database import intpk, Base, TimeStampMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import CITEXT
from dataclasses import InitVar
from sqlalchemy import ForeignKey
from core.auth import password_hasher


class User(TimeStampMixin, Base):
    __tablename__ = "users"

    id: Mapped[intpk] = mapped_column(init=False)
    username: Mapped[str] = mapped_column(CITEXT, unique=True)
    email: Mapped[str] = mapped_column(CITEXT, unique=True)

    password: InitVar[str]
    repeat_password: InitVar[str]
    password_hash: Mapped[str] = mapped_column(repr=False, init=False)

    patients: Mapped[list["Patient"]] = relationship(
        back_populates="user",
        default_factory=list,
        cascade="save-update, merge",
        repr=False,
    )
    settings: Mapped["UserSettings"] = relationship(
        back_populates="user",
        default=None,
        repr=False,
        single_parent=True,
        cascade="all, delete-orphan",
    )

    def __post_init__(self, password: str, repeat_password: str):
        if password != repeat_password:
            raise ValueError("Passwords do not match")
        self.password_hash = password_hasher.hash(password)

    def verify_password(self, password: str) -> bool:
        return password_hasher.verify(password, self.password_hash)


class UserSettings(TimeStampMixin, Base):
    __tablename__ = "user_settings"

    id: Mapped[intpk] = mapped_column(init=False)

    individual_pd: Mapped[bool] = mapped_column(default=True, server_default="true")
    individual_add: Mapped[bool] = mapped_column(default=True, server_default="true")

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, default=None)
    user: Mapped["User"] = relationship(
        back_populates="settings",
        default=None,
        repr=False,
        single_parent=True,
    )


# Register user session listeners after all user models are defined.
import apps.users.events
