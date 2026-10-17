import pytest

from app.logic.EmailParsing import EmailParsing


@pytest.mark.parametrize("content, expected_subject, expected_who_sent, expected_sent_to, expected_text",
    [
    (
            ("Subject: Meeting\n"
            "From: Ivan\n"
            "To: Team\n"
            "\n"
            "Tuzik"),
            "Meeting",
            "Ivan",
            "Team",
            "Tuzik",
    ),
        (
            ("Тема: ВВП\n"
            "От кого: Петя\n"
            "Кому: Лорик\n"
            "\n"
            "Пора чет делать"),
            "ВВП",
            "Петя",
            "Лорик",
            "Пора чет делать",),
        (
            ("subject: lower-temka\n"
            "from: losharik\n"
            "to: barni\n"
            "\n"
            "text"),
            "lower-temka",
            "losharik",
            "barni",
            "text",
        ),
        (
            ("SUBJECT: KIRIKI\n"
            "FROM: IVAN\n"
            "TO: TEAM\n"
            "\n"
            "TUZIK"),
            "KIRIKI",
            "IVAN",
            "TEAM",
            "TUZIK",
        ),
        (
            ("SuBjEcT: Mixed\n"
            "FrOm: Ivan\n"
            "To: Reciever\n"
            "\n"
            "TuZiK"),
            "Mixed",
            "Ivan",
            "Reciever",
            "TuZiK",
        ),
        (
            ("From: Ivan\n"
            "To: Team\n"
            "\n"
            "No subject"),
            None,
            "Ivan",
            "Team",
            "No subject",
        ),
        (
            ("Subject: dodge\n"
            "From: Ivan\n"
            "\n"
            "No reciever"),
            "dodge",
            "Ivan",
            None,
            "No reciever",
        ),
        (   ("\n"
            "Only text"),
            None,
            None,
            None,
            "Only text",
        ),
        (
            ("Просто текст без заголовков\n"
            "вторая строка"),
            None,
            None,
            None,
            "Просто текст без заголовков\nвторая строка",
        ),
        (
            ("Tema: Hack\n"
            "Ot kogo: Ivan\n"
            "Komu: Team\n"
            "\n"
            "Ne zdanul"),
            "Hack",
            "Ivan",
            "Team",
            "Ne zdanul",
        ),
        (
            ("Subject: Two lines\n"
            "\n"
            "first\n"
            "second"),
            "Two lines",
            None,
            None,
            "first\nsecond",
        ),
    ]
)
def test_email_parsing(content, expected_subject, expected_who_sent, expected_sent_to, expected_text):#проверка корректного парсинга
    parser = EmailParsing()
    email = parser.parse("lydka.txt", content.encode("utf-8"))
    assert email.filename == "lydka.txt"
    assert email.subject == expected_subject
    assert email.who_sent == expected_who_sent
    assert email.sent_to == expected_sent_to
    assert email.text == expected_text
    assert email.is_readable is True


def test_email_parsing_headers_only():#только заголовки, текста нет
    parser = EmailParsing()
    email = parser.parse("mail.txt", "Тема: Акция\n".encode())
    assert email.subject == "Акция"
    assert email.text == ""
    assert email.is_readable is True


@pytest.mark.parametrize(
    "file_name, content, expected_format, expected_is_readable",
    [("mail.txt", b"Subject: 123\n\nText", "txt", True),
     ("MAIL.TXT", b"Subject: 123\n\nText", "txt", True),
     ("mail", b"Subject: 123\n\nText", "noext", True),
     ("image.jpg", b"\xff\xd8\xff\xe0", "image", False),
     ("image.jpeg", b"\xff\xd8\xff\xe0", "image", False),
     ("image.png", b"\x89PNG\r\n", "image", False),
     ("image.gif", b"GIF89a", "image", False),
     ("data.bin", b"\x00\x01\x02\x03", "binary", False),
     ("unknown.abc", b"some unknown data", "unknown", False),
    ],
)
def test_email_parsing_format_and_readability(file_name, content, expected_format, expected_is_readable):#проверка читаемости при определенных форматах
    parser = EmailParsing()
    email = parser.parse(file_name, content)
    assert email.filename == file_name
    assert email.format == expected_format
    assert email.is_readable is expected_is_readable


def test_email_parsing_valid_json():#проверка корректного парсинга валидного JSON писем
    parser = EmailParsing()
    email = parser.parse("mail.json", b'{"subject": "JSON subject", "from": "Lolya", "body": "Body"}')
    assert email.filename == "mail.json"
    assert email.format == "json"
    assert email.subject == "JSON subject"
    assert email.who_sent == "Lolya"
    assert email.text == "Body"
    assert email.is_readable is True


def test_email_parsing_json_not_string():#число или список вместо строки превращается в None
    parser = EmailParsing()
    email = parser.parse("mail.json", b'{"subject": 123, "from": ["Ivan"], "body": "Body"}')
    assert email.subject is None
    assert email.who_sent is None
    assert email.text == "Body"
    assert email.is_readable is True


def test_email_parsing_invalid_json():#проверка корректного парсинга порвежденного JSON файла
    parser = EmailParsing()
    email = parser.parse("broken.json", b'{"subject": "Broken", "from": "Ivan", ')
    assert email.filename == "broken.json"
    assert email.format == "json"
    assert email.is_readable is False


def test_email_parsing_json_list():#JSON-массив вместо объекта — нечитаемое письмо
    parser = EmailParsing()
    email = parser.parse("list.json", b'[1, 2, 3]')
    assert email.is_readable is False