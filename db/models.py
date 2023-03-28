import uuid
from enum import Enum

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base


Base = declarative_base()

#########################
#  Table Classes in DB #
#########################


class UserRole(str, Enum):
    ROLE_USER_SIMPLE = "ROLE_USER_SIMPLE"
    ROLE_USER_ADMIN = "ROLE_USER_ADMIN"
    ROLE_USER_SUPERADMIN = "ROLE_USER_SUPERADMIN"


class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean, default=True)
    hashed_password = Column(String, nullable=False)
    roles = Column(ARRAY(String), nullable=False)

    @property
    def is_superadmin(self) -> bool:
        return UserRole.ROLE_USER_SUPERADMIN in self.roles

    @property
    def is_admin(self) -> bool:
        return UserRole.ROLE_USER_ADMIN in self.roles

    def add_admin_privilages(self):
        if not self.is_admin:
            return {*self.roles, UserRole.ROLE_USER_ADMIN}

    def revoke_admin_privileges(self):
        if self.is_admin:
            return {role for role in self.roles if role != UserRole.ROLE_USER_ADMIN}
