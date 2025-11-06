from typing import TypedDict, List

class Message(TypedDict):
    role: str  # "interviewer" or "candidate"
    content: str

class InterviewState(TypedDict):
    messages: List[Message]
    category: str
    question_count: int
    current_question: str
    current_question_id: str
    user_answer: str
    evaluation: str
    score: int
