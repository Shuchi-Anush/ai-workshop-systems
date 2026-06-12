import os
import shutil
from pathlib import Path

repo_root = Path("d:/ai-workshop-systems")
app_pipelines = repo_root / "apps/resume-analyzer/src/apps/resume_analyzer/backend/pipelines"
app_di = repo_root / "apps/resume-analyzer/src/apps/resume_analyzer/backend/di"

app_pipelines.mkdir(parents=True, exist_ok=True)
(app_pipelines / "__init__.py").touch()
app_di.mkdir(parents=True, exist_ok=True)
(app_di / "__init__.py").touch()

# ----------------------------------------
# WAVE E3: Migrate Pipelines
# ----------------------------------------

# 1. Ingestion Pipeline
ingestion_src = repo_root / "shared/pipelines/ingestion_pipeline.py"
ingestion_dest = app_pipelines / "ingestion_pipeline.py"
if ingestion_src.exists():
    shutil.copy2(ingestion_src, ingestion_dest)
    content = ingestion_dest.read_text(encoding="utf-8")
    content = content.replace("from shared.schemas.ingestion import IngestionRequest, IngestionResult", 
                              "from apps.resume_analyzer.backend.schemas.ingestion import IngestionRequest, IngestionResult")
    content = content.replace("from .base import PipelineObservabilityMixin",
                              "from shared.pipelines.base import PipelineObservabilityMixin")
    ingestion_dest.write_text(content, encoding="utf-8")
    ingestion_src.write_text("from apps.resume_analyzer.backend.pipelines.ingestion_pipeline import IngestionPipeline\n", encoding="utf-8")

# 2. Ranking Pipeline
ranking_src = repo_root / "shared/pipelines/ranking_pipeline.py"
ranking_dest = app_pipelines / "ranking_pipeline.py"
if ranking_src.exists():
    shutil.copy2(ranking_src, ranking_dest)
    content = ranking_dest.read_text(encoding="utf-8")
    content = content.replace("from shared.schemas.ranking import RankedCandidate, RankingResult, CandidateScore, RankingBreakdown",
                              "from apps.resume_analyzer.backend.schemas.ranking import RankedCandidate, RankingResult, CandidateScore, RankingBreakdown")
    content = content.replace("from shared.schemas.domain import Candidate",
                              "from apps.resume_analyzer.backend.schemas.domain import Candidate")
    content = content.replace("from .base import PipelineObservabilityMixin",
                              "from shared.pipelines.base import PipelineObservabilityMixin")
    ranking_dest.write_text(content, encoding="utf-8")
    ranking_src.write_text("from apps.resume_analyzer.backend.pipelines.ranking_pipeline import CandidateAggregator, RankingPipeline\n", encoding="utf-8")

# ----------------------------------------
# WAVE E4: Migrate DI/Providers
# ----------------------------------------

# 1. Container
container_src = repo_root / "shared/providers/container.py"
container_dest = app_di / "container.py"
if container_src.exists():
    shutil.copy2(container_src, container_dest)
    content = container_dest.read_text(encoding="utf-8")
    content = content.replace("from .registry import DependencyRegistry", "from shared.providers.registry import DependencyRegistry")
    container_dest.write_text(content, encoding="utf-8")
    container_src.write_text("from apps.resume_analyzer.backend.di.container import global_container, get_container\n", encoding="utf-8")

# 2. Factories
factories_src = repo_root / "shared/providers/factories.py"
factories_dest = app_di / "factories.py"
if factories_src.exists():
    shutil.copy2(factories_src, factories_dest)
    content = factories_dest.read_text(encoding="utf-8")
    # imports from .container will implicitly work, but let's be absolute
    content = content.replace("from .container import get_container", "from apps.resume_analyzer.backend.di.container import get_container")
    factories_dest.write_text(content, encoding="utf-8")
    factories_src.write_text("from apps.resume_analyzer.backend.di.factories import configure_mock_infrastructure\n", encoding="utf-8")

print("Wave E3 & E4 script executed successfully.")
