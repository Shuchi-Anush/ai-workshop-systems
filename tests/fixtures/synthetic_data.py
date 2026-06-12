from shared.schemas.domain import Candidate, SkillTag, BaseMetadata

# Synthetic Resumes (Raw Text)
RESUME_BACKEND = """
John Doe - Backend Engineer

EXPERIENCE
Senior Backend Engineer at TechCorp
Built scalable microservices using Python, FastAPI, and PostgreSQL. 
Designed high-throughput vector search pipelines.

SKILLS
Python, FastAPI, SQL, Docker, Kubernetes
"""

RESUME_ML = """
Jane Smith - Machine Learning Engineer

EXPERIENCE
ML Researcher at AI Labs
Trained large language models using PyTorch.
Implemented retrieval augmented generation (RAG) using FAISS and HuggingFace.

SKILLS
Python, PyTorch, Machine Learning, NLP, FAISS
"""

# Synthetic Candidate Metadata
CANDIDATE_BACKEND = Candidate(
    candidate_id="cand_backend_001",
    first_name="John",
    last_name="Doe",
    primary_skills=[SkillTag(name="Python"), SkillTag(name="FastAPI")],
    metadata=BaseMetadata()
)

CANDIDATE_ML = Candidate(
    candidate_id="cand_ml_002",
    first_name="Jane",
    last_name="Smith",
    primary_skills=[SkillTag(name="PyTorch"), SkillTag(name="Machine Learning")],
    metadata=BaseMetadata()
)
