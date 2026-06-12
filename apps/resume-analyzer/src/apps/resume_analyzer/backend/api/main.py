from fastapi import FastAPI
from .routes import router

app = FastAPI(
    title="Resume Analyzer API",
    description="API for processing and ranking resumes",
    version="1.0.0"
)

app.include_router(router)
