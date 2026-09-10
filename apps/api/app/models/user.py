from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    name: str
    email: str


class User(UserBase, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class UserCreate(UserBase):
    pass


class UserPublic(UserBase):
    id: int
    created_at: datetime


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int
