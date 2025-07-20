from fastapi import APIRouter
from app.models.model_wrapper import QuestionModelWrapper
from pydantic import BaseModel

router = APIRouter()

class QuestionRequest(BaseModel):
    question: str
    file_path: str

@router.post("/question")
async def process_questions(payload: QuestionRequest):
    print(f"Processing question: {payload.question} for file: {payload.file_path}")

    model = QuestionModelWrapper()
    try:
        answer = model.process_pdf(payload.file_path, payload.question)
        print(f"Answer: {answer}")
        return {"question": payload.question, "answer": answer}
    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}