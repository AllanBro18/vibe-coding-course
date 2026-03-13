from __future__ import annotations

import asyncio
import logging
import os
import sys
from typing import Any, Dict, List, Optional

import httpx
from mcp.server.fastmcp import FastMCP
from mcp.types import EmbeddedResource

from .movie_api import (
    MovieApiError,
    MovieApiRateLimitError,
    MovieDetails,
    MovieSummary,
    get_movie_details,
    search_movies,
)


logger = logging.getLogger("week3_movie_mcp")


def _setup_logging() -> None:
    handler = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(name)s - %(message)s",
    )
    handler.setFormatter(formatter)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)


mcp = FastMCP("movie-mcp")


@mcp.tool()
async def search_movies_tool(
    title: str,
    year: Optional[int] = None,
    limit: int = 10,
) -> Dict[str, Any]:
    """
    Search for movies by title (and optional year).

    Returns a list of matching movies with id, title, year, and type.
    """
    api_key = os.environ.get("OMDB_API_KEY")
    if not api_key:
        return {
            "error": "OMDB_API_KEY is not set. Please set this environment variable with your OMDb API key.",
        }

    if not title.strip():
        return {"error": "Title must not be empty."}

    # Apply basic bounds to limit to avoid excessive responses.
    limit = max(1, min(limit, 20))

    logger.info("search_movies_tool called title=%r year=%r limit=%r", title, year, limit)

    async with httpx.AsyncClient() as client:
        try:
            movies: List[MovieSummary] = await search_movies(
                client=client,
                api_key=api_key,
                title=title,
                year=year,
                limit=limit,
            )
        except MovieApiRateLimitError as exc:
            logger.warning("Movie API rate limit hit: %s", exc)
            return {
                "error": "The movie API reported a rate limit or too many requests. Please wait a bit and try again.",
                "details": str(exc),
            }
        except MovieApiError as exc:
            logger.error("Movie API error in search_movies_tool: %s", exc)
            return {"error": "Movie API error during search.", "details": str(exc)}
        except ValueError as exc:
            return {"error": str(exc)}

    return {
        "movies": [
            {
                "id": movie.id,
                "title": movie.title,
                "year": movie.year,
                "type": movie.type,
            }
            for movie in movies
        ],
        "count": len(movies),
    }


@mcp.tool()
async def get_movie_details_tool(movie_id: str) -> Dict[str, Any]:
    """
    Get detailed information for a movie by its ID (e.g., IMDB ID).
    """
    api_key = os.environ.get("OMDB_API_KEY")
    if not api_key:
        return {
            "error": "OMDB_API_KEY is not set. Please set this environment variable with your OMDb API key.",
        }

    if not movie_id.strip():
        return {"error": "movie_id must not be empty."}

    logger.info("get_movie_details_tool called movie_id=%r", movie_id)

    async with httpx.AsyncClient() as client:
        try:
            details: MovieDetails = await get_movie_details(
                client=client,
                api_key=api_key,
                movie_id=movie_id,
            )
        except MovieApiRateLimitError as exc:
            logger.warning("Movie API rate limit hit: %s", exc)
            return {
                "error": "The movie API reported a rate limit or too many requests. Please wait a bit and try again.",
                "details": str(exc),
            }
        except MovieApiError as exc:
            logger.error("Movie API error in get_movie_details_tool: %s", exc)
            return {"error": "Movie API error while fetching details.", "details": str(exc)}
        except ValueError as exc:
            return {"error": str(exc)}

    return {
        "id": details.id,
        "title": details.title,
        "year": details.year,
        "type": details.type,
        "plot": details.plot,
        "genre": details.genre,
        "runtime_minutes": details.runtime_minutes,
        "director": details.director,
        "actors": details.actors,
        "imdb_rating": details.imdb_rating,
    }


@mcp.resource("movie:by-id/{movie_id}")
async def movie_resource(movie_id: str) -> EmbeddedResource:
    """
    Expose movie details as a resource so they can be fetched like a file.
    """
    api_key = os.environ.get("OMDB_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OMDB_API_KEY is not set. Please set this environment variable with your OMDb API key."
        )

    async with httpx.AsyncClient() as client:
        details = await get_movie_details(client=client, api_key=api_key, movie_id=movie_id)

    text_lines = [
        f"Title: {details.title}",
        f"Year: {details.year}",
        f"Type: {details.type}",
        f"Genre: {details.genre}",
        f"Runtime (minutes): {details.runtime_minutes}",
        f"Director: {details.director}",
        f"Actors: {details.actors}",
        "",
        f"Plot: {details.plot}",
    ]
    text = "\n".join(line for line in text_lines if line is not None)

    return EmbeddedResource(uri=f"movie://{details.id}", mimeType="text/plain", text=text)


def main() -> None:
    """
    Entrypoint for running the MCP server over STDIO.
    """
    _setup_logging()
    # FastMCP's run() starts the stdio server by default.
    mcp.run()


if __name__ == "__main__":
    main()

