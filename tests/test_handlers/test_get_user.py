from uuid import uuid4

from tests.conftest import create_test_auth_headers_for_user


async def test_get_user(client, create_user_in_database, get_user_from_database):
    user_data = {
        "user_id": uuid4(),
        "name": "Soma",
        "surname": "Jarlscona",
        "email": "jarlscona_grantsh@clan.com",
        "is_active": True,
        "hashed_password": "Raven123",
    }
    await create_user_in_database(**user_data)
    resp = client.get(
        f'/user/?user_id={user_data["user_id"]}',
        headers=create_test_auth_headers_for_user(user_data["email"]),
    )
    assert resp.status_code == 200
    users_from_response = resp.json()
    assert users_from_response["name"] == user_data["name"]
    assert users_from_response["surname"] == user_data["surname"]
    assert users_from_response["email"] == user_data["email"]
    assert users_from_response["user_id"] == str(user_data["user_id"])


async def test_get_user_id_validation_error(client, create_user_in_database):
    user_data = {
        "user_id": uuid4(),
        "name": "Soma",
        "surname": "Jarlscona",
        "email": "jarlscona_grantsh@clan.com",
        "is_active": True,
        "hashed_password": "Raven123",
    }
    invalid_user_id = 123
    await create_user_in_database(**user_data)
    resp = client.delete(
        f"/user/?user_id={invalid_user_id}",
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


async def test_get_user_id_not_found(client, create_user_in_database):
    user_data = {
        "user_id": uuid4(),
        "name": "Soma",
        "surname": "Jarlscona",
        "email": "jarlscona_grantsh@clan.com",
        "is_active": True,
        "hashed_password": "Raven123",
    }
    another_user_id = uuid4()
    await create_user_in_database(**user_data)
    resp = client.delete(
        f"/user/?user_id={another_user_id}",
        headers=create_test_auth_headers_for_user(user_data["email"]),
    )
    data_from_response = resp.json()
    assert data_from_response == {
        "detail": f"User with id {another_user_id} doesn't exist"
    }
