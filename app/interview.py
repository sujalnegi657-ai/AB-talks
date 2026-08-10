import os
from typing import Any, Dict, List

from google import genai

from .prompts import (
    INTERVIEWER_SYSTEM_PROMPT,
    QUESTION_PROMPT,
)
from .utils import clean_json_response


class Interviewer:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY", "")
        self.model = os.getenv("GOOGLE_MODEL", "gemini-2.5-flash")

        self.client = None

        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)

    def generate_question(
        self,
        candidate: Dict[str, Any],
        curriculum: Dict[str, Any],
        previous_questions: List[str],
        evaluations: List[Dict[str, Any]],
        difficulty: str,
        question_number: int,
    ) -> Dict[str, Any]:

        # Fallback if API key is not configured
        if not self.client:
            return self._fallback_question(
                curriculum,
                previous_questions,
                difficulty,
            )

        prompt = QUESTION_PROMPT.format(
            candidate=candidate,
            curriculum=curriculum,
            previous_questions=previous_questions,
            evaluations=evaluations,
            difficulty=difficulty,
            question_number=question_number,
        )

        full_prompt = f"""
{INTERVIEWER_SYSTEM_PROMPT}

{prompt}

Return ONLY valid JSON.
Do not use markdown code fences.
"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=full_prompt,
        )

        content = response.text

        if not content:
            raise ValueError("AI did not return a question.")

        return clean_json_response(content)

    def _fallback_question(
        self,
        curriculum: Dict[str, Any],
        previous_questions: List[str],
        difficulty: str,
    ) -> Dict[str, Any]:

        skills = curriculum.get("skills", [])

        if not skills:
            skills = [
                "Data Structures",
                "Algorithms",
                "Programming",
            ]

        available_skills = [
            skill
            for skill in skills
            if skill not in " ".join(previous_questions)
        ]

        skill = (
            available_skills[0]
            if available_skills
            else skills[len(previous_questions) % len(skills)]
        )

        questions = {
            "easy": f"What are the basic concepts of {skill}?",
            "medium": f"Explain how you would use {skill} in a real-world project.",
            "hard": (
                f"Describe a challenging problem involving {skill} "
                f"and explain how you would solve it."
            ),
        }

        return {
            "question": questions.get(
                difficulty,
                questions["medium"],
            ),
            "difficulty": difficulty,
            "skill": skill,
            "reason": "Selected based on the curriculum.",
        }