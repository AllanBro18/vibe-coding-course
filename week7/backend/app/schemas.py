from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    project_id: int | None = None

    @field_validator("title", "content", mode="before")
    @classmethod
    def strip_whitespace(cls, value: str) -> str:
        if isinstance(value, str):
            value = value.strip()
        return value

    @field_validator("content")
    @classmethod
    def validate_content_length(cls, value: str) -> str:
        if len(value) > 10000:
            raise ValueError("Content must be 10000 characters or less")
        return value

    @field_validator("content")
    @classmethod
    def validate_no_script_tags(cls, value: str) -> str:
        if "<script" in value.lower():
            raise ValueError("Content cannot contain script tags")
        return value


class NoteRead(BaseModel):
    id: int
    title: str
    content: str
    project_id: int | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotePatch(BaseModel):
    title: str | None = None
    content: str | None = None


class ActionItemCreate(BaseModel):
    description: str = Field(..., min_length=1)
    project_id: int | None = None

    @field_validator("description", mode="before")
    @classmethod
    def strip_whitespace(cls, value: str) -> str:
        if isinstance(value, str):
            value = value.strip()
        return value


class ActionItemRead(BaseModel):
    id: int
    description: str
    completed: bool
    project_id: int | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ActionItemPatch(BaseModel):
    description: str | None = None
    completed: bool | None = None


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name_not_reserved(cls, value: str) -> str:
        reserved_names = ["admin", "system", "root", "default"]
        if value.lower().strip() in reserved_names:
            raise ValueError("Project name cannot be a reserved word")
        return value.strip()

    @field_validator("description")
    @classmethod
    def validate_description_length(cls, value: str | None) -> str | None:
        if value and len(value) > 1000:
            raise ValueError("Description must be 1000 characters or less")
        return value


class ProjectPatch(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None


class ProjectRead(BaseModel):
    id: int
    name: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
