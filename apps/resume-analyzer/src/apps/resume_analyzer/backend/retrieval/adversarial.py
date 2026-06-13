import re
from typing import Dict, List, Any

class AdversarialDetector:
    """
    Lightweight, deterministic detection of keyword stuffing and adversarial injection.
    """
    
    def __init__(self, skill_map: Dict[str, List[str]]):
        self.skill_map = skill_map
        self.canonical_skills = list(skill_map.keys())

    def analyze(self, text: str, query_skills: List[str]) -> Dict[str, float]:
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        total_words = len(words)
        if total_words == 0:
            return {"adversarial_score": 0.0, "keyword_density": 0.0}

        # 1. Detect Keyword Density
        skill_counts = 0
        for skill in self.canonical_skills:
            if skill in text_lower:
                skill_counts += text_lower.count(skill)
        
        keyword_density = skill_counts / total_words if total_words > 0 else 0
        
        # 2. Detect Suspicious Noun Stacking (comma separated lists of skills with no verbs)
        # e.g., "Python, FastAPI, Docker, Kubernetes, React, C#, Java"
        stacking_pattern = r'([a-z0-9#\+\-]+(?:,\s*[a-z0-9#\+\-]+){4,})'
        stacking_matches = re.findall(stacking_pattern, text_lower)
        stacking_penalty = 0.5 if len(stacking_matches) > 0 else 0.0
        
        # 3. Detect Explicit Injection Phrases
        injection_phrases = ["i hire for", "i am not a developer", "skills:"]
        injection_penalty = 0.0
        for phrase in injection_phrases:
            if phrase in text_lower:
                injection_penalty += 0.3
                
        # 4. Low Semantic Diversity (too few total words vs too many unique skills)
        unique_skills_found = sum(1 for skill in self.canonical_skills if skill in text_lower)
        semantic_diversity_penalty = 0.0
        if total_words < 50 and unique_skills_found > 5:
            semantic_diversity_penalty = 0.5
            
        adversarial_score = keyword_density * 2.0 + stacking_penalty + injection_penalty + semantic_diversity_penalty
        
        # Cap score at 1.0
        adversarial_score = min(1.0, adversarial_score)
        
        return {
            "adversarial_score": adversarial_score,
            "keyword_density": keyword_density,
            "semantic_diversity_penalty": semantic_diversity_penalty,
            "stacking_penalty": stacking_penalty
        }

    def compute_penalty_multiplier(self, text: str, query_skills: List[str]) -> float:
        """
        Returns a multiplier between 0.01 (heavily penalized) and 1.0 (no penalty)
        """
        analysis = self.analyze(text, query_skills)
        adv_score = analysis["adversarial_score"]
        
        if adv_score > 0.6:
            return 0.1 # Severe penalty
        elif adv_score > 0.4:
            return 0.5 # Moderate penalty
        return 1.0 # Safe
