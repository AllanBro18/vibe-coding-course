def test_create_and_list_notes(client):
    payload = {"title": "Test", "content": "Hello world"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["title"] == "Test"

    r = client.get("/notes/")
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    r = client.get("/notes/search/")
    assert r.status_code == 200

    r = client.get("/notes/search/", params={"q": "Hello"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1


def _create_note(client, title="Test", content="Hello world"):
    r = client.post("/notes/", json={"title": title, "content": content})
    assert r.status_code == 201
    return r.json()


def test_update_note_success(client):
    note = _create_note(client)
    r = client.put(f"/notes/{note['id']}", json={"title": "Updated", "content": "New content"})
    assert r.status_code == 200
    data = r.json()
    assert data["title"] == "Updated"
    assert data["content"] == "New content"


def test_update_note_not_found(client):
    r = client.put("/notes/99999", json={"title": "X", "content": "Y"})
    assert r.status_code == 404


def test_update_note_empty_title(client):
    note = _create_note(client)
    r = client.put(f"/notes/{note['id']}", json={"title": "", "content": "Y"})
    assert r.status_code == 422


def test_update_note_title_too_long(client):
    note = _create_note(client)
    r = client.put(f"/notes/{note['id']}", json={"title": "A" * 201, "content": "Y"})
    assert r.status_code == 422


def test_create_note_empty_title(client):
    r = client.post("/notes/", json={"title": "", "content": "Y"})
    assert r.status_code == 422


def test_create_note_empty_content(client):
    r = client.post("/notes/", json={"title": "X", "content": ""})
    assert r.status_code == 422


def test_delete_note_success(client):
    note = _create_note(client)
    r = client.delete(f"/notes/{note['id']}")
    assert r.status_code == 204
    # verify it's gone
    r = client.get(f"/notes/{note['id']}")
    assert r.status_code == 404


def test_delete_note_not_found(client):
    r = client.delete("/notes/99999")
    assert r.status_code == 404
