import os
from pathlib import Path

base_dir = Path("d:/ai-workshop-systems/shared")
mocks_dir = base_dir / "mocks"
pipelines_dir = base_dir / "pipelines"

pipelines_dir.mkdir(parents=True, exist_ok=True)

files_content = {
    "mocks/mock_embedder.py": """import hashlib
import numpy as np
from typing import List
from shared.interfaces.embedder import IEmbedder
from shared.schemas.domain import DocumentChunk
from shared.schemas.vector import EmbeddingVector

class MockEmbedder(IEmbedder):
    \"\"\"
    Deterministic mock embedder.
    Uses MD5 hashing to generate consistent pseudorandom vectors from text.
    Designed purely for orchestration validation and reproducible tests.
    \"\"\"
    
    def __init__(self, dimensions: int = 384):
        self.dimensions = dimensions
        self.model_name = "mock-hashing-embedder"
        self.model_version = "v1.0.0"
        
    def _text_to_deterministic_vector(self, text: str) -> np.ndarray:
        # Generate a deterministic seed from the text
        seed_bytes = hashlib.md5(text.encode('utf-8')).digest()
        seed = int.from_bytes(seed_bytes[:4], byteorder='little')
        
        # Use the seed to generate a reproducible "random" vector
        rng = np.random.RandomState(seed)
        vec = rng.uniform(-1.0, 1.0, self.dimensions)
        
        # Normalize the vector for cosine similarity
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
            
        return vec

    def embed_text(self, text: str) -> EmbeddingVector:
        vec = self._text_to_deterministic_vector(text)
        return EmbeddingVector(
            vector=vec.tolist(),
            dimensions=self.dimensions,
            model_name=self.model_name,
            model_version=self.model_version
        )
        
    def embed_chunks(self, chunks: List[DocumentChunk]) -> List[EmbeddingVector]:
        return [self.embed_text(chunk.content) for chunk in chunks]
        
    async def embed_chunks_async(self, chunks: List[DocumentChunk]) -> List[EmbeddingVector]:
        # Sync execution wrapper for mock async behavior
        return self.embed_chunks(chunks)
""",

    "pipelines/__init__.py": "",
    "pipelines/base.py": """import time
from typing import Callable, Any, TypeVar

T = TypeVar('T')

class PipelineObservabilityMixin:
    \"\"\"
    Base class providing lightweight observability and tracing hooks.
    \"\"\"
    
    def _trace_execution(self, stage_name: str, trace_id: str, func: Callable[..., T], *args, **kwargs) -> T:
        \"\"\"
        Wraps function execution to log timing and trace propagation.
        In production, this would integrate with OpenTelemetry.
        \"\"\"
        start_time = time.time()
        # Simulated trace start hook
        # print(f"[TRACE:{trace_id}] Starting {stage_name}")
        
        result = func(*args, **kwargs)
        
        end_time = time.time()
        elapsed_ms = (end_time - start_time) * 1000
        # Simulated trace end hook
        # print(f"[TRACE:{trace_id}] Completed {stage_name} in {elapsed_ms:.2f}ms")
        
        return result
""",

    "pipelines/retrieval_pipeline.py": """import time
from typing import List
from shared.interfaces.retriever import IRetriever
from shared.interfaces.embedder import IEmbedder
from shared.interfaces.vectordb import IVectorDB
from shared.interfaces.storage import IMetadataStore
from shared.schemas.retrieval import RetrievalQuery, RetrievedChunk, RetrievalResult
from .base import PipelineObservabilityMixin

class RetrievalPipeline(IRetriever, PipelineObservabilityMixin):
    \"\"\"
    Coordinates vector retrieval and metadata rehydration.
    Depends solely on abstract interfaces.
    \"\"\"
    
    def __init__(self, embedder: IEmbedder, vectordb: IVectorDB, metadata_store: IMetadataStore):
        self._embedder = embedder
        self._vectordb = vectordb
        self._metadata_store = metadata_store
        
    def retrieve(self, query: RetrievalQuery) -> RetrievalResult:
        start_time = time.time()
        trace_id = query.trace_id or "UNKNOWN_TRACE"
        
        # 1. Generate Query Vector
        query_vector = self._trace_execution(
            "embed_query", trace_id,
            self._embedder.embed_text, query.query_text
        )
        
        # 2. Vector DB Search (Returns only IDs and Scores)
        search_results = self._trace_execution(
            "vector_search", trace_id,
            self._vectordb.search, query_vector, query.top_k, query.filters
        )
        
        # 3. Metadata Rehydration
        chunk_ids = [result.chunk_id for result in search_results]
        chunks = self._trace_execution(
            "metadata_rehydration", trace_id,
            self._metadata_store.get_chunks_by_ids, chunk_ids
        )
        
        # Map DB results back to chunks
        chunk_map = {chunk.metadata.chunk_id: chunk for chunk in chunks}
        
        # Build strict output
        retrieved_chunks: List[RetrievedChunk] = []
        for result in search_results:
            chunk = chunk_map.get(result.chunk_id)
            if chunk:
                retrieved_chunks.append(
                    RetrievedChunk(
                        chunk=chunk,
                        similarity_score=result.similarity_score
                    )
                )
                
        execution_time_ms = (time.time() - start_time) * 1000
        
        return RetrievalResult(
            query=query,
            results=retrieved_chunks,
            execution_time_ms=execution_time_ms
        )

    async def retrieve_async(self, query: RetrievalQuery) -> RetrievalResult:
        # In a real implementation, this would yield to the event loop.
        # For the orchestration mock, we wrap the sync call.
        return self.retrieve(query)
""",

    "pipelines/ranking_pipeline.py": """import time
from typing import List, Dict
from shared.interfaces.ranking import ICandidateAggregator, IRanker
from shared.schemas.retrieval import RetrievedChunk
from shared.schemas.ranking import RankedCandidate, RankingResult, CandidateScore, RankingBreakdown
from shared.schemas.domain import Candidate
from shared.interfaces.storage import IMetadataStore
from .base import PipelineObservabilityMixin

class CandidateAggregator(ICandidateAggregator, PipelineObservabilityMixin):
    \"\"\"
    Groups raw chunk hits by candidate, pulling full candidate profiles from the metadata store.
    \"\"\"
    def __init__(self, metadata_store: IMetadataStore):
        self._metadata_store = metadata_store
        
    def aggregate(self, retrieved_chunks: List[RetrievedChunk]) -> List[RankedCandidate]:
        # Group chunks by candidate
        candidate_chunk_map: Dict[str, List[RetrievedChunk]] = {}
        for rc in retrieved_chunks:
            cid = rc.chunk.metadata.candidate_id
            if cid not in candidate_chunk_map:
                candidate_chunk_map[cid] = []
            candidate_chunk_map[cid].append(rc)
            
        aggregated_results = []
        for cid, chunks in candidate_chunk_map.items():
            candidate_profile = self._metadata_store.get_candidate(cid)
            if not candidate_profile:
                # If metadata is missing, we must skip to maintain integrity
                continue
                
            # Create a placeholder score, Ranker will overwrite this
            placeholder_score = CandidateScore(
                final_score=0.0,
                breakdown=RankingBreakdown(base_similarity_score=0.0),
                explainability_log=["Aggregation initialized."]
            )
            
            aggregated_results.append(
                RankedCandidate(
                    candidate=candidate_profile,
                    score=placeholder_score,
                    supporting_chunks=chunks
                )
            )
            
        return aggregated_results

class RankingPipeline(IRanker, PipelineObservabilityMixin):
    \"\"\"
    Applies heuristic scoring rules to aggregated candidates.
    \"\"\"
    
    def rank(self, candidates: List[RankedCandidate], job_description: str) -> RankingResult:
        start_time = time.time()
        
        scored_candidates = []
        
        for rc in candidates:
            # 1. Base Score: Max similarity score among retrieved chunks
            base_sim = max((chunk.similarity_score for chunk in rc.supporting_chunks), default=0.0)
            
            # 2. Section Bonus (Explainability preparation)
            # Heuristic: Chunks from EXPERIENCE sections are weighted heavier
            section_bonus = 0.0
            for chunk in rc.supporting_chunks:
                if chunk.chunk.metadata.section_type.value == "EXPERIENCE":
                    section_bonus += 0.05
                    
            final_score = base_sim + section_bonus
            
            # 3. Create explainability trace
            explain_log = [
                f"Base vector similarity: {base_sim:.3f}",
                f"Section weighting bonus: {section_bonus:.3f}"
            ]
            
            rc.score = CandidateScore(
                final_score=final_score,
                breakdown=RankingBreakdown(
                    base_similarity_score=base_sim,
                    section_weight_bonus=section_bonus
                ),
                explainability_log=explain_log
            )
            scored_candidates.append(rc)
            
        # 4. Sort deterministicly
        scored_candidates.sort(key=lambda x: (-x.score.final_score, x.candidate.candidate_id))
        
        return RankingResult(
            job_description=job_description,
            ranked_candidates=scored_candidates,
            execution_time_ms=(time.time() - start_time) * 1000
        )
""",

    "pipelines/ingestion_pipeline.py": """import time
import uuid
from typing import List
from shared.interfaces.ingestion import IIngestionService
from shared.interfaces.parser import IParser
from shared.interfaces.cleaner import ICleaner
from shared.interfaces.chunker import ISectionParser, IChunker
from shared.interfaces.embedder import IEmbedder
from shared.interfaces.vectordb import IVectorDB
from shared.interfaces.storage import IMetadataStore
from shared.schemas.ingestion import IngestionRequest, IngestionResult, ProcessingStatus, ErrorInfo
from shared.schemas.vector import VectorRecord
from .base import PipelineObservabilityMixin

class IngestionPipeline(IIngestionService, PipelineObservabilityMixin):
    \"\"\"
    Coordinates the extraction, chunking, and dual-storage of resumes.
    \"\"\"
    
    def __init__(self,
                 parser: IParser,
                 cleaner: ICleaner,
                 section_parser: ISectionParser,
                 chunker: IChunker,
                 embedder: IEmbedder,
                 vectordb: IVectorDB,
                 metadata_store: IMetadataStore):
        self._parser = parser
        self._cleaner = cleaner
        self._section_parser = section_parser
        self._chunker = chunker
        self._embedder = embedder
        self._vectordb = vectordb
        self._metadata_store = metadata_store

    def ingest(self, request: IngestionRequest) -> IngestionResult:
        trace_id = request.trace_id or str(uuid.uuid4())
        
        # Note: In a real system we would read the file bytes here.
        # This pipeline assumes the parser takes the path and handles bytes internally for now.
        try:
            # 1. Parse
            parse_res = self._trace_execution("parse", trace_id, self._parser.parse, None, request.file_path)
            if parse_res.status == ProcessingStatus.FAILED or not parse_res.document:
                return IngestionResult(candidate_id=request.candidate_id, document_id="unknown", status=ProcessingStatus.FAILED, error=parse_res.error)
                
            doc = parse_res.document
            doc.candidate_id = request.candidate_id
            
            # 2. Clean
            doc = self._trace_execution("clean", trace_id, self._cleaner.clean, doc)
            
            # 3. Sectioning
            doc = self._trace_execution("section", trace_id, self._section_parser.parse_sections, doc)
            
            # 4. Chunking
            chunks = self._trace_execution("chunk", trace_id, self._chunker.chunk, doc)
            
            # 5. Embedding
            embeddings = self._trace_execution("embed", trace_id, self._embedder.embed_chunks, chunks)
            
            # 6. Storage Dual-Write
            vector_records = []
            for chunk, emb in zip(chunks, embeddings):
                vector_records.append(VectorRecord(chunk_id=chunk.metadata.chunk_id, embedding=emb))
                
            # Write to metadata store first to preserve relational integrity
            self._trace_execution("store_metadata", trace_id, self._metadata_store.save_chunks, chunks)
            
            # Write to vector store
            self._trace_execution("store_vectors", trace_id, self._vectordb.upsert, vector_records)
            
            return IngestionResult(
                candidate_id=request.candidate_id,
                document_id=doc.document_id,
                status=ProcessingStatus.COMPLETED,
                chunks_indexed=len(chunks)
            )
            
        except Exception as e:
            return IngestionResult(
                candidate_id=request.candidate_id,
                document_id="unknown",
                status=ProcessingStatus.FAILED,
                error=ErrorInfo(code="INGEST_ERR", message=str(e))
            )

    async def ingest_async(self, request: IngestionRequest) -> IngestionResult:
        # Simulate async worker offloading
        return self.ingest(request)
"""
}

for path_str, content in files_content.items():
    full_path = base_dir / path_str
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print(f"Successfully generated {len(files_content)} pipeline files.")
