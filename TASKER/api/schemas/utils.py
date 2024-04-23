from pydantic import BaseModel, Field
from typing import Optional


class SearchRequest(BaseModel):
    request: Optional[str] = Field(min_length=2)


class CreateGroupTitle(BaseModel):
    title: Optional[str] = Field(min_length=3)

class UsersFromGroup(BaseModel):
    chat: Optional[int]
    users: Optional[list[int]]

class KickUser(BaseModel):
    chat: Optional[int]
    user: Optional[int]
