import pytest

from app.config import settings

pytestmark = pytest.mark.anyio


async def test_upload_txt(client):
    content = "Тема: Вы выиграли приз\nОт кого: Petya\n\nПерейдите по ссылке".encode()
    response = await client.post("/api/emails/upload", files=[("files", ("mail.txt", content))])
    assert response.status_code == 201
    data = response.json()
    assert len(data) == 1
    assert data[0]["subject"] == "Вы выиграли приз"
    assert data[0]["who_sent"] == "Petya"
    assert data[0]["body"] == "Перейдите по ссылке"
    assert data[0]["category"]["name"] == "spam"
    assert data[0]["source"] == "upload"
    assert data[0]["filename"] == "mail.txt"
    assert data[0]["is_corrupted"] is False


async def test_upload_json(client):
    content = '{"subject": "Не работает принтер", "from": "Ivan", "body": "Не включается"}'.encode()
    response = await client.post("/api/emails/upload", files=[("files", ("mail.json", content))])
    assert response.status_code == 201
    data = response.json()[0]
    assert data["subject"] == "Не работает принтер"
    assert data["who_sent"] == "Ivan"
    assert data["category"]["name"] == "hardware"


async def test_upload_no_extension(client):
    content = b"Subject: Alert\n\ndatabase cluster warning"
    response = await client.post("/api/emails/upload", files=[("files", ("mail", content))])
    assert response.status_code == 201
    assert response.json()[0]["category"]["name"] == "monitoring"


async def test_upload_batch_with_corrupted(client):
    files = [
        ("files", ("good.txt", "Тема: Акция\n\nСкидка".encode())),
        ("files", ("good.json", '{"subject": "Договор", "body": "Направляем акт"}'.encode())),
        ("files", ("broken.json", b'{"subject": "Broken", ')),
        ("files", ("cp1251.txt", "Тема: Привет".encode("cp1251"))),
    ]
    response = await client.post("/api/emails/upload", files=files)
    assert response.status_code == 201
    data = {e["filename"]: e for e in response.json()}
    assert len(data) == 4
    assert data["good.txt"]["category"]["name"] == "spam"
    assert data["good.json"]["category"]["name"] == "documents"
    for name in ["broken.json", "cp1251.txt"]:
        assert data[name]["category"]["name"] == "corrupted"
        assert data[name]["is_corrupted"] is True
        assert data[name]["matched_keywords"] == []
    emails = (await client.get("/api/emails")).json()
    assert emails["total"] == 4


async def test_upload_headers_only(client):
    content = "Тема: Акция\n".encode()
    response = await client.post("/api/emails/upload", files=[("files", ("mail.txt", content))])
    assert response.status_code == 201
    assert response.json()[0]["subject"] == "Акция"
    assert response.json()[0]["category"]["name"] == "spam"


async def test_upload_wrong_extension(client):
    response = await client.post("/api/emails/upload", files=[("files", ("mail.pdf", b"%PDF-1.4"))])
    assert response.status_code == 415
    assert "mail.pdf" in response.json()["detail"]


async def test_upload_all_or_nothing(client):
    files = [
        ("files", ("good1.txt", "Тема: Акция\n\nСкидка".encode())),
        ("files", ("good2.txt", "Тема: Отпуск\n\nПрошу согласовать".encode())),
        ("files", ("bad.pdf", b"%PDF-1.4")),
    ]
    response = await client.post("/api/emails/upload", files=files)
    assert response.status_code == 415
    emails = (await client.get("/api/emails")).json()
    assert emails["total"] == 0


async def test_upload_too_big(client, monkeypatch):
    monkeypatch.setattr(settings, "max_file_size", 10)
    content = "Тема: Акция\n\nСкидка только сегодня".encode()
    response = await client.post("/api/emails/upload", files=[("files", ("big.txt", content))])
    assert response.status_code == 413
    emails = (await client.get("/api/emails")).json()
    assert emails["total"] == 0


async def test_upload_without_files(client): 
    response = await client.post("/api/emails/upload")
    assert response.status_code == 422