from typing import Any, Dict, List
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone
from enum import Enum


class Role(Enum):
    user = 'user'
    admin = 'admin'
    todo_owner = 'todo_owner'


class StatusFriend(Enum):
    pending = 'pending'
    accepted = 'accepted'


class FriendRequest(BaseModel):
    sender_name: str
    receiver_name: str
    status: StatusFriend = Field(default=StatusFriend.pending)


class FriendShip(BaseModel):
    user_name: str
    friend_name: str


class User(BaseModel):
    username: str
    password: str
    online: bool = Field(default=False)
    last_seen: datetime = Field(default=datetime.now(timezone.utc))
    role: Role = Field(default=Role.user)


class Login(BaseModel):
    username: str
    password: str


class Registration(BaseModel):
    username: str
    password: str
    re_password: str

    @field_validator('username')
    def validate_username(cls, v: str):
        if not (3 <= len(v) <= 25) or not v.isalnum():
            raise ValueError('Нікнейм повинен бути в межах від 3 до 25 літер')
        return v

    @field_validator('password')
    def validate_password(cls, v: str):
        if len(v) < 8:
            raise ValueError('Пароль повинен бути не менше ніж 8 літер')
        return v

    @field_validator('re_password')
    def validate_re_password(cls, v: str, values: Dict[str, Any]):
        if values.data.get('password'):
            if v != values.data.get('password'):
                raise ValueError('Паролі не збігаються')
            return values
