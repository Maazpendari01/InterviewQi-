from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# Request schemas
class StartInterviewRequest(BaseModel):
    category: str = Field(..., description="Interview category: coding, system_design, behavioral")
    difficulty: str = Field(default="medium", description="Difficulty level")

class SubmitAnswerRequest(BaseModel):
    session_id: str
    answer: str = Field(..., min_length=10, description="User's answer to the question")

# Response schemas
class QuestionResponse(BaseModel):
    session_id: str
    question: str
    question_id: str
    question_number: int
    category: str

class EvaluationResponse(BaseModel):
    evaluation: str
    score: int = Field(..., ge=0, le=100)
    question_number: int
    continue: bool
    next_question: Optional[str] = None
    next_question_id: Optional[str] = None

class SessionSummary(BaseModel):
    session_id: str
    category: str
    total_questions: int
    average_score: Optional[float]
    started_at: datetime
    completed_at: Optional[datetime]
    is_completed: bool

class AnalyticsStats(BaseModel):
    total_sessions: int
    completed_sessions: int
    completion_rate: float
    average_score: float
    by_category: dict
