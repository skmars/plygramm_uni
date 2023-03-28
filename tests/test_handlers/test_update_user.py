import json
from uuid import uuid4

import pytest

from db.models import UserRole
from tests.conftest import create_test_auth_headers_for_user


@pytest.mark.parametrize(
    "user_roles",
    [
        [
            UserRole.ROLE_USER_SIMPLE,
            UserRole.ROLE_USER_SUPERADMIN,
        ],
        [
            UserRole.ROLE_USER_SUPERADMIN,
        ],
        [
            UserRole.ROLE_USER_ADMIN,
        ],
        [
            UserRole.ROLE_USER_SIMPLE,
        ],
    ],
)
async def test_update_user(
    client, create_user_in_database, get_user_from_database, user_roles
):
    user_data = {
        "user_id": uuid4(),
        "name": "Richard",
        "surname": "Hunter",
        "email": "guest_raven@clan.com",
        "is_active": True,
        "hashed_password": "Raven123",
        "roles": user_roles,
    }

    new_user_data = {
        "name": "Petra",
        "surname": "Hunter",
        "email": "hunter_raven@clan.com",
        "is_active": True,
    }
    await create_user_in_database(**user_data)
    resp = client.patch(
        f'/user/?user_id={user_data["user_id"]}',
        data=json.dumps(new_user_data),
        headers=create_test_auth_headers_for_user(user_data["email"]),
    )
    assert resp.status_code == 200
    resp_data = resp.json()
    assert resp_data["updated_user_id"] == str(user_data["user_id"])
    users_from_db = await get_user_from_database(user_data["user_id"])
    user_from_db = dict(users_from_db[0])
    assert user_from_db["name"] == new_user_data["name"]
    assert user_from_db["email"] == new_user_data["email"]
    assert user_from_db["surname"] == user_data["surname"]
    assert user_from_db["is_active"] is new_user_data["is_active"]
    assert user_from_db["user_id"] == user_data["user_id"]


async def test_update_user_check_only_one_updated(
    client, create_user_in_database, get_user_from_database
):
    user_data0 = {
        "user_id": uuid4(),
        "name": "Styrbjorn",
        "surname": "Jarl",
        "email": "old_jarl_raven@clan.com",
        "is_active": True,
        "hashed_password": "Raven123",
        "roles": [UserRole.ROLE_USER_SIMPLE],
    }
    user_data1 = {
        "user_id": uuid4(),
        "name": "Gunnar",
        "surname": "Smith",
        "email": "smith_raven@clan.com",
        "is_active": True,
        "hashed_password": "Raven123",
        "roles": [UserRole.ROLE_USER_SIMPLE],
    }
    user_data2 = {
        "user_id": uuid4(),
        "name": "Valka",
        "surname": "Witch",
        "email": "witch_raven@clan.com",
        "is_active": True,
        "hashed_password": "Raven123",
        "roles": [UserRole.ROLE_USER_SIMPLE],
    }
    user_data_updated = {
        "name": "Basim",
        "surname": "Assasin",
        "email": "hidden@one.com",
    }
    for user_data in [user_data0, user_data1, user_data2]:
        await create_user_in_database(**user_data)
    resp = client.patch(
        f"/user/?user_id={user_data0['user_id']}",
        data=json.dumps(user_data_updated),
        headers=create_test_auth_headers_for_user(user_data["email"]),
    )
    assert resp.status_code == 200
    resp_data = resp.json()
    assert resp_data["updated_user_id"] == str(user_data0["user_id"])
    users_from_db = await get_user_from_database(user_data0["user_id"])
    user_from_db = dict(users_from_db[0])
    assert user_from_db["name"] == user_data_updated["name"]
    assert user_from_db["surname"] == user_data_updated["surname"]
    assert user_from_db["email"] == user_data_updated["email"]
    assert user_from_db["is_active"] == user_data0["is_active"]
    assert user_from_db["user_id"] == user_data0["user_id"]

    # check if only one user was updated
    users_from_db = await get_user_from_database(user_data1["user_id"])
    user_from_db = dict(users_from_db[0])
    assert user_from_db["name"] == user_data1["name"]
    assert user_from_db["surname"] == user_data1["surname"]
    assert user_from_db["email"] == user_data1["email"]
    assert user_from_db["is_active"] == user_data1["is_active"]
    assert user_from_db["user_id"] == user_data1["user_id"]

    users_from_db = await get_user_from_database(user_data2["user_id"])
    user_from_db = dict(users_from_db[0])
    assert user_from_db["name"] == user_data2["name"]
    assert user_from_db["surname"] == user_data2["surname"]
    assert user_from_db["email"] == user_data2["email"]
    assert user_from_db["is_active"] == user_data2["is_active"]
    assert user_from_db["user_id"] == user_data2["user_id"]


