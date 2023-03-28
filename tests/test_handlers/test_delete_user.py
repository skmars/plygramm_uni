from uuid import uuid4

import pytest

from db.models import UserRole
from tests.conftest import create_test_auth_headers_for_user


async def test_delete_user(client, create_user_in_database, get_user_from_database):
    user_data = {
        "user_id": uuid4(),
        "name": "Randvi",
        "surname": "Jarlscona",
        "email": "jarlscona_raven@clan.com",
        "is_active": True,
        "hashed_password": "Raven123",
        "roles": [UserRole.ROLE_USER_SIMPLE],
    }
    await create_user_in_database(**user_data)
    resp = client.delete(
        f'/user/?user_id={user_data["user_id"]}',
        headers=create_test_auth_headers_for_user(user_data["email"]),
    )
    assert resp.status_code == 200
    assert resp.json() == {"deleted_user_id": str(user_data["user_id"])}
    users_from_db = await get_user_from_database(user_data["user_id"])
    users_from_db = dict(users_from_db[0])
    assert users_from_db["name"] == user_data["name"]
    assert users_from_db["surname"] == user_data["surname"]
    assert users_from_db["email"] == user_data["email"]
    assert users_from_db["is_active"] is False
    assert users_from_db["user_id"] == user_data["user_id"]


async def test_delete_user_not_found(client, create_user_in_database):
    user_to_delete = {
        "user_id": uuid4(),
        "name": "Rollo",
        "surname": "Warrior",
        "email": "warrior_noble@fr.com",
        "is_active": True,
        "hashed_password": "Loyal1777",
        "roles": [UserRole.ROLE_USER_SIMPLE],
    }
    admin_user_data = {
        "user_id": uuid4(),
        "name": "Randvi",
        "surname": "Jarlscona",
        "email": "jarlscona_admin@clan.com",
        "is_active": True,
        "hashed_password": "Raven123",
        "roles": [UserRole.ROLE_USER_SIMPLE, UserRole.ROLE_USER_SUPERADMIN],
    }
    await create_user_in_database(**admin_user_data)
    await create_user_in_database(**user_to_delete)
    user_id_not_exist = uuid4()
    resp = client.delete(
        f"/user/?user_id={user_id_not_exist}",
        headers=create_test_auth_headers_for_user(admin_user_data["email"]),
    )
    assert resp.status_code == 404
    assert resp.json() == {"detail": f"User with id {user_id_not_exist} doesn't exist"}


async def test_delete_user_validation_error(client, create_user_in_database):
    user_data = {
        "user_id": uuid4(),
        "name": "Randvi",
        "surname": "Jarlscona",
        "email": "jarlscona_raven@clan.com",
        "is_active": True,
        "hashed_password": "Raven123",
        "roles": [UserRole.ROLE_USER_SIMPLE],
    }
    await create_user_in_database(**user_data)
    resp = client.delete(
        "/user/?user_id=333",
        headers=create_test_auth_headers_for_user(user_data["email"]),
    )
    assert resp.status_code == 422
    resp_data = resp.json()
    assert resp_data == {
        "detail": [
            {
                "loc": ["query", "user_id"],
                "msg": "value is not a valid uuid",
                "type": "type_error.uuid",
            }
        ]
    }


async def test_delete_user_bad_credentilas(client, create_user_in_database):
    user_data = {
        "user_id": uuid4(),
        "name": "Randvi",
        "surname": "Jarlscona",
        "email": "jarlscona_raven@clan.com",
        "is_active": True,
        "hashed_password": "Raven123",
        "roles": [UserRole.ROLE_USER_SIMPLE],
    }
    await create_user_in_database(**user_data)
    user_id = uuid4()
    resp = client.delete(
        f"/user/?user_id={user_id}",
        headers=create_test_auth_headers_for_user(user_data["email"] + "extra_str"),
    )
    assert resp.status_code == 401
    assert resp.json() == {"detail": "Couldn't validate credentials"}


async def test_delete_user_not_authenticated(client, create_user_in_database):
    user_data = {
        "user_id": uuid4(),
        "name": "Randvi",
        "surname": "Jarlscona",
        "email": "jarlscona_raven@clan.com",
        "is_active": True,
        "hashed_password": "Raven123",
        "roles": [UserRole.ROLE_USER_SIMPLE],
    }
    await create_user_in_database(**user_data)
    user_id = uuid4()
    resp = client.delete(f"/user/?user_id={user_id}")
    assert resp.status_code == 401
    assert resp.json() == {"detail": "Not authenticated"}


