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

### 8. AI Guidance & Usage
I treated the AI agent as a junior developer working under strict instructions:
- **Guidance:** I created `AGENTS.md` (included in the repo) which acts as the strict "Rulebook" for the agent. It defines the folder structure, allowed libraries, and explicit boundary rules (e.g., "No direct DB access inside routes").
- **Usage & Review:** The generated code was critically reviewed. For instance, I iteratively guided the AI to refactor the structure to pull out a `utils/` directory to dry up constants, and enforced the use of Pydantic for stricter interface safety.

### 9. Communication: Tradeoffs and Weaknesses
Here are the conscious tradeoffs made during development:
| Decision | Rationale | Weakness / Future Improvement |
|---|---|---|
| **Sync vs Async AI Call** | The spec implied a standard request/response flow without Celery. | The HTTP request blocks while waiting for OpenAI. In production, this should be offloaded to a background queue (Celery/Redis) to prevent worker starvation. |
| **SQLite Default** | Enables zero-config local development and testing. | SQLite handles concurrency poorly. For staging/prod, swap to Postgres via the `DATABASE_URL` env var. |
| **Mock Fallback Logic** | Built a simple keyword matcher in `ai_service.py` when `OPENAI_API_KEY` is missing. | It's primitive, but it allows evaluators to run the app instantly without needing to provide their own funded API keys, while preserving the exact fallback architecture. |

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
