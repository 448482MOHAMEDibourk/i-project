# Setup — ai-school local LLMs (Ollama + Aider)

Assumptions

- You're on Linux (confirmed). Python 3.9+ is recommended.
- You have network access to install packages and (optionally) Docker to run services.
- Ollama and Aider local servers will be used; instructions include both native and Docker options where applicable.

1. Install system dependencies

- curl, git, and Python 3.9+.

2. Python environment

- Create venv: `python -m venv .venv` then `source .venv/bin/activate`
- Install requirements: `pip install -r requirements.txt`

3. Ollama

- Follow Ollama install guide: https://ollama.com/docs (native binary or Docker image)
- Start Ollama locally and ensure `http://localhost:11434` (or configured port) is reachable

4. Aider

- Aider provides a local LLM interface — follow their installation docs or run via Docker if available.

5. Configuration

- Copy `.env.example` to `.env` and set endpoints/API keys as needed.

6. Run demo

- `python scripts/demo_runner.py` — runs a simple prompt through configured clients

Notes

- If either service is unavailable, the clients will run in a dry-run/mock mode.
- For production, secure the endpoints and don't store secrets in plaintext.

Running local mocks with Docker (optional)

- If you don't have real Ollama/Aider installed, start the provided mock services with Docker Compose:

```bash
docker compose up --build
```

This brings up two simple Flask mocks:

- Ollama mock at `http://localhost:11434` (endpoint `/api/generate`)
- Aider mock at `http://localhost:8000` (endpoints `/ask`, `/generate`)

Set the environment variables accordingly or copy `.env.example` to `.env`.
