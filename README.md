# InterviewIQ AI - Backend

InterviewIQ AI is an adaptive technical interview platform powered by AI.

The backend is built using FastAPI and provides APIs for:

- Starting an interview
- Generating adaptive questions
- Evaluating candidate answers
- Adjusting interview difficulty
- Generating final structured feedback
- Checking backend health

---

## Tech Stack

- Python
- FastAPI
- OpenAI API
- Pydantic
- Uvicorn

---

## Project Structure

```text
backend/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── interview.py
│   ├── evaluator.py
│   ├── prompts.py
│   ├── models.py
│   ├── schemas.py
│   ├── session.py
│   └── utils.py
│
├── data/
│   ├── curriculum.json
│   └── candidate.json
│
├── requirements.txt
├── .env.example
└── README.md