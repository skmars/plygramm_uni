from datetime import datetime
from datetime import timedelta
from typing import Optional

from jose import jwt

import settings


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    data_to_encode = data.copy()
    if expires_delta:
        expires_at = datetime.utcnow() + expires_delta
    else:
        expires_at = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    data_to_encode.update({"exp": expires_at})
    encoded_jwt = jwt.encode(data_to_encode, settings.SECRET_KEY, settings.ALGORITHM)
    return encoded_jwt
