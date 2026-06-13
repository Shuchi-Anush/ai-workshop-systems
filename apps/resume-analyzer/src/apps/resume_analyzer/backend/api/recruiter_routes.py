import os
import shutil
import uuid
import json
import csv
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, BackgroundTasks
from pydantic import BaseModel
from pathlib import Path
import time
from apps.resume_analyzer.backend.api.dependencies import get_ingestion_pipeline, get_ranking_pipeline, get_container
from ai_contracts.interfaces.ingestion import IIngestionService
from apps.resume_analyzer.backend.schemas.ingestion import IngestionRequest

recruiter_router = APIRouter()

SESSIONS_DIR = Path("apps/resume-analyzer/.data/backend_sessions")
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

class SessionCreateResponse(BaseModel):
    session_id: str
    message: str

@recruiter_router.post("/sessions/create", response_model=SessionCreateResponse)
async def create_session():
    session_id = f"sess_{uuid.uuid4().hex[:8]}"
    session_data = {
        "session_id": session_id,
        "job_description": "",
        "resumes": [],
        "shortlisted": [],
        "created_at": time.time()
    }
    
    with open(SESSIONS_DIR / f"{session_id}.json", "w") as f:
        json.dump(session_data, f)
        
    return SessionCreateResponse(session_id=session_id, message="Session created successfully")

@recruiter_router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    file_path = SESSIONS_DIR / f"{session_id}.json"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Session not found")
        
    with open(file_path, "r") as f:
        return json.load(f)

@recruiter_router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    file_path = SESSIONS_DIR / f"{session_id}.json"
    if file_path.exists():
        file_path.unlink()
    return {"message": "Session deleted"}

class UploadResponse(BaseModel):
    session_id: str
    uploaded_files: List[str]
    ingested_candidates: List[str]

@recruiter_router.post("/upload-resumes", response_model=UploadResponse)
async def upload_resumes(
    session_id: str = Form(...),
    files: List[UploadFile] = File(...),
    pipeline: IIngestionService = Depends(get_ingestion_pipeline)
):
    session_file = SESSIONS_DIR / f"{session_id}.json"
    if not session_file.exists():
        raise HTTPException(status_code=404, detail="Session not found")
        
    upload_dir = Path(f"apps/resume-analyzer/.data/uploads/{session_id}")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    with open(session_file, "r") as f:
        session_data = json.load(f)
        
    uploaded_names = []
    ingested = []
    
    for file in files:
        if not file.filename.endswith((".pdf", ".docx", ".txt")):
            continue
            
        file_path = upload_dir / file.filename
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
                
            candidate_id = f"{session_id}_{file.filename.split('.')[0].replace(' ', '_').lower()}"
            
            # Re-open for ingestion
            with open(file_path, "rb") as f:
                request = IngestionRequest(
                    candidate_id=candidate_id,
                    file_stream=f,
                    file_name=file.filename,
                    trace_id=session_id
                )
                if hasattr(pipeline, "ingest_async"):
                    res = await pipeline.ingest_async(request)
                else:
                    res = pipeline.ingest(request)
                    
            uploaded_names.append(file.filename)
            ingested.append(candidate_id)
            session_data["resumes"].append({"filename": file.filename, "candidate_id": candidate_id})
        except Exception as e:
            print(f"Error ingesting {file.filename}: {e}")
            pass
            
    # Rebuild BM25 globally after new ingestion
    try:
        from ai_contracts.interfaces.storage import IMetadataStore
        store = get_container().resolve(IMetadataStore)
        from apps.resume_analyzer.backend.retrieval.bm25 import LocalBM25Retriever
        bm25_retriever = get_container().resolve(LocalBM25Retriever)
        if bm25_retriever:
            bm25_retriever.rebuild_from_store(store)
    except Exception as e:
        pass
        
    with open(session_file, "w") as f:
        json.dump(session_data, f)
        
    return UploadResponse(
        session_id=session_id,
        uploaded_files=uploaded_names,
        ingested_candidates=ingested
    )

class EvaluateRequest(BaseModel):
    job_description: str
    top_k: int = 5

