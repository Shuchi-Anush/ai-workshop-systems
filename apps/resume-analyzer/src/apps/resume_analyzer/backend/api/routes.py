from fastapi import APIRouter, Depends, UploadFile, File, Form, BackgroundTasks
from pydantic import BaseModel
from typing import List, Any
from .dependencies import get_ingestion_pipeline, get_ranking_pipeline, get_container
from ai_contracts.interfaces.ingestion import IIngestionService
from ai_contracts.interfaces.ranking import IRanker, ICandidateAggregator
from ai_contracts.interfaces.retriever import IRetriever
from apps.resume_analyzer.backend.schemas.ingestion import IngestionRequest, IngestionResult
from apps.resume_analyzer.backend.schemas.ranking import RankingResult
from ai_contracts.schemas.retrieval import RetrievedChunk, RetrievalQuery

router = APIRouter()

def get_retriever() -> IRetriever:
    return get_container().resolve(IRetriever)
    
def get_aggregator() -> ICandidateAggregator:
    return get_container().resolve(ICandidateAggregator)

@router.get("/health")
async def health_check():
    return {"status": "ok"}

@router.post("/ingest", response_model=IngestionResult)
async def ingest_resume(
    candidate_id: str = Form(...),
    file: UploadFile = File(...),
    trace_id: str = Form(None),
    pipeline: IIngestionService = Depends(get_ingestion_pipeline)
):
    request = IngestionRequest(
        candidate_id=candidate_id,
        file_stream=file.file,
        file_name=file.filename,
        trace_id=trace_id
    )
    if hasattr(pipeline, "ingest_async"):
        return await pipeline.ingest_async(request)
    return pipeline.ingest(request)

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

@router.post("/search", response_model=List[RetrievedChunk])
async def search_candidates(
    request: SearchRequest,
    retriever: IRetriever = Depends(get_retriever)
):
    req = RetrievalQuery(query_text=request.query, top_k=request.top_k)
    res = retriever.retrieve(req)
    return res.results

class EvaluateRequest(BaseModel):
    job_description: str
    top_k: int = 5

@router.post("/evaluate", response_model=RankingResult)
async def evaluate_candidates(
    request: EvaluateRequest,
    retriever: IRetriever = Depends(get_retriever),
    aggregator: ICandidateAggregator = Depends(get_aggregator),
    ranker: IRanker = Depends(get_ranking_pipeline)
):
    # 1. Retrieve
    req = RetrievalQuery(query_text=request.job_description, top_k=request.top_k)
    retrieval_res = retriever.retrieve(req)
    chunks = retrieval_res.results
    
    # 2. Aggregate
    candidates = aggregator.aggregate(chunks)
    
    # 3. Rank
    return ranker.rank(candidates, request.job_description)

