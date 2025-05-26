from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import SQLModel

from src.routers import flats, items, reset, transactions, users
from src.utils import engine


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Startup logic
    create_db_and_tables()
    yield
    # Shutdown logic (optional)


app = FastAPI(lifespan=lifespan)

app.include_router(users.router)
app.include_router(flats.router)
app.include_router(items.router)
app.include_router(transactions.router)
app.include_router(reset.router)
