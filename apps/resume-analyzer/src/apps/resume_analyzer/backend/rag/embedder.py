from typing import List
from ai_contracts.interfaces.embedder import IEmbedder
from ai_contracts.schemas.chunk import DocumentChunk
from ai_vector.schemas.vector import EmbeddingVector
from langchain_ollama import OllamaEmbeddings

class OllamaLocalEmbedder(IEmbedder[EmbeddingVector]):
    def __init__(self, model: str = "nomic-embed-text"):
        self.model_name = model
        self.embeddings = OllamaEmbeddings(model=model)

    def embed_text(self, text: str) -> EmbeddingVector:
        vec = self.embeddings.embed_query(text)
        return EmbeddingVector(vector=vec, dimensions=len(vec), model_name=self.model_name, model_version="1.0")

    def embed_chunks(self, chunks: List[DocumentChunk]) -> List[EmbeddingVector]:
        texts = [chunk.content for chunk in chunks]
        vecs = self.embeddings.embed_documents(texts)
        return [EmbeddingVector(vector=v, dimensions=len(v), model_name=self.model_name, model_version="1.0") for v in vecs]
        
    async def embed_chunks_async(self, chunks: List[DocumentChunk]) -> List[EmbeddingVector]:
        # Awaitable version if supported, fallback to sync
        return self.embed_chunks(chunks)
