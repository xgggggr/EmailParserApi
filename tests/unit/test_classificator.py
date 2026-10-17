
import pytest

from app.logic.classificator import Classificator

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
    classificator = Classificator()
    category, keywords = classificator.categorise(subject, text)
    assert category == expected_category
    assert keywords != []


def test_classificator_categories_unknown():#тест на unknown
    classificator = Classificator()
    assert classificator.categorise("unknown", "ГО ГУЛ") == ("unknown", [])


def test_classificator_priority():#тест на приоритет
    classificator = Classificator()
    category, _ = classificator.categorise("Вы выиграли приз", "Критический инцидент")
    assert category == "spam"


def test_classificator_none():#тест на None
    classificator = Classificator()
    assert classificator.categorise(None, None) == ("unknown", [])


def test_classificator_matched_keywords():
    classificator = Classificator()
    category, keywords = classificator.categorise("Акция", "Скидка только сегодня")
    assert category == "spam"
    assert keywords == ["акция", "скидка", "только сегодня"]
