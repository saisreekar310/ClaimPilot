# ClaimPilot MVP Architecture

## 1. System Architecture

ClaimPilot is a modular monolith for preparing an explainable pre-survey assessment of a motor insurance claim. It runs locally as two Python processes:

- **FastAPI backend**: owns the claim workflow, agent orchestration, document and image processing, RAG retrieval, persistence, and API.
- **Streamlit frontend**: provides the claims employee/surveyor workspace and calls the backend over HTTP.
- **SQLite**: stores claim records, extracted results, evidence references, workflow state, and human decisions.
- **Local file storage**: stores uploaded policies, documents, photographs, estimates, and generated reports under `data/`.
- **Vector store**: stores embeddings for policy and claim-document chunks. It may be a local persistent vector database suitable for a hackathon, such as Chroma or FAISS with persisted metadata.
- **External AI providers**: configurable LLM and vision model APIs. Mock adapters are used when credentials are unavailable or for a deterministic demo.

The backend is a single deployable application with internal modules rather than separate services. A claim analysis is started through the API, executed by the orchestrator, persisted after each stage, and exposed to the frontend for review. Long-running work is represented as a background task in the backend; a production queue is out of scope for the MVP.

```text
Streamlit UI
    |
    | HTTP/JSON and file upload
    v
FastAPI modular monolith
    |-- Claim workflow and API
    |-- Orchestrator and agents
    |-- Document/image processing
    |-- RAG retrieval
    |-- Mock/model adapters
    |-- SQLite repository
    |-- Local file storage
    |
    |-- SQLite database
    |-- Local vector store
    |-- Configurable LLM/vision provider
```

The system is advisory. It must not reject a claim, approve a final settlement, declare fraud, or make a legally binding coverage decision. All such decisions remain with an authorized surveyor or insurer employee.

## 2. Directory Structure

The following structure matches the existing repository and keeps the MVP easy to run from VS Code:

```text
ClaimPilot/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Environment-backed settings
│   ├── api/                    # HTTP routes and request/response schemas
│   ├── domain/                 # Claim, workflow, evidence, and decision models
│   ├── services/               # Use cases: claims, analysis, reports, files
│   ├── agents/                 # Orchestrator and individual agent modules
│   ├── processing/             # PDF/text extraction and image preparation
│   ├── rag/                    # Chunking, embeddings, indexing, retrieval
│   ├── repositories/           # SQLite and vector-store persistence adapters
│   ├── providers/              # LLM, vision, embeddings, and mock adapters
│   └── prompts/                # Versioned prompt templates and output contracts
├── frontend/
│   └── streamlit_app.py        # Streamlit surveyor workspace
├── data/
│   ├── uploads/                # Original demo and user-uploaded files
│   ├── processed/              # Extracted text, thumbnails, and artifacts
│   ├── reports/                # Generated pre-survey reports
│   ├── vectorstore/            # Persisted local vector index
│   └── claimpilot.db           # SQLite database created at runtime
├── docs/
│   ├── product-spec.md
│   └── architecture.md
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/               # Deterministic mock claims and files
└── requirements.txt
```

The exact Python module names can change during implementation, but the ownership boundaries should remain. No microservice, message broker, or cloud deployment is required for the MVP.

## 3. Backend Architecture

The backend uses layered modules inside one process:

1. **API layer** validates HTTP input, handles uploads, returns workflow status, and maps domain errors to HTTP responses.
2. **Application/service layer** coordinates use cases such as creating a claim, starting analysis, retrieving a report, and recording a surveyor action.
3. **Domain layer** defines claim lifecycle states, agent result contracts, evidence references, triage routes, anomaly levels, and allowed human actions.
4. **Agent layer** performs bounded analysis through a common result format. Agents do not directly own HTTP concerns.
5. **Processing and RAG layers** turn uploaded source files into text, image inputs, searchable chunks, and evidence references.
6. **Repository layer** hides SQLite and vector-store details from services and agents.
7. **Provider layer** isolates model APIs. A mock provider implements the same contract as a real LLM, vision, or embedding provider.

