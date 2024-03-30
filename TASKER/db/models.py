from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, declarative_base, relationship
from sqlalchemy import BigInteger, func, VARCHAR, DateTime, Integer, ForeignKey, String
from datetime import datetime
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
                        foreign_keys=[user_name], lazy='selectin')
    friend = relationship('UserDB', foreign_keys=[friend_name])

    def as_dict(self):
        result = {}
        result['id'] = self.user.id
        result['username'] = self.user.username
        result['online'] = self.user.online
        result['last_seen'] = self.user.last_seen.strftime("%d-%m-%y %H:%M")
        return result


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
        'UserDB', back_populates='sent_requests', foreign_keys=[sender_name], lazy='selectin')
    receiver = relationship(
        'UserDB', back_populates='received_requests', foreign_keys=[receiver_name], lazy='selectin')

    notifications = relationship(
        'NotificationDB', back_populates='friend_request', cascade='all, delete-orphan')


class NotificationDB(Base):
    __tablename__ = 'notification'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(VARCHAR, ForeignKey('user.username'))
    friend_request_id: Mapped[int] = mapped_column(
        ForeignKey('friend_request.id'), nullable=True)
    message_id: Mapped[int] = mapped_column(
        ForeignKey('message.id'), nullable=True)
    is_read: Mapped[bool] = mapped_column(default=False)

    user = relationship(
        'UserDB', back_populates='notifications', foreign_keys=[username], lazy='selectin')
    friend_request = relationship(
        'FriendRequestDB', back_populates='notifications', foreign_keys=[friend_request_id], lazy='selectin')
    message = relationship(
        'MessageDB', back_populates='notifications', foreign_keys=[message_id])


class UserDB(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(VARCHAR, unique=True, index=True)
    password: Mapped[str]
    online: Mapped[bool] = mapped_column(default=False)
    last_seen: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now())
    role: Mapped[Role] = mapped_column(role_enum, default=Role.user.value)

    chats = relationship('ChatUser', back_populates='user')
    friends = relationship(
        'FriendshipDB', back_populates='user', foreign_keys='FriendshipDB.user_name', lazy='selectin')
    sent_requests = relationship(
        'FriendRequestDB', back_populates='sender', foreign_keys='FriendRequestDB.sender_name', lazy='selectin')
    received_requests = relationship(
        'FriendRequestDB', back_populates='receiver', foreign_keys='FriendRequestDB.receiver_name', lazy='selectin')
    notifications = relationship(
        'NotificationDB', back_populates='user', cascade='all, delete-orphan')

    def as_dict(self, fields=None):
        result = {}
        columns = self.__table__.columns
        if fields:
            columns = [c for c in columns if c.name in fields]
        for column in columns:
            value = getattr(self, column.name)
            # Перевіряємо, чи значення є об'єктом datetime
            if isinstance(value, datetime):
                # Конвертуємо об'єкт datetime у рядок
                # result[column.name] = value.strftime("%Y-%m-%d %H:%M")
                result[column.name] = value.strftime("%d-%m-%y %H:%M")
            else:
                result[column.name] = value
        return result


class Chat(Base):
    __tablename__ = 'chat'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    chat: Mapped[str] = mapped_column(VARCHAR, index=True)

    users = relationship('ChatUser', back_populates='chat')
    messages = relationship('MessageDB', back_populates='chat')


class ChatUser(Base):
    __tablename__ = 'chat_users'

    chat_id = mapped_column(Integer, ForeignKey('chat.id'), primary_key=True)
    user_id = mapped_column(Integer, ForeignKey('user.id'), primary_key=True)

    chat = relationship('Chat', back_populates='users')
    user = relationship('UserDB', back_populates='chats')


class MessageDB(Base):
    __tablename__ = 'message'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    chat_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey('chat.id'), index=True)
    sender_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('user.id'))
    message: Mapped[str] = mapped_column(String)

    chat = relationship('Chat', back_populates='messages')
    sender = relationship('UserDB')
    notifications = relationship(
        'NotificationDB', back_populates='message', cascade='all, delete-orphan')

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
