from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from app.deps import SessionDep
from app.models.user import UserCreate, UserPublic, UsersPublic
from app.services import user_service

router = APIRouter(tags=["users"])


@router.get("/users", operation_id="listUsers", response_model=UsersPublic)
def list_users(
    session: SessionDep,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> UsersPublic:
    """List users (paginated)."""
    return user_service.list_users(session, limit=limit, offset=offset)


@router.post("/users", operation_id="createUser", response_model=UserPublic, status_code=201)
def create_user(session: SessionDep, data: UserCreate) -> UserPublic:
    """Create a user."""
    return user_service.create_user(session, data)


@router.get("/users/{user_id}", operation_id="getUserById", response_model=UserPublic)
def get_user(session: SessionDep, user_id: int) -> UserPublic:
    """Fetch a single user by id."""
    user = user_service.get_user(session, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
