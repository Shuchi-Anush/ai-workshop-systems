import time
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
