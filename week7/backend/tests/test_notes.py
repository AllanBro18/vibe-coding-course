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
    # Create multiple notes with different timestamps and content
    created_notes = []
    for i in range(10):
        r = client.post(
            "/notes/",
            json={"title": f"Note {i:02d}", "content": f"Content {i} with search term"},
        )
        assert r.status_code == 201
        created_notes.append(r.json())

    # Sort notes by ID ascending and verify order
    r = client.get("/notes/", params={"sort": "id"})
    assert r.status_code == 200
    items = r.json()
    ids = [item["id"] for item in items]
    assert ids == sorted(ids)

    # Test descending sort
    r = client.get("/notes/", params={"sort": "-id"})
    assert r.status_code == 200
    items_desc = r.json()
    ids_desc = [item["id"] for item in items_desc]
    assert ids_desc == sorted(ids, reverse=True)

    # Test pagination: skip first 3, take 2
    r = client.get("/notes/", params={"sort": "id", "skip": 3, "limit": 2})
    assert r.status_code == 200
    page = r.json()
    assert len(page) == 2
    assert page[0]["id"] == ids[3]
    assert page[1]["id"] == ids[4]

    # Test pagination with search: should filter then paginate
    r = client.get("/notes/", params={"q": "search", "sort": "id", "skip": 0, "limit": 5})
    assert r.status_code == 200
    search_results = r.json()
    assert len(search_results) == 5  # All notes contain "search term"
    search_ids = [item["id"] for item in search_results]
    assert search_ids == sorted(search_ids)

    # Test edge case: skip beyond total items
    r = client.get("/notes/", params={"sort": "id", "skip": 50, "limit": 10})
    assert r.status_code == 200
    empty_page = r.json()
    assert len(empty_page) == 0

    # Test edge case: limit = 1 (minimum allowed)
    r = client.get("/notes/", params={"sort": "id", "limit": 1})
    assert r.status_code == 200
    single_item = r.json()
    assert len(single_item) == 1

    # Test maximum limit (200)
    r = client.get("/notes/", params={"sort": "id", "limit": 200})
    assert r.status_code == 200
    max_limit = r.json()
    assert len(max_limit) <= 200

    # Test invalid sort field falls back to -created_at
    r_default = client.get("/notes/", params={"sort": "-created_at"})
    r_invalid = client.get("/notes/", params={"sort": "nonexistent_field"})
    assert r_default.status_code == 200
    assert r_invalid.status_code == 200
    default_ids = [item["id"] for item in r_default.json()]
    invalid_ids = [item["id"] for item in r_invalid.json()]
    assert invalid_ids == default_ids

    # Test sorting by title
    r = client.get("/notes/", params={"sort": "title"})
    assert r.status_code == 200
    title_sorted = r.json()
    titles = [item["title"] for item in title_sorted]
    assert titles == sorted(titles)

    # Test descending title sort
    r = client.get("/notes/", params={"sort": "-title"})
    assert r.status_code == 200
    title_desc = r.json()
    titles_desc = [item["title"] for item in title_desc]
    assert titles_desc == sorted(titles, reverse=True)

    # Test consistency: same results for same parameters
    r1 = client.get("/notes/", params={"sort": "id", "limit": 3})
    r2 = client.get("/notes/", params={"sort": "id", "limit": 3})
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json() == r2.json()

    # Test parameter validation: negative skip should fail
    r = client.get("/notes/", params={"skip": -1})
    assert r.status_code == 422  # Validation error

    # Test parameter validation: limit too low should fail (limit must be >= 1)
    r = client.get("/notes/", params={"limit": 0})
    assert r.status_code == 422  # Validation error

    # Test parameter validation: limit too high should fail
    r = client.get("/notes/", params={"limit": 201})
    assert r.status_code == 422  # Validation error
