from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict
from ..services.interview_graph import InterviewGraph
from ..services.interview_state import InterviewState, Message

router = APIRouter(prefix="/api/interview", tags=["interview"])

sessions: Dict[str, dict] = {}
graph = InterviewGraph()

class StartRequest(BaseModel):
    category: str = "coding"

class AnswerRequest(BaseModel):
    session_id: str
    answer: str

@router.post("/start")
async def start_interview(request: StartRequest):
    """Start interview with LangGraph"""
    session_id = f"session_{len(sessions) + 1}"

    # Initialize state
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

    # Run start node
    result = graph.start_node(state)
    state.update(result)

    sessions[session_id] = {"state": state}

    return {
        "session_id": session_id,
        "question": state['current_question'],
        "question_number": state['question_count']
    }

@router.post("/answer")
async def submit_answer(request: AnswerRequest):
    """Submit answer"""
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Not found")

    state = sessions[request.session_id]['state']

    # Update with answer
    state['user_answer'] = request.answer
    state['messages'].append(Message(role="candidate", content=request.answer))

    # Evaluate
    eval_result = graph.evaluate_node(state)
    state.update(eval_result)

    # Check continue
    should_continue = graph.should_continue(state)

    response = {
        "evaluation": state['evaluation'],
        "score": state['score'],
        "continue": should_continue == "continue"
    }

    # Generate follow-up if continuing
    if should_continue == "continue":
        followup = graph.followup_node(state)
        state.update(followup)
        response["next_question"] = state['current_question']

    return response

@router.get("/{session_id}/transcript")
async def get_transcript(session_id: str):
    """Get conversation"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Not found")

    state = sessions[session_id]['state']

    return {
        "messages": state['messages'],
        "total_questions": state['question_count'],
        "final_score": state['score']
    }
