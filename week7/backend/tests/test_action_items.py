def test_create_complete_list_and_patch_action_item(client):
    payload = {"description": "Ship it"}
    r = client.post("/action-items/", json=payload)
    assert r.status_code == 201, r.text
    item = r.json()
    assert item["completed"] is False
    assert "created_at" in item and "updated_at" in item

    r = client.put(f"/action-items/{item['id']}/complete")
    assert r.status_code == 200
    done = r.json()
    assert done["completed"] is True

    r = client.get("/action-items/", params={"completed": True, "limit": 5, "sort": "-created_at"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    r = client.patch(f"/action-items/{item['id']}", json={"description": "Updated"})
    assert r.status_code == 200
    patched = r.json()
    assert patched["description"] == "Updated"


def test_action_item_validation_get_and_delete(client):
    # Empty description should fail validation
    r = client.post("/action-items/", json={"description": "   "})
    assert r.status_code == 422

    # Create a valid item
    r = client.post("/action-items/", json={"description": "Something to do"})
    assert r.status_code == 201
    item_id = r.json()["id"]

    # Retrieve single item
    r = client.get(f"/action-items/{item_id}")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == item_id

    # Delete item
    r = client.delete(f"/action-items/{item_id}")
    assert r.status_code == 204

    # Subsequent fetch should return 404
    r = client.get(f"/action-items/{item_id}")
    assert r.status_code == 404


def test_extract_items_endpoint(client):
    text = """
    TODO: write tests
    1. Fix bug
    This is just commentary.
    """.strip()
    r = client.post("/action-items/extract", json={"text": text})
    assert r.status_code == 200
    items = r.json()
    assert any("TODO: write tests" in i for i in items)
    assert any("Fix bug" in i for i in items)
    assert all("commentary" not in i for i in items)


def test_action_items_pagination_and_sorting(client):
    # Create multiple items, mark one completed
    ids: list[int] = []
    for i in range(3):
        r = client.post("/action-items/", json={"description": f"Task {i}"})
        assert r.status_code == 201
        ids.append(r.json()["id"])

    r = client.put(f"/action-items/{ids[0]}/complete")
    assert r.status_code == 200

    # Verify sorting by id ascending
    r = client.get("/action-items/", params={"sort": "id"})
    assert r.status_code == 200
    items = r.json()
    all_ids = [item["id"] for item in items]
    assert all_ids == sorted(all_ids)

    # Pagination with filter: only completed items, limit/skip
    r = client.get(
        "/action-items/",
        params={"completed": True, "sort": "id", "skip": 0, "limit": 1},
    )
    assert r.status_code == 200
    page = r.json()
    assert len(page) == 1
    assert page[0]["completed"] is True

    # Invalid sort falls back to -created_at
    r_default = client.get("/action-items/", params={"sort": "-created_at"})
    r_invalid = client.get("/action-items/", params={"sort": "does_not_exist"})
    assert r_default.status_code == 200
    assert r_invalid.status_code == 200
    ids_default = [item["id"] for item in r_default.json()]
    ids_invalid = [item["id"] for item in r_invalid.json()]
    assert ids_invalid == ids_default
