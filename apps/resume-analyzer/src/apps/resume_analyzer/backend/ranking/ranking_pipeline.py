from typing import List
import time
from ai_contracts.interfaces.ranking import IRanker, ICandidateAggregator
from ai_contracts.schemas.retrieval import RetrievedChunk
from apps.resume_analyzer.backend.schemas.ranking import RankedCandidate, RankingResult, CandidateScore, RankingBreakdown
from apps.resume_analyzer.backend.schemas.domain import Candidate
from ai_contracts.schemas.common import BaseMetadata
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

class SimpleCandidateAggregator(ICandidateAggregator[RetrievedChunk, RankedCandidate]):
    def aggregate(self, retrieved_chunks: List[RetrievedChunk]) -> List[RankedCandidate]:
        candidates_map = {}
        for rc in retrieved_chunks:
            candidate_id = "unknown"
            if rc.chunk and rc.chunk.metadata:
                candidate_id = rc.chunk.metadata.candidate_id
                
            if candidate_id not in candidates_map:
                cand = Candidate(candidate_id=candidate_id, metadata=BaseMetadata())
                candidates_map[candidate_id] = RankedCandidate(
                    candidate=cand,
                    score=CandidateScore(
                        final_score=rc.similarity_score,
                        breakdown=RankingBreakdown(base_similarity_score=rc.similarity_score),
                        explainability_log=[]
                    ),
                    supporting_chunks=[]
                )
            candidates_map[candidate_id].supporting_chunks.append(rc)
            
        return list(candidates_map.values())

class LLMRanker(IRanker[RankedCandidate, RankingResult]):
    def __init__(self, model: str = "phi3:mini"):
        self.llm = ChatOllama(model=model, temperature=0.1)

    def rank(self, candidates: List[RankedCandidate], job_description: str) -> RankingResult:
        start_time = time.time()
        sorted_candidates = sorted(candidates, key=lambda c: c.score.final_score, reverse=True)
        
        if sorted_candidates:
            top_c = sorted_candidates[0]
            context = "\n".join([rc.chunk.content for rc in top_c.supporting_chunks if rc.chunk])
            prompt = f"Given the job description: {job_description}\nAnd the resume chunks: {context}\nWhy is this candidate a good fit in 2 sentences?"
            
            try:
                response = self.llm.invoke([HumanMessage(content=prompt)])
                top_c.score.explainability_log.append(f"LLM Eval: {response.content}")
            except Exception as e:
                top_c.score.explainability_log.append(f"LLM Error: {str(e)}")
                
        return RankingResult(
            job_description=job_description,
            ranked_candidates=sorted_candidates,
            execution_time_ms=(time.time() - start_time) * 1000
        )
