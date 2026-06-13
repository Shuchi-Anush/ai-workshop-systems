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
    Hybrid Retrieval Engine with RRF and Adversarial Filtering.
    """
    
    def __init__(self, embedder: IEmbedder, vectordb: IVectorDB, metadata_store: IMetadataStore, skill_extractor: 'ISkillExtractor' = None):
        from ai_contracts.interfaces.extraction import ISkillExtractor
        from apps.resume_analyzer.backend.retrieval.bm25 import LocalBM25Retriever
        from apps.resume_analyzer.backend.retrieval.adversarial import AdversarialDetector
        from apps.resume_analyzer.backend.di.container import get_container
        
        self._skill_extractor = skill_extractor
        self._embedder = embedder
        self._vectordb = vectordb
        self._metadata_store = metadata_store
        self._bm25_retriever = get_container().resolve(LocalBM25Retriever)
        
        # Initialize Adversarial Detector
        skill_map = {}
        if hasattr(self._skill_extractor, "skill_map"):
            skill_map = self._skill_extractor.skill_map
        self._adversarial_detector = AdversarialDetector(skill_map)
        
    def retrieve(self, query: RetrievalQuery) -> RetrievalResult:
        start_time = time.time()
        trace_id = query.trace_id or "UNKNOWN_TRACE"
        
        # 0. Extract Skills for Metadata Filtering
        skills = []
        if self._skill_extractor:
            skills = self._trace_execution("extract_skills", trace_id, self._skill_extractor.extract, query.query_text)
            if skills:
                query.filters = query.filters or {}
                if len(skills) == 1:
                    query.filters[f"skill_{skills[0]}"] = True
                elif len(skills) > 1:
                    clauses = [{f"skill_{s}": True} for s in skills]
                    query.filters["$or"] = clauses
                
        # 1. Generate Query Vector & Dense Search
        dense_results = []
        if query.mode in ["hybrid", "dense"]:
            query_vector_obj = self._trace_execution(
                "embed_query", trace_id,
                self._embedder.embed_text, query.query_text
            )
            query_vector = query_vector_obj.vector if query_vector_obj else []
            
            dense_results = self._trace_execution(
                "vector_search", trace_id,
                self._vectordb.search, query_vector, query.top_k * 2, query.filters
            )
        
        # 2. BM25 Search
        bm25_results = []
        if query.mode in ["hybrid", "sparse"]:
            bm25_results = self._trace_execution(
                "bm25_search", trace_id,
                self._bm25_retriever.search, query.query_text, query.top_k * 2
            )
        
        # 3. Reciprocal Rank Fusion (RRF)
        k_rrf = 60
        fused_scores = {}
        diagnostics_map = {}
        
        for rank, res in enumerate(dense_results):
            chunk_id = res.chunk_id
            if chunk_id not in fused_scores:
                fused_scores[chunk_id] = 0.0
                diagnostics_map[chunk_id] = {"dense_rank": -1, "bm25_rank": -1, "dense_score": res.similarity_score, "bm25_score": 0.0}
            
            if query.mode == "dense":
                fused_scores[chunk_id] = float(res.similarity_score) # Just use raw score
            else:
                fused_scores[chunk_id] += 1.0 / (k_rrf + rank + 1)
                
            diagnostics_map[chunk_id]["dense_rank"] = rank + 1
            
        for rank, res in enumerate(bm25_results):
            chunk_id = res["chunk_id"]
            if chunk_id not in fused_scores:
                fused_scores[chunk_id] = 0.0
                diagnostics_map[chunk_id] = {"dense_rank": -1, "bm25_rank": -1, "dense_score": 0.0, "bm25_score": 0.0}
            
            if query.mode == "sparse":
                fused_scores[chunk_id] = float(res["score"]) # Just use raw score
            else:
                fused_scores[chunk_id] += 1.0 / (k_rrf + rank + 1)
                
            diagnostics_map[chunk_id]["bm25_rank"] = rank + 1
            diagnostics_map[chunk_id]["bm25_score"] = res["score"]
            
        # 4. Metadata Rehydration
        chunk_ids = list(fused_scores.keys())
        chunks = self._trace_execution(
            "metadata_rehydration", trace_id,
            self._metadata_store.get_chunks_by_ids, chunk_ids
        )
        
        chunk_map = {c.metadata.chunk_id: c for c in chunks}
        
        # 5. Apply Adversarial Filtering
        final_results = []
        from apps.resume_analyzer.backend.retrieval.explainability import ExplainabilityEngine
        explainer = ExplainabilityEngine()
        
        for chunk_id, rrf_score in fused_scores.items():
            chunk = chunk_map.get(chunk_id)
            if not chunk:
                continue
                
            adv_analysis = self._adversarial_detector.analyze(chunk.content, skills)
            penalty_multiplier = 1.0
            if adv_analysis["adversarial_score"] > 0.6:
                penalty_multiplier = 0.1
            elif adv_analysis["adversarial_score"] > 0.4:
                penalty_multiplier = 0.5
                
            final_score = rrf_score * penalty_multiplier
            
            diag = diagnostics_map[chunk_id]
            diag.update(adv_analysis)
            diag["rrf_score"] = rrf_score
            diag["final_score"] = final_score
            diag["penalty_multiplier"] = penalty_multiplier
            
            # Compute deep explainability
            explain_data = explainer.explain(
                query.query_text, 
                chunk.content, 
                chunk.metadata, 
                diag,
                query.mode
            )
            diag["explainability"] = explain_data
            
            diag["retrieval_sources"] = []
            if diag["dense_rank"] > 0: diag["retrieval_sources"].append("dense")
            if diag["bm25_rank"] > 0: diag["retrieval_sources"].append("bm25")
            
            final_results.append((chunk, final_score, diag))
            
        # Sort and take Top-K
        final_results.sort(key=lambda x: x[1], reverse=True)
        top_results = final_results[:query.top_k]
        
        retrieved_chunks = [
            RetrievedChunk(chunk=c, similarity_score=score, diagnostics=diag)
            for c, score, diag in top_results
        ]
        
        execution_time_ms = (time.time() - start_time) * 1000
        
        return RetrievalResult(
            query=query,
            results=retrieved_chunks,
            execution_time_ms=execution_time_ms
        )

    async def retrieve_async(self, query: RetrievalQuery) -> RetrievalResult:
        return self.retrieve(query)
