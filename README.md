# eagle-api
Eagle Bank REST API

## Running locally

```bash
docker-compose -p eagle-api up --build -d
```

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- pgAdmin: http://localhost:5050

---

## Testing with Swagger UI (`/docs`)

Open http://localhost:8000/docs in your browser.

---

### 1. Create a user — `POST /v1/users`

No auth required. Expand the endpoint, click **Try it out**, paste:

```json
{
  "name": "Alice Smith",
  "email": "alice@example.com",
  "password": "password123",
  "phoneNumber": "+447911123456",
  "address": {
    "line1": "1 Test Street",
    "town": "London",
    "county": "Greater London",
    "postcode": "SW1A 1AA"
  }
}
```

Expected: **201** with the user object including an `id` (e.g. `usr-a1b2c3d4`). Copy the `id`.

---

### 2. Login — `POST /v1/auth/login`

```json
{
  "email": "alice@example.com",
  "password": "password123"
}
```

Expected: **200**

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

Copy the `access_token` value.

---

### 3. Authorise Swagger

Click the **Authorize** button (top-right of the `/docs` page), paste the token into the **bearerAuth** field, click **Authorize**, then **Close**.

All subsequent requests will include `Authorization: Bearer <token>` automatically.

---

### 4. Get own user — `GET /v1/users/{userId}`

Set `userId` to the `id` returned in step 1.

Expected: **200** with the full user object.

---

### 5. Try to get another user — `GET /v1/users/{userId}`

Set `userId` to any other value, e.g. `usr-00000000`.

Expected: **403**

```json
{ "message": "You do not have permission to access this user" }
```

---

### 6. Update user — `PATCH /v1/users/{userId}`

Set `userId` to your own `id`. All fields are optional — only send what you want to change:

```json
{
  "name": "Alice Updated"
}
```

Expected: **200** with updated user object.

---

### 7. Delete user — `DELETE /v1/users/{userId}`

Set `userId` to your own `id`.

Expected: **204** (empty body).

> Note: deletion is blocked with **409** if the user has accounts. Complete step 7 before creating accounts, or create a fresh user to test deletion.

---

### Error cases to verify

| Action | Expected |
|---|---|
| `POST /v1/users` with the same email again | **409** `A user with this email already exists` |
| `POST /v1/users` missing required fields | **400** with `details` array listing each missing field |
| `POST /v1/auth/login` with wrong password | **401** `Invalid credentials` |
| Any protected endpoint without authorising | **403** (Swagger sends no header if not authorised) |
| `GET /v1/users/{userId}` with someone else's `userId` | **403** `You do not have permission to access this user` |

---

## Accounts (`/v1/accounts`)

All accounts endpoints require the bearer token from the login step. Ensure Swagger is authorised first.

### 8. Create an account — `POST /v1/accounts`

```json
{
  "name": "My Current Account",
  "accountType": "personal"
}
```

Expected: **201** with the account object. Copy the `accountNumber` (e.g. `01123456`).

### 9. List accounts — `GET /v1/accounts`

No body. Expected: **200**

```json
{
  "accounts": [
    { "accountNumber": "01123456", "sortCode": "10-10-10", "balance": "0.00", ... }
  ]
}
```

### 10. Get account — `GET /v1/accounts/{accountNumber}`

Set `accountNumber` to the value from step 8.

Expected: **200** with the account object.

### 11. Update account — `PATCH /v1/accounts/{accountNumber}`

```json
{
  "name": "My Renamed Account"
}
```

Expected: **200** with updated `name`.

### 12. Delete account — `DELETE /v1/accounts/{accountNumber}`

Expected: **204** (empty body).

> Note: deletion is blocked with **409** if the account has transactions. Delete transactions first or use a fresh account.

### Accounts error cases

| Action | Expected |
|---|---|
| `GET /v1/accounts/{accountNumber}` for another user's account | **403** |
| `GET /v1/accounts/00000000` (non-existent) | **404** `Account not found` |
| `DELETE` an account that has transactions | **409** |

