from Statistics import Statistics


def test_statistics_empty():#проверка поведения программы при отсутствии обработаныых писем
    statistics = Statistics()
    assert statistics.get_summary() == "Новых писем не поступило :("


def test_statistics_one_record():#проверка записи статистики для одной категории
    statistics = Statistics()
    statistics.record_statistic("spam")
    assert statistics.total_count == 1
    assert statistics.non_readable_count == 0
    assert statistics.counter["spam"] == 1


def test_statistics_non_readable():#проверка учета нечитаемых писем
    statistics = Statistics()
    statistics.record_statistic("corrupted", False)
    assert statistics.non_readable_count == 1
    assert statistics.total_count == 1


def test_statistics_summ():#проверка корректности итогового отчета по категориям
    statistics = Statistics()
    statistics.record_statistic("spam")
    statistics.record_statistic("access_control")
    statistics.record_statistic("hardware")
    summa = statistics.get_summary()
    assert "Обработано писем : 3" in summa
    assert "spam" in summa
    assert "access_control" in summa
    assert "hardware" in summa
