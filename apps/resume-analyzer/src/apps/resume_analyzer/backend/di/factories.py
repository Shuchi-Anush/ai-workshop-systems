from ai_contracts.interfaces.vectordb import IVectorDB
from ai_contracts.interfaces.storage import IMetadataStore
from ai_contracts.interfaces.embedder import IEmbedder
from ai_contracts.interfaces.parser import IParser
from ai_contracts.interfaces.cleaner import ICleaner
from ai_contracts.interfaces.chunker import ISectionParser, IChunker
from ai_contracts.interfaces.ranking import IRanker, ICandidateAggregator
from ai_contracts.interfaces.retriever import IRetriever

from apps.resume_analyzer.backend.di.container import get_container
from apps.resume_analyzer.backend.rag.vectordb import ChromaVectorDB
from apps.resume_analyzer.backend.rag.embedder import OllamaLocalEmbedder
from apps.resume_analyzer.backend.parser.pdf_parser import PyPDFParser
from apps.resume_analyzer.backend.parser.cleaner import SimpleCleaner
from apps.resume_analyzer.backend.rag.chunker import SimpleSectionParser, SimpleChunker
from apps.resume_analyzer.backend.ranking.ranking_pipeline import LLMRanker, SimpleCandidateAggregator
from apps.resume_analyzer.backend.pipelines.retrieval_pipeline import RetrievalPipeline

from apps.resume_analyzer.backend.pipelines.ingestion_pipeline import IngestionPipeline
from ai_contracts.interfaces.ingestion import IIngestionService

class InMemoryMetadataStore(IMetadataStore):
    def __init__(self):
        self.chunks = {}
        self.candidates = {}
        self.documents = {}
        
    def save_candidate(self, candidate):
        self.candidates[candidate.candidate_id] = candidate
        
    def get_candidate(self, candidate_id):
        return self.candidates.get(candidate_id)
        
    def save_chunks(self, chunks):
        for chunk in chunks:
            self.chunks[chunk.metadata.chunk_id] = chunk
            
    def get_chunks_by_ids(self, chunk_ids):
        return [self.chunks[cid] for cid in chunk_ids if cid in self.chunks]
        
    def get_chunks_by_candidate(self, candidate_id):
        return [chunk for chunk in self.chunks.values() if chunk.metadata.candidate_id == candidate_id]

def configure_infrastructure() -> None:
    """Wires the container with real implementations."""
    container = get_container()
    
    # Store
    container.register_singleton(IMetadataStore, InMemoryMetadataStore())
    
    # Models & DB
    container.register_singleton(IEmbedder, OllamaLocalEmbedder(model="nomic-embed-text"))
    container.register_singleton(IVectorDB, ChromaVectorDB(persist_directory="./chroma_db", collection_name="resumes"))
    
    # Parser
    container.register_singleton(IParser, PyPDFParser())
    container.register_singleton(ICleaner, SimpleCleaner())
    container.register_singleton(ISectionParser, SimpleSectionParser())
    container.register_singleton(IChunker, SimpleChunker())
    
    # Ranking
    container.register_singleton(ICandidateAggregator, SimpleCandidateAggregator())
    container.register_singleton(IRanker, LLMRanker(model="phi3:mini"))
    
    # Pipelines
    container.register_singleton(
        IIngestionService,
        IngestionPipeline(
            parser=container.resolve(IParser),
            cleaner=container.resolve(ICleaner),
            section_parser=container.resolve(ISectionParser),
            chunker=container.resolve(IChunker),
            embedder=container.resolve(IEmbedder),
            vectordb=container.resolve(IVectorDB),
            metadata_store=container.resolve(IMetadataStore)
        )
    )
    container.register_singleton(
        IRetriever,
        RetrievalPipeline(
            embedder=container.resolve(IEmbedder),
            vectordb=container.resolve(IVectorDB),
            metadata_store=container.resolve(IMetadataStore)
        )
    )

def configure_mock_infrastructure() -> None:
    """Wires the container with mock implementations for tests."""
    from ai_testing.mocks.mock_vectordb import MockVectorDB
    from mocks.mock_metadata_store import MockMetadataStore
    container = get_container()
    container.register_singleton(IVectorDB, MockVectorDB())
    container.register_singleton(IMetadataStore, MockMetadataStore())

