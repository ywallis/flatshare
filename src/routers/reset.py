from fastapi import APIRouter, Depends
from sqlmodel import Session, SQLModel

from datetime import datetime
from src.models import Flat, Item, User
from src.utils import get_session

router = APIRouter()

user_1 = User(
    first_name="Yann",
    last_name="Wallis",
    email="y.w@g.c",
    flat_id=None,
    hashed_password="pw",
)

user_2 = User(
    first_name="Ilias",
    last_name="Trichopoulos",
    email="i.t@g.c",
    flat_id=None,
    hashed_password="pw",
)

flat_1 = Flat(name="Olympus")

item_1 = Item(
    name="TV",
    is_bill=False,
    initial_value=1000.0,
    purchase_date= datetime.strptime("2025-01-01", "%Y-%m-%d"),
    yearly_depreciation=0.2,
    minimum_value=None,
    minimum_value_pct=None,
)


@router.post("/reset/")
def reset_app(*, session: Session = Depends(get_session)):
    for table in reversed(SQLModel.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()

    session.add(user_1)
    session.add(user_2)
    session.commit()
    session.refresh(user_1)
    session.refresh(user_2)
    flat_1.users.append(user_1)
    session.add(flat_1)
    session.commit()
    session.refresh(flat_1)
    item_1.flat_id = flat_1.id
    item_1.users = flat_1.users
    session.add(item_1)
    session.commit()

    return {"deleted": True}
