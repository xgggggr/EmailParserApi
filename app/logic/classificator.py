import logging
logger = logging.getLogger(__name__)
class Classificator:
    CATEGORIES: dict[str, list[str]] = {"spam": ["перейдите по ссылке","заблокирован", "истекает", "выиграли", "введите логин и пароль", "акция", "скидка", "только сегодня", "верификация", "по ссылке", "победител", "приз", "данные банковской карты", "внимание!", "розыгрыш" ],
                  "critical_incidents": ["инцидент", "критичный", "критический", "ошибку 500", "ошибка 500", "затронуто", "срочно", "не отвечает", "всех", "массовый", "сбой", "падает"],
                  "monitoring": ["alert", "мониторинг", "healthcheck", "database", "cluster", "плановый отчёт", "uptime", "ошибок 5xx", "warning" ],
                  "HR": ["отпуск", "технические работы", "больничный", "согласовать", "ежегодный", "нетрудоспособност", "созвон", "обсудить", "приглашение", "корпоратив", "дайджест", "итоги", "встретиться", "участие", "демо", "приглашаем"],
                  "access_control": ["доступ", "новый сотрудник", "приступает к работе", "рабочее место","gitlab", "чтение", "редактирование", "выдать", "подготовить", "права", "1C".lower(), "vpn" ],

                  "hardware": ["неисправность", "оборудован", "гарнитура", "ремонт", "сканер", "не включается", "сломал", "замен", "диагностик", "ноутбук", "перестал работать", "симптомы", "принтер", "устройство", "зависает", "мышь", "экран"],
                  "software_failures": ["антивирус", "после обновления", "не открывает", "раньше всё работало", "ошибк","перестал запускаться", "adobe reader", "excel"],
                  "documents": ["направляем", "инструкц", "согласование", "условия", "правк", "техническое задание", "подтвердить", "расхождение", "приложение", "документ", "оплат", "счёт", "акт", "статус оплаты", "договор", "бухгалтер"]}
    PRIORITY: list[str] = ["spam", "critical_incidents", "monitoring", "software_failures", "access_control",  "hardware", "documents", "HR"]
    UNKNOWN_CATEGORY: str = "unknown"
    CORRUPTED_CATEGORY: str = "corrupted"
    def categorise(self, subject:str | None, body:str | None) -> tuple[str, list[str]]:
        subject = (subject or "").lower()
        body = (body or "").lower()
        score: dict[str, int] = {}
        match: dict[str, list[str]] = {}
        for category, keywords in self.CATEGORIES.items():
            for keyword in keywords:
                c = 0
                if keyword in subject:
                    c += 1
                if keyword in body:
                    c += 1
                if c > 0:
                    score[category] = score.get(category, 0) + c
                    if category not in match:
                        match[category] = []
                    match[category].append(keyword)
        if not score:
            logger.info(f"Письмо не совпало ни с одной категорией")
            return self.UNKNOWN_CATEGORY, []
        max_c = max(score.values())
        result = [i for i in score if score[i] == max_c ]
        if len(result) == 1:
            return result[0], match[result[0]]
        else:
            for i in self.PRIORITY:
                if i in result:
                    return i, match[i]
        logger.info(f"Письму не удалось присвоить категорию")
        return self.UNKNOWN_CATEGORY, []