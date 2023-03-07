from logging import getLogger
from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.handlers.auth import get_current_user_from_token
from api.handlers.user import _create_new_user
from api.handlers.user import _delete_user
from api.handlers.user import _get_user_by_id
from api.handlers.user import _update_user
from api.models import CreateUser
from api.models import DeleteUserResponse
from api.models import ShowUser
from api.models import UpdateUserRequest
from api.models import UpdateUserResponse
from db.models import User
from db.session import get_db

logger = getLogger(__name__)

user_router = APIRouter()

#############################################
# Endpoints for user #
############################################


@user_router.post("/", response_model=ShowUser)
async def create_user(
    body: CreateUser, db_session: AsyncSession = Depends(get_db)
) -> ShowUser:
    try:
        return await _create_new_user(body, db_session)
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f"Database error: {err}")


@user_router.delete("/", response_model=DeleteUserResponse)
async def delete_user(
    user_id: UUID,
    db_session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
) -> DeleteUserResponse:
    deleted_user_id = await _delete_user(user_id, db_session)
    if deleted_user_id is None:
        raise HTTPException(
            status_code=404, detail=f"User with id {user_id} doesn't exist"
        )
    return DeleteUserResponse(deleted_user_id=deleted_user_id)


@user_router.get("/", response_model=ShowUser)
async def get_user_by_id(
    user_id: UUID,
    db_session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
) -> ShowUser:
    user = await _get_user_by_id(user_id, db_session)
    if user is None:
        raise HTTPException(
            status_code=404, detail=f"User with id {user_id} doesn't exist"
        )
    return user


@user_router.patch("/", response_model=UpdateUserResponse)
async def update_user_by_id(
    user_id: UUID,
    body: UpdateUserRequest,
    db_session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
) -> UpdateUserResponse:
    user_params_to_update = body.dict(exclude_none=True)
    if user_params_to_update == {}:
        raise HTTPException(
            status_code=422, detail="At least one parametr to update should be provided"
        )
    user = await _get_user_by_id(user_id, db_session)
    if user is None:
        raise HTTPException(
            status_code=404, detail=f"User with id {user_id} doesn't exist"
        )
    try:
        updated_user_id = await _update_user(
            user_params_to_update=user_params_to_update,
            user_id=user_id,
            db_session=db_session,
        )
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f"Database error: {err}")
    return UpdateUserResponse(updated_user_id=updated_user_id)
