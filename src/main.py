from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.middleware import LoggingMiddleware
from src.routers import flats, items, reset, transactions, users
from src.utils import create_db_and_tables


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Startup logic
    create_db_and_tables()
    yield
    # Shutdown logic (optional)


app = FastAPI(lifespan=lifespan)

app.add_middleware(LoggingMiddleware)


app.include_router(users.router)
app.include_router(flats.router)
app.include_router(items.router)
app.include_router(transactions.router)
app.include_router(reset.router)
