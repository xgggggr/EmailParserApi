import pytest

pytestmark = pytest.mark.anyio


async def test_stats_empty(client):
    response = await client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 10
    assert all(row["count"] == 0 for row in data)


async def test_stats_count(client):
    for subject in ["Вы выиграли приз", "Акция", "Не работает принтер"]:
        await client.post("/api/emails", json={"subject": subject, "body": "текст"})
    response = await client.get("/api/stats")
    counts = {row["category"]: row["count"] for row in response.json()}
    assert counts["spam"] == 2
    assert counts["hardware"] == 1
    assert counts["HR"] == 0
    assert sum(counts.values()) == 3


async def test_stats_sorted(client):
    for subject in ["Акция", "Скидка", "Не работает принтер"]:
        await client.post("/api/emails", json={"subject": subject, "body": "текст"})
    response = await client.get("/api/stats")
    data = response.json()
    assert data[0] == {"category": "spam", "count": 2}
    assert data[1] == {"category": "hardware", "count": 1}


async def test_stats_after_delete(client):  
    created = (await client.post("/api/emails", json={"subject": "Акция", "body": "текст"})).json()
    await client.delete(f"/api/emails/{created['id']}")
    response = await client.get("/api/stats")
    counts = {row["category"]: row["count"] for row in response.json()}
    assert counts["spam"] == 0