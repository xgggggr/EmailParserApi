
from pydantic import BaseModel

class CategoryStat(BaseModel):
    category: str
    count: int
