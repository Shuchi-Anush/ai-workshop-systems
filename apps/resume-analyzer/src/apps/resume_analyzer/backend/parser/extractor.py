import re
from typing import List
from ai_contracts.interfaces.extraction import ISkillExtractor

class RuleBasedSkillExtractor(ISkillExtractor):
    def __init__(self):
        # Deterministic, local-first dictionary of skills with synonyms mapping to a canonical form
        self.skill_map = {
            "python": ["python", "py"],
            "fastapi": ["fastapi", "fast api"],
            "react": ["react", "react.js", "reactjs"],
            "django": ["django"],
            "node.js": ["node.js", "nodejs", "node"],
            "c#": ["c#", "c-sharp", "c sharp", "asp.net", ".net", "dotnet"],
            "java": ["java"],
            "spring": ["spring", "spring boot", "springboot"],
            "docker": ["docker", "dockerize"],
            "kubernetes": ["kubernetes", "k8s"],
            "sql": ["sql"],
            "postgresql": ["postgres", "postgresql", "psql"],
            "mongodb": ["mongodb", "mongo"],
            "aws": ["aws", "amazon web services"],
            "gcp": ["gcp", "google cloud platform", "google cloud"],
            "azure": ["azure"],
            "tensorflow": ["tensorflow", "tf"],
            "pytorch": ["pytorch"],
            "machine learning": ["machine learning", "ml"],
            "rag": ["rag", "retrieval augmented generation"],
            "llm": ["llm", "large language model"],
            "langchain": ["langchain"],
            "chromadb": ["chromadb", "chroma"],
            "javascript": ["javascript", "js"],
            "typescript": ["typescript", "ts"],
            "golang": ["golang", "go"],
            "rust": ["rust"],
            "c++": ["c++", "cpp"]
        }
        
    def extract(self, text: str) -> List[str]:
        if not text:
            return []
            
        text_lower = text.lower()
        extracted = set()
        
        for canonical, synonyms in self.skill_map.items():
            for syn in synonyms:
                # Word boundary regex to avoid partial matches
                # If synonym has special chars like C++, escape them
                pattern = r'\b' + re.escape(syn) + r'(?:\b|$)'
                if syn == "c++" or syn == "c#":
                    pattern = r'(?:\b|^)' + re.escape(syn) + r'(?:\b|$|\s)'
                if re.search(pattern, text_lower):
                    extracted.add(canonical)
                    break # Already found canonical skill
                    
        return list(extracted)
