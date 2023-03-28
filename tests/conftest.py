import asyncio
import os
from datetime import timedelta
from typing import Any
from typing import Generator

import asyncpg
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from starlette.testclient import TestClient

import settings
from db.models import UserRole
from db.session import get_db
from main import app
from security import create_access_token
from settings import HOME_DIRECTORY


CLEAN_TABLES = [
    "users",
]


@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def run_migrations():
    os.chdir(f"{HOME_DIRECTORY}/tests")
    os.system(f"{HOME_DIRECTORY}/venv/bin/alembic --version")
    # uncomment while first run
    # os.system(f"{HOME_DIRECTORY}/venv/bin/alembic init migrations")
    os.system(
        f"{HOME_DIRECTORY}/venv/bin/alembic "
        f"revision --autogenerate -m 'running test migrations'"
    )
    os.system(f"{HOME_DIRECTORY}/venv/bin/alembic upgrade heads")


@pytest_asyncio.fixture(scope="session")
async def async_session_test():
    engine = create_async_engine(settings.TEST_DATABASE_URL, future=True, echo=True)
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    yield async_session


@pytest_asyncio.fixture(scope="function", autouse=True)
async def clean_tables(async_session_test):
    # clean data in all the tables before running test function
    async with async_session_test() as session:
        async with session.begin():
            for table_for_cleaning in CLEAN_TABLES:
                await session.execute(text(f"TRUNCATE TABLE {table_for_cleaning};"))


"""
Create a new FASTAPI TestClient that uses the 'db_session' fixture
to override the the 'get_db' dependency injected into to the routs.
"""


@pytest_asyncio.fixture(scope="function")
async def client() -> Generator[TestClient, Any, None]:
    async def _get_test_db():
        try:
            # create async engine for interaction with database
            test_async_engine = create_async_engine(
                settings.TEST_DATABASE_URL, future=True, echo=True
            )

            # create async session for interaction with database
            test_async_session = sessionmaker(
                test_async_engine, expire_on_commit=False, class_=AsyncSession
            )
            yield test_async_session()
        finally:
            pass

    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as client:
        yield client


# different source to check the real maintaince (temporate)
@pytest_asyncio.fixture(scope="session")
async def asyncpg_pool():
    pool = await asyncpg.create_pool(
        "".join(settings.TEST_DATABASE_URL.split("+asyncpg"))
    )
    yield pool
    pool.close()


@pytest_asyncio.fixture
async def get_user_from_database(asyncpg_pool):
    async def get_user_from_database_by_uuid(user_id: str):
        async with asyncpg_pool.acquire() as connection:
            return await connection.fetch(
                """SELECT * FROM users WHERE user_id = $1;""", user_id
            )

    return get_user_from_database_by_uuid


@pytest_asyncio.fixture
async def create_user_in_database(asyncpg_pool):
    async def create_user_in_database(
        user_id: str,
        name: str,
        surname: str,
        email: str,
        is_active: bool,
        hashed_password: str,
        roles: list[UserRole],
    ):
        async with asyncpg_pool.acquire() as connection:
            return await connection.execute(
                """INSERT INTO users VALUES ($1, $2, $3, $4, $5, $6, $7);""",
                user_id,
                name,
                surname,
                email,
                is_active,
                hashed_password,
                roles,
            )

    return create_user_in_database


def create_test_auth_headers_for_user(email: str) -> dict[str, str]:
    access_token = create_access_token(
        data={"sub": email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"Authorization": f"Bearer {access_token}"}