Each analysis stage writes its result and status before the next stage begins. This makes partial failures visible and allows a failed claim to be retried without losing uploaded evidence.

## 4. Frontend Architecture

Streamlit is a thin operator console, not a second business-logic implementation. It should provide:

- A claim list with status, recommended route, and anomaly/review level.
- A claim intake form for accident information and file uploads.
- A claim detail view with claim summary, document status, damage assessment, estimate analysis, anomaly analysis, triage, evidence, confidence, and source references.
- Progress indicators for each analysis stage and clear error/retry states.
- A surveyor decision control for **Approve**, **Request more information**, or **Physical inspection**.
- An audit-visible distinction between AI recommendations and the surveyor's final action.

The frontend calls the FastAPI endpoints and refreshes analysis status. It may render tables, images, confidence indicators, and report sections, but triage rules and authorization constraints remain in the backend.

## 5. Agent Architecture

The orchestrator runs the following bounded agents in a defined workflow:

- **Policy Agent**: extracts policy number, vehicle information, IDV, coverage, deductible, add-ons, exclusions, and relevant conditions. Each extracted item should include source evidence where available.
- **Document Agent**: identifies received and missing required claim documents and extracts relevant fields with confidence.
- **Damage Agent**: sends vehicle photographs to a vision provider or mock adapter and returns vehicle, damaged parts, severity, and confidence. Every result is labeled an AI assessment, not a definitive surveyor conclusion.
- **Estimate Agent**: extracts the garage estimate, creates an AI estimated range, compares it with the estimate, and records variance and supporting reasons.
- **Fraud/Anomaly Agent**: finds suspicious inconsistencies without declaring fraud. It returns **Low concern**, **Review recommended**, or **Investigation recommended**, plus reasons and evidence.
- **Triage Agent**: combines policy, document, damage, estimate, and anomaly results into an advisory **Fast-track**, **Remote survey**, or **Physical survey** recommendation with reason and confidence.
- **Orchestrator Agent**: coordinates dependencies, persists stage results, passes structured outputs to later agents, and assembles the pre-survey report.

Agents should return structured results with at least `status`, `confidence`, `findings`, `evidence`, `warnings`, and `model_metadata`. The orchestrator must treat low-confidence or missing inputs as uncertainty, not as a positive conclusion.

## 6. Data Flow

1. A claims employee creates a claim with accident information and simulated policy/vehicle context.
2. Files are uploaded, assigned a claim and document type, stored locally, and registered in SQLite.
3. The backend validates file type and size, extracts text or image metadata, and records processing errors without deleting the original.
4. Policy and text-bearing documents are chunked, embedded, and indexed with claim/document/source metadata.
5. The orchestrator runs the policy and document stages, then the damage and estimate stages, followed by anomaly analysis and triage.
6. Agents retrieve only relevant claim-scoped chunks and return findings with evidence references.
7. Results are persisted after each stage and assembled into a pre-survey claim report.
8. The Streamlit UI displays the report, evidence, uncertainty, and advisory route.
9. A surveyor records one final workflow action: approve, request more information, or physical inspection.
10. The decision and optional note are stored with timestamp and actor label; the AI recommendation remains unchanged for auditability.

## 7. Claim Lifecycle

The MVP uses these states:

`Draft` -> `Submitted` -> `Analyzing` -> `Ready for review` -> `Decision recorded`

Additional states are `Needs information`, `Analysis failed`, and `Archived`.

- **Draft**: basic claim data exists but submission is incomplete.
- **Submitted**: required intake fields and available files were submitted for analysis.
- **Analyzing**: one or more agent stages are running.
- **Ready for review**: a report and triage recommendation are available, even if warnings exist.
- **Needs information**: the surveyor requests missing or clarifying information.
- **Decision recorded**: the surveyor records Approve, Request more information, or Physical inspection. A request for more information may return the claim to `Needs information`.
- **Analysis failed**: a technical failure prevents a complete report; the claim remains reviewable with an explicit failure reason where possible.
- **Archived**: demo or completed claim is retained but no longer active.

State transitions are enforced by the backend. No AI agent may transition a claim to a final human decision state.

