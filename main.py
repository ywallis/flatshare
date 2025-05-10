from fastapi import Depends, FastAPI, Query
from fastapi.exceptions import HTTPException
from sqlmodel import Session, SQLModel, create_engine, select

from src.models import (
    Flat,
    FlatCreate,
    FlatPublic,
    FlatPublicWithUsers,
    FlatUpdate,
    Item,
    ItemCreate,
    ItemPublic,
    ItemPublicWithUsers,
    ItemUpdate,
    User,
    UserCreate,
    UserPublic,
    UserPublicWithItems,
    UserUpdate,
)

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


app = FastAPI()


def get_session():
    with Session(engine) as session:
        yield session


def hash_password(password: str) -> str:
    return f"actuallynotahash{password}"


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post("/flats/", response_model=FlatPublic)
def add_flat(
    *, session: Session = Depends(get_session), flat: FlatCreate
):
    db_flat = Flat.model_validate(flat)
    session.add(db_flat)
    session.commit()
    session.refresh(db_flat)
    return db_flat


@app.get("/flats/", response_model=list[FlatPublic])
def fetch_flats(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=10, le=10),
):
    flats = session.exec(select(Flat).offset(offset).limit(limit)).all()
    return flats


@app.get("/flats/{flat_id}", response_model=FlatPublicWithUsers)
def fetch_flat(*, session: Session = Depends(get_session), flat_id: int):
    flat = session.get(Flat, flat_id)
    if not flat:
        raise HTTPException(status_code=404, detail="Flat not found")
    return flat


@app.patch("/flats/{flat_id}", response_model=FlatPublic)
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


@app.delete("/flats/{flat_id}")
def delete_flat(*, session: Session = Depends(get_session), flat_id: int):
    db_flat = session.get(User, flat_id)
    if not db_flat:
        raise HTTPException(status_code=404, detail="Flat not found")
    session.delete(db_flat)
    session.commit()
    return {"ok": True}


@app.post("/users/", response_model=UserPublic)
def add_user(*, session: Session = Depends(get_session), user: UserCreate):
    hashed_pw = hash_password(user.password)
    extra_data = {"hashed_password": hashed_pw}
    db_user = User.model_validate(user, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@app.get("/users/", response_model=list[UserPublic])
def fetch_users(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=10, le=10),
):
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users


@app.get("/users/{user_id}", response_model=UserPublicWithItems)
def fetch_user(*, session: Session = Depends(get_session), user_id: int):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.patch("/users/{user_id}", response_model=UserPublic)
def update_user(
    *, session: Session = Depends(get_session), user_id: int, user: UserUpdate
):
    db_user = session.get(Item, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    user_data = user.model_dump(exclude_unset=True)
    db_user.sqlmodel_update(user_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@app.delete("/users/{user_id}")
def delete_user(*, session: Session = Depends(get_session), user_id: int):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(db_user)
    session.commit()
    return {"ok": True}


@app.post("/items/", response_model=ItemPublicWithUsers)
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


@app.get("/items/", response_model=list[ItemPublicWithUsers])
def fetch_items(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=10, le=10),
):
    items = session.exec(select(Item).offset(offset).limit(limit)).all()
    return items


@app.get("/items/{item_id}", response_model=ItemPublicWithUsers)
def fetch_item(*, session: Session = Depends(get_session), item_id: int):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.patch("/items/{item_id}", response_model=ItemPublic)
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


@app.delete("/items/{item_id}")
def delete_item(*, session: Session = Depends(get_session), item_id: int):
    db_item = session.get(Item, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    session.delete(db_item)
    session.commit()
    return {"ok": True}


@app.patch("/items/{item_id}/add/{user_id}", response_model=ItemPublicWithUsers)
def add_user_from_item(
    *, session: Session = Depends(get_session), item_id: int, user_id: int
):
    db_item = session.get(Item, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user in db_item.users:
        raise HTTPException(status_code=409, detail="User is already assigned to item")
    else:
        db_item.users.append(db_user)

    session.commit()
    session.refresh(db_item)
    return db_item


@app.patch("/items/{item_id}/remove/{user_id}", response_model=ItemPublicWithUsers)
def remove_user_from_item(
    *, session: Session = Depends(get_session), item_id: int, user_id: int
):
    db_item = session.get(Item, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user in db_item.users:
        db_item.users.remove(db_user)
    else:
        raise HTTPException(status_code=404, detail="User was not item owner")

    session.commit()
    session.refresh(db_item)
    return db_item


@app.post(
    "/flat/{flat_id}/move_in/{user_id}", response_model=UserPublicWithItems
)
def user_move_in(
    *,
    session: Session = Depends(get_session),
    flat_id: int,
    user_id: int,
    exclude_items: list[int],
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
            db_user.items.append(item)

    session.commit()
    session.refresh(db_user)
    return db_user
@app.post(
    "/flat/{flat_id}/move_out/{user_id}", response_model=UserPublicWithItems
)
def user_move_out(
    *,
    session: Session = Depends(get_session),
    flat_id: int,
    user_id: int,
):

    db_flat = session.get(Flat, flat_id)
    if not db_flat:
        raise HTTPException(status_code=404, detail="Flat not found")
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user.flat is None:
        raise HTTPException(status_code=400, detail="User has no flat")
    if db_user.flat.id != db_flat.id:
        raise HTTPException(status_code=400, detail="User not in flat")

    db_user.flat = None
    db_user.items = []
    session.commit()
    session.refresh(db_user)
    return db_user
