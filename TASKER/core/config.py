from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData
from dotenv import load_dotenv
import logging
import os


load_dotenv('.env')


# jwt
secret_jwt = os.getenv('MY_SECRET_JWT')
algorithm = os.getenv('ALGORITHM')


# PostgreSQL
host = os.getenv('POSTGRES_HOST')
port = os.getenv('POSTGRES_PORT')
database = os.getenv('POSTGRES_DB')
user = os.getenv('POSTGRES_USER')
password = os.getenv('POSTGRES_PASSWORD')
POSTGRES_URI = f'postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}'


# SQLAlchemy
engine = create_async_engine(POSTGRES_URI)
metadata = MetaData()
SessionLocal = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession)


async def get_session():
    async with SessionLocal() as session:
        yield session


# Front-end
templates = Jinja2Templates(directory='TASKER/templates')


# Logging
logging.basicConfig(level=logging.WARNING, filename='check_db_log.log',
                    filemode='w', format="%(asctime)s %(levelname)s %(message)s", encoding='UTF-8')
