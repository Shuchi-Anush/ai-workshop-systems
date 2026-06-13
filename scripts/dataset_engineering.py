import os
import glob
import json
import random
import shutil
from collections import Counter
from pypdf import PdfReader
from pathlib import Path
import traceback

class DatasetEngineer:
    def __init__(self, raw_dir, processed_dir, reports_dir):
        self.raw_dir = Path(raw_dir)
        self.processed_dir = Path(processed_dir)
        self.reports_dir = Path(reports_dir)
        self.stats = {
            "total_files_scanned": 0,
            "corrupt_files": 0,
            "domains": Counter(),
            "skills": Counter(),
            "token_lengths": [],
            "top_ambiguous": Counter()
        }
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

    def _extract_skills(self, text):
        import re
        extracted = set()
        text_lower = text.lower()
        for canonical, synonyms in self.skill_map.items():
            for syn in synonyms:
                pattern = r'\b' + re.escape(syn) + r'(?:\b|$)'
                if syn == "c++" or syn == "c#":
                    pattern = r'(?:\b|^)' + re.escape(syn) + r'(?:\b|$|\s)'
                if re.search(pattern, text_lower):
                    extracted.add(canonical)
                    break
        return list(extracted)

    def run(self):
        print("Starting Dataset Engineering Pipeline...")
        if os.path.exists(self.processed_dir / "benchmark_ready"):
            shutil.rmtree(self.processed_dir / "benchmark_ready")
        os.makedirs(self.processed_dir / "benchmark_ready/golden", exist_ok=True)
        os.makedirs(self.processed_dir / "benchmark_ready/distractors", exist_ok=True)
        os.makedirs(self.processed_dir / "benchmark_ready/adversarial", exist_ok=True)
        os.makedirs(self.processed_dir / "benchmark_ready/noisy", exist_ok=True)
        os.makedirs(self.processed_dir / "cleaned", exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)

        golden_candidates = []
        distractor_candidates = []
        noisy_candidates = []

        # Analyze a subset for speed, limit to 20 per domain
        for domain_dir in self.raw_dir.glob("*"):
            if not domain_dir.is_dir(): continue
            domain = domain_dir.name
            
            files = list(domain_dir.glob("*.pdf"))
            self.stats["total_files_scanned"] += len(files)
            
            sample_files = files if domain == "INFORMATION-TECHNOLOGY" else files[:10]
            for pdf_file in sample_files:
                try:
                    reader = PdfReader(pdf_file)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                        
                    if not text.strip():
                        self.stats["corrupt_files"] += 1
                        continue
                        
                    self.stats["domains"][domain] += 1
                    tokens = len(text.split())
                    self.stats["token_lengths"].append(tokens)
                    
                    skills = self._extract_skills(text)
                    for s in skills:
                        self.stats["skills"][s] += 1
                        
                    candidate_info = {
                        "id": pdf_file.stem,
                        "domain": domain,
                        "skills": skills,
                        "path": str(pdf_file)
                    }

                    if domain == "INFORMATION-TECHNOLOGY":
                        if "python" in skills and len(golden_candidates) < 5:
                            golden_candidates.append(candidate_info)
                        elif ("react" in skills or "c#" in skills) and len(distractor_candidates) < 10:
                            distractor_candidates.append(candidate_info)
                        elif len(noisy_candidates) < 10:
                            noisy_candidates.append(candidate_info)
                    else:
                        if ("python" in skills or "react" in skills) and len(distractor_candidates) < 20:
                            distractor_candidates.append(candidate_info)
                        elif len(noisy_candidates) < 20:
                            noisy_candidates.append(candidate_info)
                            
                except Exception as e:
                    self.stats["corrupt_files"] += 1

        print("Building Benchmark Subset...")
        self._build_benchmarks(golden_candidates, distractor_candidates, noisy_candidates)
        
        print("Generating Adversarial Resumes...")
        self._generate_adversarial()

        print("Generating Reports...")
        self._generate_reports()

    def _build_benchmarks(self, golden, distractors, noisy):
        for g in golden[:5]:
            skills_str = "_".join(sorted(list(g["skills"])))
            shutil.copy(g["path"], self.processed_dir / f"benchmark_ready/golden/{g['id']}_{g['domain']}_{skills_str}.pdf")
        for d in distractors[:10]:
            skills_str = "_".join(sorted(list(d["skills"])))
            shutil.copy(d["path"], self.processed_dir / f"benchmark_ready/distractors/{d['id']}_{d['domain']}_{skills_str}.pdf")
        for n in noisy[:10]:
            skills_str = "_".join(sorted(list(n["skills"])))
            shutil.copy(n["path"], self.processed_dir / f"benchmark_ready/noisy/{n['id']}_{n['domain']}_{skills_str}.pdf")

    def _generate_adversarial(self):
        from reportlab.pdfgen import canvas
        adv_path = self.processed_dir / "benchmark_ready/adversarial"
        # 1. Keyword Stuffed HR
        c = canvas.Canvas(str(adv_path / "adv_hr_keyword_stuffed.pdf"))
        c.drawString(50, 800, "Human Resources Manager")
        c.drawString(50, 780, "I hire for: Python, FastAPI, Docker, Kubernetes, React, C#, Java")
        c.drawString(50, 760, "I am not a developer but I know Python Excel scripting.")
        c.save()

        # 2. Fake Seniority
        c = canvas.Canvas(str(adv_path / "adv_fake_seniority.pdf"))
        c.drawString(50, 800, "Junior Developer")
        c.drawString(50, 780, "Skills: HTML, CSS, JavaScript")
        c.drawString(50, 760, "Aspiring to be a Senior Staff Python Backend Architect with Docker.")
        c.save()

    def _generate_reports(self):
        with open(self.reports_dir / "dataset_analysis.json", "w") as f:
            json.dump({
                "total_scanned": self.stats["total_files_scanned"],
                "corrupt_files": self.stats["corrupt_files"],
                "domains": dict(self.stats["domains"].most_common()),
                "top_skills": dict(self.stats["skills"].most_common(15)),
                "avg_tokens": sum(self.stats["token_lengths"]) / max(1, len(self.stats["token_lengths"]))
            }, f, indent=2)

        with open(self.reports_dir / "dataset_analysis.md", "w") as f:
            f.write("# Dataset Intelligence Report\n\n")
            f.write(f"- **Total Resumes Scanned:** {self.stats['total_files_scanned']}\n")
            f.write(f"- **Corrupt/Unparsable:** {self.stats['corrupt_files']}\n")
            avg_tok = sum(self.stats["token_lengths"]) / max(1, len(self.stats["token_lengths"]))
            f.write(f"- **Average Token Length:** {avg_tok:.0f}\n\n")
            f.write("## Top Skills Detected\n")
            for k, v in self.stats["skills"].most_common(10):
                f.write(f"- {k}: {v}\n")

if __name__ == "__main__":
    os.makedirs("scripts", exist_ok=True)
    eng = DatasetEngineer(
        raw_dir="datasets/raw/resume_corpus_v1/categorized_resumes",
        processed_dir="datasets/processed",
        reports_dir="reports"
    )
    eng.run()
