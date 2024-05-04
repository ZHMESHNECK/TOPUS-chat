from pydantic import BaseModel
from typing import Optional


class SearchRequest(BaseModel):
    request: Optional[str]

class UsersFromGroup(BaseModel):
    chat: int
    users: list[int]

class KickUser(BaseModel):
    chat: int
    user: int
