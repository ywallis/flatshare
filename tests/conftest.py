from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from main import app
from src.models import Flat, Item, User
from src.utils import get_session


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def user_1():
    user = User(
        first_name="Yann",
        last_name="Wallis",
        email="y.w@g.c",
        flat_id=None,
        hashed_password="pw",
    )
    return user


@pytest.fixture
def user_2():
    user = User(
        first_name="Ilias",
        last_name="Trichopoulos",
        email="i.t@g.c",
        flat_id=None,
        hashed_password="pw",
    )
    return user


@pytest.fixture
def flat_1():
    flat = Flat(name="Olympus", users=[], items=[])
    return flat


@pytest.fixture
def item_1():
    item = Item(
        name="TV",
        flat_id=None,
        is_bill=False,
        initial_value=1000.0,
        purchase_date=datetime.strptime("2025-01-01", "%Y-%m-%d").date(),
        yearly_depreciation=0.2,
        minimum_value=None,
        minimum_value_pct=None,
    )
    return item

