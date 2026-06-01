from tests.conftest import BASE_USER


async def test_create_user_returns_201(client):
    resp = await client.post("/v1/users", json=BASE_USER)
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"].startswith("usr-")
    assert body["email"] == BASE_USER["email"]
    assert body["name"] == BASE_USER["name"]
    # Password must never appear in responses
    assert "password" not in body
    assert "passwordHash" not in body


async def test_create_user_duplicate_email_returns_409(client):
    await client.post("/v1/users", json=BASE_USER)
    resp = await client.post("/v1/users", json=BASE_USER)
    assert resp.status_code == 409
    assert "already exists" in resp.json()["message"]


async def test_create_user_missing_fields_returns_400(client):
    resp = await client.post("/v1/users", json={"email": "incomplete@example.com"})
    assert resp.status_code == 400
    body = resp.json()
    assert "details" in body
    missing = [d["field"] for d in body["details"]]
    assert "name" in missing


async def test_login_returns_token(client, test_user):
    payload, _ = test_user
    resp = await client.post(
        "/v1/auth/login",
        json={"email": payload["email"], "password": payload["password"]},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


async def test_login_wrong_password_returns_401(client, test_user):
    payload, _ = test_user
    resp = await client.post(
        "/v1/auth/login",
        json={"email": payload["email"], "password": "wrongpassword"},
    )
    assert resp.status_code == 401
    assert resp.json()["message"] == "Invalid credentials"


async def test_get_own_user_returns_200(client, test_user, auth_headers):
    _, user_data = test_user
    resp = await client.get(f"/v1/users/{user_data['id']}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == user_data["id"]


async def test_get_other_user_returns_403(client, auth_headers):
    resp = await client.get("/v1/users/usr-00000000", headers=auth_headers)
    assert resp.status_code == 403


async def test_get_user_without_token_returns_403(client, test_user):
    _, user_data = test_user
    resp = await client.get(f"/v1/users/{user_data['id']}")
    assert resp.status_code == 403


async def test_patch_user_updates_name(client, test_user, auth_headers):
    _, user_data = test_user
    resp = await client.patch(
        f"/v1/users/{user_data['id']}",
        json={"name": "Alice Updated"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Alice Updated"


async def test_delete_user_returns_204(client, test_user, auth_headers):
    _, user_data = test_user
    resp = await client.delete(f"/v1/users/{user_data['id']}", headers=auth_headers)
    assert resp.status_code == 204


async def test_delete_user_with_account_returns_409(
    client, test_user, auth_headers, test_account
):
    _, user_data = test_user
    resp = await client.delete(f"/v1/users/{user_data['id']}", headers=auth_headers)
    assert resp.status_code == 409
    assert "accounts" in resp.json()["message"].lower()
