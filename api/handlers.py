from logging import getLogger
from typing import Union
from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.models import CreateUser
from api.models import DeleteUserResponse
from api.models import ShowUser
from api.models import UpdateUserRequest
from api.models import UpdateUserResponse
from db.crud import UserCRUD
from db.session import get_db
from hashing import Hasher

logger = getLogger(__name__)

user_router = APIRouter()

#############################################
# Handlers and input points for user auth #
############################################

# TODO Separate points and handlers

# Handlers


async def _create_new_user(body: CreateUser, db) -> ShowUser:
    async with db as session:
        async with session.begin():
            user_crud = UserCRUD(session)
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


async def _get_user_by_id(user_id, db) -> Union[ShowUser, None]:
    async with db as session:
        async with session.begin():
            user_crud = UserCRUD(session)
            user = await user_crud.get_user_by_id(user_id=user_id)  # SQLAlchemy object
            if user is not None:
                return ShowUser(
                    user_id=user.user_id,
                    name=user.name,
                    surname=user.surname,
                    email=user.email,
                    is_active=user.is_active,
                )


async def _delete_user(user_id, db) -> Union[UUID, None]:
    async with db as session:
        async with session.begin():
            user_crud = UserCRUD(session)
            deleted_user_id = await user_crud.delete_user(user_id=user_id)
            return deleted_user_id


async def _update_user(
    user_params_to_update: dict, user_id: UUID, db
) -> Union[UUID, None]:
    async with db as session:
        async with session.begin():
            user_crud = UserCRUD(session)
            updated_user_id = await user_crud.update_user(
                user_id, **user_params_to_update
            )
            return updated_user_id


# Endpoints #


@user_router.post("/", response_model=ShowUser)
async def create_user(body: CreateUser, db: AsyncSession = Depends(get_db)) -> ShowUser:
    try:
        return await _create_new_user(body, db)
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f"Database error: {err}")


@user_router.delete("/", response_model=DeleteUserResponse)
async def delete_user(
    user_id: UUID, db: AsyncSession = Depends(get_db)
) -> DeleteUserResponse:
    deleted_user_id = await _delete_user(user_id, db)
    if deleted_user_id is None:
        raise HTTPException(
            status_code=404, detail=f"User with id {user_id} doesn't exist"
        )
    return DeleteUserResponse(deleted_user_id=deleted_user_id)


@user_router.get("/", response_model=ShowUser)
async def get_user_by_id(user_id: UUID, db: AsyncSession = Depends(get_db)) -> ShowUser:
    user = await _get_user_by_id(user_id, db)
    if user is None:
        raise HTTPException(
            status_code=404, detail=f"User with id {user_id} doesn't exist"
        )
    return user


@user_router.patch("/", response_model=UpdateUserResponse)
async def update_user_by_id(
    user_id: UUID, body: UpdateUserRequest, db: AsyncSession = Depends(get_db)
) -> UpdateUserResponse:
    user_params_to_update = body.dict(exclude_none=True)
    if user_params_to_update == {}:
        raise HTTPException(
            status_code=422, detail="At least one parametr to update should be provided"
        )
    user = await _get_user_by_id(user_id, db)
    if user is None:
        raise HTTPException(
            status_code=404, detail=f"User with id {user_id} doesn't exist"
        )
    try:
        updated_user_id = await _update_user(
            user_params_to_update=user_params_to_update, user_id=user_id, db=db
        )
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f"Database error: {err}")
    return UpdateUserResponse(updated_user_id=updated_user_id)
