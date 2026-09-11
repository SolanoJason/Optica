from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from core.database import SessionDep
from apps.users.models import User, UserSettings
from apps.users.schemas import TokenResponse, UserCreate, UserResponse
from apps.users.dependencies import get_current_user
from core.auth import create_access_token
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from typing import Annotated

router = APIRouter()

CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, session: SessionDep) -> User:
    existing_user = await session.scalar(
        select(User).where(
            (User.username == user_data.username) | (User.email == user_data.email)
        )
    )
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email is already registered",
        )

    user = User(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
        repeat_password=user_data.repeat_password,
        settings=UserSettings(),
    )
    session.add(user)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email is already registered",
        ) from None

    await session.refresh(user)
    return user


@router.post("/token", response_model=TokenResponse)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep,
) -> TokenResponse:
    user = await session.scalar(select(User).where(User.username == form_data.username))
    if user is None or not user.verify_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenResponse(access_token=create_access_token({"sub": str(user.id)}))


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: CurrentUser) -> User:
    return current_user