@pytest.mark.parametrize(
    "user_roles_list",
    [
        [UserRole.ROLE_USER_SIMPLE, UserRole.ROLE_USER_ADMIN],
    ],
)
async def test_delete_user_by_privilage(
    client, create_user_in_database, get_user_from_database, user_roles_list
):
    user_to_delete = {
        "user_id": uuid4(),
        "name": "Rollo",
        "surname": "Warrior",
        "email": "warrior_noble@fr.com",
        "is_active": True,
        "hashed_password": "Loyal1777",
        "roles": [UserRole.ROLE_USER_SIMPLE],
    }

    user_data = {
        "user_id": uuid4(),
        "name": "RandviAdmin",
        "surname": "Jarlscona",
        "email": "admin_raven@clan.com",
        "is_active": True,
        "hashed_password": "Raven123",
        "roles": user_roles_list,
    }
    await create_user_in_database(**user_data)
    await create_user_in_database(**user_to_delete)
    resp = client.delete(
        f"/user/?user_id={user_to_delete['user_id']}",
        headers=create_test_auth_headers_for_user(user_data["email"]),
    )
    assert resp.status_code == 200
    assert resp.json() == {"deleted_user_id": str(user_to_delete["user_id"])}
    users_from_db = await get_user_from_database(user_to_delete["user_id"])
    user_from_db = dict(users_from_db[0])
    assert user_from_db["user_id"] == user_to_delete["user_id"]
    assert user_from_db["name"] == user_to_delete["name"]
    assert user_from_db["surname"] == user_to_delete["surname"]
    assert user_from_db["email"] == user_to_delete["email"]
    assert user_from_db["is_active"] == False


@pytest.mark.parametrize(
    "user_to_delete, user_who_delete",
    [
        (
            {
                "user_id": uuid4(),
                "name": "Rollo",
                "surname": "Warrior",
                "email": "warrior_noble@fr.com",
                "is_active": True,
                "hashed_password": "Loyal1777",
                "roles": [UserRole.ROLE_USER_SIMPLE],
            },
            {
                "user_id": uuid4(),
                "name": "RandviAdmin",
                "surname": "Jarlscona",
                "email": "admin_raven@clan.com",
                "is_active": True,
                "hashed_password": "Raven123",
                "roles": [UserRole.ROLE_USER_SIMPLE],
            },
        ),
        (
            {
                "user_id": uuid4(),
                "name": "Rollo",
                "surname": "Warrior",
                "email": "warrior_noble@fr.com",
                "is_active": True,
                "hashed_password": "Loyal1777",
                "roles": [UserRole.ROLE_USER_SIMPLE, UserRole.ROLE_USER_SUPERADMIN],
            },
            {
                "user_id": uuid4(),
                "name": "RandviAdmin",
                "surname": "Jarlscona",
                "email": "admin_raven@clan.com",
                "is_active": True,
                "hashed_password": "Raven123",
                "roles": [UserRole.ROLE_USER_SIMPLE, UserRole.ROLE_USER_ADMIN],
            },
        ),
        (
            {
                "user_id": uuid4(),
                "name": "Rollo",
                "surname": "Warrior",
                "email": "warrior_noble@fr.com",
                "is_active": True,
                "hashed_password": "Loyal1777",
                "roles": [UserRole.ROLE_USER_SIMPLE, UserRole.ROLE_USER_ADMIN],
            },
            {
                "user_id": uuid4(),
                "name": "RandviAdmin",
                "surname": "Jarlscona",
                "email": "admin_raven@clan.com",
                "is_active": True,
                "hashed_password": "Raven123",
                "roles": [UserRole.ROLE_USER_SIMPLE, UserRole.ROLE_USER_ADMIN],
            },
        ),
    ],
)
async def test_user_delete_another_user_not_allowed(
    client, create_user_in_database, user_to_delete, user_who_delete
):

    await create_user_in_database(**user_who_delete)
    await create_user_in_database(**user_to_delete)
    resp = client.delete(
        f"/user/?user_id={user_to_delete['user_id']}",
        headers=create_test_auth_headers_for_user(user_who_delete["email"]),
    )
    assert resp.status_code == 403


async def test_reject_delete_superadmin(
    client, create_user_in_database, get_user_from_database
):
    user_to_delete = {
        "user_id": uuid4(),
        "name": "Rollo",
        "surname": "Warrior",
        "email": "warrior_noble@fr.com",
        "is_active": True,
        "hashed_password": "Loyal1777",
        "roles": [UserRole.ROLE_USER_SUPERADMIN],
    }
    await create_user_in_database(**user_to_delete)
    resp = client.delete(
        f"/user/?user_id={user_to_delete['user_id']}",
        headers=create_test_auth_headers_for_user(user_to_delete["email"]),
    )
    assert resp.status_code == 406
    assert resp.json() == {"detail": "Superadmin can't be deleted via API"}
    user_from_db = await get_user_from_database(user_to_delete["user_id"])
    assert UserRole.ROLE_USER_SUPERADMIN in dict(user_from_db[0])["roles"]
