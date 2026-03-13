def _create_item(client, desc="Ship it"):
    r = client.post("/action-items/", json={"description": desc})
    assert r.status_code == 201
    return r.json()


def test_create_and_complete_action_item(client):
    payload = {"description": "Ship it"}
    r = client.post("/action-items/", json=payload)
    assert r.status_code == 201, r.text
    item = r.json()
    assert item["completed"] is False

    r = client.put(f"/action-items/{item['id']}/complete")
    assert r.status_code == 200
    done = r.json()
    assert done["completed"] is True

    r = client.get("/action-items/")
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1


def test_filter_completed_true(client):
    a = _create_item(client, "task a")
    _create_item(client, "task b")
    client.put(f"/action-items/{a['id']}/complete")

    r = client.get("/action-items/", params={"completed": True})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1
    assert items[0]["completed"] is True


def test_filter_completed_false(client):
    a = _create_item(client, "task a")
    b = _create_item(client, "task b")
    client.put(f"/action-items/{a['id']}/complete")

    r = client.get("/action-items/", params={"completed": False})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1
    assert items[0]["id"] == b["id"]


def test_filter_no_param_returns_all(client):
    _create_item(client, "task a")
    b = _create_item(client, "task b")
    client.put(f"/action-items/{b['id']}/complete")

    r = client.get("/action-items/")
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_bulk_complete_success(client):
    a = _create_item(client, "task a")
    b = _create_item(client, "task b")
    c = _create_item(client, "task c")

    r = client.post("/action-items/bulk-complete", json={"ids": [a["id"], b["id"]]})
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 2
    assert all(item["completed"] is True for item in data)

    # c should still be open
    r = client.get("/action-items/", params={"completed": False})
    assert len(r.json()) == 1
    assert r.json()[0]["id"] == c["id"]


def test_bulk_complete_invalid_id(client):
    a = _create_item(client, "task a")
    r = client.post("/action-items/bulk-complete", json={"ids": [a["id"], 99999]})
    assert r.status_code == 404

    # transaction should have rolled back — a should still be open
    r = client.get("/action-items/", params={"completed": False})
    items = r.json()
    assert any(item["id"] == a["id"] for item in items)


def test_bulk_complete_empty_ids(client):
    r = client.post("/action-items/bulk-complete", json={"ids": []})
    assert r.status_code == 422


def test_create_action_item_empty_description(client):
    r = client.post("/action-items/", json={"description": ""})
    assert r.status_code == 422
