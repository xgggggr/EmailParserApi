from pathlib import Path
import pytest
from Email import Email
from Classificator import Classificator


@pytest.mark.parametrize("subject, text, expected_category",
    [("Вы выиграли тачку", "", "spam"),
     ("Критический инцидент", "", "critical_incidents"),
     ("Alert database cluster", "", "monitoring"),
     ("После обновления excel не открывается файл", "", "software_failures"),
     ("Выдать доступ в GitLab", "", "access_control"),
     ("Не работает принтер", "", "hardware"),
     ("Направляем договор на согласование", "", "documents"),
     ("Заявление на отпуск", "", "HR"),
    ]
)
def test_classificator_category(subject, text, expected_category):#Верно ли определяет категорию
    email = Email(source=Path("mail.txt"), format="txt", subject=subject, text=text)
    classificator = Classificator()
    assert classificator.categorise(email) == expected_category


def test_classificator_categories_unknown():#тест на unknown
    email = Email(source=Path("mail.txt"), format="txt", subject="unknown", text="ГО ГУЛ")
    classificator = Classificator()
    assert classificator.categorise(email) == "unknown"


def test_classificator_categories_corrupted():#тест на corrupted
    email = Email(source=Path("mail.ru"), format="image", is_readable=False)
    classificator = Classificator()
    assert classificator.categorise(email) == "corrupted"


def test_classificator_priority():#тест на приоритет
    email = Email(source=Path("mail.txt"), format="txt", subject="Вы выиграли приз", text="Критический инцидент")
    classificator = Classificator()
    assert classificator.categorise(email) == "spam"


def test_classificator_none():#тест на None
    email = Email(source=Path("email.txt"), format="txt", subject=None, text=None)
    classificator = Classificator()
    assert classificator.categorise(email) == "unknown"