import os
from typing import Any, Dict, List

from openai import OpenAI

from .prompts import (
    INTERVIEWER_SYSTEM_PROMPT,
    QUESTION_PROMPT,
)
from .utils import clean_json_response


class Interviewer:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        self.client = None

        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)

    def generate_question(
        self,
        candidate: Dict[str, Any],
        curriculum: Dict[str, Any],
        previous_questions: List[str],
        evaluations: List[Dict[str, Any]],
        difficulty: str,
        question_number: int,
    ) -> Dict[str, Any]:

        # Fallback questions if API key is not configured
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

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": INTERVIEWER_SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
        )

        content = response.choices[0].message.content

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
            skill for skill in skills
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
            "hard": f"Describe a challenging problem involving {skill} and explain how you would solve it.",
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