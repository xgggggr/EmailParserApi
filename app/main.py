from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import select


from app import models
from app.logic.classificator import Classificator
from app.schemas.email import ClassificatorResult, EmailCreate, EmailResponse
from sqlalchemy.orm import Session
import app.models
from app.database import Base, engine, get_db, SessionLocal
from app.seed import seed_categories

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    with SessionLocal() as session:
        seed_categories(session)
    yield

app = FastAPI(title="Email Parser API", lifespan=lifespan)
classifier = Classificator()


@app.get('/healthcheck')
def healthcheck():
    return {'status': 'ok'}

@app.post('/api/emails', response_model=EmailResponse)
def classify_email(email: EmailCreate, db: Annotated[Session, Depends(get_db)]):
    category_name, keywords = classifier.categorise(email.subject, email.body)
    result = db.execute(select(models.Category).where(models.Category.name == category_name))
    category = result.scalars().first()
    email = models.Email(who_sent = email.who_sent, subject = email.subject, body = email.body, matched_keywords = keywords, category = category)
    db.add(email)
    db.commit()
    db.refresh(email)
    return email

@app.get('/api/emails', response_model=list[EmailResponse])
def get_all_emails(db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Email))
    emails = result.scalars().all()
    return emails

@app.get('/api/emails/{email_id}', response_model=EmailResponse)
def get_email(email_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Email).where(models.Email.id == email_id),)
    email = result.scalars().first()
    if email:
        return email
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found")
