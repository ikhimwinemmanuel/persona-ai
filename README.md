# PersonaAI

**A full-stack conversational AI application with persistent conversation memory, built using Next.js, FastAPI, and OpenAI.**

PersonaAI is a personalised conversational AI application designed to represent an individual through a natural-language interface. It uses structured personality instructions and conversation history to provide context-aware responses across multiple interactions.

The project focuses on full-stack AI engineering, conversational memory, API development, and cloud deployment using AWS.

## Features

- **Personalised AI conversations** — Uses a configurable personality file to guide responses.
- **Persistent conversation memory** — Stores conversation history in JSON files and retrieves previous messages using session identifiers.
- **Session management** — Generates unique session IDs to maintain separate conversation histories.
- **Interactive chat interface** — Responsive React interface with message history, loading indicators, and automatic scrolling.
- **REST API** — FastAPI backend with Pydantic request and response validation.
- **Environment-based configuration** — Separates application settings and API credentials from source code.

## Technology Stack

| Layer                 | Technologies                              |
|-----------------------|-------------------------------------------|
| Frontend              | Next.js, React, TypeScript, Tailwind CSS  |
| Backend               | Python, FastAPI, Pydantic, Uvicorn        |
| AI                    | OpenAI API (GPT-4o mini)                  |
| Memory                | JSON-based file storage                   |
| Dependency Management | npm, uv                                   |
| Version Control       | Git, GitHub                               |

## System Architecture

The current implementation runs locally, with the frontend communicating with the FastAPI backend over HTTP.

```text
               User / Browser
                     |
                     v
             Next.js Frontend
              localhost:3000
                     |
                POST /chat
                     |
                     v
              FastAPI Backend
              localhost:8000
                     |
              +------+------+
              |             |
              v             v
         OpenAI API     JSON Memory
        GPT-4o mini     Local Files
```

**Conversation flow:**

1. The user submits a message through the Next.js interface.
2. FastAPI identifies the conversation session and retrieves its stored history.
3. The backend sends the personality instructions, conversation history, and latest message to OpenAI.
4. The generated response and new message are saved to the session's JSON file.
5. FastAPI returns the response to the frontend for display.

Conversation history is stored outside the model and supplied with subsequent requests. This enables contextual conversations without modifying or fine-tuning the underlying model.

## Project Structure

```text
PersonaAI/
├── backend/
│   ├── me.txt
│   ├── server.py
│   ├── requirements.txt
│   ├── pyproject.toml
│   └── uv.lock
├── frontend/
│   ├── app/
│   ├── components/
│   │   └── twin.tsx
│   ├── package.json
│   └── next.config.ts
├── memory/
├── .gitignore
└── README.md
```

The `memory/` directory stores local conversation data, which is excluded from version control.

## Local Development

**Prerequisites:** Python 3.12, Node.js, npm, uv, and an OpenAI API key.

**1. Configure the backend**

Create `backend/.env`:

```env
OPENAI_API_KEY=your_openai_api_key
CORS_ORIGINS=http://localhost:3000
```

**2. Start the backend**

From the `backend` directory:

```bash
uv sync
uv run uvicorn server:app --reload
```

FastAPI runs at `http://localhost:8000`.

**3. Start the frontend**

From the `frontend` directory:

```bash
npm install
npm run dev
```

Open `http://localhost:3000` to access PersonaAI.

## Current Validation

The following functionality has been manually tested locally:

- Frontend and backend connectivity
- OpenAI-generated conversational responses
- Session-based conversation memory
- Retrieval of earlier conversation details
- Local JSON conversation persistence

## Current Limitations

- Conversation memory is stored locally rather than in managed cloud storage.
- Previous messages are included in model requests without a conversation-length limit.
- The current application has no user authentication.
- The backend has not yet been deployed to AWS.

## AWS Deployment

AWS deployment is the next development milestone. The planned architecture uses AWS Lambda, API Gateway, Amazon S3, and Amazon CloudFront.

Deployment architecture, operational configuration, screenshots, and verification results will be documented here as each component is implemented and tested.

---