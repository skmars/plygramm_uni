from uuid import uuid4

import pytest

from db.models import UserRole
from tests.conftest import create_test_auth_headers_for_user


async def test_grant_admin_role_by_superadmin(
    client, create_user_in_database, get_user_from_database
):
    superadmin = {
        "user_id": uuid4(),
        "name": "Odin",
        "surname": "Harvy",
        "email": "the_one@god.com",
        "is_active": True,
        "hashed_password": "GOD1",
        "roles": [UserRole.ROLE_USER_SUPERADMIN],
    }
    user_to_grant_admin = {
        "user_id": uuid4(),
        "name": "Valka",
        "surname": "Witch",
        "email": "witch_raven@clan.com",
        "is_active": True,
        "hashed_password": "Witch123",
        "roles": [UserRole.ROLE_USER_SIMPLE],
    }
    await create_user_in_database(**superadmin)
    await create_user_in_database(**user_to_grant_admin)
    resp = client.patch(
        f"/user/admin_privilege/?user_id={user_to_grant_admin['user_id']}",
        headers=create_test_auth_headers_for_user(superadmin["email"]),
    )
    assert resp.status_code == 200
    data_from_json = resp.json()
    failed_to_revoke_admin_role = await get_user_from_database(
        data_from_json["updated_user_id"]
    )
    assert len(failed_to_revoke_admin_role) == 1
    failed_to_revoke_admin_role = dict(failed_to_revoke_admin_role[0])
    assert failed_to_revoke_admin_role["user_id"] == user_to_grant_admin["user_id"]
    assert UserRole.ROLE_USER_ADMIN in failed_to_revoke_admin_role["roles"]


async def test_revoke_admin_role_by_superadmin(
    client, create_user_in_database, get_user_from_database
):
    superadmin = {
        "user_id": uuid4(),
        "name": "Odin",
        "surname": "Harvy",
        "email": "the_one@god.com",
        "is_active": True,
        "hashed_password": "GOD1",
        "roles": [
            UserRole.ROLE_USER_SUPERADMIN,
        ],
    }
    user_to_revoke_admin_role = {
        "user_id": uuid4(),
        "name": "Valka",
        "surname": "Witch",
        "email": "witch_raven@clan.com",
        "is_active": True,
        "hashed_password": "Witch123",
        "roles": [UserRole.ROLE_USER_SIMPLE, UserRole.ROLE_USER_ADMIN],
    }
    await create_user_in_database(**superadmin)
    await create_user_in_database(**user_to_revoke_admin_role)
    resp = client.delete(
        f"/user/admin_privilege/?user_id={user_to_revoke_admin_role['user_id']}",
        headers=create_test_auth_headers_for_user(superadmin["email"]),
    )
    assert resp.status_code == 200
    data_from_json = resp.json()
    failed_to_revoke_admin_role = await get_user_from_database(
        data_from_json["updated_user_id"]
    )
    assert len(failed_to_revoke_admin_role) == 1
    failed_to_revoke_admin_role = dict(failed_to_revoke_admin_role[0])
    assert (
        failed_to_revoke_admin_role["user_id"] == user_to_revoke_admin_role["user_id"]
    )
    assert UserRole.ROLE_USER_ADMIN not in failed_to_revoke_admin_role["roles"]


@pytest.mark.parametrize(
    "roles_who_revoke",
    [
        [
            UserRole.ROLE_USER_SIMPLE,
            UserRole.ROLE_USER_ADMIN,
        ],
        [
            UserRole.ROLE_USER_SIMPLE,
        ],
    ],
)
async def test_revoke_admin_role_from_not_superadmin(
    client, create_user_in_database, get_user_from_database, roles_who_revoke
):
    superadmin = {
        "user_id": uuid4(),
        "name": "Odin",
        "surname": "Harvy",
        "email": "the_one@god.com",
        "is_active": True,
        "hashed_password": "GOD1",
        "roles": roles_who_revoke,
    }
    user_to_revoke_admin_role = {
        "user_id": uuid4(),
        "name": "Valka",
        "surname": "Witch",
        "email": "witch_raven@clan.com",
        "is_active": True,
        "hashed_password": "Witch123",
        "roles": [UserRole.ROLE_USER_SIMPLE, UserRole.ROLE_USER_ADMIN],
    }
    await create_user_in_database(**superadmin)
    await create_user_in_database(**user_to_revoke_admin_role)
    resp = client.delete(
        f"/user/admin_privilege/?user_id={user_to_revoke_admin_role['user_id']}",
        headers=create_test_auth_headers_for_user(superadmin["email"]),
    )
    assert resp.status_code == 403
    assert resp.json() == {"detail": "Forbidden"}
    failed_to_revoke_admin_role = await get_user_from_database(
        user_to_revoke_admin_role["user_id"]
    )
    assert len(failed_to_revoke_admin_role) == 1
    failed_to_revoke_admin_role = dict(failed_to_revoke_admin_role[0])
    assert (
        failed_to_revoke_admin_role["user_id"] == user_to_revoke_admin_role["user_id"]
    )
    assert UserRole.ROLE_USER_ADMIN in failed_to_revoke_admin_role["roles"]
