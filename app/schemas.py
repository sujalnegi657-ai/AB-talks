from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class StartInterviewRequest(BaseModel):
    candidate: Dict[str, Any]
    curriculum: Dict[str, Any]
    max_questions: int = Field(default=7, ge=3, le=15)


class StartInterviewResponse(BaseModel):
    session_id: str
    question: str
    question_number: int
    total_questions: int
    difficulty: str


class AnswerRequest(BaseModel):
    session_id: str
    answer: str = Field(min_length=1)


class AnswerResponse(BaseModel):
    session_id: str
    completed: bool
    question: Optional[str] = None
    question_number: Optional[int] = None
    total_questions: int
    difficulty: Optional[str] = None
    evaluation: Optional[Dict[str, Any]] = None
    feedback: Optional[Dict[str, Any]] = None


class FeedbackResponse(BaseModel):
    session_id: str
    feedback: Dict[str, Any]