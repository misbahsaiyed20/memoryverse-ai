"""Dashboard routes. Real stats — composes CareerBrainService for
knowledge counts rather than re-querying knowledge_nodes here."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.document import Document
from app.models.user import User
from app.services.career_brain_service import CareerBrainService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats")
def get_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    documents = (
        db.query(Document)
        .filter(Document.user_id == current_user.id)
        .order_by(Document.created_at.desc())
        .all()
    )

    by_status: dict[str, int] = {}
    for doc in documents:
        by_status[doc.status.value] = by_status.get(doc.status.value, 0) + 1

    knowledge_counts = CareerBrainService(db).get_entity_counts(current_user.id)

    return {
        "documents": {"total": len(documents), "by_status": by_status},
        "knowledge": knowledge_counts,
        "recent_documents": [
            {
                "id": str(doc.id),
                "filename": doc.title,
                "status": doc.status.value,
                "created_at": doc.created_at.isoformat(),
            }
            for doc in documents[:5]
        ],
        # Kept for any existing frontend code still reading the flat
        # Sprint 2 shape directly instead of documents.total/knowledge.*.
        "skills": knowledge_counts.get("SKILL", 0),
        "projects": knowledge_counts.get("PROJECT", 0),
        "certificates": knowledge_counts.get("CERTIFICATE", 0),
    }
