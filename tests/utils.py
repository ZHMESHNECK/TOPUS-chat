from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from TASKER.core.security import hash_password
from TASKER.api.schemas.users import Role, StatusFriend
from TASKER.db.models import AdminsOfGroup, ChatDB, ChatUserDB, FriendRequestDB, FriendshipDB, UserDB
from dotenv import load_dotenv
import logging
import os


load_dotenv('.env-dev')

# PostgreSQL
host = os.getenv('T_POSTGRES_HOST')
port = os.getenv('T_POSTGRES_PORT')
database = os.getenv('T_POSTGRES_DB')
user = os.getenv('T_POSTGRES_USER')
password = os.getenv('T_POSTGRES_PASSWORD')
TEST_POSTGRES_URI = f'postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}'


engine_test = create_async_engine(TEST_POSTGRES_URI, poolclass=NullPool)
async_session_maker = async_sessionmaker(
    engine_test, class_=AsyncSession, expire_on_commit=False
)


async def default_groups():
    try:
        async with async_session_maker() as session:
            group1 = ChatDB(title='test_group1')
            group2 = ChatDB(title='test_group2')
            group3 = ChatDB(title='test_group3')
            session.add_all([group1, group2, group3])
            await session.commit()
            await session.refresh(group1)
            await session.refresh(group2)
            await session.refresh(group3)
            user1 = ChatUserDB(chat_id=group1.id, user_id=1)
            user2 = ChatUserDB(chat_id=group2.id, user_id=1)
            user3 = ChatUserDB(chat_id=group3.id, user_id=1)
            status1_ = AdminsOfGroup(user_id=1, chat_id=group1.id, status=Role.admin.value)
            status2_ = AdminsOfGroup(user_id=1, chat_id=group2.id, status=Role.admin.value)
            status3_ = AdminsOfGroup(user_id=1, chat_id=group3.id, status=Role.admin.value)
            status4_ = AdminsOfGroup(user_id=2, chat_id=group3.id, status=Role.user.value)
            session.add_all([user1, user2, user3, status1_, status2_, status3_, status4_])
            await session.commit()
    except Exception as e:
        logging.error(msg='default_groups', exc_info=True)
        print(f"An error occurred while adding default group: {e}")


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
            session.add_all([test_user3, test_user4])
            await session.commit()
            await session.refresh(test_user3)
            await session.refresh(test_user4)

            friend_req = FriendRequestDB(
                sender_id=test_user3.id,
                receiver_id=test_user4.id,
                status=StatusFriend.accepted.value
            )
            friendship1 = FriendshipDB(
                user_id=test_user3.id,
                friend_id=test_user4.id,
            )
            friendship2 = FriendshipDB(
                friend_id=test_user3.id,
                user_id=test_user4.id,
            )

            session.add_all(
                [test_user3, test_user4, friend_req, friendship1, friendship2])
            await session.commit()
    except Exception as e:
        logging.error(msg='default_friendship', exc_info=True)
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
