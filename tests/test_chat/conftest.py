from fastapi.testclient import TestClient
from TASKER.core.config import get_session
from TASKER.db.models import Base
from tests.utils import default_friendship, default_groups, defaults_user, async_session_maker, engine_test
from main import topus
import logging
import pytest


# logging
def pytest_configure(config):
    logging.basicConfig(level=logging.WARNING, filename='check_db_log.log',
                        filemode='w', format="%(asctime)s %(levelname)s %(message)s")


async def override_session():
    async with async_session_maker() as session:
        yield session

topus.dependency_overrides[get_session] = override_session


@pytest.fixture(autouse=True, scope='session')
async def lifespan():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await defaults_user()
    await default_friendship()
    await default_groups()
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope='function')
async def client():
    return TestClient(topus)
