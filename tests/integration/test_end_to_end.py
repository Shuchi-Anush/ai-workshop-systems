import pytest
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