@recruiter_router.post("/sessions/{session_id}/evaluate")
async def evaluate_session(session_id: str, request: EvaluateRequest):
    session_file = SESSIONS_DIR / f"{session_id}.json"
    if not session_file.exists():
        raise HTTPException(status_code=404, detail="Session not found")
        
    with open(session_file, "r") as f:
        session_data = json.load(f)
        
    session_data["job_description"] = request.job_description
    
    # Run the existing retrieval but pre-filter by the session's candidate_ids
    candidate_ids = [r["candidate_id"] for r in session_data.get("resumes", [])]
    
    from ai_contracts.interfaces.retriever import IRetriever
    from ai_contracts.interfaces.ranking import ICandidateAggregator
    from ai_contracts.schemas.retrieval import RetrievalQuery
    
    retriever = get_container().resolve(IRetriever)
    aggregator = get_container().resolve(ICandidateAggregator)
    
    # Hybrid retrieval
    req = RetrievalQuery(
        query_text=request.job_description,
        top_k=request.top_k * 3, # over-fetch before filtering
        mode="hybrid"
    )
    retrieval_res = retriever.retrieve(req)
    
    # Filter chunks to only those belonging to this session's candidates
    valid_chunks = []
    for c in retrieval_res.results:
        if isinstance(c.chunk.metadata, dict):
            cid = c.chunk.metadata.get("candidate_id")
        else:
            cid = getattr(c.chunk.metadata, "candidate_id", None)
            
        if cid in candidate_ids:
            valid_chunks.append(c)
    
    # Aggregate
    candidates = aggregator.aggregate(valid_chunks)
    candidates = candidates[:request.top_k]
    
    candidate_list = []
    for c in candidates:
        candidate_dict = {"candidate": c.candidate, "score": c.score, "chunks": c.supporting_chunks}
        if c.supporting_chunks and hasattr(c.supporting_chunks[0], "diagnostics"):
            candidate_dict["diagnostics"] = c.supporting_chunks[0].diagnostics
        candidate_list.append(candidate_dict)
        
    session_data["last_evaluation"] = candidate_list
    with open(session_file, "w") as f:
        json.dump(session_data, f)
        
    return {
        "session_id": session_id,
        "job_description": request.job_description,
        "candidates": candidate_list
    }

@recruiter_router.post("/sessions/{session_id}/shortlist/{candidate_id}")
async def toggle_shortlist(session_id: str, candidate_id: str):
    session_file = SESSIONS_DIR / f"{session_id}.json"
    if not session_file.exists():
        raise HTTPException(status_code=404, detail="Session not found")
        
    with open(session_file, "r") as f:
        session_data = json.load(f)
        
    if candidate_id in session_data["shortlisted"]:
        session_data["shortlisted"].remove(candidate_id)
        action = "removed"
    else:
        session_data["shortlisted"].append(candidate_id)
        action = "added"
        
    with open(session_file, "w") as f:
        json.dump(session_data, f)
        
    return {"status": "success", "action": action, "shortlisted": session_data["shortlisted"]}

@recruiter_router.get("/sessions/{session_id}/shortlist")
async def get_shortlist(session_id: str):
    session_file = SESSIONS_DIR / f"{session_id}.json"
    if not session_file.exists():
        raise HTTPException(status_code=404, detail="Session not found")
        
    with open(session_file, "r") as f:
        return {"shortlisted": json.load(f).get("shortlisted", [])}

from fastapi.responses import PlainTextResponse

@recruiter_router.get("/sessions/{session_id}/export")
async def export_shortlist(session_id: str):
    session_file = SESSIONS_DIR / f"{session_id}.json"
    if not session_file.exists():
        raise HTTPException(status_code=404, detail="Session not found")
        
    with open(session_file, "r") as f:
        session_data = json.load(f)
        
    shortlisted = session_data.get("shortlisted", [])
    eval_candidates = session_data.get("last_evaluation", [])
    
    # Build CSV
    import io
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Candidate ID", "Name", "Experience", "Education"])
    
    for ec in eval_candidates:
        cand = ec.get("candidate", {})
        cid = cand.get("candidate_id")
        if cid in shortlisted:
            writer.writerow([
                cid,
                cand.get("name", ""),
                cand.get("experience", "").replace("\n", " "),
                cand.get("education", "").replace("\n", " ")
            ])
            
    return PlainTextResponse(output.getvalue(), media_type="text/csv")

class ChatRequest(BaseModel):
    query: str
    candidate_ids: List[str]

@recruiter_router.post("/chat")
async def chat_with_assistant(request: ChatRequest):
    from apps.resume_analyzer.backend.rag.langchain_service import RAGService
    try:
        service = RAGService()
        response_text = service.ask_batch(request.query, request.candidate_ids)
        return {"status": "ok", "response": response_text}
    except Exception as e:
        print(f"RAG Error: {e}")
        raise HTTPException(status_code=500, detail="Error communicating with LangChain assistant.")
