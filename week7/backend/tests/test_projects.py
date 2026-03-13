def test_create_and_fetch_project_with_related_items(client):
    # Create a project
    r = client.post(
        "/projects/",
        json={"name": "Project Alpha", "description": "First project"},
    )
    assert r.status_code == 201, r.text
    project = r.json()
    project_id = project["id"]

    # Create a note and action item associated with the project
    r = client.post(
        "/notes/",
        json={"title": "Project note", "content": "Some content", "project_id": project_id},
    )
    assert r.status_code == 201
    note = r.json()
    assert note["project_id"] == project_id

    r = client.post(
        "/action-items/",
        json={"description": "Project task", "project_id": project_id},
    )
    assert r.status_code == 201
    item = r.json()
    assert item["project_id"] == project_id

    # Fetch project and ensure it still exists
    r = client.get(f"/projects/{project_id}")
    assert r.status_code == 200
    fetched = r.json()
    assert fetched["id"] == project_id
    assert fetched["name"] == "Project Alpha"
