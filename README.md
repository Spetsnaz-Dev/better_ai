# InfraTask — AI-Assisted Task Classification System

Welcome to my submission for the Senior Software Engineer (Infrastructure) assessment. 

InfraTask is a minimal, robust task management system where users create tasks, the backend validates the input strictly, an LLM classifies the task category, and the result is safely stored in a relational database.

My approach to this assessment was to focus heavily on **production-readiness over feature richness**. The codebase is designed to be observable, testable, and deeply resilient to change, strictly adhering to the mandated architectural boundaries.

---

## 🏗️ Evaluation Criteria Addressed

Below I have outlined exactly how this project satisfies the assessment's core evaluation criteria:

### 1. Structure: Clear boundaries and logical organization
I implemented a strict **Service Layer Pattern** to ensure separation of concerns. 
- **Routes** (`routes/routes.py`): HTTP endpoint definitions only. They receive requests, delegate to validators and services, and return responses. Zero business logic.
- **Services** (`services/`): All business logic is isolated here. DB operations live exclusively in `task_service.py`, while LLM operations live in `ai_service.py`.
- **Data Access** (`db/models.py`): SQLAlchemy ORM models.
- **Cross-cutting** (`utils/`): Shared constants, formatting, and standardized JSON responses.

### 2. Simplicity: Readable, predictable code
I chose "simple over clever." 
- The App Factory pattern (`app/__init__.py`) makes the application lifecycle highly predictable and easy to test.
- Configuration is class-based and environment-driven.
- Control flow is straightforward: Validation -> AI Call -> Database Write -> Response.

### 3. Correctness: Prevents invalid states
The application strictly enforces data integrity:
- Tasks cannot be saved without a classification.
- If the AI fails, quota is exceeded, or it returns hallucinated data, the system gracefully traps the error and applies a safe fallback (`OTHER`).
- SQLAlchemy sessions are wrapped in `try/except` blocks with explicit `db.session.rollback()` calls to prevent corrupted transaction scopes.

### 4. Interface Safety: Guards against misuse
I utilized **Pydantic** (`schemas/input.py`) as an impenetrable shield at the API boundary. 
- Incoming JSON is strictly validated against `TaskCreateInput` before it ever reaches the service layer.
- Missing fields, empty strings, and type mismatches instantly result in a standardized `400 Bad Request` with structured error details, rejecting bad data at the door.

### 5. Change Resilience: Modularity
The codebase is designed so that new features don't cause widespread impact.
- **Adding a new category:** Simply add it to `ALLOWED_CATEGORIES` in `utils/constants.py`. No route or DB changes required.
- **Swapping AI providers:** Only `ai_service.py` needs to be touched. The `task_service` is completely agnostic to *how* classification happens.
- **Changing Databases:** Swap the `DATABASE_URL` environment variable. Zero code changes required.

### 6. Verification: Automated tests
I wrote a comprehensive `pytest` suite (`tests/test_app.py`) proving the behavior remains correct.
- Uses an in-memory SQLite database (`TestConfig`) for fast, isolated execution.
- Achieves excellent coverage across the service layer and API boundaries.
- The AI service is mocked during tests using `unittest.mock.patch` to ensure repeatable, deterministic tests without hitting external rate limits.

### 7. Observability: Failures are visible and diagnosable
I implemented a custom **Structured JSON Logging** middleware (`logging_config.py`).
- Every single log entry (start, finish, errors, AI fallbacks) is emitted as JSON containing `timestamp`, `level`, `module`, `message`, and `metadata`.
- This ensures that in a real infrastructure environment (like ELK or Datadog), user activity and system failures are easily searchable and trackable.
- Production systems should never use `print()`; I rely entirely on structured `logging`.

## 🎥 Walkthrough (10–15 min)

This section provides a deep dive into the core decisions, AI workflows, risk management, and extensibility of the architecture.

### 1. Structure (Service Layer Architecture)
The application strictly enforces a **Service Layer Pattern** separating HTTP delivery from business logic and data access.
- **API Boundary (`routes/`)**: Flask routes strictly handle HTTP parsing and sending responses. They do **not** contain business logic.
- **Validation Shield (`schemas/`)**: Pydantic strictly types and validates incoming payloads. Invalid data (e.g., empty tasks, missing fields) results in immediate `400 Bad Request` responses.
- **Business Logic (`services/`)**: The core functionality.
  - `task_service.py` handles database interactions and tying the AI step to model persistence.
  - `ai_service.py` encapsulates solely the LLM network call and prompt management.
