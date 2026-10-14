from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Category

CATEGORY_DESCRIPTIONS = {"spam": "Спам и фишинг",
                         "critical_incidents": "Критические инциденты и сбой",
                         "monitoring": "Автоматические уведомления мониторинга",
                         "access_control": "Запросы доступа и новые сотрудники",
                         "hardware": "Проблемы с оборудованием",
                         "software_failures": "Сбои программного обеспечения",
                         "documents": "Документооборот и финансы",
                        "HR": "Кадровые вопросы и встречи",
                        "unknown": "Не удалось определить категорию",
                        "corrupted": "Нечитаемые файлы",}

def seed_categories(session: Session) -> None:
    existing = set(session.scalars(select(Category.name)))
    for name, description in CATEGORY_DESCRIPTIONS.items():
        if name not in existing:
            session.add(Category(name=name, description=description))
    session.commit()