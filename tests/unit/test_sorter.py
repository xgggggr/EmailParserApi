import pytest

from Sorter import Sorter
from pathlib import Path

def test_sorter_movement(tmp_path):#проверка успешного перемещения файла
    file_path = tmp_path / "test_sorter.txt"
    file_path.write_text("Йехай", encoding="utf-8")
    res_dir = tmp_path / "res"
    res_dir = Sorter(res_dir)
    result = res_dir.sort(file_path, "spam")
    assert file_path.exists() is False
    assert result["path"].exists()
    assert result["status"] == "success"
    assert result["category"] == "spam"
    assert result["renamed"] is False


def test_sorter_missing_file(tmp_path):#проверка обработки отсутсвующего файла
    file_path = tmp_path / "test_sorter.txt"
    res_dir = tmp_path / "res"
    res_dir = Sorter(res_dir)
    result = res_dir.sort(file_path, "spam")
    assert result["status"] == "error"
    assert result["error"] == "file not found"


def test_sorter_duplicate_file(tmp_path):#проверка работы программы при конфликте нейминга файлов
    file_path = tmp_path / "test_sorter.txt"
    file_path.write_text("Йяхай", encoding="utf-8")
    res_dir = tmp_path / "res"
    res_dir = Sorter(res_dir)
    result = res_dir.sort(file_path, "spam")
    file_path_1 = tmp_path / "test_sorter.txt"
    file_path_1.write_text("123", encoding="utf-8")
    result = res_dir.sort(file_path_1, "spam")
    assert result["path"].name == "test_sorter_1.txt"
    assert result["renamed"] is True
    assert result["path"].exists()


@pytest.mark.parametrize("category", ["spam", "critical_incidents", "monitoring", "software_failures", "access_control",  "hardware", "documents", "HR"])
def test_sorter_categories(category, tmp_path):#проверка создания папок под все категории
    file_path = tmp_path / "test_sorter.txt"
    file_path.write_text(category, encoding="utf-8")
    res_dir = tmp_path / "res"
    res_dir = Sorter(res_dir)
    result = res_dir.sort(file_path, category)
    assert result["category"] == category
    assert (tmp_path / "res" / category / "test_sorter.txt").exists() is True


def test_sorter_text(tmp_path):#проверка сохранения содержимого файла
    file_path = tmp_path / "test_sorter.txt"
    file_path.write_text("psg", encoding="utf-8")
    res_dir = tmp_path / "res"
    res_dir = Sorter(res_dir)
    result = res_dir.sort(file_path, "spam")
    assert result["path"].read_text(encoding="utf-8") == "psg"



