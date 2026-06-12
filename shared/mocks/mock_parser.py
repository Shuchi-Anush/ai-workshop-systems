from typing import BinaryIO, List
from shared.interfaces.parser import IParser
from shared.interfaces.cleaner import ICleaner
from shared.interfaces.chunker import ISectionParser, IChunker
from shared.schemas.ingestion import ParsingResult, ProcessingStatus
from shared.schemas.domain import ResumeDocument, ResumeSection, DocumentChunk, SectionType, ChunkMetadata, BaseMetadata
import uuid

class MockParser(IParser):
    def parse(self, file_stream: BinaryIO, file_name: str) -> ParsingResult:
        # In a real system, we'd extract text. Here we assume file_name holds the raw text for the mock.
        doc = ResumeDocument(
            document_id=str(uuid.uuid4()),
            candidate_id="unknown",
            raw_text=file_name,
            sections=[],
            metadata=BaseMetadata()
        )
        return ParsingResult(status=ProcessingStatus.COMPLETED, document=doc)
        
    async def parse_async(self, file_stream: BinaryIO, file_name: str) -> ParsingResult:
        return self.parse(file_stream, file_name)

class MockCleaner(ICleaner):
    def clean(self, document: ResumeDocument) -> ResumeDocument:
        document.raw_text = document.raw_text.strip()
        return document

class MockSectionParser(ISectionParser):
    def parse_sections(self, document: ResumeDocument) -> ResumeDocument:
        # Naive mock: splits by double newline and guesses section
        blocks = document.raw_text.split("\n\n")
        sections = []
        for i, block in enumerate(blocks):
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

class MockChunker(IChunker):
    def chunk(self, document: ResumeDocument) -> List[DocumentChunk]:
        chunks = []
        for i, sec in enumerate(document.sections):
            meta = ChunkMetadata(
                candidate_id=document.candidate_id,
                document_id=document.document_id,
                chunk_id=f"{document.document_id}_chunk_{i}",
                section_id=sec.section_id,
                section_type=sec.section_type,
                source_file="mock_source",
                parser_version="1.0",
                chunk_strategy="mock_section_split"
            )
            chunks.append(
                DocumentChunk(
                    metadata=meta,
                    content=sec.content,
                    token_count=len(sec.content.split())
                )
            )
        return chunks
