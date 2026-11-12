# Mail_Genius

**Intelligent Email Classification & Response Automation**

Mail_Genius is a Python-based email automation project designed to help businesses manage customer support emails more efficiently.

The system aims to retrieve incoming customer emails, validate and process email content, classify customer issues using AI, determine priority and sentiment, generate AI-assisted response drafts, and organize the review and approval process before replies are sent.

The project is being developed incrementally, starting with a FastAPI-based classification API and progressing toward AI-powered email processing, Gmail integration, and external workflow services.

## Project Inspiration

Mail_Genius was inspired by the InboxPilot concept featured in [Arslan Manzoor's AgenticFlow Portfolio](https://github.com/arslanmanzoorr/agenticflow-portfolio).

The original portfolio describes an AI email classifier and auto-responder using Python, FastAPI, OpenAI, Gmail API, and Airtable.

This repository is my independent learning and implementation project. I am using the original concept as inspiration while developing my own application structure, business logic, implementation decisions, and workflow.

This project is not affiliated with or endorsed by the original author.

## Project Goals

The long-term objective is to build an intelligent email support automation workflow that can:

- Retrieve incoming customer emails from Gmail.
- Parse and extract email content and metadata.
- Validate and normalize incoming email data.
- Classify emails by category using AI.
- Determine urgency and customer sentiment.
- Generate AI-powered email summaries.
- Generate contextual response drafts.
- Store processed emails and drafts in Airtable.
- Allow human reviewers to approve, edit, or reject generated drafts.
- Send approved responses through Gmail.
- Track processing status, errors, and failures.
- Prevent duplicate email processing.

**Human approval is mandatory for all outgoing replies in the initial version.**

## Current Implementation

Development is organized into milestones, with each milestone introducing a specific capability.

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

### Milestone 2 — AI Integration

#### 2.1 AI Provider Foundation

- [x] AI provider abstraction.
- [x] Structured AI response interface.
- [x] Provider factory.
- [x] Centralized AI exception handling.

#### 2.2 Google Gemini Integration

- [x] Google Gemini provider implementation.
- [x] Structured response generation using Pydantic schemas.
- [x] Asynchronous AI request handling.
- [x] Provider error handling and retry support.
- [x] Configurable AI model and generation settings.
- [x] Asynchronous provider resource cleanup.

#### 2.3 Gmail Integration & AI Classification

**Gmail Authentication and Client**

- [x] Gmail OAuth 2.0 authentication.
- [x] Gmail API client implementation.
- [x] Retrieve Gmail account profile.
- [x] Retrieve messages from the inbox.
- [x] Fetch individual Gmail messages.

**Email Parsing**

- [x] Extract Gmail message ID and thread ID.
- [x] Extract sender, subject, and received timestamp.
- [x] Decode Base64URL-encoded email content.
- [x] Parse MIME email structures.
- [x] Extract plain-text email content.
- [x] Convert HTML email content into readable text.
- [x] Handle missing subjects and unreadable email bodies.
- [x] Add Gmail parser unit tests.

**Email Validation & Normalization**

- [x] Validate extracted sender email addresses.
- [x] Normalize email subjects.
- [x] Normalize email body content.
- [x] Normalize line endings.
- [x] Remove unwanted control characters.
- [x] Enforce application-level email constraints.
- [x] Convert parsed Gmail messages into the standard `EmailRequest` schema.

**Gemini-Powered Email Classification**

- [x] Implement AI-powered email classification service.
- [x] Use the provider abstraction to keep classification independent of the AI provider implementation.
- [x] Generate structured classification responses using Pydantic schemas.
- [x] Add a dedicated AI classification API endpoint.
- [x] Configure Gemini through environment variables.
- [x] Reuse the application-wide AI provider through FastAPI dependencies and lifespan management.
- [x] Preserve the original rule-based classification endpoint.

**Upcoming Work**

- [ ] 2.3.6 Email deduplication and integration tests.

#### 2.4 Email Summarization

- [ ] AI-powered email summarization.
- [ ] Structured summary responses.

#### 2.5 Reply Generation

- [ ] AI-powered reply generation.
- [ ] Context-aware response drafts.
- [ ] Response tone and style management.

#### 2.6 Prompt Security & Management

- [ ] Centralized prompt management.
- [ ] Prompt injection protection.
- [ ] Safe handling of untrusted email content.

#### 2.7 Reliability & Cost Controls

- [ ] Retry and timeout management improvements.
- [ ] AI usage and cost controls.
- [ ] Robust handling of external service failures.

#### 2.8 Testing & Documentation

- [ ] Comprehensive AI integration tests.
- [ ] End-to-end email processing tests.
- [ ] Documentation improvements.

## Current API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/health` | Check application health |
| POST | `/api/v1/emails/classify` | Classify a customer email using rule-based classification |
| POST | `/api/v1/emails/classify/ai` | Classify a customer email using Google Gemini |

The two classification endpoints are intentionally separate. This allows the rule-based and AI-powered approaches to coexist.

The Gmail integration currently provides internal components for authentication, message retrieval, parsing, and normalization. A complete automated Gmail-to-Gemini processing workflow has not yet been implemented.

## Classification Categories

| Category | Description |
|---|---|
| `payment_issue` | Payments, billing, refunds, and transactions |
| `order_status` | Orders, shipments, delivery, and tracking |
| `complaint` | Customer complaints and dissatisfaction |
| `general` | General enquiries and other messages |

### Classification Response

Both classification endpoints return the same structured response schema.

Example:

```json
{
  "category": "payment_issue",
  "priority": "high",
  "sentiment": "negative",
  "requires_human": true
}
```

The rule-based classifier uses keyword-based rules, while the AI-powered classifier uses Google Gemini to interpret the meaning and context of customer emails.

## Technology Stack

### Backend

| Technology | Purpose |
|---|---|
| Python | Primary programming language |
| FastAPI | REST API framework |
| Pydantic | Data validation and schemas |
| Pydantic Settings | Application configuration |
| Uvicorn | ASGI server |

### AI Integration

| Technology | Purpose |
|---|---|
| Google Gemini API | AI-powered email classification and processing |
| Google Gen AI SDK | Gemini API communication |
| Tenacity | Retry handling for transient failures |

### Gmail Integration

| Technology | Purpose |
|---|---|
| Gmail API | Retrieve incoming emails |
| Google OAuth 2.0 | Gmail authentication |
| Google API Python Client | Gmail API communication |
| Google Auth | Credential and token management |

### Testing & Code Quality

| Technology | Purpose |
|---|---|
| Pytest | Automated testing |
| HTTPX | API testing |
| Pytest-Cov | Test coverage |
| Ruff | Linting and code formatting |

### Planned Integrations

| Technology | Purpose |
|---|---|
| Airtable | Email review and approval workspace |
| APScheduler | Periodic email polling |
| Gmail API | Sending approved email replies |

## Architecture

Mail_Genius follows a modular architecture that separates API endpoints, business logic, data validation, AI providers, and external integrations.

The application uses an abstraction-based AI integration design so that application services do not depend directly on a specific AI provider implementation.

### AI Provider Architecture

The AI integration uses a provider abstraction:

- `AIProvider` defines the common interface for AI providers.
- `GeminiProvider` implements the interface using Google's Gen AI SDK.
- `factory.py` creates the configured AI provider.
- `AIClassificationService` uses the provider interface rather than directly depending on Gemini.
- FastAPI dependencies retrieve the shared provider from application state.
- FastAPI lifespan management initializes the provider during application startup and closes it during shutdown.

This architecture makes the AI integration easier to maintain and allows additional AI providers to be introduced without rewriting application services.

### Email Processing Workflow

The intended workflow is:

1. **Email Retrieval**
   - Authenticate with Gmail using OAuth 2.0.
   - Retrieve incoming messages through the Gmail API.

2. **Email Parsing**
   - Extract sender, subject, body, message ID, thread ID, and timestamp.
   - Decode MIME content and handle plain-text and HTML email formats.

3. **Email Validation & Normalization**
   - Validate sender email addresses.
   - Normalize email subjects and body content.
   - Enforce application-level field constraints.
   - Produce a standardized email request.

4. **Email Deduplication**
   - Check whether a Gmail message has already been processed.
   - Prevent duplicate processing.

5. **AI Classification**
   - Classify customer emails using Google Gemini.
   - Determine category, priority, and sentiment.
   - Identify emails requiring human review.

6. **Email Summarization**
   - Generate concise summaries of customer emails.

7. **Reply Generation**
   - Generate contextual response drafts.

8. **Human Approval**
   - Allow reviewers to review, edit, approve, or reject generated replies.

9. **Email Delivery**
   - Send approved responses through Gmail.

10. **Status Tracking**
    - Track email processing, approval, delivery, and failure states.

Gmail authentication, message retrieval, parsing, and normalization components are implemented. AI classification is available through a separate API endpoint. Automated orchestration of the complete Gmail-to-AI workflow and the remaining steps are under development.

### Project Structure

```text
Mail_Genius/
├── app/
│   ├── api/
│   │   ├── dependencies.py
│   │   ├── router.py
│   │   └── v1/
│   │       ├── router.py
│   │       └── endpoints/
│   │           ├── health.py
│   │           └── emails.py
│   ├── core/
│   │   └── config.py
│   ├── integrations/
│   │   ├── ai/
│   │   │   ├── base.py
│   │   │   ├── exceptions.py
│   │   │   ├── factory.py
│   │   │   └── providers/
│   │   │       ├── gemini_provider.py
│   │   │       └── mock_provider.py
│   │   └── gmail/
│   │       ├── auth.py
│   │       ├── client.py
│   │       ├── exceptions.py
│   │       └── parser.py
│   ├── models/
│   │   └── enums.py
│   ├── schemas/
│   │   ├── classification.py
│   │   ├── email.py
│   │   └── gmail.py
│   ├── services/
│   │   ├── ai_classification_service.py
│   │   ├── classification_service.py
│   │   └── email_normalization_service.py
│   └── main.py
├── scripts/
│   └── test_gmail_connection.py
├── tests/
│   ├── api/
│   ├── integration/
│   └── unit/
├── .env.example
├── .gitignore
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

The project structure will expand as email orchestration, deduplication, Airtable, and workflow components are introduced.

## Getting Started

### Requirements

- Python 3.12 or compatible newer version.
- pip.
- A Google account for Gmail integration.
- A Google Gemini API key for AI integration.

### 1. Clone the repository

```powershell
git clone <YOUR_REPOSITORY_URL>
cd Mail_Genius
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
```

### 3. Activate the environment

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```powershell
python -m pip install -r requirements-dev.txt
```

### 5. Configure environment variables

Create your local environment file:

```powershell
Copy-Item .env.example .env
```

Configure the required values in `.env`.

Example:

```env
APP_NAME=Mail Genius API
APP_VERSION=1.0.0
DEBUG=false

AI_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=your_supported_gemini_model_id

AI_TEMPERATURE=0.2
AI_MAX_OUTPUT_TOKENS=1000
AI_TIMEOUT_SECONDS=30

GMAIL_CREDENTIALS_FILE=credentials.json
GMAIL_TOKEN_FILE=token.json
GMAIL_MAX_RESULTS=10
GMAIL_QUERY=in:inbox
```

Use a Gemini model ID supported by your Google AI Studio account and API access.

Do not commit your actual `.env` file or API credentials.

### 6. Configure Gmail OAuth

Gmail integration requires Google OAuth credentials.

1. Create or configure a project in Google Cloud Console.
2. Enable the Gmail API.
3. Configure the OAuth consent screen.
4. Create OAuth 2.0 Desktop application credentials.
5. Download the credentials JSON file.
6. Place it in the project root as `credentials.json`.

The Gmail authentication flow generates `token.json` after successful authorization.

The current Gmail integration uses the read-only Gmail scope. Sending permissions will be introduced when approved reply delivery is implemented.

### 7. Run the application

```powershell
python -m uvicorn app.main:app --reload
```

The API will be available at:

`http://127.0.0.1:8000`

Interactive API documentation:

`http://127.0.0.1:8000/docs`

## Example API Requests

### Rule-Based Classification

**POST** `/api/v1/emails/classify`

Request:

```json
{
  "sender": "customer@gmail.com",
  "subject": "Payment problem",
  "body": "I was charged twice and this is unacceptable. Please resolve immediately."
}
```

### Gemini-Powered Classification

**POST** `/api/v1/emails/classify/ai`

Request:

```json
{
  "sender": "customer@gmail.com",
  "subject": "Payment problem",
  "body": "I was charged twice and this is unacceptable. Please resolve immediately."
}
```

Example response:

```json
{
  "category": "payment_issue",
  "priority": "high",
  "sentiment": "negative",
  "requires_human": true
}
```

Both endpoints use the same request and response schemas, making their outputs consistent and easier to compare.

## Testing

Run all automated tests:

```powershell
python -m pytest -v
```

Run tests with coverage:

```powershell
python -m pytest --cov=app --cov-report=term-missing
```

Run unit tests:

```powershell
python -m pytest tests/unit -v
```

Run API tests:

```powershell
python -m pytest tests/api -v
```

## Code Quality

Check code quality:

```powershell
python -m ruff check app tests
```

Format code:

```powershell
python -m ruff format app tests
```

Check formatting without modifying files:

```powershell
python -m ruff format --check app tests
```

## Security Considerations

- Gmail authentication uses OAuth 2.0.
- Gmail currently uses read-only access.
- OAuth credentials and access tokens must never be committed to version control.
- API keys and sensitive configuration values are stored in environment variables.
- Email content should not be logged unnecessarily.
- Customer email content is untrusted input and must be handled carefully when passed to AI models.
- AI-generated replies must be reviewed and approved by a human before sending.
- Use synthetic customer emails during development and review the AI provider's data-use terms before processing real customer information.

Ensure the following files are excluded from Git:

```gitignore
.env
credentials.json
token.json
.venv/
__pycache__/
.pytest_cache/
.ruff_cache/
.coverage
htmlcov/
```

## Development Roadmap

- [x] Milestone 1 — FastAPI foundation and rule-based classification.
- [x] Milestone 2.1 — AI provider abstraction and foundation.
- [x] Milestone 2.2 — Google Gemini provider integration.
- [x] Milestone 2.3.1 — Gmail OAuth authentication.
- [x] Milestone 2.3.2 — Gmail API client.
- [x] Milestone 2.3.3 — Gmail email parsing.
- [x] Milestone 2.3.4 — Email validation and normalization.
- [x] Milestone 2.3.5 — Gemini-powered email classification.
- [ ] Milestone 2.3.6 — Email deduplication and integration tests.
- [ ] Milestone 2.4 — AI-powered email summarization.
- [ ] Milestone 2.5 — AI-powered reply generation.
- [ ] Milestone 2.6 — Prompt security and management.
- [ ] Milestone 2.7 — Reliability and cost controls.
- [ ] Milestone 2.8 — Comprehensive testing and documentation.
- [ ] Milestone 3 — Airtable integration.
- [ ] Milestone 4 — Human approval workflow.
- [ ] Milestone 5 — Sending approved replies through Gmail.
- [ ] Milestone 6 — Automated email polling.
- [ ] Milestone 7 — Deployment and production readiness.

## Design Principles

- Separation of concerns.
- Modular and maintainable architecture.
- Provider abstraction and loose coupling.
- Input validation at application boundaries.
- Standardized data contracts.
- Human oversight for outgoing communications.
- Secure handling of credentials and environment variables.
- Reliable processing and clear error handling.
- Incremental development with automated testing.

## Acknowledgements

Special thanks to [Arslan Manzoor](https://github.com/arslanmanzoorr) for publishing the [AgenticFlow Portfolio](https://github.com/arslanmanzoorr/agenticflow-portfolio), which provided the inspiration for this project.

## License

A license will be added after reviewing the applicable licensing requirements and deciding how this independent implementation will be distributed.
