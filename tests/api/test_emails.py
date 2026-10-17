import pytest

pytestmark = pytest.mark.anyio


async def create_email(client, subject, body, who_sent=None):
    response = await client.post("/api/emails", json={"who_sent": who_sent, "subject": subject, "body": body})
    assert response.status_code == 201
    return response.json()


# ---------- POST /api/emails ----------

async def test_emails_create(client):
    response = await client.post("/api/emails", json={"who_sent": "Ivan", "subject": "Вы выиграли приз", "body": "Перейдите по ссылке"})
    assert response.status_code == 201
    data = response.json()
    assert isinstance(data["id"], int)
    assert data["who_sent"] == "Ivan"
    assert data["subject"] == "Вы выиграли приз"
    assert data["body"] == "Перейдите по ссылке"
    assert data["category"]["name"] == "spam"
    assert "выиграли" in data["matched_keywords"]
    assert data["source"] == "api"
    assert data["filename"] is None
    assert data["is_corrupted"] is False


async def test_emails_create_unknown(client):
    data = await create_email(client, "ДАРОВА", "ЧЕ ДЕЛаеЕШЬ?")
    assert data["category"]["name"] == "unknown"
    assert data["matched_keywords"] == []


async def test_emails_create_only_body(client):
    data = await create_email(client, None, "Срочно! Сбой на сервере")
    assert data["subject"] is None
    assert data["category"]["name"] == "critical_incidents"


@pytest.mark.parametrize("payload", [{"subject": "", "body": "текст"}, {"subject": "тема", "body": ""}])
async def test_emails_create_empty_strings(client, payload):
    response = await client.post("/api/emails", json=payload)
    assert response.status_code == 422


# ---------- GET /api/emails/{id} ----------

async def test_emails_get(client):
    created = await create_email(client, "Заявление на отпуск", "Прошу согласовать")
    response = await client.get(f"/api/emails/{created['id']}")
    assert response.status_code == 200
    assert response.json() == created


async def test_emails_get_not_found(client):
    response = await client.get("/api/emails/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Email not found"


async def test_emails_get_wrong_id(client):
    response = await client.get("/api/emails/abc")
    assert response.status_code == 422


# ---------- GET /api/emails ----------

async def test_emails_list_empty(client):
    response = await client.get("/api/emails")
    assert response.status_code == 200
    assert response.json() == {"items": [], "total": 0, "limit": 20, "offset": 0}


async def test_emails_list_newest_first(client):
    first = await create_email(client, "Первое", "текст")
    second = await create_email(client, "Второе", "текст")
    response = await client.get("/api/emails")
    data = response.json()
    assert data["total"] == 2
    assert [e["id"] for e in data["items"]] == [second["id"], first["id"]]


async def test_emails_list_limit_offset(client):
    for i in range(5):
        await create_email(client, f"Письмо {i}", "текст")
    page1 = (await client.get("/api/emails?limit=2&offset=0")).json()
    page3 = (await client.get("/api/emails?limit=2&offset=4")).json()
    assert len(page1["items"]) == 2
    assert len(page3["items"]) == 1
    assert page1["total"] == 5
    assert page3["total"] == 5
    assert page1["limit"] == 2
    assert page3["offset"] == 4


async def test_emails_list_filter_category(client):
    await create_email(client, "Вы выиграли приз", "текст")
    await create_email(client, "Акция", "Скидка только сегодня")
    await create_email(client, "Не работает принтер", "текст")
    response = await client.get("/api/emails?category=spam")
    data = response.json()
    assert data["total"] == 2
    assert all(e["category"]["name"] == "spam" for e in data["items"])


async def test_emails_list_filter_unknown_category(client):
    await create_email(client, "Вы выиграли приз", "текст")
    response = await client.get("/api/emails?category=sixseven")
    assert response.status_code == 200
    assert response.json()["total"] == 0


@pytest.mark.parametrize("query", ["limit=0", "limit=101", "limit=500", "offset=-1", "limit=abc"])
async def test_emails_list_bad_params(client, query):
    response = await client.get(f"/api/emails?{query}")
    assert response.status_code == 422


# ---------- PATCH /api/emails/{id} ----------

async def test_emails_change_category(client):
    created = await create_email(client, "Привет", "Как дела?")
    response = await client.patch(f"/api/emails/{created['id']}", json={"category": "HR"})
    assert response.status_code == 200
    assert response.json()["category"]["name"] == "HR"
    again = await client.get(f"/api/emails/{created['id']}")
    assert again.json()["category"]["name"] == "HR"


async def test_emails_change_category_not_found(client):
    response = await client.patch("/api/emails/999", json={"category": "HR"})
    assert response.status_code == 404


async def test_emails_change_category_wrong_category(client):
    created = await create_email(client, "Вы выиграли приз", "текст")
    response = await client.patch(f"/api/emails/{created['id']}", json={"category": "sixseven"})
    assert response.status_code == 422
    assert response.json()["detail"] == "Нет категории sixseven"
    again = await client.get(f"/api/emails/{created['id']}")
    assert again.json()["category"]["name"] == "spam"


async def test_emails_change_category_empty_body(client):
    created = await create_email(client, "Привет", "текст")
    response = await client.patch(f"/api/emails/{created['id']}", json={})
    assert response.status_code == 422


# ---------- DELETE /api/emails/{id} ----------

async def test_emails_delete(client):
    created = await create_email(client, "Привет", "текст")
    response = await client.delete(f"/api/emails/{created['id']}")
    assert response.status_code == 204
    assert response.content == b""
    again = await client.get(f"/api/emails/{created['id']}")
    assert again.status_code == 404


async def test_emails_delete_not_found(client):
    response = await client.delete("/api/emails/999")
    assert response.status_code == 404