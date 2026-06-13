from ai_contracts.interfaces.cleaner import ICleaner
from apps.resume_analyzer.backend.schemas.domain import ResumeDocument

class SimpleCleaner(ICleaner[ResumeDocument]):
    def clean(self, document: ResumeDocument) -> ResumeDocument:
        # Very simple text cleaning
        import re
        text = document.raw_text
        text = re.sub(r'\r\n', '\n', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        document.raw_text = text.strip()
        return document
