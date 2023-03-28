from logging import getLogger
from typing import Union
from uuid import UUID

from fastapi import APIRouter
from fastapi import HTTPException

from api.schemas import CreateUser
from api.schemas import ShowUser
from db.crud import User
from db.crud import UserCRUD
from db.models import UserRole
from hashing import Hasher

logger = getLogger(__name__)

user_router = APIRouter()

#############################################
# Handlers for user #
############################################


async def _create_new_user(body: CreateUser, db_session) -> ShowUser:
    async with db_session.begin():
        user_crud = UserCRUD(db_session)
        user = await user_crud.create_user(  # SQLAlchemy object
            name=body.name,
            surname=body.surname,
            email=body.email,
            hashed_password=Hasher.set_password_hashed(body.password),
            roles=[
                UserRole.ROLE_USER_SIMPLE,
            ],
        )
        return ShowUser(
            user_id=user.user_id,
            name=user.name,
            surname=user.surname,
            email=user.email,
            is_active=user.is_active,
        )


async def _get_user_by_id(user_id, db_session) -> Union[User, None]:
    async with db_session.begin():
        user_crud = UserCRUD(db_session)
        user = await user_crud.get_user_by_id(user_id=user_id)  # SQLAlchemy object
        if user is not None:
            return user


async def _delete_user(user_id, db_session) -> Union[UUID, None]:
    async with db_session.begin():
        user_crud = UserCRUD(db_session)
        deleted_user_id = await user_crud.delete_user(user_id=user_id)
        return deleted_user_id


async def _update_user(
    user_params_to_update: dict, user_id: UUID, db_session
) -> Union[UUID, None]:
    async with db_session.begin():
        user_crud = UserCRUD(db_session)
        updated_user_id = await user_crud.update_user(user_id, **user_params_to_update)
        return updated_user_id


def check_user_permissions(target_user: User, current_user: User) -> bool:
    if UserRole.ROLE_USER_SUPERADMIN in current_user.roles:
        raise HTTPException(
            status_code=406, detail="Superadmin can't be deleted via API"
        )
    if target_user.user_id != current_user.user_id:
        # if user has admin permissions
        if not {
            UserRole.ROLE_USER_ADMIN,
            UserRole.ROLE_USER_SUPERADMIN,
        }.intersection(current_user.roles):
            return False
        # if user as admin attempts to delete superadmin
        if (
            UserRole.ROLE_USER_SUPERADMIN in target_user.roles
            and UserRole.ROLE_USER_ADMIN in current_user.roles
        ):
            return False
        # if user has superadmin permissions
        if (
            UserRole.ROLE_USER_ADMIN in target_user.roles
            and UserRole.ROLE_USER_ADMIN in current_user.roles
        ):
            return False
    return True
