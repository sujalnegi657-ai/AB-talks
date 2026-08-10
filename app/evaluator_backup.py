import os
from typing import Any, Dict, List

from openai import OpenAI

from .prompts import (
    EVALUATION_SYSTEM_PROMPT,
    ANSWER_EVALUATION_PROMPT,
    FINAL_FEEDBACK_PROMPT,
)
from .utils import clean_json_response, average


class Evaluator:

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        self.client = None

        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)

    def evaluate_answer(
        self,
        candidate: Dict[str, Any],
        curriculum: Dict[str, Any],
        question: str,
        answer: str,
    ) -> Dict[str, Any]:

        if not self.client:
            return self._fallback_evaluation(answer)

        prompt = ANSWER_EVALUATION_PROMPT.format(
            candidate=candidate,
            curriculum=curriculum,
            question=question,
            answer=answer,
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": EVALUATION_SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )

        content = response.choices[0].message.content

        if not content:
            raise ValueError("AI did not return an evaluation.")

        return clean_json_response(content)

    def generate_final_feedback(
        self,
        candidate: Dict[str, Any],
        curriculum: Dict[str, Any],
        evaluations: List[Dict[str, Any]],
    ) -> Dict[str, Any]:

        if not evaluations:
            return {
                "overall_score": 0,
                "technical_score": 0,
                "communication_score": 0,
                "problem_solving_score": 0,
                "recommendation": "No Hire",
                "summary": "No interview answers were provided.",
                "strengths": [],
                "weaknesses": [],
                "skill_breakdown": [],
                "learning_plan": [],
            }

        if not self.client:
            return self._fallback_final_feedback(evaluations)

        prompt = FINAL_FEEDBACK_PROMPT.format(
            candidate=candidate,
            curriculum=curriculum,
            evaluations=evaluations,
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": EVALUATION_SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )

        content = response.choices[0].message.content

        if not content:
            raise ValueError("AI did not return final feedback.")

        return clean_json_response(content)

    def _fallback_evaluation(self, answer: str) -> Dict[str, Any]:
        """
        Simple fallback evaluator.
        Used only when OPENAI_API_KEY is not configured.
        """

        word_count = len(answer.split())

        if word_count >= 80:
            score = 85
        elif word_count >= 40:
            score = 70
        elif word_count >= 15:
            score = 55
        else:
            score = 35

        return {
            "score": score,
            "technical_score": score,
            "communication_score": min(score + 5, 100),
            "problem_solving_score": score,
            "feedback": (
                "This is a basic fallback evaluation. "
                "Configure OPENAI_API_KEY for AI-powered evaluation."
            ),
            "strengths": [
                "Candidate attempted the question."
            ],
            "weaknesses": [
                "Detailed AI evaluation is unavailable."
            ],
            "recommended_difficulty": (
                "hard" if score >= 80
                else "medium" if score >= 55
                else "easy"
            ),
        }

    def _fallback_final_feedback(
        self,
        evaluations: List[Dict[str, Any]],
    ) -> Dict[str, Any]:

        overall = average([
            item.get("score", 0)
            for item in evaluations
        ])

        technical = average([
            item.get("technical_score", 0)
            for item in evaluations
        ])

        communication = average([
            item.get("communication_score", 0)
            for item in evaluations
        ])

        problem_solving = average([
            item.get("problem_solving_score", 0)
            for item in evaluations
        ])

        if overall >= 80:
            recommendation = "Strong Hire"
        elif overall >= 65:
            recommendation = "Hire"
        elif overall >= 50:
            recommendation = "Borderline"
        else:
            recommendation = "No Hire"

        strengths = []
        weaknesses = []

        for evaluation in evaluations:
            strengths.extend(
                evaluation.get("strengths", [])
            )
            weaknesses.extend(
                evaluation.get("weaknesses", [])
            )

        return {
            "overall_score": overall,
            "technical_score": technical,
            "communication_score": communication,
            "problem_solving_score": problem_solving,
            "recommendation": recommendation,
            "summary": (
                "Interview completed using the fallback "
                "evaluation system."
            ),
            "strengths": list(dict.fromkeys(strengths))[:5],
            "weaknesses": list(dict.fromkeys(weaknesses))[:5],
            "skill_breakdown": [],
            "learning_plan": [
                {
                    "topic": "Technical fundamentals",
                    "priority": "High",
                    "action": (
                        "Practice the topics covered during "
                        "the interview."
                    ),
                }
            ],
        }