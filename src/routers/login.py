from datetime import timedelta

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from src.authentication import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    Token,
    create_access_token,
    get_current_user,
)
from src.models import User
from src.utils import check_hash, get_session

router = APIRouter()


@router.post("/token")
async def login_for_token(
    *,
    session: Session = Depends(get_session),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Token:
    statement = select(User).where(User.email == form_data.username)
    user = session.exec(statement).one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Cannot authenticate")
    if not check_hash(form_data.password, user.hashed_password):
        raise HTTPException(status_code=404, detail="Cannot authenticate")

    token_expiration = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires=token_expiration
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=User)
async def read_me(current_user: User = Depends(get_current_user)):
    return current_user
