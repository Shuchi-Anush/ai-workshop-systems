import uuid
from typing import List
from ai_contracts.interfaces.chunker import ISectionParser, IChunker
from ai_contracts.schemas.chunk import DocumentChunk, ChunkMetadata
from apps.resume_analyzer.backend.schemas.domain import ResumeDocument, ResumeSection, SectionType

class SimpleSectionParser(ISectionParser[ResumeDocument]):
    def parse_sections(self, document: ResumeDocument) -> ResumeDocument:
        # Simple sectioning by double newlines for demo purposes
        blocks = document.raw_text.split("\n\n")
        sections = []
        for i, block in enumerate(blocks):
            if not block.strip(): continue
            stype = SectionType.UNKNOWN
            block_upper = block.upper()
            if "EXPERIENCE" in block_upper or "WORK" in block_upper:
                stype = SectionType.EXPERIENCE
            elif "EDUCATION" in block_upper:
                stype = SectionType.EDUCATION
            elif "SKILL" in block_upper:
                stype = SectionType.SKILLS
                
            sections.append(
                ResumeSection(
                    section_id=f"sec_{i}",
                    section_type=stype,
                    content=block,
                    start_index=0,
                    end_index=len(block)
                )
            )
        document.sections = sections
        return document

class SimpleChunker(IChunker[ResumeDocument]):
    def chunk(self, document: ResumeDocument) -> List[DocumentChunk]:
        chunks = []
        for i, sec in enumerate(document.sections):
            meta = ChunkMetadata(
                candidate_id=document.candidate_id,
                document_id=document.document_id,
                chunk_id=f"{document.document_id}_chunk_{i}",
                section_id=sec.section_id,
                section_type=sec.section_type.value,
                source_file="parsed_pdf",
                parser_version="1.0",
                chunk_strategy="simple_section_split"
            )
            chunks.append(
                DocumentChunk(
                    metadata=meta,
                    content=sec.content,
                    token_count=len(sec.content.split())
                )
            )
        return chunks
