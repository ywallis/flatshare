from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from sqlmodel import Session, select

from src.buy_in import item_buy_in
from src.buy_out import item_buy_out
from src.models import (
    Flat,
    FlatCreate,
    FlatPublic,
    FlatPublicWithUsers,
    FlatUpdate,
)
from src.models import User, UserPublicWithItems
from src.utils import get_session

router = APIRouter()


@router.post("/flats/", response_model=FlatPublic)
def add_flat(*, session: Session = Depends(get_session), flat: FlatCreate):
    db_first_user = session.get(User, flat.first_user_id)
    if not db_first_user:
        raise HTTPException(status_code=404, detail="First user not found")
    db_flat = Flat.model_validate(flat)
    db_flat.users.append(db_first_user)
    session.add(db_flat)
    session.commit()
    session.refresh(db_flat)
    return db_flat


@router.get("/flats/", response_model=list[FlatPublic])
def fetch_flats(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=10, le=10),
):
    flats = session.exec(select(Flat).offset(offset).limit(limit)).all()
    return flats


@router.get("/flats/{flat_id}", response_model=FlatPublicWithUsers)
def fetch_flat(*, session: Session = Depends(get_session), flat_id: int):
    flat = session.get(Flat, flat_id)
    if not flat:
        raise HTTPException(status_code=404, detail="Flat not found")
    return flat


@router.patch("/flats/{flat_id}", response_model=FlatPublic)
def update_flat(
    *,
    session: Session = Depends(get_session),
    flat_id: int,
    flat: FlatUpdate,
):
    db_flat = session.get(Flat, flat_id)
    if not db_flat:
        raise HTTPException(status_code=404, detail="Flat not found")
    flat_data = flat.model_dump(exclude_unset=True)
    db_flat.sqlmodel_update(flat_data)
    session.add(db_flat)
    session.commit()
    session.refresh(db_flat)
    return db_flat


@router.delete("/flats/{flat_id}")
def delete_flat(*, session: Session = Depends(get_session), flat_id: int):
    db_flat = session.get(User, flat_id)
    if not db_flat:
        raise HTTPException(status_code=404, detail="Flat not found")
    session.delete(db_flat)
    session.commit()
    return {"ok": True}


@router.post("/flats/{flat_id}/move_in/{user_id}", response_model=UserPublicWithItems)
def user_move_in(
    *,
    session: Session = Depends(get_session),
    flat_id: int,
    user_id: int,
    exclude_items: list[int],
    date: str,
):
    db_flat = session.get(Flat, flat_id)
    if not db_flat:
        raise HTTPException(status_code=404, detail="Flat not found")
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user.flat is not None:
        raise HTTPException(status_code=400, detail="User already in an flat")
    db_flat.users.append(db_user)
    for item in db_flat.items:
        if item.id not in exclude_items:
            item_buy_in(session, db_user, item, date)
            db_user.items.append(item)

    session.commit()
    session.refresh(db_user)
    return db_user


@router.post("/flats/{flat_id}/move_out/{user_id}", response_model=UserPublicWithItems)
def user_move_out(
    *,
    session: Session = Depends(get_session),
    flat_id: int,
    user_id: int,
    date: str,
):
    db_flat = session.get(Flat, flat_id)
    if not db_flat:
        raise HTTPException(status_code=404, detail="Flat not found")
    if len(db_flat.users) == 1:
        raise HTTPException(status_code=404, detail="User is the last user in the flat")
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user.flat is None:
        raise HTTPException(status_code=400, detail="User has no flat")
    if db_user.flat.id != db_flat.id:
        raise HTTPException(status_code=400, detail="User not in flat")

    for item in db_user.items:
        item_buy_out(session, db_user, item, date)

    db_user.flat = None
    db_user.items = []
    session.commit()
    session.refresh(db_user)
    return db_user
