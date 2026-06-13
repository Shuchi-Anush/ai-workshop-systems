from typing import Dict, Any
from apps.resume_analyzer.frontend.services.api_client import APIClient

class RAGService:
    """Handles communication with the backend RAG/AI Assistant APIs."""
    
    @staticmethod
    def ask_assistant(session_id: str, query: str, context_candidates: list[str]) -> str:
        """
        Sends a natural language query to the backend RAG system.
        """
        payload = {
            "session_id": session_id,
            "query": query,
            "candidate_ids": context_candidates
        }
        
        # If the actual backend doesn't support chat natively yet, we safely mock
        # or use evaluate. For this refactor, we attempt a chat endpoint and fallback.
        res = APIClient.post("/api/v1/chat", payload)
        
        if res.get("status") == "error":
            return "I'm currently unable to connect to the AI model. Please check the Technical Insights page to ensure the Ollama daemon is running."
            
        return res.get("response", "The AI could not generate a response.")
