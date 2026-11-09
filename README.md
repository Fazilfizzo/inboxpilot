# InboxPilot

**Intelligent Email Classification & Response Automation**

InboxPilot is a Python-based email automation project designed to help businesses manage customer support emails more efficiently.

The system aims to classify incoming emails, identify customer issues, determine priority, generate suggested responses, and organize the review and approval process before replies are sent.

The project is being developed incrementally, starting with a FastAPI-based classification API and progressing toward AI-assisted email processing and external service integrations.

## Project Inspiration

InboxPilot was inspired by the InboxPilot project featured in [Arslan Manzoor's AgenticFlow Portfolio](https://github.com/arslanmanzoorr/agenticflow-portfolio).

The original portfolio describes InboxPilot as an AI email classifier and auto-responder using Python, FastAPI, OpenAI, Gmail API, and Airtable.

This repository is my independent learning and implementation project. I am using the original concept as inspiration while developing my own application structure, business logic, implementation decisions, and workflow.

This project is not affiliated with or endorsed by the original author.

## Project Goals

The long-term objective is to build an email support automation workflow that can:

- Retrieve incoming customer emails from Gmail.
- Validate and process email content.
- Classify emails by category.
- Determine urgency and customer sentiment.
- Generate AI-assisted response drafts.
- Store processed emails and drafts in Airtable.
- Allow human reviewers to approve, edit, or reject drafts.
- Send approved responses through Gmail.
- Track processing status and failures.

**Human approval is mandatory for all outgoing replies in the initial version.**

## Current Implementation

### Milestone 1 — FastAPI Foundation

- [x] FastAPI application setup.
- [x] Pydantic request and response schemas.
- [x] Email input validation.
- [x] Rule-based email classification.
- [x] Email priority detection.
- [x] Basic sentiment detection.
- [x] Human-review requirement detection.
- [x] Health-check endpoint.
- [x] Email classification endpoint.
- [x] Automated schema, service, and API tests.
- [x] Centralized application configuration.
- [x] Development tooling and project documentation.

### Current API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Check application health |
| POST | `/api/v1/emails/classify` | Classify a customer email |

### Classification Categories

| Category | Description |
|---|---|
| `payment_issue` | Payments, billing, refunds, and transactions |
| `order_status` | Orders, shipments, delivery, and tracking |
| `complaint` | Customer complaints and dissatisfaction |
| `general` | General enquiries and other messages |

### Classification Response

Example:

```json
{
  "category": "payment_issue",
  "priority": "high",
  "sentiment": "negative",
  "requires_human": true
}
```

The current classifier uses keyword-based rules. It is an initial implementation, not an AI-powered classifier.

## Technology Stack

### Current

- Python
- FastAPI
- Pydantic
- Pydantic Settings
- Uvicorn
- Pytest
- HTTPX
- Ruff

### Planned Integrations

| Technology | Purpose |
|---|---|
| OpenAI API | AI-assisted classification and reply generation |
| Gmail API | Email retrieval and sending |
| Airtable | Email review and approval workspace |
| APScheduler | Periodic email polling |
| HTTPX | External API communication |
| Tenacity | Retry handling for transient failures |

Integrations will be introduced as development progresses.

## Architecture

The application follows a modular structure that separates API endpoints, business logic, data validation, configuration, and external integrations.

```text
inboxpilot/
├── app/
│   ├── api/
│   │   ├── router.py
│   │   └── v1/
│   │       ├── router.py
│   │       └── endpoints/
│   │           ├── health.py
│   │           └── emails.py
│   ├── core/
│   │   └── config.py
│   ├── models/
│   │   └── enums.py
│   ├── schemas/
│   │   ├── email.py
│   │   └── classification.py
│   ├── services/
│   │   └── classification_service.py
│   └── main.py
├── tests/
│   ├── conftest.py
│   ├── test_api.py
│   ├── test_schemas.py
│   └── test_classification_service.py
├── .env.example
├── .gitignore
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

The structure will expand as Gmail, Airtable, AI processing, and workflow components are implemented.

## Getting Started

### Requirements

- Python 3.12 or compatible newer version.
- pip.

### 1. Clone the repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd inboxpilot
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the environment

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
python -m pip install -r requirements-dev.txt
```

### 5. Configure environment variables

```powershell
Copy-Item .env.example .env
```

Update `.env` with your local configuration if needed.

### 6. Run the application

```bash
python -m uvicorn app.main:app --reload
```

The API will be available at:

`http://127.0.0.1:8000`

Interactive API documentation:

`http://127.0.0.1:8000/docs`

## Example API Request

**POST** `/api/v1/emails/classify`

Request:

```json
{
  "sender": "customer@gmail.com",
  "subject": "Payment problem",
  "body": "I was charged twice and this is unacceptable. Please resolve immediately."
}
```

Response:

```json
{
  "category": "payment_issue",
  "priority": "high",
  "sentiment": "negative",
  "requires_human": true
}
```

## Testing

Run all automated tests:

```bash
python -m pytest -v
```

Run tests with coverage:

```bash
python -m pytest --cov=app --cov-report=term-missing
```

## Code Quality

Check code quality:

```bash
python -m ruff check app tests
```

Format code:

```bash
python -m ruff format app tests
```

## Development Roadmap

- [x] Milestone 1 — FastAPI foundation and rule-based classification.
- [ ] Milestone 2 — AI-powered classification and reply generation.
- [ ] Milestone 3 — Airtable integration.
- [ ] Milestone 4 — Gmail authentication and email retrieval.
- [ ] Milestone 5 — Human approval workflow.
- [ ] Milestone 6 — Sending approved replies through Gmail.
- [ ] Milestone 7 — Automated email polling.
- [ ] Milestone 8 — Reliability, testing, documentation, and deployment.

## Design Principles

- Separation of concerns.
- Modular and maintainable architecture.
- Input validation at application boundaries.
- Human oversight for outgoing communications.
- Secure handling of credentials and environment variables.
- Reliable processing and clear error handling.
- Incremental development with automated testing.

## Acknowledgements

Special thanks to [Arslan Manzoor](https://github.com/arslanmanzoorr) for publishing the [AgenticFlow Portfolio](https://github.com/arslanmanzoorr/agenticflow-portfolio), which provided the inspiration for this project.

## License

A license will be added after reviewing the applicable licensing requirements and deciding how this independent implementation will be distributed.