from typing import Optional
from pydantic import BaseModel, Field, field_validator


class SearchRequest(BaseModel):
    request: Optional[str] = Field(min_length=2)
