from __future__ import annotations

from typing import Any, Dict

import pytest

from .movie_api import (
    MovieApiError,
    _check_response_for_errors,
    _parse_float,
    _parse_int,
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("123", 123),
        ("123 min", 123),
        ("N/A", None),
        ("", None),
        (None, None),
        ("abc", None),
    ],
)
def test_parse_int(value: Any, expected: int | None) -> None:
    assert _parse_int(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("7.5", 7.5),
        ("N/A", None),
        ("", None),
        (None, None),
        ("not-a-number", None),
    ],
)
def test_parse_float(value: Any, expected: float | None) -> None:
    assert _parse_float(value) == expected


def test_check_response_for_errors_ok() -> None:
    data: Dict[str, Any] = {"Response": "True", "Search": []}
    # Should not raise
    _check_response_for_errors(data)


def test_check_response_for_errors_generic_error() -> None:
    data: Dict[str, Any] = {"Response": "False", "Error": "Movie not found!"}
    with pytest.raises(MovieApiError):
        _check_response_for_errors(data)

