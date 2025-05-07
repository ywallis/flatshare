from fastapi import Depends, FastAPI, Query
from fastapi.exceptions import HTTPException
from sqlmodel import Session, SQLModel, create_engine, select

from src.models import (
    Apartment,
    ApartmentCreate,
    ApartmentPublic,
    ApartmentPublicWithUsers,
    ApartmentUpdate,
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


@app.post("/apartments/", response_model=ApartmentPublic)
def add_apartment(
    *, session: Session = Depends(get_session), apartment: ApartmentCreate
):
    db_apartment = Apartment.model_validate(apartment)
    session.add(db_apartment)
    session.commit()
    session.refresh(db_apartment)
    return db_apartment


@app.get("/apartments/", response_model=list[ApartmentPublic])
def fetch_apartments(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=10, le=10),
):
    apartments = session.exec(select(Apartment).offset(offset).limit(limit)).all()
    return apartments


@app.get("/apartments/{apartment_id}", response_model=ApartmentPublicWithUsers)
def fetch_apartment(*, session: Session = Depends(get_session), apartment_id: int):
    apartment = session.get(Apartment, apartment_id)
    if not apartment:
        raise HTTPException(status_code=404, detail="Apartment not found")
    return apartment


@app.patch("/apartments/{apartment_id}", response_model=ApartmentPublic)
def update_apartment(
    *,
    session: Session = Depends(get_session),
    apartment_id: int,
    apartment: ApartmentUpdate,
):
    db_apartment = session.get(Apartment, apartment_id)
    if not db_apartment:
        raise HTTPException(status_code=404, detail="Apartment not found")
    apartment_data = apartment.model_dump(exclude_unset=True)
    db_apartment.sqlmodel_update(apartment_data)
    session.add(db_apartment)
    session.commit()
    session.refresh(db_apartment)
    return db_apartment


@app.delete("/apartments/{apartment_id}")
def delete_apartment(*, session: Session = Depends(get_session), apartment_id: int):
    db_apartment = session.get(User, apartment_id)
    if not db_apartment:
        raise HTTPException(status_code=404, detail="Apartment not found")
    session.delete(db_apartment)
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
    if len(item.user_ids) == 0:
        raise HTTPException(status_code=400, detail="Item must have at least one user")
    users = session.exec(select(User).where(User.id.in_ item.user_ids)).all()

    db_item = Item.model_validate(item)
    db_item.users = list(users)
    session.add(db_item)
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
