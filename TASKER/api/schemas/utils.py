from pydantic import BaseModel, Field
from typing import Optional


class SearchRequest(BaseModel):
    request: Optional[str]


class CreateGroupTitle(BaseModel):
    title: Optional[str]

class UsersFromGroup(BaseModel):
    chat: Optional[int]
    users: Optional[list[int]]

class KickUser(BaseModel):
    chat: Optional[int]
    user: Optional[int]
