from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    emails: Mapped[list[Email]] = relationship(back_populates="category")
class Email(Base):
    __tablename__ = 'email'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    who_sent: Mapped[str | None] = mapped_column(String(50))
    subject: Mapped[str | None] = mapped_column(Text)
    body: Mapped[str | None] = mapped_column(Text)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False, default='api')
    filename: Mapped[str | None] = mapped_column(String(200))
    matched_keywords: Mapped[list[str]] = mapped_column(JSONB, default=list)
    is_corrupted: Mapped[bool] = mapped_column(Boolean, default=False)
    email_created: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    category: Mapped[Category] = relationship(back_populates='emails', lazy="selectin")
    

