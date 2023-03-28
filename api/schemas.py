import re
import uuid
from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel
from pydantic import constr
from pydantic import EmailStr
from pydantic import validator

LETTER_MATCH_PATTERN = re.compile(r"^[a-z-A-Z\-]+$")


# Adjust class to make sure pydantic will convert even non dict objects to json
class AdjustPydanticModel(BaseModel):
    class Config:
        orm_mode = True


# class as a response model to be shown to user
class ShowUser(AdjustPydanticModel):
    user_id: uuid.UUID
    name: str
    surname: str
    email: EmailStr
    is_active: bool


# class model to process input request
class CreateUser(BaseModel):
    name: str
    surname: str
    email: EmailStr
    password: str

    @validator("name")
    def validate_name(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail="Name should contain only letters"
            )
        return value

    @validator("surname")
    def validate_surname(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail="Surname should contain only letters"
            )
        return value


class DeleteUserResponse(BaseModel):
    deleted_user_id: uuid.UUID


class UpdateUserResponse(BaseModel):
    updated_user_id: uuid.UUID


class UpdateUserRequest(BaseModel):
    name: Optional[constr(min_length=3)]
    surname: Optional[constr(min_length=1)]
    email: Optional[EmailStr]

    @validator("name")
    def validate_name(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail="Name should contain only letters"
            )
        return value

    @validator("surname")
    def validate_surname(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail="Surname should contain only letters"
            )
        return value


class Token(BaseModel):
    access_token: str
    token_type: str
