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


def test_extract_action_items_enhanced_patterns():
    text = """
    Urgent: fix security vulnerability by tomorrow
    @john should review the database migration
    What should we do about the failing tests?
    After deployment, monitor error rates
    Schedule team meeting for next week
    Need to upgrade dependencies immediately
    Contact client about project deadline
    Investigate performance issue by end of day
    """.strip()
    
    items = extract_action_items(text)
    
    # Priority and urgency
    assert any("fix security vulnerability" in item for item in items)
    
    # Assignment patterns
    assert any("@john" in item for item in items)
    
    # Question patterns
    assert any("failing tests" in item for item in items)
    
    # Conditional actions
    assert any("deployment" in item and "monitor" in item for item in items)
    
    # Time-based patterns
    assert any("next week" in item for item in items)
    
    # Additional action verbs
    assert any("upgrade dependencies" in item.lower() for item in items)
    assert any("contact client" in item.lower() for item in items)
    assert any("investigate performance" in item.lower() for item in items)
