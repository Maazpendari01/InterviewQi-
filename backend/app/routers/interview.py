from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime

# Existing imports
from ..models.database import get_db
from ..services.db_service import DatabaseService
from ..services.interview_graph import InterviewGraph
from ..services.interview_state import InterviewState, Message

router = APIRouter(prefix="/api/interview", tags=["interview"])

# In-memory storage for active sessions (still needed during interview)
active_sessions: Dict[str, dict] = {}
graph = InterviewGraph()

class StartRequest(BaseModel):
    category: str = "coding"
    difficulty: str = "medium"

class AnswerRequest(BaseModel):
    session_id: str
    answer: str

@router.post("/start")
async def start_interview(request: StartRequest, db: Session = Depends(get_db)):
    """Start interview - now with database persistence"""

    # Generate unique session ID
    session_id = f"session_{datetime.now().timestamp()}"

    # Initialize LangGraph state
    state = InterviewState(
        messages=[],
        category=request.category,
        question_count=0,
        current_question="",
        current_question_id="",
        user_answer="",
        evaluation="",
        score=0
    )

    # Get first question from graph
    result = graph.start_node(state)
    state.update(result)

    # Save to database
    db_service = DatabaseService(db)
    db_session = db_service.create_session(
        session_id=session_id,
        category=request.category,
        difficulty=request.difficulty
    )

    # Store in memory for active session
    active_sessions[session_id] = {
        "state": state,
        "db_id": db_session.id,  # Store DB ID
        "db_service": db_service
    }

    return {
        "session_id": session_id,
        "question": state['current_question'],
        "question_number": state['question_count'],
        "category": request.category
    }

@router.post("/answer")
async def submit_answer(request: AnswerRequest, db: Session = Depends(get_db)):
    """Submit answer - with database persistence"""

    if request.session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found or expired")

    session = active_sessions[request.session_id]
    state = session['state']
    db_service = DatabaseService(db)

    # Update state with user's answer
    state['user_answer'] = request.answer
    state['messages'].append(Message(role="candidate", content=request.answer))

    # Evaluate using LangGraph
    eval_result = graph.evaluate_node(state)
    state.update(eval_result)

    # Save response to database
    db_service.save_response(
        session_db_id=session['db_id'],
        question_id=state['current_question_id'],
        question_text=state['current_question'],
        question_number=state['question_count'],
        user_answer=request.answer,
        evaluation=state['evaluation'],
        score=state['score'],
        category=state['category']
    )

    # Check if should continue
    should_continue = graph.should_continue(state)

    response = {
        "evaluation": state['evaluation'],
        "score": state['score'],
        "question_number": state['question_count'],
        "continue": should_continue == "continue"
    }

    # Generate follow-up or complete session
    if should_continue == "continue":
        followup_result = graph.followup_node(state)
        state.update(followup_result)
        response.update({
            "next_question": state['current_question'],
            "next_question_id": state['current_question_id']
        })
    else:
        # Complete session in database
        db_service.complete_session(request.session_id, state['messages'])

        # Clean up active session
        del active_sessions[request.session_id]

        response["message"] = "Interview complete!"

    return response

@router.get("/{session_id}/summary")
async def get_summary(session_id: str, db: Session = Depends(get_db)):
    """Get interview summary from database"""

    db_service = DatabaseService(db)
    session = db_service.get_session(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Get all responses
    responses = db_service.get_session_responses(session.id)

    return {
        "session_id": session_id,
        "category": session.category,
        "difficulty": session.difficulty,
        "started_at": session.started_at.isoformat(),
        "completed_at": session.completed_at.isoformat() if session.completed_at else None,
        "total_questions": session.total_questions,
        "average_score": session.average_score,
        "is_completed": session.is_completed,
        "responses": [
            {
                "question_number": r.question_number,
                "question": r.question_text,
                "answer": r.user_answer,
                "score": r.score,
                "evaluation": r.evaluation
            }
            for r in responses
        ],
        "transcript": session.transcript
    }

@router.get("/sessions/recent")
async def get_recent_sessions(limit: int = 10, db: Session = Depends(get_db)):
    """Get recent interview sessions"""

    db_service = DatabaseService(db)
    sessions = db_service.get_recent_sessions(limit=limit)

    return {
        "total": len(sessions),
        "sessions": [
            {
                "session_id": s.session_id,
                "category": s.category,
                "started_at": s.started_at.isoformat(),
                "completed": s.is_completed,
                "average_score": s.average_score,
                "total_questions": s.total_questions
            }
            for s in sessions
        ]
    }
