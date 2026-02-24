"""
Projects API endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

from app.repository.project_repo import (
    get_all_projects,
    get_project_by_id,
    get_project_by_name,
    create_project,
    update_project,
    delete_project_by_id,
    delete_project_by_name,
    search_projects
)

router = APIRouter(prefix="/api", tags=["Projects"])


class ProjectRequest(BaseModel):
    name: str
    location: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class ProjectUpdateRequest(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


@router.get("/projects")
def get_projects(skip: int = Query(0, ge=0), limit: int = Query(1000, ge=1, le=5000)):
    """Get all projects with pagination"""
    try:
        projects = get_all_projects(skip=skip, limit=limit)
        return {
            "status": "SUCCESS",
            "project_count": len(projects),
            "projects": projects
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch projects: {str(e)}")


@router.get("/projects/{project_id}")
def get_project(project_id: int):
    """Get a specific project by ID"""
    try:
        project = get_project_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return {
            "status": "SUCCESS",
            "project": project
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch project: {str(e)}")


@router.post("/projects")
def create_new_project(project: ProjectRequest):
    """Create a new project"""
    try:
        result = create_project(
            name=project.name,
            location=project.location,
            city=project.city,
            state=project.state,
            country=project.country,
            latitude=project.latitude,
            longitude=project.longitude
        )
        return {
            "status": "SUCCESS",
            "message": "Project created successfully",
            "project": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create project: {str(e)}")


@router.put("/projects/{project_id}")
def update_project_by_id(project_id: int, project: ProjectUpdateRequest):
    """Update a project by ID"""
    try:
        existing = get_project_by_id(project_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Project not found")
        
        updated = update_project(project_id, **project.dict(exclude_unset=True))
        return {
            "status": "SUCCESS",
            "message": "Project updated successfully",
            "project": updated
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update project: {str(e)}")


# NOTE: DELETE /api/projects (by query param) is handled by po_management.router
# which is registered first in main.py and uses the more comprehensive
# delete_project() from po_management_repo.py. Do NOT duplicate it here.



@router.delete("/projects/{project_id}")
def delete_project_by_id_endpoint(project_id: int):
    """Delete a project by ID"""
    try:
        success = delete_project_by_id(project_id)
        if not success:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return {
            "status": "SUCCESS",
            "message": "Project deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete project: {str(e)}")


@router.get("/projects/search")
def search(q: str = Query(..., min_length=1, description="Search term")):
    """Search projects by name or description"""
    try:
        projects = search_projects(q)
        return {
            "status": "SUCCESS",
            "project_count": len(projects),
            "projects": projects
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search projects: {str(e)}")
