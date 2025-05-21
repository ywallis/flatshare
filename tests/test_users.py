from fastapi.testclient import TestClient
from sqlmodel import Session

from main import app
from src.models import User


def test_create_user(client: TestClient):
    response = client.post(
        "/users/",
        json={
            "first_name": "Yann",
            "last_name": "Wallis",
            "email": "y.w@g.c",
            "flat_id": "0",
            "password": "pw",
        },
    )
    app.dependency_overrides.clear()
    data = response.json()

    assert response.status_code == 200
    assert data["first_name"] == "Yann"
    assert data["last_name"] == "Wallis"
    assert data["email"] == "y.w@g.c"
    assert data["flat_id"] == 0


def test_read_user(client: TestClient, session: Session):
    user_1 = User(
        first_name="Yann",
        last_name="Wallis",
        email="y.w@g.c",
        flat_id=0,
        hashed_password="pw",
    )
    session.add(user_1)
    session.commit()
    session.refresh(user_1)
    db_user = session.get(User, user_1.id)
    if not db_user:
        raise Exception("User not found")
    assert db_user.first_name == "Yann"


    response = client.get(f"users/{user_1.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Yann"
    assert data["last_name"] == "Wallis"
    assert data["email"] == "y.w@g.c"
    assert data["flat_id"] == 0
