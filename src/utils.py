from sqlmodel import Session, create_engine

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args, echo=True)


def get_session():
    with Session(engine) as session:
        yield session


def hash_password(password: str) -> str:
    return f"actuallynotahash{password}"
