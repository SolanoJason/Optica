from typing import Annotated
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from apps.optic.models import Patient, Prescription
from apps.optic.schemas import (
    PatientResponse,
    PrescriptionResponse,
    PrescriptionSubmission,
)
from apps.users.dependencies import get_current_user, CurrentUser
from apps.users.models import User
from core.database import SessionDep

patient_router = APIRouter()
prescription_router = APIRouter()



@patient_router.get("/patients", response_model=list[PatientResponse])
async def list_patients(
    current_user: CurrentUser,
    session: SessionDep,
    q: Annotated[str | None, Query(min_length=1, max_length=100)] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[Patient]:
    query = select(Patient).where(Patient.user_id == current_user.id)
    if q is not None:
        query = query.where(Patient.full_name.ilike(f"%{q}%"))
    query = query.order_by(Patient.full_name, Patient.id).offset(offset).limit(limit)
    result = await session.scalars(query)
    return list(result)


@patient_router.get("/patients/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: int,
    current_user: CurrentUser,
    session: SessionDep,
) -> Patient:
    patient = await session.scalar(
        select(Patient).where(
            Patient.id == patient_id,
            Patient.user_id == current_user.id,
        )
    )
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    return patient


@prescription_router.post(
    "",
    response_model=PrescriptionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_prescription(
    submission: PrescriptionSubmission,
    current_user: CurrentUser,
    session: SessionDep,
) -> Prescription:
    if submission.patient_id is not None:
        patient = await session.scalar(
            select(Patient).where(
                Patient.id == submission.patient_id,
                Patient.user_id == current_user.id,
            )
        )
        if patient is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    else:
        patient = Patient(user_id=current_user.id, **submission.patient.model_dump())
        session.add(patient)
        await session.flush()

    prescription = Prescription(
        patient=patient,
        **submission.prescription.model_dump(),
    )
    session.add(prescription)
    await session.commit()

    result = await session.scalar(
        select(Prescription)
        .options(selectinload(Prescription.patient))
        .where(Prescription.id == prescription.id)
    )
    return result


@prescription_router.get("", response_model=list[PrescriptionResponse])
async def list_prescriptions(
    current_user: CurrentUser,
    session: SessionDep,
    q: Annotated[str | None, Query(min_length=1, max_length=100)] = None,
    patient_id: Annotated[int | None, Query(gt=0)] = None,
    prescribed_after: datetime | None = None,
    prescribed_before: datetime | None = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[Prescription]:
    query = (
        select(Prescription)
        .join(Patient)
        .options(selectinload(Prescription.patient))
        .where(Patient.user_id == current_user.id)
    )
    if q is not None:
        query = query.where(Patient.full_name.ilike(f"%{q}%"))
    if patient_id is not None:
        query = query.where(Patient.id == patient_id)
    if prescribed_after is not None:
        query = query.where(Prescription.prescribed_at >= prescribed_after)
    if prescribed_before is not None:
        query = query.where(Prescription.prescribed_at <= prescribed_before)
    query = query.order_by(Prescription.prescribed_at.desc(), Prescription.id.desc())
    query = query.offset(offset).limit(limit)
    result = await session.scalars(query)
    return list(result)


@prescription_router.get("/{prescription_id}", response_model=PrescriptionResponse)
async def get_prescription(
    prescription_id: int,
    current_user: CurrentUser,
    session: SessionDep,
) -> Prescription:
    prescription = await session.scalar(
        select(Prescription)
        .join(Patient)
        .options(selectinload(Prescription.patient))
        .where(
            Prescription.id == prescription_id,
            Patient.user_id == current_user.id,
        )
    )
    if prescription is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found",
        )
    return prescription
