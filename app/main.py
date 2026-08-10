import os
import uuid

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

from .interview import Interviewer
from .evaluator import Evaluator
from .models import InterviewSession, AnswerRecord
from .schemas import (
    StartInterviewRequest,
    StartInterviewResponse,
    AnswerRequest,
    AnswerResponse,
    FeedbackResponse,
)
from .session import (
    create_session,
    get_session,
    update_session,
)

load_dotenv()

app = FastAPI(
    title="AI Technical Interviewer",
    description="AI-powered technical interview and candidate evaluation system",
    version="1.0.0",
)

interviewer = Interviewer()
evaluator = Evaluator()


@app.get("/")
def root():
    return {
        "message": "AI Technical Interviewer API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post(
    "/interview/start",
    response_model=StartInterviewResponse,
)
def start_interview(
    request: StartInterviewRequest,
):
    session_id = str(uuid.uuid4())

    session = InterviewSession(
        session_id=session_id,
        candidate=request.candidate,
        curriculum=request.curriculum,
        max_questions=request.max_questions,
        difficulty="medium",
    )

    question_data = interviewer.generate_question(
        candidate=session.candidate,
        curriculum=session.curriculum,
        previous_questions=[],
        evaluations=[],
        difficulty=session.difficulty,
        question_number=1,
    )

    question = question_data.get("question")

    if not question:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate interview question.",
        )

    session.questions.append(question)
    session.current_question = question
    session.question_number = 1

    create_session(session)

    return StartInterviewResponse(
        session_id=session_id,
        question=question,
        question_number=1,
        total_questions=session.max_questions,
        difficulty=session.difficulty,
    )


@app.post(
    "/interview/answer",
    response_model=AnswerResponse,
)
def submit_answer(
    request: AnswerRequest,
):
    session = get_session(request.session_id)

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Interview session not found.",
        )

    if session.completed:
        raise HTTPException(
            status_code=400,
            detail="Interview is already completed.",
        )

    if not session.current_question:
        raise HTTPException(
            status_code=400,
            detail="No active question found.",
        )

    evaluation = evaluator.evaluate_answer(
        candidate=session.candidate,
        curriculum=session.curriculum,
        question=session.current_question,
        answer=request.answer,
    )

    answer_record = AnswerRecord(
        question=session.current_question,
        answer=request.answer,
        score=evaluation.get("score", 0),
        technical_score=evaluation.get(
            "technical_score",
            0,
        ),
        communication_score=evaluation.get(
            "communication_score",
            0,
        ),
        problem_solving_score=evaluation.get(
            "problem_solving_score",
            0,
        ),
        feedback=evaluation.get(
            "feedback",
            "",
        ),
        strengths=evaluation.get(
            "strengths",
            [],
        ),
        weaknesses=evaluation.get(
            "weaknesses",
            [],
        ),
    )

    session.answers.append(answer_record)

    if session.question_number >= session.max_questions:
        final_feedback = evaluator.generate_final_feedback(
            candidate=session.candidate,
            curriculum=session.curriculum,
            evaluations=[
                answer.model_dump()
                for answer in session.answers
            ],
        )

        session.final_feedback = final_feedback
        session.completed = True
        session.current_question = None

        update_session(session)

        return AnswerResponse(
            session_id=session.session_id,
            completed=True,
            total_questions=session.max_questions,
            evaluation=evaluation,
            feedback=final_feedback,
        )

    recommended_difficulty = evaluation.get(
        "recommended_difficulty",
        session.difficulty,
    )

    if recommended_difficulty not in {
        "easy",
        "medium",
        "hard",
    }:
        recommended_difficulty = "medium"

    session.difficulty = recommended_difficulty

    next_question_number = session.question_number + 1

    evaluations = [
        answer.model_dump()
        for answer in session.answers
    ]

    question_data = interviewer.generate_question(
        candidate=session.candidate,
        curriculum=session.curriculum,
        previous_questions=session.questions,
        evaluations=evaluations,
        difficulty=session.difficulty,
        question_number=next_question_number,
    )

    next_question = question_data.get("question")

    if not next_question:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate next interview question.",
        )

    session.questions.append(next_question)
    session.current_question = next_question
    session.question_number = next_question_number

    update_session(session)

    return AnswerResponse(
        session_id=session.session_id,
        completed=False,
        question=next_question,
        question_number=next_question_number,
        total_questions=session.max_questions,
        difficulty=session.difficulty,
        evaluation=evaluation,
    )


@app.get(
    "/interview/{session_id}/feedback",
    response_model=FeedbackResponse,
)
def get_feedback(session_id: str):
    session = get_session(session_id)

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Interview session not found.",
        )

    if not session.completed:
        raise HTTPException(
            status_code=400,
            detail="Interview is not completed yet.",
        )

    return FeedbackResponse(
        session_id=session.session_id,
        feedback=session.final_feedback or {},
    )