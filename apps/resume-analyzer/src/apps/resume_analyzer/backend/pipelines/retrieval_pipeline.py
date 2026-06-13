import time
from typing import List
from ai_contracts.interfaces.retriever import IRetriever
from ai_contracts.interfaces.embedder import IEmbedder
from ai_contracts.interfaces.vectordb import IVectorDB
from ai_contracts.interfaces.storage import IMetadataStore
from ai_contracts.schemas.retrieval import RetrievalQuery, RetrievedChunk, RetrievalResult
from ai_observability.pipelines.base import PipelineObservabilityMixin

class RetrievalPipeline(IRetriever, PipelineObservabilityMixin):
    """
    Coordinates vector retrieval and metadata rehydration.
    Depends solely on abstract interfaces.
    """
    
    def __init__(self, embedder: IEmbedder, vectordb: IVectorDB, metadata_store: IMetadataStore):
        self._embedder = embedder
        self._vectordb = vectordb
        self._metadata_store = metadata_store
        
    def retrieve(self, query: RetrievalQuery) -> RetrievalResult:
        start_time = time.time()
        trace_id = query.trace_id or "UNKNOWN_TRACE"
        
        # 1. Generate Query Vector
        query_vector_obj = self._trace_execution(
            "embed_query", trace_id,
            self._embedder.embed_text, query.query_text
        )
        query_vector = query_vector_obj.vector if query_vector_obj else []
        
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
