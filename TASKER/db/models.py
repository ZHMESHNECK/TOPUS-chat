from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, declarative_base, relationship
from sqlalchemy import BigInteger, func, VARCHAR, DateTime, Integer, ForeignKey
from pydantic import field_validator
from datetime import datetime, timezone
from TASKER.api.schemas.users import Role, StatusFriend
Base = declarative_base()


role_enum = ENUM('user', 'admin', 'todo_owner', name='role')
status_enum = ENUM('pending', 'accepted', name='status')


class FriendshipDB(Base):
    __tablename__ = 'friendship'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_name: Mapped[str] = mapped_column(
        VARCHAR, ForeignKey('user.username'))
    friend_name: Mapped[str] = mapped_column(
        VARCHAR, ForeignKey('user.username'))

    user = relationship('UserDB', back_populates='friends',
                        foreign_keys=[user_name])
    friend = relationship('UserDB', foreign_keys=[friend_name])


class FriendRequestDB(Base):
    __tablename__ = 'friend_request'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    sender_name: Mapped[str] = mapped_column(
        VARCHAR, ForeignKey('user.username'))
    receiver_name: Mapped[str] = mapped_column(
        VARCHAR, ForeignKey('user.username'))
    status: Mapped[StatusFriend] = mapped_column(
        status_enum, default='pending')

    sender = relationship(
        'UserDB', back_populates='sent_requests', foreign_keys=[sender_name])
    receiver = relationship(
        'UserDB', back_populates='received_requests', foreign_keys=[receiver_name])


class UserDB(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(VARCHAR, unique=True, index=True)
    password: Mapped[str]
    online: Mapped[bool] = mapped_column(default=False)
    last_seen: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now())
    role: Mapped[Role] = mapped_column(role_enum, default=Role.user.value)

    friends = relationship(
        'FriendshipDB', back_populates='user', foreign_keys='FriendshipDB.user_name')
    sent_requests = relationship(
        'FriendRequestDB', back_populates='sender', foreign_keys='FriendRequestDB.sender_name')
    received_requests = relationship(
        'FriendRequestDB', back_populates='receiver', foreign_keys='FriendRequestDB.receiver_name')

    @field_validator('last_seen')
    def set_online_status(cls, v):
        v = True
        cls.last_seen = datetime.now(timezone.utc)
        return v
