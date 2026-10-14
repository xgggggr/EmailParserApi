from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, EmailStr

from app.models import Category


class EmailCreate(BaseModel):
    who_sent: EmailStr | None = None
    subject: str | None = Field(default = None, min_length=1)
    body: str | None = Field(default = None, min_length=1)

class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str


class EmailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    who_sent: EmailStr
    subject: str | None
    body: str | None = Field(min_length=1)
    category: CategoryRead
    matched_keywords: list[str]
    email_created: datetime
    filename: str | None = Field(default=None, min_length=1)
    source: str = Field(min_length=1)
    is_corrupted: bool = Field(default=False)


class EmailUpdate(BaseModel):
    category: str




class ClassificatorResult(BaseModel):
    category: str
    match_keywords: list[str]