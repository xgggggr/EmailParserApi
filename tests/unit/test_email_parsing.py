import pytest
from EmailParsing import EmailParsing



@pytest.mark.parametrize("content, expected_subject, expected_who_sent, expected_sent_to, expected_text",
    [
    (
            "Subject: Meeting\n"
            "From: Ivan\n"
            "To: Team\n"
            "\n"
            "Tuzik",
            "Meeting",
            "Ivan",
            "Team",
            "Tuzik",
    ),
        (
            "Тема: ВВП\n"
            "От кого: Петя\n"
            "Кому: Лорик\n"
            "\n"
            "Пора чет делать",
            "ВВП",
            "Петя",
            "Лорик",
            "Пора чет делать",),
        (
            "subject: lower-temka\n"
            "from: losharik\n"
            "to: barni\n"
            "\n"
            "text",
            "lower-temka",
            "losharik",
            "barni",
            "text",
        ),
        (
            "SUBJECT: KIRIKI\n"
            "FROM: IVAN\n"
            "TO: TEAM\n"
            "\n"
            "TUZIK",
            "KIRIKI",
            "IVAN",
            "TEAM",
            "TUZIK",
        ),
        (
            "SuBjEcT: Mixed\n"
            "FrOm: Ivan\n"
            "To: Reciever\n"
            "\n"
            "TuZiK",
            "Mixed",
            "Ivan",
            "Reciever",
            "TuZiK",
        ),
        (
            "From: Ivan\n"
            "To: Team\n"
            "\n"
            "No subject",
            None,
            "Ivan",
            "Team",
            "No subject",
        ),
        (
            "Subject: dodge\n"
            "From: Ivan\n"
            "\n"
            "No reciever",
            "dodge",
            "Ivan",
            None,
            "No reciever",
        ),
        (   "\n"
            "Only text",
            None,
            None,
            None,
            "Only text",
        ),
        (
            "Tema: Hack\n"
            "Ot kogo: Ivan\n"
            "Komu: Team\n"
            "\n"
            "Ne zdanul",
            "Hack",
            "Ivan",
            "Team",
            "Ne zdanul",
        )
    ]
)
def test_email_parsing(tmp_path, content, expected_subject, expected_who_sent, expected_sent_to, expected_text):#проверка корректного парсинга
    file_path = tmp_path / "lydka.txt"
    file_path.write_text(content, encoding="utf-8")
    parser = EmailParsing()
    email = parser.parse(file_path)
    assert email.source == file_path
    assert email.subject == expected_subject
    assert email.who_sent == expected_who_sent
    assert email.sent_to == expected_sent_to
    assert email.text == expected_text
    assert email.is_readable == True


@pytest.mark.parametrize(
    "file_name, content, use_bytes, expected_format, expected_is_readable",
    [("mail.txt", "Subject: 123\n\nText", False, "txt", True),
     ("mail", "Subject: 123\n\nText", False, "noext", True),
     ("image.jpg", b"\xff\xd8\xff\xe0", True, "image", False),
     ("image.jpeg", b"\xff\xd8\xff\xe0", True, "image", False),
     ("image.png", b"\x89PNG\r\n", True, "image", False),
     ("data.bin", b"\x00\x01\x02\x03", True, "binary", False),
     ("unknown.abc", b"some unknown data", True, "unknown", False),
    ],
)
def test_email_parsing_format_and_readability(tmp_path, file_name, content, use_bytes, expected_format, expected_is_readable,):#проверка читаемости при определенных форматах
    file_path = tmp_path / file_name
    if use_bytes:
        file_path.write_bytes(content)
    else:
        file_path.write_text(content, encoding="utf-8")
    parser = EmailParsing()
    email = parser.parse(file_path)
    assert email.source == file_path
    assert email.format == expected_format
    assert email.is_readable is expected_is_readable


def test_email_parsing_valid_json(tmp_path):#проверка корректного парсинга валидного JSON писем
    file_path = tmp_path / "mail.json"
    file_path.write_text('{"subject": "JSON subject", "from": "Lolya", "body": "Body"}', encoding="utf-8",)
    parser = EmailParsing()
    email = parser.parse(file_path)
    assert email.source == file_path
    assert email.format == "json"
    assert email.subject == "JSON subject"
    assert email.who_sent == "Lolya"
    assert email.text == "Body"
    assert email.is_readable is True


def test_email_parsing_invalid_json(tmp_path):#проверка корректного парсинга порвежденного JSON файла
    file_path = tmp_path / "broken.json"
    file_path.write_text('{"subject": "Broken", "from": "Ivan", ', encoding="utf-8",)
    parser = EmailParsing()
    email = parser.parse(file_path)
    assert email.source == file_path
    assert email.format == "json"
    assert email.is_readable is False


