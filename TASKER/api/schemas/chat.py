from pydantic import BaseModel, Field
from TASKER.api.schemas.users import Role


class Chat(BaseModel):
    id: int
    chat: str


class GroupChatCreate(BaseModel):
    user: int
    chat: str
    status: Role = Field(default=Role.user)
