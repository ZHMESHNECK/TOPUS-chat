from pydantic import BaseModel, Field
from typing import Optional


class SearchRequest(BaseModel):
    request: Optional[str] = Field(min_length=2)
