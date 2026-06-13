import chromadb
from typing import List, Dict, Any, Optional
from ai_contracts.interfaces.vectordb import IVectorDB
from ai_vector.schemas.vector import VectorRecord, VectorSearchResult
import os

class ChromaVectorDB(IVectorDB[VectorRecord, VectorSearchResult, List[float]]):
    def __init__(self, persist_directory: str = "./chroma_db", collection_name: str = "resumes"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def upsert(self, records: List[VectorRecord]) -> None:
        ids = []
        embeddings = []
        metadatas = []
        
        for record in records:
            ids.append(record.chunk_id)
            embeddings.append(record.embedding.vector)
            # Serialize metadata (chroma requires flat dict of str/int/float)
            # Build Chroma-compatible flat metadata dictionary
            meta = {"candidate_id": getattr(record, "candidate_id", "unknown")}
            if hasattr(record, "metadata") and record.metadata:
                for k, v in record.metadata.items():
                    if isinstance(v, (str, int, float, bool)):
                        meta[k] = v
            metadatas.append(meta)
            
        if ids:
            self.collection.upsert(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas
            )

    def search(self, query_vector: List[float], top_k: int, filters: Optional[Dict[str, Any]] = None) -> List[VectorSearchResult]:
        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=top_k,
            where=filters
        )
        
        search_results = []
        if results and results['ids'] and len(results['ids']) > 0:
            for i in range(len(results['ids'][0])):
                search_results.append(VectorSearchResult(
                    chunk_id=results['ids'][0][i],
                    similarity_score=1.0 - (results['distances'][0][i] if 'distances' in results and results['distances'] else 0.0),
                    distance=results['distances'][0][i] if 'distances' in results and results['distances'] else 0.0
                ))
                
        return search_results

    def delete(self, chunk_ids: List[str]) -> None:
        self.collection.delete(ids=chunk_ids)
