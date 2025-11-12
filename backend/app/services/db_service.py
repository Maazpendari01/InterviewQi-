from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.database import InterviewSession, QuestionResponse, WeakArea
from datetime import datetime
from typing import List, Dict, Optional


class DatabaseService:
    """Service for database operations"""

    def __init__(self, db: Session):
        self.db = db

    # ==================== SESSION OPERATIONS ====================

    def create_session(
        self,
        session_id: str,
        category: str,
        difficulty: str = "medium",
        user_id: int = None,
    ) -> InterviewSession:
        """Create new interview session"""
        session = InterviewSession(
            session_id=session_id,
            user_id=user_id,
            category=category,
            difficulty=difficulty,
            started_at=datetime.utcnow(),
            is_completed=False,
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_session(self, session_id: str) -> Optional[InterviewSession]:
        """Get session by session_id"""
        return (
            self.db.query(InterviewSession)
            .filter(InterviewSession.session_id == session_id)
            .first()
        )

    def get_session_by_db_id(self, db_id: int) -> Optional[InterviewSession]:
        """Get session by database ID"""
        return (
            self.db.query(InterviewSession).filter(InterviewSession.id == db_id).first()
        )

    # ==================== RESPONSE OPERATIONS ====================

    def save_response(
        self,
        session_db_id: int,
        question_id: str,
        question_text: str,
        question_number: int,
        user_answer: str,
        evaluation: str,
        score: int,
        category: str,
    ) -> QuestionResponse:
        """Save individual question response"""
        response = QuestionResponse(
            session_id=session_db_id,
            question_id=question_id,
            question_text=question_text,
            question_number=question_number,
            user_answer=user_answer,
            evaluation=evaluation,
            score=score,
            category=category,
            created_at=datetime.utcnow(),
        )

        self.db.add(response)
        self.db.commit()
        self.db.refresh(response)
        return response

    def get_session_responses(self, session_db_id: int) -> List[QuestionResponse]:
        """Get all responses for a session"""
        return (
            self.db.query(QuestionResponse)
            .filter(QuestionResponse.session_id == session_db_id)
            .order_by(QuestionResponse.question_number)
            .all()
        )

    # ==================== COMPLETION ====================

    def complete_session(
        self, session_id: str, transcript: List[Dict]
    ) -> InterviewSession:
        """Mark session as complete and calculate stats"""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        # Get all responses for this session
        responses = self.get_session_responses(session.id)

        if responses:
            # Calculate average score
            avg_score = sum(r.score for r in responses) / len(responses)
            session.average_score = round(avg_score, 1)
            session.total_questions = len(responses)

        # ✅ Serialize any Message objects to dicts
        def serialize_transcript(messages):
            serialized = []
            for m in messages:
                if hasattr(m, "role") and hasattr(m, "content"):
                    serialized.append({"role": m.role, "content": m.content})
                elif isinstance(m, dict):
                    serialized.append(m)
                else:
                    serialized.append({"role": "unknown", "content": str(m)})
            return serialized

        session.transcript = serialize_transcript(transcript)
        session.completed_at = datetime.utcnow()
        session.is_completed = True

        self.db.commit()
        self.db.refresh(session)
        return session

    # ==================== ANALYTICS ====================

    def get_total_sessions(self) -> int:
        """Get total number of sessions"""
        return self.db.query(InterviewSession).count()

    def get_completed_sessions(self) -> int:
        """Get number of completed sessions"""
        return (
            self.db.query(InterviewSession)
            .filter(InterviewSession.is_completed == True)
            .count()
        )

    def get_average_score(self) -> float:
        """Get average score across all sessions"""
        avg = self.db.query(func.avg(InterviewSession.average_score)).scalar()
        return round(avg, 1) if avg else 0

    def get_sessions_by_category(self) -> Dict[str, int]:
        """Get session count by category"""
        results = (
            self.db.query(InterviewSession.category, func.count(InterviewSession.id))
            .group_by(InterviewSession.category)
            .all()
        )
        return {category: count for category, count in results}

    def get_recent_sessions(
        self, limit: int = 10, user_id: int = None
    ) -> List[InterviewSession]:
        """Get recent sessions"""
        query = self.db.query(InterviewSession)
        if user_id:
            query = query.filter(InterviewSession.user_id == user_id)

        return query.order_by(InterviewSession.started_at.desc()).limit(limit).all()

    # ==================== WEAK AREAS ====================

    def identify_weak_areas(
        self, user_id: int = None, threshold: int = 60
    ) -> Dict[str, Dict]:
        """Find topics where users struggle (score < threshold)"""
        query = self.db.query(QuestionResponse)

        if user_id:
            query = query.join(
                InterviewSession, QuestionResponse.session_id == InterviewSession.id
            ).filter(InterviewSession.user_id == user_id)
        weak_responses = query.filter(QuestionResponse.score < threshold).all()

        weak_by_category = {}
        for response in weak_responses:
            category = response.category
            if category not in weak_by_category:
                weak_by_category[category] = {
                    "count": 0,
                    "total_score": 0,
                    "avg_score": 0,
                    "questions": [],
                }
            weak_by_category[category]["count"] += 1
            weak_by_category[category]["total_score"] += response.score
            weak_by_category[category]["questions"].append(response.question_id)

        for category in weak_by_category:
            count = weak_by_category[category]["count"]
            total = weak_by_category[category]["total_score"]
            weak_by_category[category]["avg_score"] = round(total / count, 1)
            del weak_by_category[category]["total_score"]
        return weak_by_category

    def get_user_progress(self, user_id: int, limit: int = 20) -> Dict:
        """Get user's progress over time"""
        sessions = (
            self.db.query(InterviewSession)
            .filter(
                InterviewSession.user_id == user_id,
                InterviewSession.is_completed == True,
            )
            .order_by(InterviewSession.started_at.desc())
            .limit(limit)
            .all()
        )

        if not sessions:
            return {
                "total_sessions": 0,
                "progress": [],
                "improvement": 0,
            }

        progress = []
        for session in reversed(sessions):
            progress.append(
                {
                    "date": session.started_at.isoformat(),
                    "category": session.category,
                    "score": session.average_score,
                    "questions": session.total_questions,
                }
            )

        if len(progress) > 1:
            recent_avg = sum(p["score"] for p in progress[-5:]) / min(5, len(progress))
            older_avg = sum(p["score"] for p in progress[:5]) / min(5, len(progress))
            improvement = round(recent_avg - older_avg, 1)
        else:
            improvement = 0

        return {
            "total_sessions": len(sessions),
            "progress": progress,
            "improvement": improvement,
        }
