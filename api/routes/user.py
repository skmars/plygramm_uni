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
from api.handlers.user import check_user_permissions
from api.schemas import CreateUser
from api.schemas import DeleteUserResponse
from api.schemas import ShowUser
from api.schemas import UpdateUserRequest
from api.schemas import UpdateUserResponse
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
    user_to_delete = await _get_user_by_id(user_id=user_id, db_session=db_session)
    if user_to_delete is None:
        raise HTTPException(
            status_code=404, detail=f"User with id {user_id} doesn't exist"
        )
    if not check_user_permissions(
        target_user=user_to_delete,
        current_user=current_user,
    ):
        raise HTTPException(status_code=403, detail="Not allowed.")
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
    user_to_update = await _get_user_by_id(user_id, db_session)
    if user_to_update is None:
        raise HTTPException(
            status_code=404, detail=f"User with id {user_id} doesn't exist"
        )
    if user_id != current_user.user_id:
        if check_user_permissions(
            target_user=user_to_update, current_user=current_user
        ):
            raise HTTPException(status_code=403, detail="Forbidden.")

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


@user_router.patch("/admin_privilege", response_model=UpdateUserResponse)
async def grant_admin_privilages(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    if not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Forbidden")
    if current_user.user_id == user_id:
        raise HTTPException(
            status_code=400, detail="It's impossible to grant privileges to yourself"
        )
    user_to_grant = await _get_user_by_id(user_id, db)
    if user_to_grant.is_admin or user_to_grant.is_superadmin:
        raise HTTPException(
            status_code=409,
            detail=f"User with id {user_id} is already an admin",
        )

    if user_to_grant is None:
        raise HTTPException(status_code=404, detail=f"User with id{user_id} not found")
    updated_user_roles = {"roles": user_to_grant.add_admin_privilages()}
    try:
        updated_user_roles = await _update_user(
            user_params_to_update=updated_user_roles,
            db_session=db,
            user_id=user_id,
        )
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f"Database error: {err}")
    return UpdateUserResponse(updated_user_id=user_id)


@user_router.delete("/admin_privilege", response_model=UpdateUserResponse)
async def revoke_admin_privileges(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    if not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Forbidden")
    user_to_revoke_admon_priviileges = await _get_user_by_id(user_id, db)
    if not user_to_revoke_admon_priviileges.is_admin:
        raise HTTPException(
            status_code=409, detail=f"User with id {user_id} is not an admin"
        )
    if user_to_revoke_admon_priviileges is None:
        raise HTTPException(status_code=404, detail=f"User with id{user_id} not found")
    if current_user.user_id == user_id:
        raise HTTPException(
            status_code=400, detail="It's impossible to grant privileges to yourself"
        )
    updated_user_roles = {
        "roles": user_to_revoke_admon_priviileges.revoke_admin_privileges()
    }
    try:
        updated_user_roles = await _update_user(
            user_params_to_update=updated_user_roles,
            db_session=db,
            user_id=user_id,
        )
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f"Database error: {err}")
    return UpdateUserResponse(updated_user_id=user_id)
