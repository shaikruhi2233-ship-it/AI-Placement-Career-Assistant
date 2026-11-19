from fastapi import APIRouter

from app import schemas
from app.services import learning_portal, skill_resources

router = APIRouter(prefix="/learning", tags=["Learning Portals"])


@router.get("/portals", response_model=schemas.LearningPortalsOut)
def get_portals():
    return learning_portal.get_learning_portals()


@router.get("/resources/{skill}", response_model=schemas.SkillResourcesOut)
def get_skill_resources(skill: str):
    """Priority 4 - categorized learning resources for a single skill:
    YouTube, Notes, Documentation, Course, Practice, Project."""
    return skill_resources.get_resources(skill)
