from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from fastapi.testclient import TestClient
from TASKER.core.security import hash_password
from TASKER.core.config import get_session
from TASKER.api.schemas.users import StatusFriend
from TASKER.db.models import Base, UserDB, FriendshipDB, FriendRequestDB
from dotenv import load_dotenv
from httpx import ASGITransport, AsyncClient
from main import topus
import logging
import pytest
import os

load_dotenv('.env-dev')


# PostgreSQL
host = os.getenv('T_POSTGRES_HOST')
port = os.getenv('T_POSTGRES_PORT')
database = os.getenv('T_POSTGRES_DB')
user = os.getenv('T_POSTGRES_USER')
password = os.getenv('T_POSTGRES_PASSWORD')
TEST_POSTGRES_URI = f'postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}'


def pytest_configure(config):
    logging.basicConfig(level=logging.WARNING, filename='check_db_log.log',
                        filemode='w', format="%(asctime)s %(levelname)s %(message)s")


engine_test = create_async_engine(TEST_POSTGRES_URI, poolclass=NullPool)
async_session_maker = async_sessionmaker(
    engine_test, class_=AsyncSession, expire_on_commit=False
)


async def override_session():
    async with async_session_maker() as session:
        yield session

topus.dependency_overrides[get_session] = override_session


@pytest.fixture(scope='module')
async def default_friendship():
    try:
        async with async_session_maker() as session:
            test_user3 = UserDB(
                username="TestUserDBFriend3",
                password=hash_password("12345678"),
            )
            test_user4 = UserDB(
                username="TestUserDBFriend4",
                password=hash_password("12345678"),
            )

            friend_req = FriendRequestDB(
                sender_name=test_user3.username,
                receiver_name=test_user4.username,
                status=StatusFriend.accepted.value
            )
            friendship = FriendshipDB(
                user_name=test_user3.username,
                friend_name=test_user4.username
            )

            session.add_all([test_user3, test_user4, friend_req, friendship])
            await session.commit()
    except Exception as e:
        print(f"An error occurred while adding default user: {e}")


async def defaults_user():
    try:
        async with async_session_maker() as session:
            test_user = UserDB(
                username="TestUserDB",
                password=hash_password("12345678"),
            )
            test_user2 = UserDB(
                username="TestUserDB2",
                password=hash_password("12345678"),
            )

            session.add_all([test_user, test_user2])
            await session.commit()
    except Exception as e:
        print(f"An error occurred while adding default user: {e}")


@pytest.fixture(autouse=True, scope='module')
async def lifespan():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await defaults_user()
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope='function')
async def client():
    app_client = TestClient(topus)
    async with AsyncClient(transport=ASGITransport(app=app_client.app), base_url='http://test') as ac:
        yield ac
