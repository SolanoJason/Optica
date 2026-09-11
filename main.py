from fastapi import FastAPI
from contextlib import asynccontextmanager
from apps.users.routers import api_router
from apps.optic.routers import patient_router, prescription_router
from core.database import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(
    lifespan=lifespan,
)

app.include_router(api_router, prefix="/auth", tags=["authentication"])
app.include_router(patient_router, tags=["patients"])
app.include_router(prescription_router, prefix="/prescriptions", tags=["prescriptions"])