## 8. Database Entities

SQLite stores the minimum data needed for workflow, explainability, and the demo:

- **Claim**: ID, claim type, reported loss, accident description, status, timestamps, policy reference, and final surveyor action.
- **Policy**: policy number, vehicle details, IDV, coverage, deductible, add-ons, exclusions, and source document reference.
- **Document**: claim ID, category, original filename, storage path, MIME type, upload timestamp, processing status, and extraction confidence.
- **Photo**: claim ID, storage path, metadata, processing status, and image hash where available.
- **Estimate**: claim ID, garage information, extracted total, line items, source document reference, and extraction confidence.
- **AgentRun**: claim ID, agent name, status, input/output metadata, model/provider, confidence, error message, start time, and completion time.
- **Finding**: claim ID and agent run, category, text, severity, confidence, and evidence references.
- **Evidence**: source document/photo ID, page or region reference, quoted/extracted text or image description, and retrieval score where applicable.
- **TriageRecommendation**: route, reason, confidence, anomaly level, and agent run reference.
- **SurveyorDecision**: claim ID, action, note, actor label, timestamp, and optional linked request for information.
- **AuditEvent**: claim ID, event type, actor, timestamp, and structured event details.

SQLite foreign keys should preserve claim ownership for all records. Files and vector entries are referenced by IDs and paths rather than embedded in database blobs.

## 9. API Endpoints

The API is versioned under `/api/v1`:

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Report backend readiness and configured provider mode. |
| `POST` | `/api/v1/claims` | Create a claim from intake data. |
| `GET` | `/api/v1/claims` | List claims with status and triage summary. |
| `GET` | `/api/v1/claims/{claim_id}` | Return claim detail and lifecycle status. |
| `POST` | `/api/v1/claims/{claim_id}/documents` | Upload a policy, vehicle, accident, or estimate document. |
| `POST` | `/api/v1/claims/{claim_id}/photos` | Upload vehicle damage photographs. |
| `POST` | `/api/v1/claims/{claim_id}/analyze` | Start or retry the orchestrated analysis. |
| `GET` | `/api/v1/claims/{claim_id}/analysis` | Return stage statuses, findings, warnings, and evidence. |
| `GET` | `/api/v1/claims/{claim_id}/report` | Return the assembled pre-survey claim report. |
| `GET` | `/api/v1/claims/{claim_id}/files/{file_id}` | Retrieve an authorized source file or thumbnail. |
| `POST` | `/api/v1/claims/{claim_id}/decision` | Record Approve, Request more information, or Physical inspection. |
| `POST` | `/api/v1/demo/seed` | Load deterministic Claim A and Claim B fixtures for the demo. |

Responses should use stable JSON contracts and include identifiers, status, confidence, evidence, and warnings where relevant. The decision endpoint validates the finite action set and records the human actor; it does not allow an AI-generated action to masquerade as a surveyor decision.

## 10. RAG Pipeline

RAG is used primarily for explainable policy and document lookup:

1. Extract text from policy and claim documents with page boundaries preserved.
2. Normalize whitespace while retaining the original source path, document ID, page number, and document category.
3. Split text into modest overlapping chunks that preserve headings and nearby context.
4. Generate embeddings through the configured embedding provider or a deterministic mock provider.
5. Persist vectors in the local vector store with claim ID and source metadata.
6. For an agent question, retrieve top relevant chunks scoped to the current claim and document categories.
7. Pass retrieved context to the agent with source identifiers and instruct the model to distinguish evidence from inference.
8. Store the selected source chunks and retrieval metadata as evidence on the agent result.

If embeddings or the vector store are unavailable, the MVP may use a clearly labeled lexical fallback over extracted text. The fallback must not silently claim vector retrieval. Retrieved content is supporting evidence; it is not itself a coverage decision.

## 11. Document Processing Pipeline

For each uploaded document:

