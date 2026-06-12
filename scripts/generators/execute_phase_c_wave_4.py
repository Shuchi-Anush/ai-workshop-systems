import os
from pathlib import Path

repo_root = Path("d:/ai-workshop-systems")

# STEP 1: Create generic chunk.py
chunk_py_content = '''from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from ai_contracts.schemas.common import BaseMetadata

class ChunkMetadata(BaseMetadata):
    model_config = ConfigDict(extra="allow")
    
    document_id: str
    chunk_id: str
    source_file: str
    chunk_strategy: str
    parser_version: str
    parent_chunk_id: Optional[str] = None

class DocumentChunk(BaseModel):
    model_config = ConfigDict(extra="allow")
    
    metadata: ChunkMetadata
    content: str
    token_count: int
'''
chunk_py_path = repo_root / "packages/ai-contracts/src/ai_contracts/schemas/chunk.py"
chunk_py_path.parent.mkdir(parents=True, exist_ok=True)
chunk_py_path.write_text(chunk_py_content, encoding='utf-8')
(chunk_py_path.parent / "__init__.py").touch()

# STEP 2: Create app-specific domain.py
app_domain_content = '''from typing import List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum
from ai_contracts.schemas.common import BaseMetadata

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
'''
app_domain_path = repo_root / "task_01_resume_rag/src/schemas/domain.py"
app_domain_path.parent.mkdir(parents=True, exist_ok=True)
app_domain_path.write_text(app_domain_content, encoding='utf-8')
(app_domain_path.parent / "__init__.py").touch()

# STEP 3: Create compatibility shim
shim_content = '''from ai_contracts.schemas.chunk import DocumentChunk, ChunkMetadata
from task_01_resume_rag.src.schemas.domain import (
    SectionType, SkillTag, ExperienceEntry, EducationEntry,
    ResumeSection, ResumeDocument, Candidate
)
'''
shim_path = repo_root / "shared/schemas/domain.py"
shim_path.write_text(shim_content, encoding='utf-8')

# STEP 4: Refactor Ingestion to Generics
ingestion_path = repo_root / "shared/schemas/ingestion.py"
ingestion_content = '''from typing import Optional, List, Generic, TypeVar
from pydantic import BaseModel
from ai_contracts.schemas.common import ProcessingStatus, ErrorInfo, TimestampMixin
from ai_contracts.schemas.chunk import DocumentChunk

DocT = TypeVar("DocT")

class IngestionRequest(BaseModel):
    candidate_id: str
    file_path: str
    trace_id: Optional[str] = None

class ParsingResult(BaseModel, Generic[DocT]):
    status: ProcessingStatus
    document: Optional[DocT] = None
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
'''
ingestion_path.write_text(ingestion_content, encoding='utf-8')

# STEP 5: Refactor Interfaces
parser_path = repo_root / "packages/ai-contracts/src/ai_contracts/interfaces/parser.py"
parser_content = '''from abc import ABC, abstractmethod
from typing import BinaryIO, TypeVar, Generic
from shared.schemas.ingestion import ParsingResult

DocT = TypeVar("DocT")

class IParser(ABC, Generic[DocT]):
    """
    Abstract base class for document parsing.
    Responsible for extracting raw text from bytes.
    """
    
    @abstractmethod
    def parse(self, file_stream: BinaryIO, file_name: str) -> ParsingResult[DocT]:
        pass
        
    @abstractmethod
    async def parse_async(self, file_stream: BinaryIO, file_name: str) -> ParsingResult[DocT]:
        pass
'''
parser_path.write_text(parser_content, encoding='utf-8')

chunker_path = repo_root / "packages/ai-contracts/src/ai_contracts/interfaces/chunker.py"
chunker_content = '''from abc import ABC, abstractmethod
from typing import List, TypeVar, Generic
from ai_contracts.schemas.chunk import DocumentChunk

DocT = TypeVar("DocT")

class ISectionParser(ABC, Generic[DocT]):
    """
    Identifies and tags semantic sections within a cleaned document.
    """
    
    @abstractmethod
    def parse_sections(self, document: DocT) -> DocT:
        pass

class IChunker(ABC, Generic[DocT]):
    """
    Divides semantic sections into embeddable DocumentChunks.
    """
    
    @abstractmethod
    def chunk(self, document: DocT) -> List[DocumentChunk]:
        pass
'''
chunker_path.write_text(chunker_content, encoding='utf-8')

cleaner_path = repo_root / "packages/ai-contracts/src/ai_contracts/interfaces/cleaner.py"
cleaner_content = '''from abc import ABC, abstractmethod
from typing import TypeVar, Generic

DocT = TypeVar("DocT")

class ICleaner(ABC, Generic[DocT]):
    """
    Cleans raw text (e.g. standardizing whitespace, removing garbled characters).
    """
    
    @abstractmethod
    def clean(self, document: DocT) -> DocT:
        pass
'''
cleaner_path.write_text(cleaner_content, encoding='utf-8')

ingestion_iface_path = repo_root / "packages/ai-contracts/src/ai_contracts/interfaces/ingestion.py"
ingestion_iface_content = '''from abc import ABC, abstractmethod
from shared.schemas.ingestion import IngestionRequest, IngestionResult

class IIngestionService(ABC):
    """
    Orchestrates the entire ingestion lifecycle.
    """
    
    @abstractmethod
    def ingest(self, request: IngestionRequest) -> IngestionResult:
        pass
        
    @abstractmethod
    async def ingest_async(self, request: IngestionRequest) -> IngestionResult:
        pass
'''
ingestion_iface_path.write_text(ingestion_iface_content, encoding='utf-8')

# Clean up shared/mocks/mock_parser.py imports
mock_parser_path = repo_root / "shared/mocks/mock_parser.py"
mock_parser_content = mock_parser_path.read_text(encoding='utf-8')
mock_parser_content = mock_parser_content.replace(
    "from ai_contracts.interfaces.parser import IParser",
    "from ai_contracts.interfaces.parser import IParser\\nfrom ai_contracts.interfaces.cleaner import ICleaner"
)
mock_parser_path.write_text(mock_parser_content, encoding='utf-8')

# Clean up shared/pipelines/ingestion_pipeline.py typing if needed
ingestion_pipe_path = repo_root / "shared/pipelines/ingestion_pipeline.py"
pipe_content = ingestion_pipe_path.read_text(encoding='utf-8')
pipe_content = pipe_content.replace("from shared.schemas.vector import VectorRecord", "from ai_vector.schemas.vector import VectorRecord")
ingestion_pipe_path.write_text(pipe_content, encoding='utf-8')

print("Surgery Complete")
