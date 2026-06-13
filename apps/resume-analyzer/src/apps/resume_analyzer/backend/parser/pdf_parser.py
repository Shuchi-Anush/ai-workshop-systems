import uuid
from typing import BinaryIO
from ai_contracts.interfaces.parser import IParser
from ai_contracts.schemas.common import BaseMetadata, ProcessingStatus
from ai_contracts.schemas.ingestion import ParsingResult
from apps.resume_analyzer.backend.schemas.domain import ResumeDocument
from pypdf import PdfReader

class PyPDFParser(IParser[ResumeDocument]):
    def parse(self, file_stream: BinaryIO, file_name: str) -> ParsingResult[ResumeDocument]:
        try:
            reader = PdfReader(file_stream)
            text = ""
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
            
            doc = ResumeDocument(
                document_id=str(uuid.uuid4()),
                candidate_id="unknown",
                raw_text=text,
                sections=[],
                metadata=BaseMetadata(source_file=file_name)
            )
            return ParsingResult(status=ProcessingStatus.COMPLETED, document=doc)
        except Exception as e:
            return ParsingResult(status=ProcessingStatus.FAILED, error={"message": str(e), "code": "PARSE_ERROR"})
            
    async def parse_async(self, file_stream: BinaryIO, file_name: str) -> ParsingResult[ResumeDocument]:
        return self.parse(file_stream, file_name)
