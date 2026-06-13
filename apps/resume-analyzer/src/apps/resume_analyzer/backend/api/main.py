from fastapi import FastAPI
from contextlib import asynccontextmanager
from .routes import router
from apps.resume_analyzer.backend.di.factories import configure_infrastructure

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize infrastructure before serving requests
    configure_infrastructure()
    yield
    # Cleanup logic if needed
    
app = FastAPI(
    title="Resume Analyzer API",
    description="API for processing and ranking resumes",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router, prefix="/api/v1")
