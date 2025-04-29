from collections.abc import Sequence
from fastapi import FastAPI
from sqlmodel import Field, SQLModel, Session, create_engine, select


class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    secret_name: str
    age: int | None = None


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)

SQLModel.metadata.create_all(engine)
session = Session(engine)
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/items/{id}")
async def get_item(id: int):
    return {"id": id}


@app.put("/heros/")
async def create_hero(name: str, secret_name: str, age: int | None = None):
    session.add(Hero(name=name, secret_name=secret_name, age=age))
    session.commit()

@app.get("/heros/")
def get_heroes() -> Sequence[Hero]:
   with Session(engine) as session:
        statement = select(Hero)
        results = session.exec(statement)
        heroes = results.all()
        return heroes 