1. Validate extension, MIME type, size, and claim ownership.
2. Store the immutable original under the claim's data directory.
3. Classify or confirm its category: policy, vehicle document, accident document, garage estimate, previous claim, or other.
4. Extract text and page structure using PyMuPDF or an equivalent local PDF parser. Image-only pages may be marked as requiring OCR; OCR is optional for the MVP and must be reported when unavailable.
5. Extract candidate fields through the Document Agent or Policy Agent.
6. Validate obvious fields and attach confidence plus page-level evidence.
7. Index eligible text in the RAG store.
8. Persist processing status, warnings, and errors. A malformed optional document should not erase or invalidate the claim.

The original file remains available for human review. Extracted values are not treated as authoritative when confidence is low or sources conflict.

## 12. Computer Vision Pipeline

1. Validate and store uploaded vehicle photographs, preserving the original.
2. Create display thumbnails and basic metadata without changing the evidence source.
3. Send authorized image inputs to the configured vision provider or mock adapter.
4. Ask for vehicle identification, visible damaged components, severity, confidence, and uncertainty in a structured response.
5. Normalize component names and aggregate multiple photographs while retaining per-image evidence.
6. Compare identified components and severity with the garage estimate through the Estimate Agent.
7. Store image references, provider metadata, findings, confidence, and warnings in the report.

Vision results must be displayed as AI assessments. They are indicative evidence for triage and never a definitive surveyor conclusion.

## 13. Triage Logic

The Triage Agent combines deterministic checks with agent findings. The exact thresholds should be configuration, but the route meaning is fixed:

- **Fast-track**: low-complexity claim, complete and consistent documents, low apparent damage, estimate within the AI range, and low anomaly concern.
- **Remote survey**: information is broadly consistent and damage appears assessable from documents/photos, but a remote human review remains appropriate or some uncertainty exists.
- **Physical survey**: material document gaps, significant or uncertain damage, estimate/damage mismatch, conflicting evidence, or anomaly level of review recommended/investigation recommended.

The triage result includes route, reason, confidence, contributing findings, and warnings. High anomaly concern or low confidence must not be converted into a fraud declaration. The route is advisory and must be reviewed by a surveyor.

The deterministic portion should make the demo repeatable: Claim A is seeded with complete, consistent low-complexity evidence and should recommend Remote survey or Fast-track; Claim B is seeded with high-complexity evidence and anomalies and should recommend Physical survey.

## 14. Human-in-the-Loop Flow

1. The surveyor opens a `Ready for review` claim.
2. The UI presents the structured report, source evidence, confidence, warnings, missing documents, and AI labels.
3. The surveyor can inspect original documents/photos and compare the estimate with the damage findings.
4. The surveyor selects **Approve**, **Request more information**, or **Physical inspection**, with an optional note.
5. The backend validates and records the action, actor, timestamp, and report version reviewed.
6. A request for information records what is missing and moves the claim to `Needs information`; it does not imply rejection.
7. The final action is shown separately from the AI recommendation in subsequent views.

No agent endpoint or background task can submit a final surveyor action.

## 15. Error Handling

- **Input errors**: return `400` or `422` with field-level details; do not start analysis.
- **Missing required evidence**: keep the claim analyzable where possible, mark the document status and warning, and allow triage to recommend more review.
- **Unsupported/corrupt file**: retain an error record, reject that file with a clear message, and preserve other claim evidence.
- **Provider timeout/rate limit**: retry a small configured number of times for safe idempotent calls, then use a mock provider only when explicitly configured; otherwise mark that stage failed.
- **Malformed model output**: validate against the agent result contract, record the raw failure metadata safely, and mark the stage failed or uncertain rather than inventing values.
- **RAG unavailable**: use the labeled lexical fallback or mark evidence retrieval unavailable; never imply source-backed reasoning when no source was retrieved.
- **Partial workflow failure**: persist completed stages, expose the failed stage and reason, and allow analysis retry from the failed stage.
- **Database or storage failure**: return a server error, log a correlation ID, and avoid reporting a successful analysis that was not persisted.
- **Human decision conflict**: reject invalid or duplicate transitions with a clear domain error while preserving the audit trail.

UI errors should identify the affected stage and next action without exposing API keys, stack traces, or sensitive provider responses.

