# Goal Description
Transform the AI Resume Screening frontend from an ML-centric observability dashboard into a polished, recruiter-first enterprise SaaS platform. This involves completely restructuring the Streamlit frontend architecture with a robust service layer, centralized state management, typed models, and clean UI components, while leaving the existing FastAPI backend and AI pipelines completely untouched. Advanced engineering diagnostics will be sandboxed in a hidden "Technical Insights" page.

## Open Questions
> [!IMPORTANT]  
> - **Authentication/Multi-Tenancy:** This plan assumes a single-user local deployment (per the existing workshop constraints). Multi-tenant session state is currently isolated per browser tab via Streamlit. Is this sufficient?
> - **File Upload Constraints:** The current backend has specific endpoints for evaluation but may lack full CRUD endpoints for resume PDFs in a session. We will mock the "Upload" state in the frontend if the backend doesn't explicitly persist raw PDFs, focusing primarily on the AI evaluation lifecycle.

## Proposed Changes

We will introduce a layered architecture within `apps/resume-analyzer/src/apps/resume_analyzer/frontend/` with the following structure:
```
frontend/
├── app.py (Entry point replacing dashboard.py)
├── config/
│   ├── theme.py (CSS injected styles)
│   └── settings.py
├── models/
│   └── domain.py (CandidateProfile, MatchTier, etc.)
├── services/
│   ├── api_client.py (Core HTTP wrapper)
│   ├── ranking_service.py (Adapter for AI evaluation)
│   └── state_manager.py (Centralized Session State)
├── components/
│   ├── candidate_card.py
│   ├── workflow_wizard.py
│   └── layout.py
└── pages/
    ├── 01_Dashboard.py
    ├── 02_New_Screening.py
    ├── 03_Candidates.py
    ├── 04_AI_Assistant.py
    ├── 05_Reports.py
    └── 99_Technical_Insights.py (Hidden)
```

### [Frontend Core]
#### [NEW] [app.py](file:///d:/ai-workshop-systems/apps/resume-analyzer/src/apps/resume_analyzer/frontend/app.py)
The new entry point. Initializes state, applies global CSS themes, and configures multi-page routing. Replaces the monolithic `dashboard.py`.

#### [DELETE] [dashboard.py](file:///d:/ai-workshop-systems/apps/resume-analyzer/src/apps/resume_analyzer/frontend/dashboard.py)
The legacy ML observability dashboard.

### [Models & Configuration]
#### [NEW] [models/domain.py](file:///d:/ai-workshop-systems/apps/resume-analyzer/src/apps/resume_analyzer/frontend/models/domain.py)
Dataclasses and Enums representing recruiter abstractions: `CandidateCard`, `CandidateProfile`, `ScreeningSession`, `MatchTier` (e.g., "Highly Recommended", "Needs Review").

#### [NEW] [config/theme.py](file:///d:/ai-workshop-systems/apps/resume-analyzer/src/apps/resume_analyzer/frontend/config/theme.py)
Custom CSS injection to make Streamlit feel like an enterprise SaaS platform (hiding default paddings, styling cards, standardizing typography).

### [Service Layer]
#### [NEW] [services/api_client.py](file:///d:/ai-workshop-systems/apps/resume-analyzer/src/apps/resume_analyzer/frontend/services/api_client.py)
Base wrapper around `requests` targeting the existing FastAPI backend (`http://127.0.0.1:8081`). Includes safe error handling and timeout configurations.

#### [NEW] [services/ranking_service.py](file:///d:/ai-workshop-systems/apps/resume-analyzer/src/apps/resume_analyzer/frontend/services/ranking_service.py)
Translates backend responses. Maps raw `rrf_score` into a 0-100 `Match Score %`, extracts adversarial penalties into recruiter-friendly "Flags", and abstracts away Dense/Sparse diagnostic logic.

#### [NEW] [services/state_manager.py](file:///d:/ai-workshop-systems/apps/resume-analyzer/src/apps/resume_analyzer/frontend/services/state_manager.py)
Singleton-patterned helper to manage `st.session_state` consistently. Tracks `current_session_id`, `shortlisted_candidates`, and `chat_history` across pages.

### [UI Components]
#### [NEW] [components/candidate_card.py](file:///d:/ai-workshop-systems/apps/resume-analyzer/src/apps/resume_analyzer/frontend/components/candidate_card.py)
Reusable UI for rendering candidates with progress bars for match score, skill chips, and a "Shortlist" button.

#### [NEW] [components/layout.py](file:///d:/ai-workshop-systems/apps/resume-analyzer/src/apps/resume_analyzer/frontend/components/layout.py)
Common headers, footers, and navigation sidebar logic for consistent SaaS branding.

### [Pages]
#### [NEW] [pages/01_Dashboard.py](file:///d:/ai-workshop-systems/apps/resume-analyzer/src/apps/resume_analyzer/frontend/pages/01_Dashboard.py)
High-level metrics: Active screening sessions, total candidates processed, recent shortlists.

#### [NEW] [pages/02_New_Screening.py](file:///d:/ai-workshop-systems/apps/resume-analyzer/src/apps/resume_analyzer/frontend/pages/02_New_Screening.py)
Step-by-step wizard to define a Job Description and trigger the backend `/api/v1/evaluate` endpoint.

#### [NEW] [pages/03_Candidates.py](file:///d:/ai-workshop-systems/apps/resume-analyzer/src/apps/resume_analyzer/frontend/pages/03_Candidates.py)
Main workspace. Renders `candidate_card` instances based on AI evaluation results, allows drilling down into profiles, and managing the shortlist.

#### [NEW] [pages/04_AI_Assistant.py](file:///d:/ai-workshop-systems/apps/resume-analyzer/src/apps/resume_analyzer/frontend/pages/04_AI_Assistant.py)
Chat interface for querying the backend about shortlisted candidates (RAG workflow).

#### [NEW] [pages/99_Technical_Insights.py](file:///d:/ai-workshop-systems/apps/resume-analyzer/src/apps/resume_analyzer/frontend/pages/99_Technical_Insights.py)
The sandboxed engineering view. Restores the "Attack Simulator", BM25 metrics, latency tracing, and raw Vector DB stats.

## Verification Plan

### Automated Tests
- Static type checking across the new frontend directory using `uv run mypy`.
- Validation of `py_compile` across all new Python files.

### Manual Verification
- Boot the new `app.py` via Streamlit.
- Verify the side navigation renders the 5 recruiter pages and the hidden insights page.
- Execute a "New Screening" and confirm the backend correctly evaluates the job description.
- Confirm BM25 and Dense metrics are strictly hidden from the Candidate presentation, replaced by an aggregated "Match Score %".
- Verify state persistence by navigating between "Candidates" and "Dashboard" without losing evaluation results.
