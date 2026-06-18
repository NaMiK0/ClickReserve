from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from backend.app.repositories.user import UserRepository
from backend.app.routers.dependencies import get_session
from backend.app.schemas.user import Token, UserCreate, UserLogin, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session),
) -> UserRead:
    user_repo = UserRepository(session)

    if await user_repo.get_user_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    if await user_repo.get_user_by_username(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken",
        )

    hashed_password = hash_password(user_data.password)
    user = await user_repo.create_user(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
    )
    return user


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    session: AsyncSession = Depends(get_session),
) -> Token:
    user_repo = UserRepository(session)
    user = await user_repo.get_user_by_email(credentials.email)

    if user is None or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token = create_access_token({"sub": str(user.id)})
    return Token(access_token=access_token, token_type="bearer")
