from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.knowledge_node import EntityType
from app.models.user import User
from app.services.career_brain_service import CareerBrainService
from app.services.career_intelligence_service import CareerIntelligenceService
from app.utils.response import success_response

router = APIRouter(prefix="/career-brain", tags=["career-brain"])


@router.get("/summary")
def get_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = CareerBrainService(db)
    return success_response(service.get_entity_counts(current_user.id), "Career Brain summary.")


@router.get("/nodes")
def get_nodes(
    entity_type: EntityType | None = Query(default=None),
    related_to: str | None = Query(default=None, description="Filter to nodes linked to an entity with this name"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Covers skills / projects / certifications / internships / education /
    technologies / companies — all are just entity_type filters over the
    same evidence-backed query. "projects that use Python" is
    entity_type=PROJECT&related_to=Python."""
    service = CareerBrainService(db)
    nodes = service.get_nodes(current_user.id, entity_type=entity_type, related_to=related_to)
    return success_response({"nodes": nodes, "count": len(nodes)}, "Nodes retrieved.")


@router.get("/insights")
def get_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Reasoning over already-verified Career Brain data, not raw
    documents. missing_skills/learning_suggestions are the model's
    opinion, not evidence-backed facts — kept as separate fields so the
    frontend can label them distinctly."""
    service = CareerIntelligenceService(db)
    insights = service.get_insights(current_user.id)
    return success_response(insights.model_dump(), "Career insights generated.")


@router.get("/edges")
def get_edges(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = CareerBrainService(db)
    return success_response({"edges": service.get_edges(current_user.id)}, "Edges retrieved.")


@router.get("/timeline")
def get_timeline(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = CareerBrainService(db)
    return success_response({"timeline": service.get_timeline(current_user.id)}, "Timeline retrieved.")
