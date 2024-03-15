from typing import Any, Dict
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime
from enum import Enum


class Role(Enum):
    user = 'user'
    admin = 'admin'
    todo_owner = 'todo_owner'


class User(BaseModel):
    username: str = Field()
    password: str = Field()
    online: bool = Field(default=False)
    last_seen: datetime = Field(default=datetime.utcnow())
    role: Role = Field(default=Role.user)


class Login(BaseModel):
    username: str = Field()
    password: str = Field()

    @field_validator('username')
    def validate_username(cls, v: str):
        if not (2 <= len(v) <= 25) or not v.isalnum():
            raise ValueError('Нікнейм повинен бути в межах від 2 до 25 літер')
        return v

    @field_validator('password')
    def validate_paswwor(cls, v: str):
        if len(v) < 8:
            raise ValueError('Пароль повинен бути не менше 8 літер')
        return v


class Registration(BaseModel):
    username: str = Field()
    password: str = Field()
    re_password: str = Field()

    @field_validator('username')
    def validate_username(cls, v: str):
        if not (2 <= len(v) <= 25) or not v.isalnum():
            raise ValueError('Нікнейм повинен бути в межах від 2 до 25 літер')
        return v

    @field_validator('password')
    def validate_password(cls, v: str):
        if len(v) < 8:
            raise ValueError('Пароль повинен бути не менше ніж 8 літер')
        return v

    @field_validator('re_password')
    def validate_re_password(cls, v: str, values: Dict[str, Any]):
        if v != values.data.get('password'):
            raise ValueError('Паролі не збігаються')
        return values