@pytest.mark.parametrize(
    "user_data_updated, expected_status_code, expected_detail",
    [
        ({}, 422, {"detail": "At least one parametr to update should be provided"}),
        ({"name": "333"}, 422, {"detail": "Name should contain only letters"}),
        # (
        #     {"name": ""},
        #     422,
        #     {"detail": "At least one parametr to update should be provided"},
        # ),
        (
            {"name": ""},
            422,
            {
                "detail": [
                    {
                        "ctx": {"limit_value": 3},
                        "loc": ["body", "name"],
                        "msg": "ensure this value has at least 3 characters",
                        "type": "value_error.any_str.min_length",
                    }
                ]
            },
        ),
        (
            {"surname": ""},
            422,
            {
                "detail": [
                    {
                        "loc": ["body", "surname"],
                        "msg": "ensure this value has at least 1 characters",
                        "type": "value_error.any_str.min_length",
                        "ctx": {"limit_value": 1},
                    }
                ]
            },
        ),
        ({"surname": "333"}, 422, {"detail": "Surname should contain only letters"}),
        (
            {"email": ""},
            422,
            {
                "detail": [
                    {
                        "loc": ["body", "email"],
                        "msg": "value is not a valid email address",
                        "type": "value_error.email",
                    }
                ]
            },
        ),
        (
            {"email": "333"},
            422,
            {
                "detail": [
                    {
                        "loc": ["body", "email"],
                        "msg": "value is not a valid email address",
                        "type": "value_error.email",
                    }
                ]
            },
        ),
    ],
)
async def test_update_user_validation_error(
    client,
    create_user_in_database,
    user_data_updated,
    expected_status_code,
    expected_detail,
):
    user_data = {
        "user_id": uuid4(),
        "name": "Alfred",
        "surname": "King",
        "email": "king@britania.com",
        "is_active": True,
        "hashed_password": "Raven123",
        "roles": [UserRole.ROLE_USER_SIMPLE],
    }
    await create_user_in_database(**user_data)
    resp = client.patch(
        f"/user/?user_id={user_data['user_id']}",
        data=json.dumps(user_data_updated),
        headers=create_test_auth_headers_for_user(user_data["email"]),
    )
    assert resp.status_code == expected_status_code
    resp_data = resp.json()
    assert resp_data == expected_detail


async def test_update_user_id_validation_error(client, create_user_in_database):
    user_data = {
        "user_id": uuid4(),
        "name": "Soma",
        "surname": "Jarlscona",
        "email": "jarlscona_grantsh@clan.com",
        "is_active": True,
        "hashed_password": "Raven123",
        "roles": [UserRole.ROLE_USER_SIMPLE],
    }
    await create_user_in_database(**user_data)
    user_data_to_update = {
        "name": "Richard",
        "surname": "Lord",
        "email": "lord@wessexs.com",
    }
    invalid_user_id = 123
    resp = client.patch(
        f"/user/?user_id={invalid_user_id}",
        data=json.dumps(user_data_to_update),
        headers=create_test_auth_headers_for_user(user_data["email"]),
    )
    assert resp.status_code == 422
    data_from_response = resp.json()
    assert data_from_response == {
        "detail": [
            {
                "loc": ["query", "user_id"],
                "msg": "value is not a valid uuid",
                "type": "type_error.uuid",
            }
        ]
    }


async def test_update_user_id_not_found(client, create_user_in_database):
    user_data = {
        "user_id": uuid4(),
        "name": "Soma",
        "surname": "Jarlscona",
        "email": "jarlscona_grantsh@clan.com",
        "is_active": True,
        "hashed_password": "Raven123",
        "roles": [UserRole.ROLE_USER_SIMPLE],
    }
    await create_user_in_database(**user_data)
    user_data_to_update = {
        "name": "Richard",
        "surname": "Lord",
        "email": "lord@wessexs.com",
    }
    another_user_id = uuid4()
    resp = client.patch(
        f"/user/?user_id={another_user_id}",
        data=json.dumps(user_data_to_update),
        headers=create_test_auth_headers_for_user(user_data["email"]),
    )
    assert resp.status_code == 404
    data_from_response = resp.json()
    assert data_from_response == {
        "detail": f"User with id {another_user_id} doesn't exist"
    }


async def test_update_user_duplicate_mail_error(client, create_user_in_database):
    user_data0 = {
        "user_id": uuid4(),
        "name": "Ivar",
        "surname": "Boneless",
        "email": "frenetic@warrior.com",
        "is_active": True,
        "hashed_password": "Ragnar124",
        "roles": [UserRole.ROLE_USER_SIMPLE],
    }
    user_data1 = {
        "user_id": uuid4(),
        "name": "Ubba",
        "surname": "Fairfull",
        "email": "ragnar@warrior.com",
        "is_active": True,
        "hashed_password": "Ragnar124",
        "roles": [UserRole.ROLE_USER_SIMPLE],
    }
    user_data_updated = {"email": user_data1["email"]}
    for user_data in [user_data0, user_data1]:
        await create_user_in_database(**user_data)
    resp = client.patch(
        f"/user/?user_id={user_data0['user_id']}",
        data=json.dumps(user_data_updated),
        headers=create_test_auth_headers_for_user(user_data["email"]),
    )
    assert resp.status_code == 503
    assert (
        'duplicate key value violates unique constraint "users_email_key"'
        in resp.json()["detail"]
    )
