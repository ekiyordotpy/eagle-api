import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.config import settings
from app.database import Base, get_db
from app.main import create_app


@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_tables():
    """Create all tables once before any test runs."""
    engine = create_async_engine(settings.DATABASE_URL, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def client():
    """Per-test AsyncClient with an isolated NullPool engine."""
    engine = create_async_engine(settings.DATABASE_URL, poolclass=NullPool)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    app = create_app()

    async def override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Clean slate before each test in case a previous run left data
        async with engine.begin() as conn:
            await conn.execute(text("TRUNCATE TABLE transactions, accounts, users CASCADE"))
        yield ac

    async with engine.begin() as conn:
        await conn.execute(text("TRUNCATE TABLE transactions, accounts, users CASCADE"))
    await engine.dispose()


# SHARED FIXTURES

BASE_USER = {
    "name": "Alice Smith",
    "email": "alice@example.com",
    "password": "password123",
    "phoneNumber": "+447911123456",
    "address": {
        "line1": "1 Test Street",
        "town": "London",
        "county": "Greater London",
        "postcode": "SW1A 1AA",
    },
}


@pytest_asyncio.fixture
async def test_user(client):
    """Create a user and return (payload, response body)."""
    resp = await client.post("/v1/users", json=BASE_USER)
    assert resp.status_code == 201
    return BASE_USER, resp.json()


@pytest_asyncio.fixture
async def auth_headers(client, test_user):
    """Log in as the test user and return Authorization headers."""
    payload, _ = test_user
    resp = await client.post(
        "/v1/auth/login",
        json={"email": payload["email"], "password": payload["password"]},
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def test_account(client, auth_headers):
    """Create an account for the test user and return the response body."""
    resp = await client.post(
        "/v1/accounts",
        json={"name": "Test Account", "accountType": "personal"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    return resp.json()
