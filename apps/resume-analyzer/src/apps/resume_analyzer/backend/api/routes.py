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

class BulkIngestResult(BaseModel):
    success_count: int
    failure_count: int
    failed_filenames: list[str]
    indexed_candidates: list[str]
    total_chunks: int

@router.post("/bulk-ingest", response_model=BulkIngestResult)
async def bulk_ingest_resumes(
    files: List[UploadFile] = File(...),
    pipeline: IIngestionService = Depends(get_ingestion_pipeline)
):
    import os
    import shutil
    
    upload_dir = "apps/resume-analyzer/data/resumes"
    os.makedirs(upload_dir, exist_ok=True)
    
    success = 0
    failures = 0
    failed_files = []
    indexed = []
    total_chunks = 0
    
    for file in files:
        if not file.filename.endswith(".pdf"):
            failures += 1
            failed_files.append(file.filename)
            continue
            
        candidate_id = file.filename.replace(".pdf", "").replace(" ", "_").lower()
        file_path = os.path.join(upload_dir, file.filename)
        
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
                
            # Re-open for ingestion
            with open(file_path, "rb") as f:
                request = IngestionRequest(
                    candidate_id=candidate_id,
                    file_stream=f,
                    file_name=file.filename,
                    trace_id=f"bulk_{candidate_id}"
                )
                if hasattr(pipeline, "ingest_async"):
                    res = await pipeline.ingest_async(request)
                else:
                    res = pipeline.ingest(request)
                    
                success += 1
                indexed.append(candidate_id)
                total_chunks += res.chunks_indexed
        except Exception as e:
            failures += 1
            failed_files.append(file.filename)
            # Safe boundary
            pass
            
    return BulkIngestResult(
        success_count=success,
        failure_count=failures,
        failed_filenames=failed_files,
        indexed_candidates=indexed,
        total_chunks=total_chunks
    )

class StatsResult(BaseModel):
    total_candidates: int
    total_chunks: int
    
@router.get("/stats", response_model=StatsResult)
async def get_stats():
    from ai_contracts.interfaces.storage import IMetadataStore
    store = get_container().resolve(IMetadataStore)
    return StatsResult(
        total_candidates=len(store.candidates),
        total_chunks=len(store.chunks)
    )

@router.get("/candidates")
async def list_candidates():
    from ai_contracts.interfaces.storage import IMetadataStore
    store = get_container().resolve(IMetadataStore)
    return list(store.candidates.keys())

@router.get("/candidate/{candidate_id}")
async def get_candidate(candidate_id: str):
    from ai_contracts.interfaces.storage import IMetadataStore
    store = get_container().resolve(IMetadataStore)
    candidate = store.get_candidate(candidate_id)
    if not candidate:
        return {"error": "Candidate not found"}
    chunks = store.get_chunks_by_candidate(candidate_id)
    return {
        "candidate": candidate,
        "chunk_count": len(chunks),
        "chunks": chunks
    }

@router.post("/reset-db")
async def reset_db(confirm: bool = False):
    if not confirm:
        return {"error": "Must pass confirm=true to reset database"}
    
    # Reset Metadata
    from ai_contracts.interfaces.storage import IMetadataStore
    store = get_container().resolve(IMetadataStore)
    if hasattr(store, "clear"):
        store.clear()
        
    # Reset VectorDB
    from ai_contracts.interfaces.vectordb import IVectorDB
    vectordb = get_container().resolve(IVectorDB)
    # Chroma requires recreating the collection
    if hasattr(vectordb, "client") and hasattr(vectordb, "collection"):
        try:
            vectordb.client.delete_collection(vectordb.collection.name)
            vectordb.collection = vectordb.client.create_collection(vectordb.collection.name)
        except Exception as e:
            pass
            
    return {"status": "Database reset successful"}

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

