
from typing import Annotated

from fastapi import  Depends, APIRouter
from sqlalchemy import select


from app import models
from app.database import get_db

from app.schemas.email import CategoryResponse
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()



@router.get('/api/categories', response_model=list[CategoryResponse])
async def get_categories(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Category).order_by(models.Category.id))
    categories = result.scalars().all()
    return categories