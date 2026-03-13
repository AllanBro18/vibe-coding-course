from backend.app.services.extract import extract_action_items


def test_extract_action_items_basic_markers():
    text = """
    This is a note
    - TODO: write tests
    - ACTION: review PR
    - Ship it!
    Not actionable
    """.strip()
    items = extract_action_items(text)
    assert "TODO: write tests" in items
    assert "ACTION: review PR" in items
    assert "Ship it!" in items
    assert "Not actionable" not in items


def test_extract_action_items_extended_patterns():
    text = """
    1. Fix login bug
    2. implement feature flag
    * Review deployment plan
    [ ] write docs
    [x] update changelog
    This is just commentary.
    """.strip()
    items = extract_action_items(text)

    assert "1. Fix login bug" in items
    assert "2. implement feature flag" in items
    assert "Review deployment plan" in {i.lstrip("* ").strip() for i in items}
    assert "[ ] write docs" in items
    assert "[x] update changelog" in items
    assert "This is just commentary." not in items
