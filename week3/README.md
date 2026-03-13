## Week 3 – Movie MCP Server

This week’s assignment implements a **local STDIO MCP server** that wraps the free
**OMDb** movie API. The server exposes tools to search for movies and fetch detailed
information, and is designed to work with **Claude Desktop**.

The code lives under `week3/server/`.

### 1. External API: OMDb

- **Base URL**: `https://www.omdbapi.com/`
- **Auth scheme**: API key passed as query parameter `apikey=...`
- **Key endpoints used**:
  - `GET /?s={title}&y={year?}&apikey={key}` – search for movies by title
  - `GET /?i={imdbID}&plot=full&apikey={key}` – detailed info for a specific movie

Obtain a free key from the OMDb website, then set it as an environment variable:

```powershell
$env:OMDB_API_KEY = "your_api_key_here"
```

The server expects `OMDB_API_KEY` to be set; if it is missing, tools return a clear error.

### 2. Project structure

- `week3/server/__init__.py` – package marker.
- `week3/server/movie_api.py` – async OMDb client with:
  - `search_movies(...)` – search movies by title/year with robust error handling.
  - `get_movie_details(...)` – fetch detailed information for a movie by ID.
- `week3/server/main.py` – MCP STDIO server using `FastMCP` from the `mcp` SDK:
  - Tool: `search_movies_tool`
  - Tool: `get_movie_details_tool`
  - Resource: `movie:by-id` (movie details as text)
  - Entrypoint: `main()` → `mcp.run_stdio_server()`
- `week3/server/test_movie_api.py` – small pytest suite for parsing and error helpers.
- `week3/server/manual_check.py` – manual script to verify the raw OMDb calls.

### 3. Setup instructions

From the repo root:

1. **Ensure Python 3.10+ is available.**
2. Install dependencies using `uv` (recommended by this project):

```powershell
uv sync
```

3. Set your OMDb API key in the current shell:

```powershell
$env:OMDB_API_KEY = "your_api_key_here"
```

4. (Optional) Run basic tests:

```powershell
uv run pytest week3/server/test_movie_api.py
```

5. (Optional) Manually check the API wrapper:

```powershell
uv run python -m week3.server.manual_check
```

This should print a small list of search results for “Inception” and details for the first one.

### 4. Running the MCP server (local STDIO)

To run the MCP server directly:

```powershell
uv run python -m week3.server.main
```

The server speaks MCP over **STDIO** and **must not print to stdout** outside of the MCP
protocol. Logging is configured to write to **stderr** instead.

### 5. Tools exposed

#### `search_movies_tool`

- **Description**: Search OMDb for movies by title (optionally year) and return a concise list.
- **Parameters**:
  - `title` (string, required): Movie title or partial title. Must not be empty.
  - `year` (integer, optional): Release year filter.
  - `limit` (integer, optional, default 10): Maximum number of results (1–20).
- **Response shape**:

```json
{
  "movies": [
    {
      "id": "tt1375666",
      "title": "Inception",
      "year": 2010,
      "type": "movie"
    }
  ],
  "count": 1
}
```

- **Error behavior**:
  - Missing `OMDB_API_KEY` → `{ "error": "OMDB_API_KEY is not set. ..." }`
  - Empty title → `{ "error": "Title must not be empty." }`
  - Upstream API/network problems → `{ "error": "Movie API error during search.", "details": "..." }`
  - Rate limit messages from OMDb are surfaced as:
    `{ "error": "The movie API reported a rate limit or too many requests. Please wait a bit and try again.", "details": "..." }`

#### `get_movie_details_tool`

- **Description**: Fetch detailed information for a single movie by its ID (e.g. IMDb ID).
- **Parameters**:
  - `movie_id` (string, required): Movie identifier (e.g. `"tt1375666"`). Must not be empty.
- **Response shape**:

```json
{
  "id": "tt1375666",
  "title": "Inception",
  "year": 2010,
  "type": "movie",
  "plot": "...",
  "genre": "Action, Sci-Fi",
  "runtime_minutes": 148,
  "director": "Christopher Nolan",
  "actors": "Leonardo DiCaprio, Joseph Gordon-Levitt, Ellen Page",
  "imdb_rating": 8.8
}
```

- **Error behavior**:
  - Missing `OMDB_API_KEY` → similar error object as above.
  - Empty `movie_id` → `{ "error": "movie_id must not be empty." }`
  - Invalid or unknown ID → error from OMDb wrapped as:
    `{ "error": "Movie API error while fetching details.", "details": "Movie not found!" }`
  - Rate-limit messages → same pattern as `search_movies_tool`.

### 6. Resource: `movie:by-id`

The server also exposes a simple **resource**:

- **Name**: `movie:by-id`
- **Parameters**:
  - `movie_id` (string, required): Identifier such as an IMDb ID.
- **Behavior**:
  - Fetches movie details via OMDb.
  - Returns an `EmbeddedResource` with:
    - `uri`: `movie://{id}`
    - `mimeType`: `"text/plain"`
    - `text`: Human-readable summary (title, year, genre, runtime, director, actors, and plot).

This allows clients that understand MCP resources to fetch movie details as if they were files.

### 7. Using the server from Claude Desktop

1. Make sure you can run the server manually:

```powershell
uv run python -m week3.server.main
```

2. Open your Claude Desktop MCP configuration file (on Windows it is typically in your
user profile directory, e.g. `claude_desktop_config.json`).

3. Add a new server entry similar to:

```jsonc
{
  "mcpServers": {
    "movie-mcp": {
      "command": "uv",
      "args": [
        "run",
        "python",
        "-m",
        "week3.server.main"
      ],
      "env": {
        "OMDB_API_KEY": "your_api_key_here",
        "PYTHONPATH": "C:\\Users\\allan\\OneDrive\\Documents\\Coding\\ppkpl\\modern-software-dev-assignments"
      }
    }
  }
}
```

If you see `ModuleNotFoundError: No module named 'week3'` in Claude Desktop logs, it means the
server process is starting outside the repo root. Setting `PYTHONPATH` to the repo root (as above)
fixes module resolution reliably.

4. Restart Claude Desktop so it picks up the new MCP server.

5. In a new chat, you can type prompts like:
   - “Use the `movie-mcp` tools to search for movies titled ‘Inception’.”
   - “Call `search_movies_tool` for ‘The Matrix’ and then `get_movie_details_tool` for the first result.”

Claude Desktop should list the `search_movies_tool`, `get_movie_details_tool`, and `movie:by-id`
resource and call them over STDIO.

