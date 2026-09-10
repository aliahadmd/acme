"""Business logic — routers stay thin; anything beyond CRUD belongs here."""

from sqlalchemy import func
from sqlmodel import Session, select

from app.models.user import User, UserCreate, UserPublic, UsersPublic


def list_users(session: Session, *, limit: int = 50, offset: int = 0) -> UsersPublic:
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    count = session.exec(select(func.count()).select_from(User)).one()
    return UsersPublic(
        data=[UserPublic.model_validate(user) for user in users],
        count=count,
    )


def create_user(session: Session, data: UserCreate) -> UserPublic:
    user = User.model_validate(data)
    session.add(user)
    session.commit()
    session.refresh(user)
    return UserPublic.model_validate(user)


def get_user(session: Session, user_id: int) -> UserPublic | None:
    user = session.get(User, user_id)
    return UserPublic.model_validate(user) if user else None
