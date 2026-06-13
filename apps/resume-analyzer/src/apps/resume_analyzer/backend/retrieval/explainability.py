import re
from typing import Any
class ExplainabilityEngine:
    def __init__(self):
        pass

    def explain(self, query_text: str, chunk_content: str, metadata: Any, diagnostics: dict, query_mode: str) -> dict:
        # Extract matched sparse terms (simple overlap)
        query_words = set(re.findall(r'\b\w+\b', query_text.lower()))
        chunk_words = set(re.findall(r'\b\w+\b', chunk_content.lower()))
        matched_sparse = list(query_words.intersection(chunk_words))
        
        # Approximate dense concepts (skills from metadata)
        if isinstance(metadata, dict):
            query_skills = metadata.get("skills", [])
        else:
            query_skills = getattr(metadata, "skills", [])
            
        matched_dense = [s for s in query_skills if s.lower() in query_text.lower()]
        if not matched_dense and len(matched_sparse) > 0:
             matched_dense = ["semantic_embedding_match"]

        rrf_contribution = {}
        if diagnostics.get("dense_rank", -1) != -1:
            rrf_contribution["dense"] = 1.0 / (60 + diagnostics["dense_rank"])
        if diagnostics.get("bm25_rank", -1) != -1:
            rrf_contribution["bm25"] = 1.0 / (60 + diagnostics["bm25_rank"])
            
        retrieval_path = []
        # Check metadata path (basic fallback)
        has_meta = len(query_skills) > 0
        if has_meta:
            retrieval_path.append("metadata")
        if "bm25" in rrf_contribution or query_mode == "sparse":
            retrieval_path.append("bm25")
        if "dense" in rrf_contribution or query_mode == "dense":
            retrieval_path.append("dense")

        return {
            "matched_sparse_terms": matched_sparse,
            "matched_dense_concepts": matched_dense,
            "metadata_matches": query_skills,
            "rrf_contribution": rrf_contribution,
            "adversarial_penalty": diagnostics.get("penalty_multiplier", 1.0),
            "retrieval_path": retrieval_path
        }
