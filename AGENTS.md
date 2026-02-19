# Senior Software Engineer (Infrastructure) Assessment

# AI Agent Implementation Guidelines

This document defines strict rules, architecture boundaries, and
implementation constraints.

The goal is NOT feature richness. The goal is correctness, structure,
safety, observability, and resilience to change.

AI must follow these rules strictly.

------------------------------------------------------------------------

# 1. PRODUCT DEFINITION

## Product Name

InfraTask -- AI-Assisted Task Classification System

## Core Idea

A minimal task management system where:

-   Users create tasks.
-   Backend validates input strictly.
-   Backend calls an LLM to classify task category.
-   Result is stored safely in a relational database.
-   System is observable, testable, and resilient.

No unnecessary features. No UI polish. No feature creep.

------------------------------------------------------------------------

# 2. TECH STACK (MANDATORY)

Backend: - Python 3.11+ - Flask (NOT FastAPI) - SQLAlchemy ORM -
Pydantic (for validation schemas) - PostgreSQL (default) - pytest
(for tests)

Frontend: - React (functional components only) - No Redux - No heavy UI
libraries - Axios for API calls

Infra: - Docker (multi-stage build) - docker-compose for local setup -
Structured logging - Environment-based config

------------------------------------------------------------------------

# 3. ARCHITECTURE RULES (CRITICAL)

Follow strict separation of concerns.

Project structure must be:

root/ │ ├── api/ │ ├── app/ │ │ ├── **init**.py │ │ ├── config.py │ │
├── db/ │ │ │ └── models.py │ │ ├── schemas/ │ │ │ ├── input.py │ │ │
└── output.py │ │ ├── routes/ │ │ │ └── routes.py │ │ ├── services/ │ │
│ ├── ai_service.py │ │ │ └── task_service.py │ │ ├── utils/ │ │ ├── errors.py │ │ └──
logging_config.py │ │ │ ├── tests/ │ ├── run.py │ └── requirements.txt │
├── frontend/ │ ├── docker-compose.yml ├── Dockerfile ├── README.md └──
AGENTS.md

STRICT RULES: - Routes must NOT contain business logic. - AI logic must
live only inside ai service file. - Database logic must live only inside
task service file. - No direct DB access inside routes. - No direct OpenAI
calls inside routes. - All input must go through Pydantic validation.

------------------------------------------------------------------------

# 4. DATABASE DESIGN

Table: tasks

Columns: - id (UUID, primary key) - title (string, required) - description (text, required) - category
(string, nullable initially) - status (enum: PENDING, PROCESSED) -
created_at (timestamp, default now)

Constraints: - title must not be empty - description must not be empty -
status default = PENDING

AI classification must update: - category - status = PROCESSED

------------------------------------------------------------------------

# 5. API CONTRACT

## POST /api/tasks

Request: { "title": "string", "description": "string" }

Response (201): { "id": "uuid", "title": "...", "description": "...",
"category": "...", "status": "PROCESSED", "created_at": "ISO8601" }

Validation failures return 400 with structured errors.

------------------------------------------------------------------------

## GET /api/tasks

Returns list of tasks.
Response (200)

------------------------------------------------------------------------

## GET /api/health

Returns: { "status": "ok" }

Used for Docker healthcheck(if we use docker).

------------------------------------------------------------------------

# 6. AI SERVICE RULES

Allowed categories: - WORK - PERSONAL - FINANCE - HEALTH - OTHER

Prompt template:

You are a strict classifier. Classify the following task into one of
these categories: WORK, PERSONAL, FINANCE, HEALTH, OTHER.

Return ONLY the category name. Do not explain.

Task: "{description}"

If AI response is not in allowed list: → fallback to OTHER

All AI calls must: - Be wrapped in try/except - Log failures - Never
crash request flow

------------------------------------------------------------------------

# 7. LOGGING REQUIREMENTS

Use structured logging.

Log: - Incoming requests - Validation failures - AI failures - DB errors

Format: timestamp \| level \| module \| message \| metadata

No print statements allowed.

Make sure to use logger in a way that user activity can be tracked.

------------------------------------------------------------------------

# 8. ERROR HANDLING

Centralized error handlers only.

Return JSON errors: { "error": { "type": "...", "message": "...",
"details": {...} } }

Never expose stack traces in production.

------------------------------------------------------------------------

# 9. TESTING REQUIREMENTS

Use pytest.

Required test cases: 1. Valid task creation 2. Invalid task creation
(missing title) 3. AI returns invalid category → fallback works 4. GET
tasks returns list 5. Health endpoint works

AI calls must be mocked.

------------------------------------------------------------------------

# 10. DOCKER REQUIREMENTS

Docker not required, so ignore this section.

------------------------------------------------------------------------

# 11. FRONTEND REQUIREMENTS

Minimal UI: - Form (title + description) - Submit button - Task list
display

Must: - Handle loading state - Handle API errors - Use environment
variable for API base URL - Contain NO business logic

------------------------------------------------------------------------

# 12. CHANGE RESILIENCE

Design so that: - Adding new category does not require route changes -
Changing AI provider affects only ai_service.py - Changing DB does not
affect routes

------------------------------------------------------------------------

# 13. README REQUIREMENTS

README must include: 1. Architecture explanation 2. Folder structure
explanation 3. AI prompt explanation 4. Tradeoffs made 5. Failure
scenarios handled 6. Extension plan

------------------------------------------------------------------------

# 14. WHAT AI MUST NOT DO

-   Do not combine logic into one file.
-   Do not skip validation.
-   Do not hardcode secrets.
-   Make .env file for secrets.
-   Make Config file and import all env variables from .env file into the config file using a class based Config class.
-   Do not add unnecessary features.
-   Do not introduce microservices.
-   Do not add Celery.

------------------------------------------------------------------------

# 15. IMPLEMENTATION ORDER

1.  Flask app factory
2.  Config system
3.  Models
4.  Schemas
5.  Services
6.  Routes
7.  Error handlers
8.  Logging
9.  Tests
10. Frontend

------------------------------------------------------------------------

# 16. EVALUATION PRIORITY

Optimize for: - Clarity - Predictability - Correctness - Observability -
Testability

Not: - UI beauty - Feature count - Clever tricks
