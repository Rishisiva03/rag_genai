from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import upload_file, process_questions

app = FastAPI()

app.include_router(upload_file.router, tags=["upload"])
app.include_router(process_questions.router, tags=["questions"])
