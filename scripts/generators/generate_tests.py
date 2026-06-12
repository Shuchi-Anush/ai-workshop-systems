import os
from pathlib import Path

base_dir = Path("d:/ai-workshop-systems")
tests_dir = base_dir / "tests"
mocks_dir = base_dir / "shared" / "mocks"

(tests_dir / "fixtures").mkdir(parents=True, exist_ok=True)
(tests_dir / "integration").mkdir(parents=True, exist_ok=True)
mocks_dir.mkdir(parents=True, exist_ok=True)

# Important: ensure tests acts as a module
(tests_dir / "__init__.py").touch()
(tests_dir / "integration" / "__init__.py").touch()
(tests_dir / "fixtures" / "__init__.py").touch()

files_content = {
    "shared/mocks/mock_parser.py": """from typing import BinaryIO, List
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
        blocks = document.raw_text.split("\\n\\n")
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
""",

    "tests/fixtures/synthetic_data.py": """from shared.schemas.domain import Candidate, SkillTag, BaseMetadata

# Synthetic Resumes (Raw Text)
RESUME_BACKEND = \"\"\"
John Doe - Backend Engineer

EXPERIENCE
Senior Backend Engineer at TechCorp
Built scalable microservices using Python, FastAPI, and PostgreSQL. 
Designed high-throughput vector search pipelines.

SKILLS
Python, FastAPI, SQL, Docker, Kubernetes
\"\"\"

RESUME_ML = \"\"\"
Jane Smith - Machine Learning Engineer

EXPERIENCE
ML Researcher at AI Labs
Trained large language models using PyTorch.
Implemented retrieval augmented generation (RAG) using FAISS and HuggingFace.

SKILLS
Python, PyTorch, Machine Learning, NLP, FAISS
\"\"\"

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
""",

    "tests/integration/test_end_to_end.py": """import pytest
from shared.mocks.mock_parser import MockParser, MockCleaner, MockSectionParser, MockChunker
from shared.mocks.mock_embedder import MockEmbedder
from shared.mocks.mock_vectordb import MockVectorDB
from shared.mocks.mock_metadata_store import MockMetadataStore
from shared.pipelines.ingestion_pipeline import IngestionPipeline
from shared.pipelines.retrieval_pipeline import RetrievalPipeline
from shared.pipelines.ranking_pipeline import CandidateAggregator, RankingPipeline
from shared.schemas.ingestion import IngestionRequest, ProcessingStatus
from shared.schemas.retrieval import RetrievalQuery
from tests.fixtures.synthetic_data import RESUME_BACKEND, RESUME_ML, CANDIDATE_BACKEND, CANDIDATE_ML

@pytest.fixture
def infrastructure():
    vectordb = MockVectorDB()
    meta_store = MockMetadataStore()
    embedder = MockEmbedder(dimensions=384)
    
    # Save candidate metadata upfront
    meta_store.save_candidate(CANDIDATE_BACKEND)
    meta_store.save_candidate(CANDIDATE_ML)
    
    ingestion = IngestionPipeline(
        parser=MockParser(),
        cleaner=MockCleaner(),
        section_parser=MockSectionParser(),
        chunker=MockChunker(),
        embedder=embedder,
        vectordb=vectordb,
        metadata_store=meta_store
    )
    
    retriever = RetrievalPipeline(
        embedder=embedder,
        vectordb=vectordb,
        metadata_store=meta_store
    )
    
    aggregator = CandidateAggregator(metadata_store=meta_store)
    ranker = RankingPipeline()
    
    return ingestion, retriever, aggregator, ranker, vectordb, meta_store

def test_end_to_end_orchestration(infrastructure):
    ingestion, retriever, aggregator, ranker, vectordb, meta_store = infrastructure
    
    # 1. Ingest Candidates
    res_backend = ingestion.ingest(IngestionRequest(
        candidate_id="cand_backend_001",
        file_path=RESUME_BACKEND  # Passing raw text as path for the mock
    ))
    res_ml = ingestion.ingest(IngestionRequest(
        candidate_id="cand_ml_002",
        file_path=RESUME_ML
    ))
    
    assert res_backend.status == ProcessingStatus.COMPLETED
    assert res_ml.status == ProcessingStatus.COMPLETED
    assert res_backend.chunks_indexed > 0
    
    # 2. Retrieval Validation
    # Query tailored for ML
    query = RetrievalQuery(query_text="Machine Learning PyTorch NLP", top_k=5, trace_id="trace_ml_query")
    retrieval_result = retriever.retrieve(query)
    
    assert len(retrieval_result.results) > 0
    # The top returned chunks should contain ML terms, and belong to cand_ml_002
    
    # 3. Candidate Aggregation
    aggregated = aggregator.aggregate(retrieval_result.results)
    assert len(aggregated) > 0
    
    # 4. Ranking Validation
    ranking_result = ranker.rank(aggregated, job_description="Looking for an ML expert")
    
    assert len(ranking_result.ranked_candidates) > 0
    top_candidate = ranking_result.ranked_candidates[0]
    
    # Since query was ML-focused, the ML candidate should win
    assert top_candidate.candidate.candidate_id == "cand_ml_002"
    
    # 5. Explainability Validation
    score = top_candidate.score
    assert score.final_score > 0
    assert len(score.explainability_log) > 0
    
    # 6. Metadata Lineage Verification
    first_chunk = top_candidate.supporting_chunks[0].chunk
    assert first_chunk.metadata.candidate_id == "cand_ml_002"
    assert first_chunk.metadata.document_id is not None
    assert first_chunk.metadata.trace_id is None # was not set at chunk level, but at request
    assert first_chunk.metadata.section_type.value in ["EXPERIENCE", "SKILLS", "UNKNOWN"]
"""
}

for path_str, content in files_content.items():
    full_path = base_dir / path_str
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print(f"Successfully generated {len(files_content)} test files.")
