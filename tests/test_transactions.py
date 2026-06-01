async def test_deposit_returns_201_and_updates_balance(client, auth_headers, test_account):
    resp = await client.post(
        f"/v1/accounts/{test_account['accountNumber']}/transactions",
        json={"amount": 500, "currency": "GBP", "type": "deposit", "reference": "Salary"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"].startswith("tan-")
    assert body["type"] == "deposit"
    assert float(body["amount"]) == 500.0
    assert body["currency"] == "GBP"
    assert body["reference"] == "Salary"

    account_resp = await client.get(
        f"/v1/accounts/{test_account['accountNumber']}", headers=auth_headers
    )
    assert float(account_resp.json()["balance"]) == 500.0


async def test_withdrawal_returns_201_and_updates_balance(
    client, auth_headers, test_account
):
    await client.post(
        f"/v1/accounts/{test_account['accountNumber']}/transactions",
        json={"amount": 500, "currency": "GBP", "type": "deposit"},
        headers=auth_headers,
    )
    resp = await client.post(
        f"/v1/accounts/{test_account['accountNumber']}/transactions",
        json={"amount": 100, "currency": "GBP", "type": "withdrawal"},
        headers=auth_headers,
    )
    assert resp.status_code == 201

    account_resp = await client.get(
        f"/v1/accounts/{test_account['accountNumber']}", headers=auth_headers
    )
    assert float(account_resp.json()["balance"]) == 400.0


async def test_withdrawal_insufficient_funds_returns_422(
    client, auth_headers, test_account
):
    resp = await client.post(
        f"/v1/accounts/{test_account['accountNumber']}/transactions",
        json={"amount": 100, "currency": "GBP", "type": "withdrawal"},
        headers=auth_headers,
    )
    assert resp.status_code == 422
    assert "Insufficient funds" in resp.json()["message"]


async def test_deposit_amount_above_schema_limit_returns_400(
    client, auth_headers, test_account
):
    # amount > 10000 is rejected by Pydantic schema validation → 400
    resp = await client.post(
        f"/v1/accounts/{test_account['accountNumber']}/transactions",
        json={"amount": 10000.01, "currency": "GBP", "type": "deposit"},
        headers=auth_headers,
    )
    assert resp.status_code == 400


async def test_deposit_would_exceed_max_balance_returns_422(
    client, auth_headers, test_account
):
    # Fill balance to 10000
    await client.post(
        f"/v1/accounts/{test_account['accountNumber']}/transactions",
        json={"amount": 10000, "currency": "GBP", "type": "deposit"},
        headers=auth_headers,
    )
    # One more deposit should fail with 422 (business rule, not schema)
    resp = await client.post(
        f"/v1/accounts/{test_account['accountNumber']}/transactions",
        json={"amount": 1, "currency": "GBP", "type": "deposit"},
        headers=auth_headers,
    )
    assert resp.status_code == 422
    assert "maximum" in resp.json()["message"].lower()


async def test_list_transactions_returns_all(client, auth_headers, test_account):
    await client.post(
        f"/v1/accounts/{test_account['accountNumber']}/transactions",
        json={"amount": 500, "currency": "GBP", "type": "deposit"},
        headers=auth_headers,
    )
    await client.post(
        f"/v1/accounts/{test_account['accountNumber']}/transactions",
        json={"amount": 100, "currency": "GBP", "type": "withdrawal"},
        headers=auth_headers,
    )
    resp = await client.get(
        f"/v1/accounts/{test_account['accountNumber']}/transactions",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert len(resp.json()["transactions"]) == 2


async def test_get_transaction_returns_200(client, auth_headers, test_account):
    txn_resp = await client.post(
        f"/v1/accounts/{test_account['accountNumber']}/transactions",
        json={"amount": 200, "currency": "GBP", "type": "deposit"},
        headers=auth_headers,
    )
    txn_id = txn_resp.json()["id"]

    resp = await client.get(
        f"/v1/accounts/{test_account['accountNumber']}/transactions/{txn_id}",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["id"] == txn_id


async def test_get_nonexistent_transaction_returns_404(client, auth_headers, test_account):
    resp = await client.get(
        f"/v1/accounts/{test_account['accountNumber']}/transactions/tan-00000000",
        headers=auth_headers,
    )
    assert resp.status_code == 404
    assert "not found" in resp.json()["message"].lower()
