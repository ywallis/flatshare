from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from sqlmodel import Session, select

from src.buy_in import item_buy_in
from src.buy_out import item_buy_out
from src.models import Flat
from src.models import (
    Item,
    ItemCreate,
    ItemPublic,
    ItemPublicWithUsers,
    ItemUpdate,
)
from src.models import User
from src.utils import get_session

router = APIRouter()


@router.post("/items/", response_model=ItemPublicWithUsers)
def add_item(*, session: Session = Depends(get_session), item: ItemCreate):
    db_item = Item.model_validate(item)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    flat = session.get(Flat, db_item.flat.id)
    if not flat:
        raise HTTPException(status_code=404, detail="Flat not found")
    db_item.users = flat.users
    session.commit()
    session.refresh(db_item)
    return db_item


@router.get("/items/", response_model=list[ItemPublicWithUsers])
def fetch_items(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=10, le=10),
):
    items = session.exec(select(Item).offset(offset).limit(limit)).all()
    return items


@router.get("/items/{item_id}", response_model=ItemPublicWithUsers)
def fetch_item(*, session: Session = Depends(get_session), item_id: int):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.patch("/items/{item_id}", response_model=ItemPublic)
def update_item(
    *, session: Session = Depends(get_session), item_id: int, item: ItemUpdate
):
    db_item = session.get(User, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    item_data = item.model_dump(exclude_unset=True)
    db_item.sqlmodel_update(item_data)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


@router.delete("/items/{item_id}")
def delete_item(*, session: Session = Depends(get_session), item_id: int):
    db_item = session.get(Item, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    session.delete(db_item)
    session.commit()
    return {"ok": True}


@router.patch("/items/{item_id}/add/{user_id}", response_model=ItemPublicWithUsers)
def add_user_from_item(
    *, session: Session = Depends(get_session), item_id: int, user_id: int, date: str
):
    db_item = session.get(Item, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user in db_item.users:
        raise HTTPException(status_code=409, detail="User is already assigned to item")

    item_buy_in(session, db_user, db_item, date)
    db_item.users.append(db_user)

    session.commit()
    session.refresh(db_item)
    return db_item


@router.patch("/items/{item_id}/remove/{user_id}", response_model=ItemPublicWithUsers)
def remove_user_from_item(
    *, session: Session = Depends(get_session), item_id: int, user_id: int, date: str
):
    db_item = session.get(Item, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user in db_item.users:
        item_buy_out(session, db_user, db_item, date)
        db_item.users.remove(db_user)
    else:
        raise HTTPException(status_code=404, detail="User was not item owner")

    session.commit()
    session.refresh(db_item)
    return db_item