- **Data Access (`db/`)**: SQLAlchemy ORM models define the schema clearly.
- **Shared Utilities (`utils/`)**: Constants (`ALLOWED_CATEGORIES`), standard response formatters.

This prevents the "fat controller" anti-pattern and guarantees testability.

### 2. AI Usage & Guidance
I treated the AI agent (both Copilot and prompt-driven generation) as a junior developer governed by strict architectural policies.
- **Guidance Rulebook (`AGENTS.md`)**: I provided explicit boundaries up-front: no direct DB access in routes, mandatory use of Pydantic for API layers, and a strictly defined folder hierarchy.
- **Iterative Refinement**: Code generated by the AI was deeply reviewed and refactored. For example, I noticed the AI initially hardcoded categories in the routes and db models; I directed it to refactor those into a single source of truth (`utils/constants.py`).
- **Mock Fallback Strategy**: To ensure the evaluator can run this locally without an OpenAI key, I asked the AI to build a primitive keyword-matcher fallback. This preserves the architectural flow (Service -> AI -> Service) without external dependency failures blocking the review.

### 3. Risks & Tradeoffs
No architecture is perfect; below are the conscious tradeoffs and infrastructural risks inherent in this MVP:

| Risk / Tradeoff | Impact | Mitigation / Future Approach |
|---|---|---|
| **Synchronous AI Calls** | Flask HTTP worker blocks while waiting for OpenAI's API. Under high load, this causes worker starvation and timeouts. | **Move to Async Workers**: Introduce a task queue (Celery/Redis) for background processing, returning an accepted task ID, then using WebSockets or polling for the final category. |
| **SQLite as Default** | SQLite struggles with heavy concurrent writes and locks the database. | **PostgreSQL Switch**: We utilized SQLAlchemy to abstract the DB. Transitioning to Postgres only requires updating the `DATABASE_URL` environment variable. |
| **LLM Hallucinations** | The AI might return an invalid category not defined in our DB schema, crashing the insert. | **Strict Output Parsers & Fallbacks**: The `ai_service` checks if the output matches `ALLOWED_CATEGORIES`. If it hallucinates or the API fails, it defaults to a safe `OTHER` category, ensuring the data is saved regardless of AI failure. |
| **API Rate Limiting** | Spamming the task creation endpoint could exhaust OpenAI quota or incur huge costs. | **API Gateway / Throttling**: Implement rate limiting middleware (e.g., `Flask-Limiter` or API Gateway) based on user IP or API keys. |

### 4. Extension Approach (Scaling Up)
This project is built to absorb changes with minimal friction:
- **Adding new Categories**: No core logic needs rewriting. Simply add the new category to the `ALLOWED_CATEGORIES` list in `utils/constants.py`. Pydantic and SQLAlchemy will automatically accept it.
- **Swapping LLMs (e.g., to Anthropic)**: Because the `task_service` only cares about receiving a string category, we simply rewrite the `ai_service.py` method to call Anthropic instead of OpenAI. The rest of the app is oblivious.
- **Adding Authentication**: The route structure makes it trivial to slap a `@jwt_required` decorator on the endpoints to enforce user identity before hitting the validation or service layers.
- **Multi-Tenant Logging**: The custom JSON logger (`logging_config.py`) currently records timestamps and messages. It can easily be extended to inject `request_id` or `user_id` into the JSON payload, making traces trivial to follow in tools like Datadog or ELK.

---

## 🚀 Running the Project Locally

### Prerequisites
- Python 3.11+
- Node.js (v18+)

### 1. Backend Setup
```bash
cd api
python -m venv venv

# Windows
.\venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

*(Optional)* To use real OpenAI classification instead of the mock, add your key to `api/.env`:
```
OPENAI_API_KEY=sk-your-key-here
```

Start the Flask server:
```bash
python run.py
```
*Backend runs on `http://localhost:5000`*

### 2. Frontend Setup
Open a new terminal:
```bash
cd frontend
npm install
npm run dev
```
*Frontend runs on `http://localhost:3000`*

### 3. Running the Tests
From the `api` directory (with your virtual environment active):
```bash
pytest tests/ -v
```

---

Thank you for your time reviewing this submission. I look forward to discussing the architectural decisions and extension approaches during the walkthrough!
