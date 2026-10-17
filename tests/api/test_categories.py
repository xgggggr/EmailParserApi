import pytest

from app.seed import CATEGORY_DESCRIPTIONS

pytestmark = pytest.mark.anyio


async def test_categories_all(client):
    response = await client.get("/api/categories")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 10
    assert {c["name"] for c in data} == set(CATEGORY_DESCRIPTIONS)


async def test_categories_have_description(client):
    response = await client.get("/api/categories")
    for category in response.json():
        assert isinstance(category["id"], int)
        assert category["description"] == CATEGORY_DESCRIPTIONS[category["name"]]