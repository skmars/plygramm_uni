from datetime import timedelta
from logging import getLogger

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

import settings
from api.handlers.auth import authenticate_user
from api.schemas import Token
from db.session import get_db
from security import create_access_token

logger = getLogger(__name__)

login_router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/token")


@login_router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db_session: AsyncSession = Depends(get_db),
):
    user = await authenticate_user(form_data.username, form_data.password, db_session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The username or password is incorrect.",
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "other_custom_data": [1, 2, 3, 4]},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}
