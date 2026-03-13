from __future__ import annotations

import asyncio
import os

import httpx

from .movie_api import get_movie_details, search_movies


async def main() -> None:
    api_key = os.environ.get("OMDB_API_KEY")
    if not api_key:
        raise SystemExit("OMDB_API_KEY is not set.")

    async with httpx.AsyncClient() as client:
        movies = await search_movies(client, api_key, title="Inception", year=2010, limit=3)
        print("Search results:", movies)
        if movies:
            details = await get_movie_details(client, api_key, movie_id=movies[0].id)
            print("First result details:", details)


if __name__ == "__main__":
    asyncio.run(main())

