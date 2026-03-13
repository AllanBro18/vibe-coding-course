from backend.app.models import Tag


def test_create_and_fetch_tag(client):
    payload = {"name": "urgent", "color": "#FF5733"}
    r = client.post("/tags/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["name"] == "urgent"
    assert data["color"] == "#FF5733"
    assert "created_at" in data and "updated_at" in data

    r = client.get("/tags/")
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    tag_id = data["id"]
    r = client.get(f"/tags/{tag_id}")
    assert r.status_code == 200
    fetched = r.json()
    assert fetched["id"] == tag_id
    assert fetched["name"] == "urgent"


def test_tag_validation_and_delete(client):
    # Empty name should fail validation
    r = client.post("/tags/", json={"name": "", "color": "#FF5733"})
    assert r.status_code == 422

    # Invalid color format
    r = client.post("/tags/", json={"name": "test", "color": "red"})
    assert r.status_code == 422

    # Invalid name format
    r = client.post("/tags/", json={"name": "test@tag"})
    assert r.status_code == 422

    # Create a valid tag then delete it
    r = client.post("/tags/", json={"name": "to-delete", "color": "#33FF57"})
    assert r.status_code == 201
    tag_id = r.json()["id"]

    r = client.delete(f"/tags/{tag_id}")
    assert r.status_code == 204

    # Subsequent fetch should return 404
    r = client.get(f"/tags/{tag_id}")
    assert r.status_code == 404


def test_tag_uniqueness(client):
    # Create first tag
    r = client.post("/tags/", json={"name": "unique-tag"})
    assert r.status_code == 201

    # Try to create duplicate
    r = client.post("/tags/", json={"name": "unique-tag"})
    assert r.status_code == 409


def test_tag_association_with_notes(client):
    # Create a tag
    r = client.post("/tags/", json={"name": "test-tag"})
    assert r.status_code == 201
    tag_id = r.json()["id"]

    # Create a note
    r = client.post("/notes/", json={"title": "Test Note", "content": "Test content"})
    assert r.status_code == 201
    note_id = r.json()["id"]

    # Associate tag with note
    r = client.post(f"/notes/{note_id}/tags/{tag_id}")
    assert r.status_code == 204

    # Fetch note and check it has the tag
    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 200
    note = r.json()
    assert len(note["tags"]) == 1
    assert note["tags"][0]["name"] == "test-tag"

    # Try to associate same tag again (should fail)
    r = client.post(f"/notes/{note_id}/tags/{tag_id}")
    assert r.status_code == 409

    # Remove tag from note
    r = client.delete(f"/notes/{note_id}/tags/{tag_id}")
    assert r.status_code == 204

    # Fetch note again and check tag is removed
    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 200
    note = r.json()
    assert len(note["tags"]) == 0


def test_tag_association_with_action_items(client):
    # Create a tag
    r = client.post("/tags/", json={"name": "action-tag"})
    assert r.status_code == 201
    tag_id = r.json()["id"]

    # Create an action item
    r = client.post("/action-items/", json={"description": "Test action"})
    assert r.status_code == 201
    item_id = r.json()["id"]

    # Associate tag with action item
    r = client.post(f"/action-items/{item_id}/tags/{tag_id}")
    assert r.status_code == 204

    # Fetch action item and check it has the tag
    r = client.get(f"/action-items/{item_id}")
    assert r.status_code == 200
    item = r.json()
    assert len(item["tags"]) == 1
    assert item["tags"][0]["name"] == "action-tag"

    # Remove tag from action item
    r = client.delete(f"/action-items/{item_id}/tags/{tag_id}")
    assert r.status_code == 204

    # Fetch action item again and check tag is removed
    r = client.get(f"/action-items/{item_id}")
    assert r.status_code == 200
    item = r.json()
    assert len(item["tags"]) == 0