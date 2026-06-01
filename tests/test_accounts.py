async def test_create_account_returns_201(client, auth_headers):
    resp = await client.post(
        "/v1/accounts",
        json={"name": "My Account", "accountType": "personal"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["accountNumber"].startswith("01")
    assert len(body["accountNumber"]) == 8
    assert body["sortCode"] == "10-10-10"
    assert float(body["balance"]) == 0.0
    assert body["currency"] == "GBP"
    assert body["accountType"] == "personal"


async def test_list_accounts_returns_created_account(client, auth_headers, test_account):
    resp = await client.get("/v1/accounts", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["accounts"]) == 1
    assert body["accounts"][0]["accountNumber"] == test_account["accountNumber"]


async def test_list_accounts_empty_for_new_user(client, auth_headers):
    resp = await client.get("/v1/accounts", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["accounts"] == []


async def test_get_account_returns_200(client, auth_headers, test_account):
    resp = await client.get(
        f"/v1/accounts/{test_account['accountNumber']}", headers=auth_headers
    )
    assert resp.status_code == 200
    assert resp.json()["accountNumber"] == test_account["accountNumber"]


async def test_get_account_not_found_returns_404(client, auth_headers):
    resp = await client.get("/v1/accounts/01000000", headers=auth_headers)
    assert resp.status_code == 404
    assert "not found" in resp.json()["message"].lower()


async def test_get_account_other_user_returns_403(client, test_account):
    second = {
        "name": "Bob",
        "email": "bob@example.com",
        "password": "password123",
        "phoneNumber": "+447911999999",
        "address": {
            "line1": "2 Test St",
            "town": "London",
            "county": "Greater London",
            "postcode": "SW1A 1AA",
        },
    }
    await client.post("/v1/users", json=second)
    token_resp = await client.post(
        "/v1/auth/login", json={"email": "bob@example.com", "password": "password123"}
    )
    bob_headers = {"Authorization": f"Bearer {token_resp.json()['access_token']}"}

    resp = await client.get(
        f"/v1/accounts/{test_account['accountNumber']}", headers=bob_headers
    )
    assert resp.status_code == 403


async def test_patch_account_updates_name(client, auth_headers, test_account):
    resp = await client.patch(
        f"/v1/accounts/{test_account['accountNumber']}",
        json={"name": "Renamed Account"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Renamed Account"


async def test_delete_account_returns_204(client, auth_headers, test_account):
    resp = await client.delete(
        f"/v1/accounts/{test_account['accountNumber']}", headers=auth_headers
    )
    assert resp.status_code == 204


async def test_delete_account_with_transactions_returns_409(
    client, auth_headers, test_account
):
    await client.post(
        f"/v1/accounts/{test_account['accountNumber']}/transactions",
        json={"amount": 100, "currency": "GBP", "type": "deposit"},
        headers=auth_headers,
    )
    resp = await client.delete(
        f"/v1/accounts/{test_account['accountNumber']}", headers=auth_headers
    )
    assert resp.status_code == 409
