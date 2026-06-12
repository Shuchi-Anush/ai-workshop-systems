import os
from pathlib import Path

base_dir = Path("d:/ai-workshop-systems/shared")
schemas_dir = base_dir / "schemas"
interfaces_dir = base_dir / "interfaces"

schemas_dir.mkdir(parents=True, exist_ok=True)
interfaces_dir.mkdir(parents=True, exist_ok=True)

files_content = {
    "schemas/__init__.py": "",
    "schemas/common.py": """from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class ProcessingStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class ErrorInfo(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None

class TimestampMixin(BaseModel):
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class BaseMetadata(TimestampMixin):
    version: str = "1.0.0"
    trace_id: Optional[str] = None
""",

    "schemas/domain.py": """from typing import List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum
from .common import BaseMetadata

class SectionType(str, Enum):
    HEADER = "HEADER"
    SUMMARY = "SUMMARY"
    EXPERIENCE = "EXPERIENCE"
    EDUCATION = "EDUCATION"
    SKILLS = "SKILLS"
    PROJECTS = "PROJECTS"
    CERTIFICATIONS = "CERTIFICATIONS"
    UNKNOWN = "UNKNOWN"

class SkillTag(BaseModel):
    name: str
    confidence: float = 1.0

class ExperienceEntry(BaseModel):
    company: str
    role: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: str

class EducationEntry(BaseModel):
    institution: str
    degree: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class ResumeSection(BaseModel):
    section_id: str
    section_type: SectionType
    content: str
    start_index: int
    end_index: int

class ChunkMetadata(BaseMetadata):
    candidate_id: str
    document_id: str
    chunk_id: str
    section_id: str
    section_type: SectionType
    semantic_tags: List[str] = Field(default_factory=list)
    source_file: str
    parser_version: str
    chunk_strategy: str
    parent_chunk_id: Optional[str] = None

class DocumentChunk(BaseModel):
    metadata: ChunkMetadata
    content: str
    token_count: int

class ResumeDocument(BaseModel):
    document_id: str
    candidate_id: str
    raw_text: str
    sections: List[ResumeSection]
    metadata: BaseMetadata

class Candidate(BaseModel):
    candidate_id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    primary_skills: List[SkillTag] = Field(default_factory=list)
    metadata: BaseMetadata
""",

    "schemas/ingestion.py": """from typing import Optional, List
from pydantic import BaseModel
from .common import ProcessingStatus, ErrorInfo, TimestampMixin
from .domain import ResumeDocument, DocumentChunk

class IngestionRequest(BaseModel):
    candidate_id: str
    file_path: str
    trace_id: Optional[str] = None

class ParsingResult(BaseModel):
    status: ProcessingStatus
    document: Optional[ResumeDocument] = None
    error: Optional[ErrorInfo] = None

class ChunkingResult(BaseModel):
    status: ProcessingStatus
    chunks: List[DocumentChunk] = []
    error: Optional[ErrorInfo] = None

class IngestionResult(TimestampMixin):
    candidate_id: str
    document_id: str
    status: ProcessingStatus
    chunks_indexed: int = 0
    error: Optional[ErrorInfo] = None
""",

    "schemas/vector.py": """from typing import List, Union, Dict, Any
from pydantic import BaseModel, ConfigDict
import numpy as np

class EmbeddingVector(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    vector: Union[List[float], np.ndarray]
    dimensions: int
    model_name: str
    model_version: str

class VectorRecord(BaseModel):
    chunk_id: str
    embedding: EmbeddingVector
    
class VectorSearchResult(BaseModel):
    chunk_id: str
    similarity_score: float
    distance: Optional[float] = None
""",

    "schemas/retrieval.py": """from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from .domain import DocumentChunk
from .common import TimestampMixin

class RetrievalQuery(BaseModel):
    query_text: str
    top_k: int = 10
    filters: Optional[Dict[str, Any]] = None
    trace_id: Optional[str] = None

class RetrievedChunk(BaseModel):
    chunk: DocumentChunk
    similarity_score: float

class RetrievalResult(TimestampMixin):
    query: RetrievalQuery
    results: List[RetrievedChunk]
    execution_time_ms: float
""",

    "schemas/ranking.py": """from typing import List, Dict, Optional
from pydantic import BaseModel
from .domain import Candidate
from .retrieval import RetrievedChunk
from .common import TimestampMixin

class RankingBreakdown(BaseModel):
    base_similarity_score: float
    skill_overlap_bonus: float = 0.0
    experience_bonus: float = 0.0
    section_weight_bonus: float = 0.0

class CandidateScore(BaseModel):
    final_score: float
    breakdown: RankingBreakdown
    explainability_log: List[str]

class RankedCandidate(BaseModel):
    candidate: Candidate
    score: CandidateScore
    supporting_chunks: List[RetrievedChunk]

class RankingResult(TimestampMixin):
    job_description: str
    ranked_candidates: List[RankedCandidate]
    execution_time_ms: float
""",

    "interfaces/__init__.py": "",
    
    "interfaces/parser.py": """from abc import ABC, abstractmethod
from typing import BinaryIO
from shared.schemas.ingestion import ParsingResult

class IParser(ABC):
    \"\"\"
    Abstract base class for document parsing.
    Responsible for extracting raw text from bytes.
    \"\"\"
    
    @abstractmethod
    def parse(self, file_stream: BinaryIO, file_name: str) -> ParsingResult:
        pass
        
    @abstractmethod
    async def parse_async(self, file_stream: BinaryIO, file_name: str) -> ParsingResult:
        pass
""",

    "interfaces/cleaner.py": """from abc import ABC, abstractmethod
from shared.schemas.domain import ResumeDocument

class ICleaner(ABC):
    \"\"\"
    Abstract base class for text normalization and artifact removal.
    \"\"\"
    
    @abstractmethod
    def clean(self, document: ResumeDocument) -> ResumeDocument:
        pass
""",

    "interfaces/chunker.py": """from abc import ABC, abstractmethod
from typing import List
from shared.schemas.domain import ResumeDocument, DocumentChunk

class ISectionParser(ABC):
    \"\"\"
    Identifies and tags semantic sections within a cleaned document.
    \"\"\"
    
    @abstractmethod
    def parse_sections(self, document: ResumeDocument) -> ResumeDocument:
        pass

class IChunker(ABC):
    \"\"\"
    Divides semantic sections into embeddable DocumentChunks.
    \"\"\"
    
    @abstractmethod
    def chunk(self, document: ResumeDocument) -> List[DocumentChunk]:
        pass
""",

    "interfaces/embedder.py": """from abc import ABC, abstractmethod
from typing import List, Union
from shared.schemas.domain import DocumentChunk
from shared.schemas.vector import EmbeddingVector

class IEmbedder(ABC):
    \"\"\"
    Converts text or DocumentChunks into dense vector representations.
    \"\"\"
    
    @abstractmethod
    def embed_text(self, text: str) -> EmbeddingVector:
        pass
        
    @abstractmethod
    def embed_chunks(self, chunks: List[DocumentChunk]) -> List[EmbeddingVector]:
        pass
        
    @abstractmethod
    async def embed_chunks_async(self, chunks: List[DocumentChunk]) -> List[EmbeddingVector]:
        pass
""",

    "interfaces/vectordb.py": """from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from shared.schemas.vector import VectorRecord, VectorSearchResult, EmbeddingVector

class IVectorDB(ABC):
    \"\"\"
    Interface for vector storage and similarity search.
    Must NOT leak implementation details (e.g., FAISS indices) to callers.
    \"\"\"
    
    @abstractmethod
    def upsert(self, records: List[VectorRecord]) -> None:
        pass
        
    @abstractmethod
    def search(self, query_vector: EmbeddingVector, top_k: int, filters: Optional[Dict[str, Any]] = None) -> List[VectorSearchResult]:
        pass
        
    @abstractmethod
    def delete(self, chunk_ids: List[str]) -> None:
        pass
""",

    "interfaces/storage.py": """from abc import ABC, abstractmethod
from typing import List, Optional
from shared.schemas.domain import Candidate, DocumentChunk

class IMetadataStore(ABC):
    \"\"\"
    Relational metadata storage interface (e.g., PostgreSQL).
    Isolates business entity persistence from vector storage.
    \"\"\"
    
    @abstractmethod
    def save_candidate(self, candidate: Candidate) -> None:
        pass
        
    @abstractmethod
    def get_candidate(self, candidate_id: str) -> Optional[Candidate]:
        pass
        
    @abstractmethod
    def save_chunks(self, chunks: List[DocumentChunk]) -> None:
        pass
        
    @abstractmethod
    def get_chunks_by_ids(self, chunk_ids: List[str]) -> List[DocumentChunk]:
        pass
        
    @abstractmethod
    def get_chunks_by_candidate(self, candidate_id: str) -> List[DocumentChunk]:
        pass
""",

    "interfaces/retriever.py": """from abc import ABC, abstractmethod
from shared.schemas.retrieval import RetrievalQuery, RetrievalResult

class IRetriever(ABC):
    \"\"\"
    Coordinates vector search and metadata rehydration.
    \"\"\"
    
    @abstractmethod
    def retrieve(self, query: RetrievalQuery) -> RetrievalResult:
        pass
        
    @abstractmethod
    async def retrieve_async(self, query: RetrievalQuery) -> RetrievalResult:
        pass
""",

    "interfaces/ranking.py": """from abc import ABC, abstractmethod
from typing import List
from shared.schemas.retrieval import RetrievedChunk
from shared.schemas.ranking import RankedCandidate, RankingResult

class ICandidateAggregator(ABC):
    \"\"\"
    Groups retrieved chunks by candidate to form the basis for candidate-level scoring.
    \"\"\"
    
    @abstractmethod
    def aggregate(self, retrieved_chunks: List[RetrievedChunk]) -> List[RankedCandidate]:
        pass

class IRanker(ABC):
    \"\"\"
    Scores and sorts aggregated candidates based on heuristics and vector similarity.
    \"\"\"
    
    @abstractmethod
    def rank(self, candidates: List[RankedCandidate], job_description: str) -> RankingResult:
        pass
""",

    "interfaces/ingestion.py": """from abc import ABC, abstractmethod
from shared.schemas.ingestion import IngestionRequest, IngestionResult

class IIngestionService(ABC):
    \"\"\"
    Orchestrates the entire ingestion pipeline: Parse -> Clean -> Section -> Chunk -> Embed -> Store.
    \"\"\"
    
    @abstractmethod
    def ingest(self, request: IngestionRequest) -> IngestionResult:
        pass
        
    @abstractmethod
    async def ingest_async(self, request: IngestionRequest) -> IngestionResult:
        pass
"""
}

for path_str, content in files_content.items():
    full_path = base_dir / path_str
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print(f"Successfully generated {len(files_content)} schema and interface files.")
