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
    # Create multiple action items
    created_items = []
    for i in range(8):
        r = client.post("/action-items/", json={"description": f"Task {i:02d}"})
        assert r.status_code == 201
        created_items.append(r.json())

    # Mark some as completed
    completed_ids = [created_items[0]["id"], created_items[2]["id"], created_items[4]["id"]]
    for item_id in completed_ids:
        r = client.put(f"/action-items/{item_id}/complete")
        assert r.status_code == 200

    # Test sorting by id ascending
    r = client.get("/action-items/", params={"sort": "id"})
    assert r.status_code == 200
    items = r.json()
    ids = [item["id"] for item in items]
    assert ids == sorted(ids)

    # Test descending sort
    r = client.get("/action-items/", params={"sort": "-id"})
    assert r.status_code == 200
    items_desc = r.json()
    ids_desc = [item["id"] for item in items_desc]
    assert ids_desc == sorted(ids, reverse=True)

    # Test pagination with skip and limit
    r = client.get("/action-items/", params={"sort": "id", "skip": 2, "limit": 3})
    assert r.status_code == 200
    page = r.json()
    assert len(page) == 3
    assert page[0]["id"] == ids[2]
    assert page[1]["id"] == ids[3]
    assert page[2]["id"] == ids[4]

    # Test pagination with filtering: only completed items
    r = client.get("/action-items/", params={"completed": True, "sort": "id", "skip": 0, "limit": 2})
    assert r.status_code == 200
    completed_page = r.json()
    assert len(completed_page) == 2
    assert all(item["completed"] for item in completed_page)
    completed_page_ids = [item["id"] for item in completed_page]
    assert completed_page_ids == sorted(completed_ids)[:2]

    # Test pagination with filtering: only pending items
    r = client.get("/action-items/", params={"completed": False, "sort": "id", "skip": 1, "limit": 2})
    assert r.status_code == 200
    pending_page = r.json()
    assert len(pending_page) == 2
    assert all(not item["completed"] for item in pending_page)

    # Test edge case: skip beyond available filtered items
    r = client.get("/action-items/", params={"completed": True, "sort": "id", "skip": 10, "limit": 5})
    assert r.status_code == 200
    empty_filtered_page = r.json()
    assert len(empty_filtered_page) == 0

    # Test boundary: limit = 1 (minimum allowed)
    r = client.get("/action-items/", params={"sort": "id", "limit": 1})
    assert r.status_code == 200
    single_item = r.json()
    assert len(single_item) == 1

    # Test maximum limit (200)
    r = client.get("/action-items/", params={"sort": "id", "limit": 200})
    assert r.status_code == 200
    max_limit = r.json()
    assert len(max_limit) <= 200

    # Test sorting by description
    r = client.get("/action-items/", params={"sort": "description"})
    assert r.status_code == 200
    desc_sorted = r.json()
    descriptions = [item["description"] for item in desc_sorted]
    assert descriptions == sorted(descriptions)

    # Test invalid sort field falls back to -created_at
    r_default = client.get("/action-items/", params={"sort": "-created_at"})
    r_invalid = client.get("/action-items/", params={"sort": "invalid_field"})
    assert r_default.status_code == 200
    assert r_invalid.status_code == 200
    default_ids = [item["id"] for item in r_default.json()]
    invalid_ids = [item["id"] for item in r_invalid.json()]
    assert invalid_ids == default_ids

    # Test consistency: same parameters return same results
    r1 = client.get("/action-items/", params={"sort": "id", "limit": 3, "completed": False})
    r2 = client.get("/action-items/", params={"sort": "id", "limit": 3, "completed": False})
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json() == r2.json()

    # Test parameter validation: negative skip
    r = client.get("/action-items/", params={"skip": -1})
    assert r.status_code == 422

    # Test parameter validation: limit too low should fail (limit must be >= 1)
    r = client.get("/action-items/", params={"limit": 0})
    assert r.status_code == 422

    # Test parameter validation: limit too high
    r = client.get("/action-items/", params={"limit": 201})
    assert r.status_code == 422

    # Test combined filtering and pagination with large skip
    r = client.get("/action-items/", params={"completed": False, "sort": "-id", "skip": 5, "limit": 10})
    assert r.status_code == 200
    large_skip_page = r.json()
    # Should return remaining items after skip, limited by actual available items
    assert len(large_skip_page) <= 5  # 8 total - 3 completed = 5 pending, skip 5 = 0
