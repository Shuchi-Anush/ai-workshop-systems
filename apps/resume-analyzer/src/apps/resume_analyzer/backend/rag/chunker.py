import uuid
import re
from typing import List
from ai_contracts.interfaces.chunker import ISectionParser, IChunker
from ai_contracts.schemas.chunk import DocumentChunk, ChunkMetadata
from apps.resume_analyzer.backend.schemas.domain import ResumeDocument, ResumeSection, SectionType

class AdvancedSectionParser(ISectionParser[ResumeDocument]):
    def parse_sections(self, document: ResumeDocument) -> ResumeDocument:
        # Better heuristic section splitting
        lines = document.raw_text.split("\n")
        sections = []
        
        current_type = SectionType.UNKNOWN
        current_content = []
        
        section_headers = {
            "EXPERIENCE": SectionType.EXPERIENCE,
            "WORK HISTORY": SectionType.EXPERIENCE,
            "EMPLOYMENT": SectionType.EXPERIENCE,
            "EDUCATION": SectionType.EDUCATION,
            "ACADEMIC": SectionType.EDUCATION,
            "SKILLS": SectionType.SKILLS,
            "TECHNICAL SKILLS": SectionType.SKILLS,
            "PROJECTS": SectionType.UNKNOWN, # Map to unknown or add to enum
        }
        
        for line in lines:
            line_clean = line.strip().upper()
            matched_type = None
            for header, stype in section_headers.items():
                if line_clean == header or line_clean.startswith(header + ":"):
                    matched_type = stype
                    break
                    
            if matched_type:
                if current_content:
                    sections.append(ResumeSection(
                        section_id=str(uuid.uuid4()),
                        section_type=current_type,
                        content="\n".join(current_content),
                        start_index=0, end_index=0
                    ))
                current_type = matched_type
                current_content = [line]
            else:
                current_content.append(line)
                
        if current_content:
            sections.append(ResumeSection(
                section_id=str(uuid.uuid4()),
                section_type=current_type,
                content="\n".join(current_content),
                start_index=0, end_index=0
            ))
            
        document.sections = sections
        return document

class ContextAwareChunker(IChunker[ResumeDocument]):
    def chunk(self, document: ResumeDocument) -> List[DocumentChunk]:
        chunks = []
        for i, sec in enumerate(document.sections):
            
            # Simple role detection (assuming short bold lines or all caps might be roles/companies)
            # In a real system, use NER. Here we approximate by splitting double newlines
            blocks = sec.content.split("\n\n")
            
            for j, block in enumerate(blocks):
                cleaned_block = block.strip()
                if not cleaned_block or len(cleaned_block.split()) < 3: 
                    continue
                
                # Try to extract the first line as Role/Company if it's experience
                role_company = "General"
                if sec.section_type == SectionType.EXPERIENCE:
                    first_line = block.split("\n")[0].strip()
                    if len(first_line) > 3 and len(first_line) < 60:
                        role_company = first_line
                        
                # Context Injection
                context_prefix = f"[Candidate: {document.candidate_id} | Section: {sec.section_type.value} | Role/Company: {role_company}]\n"
                injected_content = context_prefix + block
                
                meta = ChunkMetadata(
                    candidate_id=document.candidate_id,
                    document_id=document.document_id,
                    chunk_id=f"{document.document_id}_{sec.section_type.value}_{j}",
                    section_id=sec.section_id,
                    section_type=sec.section_type.value,
                    source_file="parsed_pdf",
                    parser_version="2.0",
                    chunk_strategy="context_injected_blocks"
                )
                
                chunks.append(
                    DocumentChunk(
                        metadata=meta,
                        content=injected_content,
                        token_count=len(injected_content.split())
                    )
                )
        return chunks
