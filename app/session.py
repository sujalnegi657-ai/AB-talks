from typing import Dict, Optional

from .models import InterviewSession


sessions: Dict[str, InterviewSession] = {}


def create_session(session: InterviewSession) -> InterviewSession:
    sessions[session.session_id] = session
    return session


def get_session(session_id: str) -> Optional[InterviewSession]:
    return sessions.get(session_id)


def update_session(session: InterviewSession) -> InterviewSession:
    sessions[session.session_id] = session
    return session


def delete_session(session_id: str) -> bool:
    if session_id in sessions:
        del sessions[session_id]
        return True

    return False