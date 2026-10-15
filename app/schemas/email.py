from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, EmailStr

class EmailCreate(BaseModel):
    who_sent: str | None = None
    subject: str | None = Field(default = None, min_length=1)
    body: str | None = Field(default = None, min_length=1)

class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str


class EmailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    who_sent: str | None
    subject: str | None
    body: str | None = Field(min_length=1)
    category: CategoryResponse
    matched_keywords: list[str]
    email_created: datetime
    filename: str | None = Field(default=None, min_length=1)
    source: str = Field(min_length=1)
    is_corrupted: bool = Field(default=False)


class EmailUpdate(BaseModel):
    category: str
