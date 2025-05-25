from fastapi import FastAPI
from sqlmodel import SQLModel

from src.routers import flats, items, transactions, users, reset
from src.utils import engine


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


app = FastAPI()

app.include_router(users.router)
app.include_router(flats.router)
app.include_router(items.router)
app.include_router(transactions.router)
app.include_router(reset.router)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
