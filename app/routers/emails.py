from pathlib import Path
from typing import Annotated
from pydantic import WithJsonSchema

from fastapi import Depends, HTTPException, status, APIRouter, UploadFile, File
from sqlalchemy import select


from app import models
from app.logic.classificator import Classificator

from app.schemas.email import EmailCreate, EmailResponse, EmailUpdate, EmailPage
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.config import settings
from app.logic.EmailParsing import EmailParsing

router = APIRouter()
classifier = Classificator()
parser = EmailParsing()
BinaryFile = Annotated[UploadFile, WithJsonSchema({"type": "string", "format": "binary"})]
@router.post('', response_model=EmailResponse, status_code=status.HTTP_201_CREATED)
async def classify_email(email: EmailCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    category_name, keywords = classifier.categorise(email.subject, email.body)
    result = await db.execute(select(models.Category).where(models.Category.name == category_name))
    category = result.scalars().first()
    email = models.Email(who_sent = email.who_sent, subject = email.subject, body = email.body, matched_keywords = keywords, category = category)
    db.add(email)
    await db.commit()
    await db.refresh(email)
    return email

from fastapi import Query
from sqlalchemy import func


@router.get("", response_model=EmailPage)
async def list_emails(db: AsyncSession = Depends(get_db), category: str | None = None, limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0),):
    query = select(models.Email)
    count_query = select(func.count(models.Email.id))
    if category:
        query = query.join(models.Category).where(models.Category.name == category)
        count_query = count_query.join(models.Category).where(models.Category.name == category)

    total = await db.scalar(count_query)
    result = await db.scalars(query.order_by(models.Email.email_created.desc()).limit(limit).offset(offset))
    return {"items": result.all(), "total": total, "limit": limit, "offset": offset}

@router.get('/{email_id}', response_model=EmailResponse)
async def get_email(email_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Email).where(models.Email.id == email_id),)
    email = result.scalars().first()
    if email:
        return email
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found")

@router.patch('/{email_id}', response_model=EmailResponse)
async def change_category_of_email(email_id: int,email_data: EmailUpdate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Email).where(models.Email.id == email_id))
    email = result.scalars().first()
    if not email:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found")
    result2 =  await db.execute(select(models.Category).where(models.Category.name == email_data.category))
    category = result2.scalars().first()
    if not category:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=f"Нет категории {email_data.category}")
    email.category = category
    await db.commit()
    await db.refresh(email)
    return email

@router.delete('/{email_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_email(email_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Email).where(models.Email.id == email_id))
    email = result.scalars().first()
    if not email:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found")
    await db.delete(email)
    await db.commit()
@router.post('/upload', status_code=status.HTTP_201_CREATED, response_model=list[EmailResponse])
async def upload_emails(files: Annotated[list[BinaryFile], File()], db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Category))
    categories = {c.name: c for c in result.scalars().all()}
    created = []
    for file in files:
        filename = file.filename or "unnamed"
        if Path(filename).suffix.lower() not in settings.allowed_extensions:
            raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=f"Файл '{filename}': допустимы только .txt и .json")
        content = await file.read()
        if len(content) > settings.max_file_size:
            raise HTTPException(status_code=status.HTTP_413_CONTENT_TOO_LARGE, detail=f"Файл '{filename}' больше {settings.max_file_size} байт")
        parsed_content = parser.parse(filename, content)
        if parsed_content.is_readable:
            category_name, keywords = classifier.categorise(parsed_content.subject, parsed_content.text)
        else:
            category_name, keywords = Classificator.CORRUPTED_CATEGORY, []
        email = models.Email(who_sent=parsed_content.who_sent, subject=parsed_content.subject, body=parsed_content.text,
                             matched_keywords=keywords, category=categories[category_name], source="upload", filename=filename, is_corrupted=not parsed_content.is_readable)
        db.add(email)
        created.append(email)
    await db.commit()
    for email in created:
        await db.refresh(email)
    return created
