"""seed categories

Revision ID: 7a274aacb81d
Revises: 6f980ea3586f
Create Date: 2026-10-17 14:17:58.825964

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
categories = sa.table(
    "categories",
    sa.column("name", sa.String),
    sa.column("description", sa.Text),
)

CATEGORIES = [
    ("spam", "Спам и фишинг"),
    ("critical_incidents", "Критические инциденты и сбои"),
    ("monitoring", "Автоматические уведомления мониторинга"),
    ("access_control", "Запросы доступа и новые сотрудники"),
    ("hardware", "Проблемы с оборудованием"),
    ("software_failures", "Сбои программного обеспечения"),
    ("documents", "Документооборот и финансы"),
    ("HR", "Кадровые вопросы и встречи"),
    ("unknown", "Не удалось определить категорию"),
    ("corrupted", "Нечитаемые файлы"),
]



# revision identifiers, used by Alembic.
revision: str = '7a274aacb81d'
down_revision: Union[str, Sequence[str], None] = '6f980ea3586f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.bulk_insert(categories, [{"name": n, "description": d} for n, d in CATEGORIES])
    pass


def downgrade() -> None:
    names = [n for n, _ in CATEGORIES]
    op.execute(categories.delete().where(categories.c.name.in_(names)))
    pass
