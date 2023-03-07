from logging import getLogger
from typing import Union

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

import settings
from db.crud import UserCRUD
from db.models import User
from db.session import get_db
from hashing import Hasher

logger = getLogger(__name__)

login_router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/token")


async def _get_user_by_email(email: str, db_session: AsyncSession):
    async with db_session.begin():
        user_crud = UserCRUD(db_session)
        return await user_crud.get_user_by_email(email=email)


async def authenticate_user(
    email: str, password: str, db_session: AsyncSession
) -> Union[User, None]:
    user = await _get_user_by_email(email=email, db=db_session)
    if user is None:
        return
    if not Hasher.verify_password(password, user.hashed_password):
        return
    return user


# Recieved token validation. Trying to get user data from recived token #


async def get_current_user_from_token(
    token: str = Depends(oauth2_scheme), db_session: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Couldn't validate credentials",
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, [settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        credentials_exception
    user = await _get_user_by_email(email=email, db_session=db_session)
    if user is None:
        raise credentials_exception
    return user
