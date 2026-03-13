from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Tag
from ..schemas import TagCreate, TagRead, TagUpdate

router = APIRouter(prefix="/tags", tags=["tags"])


@router.post("/", response_model=TagRead, status_code=201)
def create_tag(payload: TagCreate, db: Session = Depends(get_db)) -> TagRead:
    # Check if tag with this name already exists
    existing = db.scalar(select(Tag).where(Tag.name == payload.name))
    if existing:
        raise HTTPException(status_code=409, detail="Tag with this name already exists")
    
    tag = Tag(name=payload.name, color=payload.color)
    db.add(tag)
    db.flush()
    db.refresh(tag)
    return TagRead.model_validate(tag)


@router.get("/", response_model=list[TagRead])
def list_tags(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of items to skip for pagination"),
    limit: int = Query(
        50,
        ge=1,
        le=200,
        description="Maximum number of items to return (1-200)",
    ),
) -> list[TagRead]:
    rows = db.execute(select(Tag).offset(skip).limit(limit)).scalars().all()
    return [TagRead.model_validate(row) for row in rows]


@router.get("/{tag_id}", response_model=TagRead)
def get_tag(tag_id: int, db: Session = Depends(get_db)) -> TagRead:
    tag = db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return TagRead.model_validate(tag)


@router.put("/{tag_id}", response_model=TagRead)
def update_tag(tag_id: int, payload: TagCreate, db: Session = Depends(get_db)) -> TagRead:
    tag = db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    # Check if another tag with this name exists
    existing = db.scalar(select(Tag).where(Tag.name == payload.name, Tag.id != tag_id))
    if existing:
        raise HTTPException(status_code=409, detail="Tag with this name already exists")
    
    tag.name = payload.name
    tag.color = payload.color
    db.add(tag)
    db.flush()
    db.refresh(tag)
    return TagRead.model_validate(tag)


@router.patch("/{tag_id}", response_model=TagRead)
def patch_tag(tag_id: int, payload: TagUpdate, db: Session = Depends(get_db)) -> TagRead:
    tag = db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    if payload.name is not None:
        # Check if another tag with this name exists
        existing = db.scalar(select(Tag).where(Tag.name == payload.name, Tag.id != tag_id))
        if existing:
            raise HTTPException(status_code=409, detail="Tag with this name already exists")
        tag.name = payload.name
    
    if payload.color is not None:
        tag.color = payload.color
    
    db.add(tag)
    db.flush()
    db.refresh(tag)
    return TagRead.model_validate(tag)


@router.delete("/{tag_id}", status_code=204)
def delete_tag(tag_id: int, db: Session = Depends(get_db)) -> None:
    tag = db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    db.delete(tag)
    db.flush()