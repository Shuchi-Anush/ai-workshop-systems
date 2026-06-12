from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Any
from .dependencies import get_ingestion_pipeline, get_ranking_pipeline
from ai_contracts.interfaces.ingestion import IIngestionService
from ai_contracts.interfaces.ranking import IRanker
from apps.resume_analyzer.backend.schemas.ingestion import IngestionRequest, IngestionResult
from apps.resume_analyzer.backend.schemas.ranking import RankingResult
from ai_contracts.schemas.retrieval import RetrievedChunk

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "ok"}

@router.post("/ingest", response_model=IngestionResult)
async def ingest_resume(
    request: IngestionRequest,
    pipeline: IIngestionService = Depends(get_ingestion_pipeline)
):
    # Depending on pipeline implementation, it may be sync or async
    if hasattr(pipeline, "ingest_async"):
        return await pipeline.ingest_async(request)
    return pipeline.ingest(request)

class RankRequest(BaseModel):
    chunks: List[RetrievedChunk]
    job_description: str

@router.post("/rank", response_model=RankingResult)
async def rank_candidates(
    request: RankRequest,
    pipeline: IRanker = Depends(get_ranking_pipeline)
):
    if hasattr(pipeline, "rank_async"):
        return await pipeline.rank_async(request.chunks, request.job_description)
    return pipeline.rank(request.chunks, request.job_description)
