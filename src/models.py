from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel


class ApartmentBase(SQLModel):
    name: str


class Apartment(ApartmentBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    users: list["User"] = Relationship(back_populates="apartment")
    items: list["Item"] = Relationship(back_populates="apartment")


class ApartmentPublic(ApartmentBase):
    id: int


class ApartmentCreate(ApartmentBase):
    pass


class ApartmentUpdate(SQLModel):
    name: str | None = None


class UserBase(SQLModel):
    first_name: str
    last_name: str
    email: str
    apartment_id: int | None = Field(default=None, foreign_key="apartment.id")


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str = Field()
    apartment: Apartment | None = Relationship(back_populates="users")


class UserPublic(UserBase):
    id: int


class UserCreate(UserBase):
    password: str


class UserUpdate(SQLModel):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    hashed_password: str | None = None
    apartment_id: int | None = None


class ItemBase(SQLModel):
    name: str
    apartment_id: int | None = Field(default=None, foreign_key="apartment.id")
    is_bill: bool
    initial_value: float
    purchase_date: datetime
    yearly_depreciation: float
    minimum_value: float | None
    minimum_value_pct: float | None


class Item(ItemBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    apartment: Apartment = Relationship(back_populates="items")


class ItemPublic(ItemBase):
    id: int


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
