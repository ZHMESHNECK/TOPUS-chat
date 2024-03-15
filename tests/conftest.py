from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from fastapi.testclient import TestClient
from TASKER.core.config import get_session, engine, POSTGRES_URI
from TASKER.db.models import Base
from httpx import ASGITransport, AsyncClient
from main import topus
import logging
import pytest


def pytest_configure(config):
    logging.basicConfig(level=logging.WARNING, filename='check_db_log.log',
                        filemode='w', format="%(asctime)s %(levelname)s %(message)s")


engine_test = create_async_engine(POSTGRES_URI, poolclass=NullPool)
async_session_maker = async_sessionmaker(
    engine_test, class_=AsyncSession, expire_on_commit=False
)


async def override_session():
    async with async_session_maker() as session:
        yield session

topus.dependency_overrides[get_session] = override_session


@pytest.fixture(autouse=True, scope='module')
async def lifespan():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope='function')
async def client():
    app_client = TestClient(topus)
    async with AsyncClient(transport=ASGITransport(app=app_client.app), base_url='http://test') as ac:
        yield ac
