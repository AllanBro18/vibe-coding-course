import json
import pytest

from ..app.services import extract as extract_service
from ..app.services.extract import extract_action_items, extract_action_items_llm


def test_extract_bullets_and_checkboxes():
    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()

    items = extract_action_items(text)
    assert "Set up database" in items
    assert "implement API extract endpoint" in items
    assert "Write tests" in items


def test_extract_action_items_llm_bulleted_lists(monkeypatch: pytest.MonkeyPatch):
    def fake_chat(*, model: str, messages, format: str):
        assert model == "llama3.1:8b"
        assert format == "json"
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
        return {
            "message": {
                "content": json.dumps(
                    ["Set up database", "Implement API extract endpoint", "Write tests"]
                )
            }
        }

    monkeypatch.setattr(extract_service, "chat", fake_chat)

    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    """.strip()

    items = extract_action_items_llm(text)
    assert items == ["Set up database", "Implement API extract endpoint", "Write tests"]


def test_extract_action_items_llm_keyword_prefixed_todo(monkeypatch: pytest.MonkeyPatch):
    def fake_chat(*, model: str, messages, format: str):
        return {"message": {"content": json.dumps(["Email the client", "Update README"])}}  # noqa: E501

    monkeypatch.setattr(extract_service, "chat", fake_chat)

    text = """
    TODO: email the client
    Action: update README
    """.strip()

    items = extract_action_items_llm(text)
    assert items == ["Email the client", "Update README"]


def test_extract_action_items_llm_empty_input(monkeypatch: pytest.MonkeyPatch):
    def fake_chat(*, model: str, messages, format: str):
        return {"message": {"content": "[]"}}

    monkeypatch.setattr(extract_service, "chat", fake_chat)

    assert extract_action_items_llm("") == []
