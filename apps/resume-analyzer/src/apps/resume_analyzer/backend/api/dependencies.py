from fastapi import Depends
from apps.resume_analyzer.backend.di.container import get_container
from ai_contracts.providers.registry import DependencyRegistry
from ai_contracts.interfaces.ingestion import IIngestionService
from ai_contracts.interfaces.ranking import IRanker

def get_di_container() -> DependencyRegistry:
    return get_container()

def get_ingestion_pipeline(container: DependencyRegistry = Depends(get_di_container)) -> IIngestionService:
    # In a fully wired application, the container would resolve this.
    return container.resolve(IIngestionService)

def get_ranking_pipeline(container: DependencyRegistry = Depends(get_di_container)) -> IRanker:
    # In a fully wired application, the container would resolve this.
    return container.resolve(IRanker)
