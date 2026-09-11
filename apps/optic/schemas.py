from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PatientInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    full_name: Annotated[str, Field(min_length=1, max_length=255)]
    phone_number: Annotated[str | None, Field(max_length=50)] = None
    notes: Annotated[str | None, Field(max_length=2000)] = None


class PatientResponse(PatientInput):
    id: int

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)


class PrescriptionInput(BaseModel):
    prescribed_at: datetime
    sphere_od: Decimal | None = Field(default=None, max_digits=4, decimal_places=2)
    sphere_os: Decimal | None = Field(default=None, max_digits=4, decimal_places=2)
    cylinder_od: Decimal | None = Field(default=None, max_digits=4, decimal_places=2)
    cylinder_os: Decimal | None = Field(default=None, max_digits=4, decimal_places=2)
    axis_od: Annotated[int | None, Field(ge=0, le=180)] = None
    axis_os: Annotated[int | None, Field(ge=0, le=180)] = None
    pd_od: Annotated[Decimal | None, Field(ge=0, max_digits=4, decimal_places=2)] = None
    pd_os: Annotated[Decimal | None, Field(ge=0, max_digits=4, decimal_places=2)] = None
    add_od: Annotated[Decimal | None, Field(ge=0, max_digits=4, decimal_places=2)] = None
    add_os: Annotated[Decimal | None, Field(ge=0, max_digits=4, decimal_places=2)] = None
    notes: Annotated[str | None, Field(max_length=2000)] = None

    @model_validator(mode="after")
    def require_eye_metric(self) -> "PrescriptionInput":
        metric_names = (
            "sphere_od",
            "sphere_os",
            "cylinder_od",
            "cylinder_os",
            "axis_od",
            "axis_os",
            "pd_od",
            "pd_os",
            "add_od",
            "add_os",
        )
        if not any(getattr(self, name) is not None for name in metric_names):
            raise ValueError("At least one eye metric is required")
        return self


class PrescriptionSubmission(BaseModel):
    patient_id: int | None = Field(default=None, gt=0)
    patient: PatientInput | None = None
    prescription: PrescriptionInput

    @model_validator(mode="after")
    def require_one_patient_source(self) -> "PrescriptionSubmission":
        if (self.patient_id is None) == (self.patient is None):
            raise ValueError("Provide either patient_id or patient data")
        return self


class PrescriptionResponse(PrescriptionInput):
    id: int
    patient: PatientResponse

    model_config = ConfigDict(from_attributes=True)
