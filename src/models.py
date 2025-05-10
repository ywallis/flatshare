from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel


class FlatBase(SQLModel):
    name: str


class Flat(FlatBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    users: list["User"] = Relationship(back_populates="flat")
    items: list["Item"] = Relationship(back_populates="flat")


class FlatPublic(FlatBase):
    id: int


class FlatPublicWithUsers(FlatPublic):
    users: list["UserPublic"] | None = Field(default_factory=list)


class FlatCreate(FlatBase):
    pass


class FlatUpdate(SQLModel):
    name: str | None = None


class UserItems(SQLModel, table=True):
    user_id: int | None = Field(foreign_key="user.id", primary_key=True)
    item_id: int | None = Field(foreign_key="item.id", primary_key=True)


class UserItemsPublic(SQLModel):
    user_id: int
    item_id: int


class UserBase(SQLModel):
    first_name: str
    last_name: str
    email: str
    flat_id: int | None = Field(default=None, foreign_key="flat.id")


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str = Field()
    flat: Flat | None = Relationship(back_populates="users")
    items: list["Item"] = Relationship(back_populates="users", link_model=UserItems)


class UserPublic(UserBase):
    id: int


class UserPublicWithItems(UserPublic):
    items: list["Item"] | None = Field(default_factory=list)


class UserCreate(UserBase):
    password: str


class UserUpdate(SQLModel):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    hashed_password: str | None = None
    flat_id: int | None = None


class ItemBase(SQLModel):
    name: str
    flat_id: int | None = Field(default=None, foreign_key="flat.id")
    is_bill: bool
    initial_value: float
    purchase_date: datetime
    yearly_depreciation: float
    minimum_value: float | None
    minimum_value_pct: float | None


class Item(ItemBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    flat: Flat = Relationship(back_populates="items")
    users: list[User] = Relationship(back_populates="items", link_model=UserItems)


class ItemPublic(ItemBase):
    id: int


class ItemPublicWithUsers(ItemPublic):
    users: list[User] | None = []


class ItemCreate(ItemBase):
    pass


class ItemUpdate(SQLModel):
    name: str | None = None
    is_bill: bool | None = None
    initial_value: float | None = None
    purchase_date: datetime | None = None
    yearly_depreciation: float | None = None
    minimum_value: float | None = None
    minimum_value_pct: float | None = None


class TransactionBase(SQLModel):
    creditor_id: int = Field(foreign_key="user.id")
    debtor_id: int = Field(foreign_key="user.id")
    item_id: int = Field(foreign_key="item.id")
    amount: float
    paid: bool


class Transaction(TransactionBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(SQLModel):
    paid: bool


class TransactionPublic(TransactionBase):
    id: int
