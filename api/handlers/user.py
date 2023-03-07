from logging import getLogger
from typing import Union
from uuid import UUID

from fastapi import APIRouter

from api.models import CreateUser
from api.models import ShowUser
from db.crud import UserCRUD
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
        )
        return ShowUser(
            user_id=user.user_id,
            name=user.name,
            surname=user.surname,
            email=user.email,
            is_active=user.is_active,
        )


async def _get_user_by_id(user_id, db_session) -> Union[ShowUser, None]:
    async with db_session.begin():
        user_crud = UserCRUD(db_session)
        user = await user_crud.get_user_by_id(user_id=user_id)  # SQLAlchemy object
        if user is not None:
            return ShowUser(
                user_id=user.user_id,
                name=user.name,
                surname=user.surname,
                email=user.email,
                is_active=user.is_active,
            )


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
