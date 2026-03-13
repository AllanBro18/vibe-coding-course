def test_create_list_and_patch_notes(client):
    payload = {"title": "Test", "content": "Hello world"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["title"] == "Test"
    assert "created_at" in data and "updated_at" in data

    r = client.get("/notes/")
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    r = client.get("/notes/", params={"q": "Hello", "limit": 10, "sort": "-created_at"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    note_id = data["id"]
    r = client.patch(f"/notes/{note_id}", json={"title": "Updated"})
    assert r.status_code == 200
    patched = r.json()
    assert patched["title"] == "Updated"


def test_note_validation_and_delete(client):
    # Empty title should fail validation
    r = client.post("/notes/", json={"title": "   ", "content": "Body"})
    assert r.status_code == 422

    # Empty content should fail validation
    r = client.post("/notes/", json={"title": "Valid", "content": ""})
    assert r.status_code == 422

    # Create a valid note then delete it
    r = client.post("/notes/", json={"title": "To delete", "content": "Some content"})
    assert r.status_code == 201
    note_id = r.json()["id"]

    r = client.delete(f"/notes/{note_id}")
    assert r.status_code == 204

    # Subsequent fetch should return 404
    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 404


def test_notes_pagination_and_sorting(client):
    # Create multiple notes
    created_ids: list[int] = []
    for i in range(3):
        r = client.post(
            "/notes/",
            json={"title": f"Note {i}", "content": f"Content {i}"},
        )
        assert r.status_code == 201
        created_ids.append(r.json()["id"])

    # Verify sorting by id ascending
    r = client.get("/notes/", params={"sort": "id"})
    assert r.status_code == 200
    items = r.json()
    ids = [item["id"] for item in items]
    assert ids == sorted(ids)

    # Pagination: skip first, take one
    r = client.get("/notes/", params={"sort": "id", "skip": 1, "limit": 1})
    assert r.status_code == 200
    page = r.json()
    assert len(page) == 1
    assert page[0]["id"] == ids[1]

    # Invalid sort falls back to -created_at; compare with explicit -created_at
    r_default = client.get("/notes/", params={"sort": "-created_at"})
    r_invalid = client.get("/notes/", params={"sort": "does_not_exist"})
    assert r_default.status_code == 200
    assert r_invalid.status_code == 200
    ids_default = [item["id"] for item in r_default.json()]
    ids_invalid = [item["id"] for item in r_invalid.json()]
    assert ids_invalid == ids_default
