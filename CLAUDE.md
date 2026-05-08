# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

NVIC-质象 is a local FastAPI web app that turns a user-provided concept into a generated HTML/CSS/JS/SVG animation using an LLM. The browser UI streams generated code from the backend, renders it in a sandboxed iframe, and supports multi-turn refinement by sending conversation history back to the generation endpoint.

## Development commands

- Install dependencies: `pip install -r requirements.txt`
- Run the local launcher and open the browser: `python start_zhixiang.py`
- Run the API server directly: `python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload`
- Run the API server without verbose LLM logging: `DEBUG_LLM=0 python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload`
- Run with Docker Compose: `docker-compose up -d`
- Stop Docker Compose: `docker-compose down`
- Use a custom Docker host port: `HOST_PORT=3000 docker-compose up -d`

There is no project test suite, single-test command, build step, or lint configuration in the repository currently.

## Configuration

The backend reads `credentials.json` at import time and expects `API_KEY`, plus optional `BASE_URL` and `MODEL` fields. If `API_KEY` starts with `sk-`, the app uses the OpenAI-compatible `AsyncOpenAI` client and passes `BASE_URL`; otherwise it treats the key as Gemini and uses `google-genai` with `GEMINI_API_KEY` set from the file. The default model is `gemini-2.5-pro`.

LLM request/response debug logging is enabled by default; set `DEBUG_LLM=0` to disable it. `credentials.json` is mounted read-only into the container by `docker-compose.yml`. Be careful not to overwrite or expose the local credentials file.

## Architecture

- `app.py` contains the full FastAPI backend: credential loading, LLM client selection, prompt construction, SSE streaming generation, static file mounting, and the two routes.
- `POST /generate` accepts JSON `{ "topic": string, "history"?: list, "settings"?: object }` and returns `text/event-stream` chunks shaped as `data: {"token":"..."}` followed by `[DONE]`.
- `GET /` renders `templates/index.html` with a timestamp used for cache-busting static assets.
- `templates/index.html` defines the single-page interface, message templates, animation iframe player, language switcher, settings panel, and modal markup.
- `static/script.js` owns all frontend behavior: language selection, settings collection, form handling, conversation history, SSE response parsing, code block extraction from fenced Markdown, HTML validation, iframe rendering, and save/open actions.
- `static/style.css` styles the initial concept input view, chat view, generated-code details block, animation player, modal, settings panel, and warning overlay.
- `start_zhixiang.py` starts uvicorn in a background thread and opens `http://127.0.0.1:8000` in the default browser.

## Important implementation details

- The frontend expects the LLM response to contain a fenced code block; if no code block is parsed or the parsed HTML body is empty, it shows a parse error.
- Generation settings are constrained on the backend to known style, duration, aspect ratio, and depth values before they are interpolated into the prompt.
- Generated animation HTML is assigned to `iframe.srcdoc` inside an iframe with `sandbox="allow-scripts allow-same-origin"`.
- The chat history stored in the browser includes the full accumulated generated HTML as the assistant message after a successful stream.
- OpenRouter-specific headers are added only when `BASE_URL` contains `openrouter.ai`.
- The Docker image uses `python:3.10-slim`, matching the local Python 3.10+ requirement.
