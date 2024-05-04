from pydantic import BaseModel


class Chat(BaseModel):
    id: int
    title: str


class CreateGroupTitle(BaseModel):
    title: str
