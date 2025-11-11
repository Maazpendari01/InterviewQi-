from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from ..models.database import get_db
from ..services.db_service import DatabaseService

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/stats")
async def get_platform_stats(db: Session = Depends(get_db)):
    """Get overall platform statistics"""
    db_service = DatabaseService(db)
    total_sessions = db_service.get_total_sessions()
    completed_sessions = db_service.get_completed_sessions()
    avg_score = db_service.get_average_score()
    by_category = db_service.get_sessions_by_category()

    return {
        "total_sessions": total_sessions,
        "completed_sessions": completed_sessions,
        "completion_rate": round(
            (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0, 1
        ),
        "average_score": avg_score,
        "by_category": by_category,
    }


@router.get("/weak-areas")
async def get_weak_areas(
    threshold: int = Query(default=60, ge=0, le=100),
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Find topics where users struggle (score < threshold)"""
    db_service = DatabaseService(db)
    weak_areas = db_service.identify_weak_areas(user_id=user_id, threshold=threshold)
    return {
        "threshold": threshold,
        "weak_areas": weak_areas,
        "total_categories": len(weak_areas),
    }


@router.get("/progress/{user_id}")
async def get_user_progress(
    user_id: int,
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get user's progress over time"""
    db_service = DatabaseService(db)
    progress_data = db_service.get_user_progress(user_id, limit)
    if progress_data["total_sessions"] == 0:
        return {
            "user_id": user_id,
            "message": "No sessions found for this user",
            "total_sessions": 0,
        }
    return {"user_id": user_id, **progress_data}


@router.get("/sessions/stats")
async def get_session_stats(
    category: Optional[str] = None, db: Session = Depends(get_db)
):
    """Get detailed session statistics"""
    db_service = DatabaseService(db)
    sessions = db_service.get_recent_sessions(limit=100)
    if category:
        sessions = [s for s in sessions if s.category == category]
    if not sessions:
        return {"message": "No sessions found", "total": 0}
    completed = [s for s in sessions if s.is_completed]
    scores = [s.average_score for s in completed if s.average_score]
    return {
        "total_sessions": len(sessions),
        "completed_sessions": len(completed),
        "completion_rate": round(len(completed) / len(sessions) * 100, 1)
        if sessions
        else 0,
        "average_score": round(sum(scores) / len(scores), 1) if scores else 0,
        "max_score": max(scores) if scores else 0,
        "min_score": min(scores) if scores else 0,
        "category_filter": category,
    }


@router.get("/leaderboard")
async def get_leaderboard(
    category: Optional[str] = None,
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """Get top performing sessions (leaderboard)"""
    from ..models.database import InterviewSession

    query = db.query(InterviewSession).filter(
        InterviewSession.is_completed == True,
        InterviewSession.average_score.isnot(None),
    )
    if category:
        query = query.filter(InterviewSession.category == category)
    top_sessions = (
        query.order_by(InterviewSession.average_score.desc()).limit(limit).all()
    )
    return {
        "leaderboard": [
            {
                "rank": idx + 1,
                "session_id": s.session_id,
                "category": s.category,
                "score": s.average_score,
                "questions": s.total_questions,
                "date": s.completed_at.isoformat() if s.completed_at else None,
            }
            for idx, s in enumerate(top_sessions)
        ],
        "total_entries": len(top_sessions),
    }
