from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class NoteCreate(BaseModel):
    content: str = Field(min_length=1)


class NoteOut(BaseModel):
    id: int
    content: str
    created_at: str


class ActionItemOut(BaseModel):
    id: int
    note_id: Optional[int] = None
    text: str
    done: bool = False
    created_at: Optional[str] = None


class ExtractActionItemsRequest(BaseModel):
    text: str = Field(min_length=1)
    save_note: bool = False


class ExtractedActionItem(BaseModel):
    id: int
    text: str


class ExtractActionItemsResponse(BaseModel):
    note_id: Optional[int] = None
    items: List[ExtractedActionItem]


class MarkDoneRequest(BaseModel):
    done: bool = True


class MarkDoneResponse(BaseModel):
    id: int
    done: bool

