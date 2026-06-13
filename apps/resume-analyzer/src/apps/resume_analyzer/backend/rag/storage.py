import json
import os
import logging
from typing import List, Dict, Any, Optional
from ai_contracts.interfaces.storage import IMetadataStore
from ai_contracts.schemas.chunk import DocumentChunk
from apps.resume_analyzer.backend.schemas.ingestion import IngestionResult

logger = logging.getLogger(__name__)

class LocalJSONMetadataStore(IMetadataStore):
    """
    Workshop-safe metadata persistence using local JSON.
    Provides atomic writes and graceful corruption recovery.
    """
    def __init__(self, file_path: str = "data/metadata/metadata.json"):
        self.file_path = file_path
        self.chunks: Dict[str, DocumentChunk] = {}
        self.candidates: Dict[str, Any] = {}
        self._load()

    def _load(self):
        if not os.path.exists(self.file_path):
            return
            
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            # Rehydrate chunks back into objects
            raw_chunks = data.get("chunks", {})
            for cid, raw_chunk in raw_chunks.items():
                try:
                    self.chunks[cid] = DocumentChunk.model_validate(raw_chunk)
                except Exception as e:
                    logger.warning(f"Failed to rehydrate chunk {cid}: {e}")
                    
            self.candidates = data.get("candidates", {})
            
        except json.JSONDecodeError as e:
            logger.warning(f"Metadata JSON corrupted, starting fresh. Error: {e}")
            self._save() # Overwrite corrupted with empty state
        except Exception as e:
            logger.error(f"Failed to load metadata: {e}")

    def _save(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        # Atomic write with unique temp file
        import uuid
        temp_path = f"{self.file_path}.{uuid.uuid4().hex}.tmp"
        try:
            data = {
                "chunks": {k: v.model_dump(mode="json") if hasattr(v, "model_dump") else v for k, v in self.chunks.items()},
                "candidates": self.candidates
            }
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)
            os.replace(temp_path, self.file_path)
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def save_candidate(self, candidate: Any) -> None:
        if isinstance(candidate, dict):
            candidate_data = candidate.copy()
            candidate_id = candidate_data.get("candidate_id", "unknown")
        elif hasattr(candidate, "model_dump"):
            candidate_data = candidate.model_dump()
            candidate_id = getattr(candidate, "candidate_id", "unknown")
        elif hasattr(candidate, "__dict__"):
            candidate_data = vars(candidate).copy()
            candidate_id = getattr(candidate, "candidate_id", "unknown")
        else:
            candidate_id = getattr(candidate, "candidate_id", str(candidate))
            candidate_data = {"id": candidate_id}
            
        # Strip out file_stream to avoid JSON serialization errors
        if "file_stream" in candidate_data:
            del candidate_data["file_stream"]
            
        self.candidates[candidate_id] = candidate_data
        self._save()

    def get_candidate(self, candidate_id: str) -> Optional[Any]:
        return self.candidates.get(candidate_id)

    def save_chunks(self, chunks: List[DocumentChunk]) -> None:
        for chunk in chunks:
            self.chunks[chunk.metadata.chunk_id] = chunk
        self._save()

    def get_chunks_by_ids(self, chunk_ids: List[str]) -> List[DocumentChunk]:
        return [self.chunks[cid] for cid in chunk_ids if cid in self.chunks]

    def get_chunks_by_candidate(self, candidate_id: str) -> List[DocumentChunk]:
        return [c for c in self.chunks.values() if c.metadata.candidate_id == candidate_id]

    def clear(self) -> None:
        self.chunks = {}
        self.candidates = {}
        self._save()
