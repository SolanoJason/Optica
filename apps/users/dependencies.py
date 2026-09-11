from typing import Annotated
from fastapi import Depends, HTTPException, status
from core.auth import oauth2_scheme, verify_access_token
from core.database import SessionDep
from apps.users.models import User


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: SessionDep
) -> User:
    user_id = verify_access_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        user = await session.get(User, int(user_id))
    except (TypeError, ValueError):
        user = None
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user

CurrentUser = Annotated[User, Depends(get_current_user)]
