from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from src.authentication import get_current_user
from src.errors import unauthorized_error
from src.models import (
    User,
    UserCreate,
    UserPublic,
    UserPublicWithItems,
    UserPublicWithTransactions,
    UserUpdate,
)
from src.utils import get_session, hash_password

router = APIRouter()


@router.post("/users/", response_model=UserPublic)
def add_user(*, session: Session = Depends(get_session), user: UserCreate):
    hashed_pw = hash_password(user.password)
    extra_data = {"hashed_password": hashed_pw}
    db_user = User.model_validate(user, update=extra_data)
    try:
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user

    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail="Email already exists")


@router.get("/users/", response_model=list[UserPublic])
def fetch_users(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=10, le=10),
):
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users


@router.get("/users/{user_id}", response_model=UserPublicWithItems)
def fetch_user(
    *,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    user_id: int,
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.flat_id != current_user.flat_id:
        raise unauthorized_error
    return user


@router.get("/users/{user_id}/transactions", response_model=UserPublicWithTransactions)
def fetch_user_with_transactions(
    *,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    user_id: int,
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.flat_id != current_user.flat_id:
        raise unauthorized_error
    return user


@router.patch("/users/{user_id}", response_model=UserPublic)
def update_user(
    *,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    user_id: int,
    user: UserUpdate,
):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user.id != current_user.id:
        raise unauthorized_error

    user_data = user.model_dump(exclude_unset=True)

    if user.password:
        user_data["hashed_password"] = hash_password(user.password)
        user_data.pop("password", None)

    db_user.sqlmodel_update(user_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.delete("/users/{user_id}")
def delete_user(
    *,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    user_id: int,
):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user.id != current_user.id:
        raise unauthorized_error
    session.delete(db_user)
    session.commit()
    return {"ok": True}
