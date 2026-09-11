import pytest
from pydantic import ValidationError

from apps.optic.schemas import PrescriptionSubmission
from apps.users.schemas import UserCreate


def valid_prescription() -> dict:
    return {
        "patient": {"full_name": "Jane Doe"},
        "prescription": {
            "prescribed_at": "2026-09-11T10:00:00Z",
            "sphere_od": "-1.25",
        },
    }


def test_user_passwords_must_match() -> None:
    with pytest.raises(ValidationError):
        UserCreate(
            username="owner",
            email="owner@example.com",
            password="password123",
            repeat_password="different123",
        )


def test_prescription_requires_an_eye_metric() -> None:
    payload = valid_prescription()
    payload["prescription"].pop("sphere_od")

    with pytest.raises(ValidationError):
        PrescriptionSubmission.model_validate(payload)


@pytest.mark.parametrize(
    ("field", "value"),
    [("axis_od", 181), ("axis_os", -1), ("pd_od", -1), ("add_os", -1)],
)
def test_prescription_rejects_invalid_metric_values(field: str, value: int) -> None:
    payload = valid_prescription()
    payload["prescription"][field] = value

    with pytest.raises(ValidationError):
        PrescriptionSubmission.model_validate(payload)


def test_prescription_requires_exactly_one_patient_source() -> None:
    payload = valid_prescription()
    payload["patient_id"] = 1

    with pytest.raises(ValidationError):
        PrescriptionSubmission.model_validate(payload)

    payload.pop("patient")
    payload.pop("patient_id")
    with pytest.raises(ValidationError):
        PrescriptionSubmission.model_validate(payload)
