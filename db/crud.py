from typing import Union
from uuid import UUID

from sqlalchemy import and_
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User
from .models import UserRole

##########################################
#  CRUD-Class operations to deal with DB #
##########################################


class UserCRUD:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user(
        self,
        name: str,
        surname: str,
        email: str,
        hashed_password: str,
        roles: list[UserRole],
    ) -> User:
        new_user = User(
            name=name,
            surname=surname,
            email=email,
            hashed_password=hashed_password,
            roles=roles,
        )
        self.db_session.add(new_user)
        await self.db_session.flush()
        return new_user

    async def delete_user(self, user_id: UUID) -> Union[UUID, None]:
        query = (
            update(User)
            .where(and_(User.user_id == user_id, User.is_active == True))
            .values(is_active=False)
            .returning(User.user_id)
        )
        res = await self.db_session.execute(query)  # send coroutine to event loop
        deleted_user_id_row = res.fetchone()

        if deleted_user_id_row is not None:
            return deleted_user_id_row[0]

    async def get_user_by_id(self, user_id: UUID) -> Union[User, None]:
        query = select(User).where(User.user_id == user_id)
        res = await self.db_session.execute(query)
        user_row = res.fetchone()

        if user_row is not None:
            return user_row[0]

    async def get_user_by_email(self, email: str) -> Union[User, None]:
        query = select(User).where(User.email == email)
        res = await self.db_session.execute(query)
        user_row = res.fetchone()

        if user_row is not None:
            return user_row[0]

    async def update_user(
        self, user_id: UUID, **user_params_to_update
    ) -> Union[User, None]:
        query = (
            update(User)
            .where(and_(User.user_id == user_id, User.is_active == True))
            .values(user_params_to_update)
            .returning(User.user_id)
        )
        res = await self.db_session.execute(query)
        updated_user__id_row = res.fetchone()

        if updated_user__id_row is not None:
            return updated_user__id_row[0]
