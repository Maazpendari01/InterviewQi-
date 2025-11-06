from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from ..services.interview_agent import InterviewAgent

router = APIRouter(prefix="/api/interview", tags=["interview"])

# In-memory sessions (will add DB later)
sessions = {}
agent = InterviewAgent()

class StartRequest(BaseModel):
    category: str = "coding"

class AnswerRequest(BaseModel):
    session_id: str
    answer: str

@router.post("/start")
async def start_interview(request: StartRequest):
    """Start new interview"""
    question_data = agent.get_question(request.category)

    session_id = f"session_{len(sessions) + 1}"
    sessions[session_id] = {
        "category": request.category,
        "current_question": question_data,
        "answers": []
    }

    return {
        "session_id": session_id,
        "question": question_data['question'],
        "question_id": question_data['id']
    }

@router.post("/answer")
async def submit_answer(request: AnswerRequest):
    """Submit answer and get evaluation"""
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions[request.session_id]
    current_q = session['current_question']

    # Evaluate
    evaluation = agent.evaluate_answer(
        current_q['question'],
        request.answer,
        current_q['category']
    )

    # Save
    session['answers'].append({
        "question": current_q['question'],
        "answer": request.answer,
        "evaluation": evaluation
    })

    return {
        "evaluation": evaluation,
        "total_answered": len(session['answers'])
    }

@router.get("/{session_id}/summary")
async def get_summary(session_id: str):
    """Get interview summary"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    return sessions[session_id]
