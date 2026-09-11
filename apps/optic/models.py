from core.database import Base, TimeStampMixin, intpk, ImageFile
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, CheckConstraint
from decimal import Decimal
from sqlalchemy.sql.sqltypes import Numeric, DateTime
from datetime import datetime
from sqlalchemy.dialects.postgresql import CITEXT


class Patient(TimeStampMixin, Base):
    __tablename__ = "patients"

    id: Mapped[intpk] = mapped_column(init=False)

    full_name: Mapped[str] = mapped_column(CITEXT, index=True)
    phone_number: Mapped[str | None] = mapped_column(default=None)
    notes: Mapped[str | None] = mapped_column(default=None, repr=False)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), default=None, index=True)
    user: Mapped["User"] = relationship(
        back_populates="patients",
        default=None,
        repr=False,
        single_parent=True,
    )

    prescriptions: Mapped[list["Prescription"]] = relationship(
        back_populates="patient",
        default_factory=list,
        cascade="all, delete-orphan",
        repr=False,
    )


class Prescription(TimeStampMixin, Base):
    __tablename__ = "prescriptions"

    id: Mapped[intpk] = mapped_column(init=False)

    prescribed_at: Mapped[datetime] = mapped_column(DateTime(True))
    sphere_od: Mapped[Decimal | None] = mapped_column(Numeric(4, 2), default=None)
    sphere_os: Mapped[Decimal | None] = mapped_column(Numeric(4, 2), default=None)
    cylinder_od: Mapped[Decimal | None] = mapped_column(Numeric(4, 2), default=None)
    cylinder_os: Mapped[Decimal | None] = mapped_column(Numeric(4, 2), default=None)
    axis_od: Mapped[int | None] = mapped_column(default=None)
    axis_os: Mapped[int | None] = mapped_column(default=None)
    pd_od: Mapped[Decimal | None] = mapped_column(Numeric(4, 2), default=None)
    pd_os: Mapped[Decimal | None] = mapped_column(Numeric(4, 2), default=None)
    add_od: Mapped[Decimal | None] = mapped_column(Numeric(4, 2), default=None)
    add_os: Mapped[Decimal | None] = mapped_column(Numeric(4, 2), default=None)

    image: Mapped[ImageFile | None] = mapped_column(default=None, repr=False)
    notes: Mapped[str | None] = mapped_column(default=None, repr=False)

    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), default=None, index=True)
    patient: Mapped["Patient"] = relationship(
        back_populates="prescriptions",
        default=None,
        repr=False,
        single_parent=True,
    )

    __table_args__ = (
        CheckConstraint("axis_od BETWEEN 0 AND 180", name="check_axis_od"),
        CheckConstraint("axis_os BETWEEN 0 AND 180", name="check_axis_os"),
        CheckConstraint("add_od >= 0", name="check_add_od"),
        CheckConstraint("add_os >= 0", name="check_add_os"),
        CheckConstraint("pd_od >= 0", name="check_pd_od"),
        CheckConstraint("pd_os >= 0", name="check_pd_os"),
        CheckConstraint(
            """sphere_od IS NOT NULL OR 
            sphere_os IS NOT NULL OR 
            cylinder_od IS NOT NULL OR 
            cylinder_os IS NOT NULL OR 
            axis_od IS NOT NULL OR 
            axis_os IS NOT NULL OR 
            add_od IS NOT NULL OR 
            add_os IS NOT NULL OR 
            pd_od IS NOT NULL OR 
            pd_os IS NOT NULL""",
            name="check_at_least_one",
        ),
    )
