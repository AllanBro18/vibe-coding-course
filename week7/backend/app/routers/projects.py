from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Project
from ..schemas import ProjectCreate, ProjectPatch, ProjectRead

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=ProjectRead, status_code=201)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)) -> ProjectRead:
    project = Project(name=payload.name, description=payload.description)
    db.add(project)
    db.flush()
    db.refresh(project)
    return ProjectRead.model_validate(project)


@router.get("/", response_model=list[ProjectRead])
def list_projects(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of items to skip for pagination"),
    limit: int = Query(
        50,
        ge=1,
        le=200,
        description="Maximum number of items to return (1-200)",
    ),
) -> list[ProjectRead]:
    rows = db.execute(select(Project).offset(skip).limit(limit)).scalars().all()
    return [ProjectRead.model_validate(row) for row in rows]


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project_id: int, db: Session = Depends(get_db)) -> ProjectRead:
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectRead.model_validate(project)


@router.patch("/{project_id}", response_model=ProjectRead)
def patch_project(project_id: int, payload: ProjectPatch, db: Session = Depends(get_db)) -> ProjectRead:
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if payload.name is not None:
        project.name = payload.name
    if payload.description is not None:
        project.description = payload.description
    db.add(project)
    db.flush()
    db.refresh(project)
    return ProjectRead.model_validate(project)


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: int, db: Session = Depends(get_db)) -> None:
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.flush()
