from typing import List, Optional, Any
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
