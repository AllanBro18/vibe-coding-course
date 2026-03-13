# API Documentation

## Overview

The Modern Software Dev Starter is a notes and action items management application built with FastAPI.

## Base URL

`http://localhost:8000`

## Authentication

None (unauthenticated endpoints)

## Notes Endpoints

### List Notes

```
GET /notes/
```

**Response (200):**

```json
[
  {
    "id": 1,
    "title": "My Note",
    "content": "Note content here"
  }
]
```

### Create Note

```
POST /notes/
Content-Type: application/json
```

**Request:**

```json
{
  "title": "Note Title",
  "content": "Note content"
}
```

**Response (201):**

```json
{
  "id": 1,
  "title": "Note Title",
  "content": "Note content"
}
```

### Get Note by ID

```
GET /notes/{id}
```

**Response (200):**

```json
{
  "id": 1,
  "title": "Note Title",
  "content": "Note content"
}
```

### Search Notes

```
GET /notes/search/?q={query}
```

Query Parameters:

- `q` (optional): Search term (matches title or content, case-sensitive)

**Response (200):**

```json
[
  {
    "id": 1,
    "title": "My Note",
    "content": "Note content"
  }
]
```

## Action Items Endpoints

### List Action Items

```
GET /action-items/
```

**Response (200):**

```json
[
  {
    "id": 1,
    "description": "Tasks to do",
    "completed": false
  }
]
```

### Create Action Item

```
POST /action-items/
Content-Type: application/json
```

**Request:**

```json
{
  "description": "Task description"
}
```

**Response (201):**

```json
{
  "id": 1,
  "description": "Task description",
  "completed": false
}
```

### Get Action Item by ID

```
GET /action-items/{id}
```

**Response (200):**

```json
{
  "id": 1,
  "description": "Task description",
  "completed": false
}
```

### Complete Action Item

```
PUT /action-items/{id}/complete
```

**Response (200):**

```json
{
  "id": 1,
  "description": "Task description",
  "completed": true
}
```

## Status Codes

- `200 OK`: Successful GET/PUT request
- `201 Created`: Successful POST request
- `404 Not Found`: Resource not found
- `400 Bad Request`: Invalid request data
- `500 Internal Server Error`: Server error

## Interactive API Docs

Swagger UI: `http://localhost:8000/docs`
ReDoc: `http://localhost:8000/redoc`

---

Last updated: 2026-03-12
