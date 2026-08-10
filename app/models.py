from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AnswerRecord(BaseModel):
    question: str
    answer: str

    score: float = 0.0
    technical_score: float = 0.0
    communication_score: float = 0.0
    problem_solving_score: float = 0.0

    feedback: str = ""

    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)


class InterviewSession(BaseModel):
    session_id: str
    candidate: Dict[str, Any]
    curriculum: Dict[str, Any]

    questions: List[str] = Field(default_factory=list)
    answers: List[AnswerRecord] = Field(default_factory=list)

    current_question: Optional[str] = None
    question_number: int = 0
    max_questions: int = 7

    difficulty: str = "medium"
    completed: bool = False

    final_feedback: Optional[Dict[str, Any]] = None