## 16. Configuration and Environment Variables

Configuration is loaded from environment variables, with a local `.env` file supported but excluded from version control:

| Variable | Purpose | MVP default |
|---|---|---|
| `CLAIMPILOT_ENV` | Runtime profile | `development` |
| `CLAIMPILOT_DATABASE_URL` | SQLite location | `sqlite:///data/claimpilot.db` |
| `CLAIMPILOT_DATA_DIR` | Upload and artifact root | `data` |
| `CLAIMPILOT_VECTOR_DIR` | Local vector-store location | `data/vectorstore` |
| `CLAIMPILOT_LLM_PROVIDER` | LLM adapter selection | `mock` |
| `CLAIMPILOT_LLM_MODEL` | LLM model name | provider-specific |
| `CLAIMPILOT_LLM_API_KEY` | Optional LLM credential | unset |
| `CLAIMPILOT_VISION_PROVIDER` | Vision adapter selection | `mock` |
| `CLAIMPILOT_VISION_MODEL` | Vision model name | provider-specific |
| `CLAIMPILOT_VISION_API_KEY` | Optional vision credential | unset |
| `CLAIMPILOT_EMBEDDING_PROVIDER` | Embedding adapter selection | `mock` or local |
| `CLAIMPILOT_EMBEDDING_MODEL` | Embedding model name | provider-specific |
| `CLAIMPILOT_BACKEND_URL` | URL used by Streamlit | `http://localhost:8000` |
| `CLAIMPILOT_MAX_UPLOAD_MB` | Upload size limit | small local-demo limit |
| `CLAIMPILOT_ALLOW_MOCKS` | Permit deterministic mock providers | `true` |

The application must start with mock providers and sample data so judges can run it locally without real insurance or AI integrations. Provider adapters must not be hard-coded to a real insurer.

## 17. Testing Strategy

Testing is focused on the high-risk contracts and the two demo paths:

- **Unit tests**: claim state transitions, triage rules, confidence/warning propagation, anomaly wording, document classification, estimate variance, API schema validation, and agent output validation.
- **Agent contract tests**: run every agent against deterministic mock inputs and verify required fields, evidence references, confidence, and prohibited conclusions such as declaring fraud.
- **RAG tests**: verify chunk metadata, claim-scoped retrieval, page/source evidence, and labeled fallback behavior.
- **Processing tests**: parse fixture PDFs, handle corrupt/unsupported files, preserve page references, validate images, and produce expected thumbnails/metadata.
- **API integration tests**: create a claim, upload fixture files, start analysis, poll status, retrieve the report, and record each allowed surveyor action.
- **End-to-end demo tests**: seed Claim A and Claim B and verify that Claim A produces Remote survey/Fast-track and Claim B produces Physical survey, subject to the documented deterministic fixture rules.
- **Failure tests**: provider timeout, malformed model response, missing documents, vector-store failure, partial agent failure, retry, and invalid human decision transition.
- **Frontend smoke test**: start the local backend with mocks, open the Streamlit workspace, load both demo claims, inspect the report, and submit a surveyor action.

The MVP should run tests without network access by default. Real providers are optional integration tests and must be isolated from deterministic CI tests. Test fixtures must use simulated insurance data only.

## Assumptions

- The hackathon demo is single-tenant and uses one local operator role; full authentication and authorization are out of scope, but actor identity is still recorded as a field.
- SQLite and local filesystem storage are acceptable for a single-machine demonstration; concurrent multi-user production deployment is out of scope.
- Uploads are limited to common PDFs, images, and text-bearing claim files. OCR is optional and its absence is surfaced as uncertainty.
- The product specification's "vector database + embeddings" is satisfied by a local persistent vector store with a lexical fallback for offline operation.
- Mock providers return deterministic outputs for the two seeded demo claims, while real provider adapters remain configurable and unrequired.
- "Approve" is modeled as a surveyor workflow action, not an autonomous final settlement approval or legally binding coverage decision.
- The product specification does not define numeric confidence or variance thresholds, so those thresholds are configuration and must be documented with the demo fixtures when implemented.