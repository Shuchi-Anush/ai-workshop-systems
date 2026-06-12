import time
from typing import List, Dict
from ai_contracts.interfaces.ranking import ICandidateAggregator, IRanker
from shared.schemas.retrieval import RetrievedChunk
from apps.resume_analyzer.backend.schemas.ranking import RankedCandidate, RankingResult, CandidateScore, RankingBreakdown
from apps.resume_analyzer.backend.schemas.domain import Candidate
from ai_contracts.interfaces.storage import IMetadataStore
from shared.pipelines.base import PipelineObservabilityMixin

class CandidateAggregator(ICandidateAggregator, PipelineObservabilityMixin):
    """
    Groups raw chunk hits by candidate, pulling full candidate profiles from the metadata store.
    """
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
    """
    Applies heuristic scoring rules to aggregated candidates.
    """
    
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
