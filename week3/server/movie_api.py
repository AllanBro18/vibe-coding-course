from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import httpx


OMDB_BASE_URL = "https://www.omdbapi.com/"


class MovieApiError(Exception):
    """Base error for movie API failures."""


class MovieApiRateLimitError(MovieApiError):
    """Error raised when the upstream API appears to be rate limited."""


@dataclass
class MovieSummary:
    id: str
    title: str
    year: Optional[int]
    type: Optional[str]


@dataclass
class MovieDetails:
    id: str
    title: str
    year: Optional[int]
    type: Optional[str]
    plot: Optional[str]
    genre: Optional[str]
    runtime_minutes: Optional[int]
    director: Optional[str]
    actors: Optional[str]
    imdb_rating: Optional[float]
    raw: Dict[str, Any]


def _parse_int(value: Any) -> Optional[int]:
    if value in (None, "", "N/A"):
        return None
    try:
        return int(str(value).split(" ", 1)[0])
    except (TypeError, ValueError):
        return None


def _parse_float(value: Any) -> Optional[float]:
    if value in (None, "", "N/A"):
        return None
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return None


def _check_response_for_errors(data: Dict[str, Any]) -> None:
    # OMDb includes "Response": "False" and an "Error" message on failure.
    if data.get("Response") == "False":
        message = str(data.get("Error") or "Unknown error from movie API")
        lower = message.lower()
        if "limit" in lower or "too many requests" in lower:
            raise MovieApiRateLimitError(message)
        raise MovieApiError(message)


async def search_movies(
    client: httpx.AsyncClient,
    api_key: str,
    title: str,
    year: Optional[int] = None,
    limit: int = 10,
) -> List[MovieSummary]:
    if not title.strip():
        raise ValueError("Title must not be empty.")
    limit = max(1, min(limit, 20))

    params: Dict[str, Any] = {"apikey": api_key, "s": title.strip()}
    if year is not None:
        params["y"] = year

    try:
        response = await client.get(OMDB_BASE_URL, params=params, timeout=10.0)
    except httpx.RequestError as exc:
        raise MovieApiError(f"Network error talking to movie API: {exc}") from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise MovieApiError("Movie API returned invalid JSON.") from exc

    _check_response_for_errors(data)

    results: List[MovieSummary] = []
    for item in data.get("Search", [])[:limit]:
        imdb_id = str(item.get("imdbID") or "").strip()
        if not imdb_id:
            # Skip malformed entries rather than failing the whole call.
            continue
        results.append(
            MovieSummary(
                id=imdb_id,
                title=str(item.get("Title") or "").strip(),
                year=_parse_int(item.get("Year")),
                type=str(item.get("Type") or "").strip() or None,
            )
        )
    return results


async def get_movie_details(
    client: httpx.AsyncClient,
    api_key: str,
    movie_id: str,
) -> MovieDetails:
    movie_id = movie_id.strip()
    if not movie_id:
        raise ValueError("movie_id must not be empty.")

    params = {"apikey": api_key, "i": movie_id, "plot": "full"}

    try:
        response = await client.get(OMDB_BASE_URL, params=params, timeout=10.0)
    except httpx.RequestError as exc:
        raise MovieApiError(f"Network error talking to movie API: {exc}") from exc

    try:
        data: Dict[str, Any] = response.json()
    except ValueError as exc:
        raise MovieApiError("Movie API returned invalid JSON.") from exc

    _check_response_for_errors(data)

    imdb_id = str(data.get("imdbID") or "").strip() or movie_id
    return MovieDetails(
        id=imdb_id,
        title=str(data.get("Title") or "").strip(),
        year=_parse_int(data.get("Year")),
        type=str(data.get("Type") or "").strip() or None,
        plot=str(data.get("Plot") or "").strip() or None,
        genre=str(data.get("Genre") or "").strip() or None,
        runtime_minutes=_parse_int(data.get("Runtime")),
        director=str(data.get("Director") or "").strip() or None,
        actors=str(data.get("Actors") or "").strip() or None,
        imdb_rating=_parse_float(data.get("imdbRating")),
        raw=data,
    )

