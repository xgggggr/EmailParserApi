from typing import Annotated

from fastapi import Depends, APIRouter
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.database import get_db
from app.schemas.stats import CategoryStat

router = APIRouter()

@router.get('', response_model=list[CategoryStat])
async def get_stats(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Category.name, func.count(models.Email.id)).outerjoin(models.Email).group_by(models.Category.name).order_by(func.count(models.Email.id).desc()))
    return [CategoryStat(category=name, count=c) for name, c in result.all()]
