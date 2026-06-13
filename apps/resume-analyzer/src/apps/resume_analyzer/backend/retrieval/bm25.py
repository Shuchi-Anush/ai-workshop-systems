import os
import pickle
import re
from typing import List, Dict, Any, Optional
from rank_bm25 import BM25Okapi
from ai_contracts.schemas.retrieval import RetrievedChunk

class LocalBM25Retriever:
    """
    Local BM25 Sparse Retriever using rank_bm25.
    Persists index to disk.
    """
    def __init__(self, index_dir: str = ".data/bm25/"):
        self.index_dir = index_dir
        self.index_file = os.path.join(index_dir, "bm25_index.pkl")
        self.chunk_ids_file = os.path.join(index_dir, "chunk_ids.pkl")
        self.bm25: Optional[BM25Okapi] = None
        self.chunk_ids: List[str] = []
        os.makedirs(self.index_dir, exist_ok=True)
        self.load()

    def _tokenize(self, text: str) -> List[str]:
        # Simple tokenization: lowercase, keep alphanumeric, remove short words
        text = text.lower()
        tokens = re.findall(r'\b[a-z0-9#\+\-]{2,}\b', text)
        return tokens

    def rebuild_from_store(self, store: Any):
        """
        Rebuilds the entire BM25 index from all chunks in the metadata store.
        """
        all_chunks = list(store.chunks.values())
        if all_chunks:
            self.add_documents(all_chunks)

    def add_documents(self, chunks: List[Any]):
        """
        Rebuilds the entire BM25 index from the given chunks.
        chunks: List of DocumentChunk schema.
        """
        self.chunk_ids = [c.chunk_id for c in chunks]
        tokenized_corpus = [self._tokenize(c.text) for c in chunks]
        self.bm25 = BM25Okapi(tokenized_corpus)
        self.save()

    def search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Returns a list of dicts with chunk_id and score.
        """
        if not self.bm25 or not self.chunk_ids:
            return []
            
        tokenized_query = self._tokenize(query)
        doc_scores = self.bm25.get_scores(tokenized_query)
        
        # Sort by score descending
        results = []
        for idx, score in enumerate(doc_scores):
            if score > 0:
                results.append({
                    "chunk_id": self.chunk_ids[idx],
                    "score": float(score)
                })
        
        # Sort and take top_k
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def save(self):
        if self.bm25:
            with open(self.index_file, "wb") as f:
                pickle.dump(self.bm25, f)
            with open(self.chunk_ids_file, "wb") as f:
                pickle.dump(self.chunk_ids, f)

    def load(self):
        if os.path.exists(self.index_file) and os.path.exists(self.chunk_ids_file):
            with open(self.index_file, "rb") as f:
                self.bm25 = pickle.load(f)
            with open(self.chunk_ids_file, "rb") as f:
                self.chunk_ids = pickle.load(f)
