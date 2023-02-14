import json

import pytest


async def test_create_user(client, get_user_from_database):
    user_data = {
        "name": "Randvi",
        "surname": "Jarlscona",
        "email": "jarlscona_raven@clan.com",
    }
    resp = client.post("/user/", data=json.dumps(user_data))
    data_from_resp = resp.json()
    assert resp.status_code == 200
    assert data_from_resp["name"] == user_data["name"]
    assert data_from_resp["surname"] == user_data["surname"]
    assert data_from_resp["email"] == user_data["email"]
    assert data_from_resp["is_active"] is True
    users_from_db = await get_user_from_database(data_from_resp["user_id"])
    assert len(users_from_db) == 1
    users_from_db = dict(users_from_db[0])
    assert data_from_resp["name"] == user_data["name"]
    assert data_from_resp["surname"] == user_data["surname"]
    assert data_from_resp["email"] == user_data["email"]
    assert data_from_resp["is_active"] is True
    assert str(users_from_db["user_id"]) == data_from_resp["user_id"]


async def test_create_user_duplicate_mail(client, get_user_from_database):
    user_data = {"name": "Ivar", "surname": "Boneless", "email": "ragnar@warrior.com"}
    duplicate_mail_user_data = {
        "name": "Ubba",
        "surname": "Fairfull",
        "email": "ragnar@warrior.com",
    }
    resp = client.post("/user/", data=json.dumps(user_data))
    data_from_resp = resp.json()
    assert resp.status_code == 200
    assert data_from_resp["name"] == user_data["name"]
    assert data_from_resp["surname"] == user_data["surname"]
    assert data_from_resp["email"] == user_data["email"]
    assert data_from_resp["is_active"] is True
    users_from_db = await get_user_from_database(data_from_resp["user_id"])
    assert len(users_from_db) == 1
    users_from_db = dict(users_from_db[0])
    assert data_from_resp["name"] == user_data["name"]
    assert data_from_resp["surname"] == user_data["surname"]
    assert data_from_resp["email"] == user_data["email"]
    assert data_from_resp["is_active"] is True
    assert str(users_from_db["user_id"]) == data_from_resp["user_id"]
    # next user with the same email
    resp = client.post("/user/", data=json.dumps(duplicate_mail_user_data))
    assert resp.status_code == 503
    assert (
        'duplicate key value violates unique constraint "users_email_key"'
        in resp.json()["detail"]
    )


@pytest.mark.parametrize(
    "user_data_to_create, expected_status_code, expected_detail",
    [
        (
            {},
            422,
            {
                "detail": [
                    {
                        "loc": ["body", "name"],
                        "msg": "field required",
                        "type": "value_error.missing",
                    },
                    {
                        "loc": ["body", "surname"],
                        "msg": "field required",
                        "type": "value_error.missing",
                    },
                    {
                        "loc": ["body", "email"],
                        "msg": "field required",
                        "type": "value_error.missing",
                    },
                ]
            },
        ),
        (
            {"name": 333, "surname": 333, "email": "eeeee"},
            422,
            {"detail": "Name should contain only letters"},
        ),
        (
            {"name": "Dag", "surname": 333, "email": "eeeee"},
            422,
            {"detail": "Surname should contain only letters"},
        ),
        (
            {"name": "Dag", "surname": "Major", "email": 333},
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
async def test_create_user_validation_error(
    client, user_data_to_create, expected_status_code, expected_detail
):
    resp = client.post("/user/", data=json.dumps(user_data_to_create))
    assert resp.status_code == expected_status_code
    resp_data = resp.json()
    assert resp_data == expected_detail
