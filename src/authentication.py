from datetime import datetime, timedelta
from fastapi import Depends
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel
from sqlmodel import Session, select

from src.models import User
from src.utils import get_session

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None


def create_access_token(data: dict, expires: timedelta | None = None):
    to_encode = data.copy()
    if expires:
        expiration = datetime.now() + expires
    else:
        expiration = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expiration})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    *, session: Session = Depends(get_session), token: str = Depends(oauth2_scheme)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=401, detail="Could not validate credentials"
            )
        token_data = TokenData(email=email)
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    statement = select(User).where(User.email == token_data.email)
    user = session.exec(statement).one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    return user
