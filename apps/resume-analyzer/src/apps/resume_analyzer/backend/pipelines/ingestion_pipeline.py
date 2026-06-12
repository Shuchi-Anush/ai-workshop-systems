import time
import uuid
from typing import List
from ai_contracts.interfaces.ingestion import IIngestionService
from ai_contracts.interfaces.parser import IParser
from ai_contracts.interfaces.cleaner import ICleaner
from ai_contracts.interfaces.chunker import ISectionParser, IChunker
from ai_contracts.interfaces.embedder import IEmbedder
from ai_contracts.interfaces.vectordb import IVectorDB
from ai_contracts.interfaces.storage import IMetadataStore
from ai_contracts.schemas.common import ProcessingStatus, ErrorInfo
from apps.resume_analyzer.backend.schemas.ingestion import IngestionRequest, IngestionResult
from ai_vector.schemas.vector import VectorRecord
from shared.pipelines.base import PipelineObservabilityMixin

class IngestionPipeline(IIngestionService, PipelineObservabilityMixin):
    """
    Coordinates the extraction, chunking, and dual-storage of resumes.
    """
    
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
