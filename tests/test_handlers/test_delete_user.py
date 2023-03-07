from uuid import uuid4

from tests.conftest import create_test_auth_headers_for_user


async def test_delete_user(client, create_user_in_database, get_user_from_database):
    user_data = {
        "user_id": uuid4(),
        "name": "Randvi",
        "surname": "Jarlscona",
        "email": "jarlscona_raven@clan.com",
        "is_active": True,
        "hashed_password": "Raven123",
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
    user_data = {
        "user_id": uuid4(),
        "name": "Randvi",
        "surname": "Jarlscona",
        "email": "jarlscona_raven@clan.com",
        "is_active": True,
        "hashed_password": "Raven123",
    }
    await create_user_in_database(**user_data)
    user_id = uuid4()
    resp = client.delete(
        f"/user/?user_id={user_id}",
        headers=create_test_auth_headers_for_user(user_data["email"]),
    )
    assert resp.status_code == 404
    assert resp.json() == {"detail": f"User with id {user_id} doesn't exist"}


async def test_delete_user_validation_error(client, create_user_in_database):
    user_data = {
        "user_id": uuid4(),
        "name": "Randvi",
        "surname": "Jarlscona",
        "email": "jarlscona_raven@clan.com",
        "is_active": True,
        "hashed_password": "Raven123",
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
    }
    await create_user_in_database(**user_data)
    user_id = uuid4()
    resp = client.delete(
        f"/user/?user_id={user_id}",
        headers=create_test_auth_headers_for_user(user_data["email"] + "extra_str"),
    )
    assert resp.status_code == 401
    assert resp.json() == {"detail": "Couldn't validate credentials"}


async def test_delete_user_not_authenticatied(client, create_user_in_database):
    user_data = {
        "user_id": uuid4(),
        "name": "Randvi",
        "surname": "Jarlscona",
        "email": "jarlscona_raven@clan.com",
        "is_active": True,
        "hashed_password": "Raven123",
    }
    await create_user_in_database(**user_data)
    user_id = uuid4()
    resp = client.delete(f"/user/?user_id={user_id}")
    assert resp.status_code == 401
    assert resp.json() == {"detail": "Not authenticated"}
