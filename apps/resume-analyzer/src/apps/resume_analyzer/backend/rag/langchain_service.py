import os
import requests
from typing import List

class RAGService:
    def __init__(self):
        pass

    def ask_batch(self, query: str, candidate_ids: List[str]) -> str:
        """Query multiple candidates using simple RAG and IRetriever."""
        if not candidate_ids:
            return "Please provide candidate context for me to analyze."

        try:
            from apps.resume_analyzer.backend.api.dependencies import get_container
            from ai_contracts.interfaces.retriever import IRetriever
            from ai_contracts.schemas.retrieval import RetrievalQuery
            
            retriever = get_container().resolve(IRetriever)
            if not retriever:
                return "Retriever not found."

            req = RetrievalQuery(
                query_text=query,
                top_k=20,
                mode="hybrid"
            )
            retrieval_res = retriever.retrieve(req)
            
            docs = []
            for c in retrieval_res.results:
                if isinstance(c.chunk.metadata, dict):
                    cid = c.chunk.metadata.get("candidate_id")
                else:
                    cid = getattr(c.chunk.metadata, "candidate_id", None)
                    
                if cid in candidate_ids:
                    docs.append(c.chunk.text)
                    
            context_text = "\n\n".join(docs)
            
            prompt = f"""You are an expert AI Recruitment Assistant. Use the following candidate resume excerpts to answer the recruiter's question.
If the information is not present in the excerpts, clearly state that you don't know rather than making it up.

Candidate Excerpts:
{context_text}

Recruiter's Question: {query}
Helpful Answer:"""
            
            # Invoke Ollama directly
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "phi3",
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get("response", "No response generated.")
            else:
                return f"Error from Ollama: {response.status_code} {response.text}"
                
        except Exception as e:
            return f"Error during retrieval: {str(e)}"
